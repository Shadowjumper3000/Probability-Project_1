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
                    station=name,
                    length=queue_length,
                    time=current_time
                )

                # Calculate utilization based on station type
                if name == "checkin":
                    total_used = station.iberia_desks.count + station.other_desks.count
                    total_capacity = station.iberia_desks.capacity + station.other_desks.capacity
                    util = total_used / total_capacity if total_capacity > 0 else 0

                elif name == "security":
                    util = station.lanes.count / station.lanes.capacity

                elif name == "passport":
                    total_used = station.booths.count + station.egates.count
                    total_capacity = station.booths.capacity + station.egates.capacity
                    util = total_used / total_capacity if total_capacity > 0 else 0

                elif name == "boarding":
                    # Calculate total utilization across all flight agents
                    if station.flight_agents:
                        total_used = sum(agent.count for agent in station.flight_agents.values())
                        total_capacity = sum(agent.capacity for agent in station.flight_agents.values())
                        util = total_used / total_capacity if total_capacity > 0 else 0
                    else:
                        util = 0.0

                # Record utilization
                self.stats.record_utilization(name, util, current_time)

            yield self.env.timeout(5)  # Monitor every 5 minutes
