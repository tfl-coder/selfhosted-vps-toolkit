# xray-pc-kit：Windows 免安装极简套件

不想装完整 GUI 客户端时，用官方 xray-core 二进制 + 一份配置就能跑：

```
xray-pc-kit/
├─ xray.exe          # 官方 Xray-windows-64 发布包
├─ config.json       # 由 config.template.json 填好自己的值后改名为这个
├─ start.bat         # 启动 xray 并把系统代理设为 127.0.0.1:10808
└─ stop.bat          # 退出 xray 并恢复系统代理
```

用法：双击 `start.bat`（黑窗口保持开着），用完先 `stop.bat` 再关窗口，
顺序反了系统代理会指向空端口导致断网感。

经验：Reality 入站就用这种 xray-core 直连方式，不要绕 mihomo。
`config.json` 必须正好叫这个名字；浏览器下载出 `config (1).json` 之类
要改名替换，否则 xray 读的是旧配置。
