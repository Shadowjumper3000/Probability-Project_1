# Random seed for reproducibility
RANDOM_SEED = 42

# Simulation parameters
SIM_TIME = 24 * 60  # 24 hours in minutes
CHECKIN_DESKS = 100
IBERIA_DESKS = 60
SECURITY_LANES = 24  # Increased from 10 to 24 lanes total
BAG_SCANNERS = 24  # One scanner per lane
PASSPORT_BOOTHS = 10
PASSPORT_EGATES = 6
BOARDING_AGENTS = 2

# Service time parameters (all times in n/60 format for minutes)
CHECKIN_SERVICE_TIME = 60 / 60  # 1 minutes (100 seconds)
CHECKIN_SERVICE_TIME_STDDEV = 25 / 60  # 0.2 minute variation

BAG_SCAN_TIME = 20 / 60  # Reduced to 20 seconds per bag (modern scanners)
BAG_SCAN_TIME_STDDEV = 10 / 60  # 10 seconds variation

SECURITY_SERVICE_TIME = 20 / 60  # Reduced to 20 seconds screening
SECURITY_SERVICE_TIME_STDDEV = 5 / 60  # 5 seconds variation

EGATE_SERVICE_TIME = 30 / 60  # 30 seconds for e-gate
MANUAL_PASSPORT_TIME = 90 / 60  # 90 seconds for manual check

BOARDING_SERVICE_TIME = 15 / 60  # 15  seconds per passenger boarding

# Passenger behavior parameters
ONLINE_CHECKIN_RATE = 0.5
CARRYON_ONLY_RATE = 0.45
CONNECTING_PASSENGER_RATE = 0.0  # Maybe to be used in future
EGATE_ELIGIBLE_RATE = 0.7
PRIORITY_PASSENGER_RATE = 0.15
AVG_BAGS_PER_PASSENGER = 1.2

# Flight parameters
FLIGHTS_PER_DAY = 225  # The primary parameter to control flight volume
MEAN_FLIGHTS_PER_HOUR = 11.04

# Flight load factors
FLIGHT_LOAD_FACTOR = 0.92  # Increase from current 0.85 (85%) to 92%
FLIGHT_LOAD_FACTOR_STDDEV = 0.05  # Standard deviation for realistic variation

# Flight generation parameters
BASE_INTERARRIVAL_MINUTES = 5.45
INTERARRIVAL_STD_DEV = 11.37

# Flight generation parameters - updated with exact hourly distribution
HOURLY_PATTERNS = {
    0: 0.09,  # Midnight
    1: 0.09,  # Early morning
    2: 0.09,  # Early morning
    3: 0.09,  # Early morning
    4: 0.09,  # Early morning
    5: 0.01,  # Early morning
    6: 1.09,  # Early morning
    7: 2.54,  # Early morning
    8: 1.18,
    9: 1.36,
    10: 1.81,
    11: 1.36,
    12: 1.18,  # Afternoon
    13: 0.45,  # Afternoon
    14: 0.72,  # Afternoon
    15: 2.35,
    16: 1.99,
    17: 0.91,
    18: 0.81,
    19: 2.17,  # Evening peak
    20: 1.18,  # Late evening
    21: 0.72,  # Late evening
    22: 0.54,  # Late evening
    23: 0.18,  # Late evening
}

# Schengen airports mapping
SCHENGEN_AIRPORTS = {
    # Austria
    "VIE": "Austria",
    "GRZ": "Austria",
    "INN": "Austria",
    "SZG": "Austria",
    # Belgium
    "BRU": "Belgium",
    "CRL": "Belgium",
    "ANR": "Belgium",
    # France
    "CDG": "France",
    "ORY": "France",
    "NCE": "France",
    "LYS": "France",
    # Germany
    "FRA": "Germany",
    "MUC": "Germany",
    "DUS": "Germany",
    "TXL": "Germany",
    # Italy
    "FCO": "Italy",
    "MXP": "Italy",
    "LIN": "Italy",
    "VCE": "Italy",
    # Spain
    "MAD": "Spain",
    "BCN": "Spain",
    "AGP": "Spain",
    "PMI": "Spain",
    # And more... (abbreviated for clarity)
}

# Schengen destinations with normalized probabilities
SCHENGEN_DESTINATIONS = {
    "BCN": 0.28,  # Barcelona
    "PMI": 0.09,  # Palma
    "FRA": 0.08,  # Frankfurt
    "CDG": 0.16,  # Paris
    "AMS": 0.04,  # Amsterdam
    "MAD": 0.15,  # Madrid
    "BRU": 0.06,  # Brussels
    "LIS": 0.09,  # Lisbon
    "VIE": 0.05,  # Vienna
}

# Aircraft capacity by type
AIRCRAFT_CAPACITY = {
    "B738": 180,
    "A320": 150,
    "CRJX": 90,
    "A20N": 150,
    "A321": 200,
    "B38M": 170,
    "A21N": 200,
    "A319": 120,
    "B789": 290,
}

# Aircraft mix with validated probabilities
AIRCRAFT_MIX = {
    "B738": 0.224,
    "A320": 0.181,
    "CRJX": 0.134,
    "A20N": 0.130,
    "A321": 0.122,
    "B38M": 0.051,
    "A21N": 0.051,
    "A319": 0.024,
    "B789": 0.012,
    "ATR": 0.071,  # Combined remaining types
}

# Overbooking parameters
OVERBOOKING_CHANCE = 0.02  # 02% chance of a flight being overbooked
MAX_OVERBOOKING_FACTOR = 1.10  # Maximum overbooking is 10% over capacity