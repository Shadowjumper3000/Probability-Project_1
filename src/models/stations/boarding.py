import simpy
from ...config import BOARDING_AGENTS, BOARDING_SERVICE_TIME


class Boarding:
    """Flight boarding with dedicated agents per flight"""

    def __init__(self, env):
        self.env = env
        self.flight_agents = {}  # Agents per flight
        self.queue = []

    def get_flight_agents(self, flight):
        """Get or create dedicated agents for a flight"""
        if flight.flight_number not in self.flight_agents:
            # Create new agents for this flight
            self.flight_agents[flight.flight_number] = simpy.Resource(
                self.env, capacity=BOARDING_AGENTS  # Now represents agents per flight
            )
        return self.flight_agents[flight.flight_number]

    def process(self, passenger):
        """Process passenger boarding"""
        entry_time = self.env.now
        self.queue.append(entry_time)

        # Get agents dedicated to this flight
        agents = self.get_flight_agents(passenger.flight)

        with agents.request() as agent:
            yield agent
            self.queue.remove(entry_time)

            # Process boarding
            yield self.env.timeout(BOARDING_SERVICE_TIME)

            # Record statistics
            passenger.boarding_wait = self.env.now - entry_time
            passenger.boarding_complete = self.env.now

        # Cleanup completed flights
        if all(p.boarding_complete for p in passenger.flight.passengers):
            del self.flight_agents[passenger.flight.flight_number]
