# Tools 测试用例文档

## 1. 概述

本文档详细描述了 VSCode 插件中 Python 工具模块（tools 目录）的测试用例设计。这些工具包括交互式执行工具、命令执行工具等，负责处理来自前端的命令请求并执行相应操作。

## 2. 测试环境

- **Python 版本**: 3.7+ 
- **测试框架**: pytest
- **操作系统**: Windows, Linux, macOS
- **依赖**: 无特殊依赖（标准库即可运行）

## 3. 测试用例分类

### 3.1 execinfo.py 测试用例

execinfo.py 是命令执行信息工具，负责在后台执行命令并返回格式化的结果。

#### 3.1.1 JSON 输入解析测试
**测试用例1：JSON输入解析测试**
- **目的**：验证 execinfo.py 能够正确解析 JSON 格式输入
- **步骤**：
  1. 准备包含 content 和 projectDir 的 JSON 格式输入
  2. 调用 execinfo.py 并传入 JSON 输入
  3. 检查输出是否包含命令执行信息
- **预期结果**：工具成功解析 JSON 输入并执行命令
- **测试数据**：`{"content": "echo Hello, World!", "projectDir": "/path/to/project"}`
- **测试工具**：pytest, subprocess

#### 3.1.2 命令执行测试
**测试用例2：命令执行基本功能测试**
- **目的**：验证 execinfo.py 能够正确执行命令并返回结果
- **步骤**：
  1. 准备简单的测试命令（如 echo）
  2. 调用 execinfo.py 执行命令
  3. 检查输出是否包含命令的预期结果
- **预期结果**：命令成功执行，输出包含预期结果
- **测试数据**：`echo "Hello, World!"`
- **测试工具**：pytest, subprocess

#### 3.1.3 错误处理测试
**测试用例3：错误处理功能测试**
- **目的**：验证 execinfo.py 在执行失败命令时的错误处理能力
- **步骤**：
  1. 准备肯定会失败的命令（如不存在的命令）
  2. 调用 execinfo.py 执行命令
  3. 检查输出是否包含错误信息
- **预期结果**：工具能够捕获错误，输出包含错误信息，且工具自身正常退出
- **测试数据**：`nonexistent_command`
- **测试工具**：pytest, subprocess

#### 3.1.4 项目目录处理测试
**测试用例4：项目目录参数处理测试**
- **目的**：验证 execinfo.py 能够正确处理项目目录参数
- **步骤**：
  1. 创建临时目录并在其中创建测试文件
  2. 准备列出目录内容的命令
  3. 调用 execinfo.py 执行命令，并指定临时目录为 projectDir
  4. 检查输出是否包含测试文件名
- **预期结果**：工具在指定目录下执行命令，输出包含测试文件
- **测试数据**：目录列表命令（dir /b 或 ls）
- **测试工具**：pytest, subprocess, tempfile

#### 3.1.5 原始命令输入测试
**测试用例5：原始命令输入处理测试**
- **目的**：验证 execinfo.py 能够处理非 JSON 格式的原始命令输入
- **步骤**：
  1. 准备简单的原始命令（非 JSON 格式）
  2. 调用 execinfo.py 并传入原始命令
  3. 检查命令是否成功执行
- **预期结果**：工具能够正确解析并执行原始命令
- **测试数据**：`echo Hello, Raw Command!`
- **测试工具**：pytest, subprocess

#### 3.1.6 返回码测试
**测试用例6：命令返回码测试**
- **目的**：验证 execinfo.py 能够正确捕获并返回命令的返回码
- **步骤**：
  1. 准备已知返回特定码的命令
  2. 调用 execinfo.py 执行命令
  3. 检查输出是否包含正确的返回码信息
- **预期结果**：输出中包含命令的正确返回码
- **测试数据**：`exit 0`（成功）或 `exit 1`（失败）
- **测试工具**：pytest, subprocess

### 3.2 interactive_tool.py 测试用例

interactive_tool.py 是交互式执行工具，提供交互式命令执行体验。

#### 3.2.1 JSON 输入解析测试
**测试用例7：JSON输入解析测试**
- **目的**：验证 interactive_tool.py 能够正确解析 JSON 格式输入
- **步骤**：
  1. 准备包含 content 和 projectDir 的 JSON 格式输入
  2. 调用 interactive_tool.py 并传入 JSON 输入
  3. 检查输出是否包含命令执行信息
