from ..models.flight import Flight
import pandas as pd
import numpy as np


class FlightScheduler:
    """Manages flight scheduling and passenger generation"""

    def __init__(self, env, flights_df):
        self.env = env
        self.flights_df = flights_df
        self.scheduled_flights = []

    def schedule_flights(self):
        """Convert flight data to simulation events"""
        for _, row in self.flights_df.iterrows():
            flight = Flight(
                env=self.env,
                flight_number=row["flight"],
                destination=row["destination"],
                scheduled_time=row["scheduled_time"],
                aircraft_type=row["aircraft"],
                airline=row["airline"],
            )

            # Schedule flight processing
            delay = (flight.scheduled_time - pd.Timestamp.now()).total_seconds() / 60
            self.env.process(self.process_flight(flight, delay))
            self.scheduled_flights.append(flight)

    def process_flight(self, flight, delay):
        """Process a flight's passengers"""
        # Wait until scheduled time
        yield self.env.timeout(delay)

        # Generate passengers with arrival time variation
        passengers = flight.generate_passengers()

        for passenger in passengers:
            # Add normal distribution for arrival time before flight
            arrival_offset = max(
                0, np.random.normal(120, 45)
            )  # Mean 120 minutes, std 45 minutes
            passenger.arrival_time = self.env.now - arrival_offset
            self.env.process(self.process_passenger(passenger))

    def process_passenger(self, passenger):
        """Process a passenger through all stations"""
        if not passenger.online_checkin:
            yield from self.stations["checkin"].process(passenger)
        yield from self.stations["security"].process(passenger)

        if not passenger.flight.is_schengen:
            yield from self.stations["passport"].process(passenger)

        if passenger.has_bags:
            yield from self.stations["baggage"].process(passenger)

        yield from self.stations["boarding"].process(passenger)
