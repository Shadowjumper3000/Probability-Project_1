def print_statistics(results):
    """Print summary statistics with error handling"""
    print("=== Madrid T4 Airport Simulation Results ===")

    if not results:
        print("No results available - simulation failed")
        return

    print("\nPassenger Statistics:")
    print(f"Total Passengers: {results['total_passengers']}")
    print(f"Processed Passengers: {results['processed_passengers']}")
    if "priority_passengers" in results:
        print(
            f"Priority Passengers: {results['priority_passengers']} ({results['priority_percentage']:.1f}%)"
        )

    # Print overbooking statistics
    if "overbooked_flights" in results:
        print("\nFlight Statistics:")
        print(f"Total Flights: {results['total_flights']}")
        print(
            f"Overbooked Flights: {results['overbooked_flights']} ({results['overbooked_percentage']:.1f}%)"
        )
        print(f"Average Overbooking Factor: {results['avg_overbooking_factor']:.2f}x")

    if results["processed_passengers"] > 0:
        print("\nProcessing Times (minutes):")
        print(f"Average Total Time: {results['avg_total_time']:.1f}")
        print(f"Maximum Total Time: {results['max_total_time']:.1f}")
        print(
            f"Minimum Total Time: {results['min_total_time']:.1f}"
        )  # Add minimum time

        if "avg_priority_time" in results and "avg_regular_time" in results:
            print(
                f"Average Priority Passenger Time: {results['avg_priority_time']:.1f}"
            )
            print(f"Average Regular Passenger Time: {results['avg_regular_time']:.1f}")

        for station in ["checkin", "security", "passport", "boarding"]:
            if f"{station}_avg_wait" in results:
                print(f"\n{station.title()} Station:")
                print(f"Average Wait: {results[f'{station}_avg_wait']:.1f}")
                print(f"Maximum Wait: {results[f'{station}_max_wait']:.1f}")
                print(f"Average Queue: {results[f'{station}_queue_length']:.1f}")

        # Add priority boarding statistics
        if (
            "priority_boarding_avg_wait" in results
            and "regular_boarding_avg_wait" in results
        ):
            print("\nPriority vs Regular Boarding:")
            print(
                f"Priority Boarding Wait: {results['priority_boarding_avg_wait']:.1f}"
            )
            print(f"Regular Boarding Wait: {results['regular_boarding_avg_wait']:.1f}")
            print(f"Time Savings for Priority: {results['boarding_time_savings']:.1f}")
