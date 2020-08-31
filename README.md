# 雲儀開窗器


雲儀開窗器接入HomeAssistant組件


## 安装




###解壓後將yunyi_windows資料夾放入custom_components

### configuration.yaml
```
cover:
  - platform: yeelight_yuba
    name: xxxxx
    host: xxx.xxx.xxx.xxx
    token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
```

可選屬性:scan_interval: x
每x秒更新一次

```



## 功能服務

### cover服務  `stop_cover`

### cover服務  `open_cover`

### cover服務  `close_cover`

### cover服務  `set_cover_position`

### cover服務  `open_cover_tilt(窗戶上鎖)`    

### cover服務  `close_cover_tilt(窗戶解鎖)`



```
```
所有插件都經參考syssi，修改而來。特別感謝https://github.com/syssi
```
