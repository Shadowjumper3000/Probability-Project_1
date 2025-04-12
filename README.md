# Madrid Airport T4 Departure Simulation

A discrete event simulation of passenger flow through Madrid Barajas Airport Terminal 4 departure processes using SimPy.

## How the Simulation Works

### SimPy Framework
This simulation uses SimPy, a process-based discrete-event simulation framework. The key components include:
- **Environment**: [`simpy.Environment`] that drives the simulation time
- **Resources**: [`simpy.Resource`] objects representing service points (check-in desks, security lanes, etc.)
- **Processes**: Functions that model the activities of passengers moving through the airport

### Passenger Flow
1. **Flight Generation**: The simulation loads flight data and schedules them based on departure times. 
   - Each flight has a unique set of attributes (e.g., airline, destination, departure time).
   - Flights are generated from a CSV file (`data/processed/flights.db`) containing historical flight data.
   - The simulation can be customized to generate flights based on different parameters (e.g., peak hours, airline types).
   - The simulation can also be run with a fixed set of flights for testing purposes.
2. **Passenger Generation**: Each flight generates a random number of passengers with varying attributes:
   - Online check-in status
   - Baggage requirements
   - Priority status
   - Passport/e-gate eligibility
3. **Processing Stations**: Passengers move through these stations in sequence:
   - Check-in (if not already online)
   - Security screening
   - Passport control (for non-Schengen flights)
   - Boarding gate

### Data Collection
The [`SimulationMonitor`] class tracks:
- Queue lengths at each station
- Resource utilization rates
- Passenger waiting and processing times
- Bottlenecks and resource conflicts

## Project Structure

```
.
├── data
│   ├── processed
│   │   └── flights.db
│   └── raw
│       └── flights.csv
├── logs
│   └── simulation_YYYYMMDD_HHMM.log
├── notebooks
│   └── analysis.ipynb
├── results
│   ├── plots
│   │   ├── queue_lengths.png
│   │   ├── resource_utilization.png
│   │   └── passenger_processing_times.png
│   └── T4_simulation_report.pdf
├── src
│   ├── __init__.py
│   ├── config.py <!-- Simulation parameters and configuration -->
│   ├── simulation
│   │   ├── __init__.py
│   │   ├── airport.py
│   │   ├── passenger.py
│   │   └── simulation_monitor.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── logger.py
│   │   └── sim_params.py
├── main.py <!-- Main entry point for the simulation -->
└── requirements.txt <!-- Project dependencies and requirements --> 
```

## Installation

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install requirements:
```powershell
pip install -r requirements.txt
```

3. Run the simulation:
```powershell
python main.py
```

## Configuration & Parameter Customization

### Basic Parameters
Edit [`src/config.py`] to modify simulation parameters:

```python
# Simulation duration (in minutes)
SIM_TIME = 24 * 60  # 24 hours

# Resource allocation
CHECKIN_DESKS = 80
IBERIA_DESKS = 60
SECURITY_LANES = 24
BAG_SCANNERS = 24
PASSPORT_BOOTHS = 8
PASSPORT_EGATES = 6

# Service time parameters (minutes)
CHECKIN_SERVICE_TIME = 2.5
SECURITY_SERVICE_TIME = 0.75
BAG_SCAN_TIME = 0.33

# Passenger behavior rates
ONLINE_CHECKIN_RATE = 0.5
CARRYON_ONLY_RATE = 0.45
EGATE_ELIGIBLE_RATE = 0.7
```

### Advanced Configuration
For scenario testing, use the [`SimulationParameters`] class to create and validate custom parameter sets:

```python
# Example of creating custom parameters
params = SimulationParameters(
    sim_duration=12*60,  # 12-hour simulation
    num_security_lanes=30,  # Increased security capacity
    online_checkin_rate=0.7  # Higher online check-in rate
)
```

### Running Scenarios
The [`ScenarioManager`] class allows you to run and compare multiple parameter configurations:

```python
# Example of scenario comparison
scenario_mgr = ScenarioManager()
baseline = scenario_mgr.run_scenario("baseline", AirportSimulation)
improved = scenario_mgr.run_scenario(
    "improved_security", 
    AirportSimulation, 
    num_security_lanes=30
)
```

## Running the Simulation

### Basic Execution
Run the default simulation:

```powershell
python main.py
```

This will:
1. Load flight data from `data/processed/flights.db`
2. Initialize the simulation with default parameters
3. Run the simulation for 24 hours (simulated time)
4. Generate analysis outputs in `results/plots/`
5. Create a detailed PDF report at `results/T4_simulation_report.pdf`
6. Save logs to `logs/simulation_YYYYMMDD_HHMM.log`

### Customizing Execution
To modify simulation behavior without changing the config file, you can:

1. Edit the [`main.py`] file to use custom parameters:
   ```python
   # Initialize simulation with custom parameters
   params = SimulationParameters(
       sim_duration=12*60,  # 12-hour simulation
       num_security_lanes=30  # Increased security capacity
   )
   simulation = AirportSimulation(params=params, flights_df=flights_df)
   ```

2. Create a custom script that imports and uses the simulation components:
   ```python
   from src.simulation.airport import AirportSimulation
   from src.utils.sim_params import SimulationParameters
   
   # Custom simulation setup
   params = SimulationParameters(online_checkin_rate=0.8)
   sim = AirportSimulation(params)
   results = sim.run()
   ```

## Analysis and Visualization

The simulation automatically generates:
- Queue length plots over time
- Resource utilization graphs
- Passenger processing time distributions
- Detailed statistics on wait times and throughput
- A PDF report summarizing findings

For custom analysis, explore the notebooks in the `notebooks/` directory:
```powershell
jupyter notebook notebooks/
```

## Dependencies

- Python 3.8+
- SimPy (discrete-event simulation framework)
- Pandas (data handling)
- Matplotlib/Seaborn (visualization)
- ReportLab (PDF report generation)

## License

MIT License - See LICENSE file for details