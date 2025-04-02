from ..models.flight import Flight


class FlightScheduler:
    """Manages flight scheduling and passenger generation"""

    def __init__(self, env, flights_df, stations):
        self.env = env
        self.flights_df = flights_df
        self.stations = stations
        self.scheduled_flights = []
        self.processed_passengers = []
        self.base_time = None
        self.stats = None  # Will be set by AirportSimulation
        self.total_passengers = 0

    def set_stats_collector(self, stats_collector):
        """Set the stats collector for tracking passengers"""
        self.stats = stats_collector

    def schedule_flights(self):
        """Convert flight data to simulation events"""
        if self.flights_df is None:
            raise ValueError("No flight data available")

        # Set base time to first flight time
        self.base_time = self.flights_df["scheduled_time"].min()

        for _, row in self.flights_df.iterrows():
            # Calculate delay in minutes from base time
            delay = (row["scheduled_time"] - self.base_time).total_seconds() / 60

            if delay < 0:
                continue  # Skip flights before base time

            flight = Flight(
                env=self.env,
                flight_number=row["flight"],
                destination=row["destination"],
                scheduled_time=row["scheduled_time"],
                aircraft_type=row["aircraft"],
                airline=row["airline"],
            )

            # Schedule flight processing
            self.env.process(self.process_flight(flight, delay))
            self.scheduled_flights.append(flight)

    def process_flight(self, flight, delay):
        """Process a flight's passengers"""
        # Wait until scheduled time
        yield self.env.timeout(delay)

        # Generate and process passengers
        passengers = flight.generate_passengers()
        self.total_passengers += len(passengers)
        self.stats.stats["total_passengers"] = self.total_passengers

        for passenger in passengers:
            passenger.arrival_time = self.env.now
            self.env.process(self.process_passenger(passenger))

    def process_passenger(self, passenger):
        """Process a passenger through all departure stations"""
        try:
            if not passenger.online_checkin:
                yield from self.stations["checkin"].process(passenger)

            yield from self.stations["security"].process(passenger)

            if not passenger.flight.is_schengen:
                yield from self.stations["passport"].process(passenger)

            yield from self.stations["boarding"].process(passenger)

            # Record completed passenger
            self.stats.record_passenger(passenger)

        except Exception as e:
            print(f"Error processing passenger {passenger.id}: {str(e)}")
