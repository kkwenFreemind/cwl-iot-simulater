#!/usr/bin/env python3
"""
Water Level Simulator - MQTT Data Transmission

Simulates water level sensor data and transmits it to EMQX MQTT Broker.
This basic simulator provides fundamental water level monitoring capabilities
with MQTT connectivity for IoT applications and testing scenarios.

Features:
    - Realistic water level simulation with sine wave patterns
    - MQTT QoS 1 reliable transmission
    - Comprehensive sensor data (temperature, humidity, battery, signal)
    - Configurable transmission intervals
    - Graceful error handling and logging

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT
"""

import json
import time
import random
import logging
import math
from datetime import datetime
import paho.mqtt.client as mqtt

# Configure application-wide logging for monitoring and debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WaterLevelSimulator:
    """
    Basic water level monitoring device simulator with MQTT connectivity.
    
    This class simulates a single water level sensor that generates realistic
    environmental data and transmits it via MQTT. It provides fundamental IoT
    device simulation capabilities for testing and development purposes.
    
    Key Features:
        - Dynamic water level simulation using mathematical models
        - Multi-sensor data generation (temperature, humidity, battery, signal)
        - MQTT-based telemetry with QoS 1 reliability
        - Configurable simulation parameters and transmission intervals
        
    Attributes:
        device_id (str): Unique device identifier (UUID format)
        client_id (str): MQTT client connection identifier
        username (str): EMQX broker authentication username
        password (str): EMQX broker authentication password
        topic (str): MQTT telemetry data publication topic
        broker_host (str): MQTT broker hostname or IP address
        broker_port (int): MQTT broker connection port
        client (mqtt.Client): Paho MQTT client instance
        current_level (float): Current simulated water level in meters
        send_interval (int): Data transmission interval in seconds
    """
    
    def __init__(self, device_config):
        """
        Initialize the water level simulator with device configuration.
        
        Sets up MQTT client connection, authentication parameters, and simulation
        variables for basic water level monitoring. Configures callback handlers
        for connection events and establishes baseline simulation parameters.
        
        Args:
            device_config (dict): Device configuration dictionary containing:
                - device_id (str): Unique device identifier
                - client_id (str): MQTT client ID for connection
                - username (str): EMQX authentication username
                - password (str): EMQX authentication password
                - topic (str): MQTT telemetry topic for data publication
                - broker_host (str, optional): MQTT broker address (default: 'localhost')
                - broker_port (int, optional): MQTT broker port (default: 1883)
                
        Simulation Parameters:
            - Base water level: 1.5 meters
            - Maximum variation: ±0.3 meters
            - Transmission interval: 5 seconds
        """
        self.device_id = device_config['device_id']
        self.client_id = device_config['client_id']
        self.username = device_config['username']
        self.password = device_config['password']
        self.topic = device_config['topic']
        self.broker_host = device_config.get('broker_host', 'localhost')
        self.broker_port = device_config.get('broker_port', 1883)
        
        # MQTT 客戶端設置
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # 水位模擬參數
        self.base_water_level = 1.5  # 基礎水位 (米)
        self.max_variation = 0.3     # 最大變化幅度 (米)
        self.current_level = self.base_water_level
        
        # 發送間隔 (秒)
        self.send_interval = 5
        
    def _on_connect(self, client, userdata, flags, rc):
        """
        MQTT connection callback handler.
        
        Called automatically when the MQTT client connects or fails to connect
        to the broker. Logs connection status with device-specific information
        for monitoring and debugging purposes.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            flags: Connection flags from the broker
            rc (int): Connection result code (0 = success, non-zero = failure)
        """
        if rc == 0:
            logger.info(f"成功連接到 MQTT Broker - 設備: {self.device_id}")
        else:
            logger.error(f"連接失敗，返回碼: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """
        MQTT disconnection callback handler.
        
        Called automatically when the MQTT client disconnects from the broker.
        Logs disconnection events with device context for monitoring connection
        stability and troubleshooting network issues.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            rc (int): Disconnect reason code
        """
        logger.info(f"已斷開 MQTT 連接 - 設備: {self.device_id}")
        
    def _on_publish(self, client, userdata, mid):
        """
        MQTT publish callback handler.
        
        Called when a message publish operation completes. This callback can be
        used for delivery confirmation and quality of service (QoS) acknowledgments.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            mid (int): Message ID of the published message
        """
        logger.debug(f"消息已發布，消息ID: {mid}")
        
    def generate_water_level_data(self):
        """
        Generate simulated water level sensor data.
        
        Creates realistic environmental monitoring data using mathematical models
        that simulate natural water level fluctuations. Combines sine wave patterns
        with random noise to create believable sensor readings.
        
        Returns:
            dict: Complete sensor data payload containing:
                - deviceId (str): Unique device identifier
                - timestamp (str): ISO format timestamp
                - waterLevel (float): Current water level in meters (0.0-3.0)
                - temperature (float): Ambient temperature in Celsius (18.0-25.0)
                - humidity (float): Relative humidity percentage (60.0-80.0)
                - batteryLevel (float): Battery charge percentage (85.0-100.0)
                - signalStrength (int): WiFi signal strength in dBm (-80 to -50)
                - status (str): Device operational status
                
        Simulation Features:
            - Sine wave water level patterns with configurable amplitude
            - Random noise for realistic sensor variation
            - Physically constrained value ranges
            - Multi-sensor environmental data generation
        """
        # 模擬水位波動（正弦波 + 隨機噪聲）
        time_factor = time.time() / 100  # 緩慢變化
        sine_wave = math.sin(time_factor) * 0.1
        random_noise = random.uniform(-0.05, 0.05)
        
        self.current_level = self.base_water_level + sine_wave + random_noise
        
        # 確保水位在合理範圍內
        self.current_level = max(0.0, min(3.0, self.current_level))
        
        # 生成完整的傳感器數據
        data = {
            "deviceId": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "waterLevel": round(self.current_level, 3),  # 水位 (米)
            "temperature": round(random.uniform(18.0, 25.0), 1),  # 溫度 (攝氏度)
            "humidity": round(random.uniform(60.0, 80.0), 1),     # 濕度 (%)
            "batteryLevel": round(random.uniform(85.0, 100.0), 1), # 電池電量 (%)
            "signalStrength": random.randint(-80, -50),           # 信號強度 (dBm)
            "status": "normal"  # 設備狀態
        }
        
        return data
        
    def connect(self):
        """
        Establish MQTT broker connection with authentication.
        
        Attempts to connect to the configured MQTT broker using device-specific
        credentials and client identification. Starts the MQTT client loop for
        asynchronous message processing and callback handling.
        
        Returns:
            bool: True if connection successful, False if connection failed
        """
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"連接失敗: {e}")
            return False
            
    def disconnect(self):
        """
        Gracefully disconnect from MQTT broker.
        
        Stops the MQTT client loop and closes the connection to the broker.
        Ensures proper cleanup of network resources and pending message queues.
        """
        self.client.loop_stop()
        self.client.disconnect()
        
    def send_data(self, data):
        """
        Publish sensor data to MQTT broker with quality of service guarantees.
        
        Serializes sensor data to JSON format and publishes it to the device's
        configured MQTT topic with QoS 1 reliability. Logs successful transmissions
        and handles publish failures gracefully.
        
        Args:
            data (dict): Sensor data dictionary to be published
        """
        try:
            payload = json.dumps(data, ensure_ascii=False, indent=2)
            result = self.client.publish(self.topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"數據已發送 - 水位: {data['waterLevel']}m, Topic: {self.topic}")
            else:
                logger.error(f"發送失敗，錯誤碼: {result.rc}")
                
        except Exception as e:
            logger.error(f"發送數據時發生錯誤: {e}")
            
    def start_simulation(self, duration_minutes=None):
        """
        Execute the main water level monitoring simulation loop.
        
        Runs the device simulation for a specified duration or indefinitely,
        generating sensor data at configured intervals and publishing via MQTT.
        Handles connection establishment, data generation, transmission, and
        graceful shutdown on interruption or duration expiration.
        
        Args:
            duration_minutes (int, optional): Simulation duration in minutes.
                If None, runs indefinitely until interrupted.
        """
        if not self.connect():
            return
            
        logger.info(f"開始水位數據模擬 - 設備: {self.device_id}")
        logger.info(f"發送間隔: {self.send_interval}秒")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        
        try:
            while True:
                # 生成並發送數據
                water_data = self.generate_water_level_data()
                self.send_data(water_data)
                
                # 檢查是否已達到運行時間
                if end_time and time.time() > end_time:
                    break
                    
                # 等待下次發送
                time.sleep(self.send_interval)
                
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在停止模擬器...")
        except Exception as e:
            logger.error(f"模擬過程中發生錯誤: {e}")
        finally:
            self.disconnect()
            logger.info("水位模擬器已停止")


def main():
    """
    Main entry point for the basic water level simulator application.
    
    Initializes and starts the water level monitoring simulation with default
    MQTT broker configuration. Demonstrates fundamental IoT device simulation
    capabilities including sensor data generation and MQTT transmission.
    
    Configuration:
        - Broker Host: localhost (modify for production deployment)
        - Broker Port: 1883 (standard MQTT port)
        - Simulation Duration: 10 minutes (configurable)
        
    Device Configuration:
        Pre-configured with sample device credentials from env.md
        Modify broker_host for different MQTT broker locations
    """
    
    # 設備配置 (從 env.md 獲取)
    device_config = {
        'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',
        'client_id': 'client_9d3e50ea',
        'username': 'device_2_9d3e50ea',
        'password': 'b1652e4bac404628',
        'topic': 'tenants/2/devices/9d3e50ea/telemetry',
        'broker_host': 'localhost',  # 請修改為您的 EMQX Broker 地址
        'broker_port': 1883
    }
    
    # 創建並啟動模擬器
    simulator = WaterLevelSimulator(device_config)
    
    # 運行 10 分鐘 (可以修改為 None 無限運行)
    simulator.start_simulation(duration_minutes=10)


if __name__ == "__main__":
    main()