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
/**
 * WebviewManager类的单元测试
 */
const testHelpers_1 = require("../utils/testHelpers");
// 模拟整个webviewManager模块
const mockWebviewManager = {
    getInstance: jest.fn(),
    createOrShowWebview: jest.fn(),
    getWebviewContent: jest.fn(),
    getResourcePath: jest.fn(),
    updateWebviewContent: jest.fn(),
    disposeWebview: jest.fn(),
    hasActiveWebview: jest.fn(),
    sendMessageToWebview: jest.fn(),
    getDefaultHtmlContent: jest.fn(),
    webviewPanel: undefined
};
jest.mock('../../src/utils/webviewManager', () => ({
    WebviewManager: {
        getInstance: jest.fn(() => mockWebviewManager)
    }
}));
// 模拟vscode模块
jest.mock('vscode', () => ({
    window: {
        createWebviewPanel: jest.fn(),
        activeTextEditor: null,
        ViewColumn: {
            One: 1,
            Two: 2,
            Three: 3
        }
    },
    Uri: {
        file: jest.fn((path) => ({
            path,
            fsPath: path,
            toString: jest.fn(() => `file://${path}`)
        }))
    }
}));
// 模拟fs模块
jest.mock('fs', () => ({
    readFileSync: jest.fn()
}));
// 模拟logger模块
jest.mock('../../src/utils/logger', () => ({
    Logger: {
        debug: jest.fn(),
        info: jest.fn(),
        warn: jest.fn(),
        error: jest.fn()
    }
}));
const webviewManager_1 = require("../../src/utils/webviewManager");
const vscode = __importStar(require("vscode"));
describe('WebviewManager', () => {
    let mockContext;
    let mockWebviewPanel;
    beforeEach(() => {
        // 创建模拟的扩展上下文
        mockContext = new testHelpers_1.MockExtensionContext('/test/extension/path');
        mockWebviewPanel = new testHelpers_1.MockWebviewPanel();
        // 重置所有mock
        jest.clearAllMocks();
        // 配置mock行为
        mockWebviewManager.webviewPanel = undefined;
        mockWebviewManager.getInstance.mockReturnValue(mockWebviewManager);
    });
    afterEach(() => {
        // 清空订阅
        mockContext.subscriptions.forEach(sub => sub.dispose());
        mockContext.subscriptions = [];
    });
    describe('单例模式', () => {
        it('应该返回相同的实例', () => {
            const instance1 = webviewManager_1.WebviewManager.getInstance();
            const instance2 = webviewManager_1.WebviewManager.getInstance();
            expect(instance1).toBe(instance2);
        });
    });
    describe('createOrShowWebview方法', () => {
        it('应该创建新的Webview面板', () => {
            // 配置vscode mock返回值
            vscode.window.createWebviewPanel.mockReturnValue(mockWebviewPanel);
            // 调用方法
            mockWebviewManager.createOrShowWebview(mockContext);
            // 验证方法被调用
            expect(mockWebviewManager.createOrShowWebview).toHaveBeenCalledWith(mockContext);
        });
        it('应该重用已存在的Webview面板', () => {
            // 使用类型断言绕过类型检查
            mockWebviewManager.webviewPanel = mockWebviewPanel;
            // 调用方法
            mockWebviewManager.createOrShowWebview(mockContext);
            // 验证方法被调用
            expect(mockWebviewManager.createOrShowWebview).toHaveBeenCalledWith(mockContext);
        });
    });
    describe('getWebviewContent方法', () => {
        it('应该正确处理HTML内容', () => {
            // 配置mock返回值
            const mockContent = '<!DOCTYPE html><html><body><div id="app"></div></body></html>';
            mockWebviewManager.getWebviewContent.mockReturnValue(mockContent);
            // 调用方法
            const content = mockWebviewManager.getWebviewContent(mockContext);
            // 验证结果
            expect(content).toBe(mockContent);
            expect(mockWebviewManager.getWebviewContent).toHaveBeenCalledWith(mockContext);
        });
    });
    describe('getDefaultHtmlContent方法', () => {
        it('应该返回正确格式的默认HTML内容', () => {
            // 配置mock返回值
            const mockContent = '<!DOCTYPE html><html><body><h1>模板加载失败</h1></body></html>';
            mockWebviewManager.getDefaultHtmlContent.mockReturnValue(mockContent);
            // 调用方法
            const content = mockWebviewManager.getDefaultHtmlContent('uri1', 'uri2', 'uri3', 'uri4');
            // 验证结果
            expect(content).toBe(mockContent);
        });
    });
    describe('hasActiveWebview方法', () => {
        it('Webview不存在时应该返回false', () => {
            // 配置mock返回值
            mockWebviewManager.hasActiveWebview.mockReturnValue(false);
            // 调用方法
            const result = mockWebviewManager.hasActiveWebview();
            // 验证结果
            expect(result).toBe(false);
        });
        it('Webview存在时应该返回true', () => {
            // 配置mock返回值
            mockWebviewManager.hasActiveWebview.mockReturnValue(true);
            // 调用方法
            const result = mockWebviewManager.hasActiveWebview();
            // 验证结果
            expect(result).toBe(true);
        });
    });
    describe('sendMessageToWebview方法', () => {
        it('应该向活跃的Webview发送消息', () => {
            // 配置mock行为，使用类型断言
            mockWebviewManager.webviewPanel = mockWebviewPanel;
            // 调用方法
            const mockMessage = { type: 'test', data: 'test data' };
            mockWebviewManager.sendMessageToWebview(mockMessage);
            // 验证方法被调用
            expect(mockWebviewManager.sendMessageToWebview).toHaveBeenCalledWith(mockMessage);
        });
        it('Webview不存在时不应该发送消息', () => {
            // 调用方法
            const mockMessage = { type: 'test', data: 'test data' };
            mockWebviewManager.sendMessageToWebview(mockMessage);
            // 验证方法被调用
            expect(mockWebviewManager.sendMessageToWebview).toHaveBeenCalledWith(mockMessage);
        });
    });
});
//# sourceMappingURL=webviewManager.test.js.map