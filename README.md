# selfhosted-vps-toolkit

在一台 **1 vCPU / 1 GB RAM** 的小 VPS 上自托管网络服务的部署记录与脚本：
多协议代理节点（3x-ui + Xray）、按域名分流的住宅出口中转、以及一个带自愈能力的
Invidious（YouTube 前端）镜像。全部内容为**脱敏模板**：所有 IP、UUID、端口、
凭证均为占位符，真实值只应存在于你自己的 `.env` / 服务器本地文件中。

## 架构

```
                        ┌─ 直出（默认）──────────────► 一般网站
客户端 ──► VPS 上的 Xray ┤
 （手机/电脑）            └─ 住宅 SOCKS5 出口 ─────────► AI 服务 / 流媒体
                             （按域名规则匹配）           （对出口 IP 敏感的站点）

同一台机器上还跑着：Invidious + Companion + PostgreSQL（Docker Compose）
                    + Caddy 反向代理（HTTPS）
                    + systemd 定时器做健康检查 / 自动更新 / 告警
```

为什么要住宅出口：机房 IP 在部分 AI 与流媒体服务上会被直接拒绝（403 / 地区
不可用），把这些域名单独经静态住宅 IP 出去即可，其余流量直出不绕路。

## 目录

| 路径 | 内容 |
|---|---|
| `proxy-node/` | 3x-ui 多协议入站、住宅分流脚本、API 入站启用修复、客户端配置模板 |
| `invidious/` | 小内存 Docker Compose（带内存上限）＋ 健康自检 / 自动更新 / 告警的 systemd 单元模板 |
| `docs/pitfalls.md` | 实测踩坑：mihomo × Reality 不兼容、3x-ui API 入站客户端默认禁用、客户端 DNS 写法 |

## 部署顺序（概要）

1. VPS 基础：加 swap（1 GB 内存必备）、SSH 仅密钥登录、防火墙放行所需端口。
2. 装 3x-ui，按 `proxy-node/README.md` 建入站；**经 API 建的入站务必跑一次
   `fix_api_inbound_enable.py`**（原因见踩坑文档）。
3. 有住宅代理的话，用 `proxy-node/setup_relay.py` 把分流规则持久化进面板模板。
4. 客户端用 `proxy-node/client/` 里的模板填自己的参数导入。
5. Invidious 按 `invidious/README.md` 起 Compose，再装 systemd 定时器。

## 安全说明

- 本仓库**不包含**任何真实服务器地址、密钥或订阅信息；提交前请用
  `grep -R "你的真实IP" .` 自查一遍。
- `.env`、导出的客户端配置（含真实 UUID 的）已被 `.gitignore` 排除。
- 面板请务必使用随机端口 + 随机路径 + 强密码，并开启 HTTPS（可用 IP 证书）。

## License

MIT
