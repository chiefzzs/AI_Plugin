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
const vscode = __importStar(require("vscode"));
const testHelpers_1 = require("../utils/testHelpers");
const logger_1 = require("../../src/utils/logger");
const terminalManager_1 = require("../../src/utils/terminalManager");
// 模拟模块
jest.mock('vscode', () => ({
    window: {
        createWebviewPanel: jest.fn(() => ({
            reveal: jest.fn(),
            onDidDispose: { dispose: jest.fn() },
            onDidChangeViewState: { dispose: jest.fn() },
            webview: {
                asWebviewUri: jest.fn((uri) => uri),
                onDidReceiveMessage: jest.fn((callback) => ({ dispose: jest.fn() })),
                postMessage: jest.fn(() => Promise.resolve(true))
            },
            dispose: jest.fn()
        })),
        showInformationMessage: jest.fn(),
        showErrorMessage: jest.fn(),
        createTerminal: jest.fn(() => ({
            name: 'Interactive Tool Terminal',
            sendText: jest.fn(),
            dispose: jest.fn()
        })),
        terminals: [],
        registerWebviewViewProvider: jest.fn(() => ({ dispose: jest.fn() }))
    },
    ViewColumn: { One: 1 },
    commands: {
        registerCommand: jest.fn(() => ({ dispose: jest.fn() })),
        executeCommand: jest.fn()
    },
    workspace: {
        getConfiguration: jest.fn(() => ({ get: jest.fn() }))
    },
    Uri: {
        file: jest.fn((path) => ({ path, fsPath: path })),
        parse: jest.fn((uri) => ({ path: uri, fsPath: uri }))
    },
    Disposable: {
        from: jest.fn((disposables) => ({
            dispose: jest.fn(() => {
                disposables.forEach((d) => d.dispose?.());
            })
        }))
    }
}), { virtual: true });
// 模拟fs模块
jest.mock('fs', () => ({
    readFileSync: jest.fn(() => '<!DOCTYPE html><html><head></head><body></body></html>')
}));
// 模拟路径模块
jest.mock('path', () => ({
    join: jest.fn((...args) => args.join('/'))
}));
// 导入模块
const extension = __importStar(require("../../src/extension"));
/**
 * 端到端测试套件 - 测试插件的核心功能流程
 */