- **预期结果**：工具成功解析 JSON 输入并执行命令
- **测试数据**：`{"content": "info features", "projectDir": "/path/to/project"}`
- **测试工具**：pytest, subprocess

#### 3.2.2 命令执行测试
**测试用例8：内置命令执行测试**
- **目的**：验证 interactive_tool.py 能够正确执行内置命令
- **步骤**：
  1. 准备内置命令（如 info、help）
  2. 调用 interactive_tool.py 执行命令
  3. 检查输出是否包含预期的命令结果
- **预期结果**：内置命令成功执行，输出包含预期结果
- **测试数据**：`info features`
- **测试工具**：pytest, subprocess

#### 3.2.3 未知命令处理测试
**测试用例9：未知命令处理测试**
- **目的**：验证 interactive_tool.py 能够正确处理未知命令
- **步骤**：
  1. 准备一个不存在的内置命令
  2. 调用 interactive_tool.py 执行该命令
  3. 检查输出是否包含帮助信息或错误提示
- **预期结果**：工具能够识别未知命令并提供适当的帮助信息
- **测试数据**：`unknown_command`
- **测试工具**：pytest, subprocess

#### 3.2.4 项目目录处理测试
**测试用例10：项目目录参数处理测试**
- **目的**：验证 interactive_tool.py 能够正确处理项目目录参数
- **步骤**：
  1. 创建临时目录
  2. 准备需要在特定目录下执行的命令
  3. 调用 interactive_tool.py 执行命令，并指定临时目录为 projectDir
  4. 检查命令是否在指定目录下执行
- **预期结果**：工具在指定目录下执行命令
- **测试数据**：`list` 命令
- **测试工具**：pytest, subprocess, tempfile

#### 3.2.5 原始命令输入测试
**测试用例11：原始命令输入处理测试**
- **目的**：验证 interactive_tool.py 能够处理非 JSON 格式的原始命令输入
- **步骤**：
  1. 准备简单的原始命令（非 JSON 格式）
  2. 调用 interactive_tool.py 并传入原始命令
  3. 检查命令是否成功执行
- **预期结果**：工具能够正确解析并执行原始命令
- **测试数据**：`info help`
- **测试工具**：pytest, subprocess

## 4. 测试目录结构

```
test/
├── tools/                    # Python工具测试目录
│   ├── test_execinfo.py      # execinfo.py 测试文件
│   └── test_interactive_tool.py  # interactive_tool.py 测试文件
└── unit/tools/               # 工具核心模块单元测试
    └── core/
        ├── test_command_processor.py  # 命令处理器测试
        ├── test_llm_client.py         # LLM客户端测试
        ├── test_mock_llm.py           # 模拟LLM测试
        ├── test_output_formatter.py   # 输出格式化器测试
        └── test_tool_handler.py       # 工具处理器测试
```

## 5. 测试执行方式

### 5.1 运行所有工具测试

```bash
cd d:\learnning\plugin
python -m pytest test/tools/ -v
```

### 5.2 运行特定工具测试

```bash
# 运行 execinfo.py 测试
python -m pytest test/tools/test_execinfo.py -v

# 运行 interactive_tool.py 测试
python -m pytest test/tools/test_interactive_tool.py -v

# 运行核心模块测试
python -m pytest test/unit/tools/core/ -v
```

### 5.3 直接运行单个测试文件

```bash
# 直接运行测试文件
python ./test/tools/test_execinfo.py
python ./test/unit/tools/core/test_mock_llm.py
```

## 6. 测试维护指南

1. **添加新测试用例**：当开发新功能时，请在相应的测试文件中添加对应的测试用例
2. **更新测试用例**：当修改现有功能时，请同步更新相关的测试用例
3. **修复失败的测试**：如果测试失败，请分析原因并修复代码或测试用例
4. **测试覆盖**：尽量保持高测试覆盖率，确保代码质量和稳定性

## 7. 常见问题及解决方案

1. **测试失败：未找到测试文件**
   - 检查文件路径是否正确
   - 确认测试文件是否存在

2. **测试失败：命令执行错误**
   - 检查命令是否在当前操作系统上有效
   - 确认测试环境是否有足够的权限执行命令

3. **测试失败：JSON解析错误**
   - 检查JSON格式是否正确
   - 确保特殊字符已正确转义

4. **测试失败：相对导入错误**
   - 确保从正确的目录运行测试
   - 检查PYTHONPATH环境变量是否正确设置