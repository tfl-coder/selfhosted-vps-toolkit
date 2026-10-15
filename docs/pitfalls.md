# 踩坑实录（全部实测，非转述）

## 1. mihomo（Clash Meta / Clash Verge）连不上 Xray 的 VLESS+Reality

**结论：别在这条路上耗时间。Clash 系用 Trojan / Hysteria2，Reality 留给
xray-core 系客户端（v2rayN / v2rayNG / 裸 xray）。**

排查证据链（参数无误的前提下）：

- 客户端配置与服务器参数三方逐字核对（UUID、Reality 公钥、short-id、
  SNI、flow）完全一致，排除填错；
- 同一台服务器、同一组参数，xray-core 客户端 100% 连通，排除服务器
  与 IP 被封；
- 换到另一个端口的 Reality 入站，mihomo 同样失败，排除端口因素；
- 服务器端抓包：mihomo 的连接只收到约 6 KB 的 dest 证书 flight，
  随后被服务器当作未认证连接 fallback 到伪装站，客户端日志报
  `REALITY authentication failed`。

定性为 mihomo 与新版 Xray 的 Reality 握手实现不兼容。服务器侧能改的
都试过，无效。

## 2. 3x-ui 面板 API 加的入站，客户端默认是禁用的

经 `/panel/api/inbounds/add` 新建的入站，客户端会在三处被置为禁用：
`clients` 表、`client_traffics` 表、入站 settings JSON 里的 `enable`。
生成的 `/usr/local/x-ui/bin/config.json` 里该入站的 `clients` 直接是
空的，表现就是"端口通、怎么都认证失败"，极易误判为协议/线路问题。

规矩：API 加完任何入站 → 三处 enable 置 1 → `systemctl restart x-ui`
→ 读回生成配置确认客户端在里面 → 才算建好。脚本见
`proxy-node/fix_api_inbound_enable.py`。（面板 UI 手动加的入站不受此
问题影响；出厂安装流程建的入站也是好的。）

## 3. Clash 客户端 DNS 只写国外 DoH，国内域名全挂

症状：走代理的站点正常，规则里标 DIRECT 的国内站点打不开。
原因：`nameserver` 只填国外 DoH 时，国内域名的解析请求本身就出不去/
被 fake-ip 流程吞掉。修法：nameserver 与 default-nameserver 都放国内
可直达的解析（如 223.5.5.5、119.29.29.29、114.114.114.114），
enhanced-mode 用 fake-ip，模板见 `proxy-node/client/clash-template.yaml`。

## 4. 零散但能省半天的小坑

- 裸 xray 套件的配置文件必须叫 `config.json`，浏览器下载重名成
  `config (1).json` 不改名就会一直读旧配置。
- xray 路由规则里引用的 `outboundTag` 必须指向一个真的打了该 tag 的
  出站，否则启动直接报 `non existing outTag`。
- 给 Reality 入站加 TCP MSS 钳制对坑 1 没有帮助，试过，无效——
  握手问题不在 MTU。
- Invidious 的 API 返回的播放地址是 IP 绑定的直链，客户端必须走
  实例代理（Clipious 默认如此）；拿直链去别处播必然失败，排查
  播放问题时先确认这一点。
