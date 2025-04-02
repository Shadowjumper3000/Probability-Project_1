# Madrid Airport T4 Departure Simulation

A discrete event simulation of passenger flow through Madrid Barajas Airport Terminal 4 departure processes.

## Overview

This simulation models passenger flow through departure processes including:
- Check-in desk operations
- Security screening
- Passport control (for non-Schengen flights)
- Boarding processes

The model uses real flight data and simulates resource utilization, queue dynamics, and passenger processing times.

## Project Structure

```
project_root/
├── src/                  # Source code
│   ├── models/          # Core simulation models
│   ├── simulation/      # Simulation engine
│   ├── visualization/   # Plotting and statistics
│   └── utils/          # Helper functions
├── data/                # Flight data
│   ├── raw/            # Raw PDF files
│   └── processed/      # SQLite databases
├── results/             # Simulation output
│   └── plots/          # Generated visualizations
├── notebooks/          # Analysis notebooks
└── logs/               # Simulation logs
```

## Installation

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate     # Windows
```

2. Install requirements:
```powershell
pip install -r requirements.txt
```

## Configuration

Modify simulation parameters in `src/config.py`:

### Resource Configuration
```python
# Number of service points
CHECKIN_DESKS = 174       # Check-in desks
SECURITY_LANES = 26       # Security lanes
PASSPORT_BOOTHS = 15      # Manual passport control
PASSPORT_EGATES = 10      # Automated passport gates
BOARDING_AGENTS = 2       # Boarding gate agents

# Service times (minutes)
CHECKIN_SERVICE_TIME = 2.0
SECURITY_SERVICE_TIME = 0.42
MANUAL_PASSPORT_TIME = 0.75
EGATE_SERVICE_TIME = 0.21
BOARDING_SERVICE_TIME = 0.1

# Passenger behavior rates
ONLINE_CHECKIN_RATE = 0.5
CARRYON_ONLY_RATE = 0.45
EGATE_ELIGIBLE_RATE = 0.7
PRIORITY_PASSENGER_RATE = 0.15
```

## Usage

1. Ensure data is present in `data/processed/flights.db`

2. Run the simulation:
```powershell
python main.py
```

3. View results in:
- `results/plots/`: Queue length, resource utilization, and passenger time plots
- `logs/`: Detailed simulation logs

## Analysis

The `notebooks/` directory contains Jupyter notebooks for:
- `analysis.ipynb`: Performance metrics and bottleneck analysis
- `statistics-calc.ipynb`: Flight data processing and statistical analysis

To run notebooks:
```powershell
jupyter notebook notebooks/
```

## Output

The simulation generates:
1. Queue length plots over time
2. Resource utilization graphs
3. Passenger processing time distributions
4. Summary statistics including:
   - Average wait times
   - Resource utilization rates
   - Passenger throughput
   - Queue lengths

## Dependencies

- Python 3.8+
- SimPy (discrete event simulation)
- Pandas (data handling)
- Matplotlib/Seaborn (visualization)
- SQLite3 (data storage)

## License

MIT License - See LICENSE file for details