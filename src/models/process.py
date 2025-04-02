from datetime import timedelta


class PassengerProcess:
    """Handles the movement of passengers through airport stations"""

    def __init__(self, env, stations):
        self.env = env
        self.stations = stations

    def process_passenger(self, passenger):
        """Process a passenger through all departure stations"""
        # Set arrival time
        passenger.arrival_time = self.env.now

        # Check-in (if needed)
        if not passenger.online_checkin:
            yield from self.stations["checkin"].process(passenger)

        # Security screening
        yield from self.stations["security"].process(passenger)

        # Passport control (if not Schengen flight)
        if not passenger.flight.is_schengen:
            yield from self.stations["passport"].process(passenger)

        # Boarding
        yield from self.stations["boarding"].process(passenger)
