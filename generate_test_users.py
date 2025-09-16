#!/usr/bin/env python3
"""
Test User Generator for AtHoc
Generates a CSV file with test user accounts containing collar IDs and emails.
"""

import csv
import random
from pathlib import Path

def generate_test_users(num_users=5000, min_collar=100, max_collar=12000, output_file="test_users.csv"):
    """
    Generate test user accounts with random collar IDs and corresponding emails
    
    Args:
        num_users: Number of user accounts to generate
        min_collar: Minimum collar ID value
        max_collar: Maximum collar ID value
        output_file: Output CSV filename
    """
    
    # Generate unique collar IDs
    print(f"Generating {num_users} test user accounts...")
    
    # Use a set to ensure unique collar IDs
    collar_ids = set()
    while len(collar_ids) < num_users:
        collar_id = random.randint(min_collar, max_collar)
        collar_ids.add(collar_id)
    
    # Convert to sorted list for consistent output
    collar_ids = sorted(list(collar_ids))
    
    # Create output file path
    output_path = Path(__file__).parent / output_file
    
    # Generate CSV file
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['collar_id', 'email'])
        
        # Write user data
        for collar_id in collar_ids:
            padded_collar_id = f"{collar_id:05d}"  # Pad with leading zeros to 5 places
            email = f"{collar_id}@bobosynctest.net"  # Email uses unpadded number
            writer.writerow([padded_collar_id, email])
    
    print(f"Successfully generated {len(collar_ids)} test users")
    print(f"Collar ID range: {min(collar_ids)} - {max(collar_ids)}")
    print(f"Output file: {output_path}")
    print(f"File size: {output_path.stat().st_size:,} bytes")
    
    # Show first few entries as sample
    print("\nFirst 10 entries:")
    print("Collar ID | Email")
    print("-" * 40)
    for i, collar_id in enumerate(collar_ids[:10]):
        padded_collar_id = f"{collar_id:05d}"
        email = f"{collar_id}@bobosynctest.net"
        print(f"{padded_collar_id:9} | {email}")
    
    print(f"\n... and {len(collar_ids) - 10} more entries")

def main():
    """Main entry point"""
    try:
        generate_test_users(
            num_users=5000,
            min_collar=100,
            max_collar=12000,
            output_file="test_users_athoc.csv"
        )
        print("\n✅ Test user CSV generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error generating test users: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 