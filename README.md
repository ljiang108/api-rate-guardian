# 🔔 API Rate Guardian

> 通用 API 限流预警系统 - 再也不用担心 API 被限流了！

[![Python Version](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/api-rate-guardian)](https://github.com/your-username/api-rate-guardian)

## ✨ 特性

- 🌐 **多平台支持** - 支持 OpenAI、MiniMax、DeepSeek、Claude、GitHub 等主流 API
- ⚙️ **自定义阈值** - 根据需求设置预警阈值（默认 80%）
- 📱 **多种通知** - 支持 Telegram、邮件、短信、Webhook、Bark 等通知方式
- 🪶 **轻量级** - 简单易用，部署方便
- 🔄 **实时监控** - 每隔指定时间自动检查 API 使用情况

## 📦 安装

```bash
# 克隆项目
git clone https://github.com/your-username/api-rate-guardian.git
cd api-rate-guardian

# 安装依赖
pip install -r requirements.txt
```

## ⚡ 快速开始

### 1. 复制配置

```bash
cp config.example.yaml config.yaml
```

### 2. 编辑配置

```yaml
apis:
  # MiniMax API
  - name: "MiniMax"
    provider: minimax
    api_key: "your-minimax-api-key"
    threshold: 70  # 使用率超过 70% 触发预警
    check_interval: 60  # 每 60 秒检查一次

  # OpenAI API
  - name: "OpenAI"
    provider: openai
    api_key: "your-openai-api-key"
    threshold: 80
    check_interval: 60

  # DeepSeek API
  - name: "DeepSeek"
    provider: deepseek
    api_key: "your-deepseek-api-key"
    threshold: 75
    check_interval: 60

notifications:
  telegram:
    enabled: true
    token: "your-telegram-bot-token"
    chat_id: "your-chat-id"

  email:
    enabled: false
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL}"
    password: "${EMAIL_PASSWORD}"
    from_email: "your-email@gmail.com"
    to_email: "notify@example.com"

  webhook:
    enabled: false
    url: "https://your-webhook.com/notify"
```

### 3. 运行

```bash
python -m src.main
# 或者
python src/main.py
```

## 🔧 支持的 API

| API | Provider Name | 说明 |
|-----|---------------|------|
| OpenAI | `openai` | GPT-4, GPT-3.5 等 |
| MiniMax | `minimax` | M2.1, M2 等 |
| DeepSeek | `deepseek` | DeepSeek Chat, Coder |
| Claude | `anthropic` | Claude 3 系列 |
| GitHub | `github` | GitHub API |

## 📱 通知方式

### Telegram

1. 创建 Bot: @BotFather
2. 获取 Bot Token
3. 获取 Chat ID: @userinfobot
4. 填入配置

### 邮件

支持 Gmail、QQ 邮箱、企业邮箱等 SMTP 服务。

### Webhook

支持任意 HTTP 接口，可对接钉钉、企业微信、飞书等。

### Bark (iOS)

iOS 推送通知，需要安装 Bark App。

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| name | API 名称 | - |
| provider | API 类型 | - |
| api_key | API 密钥 | - |
| threshold | 预警阈值 (%) | 80 |
| check_interval | 检查间隔 (秒) | 60 |

## 🐳 Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "-m", "src.main"]
```

```bash
docker build -t api-rate-guardian .
docker run -d -v $(pwd)/config.yaml:/app/config.yaml api-rate-guardian
```

## 📖 API

```python
from src.checkers import get_checker
from src.notifiers import TelegramNotifier

# 创建检查器
checker = get_checker("minimax", "your-api-key")
result = checker.check()

print(f"使用率: {result['usage_percent']}%")
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📝 License

MIT License - 自由使用，商用付费

---

**让 API 限流不再困扰你！** 🚀
