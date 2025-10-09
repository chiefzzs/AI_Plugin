import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import io
import requests
import re

# 添加工具目录到系统路径
import importlib.util
import sys
import os

tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../tools'))
sys.path.append(tools_dir)

# 动态导入interactive-tool.py文件
spec = importlib.util.spec_from_file_location("interactive_tool", os.path.join(tools_dir, "interactive-tool.py"))
interactive_tool = importlib.util.module_from_spec(spec)
sys.modules["interactive_tool"] = interactive_tool
spec.loader.exec_module(interactive_tool)

# 从导入的模块中获取类
InteractiveTool = interactive_tool.InteractiveTool
QianwenClient = interactive_tool.QianwenClient

class TestQianwenClient(unittest.TestCase):
    
    def setUp(self):
        # 创建QianwenClient实例用于测试
        self.client = QianwenClient(api_key="test-api-key", base_url="https://api.example.com")
    
    @patch('requests.post')
    def test_send_request_success(self, mock_post):
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 200,
            "data": {
                "result": "这是千问大模型的回复"
            },
            "message": "success"
        }
        mock_post.return_value = mock_response
        
        # 发送请求
        response = self.client.send_request("你好，千问")
        
        # 验证结果
        self.assertEqual(response, {"code": 200, "data": {"result": "这是千问大模型的回复"}, "message": "success"})
        mock_post.assert_called_once_with(
            "https://api.example.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-api-key"
            },
            data=json.dumps({
                "model": "ERNIE-Bot",
                "messages": [{"role": "user", "content": "你好，千问"}]
            })
        )
    
    @patch('requests.post')
    def test_send_request_api_error(self, mock_post):
        # 模拟API错误
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 400,
            "message": "请求参数错误"
        }
        mock_post.return_value = mock_response
        
        # 发送请求
        response = self.client.send_request("你好，千问")
        
        # 验证结果
        self.assertEqual(response, {"code": 400, "message": "请求参数错误"})
    
    @patch('requests.post')
    def test_send_request_exception(self, mock_post):
        # 模拟请求异常
        mock_post.side_effect = requests.RequestException("网络错误")
        
        # 发送请求
        response = self.client.send_request("你好，千问")
        
        # 验证结果
        self.assertEqual(response, {"code": 500, "message": "请求失败: 网络错误"})

