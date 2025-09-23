# 水位計 IoT 模擬器

> 📖 **English Version**: [README_EN.md](README_EN.md) - English version of this documentation

這個目錄包含 Python 版本的水位計 IoT 設備模擬器，用於模擬水位傳感器數據並通過 MQTT 協議發送到 EMQX Broker。

## 檔案說明

### 1. `water_level_simulator.py` - 單設備模擬器

- 模擬單個水位計設備
- 發送水位、溫度、濕度等傳感器數據
- 支持 MQTT 連接和數據傳輸

### 2. `multi_device_simulator.py` - 多設備模擬器

- 同時模擬多個水位計設備
- 支持並發數據傳輸
- 每個設備有不同的數據模式和發送間隔

### 3. `deviceInfo.md` - 設備配置信息

- 包含設備 ID、MQTT 客戶端 ID、認證信息
- Topic 配置信息

## 安裝依賴

```bash
pip install paho-mqtt
```

## 使用方式

### 單設備模擬器

```bash
python water_level_simulator.py
```

### 多設備模擬器

```bash
python multi_device_simulator.py
```

## 配置說明

在運行模擬器之前，請確保修改以下配置：

1. **MQTT Broker 地址**: 將 `broker_host` 改為您的 EMQX 服務器 IP 地址
2. **設備認證**: 確認 `deviceInfo.md` 中的設備配置信息正確
3. **Topic**: 確認 telemetry topic 路徑正確

## 數據格式

模擬器發送的 JSON 數據格式：

```json
{
  "deviceId": "9d3e50ea-e160-4e59-a98e-6b13f51e5e1f",
  "timestamp": "2025-09-23T10:30:00.123456",
  "waterLevel": 1.523,
  "temperature": 22.1,
  "humidity": 68.5,
  "batteryLevel": 87.2,
  "signalStrength": -65,
  "status": "normal"
}
```

## 功能特色

- ✅ 真實的水位波動模擬（正弦波 + 隨機噪聲）
- ✅ MQTT QoS 1 可靠傳輸
- ✅ 多設備並發支持
- ✅ 詳細的日誌記錄
- ✅ 優雅的程序關閉
- ✅ 設備狀態監控
- ✅ 電池電量模擬
- ✅ 信號強度模擬
