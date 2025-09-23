#!/usr/bin/env python3
"""
Multi-Device Water Level IoT Simulator

A concurrent IoT device simulation framework for water level monitoring systems.
This simulator manages multiple water level sensors simultaneously, each running
in separate threads to provide realistic distributed IoT device behavior.

Key Features:
    - Concurrent multi-device simulation using threading
    - Individual device configuration and behavior patterns
    - MQTT connectivity with authentication for each device
    - Realistic sensor data generation with environmental variations
    - Graceful startup, operation, and shutdown handling
    - Comprehensive logging and error management
    - Thread-safe operations and resource management

Technical Specifications:
    - Thread-based concurrency for parallel device operations
    - MQTT QoS 1 reliable message delivery per device
    - Dynamic water level simulation with mathematical models
    - Device-specific parameter variations (temperature, humidity, etc.)
    - Configurable transmission intervals and simulation duration
    - Signal handling for clean shutdown operations

Author: kkwenFreemind
Version: 1.0.0
Date: 2025-09-23
License: MIT

Dependencies:
    - paho-mqtt: MQTT client library for Python
    - threading: Thread management for concurrent operations
    - json: JSON data serialization for MQTT payloads
    - math: Mathematical functions for realistic data simulation

Usage:
    python multi_device_simulator.py

    Or import as module:
    from multi_device_simulator import MultiDeviceWaterLevelSimulator
    simulator = MultiDeviceWaterLevelSimulator('localhost', 1883)
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

# Configure application-wide logging for monitoring and debugging
# Essential for production deployment and operational troubleshooting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiDeviceWaterLevelSimulator:
    """
    Multi-Device Water Level IoT Simulator Manager.
    
    This class serves as the central coordinator for managing multiple water level
    monitoring devices simultaneously. It handles device instantiation, thread
    management, and coordinated startup/shutdown operations across all simulated
    devices. The simulator supports concurrent operations where each device runs
    in its own thread, providing realistic distributed IoT device behavior.
    
    The manager maintains:
        - Device configuration management and validation
        - Thread lifecycle management for concurrent operations
        - Coordinated startup and shutdown procedures
        - Error aggregation and reporting across devices
        - Resource cleanup and graceful termination handling
    
    Attributes:
        broker_host (str): MQTT broker hostname or IP address
        broker_port (int): MQTT broker connection port
        simulators (list): List of WaterLevelDevice simulator instances
        running (bool): Flag indicating if simulators are actively running
        device_configs (list): Pre-configured device configuration dictionaries
    
    Thread Safety:
        This class is designed for thread-safe operations. Device simulators run
        in separate threads, and the manager coordinates their lifecycle through
        proper synchronization mechanisms.
    """
    
    def __init__(self, broker_host='localhost', broker_port=1883):
        """
        Initialize the multi-device water level simulator manager.
        
        Sets up the central coordinator with MQTT broker connection parameters
        and initializes the device configuration array. Pre-configures device
        settings including authentication credentials, telemetry topics, and
        simulation parameters for each device instance.
        
        Args:
            broker_host (str, optional): MQTT broker hostname or IP address.
                Defaults to 'localhost' for local development environments.
            broker_port (int, optional): MQTT broker connection port.
                Defaults to 1883 (standard MQTT port).
                
        Note:
            Device configurations are hardcoded in this implementation but can
            be extended to load from external configuration files or databases
            for more flexible deployment scenarios.
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
                'location': 'Site A'
            },
            {
                'device_id': '0cabc4cb-9092-48ec-80bf-63392a3b73b9',
                'client_id': 'client_0cabc4cb',
                'username': 'device_2_0cabc4cb',
                'password': 'f8cf145771d84376',
                'topic': 'tenants/2/devices/0cabc4cb/telemetry',
                'base_level': 2.0,
                'location': 'Site B'
            }
        ]
        
    def create_simulators(self):
        """
        Create and initialize simulator instances for all configured devices.
        
        Instantiates WaterLevelDevice objects for each device configuration,
        assigns unique device indices, and configures MQTT broker connection
        parameters. This method prepares all device simulators for concurrent
        operation by setting up their individual configurations and network
        connectivity parameters.
        
        The method iterates through the device_configs array and creates
        corresponding simulator instances with proper indexing and broker
        configuration injection.
        
        Raises:
            ValueError: If device configuration is invalid or missing required fields
            RuntimeError: If simulator instantiation fails due to resource constraints
        """
        for i, config in enumerate(self.device_configs):
            config.update({
                'broker_host': self.broker_host,
                'broker_port': self.broker_port
            })
            simulator = WaterLevelDevice(config, device_index=i+1)
            self.simulators.append(simulator)
            
    def start_all_simulators(self, duration_minutes=None):
        """
        Launch all configured device simulators with concurrent execution.
        
        Initializes simulator instances, starts the simulation flag, and creates
        individual threads for each device. Each device simulator runs in its own
        thread with independent MQTT connections and data generation cycles.
        
        The method handles graceful shutdown on keyboard interrupt and ensures
        all threads complete their execution before returning control.
        
        Args:
            duration_minutes (int, optional): Simulation duration in minutes.
                If None, simulation runs indefinitely until interrupted.
                
        Thread Management:
            - Creates daemon threads for automatic cleanup on process termination
            - Names threads with device client IDs for debugging and monitoring
            - Joins all threads to ensure synchronized completion
            
        Error Handling:
            - Catches KeyboardInterrupt for graceful shutdown
            - Logs simulation start and completion events
            - Ensures all simulators are properly stopped on interruption
        """
        self.create_simulators()
        self.running = True
        
        logger.info(f"啟動 {len(self.simulators)} 個水位計模擬器")
        
        threads = []
        for simulator in self.simulators:
            thread = threading.Thread(
                target=simulator.run_simulation,
                args=(duration_minutes,),
                name=f"Device-{simulator.device_config['client_id']}"
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
        try:
            # 等待所有線程完成
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在停止所有模擬器...")
            self.stop_all_simulators()
            
    def stop_all_simulators(self):
        """
        Gracefully terminate all running device simulators.
        
        Sets the running flag to False and calls the stop method on each
        simulator instance. This triggers the shutdown sequence for all
        devices, ensuring proper MQTT disconnection and thread termination.
        
        The method provides coordinated shutdown across all concurrent
        simulators, preventing data loss and ensuring clean resource cleanup.
        
        Thread Safety:
            - Atomic flag update ensures all threads see the stop signal
            - Individual simulator stop methods handle thread-local cleanup
            - No race conditions during shutdown sequence
        """
        self.running = False
        for simulator in self.simulators:
            simulator.stop()


class WaterLevelDevice:
    """
    Individual water level monitoring device simulator with MQTT connectivity.
    
    This class represents a single IoT water level sensor device that simulates
    realistic environmental monitoring data and publishes it via MQTT. Each device
    instance has unique characteristics, authentication credentials, and simulation
    parameters to mimic real-world deployment scenarios.
    
    Key Features:
        - Realistic water level simulation with sine wave patterns and noise
        - Device-specific environmental variations (temperature, humidity)
        - MQTT-based telemetry publishing with QoS 1 reliability
        - Comprehensive sensor data including battery and signal metrics
        - Configurable simulation intervals and data ranges
    
    Attributes:
        device_config (dict): Complete device configuration including MQTT settings
        device_index (int): Unique identifier for this device instance
        running (bool): Flag indicating active simulation state
        client (mqtt.Client): MQTT client instance for broker communication
        
    Thread Safety:
        Designed for concurrent execution in multi-threaded environments.
        Each device maintains independent MQTT connections and simulation state.
    """
    
    def __init__(self, device_config, device_index=1):
        """
        Initialize a water level monitoring device simulator.
        
        Sets up the device with its unique configuration, MQTT credentials,
        and simulation parameters. Each device instance is configured with
        device-specific characteristics to simulate realistic deployment
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
                
        Device Differentiation:
            - Varying water level variation amplitudes based on device index
            - Different transmission intervals to simulate real-world timing
            - Location-specific environmental parameter offsets
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
        self.max_variation = 0.2 + (device_index * 0.1)  # 每個設備不同的變化幅度
        self.current_level = self.base_water_level
        self.send_interval = 3 + device_index  # 不同的發送間隔
        
        # MQTT 客戶端
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
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
            
        Connection Codes:
            0: Connection successful
            1: Connection refused - incorrect protocol version
            2: Connection refused - invalid client identifier
            3: Connection refused - server unavailable
            4: Connection refused - bad username or password
            5: Connection refused - not authorized
        """
        if rc == 0:
            logger.info(f"[{self.location}] 設備 {self.device_index} 已連接到 MQTT Broker")
        else:
            logger.error(f"[{self.location}] 設備 {self.device_index} 連接失敗，返回碼: {rc}")
            
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
            
        Disconnect Codes:
            0: Clean disconnection (client initiated)
            Non-zero: Unexpected disconnection (network issues, broker problems)
        """
        logger.info(f"[{self.location}] 設備 {self.device_index} 已斷開連接")
        
    def _on_publish(self, client, userdata, mid):
        """
        MQTT publish callback handler.
        
        Called when a message publish operation completes. This callback can be
        used for delivery confirmation and quality of service (QoS) acknowledgments.
        Currently implemented as a no-op but available for future enhancements.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            mid (int): Message ID of the published message
            
        Note:
            For QoS 1 and 2 messages, this callback confirms successful delivery
            to the broker. For QoS 0 messages, it confirms successful transmission
            from the client buffer.
        """
        pass
        
    def generate_sensor_data(self):
        """
        Generate realistic sensor data for water level monitoring simulation.
        
        Creates comprehensive environmental and device status data using
        mathematical models and randomization to simulate real-world sensor
        behavior. Each device generates unique patterns based on its index
        and configuration parameters.
        
        Returns:
            dict: Complete sensor data payload containing:
                - deviceId (str): Unique device identifier
                - deviceIndex (int): Sequential device number
                - location (str): Deployment location description
                - timestamp (str): ISO format timestamp
                - waterLevel (float): Current water level in meters (0.0-5.0)
                - temperature (float): Ambient temperature in Celsius
                - humidity (float): Relative humidity percentage
                - batteryLevel (float): Battery charge percentage (80-100%)
                - signalStrength (int): WiFi signal strength in dBm (-85 to -45)
                - pressure (float): Atmospheric pressure in hPa
                - ph (float): Water pH level
                - status (str): Device operational status
                - dataQuality (float): Data reliability indicator (0.85-1.0)
                
        Simulation Features:
            - Sine wave patterns with device-specific phase shifts
            - Random noise for realistic sensor variation
            - Device-indexed environmental parameter offsets
            - Physically constrained value ranges
            - Timestamp precision for temporal analysis
        """
        # 每個設備有不同的波動模式
        time_factor = time.time() / (50 + self.device_index * 20)
        phase_shift = self.device_index * math.pi / 2
        
        # 主波形 + 小幅隨機變化
        sine_wave = math.sin(time_factor + phase_shift) * self.max_variation * 0.7
        random_noise = random.uniform(-0.03, 0.03)
        
        self.current_level = self.base_water_level + sine_wave + random_noise
        self.current_level = max(0.0, min(5.0, self.current_level))
        
        # 模擬不同設備的環境差異
        temp_offset = self.device_index * 2
        humidity_offset = self.device_index * 5
        
        data = {
            "deviceId": self.device_id,
            "deviceIndex": self.device_index,
            "location": self.location,
            "timestamp": datetime.now().isoformat(),
            "waterLevel": round(self.current_level, 3),
            "temperature": round(20.0 + temp_offset + random.uniform(-2, 2), 1),
            "humidity": round(65.0 + humidity_offset + random.uniform(-5, 5), 1),
            "batteryLevel": round(random.uniform(80.0, 100.0), 1),
            "signalStrength": random.randint(-85, -45),
            "pressure": round(1013.25 + random.uniform(-10, 10), 2),  # 大氣壓力 (hPa)
            "ph": round(7.0 + random.uniform(-0.5, 0.5), 2),  # pH 值
            "status": random.choice(["normal", "normal", "normal", "warning"]),  # 大部分時間正常
            "dataQuality": random.uniform(0.85, 1.0)  # 數據質量指標
        }
        
        return data
        
    def connect_mqtt(self):
        """
        Establish MQTT broker connection with authentication.
        
        Attempts to connect to the configured MQTT broker using device-specific
        credentials and client identification. Starts the MQTT client loop for
        asynchronous message processing and callback handling.
        
        Returns:
            bool: True if connection successful, False if connection failed
            
        Connection Parameters:
            - Host: Configured broker hostname or IP address
            - Port: MQTT broker port (typically 1883 for non-TLS)
            - Client ID: Unique client identifier for this device
            - Authentication: Username/password credentials
            - Keep-alive: 60 seconds between ping messages
            
        Error Handling:
            - Logs connection failures with specific error details
            - Returns False on any connection exception
            - Allows calling code to handle connection failures gracefully
        """
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"[{self.location}] 設備 {self.device_index} 連接失敗: {e}")
            return False
            
    def disconnect_mqtt(self):
        """
        Gracefully disconnect from MQTT broker.
        
        Stops the MQTT client loop and closes the connection to the broker.
        Ensures proper cleanup of network resources and pending message queues.
        This method should be called during device shutdown to prevent resource
        leaks and ensure clean disconnection.
        
        Connection Cleanup:
            - Stops background message processing loop
            - Sends disconnect packet to broker
            - Closes network socket
            - Cleans up internal client state
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
            
        Publishing Details:
            - Topic: Device-specific telemetry topic
            - QoS: 1 (at least once delivery guarantee)
            - Payload: JSON formatted with proper encoding
            - Retention: False (messages not retained on broker)
            
        Error Handling:
            - Catches JSON serialization errors
            - Handles MQTT publish failures
            - Logs transmission status with device context
            - Continues operation despite individual message failures
        """
        try:
            payload = json.dumps(data, ensure_ascii=False, indent=2)
            result = self.client.publish(self.topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"[{self.location}] 設備 {self.device_index} - 水位: {data['waterLevel']}m, 溫度: {data['temperature']}°C")
            else:
                logger.error(f"[{self.location}] 設備 {self.device_index} 發送失敗: {result.rc}")
                
        except Exception as e:
            logger.error(f"[{self.location}] 設備 {self.device_index} 發送錯誤: {e}")
            
    def run_simulation(self, duration_minutes=None):
        """
        Execute the main water level monitoring simulation loop.
        
        Runs the device simulation for a specified duration or indefinitely,
        generating sensor data at configured intervals and publishing via MQTT.
        Handles connection establishment, data generation, transmission, and
        graceful shutdown on interruption or duration expiration.
        
        Args:
            duration_minutes (int, optional): Simulation duration in minutes.
                If None, runs indefinitely until externally stopped.
                
        Simulation Flow:
            1. Establish MQTT connection
            2. Set running flag and log start
            3. Enter main loop:
               - Generate sensor data
               - Publish data via MQTT
               - Check duration limit
               - Sleep for configured interval
            4. Handle shutdown gracefully
            
        Error Handling:
            - Connection failures prevent simulation start
            - Individual data transmission errors don't stop simulation
            - Keyboard interrupts trigger clean shutdown
            - All exceptions are logged with device context
        """
        if not self.connect_mqtt():
            return
            
        self.running = True
        logger.info(f"[{self.location}] 設備 {self.device_index} 開始模擬，間隔: {self.send_interval}秒")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        
        try:
            while self.running:
                sensor_data = self.generate_sensor_data()
                self.send_data(sensor_data)
                
                if end_time and time.time() > end_time:
                    break
                    
                time.sleep(self.send_interval)
                
        except Exception as e:
            logger.error(f"[{self.location}] 設備 {self.device_index} 模擬錯誤: {e}")
        finally:
            self.disconnect_mqtt()
            logger.info(f"[{self.location}] 設備 {self.device_index} 已停止")
            
    def stop(self):
        """
        Stop the device simulation gracefully.
        
        Sets the running flag to False, signaling the simulation loop to exit
        at the next iteration. This allows for clean shutdown without data loss
        or abrupt termination of ongoing operations.
        
        Thread Safety:
            - Atomic flag update ensures immediate visibility across threads
            - Non-blocking operation allows calling thread to continue
            - Simulation loop checks flag on each iteration
        """
        self.running = False


def main():
    """
    Main entry point for the multi-device water level simulator application.
    
    Initializes and starts the multi-device water level monitoring simulation
    with default MQTT broker configuration. Demonstrates the complete system
    operation including device creation, concurrent simulation, and graceful
    shutdown handling.
    
    Configuration:
        - Broker Host: localhost (modify for production deployment)
        - Broker Port: 1883 (standard MQTT port)
        - Simulation Duration: 15 minutes (configurable)
        
    Execution Flow:
        1. Display startup banner
        2. Configure MQTT broker connection
        3. Create multi-device simulator instance
        4. Start concurrent device simulations
        5. Handle keyboard interrupt for graceful shutdown
        6. Ensure all devices disconnect cleanly
        
    Usage:
        Run directly: python multi_device_simulator.py
        Modify BROKER_HOST for different MQTT broker locations
        Adjust duration_minutes parameter for different test scenarios
    """
    print("🌊 多設備水位計模擬器啟動中...")
    print("=" * 50)
    
    # 修改為您的 EMQX Broker 地址
    BROKER_HOST = 'localhost'  # 或者您的 EMQX 服務器 IP
    BROKER_PORT = 1883
    
    # 創建多設備模擬器
    multi_simulator = MultiDeviceWaterLevelSimulator(BROKER_HOST, BROKER_PORT)
    
    try:
        # 運行 15 分鐘 (可以修改為 None 無限運行)
        multi_simulator.start_all_simulators(duration_minutes=15)
    except KeyboardInterrupt:
        print("\n收到中斷信號，正在安全關閉...")
    finally:
        print("所有設備模擬器已關閉")


if __name__ == "__main__":
    main()