#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
第三命令文件：cmd-third.py

该文件是VSCode插件的第三命令实现，负责：
1. 接收JSON格式输入，包含金额数据等信息
2. 处理金额数据并执行相关命令
3. 捕获命令执行的标准输出和错误输出
4. 格式化并返回JSON格式执行结果（以接口4格式）
5. 支持多种返回类型（text, error, command, python, table等）
6. 支持多次输出和结束标志

使用方式：
python cmd-third.py "{\"amount\": \"100.00\", \"currency\": \"CNY\", \"projectDir\": \/path\/to\/project, \"sequenceId\": \"unique-id\"}"

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

class CmdThird:
    """第三命令工具类，负责处理金额数据并执行命令"""
    
    def __init__(self):
        """初始化第三命令工具"""
        self.system = platform.system()
        # 定义命令行代码时刻标记和结束标记
        self.CODE_BLOCK_MARKER = "[CODE_BLOCK_BEGIN]"
        self.CODE_BLOCK_END_MARKER = "[CODE_BLOCK_END]"
        self.ERROR_MARKER = "[ERROR_MARKER]"
        self.END_MARKER = "[COMMAND_EXECUTION_END]"

    def execute(self) -> None:
        """执行处理金额数据的逻辑并输出结果"""
        try:
            # 读取命令行参数中的JSON输入
            if len(sys.argv) > 1:
                input_arg = sys.argv[1]
                
                # 尝试直接解析参数作为JSON
                try:
                    input_data = json.loads(input_arg)
                    amount = input_data.get('amount', '')
                    currency = input_data.get('currency', 'CNY')
                    project_dir = input_data.get('projectDir', os.getcwd())
                    sequence_id = input_data.get('sequenceId', '')
                except json.JSONDecodeError:
                    # 尝试处理转义问题
                    try:
                        # 处理常见的转义问题，比如额外的反斜杠
                        if '\\' in input_arg:
                            # 尝试去除一层转义
                            input_arg_fixed = input_arg.replace('\\', '')
                            input_data = json.loads(input_arg_fixed)
                            amount = input_data.get('amount', '')
                            currency = input_data.get('currency', 'CNY')
                            project_dir = input_data.get('projectDir', os.getcwd())
                            sequence_id = input_data.get('sequenceId', '')
                        else:
                            # 如果不是JSON格式，将整个参数视为原始数据
                            amount = input_arg
                            currency = 'CNY'
                            project_dir = os.getcwd()
                            sequence_id = ''
                    except json.JSONDecodeError:
                        # 如果仍然不是有效的JSON，则将其视为原始数据
                        amount = input_arg
                        currency = 'CNY'
                        project_dir = os.getcwd()
                        sequence_id = ''
                
                # 记录执行开始
                self._output_json({
                    "type": "text",
                    "content": f"处理金额数据: {amount} {currency}",
                    "isError": False,
                    "isEnd": False,
                    "sequenceId": sequence_id
                })
                time.sleep(0.2)  # 模拟执行准备时间
                
                # 执行命令处理金额数据
                self._process_amount_data(amount, currency, project_dir, sequence_id)
            else:
                # 没有输入参数，显示帮助
                self._show_help()
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

    def _process_amount_data(self, amount: str, currency: str, project_dir: str, sequence_id: str = '') -> None:
        """处理金额数据并执行相关命令"""
        try:
            # 构造处理金额的命令
            # 这里根据不同操作系统选择合适的命令
            if self.system == "Windows":
                # Windows系统下的命令示例
                if currency == 'CNY':
                    # 显示人民币金额格式化信息
                    command = f"echo 处理人民币金额: {amount} 元"
                else:
                    # 显示其他货币格式化信息
                    command = f"echo 处理{currency}金额: {amount}"
            else:
                # Unix/Linux/Mac系统下的命令示例
                if currency == 'CNY':
                    # 显示人民币金额格式化信息
                    command = f"echo '处理人民币金额: {amount} 元'"
                else:
                    # 显示其他货币格式化信息
                    command = f"echo '处理{currency}金额: {amount}'"
            
            # 保存当前目录并切换到指定目录
            original_dir = os.getcwd()
            if project_dir and os.path.exists(project_dir):
                os.chdir(project_dir)
            
            # 执行命令并捕获输出
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时捕获和输出标准输出
            self._capture_and_output_stream(process.stdout, is_error=False, sequence_id=sequence_id)
            
            # 捕获和输出错误输出
            self._capture_and_output_stream(process.stderr, is_error=True, sequence_id=sequence_id)
            
            # 等待进程完成并获取返回码
            return_code = process.wait()
            
            # 输出返回码信息
            self._output_json({
                "type": "text",
                "content": f"命令执行完成，返回码: {return_code}",
                "isError": False,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            
            # 生成额外的处理信息
            self._generate_additional_info(amount, currency, sequence_id)
            
        except Exception as e:
            # 输出执行错误
            self._output_json({
                "type": "error",
                "content": f"命令执行错误: {str(e)}",
                "isError": True,
                "isEnd": False,
                "sequenceId": sequence_id
            })
        finally:
            # 切换回原始目录
            os.chdir(original_dir)
            # 输出结束标志
            self._output_json({
                "type": "end",
                "content": "",
                "isError": False,
                "isEnd": True,
                "sequenceId": sequence_id
            })

    def _output_json(self, data: Dict[str, Any]) -> None:
        """输出JSON格式的数据"""
        print(json.dumps(data))
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        self._output_json({
            "type": "text",
            "content": "=== CmdThird Tool Help ===",
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
            "content": "  python cmd-third.py \"{\\\"amount\\\": \\"100.00\\\", \\"currency\\\": \\"CNY\\\"}\"",
            "isError": False,
            "isEnd": False
        })
        self._output_json({
            "type": "end",
            "content": "",
            "isError": False,
            "isEnd": True
        })

    def _capture_and_output_stream(self, stream, is_error: bool = False, sequence_id: str = '') -> None:
        """捕获并输出流内容"""
        if not stream:
            return
        
        while True:
            line = stream.readline()
            if not line:
                break
            
            # 移除行尾换行符
            line = line.rstrip('\r\n')
            
            # 使用JSON格式输出内容
            output_type = "error" if is_error else "text"
            self._output_json({
                "type": output_type,
                "content": line,
                "isError": is_error,
                "isEnd": False,
                "sequenceId": sequence_id
            })
            
            # 添加小延迟，模拟实时输出效果
            time.sleep(0.1)

    def _generate_additional_info(self, amount: str, currency: str, sequence_id: str = '') -> None:
        """生成额外的处理信息"""
        # 输出金额处理的详细信息
        self._output_json({
            "type": "text",
            "content": "金额数据处理完成",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        
        # 输出命令行代码块供用户进一步交互
        time.sleep(0.5)
        self._output_json({
            "type": "text",
            "content": "是否需要进行更多金额处理操作？",
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
        
        # 生成额外的命令行代码块
        self._output_code_block(f"echo '继续处理金额: {amount} {currency}'", sequence_id)

    def _output_code_block(self, code: str, sequence_id: str = '') -> None:
        """输出命令行代码块"""
        # 输出命令行代码时刻标记和代码内容
        self._output_json({
            "type": "command",
            "content": code,
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        # 创建实例以访问类变量
        cmd_tool = CmdThird()
        print(f"{cmd_tool.ERROR_MARKER}\nError: No amount data provided")
        print("Usage: python cmd-third.py \"amount_data_in_json_format\"")
        print(cmd_tool.END_MARKER)
        sys.exit(1)
    
    # 获取要处理的金额数据
    amount_data = sys.argv[1]
    
    # 创建并执行第三命令工具
    cmd_tool = CmdThird()
    cmd_tool.execute()