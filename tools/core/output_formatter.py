#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
输出格式化模块
负责处理各种类型的输出格式化，支持文本、表格、进度等多种输出类型
"""

import json
from typing import Dict, Any, List, Optional

class OutputFormatter:
    """输出格式化器，处理各种类型的输出格式化"""
    
    # 定义命令行代码时刻标记
    CODE_BLOCK_MARKER = "[CODE_BLOCK_BEGIN]"
    CODE_BLOCK_END_MARKER = "[CODE_BLOCK_END]"
    
    def __init__(self):
        """初始化输出格式化器"""
        pass
    
    def output_json(self, data: Dict[str, Any]) -> None:
        """输出JSON格式的数据"""
        print(json.dumps(data))
    
    def output_text(self, content: str, is_error: bool = False, sequence_id: str = '') -> None:
        """输出文本信息"""
        self.output_json({
            "type": "text",
            "content": content,
            "isError": is_error,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def output_table(self, header: List[str], rows: List[List[Any]], 
                     metadata: Dict[str, Any] = None, sequence_id: str = '') -> None:
        """输出表格数据"""
        if metadata is None:
            metadata = {}
        self.output_json({
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
    
    def output_progress(self, current: int, total: int = 100, 
                        status: str = "处理中...", sequence_id: str = '') -> None:
        """输出进度信息"""
        self.output_json({
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
    
    def output_input_request(self, prompt: str, sequence_id: str = '') -> None:
        """输出请求输入的信息"""
        self.output_json({
            "type": "input_request",
            "content": {
                "prompt": prompt
            },
            "isError": False,
            "isEnd": False,
            "sequenceId": sequence_id
        })
    
    def output_end(self, message: str = "", sequence_id: str = '') -> None:
        """输出结束标志"""
        self.output_json({
            "type": "end",
            "content": message,
            "isError": False,
            "isEnd": True,
            "sequenceId": sequence_id
        })
    
    def output_code_block(self, code: str) -> None:
        """输出命令行代码块"""
        # 输出命令行代码时刻标记和代码内容
        print(f"{self.CODE_BLOCK_MARKER}\n{code}\n{self.CODE_BLOCK_END_MARKER}")
    
    def output_error(self, content: str, sequence_id: str = '') -> None:
        """输出错误信息"""
        self.output_text(content, is_error=True, sequence_id=sequence_id)

# 测试代码
if __name__ == "__main__":
    formatter = OutputFormatter()
    
    # 测试文本输出
    formatter.output_text("这是一条测试文本")
    
    # 测试表格输出
    formatter.output_table(
        ["名称", "类型"],
        [["文件1", "文本"], ["文件2", "图片"]],
        {"title": "测试表格"}
    )
    
    # 测试进度输出
    formatter.output_progress(50, 100, "处理中...")
    
    # 测试代码块输出
    formatter.output_code_block("print('Hello, World!')")
    
    # 测试结束输出
    formatter.output_end("测试完成")