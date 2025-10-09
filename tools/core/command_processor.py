#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令处理模块
负责处理命令解析和执行
"""

import json
import os
from typing import Dict, Any, List, Optional
from .llm_client import QianwenClient
from .mock_llm import MockQianwenClient
from .tool_handler import ToolHandler
from .output_formatter import OutputFormatter

class CommandProcessor:
    """命令处理器，负责处理命令解析和执行"""
    
    def __init__(self, use_mock: bool = False):
        """初始化命令处理器"""
        self.use_mock = use_mock
        self.formatter = OutputFormatter()
        self.tool_handler = ToolHandler(self.formatter)
        
        # 根据配置决定使用真实客户端还是模拟客户端
        if use_mock:
            self.llm_client = MockQianwenClient()
        else:
            # 从环境变量获取千问大模型配置
            base_url = os.environ.get('LLM_BASE_URL', 'https://api-inference.modelscope.cn/v1/')
            api_key = os.environ.get('LLM_TOKEN', '')
            self.llm_client = QianwenClient(base_url, api_key)
        
        # 命令映射表
        self.commands = {
            'exit': self._handle_exit,
            'help': self._handle_help,
            'info': self._handle_info,
            'qianwen': self._handle_qianwen,
            'code': self._handle_code,
        }
    
    def process_command(self, command: str, sequence_id: str = '') -> Any:
        """处理用户输入的命令"""
        try:
            # 命令解析
            parts = command.strip().split(' ', 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''
            
            # 检查是否为支持的命令
            if cmd in self.commands:
                return self.commands[cmd](args, sequence_id)
            elif cmd == '':
                # 空命令，不做任何处理
                return None
            else:
                # 未识别的命令，尝试通过千问大模型处理
                return self._handle_qianwen(command, sequence_id)
        except Exception as e:
            self.formatter.output_error(f"处理命令失败: {str(e)}", sequence_id)
            return None
    
    def _handle_exit(self, args: str, sequence_id: str) -> bool:
        """处理退出命令"""
        self.formatter.output_text("正在退出...", sequence_id)
        return True  # 返回True表示请求退出
    
    def _handle_help(self, args: str, sequence_id: str) -> None:
        """处理帮助命令"""
        self.formatter.show_help()
    
    def _handle_info(self, args: str, sequence_id: str) -> None:
        """处理信息命令"""
        topics = args.strip().split() if args.strip() else ['features']
        self.formatter.show_info(topics)
    
    def _handle_qianwen(self, args: str, sequence_id: str) -> Any:
        """处理千问大模型命令"""
        if not args.strip():
            self.formatter.output_error("请提供要发送给千问大模型的内容", sequence_id)
            return None
        
        try:
            self.formatter.output_progress(0, 100, "正在向千问大模型发送请求...", sequence_id)
            
            # 准备发送给千问大模型的请求
            request_data = {
                "messages": [
                    {"role": "user", "content": args.strip()}
                ],
                "tools": self.tool_handler.register_extension_tools(sequence_id)
            }
            
            # 发送请求到千问大模型
            response = self.llm_client.send_request(request_data, sequence_id)
            self.formatter.output_progress(50, 100, "正在处理千问大模型响应...", sequence_id)
            
            # 处理响应
            return self._process_llm_response(response, sequence_id)
        except Exception as e:
            self.formatter.output_error(f"千问大模型请求失败: {str(e)}", sequence_id)
            return None
    
    def _process_llm_response(self, response: Dict[str, Any], sequence_id: str) -> Any:
        """处理大模型的响应"""
        # 检查响应是否包含工具调用
        if isinstance(response, dict) and "tool_calls" in response and response["tool_calls"]:
            self.formatter.output_progress(75, 100, "正在处理工具调用...", sequence_id)
            
            # 处理所有工具调用
            results = []
            for tool_call in response["tool_calls"]:
                result = self.tool_handler.handle_tool_call(tool_call, sequence_id)
                results.append(result)
            
            self.formatter.output_progress(100, 100, "工具调用处理完成", sequence_id)
            return results
        
        # 普通文本响应
        elif isinstance(response, dict) and "content" in response:
            self.formatter.output_text(response["content"], sequence_id=sequence_id)
        elif isinstance(response, str):
            self.formatter.output_text(response, sequence_id=sequence_id)
        
        self.formatter.output_progress(100, 100, "响应处理完成", sequence_id)
        return response
    
    def _handle_code(self, args: str, sequence_id: str) -> None:
        """处理代码生成命令"""
        parts = args.strip().split(' ', 1)
        if len(parts) < 2:
            self.formatter.output_error("请指定代码类型和描述，格式: code <type> <description>", sequence_id)
            return
        
        code_type = parts[0].lower()
        description = parts[1]
        
        try:
            self.formatter.output_progress(0, 100, "正在生成代码...", sequence_id)
            
            # 生成代码
            code = self.formatter.generate_code(code_type, description)
            
            # 输出代码
            self.formatter.output_code_block(code, code_type, sequence_id)
            self.formatter.output_progress(100, 100, "代码生成完成", sequence_id)
        except Exception as e:
            self.formatter.output_error(f"代码生成失败: {str(e)}", sequence_id)
    
    def set_mock_mode(self, use_mock: bool) -> None:
        """设置是否使用模拟模式"""
        if use_mock != self.use_mock:
            self.use_mock = use_mock
            if use_mock:
                self.llm_client = MockQianwenClient()
            else:
                # 从环境变量获取千问大模型配置
                base_url = os.environ.get('LLM_BASE_URL', 'https://api-inference.modelscope.cn/v1/')
                api_key = os.environ.get('LLM_TOKEN', '')
                self.llm_client = QianwenClient(base_url, api_key)
            
            self.formatter.output_text(f"已切换到{'模拟' if use_mock else '真实'}千问大模型模式", "")
    
    def register_custom_command(self, name: str, handler: callable, description: str = "") -> bool:
        """注册自定义命令"""
        try:
            if not callable(handler):
                self.formatter.output_error("注册自定义命令失败：处理器必须是可调用对象", "")
                return False
            
            self.commands[name.lower()] = handler
            
            # 如果提供了描述，更新帮助信息
            if description:
                self.formatter.register_custom_command(name, description)
            
            return True
        except Exception as e:
            self.formatter.output_error(f"注册自定义命令失败: {str(e)}", "")
            return False

# 测试代码
if __name__ == "__main__":
    # 使用模拟模式进行测试
    processor = CommandProcessor(use_mock=True)
    
    # 测试help命令
    processor.process_command("help", "test-seq")
    
    # 测试info命令
    processor.process_command("info commands", "test-seq")
    
    # 测试qianwen命令（使用模拟响应）
    processor.process_command("qianwen 你好", "test-seq")
    
    # 测试代码生成命令
    processor.process_command("code python 生成一个简单的Hello World程序", "test-seq")
    
    # 测试自定义命令注册
    def custom_handler(args, seq_id):
        processor.formatter.output_text(f"执行自定义命令，参数：{args}", seq_id)
    
    processor.register_custom_command("custom", custom_handler, "自定义命令示例")
    processor.process_command("custom test", "test-seq")