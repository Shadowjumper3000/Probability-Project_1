#!/usr/bin/env python3
# Statistics Calculation for Madrid T4 Airport Simulation
# This script loads flight data from the SQLite database and calculates all necessary statistics

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import re
from datetime import datetime
from scipy import stats
import os
from matplotlib.backends.backend_pdf import PdfPages
from io import StringIO
import contextlib

# Set paths and constants
DATABASE_PATH = "data/processed/departures.db"
OUTPUT_DIR = "data/processed/plots"
DATA_PATH = "data/processed"  # Define data path for storing output files
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)  # Ensure the data directory exists

# Set default style
plt.style.use("default")
sns.set(style="whitegrid")


def load_data_from_db(db_path):
    """Load flight data from SQLite database"""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)

        # Query all flights
        query = "SELECT * FROM flights"
        df = pd.read_sql_query(query, conn)

        conn.close()

        print(f"Loaded {len(df)} flights from database.")
        print("\nSample of data:")
        print(df.head())

        return df

    except Exception as e:
        print(f"Error loading data from database: {str(e)}")
        return None


def create_flight_statistics(df):
    """Calculate basic flight statistics"""
    # Extract hour from time
    df["hour"] = df["time"].apply(lambda x: int(x.split(":")[0]) if ":" in x else None)

    # Remove rows with invalid hours
    df = df.dropna(subset=["hour"])
    df["hour"] = df["hour"].astype(int)

    # Convert time to datetime
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

    # Calculate hourly flights
    hourly_flights = df.groupby(df["datetime"].dt.hour).size()

    # Add daily flight calculation
    df["date_only"] = pd.to_datetime(df["date"])
    daily_flights = df.groupby(df["date_only"]).size()

    # Calculate daily flight statistics
    daily_stats = {
        "Average Flights per Day": daily_flights.mean(),
        "Median Flights per Day": daily_flights.median(),
        "Min Flights per Day": daily_flights.min(),
        "Max Flights per Day": daily_flights.max(),
        "Std Dev Flights per Day": daily_flights.std(),
        "Total Days in Dataset": len(daily_flights),
        "Total Flights": len(df),
    }

    # Calculate time-based statistics
    time_stats = {
        "Peak Hour": hourly_flights.idxmax(),
        "Peak Hour Flights": hourly_flights.max(),
        "Average Flights per Hour": hourly_flights.mean(),
        "Std Dev Flights per Hour": hourly_flights.std(),
    }

    # Calculate inter-arrival times
    df_sorted = df.sort_values("datetime")
    df_sorted["next_arrival"] = df_sorted["datetime"].shift(-1)
    df_sorted["inter_arrival_minutes"] = (
        df_sorted["next_arrival"] - df_sorted["datetime"]
    ).dt.total_seconds() / 60

    return df, hourly_flights, time_stats, df_sorted, daily_flights, daily_stats


