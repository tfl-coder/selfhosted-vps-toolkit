# proxy-node：3x-ui 多协议节点 + 住宅分流

面板：3x-ui（v3.x）+ Xray-core。入站组合（同一台机、不同端口）：

| 协议 | 传输 | 典型用途 | 备注 |
|---|---|---|---|
| VLESS + Reality | TCP | xray 系客户端主力 | **mihomo/Clash 系连不上**，见 `../docs/pitfalls.md` |
| Hysteria2 | UDP | 弱网/移动网络 | 需要证书（可用面板的 IP 证书） |
| Trojan | TCP | Clash 系的稳妥选择 | 同样走 TLS 证书 |

客户端选型结论（实测）：xray-core 系客户端（v2rayN / v2rayNG）全协议可用；
Clash 系（mihomo 内核）请用 Trojan 或 Hysteria2，不要用 Reality 入站。

## 住宅分流

思路：面板的 Xray 模板里加一个 SOCKS5 出站（静态住宅代理），再加一条
域名规则：AI 服务与流媒体域名走住宅出口，其余直出。规则在**模板层**，
所有入站自动继承，新增入站不用重配。

持久化用 `setup_relay.py`（在服务器上运行）：以当前生成的
`/usr/local/x-ui/bin/config.json` 为基底，注入出站与规则后写回面板的
`xrayTemplateConfig` 设置项，这样面板重启/重生成配置也不会丢。
住宅代理的地址与凭证只从环境变量读，脚本不打印、不落盘到仓库：

```bash
RES_HOST=<住宅代理地址> RES_PORT=<端口> \
RES_USER=<用户名> RES_PASS=<密码> \
python3 setup_relay.py
```

改完后 `systemctl restart x-ui`，并读回生成的 `config.json` 确认规则在位。

## API 建入站的必修课

用面板 API（`/panel/api/inbounds/add`）新建的入站，其客户端会被建为
**禁用**状态，生成的配置里根本没有这个客户端，现象是"端口通、认证永远
失败"。修复脚本 `fix_api_inbound_enable.py` 会把 `clients`、
`client_traffics` 两张表和入站 settings JSON 里的 enable 一并置 1；
执行后重启 x-ui 并读回生成配置确认客户端出现，才算建好。
