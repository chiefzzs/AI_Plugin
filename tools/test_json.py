#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def test_json_parsing():
    """测试JSON解析逻辑"""
    
    # 测试不同格式的JSON字符串
    test_cases = [
        '{"content":"dir","projectDir":""}',  # 标准JSON
        '{\"content\":\"dir\",\"projectDir\":\"\"}',  # 转义双引号的JSON
        '{content:dir,projectDir:}',  # 缺少引号的JSON（PowerShell可能传递这种格式）
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_case}")
        
        # 尝试直接解析参数作为JSON
        try:
            input_data = json.loads(test_case)
            print(f"直接解析成功: {input_data}")
        except json.JSONDecodeError as e:
            print(f"直接解析失败: {str(e)}")
            
            # 尝试处理转义问题
            try:
                # 处理常见的转义问题，比如额外的反斜杠
                if '\\' in test_case:
                    # 尝试去除一层转义
                    test_case_fixed = test_case.replace('\\', '')
                    print(f"去除转义后: {test_case_fixed}")
                    input_data = json.loads(test_case_fixed)
                    print(f"去除转义后解析成功: {input_data}")
                else:
                    print("没有发现反斜杠，无法进一步处理")
            except json.JSONDecodeError as e2:
                print(f"去除转义后解析失败: {str(e2)}")

if __name__ == "__main__":
    test_json_parsing()