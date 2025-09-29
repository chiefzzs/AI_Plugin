"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
// extension.ts
/**
 * VSCode插件的主入口文件
 */
const vscode = __importStar(require("vscode"));
const logger_1 = require("./utils/logger");
const webviewManager_1 = require("./utils/webviewManager");
const terminalManager_1 = require("./utils/terminalManager");
class InteractiveToolViewProvider {
    constructor(_context) {
        this._context = _context;
        this._webviewManager = webviewManager_1.WebviewManager.getInstance();
    }
    resolveWebviewView(webviewView, context, _token) {
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
        webviewView.webview.onDidReceiveMessage((message) => {
            switch (message.command) {
                case 'executeCommand': {
                    // 处理从Webview发送的命令
                    logger_1.Logger.debug(`Received command from webview: ${message.text || ''}`);
                    const terminalManager = new terminalManager_1.TerminalManager();
                    void terminalManager.executeCommand('Interactive Tool Terminal', message.text || '')
                        .then(result => {
                        void webviewView.webview.postMessage({
                            command: 'commandResult',
                            result: result
                        });
                    })
                        .catch(error => {
                        void webviewView.webview.postMessage({
                            command: 'commandError',
                            error: error instanceof Error ? error.message : String(error)
                        });
                    });
                    return;
                }
            }
        }, undefined, this._context.subscriptions);
    }
}
InteractiveToolViewProvider.viewType = 'interactive-tool.webview';
/**
 * 插件激活时执行
 * @param context VSCode扩展上下文
 */
function activate(context) {
    logger_1.Logger.info('Interactive Tool extension activated');
    // WebviewManager实例将在InteractiveToolViewProvider中创建
    // 创建TerminalManager实例
    const terminalManager = new terminalManager_1.TerminalManager();
    // 创建视图提供程序实例
    const viewProvider = new InteractiveToolViewProvider(context);
    // 注册视图提供程序
    const viewRegistration = vscode.window.registerWebviewViewProvider(InteractiveToolViewProvider.viewType, viewProvider, {
        webviewOptions: {
            retainContextWhenHidden: true
        }
    });
    // 注册显示Webview的命令
    const showWebviewCommand = vscode.commands.registerCommand('interactive-tool.showWebview', () => {
        try {
            // 激活活动栏中的视图
            void vscode.commands.executeCommand('workbench.view.extension.interactive-tool-explorer');
            logger_1.Logger.debug('Executed showWebview command');
        }
        catch (error) {
            logger_1.Logger.error('Failed to show webview:', error);
            // 拆分长消息行，确保不超过120个字符
            const errorMessage = 'Failed to show interactive tool: ' +
                (error instanceof Error ? error.message : 'Unknown error');
            void vscode.window.showErrorMessage(errorMessage);
        }
    });
    // 注册执行终端命令的命令
    const executeCommandInTerminal = vscode.commands.registerCommand('interactive-tool.executeCommand', async (command) => {
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
            logger_1.Logger.debug(`Executing command: ${commandToExecute}`);
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
                    logger_1.Logger.debug('Command execution completed successfully');
                }
                catch (error) {
                    logger_1.Logger.error('Command execution failed:', error);
                    const execErrorMsg = 'Failed to execute command: ' +
                        (error instanceof Error ? error.message : 'Unknown error');
                    void vscode.window.showErrorMessage(execErrorMsg);
                }
            });
        }
        catch (error) {
            logger_1.Logger.error('Failed to execute command:', error);
            const topExecErrorMsg = 'Failed to execute command: ' +
                (error instanceof Error ? error.message : 'Unknown error');
            void vscode.window.showErrorMessage(topExecErrorMsg);
        }
    });
    // 注册清理终端的命令
    const clearTerminalsCommand = vscode.commands.registerCommand('interactive-tool.clearTerminals', () => {
        try {
            terminalManager.disposeAllTerminals();
            logger_1.Logger.debug('Cleared all terminals');
            void vscode.window.showInformationMessage('All terminals cleared');
        }
        catch (error) {
            logger_1.Logger.error('Failed to clear terminals:', error);
            const clearErrorMsg = 'Failed to clear terminals: ' +
                (error instanceof Error ? error.message : 'Unknown error');
            void vscode.window.showErrorMessage(clearErrorMsg);
        }
    });
    // 将命令添加到上下文中，以便在插件停用时自动释放
    context.subscriptions.push(showWebviewCommand, executeCommandInTerminal, clearTerminalsCommand, viewRegistration, 
    // 添加清理逻辑
    {
        dispose: () => {
            terminalManager.disposeAllTerminals();
            logger_1.Logger.info('Interactive Tool extension resources disposed');
        }
    });
}
exports.activate = activate;
/**
 * 插件停用时执行
 */
function deactivate() {
    logger_1.Logger.info('Interactive Tool extension deactivated');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map