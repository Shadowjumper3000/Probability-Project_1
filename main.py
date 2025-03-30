#!/usr/bin/env python3
# Madrid Barajas Airport T4 Queuing System Simulation
# Simulation of passenger flow through airport processes

import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import sqlite3
from datetime import datetime, timedelta
import seaborn as sns
from collections import defaultdict, Counter
import re
import os

# Set visualization style
plt.style.use('default')
sns.set(style="whitegrid")

# Random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Define Schengen countries for passport control decisions
SCHENGEN_AIRPORTS = {
    # Austria
    'VIE': 'Austria', 'GRZ': 'Austria', 'INN': 'Austria', 'SZG': 'Austria',
    # Belgium
    'BRU': 'Belgium', 'CRL': 'Belgium', 'ANR': 'Belgium',
    # France
    'CDG': 'France', 'ORY': 'France', 'NCE': 'France', 'LYS': 'France',
    # Germany
    'FRA': 'Germany', 'MUC': 'Germany', 'DUS': 'Germany', 'TXL': 'Germany',
    # Italy
    'FCO': 'Italy', 'MXP': 'Italy', 'LIN': 'Italy', 'VCE': 'Italy',
    # Spain
    'MAD': 'Spain', 'BCN': 'Spain', 'AGP': 'Spain', 'PMI': 'Spain',
    # And more... (abbreviated for clarity)
}

# Simulation time parameters
SIM_TIME = 24 * 60  # 24 hours in minutes

# Check-in parameters
CHECKIN_DESKS = 174  # Total check-in desks
IBERIA_DESKS = 100   # Iberia-dedicated desks
CHECKIN_SERVICE_TIME = 2  # minutes per passenger
CHECKIN_SERVICE_TIME_STDDEV = 0.5  # Standard deviation for service time
ONLINE_CHECKIN_RATE = 0.5  # 50% of passengers check in online
CARRYON_ONLY_RATE = 0.45  # 45% of passengers have only carry-on luggage
CONNECTING_PASSENGER_RATE = 0.3  # 30% of passengers are connecting

# Baggage security parameters
BAG_SCANNERS = 31  # Number of baggage scanners
BAG_SCAN_TIME = 8.5/60  # 7-10 seconds per bag, using midpoint (in minutes)
BAG_SCAN_TIME_STDDEV = 1.5/60  # Standard deviation
AVG_BAGS_PER_PASSENGER = 0.8  # Average number of bags per passenger

# Security screening parameters
SECURITY_LANES = 26  # Number of security lanes
SECURITY_SERVICE_TIME = 25/60  # 20-30 seconds per passenger, using midpoint (in minutes)
SECURITY_SERVICE_TIME_STDDEV = 5/60  # Standard deviation

# Passport control parameters
PASSPORT_BOOTHS = 15  # Manual passport control booths
PASSPORT_EGATES = 10  # Automated e-Gates
EGATE_SERVICE_TIME = 12.5/60  # 10-15 seconds per passenger (in minutes)
MANUAL_PASSPORT_TIME = 45/60  # 30-60 seconds per passenger (in minutes)
EGATE_ELIGIBLE_RATE = 0.7  # 70% of passengers can use e-Gates (EU citizens)
NON_SCHENGEN_RATE = 0.35  # 30-40% of passengers need passport control

# Boarding parameters
BOARDING_AGENTS = 2  # Agents per gate
BOARDING_SERVICE_TIME = 6/60  # 6 seconds per boarding pass scan (in minutes)
PRIORITY_PASSENGER_RATE = 0.15  # Business class and elite passengers

# Flight parameters
FLIGHTS_PER_DAY = 325  # 300-350 flights per day
FLIGHTS_PER_HOUR = 13.5  # 12-15 flights per hour
PASSENGERS_PER_DAY = 50000  # Approx 50,000 passengers per day
AVG_PASSENGERS_PER_FLIGHT = PASSENGERS_PER_DAY / FLIGHTS_PER_DAY

# Delay probabilities by airline
DELAY_PROBABILITIES = {
    'Iberia': 0.16,  # 84% on-time = 16% delayed
    'Vueling': 0.15,  # 85% on-time
    'British Airways': 0.24,  # 76% on-time
    'default': 0.21  # 79% on-time (average T4)
}
AVG_DELAY_MINUTES = 27  # Average delay if flight is delayed

# Passenger behavior parameters
EARLY_ARRIVAL_MEAN = 120  # Mean time (in minutes) passengers arrive before flight
EARLY_ARRIVAL_STDDEV = 30  # Standard deviation for early arrival
MAX_WAIT_TOLERANCE = 60  # Maximum time (in minutes) a passenger will wait before reneging
JOCKEYING_THRESHOLD = 3  # Difference in queue length that triggers jockeying

# Function to load flight data from database
def load_flight_data(db_path="statistics/Departures.db"):
    """Load flight data from SQLite database"""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Query all flights from flights table
        df = pd.read_sql_query("SELECT * FROM flights", conn)
        
        # Close connection
        conn.close()
        
        # Convert time to datetime
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        
        # Extract hour for grouping
        df['hour'] = df['datetime'].dt.hour
        
        # Extract airport code from external column
        df['airport_code'] = df['external'].str.extract(r'\(([A-Z]{3})\)')
        
        print(f"Loaded {len(df)} flights from database")
        return df
    
    except Exception as e:
        print(f"Error loading flight data: {str(e)}")
        print("Will use synthetic flight data instead")
        return None 

