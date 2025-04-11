import simpy
from ..models.stations import CheckIn, SecurityScreening, PassportControl, Boarding
from ..utils.stats_collector import StatsCollector
from ..utils.logger import setup_logger
from .scheduler import FlightScheduler  # Updated import path
from .monitor import SimulationMonitor


class AirportSimulation:
    """Main airport simulation class"""

    def __init__(self, params, flights_df=None):
        self.env = simpy.Environment()
        self.params = params
        self.flights_df = flights_df
        self.stats = StatsCollector()

        # Initialize stations
        self.stations = {
            "checkin": CheckIn(self.env),
            "security": SecurityScreening(self.env),
            "passport": PassportControl(self.env),
            "boarding": Boarding(self.env),
        }

        # Initialize monitor
        self.monitor = SimulationMonitor(
            env=self.env, stations=self.stations, stats_collector=self.stats
        )

        # Debug logging
        self.logger = setup_logger()

    def run(self):
        """Run the simulation"""
        try:
            # Initialize scheduler with stats collector
            scheduler = FlightScheduler(
                env=self.env, flights_df=self.flights_df, stations=self.stations
            )
            scheduler.set_stats_collector(self.stats)
            scheduler.schedule_flights()

            # Run simulation
            self.env.run(until=self.params["sim_duration"])

            return self.stats.get_summary()

        except Exception as e:
            self.logger.error(f"Simulation failed: {str(e)}")
            raise
