# Madrid Barajas Airport T4 Queuing System Simulation Analysis

## Executive Summary

This document analyzes the results of a discrete event simulation modeling passenger flow through Madrid Barajas Airport Terminal 4. The simulation implements a network of queues representing check-in, baggage security, security screening, passport control, and boarding processes. Results show significant bottlenecks at security screening, while check-in and passport control resources are underutilized.

## Queue Length Analysis

The simulation revealed several critical insights about queue formation throughout the day:

- **Security Screening**: The primary bottleneck in the system with queue lengths reaching up to 350 passengers during peak periods
- **Three Distinct Peaks**: Security queues show major congestion around hours 7, 14, and 19, corresponding to morning, afternoon, and evening flight waves
- **Negligible Check-in Queues**: Despite processing over 20,000 passengers, check-in facilities show minimal queuing due to excess capacity and distributed service points
- **Minimal Passport Control Queues**: Passport control processes passengers efficiently with no significant queue formation

The near-zero queue lengths for check-in and passport control against security's substantial queues highlight a significant resource allocation imbalance.

## Processing Station Performance

### Check-in
- **Processed Passengers**: ~20,500 (54.5% of total passengers)
- **Average Queue Time**: Near zero (~0.0003 minutes)
- **Maximum Queue Time**: 0.51 minutes
- **Resource Utilization**: Very low, indicating significant excess capacity
- **Observations**: 
  - Online check-in (50%) and connecting passengers (30%) reduce demand
  - 174 desks provide more capacity than required

### Security Screening
- **Processed Passengers**: ~30,000 (80% of total passengers)
- **Average Queue Time**: 5.6 minutes
- **Maximum Queue Time**: 60 minutes
- **Reneged Passengers**: 1,080 (passengers who abandoned due to long waits)
- **Jockeyed Passengers**: 785 (passengers who switched queues)
- **Observations**:
  - Clear system bottleneck with inadequate capacity
  - Severe congestion during peak periods
  - Queue formation follows flight schedule patterns

### Passport Control
- **Processed Passengers**: ~14,450 (38.4% of total passengers)
- **E-Gate Usage**: 69.8% of passport control passengers
- **Average Queue Time**: ~0.002 minutes
- **Maximum Queue Time**: 0.07 minutes
- **Observations**:
  - Limited to non-Schengen flights (30-40% of passengers)
  - Excess capacity with 15 manual booths and 10 e-Gates
  - Very efficient processing with minimal waiting

### Baggage Security
- **Bags Processed**: ~15,200
- **Average Bags Per Passenger**: 0.40
- **Observations**:
  - Automated system handles baggage efficiently
  - 31 scanners provide adequate capacity

### Boarding Process
- **Successfully Boarded**: ~30,300 passengers (80.6% of total)
- **Average Boarding Queue Time**: 2.1 minutes
- **Observations**:
  - Boarding processes function adequately
  - Limited by upstream bottlenecks (primarily security)

## Scenario Comparison

Four scenarios were simulated to evaluate system performance under different conditions:

### Baseline
- **Average Total Time in Airport**: 91.6 minutes
- **Security Queue Time**: 5.6 minutes
- **Reneged Passengers**: 1,080

### Increased Online Check-in (70% vs 50%)
- **Average Total Time in Airport**: 91.7 minutes
- **Security Queue Time**: 5.9 minutes
- **Reneged Passengers**: 1,197
- **Impact**: Minimal improvement to overall system due to security bottleneck

### Reduced Security Lanes (20 vs 26)
- **Average Total Time in Airport**: 91.8 minutes
- **Security Queue Time**: 5.8 minutes
- **Reneged Passengers**: 1,024
- **Impact**: Counter-intuitively shows slightly fewer reneged passengers, likely due to simulation variance

### High Passenger Volume (60,000 vs 50,000)
- **Average Total Time in Airport**: 91.3 minutes
- **Security Queue Time**: 5.6 minutes
- **Reneged Passengers**: 1,152
- **Impact**: System shows some resilience but with increased passenger abandonment

## Key Findings

1. **Resource Imbalance**: The airport has significant resource misallocation with excess capacity at check-in and passport control while security is understaffed.

2. **Bottleneck Identification**: Security screening is the clear constraint in the system, with queue lengths up to 350 passengers and processing times reaching capacity limits.

3. **Passenger Flow Characteristics**: 
   - 80.6% of passengers successfully complete their journey
   - 2.9% abandon the process (primarily at security)
   - Average time in airport is 91.6 minutes, with maximum times of ~208 minutes

4. **Time-of-Day Patterns**: Security queue formation follows distinct patterns with three major peaks throughout the day, suggesting the need for dynamic staffing.

5. **Passenger Mix Impact**: The high proportion of online check-in (50%) and connecting passengers (30%) significantly reduces demand on check-in facilities.

## Recommendations

### Short-Term Operational Improvements

1. **Dynamic Resource Allocation**:
   - Reallocate staff from underutilized check-in and passport control to security during peak periods
   - Implement flexible staffing based on predicted flight waves

2. **Queue Management**:
   - Implement jockeying encouragement systems to balance security lanes
   - Enhance signage and passenger information about current wait times

3. **Process Optimization**:
   - Further promote online check-in to reduce check-in desk requirements
   - Implement priority screening for time-sensitive passengers

### Medium-Term Strategic Changes

1. **Security Capacity Expansion**:
   - Increase the number of security lanes, particularly during peak hours
   - Invest in faster screening technologies

2. **Resource Rebalancing**:
   - Reduce check-in desk allocations
   - Convert some check-in space to additional security screening areas

3. **Passenger Flow Redesign**:
   - Evaluate the physical layout to improve flow between processes
   - Consider dedicated pathways for different passenger types

### Long-Term Infrastructure Planning

1. **Capacity Planning**:
   - Design future expansions with balanced processing capabilities
   - Focus investment on identified bottlenecks rather than uniform expansion

2. **Technology Integration**:
   - Implement advanced passenger flow monitoring systems
   - Develop predictive algorithms for dynamic resource allocation

## Simulation Limitations

1. **Simplifications**: The model necessarily simplifies some aspects of airport operations.

2. **Passenger Behavior**: Actual passenger behavior (arrival patterns, reneging thresholds) may vary from modeled assumptions.

3. **Spatial Constraints**: The simulation does not account for physical walking distances between process stations.

4. **Operational Variations**: Day-to-day variations in staffing, equipment functionality, and external factors are not captured.

## Conclusion

Madrid Barajas Airport Terminal 4 operations exhibit a significant imbalance in resource allocation, with security screening forming a clear bottleneck while check-in and passport control resources are underutilized. The simulation demonstrates that even with reasonable overall capacity, poor distribution of resources leads to substantial passenger queues and waiting times.

The primary recommendation is to rebalance resources by reallocating staff from underutilized areas to security screening and implementing dynamic staffing based on predicted passenger flows throughout the day. These changes could substantially improve passenger experience and operational efficiency without requiring significant capital investment. 