class Flight:
    """Class representing a flight at Madrid T4"""
    
    def __init__(self, env, id, airline, destination, scheduled_time, aircraft_type, is_schengen):
        self.env = env
        self.id = id
        self.airline = airline
        self.destination = destination
        self.scheduled_time = scheduled_time
        self.aircraft_type = aircraft_type
        self.is_schengen = is_schengen
        self.passengers = []
        self.gate = None
        self.status = "Scheduled"
        
        # Determine number of passengers based on aircraft type
        self.capacity = self.determine_capacity()
        self.passenger_count = self.determine_passenger_count()
        
        # Calculate actual departure time (with possible delay)
        self.is_delayed, self.actual_time = self.calculate_delay()
        
        # Statistics
        self.boarded_passengers = 0
        self.boarding_start_time = None
        self.boarding_complete_time = None
    
    def determine_capacity(self):
        """Determine aircraft capacity based on type"""
        capacity_dict = {
            'A319': 141,
            'A320': 180,
            'A321': 220,
            'A20N': 180,  # A320neo
            'A21N': 220,  # A321neo
            'B738': 189,  # Boeing 737-800
            'B38M': 189,  # Boeing 737 MAX 8
            'B788': 330,  # Boeing 787-8
            'B789': 360,  # Boeing 787-9
            'B77L': 300,  # Boeing 777-200LR
            'CRJX': 90,   # CRJ regional jets
            'ATZ': 70,    # ATR 72
            'ATF': 50,    # ATR 42
            'E290': 114,  # Embraer E-Jet
            'A332': 330   # Airbus A330-200
        }
        return capacity_dict.get(self.aircraft_type, 180)  # Default to 180 if not found
    
    def determine_passenger_count(self):
        """Determine actual number of passengers on this flight"""
        # Randomize load factor between 70% and 95%
        load_factor = np.random.uniform(0.7, 0.95)
        return int(self.capacity * load_factor)
    
    def calculate_delay(self):
        """Calculate if flight is delayed and by how much"""
        # Get delay probability for this airline
        delay_prob = DELAY_PROBABILITIES.get(self.airline, DELAY_PROBABILITIES['default'])
        
        # Determine if flight is delayed
        is_delayed = random.random() < delay_prob
        
        if is_delayed:
            # Calculate delay - gamma distribution to model real-world delays
            delay_minutes = np.random.gamma(shape=2.0, scale=AVG_DELAY_MINUTES/2.0)
            actual_time = self.scheduled_time + delay_minutes
        else:
            actual_time = self.scheduled_time
            
        return is_delayed, actual_time
    
    def assign_gate(self, gate):
        """Assign gate to this flight"""
        self.gate = gate
        
    def add_passenger(self, passenger):
        """Add passenger to this flight"""
        self.passengers.append(passenger)
        
    def __str__(self):
        status_str = "DELAYED" if self.is_delayed else "ON TIME"
        return f"Flight {self.id} to {self.destination} ({self.airline}): {status_str}"


class Passenger:
    """Class representing a passenger moving through the airport"""
    
    id_counter = 0
    
    def __init__(self, env, flight):
        Passenger.id_counter += 1
        self.id = Passenger.id_counter
        self.env = env
        self.flight = flight
        self.arrival_time = self.calculate_arrival_time()
        
        # Assign passenger attributes
        self.is_online_checkin = random.random() < ONLINE_CHECKIN_RATE
        self.is_carryon_only = random.random() < CARRYON_ONLY_RATE
        self.is_connecting = random.random() < CONNECTING_PASSENGER_RATE
        self.is_priority = random.random() < PRIORITY_PASSENGER_RATE
        self.is_egate_eligible = random.random() < EGATE_ELIGIBLE_RATE
        
        # Baggage attributes
        self.checked_bags = 0 if self.is_carryon_only else self.generate_bag_count()
        
        # Tracking passenger state
        self.state = "Created"
        self.has_boarding_pass = self.is_online_checkin
        self.bags_checked = False
        self.cleared_security = False
        self.cleared_passport = False
        self.is_boarded = False
        
        # Stats tracking
        self.checkin_queue_time = 0
        self.security_queue_time = 0
        self.passport_queue_time = 0
        self.boarding_queue_time = 0
        self.total_airport_time = 0
        self.reneged = False
        self.service_times = {}
        
        # Add passenger to flight
        flight.add_passenger(self)
    
    def calculate_arrival_time(self):
        """Calculate passenger arrival time at the airport"""
        # Passengers arrive following a normal distribution centered on EARLY_ARRIVAL_MEAN
        # minutes before departure
        arrival_offset = max(30, np.random.normal(EARLY_ARRIVAL_MEAN, EARLY_ARRIVAL_STDDEV))
        return max(0, self.flight.scheduled_time - arrival_offset)
    
    def generate_bag_count(self):
        """Generate number of checked bags for this passenger"""
        # Use Poisson distribution with mean = AVG_BAGS_PER_PASSENGER
        return np.random.poisson(AVG_BAGS_PER_PASSENGER)
    
    def needs_checkin(self):
        """Determine if passenger needs to go through check-in"""
        # Skip check-in if passenger is connecting, has online check-in and no bags
        if self.is_connecting:
            return False
        if self.is_online_checkin and self.is_carryon_only:
            return False
        return True
    
    def needs_baggage_drop(self):
        """Determine if passenger needs to drop bags"""
        return not self.is_carryon_only and not self.is_connecting
    
    def needs_security(self):
        """Determine if passenger needs to go through security"""
        return not self.is_connecting
    
    def needs_passport_control(self):
        """Determine if passenger needs passport control"""
        # Only need passport control for non-Schengen flights
        return not self.flight.is_schengen
    
    def __str__(self):
        return f"Passenger {self.id} for {self.flight.id}" 

