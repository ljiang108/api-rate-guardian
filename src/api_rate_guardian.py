"""
API Rate Guardian - 核心模块
"""
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class Provider(Enum):
    OPENAI = "openai"
    MINIMAX = "minimax"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    GITHUB = "github"
    CUSTOM = "custom"


@dataclass
class APIConfig:
    provider: Provider
    api_key: str
    base_url: Optional[str] = None
    threshold: int = 80  # 80% 触发预警
    check_interval: int = 60  # 检查间隔（秒）


class NotificationHandler:
    """通知处理器基类"""
    
    def send(self, message: str, level: str = "warning") -> None:
        raise NotImplementedError


class TelegramNotifier(NotificationHandler):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
    
    def send(self, message: str, level: str = "warning") -> None:
        # 实现 Telegram 发送逻辑
        print(f"[Telegram] {message}")


class RateLimitChecker:
    """API 速率限制检查器"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.usage_percent = 0
        self.notifiers: List[NotificationHandler] = []
        self._running = False
        self._thread = None
        self._last_warning_time = 0
    
    def add_notifier(self, notifier: NotificationHandler) -> None:
        self.notifiers.append(notifier)
    
    def check_rate_limit(self) -> Dict:
        """检查当前 API 使用情况"""
        # 这里需要根据不同 provider 实现具体的检查逻辑
        # 返回 usage_percent 和 remaining 等信息
        return {
            "usage_percent": 0,
            "remaining": 100,
            "limit": 100,
            "reset_time": 0
        }
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while self._running:
            try:
                result = self.check_rate_limit()
                self.usage_percent = result["usage_percent"]
                
                # 触发预警
                if self.usage_percent >= self.config.threshold:
                    current_time = time.time()
                    # 防止频繁预警（间隔5分钟）
                    if current_time - self._last_warning_time > 300:
                        self._send_warning(result)
                        self._last_warning_time = current_time
                
            except Exception as e:
                print(f"检查出错: {e}")
            
            time.sleep(self.config.check_interval)
    
    def _send_warning(self, result: Dict) -> None:
        message = f"⚠️ API 限流预警\n{self.config.provider.value}: {self.usage_percent}% 使用率"
        for notifier in self.notifiers:
            notifier.send(message)
    
    def start(self) -> None:
        """启动监控"""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self) -> None:
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join()


class APIGuardian:
    """API Guardian 主类"""
    
    def __init__(self):
        self.checkers: Dict[Provider, RateLimitChecker] = {}
    
    def add_api(self, config: APIConfig) -> RateLimitChecker:
        checker = RateLimitChecker(config)
        self.checkers[config.provider] = checker
        return checker
    
    def start_all(self) -> None:
        for checker in self.checkers.values():
            checker.start()
    
    def stop_all(self) -> None:
        for checker in self.checkers.values():
            checker.stop()


if __name__ == "__main__":
    # 示例用法
    guardian = APIGuardian()
    
    # 添加 MiniMax API
    config = APIConfig(
        provider=Provider.MINIMAX,
        api_key="your-api-key",
        threshold=70
    )
    checker = guardian.add_api(config)
    
    # 添加 Telegram 通知
    checker.add_notifier(TelegramNotifier("token", "chat_id"))
    
    # 启动
    guardian.start_all()
    
    print("API Rate Guardian 运行中...")
