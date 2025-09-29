# 模块功能与代码文件规划

本文档依据类图和现有的代码实现，规划AI_Plugin插件中每个模块的功能和对应的代码文件。

## 1. 扩展激活模块 (MOD-001)

**核心功能**：负责插件的初始化、生命周期管理，接收用户事件并调用相应模块处理。

**代码文件**：
- `src/extension.ts`: 插件的主入口文件，负责初始化插件、注册命令、管理插件生命周期。

**文件内容描述**：
- 包含`activate`函数，在插件激活时执行初始化操作
- 包含`deactivate`函数，在插件停用时执行清理操作
- 注册用户命令（showWebview、executeCommand、clearTerminals等）
- 创建和管理视图提供程序实例
- 初始化日志系统和其他核心模块

## 2. Webview管理模块 (MOD-002)

**核心功能**：负责创建和管理Webview面板，加载基础HTML内容和资源，配置通信渠道，转发命令和结果，显示Webview界面。

**代码文件**：
- `src/utils/webviewManager.ts`: 实现Webview的创建、显示、隐藏和销毁功能，处理Webview与VSCode的通信。

**文件内容描述**：
- 采用单例模式实现WebviewManager类
- 提供`createOrShowWebview`方法创建或显示Webview面板
- 实现`getWebviewContent`方法，通过HTML模板生成Webview内容
- 处理Webview的消息通信，实现`handleWebviewMessage`方法
- 管理Webview的生命周期，处理关闭事件

## 3. Vue应用模块 (MOD-003)

**核心功能**：负责前端界面的渲染和交互，捕获用户操作，显示命令执行结果，支持Vue-i18n国际化，处理命令行代码块显示与执行，管理输出内容的动态渲染与阻塞控制。

**代码文件**：
- `static/html/webview-template.html`: Webview的HTML模板文件，定义了Vue应用的基本结构。
- `static/js/app.js`: Vue应用的主要实现文件（待创建）。
- `static/css/style.css`: 前端样式文件（待创建）。

**文件内容描述**：
- webview-template.html: 定义HTML结构，引入Vue库和相关资源，设置Vue应用的挂载点。
- app.js: 实现Vue应用实例，包含数据模型、方法和组件，处理用户交互和命令发送。
- style.css: 定义Webview界面的样式，确保良好的用户体验。

## 4. 命令执行模块 (MOD-004)

**核心功能**：负责处理用户命令，解析命令类型，执行相应操作，调用相应模块，处理命令执行过程中的状态变化。

**代码文件**：
- `src/utils/commandExecutor.ts`: 专门处理命令执行逻辑（待创建）。
- 部分功能在`src/extension.ts`中实现。


**文件内容描述**：
- 实现命令解析和路由功能
- 处理不同类型的命令（showWebview、clearTerminals、executeCommand等）


## 5. 终端管理模块 (MOD-005)

**核心功能**：负责创建和管理终端实例，支持后台运行模式和窗口可见模式，执行Python脚本，捕获命令输出，监控命令执行状态，销毁终端实例。

**代码文件**：
- `src/utils/terminalManager.ts`: 实现终端的创建、复用、命令执行和销毁功能。
- `tools/interactive-tool.py`: 主命令Python脚本，处理命令执行和输出格式化。
- `tools/execinfo.py`: 第二命令Python脚本，用于后台执行命令行代码。

**文件内容描述**：
- 管理终端实例集合（Map结构）
- 提供`createTerminal`方法创建或复用终端
- 实现`executeCommand`方法在指定终端执行命令
- 支持终端的单独销毁和批量销毁
- 提供终端状态查询功能
- 协调多个模块完成复杂命令的执行
- 管理命令执行的状态和结果

### 子模块：工具脚本 (MOD-005-SUB01)

**核心功能**：提供命令行交互能力，通过JSON格式的输入输出机制，支持多次输出、递归处理和代码块标记，实现插件的交互式命令执行体验，并与Vue前端建立完整的命令执行-渲染闭环。

**代码文件**：
- `tools/interactive-tool.py`: 主命令脚本，负责接收JSON格式的输入参数，执行相应操作，生成结构化的JSON输出。
- `tools/execinfo.py`: 第二命令脚本，负责在后台执行命令行代码，实时捕获输出并以JSON格式返回结果。
- `tools/README.md`: 工具脚本说明文档，详细规定了JSON交互格式和协议。

