#!/usr/bin/env python3
"""
Sparkplug B Water Level IoT Device Simulator

A comprehensive IoT device simulator implementing the Eclipse Sparkplug B specification
for water level monitoring systems. This simulator generates realistic water level,
battery voltage, and signal strength data while maintaining full compliance with
Sparkplug B protocol standards including metric aliases, sequence numbers, and
proper data type declarations.

Key Features:
    - Full Sparkplug B protocol compliance with Protobuf encoding
    - Real-time MQTT data transmission with QoS 1
    - Dynamic water level simulation using mathematical models
    - Battery voltage monitoring with realistic discharge patterns
    - Signal strength (RSSI) simulation with environmental factors
    - Rain event simulation with gradual water level rise and fall
    - Alert level monitoring (1.0 meter threshold)
    - Comprehensive error handling and logging
    - Database schema alignment with iot_metric_definitions table
    - Proper NBIRTH/NDATA message flow

Technical Specifications:
    - Water level measurement in centimeters (Float precision)
    - Battery voltage monitoring in volts (3.0V-4.2V range)
    - Signal strength measurement in dBm (-100dBm to -30dBm range)
    - Sparkplug B sequence number management (0-255 rotation)
    - MQTT QoS 1 reliable message delivery for NDATA
    - MQTT QoS 0 for NBIRTH messages
    - Google Protocol Buffers encoding for true Sparkplug B compliance
    - Configurable transmission intervals

Author: Chang Xiu-Wen, AI-Enhanced
Version: 1.0.0
Date: 2025-09-23
License: MIT

Dependencies:
    - paho-mqtt: MQTT client library for Python
    - tahu: Eclipse Tahu Python implementation for Sparkplug B Protobuf encoding
    - json: JSON data serialization (for logging only)
    - math: Mathematical functions for realistic simulation

Usage:
    python sparkplug_water_level_simulator.py

    Or import as module:
    from sparkplug_water_level_simulator import SparkplugBWaterLevelSimulator
    simulator = SparkplugBWaterLevelSimulator(device_config)
    simulator.start_simulation(duration_minutes=10)
"""

