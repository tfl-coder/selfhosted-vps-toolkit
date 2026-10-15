# invidious：1 GB 小内存上的 YouTube 镜像 + 自愈

基于 iv-org/invidious 官方 Compose，在 1 vCPU / 1 GB RAM 的机器上和
代理节点共存的做法。关键就三件事：**内存封顶、播放探活自愈、自动更新**。

## 内存预算

机器只有 1 GB（另加了 ~1.5 GB swap 兜底），给每个容器封顶，防互相饿死：

| 容器 | 内存上限 | 备注 |
|---|---|---|
| invidious | 384 MB | 主服务 |
| companion | 640 MB | 负责取流，最吃内存 |
| postgres:14 | 256 MB | `shared_buffers` 调到 64 MB |

数值都在 `docker-compose.yml` 里（`mem_limit`）。部署前把 `.env.example`
复制为 `.env` 填自己的密钥（数据库密码、Invidious 的 HMAC 等）。

## 访问方式

Caddy 反向代理到本机 Invidious 端口，对外开 HTTPS（示例里用 8446，
证书可用 Let's Encrypt 的 IP 证书）。客户端用 Clipious（Android）
添加自建实例即可；注意取流必须走实例代理（API 直链是 IP 绑定的，
客户端用 `local` 代理模式才播得了）。

注册默认开着只为先给自己建号，**建完立刻**在配置里设
`registration_enabled: false` 并重启，不要把公开注册的实例裸奔。

## 自愈三件套（systemd/）

| 单元 | 频率 | 做什么 |
|---|---|---|
| `invidious-health.timer` | 每 5 分钟 | 探活 + 用一个 canary 视频试播；连续 2 次失败 → `docker compose restart`；重启后仍不恢复 → 发 webhook 告警 |
| `invidious-companion-restart.timer` | 每周一次 | 只重启 companion（它长期运行后状态容易变差） |
| `invidious-update.timer` | 每周两次 | 拉新镜像并重建容器，跟上游播放机制变更 |

安装：把 `systemd/` 里的文件改好路径与占位符，拷到
`/etc/systemd/system/` 后 `systemctl daemon-reload && systemctl enable --now
invidious-health.timer invidious-companion-restart.timer
invidious-update.timer`。

## 现实预期

稳定性排序：梯子直连 YouTube 本体 > 镜像。镜像是"免梯子备胎"：
上游改播放机制时可能短暂不可用，自动更新装上之后一般能自愈；
客户端 App 不需要跟着更新。
