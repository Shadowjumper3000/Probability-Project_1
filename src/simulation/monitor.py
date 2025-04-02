class SimulationMonitor:
    """Monitors and collects real-time simulation statistics"""

    def __init__(self, env, stations, stats_collector):
        self.env = env
        self.stations = stations
        self.stats = stats_collector
        self.env.process(self.monitor())

    def monitor(self):
        """Monitor queues and utilization at regular intervals"""
        while True:
            current_time = self.env.now

            # Record utilization and queue lengths
            for name, station in self.stations.items():
                # Queue lengths
                queue_length = len(station.queue)
                self.stats.record_queue_length(
                    station=name, length=queue_length, time=current_time
                )

                # Resource utilization
                if hasattr(station, "resource"):
                    util = station.resource.count / station.resource.capacity
                    self.stats.record_utilization(name, util, current_time)
                elif name == "checkin":
                    # Special handling for check-in with multiple resources
                    total_used = station.iberia_desks.count + station.other_desks.count
                    total_capacity = (
                        station.iberia_desks.capacity + station.other_desks.capacity
                    )
                    util = total_used / total_capacity
                    self.stats.record_utilization(name, util, current_time)

            yield self.env.timeout(5)  # Monitor every 5 minutes
