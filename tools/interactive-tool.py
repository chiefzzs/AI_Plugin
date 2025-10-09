#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主命令文件：interactive-tool.py

该文件是VSCode插件的主命令实现，负责：
1. 接收JSON格式输入，包含content字段、序列号字段和工程目录等附加信息
2. 执行命令并返回JSON格式输出，支持多种返回类型
3. 支持生成带有命令行代码时刻标记的输出
4. 支持多次输出和结束标志
5. 提供示例功能展示插件的交互能力
6. 支持与千问大模型的集成处理

使用方式：
python interactive-tool.py "{\"content\": \"command params\", \"projectDir\": \"/path/to/project\", \"sequenceId\": \"unique-id\", \"osType\": \"windows\"}"

返回格式：
JSON数组，每个元素包含：
- type: 返回类型（text, image, command, python, table等）
- content: 内容
- isError: 是否为错误信息
- isEnd: 是否为命令执行结束标记
- sequenceId: 与输入相同的序列号
"""

import sys
import json
import time
import argparse
import os
import requests
import re
from typing import Dict, Any, Optional, List, Union, Callable

class QianwenClient:
    """千问大模型客户端，处理与千问大模型的通信"""
    
    def __init__(self, api_base: str = "http://localhost:3000/api/qianwen"):
        """初始化千问大模型客户端"""
        self.api_base = api_base
    
    def send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """向千问大模型发送请求"""
        try:
            # 实际项目中需要替换为真实的千问API调用
            # 这里仅作示例，返回模拟的响应
            if data.get("content") == "test_qianwen":
                return {
                    "code": 0,
                    "message": "success",
                    "data": {
                        "response": "这是千问大模型的模拟响应",
                        "tool_calls": [
                            {
                                "name": "output_text",
                                "parameters": {
                                    "content": "这是通过工具回调输出的文本",
                                    "isError": False
                                }
                            }
                        ]
                    }
                }
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "response": f"已处理内容: {data.get('content')}"
                }
            }
        except Exception as e:
            return {
                "code": -1,
                "message": f"调用千问大模型失败: {str(e)}"
            }


class InteractiveTool:
    """交互式工具主类，处理命令执行和输出格式化"""
    
    # 定义命令行代码时刻标记
    CODE_BLOCK_MARKER = "[CODE_BLOCK_BEGIN]"
    CODE_BLOCK_END_MARKER = "[CODE_BLOCK_END]"
    
    def __init__(self):
        """初始化交互式工具"""
        # 千问大模型客户端
        self.qianwen_client = QianwenClient()
        # 用户输入处理器字典
        self.input_handlers = {}
        # 操作系统类型
        self.os_type = "windows"
    
    def execute(self) -> None:
        """执行命令并返回结果"""
        try:
            # 读取命令行参数中的JSON输入
            if len(sys.argv) > 1:
                input_json = sys.argv[1]
                try:
                    # 解析JSON输入
                    input_data = json.loads(input_json)
                    content = input_data.get('content', '')
                    project_dir = input_data.get('projectDir', os.getcwd())
                    sequence_id = input_data.get('sequenceId', '')
                    # 获取操作系统类型
                    self.os_type = input_data.get('osType', 'windows')
                    
                    # 处理命令
                    self._process_command(content, project_dir, sequence_id)
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，则将其视为原始命令
                    content = sys.argv[1]
                    project_dir = os.getcwd()
                    sequence_id = ''
                    self._process_command(content, project_dir, sequence_id)
            else:
                # 没有输入参数，显示帮助
                self._show_help('')
        except Exception as e:
            # 输出错误信息
            self._output_json({
                "type": "text",
                "content": f"执行错误: {str(e)}",
                "isError": True,
                "isEnd": False,
                "sequenceId": ""
            })
            self._output_json({
                "type": "end",
                "content": "",
                "isError": False,
                "isEnd": True,
                "sequenceId": ""
            })


    
    def _process_command(self, content: str, project_dir: str, sequence_id: str = '') -> None:
        """处理命令内容"""
        # 解析命令和参数
        parts = content.strip().split()
        if not parts:
            self._show_help()
            return
            
        command = parts[0].lower()
        params = parts[1:] if len(parts) > 1 else []
        
        # 记录执行开始
        self._output_json({
            "type": "text",
            "content": f"Executing command: {command} with params: {params} in directory: {project_dir}",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.5)  # 模拟执行时间
        
        # 根据命令类型执行不同的操作
        if command == 'help':
            self._show_help(sequence_id)
        elif command == 'run':
            self._run_sample_command(sequence_id)
        elif command == 'info':
            self._show_info(params, sequence_id)
        elif command == 'generate':
            self._generate_code(params, sequence_id)
        # 千问大模型相关命令
        elif command == 'qianwen':
            # 使用千问大模型处理内容
            model_content = ' '.join(params)
            self.process_with_qianwen_model(model_content, sequence_id)
        elif command == 'register_tool':
            # 注册自定义工具
            tool_info = ' '.join(params)
            self._register_custom_tool(tool_info, sequence_id)
        elif command == 'unregister_tool':
            # 注销自定义工具
            tool_name = params[0] if params else ''
            self._unregister_custom_tool(tool_name, sequence_id)
        else:
            self._output_json({
                "type": "text",
                "content": f"Unknown command: {command}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            self._show_help()
        
        # 输出结束标志
        self._output_json({
            "type": "end",
            "content": "",
            "isError": False,
            "isEnd": True,
            "sequenceId": sequence_id
        })

    def process_with_qianwen_model(self, content: str, sequence_id: str) -> Dict[str, Any]:
        """使用千问大模型处理内容"""
        try:
            # 注册扩展工具给大模型
            tools = self._register_extension_tools(sequence_id)
            
            # 发送内容给大模型处理
            response = self.qianwen_client.send_request({
                "content": content,
                "tools": tools,
                "sequenceId": sequence_id,
                "osType": self.os_type
            })
            
            # 处理大模型响应
            if response.get("code") == 0:
                data = response.get("data", {})
                # 处理工具调用
                if "tool_calls" in data:
                    for tool_call in data["tool_calls"]:
                        self._handle_tool_call(tool_call, sequence_id)
                
                # 输出大模型响应
                if "response" in data:
                    self._output_json({
                        "type": "text",
                        "content": data["response"],
                        "isError": False,
                        "isEnd": False,
                        "sequenceId": sequence_id
                    })
            else:
                self._output_json({
                    "type": "text",
                    "content": f"大模型处理失败: {response.get('message', '未知错误')}",
                    "isError": True,
                    "isEnd": False,
                    "sequenceId": sequence_id
                })
            
            return response
        except Exception as e:
            self._output_json({
                "type": "text",
                "content": f"大模型处理异常: {str(e)}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            return {"code": -1, "message": str(e)}

    def _register_extension_tools(self, sequence_id: str) -> List[Dict[str, Any]]:
        """注册扩展工具给千问大模型"""
        return [
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

    def _handle_tool_call(self, tool_call: Dict[str, Any], sequence_id: str) -> Any:
        """处理大模型的工具调用请求"""
        try:
            name = tool_call.get("name")
            parameters = tool_call.get("parameters", {})
            
            # 记录工具调用信息
            self._output_json({
                "type": "text",
                "content": f"接收到工具调用: {name}",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            
            # 根据工具名称执行相应操作
            if name == "output_text":
                return self._output_text(parameters.get("content", ""), 
                                       parameters.get("isError", False), 
                                       sequence_id)
            elif name == "output_table":
                return self._output_table(parameters.get("header", []),
                                        parameters.get("rows", []),
                                        parameters.get("metadata", {}),
                                        sequence_id)
            elif name == "output_progress":
                return self._output_progress(parameters.get("current", 0),
                                           parameters.get("total", 100),
                                           parameters.get("status", "处理中..."),
                                           sequence_id)
            elif name == "request_user_input":
                return self._request_user_input(parameters.get("prompt", "请输入："),
                                              sequence_id)
            elif name == "end_execution":
                return self._end_execution(sequence_id)
            else:
                self._output_json({
                    "type": "text",
                    "content": f"未知的工具调用: {name}",
                    "isError": True,
                    "isEnd": False,
                    "sequenceId": sequence_id
                })
                return None
        except Exception as e:
            self._output_json({
                "type": "text",
                "content": f"处理工具调用失败: {str(e)}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            return None
    
    def _output_text(self, content: str, is_error: bool = False, sequence_id: str = '') -> None:
        """输出文本信息"""
        self._output_json({
            "type": "text",
            "content": content,
            "isError": is_error,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def _output_table(self, header: List[str], rows: List[List[Any]], 
                     metadata: Dict[str, Any] = None, sequence_id: str = '') -> None:
        """输出表格数据"""
        if metadata is None:
            metadata = {}
        self._output_json({
            "type": "table",
            "content": {
                "header": header,
                "rows": rows,
                "metadata": metadata
            },
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def _output_progress(self, current: int, total: int = 100, 
                        status: str = "处理中...", sequence_id: str = '') -> None:
        """输出进度信息"""
        self._output_json({
            "type": "progress",
            "content": {
                "current": current,
                "total": total,
                "status": status
            },
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def _request_user_input(self, prompt: str, sequence_id: str = '') -> str:
        """请求用户输入"""
        # 输出请求输入的信息
        self._output_json({
            "type": "input_request",
            "content": {
                "prompt": prompt
            },
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        
        # 模拟用户输入（实际应用中应等待用户输入）
        # 这里返回一个示例输入
        return "用户示例输入"
    
    def _end_execution(self, sequence_id: str = '') -> None:
        """结束当前执行流程"""
        self._output_json({
            "type": "end",
            "content": "执行已结束",
            "isError": False,
            "isEnd": True,
            "sequenceId": sequence_id
        })
    
    def _register_custom_tool(self, tool_info: str, sequence_id: str = '') -> None:
        """注册自定义工具"""
        try:
            # 解析工具信息
            tool_data = json.loads(tool_info)
            # 记录工具注册信息
            self._output_json({
                "type": "text",
                "content": f"已注册自定义工具: {tool_data.get('name', 'unknown')}",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
        except Exception as e:
            self._output_json({
                "type": "text",
                "content": f"注册自定义工具失败: {str(e)}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
    
    def _unregister_custom_tool(self, tool_name: str, sequence_id: str = '') -> None:
        """注销自定义工具"""
        self._output_json({
            "type": "text",
            "content": f"已注销自定义工具: {tool_name}",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def _output_json(self, data: Dict[str, Any]) -> None:
        """输出JSON格式的数据"""
        print(json.dumps(data))
    
    def _show_help(self, sequence_id: str = '') -> None:
        """显示帮助信息"""
        self._output_json({
            "type": "text",
            "content": "=== Interactive Tool Help ===",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        self._output_json({
            "type": "text",
            "content": "Available commands:",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        self._output_json({
            "type": "text",
            "content": "  help          - Show this help message",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        self._output_json({
            "type": "text",
            "content": "  run           - Run a sample interactive command",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        self._output_json({
            "type": "text",
            "content": "  info [topic]  - Show information about a specific topic",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        self._output_json({
            "type": "text",
            "content": "  generate [type] - Generate sample code of specified type",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def _run_sample_command(self, sequence_id: str = '') -> None:
        """运行示例命令，展示交互式功能"""
        self._output_json({
            "type": "text",
            "content": "Running sample interactive command...",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.5)
        
        # 输出一些普通信息
        self._output_json({
            "type": "text",
            "content": "This is a sample output from the main command.",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.3)
        self._output_json({
            "type": "text",
            "content": "The following code demonstrates how to list files in a directory:",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.3)
        
        # 输出命令行代码块
        self._output_json({
            "type": "command",
            "content": "ls -la",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.5)
        
        # 输出表格示例
        self._output_json({
            "type": "table",
            "content": [
                ["Name", "Size", "Date"],
                ["file1.txt", "1024", "2023-01-01"],
                ["file2.txt", "2048", "2023-01-02"]
            ],
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        time.sleep(0.3)
        
        # 输出Python代码示例
        self._output_json({
            "type": "python",
            "content": "def hello():\n    print('Hello, world!')\n\nhello()",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        print("After executing the code above, you can analyze the results.")
        time.sleep(0.3)
        print("Here's another example of creating a new directory:")
        time.sleep(0.3)
        
        # 输出另一个命令行代码块
        self._output_code_block("mkdir -p project/src")
        time.sleep(0.5)
        
        print("Sample command execution completed.")
    
    def _show_info(self, params: list, sequence_id: str = '') -> None:
        """显示信息"""
        topic = params[0] if params else "general"
        
        if topic == "general":
            self._output_json({
                "type": "text",
                "content": "这是一个交互式工具，可以执行命令并返回结果。",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            self._output_json({
                "type": "text",
                "content": "支持的命令：help, run, info, generate, qianwen, register_tool, unregister_tool",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
        elif topic == "commands":
            self._output_json({
                "type": "text",
                "content": "可用命令列表：",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            self._output_json({
                "type": "table",
                "content": {
                    "header": ["命令", "描述"],
                    "rows": [
                        ["help", "显示帮助信息"],
                        ["run <example>", "运行命令示例"],
                        ["info <type>", "显示信息"],
                        ["generate <type>", "生成代码示例"],
                        ["qianwen <content>", "使用千问大模型处理内容"],
                        ["register_tool <json>", "注册自定义工具"],
                        ["unregister_tool <name>", "注销自定义工具"]
                    ]
                },
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
        elif topic == "features":
            self._output_json({
                "type": "text",
                "content": "功能特性：",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            self._output_json({
                "type": "list",
                "content": [
                    "JSON格式输入输出",
                    "支持多种返回类型",
                    "命令行代码标记",
                    "示例命令执行",
                    "千问大模型集成处理",
                    "扩展工具注册与调用"
                ],
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
        else:
            self._output_json({
                "type": "text",
                "content": f"未知的信息类型: {topic}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
    
    def _generate_code(self, params: list, sequence_id: str = '') -> None:
        """生成示例代码"""
        code_type = params[0] if params else "python"
        
        code_samples = {
            "python": "print('Hello, World!')\nfor i in range(5):\n    print(f'Count: {i}')",
            "bash": "echo 'Hello, World!'\nfor i in {1..5}; do\n    echo \"Count: $i\"\ndone",
            "javascript": "console.log('Hello, World!');\nfor (let i = 0; i < 5; i++) {\n    console.log(`Count: ${i}`);\n}"
        }
        
        print(f"Generated {code_type} code:")
        self._output_code_block(code_samples.get(code_type, f"# No sample code for {code_type}"))
    
    def _output_code_block(self, code: str) -> None:
        """输出命令行代码块"""
        # 输出命令行代码时刻标记和代码内容
        print(f"{self.CODE_BLOCK_MARKER}\n{code}\n{self.CODE_BLOCK_END_MARKER}")

if __name__ == "__main__":
    # 创建并执行交互式工具
    tool = InteractiveTool()
    tool.execute()