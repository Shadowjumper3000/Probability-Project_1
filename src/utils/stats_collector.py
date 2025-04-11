import numpy as np


class StatsCollector:
    """Collects and aggregates simulation statistics"""

    def __init__(self):
        self.stats = {
            "total_passengers": 0,
            "processed_passengers": 0,
            "priority_passengers": 0,
            "total_times": [],
            "priority_times": [],
            "regular_times": [],
            "wait_times": {
                "checkin": [],
                "security": [],
                "passport": [],
                "boarding": [],
                "priority_boarding": [],
                "regular_boarding": [],
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
            # Added overbooking statistics
            "flights": {
                "total": 0,
                "overbooked": 0,
                "overbooking_factors": [],
                "passenger_counts": [],  # Track number of passengers per flight
            },
        }

    def record_flight(self, flight):
        """Record flight statistics including overbooking"""
        # For debugging
        print(
            f"Recording flight: {flight.flight_number}, passengers: {len(flight.passengers)}"
        )

        self.stats["flights"]["total"] += 1

        # Track passenger counts per flight for distribution analysis
        if hasattr(flight, "passengers"):
            passenger_count = len(flight.passengers)
            self.stats["flights"]["passenger_counts"].append(passenger_count)
        else:
            print(
                f"WARNING: Flight {flight.flight_number} has no 'passengers' attribute"
            )

        if flight.is_overbooked:
            self.stats["flights"]["overbooked"] += 1
            self.stats["flights"]["overbooking_factors"].append(
                flight.overbooking_factor
            )

    def record_passenger(self, passenger):
        """Record passenger statistics"""
        self.stats["processed_passengers"] += 1

        # Track priority passengers
        if passenger.is_priority:
            self.stats["priority_passengers"] += 1

        # Record total time
        if passenger.total_time > 0:
            self.stats["total_times"].append(passenger.total_time)

            # Track times by passenger type
            if passenger.is_priority:
                self.stats["priority_times"].append(passenger.total_time)
            else:
                self.stats["regular_times"].append(passenger.total_time)

        # Record wait times
        if not passenger.online_checkin:
            self.stats["wait_times"]["checkin"].append(passenger.checkin_wait)

        self.stats["wait_times"]["security"].append(passenger.security_wait)

        if not passenger.flight.is_schengen:
            self.stats["wait_times"]["passport"].append(passenger.passport_wait)

        # Record boarding wait times by passenger type
        self.stats["wait_times"]["boarding"].append(passenger.boarding_wait)
        if passenger.is_priority:
            self.stats["wait_times"]["priority_boarding"].append(
                passenger.boarding_wait
            )
        else:
            self.stats["wait_times"]["regular_boarding"].append(passenger.boarding_wait)

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
            "priority_passengers": self.stats["priority_passengers"],
            "priority_percentage": (
                (
                    self.stats["priority_passengers"]
                    / self.stats["processed_passengers"]
                    * 100
                )
                if self.stats["processed_passengers"] > 0
                else 0
            ),
            "avg_total_time": (
                np.mean(self.stats["total_times"]) if self.stats["total_times"] else 0
            ),
            "max_total_time": (
                max(self.stats["total_times"]) if self.stats["total_times"] else 0
            ),
            "min_total_time": (  # Add minimum time
                min(self.stats["total_times"]) if self.stats["total_times"] else 0
            ),
            "avg_priority_time": (
                np.mean(self.stats["priority_times"])
                if self.stats["priority_times"]
                else 0
            ),
            "avg_regular_time": (
                np.mean(self.stats["regular_times"])
                if self.stats["regular_times"]
                else 0
            ),
            # Add overbooking statistics
            "total_flights": self.stats["flights"]["total"],
            "overbooked_flights": self.stats["flights"]["overbooked"],
            "overbooked_percentage": (
                (
                    self.stats["flights"]["overbooked"]
                    / self.stats["flights"]["total"]
                    * 100
                )
                if self.stats["flights"]["total"] > 0
                else 0
            ),
            "avg_overbooking_factor": (
                np.mean(self.stats["flights"]["overbooking_factors"])
                if self.stats["flights"]["overbooking_factors"]
                else 1.0
            ),
            # Add passenger distribution statistics
            "passenger_distribution": {
                "avg_per_flight": (
                    np.mean(self.stats["flights"]["passenger_counts"])
                    if self.stats["flights"]["passenger_counts"]
                    else 0
                ),
                "min_passengers": (
                    min(self.stats["flights"]["passenger_counts"])
                    if self.stats["flights"]["passenger_counts"]
                    else 0
                ),
                "max_passengers": (
                    max(self.stats["flights"]["passenger_counts"])
                    if self.stats["flights"]["passenger_counts"]
                    else 0
                ),
                "std_dev": (
                    np.std(self.stats["flights"]["passenger_counts"])
                    if self.stats["flights"]["passenger_counts"]
                    else 0
                ),
            },
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

        # Add priority boarding statistics
        priority_waits = self.stats["wait_times"]["priority_boarding"]
        regular_waits = self.stats["wait_times"]["regular_boarding"]

        summary["priority_boarding_avg_wait"] = (
            np.mean(priority_waits) if priority_waits else 0
        )
        summary["regular_boarding_avg_wait"] = (
            np.mean(regular_waits) if regular_waits else 0
        )
        summary["boarding_time_savings"] = (
            summary["regular_boarding_avg_wait"] - summary["priority_boarding_avg_wait"]
            if priority_waits and regular_waits
            else 0
        )

        summary["timestamps"] = self.stats["timestamps"]
        summary["queue_lengths"] = self.stats["queue_lengths"]

        return summary