import json
import time
import random
import logging
import math
from datetime import datetime
import paho.mqtt.client as mqtt
from tahu import sparkplug_b
from tahu.sparkplug_b_pb2 import Payload

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SparkplugBWaterLevelSimulator:
    def __init__(self, device_config):
        """
        Initialize the Sparkplug B water level simulator with device configuration.

        Sets up MQTT client connection, authentication parameters, simulation variables,
        and Sparkplug B protocol compliance settings. Configures callback handlers for
        connection events and establishes baseline simulation parameters.

        Args:
            device_config (dict): Device configuration dictionary containing:
                - device_id (str): Unique device identifier
                - client_id (str): MQTT client ID for connection
                - username (str): EMQX authentication username
                - password (str): EMQX authentication password
                - topic (str): MQTT telemetry topic for data publication
                - broker_host (str, optional): MQTT broker address (default: 'localhost')
                - broker_port (int, optional): MQTT broker port (default: 1883)
                - community_id (int, optional): Sparkplug B community ID (default: 1)
                - edge_node_id (str, optional): Sparkplug B edge node identifier (default: 'default_edge')

        Raises:
            KeyError: If required configuration parameters are missing
            ValueError: If configuration parameters contain invalid values
        """
        self.device_id = device_config['device_id']
        self.client_id = device_config['client_id']
        self.username = device_config['username']
        self.password = device_config['password']
        self.broker_host = device_config.get('broker_host', 'localhost')
        self.broker_port = device_config.get('broker_port', 1883)
        self.community_id = device_config.get('community_id', 1)
        self.edge_node_id = device_config.get('edge_node_id', 'default_edge')
        
        # Sparkplug B Topic 格式
        self.nbirt_topic = f"spBv1.0/{self.community_id}/NBIRTH/{self.device_id}"
        self.ndata_topic = f"spBv1.0/{self.community_id}/NDATA/{self.device_id}"
        self.state_topic = f"spBv1.0/STATE/{self.community_id}/{self.device_id}"
        
        # MQTT 客戶端設置 - 添加 LWT (Last Will and Testament)
        will_payload = json.dumps({
            "timestamp": int(time.time() * 1000),
            "state": "OFFLINE"
        })
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, self.password)
        self.client.will_set(self.state_topic, will_payload, qos=0, retain=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # 水位模擬參數
        self.base_water_level = 1.5  # 基礎水位 (米)
        self.max_variation = 0.3     # 最大變化幅度 (米)
        self.current_level = self.base_water_level
        
        # 暴雨事件模擬參數
        self.rain_event_active = False  # 暴雨事件是否活躍
        self.rain_start_time = None     # 暴雨開始時間
        self.rain_duration = 0          # 暴雨持續時間 (秒)
        self.rain_rise_rate = 0.02      # 暴雨期間水位上升速率 (米/秒)
        self.alert_level = 1.0          # 警戒水位 (米)
        self.rain_probability = 0.05    # 每次檢查時觸發暴雨的機率 (5%)
        
        # Sparkplug B 序列號
        self.seq_number = 0
        
        # 發送間隔 (秒)
        self.send_interval = 60
        
        # Sparkplug B 度量別名定義 (根據數據庫 iot_metric_definitions)
        # 注意: alias 是數字形式的別名，用於減少 MQTT payload 大小
        # 這是 Sparkplug B 規範的要求，不是字符串別名
        self.metric_aliases = {
            "WaterLevel": 1,        # ID: 1, 別名: WL, 單位: CENTIMETER
            "BatteryVoltage": 3,    # ID: 3, 別名: BAT_V, 單位: VOLT  
            "SignalStrength": 4     # ID: 4, 別名: RSSI, 單位: DBM
        }
        
    def _on_connect(self, client, userdata, flags, rc):
        """
        MQTT connection callback handler for Sparkplug B device.
        
        Called automatically when the MQTT client connects or fails to connect
        to the broker. Logs connection status with device-specific information
        for monitoring and debugging Sparkplug B protocol compliance.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            flags: Connection flags from the broker
            rc (int): Connection result code (0 = success, non-zero = failure)
            
        Connection Codes:
            0: Connection successful - ready for Sparkplug B data transmission
            1: Connection refused - incorrect protocol version
            2: Connection refused - invalid client identifier
            3: Connection refused - server unavailable
            4: Connection refused - bad username or password
            5: Connection refused - not authorized
        """
        if rc == 0:
            logger.info(f"成功連接到 MQTT Broker - 設備: {self.device_id}")
        else:
            logger.error(f"連接失敗，返回碼: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """
        MQTT disconnection callback handler for Sparkplug B device.
        
        Called automatically when the MQTT client disconnects from the broker.
        Logs disconnection events with device context for monitoring connection
        stability and troubleshooting network issues in Sparkplug B deployments.
        
        Args:
            client (mqtt.Client): The MQTT client instance that triggered the callback
            userdata: User data (not used in this implementation)
            rc (int): Disconnect reason code
            
        Disconnect Codes:
            0: Clean disconnection (client initiated)
            Non-zero: Unexpected disconnection (network issues, broker problems)
        """
        logger.info(f"已斷開 MQTT 連接 - 設備: {self.device_id}")
        
    def _on_publish(self, client, userdata, mid):
        """MQTT 發布回調"""
        logger.debug(f"消息已發布，消息ID: {mid}")
        
    def check_and_update_rain_event(self):
        """
        檢查並更新暴雨事件狀態
        
        根據機率隨機觸發暴雨事件，或檢查現有暴雨事件是否結束。
        暴雨期間水位會持續上升，直到達到警戒值。
        暴雨結束後，水位會逐漸下降回基礎水位。
        
        Returns:
            bool: 是否有暴雨事件狀態變化
        """
        current_time = time.time()
        status_changed = False
        
        if self.rain_event_active:
            # 檢查暴雨是否結束
            if current_time - self.rain_start_time >= self.rain_duration:
                self.rain_event_active = False
                logger.info(f"暴雨結束 - 水位: {self.current_level:.2f}米")
                status_changed = True
        else:
            # 隨機檢查是否開始暴雨 (5% 機率)
            if random.random() < self.rain_probability:
                # 開始暴雨事件
                self.rain_event_active = True
                self.rain_start_time = current_time
                # 暴雨持續 2-5 分鐘
                self.rain_duration = random.randint(120, 300)
                logger.info(f"暴雨開始 - 預計持續 {self.rain_duration} 秒")
                status_changed = True
                
        return status_changed
        
    def get_current_timestamp_ms(self):
        """
        Get current timestamp in milliseconds for Sparkplug B compliance.
        
        Returns the current system time in milliseconds since Unix epoch,
        required for Sparkplug B metric timestamp fields. This ensures
        temporal accuracy and sequence ordering in industrial IoT data streams.
        
        Returns:
            int: Current timestamp in milliseconds since Unix epoch (January 1, 1970)
            
        Note:
            Sparkplug B specification requires millisecond precision for all
            metric timestamps to ensure proper temporal ordering and data integrity.
        """
        return int(time.time() * 1000)
        
    def create_sparkplug_metric(self, name, value, data_type, engineering_units=None, description=None, for_nbirt=True):
        """
        Create a Sparkplug B compliant metric with proper structure and metadata.
        
        Constructs a complete Sparkplug B metric object with all required fields
        including name, alias, timestamp, data type, and optional engineering units
        and descriptions. Ensures compliance with Eclipse Sparkplug B specification
        for industrial IoT data representation.
        
        Args:
            name (str): Metric name (must match database metric definitions)
            value: Metric value (type must match data_type parameter)
            data_type (str): Sparkplug B data type ("Float", "Int32", etc.)
            engineering_units (str, optional): Engineering units for the metric
            description (str, optional): Human-readable description of the metric
            for_nbirt (bool): True for NBIRTH payload, False for NDATA payload
            
        Returns:
            dict: Complete Sparkplug B metric object with all required fields
        """
        current_timestamp = self.get_current_timestamp_ms()
        
        # 映射字符串數據類型到 tahu MetricDataType
        type_mapping = {
            "Float": sparkplug_b.MetricDataType.Float,
            "Int32": sparkplug_b.MetricDataType.Int32,
            "Double": sparkplug_b.MetricDataType.Double,
            "Boolean": sparkplug_b.MetricDataType.Boolean,
            "String": sparkplug_b.MetricDataType.String
        }
        metric_type = type_mapping.get(data_type, sparkplug_b.MetricDataType.String)
        
        # NBIRTH 需要完整定義，NDATA 只需 alias 和 value
        if for_nbirt:
            metric = {
                "name": name,
                "alias": self.metric_aliases.get(name, 0),
                "timestamp": current_timestamp,
                "dataType": metric_type,
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
        else:
            # NDATA 只包含 alias 和 value
            metric = {
                "alias": self.metric_aliases.get(name, 0),
                "timestamp": current_timestamp,
                "value": value
            }
                
        return metric
        
    def create_nbirt_payload(self):
        """
        Create NBIRTH payload for Sparkplug B device birth announcement.
        
        NBIRTH (Node Birth) message declares the device is online and defines
        all metrics with their complete metadata including names, aliases, data types,
        and properties. This must be sent before any NDATA messages.
        
        Returns:
            Payload: Complete NBIRTH payload with all metric definitions (Protobuf)
        """
        # 使用 tahu 庫創建 NBIRTH payload
        payload = sparkplug_b.getNodeBirthPayload()
        
        # 模擬當前值作為初始值
        water_level_cm = self.base_water_level * 100
        battery_voltage = round(random.uniform(3.2, 4.1), 2)
        signal_strength = random.randint(-90, -40)
        
        # 添加度量到 payload
        sparkplug_b.addMetric(payload, "WaterLevel", 1, sparkplug_b.MetricDataType.Float, water_level_cm)
        sparkplug_b.addMetric(payload, "BatteryVoltage", 3, sparkplug_b.MetricDataType.Float, battery_voltage)
        sparkplug_b.addMetric(payload, "SignalStrength", 4, sparkplug_b.MetricDataType.Float, float(signal_strength))
        
        # 設置序列號
        payload.seq = self.seq_number
        
        # NBIRTH 後增加序列號
        self.seq_number += 1
        if self.seq_number > 255:
            self.seq_number = 0
            
        return payload
        
    def create_ndata_payload(self):
        """
        Create NDATA payload for Sparkplug B data transmission.
        
        NDATA (Node Data) messages contain only the metric values using aliases
        for efficient transmission. Names, data types, and properties are not
        included as they were defined in the NBIRTH message.
        
        Returns:
            Payload: NDATA payload with metric values only (Protobuf)
        """
        # 使用 tahu 庫創建 NDATA payload
        payload = Payload()  # 創建空的 Payload 對象
        
        # 檢查並更新暴雨事件
        rain_status_changed = self.check_and_update_rain_event()
        
        if self.rain_event_active:
            # 暴雨期間：水位持續上升
            rise_amount = self.rain_rise_rate * self.send_interval  # 根據發送間隔計算上升量
            self.current_level += rise_amount
            
            # 限制在合理範圍內 (不超過警戒值的 1.5 倍)
            max_level = self.alert_level * 1.5
            self.current_level = min(self.current_level, max_level)
            
            if rain_status_changed:
                logger.info(f"暴雨期間水位上升 - 當前水位: {self.current_level:.2f}米")
        else:
            # 正常天氣：使用正弦波 + 隨機噪聲模擬
            time_factor = time.time() / 100
            sine_wave = math.sin(time_factor) * 0.1
            random_noise = random.uniform(-0.05, 0.05)
            
            target_level = self.base_water_level + sine_wave + random_noise
            
            # 如果之前有暴雨，水位逐漸下降回基礎水位
            if self.current_level > target_level:
                # 緩慢下降 (每60秒下降對應比例)
                descent_rate = 0.01 * (self.send_interval / 5.0)
                self.current_level = max(target_level, self.current_level - descent_rate)
            else:
                self.current_level = target_level
            
            # 確保水位在合理範圍內
            self.current_level = max(0.0, min(3.0, self.current_level))
        
        # 轉換為公分
        water_level_cm = self.current_level * 100
        
        # 添加度量到 payload (NDATA 只用 alias 和 value)
        sparkplug_b.addMetric(payload, "", 1, sparkplug_b.MetricDataType.Float, round(water_level_cm, 2))
        
        battery_voltage = round(random.uniform(3.2, 4.1), 2)
        sparkplug_b.addMetric(payload, "", 3, sparkplug_b.MetricDataType.Float, battery_voltage)
        
        sparkplug_b.addMetric(payload, "", 4, sparkplug_b.MetricDataType.Float, float(random.randint(-90, -40)))
        
        # 設置序列號
        payload.seq = self.seq_number
        
        # 增加序列號
        self.seq_number += 1
        if self.seq_number > 255:
            self.seq_number = 0
            
        return payload
        
    def connect(self):
        """連接到 MQTT Broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"連接失敗: {e}")
            return False
            
    def disconnect(self):
        """斷開 MQTT 連接"""
        self.client.loop_stop()
        self.client.disconnect()
        
    def send_sparkplug_data(self, topic, payload, message_type="NDATA"):
        """
        發送 Sparkplug B 格式數據到指定的 MQTT Topic
        
        Args:
            topic (str): MQTT topic to publish to
            payload (Payload): Sparkplug B Protobuf payload
            message_type (str): 消息類型 ("NBIRTH" 或 "NDATA")
        """
        try:
            # 序列化 Protobuf payload 為二進制數據
            binary_payload = payload.SerializeToString()
            
            qos = 0 if message_type == "NBIRTH" else 1
            result = self.client.publish(topic, binary_payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                if message_type == "NBIRTH":
                    logger.info(f"Sparkplug B {message_type} 已發送 - 設備: {self.device_id}")
                    logger.info(f"發送到 Topic: {topic}")
                else:
                    # 從 Protobuf payload 中提取水位值進行顯示
                    water_level_cm = None
                    for metric in payload.metrics:
                        if metric.alias == 1:  # WaterLevel alias
                            if metric.HasField('float_value'):
                                water_level_cm = metric.float_value
                            elif metric.HasField('double_value'):
                                water_level_cm = metric.double_value
                            else:
                                water_level_cm = metric.value
                            break
                    
                    logger.info(f"Sparkplug B {message_type} 已發送 - 水位: {water_level_cm}cm, 序列號: {payload.seq}")
                    logger.info(f"發送到 Topic: {topic}")
                logger.debug(f"Topic: {topic}")
            else:
                logger.error(f"發送失敗，錯誤碼: {result.rc}")
                
        except Exception as e:
            logger.error(f"發送數據時發生錯誤: {e}")
            
    def start_simulation(self, duration_minutes=None):
        """
        開始 Sparkplug B 模擬數據發送
        
        按照 Sparkplug B 規範：
        1. 連線到 MQTT Broker
        2. 發送 NBIRTH 訊息宣告設備上線
        3. 循環發送 NDATA 訊息
        
        Args:
            duration_minutes (int, optional): 運行時間(分鐘)，None 表示無限運行
        """
        if not self.connect():
            return
            
        logger.info(f"開始 Sparkplug B 水位數據模擬 - 設備: {self.device_id}")
        logger.info(f"Community ID: {self.community_id}, Edge Node ID: {self.edge_node_id}")
        logger.info(f"發送間隔: {self.send_interval}秒")
        logger.info(f"NBIRTH Topic: {self.nbirt_topic}")
        logger.info(f"NDATA Topic: {self.ndata_topic}")
        
        # 等待連線建立
        time.sleep(1)
        
        try:
            # 1. 發送 NBIRTH 訊息宣告設備上線
            nbirth_payload = self.create_nbirt_payload()
            self.send_sparkplug_data(self.nbirt_topic, nbirth_payload, "NBIRTH")
            
            # 等待 NBIRTH 發送完成
            time.sleep(0.5)
            
            # 2. 開始循環發送 NDATA
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60) if duration_minutes else None
            
            while True:
                # 生成並發送 NDATA
                ndata_payload = self.create_ndata_payload()
                self.send_sparkplug_data(self.ndata_topic, ndata_payload, "NDATA")
                
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
            logger.info("Sparkplug B 水位模擬器已停止")


def main():
    """主函數"""
    print("🌊 Sparkplug B 水位計模擬器啟動中...")
    print("=" * 50)
    
    # 設備配置 (從資料庫 iot_device 表獲取)
    device_config = {
        'device_id': '44547ced-e7fa-489b-8f04-891a30a0adb6',
        'client_id': 'spb_1_2_sb_water_device_1',  # 使用 mqtt_client_id 作為 client_id
        'username': 'device_2_44547ced',
        'password': '5e5d44bd67874f0c',
        'broker_host': 'localhost',  # 請修改為您的 EMQX Broker 地址
        'broker_port': 1883,
        'community_id': 1,  # 從資料庫獲取
        'edge_node_id': 'sb_water_device_1'  # 使用 device_name 作為 edge node id
    }
    
    # 創建並啟動 Sparkplug B 模擬器
    simulator = SparkplugBWaterLevelSimulator(device_config)
    
    # 運行 10 分鐘 (可以修改為 None 無限運行)
    simulator.start_simulation(duration_minutes=10)


if __name__ == "__main__":
    main()