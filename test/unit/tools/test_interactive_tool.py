#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交互式工具主程序
"""

import unittest
from unittest.mock import patch, MagicMock, call
import json
import os
import sys

# 添加tools目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../tools')))

from interactive_tool import InteractiveTool, load_config

class TestInteractiveTool(unittest.TestCase):
    """测试交互式工具主类"""
    
    def setUp(self):
        """测试前的设置"""
        # 使用mock模式初始化交互式工具
        self.tool = InteractiveTool(use_mock=True)
    
    @patch.object(InteractiveTool, '_get_user_input')
    def test_start_exit(self, mock_get_user_input):
        """测试启动并退出交互式工具"""
        # 设置模拟输入，第一次返回exit，第二次返回None（结束循环）
        mock_get_user_input.side_effect = ["exit", None]
        
        # 调用方法
        self.tool.start()
        
        # 验证running状态
        self.assertFalse(self.tool.running)
        
        # 验证输出欢迎和告别信息
        self.tool.formatter.output_welcome.assert_called_once()
        self.tool.formatter.output_goodbye.assert_called_once()
    
    @patch.object(InteractiveTool, '_get_user_input')
    def test_start_with_commands(self, mock_get_user_input):
        """测试启动并执行一些命令"""
        # 设置模拟输入
        mock_get_user_input.side_effect = ["help", "info commands", "exit", None]
        
        # 调用方法
        self.tool.start()
        
        # 验证执行了相应的命令
        self.tool.formatter.show_help.assert_called_once()
        self.tool.formatter.show_info.assert_called_once_with(["commands"])
    
    @patch.object(InteractiveTool, '_get_user_input')
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_start_with_keyboard_interrupt(self, mock_input, mock_get_user_input):
        """测试启动时的键盘中断处理"""
        # 由于我们使用了use_mock=True，所以实际的input不会被调用
        # 但为了完整性，我们还是mock它
        
        # 模拟_get_user_input抛出KeyboardInterrupt
        mock_get_user_input.side_effect = KeyboardInterrupt
        
        # 调用方法
        self.tool.start()
        
        # 验证running状态
        self.assertFalse(self.tool.running)
        
        # 验证输出中断信息
        # 由于我们mock了_get_user_input，所以中断处理逻辑可能不会执行到
        # 这里我们主要验证程序能够正常退出
    
    @patch.object(InteractiveTool, '_generate_sequence_id', return_value="fixed-seq-id")
    def test_execute(self, mock_generate_sequence_id):
        """测试执行单个命令"""
        # 设置processor的process_command返回值
        expected_result = "命令执行结果"
        self.tool.processor.process_command = MagicMock(return_value=expected_result)
        
        # 调用方法
        result = self.tool.execute("test command")
        
        # 验证结果
        self.assertEqual(result, expected_result)
        self.tool.processor.process_command.assert_called_once_with("test command", "fixed-seq-id")
    
    def test_process_command(self):
        """测试process_command方法（execute的别名）"""
        # 设置execute方法返回值
        expected_result = "命令处理结果"
        self.tool.execute = MagicMock(return_value=expected_result)
        
        # 调用方法
        result = self.tool.process_command("test command")
        
        # 验证结果
        self.assertEqual(result, expected_result)
        self.tool.execute.assert_called_once_with("test command")
    
    def test_handle_tool_call(self):
        """测试处理工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "output_text",
            "parameters": {"content": "测试工具调用"}
        }
        sequence_id = "test-seq-tool"
        expected_result = "工具调用结果"
        
        # 设置tool_handler的handle_tool_call返回值
        self.tool.processor.tool_handler.handle_tool_call = MagicMock(return_value=expected_result)
        
        # 调用方法
        result = self.tool.handle_tool_call(tool_call, sequence_id)
        
        # 验证结果
        self.assertEqual(result, expected_result)
        self.tool.processor.tool_handler.handle_tool_call.assert_called_once_with(tool_call, sequence_id)
    
    def test_output_json(self):
        """测试输出JSON格式数据"""
        # 准备数据
        data = {"key": "value"}
        
        # 调用方法
        self.tool.output_json(data)
        
        # 验证formatter被调用
        self.tool.formatter.output_json.assert_called_once_with(data)
    
    def test_show_help(self):
        """测试显示帮助信息"""
        # 调用方法
        self.tool.show_help()
        
        # 验证formatter被调用
        self.tool.formatter.show_help.assert_called_once()
    
    def test_show_info(self):
        """测试显示信息"""
        # 调用方法
        topics = ["features", "commands"]
        self.tool.show_info(topics)
        
        # 验证formatter被调用
        self.tool.formatter.show_info.assert_called_once_with(topics)
    
    def test_generate_code(self):
        """测试生成代码"""
        # 设置formatter的generate_code返回值
        expected_code = "print('Hello')"
        self.tool.formatter.generate_code = MagicMock(return_value=expected_code)
        
        # 调用方法
        code = self.tool.generate_code("python", "简单的Hello程序")
        
        # 验证结果
        self.assertEqual(code, expected_code)
        self.tool.formatter.generate_code.assert_called_once_with("python", "简单的Hello程序")
    
    def test_output_code_block(self):
        """测试输出代码块"""
        # 准备数据
        code = "print('Hello')"
        code_type = "python"
        sequence_id = "test-seq-code"
        
        # 调用方法
        self.tool.output_code_block(code, code_type, sequence_id)
        
        # 验证formatter被调用
        self.tool.formatter.output_code_block.assert_called_once_with(code, code_type, sequence_id)
    
    def test_set_mock_mode(self):
        """测试设置模拟模式"""
        # 验证初始模式
        self.assertTrue(self.tool.use_mock)
        
        # 切换到非模拟模式
        self.tool.set_mock_mode(False)
        
        # 验证模式已切换
        self.assertFalse(self.tool.use_mock)
        
        # 验证processor的模式也已切换
        self.tool.processor.set_mock_mode.assert_called_once_with(False)
        
        # 切换回模拟模式
        self.tool.set_mock_mode(True)
        
        # 验证模式已切换
        self.assertTrue(self.tool.use_mock)
        
        # 验证processor的模式也已切换
        self.assertEqual(self.tool.processor.set_mock_mode.call_count, 2)
    
    def test_register_custom_command(self):
        """测试注册自定义命令"""
        # 定义自定义命令处理函数
        def custom_handler(args, sequence_id):
            return "自定义命令执行结果"
        
        # 调用方法
        result = self.tool.register_custom_command(
            "custom_cmd", 
            custom_handler, 
            "自定义命令描述"
        )
        
        # 验证结果
        self.assertTrue(result)
        self.tool.processor.register_custom_command.assert_called_once_with(
            "custom_cmd", custom_handler, "自定义命令描述"
        )
    
    def test_mock_input(self):
        """测试模拟输入功能"""
        # 调用mock_input方法
        # 第一次调用应该返回第一个命令
        command1 = self.tool._mock_input()
        self.assertEqual(command1, "help")
        
        # 第二次调用应该返回第二个命令
        command2 = self.tool._mock_input()
        self.assertEqual(command2, "info commands")
        
        # 重置模拟索引以便后续测试
        if hasattr(self.tool, '_mock_index'):
            delattr(self.tool, '_mock_index')
    
    def test_generate_sequence_id(self):
        """测试生成序列ID"""
        # 调用方法多次
        seq_id1 = self.tool._generate_sequence_id()
        seq_id2 = self.tool._generate_sequence_id()
        seq_id3 = self.tool._generate_sequence_id()
        
        # 验证生成的ID是唯一的且递增的
        self.assertNotEqual(seq_id1, seq_id2)
        self.assertNotEqual(seq_id2, seq_id3)
        self.assertTrue(seq_id1.startswith("seq-"))
        self.assertTrue(seq_id2.startswith("seq-"))
        self.assertTrue(seq_id3.startswith("seq-"))
        
        # 验证序列ID的数字部分是递增的
        num1 = int(seq_id1.split("-")[1])
        num2 = int(seq_id2.split("-")[1])
        num3 = int(seq_id3.split("-")[1])
        self.assertEqual(num2, num1 + 1)
        self.assertEqual(num3, num2 + 1)