def plot_flight_distributions(hourly_flights, df, output_dir=OUTPUT_DIR):
    """Create visualizations for flight data"""
    # 1. Hourly Distribution
    plt.figure(figsize=(12, 6))
    hourly_flights.plot(kind="bar", color="skyblue", alpha=0.7)
    plt.plot(
        range(len(hourly_flights)),
        hourly_flights.rolling(3, center=True, min_periods=1).mean(),
        "r-",
        linewidth=2,
        label="3-hour Moving Average",
    )
    plt.title("Hourly Distribution with Moving Average")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Flights")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/hourly_distribution.png", dpi=300)
    plt.close()

    # 2. Inter-arrival Time Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(
        df["inter_arrival_minutes"].dropna(),
        bins=30,
        density=True,
        alpha=0.7,
        color="skyblue",
    )
    plt.title("Distribution of Inter-arrival Times")
    plt.xlabel("Minutes Between Arrivals")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/interarrival_distribution.png", dpi=300)
    plt.close()

    # 3. Aircraft Type Distribution
    plt.figure(figsize=(12, 6))
    aircraft_stats = df["aircraft"].value_counts()
    aircraft_stats.plot(kind="bar", color="skyblue")
    plt.title("Aircraft Type Distribution")
    plt.xlabel("Aircraft Type")
    plt.ylabel("Number of Flights")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/aircraft_distribution.png", dpi=300)
    plt.close()

    # 4. Country Distribution
    # Extract the country from airport code
    def get_country_from_code(external):
        code_match = re.search(r"\(([A-Z]{3})\)", external)
        if not code_match:
            return "Unknown"

        # Define Schengen airport dictionary (same as in your notebook)
        schengen_airports = {
            # Austria
            "VIE": "Austria",
            "GRZ": "Austria",
            "INN": "Austria",
            "SZG": "Austria",
            "KLU": "Austria",
            "LNZ": "Austria",
            # Belgium
            "BRU": "Belgium",
            "CRL": "Belgium",
            "ANR": "Belgium",
            "LGG": "Belgium",
            "OST": "Belgium",
            # Czech Republic
            "PRG": "Czech Republic",
            "BRQ": "Czech Republic",
            "OSR": "Czech Republic",
            "KLV": "Czech Republic",
            "PED": "Czech Republic",
            # Denmark
            "CPH": "Denmark",
            "BLL": "Denmark",
            "AAL": "Denmark",
            "AAR": "Denmark",
            "EBJ": "Denmark",
            # Estonia
            "TLL": "Estonia",
            "TAY": "Estonia",
            "EPU": "Estonia",
            "URE": "Estonia",
            # Finland
            "HEL": "Finland",
            "TMP": "Finland",
            "TKU": "Finland",
            "OUL": "Finland",
            "RVN": "Finland",
            # France
            "CDG": "France",
            "ORY": "France",
            "NCE": "France",
            "LYS": "France",
            "MRS": "France",
            "BOD": "France",
            "TLS": "France",
            "NTE": "France",
            # Germany
            "FRA": "Germany",
            "MUC": "Germany",
            "DUS": "Germany",
            "TXL": "Germany",
            "HAM": "Germany",
            "STR": "Germany",
            "CGN": "Germany",
            "LEJ": "Germany",
            # Greece
            "ATH": "Greece",
            "SKG": "Greece",
            "HER": "Greece",
            "RHO": "Greece",
            "CHQ": "Greece",
            "JMK": "Greece",
            # Hungary
            "BUD": "Hungary",
            "DEB": "Hungary",
            "SOB": "Hungary",
            "PEV": "Hungary",
            # Iceland
            "KEF": "Iceland",
            "RKV": "Iceland",
            "AEY": "Iceland",
            "EGS": "Iceland",
            # Italy
            "FCO": "Italy",
            "MXP": "Italy",
            "LIN": "Italy",
            "VCE": "Italy",
            "TRN": "Italy",
            "BLQ": "Italy",
            "NAP": "Italy",
            "PSA": "Italy",
            # Latvia
            "RIX": "Latvia",
            "VNT": "Latvia",
            "LPX": "Latvia",
            "RGA": "Latvia",
            # Lithuania
            "VNO": "Lithuania",
            "KUN": "Lithuania",
            "PLQ": "Lithuania",
            "SQQ": "Lithuania",
            # Luxembourg
            "LUX": "Luxembourg",
            # Malta
            "MLA": "Malta",
            "GOZ": "Malta",
            # Netherlands
            "AMS": "Netherlands",
            "EIN": "Netherlands",
            "RTM": "Netherlands",
            "GRQ": "Netherlands",
            "MST": "Netherlands",
            # Norway
            "OSL": "Norway",
            "BGO": "Norway",
            "SVG": "Norway",
            "TOS": "Norway",
            "TRD": "Norway",
            # Poland
            "WAW": "Poland",
            "KRK": "Poland",
            "GDN": "Poland",
            "WRO": "Poland",
            "POZ": "Poland",
            "KTW": "Poland",
            # Portugal
            "LIS": "Portugal",
            "OPO": "Portugal",
            "FAO": "Portugal",
            "PDL": "Portugal",
            "FNC": "Portugal",
            # Slovakia
            "BTS": "Slovakia",
            "KSC": "Slovakia",
            "TAT": "Slovakia",
            "PZY": "Slovakia",
            # Slovenia
            "LJU": "Slovenia",
            "MBX": "Slovenia",
            "POW": "Slovenia",
            # Spain
            "MAD": "Spain",
            "BCN": "Spain",
            "AGP": "Spain",
            "PMI": "Spain",
            "VLC": "Spain",
            "SVQ": "Spain",
            "BIO": "Spain",
            "ALC": "Spain",
            # Sweden
            "ARN": "Sweden",
            "GOT": "Sweden",
            "MMX": "Sweden",
            "LLA": "Sweden",
            "BMA": "Sweden",
            # Switzerland
            "ZRH": "Switzerland",
            "GVA": "Switzerland",
            "BSL": "Switzerland",
            "LUG": "Switzerland",
            "BRN": "Switzerland",
        }

        code = code_match.group(1)
        return schengen_airports.get(code, "Unknown")

    # Add country column and plot
    df["country"] = df["external"].apply(get_country_from_code)
    country_counts = df["country"].value_counts()

    plt.figure(figsize=(12, 6))
    country_counts.plot(kind="bar", color="skyblue")
    plt.title("Flight Distribution by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Flights")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/country_distribution.png", dpi=300)
    plt.close()

    print(f"Plots saved to {output_dir} directory")
    return aircraft_stats, country_counts


