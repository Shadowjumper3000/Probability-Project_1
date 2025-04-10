import numpy as np
from .passenger import Passenger
from ..config import (
    SCHENGEN_AIRPORTS,
    AIRCRAFT_CAPACITY,
    FLIGHT_LOAD_FACTOR,
    FLIGHT_LOAD_FACTOR_STDDEV,
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
        self.max_passengers = AIRCRAFT_CAPACITY.get(aircraft_type, passengers)

        # Determine if flight is to Schengen area
        self.is_schengen = self._check_schengen()

        # Flight characteristics
        self.passengers = []
        self.status = "Scheduled"
        self.actual_time = None

    def _check_schengen(self):
        """Check if flight destination is in Schengen area"""
        airport_code = self.destination.split("(")[-1].strip(")")
        return airport_code in SCHENGEN_AIRPORTS

    def generate_passengers(self):
        """Generate passengers for this flight"""
        # Use the configurable load factor with some normal variation
        load_factor = np.clip(
            np.random.normal(FLIGHT_LOAD_FACTOR, FLIGHT_LOAD_FACTOR_STDDEV),
            0.5,  # Minimum load factor (50%)
            1.0,  # Maximum load factor (100%)
        )

        num_passengers = np.random.poisson(self.max_passengers * load_factor)

        # Log passenger generation
        print(
            f"Generating {num_passengers} passengers for flight {self.flight_number} (Load factor: {load_factor:.2f})"
        )

        # Reset passengers list
        self.passengers = []

        # Generate passengers
        for _ in range(num_passengers):
            passenger = Passenger(env=self.env, flight=self)
            self.passengers.append(passenger)

        return self.passengers

    def update_status(self, new_status):
        """Update flight status"""
        self.status = new_status
        if new_status == "Boarding":
            self.actual_time = self.env.now
