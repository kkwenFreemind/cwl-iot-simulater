# 🌊 Community Water Level IoT Simulator

> 🌍 **Language / 語言**: [English](README.md) | [中文](README_CN.md)

一個全面的 IoT 模擬套件，用於水位監測系統，實現工業標準 Sparkplug B 協議與 MQTT 連接。

## 🚀 功能特色

- **Sparkplug B 兼容**: 完全符合 Eclipse Sparkplug B 規範
- **多設備支持**: 並發模擬多個水位傳感器
- **實時 MQTT**: 安全的 MQTT 傳輸與 EMQX broker 集成
- **數據庫集成**: 指標與 `iot_metric_definitions` 表結構對齊
- **動態模擬**: 真實的水位波動，具有可配置參數
- **生產就緒**: 全面的日誌記錄、錯誤處理和優雅關閉

## 📊 支持的指標

| 指標 ID | 名稱 | 別名 | 單位 | 數據類型 | 描述 |
|---------|------|------|------|----------|------|
| 1 | WaterLevel | WL | CENTIMETER | Float | 水位測量 |
| 3 | BatteryVoltage | BAT_V | VOLT | Float | 設備電池電壓 |
| 4 | SignalStrength | RSSI | DBM | Int32 | 信號強度指標 |

## 🏗️ 項目結構

```
cwl-iot-simulater/
├── python/                                    # Python 模擬器
│   ├── sparkplug_water_level_simulator.py    # 單設備模擬器
│   ├── sparkplug_multi_device_simulator.py   # 多設備模擬器
│   ├── sparkplug_payload_example.py          # 載荷結構演示
│   ├── water_level_simulator.py              # 基礎 MQTT 模擬器
│   ├── multi_device_simulator.py             # 基礎多設備模擬器
│   ├── config.py                             # 配置管理
│   └── README.md                             # Python 實現文檔
├── doc/                                       # 文檔
│   ├── env.md                                # 環境配置
│   └── plan/                                 # 項目規劃文檔
└── README.md                                 # 此文件
```

## ⚙️ 安裝

### 先決條件

- Python 3.7+
- MQTT Broker (推薦使用 EMQX)

### 依賴項

```bash
pip install paho-mqtt
```

### 快速開始

```bash
# 克隆倉庫
git clone https://github.com/kkwenFreemind/cwl-iot-simulater.git
cd cwl-iot-simulater

# 安裝依賴項
pip install paho-mqtt

# 運行單設備模擬器
python python/sparkplug_water_level_simulator.py

# 運行多設備模擬器
python python/sparkplug_multi_device_simulator.py
```

## 📡 MQTT 配置

在您選擇的模擬器中更新 broker 配置：

```python
MQTT_CONFIG = {
    'broker_host': 'your-emqx-broker-ip',  # 替換為您的 broker
    'broker_port': 1883,
    'keepalive': 60,
    'qos': 1
}
```

## 🌊 設備配置

每個設備配置包含：

- **設備 ID**: 唯一標識符 (UUID 格式)
- **MQTT 客戶端 ID**: MQTT 連接標識符
- **憑證**: broker 認證的用戶名和密碼
- **主題**: 遙測數據發布端點

配置示例：

```python
{
    'device_id': '9d3e50ea-e160-4e59-a98e-6b13f51e5e1f',
    'client_id': 'client_9d3e50ea',
    'username': 'device_2_9d3e50ea',
    'password': 'b1652e4bac404628',
    'topic': 'tenants/2/devices/9d3e50ea/telemetry'
}
```

## 📈 Sparkplug B 載荷結構

```json
{
  "timestamp": 1727100000000,
  "metrics": [
    {
      "name": "WaterLevel",
      "alias": 1,
      "timestamp": 1727100000000,
      "dataType": "Float",
      "value": 152.75,
      "properties": {
        "Engineering Units": {
          "type": "String",
          "value": "CENTIMETER"
        },
        "Description": {
          "type": "String",
          "value": "Water level measurement in centimeters"
        }
      }
    }
  ],
  "seq": 42
}
```

## 🎯 關鍵功能

### 實時數據模擬

- **水位**: 使用正弦波模式和真實噪聲的動態波動
- **電池電壓**: 模擬鋰電池放電 (3.2V - 4.1V)
- **信號強度**: 可變 RSSI 值 (-90dBm 到 -40dBm)

### Sparkplug B 兼容性

- ✅ 載荷優化的指標別名
- ✅ 精確度的毫秒時間戳
- ✅ 序列號管理 (0-255 輪轉)
- ✅ 工程單位和屬性描述
- ✅ 適當的數據類型聲明

### 生產功能

- **日誌記錄**: 具有可配置級別的全面日誌記錄
- **錯誤處理**: 優雅的錯誤恢復和報告
- **信號處理**: 中斷時的清潔關閉
- **線程安全**: 多設備場景的安全並發操作

## 🔧 配置選項

### 模擬參數

```python
SIMULATION_CONFIG = {
    'max_water_level': 500.0,      # 最大水位 (cm)
    'min_water_level': 0.0,        # 最小水位 (cm)
    'max_variation': 30.0,         # 最大波動 (cm)
    'send_interval': 5,            # 數據傳輸間隔 (秒)
    'battery_range': (3.0, 4.2),   # 電池電壓範圍 (V)
    'signal_range': (-100, -30)     # 信號強度範圍 (dBm)
}
```

## 🌐 集成

此模擬器設計用於與以下系統集成：

- **EMQX MQTT Broker**: 企業級 MQTT 消息傳遞
- **PostgreSQL**: 具有 `iot_metric_definitions` 表的數據庫
- **Eclipse Sparkplug B**: 工業 IoT 標準協議
- **IoT 平台**: ThingsBoard, AWS IoT, Azure IoT 等

## 📚 文檔

- [環境設置](doc/env.md) - 設備憑證和配置
- [項目規劃](doc/plan/) - 開發階段和規範
- [Python 實現](python/README.md) - 詳細的 Python 文檔

## 🤝 貢獻

1. Fork 此倉庫
2. 創建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開 Pull Request

## 📄 許可證

此項目根據 MIT 許可證授權 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 🏷️ 版本

**v1.0.0** - 初始發行，包含 Sparkplug B 水位模擬器

## 👥 作者

- **kkwenFreemind** - *初始工作* - [GitHub](https://github.com/kkwenFreemind)

## 🙏 致謝

- Eclipse Sparkplug B 工作組提供規範
- Eclipse Paho MQTT Python 客戶端貢獻者
- 社區水位監測項目利益相關者

