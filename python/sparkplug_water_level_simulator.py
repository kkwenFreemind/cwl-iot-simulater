#!/usr/bin/env python3
"""
Sparkplug B 水位計模擬器
遵循 Sparkplug B 規範的 MQTT 數據傳輸
"""

import json
import time
import random
import logging
import math
from datetime import datetime
import paho.mqtt.client as mqtt

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SparkplugBWaterLevelSimulator:
    def __init__(self, device_config):
        """
        初始化 Sparkplug B 水位計模擬器
        
        Args:
            device_config (dict): 設備配置信息
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
        
        # Sparkplug B 序列號
        self.seq_number = 0
        
        # 發送間隔 (秒)
        self.send_interval = 5
        
        # Sparkplug B 度量別名定義 (根據數據庫 iot_metric_definitions)
        self.metric_aliases = {
            "WaterLevel": 1,        # ID: 1, 別名: WL, 單位: CENTIMETER
            "BatteryVoltage": 3,    # ID: 3, 別名: BAT_V, 單位: VOLT  
            "SignalStrength": 4     # ID: 4, 別名: RSSI, 單位: DBM
        }
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT 連接回調"""
        if rc == 0:
            logger.info(f"成功連接到 MQTT Broker - 設備: {self.device_id}")
        else:
            logger.error(f"連接失敗，返回碼: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """MQTT 斷線回調"""
        logger.info(f"已斷開 MQTT 連接 - 設備: {self.device_id}")
        
    def _on_publish(self, client, userdata, mid):
        """MQTT 發布回調"""
        logger.debug(f"消息已發布，消息ID: {mid}")
        
    def get_current_timestamp_ms(self):
        """獲取當前時間戳 (毫秒)"""
        return int(time.time() * 1000)
        
    def create_sparkplug_metric(self, name, value, data_type, engineering_units=None, description=None):
        """
        創建符合 Sparkplug B 規範的度量項
        
        Args:
            name (str): 度量名稱
            value: 度量值
            data_type (str): 數據類型
            engineering_units (str): 工程單位
            description (str): 描述
            
        Returns:
            dict: Sparkplug B 度量項
        """
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
        """
        生成符合 Sparkplug B 規範的數據載荷
        
        Returns:
            dict: Sparkplug B 格式的數據載荷
        """
        # 模擬水位波動
        time_factor = time.time() / 100
        sine_wave = math.sin(time_factor) * 0.1
        random_noise = random.uniform(-0.05, 0.05)
        
        self.current_level = self.base_water_level + sine_wave + random_noise
        self.current_level = max(0.0, min(3.0, self.current_level))
        
        # 轉換為公分 (數據庫要求 CENTIMETER)
        water_level_cm = self.current_level * 100  # 米轉公分
        
        # 創建度量項列表 (根據數據庫 iot_metric_definitions)
        metrics = []
        
        # 1. 水位 (WaterLevel) - ID: 1, 別名: WL, 單位: CENTIMETER, 數據類型: Float
        metrics.append(self.create_sparkplug_metric(
            "WaterLevel",
            round(water_level_cm, 2),  # 公分，保留2位小數
            "Float",
            "CENTIMETER",
            "Water level measurement in centimeters"
        ))
        
        # 2. 電池電壓 (BatteryVoltage) - ID: 3, 別名: BAT_V, 單位: VOLT, 數據類型: Float
        # 模擬鋰電池電壓範圍 3.0V - 4.2V
        battery_voltage = round(random.uniform(3.2, 4.1), 2)
        metrics.append(self.create_sparkplug_metric(
            "BatteryVoltage",
            battery_voltage,
            "Float",
            "VOLT",
            "Battery voltage in volts"
        ))
        
        # 3. 信號強度 (SignalStrength) - ID: 4, 別名: RSSI, 單位: DBM, 數據類型: Int32
        metrics.append(self.create_sparkplug_metric(
            "SignalStrength",
            random.randint(-90, -40),  # dBm 範圍
            "Int32",
            "DBM",
            "Received Signal Strength Indicator in dBm"
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
        
    def send_sparkplug_data(self, payload):
        """
        發送 Sparkplug B 格式數據到 MQTT Topic
        
        Args:
            payload (dict): Sparkplug B 格式的數據載荷
        """
        try:
            json_payload = json.dumps(payload, ensure_ascii=False, indent=2)
            result = self.client.publish(self.topic, json_payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                water_level_cm = None
                for metric in payload['metrics']:
                    if metric['name'] == 'WaterLevel':
                        water_level_cm = metric['value']
                        break
                
                logger.info(f"Sparkplug B 數據已發送 - 水位: {water_level_cm}cm, 序列號: {payload['seq']}")
                logger.debug(f"Topic: {self.topic}")
            else:
                logger.error(f"發送失敗，錯誤碼: {result.rc}")
                
        except Exception as e:
            logger.error(f"發送數據時發生錯誤: {e}")
            
    def start_simulation(self, duration_minutes=None):
        """
        開始 Sparkplug B 模擬數據發送
        
        Args:
            duration_minutes (int, optional): 運行時間(分鐘)，None 表示無限運行
        """
        if not self.connect():
            return
            
        logger.info(f"開始 Sparkplug B 水位數據模擬 - 設備: {self.device_id}")
        logger.info(f"發送間隔: {self.send_interval}秒")
        logger.info(f"Topic: {self.topic}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        
        try:
            while True:
                # 生成並發送 Sparkplug B 數據
                sparkplug_payload = self.generate_sparkplug_payload()
                self.send_sparkplug_data(sparkplug_payload)
                
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
    
    # 創建並啟動 Sparkplug B 模擬器
    simulator = SparkplugBWaterLevelSimulator(device_config)
    
    # 運行 10 分鐘 (可以修改為 None 無限運行)
    simulator.start_simulation(duration_minutes=10)


if __name__ == "__main__":
    main()