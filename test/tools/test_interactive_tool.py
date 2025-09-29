# -*- coding: utf-8 -*-

import pytest
import json
import subprocess
import sys
import os
from typing import List, Dict, Any

# 获取当前脚本所在目录
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建interactive-tool.py的路径
TOOL_PATH = os.path.join(TEST_DIR, '..', '..', 'tools', 'interactive-tool.py')
TOOL_PATH = os.path.normpath(TOOL_PATH)

class TestInteractiveTool:
    
    def test_json_input_parsing(self):
        """测试交互式工具能够正确解析JSON格式输入"""
        # 准备测试数据
        test_input = {
            'content': 'help',
            'projectDir': os.getcwd()
        }
        input_json = json.dumps(test_input)
        
        # 执行命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, input_json],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功
        assert result.returncode == 0
        
        # 验证输出包含帮助信息
        output_lines = result.stdout.strip().split('\n')
        assert len(output_lines) > 0
        
        # 解析输出的JSON行
        has_help_content = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and 'help' in output_data.get('content').lower():
                    has_help_content = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_help_content, "输出中未包含帮助信息"
    
    def test_json_output_format(self):
        """测试交互式工具能够生成符合要求的JSON格式输出"""
        # 准备测试数据
        test_input = {
            'content': 'help',
            'projectDir': os.getcwd()
        }
        input_json = json.dumps(test_input)
        
        # 执行命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, input_json],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功
        assert result.returncode == 0
        
        # 验证输出的每一行都是有效的JSON
        output_lines = result.stdout.strip().split('\n')
        assert len(output_lines) > 0
        
        # 检查是否有结束标识
        has_end_marker = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                # 验证每个JSON对象都包含必要的字段
                assert 'type' in output_data
                assert 'content' in output_data
                assert 'isError' in output_data
                assert 'isEnd' in output_data
                
                # 检查结束标识
                if output_data.get('isEnd') is True:
                    has_end_marker = True
            except json.JSONDecodeError:
                pytest.fail(f"输出行 '{line}' 不是有效的JSON")
        
        assert has_end_marker, "输出中未包含结束标识"
    
    def test_run_command(self):
        """测试run命令的执行和输出"""
        # 准备测试数据
        test_input = {
            'content': 'run',
            'projectDir': os.getcwd()
        }
        input_json = json.dumps(test_input)
        
        # 执行命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, input_json],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功
        assert result.returncode == 0
        
        # 检查输出内容
        output_lines = result.stdout.strip().split('\n')
        
        # 解析输出的JSON行
        has_sample_output = False
        has_command_output = False
        has_table_output = False
        has_python_output = False
        
        for line in output_lines:
            try:
                output_data = json.loads(line)
                
                # 检查是否有示例输出
                if output_data.get('type') == 'text' and 'sample output' in output_data.get('content').lower():
                    has_sample_output = True
                
                # 检查是否有命令代码块输出
                if output_data.get('type') == 'command' and output_data.get('content') == 'ls -la':
                    has_command_output = True
                
                # 检查是否有表格输出
                if output_data.get('type') == 'table' and isinstance(output_data.get('content'), list):
                    has_table_output = True
                
                # 检查是否有Python代码输出
                if output_data.get('type') == 'python' and 'hello' in output_data.get('content').lower():
                    has_python_output = True
            except json.JSONDecodeError:
                continue
        
        # 验证所有类型的输出都存在
        assert has_sample_output, "未找到示例文本输出"
        assert has_command_output, "未找到命令代码块输出"
        assert has_table_output, "未找到表格输出"
        assert has_python_output, "未找到Python代码输出"
    
    def test_unknown_command(self):
        """测试未知命令的处理"""
        # 准备测试数据
        test_input = {
            'content': 'unknown_command',
            'projectDir': os.getcwd()
        }
        input_json = json.dumps(test_input)
        
        # 执行命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, input_json],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功（即使命令未知，也应该正常退出）
        assert result.returncode == 0
        
        # 检查输出内容
        output_lines = result.stdout.strip().split('\n')
        
        # 解析输出的JSON行
        has_unknown_command = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and output_data.get('isError') is True and 'unknown command' in output_data.get('content').lower():
                    has_unknown_command = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_unknown_command, "未找到未知命令的错误提示"
    
    def test_project_directory(self):
        """测试项目目录参数的处理"""
        # 使用临时目录作为测试项目目录
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # 准备测试数据
            test_input = {
                'content': 'help',
                'projectDir': temp_dir
            }
            input_json = json.dumps(test_input)
            
            # 执行命令
            result = subprocess.run(
                [sys.executable, TOOL_PATH, input_json],
                capture_output=True,
                text=True
            )
            
            # 验证执行成功
            assert result.returncode == 0
            
            # 检查输出中是否包含目录信息
            output_lines = result.stdout.strip().split('\n')
            
            has_directory_info = False
            for line in output_lines:
                try:
                    output_data = json.loads(line)
                    if output_data.get('type') == 'text' and temp_dir.lower() in output_data.get('content').lower():
                        has_directory_info = True
                        break
                except json.JSONDecodeError:
                    continue
            
            assert has_directory_info, "输出中未包含项目目录信息"
    
    def test_raw_command_input(self):
        """测试直接传入原始命令（非JSON格式）的处理"""
        # 直接传入原始命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, 'help'],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功
        assert result.returncode == 0
        
        # 验证输出包含帮助信息
        output_lines = result.stdout.strip().split('\n')
        assert len(output_lines) > 0
        
        # 解析输出的JSON行
        has_help_content = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and 'help' in output_data.get('content').lower():
                    has_help_content = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_help_content, "输出中未包含帮助信息"

if __name__ == '__main__':
    pytest.main(['-v', __file__])