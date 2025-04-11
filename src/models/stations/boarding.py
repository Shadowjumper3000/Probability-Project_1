import simpy
import numpy as np
from ...config import BOARDING_AGENTS, BOARDING_SERVICE_TIME


class Boarding:
    """Flight boarding with dedicated agents per flight"""

    def __init__(self, env):
        self.env = env
        self.flight_agents = {}  # Agents per flight
        self.priority_queues = {}  # Priority queues per flight
        self.regular_queues = {}  # Regular queues per flight

    def get_flight_agents(self, flight):
        """Get or create dedicated agents for a flight"""
        if not flight or not hasattr(flight, "flight_number"):
            # Handle invalid flight object
            print("Warning: Invalid flight object passed to boarding")
            # Create a dummy resource for error handling
            return simpy.PriorityResource(self.env, capacity=BOARDING_AGENTS)

        if flight.flight_number not in self.flight_agents:
            # Create new agents for this flight
            self.flight_agents[flight.flight_number] = simpy.PriorityResource(
                self.env, capacity=BOARDING_AGENTS  # Now uses PriorityResource
            )
            # Initialize queue tracking for this flight
            self.priority_queues[flight.flight_number] = []
            self.regular_queues[flight.flight_number] = []
        return self.flight_agents[flight.flight_number]

    @property
    def queue(self):
        """Return combined queue for monitoring purposes"""
        combined = []
        for flight_num in self.flight_agents:
            combined.extend(self.priority_queues.get(flight_num, []))
            combined.extend(self.regular_queues.get(flight_num, []))
        return combined

    def process(self, passenger):
        """Process passenger boarding"""
        entry_time = self.env.now

        # Safety check for passenger and flight
        if not passenger or not hasattr(passenger, "flight") or not passenger.flight:
            print(f"Warning: Invalid passenger or flight reference at boarding")
            # Mark passenger as boarded to avoid simulation errors
            passenger.boarding_wait = 0
            passenger.boarding_complete = self.env.now
            passenger.is_boarded = True
            return

        try:
            # Get agents dedicated to this flight
            agents = self.get_flight_agents(passenger.flight)
            flight_num = getattr(passenger.flight, "flight_number", "unknown")

            # Add to appropriate queue based on priority status
            if hasattr(passenger, "is_priority") and passenger.is_priority:
                if flight_num in self.priority_queues:
                    self.priority_queues[flight_num].append(entry_time)
                # Use priority 1 (higher priority) for priority passengers
                priority_level = 1
            else:
                if flight_num in self.regular_queues:
                    self.regular_queues[flight_num].append(entry_time)
                # Use priority 2 (lower priority) for regular passengers
                priority_level = 2

            with agents.request(priority=priority_level) as agent:
                yield agent

                # Remove from appropriate queue
                if hasattr(passenger, "is_priority") and passenger.is_priority:
                    if (
                        flight_num in self.priority_queues
                        and entry_time in self.priority_queues[flight_num]
                    ):
                        self.priority_queues[flight_num].remove(entry_time)
                else:
                    if (
                        flight_num in self.regular_queues
                        and entry_time in self.regular_queues[flight_num]
                    ):
                        self.regular_queues[flight_num].remove(entry_time)

                # Process boarding
                boarding_time = max(
                    0.1,
                    np.random.normal(
                        BOARDING_SERVICE_TIME, BOARDING_SERVICE_TIME * 0.2
                    ),
                )
                yield self.env.timeout(boarding_time)

                # Record statistics
                passenger.boarding_wait = self.env.now - entry_time
                passenger.boarding_complete = self.env.now
                passenger.is_boarded = True

            # Cleanup completed flights - only if we can safely determine all passengers are boarded
            self.try_cleanup_flight(passenger.flight)

        except Exception as e:
            print(f"Error in boarding process: {str(e)}")
            # Ensure passenger is marked as processed even on error
            passenger.boarding_wait = self.env.now - entry_time
            passenger.boarding_complete = self.env.now
            passenger.is_boarded = True

    def try_cleanup_flight(self, flight):
        """Safely attempt to clean up flight resources"""
        try:
            if (
                not flight
                or not hasattr(flight, "flight_number")
                or not hasattr(flight, "passengers")
            ):
                return

            flight_num = flight.flight_number
            if flight_num not in self.flight_agents:
                return

            # Check if all passengers are boarded
            all_boarded = True
            for p in flight.passengers:
                if not hasattr(p, "is_boarded") or not p.is_boarded:
                    all_boarded = False
                    break

            if all_boarded and flight_num in self.flight_agents:
                del self.flight_agents[flight_num]
                if flight_num in self.priority_queues:
                    del self.priority_queues[flight_num]
                if flight_num in self.regular_queues:
                    del self.regular_queues[flight_num]
        except Exception as e:
            print(
                f"Error cleaning up flight {getattr(flight, 'flight_number', 'unknown')}: {str(e)}"
            )
