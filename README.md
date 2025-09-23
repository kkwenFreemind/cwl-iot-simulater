# 🌊 Community Water Level IoT Simulator

A comprehensive IoT simulation suite for water level monitoring systems, implementing industry-standard Sparkplug B protocol with MQTT connectivity.

## 🚀 Features

- **Sparkplug B Compliant**: Full compliance with Eclipse Sparkplug B specification
- **Multi-Device Support**: Concurrent simulation of multiple water level sensors
- **Real-time MQTT**: Secure MQTT transmission with EMQX broker integration
- **Database Integration**: Metrics aligned with `iot_metric_definitions` table structure
- **Dynamic Simulation**: Realistic water level fluctuations with configurable parameters
- **Production Ready**: Comprehensive logging, error handling, and graceful shutdown

## 📊 Supported Metrics

| Metric ID | Name | Alias | Unit | Data Type | Description |
|-----------|------|-------|------|-----------|-------------|
| 1 | WaterLevel | WL | CENTIMETER | Float | Water level measurement |
| 3 | BatteryVoltage | BAT_V | VOLT | Float | Device battery voltage |
| 4 | SignalStrength | RSSI | DBM | Int32 | Signal strength indicator |

## 🏗️ Project Structure

```
cwl-iot-simulater/
├── python/                                    # Python simulators
│   ├── sparkplug_water_level_simulator.py    # Single device simulator
│   ├── sparkplug_multi_device_simulator.py   # Multi-device simulator
│   ├── sparkplug_payload_example.py          # Payload structure demo
│   ├── water_level_simulator.py              # Basic MQTT simulator
│   ├── multi_device_simulator.py             # Basic multi-device
│   ├── config.py                             # Configuration management
│   └── README.md                             # Python implementation docs
├── doc/                                       # Documentation
│   ├── env.md                                # Environment configuration
│   └── plan/                                 # Project planning documents
└── README.md                                 # This file
```

## ⚙️ Installation

### Prerequisites
- Python 3.7+
- MQTT Broker (EMQX recommended)

### Dependencies
```bash
pip install paho-mqtt
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/kkwenFreemind/cwl-iot-simulater.git
cd cwl-iot-simulater

# Install dependencies
pip install paho-mqtt

# Run single device simulator
python python/sparkplug_water_level_simulator.py

# Run multi-device simulator
python python/sparkplug_multi_device_simulator.py
```

## 📡 MQTT Configuration

Update the broker configuration in your chosen simulator:

```python
MQTT_CONFIG = {
    'broker_host': 'your-emqx-broker-ip',  # Replace with your broker
    'broker_port': 1883,
    'keepalive': 60,
    'qos': 1
}
```

## 🌊 Device Configuration

Each device is configured with:
- **Device ID**: Unique identifier (UUID format)
- **MQTT Client ID**: MQTT connection identifier
- **Credentials**: Username and password for broker authentication
- **Topic**: Telemetry data publishing endpoint

Example configuration:
```python
{
    'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',
    'client_id': 'client_9d3e50ea',
    'username': 'device_2_9d3e50ea',
    'password': 'b1652e4bac404628',
    'topic': 'tenants/2/devices/9d3e50ea/telemetry'
}
```

## 📈 Sparkplug B Payload Structure

```json
{
  "timestamp": 1727100000000,
  "metrics": [
    {
      "name": "WaterLevel",
      "alias": 1,
      "timestamp": 1727100000000,
      "dataType": "Float",
      "value": 152.75,
      "properties": {
        "Engineering Units": {
          "type": "String",
          "value": "CENTIMETER"
        },
        "Description": {
          "type": "String",
          "value": "Water level measurement in centimeters"
        }
      }
    }
  ],
  "seq": 42
}
```

## 🎯 Key Features

### Real-time Data Simulation
- **Water Level**: Dynamic fluctuations using sine wave patterns with realistic noise
- **Battery Voltage**: Simulated lithium battery discharge (3.2V - 4.1V)
- **Signal Strength**: Variable RSSI values (-90dBm to -40dBm)

### Sparkplug B Compliance
- ✅ Metric aliases for payload optimization
- ✅ Millisecond timestamps for precision
- ✅ Sequence number management (0-255 rotation)
- ✅ Engineering units and property descriptions
- ✅ Proper data type declarations

### Production Features
- **Logging**: Comprehensive logging with configurable levels
- **Error Handling**: Graceful error recovery and reporting
- **Signal Handling**: Clean shutdown on interruption
- **Thread Safety**: Safe concurrent operations for multi-device scenarios

## 🔧 Configuration Options

### Simulation Parameters
```python
SIMULATION_CONFIG = {
    'max_water_level': 500.0,      # Maximum water level (cm)
    'min_water_level': 0.0,        # Minimum water level (cm)
    'max_variation': 30.0,         # Maximum fluctuation (cm)
    'send_interval': 5,            # Data transmission interval (seconds)
    'battery_range': (3.0, 4.2),   # Battery voltage range (V)
    'signal_range': (-100, -30)     # Signal strength range (dBm)
}
```

## 🌐 Integration

This simulator is designed to integrate with:
- **EMQX MQTT Broker**: Enterprise-grade MQTT messaging
- **PostgreSQL**: Database with `iot_metric_definitions` table
- **Eclipse Sparkplug B**: Industrial IoT standard protocol
- **IoT Platforms**: ThingsBoard, AWS IoT, Azure IoT, etc.

## 📚 Documentation

- [Environment Setup](doc/env.md) - Device credentials and configuration
- [Project Planning](doc/plan/) - Development phases and specifications
- [Python Implementation](python/README.md) - Detailed Python documentation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version

**v1.0.0** - Initial release with Sparkplug B water level simulators

## 👥 Authors

- **kkwenFreemind** - *Initial work* - [GitHub](https://github.com/kkwenFreemind)

## 🙏 Acknowledgments

- Eclipse Sparkplug B Working Group for the specification
- Eclipse Paho MQTT Python Client contributors
- Community water level monitoring project stakeholders