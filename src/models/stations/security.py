import simpy
import numpy as np
from ...config import (
    SECURITY_LANES,
    BAG_SCANNERS,
    SECURITY_SERVICE_TIME,
    SECURITY_SERVICE_TIME_STDDEV,
    BAG_SCAN_TIME,
    BAG_SCAN_TIME_STDDEV,
)


class SecurityScreening:
    """Security screening with multiple lanes and bag scanners"""

    def __init__(self, env):
        self.env = env
        self.lanes = simpy.Resource(env, capacity=SECURITY_LANES)
        self.scanners = simpy.Resource(env, capacity=BAG_SCANNERS)
        self.queue = []
        self.scanner_queue = []

    def process(self, passenger):
        """Process passenger through security screening"""
        entry_time = self.env.now
        self.queue.append(entry_time)

        # Request security lane
        with self.lanes.request() as lane:
            yield lane
            self.queue.remove(entry_time)

            # Process personal screening
            service_time = np.random.normal(
                SECURITY_SERVICE_TIME, SECURITY_SERVICE_TIME_STDDEV
            )
            yield self.env.timeout(max(0.1, service_time))

            # Process bags if passenger has them
            if passenger.has_bags:
                scanner_entry = self.env.now
                self.scanner_queue.append(scanner_entry)

                with self.scanners.request() as scanner:
                    yield scanner
                    self.scanner_queue.remove(scanner_entry)

                    scan_time = np.random.normal(BAG_SCAN_TIME, BAG_SCAN_TIME_STDDEV)
                    yield self.env.timeout(max(0.1, scan_time))

            # Record statistics
            passenger.security_wait = self.env.now - entry_time
            passenger.security_complete = self.env.now