def print_statistics(df, time_stats, hourly_flights):
    """Print statistical summary with improved Poisson test"""
    print("\n=== Airport Operations Statistics ===")
    print("\nTime-Based Statistics:")
    for key, value in time_stats.items():
        print(f"{key}: {value:.2f}")

    print("\nInter-arrival Time Statistics (minutes):")
    print(df["inter_arrival_minutes"].describe())

    aircraft_stats = df["aircraft"].value_counts()
    aircraft_percentages = (aircraft_stats / len(df)) * 100
    print("\nAircraft Mix:")
    for aircraft, percentage in aircraft_percentages.items():
        print(f"{aircraft}: {percentage:.1f}%")

    print("\nModeling Parameters:")
    print(f"Mean Inter-arrival Time: {df['inter_arrival_minutes'].mean():.2f} minutes")
    print(
        f"Inter-arrival Time Std Dev: {df['inter_arrival_minutes'].std():.2f} minutes"
    )

    # Improved Poisson distribution test
    try:
        # Calculate expected frequencies
        hourly_lambda = hourly_flights.mean()
        hours = len(hourly_flights)
        expected = stats.poisson.pmf(range(max(hourly_flights) + 1), hourly_lambda)
        expected = expected * sum(hourly_flights)

        # Prepare observed frequencies
        observed = hourly_flights.value_counts().sort_index()

        # Ensure observed and expected have same length
        idx = range(max(observed.index) + 1)
        observed = pd.Series(0, index=idx).add(observed, fill_value=0)
        expected = expected[: len(observed)]

        # Perform chi-square test
        chi_square_stat, p_value = stats.chisquare(observed, expected)

        print(f"\nPoisson Distribution Test:")
        print(f"Chi-square statistic: {chi_square_stat:.4f}")
        print(f"p-value: {p_value:.4f}")
        print(f"Follows Poisson distribution: {p_value > 0.05}")

    except Exception as e:
        print(f"\nPoisson Distribution Test failed: {str(e)}")
        print("Cannot determine if arrivals follow Poisson distribution")


