// webviewManager.ts
/**
 * Webview管理器类，负责创建、显示和管理VSCode Webview面板
 */
import * as vscode from 'vscode';
import { Logger } from './logger';
import * as fs from 'fs';

export class WebviewManager {
  private static instance: WebviewManager;
  private webviewPanel: vscode.WebviewPanel | undefined;

  /**
   * 私有构造函数，防止外部直接实例化
   */
  private constructor() {
    // 构造函数实现（当前为空）
  }

  /**
   * 获取WebviewManager单例实例
   * @returns WebviewManager实例
   */
  public static getInstance(): WebviewManager {
    if (!WebviewManager.instance) {
      WebviewManager.instance = new WebviewManager();
    }
    return WebviewManager.instance;
  }

  /**
   * 创建或显示已存在的Webview面板
   * @param context VSCode扩展上下文
   */
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
      (message: Record<string, unknown>) => this.handleWebviewMessage(message),
      null,
      context.subscriptions
    );
  }

  /**
   * 获取Webview内容 - 使用HTML模板文件方式
   * @param context VSCode扩展上下文
   * @returns Webview的HTML内容
   */
  public getWebviewContent(context: vscode.ExtensionContext): string {
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
      Logger.error('Failed to load HTML template:', error);
      // 如果模板加载失败，返回默认的HTML内容作为备用
      templateContent = this.getDefaultHtmlContent(vueJsPath, vueI18nJsPath, appJsPath, styleCssPath);
    }

    return templateContent;
  }

  /**
   * 默认HTML内容，作为模板加载失败时的备用
   * @param vueJsPath Vue.js资源路径
   * @param vueI18nJsPath vue-i18n资源路径
   * @param appJsPath 应用脚本路径
   * @param styleCssPath 样式文件路径
   * @returns 默认的HTML内容
   */
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
        <link rel="stylesheet" href="${styleCssPath.toString()}">
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
        
        <script src="${vueJsPath.toString()}"></script>
        <script src="${vueI18nJsPath.toString()}"></script>
        <script src="${appJsPath.toString()}"></script>
      </body>
      </html>
    `;
  }

  /**
   * 获取资源路径的辅助方法
   * @param context VSCode扩展上下文
   * @param relativePath 资源的相对路径
   * @returns 资源的Webview URI
   */
  private getResourcePath(context: vscode.ExtensionContext, relativePath: string): vscode.Uri {
    const absolutePath = vscode.Uri.file(context.asAbsolutePath(relativePath));
    if (!this.webviewPanel) {
      throw new Error('No active webview panel available');
    }
    return this.webviewPanel.webview.asWebviewUri(absolutePath);
  }

  /**
   * 处理Webview消息
   * @param message 从Webview接收的消息
   */
  private handleWebviewMessage(message: Record<string, unknown>): void {
    // 实现消息处理逻辑
    Logger.debug('Received message from webview:', message);
  }

  /**
   * 向Webview发送消息
   * @param message 要发送到Webview的消息
   */
  public sendMessageToWebview(message: Record<string, unknown>): void {
    if (this.webviewPanel) {
      void this.webviewPanel.webview.postMessage(message);
      Logger.debug('Sent message to webview:', message);
    } else {
      Logger.warn('No active webview panel to send message');
    }
  }

  /**
   * 检查Webview是否存在
   * @returns Webview是否存在
   */
  public hasActiveWebview(): boolean {
    return !!this.webviewPanel;
  }
}