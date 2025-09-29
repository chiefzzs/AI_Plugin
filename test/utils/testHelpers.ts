import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

/**
 * 测试辅助工具类，提供HTML模板测试和其他测试场景的通用辅助函数
 */
export class TestHelpers {
  /**
   * 读取HTML模板文件
   * @param templatePath 模板文件路径
   * @returns 模板文件内容
   */
  static readHtmlTemplate(templatePath: string): string {
    try {
      return fs.readFileSync(templatePath, 'utf8');
    } catch (error) {
      console.error(`Failed to read HTML template at ${templatePath}:`, error);
      throw new Error(`Failed to read HTML template: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * 渲染HTML模板，替换占位符
   * @param templateContent 模板内容
   * @param placeholders 占位符映射
   * @returns 渲染后的HTML内容
   */
  static renderHtmlTemplate(
    templateContent: string,
    placeholders: Record<string, string>
  ): string {
    let renderedHtml = templateContent;
    
    // 替换所有占位符
    for (const [placeholder, value] of Object.entries(placeholders)) {
      const placeholderRegex = new RegExp(`{{\s*${placeholder}\s*}}`, 'g');
      renderedHtml = renderedHtml.replace(placeholderRegex, value);
    }
    
    return renderedHtml;
  }

  /**
   * 验证HTML文档结构
   * @param htmlContent HTML内容
   * @returns 是否为有效的HTML结构
   */
  static validateHtmlStructure(htmlContent: string): boolean {
    // 简单验证HTML文档结构
    const hasDocType = htmlContent.includes('<!DOCTYPE html>');
    const hasHtmlTag = htmlContent.includes('<html') && htmlContent.includes('</html>');
    const hasHeadTag = htmlContent.includes('<head') && htmlContent.includes('</head>');
    const hasBodyTag = htmlContent.includes('<body') && htmlContent.includes('</body>');
    
    return hasDocType && hasHtmlTag && hasHeadTag && hasBodyTag;
  }

  /**
   * 检查HTML中是否包含所有必需的占位符
   * @param htmlContent HTML内容
   * @param requiredPlaceholders 必需的占位符列表
   * @returns 是否包含所有必需的占位符
   */
  static hasRequiredPlaceholders(
    htmlContent: string,
    requiredPlaceholders: string[]
  ): boolean {
    return requiredPlaceholders.every(placeholder => 
      htmlContent.includes(`{{${placeholder}}}`) || 
      htmlContent.includes(`{{ ${placeholder} }}`) ||
      htmlContent.includes(`{{\s*${placeholder}\s*}}`)
    );
  }

  /**
   * 创建模拟的VSCode ExtensionContext
   * @param extensionPath 扩展路径
   * @returns 模拟的ExtensionContext
   */
  static createMockExtensionContext(extensionPath: string = __dirname): MockExtensionContext {
    return new MockExtensionContext(extensionPath);
  }

  /**
   * 创建模拟的Webview
   * @returns 模拟的Webview
   */
  static createMockWebview(): MockWebview {
    return new MockWebview();
  }

  /**
   * 模拟模板文件加载失败
   */
  static mockTemplateLoadingFailure(): void {
    // 保存原始的fs.readFileSync方法
    const originalReadFileSync = fs.readFileSync;
    
    // 模拟读取失败
    jest.spyOn(fs, 'readFileSync').mockImplementation(() => {
      throw new Error('File not found');
    });
    
    // 返回恢复函数
    return () => {
      fs.readFileSync = originalReadFileSync;
    };
  }

  /**
   * 获取测试用的资源路径占位符映射
   * @returns 占位符映射
   */
  static getTestPlaceholders(): Record<string, string> {
    return {
      vueJsPath: '/test/vue.min.js',
      vueI18nJsPath: '/test/vue-i18n.min.js',
      appJsPath: '/test/app.js',
      styleCssPath: '/test/style.css'
    };
  }

  /**
   * 检查HTML内容中的安全特性
   * @param htmlContent HTML内容
   * @returns 安全检查结果
   */
  static checkHtmlSecurity(htmlContent: string): {
    usesHttpsForExternalResources: boolean;
    hasValidCsp: boolean;
    usesWebviewUri: boolean;
  } {
    // 检查是否使用https协议引用外部资源
    const hasHttpReferences = /http:\/\//i.test(htmlContent);
    const hasHttpsReferences = /https:\/\//i.test(htmlContent);
    const usesHttpsForExternalResources = hasHttpsReferences && !hasHttpReferences;
    
    // 检查是否有有效的CSP策略
    const hasCsp = /<meta\s+http-equiv="Content-Security-Policy"/i.test(htmlContent);
    
    // 检查是否使用了Webview URI
    const usesWebviewUri = /vscode-webview:\/\//i.test(htmlContent);
    
    return {
      usesHttpsForExternalResources,
      hasValidCsp,
      usesWebviewUri
    };
  }
}

/**
 * 模拟的VSCode ExtensionContext类
 */
export class MockExtensionContext implements vscode.ExtensionContext {
  subscriptions: { dispose(): void }[] = [];
  extensionPath: string;
  storagePath?: string = undefined;
  globalStoragePath: string;
  workspaceState: vscode.Memento = new MockMemento();
  globalState: vscode.Memento = new MockMemento();
  extensionUri: vscode.Uri;
  
  constructor(extensionPath: string) {
    this.extensionPath = extensionPath;
    this.globalStoragePath = path.join(extensionPath, 'globalStorage');
    this.extensionUri = vscode.Uri.file(this.extensionPath);
  }
  
  asAbsolutePath(relativePath: string): string {
    return path.join(this.extensionPath, relativePath);
  }
}

/**
 * 模拟的Memento类
 */
export class MockMemento implements vscode.Memento {
  private data: { [key: string]: any } = {};
  
  get<T>(key: string, defaultValue?: T): T | undefined {
    return this.data[key] ?? defaultValue;
  }
  
  update(key: string, value: any): Thenable<void> {
    this.data[key] = value;
    return Promise.resolve();
  }
}

/**
 * 模拟的Webview类
 */
export class MockWebview {
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

/**
 * 模拟的WebviewPanel类
 */
export class MockWebviewPanel {
  webview: MockWebview;
  
  constructor() {
    this.webview = new MockWebview();
  }
}