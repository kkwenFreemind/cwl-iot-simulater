#!/usr/bin/env python3
"""
多設備 Sparkplug B 水位計模擬器
同時模擬多個設備並遵循 Sparkplug B 規範
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
    def __init__(self, broker_host='localhost', broker_port=1883):
        """
        初始化多設備 Sparkplug B 模擬器
        
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
        """為每個設備創建 Sparkplug B 模擬器實例"""
        for i, config in enumerate(self.device_configs):
            config.update({
                'broker_host': self.broker_host,
                'broker_port': self.broker_port
            })
            simulator = SparkplugBDevice(config, device_index=i+1)
            self.simulators.append(simulator)
            
    def start_all_simulators(self, duration_minutes=None):
        """啟動所有設備模擬器"""
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
        """停止所有模擬器"""
        self.running = False
        for simulator in self.simulators:
            simulator.stop()


class SparkplugBDevice:
    def __init__(self, device_config, device_index=1):
        """
        單個 Sparkplug B 水位計設備模擬器
        
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
    """主函數 - 啟動多設備 Sparkplug B 模擬器"""
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