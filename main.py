#!/usr/bin/env python3
# Madrid Barajas Airport T4 Queuing System Simulation
# Simulation of passenger flow through airport processes

import sys
from pathlib import Path
from src.simulation.airport import AirportSimulation
from src.utils.data_loader import load_flight_data
from src.utils.sim_params import SimulationParameters
from src.visualization.plots import (
    plot_queue_lengths,
    plot_resource_utilization,
    plot_passenger_times,
    plot_average_times_breakdown,
    plot_utilization_heatmap,
)
from src.visualization.statistics import print_statistics
from src.visualization.reports import generate_detailed_report
from src.config import SIM_TIME


def ensure_output_dirs():
    """Ensure output directories exist"""
    Path("results/plots").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)


def main():
    """Main execution function"""
    print("Madrid Barajas Airport T4 Queuing System Simulation")
    ensure_output_dirs()

    try:
        # Load flight data
        flights_df = load_flight_data()
        if flights_df is None:
            raise ValueError("Failed to load flight data")

        # Initialize simulation parameters
        params = SimulationParameters(sim_duration=SIM_TIME)

        # Run simulation
        print("\nRunning simulation...")
        simulation = AirportSimulation(params=params, flights_df=flights_df)
        results = simulation.run()

        # Print and visualize results
        print("\nSimulation Results:")
        print_statistics(results)

        # Original plots
        plot_queue_lengths(results)
        plot_resource_utilization(results)
        plot_passenger_times(simulation)

        # New insights
        plot_average_times_breakdown(results)
        plot_utilization_heatmap(results)

        # Generate detailed PDF report
        generate_detailed_report(results)
        print("Detailed report generated: results/T4_simulation_report.pdf")

        print("\nSimulation completed successfully")
        print("Results saved in 'results/plots' directory")
        return 0

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
