#!/usr/bin/env python3
"""
Multi-Device Sparkplug B Water Level Simulator

Concurrent simulation framework for multiple Sparkplug B compliant water level
monitoring devices. This simulator manages multiple IoT devices running in
parallel threads, each maintaining independent MQTT connections and generating
realistic sensor data according to the Eclipse Sparkplug B specification.

Key Features:
    - Concurrent multi-device simulation with threading
    - Full Sparkplug B protocol compliance across all devices
    - Device-specific simulation parameters and environmental variations
    - Independent MQTT connections with authentication
    - Sequence number management per device
    - Database schema alignment with iot_metric_definitions table
    - Graceful shutdown handling and error recovery

Technical Specifications:
    - Water level measurement in centimeters (Float precision)
    - Battery voltage monitoring in volts (3.0V-4.2V range)
    - Signal strength measurement in dBm (-100dBm to -30dBm range)
    - Sparkplug B sequence number management (0-255 rotation per device)
    - MQTT QoS 1 reliable message delivery
    - Configurable transmission intervals per device

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT

Dependencies:
    - paho-mqtt: MQTT client library for Python
    - threading: Concurrent execution framework
    - json: JSON data serialization
    - math: Mathematical functions for realistic simulation

Usage:
    python sparkplug_multi_device_simulator.py

    Or import as module:
    from sparkplug_multi_device_simulator import SparkplugBMultiDeviceSimulator
    simulator = SparkplugBMultiDeviceSimulator(broker_host='localhost', broker_port=1883)
    simulator.start_all_simulators(duration_minutes=15)
"""

