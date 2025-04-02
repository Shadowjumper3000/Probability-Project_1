import simpy
import numpy as np
from src.config import (
    CHECKIN_DESKS,
    IBERIA_DESKS,
    CHECKIN_SERVICE_TIME,
    CHECKIN_SERVICE_TIME_STDDEV,
)


class CheckIn:
    """Check-in station with multiple desks grouped by airline"""

    def __init__(self, env):
        self.env = env
        # Iberia desks
        self.iberia_desks = simpy.Resource(env, capacity=IBERIA_DESKS)
        # Other airlines desks
        self.other_desks = simpy.Resource(env, capacity=CHECKIN_DESKS - IBERIA_DESKS)
        # Queue length tracking
        self.iberia_queue = []
        self.other_queue = []

    @property
    def queue(self):
        """Total queue length for monitoring"""
        return self.iberia_queue + self.other_queue

    def process(self, passenger):
        """Process a passenger through check-in"""
        # Track queue entry time
        entry_time = self.env.now

        # Choose appropriate desk based on airline
        if passenger.flight.airline == "Iberia":
            desk = self.iberia_desks
            queue = self.iberia_queue
        else:
            desk = self.other_desks
            queue = self.other_queue

        # Add to queue
        queue.append(self.env.now)

        # Request desk
        with desk.request() as req:
            yield req

            # Remove from queue
            queue.remove(entry_time)

            # Process check-in
            service_time = np.random.normal(
                CHECKIN_SERVICE_TIME, CHECKIN_SERVICE_TIME_STDDEV
            )
            yield self.env.timeout(max(0.1, service_time))

            # Record statistics
            passenger.checkin_wait = self.env.now - entry_time
            passenger.checkin_complete = self.env.now