class CheckIn:
    """Check-in station with multiple desks grouped by airline"""
    
    def __init__(self, env):
        self.env = env
        
        # Create airline-specific resource pools
        self.desks = {
            'Iberia': simpy.Resource(env, capacity=IBERIA_DESKS),
            'General': simpy.Resource(env, capacity=CHECKIN_DESKS - IBERIA_DESKS)
        }
        
        # Priority queue for business class
        self.priority_desks = {
            'Iberia': simpy.PriorityResource(env, capacity=int(IBERIA_DESKS * 0.2)),
            'General': simpy.PriorityResource(env, capacity=int((CHECKIN_DESKS - IBERIA_DESKS) * 0.2))
        }
        
        # Statistics
        self.passengers_processed = 0
        self.queue_times = []
        self.service_times = []
        self.queue_length_over_time = []
        self.reneged_passengers = 0
    
    def get_desk_for_passenger(self, passenger):
        """Get appropriate desk resource for a passenger"""
        airline = passenger.flight.airline
        
        if passenger.is_priority:
            if airline == 'Iberia':
                return self.priority_desks['Iberia']
            else:
                return self.priority_desks['General']
        else:
            if airline == 'Iberia':
                return self.desks['Iberia']
            else:
                return self.desks['General']
    
    def process(self, passenger):
        """Process a passenger at check-in"""
        # Skip if passenger doesn't need check-in
        if not passenger.needs_checkin():
            return True
        
        # Get appropriate desk resource
        desk = self.get_desk_for_passenger(passenger)
        
        # Record start time for queue time tracking
        start_wait = self.env.now
        passenger.state = "WaitingForCheckIn"
        
        # Request a desk, with potential for reneging
        with desk.request() as req:
            # Wait for desk or renege if taking too long
            results = yield req | self.env.timeout(MAX_WAIT_TOLERANCE)
            
            if req in results:
                # Successfully got a desk
                wait_time = self.env.now - start_wait
                passenger.checkin_queue_time = wait_time
                self.queue_times.append(wait_time)
                
                # Process time depends on baggage
                process_time = np.random.normal(
                    CHECKIN_SERVICE_TIME + (0.5 * passenger.checked_bags),
                    CHECKIN_SERVICE_TIME_STDDEV
                )
                process_time = max(0.5, process_time)  # Minimum 30 seconds
                
                passenger.state = "CheckingIn"
                yield self.env.timeout(process_time)
                
                # Update stats
                self.service_times.append(process_time)
                passenger.service_times['checkin'] = process_time
                passenger.has_boarding_pass = True
                
                if passenger.needs_baggage_drop():
                    passenger.bags_checked = True
                
                self.passengers_processed += 1
                return True
            else:
                # Passenger reneged due to long wait
                passenger.reneged = True
                self.reneged_passengers += 1
                return False


class BaggageSecurity:
    """Baggage scanning system with multiple scanners"""
    
    def __init__(self, env):
        self.env = env
        self.scanners = simpy.Resource(env, capacity=BAG_SCANNERS)
        
        # Statistics
        self.bags_processed = 0
        self.passengers_processed = 0
        self.processing_times = []
        self.queue_length_over_time = []
    
    def process(self, passenger):
        """Process a passenger's baggage"""
        if not passenger.needs_baggage_drop() or passenger.bags_checked:
            return True
        
        # Request a baggage scanner
        with self.scanners.request() as req:
            passenger.state = "WaitingForBaggageScan"
            yield req
            
            passenger.state = "BaggageScan"
            
            # Process time per bag
            total_scan_time = 0
            for _ in range(passenger.checked_bags):
                scan_time = np.random.normal(BAG_SCAN_TIME, BAG_SCAN_TIME_STDDEV)
                scan_time = max(0.05, scan_time)  # Minimum 3 seconds
                total_scan_time += scan_time
                
            yield self.env.timeout(total_scan_time)
            
            # Update stats
            self.bags_processed += passenger.checked_bags
            self.passengers_processed += 1
            self.processing_times.append(total_scan_time)
            passenger.service_times['bag_security'] = total_scan_time
            passenger.bags_checked = True
            
            return True


