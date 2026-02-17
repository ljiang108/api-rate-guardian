"""
API Rate Guardian - 主程序
"""
import os
import sys
import time
import signal
import argparse
import yaml
import threading
from pathlib import Path
from typing import Dict, Any, List

from checkers import get_checker, BaseChecker
from notifiers import NotificationManager, create_notifier, Notifier


class APIRateGuardian:
    """API 限流预警主类"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.checkers: List[BaseChecker] = []
        self.notification_manager = NotificationManager()
        self.running = False
        self.threads: List[threading.Thread] = []
        self._last_warning: Dict[str, float] = {}  # 记录每个API的最后警告时间
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(self.config_path)
        if not config_path.exists():
            print(f"配置文件不存在: {self.config_path}")
            sys.exit(1)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 处理环境变量
        config = self._process_env_vars(config)
        return config
    
    def _process_env_vars(self, config: Dict) -> Dict:
        """递归处理环境变量"""
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.environ.get(env_var, config)
        return config
    
    def _init_checkers(self) -> None:
        """初始化检查器"""
        apis = self.config.get("apis", [])
        
        for api_config in apis:
            try:
                provider = api_config.get("provider", "")
                api_key = api_config.get("api_key", "")
                
                if not api_key:
                    print(f"警告: {provider} 缺少 API Key")
                    continue
                
                # 获取额外的配置参数
                extra_kwargs = {}
                if provider == "openai":
                    extra_kwargs["organization"] = api_config.get("organization")
                elif provider == "minimax":
                    extra_kwargs["base_url"] = api_config.get("base_url")
                
                checker = get_checker(provider, api_key, **extra_kwargs)
                checker.threshold = api_config.get("threshold", 80)
                checker.check_interval = api_config.get("check_interval", 60)
                checker.name = api_config.get("name", provider)
                
                self.checkers.append(checker)
                print(f"✓ 已添加 {checker.name} 检查器")
                
            except Exception as e:
                print(f"✗ 添加 {api_config.get('name', 'unknown')} 失败: {e}")
    
    def _init_notifiers(self) -> None:
        """初始化通知器"""
        notifications = self.config.get("notifications", {})
        
        for notifier_type, notifier_config in notifications.items():
            if not notifier_config.get("enabled", False):
                continue
            
            notifier = create_notifier({**notifier_config, "type": notifier_type})
            if notifier:
                self.notification_manager.add_notifier(notifier)
                print(f"✓ 已添加 {notifier_type} 通知器")
    
    def _check_and_notify(self, checker: BaseChecker) -> None:
        """检查并通知"""
        try:
            result = checker.check()
            
            if result.get("status") == "error":
                print(f"✗ {checker.name} 检查失败: {result.get('error')}")
                return
            
            usage = result.get("usage_percent", 0)
            
            # 检查是否超过阈值
            if usage >= checker.threshold:
                current_time = time.time()
                last_time = self._last_warning.get(checker.name, 0)
                
                # 5分钟内不重复警告
                if current_time - last_time > 300:
                    message = f"""
API: {checker.name}
使用率: {usage:.1f}%
剩余: {result.get('remaining', 'unknown')}
限制: {result.get('limit', 'unknown')}

时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
                    self.notification_manager.send(
                        title=f"API 限流预警 - {checker.name}",
                        message=message,
                        level="warning" if usage < 90 else "critical"
                    )
                    self._last_warning[checker.name] = current_time
                    print(f"⚠️ {checker.name} 使用率 {usage:.1f}% 已预警!")
            else:
                print(f"✓ {checker.name} 使用率: {usage:.1f}%")
                
        except Exception as e:
            print(f"✗ {checker.name} 检查异常: {e}")
    
    def _monitor_loop(self, checker: BaseChecker) -> None:
        """监控循环"""
        while self.running:
            self._check_and_notify(checker)
            time.sleep(checker.check_interval)
    
    def start(self) -> None:
        """启动监控"""
        print("\n" + "="*50)
        print("🔔 API Rate Guardian 启动中...")
        print("="*50 + "\n")
        
        self._init_checkers()
        self._init_notifiers()
        
        if not self.checkers:
            print("❌ 没有可用的 API 检查器")
            sys.exit(1)
        
        print("\n" + "-"*50)
        print("🚀 开始监控...")
        print("-"*50 + "\n")
        
        self.running = True
        
        # 启动监控线程
        for checker in self.checkers:
            thread = threading.Thread(target=self._monitor_loop, args=(checker,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        # 等待
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """停止监控"""
        print("\n\n🛑 正在停止...")
        self.running = False
        
        for thread in self.threads:
            thread.join(timeout=2)
        
        print("✅ 已停止")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="API Rate Guardian - API 限流预警系统")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    args = parser.parse_args()
    
    guardian = APIRateGuardian(args.config)
    
    # 处理退出信号
    def signal_handler(sig, frame):
        guardian.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    guardian.start()


if __name__ == "__main__":
    main()
