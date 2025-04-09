from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from ..config import (
    AIRCRAFT_MIX,
    FLIGHTS_PER_DAY,
    BASE_INTERARRIVAL_MINUTES,
    INTERARRIVAL_STD_DEV,
    HOURLY_PATTERNS,
    SCHENGEN_DESTINATIONS,
    RANDOM_SEED,
)


def get_hourly_pattern():
    """Generate 24-hour pattern based on config parameters"""
    hourly_pattern = []
    current_factor = HOURLY_PATTERNS[0]  # Start with midnight factor

    # Calculate base flights per hour from FLIGHTS_PER_DAY
    base_flights_per_hour = FLIGHTS_PER_DAY / 24

    for hour in range(24):
        if hour in HOURLY_PATTERNS:
            current_factor = HOURLY_PATTERNS[hour]
        hourly_pattern.append(base_flights_per_hour * current_factor)

    return hourly_pattern


def generate_synthetic_flights():
    """Generate synthetic flight data based on config parameters"""
    # Create a combined destination dict with 70% Schengen, 30% non-Schengen
    # Use SCHENGEN_DESTINATIONS from config instead of hardcoded values
    DESTINATIONS = {
        # Schengen (70%)
        **SCHENGEN_DESTINATIONS,
        # Non-Schengen (30%)
        "LHR": 0.10,  # London
        "JFK": 0.10,  # New York
        "DXB": 0.10,  # Dubai
    }

    # Normalize destination probabilities
    total = sum(DESTINATIONS.values())
    DESTINATIONS = {k: v / total for k, v in DESTINATIONS.items()}

    # Validate probability sum
    if not np.isclose(sum(DESTINATIONS.values()), 1.0):
        raise ValueError("Destination probabilities must sum to 1")

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

    # Calculate the total expected flights for validation
    total_expected_flights = sum(max(1, int(flights)) for flights in hourly_pattern)
    print(
        f"Expected to generate approximately {total_expected_flights} flights based on FLIGHTS_PER_DAY={FLIGHTS_PER_DAY}"
    )

    # Calculate the average flights per hour for logging
    avg_flights_per_hour = FLIGHTS_PER_DAY / 24
    print(f"Average flights per hour: {avg_flights_per_hour:.2f}")

    for hour in range(24):
        expected_flights = max(1, int(hourly_pattern[hour]))
        print(
            f"Hour {hour}: Planning {expected_flights} flights (pattern factor: {hourly_pattern[hour]/avg_flights_per_hour:.2f}x)"
        )

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

            # Select destination based on probabilities
            destination = np.random.choice(
                list(DESTINATIONS.keys()), p=list(DESTINATIONS.values())
            )

            flight = {
                "scheduled_time": current_time,
                "flight": f"IB{flight_counter}",
                "destination": destination,
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
