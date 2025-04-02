def print_statistics(results):
    """Print summary statistics with error handling"""
    print("=== Madrid T4 Airport Simulation Results ===")

    if not results:
        print("No results available - simulation failed")
        return

    print("\nPassenger Statistics:")
    print(f"Total Passengers: {results['total_passengers']}")
    print(f"Processed Passengers: {results['processed_passengers']}")

    if results["processed_passengers"] > 0:
        print("\nProcessing Times (minutes):")
        print(f"Average Total Time: {results['avg_total_time']:.1f}")
        print(f"Maximum Total Time: {results['max_total_time']:.1f}")

        for station in ["checkin", "security", "passport", "boarding"]:
            if f"{station}_avg_wait" in results:
                print(f"\n{station.title()} Station:")
                print(f"Average Wait: {results[f'{station}_avg_wait']:.1f}")
                print(f"Maximum Wait: {results[f'{station}_max_wait']:.1f}")
                print(f"Average Queue: {results[f'{station}_queue_length']:.1f}")
