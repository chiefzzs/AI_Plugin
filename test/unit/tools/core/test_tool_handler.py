#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试工具处理器模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# 添加core目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tools/core')))

from tool_handler import ToolHandler
from output_formatter import OutputFormatter

class TestToolHandler(unittest.TestCase):
    """测试工具处理器"""
    
    def setUp(self):
        """测试前的设置"""
        self.formatter = MagicMock(spec=OutputFormatter)
        self.handler = ToolHandler(self.formatter)
    
    def test_register_extension_tools(self):
        """测试注册扩展工具"""
        # 调用方法
        tools = self.handler.register_extension_tools("test-seq-1")
        
        # 验证返回的工具列表
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # 验证包含基本工具
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("output_text", tool_names)
        self.assertIn("output_table", tool_names)
        self.assertIn("output_progress", tool_names)
        self.assertIn("request_user_input", tool_names)
        self.assertIn("end_execution", tool_names)
    
    def test_handle_tool_call_output_text(self):
        """测试处理output_text工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "output_text",
            "parameters": {
                "content": "测试文本",
                "isError": False
            }
        }
        
        # 调用方法
        self.handler.handle_tool_call(tool_call, "test-seq-2")
        
        # 验证formatter被正确调用
        self.formatter.output_text.assert_called_once_with(
            "测试文本", is_error=False, sequence_id="test-seq-2"
        )
    
    def test_handle_tool_call_output_table(self):
        """测试处理output_table工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "output_table",
            "parameters": {
                "header": ["列1", "列2"],
                "rows": [["值1", "值2"], ["值3", "值4"]],
                "metadata": {"title": "测试表格"}
            }
        }
        
        # 调用方法
        self.handler.handle_tool_call(tool_call, "test-seq-3")
        
        # 验证formatter被正确调用
        self.formatter.output_table.assert_called_once_with(
            ["列1", "列2"],
            [["值1", "值2"], ["值3", "值4"]],
            {"title": "测试表格"},
            "test-seq-3"
        )
    
    def test_handle_tool_call_output_progress(self):
        """测试处理output_progress工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "output_progress",
            "parameters": {
                "current": 75,
                "total": 100,
                "status": "处理中..."
            }
        }
        
        # 调用方法
        self.handler.handle_tool_call(tool_call, "test-seq-4")
        
        # 验证formatter被正确调用
        self.formatter.output_progress.assert_called_once_with(
            75, 100, "处理中...", "test-seq-4"
        )
    
    def test_handle_tool_call_request_user_input(self):
        """测试处理request_user_input工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "request_user_input",
            "parameters": {
                "prompt": "请输入："
            }
        }
        
        # 调用方法
        result = self.handler.handle_tool_call(tool_call, "test-seq-5")
        
        # 验证formatter被正确调用
        self.formatter.output_input_request.assert_called_once_with(
            "请输入：", "test-seq-5"
        )
        
        # 验证返回值
        self.assertEqual(result, "用户示例输入")
    
    def test_handle_tool_call_end_execution(self):
        """测试处理end_execution工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "end_execution",
            "parameters": {}
        }
        
        # 调用方法
        self.handler.handle_tool_call(tool_call, "test-seq-6")
        
        # 验证formatter被正确调用
        self.formatter.output_end.assert_called_once_with(
            "执行已结束", "test-seq-6"
        )
    
    def test_handle_tool_call_unknown(self):
        """测试处理未知工具调用"""
        # 准备工具调用数据
        tool_call = {
            "name": "unknown_tool",
            "parameters": {}
        }
        
        # 调用方法
        result = self.handler.handle_tool_call(tool_call, "test-seq-7")
        
        # 验证输出错误信息
        self.formatter.output_error.assert_called_once()
        
        # 验证返回None
        self.assertIsNone(result)
    
    def test_register_custom_tool(self):
        """测试注册自定义工具"""
        # 准备自定义工具信息
        custom_tool = {
            "name": "test_tool",
            "description": "测试自定义工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "参数1"}
                },
                "required": ["param1"]
            }
        }
        
        # 调用方法
        result = self.handler.register_custom_tool(custom_tool, "test-seq-8")
        
        # 验证注册成功
        self.assertTrue(result)
        self.assertIn("test_tool", self.handler.custom_tools)
        self.assertEqual(self.handler.custom_tools["test_tool"], custom_tool)
        
        # 验证输出成功信息
        self.formatter.output_text.assert_called_once()
    
    def test_register_custom_tool_without_name(self):
        """测试注册没有名称的自定义工具"""
        # 准备没有名称的工具信息
        custom_tool = {
            "description": "没有名称的工具",
            "parameters": {"type": "object", "properties": {}}
        }
        
        # 调用方法
        result = self.handler.register_custom_tool(custom_tool, "test-seq-9")
        
        # 验证注册失败
        self.assertFalse(result)
        
        # 验证输出错误信息
        self.formatter.output_error.assert_called_once()
    
    def test_unregister_custom_tool(self):
        """测试注销自定义工具"""
        # 先注册一个工具
        custom_tool = {
            "name": "test_tool_to_remove",
            "description": "要删除的测试工具",
            "parameters": {"type": "object", "properties": {}}
        }
        self.handler.register_custom_tool(custom_tool)
        
        # 重置mock
        self.formatter.reset_mock()
        
        # 调用方法
        result = self.handler.unregister_custom_tool("test_tool_to_remove", "test-seq-10")
        
        # 验证注销成功
        self.assertTrue(result)
        self.assertNotIn("test_tool_to_remove", self.handler.custom_tools)
        
        # 验证输出成功信息
        self.formatter.output_text.assert_called_once()
    
    def test_unregister_custom_tool_not_exist(self):
        """测试注销不存在的自定义工具"""
        # 调用方法
        result = self.handler.unregister_custom_tool("non_existent_tool", "test-seq-11")
        
        # 验证注销失败
        self.assertFalse(result)
        
        # 验证输出错误信息
        self.formatter.output_error.assert_called_once()
    
    def test_handle_custom_tool(self):
        """测试处理自定义工具调用"""
        # 先注册一个自定义工具
        custom_tool = {
            "name": "custom_tool_to_handle",
            "description": "要处理的自定义工具",
            "parameters": {"type": "object", "properties": {}}
        }
        self.handler.register_custom_tool(custom_tool)
        
        # 重置mock
        self.formatter.reset_mock()
        
        # 准备工具调用数据
        tool_call = {
            "name": "custom_tool_to_handle",
            "parameters": {"param1": "value1", "param2": "value2"}
        }
        
        # 调用方法
        result = self.handler.handle_tool_call(tool_call, "test-seq-12")
        
        # 验证输出信息
        self.assertEqual(self.formatter.output_text.call_count, 2)
        
        # 验证返回结果
        self.assertEqual(result, {"status": "success", "message": "自定义工具执行成功"})
    
    def test_handle_tool_call_exception(self):
        """测试处理工具调用时发生异常"""
        # 设置formatter方法抛出异常
        self.formatter.output_text.side_effect = Exception("Formatter error")
        
        # 准备工具调用数据
        tool_call = {
            "name": "output_text",
            "parameters": {"content": "测试文本"}
        }
        
        # 调用方法
        result = self.handler.handle_tool_call(tool_call, "test-seq-13")
        
        # 验证输出错误信息
        self.formatter.output_error.assert_called_once()
        
        # 验证返回None
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()