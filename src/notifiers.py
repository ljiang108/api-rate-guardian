"""
通知模块 - 支持多种通知方式
"""
import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Notifier(ABC):
    """通知器基类"""
    
    @abstractmethod
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        """发送通知"""
        pass


class TelegramNotifier(Notifier):
    """Telegram 通知器"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
    
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        emoji = {
            "warning": "⚠️",
            "critical": "🔴",
            "info": "ℹ️"
        }.get(level, "ℹ️")
        
        text = f"{emoji} *{title}*\n\n{message}"
        
        try:
            resp = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Telegram 发送失败: {e}")
            return False


class EmailNotifier(Notifier):
    """邮件通知器"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str, 
                 from_email: str, to_email: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_email = to_email
    
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = self.to_email
            msg["Subject"] = f"[API Guardian] {title}"
            
            body = f"""
{title}

{message}

级别: {level}
"""
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False


class WebhookNotifier(Notifier):
    """Webhook 通知器"""
    
    def __init__(self, url: str, method: str = "POST", headers: Optional[Dict] = None):
        self.url = url
        self.method = method
        self.headers = headers or {"Content-Type": "application/json"}
    
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        payload = {
            "title": title,
            "message": message,
            "level": level,
            "timestamp": int(time.time())
        }
        
        try:
            if self.method == "POST":
                resp = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
            else:
                resp = requests.get(self.url, params=payload, headers=self.headers, timeout=10)
            
            return resp.status_code in [200, 201]
        except Exception as e:
            print(f"Webhook 发送失败: {e}")
            return False


class BarkNotifier(Notifier):
    """Bark 通知器（iOS 推送）"""
    
    def __init__(self, key: str, server: str = "api.day.app"):
        self.key = key
        self.server = server
    
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        try:
            url = f"https://{self.server}/push"
            resp = requests.post(url, json={
                "title": title,
                "body": message,
                "key": self.key,
                "level": level
            }, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            print(f"Bark 发送失败: {e}")
            return False


class ConsoleNotifier(Notifier):
    """控制台通知器（用于调试）"""
    
    def send(self, title: str, message: str, level: str = "warning") -> bool:
        emoji = {"warning": "⚠️", "critical": "🔴", "info": "ℹ️"}.get(level, "ℹ️")
        print(f"{emoji} {title}: {message}")
        return True


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.notifiers = []
    
    def add_notifier(self, notifier: Notifier) -> None:
        self.notifiers.append(notifier)
    
    def send(self, title: str, message: str, level: str = "warning") -> None:
        for notifier in self.notifiers:
            try:
                notifier.send(title, message, level)
            except Exception as e:
                print(f"通知失败: {e}")


def create_notifier(config: Dict) -> Optional[Notifier]:
    """工厂函数：创建通知器"""
    notifier_type = config.get("type", "").lower()
    
    if notifier_type == "telegram":
        return TelegramNotifier(
            token=config["token"],
            chat_id=config["chat_id"]
        )
    elif notifier_type == "email":
        return EmailNotifier(
            smtp_host=config["smtp_host"],
            smtp_port=config.get("smtp_port", 587),
            username=config["username"],
            password=config["password"],
            from_email=config["from_email"],
            to_email=config["to_email"]
        )
    elif notifier_type == "webhook":
        return WebhookNotifier(
            url=config["url"],
            method=config.get("method", "POST"),
            headers=config.get("headers")
        )
    elif notifier_type == "bark":
        return BarkNotifier(
            key=config["key"],
            server=config.get("server", "api.day.app")
        )
    elif notifier_type == "console":
        return ConsoleNotifier()
    else:
        print(f"未知的通知类型: {notifier_type}")
        return None


if __name__ == "__main__":
    # 测试
    print("🔔 通知模块测试\n")
    
    # 控制台通知测试
    notifier = ConsoleNotifier()
    notifier.send("测试标题", "这是一条测试消息", "warning")
