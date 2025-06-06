import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.style.use("default")
sns.set(style="whitegrid")


def plot_queue_lengths(results):
    """Plot queue lengths over time"""
    try:
        plt.figure(figsize=(12, 6))
        for station in ["checkin", "security", "passport", "boarding"]:
            queue_data = results["queue_lengths"][station]
            if queue_data:  # Only plot if we have data
                # Apply ceiling to avoid extreme outliers in visualization
                capped_data = [min(q, 1000) for q in queue_data]

                # Create x-axis values that match the length of queue_data
                x = np.linspace(0, 24 * 60, len(capped_data))
                plt.plot(x, capped_data, label=station.capitalize())

                # Print statistics about queue data
                max_queue = max(capped_data) if capped_data else 0
                avg_queue = np.mean(capped_data) if capped_data else 0
                print(
                    f"{station.capitalize()} queue - Max: {max_queue:.1f}, Average: {avg_queue:.1f}"
                )

        plt.xlabel("Simulation Time (minutes)")
        plt.ylabel("Queue Length (passengers)")
        plt.title("Queue Lengths Over Time")
        plt.legend()
        plt.grid(True)
        plt.savefig("results/plots/queue_lengths.png")
        plt.close()

    except Exception as e:
        print(f"Error plotting queue lengths: {str(e)}")


def plot_resource_utilization(results):
    """Plot resource utilization over time"""
    try:
        plt.figure(figsize=(12, 6))
        for station in ["checkin", "security", "passport", "boarding"]:
            util_data = results.get(f"{station}_utilization", [])
            if util_data:  # Only plot if we have data
                # Create x-axis values that match the length of util_data
                x = np.linspace(0, 24 * 60, len(util_data))
                plt.plot(x, util_data, label=station.capitalize())

        plt.xlabel("Simulation Time (minutes)")
        plt.ylabel("Resource Utilization")
        plt.title("Resource Utilization Over Time")
        plt.legend()
        plt.grid(True)
        plt.savefig("results/plots/resource_utilization.png")
        plt.close()

    except Exception as e:
        print(f"Error plotting resource utilization: {str(e)}")


def plot_passenger_times(simulation):
    """Plot passenger processing time distributions"""
    try:
        stats = simulation.stats.stats

        plt.figure(figsize=(12, 6))
        stations = ["checkin", "security", "passport", "boarding"]
        wait_times = [stats["wait_times"][s] for s in stations]

        # Only plot stations with data
        labels = []
        data = []
        for station, times in zip(stations, wait_times):
            if times:
                labels.append(station.capitalize())
                data.append(times)

        if data:  # Only create plot if we have data
            plt.boxplot(data, labels=labels)
            plt.ylabel("Processing Time (minutes)")
            plt.title("Passenger Processing Times by Station")
            plt.grid(True)
            plt.savefig("results/plots/passenger_times.png")

        plt.close()

    except Exception as e:
        print(f"Error plotting passenger times: {str(e)}")


def plot_average_times_breakdown(results):
    """Plot breakdown of average time spent in each stage"""
    try:
        stations = ["checkin", "security", "passport", "boarding"]
        avg_times = [results[f"{s}_avg_wait"] for s in stations]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(stations, avg_times)

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}m",
                ha="center",
                va="bottom",
            )

        plt.title("Average Time Spent per Station")
        plt.xlabel("Processing Station")
        plt.ylabel("Average Time (minutes)")
        plt.grid(True, alpha=0.3)
        plt.savefig("results/plots/average_times_breakdown.png")
        plt.close()

    except Exception as e:
        print(f"Error plotting average times breakdown: {str(e)}")


def plot_utilization_heatmap(results):
    """Plot resource utilization heatmap"""
    try:
        stations = ["checkin", "security", "passport", "boarding"]
        times = np.arange(0, 24)  # Hours
        data = np.zeros((len(stations), 24))

        for i, station in enumerate(stations):
            util_data = results[f"{station}_utilization"]
            queue_data = results["queue_lengths"][station]

            # Ensure we have data to process
            if len(util_data) >= 288:  # Full day of 5-minute samples
                # Convert 5-min data to hourly averages - include queue data in calculation
                for hour in range(24):
                    start_idx = hour * 12
                    end_idx = (hour + 1) * 12

                    # Get samples for this hour
                    hour_util = util_data[start_idx:end_idx]
                    hour_queue = (
                        queue_data[start_idx:end_idx]
                        if len(queue_data) >= end_idx
                        else []
                    )

                    # Calculate average utilization
                    data[i, hour] = np.mean(hour_util)

                    # Adjustment: Log when large queues exist with low utilization
                    if len(hour_queue) > 0:
                        avg_queue = np.mean(hour_queue)
                        if avg_queue > 50 and data[i, hour] < 0.8:
                            print(
                                f"Warning: Large queue ({avg_queue:.1f}) with low utilization ({data[i, hour]:.2f}) at hour {hour} for {station}"
                            )

        plt.figure(figsize=(15, 6))
        sns.heatmap(
            data,
            xticklabels=times,
            yticklabels=stations,
            cmap="YlOrRd",
            vmin=0,
            vmax=1,
            cbar_kws={"label": "Utilization Rate"},
            annot=True,
            fmt=".2f",
        )

        plt.title("Resource Utilization Throughout Day")
        plt.xlabel("Hour of Day")
        plt.ylabel("Station")
        plt.savefig("results/plots/utilization_heatmap.png")
        plt.close()

    except Exception as e:
        print(f"Error plotting utilization heatmap: {str(e)}")
