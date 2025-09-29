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

使用方式：
python interactive-tool.py "{\"content\": \"command params\", \"projectDir\": \"/path/to/project\", \"sequenceId\": \"unique-id\"}"

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
from typing import Dict, Any, Optional, List

class InteractiveTool:
    """交互式工具主类，处理命令执行和输出格式化"""
    
    # 定义命令行代码时刻标记
    CODE_BLOCK_MARKER = "[CODE_BLOCK_BEGIN]"
    CODE_BLOCK_END_MARKER = "[CODE_BLOCK_END]"
    
    def __init__(self):
        """初始化交互式工具"""
        pass
    
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
    
    def _process_command(self, content: str, project_dir: str) -> None:
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
            "isEnd": False
        })
        time.sleep(0.5)  # 模拟执行时间
        
        # 根据命令类型执行不同的操作
        if command == 'help':
            self._show_help()
        elif command == 'run':
            self._run_sample_command()
        elif command == 'info':
            self._show_info(params)
        elif command == 'generate':
            self._generate_code(params)
        else:
            self._output_json({
                "type": "text",
                "content": f"Unknown command: {command}",
                "isError": True,
                "isEnd": False
            })
            self._show_help()
        
        # 输出结束标志
        self._output_json({
            "type": "end",
            "content": "",
            "isError": False,
            "isEnd": True
        })
    
    def _output_json(self, data: Dict[str, Any]) -> None:
        """输出JSON格式的数据"""
        print(json.dumps(data))
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        self._output_json({
            "type": "text",
            "content": "=== Interactive Tool Help ===",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "Available commands:",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "  help          - Show this help message",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "  run           - Run a sample interactive command",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "  info [topic]  - Show information about a specific topic",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "  generate [type] - Generate sample code of specified type",
            "isError": False,
            "isEnd": False
        })
    
    def _run_sample_command(self) -> None:
        """运行示例命令，展示交互式功能"""
        self._output_json({
            "type": "text",
            "content": "Running sample interactive command...",
            "isError": False,
            "isEnd": False
        })
        time.sleep(0.5)
        
        # 输出一些普通信息
        self._output_json({
            "type": "text",
            "content": "This is a sample output from the main command.",
            "isError": False,
            "isEnd": False
        })
        time.sleep(0.3)
        self._output_json({
            "type": "text",
            "content": "The following code demonstrates how to list files in a directory:",
            "isError": False,
            "isEnd": False
        })
        time.sleep(0.3)
        
        # 输出命令行代码块
        self._output_json({
            "type": "command",
            "content": "ls -la",
            "isError": False,
            "isEnd": False
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
            "isEnd": False
        })
        time.sleep(0.3)
        
        # 输出Python代码示例
        self._output_json({
            "type": "python",
            "content": "def hello():\n    print('Hello, world!')\n\nhello()",
            "isError": False,
            "isEnd": False
        })
        print("After executing the code above, you can analyze the results.")
        time.sleep(0.3)
        print("Here's another example of creating a new directory:")
        time.sleep(0.3)
        
        # 输出另一个命令行代码块
        self._output_code_block("mkdir -p project/src")
        time.sleep(0.5)
        
        print("Sample command execution completed.")
    
    def _show_info(self, params: list) -> None:
        """显示信息"""
        topic = params[0] if params else "general"
        
        info_topics = {
            "general": "This is a VSCode interactive tool plugin that allows executing commands and showing results in a webview.",
            "commands": "The plugin supports main commands (background execution) and secondary commands (for code blocks).",
            "features": "Features include: command execution, code block interaction, multiple output support, and logging."
        }
        
        print(f"Information about '{topic}':")
        print(info_topics.get(topic, f"No information available for topic: {topic}"))
        
        # 如果是commands主题，展示一个代码示例
        if topic == "commands":
            time.sleep(0.5)
            print("\nTry executing this sample command:")
            self._output_code_block("python -c \"print('Hello from VSCode plugin!')\"")
    
    def _generate_code(self, params: list) -> None:
        """生成示例代码"""
        code_type = params[0] if params else "python"
        
        code_samples = {
            "python": "print('Hello, World!')\nfor i in range(5):\n    print(f'Count: {i}')",
            "bash": "echo 'Hello, World!'\nfor i in {1..5}; do\n    echo "Count: $i"\ndone",
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