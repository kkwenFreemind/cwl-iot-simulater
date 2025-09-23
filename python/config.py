#!/usr/bin/env python3
"""
配置文件 - MQTT 和設備配置
"""

# MQTT Broker 配置
MQTT_CONFIG = {
    'broker_host': 'localhost',  # 請修改為您的 EMQX Broker IP 地址
    'broker_port': 1883,
    'keepalive': 60,
    'qos': 1  # 服務質量等級
}

# 設備配置 (從 env.md 文件獲取)
DEVICE_CONFIGS = [
    {
        'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',
        'client_id': 'client_9d3e50ea',
        'username': 'device_2_9d3e50ea',
        'password': 'b1652e4bac404628',
        'topic': 'tenants/2/devices/9d3e50ea/telemetry',
        'base_water_level': 1.5,  # 基礎水位 (米)
        'location': '水庫監測點 A',
        'send_interval': 5  # 發送間隔 (秒)
    },
    {
        'device_id': '0cabc4cb-9092-48ec-80bf-63392a3b73b9',
        'client_id': 'client_0cabc4cb',
        'username': 'device_2_0cabc4cb',
        'password': 'f8cf145771d84376',
        'topic': 'tenants/2/devices/0cabc4cb/telemetry',
        'base_water_level': 2.0,  # 基礎水位 (米)
        'location': '水庫監測點 B',
        'send_interval': 7  # 發送間隔 (秒)
    }
]

# 模擬參數
SIMULATION_CONFIG = {
    'max_water_level': 5.0,     # 最大水位 (米)
    'min_water_level': 0.0,     # 最小水位 (米)
    'max_variation': 0.3,       # 最大變化幅度 (米)
    'temp_range': (15.0, 30.0), # 溫度範圍 (攝氏度)
    'humidity_range': (50.0, 90.0), # 濕度範圍 (%)
    'battery_range': (70.0, 100.0), # 電池電量範圍 (%)
    'signal_range': (-90, -40),      # 信號強度範圍 (dBm)
    'ph_range': (6.0, 8.0),         # pH 值範圍
    'pressure_base': 1013.25,       # 基礎大氣壓力 (hPa)
    'pressure_variation': 15.0      # 大氣壓力變化幅度 (hPa)
}

# 日誌配置
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}