def calculate_hourly_patterns(hourly_flights):
    """Calculate hourly pattern factors relative to average flights per hour for all 24 hours"""
    # Get average flights per hour for normalization
    avg_flights_per_hour = hourly_flights.mean()
    print(f"Average flights per hour: {avg_flights_per_hour:.2f}")

    # Calculate pattern factor for each hour
    hourly_factors = hourly_flights / avg_flights_per_hour

    # Create patterns dictionary with all 24 hours
    patterns = {}

    # Fill in all 24 hours
    for hour in range(24):
        # If hour exists in data, use the calculated factor
        if hour in hourly_factors.index:
            factor = hourly_factors[hour]
        else:
            # For missing hours (e.g., hours with no flights), use a very low factor
            factor = 0.01  # Nearly zero, but not exactly zero to avoid division issues

        # Round to 2 decimal places for config file readability
        patterns[hour] = round(factor, 2)

    # Identify key hours for labeling
    morning_peak_hour = (
        hourly_factors.iloc[5:12].idxmax() if 5 in hourly_factors.index else None
    )
    afternoon_peak_hour = (
        hourly_factors.iloc[12:20].idxmax() if 12 in hourly_factors.index else None
    )

    return (
        patterns,
        hourly_factors,
        avg_flights_per_hour,
        morning_peak_hour,
        afternoon_peak_hour,
    )


def visualize_hourly_patterns(hourly_patterns, hourly_factors, output_dir=OUTPUT_DIR):
    """Visualize and generate configuration for hourly patterns"""
    # Print the results in a format ready for the config.py file
    print("\n# Hourly pattern factors (relative to average flights per hour)")
    print("HOURLY_PATTERNS = {")
    for hour, factor in sorted(hourly_patterns.items()):
        description = ""
        if hour == 0:
            description = "  # Midnight"
        elif hour < 8:
            description = "  # Early morning"
        elif hour == hourly_factors.iloc[:12].idxmax():
            description = "  # Morning peak"
        elif hour >= 12 and hour < 15:
            description = "  # Afternoon"
        elif hour >= 15 and hour < 20 and hour == hourly_factors.iloc[15:20].idxmax():
            description = "  # Evening peak"
        elif hour >= 20:
            description = "  # Late evening"
        print(f"    {hour}: {factor},{description}")
    print("}")

    # Save hourly patterns to config-ready file
    with open(f"{output_dir}/hourly_patterns.py", "w") as f:
        f.write("# Hourly pattern factors derived from flight data analysis\n")
        f.write("HOURLY_PATTERNS = {\n")
        for hour, factor in sorted(hourly_patterns.items()):
            description = ""
            if hour == 0:
                description = "  # Midnight"
            elif hour < 8:
                description = "  # Early morning"
            elif hour == hourly_factors.iloc[:12].idxmax():
                description = "  # Morning peak"
            elif hour >= 12 and hour < 15:
                description = "  # Afternoon"
            elif (
                hour >= 15 and hour < 20 and hour == hourly_factors.iloc[15:20].idxmax()
            ):
                description = "  # Evening peak"
            elif hour >= 20:
                description = "  # Late evening"
            f.write(f"    {hour}: {factor},{description}\n")
        f.write("}\n")

    # Visualize the hourly pattern factors
    plt.figure(figsize=(14, 6))
    hourly_factors.plot(kind="bar", color="skyblue")
    plt.axhline(
        y=1.0, color="r", linestyle="--", alpha=0.7, label="Average flights per hour"
    )

    # Highlight the selected pattern hours
    for hour in hourly_patterns.keys():
        plt.bar(hour, hourly_factors.get(hour, 0), color="orange", alpha=0.7)

    plt.title("Hourly Pattern Factors (relative to average flights per hour)")
    plt.xlabel("Hour of Day")
    plt.ylabel("Factor (1.0 = average)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/hourly_pattern_factors.png", dpi=300)
    plt.close()

    # Compare to original config values
    original_patterns = {
        0: 0.0,  # Midnight
        6: 0.2,  # Early morning
        8: 1.0,  # Morning peak
        14: 0.8,  # Afternoon
        17: 1.0,  # Evening peak
        22: 0.5,  # Late evening
    }

    # Create comparison table
    print("\nComparison with original patterns:")
    print("Hour | Original | Calculated | Description")
    print("-" * 50)
    all_hours = sorted(
        set(list(original_patterns.keys()) + list(hourly_patterns.keys()))
    )
    for hour in all_hours:
        orig = original_patterns.get(hour, "-")
        calc = hourly_patterns.get(hour, "-")

        # Determine description
        if hour == 0:
            desc = "Midnight"
        elif hour < 8:
            desc = "Early morning"
        elif hour == 8:
            desc = "Morning peak"
        elif hour == 14:
            desc = "Afternoon"
        elif hour == 17:
            desc = "Evening peak"
        elif hour >= 20:
            desc = "Late evening"
        else:
            desc = ""

        print(f"{hour:4d} | {orig:8} | {calc:10} | {desc}")


