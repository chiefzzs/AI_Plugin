# VSCode插件工具脚本说明

本文档详细说明VSCode插件中tools目录下的Python脚本功能、使用方式和返回格式。

## 目录结构

```
tools/
├── interactive-tool.py  # 主命令脚本
├── execinfo.py          # 第二命令脚本
└── README.md            # 工具说明文档
```

## 主命令：interactive-tool.py

### 功能描述

**interactive-tool.py**是插件的主命令脚本，负责：
1. 接收用户命令参数并执行相应操作
2. 生成结构化输出，支持多次输出
3. 创建带有"命令行代码时刻"标记的可执行代码块
4. 提供示例功能展示插件的交互能力
5. 标记命令执行结束

### 使用方式

```bash
python interactive-tool.py [command] [parameters]
```

### 支持的命令

| 命令 | 描述 | 参数 | 示例 |
|------|------|------|------|
| help | 显示帮助信息 | 无 | `python interactive-tool.py help` |
| run | 运行示例交互式命令 | 无 | `python interactive-tool.py run` |
| info | 显示特定主题的信息 | 主题名称 | `python interactive-tool.py info commands` |
| generate | 生成指定类型的示例代码 | 代码类型 | `python interactive-tool.py generate python` |

### 返回格式

脚本输出遵循特定的格式规范，以便VSCode插件正确解析：

1. **普通输出行**：直接输出内容，将显示在Webview界面上
   ```
   This is a normal output line
   ```

2. **命令行代码时刻标记**：标记可执行的代码块，格式如下
   ```
   [CODE_BLOCK_BEGIN]
   ls -la
   [CODE_BLOCK_END]
   ```
   当插件检测到这种格式时，会在Webview中显示代码块和执行按钮。

3. **结束标志**：标记命令执行结束
   ```
   [COMMAND_EXECUTION_END]
   ```
   插件收到此标志后，认为主命令执行完毕。

## 第二命令：execinfo.py

### 功能描述

**execinfo.py**是插件的第二命令脚本，负责：
1. 接收命令行代码作为参数
2. 在后台执行该命令行代码
3. 实时捕获并返回命令的标准输出和错误输出
4. 支持生成额外的命令行代码时刻标记（用于递归交互）
5. 标记命令执行结束

### 使用方式

```bash
python execinfo.py "command_to_execute"
```

### 支持的命令类型

该脚本支持执行各种类型的命令，包括：
- 简单命令（如`ls`, `pwd`, `echo`等）
- 复杂命令（包含管道、重定向等，如`ls -la | grep .py > files.txt`）
- 跨平台支持（自动适应Windows和Unix/Linux/Mac系统）

### 返回格式

脚本输出遵循以下格式规范：

1. **普通输出行**：命令的标准输出内容
   ```
   normal command output
   ```

2. **错误输出**：命令的错误输出，以特殊标记开头
   ```
   [ERROR_OUTPUT]
   Error message here
   ```

3. **命令行代码时刻标记**：与主命令相同的格式
   ```
   [CODE_BLOCK_BEGIN]
   git status
   [CODE_BLOCK_END]
   ```
   用于支持递归交互场景。

4. **结束标志**：与主命令相同的格式
   ```
   [COMMAND_EXECUTION_END]
   ```

## 交互流程说明

插件与这些脚本的交互流程如下：

1. **用户发起命令**：用户在Webview界面中发起命令请求

2. **执行主命令**：插件调用`interactive-tool.py`执行主命令
   - 主命令在后台运行
   - 主命令输出内容实时返回给插件
   - 主命令可能生成命令行代码时刻标记

3. **用户交互**：当出现命令行代码时刻标记时
   - Webview显示代码块和执行按钮
   - 用户点击执行按钮
   - 插件调用`execinfo.py`执行该代码块

4. **执行第二命令**：`execinfo.py`在后台执行用户选择的代码
   - 实时返回执行结果
   - 可能生成新的命令行代码时刻标记（递归交互）
   - 执行完成后返回结束标志

5. **继续主命令执行**：收到第二命令的结束标志后
   - 恢复主命令的输出渲染
   - 直到主命令执行完毕并返回结束标志

## 开发注意事项

1. **Python环境**：确保系统安装了Python 3.6或更高版本

2. **执行权限**：在Unix/Linux/Mac系统上，可能需要为脚本添加执行权限
   ```bash
   chmod +x interactive-tool.py execinfo.py
   ```

3. **安全考虑**：
   - 这些脚本执行用户提供的命令，存在安全风险
   - 在生产环境中，应当添加适当的安全检查和命令白名单

4. **扩展建议**：
   - 可以根据需要扩展`interactive-tool.py`中的命令集
   - 可以增强`execinfo.py`中的命令执行能力和安全性

## 示例场景

### 场景一：运行示例命令

1. 用户在Webview中发起`run`命令
2. 插件调用`python interactive-tool.py run`
3. 主命令输出示例内容和代码块
4. 用户点击代码块执行按钮
5. 插件调用`python execinfo.py "ls -la"`
6. 第二命令执行并返回结果
7. 用户可以继续与新生成的代码块交互（如果有）
8. 所有命令执行完毕，显示最终结果

### 场景二：生成和执行代码

1. 用户在Webview中发起`generate python`命令
2. 插件调用`python interactive-tool.py generate python`
3. 主命令生成Python示例代码并标记为代码块
4. 用户点击执行按钮
5. 插件调用`python execinfo.py "python -c \"print('Hello, World!')\""`
6. 第二命令执行并返回结果

通过这些工具脚本，VSCode插件可以提供丰富的交互式命令执行功能，增强用户体验和工作效率。