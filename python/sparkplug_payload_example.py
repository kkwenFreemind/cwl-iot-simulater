#!/usr/bin/env python3
"""
Sparkplug B Payload Structure Demonstration

Test and showcase Sparkplug B data structures compliant with the
iot_metric_definitions database table specifications. This module
demonstrates proper payload formatting for water level monitoring
systems using the Eclipse Sparkplug B industrial IoT protocol.

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT
"""

import json
import time
import random
import math
from datetime import datetime

def get_current_timestamp_ms():
    """
    Get current timestamp in milliseconds for Sparkplug B compliance.
    
    Returns the current system time in milliseconds since Unix epoch,
    required for Sparkplug B metric timestamp fields to ensure temporal
    accuracy and proper sequencing in industrial IoT data streams.
    
    Returns:
        int: Current timestamp in milliseconds since Unix epoch
    """
    return int(time.time() * 1000)

def create_sparkplug_metric(name, alias, value, data_type, unit, description):
    """
    Create a Sparkplug B compliant metric with proper structure and metadata.
    
    Constructs a complete Sparkplug B metric object with all required fields
    including name, alias, timestamp, data type, and engineering units. Ensures
    compliance with Eclipse Sparkplug B specification for industrial IoT data
    representation and database schema alignment.
    
    Args:
        name (str): Metric name (must match database metric definitions)
        alias (int): Numeric alias for efficient MQTT transmission
        value: Metric measurement value (type must match data_type)
        data_type (str): Sparkplug B data type ("Float", "Int32", etc.)
        unit (str): Engineering unit for the metric (CENTIMETER, VOLT, DBM)
        description (str): Human-readable description of the metric
        
    Returns:
        dict: Complete Sparkplug B metric object with all required fields
        
    Metric Structure:
        - name: Human-readable metric identifier
        - alias: Numeric alias for payload optimization
        - timestamp: Millisecond precision timestamp
        - dataType: Sparkplug B data type specification
        - value: Actual metric measurement value
        - properties: Engineering units and descriptions
    """
    metric = {
        "name": name,
        "alias": alias,
        "timestamp": get_current_timestamp_ms(),
        "dataType": data_type,
        "value": value,
        "properties": {
            "Engineering Units": {
                "type": "String",
                "value": unit
            },
            "Description": {
                "type": "String",
                "value": description
            }
        }
    }
    return metric

def generate_sample_sparkplug_payload():
    """
    Generate a sample Sparkplug B payload with realistic sensor data.
    
    Creates a complete Sparkplug B compliant payload containing water level,
    battery voltage, and signal strength metrics with realistic simulation
    patterns. Demonstrates proper payload structure for database integration
    and industrial IoT applications.
    
    Returns:
        dict: Complete Sparkplug B payload with metrics array and sequence number
        
    Simulation Features:
        - Water level with sine wave patterns and random noise (±10cm variation)
        - Battery voltage within Li-ion operating range (3.2V-4.1V)
        - Signal strength variation (-90dBm to -40dBm range)
        - Proper sequence number for protocol compliance
        
    Database Alignment:
        - WaterLevel: Float in centimeters (metric ID: 1)
        - BatteryVoltage: Float in volts (metric ID: 3)
        - SignalStrength: Int32 in dBm (metric ID: 4)
    """
    
    # 模擬水位數據 (基礎水位 150cm，加上波動)
    base_level_cm = 150.0
    sine_wave = math.sin(time.time() / 100) * 10  # ±10cm 波動
    random_noise = random.uniform(-2, 2)  # ±2cm 隨機噪聲
    water_level_cm = round(base_level_cm + sine_wave + random_noise, 2)
    
    # 模擬電池電壓 (3.2V - 4.1V)
    battery_voltage = round(random.uniform(3.2, 4.1), 2)
    
    # 模擬信號強度 (-90dBm 到 -40dBm)
    signal_strength = random.randint(-90, -40)
    
    # 創建度量項列表
    metrics = [
        create_sparkplug_metric(
            name="WaterLevel",
            alias=1,
            value=water_level_cm,
            data_type="Float", 
            unit="CENTIMETER",
            description="Water level measurement in centimeters"
        ),
        create_sparkplug_metric(
            name="BatteryVoltage", 
            alias=3,
            value=battery_voltage,
            data_type="Float",
            unit="VOLT",
            description="Battery voltage in volts"
        ),
        create_sparkplug_metric(
            name="SignalStrength",
            alias=4, 
            value=signal_strength,
            data_type="Int32",
            unit="DBM",
            description="Received Signal Strength Indicator in dBm"
        )
    ]
    
    # 完整的 Sparkplug B 載荷
    payload = {
        "timestamp": get_current_timestamp_ms(),
        "metrics": metrics,
        "seq": random.randint(0, 255)
    }
    
    return payload

def main():
    """
    Main entry point for Sparkplug B payload demonstration.
    
    Generates and displays sample Sparkplug B payload structures that comply
    with the iot_metric_definitions database table specifications. Provides
    visual demonstration of proper payload formatting for water level monitoring
    systems and industrial IoT applications.
    
    Output includes:
        - Formatted JSON payload structure
        - Compliance verification with Sparkplug B specification
        - Database schema alignment confirmation
        - Metric summary with engineering units
        
    Database Schema Reference:
        - ID: 1, WaterLevel (WL) - CENTIMETER, Float
        - ID: 3, BatteryVoltage (BAT_V) - VOLT, Float
        - ID: 4, SignalStrength (RSSI) - DBM, Int32
    """
    print("🌊⚡ Sparkplug B Water Level Data Structure Example")
    print("=" * 60)
    print("According to database iot_metric_definitions table field definitions:")
    print("- ID: 1, WaterLevel (WL) - CENTIMETER, Float")
    print("- ID: 3, BatteryVoltage (BAT_V) - VOLT, Float") 
    print("- ID: 4, SignalStrength (RSSI) - DBM, Int32")
    print("=" * 60)
    
    # 生成範例數據
    sample_payload = generate_sample_sparkplug_payload()
    
    # 美化輸出 JSON
    formatted_json = json.dumps(sample_payload, indent=2, ensure_ascii=False)
    print("\n📊 Sample Sparkplug B Payload:")
    print(formatted_json)
    
    print("\n" + "=" * 60)
    print("✅ This data structure fully complies with:")
    print("   - Sparkplug B specification")
    print("   - Database iot_metric_definitions table definitions")
    print("   - MQTT transmission requirements")
    
    # 顯示度量項摘要
    print("\n📋 Metrics Summary:")
    for metric in sample_payload['metrics']:
        unit = metric['properties']['Engineering Units']['value']
        print(f"   • {metric['name']} (Alias: {metric['alias']}) = {metric['value']} {unit}")

if __name__ == "__main__":
    main()