class TestInteractiveToolQianwenIntegration(unittest.TestCase):
    
    def setUp(self):
        # 创建InteractiveTool实例用于测试
        self.tool = InteractiveTool()
    
    @patch('builtins.print')
    def test_output_text(self, mock_print):
        # 测试_output_text方法
        self.tool._output_text("测试文本", is_error=False, sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "text",
                "content": "测试文本",
                "isError": False,
                "isEnd": False,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('builtins.print')
    def test_output_table(self, mock_print):
        # 测试_output_table方法
        header = ["名称", "大小"]
        rows = [["文件1.txt", "1024"], ["文件2.txt", "2048"]]
        metadata = {"total": 2}
        
        self.tool._output_table(header, rows, metadata, sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "table",
                "content": {
                    "header": ["名称", "大小"],
                    "rows": [["文件1.txt", "1024"], ["文件2.txt", "2048"]],
                    "metadata": {"total": 2}
                },
                "isError": False,
                "isEnd": False,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('builtins.print')
    def test_output_progress(self, mock_print):
        # 测试_output_progress方法
        self.tool._output_progress(50, 100, "处理中...", sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "progress",
                "content": {
                    "current": 50,
                    "total": 100,
                    "status": "处理中..."
                },
                "isError": False,
                "isEnd": False,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_request_user_input(self, mock_output_json):
        # 测试请求用户输入
        result = self.tool._request_user_input("请输入:", sequence_id="test-seq")
        
        # 验证输出和返回值
        mock_output_json.assert_called_once_with({
            "type": "input_request",
            "content": {"prompt": "请输入:"},
            "isError": False,
            "isEnd": False,
            "sequenceId": "test-seq"
        })
        self.assertEqual(result, "用户示例输入")
    
    @patch('builtins.print')
    def test_end_execution(self, mock_print):
        # 测试_end_execution方法
        self.tool._end_execution(sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "end",
                "content": "执行已结束",
                "isError": False,
                "isEnd": True,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('builtins.print')
    def test_register_custom_tool(self, mock_print):
        # 测试_register_custom_tool方法
        tool_info = json.dumps({"name": "test-tool", "description": "测试工具"})
        self.tool._register_custom_tool(tool_info, sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "text",
                "content": "已注册自定义工具: test-tool",
                "isError": False,
                "isEnd": False,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('builtins.print')
    def test_register_custom_tool_invalid_json(self, mock_print):
        # 测试_register_custom_tool方法处理无效JSON
        self.tool._register_custom_tool("invalid-json", sequence_id="test-seq")
        
        # 验证错误输出
        mock_print.assert_called_once()
        output = json.loads(mock_print.call_args[0][0])
        self.assertEqual(output["isError"], True)
        self.assertIn("注册自定义工具失败", output["content"])
    
    @patch('builtins.print')
    def test_unregister_custom_tool(self, mock_print):
        # 测试_unregister_custom_tool方法
        self.tool._unregister_custom_tool("test-tool", sequence_id="test-seq")
        
        # 验证输出
        mock_print.assert_called_once_with(
            json.dumps({
                "type": "text",
                "content": "已注销自定义工具: test-tool",
                "isError": False,
                "isEnd": False,
                "sequenceId": "test-seq"
            })
        )
    
    @patch('interactive_tool.InteractiveTool.process_with_qianwen_model')
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_process_command_qianwen(self, mock_output_json, mock_process_qianwen):
        # 测试处理qianwen命令
        self.tool._process_command(["qianwen", "你好，千问"], "test-seq")
        
        # 验证调用
        mock_process_qianwen.assert_called_once_with("你好，千问", "test-seq")
    
    @patch('interactive_tool.InteractiveTool._register_custom_tool')
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_process_command_register_tool(self, mock_output_json, mock_register_tool):
        # 测试处理register_tool命令
        tool_info = json.dumps({"name": "test-tool"})
        self.tool._process_command(["register_tool", tool_info], "test-seq")
        
        # 验证调用
        mock_register_tool.assert_called_once_with(tool_info, "test-seq")
    
    @patch('interactive_tool.InteractiveTool._unregister_custom_tool')
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_process_command_unregister_tool(self, mock_output_json, mock_unregister_tool):
        # 测试处理unregister_tool命令
        self.tool._process_command(["unregister_tool", "test-tool"], "test-seq")
        
        # 验证调用
        mock_unregister_tool.assert_called_once_with("test-tool", "test-seq")
    
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_handle_tool_call(self, mock_output_json):
        # 测试_handle_tool_call方法
        tool_call = {
            "name": "output_text",
            "parameters": {
                "content": "测试文本",
                "is_error": False
            }
        }
        
        result = self.tool._handle_tool_call(tool_call, "test-seq")
        
        # 验证输出和返回值
        # 检查是否至少调用了一次
        self.assertTrue(mock_output_json.called)
        self.assertIsNone(result)
    
    @patch('interactive_tool.InteractiveTool._output_json')
    def test_register_extension_tools(self, mock_output_json):
        # 测试_register_extension_tools方法
        tools = self.tool._register_extension_tools()
        
        # 验证工具列表
        self.assertIsInstance(tools, list)
        self.assertTrue(len(tools) > 0)
        # 检查是否包含所有必要的工具
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("output_text", tool_names)
        self.assertIn("output_table", tool_names)
        self.assertIn("output_progress", tool_names)
        self.assertIn("request_user_input", tool_names)
        self.assertIn("end_execution", tool_names)

if __name__ == '__main__':
    unittest.main()