def generate_pdf_report(
    df, hourly_flights, time_stats, output_path=f"{OUTPUT_DIR}/flight_statistics.pdf"
):
    """Generate PDF report with flight statistics and visualizations"""
    with PdfPages(output_path) as pdf:
        # Capture print output
        output = StringIO()
        with contextlib.redirect_stdout(output):
            print_statistics(df, time_stats, hourly_flights)
        text_output = output.getvalue()

        # Create text figure
        fig_text = plt.figure(figsize=(12, 8))
        plt.text(0.1, 0.1, text_output, family="monospace", fontsize=10)
        plt.axis("off")
        pdf.savefig(fig_text)
        plt.close()

        # Create distribution plots
        # 1. Hourly Distribution
        fig1 = plt.figure(figsize=(12, 6))
        hourly_flights.plot(kind="bar", color="skyblue", alpha=0.7)
        plt.plot(
            range(len(hourly_flights)),
            hourly_flights.rolling(3, center=True, min_periods=1).mean(),
            "r-",
            linewidth=2,
            label="3-hour Moving Average",
        )
        plt.title("Hourly Distribution with Moving Average")
        plt.xlabel("Hour of Day")
        plt.ylabel("Number of Flights")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig1)
        plt.close()

        # 2. Inter-arrival Time Distribution
        fig2 = plt.figure(figsize=(10, 6))
        plt.hist(df["inter_arrival_minutes"].dropna(), bins=30, density=True, alpha=0.7)
        plt.title("Distribution of Inter-arrival Times")
        plt.xlabel("Minutes Between Arrivals")
        plt.ylabel("Frequency")
        plt.tight_layout()
        pdf.savefig(fig2)
        plt.close()

        # 3. Aircraft Type Distribution
        fig3 = plt.figure(figsize=(12, 6))
        aircraft_stats = df["aircraft"].value_counts()
        aircraft_stats.plot(kind="bar")
        plt.title("Aircraft Type Distribution")
        plt.xlabel("Aircraft Type")
        plt.ylabel("Number of Flights")
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig(fig3)
        plt.close()

        print(f"PDF report generated: {output_path}")


def main():
    """Main function to run all analyses"""
    print("=" * 80)
    print("MADRID T4 AIRPORT FLIGHT DATA ANALYSIS")
    print("=" * 80)
    print(f"Loading data from {DATABASE_PATH}")

    # Load data
    df_schengen = load_data_from_db(DATABASE_PATH)

    if df_schengen is None or len(df_schengen) == 0:
        print("No data available for analysis!")
        return 1

    # Create flight statistics
    df_schengen, hourly_flights, time_stats, df_sorted, daily_flights, daily_stats = (
        create_flight_statistics(df_schengen)
    )

    # Plot distributions
    print("\nGenerating plots...")
    aircraft_stats, country_counts = plot_flight_distributions(
        hourly_flights, df_sorted
    )

    # Print statistics
    print_statistics(df_sorted, time_stats, hourly_flights)

    # Calculate hourly patterns
    print("\nCalculating hourly patterns...")
    (
        hourly_patterns,
        hourly_factors,
        avg_flights_per_hour,
        morning_peak_hour,
        afternoon_peak_hour,
    ) = calculate_hourly_patterns(hourly_flights)

    # Visualize hourly patterns
    visualize_hourly_patterns(hourly_patterns, hourly_factors)

    # Generate PDF report
    print("\nGenerating comprehensive PDF report...")
    output_path = f"{DATA_PATH}/Departures-flight_statistics.pdf"
    generate_pdf_report(df_sorted, hourly_flights, time_stats, output_path)

    print("\nAnalysis complete!")
    print(f"Results saved to {OUTPUT_DIR}/ and PDF report saved to {output_path}")

    return 0


if __name__ == "__main__":
    main()
