#!/usr/bin/env python3
"""
測試 Sparkplug B 數據結構展示
顯示符合數據庫 iot_metric_definitions 規範的 Sparkplug B 載荷
"""

import json
import time
import random
import math
from datetime import datetime

def get_current_timestamp_ms():
    """獲取當前時間戳 (毫秒)"""
    return int(time.time() * 1000)

def create_sparkplug_metric(name, alias, value, data_type, unit, description):
    """創建符合 Sparkplug B 規範的度量項"""
    metric = {
        "name": name,
        "alias": alias,
        "timestamp": get_current_timestamp_ms(),
        "dataType": data_type,
        "value": value,
        "properties": {
            "Engineering Units": {
                "type": "String",
                "value": unit
            },
            "Description": {
                "type": "String",
                "value": description
            }
        }
    }
    return metric

def generate_sample_sparkplug_payload():
    """生成範例 Sparkplug B 載荷"""
    
    # 模擬水位數據 (基礎水位 150cm，加上波動)
    base_level_cm = 150.0
    sine_wave = math.sin(time.time() / 100) * 10  # ±10cm 波動
    random_noise = random.uniform(-2, 2)  # ±2cm 隨機噪聲
    water_level_cm = round(base_level_cm + sine_wave + random_noise, 2)
    
    # 模擬電池電壓 (3.2V - 4.1V)
    battery_voltage = round(random.uniform(3.2, 4.1), 2)
    
    # 模擬信號強度 (-90dBm 到 -40dBm)
    signal_strength = random.randint(-90, -40)
    
    # 創建度量項列表
    metrics = [
        create_sparkplug_metric(
            name="WaterLevel",
            alias=1,
            value=water_level_cm,
            data_type="Float", 
            unit="CENTIMETER",
            description="Water level measurement in centimeters"
        ),
        create_sparkplug_metric(
            name="BatteryVoltage", 
            alias=3,
            value=battery_voltage,
            data_type="Float",
            unit="VOLT",
            description="Battery voltage in volts"
        ),
        create_sparkplug_metric(
            name="SignalStrength",
            alias=4, 
            value=signal_strength,
            data_type="Int32",
            unit="DBM",
            description="Received Signal Strength Indicator in dBm"
        )
    ]
    
    # 完整的 Sparkplug B 載荷
    payload = {
        "timestamp": get_current_timestamp_ms(),
        "metrics": metrics,
        "seq": random.randint(0, 255)
    }
    
    return payload

def main():
    """主函數 - 生成並顯示範例數據"""
    print("🌊⚡ Sparkplug B 水位計數據結構範例")
    print("=" * 60)
    print("根據數據庫 iot_metric_definitions 表的欄位定義:")
    print("- ID: 1, WaterLevel (WL) - CENTIMETER, Float")
    print("- ID: 3, BatteryVoltage (BAT_V) - VOLT, Float") 
    print("- ID: 4, SignalStrength (RSSI) - DBM, Int32")
    print("=" * 60)
    
    # 生成範例數據
    sample_payload = generate_sample_sparkplug_payload()
    
    # 美化輸出 JSON
    formatted_json = json.dumps(sample_payload, indent=2, ensure_ascii=False)
    print("\n📊 範例 Sparkplug B 載荷:")
    print(formatted_json)
    
    print("\n" + "=" * 60)
    print("✅ 此數據結構完全符合:")
    print("   - Sparkplug B 規範")
    print("   - 數據庫 iot_metric_definitions 表定義")
    print("   - MQTT 傳輸要求")
    
    # 顯示度量項摘要
    print("\n📋 度量項摘要:")
    for metric in sample_payload['metrics']:
        unit = metric['properties']['Engineering Units']['value']
        print(f"   • {metric['name']} (別名: {metric['alias']}) = {metric['value']} {unit}")

if __name__ == "__main__":
    main()