class TestLoadConfig(unittest.TestCase):
    """测试加载配置函数"""
    
    @patch('os.environ.get')
    def test_load_config_default(self, mock_getenv):
        """测试加载默认配置"""
        # 设置环境变量模拟返回值
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_BASE_URL': 'https://default-api.com/v1/',
            'LLM_TOKEN': 'default-token'
        }.get(key, default)
        
        # 调用方法
        config = load_config()
        
        # 验证默认配置
        self.assertEqual(config["use_mock"], False)
        self.assertEqual(config["llm_base_url"], "https://default-api.com/v1/")
        self.assertEqual(config["llm_token"], "default-token")
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    @patch('json.load')
    @patch('os.environ.get')
    def test_load_config_from_file(self, mock_getenv, mock_json_load, mock_open, mock_exists):
        """测试从配置文件加载配置"""
        # 设置环境变量模拟返回值
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_BASE_URL': 'https://env-api.com/v1/',
            'LLM_TOKEN': 'env-token'
        }.get(key, default)
        
        # 设置配置文件模拟内容
        mock_json_load.return_value = {
            "use_mock": True,
            "llm_base_url": "https://config-api.com/v1/",
            "llm_token": "config-token"
        }
        
        # 调用方法
        config = load_config("test_config.json")
        
        # 验证配置文件中的配置覆盖了默认值
        self.assertEqual(config["use_mock"], True)
        self.assertEqual(config["llm_base_url"], "https://config-api.com/v1/")
        self.assertEqual(config["llm_token"], "config-token")
        
        # 验证打开了正确的文件
        mock_open.assert_called_once_with("test_config.json", 'r', encoding='utf-8')
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open')
    @patch('json.load', side_effect=Exception("JSON解析错误"))
    @patch('os.environ.get')
    @patch('builtins.print')
    def test_load_config_file_error(self, mock_print, mock_getenv, mock_json_load, mock_open, mock_exists):
        """测试加载配置文件时发生错误"""
        # 设置环境变量模拟返回值
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_BASE_URL': 'https://env-api.com/v1/',
            'LLM_TOKEN': 'env-token'
        }.get(key, default)
        
        # 调用方法
        config = load_config("invalid_config.json")
        
        # 验证即使配置文件出错，仍然返回默认配置
        self.assertEqual(config["use_mock"], False)
        self.assertEqual(config["llm_base_url"], "https://env-api.com/v1/")
        self.assertEqual(config["llm_token"], "env-token")
        
        # 验证输出了错误信息
        mock_print.assert_called_once()
    
    @patch('os.path.exists', return_value=False)
    @patch('os.environ.get')
    def test_load_config_file_not_exist(self, mock_getenv, mock_exists):
        """测试配置文件不存在的情况"""
        # 设置环境变量模拟返回值
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_BASE_URL': 'https://env-api.com/v1/',
            'LLM_TOKEN': 'env-token'
        }.get(key, default)
        
        # 调用方法
        config = load_config("non_existent_config.json")
        
        # 验证返回默认配置
        self.assertEqual(config["use_mock"], False)
        self.assertEqual(config["llm_base_url"], "https://env-api.com/v1/")
        self.assertEqual(config["llm_token"], "env-token")

if __name__ == '__main__':
    unittest.main()