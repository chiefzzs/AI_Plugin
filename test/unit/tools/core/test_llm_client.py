#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试千问大模型客户端模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# 添加core目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tools/core')))

from llm_client import QianwenClient

class TestQianwenClient(unittest.TestCase):
    """测试千问大模型客户端"""
    
    def setUp(self):
        """测试前的设置"""
        self.base_url = "https://api-inference.modelscope.cn/v1/"
        self.api_key = "test-api-key"
        self.client = QianwenClient(self.base_url, self.api_key)
    
    @patch('llm_client.requests.post')
    def test_send_request_success(self, mock_post):
        """测试发送请求成功的情况"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": "这是千问大模型的回复"
        }
        mock_post.return_value = mock_response
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }
        sequence_id = "test-seq-1"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertEqual(result, {"content": "这是千问大模型的回复"})
        mock_post.assert_called_once()
        
        # 验证请求参数
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], f"{self.client.base_url}/chat/completions")
        self.assertEqual(call_args[1]["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(call_args[1]["json"], request_data)
    
    @patch('llm_client.requests.post')
    def test_send_request_with_tools(self, mock_post):
        """测试发送带有工具调用的请求"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "使用了工具调用"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "调用工具"}
            ],
            "tools": [
                {
                    "name": "output_text",
                    "description": "输出文本",
                    "parameters": {"type": "object", "properties": {}}
                }
            ]
        }
        sequence_id = "test-seq-2"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
    
    @patch('llm_client.requests.post')
    def test_send_request_api_error(self, mock_post):
        """测试API返回错误的情况"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }
        sequence_id = "test-seq-3"
        
        # 发送请求并验证异常
        with self.assertRaises(Exception) as context:
            self.client.send_request(request_data, sequence_id)
        
        # 验证异常信息
        self.assertIn("API请求失败", str(context.exception))
        self.assertIn("401", str(context.exception))
    
    @patch('llm_client.requests.post')
    def test_send_request_network_error(self, mock_post):
        """测试网络错误的情况"""
        # 模拟网络错误
        mock_post.side_effect = Exception("Network Error")
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }
        sequence_id = "test-seq-4"
        
        # 发送请求并验证异常
        with self.assertRaises(Exception) as context:
            self.client.send_request(request_data, sequence_id)
        
        # 验证异常信息
        self.assertIn("发送请求失败", str(context.exception))
        self.assertIn("Network Error", str(context.exception))
    
    @patch('llm_client.requests.post')
    def test_send_request_invalid_json(self, mock_post):
        """测试返回无效JSON的情况"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }
        sequence_id = "test-seq-5"
        
        # 发送请求并验证异常
        with self.assertRaises(Exception) as context:
            self.client.send_request(request_data, sequence_id)
        
        # 验证异常信息
        self.assertIn("解析响应失败", str(context.exception))
    
    def test_init_with_empty_params(self):
        """测试使用空参数初始化"""
        client = QianwenClient("", "")
        self.assertEqual(client.base_url, "")
        self.assertEqual(client.api_key, "")
    
    @patch('llm_client.requests.post')
    def test_send_request_with_timeout(self, mock_post):
        """测试请求超时的情况"""
        # 模拟超时错误
        mock_post.side_effect = Exception("Request timed out")
        
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "测试超时"}
            ]
        }
        sequence_id = "test-seq-6"
        
        # 发送请求并验证异常
        with self.assertRaises(Exception) as context:
            self.client.send_request(request_data, sequence_id)
        
        # 验证异常信息
        self.assertIn("发送请求失败", str(context.exception))

if __name__ == '__main__':
    unittest.main()