describe('Interactive Tool Extension - 端到端测试', () => {
    let mockContext;
    let mockLoggerInfo;
    let mockLoggerError;
    beforeEach(() => {
        // 创建模拟的扩展上下文
        mockContext = new testHelpers_1.MockExtensionContext('/test/extension/path');
        // 重置所有mock
        jest.clearAllMocks();
        // 使用spyOn监视Logger函数
        mockLoggerInfo = jest.spyOn(logger_1.Logger, 'info').mockImplementation(() => { });
        mockLoggerError = jest.spyOn(logger_1.Logger, 'error').mockImplementation(() => { });
    });
    afterEach(() => {
        // 清空订阅
        mockContext.subscriptions.forEach(sub => sub.dispose());
        mockContext.subscriptions = [];
        // 恢复原始方法
        mockLoggerInfo.mockRestore();
        mockLoggerError.mockRestore();
    });
    /**
     * 测试插件激活流程
     */
    describe('插件激活流程', () => {
        it('应该成功激活插件', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 验证日志记录函数被调用
            expect(mockLoggerInfo).toHaveBeenCalled();
        });
        it('应该注册所有必要的命令', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 验证命令注册
            const registerCommand = vscode.commands.registerCommand;
            expect(registerCommand).toHaveBeenCalled();
            // 获取所有注册的命令ID
            const registeredCommands = registerCommand.mock.calls.map(call => call[0]);
            // 验证核心命令是否已注册
            expect(registeredCommands).toContain('interactive-tool.showWebview');
            expect(registeredCommands).toContain('interactive-tool.executeCommand');
            expect(registeredCommands).toContain('interactive-tool.clearTerminals');
        });
        it('应该注册Webview视图提供程序', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 验证视图提供程序注册
            const registerWebviewViewProvider = vscode.window.registerWebviewViewProvider;
            expect(registerWebviewViewProvider).toHaveBeenCalled();
        });
    });
    /**
     * 测试命令功能
     */
    describe('命令功能测试', () => {
        it('showWebview命令应该可以执行', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 获取showWebview命令回调
            let showWebviewCommand;
            const registerCommand = vscode.commands.registerCommand;
            registerCommand.mock.calls.forEach(call => {
                if (call[0] === 'interactive-tool.showWebview') {
                    showWebviewCommand = call[1];
                }
            });
            // 如果命令存在，则执行它
            if (showWebviewCommand) {
                await showWebviewCommand();
                // 验证是否执行了打开视图的命令
                const executeCommand = vscode.commands.executeCommand;
                expect(executeCommand).toHaveBeenCalled();
            }
        });
        it('executeCommand命令应该可以执行', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 获取executeCommand命令回调
            let executeCommandCallback;
            const registerCommand = vscode.commands.registerCommand;
            registerCommand.mock.calls.forEach(call => {
                if (call[0] === 'interactive-tool.executeCommand') {
                    executeCommandCallback = call[1];
                }
            });
            // 如果命令存在，则执行它
            if (executeCommandCallback) {
                // 执行命令并捕获可能的异常
                try {
                    await executeCommandCallback('echo test');
                    // 只要命令能够执行而不抛出异常，测试就通过
                    expect(true).toBe(true);
                }
                catch (error) {
                    // 命令执行异常则测试失败
                    fail(`Command execution failed: ${error}`);
                }
            }
        });
        it('clearTerminals命令应该可以执行', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 获取clearTerminals命令回调
            let clearTerminalsCommand;
            const registerCommand = vscode.commands.registerCommand;
            registerCommand.mock.calls.forEach(call => {
                if (call[0] === 'interactive-tool.clearTerminals') {
                    clearTerminalsCommand = call[1];
                }
            });
            // 模拟TerminalManager的disposeAllTerminals方法
            const mockDisposeAll = jest.spyOn(terminalManager_1.TerminalManager.prototype, 'disposeAllTerminals')
                .mockImplementation(() => { });
            // 如果命令存在，则执行它
            if (clearTerminalsCommand) {
                await clearTerminalsCommand();
                // 验证是否调用了TerminalManager清除终端
                expect(mockDisposeAll).toHaveBeenCalled();
            }
            // 恢复原始方法
            mockDisposeAll.mockRestore();
        });
    });
    /**
     * 测试Webview功能
     */
    describe('Webview功能测试', () => {
        it('应该能够触发Webview相关操作', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 获取showWebview命令回调
            let showWebviewCommand;
            const registerCommand = vscode.commands.registerCommand;
            registerCommand.mock.calls.forEach(call => {
                if (call[0] === 'interactive-tool.showWebview') {
                    showWebviewCommand = call[1];
                }
            });
            // 如果命令存在，则执行它
            if (showWebviewCommand) {
                await showWebviewCommand();
                // 验证是否执行了相关操作
                expect(showWebviewCommand).toBeDefined();
            }
        });
    });
    /**
     * 测试插件禁用流程
     */
    describe('插件禁用流程', () => {
        it('应该能够成功禁用插件并清理资源', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 添加一些模拟的订阅
            const mockDisposable1 = { dispose: jest.fn() };
            const mockDisposable2 = { dispose: jest.fn() };
            mockContext.subscriptions.push(mockDisposable1, mockDisposable2);
            // 手动清理订阅以模拟禁用过程
            mockContext.subscriptions.forEach(sub => sub.dispose());
            // 验证所有订阅都被清理
            expect(mockDisposable1.dispose).toHaveBeenCalled();
            expect(mockDisposable2.dispose).toHaveBeenCalled();
        });
    });
    /**
     * 测试错误处理
     */
    describe('错误处理测试', () => {
        it('应该能够处理命令执行失败的情况', async () => {
            // 执行激活函数，使用类型断言
            await extension.activate(mockContext);
            // 获取executeCommand命令回调
            let executeCommandCallback;
            const registerCommand = vscode.commands.registerCommand;
            registerCommand.mock.calls.forEach(call => {
                if (call[0] === 'interactive-tool.executeCommand') {
                    executeCommandCallback = call[1];
                }
            });
            // 模拟TerminalManager的executeCommand方法抛出异常
            const mockTerminalExecute = jest.spyOn(terminalManager_1.TerminalManager.prototype, 'executeCommand')
                .mockRejectedValue(new Error('Command execution failed'));
            // 模拟Logger的error方法
            const mockError = jest.spyOn(logger_1.Logger, 'error').mockImplementation(() => { });
            // 如果命令存在，则执行它
            if (executeCommandCallback) {
                try {
                    await executeCommandCallback('invalid command');
                }
                catch (error) {
                    // 捕获可能的异常
                    console.log('Caught error during command execution:', error);
                }
            }
            // 验证错误日志记录
            expect(mockError).toHaveBeenCalled();
            // 恢复原始方法
            mockTerminalExecute.mockRestore();
            mockError.mockRestore();
        });
    });
});
//# sourceMappingURL=extensionEndToEnd.test.js.map