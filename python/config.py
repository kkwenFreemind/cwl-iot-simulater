#!/usr/bin/env python3
"""
IoT Water Level Simulator Configuration Module

This module provides comprehensive configuration settings for the Community Water Level
IoT Simulator, including MQTT broker settings, device configurations, simulation parameters,
and logging configurations. All configurations are centralized here to ensure consistency
across different simulator components.

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT

Configuration Categories:
    - MQTT_CONFIG: MQTT broker connection and communication settings
    - DEVICE_CONFIGS: Individual device configurations with credentials and parameters
    - SIMULATION_CONFIG: Physical simulation parameters for realistic data generation
    - LOGGING_CONFIG: Application logging configuration for monitoring and debugging

Usage:
    from config import MQTT_CONFIG, DEVICE_CONFIGS, SIMULATION_CONFIG, LOGGING_CONFIG
    
    # Access MQTT settings
    broker_host = MQTT_CONFIG['broker_host']
    
    # Iterate through device configurations
    for device in DEVICE_CONFIGS:
        print(f"Device: {device['device_id']}")
"""

# MQTT Broker Configuration
# Contains connection parameters for EMQX MQTT broker integration
# Used by all simulator components for consistent broker connectivity
MQTT_CONFIG = {
    'broker_host': 'localhost',  # MQTT broker IP address or hostname (modify for your EMQX instance)
    'broker_port': 1883,         # Standard MQTT port (1883 for non-TLS, 8883 for TLS)
    'keepalive': 60,             # Connection keepalive interval in seconds
    'qos': 1                     # Quality of Service level (0=At most once, 1=At least once, 2=Exactly once)
}

# Device Configuration Array
# Contains authentication credentials and operational parameters for each simulated IoT device
# Each device configuration includes MQTT credentials, telemetry topic, and simulation parameters
# Derived from env.md device information and aligned with iot_metric_definitions database schema
DEVICE_CONFIGS = [
    {
        # Primary Water Level Monitoring Device - Site A
        'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',    # Unique device identifier (UUID format)
        'client_id': 'client_9d3e50ea',                          # MQTT client identifier for connection
        'username': 'device_2_9d3e50ea',                         # EMQX authentication username
        'password': 'b1652e4bac404628',                          # EMQX authentication password
        'topic': 'tenants/2/devices/9d3e50ea/telemetry',        # MQTT telemetry data publication topic
        'base_water_level': 1.5,                                 # Baseline water level in meters for simulation
        'location': 'Reservoir Monitoring Point A',              # Physical deployment location description
        'send_interval': 5                                       # Data transmission interval in seconds
    },
    {
        # Secondary Water Level Monitoring Device - Site B
        'device_id': '0cabc4cb-9092-48ec-80bf-63392a3b73b9',    # Unique device identifier (UUID format)
        'client_id': 'client_0cabc4cb',                          # MQTT client identifier for connection
        'username': 'device_2_0cabc4cb',                         # EMQX authentication username
        'password': 'f8cf145771d84376',                          # EMQX authentication password
        'topic': 'tenants/2/devices/0cabc4cb/telemetry',        # MQTT telemetry data publication topic
        'base_water_level': 2.0,                                 # Baseline water level in meters for simulation
        'location': 'Reservoir Monitoring Point B',              # Physical deployment location description
        'send_interval': 7                                       # Data transmission interval in seconds
    }
]

# Simulation Parameters Configuration
# Defines physical and environmental parameters for realistic IoT sensor data simulation
# These parameters ensure generated data mimics real-world water level monitoring scenarios
# All ranges and thresholds are based on typical environmental monitoring requirements
SIMULATION_CONFIG = {
    'max_water_level': 5.0,           # Maximum allowable water level in meters (safety threshold)
    'min_water_level': 0.0,           # Minimum water level in meters (sensor floor)
    'max_variation': 0.3,             # Maximum water level fluctuation amplitude in meters
    'temp_range': (15.0, 30.0),       # Temperature range in Celsius (seasonal variation)
    'humidity_range': (50.0, 90.0),   # Relative humidity percentage range (weather conditions)
    'battery_range': (70.0, 100.0),   # Battery level percentage range (operational threshold)
    'signal_range': (-90, -40),       # Signal strength range in dBm (connectivity quality)
    'ph_range': (6.0, 8.0),           # Water pH level range (water quality monitoring)
    'pressure_base': 1013.25,         # Standard atmospheric pressure in hPa (sea level reference)
    'pressure_variation': 15.0        # Atmospheric pressure variation in hPa (weather influence)
}

# Logging Configuration Settings
# Defines application-wide logging behavior for monitoring, debugging, and operational analysis
# Supports multiple log levels and customizable formatting for different deployment environments
# Essential for production monitoring and troubleshooting of IoT simulator operations
LOGGING_CONFIG = {
    'level': 'INFO',                                             # Log level threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format string with timestamp and context
    'datefmt': '%Y-%m-%d %H:%M:%S'                               # Date format for log timestamps (ISO-like format for readability)
}