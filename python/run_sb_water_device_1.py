#!/usr/bin/env python3
"""
Sparkplug B Water Level Simulator Runner

This script serves as the entry point for running the Sparkplug B water level simulator
with pre-configured settings for the sb_water_device_1 device. It initializes the simulator
with database-derived configuration parameters and manages the simulation lifecycle.

The script provides a simplified interface for users to start the Sparkplug B compliant
water level monitoring simulation without manually configuring device parameters.

Key Features:
    - Pre-configured device settings from iot_device database table
    - Automatic simulator initialization and lifecycle management
    - Graceful error handling and user-friendly output
    - Configurable simulation duration with keyboard interrupt support

Usage:
    python run_sb_water_device_1.py

Requirements:
    - paho-mqtt library: pip install paho-mqtt
    - tahu library: pip install tahu
    - Running EMQX broker on localhost:1883 (or update broker_host in config)

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT
"""

import sys
import os

# Add the python directory to the path so we can import the simulator
sys.path.insert(0, os.path.dirname(__file__))

from sparkplug_water_level_simulator import SparkplugBWaterLevelSimulator


def main():
    """
    Main entry point for the sb_water_device_1 Sparkplug B simulator runner.

    This function initializes and runs the Sparkplug B water level simulator with
    pre-configured settings for the sb_water_device_1 device. It handles the complete
    simulation lifecycle from configuration setup through execution and graceful shutdown.

    The function performs the following operations:
    1. Displays startup information and device configuration
    2. Initializes the SparkplugBWaterLevelSimulator with device-specific parameters
    3. Starts the simulation with a predefined duration
    4. Handles user interrupts and error conditions gracefully

    Configuration Details:
        - Device ID: Unique identifier from iot_device table
        - Client ID: MQTT client identifier for broker connection
        - Authentication: Username/password for EMQX broker access
        - Network: Broker host and port configuration
        - Protocol: Community and edge node identifiers for Sparkplug B

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        KeyboardInterrupt: Handled gracefully to allow user-initiated shutdown
        Exception: Caught and logged with user-friendly error message

    Note:
        The simulation duration is set to 10 minutes by default. Modify the
        duration_minutes parameter to change this behavior, or set to None
        for continuous operation.
    """
    print("🚀 Starting Sparkplug B Water Level Simulator for sb_water_device_1")
    print("=" * 60)

    # Device configuration from iot_device table (sb_water_device_1)
    device_config = {
        'device_id': '44547ced-e7fa-489b-8f04-891a30a0adb6',
        'client_id': 'spb_1_2_sb_water_device_1',
        'username': 'device_2_44547ced',
        'password': '5e5d44bd67874f0c',
        'broker_host': 'localhost',  # Update this to your EMQX broker address
        'broker_port': 1883,
        'community_id': 1,
        'edge_node_id': 'sb_water_device_1'
    }

    print(f"Device ID: {device_config['device_id']}")
    print(f"Client ID: {device_config['client_id']}")
    print(f"Username: {device_config['username']}")
    print(f"Broker: {device_config['broker_host']}:{device_config['broker_port']}")
    print(f"Community ID: {device_config['community_id']}")
    print(f"Edge Node ID: {device_config['edge_node_id']}")
    print()

    # Create and start the simulator
    simulator = SparkplugBWaterLevelSimulator(device_config)

    try:
        # Run for 10 minutes (change to None for infinite run)
        print("Starting simulation... Press Ctrl+C to stop.")
        simulator.start_simulation(duration_minutes=10)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"Error during simulation: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())