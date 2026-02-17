"""
API Rate Guardian - 各平台API检查实现
"""
import os
import time
import json
import yaml
import requests
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod


class BaseChecker(ABC):
    """检查器基类"""
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """检查API使用情况"""
        pass


class OpenAIChecker(BaseChecker):
    """OpenAI API 检查器"""
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        self.api_key = api_key
        self.organization = organization
        self.base_url = "https://api.openai.com/v1"
    
    def check(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        
        try:
            # 使用 Embeddings API 检查限流
            resp = requests.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json={"input": "test", "model": "text-embedding-3-small"},
                timeout=10
            )
            
            remaining = resp.headers.get("X-RateLimit-Limit", "unknown")
            remaining_requests = resp.headers.get("X-RateLimit-Remaining", "unknown")
            reset_time = resp.headers.get("X-RateLimit-Reset", "unknown")
            
            # 计算使用百分比
            if remaining_requests != "unknown" and remaining != "unknown":
                usage_percent = (int(remaining) - int(remaining_requests)) / int(remaining) * 100
            else:
                usage_percent = 0
            
            return {
                "provider": "openai",
                "usage_percent": usage_percent,
                "remaining": remaining_requests,
                "limit": remaining,
                "reset_time": reset_time,
                "status": "ok" if resp.status_code == 200 else "error"
            }
        except Exception as e:
            return {
                "provider": "openai",
                "status": "error",
                "error": str(e)
            }


class DeepSeekChecker(BaseChecker):
    """DeepSeek API 检查器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
    
    def check(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                timeout=10
            )
            
            remaining = resp.headers.get("X-RateLimit-Remaining-Limit", "unknown")
            remaining_requests = resp.headers.get("X-RateLimit-Remaining-Requests", "unknown")
            reset_time = resp.headers.get("X-RateLimit-Reset-TTokens", "unknown")
            
            if remaining_requests != "unknown" and remaining != "unknown":
                usage_percent = (int(remaining) - int(remaining_requests)) / int(remaining) * 100
            else:
                usage_percent = 0
            
            return {
                "provider": "deepseek",
                "usage_percent": usage_percent,
                "remaining": remaining_requests,
                "limit": remaining,
                "reset_time": reset_time,
                "status": "ok" if resp.status_code == 200 else "error"
            }
        except Exception as e:
            return {
                "provider": "deepseek",
                "status": "error",
                "error": str(e)
            }


class MiniMaxChecker(BaseChecker):
    """MiniMax API 检查器"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.minimaxi.com"
    
    def check(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # MiniMax 使用 Anthropic 兼容 API
            resp = requests.post(
                f"{self.base_url}/anthropic/v1/messages",
                headers=headers,
                json={"model": "MiniMax-M2.1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                timeout=10
            )
            
            # MiniMax 的响应头
            remaining = resp.headers.get("X-RateLimit-Limit", "unknown")
            remaining_requests = resp.headers.get("X-RateLimit-Remaining", "unknown")
            reset_time = resp.headers.get("X-RateLimit-Reset", "unknown")
            
            if remaining_requests != "unknown" and remaining != "unknown":
                usage_percent = (int(remaining) - int(remaining_requests)) / int(remaining) * 100
            else:
                usage_percent = 0
            
            return {
                "provider": "minimax",
                "usage_percent": usage_percent,
                "remaining": remaining_requests,
                "limit": remaining,
                "reset_time": reset_time,
                "status": "ok" if resp.status_code in [200, 201] else "error"
            }
        except Exception as e:
            return {
                "provider": "minimax",
                "status": "error",
                "error": str(e)
            }


class AnthropicChecker(BaseChecker):
    """Anthropic (Claude) API 检查器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com"
    
    def check(self) -> Dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json={"model": "claude-3-5-sonnet-20241022", "max, "messages":_tokens": 1 [{"role": "user", "content": "hi"}]},
                timeout=10
            )
            
            remaining = resp.headers.get("anthropic-ratelimit-limit", "unknown")
            remaining_requests = resp.headers.get("anthropic-ratelimit-remaining", "unknown")
            reset_time = resp.headers.get("anthropic-ratelimit-reset", "unknown")
            
            if remaining_requests != "unknown" and remaining != "unknown":
                usage_percent = (int(remaining) - int(remaining_requests)) / int(remaining) * 100
            else:
                usage_percent = 0
            
            return {
                "provider": "anthropic",
                "usage_percent": usage_percent,
                "remaining": remaining_requests,
                "limit": remaining,
                "reset_time": reset_time,
                "status": "ok" if resp.status_code in [200, 201] else "error"
            }
        except Exception as e:
            return {
                "provider": "anthropic",
                "status": "error",
                "error": str(e)
            }


class GitHubChecker(BaseChecker):
    """GitHub API 检查器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.github.com"
    
    def check(self) -> Dict[str, Any]:
        headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            resp = requests.get(f"{self.base_url}/rate_limit", headers=headers, timeout=10)
            data = resp.json()
            
            core_limit = data["resources"]["core"]["limit"]
            core_remaining = data["resources"]["core"]["remaining"]
            core_reset = data["resources"]["core"]["reset"]
            
            usage_percent = (core_limit - core_remaining) / core_limit * 100
            
            return {
                "provider": "github",
                "usage_percent": usage_percent,
                "remaining": core_remaining,
                "limit": core_limit,
                "reset_time": core_reset,
                "status": "ok" if resp.status_code == 200 else "error"
            }
        except Exception as e:
            return {
                "provider": "github",
                "status": "error",
                "error": str(e)
            }


def get_checker(provider: str, api_key: str, **kwargs) -> BaseChecker:
    """工厂函数：获取对应的检查器"""
    checkers = {
        "openai": OpenAIChecker,
        "deepseek": DeepSeekChecker,
        "minimax": MiniMaxChecker,
        "anthropic": AnthropicChecker,
        "github": GitHubChecker,
    }
    
    provider_lower = provider.lower()
    if provider_lower not in checkers:
        raise ValueError(f"不支持的 provider: {provider}")
    
    return checkers[provider_lower](api_key, **kwargs)


if __name__ == "__main__":
    # 测试
    print("🔔 API Rate Guardian - 检查器测试\n")
    
    # 这里只是演示，实际使用需要填入真实的 API Key
    print("请在配置文件中设置 API Key")
