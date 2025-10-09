#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
千问大模型客户端模块
负责处理与千问大模型的通信，支持从环境变量读取配置
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional

class QianwenClient:
    """千问大模型客户端，处理与千问大模型的通信"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """初始化千问大模型客户端，优先从环境变量读取配置"""
        # 如果明确传入了空字符串，就使用空字符串
        # 只有在参数为None时才回退到环境变量或默认值
        if base_url is None:
            self.base_url = os.environ.get('LLM_BASE_URL', 'http://localhost:3000/api/qianwen')
        else:
            self.base_url = base_url
        
        if api_key is None:
            self.api_key = os.environ.get('LLM_TOKEN', '')
        else:
            self.api_key = api_key
        
        # 为了向后兼容保留旧的属性名
        self.api_base = self.base_url
        self.api_token = self.api_key
        
        # 如果API基础URL末尾有斜杠，去除它
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    def send_request(self, data: Dict[str, Any], sequence_id: Optional[str] = None) -> Dict[str, Any]:
        """向千问大模型发送请求"""
        try:
            # 构建请求头
            headers = {
                'Content-Type': 'application/json',
            }
            
            # 如果有API token，添加到请求头
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # 如果提供了sequence_id，可以在请求数据中包含它
            if sequence_id:
                # 根据实际API需求调整如何包含sequence_id
                pass
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",  # 假设这是千问API的端点
                headers=headers,
                json=data,
                timeout=30  # 设置超时时间
            )
            
            # 检查响应状态
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    raise Exception(f"解析响应失败: 返回了无效的JSON格式数据")
            else:
                raise Exception(f"API请求失败: HTTP {response.status_code}, {response.text}")
        except requests.exceptions.ConnectionError:
            raise Exception("发送请求失败: Network Error")
        except requests.exceptions.Timeout:
            raise Exception("发送请求失败: Request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"发送请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"发送请求失败: {str(e)}")

# 测试代码
if __name__ == "__main__":
    # 创建客户端实例
    client = QianwenClient()
    
    # 打印配置信息（不打印token的完整值）
    print(f"API Base URL: {client.base_url}")
    print(f"API Token: {'已配置' if client.api_key else '未配置'}")
    
    # 如果设置了mock环境变量，测试mock功能
    if os.environ.get('USE_MOCK_LLM') == 'true':
        from .mock_llm import MockQianwenClient
        mock_client = MockQianwenClient()
        response = mock_client.send_request({"content": "test"})
        print("Mock LLM Response:")
        print(json.dumps(response, ensure_ascii=False, indent=2))