import numpy as np


class StatsCollector:
    """Collects and aggregates simulation statistics"""

    def __init__(self):
        self.stats = {
            "total_passengers": 0,
            "processed_passengers": 0,
            "total_times": [],
            "wait_times": {
                "checkin": [],
                "security": [],
                "passport": [],
                "boarding": [],
            },
            "queue_lengths": {
                "checkin": [],
                "security": [],
                "passport": [],
                "boarding": [],
            },
            "utilization": {
                "checkin": [],
                "security": [],
                "passport": [],
                "boarding": [],
            },
            "timestamps": [],
        }

    def record_passenger(self, passenger):
        """Record passenger statistics"""
        self.stats["processed_passengers"] += 1

        # Record total time
        if passenger.total_time > 0:
            self.stats["total_times"].append(passenger.total_time)

        # Record wait times
        if not passenger.online_checkin:
            self.stats["wait_times"]["checkin"].append(passenger.checkin_wait)

        self.stats["wait_times"]["security"].append(passenger.security_wait)

        if not passenger.flight.is_schengen:
            self.stats["wait_times"]["passport"].append(passenger.passport_wait)

        self.stats["wait_times"]["boarding"].append(passenger.boarding_wait)

    def record_queue_length(self, station, length, time):
        """Record queue length for a station"""
        self.stats["queue_lengths"][station].append(length)
        if time not in self.stats["timestamps"]:
            self.stats["timestamps"].append(time)

    def record_utilization(self, station, utilization, time):
        """Record resource utilization for a station"""
        self.stats["utilization"][station].append(utilization)
        if time not in self.stats["timestamps"]:
            self.stats["timestamps"].append(time)

    def get_summary(self):
        """Get statistics summary"""
        summary = {
            "total_passengers": self.stats["total_passengers"],
            "processed_passengers": self.stats["processed_passengers"],
            "avg_total_time": (
                np.mean(self.stats["total_times"]) if self.stats["total_times"] else 0
            ),
            "max_total_time": (
                max(self.stats["total_times"]) if self.stats["total_times"] else 0
            ),
        }

        # Add station-specific statistics
        for station in ["checkin", "security", "passport", "boarding"]:
            # Wait times
            wait_times = self.stats["wait_times"][station]
            summary[f"{station}_avg_wait"] = np.mean(wait_times) if wait_times else 0
            summary[f"{station}_max_wait"] = max(wait_times) if wait_times else 0

            # Queue lengths
            queue_lengths = self.stats["queue_lengths"][station]
            summary[f"{station}_queue_length"] = (
                np.mean(queue_lengths) if queue_lengths else 0
            )
            summary[f"{station}_max_queue"] = max(queue_lengths) if queue_lengths else 0

            # Utilization
            summary[f"{station}_utilization"] = self.stats["utilization"][station]

        summary["timestamps"] = self.stats["timestamps"]
        summary["queue_lengths"] = self.stats["queue_lengths"]

        return summary
