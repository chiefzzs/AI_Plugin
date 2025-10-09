#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试模拟千问大模型客户端模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# 添加core目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tools/core')))

from mock_llm import MockQianwenClient

class TestMockQianwenClient(unittest.TestCase):
    """测试模拟千问大模型客户端"""
    
    def setUp(self):
        """测试前的设置"""
        self.client = MockQianwenClient()
    
    def test_send_request_text_response(self):
        """测试输入1：返回文本类型响应"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入1"}
            ]
        }
        sequence_id = "test-seq-1"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
        self.assertIn("这是模拟的文本响应", result["content"])
    
    def test_send_request_table_response(self):
        """测试输入2：返回表格类型响应"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入2"}
            ]
        }
        sequence_id = "test-seq-2"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_table")
        
        # 验证表格数据
        params = result["tool_calls"][0]["parameters"]
        self.assertIn("header", params)
        self.assertIn("rows", params)
        self.assertEqual(params["header"], ["列1", "列2", "列3"])
        self.assertEqual(len(params["rows"]), 2)
    
    def test_send_request_command_response(self):
        """测试输入3：返回命令行类型响应"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入3"}
            ]
        }
        sequence_id = "test-seq-3"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
        
        # 验证命令行内容
        content = result["tool_calls"][0]["parameters"]["content"]
        self.assertIn("这是模拟的命令行响应", content)
        self.assertIn("ls -la", content)
    
    def test_send_request_code_response(self):
        """测试输入4：返回代码类型响应"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入4"}
            ]
        }
        sequence_id = "test-seq-4"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
        
        # 验证代码内容
        content = result["tool_calls"][0]["parameters"]["content"]
        self.assertIn("这是模拟的代码响应", content)
        self.assertIn("def hello():", content)
    
    def test_send_request_error_command_response(self):
        """测试输入5：返回错误的命令行代码"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入5"}
            ]
        }
        sequence_id = "test-seq-5"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
        
        # 验证错误命令内容
        params = result["tool_calls"][0]["parameters"]
        content = params["content"]
        self.assertIn("这是一个错误的命令行示例", content)
        self.assertIn("rm -rf /", content)
        self.assertTrue(params.get("isError", False))
    
    def test_send_request_sequential_response(self):
        """测试输入10：连续返回多个响应"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入10"}
            ]
        }
        sequence_id = "test-seq-10"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 3)
        
        # 验证第一个响应是文本
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
        
        # 验证第二个响应是进度
        self.assertEqual(result["tool_calls"][1]["name"], "output_progress")
        
        # 验证第三个响应是文本
        self.assertEqual(result["tool_calls"][2]["name"], "output_text")
    
    def test_send_request_multi_type_sequence(self):
        """测试输入11：连续每个类型返回两次"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "输入11"}
            ]
        }
        sequence_id = "test-seq-11"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 4)
        
        # 验证第一个响应是文本
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
        
        # 验证第二个响应是文本（再次）
        self.assertEqual(result["tool_calls"][1]["name"], "output_text")
        
        # 验证第三个响应是表格
        self.assertEqual(result["tool_calls"][2]["name"], "output_table")
        
        # 验证第四个响应是表格（再次）
        self.assertEqual(result["tool_calls"][3]["name"], "output_table")
    
    def test_send_request_default_response(self):
        """测试默认响应（未匹配任何特定输入）"""
        # 准备请求数据
        request_data = {
            "messages": [
                {"role": "user", "content": "这是一个普通的问题"}
            ]
        }
        sequence_id = "test-seq-default"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
        self.assertIn("这是默认的模拟响应", result["content"])
    
    def test_send_request_with_tools(self):
        """测试带有工具调用的请求"""
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
        sequence_id = "test-seq-tools"
        
        # 发送请求
        result = self.client.send_request(request_data, sequence_id)
        
        # 验证结果 - 应该使用工具调用进行响应
        self.assertIn("tool_calls", result)
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "output_text")
    
    def test_reset_state(self):
        """测试重置状态"""
        # 先发送一个请求
        request_data = {
            "messages": [
                {"role": "user", "content": "输入1"}
            ]
        }
        self.client.send_request(request_data, "test-seq-reset-1")
        
        # 重置状态
        self.client.reset_state()
        
        # 再次发送请求，应该得到相同的结果（状态已重置）
        result = self.client.send_request(request_data, "test-seq-reset-2")
        self.assertIn("content", result)
        self.assertIn("这是模拟的文本响应", result["content"])

if __name__ == '__main__':
    unittest.main()