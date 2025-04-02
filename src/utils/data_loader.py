from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from ..config import (
    AIRCRAFT_MIX,
    BASE_FLIGHTS_PER_HOUR,
    BASE_INTERARRIVAL_MINUTES,
    INTERARRIVAL_STD_DEV,
    HOURLY_PATTERNS,
)


def get_hourly_pattern():
    """Generate 24-hour pattern based on config parameters"""
    hourly_pattern = []
    current_factor = HOURLY_PATTERNS[0]  # Start with midnight factor

    for hour in range(24):
        if hour in HOURLY_PATTERNS:
            current_factor = HOURLY_PATTERNS[hour]
        hourly_pattern.append(BASE_FLIGHTS_PER_HOUR * current_factor)

    return hourly_pattern


def generate_synthetic_flights():
    """Generate synthetic flight data based on config parameters"""
    # Validate probability sums
    aircraft_sum = sum(AIRCRAFT_MIX.values())
    print(f"\nAircraft mix probabilities sum: {aircraft_sum}")
    print("Aircraft probabilities:")
    for aircraft, prob in AIRCRAFT_MIX.items():
        print(f"{aircraft}: {prob}")

    hourly_pattern = get_hourly_pattern()
    flights = []
    current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    flight_counter = 1000

    for hour in range(24):
        expected_flights = max(1, int(hourly_pattern[hour]))

        for _ in range(expected_flights):
            minutes_delta = max(
                0, np.random.normal(BASE_INTERARRIVAL_MINUTES, INTERARRIVAL_STD_DEV)
            )

            current_time += timedelta(minutes=minutes_delta)
            if current_time.hour > hour:
                break

            # Select aircraft based on mix from config
            aircraft = np.random.choice(
                list(AIRCRAFT_MIX.keys()), p=list(AIRCRAFT_MIX.values())
            )

            flight = {
                "scheduled_time": current_time,
                "flight": f"IB{flight_counter}",  # Changed from flight_number to flight
                "destination": "BCN",  # Example Schengen destination
                "aircraft": aircraft,
                "airline": "Iberia" if np.random.random() < 0.8 else "Air Europa",
            }
            flights.append(flight)
            flight_counter += 1

    df = pd.DataFrame(flights)
    df = df.sort_values("scheduled_time")

    print(f"\nGenerated {len(df)} synthetic flights")
    print("\nHourly distribution:")
    print(df.groupby(df["scheduled_time"].dt.hour).size())

    return df


def load_flight_data():
    """Load synthetic flight data for simulation"""
    try:
        return generate_synthetic_flights()
    except Exception as e:
        print(f"Error generating flight data: {str(e)}")
        return None
