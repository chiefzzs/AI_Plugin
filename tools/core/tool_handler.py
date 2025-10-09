#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具处理模块
负责处理大模型的工具调用请求和注册扩展工具
"""

from typing import Dict, Any, List, Optional, Callable
from .output_formatter import OutputFormatter

class ToolHandler:
    """工具处理器，负责处理大模型的工具调用请求和注册扩展工具"""
    
    def __init__(self, formatter: OutputFormatter = None):
        """初始化工具处理器"""
        self.formatter = formatter or OutputFormatter()
        self.custom_tools = {}
    
    def register_extension_tools(self, sequence_id: str = '') -> List[Dict[str, Any]]:
        """注册扩展工具给千问大模型"""
        # 基本工具列表
        tools = [
            {
                "name": "output_text",
                "description": "输出文本信息给用户",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": { "type": "string", "description": "文本内容" },
                        "isError": { "type": "boolean", "description": "是否为错误信息", "default": False }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "output_table",
                "description": "输出表格数据给用户",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "header": { "type": "array", "items": { "type": "string" }, "description": "表头" },
                        "rows": { "type": "array", "items": { "type": "array" }, "description": "行数据" },
                        "metadata": { "type": "object", "description": "表格元数据", "required": False }
                    },
                    "required": ["header", "rows"]
                }
            },
            {
                "name": "output_progress",
                "description": "输出进度信息给用户",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current": { "type": "integer", "description": "当前进度值（0-100）" },
                        "total": { "type": "integer", "description": "总量", "required": False },
                        "status": { "type": "string", "description": "当前状态描述" }
                    },
                    "required": ["current", "status"]
                }
            },
            {
                "name": "request_user_input",
                "description": "请求用户输入",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": { "type": "string", "description": "提示信息" }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "end_execution",
                "description": "结束当前执行流程",
                "parameters": { "type": "object", "properties": {} }
            }
        ]
        
        # 添加自定义工具
        for tool_name, tool_info in self.custom_tools.items():
            tools.append(tool_info)
        
        return tools
    
    def handle_tool_call(self, tool_call: Dict[str, Any], sequence_id: str) -> Any:
        """处理大模型的工具调用请求"""
        try:
            name = tool_call.get("name")
            parameters = tool_call.get("parameters", {})
            
            # 记录工具调用信息
            self.formatter.output_text(f"接收到工具调用: {name}", sequence_id=sequence_id)
            
            # 根据工具名称执行相应操作
            if name == "output_text":
                return self._handle_output_text(parameters, sequence_id)
            elif name == "output_table":
                return self._handle_output_table(parameters, sequence_id)
            elif name == "output_progress":
                return self._handle_output_progress(parameters, sequence_id)
            elif name == "request_user_input":
                return self._handle_request_user_input(parameters, sequence_id)
            elif name == "end_execution":
                return self._handle_end_execution(parameters, sequence_id)
            elif name in self.custom_tools:
                # 处理自定义工具
                return self._handle_custom_tool(name, parameters, sequence_id)
            else:
                self.formatter.output_error(f"未知的工具调用: {name}", sequence_id=sequence_id)
                return None
        except Exception as e:
            self.formatter.output_error(f"处理工具调用失败: {str(e)}", sequence_id=sequence_id)
            return None
    
    def _handle_output_text(self, parameters: Dict[str, Any], sequence_id: str) -> None:
        """处理输出文本工具调用"""
        content = parameters.get("content", "")
        is_error = parameters.get("isError", False)
        self.formatter.output_text(content, is_error=is_error, sequence_id=sequence_id)
    
    def _handle_output_table(self, parameters: Dict[str, Any], sequence_id: str) -> None:
        """处理输出表格工具调用"""
        header = parameters.get("header", [])
        rows = parameters.get("rows", [])
        metadata = parameters.get("metadata", {})
        self.formatter.output_table(header, rows, metadata, sequence_id)
    
    def _handle_output_progress(self, parameters: Dict[str, Any], sequence_id: str) -> None:
        """处理输出进度工具调用"""
        current = parameters.get("current", 0)
        total = parameters.get("total", 100)
        status = parameters.get("status", "处理中...")
        self.formatter.output_progress(current, total, status, sequence_id)
    
    def _handle_request_user_input(self, parameters: Dict[str, Any], sequence_id: str) -> str:
        """处理请求用户输入工具调用"""
        prompt = parameters.get("prompt", "请输入：")
        self.formatter.output_input_request(prompt, sequence_id)
        
        # 模拟用户输入（实际应用中应等待用户输入）
        # 这里返回一个示例输入
        return "用户示例输入"
    
    def _handle_end_execution(self, parameters: Dict[str, Any], sequence_id: str) -> None:
        """处理结束执行工具调用"""
        self.formatter.output_end("执行已结束", sequence_id)
    
    def _handle_custom_tool(self, tool_name: str, parameters: Dict[str, Any], sequence_id: str) -> Any:
        """处理自定义工具调用"""
        # 这里只是简单示例，实际应用中可能需要更复杂的处理逻辑
        self.formatter.output_text(f"执行自定义工具: {tool_name}", sequence_id=sequence_id)
        self.formatter.output_text(f"工具参数: {parameters}", sequence_id=sequence_id)
        return {"status": "success", "message": "自定义工具执行成功"}
    
    def register_custom_tool(self, tool_info: Dict[str, Any], sequence_id: str = '') -> bool:
        """注册自定义工具"""
        try:
            tool_name = tool_info.get('name')
            if not tool_name:
                self.formatter.output_error("注册自定义工具失败：缺少工具名称", sequence_id)
                return False
            
            self.custom_tools[tool_name] = tool_info
            self.formatter.output_text(f"已注册自定义工具: {tool_name}", sequence_id=sequence_id)
            return True
        except Exception as e:
            self.formatter.output_error(f"注册自定义工具失败: {str(e)}", sequence_id)
            return False
    
    def unregister_custom_tool(self, tool_name: str, sequence_id: str = '') -> bool:
        """注销自定义工具"""
        if tool_name in self.custom_tools:
            del self.custom_tools[tool_name]
            self.formatter.output_text(f"已注销自定义工具: {tool_name}", sequence_id=sequence_id)
            return True
        else:
            self.formatter.output_error(f"注销自定义工具失败: 未找到工具 '{tool_name}'", sequence_id)
            return False

# 测试代码
if __name__ == "__main__":
    formatter = OutputFormatter()
    handler = ToolHandler(formatter)
    
    # 测试注册扩展工具
    tools = handler.register_extension_tools()
    print(f"注册的工具数量: {len(tools)}")
    
    # 测试处理工具调用
    handler.handle_tool_call({
        "name": "output_text",
        "parameters": {
            "content": "测试工具调用",
            "isError": False
        }
    }, "test-seq")
    
    # 测试注册和注销自定义工具
    handler.register_custom_tool({
        "name": "test_tool",
        "description": "测试自定义工具",
        "parameters": {"type": "object", "properties": {}}
    })
    
    handler.unregister_custom_tool("test_tool")