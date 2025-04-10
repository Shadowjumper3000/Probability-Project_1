# Random seed for reproducibility
RANDOM_SEED = 42

# Simulation parameters
SIM_TIME = 24 * 60  # 24 hours in minutes
CHECKIN_DESKS = 80
IBERIA_DESKS = 60
SECURITY_LANES = 24  # Increased from 10 to 24 lanes total
BAG_SCANNERS = 24  # One scanner per lane
PASSPORT_BOOTHS = 8
PASSPORT_EGATES = 6
BOARDING_AGENTS = 2

# Service time parameters (all times in n/60 format for minutes)
CHECKIN_SERVICE_TIME = 150 / 60  # 2.5 minutes (150 seconds)
CHECKIN_SERVICE_TIME_STDDEV = 60 / 60  # 1 minute variation

BAG_SCAN_TIME = 20 / 60  # Reduced to 20 seconds per bag (modern scanners)
BAG_SCAN_TIME_STDDEV = 10 / 60  # 10 seconds variation

SECURITY_SERVICE_TIME = 45 / 60  # Reduced to 45 seconds screening
SECURITY_SERVICE_TIME_STDDEV = 15 / 60  # 15 seconds variation

EGATE_SERVICE_TIME = 30 / 60  # 30 seconds for e-gate
MANUAL_PASSPORT_TIME = 90 / 60  # 90 seconds for manual check

BOARDING_SERVICE_TIME = 15 / 60  # 15  seconds per passenger boarding

# Passenger behavior parameters
ONLINE_CHECKIN_RATE = 0.5
CARRYON_ONLY_RATE = 0.45
CONNECTING_PASSENGER_RATE = 0.3
EGATE_ELIGIBLE_RATE = 0.7
PRIORITY_PASSENGER_RATE = 0.15
AVG_BAGS_PER_PASSENGER = 0.8

# Flight parameters
FLIGHTS_PER_DAY = 350  # The primary parameter to control flight volume

# Flight generation parameters
BASE_INTERARRIVAL_MINUTES = 5.45
INTERARRIVAL_STD_DEV = 11.37

# Flight generation parameters
HOURLY_PATTERNS = {
    0: 0.1,  # Midnight
    6: 0.4,  # Early morning
    8: 1.0,  # Morning peak
    14: 0.8,  # Afternoon
    17: 1.0,  # Evening peak
    22: 0.5,  # Late evening
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