class SecurityScreening:
    """Security screening with multiple lanes"""
    
    def __init__(self, env):
        self.env = env
        self.lanes = simpy.Resource(env, capacity=SECURITY_LANES - 1)  # Regular lanes
        self.fast_track = simpy.Resource(env, capacity=1)  # Fast track lane
        
        # Statistics
        self.passengers_processed = 0
        self.queue_times = []
        self.service_times = []
        self.queue_length_over_time = []
        self.reneged_passengers = 0
        self.jockeyed_passengers = 0
    
    def jockey_decision(self, passenger, regular_queue, fast_track_queue):
        """Decide if passenger should switch queues based on length difference"""
        if passenger.is_priority and regular_queue - fast_track_queue > JOCKEYING_THRESHOLD:
            # Priority passenger might switch to fast track
            return 'fast_track'
        return None  # Stay in current queue
    
    def process(self, passenger):
        """Process a passenger at security screening"""
        if not passenger.needs_security() or passenger.cleared_security:
            return True
        
        # Choose resource based on passenger type
        resource = self.fast_track if passenger.is_priority else self.lanes
        
        # Record start time for queue time tracking
        start_wait = self.env.now
        passenger.state = "WaitingForSecurity"
        
        # Queue length monitoring for jockeying
        regular_queue = len(self.lanes.queue)
        fast_track_queue = len(self.fast_track.queue)
        jockey_to = self.jockey_decision(passenger, regular_queue, fast_track_queue)
        
        if jockey_to == 'fast_track':
            resource = self.fast_track
            self.jockeyed_passengers += 1
        
        # Request a security lane, with potential for reneging
        with resource.request() as req:
            # Wait for lane or renege if taking too long
            results = yield req | self.env.timeout(MAX_WAIT_TOLERANCE)
            
            if req in results:
                # Successfully got a lane
                wait_time = self.env.now - start_wait
                passenger.security_queue_time = wait_time
                self.queue_times.append(wait_time)
                
                # Process time varies slightly by passenger type
                if passenger.is_priority:
                    # Priority passengers slightly faster due to less belongings
                    process_time = np.random.normal(
                        SECURITY_SERVICE_TIME * 0.9,
                        SECURITY_SERVICE_TIME_STDDEV
                    )
                else:
                    process_time = np.random.normal(
                        SECURITY_SERVICE_TIME,
                        SECURITY_SERVICE_TIME_STDDEV
                    )
                process_time = max(0.25, process_time)  # Minimum 15 seconds
                
                passenger.state = "SecurityScreening"
                yield self.env.timeout(process_time)
                
                # Update stats
                self.service_times.append(process_time)
                passenger.service_times['security'] = process_time
                passenger.cleared_security = True
                self.passengers_processed += 1
                
                return True
            else:
                # Passenger reneged due to long wait
                passenger.reneged = True
                self.reneged_passengers += 1
                return False


class PassportControl:
    """Passport control with manual booths and e-Gates"""
    
    def __init__(self, env):
        self.env = env
        self.booths = simpy.Resource(env, capacity=PASSPORT_BOOTHS)
        self.egates = simpy.Resource(env, capacity=PASSPORT_EGATES)
        
        # Statistics
        self.passengers_processed = 0
        self.egate_passengers = 0
        self.booth_passengers = 0
        self.queue_times = []
        self.service_times = []
        self.queue_length_over_time = []
        self.reneged_passengers = 0
    
    def process(self, passenger):
        """Process a passenger at passport control"""
        if not passenger.needs_passport_control() or passenger.cleared_passport:
            return True
        
        # Choose resource based on passenger eligibility
        if passenger.is_egate_eligible:
            resource = self.egates
            service_time = np.random.normal(EGATE_SERVICE_TIME, EGATE_SERVICE_TIME/5)
            service_type = 'egate'
        else:
            resource = self.booths
            service_time = np.random.normal(MANUAL_PASSPORT_TIME, MANUAL_PASSPORT_TIME/4)
            service_type = 'booth'
        
        service_time = max(service_time, 0.1)  # Minimum 6 seconds
        
        # Record start time for queue time tracking
        start_wait = self.env.now
        passenger.state = "WaitingForPassport"
        
        # Request a passport control point, with potential for reneging
        with resource.request() as req:
            # Wait for booth/egate or renege if taking too long
            results = yield req | self.env.timeout(MAX_WAIT_TOLERANCE)
            
            if req in results:
                # Successfully got a passport control point
                wait_time = self.env.now - start_wait
                passenger.passport_queue_time = wait_time
                self.queue_times.append(wait_time)
                
                passenger.state = "PassportControl"
                yield self.env.timeout(service_time)
                
                # Update stats
                self.service_times.append(service_time)
                passenger.service_times['passport'] = service_time
                passenger.cleared_passport = True
                
                self.passengers_processed += 1
                if service_type == 'egate':
                    self.egate_passengers += 1
                else:
                    self.booth_passengers += 1
                
                return True
            else:
                # Passenger reneged due to long wait
                passenger.reneged = True
                self.reneged_passengers += 1
                return False 

