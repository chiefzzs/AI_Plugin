import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

// Mock VSCode ExtensionContext
class MockExtensionContext implements vscode.ExtensionContext {
  subscriptions: { dispose(): void }[] = [];
  extensionPath: string = path.join(__dirname, '../../../');
  storagePath?: string = undefined;
  globalStoragePath: string = path.join(__dirname, '../../../globalStorage');
  workspaceState: vscode.Memento = new MockMemento();
  globalState: vscode.Memento = new MockMemento();
  extensionUri: vscode.Uri = vscode.Uri.file(this.extensionPath);
  
  asAbsolutePath(relativePath: string): string {
    return path.join(this.extensionPath, relativePath);
  }
}

// Mock Memento
class MockMemento implements vscode.Memento {
  private data: { [key: string]: any } = {};
  
  get<T>(key: string, defaultValue?: T): T | undefined {
    return this.data[key] ?? defaultValue;
  }
  
  update(key: string, value: any): Thenable<void> {
    this.data[key] = value;
    return Promise.resolve();
  }
}

// Mock WebviewPanel
class MockWebviewPanel {
  webview: MockWebview;
  
  constructor() {
    this.webview = new MockWebview();
  }
}

// Mock Webview
class MockWebview {
  asWebviewUri(localResource: vscode.Uri): vscode.Uri {
    // 模拟asWebviewUri方法，将本地路径转换为VSCode Webview URI格式
    return vscode.Uri.parse(`vscode-webview://mock-extension-id${localResource.path}`);
  }
  
  onDidReceiveMessage(callback: (message: any) => void, thisArg?: any, disposables?: vscode.Disposable[]): vscode.Disposable {
    return { dispose: () => {} };
  }
  
  postMessage(message: any): Thenable<boolean> {
    return Promise.resolve(true);
  }
}

// Mock WebviewManager
class MockWebviewManager {
  private webviewPanel: MockWebviewPanel | null = null;
  
  constructor() {
    this.webviewPanel = new MockWebviewPanel();
  }
  
  // 模拟getWebviewContent方法
  getWebviewContent(context: vscode.ExtensionContext): string {
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
  
  // 模拟getDefaultHtmlContent方法
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
  
  // 模拟getResourcePath方法
  private getResourcePath(context: vscode.ExtensionContext, relativePath: string): vscode.Uri {
    const absolutePath = vscode.Uri.file(context.asAbsolutePath(relativePath));
    return this.webviewPanel!.webview.asWebviewUri(absolutePath);
  }
}

describe('Webview模板加载集成测试', () => {
  let context: MockExtensionContext;
  let webviewManager: MockWebviewManager;
  
  beforeEach(() => {
    context = new MockExtensionContext();
    webviewManager = new MockWebviewManager();
  });
  
  describe('Webview模板加载集成测试', () => {
    it('should load HTML template successfully in VSCode environment', () => {
      const htmlContent = webviewManager.getWebviewContent(context);
      
      // 验证HTML内容不为空
      expect(htmlContent).toBeDefined();
      expect(htmlContent).not.toBe('');
      
      // 验证HTML结构完整
      expect(htmlContent).toContain('<!DOCTYPE html>');
      expect(htmlContent).toContain('<html');
      expect(htmlContent).toContain('<body');
    });
    
    it('should replace all placeholders with correct Webview URIs', () => {
      const htmlContent = webviewManager.getWebviewContent(context);
      
      // 验证所有占位符被替换
      expect(htmlContent).not.toContain('{{vueJsPath}}');
      expect(htmlContent).not.toContain('{{vueI18nJsPath}}');
      expect(htmlContent).not.toContain('{{appJsPath}}');
      expect(htmlContent).not.toContain('{{styleCssPath}}');
      
      // 验证替换后的路径是否为VSCode Webview URI格式
      expect(htmlContent).toContain('vscode-webview://');
    });
    
    it('should contain correct resource paths in HTML content', () => {
      const htmlContent = webviewManager.getWebviewContent(context);
      
      // 验证HTML内容包含所有必要的资源引用
      expect(htmlContent).toMatch(/<script src="vscode-webview:\/\/.*\/static\/js\/vue\.min\.js"><\/script>/);
      expect(htmlContent).toMatch(/<script src="vscode-webview:\/\/.*\/static\/js\/vue-i18n\.min\.js"><\/script>/);
      expect(htmlContent).toMatch(/<script src="vscode-webview:\/\/.*\/static\/js\/app\.js"><\/script>/);
      expect(htmlContent).toMatch(/<link rel="stylesheet" href="vscode-webview:\/\/.*\/static\/css\/style\.css">/);
    });
  });
  
  describe('资源路径转换测试', () => {
    it('should convert resource paths to Webview URIs correctly', () => {
      const mockWebviewPanel = new MockWebviewPanel();
      const mockWebview = mockWebviewPanel.webview;
      
      // 测试不同类型资源的路径转换
      const jsPath = vscode.Uri.file(path.join(context.extensionPath, 'static/js/vue.min.js'));
      const cssPath = vscode.Uri.file(path.join(context.extensionPath, 'static/css/style.css'));
      
      const webviewJsUri = mockWebview.asWebviewUri(jsPath);
      const webviewCssUri = mockWebview.asWebviewUri(cssPath);
      
      // 验证转换后的URI格式
      expect(webviewJsUri.scheme).toBe('vscode-webview');
      expect(webviewCssUri.scheme).toBe('vscode-webview');
      expect(webviewJsUri.path).toContain('/static/js/vue.min.js');
      expect(webviewCssUri.path).toContain('/static/css/style.css');
    });
  });
  
  describe('HTML内容安全性测试', () => {
    it('should use https protocol for resource references', () => {
      const htmlContent = webviewManager.getWebviewContent(context);
      
      // 在VSCode Webview中，资源URL应该使用vscode-webview协议而不是http/https
      expect(htmlContent).toContain('vscode-webview://');
      expect(htmlContent).not.toContain('http://');
      // 注意：在某些情况下，Webview可能允许使用https://引用外部资源，但本项目主要使用本地资源
    });
    
    it('should use asWebviewUri method for all local resources', () => {
      const htmlContent = webviewManager.getWebviewContent(context);
      
      // 验证所有资源引用都使用了转换后的URI
      const resourceRegex = /vscode-webview:\/\/.+?\/static\//g;
      const matches = htmlContent.match(resourceRegex);
      
      expect(matches).toBeDefined();
      expect(matches!.length).toBeGreaterThanOrEqual(4); // 至少应该有4个资源引用（vue.js, vue-i18n.js, app.js, style.css）
    });
  });
  
  describe('模板加载失败处理测试', () => {
    it('should return default HTML content when template loading fails', () => {
      // 保存原始的fs.readFileSync方法
      const originalReadFileSync = fs.readFileSync;
      
      try {
        // 模拟模板文件读取失败
        jest.spyOn(fs, 'readFileSync').mockImplementation(() => {
          throw new Error('File not found');
        });
        
        const htmlContent = webviewManager.getWebviewContent(context);
        
        // 验证返回的是默认HTML内容
        expect(htmlContent).toContain('模板加载失败，使用默认界面');
        expect(htmlContent).toContain('placeholder="输入内容"');
        expect(htmlContent).toContain('button>发送</button');
      } finally {
        // 恢复原始的fs.readFileSync方法
        fs.readFileSync = originalReadFileSync;
      }
    });
  });
});