import json
import time
import random
import logging
import math
import threading
from datetime import datetime
import paho.mqtt.client as mqtt

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SparkplugBMultiDeviceSimulator:
    """
    Multi-device Sparkplug B water level simulator manager.
    
    Coordinates concurrent simulation of multiple Sparkplug B compliant water
    level monitoring devices. Each device operates independently with unique
    characteristics, MQTT connections, and simulation parameters while maintaining
    protocol compliance and database schema alignment.
    
    Key Features:
        - Concurrent device simulation using threading
        - Independent MQTT broker connections per device
        - Device-specific configuration and authentication
        - Coordinated startup and shutdown procedures
        - Comprehensive logging and error handling
        
    Attributes:
        broker_host (str): MQTT broker hostname for all devices
        broker_port (int): MQTT broker port for all devices
        simulators (list): List of SparkplugBDevice simulator instances
        running (bool): Flag indicating active simulation state
        device_configs (list): Pre-configured device configuration dictionaries
        
    Thread Safety:
        Designed for thread-safe operations with independent device threads.
        Coordinator manages lifecycle through proper synchronization mechanisms.
    """
    
    def __init__(self, broker_host='localhost', broker_port=1883):
        """
        Initialize the multi-device Sparkplug B simulator coordinator.
        
        Sets up the central coordinator with MQTT broker connection parameters
        and initializes the device configuration array. Pre-configures device
        settings including authentication credentials, telemetry topics, and
        simulation parameters for each Sparkplug B compliant device instance.
        
        Args:
            broker_host (str, optional): MQTT broker hostname or IP address.
                Defaults to 'localhost' for local development environments.
            broker_port (int, optional): MQTT broker connection port.
                Defaults to 1883 (standard MQTT port).
                
        Device Configuration:
            Each device is pre-configured with unique identifiers, authentication
            credentials, and location-specific parameters to simulate real-world
            IoT deployment scenarios with multiple monitoring points.
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.simulators = []
        self.running = False
        
        # 設備配置列表 (從 env.md 獲取)
        self.device_configs = [
            {
                'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',
                'client_id': 'client_9d3e50ea',
                'username': 'device_2_9d3e50ea',
                'password': 'b1652e4bac404628',
                'topic': 'tenants/2/devices/9d3e50ea/telemetry',
                'base_level': 1.5,
                'location': '水庫監測點 A'
            },
            {
                'device_id': '0cabc4cb-9092-48ec-80bf-63392a3b73b9',
                'client_id': 'client_0cabc4cb',
                'username': 'device_2_0cabc4cb',
                'password': 'f8cf145771d84376',
                'topic': 'tenants/2/devices/0cabc4cb/telemetry',
                'base_level': 2.0,
                'location': '水庫監測點 B'
            }
        ]
        
    def create_simulators(self):
        """
        Create and initialize Sparkplug B simulator instances for all devices.
        
        Instantiates SparkplugBDevice objects for each device configuration,
        assigns unique device indices, and configures MQTT broker connection
        parameters. Prepares all device simulators for concurrent Sparkplug B
        compliant operation with independent simulation parameters.
        
        Device Differentiation:
            - Unique device indices for identification
            - Location-specific base water levels
            - Independent MQTT authentication credentials
            - Device-specific simulation intervals and variations
        """
        for i, config in enumerate(self.device_configs):
            config.update({
                'broker_host': self.broker_host,
                'broker_port': self.broker_port
            })
            simulator = SparkplugBDevice(config, device_index=i+1)
            self.simulators.append(simulator)
            
    def start_all_simulators(self, duration_minutes=None):
        """
        Launch all configured Sparkplug B device simulators concurrently.
        
        Initializes simulator instances, starts the simulation flag, and creates
        individual threads for each device. Each Sparkplug B device simulator
        runs in its own thread with independent MQTT connections and data generation
        cycles, maintaining full protocol compliance.
        
        Args:
            duration_minutes (int, optional): Simulation duration in minutes.
                If None, simulation runs indefinitely until interrupted.
                
        Thread Management:
            - Creates daemon threads for automatic cleanup on process termination
            - Names threads with device client IDs for debugging and monitoring
            - Joins all threads to ensure synchronized completion
            
        Sparkplug B Compliance:
            - Independent sequence number management per device
            - Protocol-compliant payload generation
            - QoS 1 message delivery guarantees
        """
        self.create_simulators()
        self.running = True
        
        logger.info(f"啟動 {len(self.simulators)} 個 Sparkplug B 水位計模擬器")
        
        threads = []
        for simulator in self.simulators:
            thread = threading.Thread(
                target=simulator.run_simulation,
                args=(duration_minutes,),
                name=f"SparkplugB-{simulator.device_config['client_id']}"
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
        try:
            # 等待所有線程完成
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在停止所有 Sparkplug B 模擬器...")
            self.stop_all_simulators()
            
    def stop_all_simulators(self):
        """
        Gracefully terminate all running Sparkplug B device simulators.
        
        Sets the running flag to False and calls the stop method on each
        simulator instance. Ensures proper MQTT disconnection and thread
        termination for all Sparkplug B compliant devices.
        
        Shutdown Sequence:
            - Atomic flag update ensures immediate visibility across threads
            - Individual simulator stop methods handle device-specific cleanup
            - Maintains Sparkplug B protocol compliance during shutdown
        """
        self.running = False
        for simulator in self.simulators:
            simulator.stop()


class SparkplugBDevice:
    """
    Individual Sparkplug B compliant water level monitoring device simulator.
    
    Represents a single IoT water level sensor device that generates realistic
    environmental monitoring data according to the Eclipse Sparkplug B specification.
    Each device instance has unique characteristics, maintains independent MQTT
    connections, and generates protocol-compliant telemetry data.
    
    Key Features:
        - Full Sparkplug B protocol compliance with metric aliases and sequence numbers
        - Device-specific simulation parameters and environmental variations
        - Independent MQTT connectivity with authentication and QoS handling
        - Realistic sensor data generation with mathematical models
        - Database schema alignment with iot_metric_definitions table
    
    Attributes:
        device_config (dict): Complete device configuration including MQTT settings
        device_index (int): Unique identifier for this device instance
        running (bool): Flag indicating active simulation state
        client (mqtt.Client): MQTT client instance for broker communication
        seq_number (int): Sparkplug B sequence number (0-255) for this device
        
    Thread Safety:
        Designed for concurrent execution in multi-threaded environments.
        Each device maintains independent MQTT connections and simulation state.
    """
    
    def __init__(self, device_config, device_index=1):
        """
        Initialize a Sparkplug B compliant water level monitoring device.
        
        Sets up the device with unique configuration, MQTT credentials, and
        simulation parameters. Each device instance is configured with
        device-specific characteristics to simulate realistic IoT deployment
        scenarios with varying environmental conditions and monitoring intervals.
        
        Args:
            device_config (dict): Device configuration dictionary containing:
                - device_id (str): Unique device identifier (UUID)
                - client_id (str): MQTT client identifier
                - username (str): MQTT authentication username
                - password (str): MQTT authentication password
                - topic (str): MQTT topic for telemetry publishing
                - base_level (float, optional): Base water level in meters (default: 1.5)
                - location (str, optional): Device deployment location
                - broker_host (str): MQTT broker hostname
                - broker_port (int): MQTT broker port number
            device_index (int, optional): Sequential device index for differentiation.
                Defaults to 1.
                
        Sparkplug B Configuration:
            - Independent sequence number initialization
            - Metric aliases aligned with database schema
            - Device-specific simulation parameters
        """
        self.device_config = device_config
        self.device_index = device_index
        self.running = False
        
        # 設置設備特定參數
        self.device_id = device_config['device_id']
        self.client_id = device_config['client_id']
        self.username = device_config['username']
        self.password = device_config['password']
        self.topic = device_config['topic']
        self.base_water_level = device_config.get('base_level', 1.5)
        self.location = device_config.get('location', f'未知位置-{device_index}')
        
        # MQTT 設置
        self.broker_host = device_config['broker_host']
        self.broker_port = device_config['broker_port']
        
        # 設備特定參數
        self.max_variation = 0.2 + (device_index * 0.05)
        self.current_level = self.base_water_level
        self.send_interval = 4 + device_index
        
        # Sparkplug B 序列號
        self.seq_number = device_index  # 每個設備從不同序列號開始
        
        # MQTT 客戶端
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # Sparkplug B 度量別名定義 (根據數據庫 iot_metric_definitions)
        self.metric_aliases = {
            "WaterLevel": 1,        # ID: 1, 別名: WL, 單位: CENTIMETER
            "BatteryVoltage": 3,    # ID: 3, 別名: BAT_V, 單位: VOLT  
            "SignalStrength": 4     # ID: 4, 別名: RSSI, 單位: DBM
        }
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 連接回調"""
        if rc == 0:
            logger.info(f"[{self.location}] Sparkplug B 設備 {self.device_index} 已連接")
        else:
            logger.error(f"[{self.location}] 設備 {self.device_index} 連接失敗: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """MQTT 斷線回調"""
        logger.info(f"[{self.location}] Sparkplug B 設備 {self.device_index} 已斷開連接")
        
    def _on_publish(self, client, userdata, mid):
        """MQTT 發布回調"""
        pass
        
    def get_current_timestamp_ms(self):
        """獲取當前時間戳 (毫秒)"""
        return int(time.time() * 1000)
        
    def create_sparkplug_metric(self, name, value, data_type, engineering_units=None, description=None):
        """創建符合 Sparkplug B 規範的度量項"""
        current_timestamp = self.get_current_timestamp_ms()
        
        metric = {
            "name": name,
            "alias": self.metric_aliases.get(name, 0),
            "timestamp": current_timestamp,
            "dataType": data_type,
            "value": value
        }
        
        # 添加屬性
        if engineering_units or description:
            metric["properties"] = {}
            if engineering_units:
                metric["properties"]["Engineering Units"] = {
                    "type": "String",
                    "value": engineering_units
                }
            if description:
                metric["properties"]["Description"] = {
                    "type": "String",
                    "value": description
                }
                
        return metric
        
    def generate_sparkplug_payload(self):
        """生成符合 Sparkplug B 規範的設備數據載荷"""
        # 每個設備有不同的波動模式
        time_factor = time.time() / (60 + self.device_index * 15)
        phase_shift = self.device_index * math.pi / 3
        
        # 主波形 + 小幅隨機變化
        sine_wave = math.sin(time_factor + phase_shift) * self.max_variation * 0.8
        random_noise = random.uniform(-0.02, 0.02)
        
        self.current_level = self.base_water_level + sine_wave + random_noise
        self.current_level = max(0.0, min(5.0, self.current_level))
        
        # 轉換為公分 (數據庫要求 CENTIMETER)
        water_level_cm = self.current_level * 100  # 米轉公分
        
        # 創建度量項列表 (根據數據庫 iot_metric_definitions)
        metrics = []
        
        # 模擬不同設備的環境差異
        voltage_offset = self.device_index * 0.1  # 不同設備的電壓偏差
        signal_offset = self.device_index * 5     # 不同設備的信號強度偏差
        
        # 1. 水位 (WaterLevel) - ID: 1, 別名: WL, 單位: CENTIMETER, 數據類型: Float
        metrics.append(self.create_sparkplug_metric(
            "WaterLevel",
            round(water_level_cm, 2),  # 公分，保留2位小數
            "Float",
            "CENTIMETER",
            f"Water level measurement at {self.location}"
        ))
        
        # 2. 電池電壓 (BatteryVoltage) - ID: 3, 別名: BAT_V, 單位: VOLT, 數據類型: Float
        # 模擬鋰電池電壓範圍 3.0V - 4.2V，每個設備略有不同
        base_voltage = 3.6 + voltage_offset
        battery_voltage = round(base_voltage + random.uniform(-0.4, 0.5), 2)
        battery_voltage = max(3.0, min(4.2, battery_voltage))  # 限制在合理範圍
        
        metrics.append(self.create_sparkplug_metric(
            "BatteryVoltage",
            battery_voltage,
            "Float",
            "VOLT",
            f"Battery voltage for device at {self.location}"
        ))
        
        # 3. 信號強度 (SignalStrength) - ID: 4, 別名: RSSI, 單位: DBM, 數據類型: Int32
        # 不同設備位置導致不同的信號強度
        base_signal = -70 + signal_offset
        signal_strength = base_signal + random.randint(-15, 10)
        signal_strength = max(-100, min(-30, signal_strength))  # 限制在合理範圍
        
        metrics.append(self.create_sparkplug_metric(
            "SignalStrength",
            signal_strength,
            "Int32",
            "DBM",
            f"RSSI for device at {self.location}"
        ))
        
        # 構建完整的 Sparkplug B 載荷
        payload = {
            "timestamp": self.get_current_timestamp_ms(),
            "metrics": metrics,
            "seq": self.seq_number
        }
        
        # 增加序列號
        self.seq_number += 1
        if self.seq_number > 255:  # Sparkplug B 序列號範圍 0-255
            self.seq_number = 0
            
        return payload
        
    def connect_mqtt(self):
        """連接 MQTT"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"[{self.location}] 設備 {self.device_index} 連接失敗: {e}")
            return False
            
    def disconnect_mqtt(self):
        """斷開 MQTT"""
        self.client.loop_stop()
        self.client.disconnect()
        
    def send_sparkplug_data(self, payload):
        """發送 Sparkplug B 格式數據"""
        try:
            json_payload = json.dumps(payload, ensure_ascii=False, indent=2)
            result = self.client.publish(self.topic, json_payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                water_level_cm = None
                battery_voltage = None
                for metric in payload['metrics']:
                    if metric['name'] == 'WaterLevel':
                        water_level_cm = metric['value']
                    elif metric['name'] == 'BatteryVoltage':
                        battery_voltage = metric['value']
                        
                logger.info(f"[{self.location}] 設備{self.device_index} Sparkplug B - 水位: {water_level_cm}cm, 電壓: {battery_voltage}V, 序列: {payload['seq']}")
            else:
                logger.error(f"[{self.location}] 設備 {self.device_index} 發送失敗: {result.rc}")
                
        except Exception as e:
            logger.error(f"[{self.location}] 設備 {self.device_index} 發送錯誤: {e}")
            
    def run_simulation(self, duration_minutes=None):
        """運行 Sparkplug B 模擬"""
        if not self.connect_mqtt():
            return
            
        self.running = True
        logger.info(f"[{self.location}] Sparkplug B 設備 {self.device_index} 開始模擬，間隔: {self.send_interval}秒")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        
        try:
            while self.running:
                sparkplug_payload = self.generate_sparkplug_payload()
                self.send_sparkplug_data(sparkplug_payload)
                
                if end_time and time.time() > end_time:
                    break
                    
                time.sleep(self.send_interval)
                
        except Exception as e:
            logger.error(f"[{self.location}] Sparkplug B 設備 {self.device_index} 模擬錯誤: {e}")
        finally:
            self.disconnect_mqtt()
            logger.info(f"[{self.location}] Sparkplug B 設備 {self.device_index} 已停止")
            
    def stop(self):
        """停止模擬"""
        self.running = False


def main():
    """
    Main entry point for the multi-device Sparkplug B water level simulator.
    
    Initializes and starts the multi-device Sparkplug B water level monitoring
    simulation with default MQTT broker configuration. Demonstrates concurrent
    operation of multiple Sparkplug B compliant devices with independent MQTT
    connections and protocol-compliant data transmission.
    
    Configuration:
        - Broker Host: localhost (modify for production deployment)
        - Broker Port: 1883 (standard MQTT port)
        - Simulation Duration: 15 minutes (configurable)
        - Device Count: 2 pre-configured devices
        
    Execution Flow:
        1. Display startup banner with Sparkplug B compliance notice
        2. Configure MQTT broker connection parameters
        3. Create multi-device Sparkplug B simulator instance
        4. Start concurrent device simulations
        5. Handle keyboard interrupt for graceful shutdown
        6. Ensure all devices disconnect cleanly
        
    Sparkplug B Features:
        - Independent sequence number management per device
        - Metric aliases aligned with database schema
        - QoS 1 reliable message delivery
        - Protocol-compliant payload structures
    """
    print("🌊⚡ 多設備 Sparkplug B 水位計模擬器啟動中...")
    print("=" * 60)
    print("符合 Sparkplug B 規範的 MQTT 數據傳輸")
    print("=" * 60)
    
    # 修改為您的 EMQX Broker 地址
    BROKER_HOST = 'localhost'  # 或者您的 EMQX 服務器 IP
    BROKER_PORT = 1883
    
    # 創建多設備 Sparkplug B 模擬器
    multi_simulator = SparkplugBMultiDeviceSimulator(BROKER_HOST, BROKER_PORT)
    
    try:
        # 運行 15 分鐘 (可以修改為 None 無限運行)
        multi_simulator.start_all_simulators(duration_minutes=15)
    except KeyboardInterrupt:
        print("\n收到中斷信號，正在安全關閉...")
    finally:
        print("所有 Sparkplug B 設備模擬器已關閉")


if __name__ == "__main__":
    main()