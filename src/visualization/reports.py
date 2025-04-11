from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io
from ..config import FLIGHT_LOAD_FACTOR, OVERBOOKING_CHANCE, MAX_OVERBOOKING_FACTOR


def create_table_style():
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )


def create_flight_distribution_chart(df):
    """Create flight distribution chart with moving average"""
    plt.figure(figsize=(10, 6))

    # Get hourly counts directly from DataFrame
    hourly_counts = (
        df["scheduled_time"].apply(lambda x: x.hour).value_counts().sort_index()
    )
    hours = range(24)
    flights_per_hour = [hourly_counts.get(hour, 0) for hour in hours]

    # Create bar chart
    bars = plt.bar(hours, flights_per_hour, color="skyblue", alpha=0.7, label="Flights")

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
            )

    # Calculate and plot 3-hour moving average
    window = 3
    weights = np.ones(window) / window
    moving_avg = np.convolve(flights_per_hour, weights, mode="valid")
    plt.plot(
        range(1, len(moving_avg) + 1),
        moving_avg,
        "r-",
        linewidth=2,
        label="3-Hour Moving Average",
    )

    plt.title("Flight Distribution Throughout the Day")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Flights")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(hours)

    # Save to bytes buffer for PDF
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
    img_buffer.seek(0)
    plt.close()

    return img_buffer


