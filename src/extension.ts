// extension.ts
/**
 * VSCode插件的主入口文件
 */
import * as vscode from 'vscode';
import * as path from 'path';
import { Logger } from './utils/logger';
import { WebviewManager } from './utils/webviewManager';
import { TerminalManager } from './utils/terminalManager';
import { ToolProcessor } from './utils/toolProcessor';

// 定义Webview消息接口
interface WebviewMessage {
  command: string;
  text?: string;
  toolName?: string;
  sequenceId?: string;
  processId?: string;
  data?: any;
}

// 定义工具响应接口
interface ToolResponse {
  type: string;
  content: string;
  isError: boolean;
  isEnd: boolean;
  sequenceId: string;
}

class InteractiveToolViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'interactive-tool.webview';

  private _view?: vscode.WebviewView;
  private readonly _context: vscode.ExtensionContext;
  private _webviewManager: WebviewManager;
  private _toolProcessor: ToolProcessor;
  private _activeProcesses: Map<string, string> = new Map(); // sequenceId -> processId

  constructor(_context: vscode.ExtensionContext) {
    this._context = _context;
    this._webviewManager = WebviewManager.getInstance();
    
    // 初始化工具处理器
    const toolsDir = path.join(this._context.extensionPath, 'tools');
    this._toolProcessor = ToolProcessor.getInstance({
      toolsDir: toolsDir
    });
  }

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      // 允许加载本地资源
      localResourceRoots: [
        vscode.Uri.joinPath(this._context.extensionUri, 'static')
      ]
    };

    // 设置Webview内容
    webviewView.webview.html = this._webviewManager.getWebviewContent(this._context);

    // 添加消息监听
    webviewView.webview.onDidReceiveMessage(
      (message: WebviewMessage) => {
        this.handleWebviewMessage(message, webviewView.webview);
      },
      undefined,
      this._context.subscriptions
    );
  }

  /**
   * 处理来自Webview的消息
   */
  private handleWebviewMessage(message: WebviewMessage, webview: vscode.Webview): void {
    switch (message.command) {
      case 'executeCommand': {
        // 处理从Webview发送的终端命令
        Logger.debug(`Received terminal command from webview: ${message.text || ''}`);
        const terminalManager = new TerminalManager();
        void terminalManager.executeCommand('Interactive Tool Terminal', message.text || '')
          .then(result => {
            void webview.postMessage({
              command: 'commandResult',
              result: result,
              sequenceId: message.sequenceId
            });
          })
          .catch(error => {
            void webview.postMessage({
              command: 'commandError',
              error: error instanceof Error ? error.message : String(error),
              sequenceId: message.sequenceId
            });
          });
        return;
      }
      
      case 'executeTool': {
        // 处理从Webview发送的工具执行请求
        if (!message.toolName || !message.text || !message.sequenceId) {
          Logger.error('Invalid tool execution request: missing required parameters');
          void webview.postMessage({
            command: 'toolError',
            error: 'Invalid request: missing required parameters',
            sequenceId: message.sequenceId
          });
          return;
        }
        
        Logger.debug(`Received tool execution request: ${message.toolName}, command: ${message.text}, sequenceId: ${message.sequenceId}`);
        
        // 执行工具
        const processId = this._toolProcessor.executeTool(
          message.toolName,
          message.text,
          message.sequenceId,
          (response: ToolResponse) => {
            // 转发响应到Webview
            void webview.postMessage({
              command: 'toolResponse',
              response: response,
              sequenceId: message.sequenceId
            });
          },
          (error: Error) => {
            // 处理执行错误
            Logger.error(`Tool execution error: ${error.message}`);
            void webview.postMessage({
              command: 'toolError',
              error: error.message,
              sequenceId: message.sequenceId
            });
          },
          () => {
            // 执行完成回调
            Logger.debug(`Tool execution completed: ${message.toolName}, sequenceId: ${message.sequenceId}`);
            if (message.sequenceId) {
              this._activeProcesses.delete(message.sequenceId);
            }
          }
        );
        
        // 记录活跃进程
        if (processId && message.sequenceId) {
          this._activeProcesses.set(message.sequenceId, processId);
        }
        
        return;
      }
      
      case 'cancelExecution': {
        // 取消工具执行
        if (message.sequenceId) {
          const processId = this._activeProcesses.get(message.sequenceId);
          if (processId) {
            Logger.debug(`Cancelling execution for sequenceId: ${message.sequenceId}`);
            this._toolProcessor.cancelExecution(processId);
            this._activeProcesses.delete(message.sequenceId);
            void webview.postMessage({
              command: 'executionCancelled',
              sequenceId: message.sequenceId
            });
          }
        }
        return;
      }
      
      case 'getActiveProcesses': {
        // 获取活跃进程数量
        const count = this._toolProcessor.getActiveProcessCount();
        void webview.postMessage({
          command: 'activeProcessesCount',
          count: count
        });
        return;
      }
    }
  }
}

