import numpy as np
from .passenger import Passenger
from ..config import (
    SCHENGEN_AIRPORTS,
    AIRCRAFT_CAPACITY,
    FLIGHT_LOAD_FACTOR,
    FLIGHT_LOAD_FACTOR_STDDEV,
    OVERBOOKING_CHANCE,
    MAX_OVERBOOKING_FACTOR,
)


class Flight:
    """Class representing a flight at Madrid T4"""

    def __init__(
        self,
        env,
        flight_number,
        destination,
        scheduled_time,
        aircraft_type,
        airline,
        passengers=150,
    ):
        self.env = env
        self.flight_number = flight_number
        self.destination = destination
        self.scheduled_time = scheduled_time
        self.aircraft_type = aircraft_type
        self.airline = airline

        # Get capacity from aircraft type with fallback to default
        self.max_passengers = AIRCRAFT_CAPACITY.get(aircraft_type, passengers)

        # Determine if flight is to Schengen area
        self.is_schengen = self._check_schengen()

        # Flight characteristics
        self.passengers = []
        self.status = "Scheduled"
        self.actual_time = None
        self.is_overbooked = False
        self.overbooking_factor = 1.0

    def _check_schengen(self):
        """Check if flight destination is in Schengen area"""
        airport_code = self.destination.split("(")[-1].strip(")")
        return airport_code in SCHENGEN_AIRPORTS

    def generate_passengers(self):
        """Generate passengers for this flight with normal distribution"""
        # Determine if flight is overbooked
        self.is_overbooked = np.random.random() < OVERBOOKING_CHANCE

        # Calculate target capacity based on overbooking status
        if self.is_overbooked:
            # Random overbooking factor between 1.0 and MAX_OVERBOOKING_FACTOR
            self.overbooking_factor = 1.0 + (
                np.random.random() * (MAX_OVERBOOKING_FACTOR - 1.0)
            )
            target_capacity = self.max_passengers * self.overbooking_factor
        else:
            target_capacity = self.max_passengers

        # Sample load factor from normal distribution
        load_factor = np.clip(
            np.random.normal(FLIGHT_LOAD_FACTOR, FLIGHT_LOAD_FACTOR_STDDEV),
            0.6,  # Minimum load factor (60%)
            0.98,  # Maximum load factor (98%)
        )

        # Calculate mean passenger count
        mean_passengers = target_capacity * load_factor

        # Generate passenger count from normal distribution
        # Use a standard deviation that's proportional to aircraft size
        std_dev = max(
            2, mean_passengers * 0.05
        )  # At least 2 passengers, typically 5% of mean

        # Draw from normal distribution and round to nearest integer
        raw_passenger_count = np.random.normal(mean_passengers, std_dev)
        passenger_count = int(round(raw_passenger_count))

        # Ensure count is within reasonable bounds
        passenger_count = max(1, min(passenger_count, int(target_capacity * 1.05)))

        # Log passenger generation
        overbook_info = (
            f", Overbooked: {self.overbooking_factor:.2f}x"
            if self.is_overbooked
            else ""
        )
        print(
            f"Flight {self.flight_number}: {self.aircraft_type} ({self.max_passengers} seats), "
            f"generating {passenger_count} passengers (load: {load_factor:.2f}{overbook_info})"
        )

        # Reset passengers list
        self.passengers = []

        # Generate passengers
        for _ in range(passenger_count):
            passenger = Passenger(env=self.env, flight=self)
            self.passengers.append(passenger)

        return self.passengers

    def update_status(self, new_status):
        """Update flight status"""
        self.status = new_status
        if new_status == "Boarding":
            self.actual_time = self.env.now
