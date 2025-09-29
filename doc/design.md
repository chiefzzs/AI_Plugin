# VSCode 插件设计方案

## 1. 架构设计

### 1.1 整体架构
- **插件层**：VSCode插件主体，负责注册命令、创建Webview等
- **Webview层**：Vue2前端应用，负责用户交互和结果展示
- **服务层**：本地命令行服务，负责业务逻辑处理

### 1.2 模块划分
项目采用清晰的目录结构，将代码、资源和测试分离，便于维护和扩展：

**核心代码结构 (src/)**：
- **extension.ts**：插件入口文件，负责激活插件和注册命令
- **webviewManager.ts**：管理Webview的创建、销毁、通信和单例模式
- **commandExecutor.ts**：负责调用本地命令行服务
- **utils/**：工具函数
  - **logger.ts**：日志工具
  - **terminalManager.ts**：终端管理工具
  - **i18n.ts**：国际化工具

**静态资源结构 (static/)**：存放Webview的静态资源，便于加载和缓存
- **js/**：直接可执行的JavaScript文件，包括Vue2库和自定义脚本
- **css/**：样式文件
- **html/**：HTML模板文件

**测试结构 (test/)**：完整的测试分层架构
- **unit/**：单元测试
- **integration/**：集成测试
- **e2e/**：端到端测试
- **mocks/**：测试模拟数据
- **utils/**：测试工具函数

**工具目录 (tools/)**：本地命令行服务和辅助脚本
- 命令行服务执行文件
- 辅助工具和脚本

### 1.3 分离式设计

#### 1.3.1 VSCode插件逻辑与界面分离
- **插件核心逻辑**：与VSCode API解耦，封装核心业务逻辑
- **VSCode界面适配层**：专门负责与VSCode API交互的适配器
- **数据传输层**：定义标准化的数据格式和接口

```typescript
// 核心逻辑模块
export class CoreService {
  // 纯业务逻辑，不依赖VSCode API
  async processCommand(inputData: any): Promise<any> {
    // 处理命令的核心逻辑
    return result;
  }
}

// VSCode界面适配层
export class VSCodeAdapter {
  private coreService: CoreService;
  
  constructor() {
    this.coreService = new CoreService();
  }
  
  // 调用VSCode API的方法
  async executeInVSCode(context: vscode.ExtensionContext, inputData: any) {
    // 使用VSCode API进行操作
    const result = await this.coreService.processCommand(inputData);
    return result;
  }
}
```

#### 1.3.2 Webview与HTML分离
- **Webview控制器**：VSCode插件中负责管理Webview生命周期的控制器
- **HTML内容生成器**：负责生成Webview加载的HTML内容
- **前端应用**：独立的Vue2应用，可以脱离VSCode环境运行

#### 1.3.3 前端应用独立测试支持
- **直接使用JavaScript**：Vue2应用采用直接使用JS方式，无需编译构建即可执行
- **Mock服务**：提供模拟的VSCode API和后端服务
- **集成适配层**：负责与VSCode环境和独立浏览器环境的适配

```javascript
// 环境适配层
const EnvironmentAdapter = {
  isVSCodeEnvironment: () => {
    return typeof acquireVsCodeApi !== 'undefined';
  },
  
  getVsCodeApi: () => {
    if (EnvironmentAdapter.isVSCodeEnvironment()) {
      return acquireVsCodeApi();
    } else {
      // 返回模拟的VSCode API
      return {
        postMessage: (message) => console.log('Mock postMessage:', message),
        // 其他模拟方法...
      };
    }
  }
};

// 在应用中使用
const vscode = EnvironmentAdapter.getVsCodeApi();
```

## 2. 国际化方案

### 2.1 技术选型
采用VSCode官方的国际化方案结合Vue-i18n实现

### 2.2 实现方式

#### 2.2.1 VSCode插件层面国际化
- 使用VSCode的`l10n` API进行插件界面元素国际化
- 创建`package.nls.json`和`package.nls.zh.json`等语言文件
- 支持根据VSCode界面语言自动切换

```json
// package.nls.json
export default {
  "extension.displayName": "Interactive Tool",
  "extension.description": "A tool for interactive operations"
}

// package.nls.zh.json
export default {
  "extension.displayName": "交互式工具",
  "extension.description": "用于交互式操作的工具"
}
```

#### 2.2.2 Webview层面国际化
- 使用Vue-i18n库实现Webview内部的国际化
- 采用直接引用JS文件方式，无需编译构建
- 创建语言包文件存放不同语言的翻译
- 支持手动切换语言

```javascript
// 在HTML中直接引用Vue2和Vue-i18n库
// <script src="path/to/vue.min.js"></script>
// <script src="path/to/vue-i18n.min.js"></script>

// app.js - 直接可执行的JavaScript文件
const i18n = new VueI18n({
  locale: 'zh', // 默认语言
  messages: {
    en: {
      // 英文翻译
    },
    zh: {
      // 中文翻译
    }
  }
})

new Vue({
  el: '#app',
  i18n,
  data() {
    return {
      // 数据模型
    }
  },
  methods: {
    // 方法
  }
})
```

#### 2.2.3 国际化资源管理
- 集中管理所有可翻译文本
- 提供翻译键的命名规范
- 支持动态加载语言包

## 3. 测试框架设计

### 3.1 测试分层
采用多层测试架构，确保不同层级都可以进行自动化测试：
- **单元测试**：测试单个组件或函数的功能
- **集成测试**：测试多个组件或模块的交互
- **前端独立测试**：在浏览器环境中测试Vue2应用
- **插件集成测试**：在VSCode环境中测试插件功能
- **端到端测试**：测试完整的用户流程

### 3.2 不同层级测试框架选型

#### 3.2.1 单元测试
- **框架**：Jest (JavaScript/TypeScript)、Vue Test Utils (Vue组件)
- **目的**：测试独立函数和组件的功能
- **适用范围**：插件核心逻辑、前端组件、工具函数
- **自动化支持**：支持CI/CD环境自动执行

```javascript
// Jest配置示例
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  moduleFileExtensions: ['ts', 'js', 'vue'],
  transform: {
    '^.+\.ts$': 'ts-jest',
    '^.+\.vue$': 'vue-jest'
  }
};
```

#### 3.2.2 前端独立测试
- **框架**：Jest + Vue Test Utils
- **目的**：在浏览器环境中测试Vue2应用，脱离VSCode插件
- **适用范围**：前端UI组件、交互逻辑、数据展示
- **自动化支持**：支持本地和CI/CD环境自动执行
- **测试方式**：直接加载JS文件进行测试，无需构建过程

```javascript
// Jest配置示例 - 针对直接使用JS的Vue应用
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['ts', 'js'],
  setupFilesAfterEnv: ['./tests/setup.js']
};
```

#### 3.2.3 插件集成测试
- **框架**：Jest + VSCode Test API
- **目的**：在VSCode环境中测试插件功能和Webview集成
- **适用范围**：命令注册、Webview创建、消息通信
- **自动化支持**：支持在VSCode测试环境中自动执行

```typescript
// VSCode测试示例
import * as vscode from 'vscode';
import * as path from 'path';

test('should activate extension', async () => {
  const extensionPath = path.resolve(__dirname, '../../');
  const extension = vscode.extensions.getExtension('publisher.extension-name');
  
  await extension?.activate();
  expect(extension?.isActive).toBe(true);
});
```

#### 3.2.4 端到端测试
- **框架**：Playwright 或 Cypress
- **目的**：测试完整的用户流程，包括VSCode交互
- **适用范围**：完整用户操作流程、界面响应、结果展示
- **自动化支持**：支持在CI/CD环境中自动执行

```javascript
// Playwright配置示例
const { PlaywrightTestConfig } = require('@playwright/test');

const config: PlaywrightTestConfig = {
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
};

module.exports = config;
```

### 3.3 测试目录结构
```
tests/
  unit/           // 单元测试
    extension.test.ts
    commandExecutor.test.ts
  integration/    // 集成测试
    webviewCommunication.test.ts
  e2e/            // 端到端测试
    basicInteraction.test.ts
  mocks/          // 测试模拟数据
  utils/          // 测试工具函数
```

### 3.4 自动执行机制
- 使用GitHub Actions或其他CI/CD工具配置自动化测试
- 支持本地和远程环境的测试执行
- 测试结果报告生成

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Run unit tests
        run: npm run test:unit
      - name: Run integration tests
        run: npm run test:integration
```

## 4. 实现细节

### 4.1 调试信息展示
- 使用VSCode的`console.log`、`console.warn`、`console.error`等方法记录调试信息
- 创建统一的日志工具函数，包含时间戳、操作类型、数据内容等信息
- 日志级别可配置（debug、info、warn、error）

```typescript
// logger.ts
export class Logger {
  private static log(level: 'debug' | 'info' | 'warn' | 'error', message: string, data?: any) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    switch (level) {
      case 'debug':
        console.log(logMessage, data);
        break;
      case 'info':
        console.info(logMessage, data);
        break;
      case 'warn':
        console.warn(logMessage, data);
        break;
      case 'error':
        console.error(logMessage, data);
        break;
    }
  }
  
  static debug(message: string, data?: any) {
    this.log('debug', message, data);
  }
  
  // 其他日志级别方法...
}
```

### 4.2 Webview创建与通信
- 使用VSCode的`createWebviewPanel`方法创建Webview
- 实现Webview单例模式，确保同一时间只能打开一个Webview实例
- 实现双向通信机制（VSCode → Webview 和 Webview → VSCode）
- 使用消息通道进行安全通信

```typescript
// webviewManager.ts
import * as vscode from 'vscode';
import { Logger } from './utils/logger';
import * as fs from 'fs';

export class WebviewManager {
  private static instance: WebviewManager;
  private webviewPanel: vscode.WebviewPanel | undefined;
  
  private constructor() {}
  
  // 单例模式获取WebviewManager实例
  public static getInstance(): WebviewManager {
    if (!WebviewManager.instance) {
      WebviewManager.instance = new WebviewManager();
    }
    return WebviewManager.instance;
  }
  
  // 创建或显示已存在的Webview
  public createOrShowWebview(context: vscode.ExtensionContext): void {
    const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;
    
    // 如果Webview已存在，则显示它
    if (this.webviewPanel) {
      this.webviewPanel.reveal(column);
      Logger.debug('Revealed existing webview panel');
      return;
    }
    
    // 创建新的Webview
    this.webviewPanel = vscode.window.createWebviewPanel(
      'interactiveTool',
      'Interactive Tool',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.file(context.asAbsolutePath('static/dist'))]
      }
    );
    
    Logger.debug('Created new webview panel');
    
    // 设置Webview内容
    this.webviewPanel.webview.html = this.getWebviewContent(context);
    
    // 处理Webview关闭事件
    this.webviewPanel.onDidDispose(() => {
      this.webviewPanel = undefined;
      Logger.debug('Webview panel disposed');
    }, null, context.subscriptions);
    
    // 设置消息接收处理
    this.webviewPanel.webview.onDidReceiveMessage(
      message => this.handleWebviewMessage(message),
      null,
      context.subscriptions
    );
  }
  
  // 获取Webview内容 - 使用HTML模板文件方式
  private getWebviewContent(context: vscode.ExtensionContext): string {
    // 获取静态资源路径
    const vueJsPath = this.getResourcePath(context, 'static/js/vue.min.js');
    const vueI18nJsPath = this.getResourcePath(context, 'static/js/vue-i18n.min.js');
    const appJsPath = this.getResourcePath(context, 'static/js/app.js');
    const styleCssPath = this.getResourcePath(context, 'static/css/style.css');
    
    // 读取HTML模板文件内容
    const templatePath = context.asAbsolutePath('static/html/webview-template.html');
    let templateContent = '';
    
    try {
      // 读取模板文件
      templateContent = fs.readFileSync(templatePath, 'utf8');
      
      // 替换模板中的占位符
      templateContent = templateContent
        .replace('{{vueJsPath}}', vueJsPath.toString())
        .replace('{{vueI18nJsPath}}', vueI18nJsPath.toString())
        .replace('{{appJsPath}}', appJsPath.toString())
        .replace('{{styleCssPath}}', styleCssPath.toString());
    } catch (error) {
      console.error('Failed to load HTML template:', error);
      // 如果模板加载失败，返回默认的HTML内容作为备用
      templateContent = this.getDefaultHtmlContent(vueJsPath, vueI18nJsPath, appJsPath, styleCssPath);
    }
    
    return templateContent;
  }
  
  // 默认HTML内容，作为模板加载失败时的备用
  private getDefaultHtmlContent(
    vueJsPath: vscode.Uri,
    vueI18nJsPath: vscode.Uri,
    appJsPath: vscode.Uri,
    styleCssPath: vscode.Uri
  ): string {
    return `
      <!DOCTYPE html>
      <html lang="zh-CN">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Tool</title>
        <link rel="stylesheet" href="${styleCssPath}">
      </head>
      <body>
        <div id="app">
          <div class="container">
            <h1>模板加载失败，使用默认界面</h1>
            <input v-model="inputData" type="text" placeholder="输入内容">
            <button @click="sendCommand">发送</button>
            <div v-if="result" class="result">{{ result }}</div>
          </div>
        </div>
        
        <script src="${vueJsPath}"></script>
        <script src="${vueI18nJsPath}"></script>
        <script src="${appJsPath}"></script>
      </body>
      </html>
    `;
  }
  
  // 获取资源路径的辅助方法
  private getResourcePath(context: vscode.ExtensionContext, relativePath: string): vscode.Uri {
    const absolutePath = vscode.Uri.file(context.asAbsolutePath(relativePath));
    return this.webviewPanel!.webview.asWebviewUri(absolutePath);
  }
  
  // 处理Webview消息
  private handleWebviewMessage(message: any): void {
    // 实现消息处理逻辑
    // ...
  }
  
  // 向Webview发送消息
  public sendMessageToWebview(message: any): void {
    if (this.webviewPanel) {
      this.webviewPanel.webview.postMessage(message);
    }
  }
  
  // 检查Webview是否存在
  public hasActiveWebview(): boolean {
    return !!this.webviewPanel;
  }
}

### 4.3 终端命令执行
- 使用VSCode的`window.createTerminal`方法创建终端窗口
- 通过终端的`sendText`方法发送命令到终端执行
- 监听终端的`onDidWriteData`事件捕获执行结果
- 实现终端管理，包括创建、复用和销毁

```typescript
// terminalManager.ts
import * as vscode from 'vscode';

export class TerminalManager {
  private terminals: Map<string, vscode.Terminal> = new Map();
  
  createTerminal(name: string): vscode.Terminal {
    let terminal = this.terminals.get(name);
    
    if (!terminal) {
      terminal = vscode.window.createTerminal({
        name: name,
        isTransient: false
      });
      this.terminals.set(name, terminal);
    }
    
    return terminal;
  }
  
  executeCommand(terminalName: string, command: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const terminal = this.createTerminal(terminalName);
      let output = '';
      
      // 监听终端输出
      const disposable = vscode.window.onDidWriteTerminalData((e) => {
        if (e.terminal === terminal) {
          output += e.data;
          // 这里可以添加判断命令是否执行完成的逻辑
        }
      });
      
      terminal.show();
      terminal.sendText(command);
      
      // 这里应该有更复杂的逻辑来判断命令何时执行完成
      // 为了简化示例，使用setTimeout
      setTimeout(() => {
        disposable.dispose();
        resolve(output);
      }, 5000);
    });
  }
  
  disposeTerminal(name: string) {
    const terminal = this.terminals.get(name);
    if (terminal) {
      terminal.dispose();
      this.terminals.delete(name);
    }
  }
}

### 4.3 资源加载策略
- 使用VSCode的Webview资源加载API直接加载JavaScript文件
- 采用直接使用JS方式，无需编译构建即可执行
- 支持加载Vue2库和自定义脚本
- 实现资源缓存策略，提高性能

```javascript
// 直接可执行的app.js示例
// 初始化Vue应用
new Vue({
  el: '#app',
  data: {
    inputData: '',
    result: ''
  },
  methods: {
    sendCommand() {
      // 获取VSCode API（可能是真实的或模拟的）
      const vscode = EnvironmentAdapter.getVsCodeApi();
      
      // 发送命令到插件
      vscode.postMessage({
        type: 'executeCommand',
        data: this.inputData
      });
      
      // 接收来自插件的消息
      window.addEventListener('message', event => {
        const message = event.data;
        if (message.type === 'commandResult') {
          this.result = message.data;
        }
      });
    }
  }
});

## 5. 扩展性设计
- 插件配置项设计，支持用户自定义设置
- 命令行服务接口标准化，支持不同后端服务接入
- Webview组件化设计，便于功能扩展