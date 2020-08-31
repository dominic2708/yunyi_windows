# Yeelight浴霸


Yeelight浴霸接入HomeAssistant組件


## 安装




###解壓後將yeelight_yuba資料夾放入custom_components

### configuration.yaml
```
light:
  - platform: yeelight_yuba
    name: xxxxx
    host: xxx.xxx.xxx.xxx
    token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
climate:
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

### light服務  `turn_on`

### light服務  `turn_off`

### climate服務  `set_hvac_mode`

### climate服務  `set_fan_mode`

### climate服務  `turn_on (預設為乾燥模式)`    

### climate服務  `turn_off`



```
```
所有插件都經參考syssi，修改而來。特別感謝https://github.com/syssi
```
