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
        self.queue = []  # Will store tuples of (passenger_id, entry_time)
        self.scanner_queue = []  # Will store tuples of (passenger_id, entry_time)

    def process(self, passenger):
        """Process passenger through security screening"""
        entry_time = self.env.now
        queue_entry = (passenger.id, entry_time)
        self.queue.append(queue_entry)

        try:
            # Request security lane
            with self.lanes.request() as lane:
                yield lane

                # Remove from queue after successfully getting a lane
                if queue_entry in self.queue:  # Safety check
                    self.queue.remove(queue_entry)

                # Process personal screening
                service_time = np.random.normal(
                    SECURITY_SERVICE_TIME, SECURITY_SERVICE_TIME_STDDEV
                )
                yield self.env.timeout(max(0.1, service_time))

                # Process bags if passenger has them
                if passenger.has_bags and passenger.num_bags > 0:
                    scanner_entry_time = self.env.now
                    scanner_queue_entry = (passenger.id, scanner_entry_time)
                    self.scanner_queue.append(scanner_queue_entry)

                    with self.scanners.request() as scanner:
                        yield scanner

                        # Remove from scanner queue
                        if scanner_queue_entry in self.scanner_queue:
                            self.scanner_queue.remove(scanner_queue_entry)

                        # Process each bag individually
                        total_bag_time = 0
                        for _ in range(passenger.num_bags):
                            bag_time = np.random.normal(
                                BAG_SCAN_TIME, BAG_SCAN_TIME_STDDEV
                            )
                            total_bag_time += max(0.1, bag_time)

                        # Apply the total bag scanning time
                        yield self.env.timeout(total_bag_time)

        except Exception as e:
            # Ensure passenger is removed from queues on exception
            if queue_entry in self.queue:
                self.queue.remove(queue_entry)
            print(
                f"Error in security processing for passenger {passenger.id}: {str(e)}"
            )

        finally:
            # Record statistics even if exception occurred
            passenger.security_wait = self.env.now - entry_time
            passenger.security_complete = self.env.now