class Boarding:
    """Boarding gate with priority and general queues"""
    
    def __init__(self, env, flight):
        self.env = env
        self.flight = flight
        
        # Gate agents
        self.agents = simpy.Resource(env, capacity=BOARDING_AGENTS)
        
        # Track boarding status
        self.is_boarding = False
        self.boarding_complete = False
        self.boarding_start_time = None
        self.boarding_end_time = None
        
        # Statistics
        self.passengers_boarded = 0
        self.priority_passengers = 0
        self.queue_times = []
        self.service_times = []
        self.queue_length_over_time = []
    
    def start_boarding(self):
        """Start the boarding process for this flight"""
        self.is_boarding = True
        self.boarding_start_time = self.env.now
        self.flight.status = "Boarding"
        self.flight.boarding_start_time = self.env.now
        
        # Determine boarding duration based on aircraft type
        # Wide-body aircraft take longer to board
        wide_body = self.flight.aircraft_type in ['B788', 'B789', 'B77L', 'A332']
        if wide_body:
            boarding_duration = 45  # 45 minutes for wide-body
        else:
            boarding_duration = 25  # 25 minutes for narrow-body
            
        # Schedule the flight to depart
        return boarding_duration
    
    def complete_boarding(self):
        """Mark boarding as complete"""
        self.is_boarding = False
        self.boarding_complete = True
        self.boarding_end_time = self.env.now
        self.flight.status = "Departed"
        self.flight.boarding_complete_time = self.env.now
    
    def process(self, passenger):
        """Process a passenger for boarding"""
        if not self.is_boarding or passenger.is_boarded or passenger.reneged:
            return False
        
        # Ensure passenger has completed all previous steps
        if not passenger.has_boarding_pass:
            return False
        
        if passenger.needs_security() and not passenger.cleared_security:
            return False
            
        if passenger.needs_passport_control() and not passenger.cleared_passport:
            return False
        
        # Record start time for queue time tracking
        start_wait = self.env.now
        passenger.state = "WaitingToBoard"
        
        # Request a boarding agent
        with self.agents.request() as req:
            yield req
            
            # Calculate queue time
            wait_time = self.env.now - start_wait
            passenger.boarding_queue_time = wait_time
            self.queue_times.append(wait_time)
            
            # Process boarding
            passenger.state = "Boarding"
            process_time = np.random.normal(BOARDING_SERVICE_TIME, BOARDING_SERVICE_TIME/3)
            process_time = max(0.05, process_time)  # Minimum 3 seconds
            
            yield self.env.timeout(process_time)
            
            # Update stats
            self.service_times.append(process_time)
            passenger.service_times['boarding'] = process_time
            passenger.is_boarded = True
            passenger.state = "Boarded"
            
            self.passengers_boarded += 1
            if passenger.is_priority:
                self.priority_passengers += 1
            
            return True


