# Sparkplug B Water Level Simulator - sb_water_device_1

This simulator generates realistic water level, battery voltage, and signal strength data for the `sb_water_device_1` device using the **Eclipse Sparkplug B protocol with proper Protobuf encoding**.

## Device Configuration

Based on the database record from `iot_device` table:

- **Device ID**: `44547ced-e7fa-489b-8f04-891a30a0adb6`
- **Device Name**: `sb_water_device_1`
- **Protocol**: `sparkplug_b`
- **Community ID**: `1`
- **Edge Node ID**: `sb_water_device_1`
- **MQTT Client ID**: `spb_1_2_sb_water_device_1`
- **EMQX Username**: `device_2_44547ced`
- **EMQX Password**: `5e5d44bd67874f0c`
- **NBIRTH Topic**: `spBv1.0/1/NBIRTH/spb_1_2_sb_water_device_1`
- **NDATA Topic**: `spBv1.0/1/NDATA/spb_1_2_sb_water_device_1`

## Prerequisites

1. **Python 3.7+** installed
2. **paho-mqtt** library:

   ```bash
   pip install paho-mqtt
   ```

3. **tahu** library (Eclipse Tahu Python implementation for Sparkplug B):

   ```bash
   pip install tahu
   ```

4. **EMQX Broker** running on `localhost:1883` (or update `broker_host` in the config)

## Running the Simulator

### Option 1: Run the dedicated runner script

```bash
python run_sb_water_device_1.py
```

### Option 2: Run the main simulator directly

```bash
python sparkplug_water_level_simulator.py
```

## What the Simulator Does

The simulator generates and sends **Sparkplug B compliant Protobuf-encoded MQTT messages** containing:

1. **Water Level** (in centimeters) - Simulates realistic water level fluctuations using sine waves and random noise
2. **Battery Voltage** (in volts) - Simulates Li-ion battery voltage between 3.0V-4.2V
3. **Signal Strength** (in dBm) - Simulates RSSI values between -100dBm to -30dBm

### Sparkplug B Protocol Implementation

- **NBIRTH**: Sent once at startup to declare device online and define all metrics with complete metadata
- **NDATA**: Sent periodically with only metric values using aliases for efficient transmission
- **Proper Protobuf Encoding**: Uses Google Protocol Buffers instead of JSON for true Sparkplug B compliance
- **Sequence Numbers**: Automatic management with rollover (0-255)
- **QoS Levels**: NBIRTH uses QoS 0, NDATA uses QoS 1

### Sample Output

```text
🌊 Sparkplug B 水位計模擬器啟動中...
==================================================
INFO - 成功連接到 MQTT Broker - 設備: 44547ced-e7fa-489b-8f04-891a30a0adb6
INFO - 開始 Sparkplug B 水位數據模擬 - 設備: 44547ced-e7fa-489b-8f04-891a30a0adb6
INFO - Community ID: 1, Edge Node ID: sb_water_device_1
INFO - 發送間隔: 5秒
INFO - NBIRTH Topic: spBv1.0/1/NBIRTH/spb_1_2_sb_water_device_1
INFO - NDATA Topic: spBv1.0/1/NDATA/spb_1_2_sb_water_device_1
INFO - Sparkplug B NBIRTH 已發送 - 設備: 44547ced-e7fa-489b-8f04-891a30a0adb6
INFO - Sparkplug B NDATA 已發送 - 水位: 139.53cm, 序列號: 1
INFO - Sparkplug B NDATA 已發送 - 水位: 142.95cm, 序列號: 2
...
```

## Configuration

To modify the simulator behavior, edit the `device_config` dictionary in `run_sb_water_device_1.py`:

- Change `broker_host` to point to your EMQX broker
- Adjust `duration_minutes` for simulation duration (set to `None` for infinite run)
- Modify simulation parameters in the main simulator class

## Troubleshooting

1. **Connection Failed**: Ensure EMQX broker is running and accessible
2. **Authentication Error**: Verify username/password match the database records
3. **Import Error**: Install required dependencies with `pip install paho-mqtt tahu`
4. **Protobuf Errors**: Ensure tahu library is properly installed

## Stopping the Simulator

Press `Ctrl+C` to gracefully stop the simulation.
