import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.style.use("default")
sns.set(style="whitegrid")


def plot_queue_lengths(results):
    """Plot queue lengths over time"""
    try:
        # Generate timestamps for x-axis
        x = np.arange(0, 24 * 60, 5)  # 5-minute intervals over 24 hours

        plt.figure(figsize=(12, 6))
        for station in ["checkin", "security", "passport", "boarding"]:
            queue_data = results["queue_lengths"][station]
            if queue_data:  # Only plot if we have data
                plt.plot(x[: len(queue_data)], queue_data, label=station.capitalize())

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
        # Generate timestamps for x-axis
        x = np.arange(0, 24 * 60, 5)  # 5-minute intervals over 24 hours

        plt.figure(figsize=(12, 6))
        for station in ["checkin", "security", "passport", "boarding"]:
            util_data = results.get(f"{station}_utilization", [])
            if util_data:  # Only plot if we have data
                plt.plot(x[: len(util_data)], util_data, label=station.capitalize())

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
