from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from ..config import (
    AIRCRAFT_MIX,
    FLIGHTS_PER_DAY,
    MEAN_FLIGHTS_PER_HOUR,
    BASE_INTERARRIVAL_MINUTES,
    INTERARRIVAL_STD_DEV,
    HOURLY_PATTERNS,
    SCHENGEN_DESTINATIONS,
    RANDOM_SEED,
)


def get_hourly_pattern():
    """Generate 24-hour pattern based on config parameters"""
    hourly_pattern = []

    # Use MEAN_FLIGHTS_PER_HOUR as the baseline for hourly calculations
    # Each hour will be scaled by the corresponding pattern factor

    for hour in range(24):
        if hour in HOURLY_PATTERNS:
            pattern_factor = HOURLY_PATTERNS[hour]
            # Scale mean flights per hour by the hourly pattern factor
            hourly_pattern.append(MEAN_FLIGHTS_PER_HOUR * pattern_factor)
        else:
            # Default to average if hour not specified (should not happen)
            hourly_pattern.append(MEAN_FLIGHTS_PER_HOUR)

    return hourly_pattern


def generate_synthetic_flights():
    """Generate synthetic flight data based on config parameters"""
    # Create destination dictionary with normalized probabilities
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

    # Define airline distribution
    AIRLINES = {
        "Iberia": 0.45,  # Primary carrier
        "Air Europa": 0.20,  # Secondary Spanish carrier
        "Vueling": 0.15,  # Spanish low-cost carrier
        "Ryanair": 0.08,  # European low-cost carrier
        "Lufthansa": 0.05,  # European major carrier
        "Air France": 0.04,  # European major carrier
        "British Airways": 0.03,  # European major carrier
    }

    # Get hourly flight distribution based on MEAN_FLIGHTS_PER_HOUR and patterns
    hourly_pattern = get_hourly_pattern()

    # Calculate total expected flights from hourly pattern
    expected_total = sum(hourly_pattern)

    # Apply normal distribution to create variance around the target FLIGHTS_PER_DAY
    # The standard deviation is 5% of the target
    target_flights = int(np.random.normal(FLIGHTS_PER_DAY, FLIGHTS_PER_DAY * 0.05))

    print(
        f"\nTarget flights per day: {target_flights} (based on normal distribution around {FLIGHTS_PER_DAY})"
    )
    print(f"Expected flights from hourly pattern: {expected_total:.1f}")

    # Calculate scaling factor to adjust hourly pattern to match target flights
    scaling_factor = target_flights / expected_total
    adjusted_hourly_pattern = [h * scaling_factor for h in hourly_pattern]

    print(f"Scaling hourly pattern by factor: {scaling_factor:.3f}")

    # Generate hourly flight counts with randomness (normal distribution around each hour's target)
    # This creates natural variance while maintaining the overall pattern
    hourly_flights = {}
    for hour in range(24):
        # Use normal distribution around the target for each hour
        # With standard deviation of 10% of the target
        mean_flights = adjusted_hourly_pattern[hour]
        std_dev = max(0.5, mean_flights * 0.1)  # Minimum std_dev of 0.5

        # Generate random count with normal distribution and round to nearest integer
        # Ensure at least 0 flights
        flight_count = max(0, round(np.random.normal(mean_flights, std_dev)))
        hourly_flights[hour] = flight_count

    # Final adjustment to exactly match target_flights
    current_total = sum(hourly_flights.values())

    if current_total != target_flights:
        # Distribute the difference proportionally
        difference = target_flights - current_total

        # Sort hours by volume for adjustment, prioritizing busier hours
        hours_by_volume = sorted(
            hourly_flights.keys(),
            key=lambda h: hourly_flights[h],
            reverse=(difference > 0),
        )

        # Apply adjustments
        for hour in hours_by_volume:
            if difference == 0:
                break

            # Don't reduce hours with 0 flights
            if hourly_flights[hour] == 0 and difference < 0:
                continue

            adjustment = 1 if difference > 0 else -1
            hourly_flights[hour] += adjustment
            difference -= adjustment

    # Verify final total matches target
    final_total = sum(hourly_flights.values())
    print(
        f"Final adjusted hourly flights total: {final_total} (target: {target_flights})"
    )

    # Report hourly distribution
    print("\nHourly flight distribution:")
    for hour in range(24):
        pattern_factor = HOURLY_PATTERNS.get(hour, 1.0)
        print(
            f"Hour {hour}: {hourly_flights[hour]} flights (pattern factor: {pattern_factor:.2f}x)"
        )

    # Generate flights
    flights = []
    flight_counters = {
        airline: 1000 + i * 1000 for i, airline in enumerate(AIRLINES.keys())
    }
    airline_codes = {
        "Iberia": "IB",
        "Air Europa": "UX",
        "Vueling": "VY",
        "Ryanair": "FR",
        "Lufthansa": "LH",
        "Air France": "AF",
        "British Airways": "BA",
    }

    current_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Generate flights for each hour
    for hour in range(24):
        num_flights = hourly_flights[hour]
        if num_flights <= 0:
            continue

        hour_start_time = current_time.replace(
            hour=hour, minute=0, second=0, microsecond=0
        )

        # Distribute flights evenly within the hour with some randomness
        for i in range(num_flights):
            # Evenly space flights within the hour
            minute_spacing = 60 / (num_flights + 1)
            minute = (i + 1) * minute_spacing

            # Add some randomness but keep within hour
            minute_jitter = np.random.normal(0, 3)  # 3-minute standard deviation
            minute = min(max(1, minute + minute_jitter), 59)

            flight_time = hour_start_time.replace(minute=int(minute))

            # Select airline based on distribution
            airline = np.random.choice(list(AIRLINES.keys()), p=list(AIRLINES.values()))
            flight_number = f"{airline_codes[airline]}{flight_counters[airline]}"
            flight_counters[airline] += 1

            # Select aircraft based on mix from config
            aircraft = np.random.choice(
                list(AIRCRAFT_MIX.keys()), p=list(AIRCRAFT_MIX.values())
            )

            # Select destination based on probabilities
            destination = np.random.choice(
                list(DESTINATIONS.keys()), p=list(DESTINATIONS.values())
            )
            destination_name = f"{destination} Airport ({destination})"

            flight = {
                "scheduled_time": flight_time,
                "flight": flight_number,
                "destination": destination_name,
                "aircraft": aircraft,
                "airline": airline,
            }
            flights.append(flight)

    # Create DataFrame and sort by time
    df = pd.DataFrame(flights)
    df = df.sort_values("scheduled_time")

    print(f"\nGenerated exactly {len(df)} flights (target: {target_flights})")

    # Analyze hourly distribution in the final data
    print("\nActual hourly distribution in generated data:")
    hourly_counts = df.groupby(df["scheduled_time"].dt.hour).size()
    print(hourly_counts)

    # Calculate some statistics about the distribution
    hourly_std = hourly_counts.std()
    hourly_mean = hourly_counts.mean()
    hourly_cv = hourly_std / hourly_mean if hourly_mean > 0 else 0

    print(f"\nDistribution statistics:")
    print(f"Mean flights per hour: {hourly_mean:.2f}")
    print(f"Standard deviation: {hourly_std:.2f}")
    print(f"Coefficient of variation: {hourly_cv:.2f}")
    print(f"Min flights per hour: {hourly_counts.min()}")
    print(f"Max flights per hour: {hourly_counts.max()}")

    return df


def load_flight_data():
    """Load synthetic flight data for simulation"""
    try:
        return generate_synthetic_flights()
    except Exception as e:
        print(f"Error generating flight data: {str(e)}")
        return None
