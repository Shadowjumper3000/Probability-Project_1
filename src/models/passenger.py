import numpy as np
from ..config import (
    ONLINE_CHECKIN_RATE,
    CARRYON_ONLY_RATE,
    EGATE_ELIGIBLE_RATE,
    PRIORITY_PASSENGER_RATE,
    CONNECTING_PASSENGER_RATE,
)


class Passenger:
    """Class representing a departing passenger"""

    id_counter = 0

    def __init__(self, env, flight):
        Passenger.id_counter += 1
        self.id = Passenger.id_counter
        self.env = env
        self.flight = flight

        # Passenger characteristics
        self.online_checkin = np.random.random() < ONLINE_CHECKIN_RATE
        self.has_bags = np.random.random() > CARRYON_ONLY_RATE
        self.egate_eligible = np.random.random() < EGATE_ELIGIBLE_RATE
        self.is_priority = np.random.random() < PRIORITY_PASSENGER_RATE
        self.is_connecting = False  # Always set to False to remove connecting passengers
        # Alternatively: self.is_connecting = np.random.random() < CONNECTING_PASSENGER_RATE

        # Timing statistics
        self.arrival_time = None
        self.checkin_wait = 0
        self.checkin_complete = 0
        self.security_wait = 0
        self.security_complete = 0
        self.passport_wait = 0
        self.passport_complete = 0
        self.boarding_wait = 0
        self.boarding_complete = 0

    @property
    def total_time(self):
        """Calculate total time in departure process"""
        return (
            self.boarding_complete - self.arrival_time if self.boarding_complete else 0
        )

    @property
    def total_wait_time(self):
        """Calculate total waiting time"""
        return (
            self.checkin_wait
            + self.security_wait
            + self.passport_wait
            + self.boarding_wait
        )