class AirportSimulation:
    """Simulation of Madrid T4 Airport operations"""
    
    def __init__(self, env, flights_df=None):
        self.env = env
        self.flights_df = flights_df
        
        # Initialize process stations
        self.checkin = CheckIn(env)
        self.baggage_security = BaggageSecurity(env)
        self.security_screening = SecurityScreening(env)
        self.passport_control = PassportControl(env)
        
        # Flight and passenger tracking
        self.flights = []
        self.passengers = []
        self.boarding_gates = {}
        
        # Statistics tracking
        self.stats = defaultdict(list)
        self.monitor_handle = None
    
    def generate_flights(self):
        """Generate flights for the simulation"""
        if self.flights_df is not None:
            # Generate flights based on database records
            for _, row in self.flights_df.iterrows():
                # Extract flight time in minutes from start of day
                flight_time = (row['hour'] * 60) + int(row['time'].split(':')[1])
                
                # Check if flight is to a Schengen destination
                is_schengen = row['airport_code'] in SCHENGEN_AIRPORTS
                
                # Create flight object
                flight = Flight(
                    env=self.env,
                    id=row['flight'],
                    airline=row['airline'],
                    destination=row['external'],
                    scheduled_time=flight_time,
                    aircraft_type=row['aircraft'],
                    is_schengen=is_schengen
                )
                
                self.flights.append(flight)
                
                # Create boarding gate for this flight
                gate = Boarding(self.env, flight)
                self.boarding_gates[flight.id] = gate
                
                # Schedule flight events
                self.env.process(self.flight_process(flight))
        else:
            # Generate synthetic flights if no database available
            airlines = ['Iberia', 'Air Europa', 'Ryanair', 'Vueling', 'Iberia Express']
            aircraft_types = ['A320', 'B738', 'A319', 'A321', 'CRJX', 'A20N']
            
            # Distribute flights throughout the day, with peak times
            peak_hours = [7, 10, 15, 19]  # Morning, mid-day, afternoon, evening peaks
            flight_count = 0
            
            for hour in range(24):
                # Calculate number of flights in this hour
                if hour in peak_hours:
                    hour_flights = np.random.poisson(FLIGHTS_PER_HOUR * 1.5)
                else:
                    hour_flights = np.random.poisson(FLIGHTS_PER_HOUR * 0.7)
                
                # Create flights for this hour
                for _ in range(hour_flights):
                    flight_count += 1
                    flight_id = f"F{flight_count}"
                    airline = random.choice(airlines)
                    aircraft = random.choice(aircraft_types)
                    
                    # Randomize minutes within the hour
                    minute = random.randint(0, 59)
                    flight_time = (hour * 60) + minute
                    
                    # 70% probability of Schengen destination
                    is_schengen = random.random() < 0.7
                    
                    # Create flight object
                    flight = Flight(
                        env=self.env,
                        id=flight_id,
                        airline=airline,
                        destination="Synthetic Destination",
                        scheduled_time=flight_time,
                        aircraft_type=aircraft,
                        is_schengen=is_schengen
                    )
                    
                    self.flights.append(flight)
                    
                    # Create boarding gate for this flight
                    gate = Boarding(self.env, flight)
                    self.boarding_gates[flight.id] = gate
                    
                    # Schedule flight events
                    self.env.process(self.flight_process(flight))
    
    def generate_passengers(self, flight):
        """Generate passengers for a specific flight"""
        passenger_count = flight.passenger_count
        
        for _ in range(passenger_count):
            passenger = Passenger(self.env, flight)
            self.passengers.append(passenger)
            
            # Start passenger process
            self.env.process(self.passenger_process(passenger))
    
    def flight_process(self, flight):
        """Manage the flight life cycle"""
        # Generate passengers for this flight
        self.generate_passengers(flight)
        
        # Wait until boarding time (30 minutes before departure)
        boarding_time = max(0, flight.scheduled_time - 30)
        yield self.env.timeout(boarding_time - self.env.now)
        
        # Start boarding
        gate = self.boarding_gates[flight.id]
        boarding_duration = gate.start_boarding()
        
        # Wait for boarding to complete
        yield self.env.timeout(boarding_duration)
        
        # Complete boarding and departure
        gate.complete_boarding()
    
    def passenger_process(self, passenger):
        """Process passenger flow through the airport"""
        # Wait until passenger arrives at the airport
        yield self.env.timeout(passenger.arrival_time - self.env.now)
        
        passenger.state = "ArrivedAtAirport"
        arrival_time = self.env.now
        
        # Step 1: Check-in (if needed)
        if passenger.needs_checkin():
            checkin_result = yield self.env.process(self.checkin.process(passenger))
            if not checkin_result:
                # Passenger reneged, abort further processing
                passenger.total_airport_time = self.env.now - arrival_time
                return
        
        # Step 2: Baggage security (if needed)
        if passenger.needs_baggage_drop() and not passenger.bags_checked:
            yield self.env.process(self.baggage_security.process(passenger))
        
        # Step 3: Security screening (if needed)
        if passenger.needs_security():
            security_result = yield self.env.process(self.security_screening.process(passenger))
            if not security_result:
                # Passenger reneged, abort further processing
                passenger.total_airport_time = self.env.now - arrival_time
                return
        
        # Step 4: Passport control (if needed)
        if passenger.needs_passport_control():
            passport_result = yield self.env.process(self.passport_control.process(passenger))
            if not passport_result:
                # Passenger reneged, abort further processing
                passenger.total_airport_time = self.env.now - arrival_time
                return
        
        # Wait at gate until boarding starts
        passenger.state = "WaitingAtGate"
        gate = self.boarding_gates[passenger.flight.id]
        
        while not gate.is_boarding and not gate.boarding_complete:
            yield self.env.timeout(5)  # Check every 5 minutes
        
        # Step 5: Boarding (if still possible)
        if gate.is_boarding:
            yield self.env.process(gate.process(passenger))
        
        # Calculate total time in airport
        passenger.total_airport_time = self.env.now - arrival_time
    
    def monitor_statistics(self):
        """Periodically collect statistics during simulation"""
        while True:
            # Record current time
            current_time = self.env.now
            
            # Queue lengths
            self.stats['time'].append(current_time)
            self.stats['checkin_queue'].append(sum(len(res.queue) for res in self.checkin.desks.values()) + 
                                             sum(len(res.queue) for res in self.checkin.priority_desks.values()))
            self.stats['security_queue'].append(len(self.security_screening.lanes.queue) + 
                                              len(self.security_screening.fast_track.queue))
            self.stats['passport_queue'].append(len(self.passport_control.booths.queue) + 
                                              len(self.passport_control.egates.queue))
            
            # Resource utilization
            self.stats['checkin_utilization'].append(
                (sum(res.count for res in self.checkin.desks.values()) + 
                 sum(res.count for res in self.checkin.priority_desks.values())) / CHECKIN_DESKS
            )
            self.stats['security_utilization'].append(
                (self.security_screening.lanes.count + self.security_screening.fast_track.count) / SECURITY_LANES
            )
            self.stats['passport_utilization'].append(
                (self.passport_control.booths.count / PASSPORT_BOOTHS if PASSPORT_BOOTHS > 0 else 0) + 
                (self.passport_control.egates.count / PASSPORT_EGATES if PASSPORT_EGATES > 0 else 0) / 2
            )
            
            # Wait for next monitoring interval
            yield self.env.timeout(10)  # Monitor every 10 minutes
    
    def run(self):
        """Run the airport simulation"""
        # Generate flights and setup monitoring
        self.generate_flights()
        self.monitor_handle = self.env.process(self.monitor_statistics())
        
        # Run the simulation
        self.env.run(until=SIM_TIME)
        
        return self.collect_results()
    
    def collect_results(self):
        """Collect and summarize simulation results"""
        results = {
            # Overall metrics
            'total_flights': len(self.flights),
            'total_passengers': len(self.passengers),
            'boarded_passengers': sum(gate.passengers_boarded for gate in self.boarding_gates.values()),
            'reneged_passengers': sum(1 for p in self.passengers if p.reneged),
            
            # Check-in stats
            'checkin_processed': self.checkin.passengers_processed,
            'checkin_avg_queue_time': np.mean(self.checkin.queue_times) if self.checkin.queue_times else 0,
            'checkin_max_queue_time': max(self.checkin.queue_times) if self.checkin.queue_times else 0,
            'checkin_reneged': self.checkin.reneged_passengers,
            
            # Security stats
            'security_processed': self.security_screening.passengers_processed,
            'security_avg_queue_time': np.mean(self.security_screening.queue_times) if self.security_screening.queue_times else 0,
            'security_max_queue_time': max(self.security_screening.queue_times) if self.security_screening.queue_times else 0,
            'security_reneged': self.security_screening.reneged_passengers,
            'security_jockeyed': self.security_screening.jockeyed_passengers,
            
            # Passport stats
            'passport_processed': self.passport_control.passengers_processed,
            'passport_egate_processed': self.passport_control.egate_passengers,
            'passport_booth_processed': self.passport_control.booth_passengers,
            'passport_avg_queue_time': np.mean(self.passport_control.queue_times) if self.passport_control.queue_times else 0,
            'passport_max_queue_time': max(self.passport_control.queue_times) if self.passport_control.queue_times else 0,
            'passport_reneged': self.passport_control.reneged_passengers,
            
            # Bags stats
            'bags_processed': self.baggage_security.bags_processed,
            
            # Passenger times
            'avg_total_time': np.mean([p.total_airport_time for p in self.passengers if p.total_airport_time > 0]),
            'max_total_time': max([p.total_airport_time for p in self.passengers if p.total_airport_time > 0]) if [p.total_airport_time for p in self.passengers if p.total_airport_time > 0] else 0,
            
            # Time series data
            'time_series': self.stats
        }
        
        return results 

