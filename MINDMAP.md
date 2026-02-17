# API Rate Guardian 思维导图

## 🌟 项目简介
通用API限流预警系统

## 🎯 核心功能
- 多平台API监控
- 自定义阈值预警
- 多种通知方式
- 实时监控

## 🔧 支持的API
### 已支持
- OpenAI
- MiniMax
- DeepSeek
- Claude (Anthropic)
- GitHub

## 📱 通知方式
- Telegram ✓
- 邮件 ✓
- Webhook ✓
- Bark (iOS) ✓

## ⚙️ 配置选项
- 预警阈值 (默认80%)
- 检查间隔 (默认60秒)
- 环境变量支持

## 🚀 快速开始
1. pip install
2. cp config.example.yaml config.yaml
3. python -m src.main

## 💡 使用场景
- AI应用开发
- 数据采集
- API集成
- 自动化脚本

## 📦 项目结构
```
api-rate-guardian/
├── src/
│   ├── main.py
│   ├── checkers.py
│   └── notifiers.py
├── config.example.yaml
├── requirements.txt
└── README.md
```

## ⭐ 特点
- 轻量级
- 简单易用
- 开源免费
- 跨平台
