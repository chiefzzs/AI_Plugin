#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式工具主程序
将各个模块组合起来，提供完整的交互式工具功能
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# 添加core目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.command_processor import CommandProcessor
from core.output_formatter import OutputFormatter

class InteractiveTool:
    """交互式工具主类"""
    
    def __init__(self, use_mock: bool = False):
        """初始化交互式工具"""
        self.use_mock = use_mock
        self.formatter = OutputFormatter()
        self.processor = CommandProcessor(use_mock=use_mock)
        self.running = False
    
    def start(self) -> None:
        """启动交互式工具"""
        self.running = True
        self.formatter.output_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                command = self._get_user_input()
                
                # 处理命令
                if command is not None:
                    result = self.processor.process_command(command, self._generate_sequence_id())
                    
                    # 检查是否请求退出
                    if result is True:
                        self.running = False
            except KeyboardInterrupt:
                # 处理Ctrl+C中断
                self.formatter.output_text("\n检测到中断，正在退出...")
                self.running = False
            except Exception as e:
                self.formatter.output_error(f"执行出错: {str(e)}")
        
        self.formatter.output_goodbye()
    
    def _get_user_input(self) -> Optional[str]:
        """获取用户输入"""
        try:
            # 在实际环境中使用input函数
            # 这里为了测试方便，添加了一些模拟输入处理
            if self.use_mock:
                # 简单的模拟输入处理
                # 实际应用中应使用input()获取用户输入
                return self._mock_input()
            else:
                return input("\n> ")
        except EOFError:
            # 处理EOF（Ctrl+D）
            return "exit"
    
    def _mock_input(self) -> Optional[str]:
        """模拟用户输入（仅用于测试）"""
        # 这个方法在实际交互式环境中会被替换为真正的用户输入
        # 这里提供一个简单的模拟实现
        mock_commands = [
            "help",
            "info commands",
            "qianwen 你好，介绍一下你自己",
            "code python 生成一个简单的函数",
            "exit"
        ]
        
        # 简单的轮询模拟
        if not hasattr(self, '_mock_index'):
            self._mock_index = 0
            self.formatter.output_text("[模拟模式] 使用示例命令序列进行演示...", "")
        
        if self._mock_index < len(mock_commands):
            command = mock_commands[self._mock_index]
            self._mock_index += 1
            self.formatter.output_text(f"> {command}", "")
            return command
        else:
            return "exit"
    
    def _generate_sequence_id(self) -> str:
        """生成唯一的序列ID"""
        if not hasattr(self, '_seq_counter'):
            self._seq_counter = 0
        self._seq_counter += 1
        return f"seq-{self._seq_counter}"
    
    def execute(self, command: str) -> Any:
        """执行单个命令"""
        return self.processor.process_command(command, self._generate_sequence_id())
    
    def process_command(self, command: str) -> Any:
        """处理命令的别名方法"""
        return self.execute(command)
    
    def handle_tool_call(self, tool_call: Dict[str, Any], sequence_id: str) -> Any:
        """处理工具调用"""
        return self.processor.tool_handler.handle_tool_call(tool_call, sequence_id)
    
    def output_json(self, data: Any) -> None:
        """输出JSON格式数据"""
        self.formatter.output_json(data)
    
    def show_help(self) -> None:
        """显示帮助信息"""
        self.formatter.show_help()
    
    def show_info(self, topics: list) -> None:
        """显示信息"""
        self.formatter.show_info(topics)
    
    def generate_code(self, code_type: str, description: str) -> str:
        """生成代码"""
        return self.formatter.generate_code(code_type, description)
    
    def output_code_block(self, code: str, code_type: str, sequence_id: str = '') -> None:
        """输出代码块"""
        self.formatter.output_code_block(code, code_type, sequence_id)
    
    def set_mock_mode(self, use_mock: bool) -> None:
        """设置是否使用模拟模式"""
        self.processor.set_mock_mode(use_mock)
        self.use_mock = use_mock
    
    def register_custom_command(self, name: str, handler: callable, description: str = "") -> bool:
        """注册自定义命令"""
        return self.processor.register_custom_command(name, handler, description)

# 配置加载函数
def load_config(config_file: str = None) -> Dict[str, Any]:
    """加载配置文件"""
    config = {
        "use_mock": False,
        "llm_base_url": os.environ.get('LLM_BASE_URL', 'https://api-inference.modelscope.cn/v1/'),
        "llm_token": os.environ.get('LLM_TOKEN', '')
    }
    
    # 如果提供了配置文件，加载配置
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    return config

# 主函数
def main():
    """主函数"""
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='交互式工具')
    parser.add_argument('--mock', action='store_true', help='使用模拟模式')
    parser.add_argument('--config', type=str, help='配置文件路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 如果命令行参数指定了mock模式，覆盖配置文件
    use_mock = args.mock or config.get('use_mock', False)
    
    # 设置环境变量
    os.environ['LLM_BASE_URL'] = config.get('llm_base_url', 'https://api-inference.modelscope.cn/v1/')
    os.environ['LLM_TOKEN'] = config.get('llm_token', '')
    
    # 创建并启动交互式工具
    tool = InteractiveTool(use_mock=use_mock)
    tool.start()

# 入口点
if __name__ == '__main__':
    main()