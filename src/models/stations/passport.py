import simpy
import numpy as np
from ...config import (
    PASSPORT_BOOTHS,
    PASSPORT_EGATES,
    EGATE_SERVICE_TIME,
    MANUAL_PASSPORT_TIME,
)


class PassportControl:
    """Passport control with manual booths and e-gates"""

    def __init__(self, env):
        self.env = env
        self.booths = simpy.Resource(env, capacity=PASSPORT_BOOTHS)
        self.egates = simpy.Resource(env, capacity=PASSPORT_EGATES)
        self.booth_queue = []
        self.egate_queue = []

    @property
    def queue(self):
        """Total queue length for monitoring"""
        return self.booth_queue + self.egate_queue

    def process(self, passenger):
        """Process passenger through passport control"""
        entry_time = self.env.now

        # Choose appropriate control method
        if passenger.egate_eligible:
            queue = self.egate_queue
            control = self.egates
            service_time = EGATE_SERVICE_TIME
        else:
            queue = self.booth_queue
            control = self.booths
            service_time = MANUAL_PASSPORT_TIME

        queue.append(entry_time)

        with control.request() as req:
            yield req
            queue.remove(entry_time)

            # Process passport check
            yield self.env.timeout(service_time)

            # Record statistics
            passenger.passport_wait = self.env.now - entry_time
            passenger.passport_complete = self.env.now
