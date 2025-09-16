#!/usr/bin/env python3
"""
BOBO CSV Data Simulator
Generates random CSV data for testing the BOBO data processing utility.
Runs continuously every minute until interrupted or max file count is reached.
"""

import csv
import random
import os
import time
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("WARNING: python-dotenv not installed. Environment variables must be set manually.")
except Exception as e:
    print(f"WARNING: Could not load .env file: {e}")

# Global variables for collar ID management
VALID_COLLAR_IDS = []
UNKNOWN_COLLAR_IDS = []

# Configuration defaults
DEFAULT_CONFIG = {
    'OUTPUT_DIR': './output',
    'SIMULATION_INTERVAL': 60,
    'MIN_ENTRIES': 5,
    'MAX_ENTRIES': 25,
    'MAX_FILE_COUNT': 100
}

def load_env_config():
    """Load configuration from environment variables (loaded from .env file)."""
    config = {}
    
    # Load configuration from environment variables with defaults
    config['OUTPUT_DIR'] = os.getenv('OUTPUT_DIR', './output')
    config['SIMULATION_INTERVAL'] = int(os.getenv('SIMULATION_INTERVAL', '60'))
    config['MIN_ENTRIES'] = int(os.getenv('MIN_ENTRIES', '5'))
    config['MAX_ENTRIES'] = int(os.getenv('MAX_ENTRIES', '25'))
    config['MAX_FILE_COUNT'] = int(os.getenv('MAX_FILE_COUNT', '100'))
    
    return config

def load_valid_collar_ids():
    """Load valid collar IDs from test_users_athoc.csv file."""
    global VALID_COLLAR_IDS
    csv_file = Path(__file__).parent / 'test_users_athoc.csv'
    
    if not csv_file.exists():
        print(f"Warning: {csv_file} not found. Using random collar IDs instead.")
        return False
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            VALID_COLLAR_IDS = []
            for row in reader:
                if row and len(row) >= 1:
                    collar_id = row[0].strip()
                    if collar_id:
                        VALID_COLLAR_IDS.append(collar_id)
        
        print(f"Loaded {len(VALID_COLLAR_IDS)} valid collar IDs from test_users_athoc.csv")
        return True
        
    except Exception as e:
        print(f"Error loading collar IDs: {e}")
        return False

def generate_unknown_collar_ids():
    """Generate collar IDs that are NOT in the test_users_athoc.csv file."""
    global UNKNOWN_COLLAR_IDS
    
    if not VALID_COLLAR_IDS:
        return
    
    # Convert valid collar IDs to integers for comparison
    valid_ids_set = set()
    for collar_id in VALID_COLLAR_IDS:
        try:
            valid_ids_set.add(int(collar_id))
        except ValueError:
            continue
    
    # Generate unknown collar IDs outside the range or not in the valid set
    UNKNOWN_COLLAR_IDS = []
    
    # Add some IDs below the minimum range
    for _ in range(10):
        unknown_id = random.randint(1, 99)
        if unknown_id not in valid_ids_set:
            UNKNOWN_COLLAR_IDS.append(f"{unknown_id:05d}")
    
    # Add some IDs above the maximum range  
    for _ in range(10):
        unknown_id = random.randint(12001, 15000)
        if unknown_id not in valid_ids_set:
            UNKNOWN_COLLAR_IDS.append(f"{unknown_id:05d}")
    
    # Add some IDs within the range but not in the valid set
    for _ in range(20):
        unknown_id = random.randint(100, 12000)
        if unknown_id not in valid_ids_set:
            UNKNOWN_COLLAR_IDS.append(f"{unknown_id:05d}")
    
    print(f"Generated {len(UNKNOWN_COLLAR_IDS)} unknown collar IDs for simulation")

def ensure_output_directory(output_dir):
    """Create output directory if it doesn't exist."""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating output directory '{output_dir}': {e}")
        return False

def generate_random_entry(execution_time, employee_id=None):
    """Generate a single random CSV entry following the BOBO format."""
    
    # Transaction type: BON or BOF
    transaction_type = random.choice(['BON', 'BOF'])
    
    # Employee ID: Use provided ID or generate random 5-digit number
    if employee_id is None:
        employee_id = f"{random.randint(1, 99999):05d}"
    
    # Payroll ID: Generate random number (to be ignored)
    payroll_id = random.randint(10000, 99999)
    
    # Use execution time for clocking date and base time
    clocking_date = execution_time.strftime('%Y%m%d')
    
    # Clocking time: Use current hour and minute, but vary seconds
    base_hour = execution_time.hour
    base_minute = execution_time.minute
    random_second = random.randint(0, 59)  # Only seconds vary
    clocking_time = f"{base_hour:02d}{base_minute:02d}{random_second:02d}"
    
    # DateTime created: combination of date and time
    datetime_created = f"{clocking_date}{clocking_time}"
    
    # GeoStatus: random integer (to be ignored)
    geo_status = random.randint(0, 5)
    
    # GeoLatitude: random latitude (to be ignored)
    geo_latitude = round(random.uniform(-90.0, 90.0), 6)
    
    # GeoLongitude: random longitude (to be ignored)
    geo_longitude = round(random.uniform(-180.0, 180.0), 6)
    
    # GeoAccuracy: random accuracy in meters (to be ignored)
    geo_accuracy = round(random.uniform(1.0, 100.0), 2)
    
    return [
        transaction_type,
        employee_id,
        payroll_id,
        clocking_date,
        clocking_time,
        datetime_created,
        geo_status,
        geo_latitude,
        geo_longitude,
        geo_accuracy
    ]

