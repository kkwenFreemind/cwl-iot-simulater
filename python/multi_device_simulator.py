#!/usr/bin/env python3
"""
雙設備水位計模擬器 - 同時模擬兩個設備
支持從 env.md 配置文件讀取設備信息
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

class MultiDeviceWaterLevelSimulator:
    def __init__(self, broker_host='localhost', broker_port=1883):
        """
        初始化多設備水位計模擬器
        
        Args:
            broker_host (str): MQTT Broker 主機地址
            broker_port (int): MQTT Broker 端口
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
        """為每個設備創建模擬器實例"""
        for i, config in enumerate(self.device_configs):
            config.update({
                'broker_host': self.broker_host,
                'broker_port': self.broker_port
            })
            simulator = WaterLevelDevice(config, device_index=i+1)
            self.simulators.append(simulator)
            
    def start_all_simulators(self, duration_minutes=None):
        """啟動所有設備模擬器"""
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
        """停止所有模擬器"""
        self.running = False
        for simulator in self.simulators:
            simulator.stop()


class WaterLevelDevice:
    def __init__(self, device_config, device_index=1):
        """
        單個水位計設備模擬器
        
        Args:
            device_config (dict): 設備配置
            device_index (int): 設備索引
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
        """MQTT 連接回調"""
        if rc == 0:
            logger.info(f"[{self.location}] 設備 {self.device_index} 已連接到 MQTT Broker")
        else:
            logger.error(f"[{self.location}] 設備 {self.device_index} 連接失敗，返回碼: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """MQTT 斷線回調"""
        logger.info(f"[{self.location}] 設備 {self.device_index} 已斷開連接")
        
    def _on_publish(self, client, userdata, mid):
        """MQTT 發布回調"""
        pass
        
    def generate_sensor_data(self):
        """生成模擬傳感器數據"""
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
        
    def send_data(self, data):
        """發送數據"""
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
        """運行模擬"""
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
        """停止模擬"""
        self.running = False


def main():
    """主函數 - 啟動多設備模擬器"""
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