#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接通信服务器 - 用于webview和Python脚本之间的直接通信
绕过VSCode插件，实现浏览器直接调用Python工具
"""

import os
import sys
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import urllib.parse
import subprocess
import threading
import time
from datetime import datetime

# 确保中文正常显示
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DirectCommHandler(BaseHTTPRequestHandler):
    """处理直接通信请求的处理器"""
    
    def do_OPTIONS(self):
        """处理跨域预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/test':
            # 测试连接
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'success',
                'message': '直接通信服务器已启动',
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 其他GET请求返回404
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {'status': 'error', 'message': '未找到请求的资源'}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # 解析JSON数据
            request_data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'error', 'message': '无效的JSON数据'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        if parsed_path.path == '/execute':
            # 执行命令
            self._handle_execute(request_data)
            return
        
        if parsed_path.path == '/process-amount':
            # 处理金额数据
            self._handle_process_amount(request_data)
            return
        
        # 其他POST请求返回404
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {'status': 'error', 'message': '未找到请求的API'}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _handle_execute(self, request_data):
        """处理执行命令的请求"""
        try:
            # 获取命令信息
            tool_name = request_data.get('toolName')
            command = request_data.get('command')
            sequence_id = request_data.get('sequenceId', 'unknown')
            
            if not command:
                raise ValueError('命令不能为空')
            
            print(f"[执行命令] tool: {tool_name}, cmd: {command}, seq: {sequence_id}")
            
            # 执行命令
            result = self._execute_command(command)
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'result': {
                    'type': 'text',
                    'content': result
                }
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _handle_process_amount(self, request_data):
        """处理金额数据的请求"""
        try:
            # 获取金额数据
            amount_data = request_data.get('amountData')
            
            if not amount_data:
                raise ValueError('金额数据不能为空')
            
            print(f"[处理金额数据] {json.dumps(amount_data, ensure_ascii=False)}")
            
            # 调用cmd-third.py处理金额数据
            cmd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmd-third.py')
            # 使用格式化字符串并避免嵌套引号问题
            escaped_json = json.dumps(amount_data, ensure_ascii=False).replace('"', '\\"')
            command = f'python "{cmd_path}" "{escaped_json}"'
            
            result = self._execute_command(command)
            
            # 解析结果
            try:
                result_json = json.loads(result)
            except json.JSONDecodeError:
                result_json = {'type': 'text', 'content': result}
            
            # 返回结果
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'result': result_json
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _execute_command(self, command):
        """执行系统命令并返回结果"""
        try:
            # 执行命令
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 获取输出
            stdout, stderr = process.communicate(timeout=60)  # 60秒超时
            
            # 检查返回码
            if process.returncode != 0:
                raise Exception(f"命令执行失败: {stderr or stdout}")
            
            return stdout or "命令执行成功，但无输出"
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("命令执行超时")
        except Exception as e:
            raise Exception(f"命令执行出错: {str(e)}")
    
    def log_message(self, format, *args):
        """重写日志方法，添加时间戳"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{current_time}] {self.client_address[0]} - {format % args}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """支持多线程的HTTP服务器"""
    daemon_threads = True

def run_server(host='localhost', port=5001, debug=False):
    """启动直接通信服务器"""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, DirectCommHandler)
    
    print(f"\n直接通信服务器启动成功!")
    print(f"服务器地址: http://{host}:{port}")
    print(f"API端点:")
    print(f"  - GET  /test              - 测试服务器连接")
    print(f"  - POST /execute           - 执行命令")
    print(f"  - POST /process-amount    - 处理金额数据")
    print(f"\n按Ctrl+C停止服务器...\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器正在关闭...")
        httpd.server_close()
        print("服务器已关闭")

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='直接通信服务器 - 用于webview和Python脚本之间的直接通信')
    parser.add_argument('--host', type=str, default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5001, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 启动服务器
    run_server(host=args.host, port=args.port, debug=args.debug)