# Visualization functions

def plot_queue_lengths(results):
    """Plot queue lengths over time"""
    plt.figure(figsize=(12, 6))
    
    # Convert minutes to hours for x-axis
    hours = [t/60 for t in results['time_series']['time']]
    
    plt.plot(hours, results['time_series']['checkin_queue'], label='Check-in Queue')
    plt.plot(hours, results['time_series']['security_queue'], label='Security Queue')
    plt.plot(hours, results['time_series']['passport_queue'], label='Passport Queue')
    
    plt.title('Queue Lengths Over Time')
    plt.xlabel('Time (hours)')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save plot
    plt.savefig('queue_lengths.png')
    plt.close()

def plot_resource_utilization(results):
    """Plot resource utilization over time"""
    plt.figure(figsize=(12, 6))
    
    # Convert minutes to hours for x-axis
    hours = [t/60 for t in results['time_series']['time']]
    
    plt.plot(hours, results['time_series']['checkin_utilization'], label='Check-in Desks')
    plt.plot(hours, results['time_series']['security_utilization'], label='Security Lanes')
    plt.plot(hours, results['time_series']['passport_utilization'], label='Passport Control')
    
    plt.title('Resource Utilization Over Time')
    plt.xlabel('Time (hours)')
    plt.ylabel('Utilization Rate')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save plot
    plt.savefig('resource_utilization.png')
    plt.close()

def plot_passenger_times(simulation):
    """Plot distribution of passenger times"""
    # Collect data
    total_times = [p.total_airport_time for p in simulation.passengers if p.total_airport_time > 0]
    checkin_times = [p.checkin_queue_time for p in simulation.passengers if p.checkin_queue_time > 0]
    security_times = [p.security_queue_time for p in simulation.passengers if p.security_queue_time > 0]
    passport_times = [p.passport_queue_time for p in simulation.passengers if p.passport_queue_time > 0]
    boarding_times = [p.boarding_queue_time for p in simulation.passengers if p.boarding_queue_time > 0]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Plot total time distribution
    plt.subplot(2, 2, 1)
    plt.hist(total_times, bins=30, alpha=0.7, color='skyblue')
    plt.title('Total Time in Airport')
    plt.xlabel('Minutes')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    
    # Plot check-in queue time
    plt.subplot(2, 2, 2)
    plt.hist(checkin_times, bins=30, alpha=0.7, color='green')
    plt.title('Check-in Queue Time')
    plt.xlabel('Minutes')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    
    # Plot security queue time
    plt.subplot(2, 2, 3)
    plt.hist(security_times, bins=30, alpha=0.7, color='orange')
    plt.title('Security Queue Time')
    plt.xlabel('Minutes')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    
    # Plot passport queue time
    plt.subplot(2, 2, 4)
    plt.hist(passport_times, bins=30, alpha=0.7, color='red')
    plt.title('Passport Control Queue Time')
    plt.xlabel('Minutes')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('passenger_times.png')
    plt.close()
    
    # Additional plot for boarding times
    plt.figure(figsize=(8, 5))
    plt.hist(boarding_times, bins=20, alpha=0.7, color='purple')
    plt.title('Boarding Queue Time')
    plt.xlabel('Minutes')
    plt.ylabel('Number of Passengers')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('boarding_times.png')
    plt.close()

def compare_scenarios(baseline, scenarios):
    """Compare key metrics across different scenarios"""
    # Define metrics to compare
    metrics = [
        'avg_total_time',
        'checkin_avg_queue_time',
        'security_avg_queue_time',
        'passport_avg_queue_time',
        'reneged_passengers'
    ]
    
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Plot each metric
    for i, metric in enumerate(metrics):
        plt.subplot(2, 3, i+1)
        
        # Prepare data
        labels = ['Baseline'] + [s[0] for s in scenarios]
        values = [baseline[metric]] + [s[1][metric] for s in scenarios]
        
        # Create bar chart
        bars = plt.bar(labels, values, color=plt.cm.viridis(np.linspace(0, 1, len(labels))))
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom', rotation=0)
        
        # Format title and labels
        metric_name = ' '.join(word.capitalize() for word in metric.split('_'))
        plt.title(metric_name)
        plt.ylabel('Minutes' if 'time' in metric else 'Count')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('scenario_comparison.png')
    plt.close()

