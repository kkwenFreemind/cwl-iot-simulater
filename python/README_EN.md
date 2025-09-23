# Water Level IoT Simulator

> 📖 **中文版本**: [README_ZH.md](README_ZH.md) - Chinese version of this documentation

This directory contains Python-based water level IoT device simulators for simulating water level sensor data and transmitting it to EMQX Broker via MQTT protocol.

## File Descriptions

### 1. `water_level_simulator.py` - Single Device Simulator

- Simulates a single water level monitoring device
- Sends sensor data including water level, temperature, humidity
- Supports MQTT connection and data transmission

### 2. `multi_device_simulator.py` - Multi-Device Simulator

- Simulates multiple water level monitoring devices concurrently
- Supports concurrent data transmission
- Each device has different data patterns and transmission intervals

### 3. `deviceInfo.md` - Device Configuration Information

- Contains device ID, MQTT client ID, authentication information
- Topic configuration details

## Installation Dependencies

```bash
pip install paho-mqtt
```

## Usage Instructions

### Single Device Simulator

```bash
python water_level_simulator.py
```

### Multi-Device Simulator

```bash
python multi_device_simulator.py
```

## Configuration Instructions

Before running the simulators, please ensure the following configurations are modified:

1. **MQTT Broker Address**: Change `broker_host` to your EMQX server IP address
2. **Device Authentication**: Verify device configuration information in `deviceInfo.md` is correct
3. **Topic**: Confirm telemetry topic paths are correct

## Data Format

The JSON data format sent by the simulators:

```json
{
  "deviceId": "9d3e50ea-e160-4e59-a98e-6b13f51e5e1f",
  "timestamp": "2025-09-23T10:30:00.123456",
  "waterLevel": 1.523,
  "temperature": 22.1,
  "humidity": 68.5,
  "batteryLevel": 87.2,
  "signalStrength": -65,
  "status": "normal"
}
```

## Key Features

- ✅ Realistic water level fluctuation simulation (sine wave + random noise)
- ✅ MQTT QoS 1 reliable transmission
- ✅ Multi-device concurrent support
- ✅ Detailed logging records
- ✅ Graceful program shutdown
- ✅ Device status monitoring
- ✅ Battery level simulation
- ✅ Signal strength simulation