def generate_detailed_report(
    results, flights_df, filename="results/T4_simulation_report.pdf"
):
    """Generate detailed PDF report with simulation statistics"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=30
    )
    elements.append(Paragraph("Madrid T4 Airport Simulation Report", title_style))
    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]
        )
    )
    elements.append(Spacer(1, 20))

    # Overall Statistics
    elements.append(Paragraph("Overall Statistics", styles["Heading2"]))
    overall_data = [
        ["Total Passengers", str(results["total_passengers"])],
        ["Processed Passengers", str(results["processed_passengers"])],
        ["Average Total Time", f"{results['avg_total_time']:.1f} minutes"],
        ["Maximum Total Time", f"{results['max_total_time']:.1f} minutes"],
        ["Minimum Total Time", f"{results['min_total_time']:.1f} minutes"],
    ]
    overall_table = Table(overall_data)
    overall_table.setStyle(create_table_style())
    elements.append(overall_table)
    elements.append(Spacer(1, 20))

    # Add baggage statistics
    if "baggage_stats" in results:
        elements.append(Paragraph("Baggage Statistics", styles["Heading2"]))
        baggage = results["baggage_stats"]

        baggage_data = [
            ["Metric", "Value"],
            ["Total Bags", str(baggage["total_bags"])],
            [
                "Passengers with Bags",
                f"{baggage['passengers_with_bags']} ({baggage['bags_percentage']:.1f}%)",
            ],
            ["Average Bags per Passenger", f"{baggage['avg_bags_per_passenger']:.2f}"],
            [
                "Average Bags per Passenger with Bags",
                f"{baggage['avg_bags_per_passenger_with_bags']:.2f}",
            ],
            ["Maximum Bags for a Passenger", str(baggage["max_bags"])],
        ]

        baggage_table = Table(baggage_data)
        baggage_table.setStyle(create_table_style())
        elements.append(baggage_table)
        elements.append(Spacer(1, 20))

    # Add overbooking statistics with passenger distribution info
    if "total_flights" in results and results["total_flights"] > 0:
        elements.append(
            Paragraph("Flight & Passenger Distribution Statistics", styles["Heading2"])
        )

        overbooking_data = [
            ["Total Flights", str(results["total_flights"])],
            [
                "Overbooked Flights",
                f"{results['overbooked_flights']} ({results['overbooked_percentage']:.1f}%)",
            ],
            ["Average Overbooking Factor", f"{results['avg_overbooking_factor']:.2f}x"],
            ["Average Load Factor", f"{FLIGHT_LOAD_FACTOR:.2f} (target)"],
            ["Passenger Distribution", "Normal distribution"],
            ["Overbooking Rate", f"{OVERBOOKING_CHANCE*100:.1f}% of flights"],
            ["Max Overbooking", f"{MAX_OVERBOOKING_FACTOR:.2f}x capacity"],
        ]

        overbooking_table = Table(overbooking_data)
        overbooking_table.setStyle(create_table_style())
        elements.append(overbooking_table)
        elements.append(Spacer(1, 20))

        # Add passenger distribution statistics
        elements.append(
            Paragraph("Passenger Distribution by Flight", styles["Heading3"])
        )

        # Check if we have detailed passenger distribution stats
        if "passenger_distribution" in results:
            passenger_dist = results["passenger_distribution"]

            # Create passenger distribution table
            pax_data = [["Metric", "Value"]]
            pax_data.append(
                [
                    "Average Passengers per Flight",
                    f"{passenger_dist['avg_per_flight']:.1f}",
                ]
            )
            pax_data.append(
                ["Minimum Passengers", f"{passenger_dist['min_passengers']}"]
            )
            pax_data.append(
                ["Maximum Passengers", f"{passenger_dist['max_passengers']}"]
            )
            pax_data.append(["Standard Deviation", f"{passenger_dist['std_dev']:.1f}"])

            pax_table = Table(pax_data)
            pax_table.setStyle(create_table_style())
            elements.append(pax_table)
        else:
            elements.append(
                Paragraph(
                    "Passenger counts follow a normal distribution based on aircraft capacity, load factor, and overbooking status.",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 20))

    # Station Statistics
    elements.append(Paragraph("Station Performance", styles["Heading2"]))

    stations = ["checkin", "security", "passport", "boarding"]
    station_data = [["Metric", "Check-in", "Security", "Passport", "Boarding"]]

    metrics = [
        ("Average Wait (min)", "_avg_wait"),
        ("Maximum Wait (min)", "_max_wait"),
        ("Average Queue Length", "_queue_length"),
        ("Maximum Queue", "_max_queue"),
    ]

    for metric_name, suffix in metrics:
        row = [metric_name]
        for station in stations:
            value = results.get(f"{station}{suffix}", 0)
            row.append(f"{value:.1f}")
        station_data.append(row)

    station_table = Table(station_data)
    station_table.setStyle(create_table_style())
    elements.append(station_table)
    elements.append(Spacer(1, 20))

    # Utilization Analysis
    elements.append(Paragraph("Resource Utilization Analysis", styles["Heading2"]))
    util_data = [["Station", "Average", "Peak", "Minimum"]]

    for station in stations:
        util_values = results.get(f"{station}_utilization", [])
        if util_values:
            util_data.append(
                [
                    station.capitalize(),
                    f"{np.mean(util_values):.1%}",
                    f"{np.max(util_values):.1%}",
                    f"{np.min(util_values):.1%}",
                ]
            )

    util_table = Table(util_data)
    util_table.setStyle(create_table_style())
    elements.append(util_table)

    # Add Flight Distribution section after Utilization Analysis
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Flight Distribution", styles["Heading2"]))

    # Create and add flight distribution chart using flights DataFrame
    chart_buffer = create_flight_distribution_chart(flights_df)
    img = Image(chart_buffer, width=450, height=270)
    elements.append(img)

    # Add flight statistics table using DataFrame
    flight_stats = [["Time Period", "Number of Flights"]]

    # Calculate flights per period using pandas
    time_periods = [
        ("Morning (6-10)", lambda x: (6 <= x.dt.hour) & (x.dt.hour < 10)),
        ("Midday (10-14)", lambda x: (10 <= x.dt.hour) & (x.dt.hour < 14)),
        ("Afternoon (14-18)", lambda x: (14 <= x.dt.hour) & (x.dt.hour < 18)),
        ("Evening (18-22)", lambda x: (18 <= x.dt.hour) & (x.dt.hour < 22)),
        ("Night (22-6)", lambda x: (x.dt.hour >= 22) | (x.dt.hour < 6)),
    ]

    for period_name, condition in time_periods:
        # Apply the condition to the Series itself, not individual elements
        count = len(flights_df[condition(flights_df["scheduled_time"])])
        flight_stats.append([period_name, str(count)])

    flight_table = Table(flight_stats)
    flight_table.setStyle(create_table_style())
    elements.append(Spacer(1, 10))
    elements.append(flight_table)

    # Build PDF
    doc.build(elements)
