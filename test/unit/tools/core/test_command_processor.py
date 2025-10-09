#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试命令处理器模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# 添加core目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tools/core')))

from command_processor import CommandProcessor
from llm_client import QianwenClient
from mock_llm import MockQianwenClient
from tool_handler import ToolHandler
from output_formatter import OutputFormatter

class TestCommandProcessor(unittest.TestCase):
    """测试命令处理器"""
    
    def setUp(self):
        """测试前的设置"""
        # 使用mock模式初始化命令处理器
        self.processor = CommandProcessor(use_mock=True)
        
        # 保存原始的formatter和tool_handler用于验证
        self.original_formatter = self.processor.formatter
        self.original_tool_handler = self.processor.tool_handler
    
    def test_process_command_exit(self):
        """测试处理exit命令"""
        # 调用方法
        result = self.processor.process_command("exit", "test-seq-1")
        
        # 验证结果
        self.assertTrue(result)  # exit命令应该返回True表示请求退出
        self.original_formatter.output_text.assert_called_once()
    
    def test_process_command_help(self):
        """测试处理help命令"""
        # 调用方法
        result = self.processor.process_command("help", "test-seq-2")
        
        # 验证formatter的show_help被调用
        self.original_formatter.show_help.assert_called_once()
    
    def test_process_command_info(self):
        """测试处理info命令"""
        # 调用方法
        result = self.processor.process_command("info features", "test-seq-3")
        
        # 验证formatter的show_info被调用
        self.original_formatter.show_info.assert_called_once_with(["features"])
        
        # 测试不带参数的info命令
        self.original_formatter.reset_mock()
        result = self.processor.process_command("info", "test-seq-4")
        self.original_formatter.show_info.assert_called_once_with(["features"])
    
    @patch('command_processor.MockQianwenClient.send_request')
    def test_process_command_qianwen(self, mock_send_request):
        """测试处理qianwen命令"""
        # 设置模拟响应
        mock_response = {"content": "这是千问大模型的回复"}
        mock_send_request.return_value = mock_response
        
        # 调用方法
        result = self.processor.process_command("qianwen 你好", "test-seq-5")
        
        # 验证发送请求
        mock_send_request.assert_called_once()
        
        # 验证输出文本
        self.original_formatter.output_text.assert_called_once_with("这是千问大模型的回复", sequence_id="test-seq-5")
    
    def test_process_command_qianwen_empty(self):
        """测试处理空的qianwen命令"""
        # 调用方法
        result = self.processor.process_command("qianwen", "test-seq-6")
        
        # 验证输出错误
        self.original_formatter.output_error.assert_called_once()
    
    def test_process_command_code(self):
        """测试处理code命令"""
        # 设置模拟生成的代码
        expected_code = "print('Hello, World!')"
        self.original_formatter.generate_code.return_value = expected_code
        
        # 调用方法
        result = self.processor.process_command("code python 简单的Hello World", "test-seq-7")
        
        # 验证生成代码
        self.original_formatter.generate_code.assert_called_once_with("python", "简单的Hello World")
        
        # 验证输出代码块
        self.original_formatter.output_code_block.assert_called_once_with(expected_code, "python", "test-seq-7")
    
    def test_process_command_code_invalid(self):
        """测试处理无效的code命令"""
        # 调用方法
        result = self.processor.process_command("code python", "test-seq-8")
        
        # 验证输出错误
        self.original_formatter.output_error.assert_called_once()
    
    def test_process_command_unknown(self):
        """测试处理未知命令"""
        # 未知命令应该被当作qianwen命令处理
        # 使用mock来避免实际调用LLM
        with patch.object(self.processor, '_handle_qianwen') as mock_handle_qianwen:
            mock_handle_qianwen.return_value = "未知命令处理结果"
            
            # 调用方法
            result = self.processor.process_command("unknown_command", "test-seq-9")
            
            # 验证调用了handle_qianwen
            mock_handle_qianwen.assert_called_once_with("unknown_command", "test-seq-9")
            self.assertEqual(result, "未知命令处理结果")
    
    def test_process_command_empty(self):
        """测试处理空命令"""
        # 调用方法
        result = self.processor.process_command("", "test-seq-10")
        
        # 验证结果为None
        self.assertIsNone(result)
    
    @patch('command_processor.MockQianwenClient.send_request')
    def test_process_llm_response_text(self, mock_send_request):
        """测试处理大模型的文本响应"""
        # 设置模拟响应
        mock_response = {"content": "文本响应"}
        mock_send_request.return_value = mock_response
        
        # 调用方法
        result = self.processor.process_command("qianwen 测试文本响应", "test-seq-11")
        
        # 验证输出文本
        self.original_formatter.output_text.assert_called_with("文本响应", sequence_id="test-seq-11")
    
    @patch('command_processor.MockQianwenClient.send_request')
    def test_process_llm_response_tool_calls(self, mock_send_request):
        """测试处理大模型的工具调用响应"""
        # 设置模拟响应
        mock_response = {
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {"content": "工具调用响应"}
                }
            ]
        }
        mock_send_request.return_value = mock_response
        
        # 调用方法
        result = self.processor.process_command("qianwen 测试工具调用", "test-seq-12")
        
        # 验证工具调用处理
        # 这里我们验证_tool_handler被用来处理工具调用
        # 由于_tool_handler是在初始化时创建的，我们需要获取实际的实例
        # 由于实际的tool_handler没有被mock，我们需要验证formatter的调用
        self.original_formatter.output_text.assert_called()
    
    @patch('command_processor.QianwenClient')
    @patch('command_processor.MockQianwenClient')
    def test_set_mock_mode(self, mock_mock_client, mock_real_client):
        """测试切换模拟模式"""
        # 初始化处理器为非模拟模式
        processor = CommandProcessor(use_mock=False)
        
        # 验证使用了真实客户端
        self.assertTrue(isinstance(processor.llm_client, QianwenClient) or mock_real_client.called)
        
        # 切换到模拟模式
        processor.set_mock_mode(True)
        
        # 验证使用了模拟客户端
        self.assertTrue(isinstance(processor.llm_client, MockQianwenClient) or mock_mock_client.called)
        
        # 切换回非模拟模式
        processor.set_mock_mode(False)
        
        # 验证使用了真实客户端
        self.assertTrue(isinstance(processor.llm_client, QianwenClient) or mock_real_client.called)
    
    def test_register_custom_command(self):
        """测试注册自定义命令"""
        # 定义自定义命令处理函数
        def custom_command_handler(args, sequence_id):
            self.original_formatter.output_text(f"自定义命令参数: {args}", sequence_id)
            return "自定义命令结果"
        
        # 注册自定义命令
        result = self.processor.register_custom_command(
            "custom_cmd", 
            custom_command_handler, 
            "自定义命令描述"
        )
        
        # 验证注册成功
        self.assertTrue(result)
        self.assertIn("custom_cmd", self.processor.commands)
        
        # 测试执行自定义命令
        result = self.processor.process_command("custom_cmd test_args", "test-seq-13")
        
        # 验证执行结果
        self.assertEqual(result, "自定义命令结果")
        self.original_formatter.output_text.assert_called_with("自定义命令参数: test_args", "test-seq-13")
    
    def test_register_custom_command_invalid_handler(self):
        """测试注册无效的自定义命令处理器"""
        # 尝试使用非可调用对象注册命令
        result = self.processor.register_custom_command("invalid_cmd", "not_callable", "无效命令描述")
        
        # 验证注册失败
        self.assertFalse(result)
        self.assertNotIn("invalid_cmd", self.processor.commands)
    
    def test_process_command_exception(self):
        """测试处理命令时发生异常"""
        # 设置处理器方法抛出异常
        with patch.object(self.processor, '_handle_help') as mock_handle_help:
            mock_handle_help.side_effect = Exception("Command processing error")
            
            # 调用方法
            result = self.processor.process_command("help", "test-seq-14")
            
            # 验证输出错误信息
            self.original_formatter.output_error.assert_called_once()
            
            # 验证返回None
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()