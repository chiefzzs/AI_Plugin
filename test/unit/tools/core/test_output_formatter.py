#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试输出格式化器模块
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# 添加core目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../tools/core')))

from output_formatter import OutputFormatter

class TestOutputFormatter(unittest.TestCase):
    """测试输出格式化器"""
    
    def setUp(self):
        """测试前的设置"""
        self.formatter = OutputFormatter()
    
    @patch('builtins.print')
    def test_output_json(self, mock_print):
        """测试输出JSON格式数据"""
        # 准备数据
        data = {"key": "value", "number": 42}
        
        # 调用方法
        self.formatter.output_json(data)
        
        # 验证print被调用，并且输出了正确的JSON字符串
        mock_print.assert_called_once()
        printed_data = json.loads(mock_print.call_args[0][0])
        self.assertEqual(printed_data, data)
    
    @patch('builtins.print')
    def test_output_text(self, mock_print):
        """测试输出文本信息"""
        # 测试普通文本
        self.formatter.output_text("测试文本", sequence_id="test-seq-1")
        mock_print.assert_called_with(json.dumps({
            "type": "text",
            "content": "测试文本",
            "sequence_id": "test-seq-1"
        }))
        
        # 测试错误文本
        mock_print.reset_mock()
        self.formatter.output_text("错误信息", is_error=True, sequence_id="test-seq-2")
        mock_print.assert_called_with(json.dumps({
            "type": "text",
            "content": "错误信息",
            "isError": True,
            "sequence_id": "test-seq-2"
        }))
        
        # 测试不带sequence_id
        mock_print.reset_mock()
        self.formatter.output_text("无序列ID文本")
        printed_data = json.loads(mock_print.call_args[0][0])
        self.assertEqual(printed_data["type"], "text")
        self.assertEqual(printed_data["content"], "无序列ID文本")
        self.assertNotIn("sequence_id", printed_data)
    
    @patch('builtins.print')
    def test_output_error(self, mock_print):
        """测试输出错误信息"""
        # 调用方法
        self.formatter.output_error("错误消息", sequence_id="test-seq-3")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "text",
            "content": "错误消息",
            "isError": True,
            "sequence_id": "test-seq-3"
        }))
    
    @patch('builtins.print')
    def test_output_table(self, mock_print):
        """测试输出表格数据"""
        # 准备数据
        header = ["姓名", "年龄", "城市"]
        rows = [["张三", 25, "北京"], ["李四", 30, "上海"]]
        metadata = {"title": "用户信息表"}
        
        # 调用方法
        self.formatter.output_table(header, rows, metadata, "test-seq-4")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "table",
            "header": header,
            "rows": rows,
            "metadata": metadata,
            "sequence_id": "test-seq-4"
        }))
        
        # 测试不带metadata和sequence_id
        mock_print.reset_mock()
        self.formatter.output_table(header, rows)
        printed_data = json.loads(mock_print.call_args[0][0])
        self.assertEqual(printed_data["type"], "table")
        self.assertEqual(printed_data["header"], header)
        self.assertEqual(printed_data["rows"], rows)
        self.assertNotIn("metadata", printed_data)
        self.assertNotIn("sequence_id", printed_data)
    
    @patch('builtins.print')
    def test_output_progress(self, mock_print):
        """测试输出进度信息"""
        # 调用方法
        self.formatter.output_progress(50, 100, "处理中...", "test-seq-5")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "progress",
            "current": 50,
            "total": 100,
            "status": "处理中...",
            "sequence_id": "test-seq-5"
        }))
    
    @patch('builtins.print')
    def test_output_input_request(self, mock_print):
        """测试输出输入请求"""
        # 调用方法
        self.formatter.output_input_request("请输入姓名：", "test-seq-6")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "input_request",
            "prompt": "请输入姓名：",
            "sequence_id": "test-seq-6"
        }))
    
    @patch('builtins.print')
    def test_output_end(self, mock_print):
        """测试输出结束信息"""
        # 调用方法
        self.formatter.output_end("执行完成", "test-seq-7")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "end",
            "message": "执行完成",
            "sequence_id": "test-seq-7"
        }))
    
    @patch('builtins.print')
    def test_show_help(self, mock_print):
        """测试显示帮助信息"""
        # 调用方法
        self.formatter.show_help()
        
        # 验证print被调用了多次，输出帮助信息
        self.assertGreater(mock_print.call_count, 0)
        
        # 验证输出的内容包含帮助信息的关键字
        for call in mock_print.call_args_list:
            output = json.loads(call[0][0])
            self.assertEqual(output["type"], "text")
    
    @patch('builtins.print')
    def test_show_info(self, mock_print):
        """测试显示信息"""
        # 测试features主题
        self.formatter.show_info(["features"])
        
        # 验证输出
        self.assertGreater(mock_print.call_count, 0)
        
        # 重置mock并测试commands主题
        mock_print.reset_mock()
        self.formatter.show_info(["commands"])
        
        # 验证输出包含commands相关信息
        found_commands = False
        for call in mock_print.call_args_list:
            output = json.loads(call[0][0])
            if "commands" in output["content"].lower():
                found_commands = True
                break
        self.assertTrue(found_commands)
        
        # 测试未知主题
        mock_print.reset_mock()
        self.formatter.show_info(["unknown_topic"])
        self.assertGreater(mock_print.call_count, 0)
    
    def test_generate_code(self):
        """测试生成代码"""
        # 测试生成Python代码
        python_code = self.formatter.generate_code("python", "简单的加法函数")
        self.assertIsInstance(python_code, str)
        self.assertIn("def", python_code)
        
        # 测试生成Bash代码
        bash_code = self.formatter.generate_code("bash", "列出目录内容")
        self.assertIsInstance(bash_code, str)
        self.assertIn("ls", bash_code)
        
        # 测试生成JavaScript代码
        js_code = self.formatter.generate_code("javascript", "简单的Hello World")
        self.assertIsInstance(js_code, str)
        self.assertIn("console.log", js_code)
        
        # 测试生成未知类型的代码
        unknown_code = self.formatter.generate_code("unknown", "测试")
        self.assertIsInstance(unknown_code, str)
        self.assertIn("Unknown code type", unknown_code)
    
    @patch('builtins.print')
    def test_output_code_block(self, mock_print):
        """测试输出代码块"""
        # 准备代码
        code = "print('Hello, World!')"
        
        # 调用方法
        self.formatter.output_code_block(code, "python", "test-seq-8")
        
        # 验证输出
        mock_print.assert_called_with(json.dumps({
            "type": "code",
            "code_type": "python",
            "content": code,
            "sequence_id": "test-seq-8"
        }))
    
    @patch('builtins.print')
    def test_output_welcome(self, mock_print):
        """测试输出欢迎信息"""
        # 调用方法
        self.formatter.output_welcome()
        
        # 验证输出
        mock_print.assert_called()
        output = json.loads(mock_print.call_args[0][0])
        self.assertEqual(output["type"], "text")
        self.assertIn("欢迎", output["content"])
    
    @patch('builtins.print')
    def test_output_goodbye(self, mock_print):
        """测试输出告别信息"""
        # 调用方法
        self.formatter.output_goodbye()
        
        # 验证输出
        mock_print.assert_called()
        output = json.loads(mock_print.call_args[0][0])
        self.assertEqual(output["type"], "text")
        self.assertIn("再见", output["content"])

if __name__ == '__main__':
    unittest.main()