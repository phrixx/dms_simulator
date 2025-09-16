# BOBO CSV Simulator

A lightweight simulator that generates BOBO CSV files for testing the BOBO → AtHoc integration. It produces realistic entries on a fixed interval and supports seeding with real-looking collar IDs.

## Prerequisites
- Python 3.10+
- Optional: virtual environment (`venv`)

## Files
- `bobosim.py` – main simulator
- `test_users_athoc.csv` – optional seed list of valid collar IDs (first column)
- `generate_test_users.py` – helper to create `test_users_athoc.csv`
- `output/` – generated CSV files

## Quick Start
```bash
cd simulator
python bobosim.py
```
This will:
- Read configuration from environment (or defaults)
- Load `test_users_athoc.csv` if present to bias valid/invalid IDs
- Generate CSVs in `output/` on a fixed interval

## Configuration
Set via environment variables (or create a `.env` alongside `bobosim.py`).

| Variable | Default | Description |
| --- | --- | --- |
| `OUTPUT_DIR` | `./output` | Directory to write CSV files |
| `SIMULATION_INTERVAL` | `60` | Seconds between file generations |
| `MIN_ENTRIES` | `5` | Minimum rows per file |
| `MAX_ENTRIES` | `25` | Maximum rows per file |
| `MAX_FILE_COUNT` | `100` | Stop after N files |

Example `.env`:
```env
OUTPUT_DIR=./output
SIMULATION_INTERVAL=30
MIN_ENTRIES=10
MAX_ENTRIES=20
MAX_FILE_COUNT=50
```

## Using Seed Users (Recommended)
If `test_users_athoc.csv` exists (first column = collar IDs):
- Simulator mixes valid IDs from the file with some unknown IDs
- Produces more realistic traffic and not-found scenarios

To generate it:
```bash
python generate_test_users.py
# creates simulator/test_users_athoc.csv (5,000 rows by default)
```

## What the CSV Looks Like
Each row has 10 columns in the expected BOBO format:
1. Transaction Type (`BON` or `BOF`)
2. Employee ID (5-digit string)
3. Payroll ID (ignored)
4. Clocking Date (`YYYYMMDD`)
5. Clocking Time (`HHMMSS`)
6. DateTime Created (`YYYYMMDDHHMMSS`)
7. Geo Status (ignored)
8. Latitude (ignored)
9. Longitude (ignored)
10. Accuracy (ignored)

Times are aligned to the current minute with randomized seconds to simulate bursts.

## Stopping the Simulator
- Ctrl+C (SIGINT) – graceful shutdown
- Auto-stops after `MAX_FILE_COUNT` files

## Common Workflows
- Change output location to the BOBO watch folder:
```env
OUTPUT_DIR=../crown_files
```
- Faster generation for testing:
```env
SIMULATION_INTERVAL=5
MAX_FILE_COUNT=20
```

## Troubleshooting
- If `test_users_athoc.csv` is missing, the simulator will print a warning and generate purely random IDs.
- Ensure `OUTPUT_DIR` exists or is creatable by the user running the script.