def create_bobo_csv(config, run_counter):
    """Create a CSV file with random BOBO data."""
    
    # Get current execution time
    execution_time = datetime.now()
    
    # Create timestamp for filename
    timestamp = execution_time.strftime('%Y%m%d_%H%M%S')
    filename = f"BOBO_{timestamp}_output.csv"
    
    # Use configured output directory
    output_path = Path(config['OUTPUT_DIR']) / filename
    
    # Generate random number of entries within configured range
    num_entries = random.randint(config['MIN_ENTRIES'], config['MAX_ENTRIES'])
    
    # Determine collar IDs to use for this run
    collar_ids_to_use = []
    unknown_count = 0
    
    if VALID_COLLAR_IDS:
        # Randomly add 0-2 unknown collar IDs for this run
        unknown_count = random.randint(0, 2)
        if unknown_count > 0 and UNKNOWN_COLLAR_IDS:
            unknown_ids = random.sample(UNKNOWN_COLLAR_IDS, min(unknown_count, len(UNKNOWN_COLLAR_IDS)))
            collar_ids_to_use.extend(unknown_ids)
        
        # Fill remaining entries with valid collar IDs
        remaining_entries = num_entries - len(collar_ids_to_use)
        if remaining_entries > 0:
            valid_ids = random.choices(VALID_COLLAR_IDS, k=remaining_entries)
            collar_ids_to_use.extend(valid_ids)
        
        # Shuffle the order so unknown IDs aren't always at the beginning
        random.shuffle(collar_ids_to_use)
    
    try:
        # Create CSV file
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Generate and write entries with appropriate collar IDs
            for i in range(num_entries):
                if collar_ids_to_use and i < len(collar_ids_to_use):
                    # Use predetermined collar ID
                    entry = generate_random_entry(execution_time, collar_ids_to_use[i])
                else:
                    # Fallback to random generation if collar ID lists aren't available
                    entry = generate_random_entry(execution_time)
                writer.writerow(entry)
        
        print(f"[{execution_time.strftime('%Y-%m-%d %H:%M:%S')}] Generated {filename} with {num_entries} entries (File #{run_counter}/{config['MAX_FILE_COUNT']})")
        print(f"  All entries use date: {execution_time.strftime('%Y%m%d')} and base time: {execution_time.strftime('%H%M')}XX")
        if VALID_COLLAR_IDS:
            valid_count = num_entries - unknown_count
            print(f"  Collar IDs: {valid_count} valid, {unknown_count} unknown (not in AtHoc)")
        return str(output_path)
    
    except Exception as e:
        print(f"[{execution_time.strftime('%Y-%m-%d %H:%M:%S')}] Error creating CSV file: {e}")
        return None

def signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received termination signal. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function to run the simulator continuously."""
    print("BOBO CSV Data Simulator - Continuous Mode")
    print("=" * 50)
    
    # Load configuration
    config = load_env_config()
    
    # Display configuration
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Load collar ID data
    print("Loading collar ID data...")
    if load_valid_collar_ids():
        generate_unknown_collar_ids()
        print("Collar ID data loaded successfully.")
    else:
        print("Warning: Failed to load collar ID data. Will use random collar IDs.")
    print()
    
    # Ensure output directory exists
    if not ensure_output_directory(config['OUTPUT_DIR']):
        print("Failed to create output directory. Exiting.")
        sys.exit(1)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    print(f"Starting continuous simulation (every {config['SIMULATION_INTERVAL']} seconds)")
    print(f"Will create maximum of {config['MAX_FILE_COUNT']} files before stopping")
    print("Each execution will use current date/time with varying seconds only")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Initialize run counter
    run_counter = 0
    
    try:
        while run_counter < config['MAX_FILE_COUNT']:
            # Increment counter
            run_counter += 1
            
            # Create CSV file
            csv_file = create_bobo_csv(config, run_counter)
            
            if csv_file:
                print(f"  Output: {csv_file}")
            
            # Check if we've reached the maximum
            if run_counter >= config['MAX_FILE_COUNT']:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Maximum file count ({config['MAX_FILE_COUNT']}) reached. Stopping simulation.")
                break
            
            # Wait for next iteration
            print(f"  Next generation in {config['SIMULATION_INTERVAL']} seconds...")
            time.sleep(config['SIMULATION_INTERVAL'])
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Simulation stopped by user after {run_counter} files.")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error: {e}")
    
    print(f"BOBO Simulator shutdown complete. Total files created: {run_counter}")

if __name__ == "__main__":
    main() 