/**
 * 插件激活时执行
 * @param context VSCode扩展上下文
 */
export function activate(context: vscode.ExtensionContext): void {
  Logger.info('Interactive Tool extension activated');

  // 初始化ToolProcessor单例
  const toolsDir = path.join(context.extensionPath, 'tools');
  ToolProcessor.getInstance({
    toolsDir: toolsDir
  });

  // 创建TerminalManager实例
  const terminalManager = new TerminalManager();

  // 创建视图提供程序实例
  const viewProvider = new InteractiveToolViewProvider(context);

  // 注册视图提供程序
  const viewRegistration = vscode.window.registerWebviewViewProvider(
    InteractiveToolViewProvider.viewType,
    viewProvider,
    {
      webviewOptions: {
        retainContextWhenHidden: true
      }
    }
  );

  // 注册显示Webview的命令
  const showWebviewCommand = vscode.commands.registerCommand('interactive-tool.showWebview', () => {
    try {
      // 激活活动栏中的视图
      void vscode.commands.executeCommand('workbench.view.extension.interactive-tool-explorer');
      Logger.debug('Executed showWebview command');
    } catch (error) {
      Logger.error('Failed to show webview:', error);
      // 拆分长消息行，确保不超过120个字符
      const errorMessage = 'Failed to show interactive tool: ' +
        (error instanceof Error ? error.message : 'Unknown error');
      void vscode.window.showErrorMessage(errorMessage);
    }
  });

  // 注册执行终端命令的命令
  const executeCommandInTerminal = vscode.commands.registerCommand(
    'interactive-tool.executeCommand',
    async (command?: string) => {
      try {
        const terminalName = 'Interactive Tool Terminal';

        // 如果没有提供命令，则让用户输入
        const commandToExecute = command || await vscode.window.showInputBox({
          prompt: 'Enter command to execute:',
          placeHolder: 'e.g. echo "Hello World"'
        });

        if (!commandToExecute) {
          return; // 用户取消了输入
        }

        Logger.debug(`Executing command: ${commandToExecute}`);

        // 显示进度通知
        const progressOptions = {
          location: vscode.ProgressLocation.Notification,
          title: 'Executing Command',
          cancellable: true
        };

        // 处理进度通知
        void vscode.window.withProgress(progressOptions, async (progress) => {
          progress.report({ message: `Running: ${commandToExecute}` });

          // 执行命令
          try {
            const result = await terminalManager.executeCommand(terminalName, commandToExecute);

            // 显示结果
            void vscode.window.showInformationMessage('Command executed successfully');

            // 可以选择在输出面板中显示详细结果
            const outputChannel = vscode.window.createOutputChannel('Interactive Tool');
            void outputChannel.appendLine(`Command: ${commandToExecute}`);
            void outputChannel.appendLine('--- Output ---');
            void outputChannel.appendLine(result);
            void outputChannel.appendLine('--- End of Output ---');
            void outputChannel.show();

            Logger.debug('Command execution completed successfully');
          } catch (error) {
            Logger.error('Command execution failed:', error);
            const execErrorMsg = 'Failed to execute command: ' +
            (error instanceof Error ? error.message : 'Unknown error');
            void vscode.window.showErrorMessage(execErrorMsg);
          }
        });
      } catch (error) {
        Logger.error('Failed to execute command:', error);
        const topExecErrorMsg = 'Failed to execute command: ' +
        (error instanceof Error ? error.message : 'Unknown error');
        void vscode.window.showErrorMessage(topExecErrorMsg);
      }
    });

  // 注册清理终端的命令
  const clearTerminalsCommand = vscode.commands.registerCommand('interactive-tool.clearTerminals', () => {
    try {
      terminalManager.disposeAllTerminals();
      Logger.debug('Cleared all terminals');
      void vscode.window.showInformationMessage('All terminals cleared');
    } catch (error) {
      Logger.error('Failed to clear terminals:', error);
      const clearErrorMsg = 'Failed to clear terminals: ' +
        (error instanceof Error ? error.message : 'Unknown error');
      void vscode.window.showErrorMessage(clearErrorMsg);
    }
  });

  // 将命令添加到上下文中，以便在插件停用时自动释放
  context.subscriptions.push(
    showWebviewCommand,
    executeCommandInTerminal,
    clearTerminalsCommand,
    viewRegistration,
    // 添加清理逻辑
    {
      dispose: () => {
        terminalManager.disposeAllTerminals();
        Logger.info('Interactive Tool extension resources disposed');
      }
    }
  );
}

/**
 * 插件停用时执行
 */
export function deactivate(): void {
  Logger.info('Interactive Tool extension deactivated');
}