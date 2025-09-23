#!/usr/bin/env python3
"""
水位計模擬器 - MQTT 數據發送
模擬水位傳感器數據並發送到 EMQX MQTT Broker
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

class WaterLevelSimulator:
    def __init__(self, device_config):
        """
        初始化水位計模擬器
        
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
        
        # 發送間隔 (秒)
        self.send_interval = 5
        
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
        
    def generate_water_level_data(self):
        """
        生成模擬的水位數據
        
        Returns:
            dict: 包含水位和相關傳感器數據的字典
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
        
    def send_data(self, data):
        """
        發送數據到 MQTT Topic
        
        Args:
            data (dict): 要發送的數據
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
        開始模擬數據發送
        
        Args:
            duration_minutes (int, optional): 運行時間(分鐘)，None 表示無限運行
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
    """主函數"""
    
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