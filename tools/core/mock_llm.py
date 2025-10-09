# -*- coding: utf-8 -*-

"""
千问大模型模拟模块
用于在测试环境中模拟千问大模型的行为，支持多种返回类型和场景
"""

from typing import Dict, Any, List
import time

class MockQianwenClient:
    """模拟千问大模型客户端"""
    
    def __init__(self):
        """初始化模拟客户端"""
        self.call_count = 0
        self.reset_state()
    
    def reset_state(self):
        """重置客户端状态"""
        self.call_count = 0
    
    def send_request(self, data: Dict[str, Any], sequence_id: str = None) -> Dict[str, Any]:
        """模拟向千问大模型发送请求，根据不同输入返回不同类型的响应"""
        self.call_count += 1
        
        # 检查是否有tools字段
        if isinstance(data, dict) and 'tools' in data and data['tools']:
            # 处理带有工具调用的请求
            return {
                "content": "",
                "tool_calls": [
                    {
                        "name": "output_text",
                        "parameters": {
                            "content": "这是通过工具调用生成的响应",
                            "isError": False
                        }
                    }
                ]
            }
        
        # 从不同的请求格式中提取内容
        if isinstance(data, dict):
            if 'messages' in data and data['messages']:
                # 处理标准聊天格式
                content = data['messages'][-1].get('content', '').strip()
            else:
                # 处理简单格式
                content = data.get("content", "").strip()
        else:
            content = str(data).strip()
        
        # 根据输入内容返回不同类型的响应
        if content == "1":
            # 1：返回文本响应
            return self._generate_text_response()
        elif content == "2":
            # 2：返回表格响应
            return self._generate_table_response()
        elif content == "3":
            # 3：返回命令行响应
            return self._generate_command_response()
        elif content == "4":
            # 4：返回代码响应
            return self._generate_code_response()
        elif content == "5":
            # 5：返回错误命令响应
            return self._generate_error_command_response()
        elif content == "6":
            # 6：返回空响应
            return {"content": "", "tool_calls": []}
        elif content == "7":
            # 7：模拟超时
            time.sleep(2)  # 模拟2秒超时
            return {"content": "请求已超时", "tool_calls": []}
        elif content == "8":
            # 8：模拟请求失败
            return {"error": "模拟请求失败", "code": 500}
        elif content == "9":
            # 9：多工具调用
            return {
                "content": "这是一个包含多个工具调用的响应",
                "tool_calls": [
                    {
                        "name": "output_text",
                        "parameters": {
                            "content": "第一个工具调用",
                            "isError": False
                        }
                    },
                    {
                        "name": "output_table",
                        "parameters": {
                            "header": ["名称", "值"],
                            "rows": [["参数1", "值1"], ["参数2", "值2"]],
                            "metadata": {"title": "参数表格"}
                        }
                    }
                ]
            }
        elif content == "10":
            # 10：连续返回
            return self._generate_sequential_response()
        elif content == "11":
            # 11：连续每个类型返回两次
            return self._generate_multi_type_sequence()
        elif content == "test_qianwen":
            # 测试用例
            return {
                "content": "这是千问大模型的模拟响应",
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
        else:
            # 默认响应
            return {
                "content": "这是默认的模拟响应",
                "tool_calls": []
            }
    
    def _generate_text_response(self) -> Dict[str, Any]:
        """生成文本响应"""
        return {
            "content": "这是模拟的文本响应",
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "这是通过工具回调输出的测试文本",
                        "isError": False
                    }
                }
            ]
        }
    
    def _generate_table_response(self) -> Dict[str, Any]:
        """生成表格响应"""
        return {
            "content": "下面是一个测试表格",
            "tool_calls": [
                {
                    "name": "output_table",
                    "parameters": {
                        "header": ["列1", "列2", "列3"],
                        "rows": [
                            ["行1值1", "行1值2", "行1值3"],
                            ["行2值1", "行2值2", "行2值3"]
                        ],
                        "metadata": {"title": "测试表格"}
                    }
                }
            ]
        }
    
    def _generate_command_response(self) -> Dict[str, Any]:
        """生成命令行响应"""
        return {
            "content": "这是模拟的命令行响应",
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "这是模拟的命令行响应\nls -la",
                        "isError": False
                    }
                }
            ]
        }
    
    def _generate_code_response(self) -> Dict[str, Any]:
        """生成代码响应"""
        return {
            "content": "这是模拟的代码响应",
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "这是模拟的代码响应\ndef hello():\n    print('Hello, World!')",
                        "isError": False
                    }
                }
            ]
        }
    
    def _generate_error_command_response(self) -> Dict[str, Any]:
        """生成错误命令行响应"""
        return {
            "content": "这是一个错误的命令行示例",
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "这是一个错误的命令行示例\nrm -rf /",
                        "isError": True
                    }
                }
            ]
        }
    
    def _generate_sequential_response(self) -> Dict[str, Any]:
        """生成连续响应"""
        return {
            "content": "开始连续输出",
            "tool_calls": [
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "连续输出第一条消息",
                        "isError": False
                    }
                },
                {
                    "name": "output_progress",
                    "parameters": {
                        "progress": 50,
                        "message": "处理中..."
                    }
                },
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "连续输出第三条消息",
                        "isError": False
                    }
                }
            ]
        }
    
    def _generate_multi_type_sequence(self) -> Dict[str, Any]:
        """生成重复响应"""
        return {
            "content": "开始重复输出各种类型",
            "tool_calls": [
                # 文本类型两次
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "文本类型第一次",
                        "isError": False
                    }
                },
                {
                    "name": "output_text",
                    "parameters": {
                        "content": "文本类型第二次",
                        "isError": False
                    }
                },
                # 表格类型两次
                {
                    "name": "output_table",
                    "parameters": {
                        "header": ["列1", "列2"],
                        "rows": [["行1值1", "行1值2"]],
                        "metadata": {"title": "表格1"}
                    }
                },
                {
                    "name": "output_table",
                    "parameters": {
                        "header": ["列A", "列B"],
                        "rows": [["行A值1", "行A值2"]],
                        "metadata": {"title": "表格2"}
                    }
                }
            ]
        }

# 测试代码
if __name__ == "__main__":
    client = MockQianwenClient()
    
    # 测试不同类型的响应
    print("测试文本响应:")
    print(client.send_request({"content": "输入1"}))
    
    print("\n测试表格响应:")
    print(client.send_request({"content": "输入2"}))