**文件内容描述**：
- interactive-tool.py: 实现InteractiveTool类，能够解析输入的JSON格式信息（包含一个hash，主要字段有content内容和工程目录等附加信息，以及一个递增的序列号），支持help/run/info/generate等命令，输出JSON格式的信息（包含一个数组，每个元素为一个hash，描述返回类型如文本、图片、命令行代码、Python代码、表格等内容，以及结束标识， 还包含字段描述是第一命令的返回还是第二命令的返回，还有一个字段描述命令字的序列号）。Vue前端收到结束标识后，会完成本命令的处理，继续上一个命令的余下部分的渲染。
- execinfo.py: 实现ExecInfo类，支持命令行代码参数接收和后台执行，能够捕获标准输出和错误输出，并将其格式化为符合规范的JSON对象返回，包含代码块标记和结束标志。
- README.md: 详细说明工具脚本的功能、使用方式、JSON交互格式规范以及与Vue前端的通信流程。
- 
## 6. 资源层 (MOD-006)

**核心功能**：负责加载和管理静态资源，包括Vue库文件、CSS样式和自定义脚本。

**代码文件**：
- `src/utils/resourceManager.ts`: 管理静态资源的加载和访问（待创建）。
- 相关静态资源文件位于`static/`目录下。

**文件内容描述**：
- 提供资源路径解析功能
- 管理静态资源的缓存策略
- 处理资源加载错误和重试机制
- 支持资源的动态更新

## 7. 通信桥接模块 (MOD-007)

**核心功能**：负责Webview与Vue应用之间的通信，封装并传递命令和结果数据。

**代码文件**：
- `src/utils/communicationBridge.ts`: 实现VSCode扩展与Webview之间的通信桥接（待创建）。

**文件内容描述**：
- 封装消息发送和接收逻辑
- 定义消息格式和协议
- 处理消息的序列化和反序列化
- 实现通信错误处理和重连机制

## 8. 服务集成模块 (MOD-008)

**核心功能**：负责与本地服务的通信，处理服务集成相关功能。

**代码文件**：
- `src/utils/serviceIntegration.ts`: 实现与本地服务的集成（待创建）。

**文件内容描述**：
- 建立与本地服务的连接
- 实现服务接口调用
- 处理服务响应和错误
- 管理服务连接的生命周期

## 9. 日志与状态模块 (MOD-009)

**核心功能**：负责记录插件运行日志，通过VSCode通知系统显示操作状态，记录命令执行过程，将详细日志输出到VSCode输出面板。

**代码文件**：
- `src/utils/logger.ts`: 实现日志记录功能。

**文件内容描述**：
- 提供不同级别的日志记录方法（debug、info、warn、error）
- 格式化日志输出，包含时间戳和日志级别
- 支持向控制台和VSCode输出面板输出日志
- 实现日志级别的控制

## 10. 模块间依赖关系

| 模块 | 依赖的模块 | 被依赖的模块 |
|------|-----------|------------|
| 扩展激活模块 | Webview管理模块、命令执行模块、日志与状态模块 | 所有模块 |
| Webview管理模块 | Vue应用模块、通信桥接模块、资源层、日志与状态模块 | 扩展激活模块、命令执行模块 |
| Vue应用模块 | 通信桥接模块 | Webview管理模块 |
| 命令执行模块 | 终端管理模块、Webview管理模块、日志与状态模块 | 扩展激活模块 |
| 终端管理模块 | 日志与状态模块 | 命令执行模块、服务集成模块 |
| 资源层 | - | Webview管理模块 |
| 通信桥接模块 | - | Webview管理模块、Vue应用模块 |
| 服务集成模块 | 终端管理模块 | - |
| 日志与状态模块 | - | 所有模块 |

## 11. 待实现的文件清单

基于现有的代码结构和模块规划，以下是需要创建的新文件：

1. `src/utils/commandExecutor.ts`
2. `src/utils/resourceManager.ts`
3. `src/utils/communicationBridge.ts`
4. `src/utils/serviceIntegration.ts`
5. `static/js/app.js`
6. `static/css/style.css`

这些文件将根据模块规划和需求文档逐步实现，以完善插件的功能。