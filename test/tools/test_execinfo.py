# -*- coding: utf-8 -*-

import pytest
import json
import subprocess
import sys
import os
import platform
from typing import List, Dict, Any

# 获取当前脚本所在目录
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建execinfo.py的路径
TOOL_PATH = os.path.join(TEST_DIR, '..', '..', 'tools', 'execinfo.py')
TOOL_PATH = os.path.normpath(TOOL_PATH)

class TestExecInfo:
    
    def test_json_input_parsing(self):
        """测试执行信息工具能够正确解析JSON格式输入"""
        # 根据操作系统选择合适的命令
        if platform.system() == 'Windows':
            test_command = 'echo Hello, World!'
        else:
            test_command = 'echo "Hello, World!"'
            
        # 准备测试数据
        test_input = {
            'content': test_command,
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
        
        # 验证输出包含命令执行信息
        output_lines = result.stdout.strip().split('\n')
        assert len(output_lines) > 0
        
        # 解析输出的JSON行
        has_command_execution = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and 'executing code' in output_data.get('content').lower():
                    has_command_execution = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_command_execution, "输出中未包含命令执行信息"
    
    def test_json_output_format(self):
        """测试执行信息工具能够生成符合要求的JSON格式输出"""
        # 根据操作系统选择合适的命令
        if platform.system() == 'Windows':
            test_command = 'echo Hello, World!'
        else:
            test_command = 'echo "Hello, World!"'
            
        # 准备测试数据
        test_input = {
            'content': test_command,
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
    
    def test_command_execution(self):
        """测试命令执行功能"""
        # 根据操作系统选择合适的命令
        if platform.system() == 'Windows':
            test_command = 'echo Hello, World!'
            expected_output = 'Hello, World!'
        else:
            test_command = 'echo "Hello, World!"'
            expected_output = 'Hello, World!'
            
        # 准备测试数据
        test_input = {
            'content': test_command,
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
        has_expected_output = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and expected_output in output_data.get('content'):
                    has_expected_output = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_expected_output, f"未找到预期输出: {expected_output}"
    
    def test_error_handling(self):
        """测试错误处理功能"""
        # 使用一个肯定会失败的命令
        if platform.system() == 'Windows':
            test_command = 'nonexistent_command'
        else:
            test_command = 'nonexistent_command'
            
        # 准备测试数据
        test_input = {
            'content': test_command,
            'projectDir': os.getcwd()
        }
        input_json = json.dumps(test_input)
        
        # 执行命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, input_json],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功（即使命令失败，工具也应该正常退出）
        assert result.returncode == 0
        
        # 检查输出内容
        output_lines = result.stdout.strip().split('\n')
        
        # 解析输出的JSON行
        has_error_output = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'error' and output_data.get('isError') is True:
                    has_error_output = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_error_output, "未找到错误输出"
    
    def test_project_directory(self):
        """测试项目目录参数的处理"""
        # 创建一个临时目录，并在其中创建一个测试文件
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # 根据操作系统选择合适的命令来列出目录内容
            if platform.system() == 'Windows':
                # 在Windows上创建一个测试文件
                test_file = os.path.join(temp_dir, 'test_file.txt')
                with open(test_file, 'w') as f:
                    f.write('test content')
                list_command = 'dir /b "' + temp_dir + '"'
            else:
                # 在Unix系统上创建一个测试文件
                test_file = os.path.join(temp_dir, 'test_file.txt')
                with open(test_file, 'w') as f:
                    f.write('test content')
                list_command = 'ls "' + temp_dir + '"'
                
            # 准备测试数据
            test_input = {
                'content': list_command,
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
            
            # 检查输出内容
            output_lines = result.stdout.strip().split('\n')
            
            # 解析输出的JSON行，检查是否包含测试文件名
            has_test_file = False
            for line in output_lines:
                try:
                    output_data = json.loads(line)
                    if output_data.get('type') == 'text' and 'test_file.txt' in output_data.get('content'):
                        has_test_file = True
                        break
                except json.JSONDecodeError:
                    continue
            
            assert has_test_file, "未在输出中找到测试文件"
    
    def test_raw_command_input(self):
        """测试直接传入原始命令（非JSON格式）的处理"""
        # 根据操作系统选择合适的命令
        if platform.system() == 'Windows':
            test_command = 'echo Hello, Raw Command!'
            expected_output = 'Hello, Raw Command!'
        else:
            test_command = 'echo "Hello, Raw Command!"'
            expected_output = 'Hello, Raw Command!'
            
        # 直接传入原始命令
        result = subprocess.run(
            [sys.executable, TOOL_PATH, test_command],
            capture_output=True,
            text=True
        )
        
        # 验证执行成功
        assert result.returncode == 0
        
        # 检查输出内容
        output_lines = result.stdout.strip().split('\n')
        
        # 解析输出的JSON行
        has_expected_output = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and expected_output in output_data.get('content'):
                    has_expected_output = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_expected_output, f"未找到预期输出: {expected_output}"
    
    def test_return_code(self):
        """测试命令返回码的处理"""
        # 使用一个肯定会成功的命令
        if platform.system() == 'Windows':
            success_command = 'echo Success'
        else:
            success_command = 'echo "Success"'
            
        # 准备测试数据
        test_input = {
            'content': success_command,
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
        
        # 解析输出的JSON行，检查是否包含返回码信息
        has_return_code = False
        for line in output_lines:
            try:
                output_data = json.loads(line)
                if output_data.get('type') == 'text' and 'return code: 0' in output_data.get('content').lower():
                    has_return_code = True
                    break
            except json.JSONDecodeError:
                continue
        
        assert has_return_code, "未在输出中找到返回码信息"

if __name__ == '__main__':
    pytest.main(['-v', __file__])