#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
第二命令文件：execinfo.py

该文件是VSCode插件的第二命令实现，负责：
1. 接收JSON格式输入，包含content字段、序列号字段和工程目录等附加信息
2. 在后台执行命令行代码
3. 捕获命令执行的标准输出和错误输出
4. 格式化并返回JSON格式执行结果
5. 支持多种返回类型（text, error, command, python, table等）
6. 支持多次输出和结束标志

使用方式：
python execinfo.py "{\"content\": \"command_to_execute\", \"projectDir\": "/path/to/project", \"sequenceId\": \"unique-id\"}"

返回格式：
JSON数组，每个元素包含：
- type: 返回类型（text, error, command, python, table等）
- content: 内容
- isError: 是否为错误信息
- isEnd: 是否为命令执行结束标记
- sequenceId: 与输入相同的序列号
"""

import sys
import subprocess
import json
import time
import platform
import os
from typing import Dict, Any, Optional, Tuple, List

class ExecInfo:
    """执行信息工具类，负责在后台执行命令并返回结果"""
    
    def __init__(self):
        """初始化执行信息工具"""
        self.system = platform.system()
        # 定义命令行代码时刻标记和结束标记
        self.CODE_BLOCK_MARKER = "[CODE_BLOCK_BEGIN]"
        self.CODE_BLOCK_END_MARKER = "[CODE_BLOCK_END]"
        self.ERROR_MARKER = "[ERROR_MARKER]"
        self.END_MARKER = "[COMMAND_EXECUTION_END]"
        
    def execute(self) -> None:
        """执行指定的命令并输出结果"""
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
                    
                    # 记录执行开始
                    self._output_json({
                        "type": "text",
                        "content": f"Executing code in background: {content}",
                        "isError": False,
                        "isEnd": False,
                        "sequenceId": sequence_id
                    })
                    time.sleep(0.2)  # 模拟执行准备时间
                    
                    # 执行命令
                    self._execute_command(content, project_dir, sequence_id)
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，则将其视为原始命令
                    content = sys.argv[1]
                    project_dir = os.getcwd()
                    sequence_id = ''
                    
                    self._output_json({
                        "type": "text",
                        "content": f"Executing code in background: {content}",
                        "isError": False,
                        "isEnd": False,
                        "sequenceId": sequence_id
                    })
                    time.sleep(0.2)
                    
                    self._execute_command(content, project_dir, sequence_id)
            else:
                # 没有输入参数，显示帮助
                self._show_help('')
        except Exception as e:
            # 输出执行错误
            self._output_json({
                "type": "error",
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
    
    def _execute_command(self, command: str, project_dir: str) -> None:
        """执行命令并处理输出"""
        # 根据操作系统选择合适的shell
        shell = True
        if self.system == "Windows":
            # 在Windows上使用cmd.exe
            shell_cmd = ["cmd.exe", "/c"]
        else:
            # 在Unix/Linux/Mac上使用bash
            shell_cmd = ["bash", "-c"]
        
        try:
            # 保存当前目录并切换到指定目录
            original_dir = os.getcwd()
            if project_dir and os.path.exists(project_dir):
                os.chdir(project_dir)
            
            # 执行命令并捕获输出
            if self._is_complex_command(command):
                # 复杂命令使用shell执行
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # 简单命令直接拆分参数执行
                cmd_parts = self._split_command(command)
                process = subprocess.Popen(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # 实时捕获和输出标准输出
            self._capture_and_output_stream(process.stdout, is_error=False)
            
            # 捕获和输出错误输出
            self._capture_and_output_stream(process.stderr, is_error=True)
            
            # 等待进程完成并获取返回码
            return_code = process.wait()
            
            # 输出返回码信息
            self._output_json({
                "type": "text",
                "content": f"Command executed with return code: {return_code}",
                "isError": False,
                "isEnd": False
            })
            
            # 对于一些特殊命令，可以生成额外的代码块供用户交互
            self._generate_additional_code_blocks(command)
            
        except Exception as e:
            # 输出执行错误
            self._output_json({
                "type": "error",
                "content": f"Command execution error: {str(e)}",
                "isError": True,
                "isEnd": False
            })
        finally:
            # 切换回原始目录
            os.chdir(original_dir)
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
            "content": "=== ExecInfo Tool Help ===",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "Usage:",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "text",
            "content": "  python execinfo.py \"{\\\"content\\\": \\"command_to_execute\\\", \\"projectDir\\\": \\/path\\/to\\/project\\"}\"",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "end",
            "content": "",
            "isError": False,
            "isEnd": True
        })
        print(f"{self.ERROR_MARKER}\nError executing command: {str(e)}")
        
        # 输出结束标志
        print(self.END_MARKER)
    
    def _is_complex_command(self, command: str) -> bool:
        """判断是否为复杂命令（包含管道、重定向等）"""
        complex_chars = ["|", "<", ">", "&&", "||"]
        return any(char in command for char in complex_chars)
    
    def _split_command(self, command: str) -> List[str]:
        """简单拆分命令字符串为参数列表"""
        # 这是一个简单的实现，实际应用中可能需要更复杂的解析
        # 考虑引号、转义字符等情况
        import shlex
        try:
            return shlex.split(command)
        except ValueError:
            # 如果解析失败，返回整个命令作为单个参数
            return [command]
    
    def _capture_and_output_stream(self, stream, is_error: bool = False) -> None:
        """捕获并输出流内容"""
        if not stream:
            return
        
        while True:
            line = stream.readline()
            if not line:
                break
            
            # 移除行尾换行符
            line = line.rstrip('\r\n')
            
            # 根据是否为错误流添加相应标记
            if is_error:
                print(f"{self.ERROR_MARKER}\n{line}")
            else:
                print(line)
            
            # 添加小延迟，模拟实时输出效果
            time.sleep(0.1)
    
    def _generate_additional_code_blocks(self, original_command: str) -> None:
        """根据原始命令生成额外的代码块供用户交互"""
        # 示例：如果原始命令是列出文件，可以生成进一步操作的代码块
        if any(cmd in original_command.lower() for cmd in ["ls", "dir"]):
            time.sleep(0.5)
            print("\nWould you like to see more details about a file?")
            self._output_code_block("stat $(ls -la | head -n 3 | tail -n 1 | awk '{print $9}')")
        
        # 示例：如果是git命令，可以生成相关操作的代码块
        elif any(cmd in original_command.lower() for cmd in ["git", "git status"]):
            time.sleep(0.5)
            print("\nWould you like to view recent commits?")
            self._output_code_block("git log --oneline -n 5")
        
        # 示例：如果是python命令，可以生成相关操作的代码块
        elif "python" in original_command.lower():
            time.sleep(0.5)
            print("\nWould you like to run a more advanced Python command?")
            self._output_code_block("python -c \"import sys, os; print('Python version:', sys.version); print('Current directory:', os.getcwd())\"")
    
    def _output_code_block(self, code: str) -> None:
        """输出命令行代码块"""
        # 输出命令行代码时刻标记和代码内容
        print(f"{self.CODE_BLOCK_MARKER}\n{code}\n{self.CODE_BLOCK_END_MARKER}")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        print(f"{ExecInfo.ERROR_MARKER}\nError: No command provided")
        print("Usage: python execinfo.py \"command_to_execute\"")
        print(ExecInfo.END_MARKER)
        sys.exit(1)
    
    # 获取要执行的命令
    command = sys.argv[1]
    
    # 创建并执行执行信息工具
    exec_tool = ExecInfo()
    exec_tool.execute(command)