def print_statistics(results):
    """Print summary statistics from simulation results"""
    print("=== Madrid T4 Airport Simulation Results ===")
    print(f"\nOverall Statistics:")
    print(f"Total Flights: {results['total_flights']}")
    print(f"Total Passengers: {results['total_passengers']}")
    boarded_pct = results['boarded_passengers']/results['total_passengers']*100 if results['total_passengers'] > 0 else 0
    print(f"Boarded Passengers: {results['boarded_passengers']} ({boarded_pct:.1f}%)")
    reneged_pct = results['reneged_passengers']/results['total_passengers']*100 if results['total_passengers'] > 0 else 0
    print(f"Reneged Passengers: {results['reneged_passengers']} ({reneged_pct:.1f}%)")

    print(f"\nCheck-In Statistics:")
    print(f"Passengers Processed: {results['checkin_processed']}")
    print(f"Average Queue Time: {results['checkin_avg_queue_time']:.2f} minutes")
    print(f"Maximum Queue Time: {results['checkin_max_queue_time']:.2f} minutes")
    print(f"Reneged Passengers: {results['checkin_reneged']}")

    print(f"\nSecurity Screening Statistics:")
    print(f"Passengers Processed: {results['security_processed']}")
    print(f"Average Queue Time: {results['security_avg_queue_time']:.2f} minutes")
    print(f"Maximum Queue Time: {results['security_max_queue_time']:.2f} minutes")
    print(f"Reneged Passengers: {results['security_reneged']}")
    print(f"Jockeyed Passengers: {results['security_jockeyed']}")

    print(f"\nPassport Control Statistics:")
    print(f"Passengers Processed: {results['passport_processed']}")
    passport_pct = results['passport_egate_processed']/results['passport_processed']*100 if results['passport_processed'] > 0 else 0
    print(f"E-Gate Passengers: {results['passport_egate_processed']} ({passport_pct:.1f}%)")
    booth_pct = results['passport_booth_processed']/results['passport_processed']*100 if results['passport_processed'] > 0 else 0
    print(f"Manual Booth Passengers: {results['passport_booth_processed']} ({booth_pct:.1f}%)")
    print(f"Average Queue Time: {results['passport_avg_queue_time']:.2f} minutes")
    print(f"Maximum Queue Time: {results['passport_max_queue_time']:.2f} minutes")
    print(f"Reneged Passengers: {results['passport_reneged']}")

    print(f"\nBaggage Statistics:")
    print(f"Bags Processed: {results['bags_processed']}")
    bags_per_pax = results['bags_processed']/results['total_passengers'] if results['total_passengers'] > 0 else 0
    print(f"Average Bags Per Passenger: {bags_per_pax:.2f}")

    print(f"\nPassenger Time Statistics:")
    print(f"Average Time in Airport: {results['avg_total_time']:.2f} minutes")
    print(f"Maximum Time in Airport: {results['max_total_time']:.2f} minutes")

def run_scenario(scenario_name, **param_changes):
    """Run a simulation scenario with modified parameters"""
    print(f"Running scenario: {scenario_name}")
    
    # Store original values
    original_values = {}
    
    # Apply parameter changes
    for param, value in param_changes.items():
        if param in globals():
            original_values[param] = globals()[param]
            globals()[param] = value
            print(f"  Changed {param}: {original_values[param]} -> {value}")
    
    # Run simulation
    env = simpy.Environment()
    simulation = AirportSimulation(env, flights_df)
    results = simulation.run()
    
    # Restore original values
    for param, value in original_values.items():
        globals()[param] = value
    
    return results, simulation


if __name__ == "__main__":
    print("Madrid Barajas Airport T4 Queuing System Simulation")
    print("--------------------------------------------------")
    
    # Load flight data
    flights_df = load_flight_data()
    
    # Run baseline simulation
    print("\nRunning baseline simulation...")
    env = simpy.Environment()
    simulation = AirportSimulation(env, flights_df)
    results = simulation.run()
    
    print(f"\nSimulation completed for {SIM_TIME/60:.1f} hours of airport operations")
    
    # Print and visualize results
    print_statistics(results)
    plot_queue_lengths(results)
    plot_resource_utilization(results)
    plot_passenger_times(simulation)
    
    print("\nRunning alternative scenarios...")
    
    # Scenario 1: Increased online check-ine 
    scenario1_results, scenario1_sim = run_scenario(
        "Increased Online Check-in",
        ONLINE_CHECKIN_RATE=0.7  # Increase from 50% to 70%
    )
    
    # Scenario 2: Reduced security lanes
    scenario2_results, scenario2_sim = run_scenario(
        "Reduced Security Lanes",
        SECURITY_LANES=20  # Reduce from 26 to 20
    )
    
    # Scenario 3: High passenger volume
    scenario3_results, scenario3_sim = run_scenario(
        "High Passenger Volume",
        PASSENGERS_PER_DAY=60000  # Increase from 50,000 to 60,000
    )
    
    # Compare scenarios
    compare_scenarios(
        results,
        [
            ("Increased Online Check-in", scenario1_results),
            ("Reduced Security Lanes", scenario2_results),
            ("High Passenger Volume", scenario3_results)
        ]
    )
    
    print("\nScenario analysis completed")
    print("\nResults saved to:")
    print("- queue_lengths.png")
    print("- resource_utilization.png")
    print("- passenger_times.png")
    print("- boarding_times.png")
    print("- scenario_comparison.png")
    
    print("\nSimulation complete.") 