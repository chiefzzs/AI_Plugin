#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
Python RESTful API服务，用于连接浏览器中的webview和Python工具
"""
import os
import sys
import json
import logging
import argparse
import subprocess
import threading
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# 导入Mock LLM客户端
from core.mock_llm import MockQianwenClient

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('REST_API_Server')

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化Mock LLM客户端
mock_llm_client = MockQianwenClient()

# 当前目录（tools目录）
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# 活跃的进程字典
active_processes = {}
process_lock = threading.Lock()

# 执行工具的函数
def execute_tool(tool_name, command, sequence_id, callback=None):
    """执行指定的Python工具并返回结果"""
    try:
        # 构建工具文件路径
        tool_file_name = tool_name if tool_name.endswith('.py') else f'{tool_name}.py'
        tool_path = os.path.join(TOOLS_DIR, tool_file_name)
        
        # 检查工具文件是否存在
        if not os.path.exists(tool_path):
            error_msg = f"工具文件不存在: {tool_path}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # 构建命令参数
        input_data = {
            'content': command,
            'projectDir': os.getcwd(),
            'sequenceId': sequence_id
        }
        
        json_input = json.dumps(input_data)
        
        logger.info(f"执行工具: {tool_path}，命令: {command}")
        
        # 启动Python进程
        process = subprocess.Popen(
            [sys.executable, tool_path, json_input],
            cwd=TOOLS_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 存储活跃进程
        with process_lock:
            active_processes[sequence_id] = process
        
        # 读取标准输出
        stdout_output = []
        stderr_output = []
        
        # 读取标准输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                stdout_output.append(line)
                logger.debug(f"工具输出: {line}")
                
                # 如果有回调函数，实时返回结果
                if callback:
                    try:
                        # 尝试解析JSON响应
                        response_data = json.loads(line)
                        callback({
                            'type': response_data.get('type', 'output'),
                            'content': response_data.get('content', line),
                            'isError': response_data.get('isError', False),
                            'isEnd': False,
                            'sequenceId': sequence_id
                        })
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，作为普通文本输出
                        callback({
                            'type': 'output',
                            'content': line,
                            'isError': False,
                            'isEnd': False,
                            'sequenceId': sequence_id
                        })
        
        # 读取错误输出
        while True:
            error = process.stderr.readline()
            if error == '' and process.poll() is not None:
                break
            if error:
                line = error.strip()
                stderr_output.append(line)
                logger.error(f"工具错误: {line}")
                
                # 如果有回调函数，实时返回错误
                if callback:
                    callback({
                        'type': 'error',
                        'content': line,
                        'isError': True,
                        'isEnd': False,
                        'sequenceId': sequence_id
                    })
        
        # 获取退出码
        return_code = process.poll()
        
        # 从活跃进程中删除
        with process_lock:
            if sequence_id in active_processes:
                del active_processes[sequence_id]
        
        # 检查是否有错误
        if return_code != 0:
            error_msg = f"工具执行失败，退出码: {return_code}\n" + '\n'.join(stderr_output)
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'stdout': '\n'.join(stdout_output),
                'stderr': '\n'.join(stderr_output)
            }
        
        # 返回成功结果
        return {
            'success': True,
            'result': {
                'type': 'output',
                'content': '\n'.join(stdout_output),
                'isError': False,
                'isEnd': True,
                'sequenceId': sequence_id
            }
        }
        
    except Exception as e:
        logger.error(f"执行工具时发生异常: {str(e)}")
        # 清理进程
        with process_lock:
            if sequence_id in active_processes:
                try:
                    active_processes[sequence_id].kill()
                    del active_processes[sequence_id]
                except:
                    pass
        
        return {'success': False, 'error': str(e)}

# 测试连接的接口
@app.route('/api/test', methods=['GET'])
def test_connection():
    """测试API连接是否正常"""
    return jsonify({
        'success': True,
        'message': 'API服务运行正常',
        'version': '1.0',
        'tools_dir': TOOLS_DIR
    })

# 执行工具的接口
@app.route('/api/execute', methods=['POST'])
def execute_tool_api():
    """执行工具的API接口"""
    try:
        # 获取请求数据
        data = request.json
        tool_name = data.get('toolName')
        command = data.get('command', '')
        sequence_id = data.get('sequenceId', f'seq-{int(time.time())}')
        
        # 验证参数
        if not tool_name:
            return jsonify({'success': False, 'error': '工具名称不能为空'})
        
        # 执行工具
        result = execute_tool(tool_name, command, sequence_id)
        
        # 返回结果
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API执行异常: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 获取活跃进程数的接口
@app.route('/api/active-processes', methods=['GET'])
def get_active_processes():
    """获取当前活跃的进程数"""
    with process_lock:
        count = len(active_processes)
        processes = list(active_processes.keys())
    
    return jsonify({
        'success': True,
        'count': count,
        'processes': processes
    })

# 取消执行的接口
@app.route('/api/cancel', methods=['POST'])
def cancel_execution():
    """取消指定序列ID的执行"""
    try:
        data = request.json
        sequence_id = data.get('sequenceId')
        
        if not sequence_id:
            return jsonify({'success': False, 'error': '序列ID不能为空'})
        
        with process_lock:
            if sequence_id in active_processes:
                process = active_processes[sequence_id]
                try:
                    process.kill()
                    del active_processes[sequence_id]
                    logger.info(f"已取消执行: {sequence_id}")
                    return jsonify({'success': True, 'message': '执行已取消'})
                except Exception as e:
                    logger.error(f"取消执行失败: {str(e)}")
                    return jsonify({'success': False, 'error': str(e)})
            else:
                return jsonify({'success': False, 'error': '未找到指定的执行任务'})
        
    except Exception as e:
        logger.error(f"取消执行异常: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 列出可用工具的接口
@app.route('/api/tools', methods=['GET'])
def list_available_tools():
    """列出所有可用的Python工具"""
    try:
        tools = []
        # 遍历tools目录，查找Python文件
        for file in os.listdir(TOOLS_DIR):
            if file.endswith('.py') and file != '__init__.py' and file != 'rest_api_server.py':
                tool_path = os.path.join(TOOLS_DIR, file)
                # 尝试获取工具信息（简单方法）
                tools.append({
                    'name': file[:-3],  # 去掉.py后缀
                    'file': file,
                    'path': tool_path,
                    'size': os.path.getsize(tool_path)
                })
        
        return jsonify({
            'success': True,
            'tools': tools
        })
        
    except Exception as e:
        logger.error(f"列出工具异常: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# 聊天接口
@app.route('/api/chat', methods=['POST'])
def chat_api():
    """处理聊天消息的API接口"""
    try:
        # 获取请求数据
        data = request.json
        
        # 打印收到的前台数据
        logger.info(f"收到前台聊天数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 提取必要信息
        message = data.get('message', '') or data.get('content', '')
        conversation_id = data.get('conversationId', '')
        
        # 确保mock_llm能够正确识别内容字段
        processed_data = data.copy()
        if message and 'content' not in processed_data:
            processed_data['content'] = message
        
        # 调用Mock LLM客户端生成响应
        response_data = mock_llm_client.send_request(processed_data)
        
        # 构建返回结果
        result = {
            'success': True,
            'data': response_data,
            'message': '聊天请求处理成功'
        }
        
        # 打印返回的JSON
        logger.info(f"返回聊天响应: {json.dumps(result, ensure_ascii=False)}")
        
        # 返回结果
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"聊天API异常: {str(e)}"
        logger.error(error_msg)
        error_result = {
            'success': False,
            'error': error_msg
        }
        logger.info(f"返回错误响应: {json.dumps(error_result, ensure_ascii=False)}")
        return jsonify(error_result)

# 流式传输结果的接口
@app.route('/api/execute/stream', methods=['POST'])
def execute_tool_stream():
    """流式传输工具执行结果的接口"""
    try:
        # 获取请求数据
        data = request.json
        tool_name = data.get('toolName')
        command = data.get('command', '')
        sequence_id = data.get('sequenceId', f'seq-{int(time.time())}')
        
        # 验证参数
        if not tool_name:
            return Response(json.dumps({'success': False, 'error': '工具名称不能为空'}), mimetype='application/json')
        
        logger.info(f"开始流式执行工具: {tool_name}，命令: {command}")
        
        # 创建一个生成器函数用于流式传输
        def generate():
            # 创建一个事件用于停止流式传输
            stop_event = threading.Event()
            
            # 回调函数，用于实时发送结果
            def stream_callback(response):
                if not stop_event.is_set():
                    # 将响应转换为JSON字符串并发送
                    yield f"data: {json.dumps(response)}\n\n"
            
            try:
                # 在单独的线程中执行工具
                result = execute_tool(tool_name, command, sequence_id, stream_callback)
                
                # 发送结束消息
                if not stop_event.is_set():
                    end_response = {
                        'type': 'complete',
                        'content': '执行完成',
                        'isError': not result['success'],
                        'isEnd': True,
                        'sequenceId': sequence_id,
                        'error': result.get('error')
                    }
                    yield f"data: {json.dumps(end_response)}\n\n"
                    
            except Exception as e:
                logger.error(f"流式执行异常: {str(e)}")
                if not stop_event.is_set():
                    error_response = {
                        'type': 'error',
                        'content': str(e),
                        'isError': True,
                        'isEnd': True,
                        'sequenceId': sequence_id
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
            finally:
                stop_event.set()
        
        # 返回SSE响应
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        logger.error(f"流式API异常: {str(e)}")
        return Response(json.dumps({'success': False, 'error': str(e)}), mimetype='application/json')

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Python RESTful API服务')
    parser.add_argument('--host', type=str, default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口号')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 检查是否安装了必要的依赖
    try:
        import flask
        import flask_cors
    except ImportError:
        logger.error('未安装必要的依赖，请先安装: pip install flask flask-cors')
        sys.exit(1)
    
    logger.info(f"启动RESTful API服务，地址: http://{args.host}:{args.port}")
    logger.info(f"工具目录: {TOOLS_DIR}")
    logger.info("可用API端点:")
    logger.info("  GET    /api/test              - 测试API连接")
    logger.info("  POST   /api/execute           - 执行工具")
    logger.info("  POST   /api/execute/stream    - 流式执行工具")
    logger.info("  POST   /api/chat              - 处理聊天消息")
    logger.info("  GET    /api/active-processes  - 获取活跃进程数")
    logger.info("  POST   /api/cancel            - 取消执行")
    logger.info("  GET    /api/tools             - 列出可用工具")
    
    # 启动服务器
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)