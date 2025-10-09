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
exports.MockWebviewPanel = exports.MockWebview = exports.MockMemento = exports.MockExtensionContext = exports.TestHelpers = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const globals_1 = require("@jest/globals");
/**
 * 测试辅助工具类，提供HTML模板测试和其他测试场景的通用辅助函数
 */
class TestHelpers {
    /**
     * 读取HTML模板文件
     * @param templatePath 模板文件路径
     * @returns 模板文件内容
     */
    static readHtmlTemplate(templatePath) {
        try {
            return fs.readFileSync(templatePath, 'utf8');
        }
        catch (error) {
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
    static renderHtmlTemplate(templateContent, placeholders) {
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
    static validateHtmlStructure(htmlContent) {
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
    static hasRequiredPlaceholders(htmlContent, requiredPlaceholders) {
        return requiredPlaceholders.every(placeholder => htmlContent.includes(`{{${placeholder}}}`) ||
            htmlContent.includes(`{{ ${placeholder} }}`) ||
            htmlContent.includes(`{{\s*${placeholder}\s*}}`));
    }
    /**
     * 创建模拟的VSCode ExtensionContext
     * @param extensionPath 扩展路径
     * @returns 模拟的ExtensionContext
     */
    static createMockExtensionContext(extensionPath = __dirname) {
        return new MockExtensionContext(extensionPath);
    }
    /**
     * 创建模拟的Webview
     * @returns 模拟的Webview
     */
    static createMockWebview() {
        return new MockWebview();
    }
    /**
     * 模拟模板文件加载失败
     * @returns 恢复函数
     */
    static mockTemplateLoadingFailure() {
        // 保存原始的fs.readFileSync方法
        const originalReadFileSync = fs.readFileSync;
        // 模拟读取失败
        const mockReadFileSync = globals_1.jest.spyOn(fs, 'readFileSync').mockImplementation(() => {
            throw new Error('File not found');
        });
        // 返回恢复函数
        return () => {
            mockReadFileSync.mockRestore();
        };
    }
    /**
     * 获取测试用的资源路径占位符映射
     * @returns 占位符映射
     */
    static getTestPlaceholders() {
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
    static checkHtmlSecurity(htmlContent) {
        // 检查是否使用https协议引用外部资源
        const hasHttpReferences = /http:\/\//i.test(htmlContent);
        const hasHttpsReferences = /https:\/\//i.test(htmlContent);
        const usesHttpsForExternalResources = hasHttpsReferences && !hasHttpReferences;
        // 检查是否有有效的CSP策略
        const hasValidCsp = /<meta\s+http-equiv="Content-Security-Policy"/i.test(htmlContent);
        // 检查是否使用了Webview URI
        const usesWebviewUri = /vscode-webview:\/\//i.test(htmlContent);
        return {
            usesHttpsForExternalResources,
            hasValidCsp,
            usesWebviewUri
        };
    }
}
exports.TestHelpers = TestHelpers;
/**
 * 模拟的VSCode ExtensionContext类
 */
class MockExtensionContext {
    constructor(extensionPath) {
        this.subscriptions = [];
        this.storagePath = undefined;
        this.workspaceState = new MockMemento();
        this.globalState = new MockMemento();
        // 使用any类型简化测试
        this.secrets = {
            get: globals_1.jest.fn(),
            store: globals_1.jest.fn(),
            delete: globals_1.jest.fn()
        };
        this.environmentVariableCollection = {
            replace: globals_1.jest.fn(),
            append: globals_1.jest.fn(),
            prepend: globals_1.jest.fn(),
            get: globals_1.jest.fn().mockReturnValue(undefined),
            delete: globals_1.jest.fn(),
            clear: globals_1.jest.fn(),
            getScoped: globals_1.jest.fn().mockReturnValue({})
        };
        this.storageUri = undefined;
        this.extensionMode = vscode.ExtensionMode.Test;
        this.logPath = '';
        this.asExternalUri = globals_1.jest.fn(async (uri) => vscode.Uri.parse('https://example.com'));
        this.extensionPath = extensionPath;
        this.globalStoragePath = path.join(extensionPath, 'globalStorage');
        this.extensionUri = vscode.Uri.file(this.extensionPath);
        this.globalStorageUri = vscode.Uri.file(this.globalStoragePath);
    }
    asAbsolutePath(relativePath) {
        return path.join(this.extensionPath, relativePath);
    }
}
exports.MockExtensionContext = MockExtensionContext;
/**
 * 模拟的Memento类
 */
class MockMemento {
    constructor() {
        this.data = {};
        this.syncKeys = [];
    }
    get(key, defaultValue) {
        return this.data[key] ?? defaultValue;
    }
    update(key, value) {
        this.data[key] = value;
        return Promise.resolve();
    }
    keys() {
        return Object.keys(this.data);
    }
    setKeysForSync(keys) {
        this.syncKeys = [...keys];
    }
}
exports.MockMemento = MockMemento;
/**
 * 模拟的Webview类
 */
class MockWebview {
    asWebviewUri(localResource) {
        // 模拟asWebviewUri方法，将本地路径转换为VSCode Webview URI格式
        return vscode.Uri.parse(`vscode-webview://mock-extension-id${localResource.path}`);
    }
    onDidReceiveMessage(callback, thisArg, disposables) {
        return { dispose: () => { } };
    }
    postMessage(message) {
        return Promise.resolve(true);
    }
}
exports.MockWebview = MockWebview;
/**
 * 模拟的WebviewPanel类
 */
class MockWebviewPanel {
    constructor() {
        this.disposables = [];
        this.webview = new MockWebview();
    }
    reveal(column, preserveFocus) {
        // 模拟reveal方法
    }
    onDidDispose(callback, thisArg, disposables) {
        // 模拟onDidDispose方法
        const disposable = { dispose: () => { } };
        if (disposables) {
            disposables.push(disposable);
        }
        else {
            this.disposables.push(disposable);
        }
        return disposable;
    }
    dispose() {
        // 模拟dispose方法
        for (const disposable of this.disposables) {
            disposable.dispose();
        }
        this.disposables = [];
    }
}
exports.MockWebviewPanel = MockWebviewPanel;
//# sourceMappingURL=testHelpers.js.map