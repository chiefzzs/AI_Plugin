"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// terminalManager.test.ts
/**
 * TerminalManager类的单元测试
 */
const terminalManager_1 = require("../../src/utils/terminalManager");
// 模拟的终端类
class MockTerminal {
    constructor(name) {
        this.disposed = false;
        this.processId = Promise.resolve(123);
        this.exitStatus = undefined;
        this.name = name;
    }
    show(preserveFocus) {
        // 模拟show方法
    }
    hide() {
        // 模拟hide方法
    }
    sendText(text, addNewLine) {
        // 模拟sendText方法
    }
    dispose() {
        // 模拟dispose方法
        this.disposed = true;
    }
    // 用于测试的额外属性
    isDisposed() {
        return this.disposed;
    }
}
describe('TerminalManager', () => {
    let terminalManager;
    let mockTerminals;
    let mockTerminalDataListeners;
    beforeEach(() => {
        jest.clearAllMocks();
        terminalManager = new terminalManager_1.TerminalManager();
        mockTerminals = new Map();
        mockTerminalDataListeners = [];
        // 模拟vscode.window.createTerminal
        jest.spyOn(vscode.window, 'createTerminal').mockImplementation((options) => {
            const terminal = new MockTerminal(options.name);
            mockTerminals.set(options.name, terminal);
            return terminal;
        });
    });
    describe('createTerminal方法', () => {
        it('应该创建新的终端', () => {
            const terminalName = 'test-terminal';
            const terminal = terminalManager.createTerminal(terminalName);
            expect(terminal).toBeDefined();
            expect(terminal.name).toBe(terminalName);
            expect(vscode.window.createTerminal).toHaveBeenCalledWith({
                name: terminalName,
                isTransient: false
            });
        });
        it('应该复用已存在的终端', () => {
            const terminalName = 'test-terminal';
            const terminal1 = terminalManager.createTerminal(terminalName);
            const terminal2 = terminalManager.createTerminal(terminalName);
            expect(vscode.window.createTerminal).toHaveBeenCalledTimes(1);
        });
    });
    describe('executeCommand方法', () => {
        it('应该在指定终端执行命令', async () => {
            const terminalName = 'test-terminal';
            const command = 'echo "Hello World"';
            // 创建终端并获取其sendText方法的spy
            const terminal = terminalManager.createTerminal(terminalName);
            const sendTextSpy = jest.spyOn(terminal, 'sendText');
            const showSpy = jest.spyOn(terminal, 'show');
            // 执行命令
            const promise = terminalManager.executeCommand(terminalName, command);
            // 验证方法调用
            expect(showSpy).toHaveBeenCalled();
            expect(sendTextSpy).toHaveBeenCalledWith(command);
            // 等待命令执行完成（模拟的setTimeout是1秒，不是5秒）
            const result = await promise;
            // 验证结果
            expect(result).toContain(command);
        }, 2000); // 超时时间设置为2秒，因为实际代码中的setTimeout是1秒
        it('应该在1秒后自动完成命令执行', async () => {
            const terminalName = 'test-terminal';
            const command = 'sleep 10'; // 模拟长时间运行的命令
            // 记录开始时间
            const startTime = Date.now();
            // 执行命令
            const result = await terminalManager.executeCommand(terminalName, command);
            // 记录结束时间
            const endTime = Date.now();
            // 验证命令在1秒左右完成
            const executionTime = endTime - startTime;
            expect(executionTime).toBeGreaterThanOrEqual(900);
            expect(executionTime).toBeLessThanOrEqual(1100);
        }, 2000); // 超时时间设置为2秒
    });
    describe('disposeTerminal方法', () => {
        it('应该销毁指定的终端', () => {
            const terminalName = 'test-terminal';
            const terminal = terminalManager.createTerminal(terminalName);
            terminalManager.disposeTerminal(terminalName);
            // 验证终端已被销毁
            expect(terminal.isDisposed()).toBe(true);
        });
        it('销毁不存在的终端不应该抛出异常', () => {
            const nonExistentTerminal = 'non-existent-terminal';
            // 应该不会抛出异常
            expect(() => {
                terminalManager.disposeTerminal(nonExistentTerminal);
            }).not.toThrow();
        });
    });
    describe('getAllTerminalNames方法', () => {
        it('应该返回所有已创建的终端名称', () => {
            const terminalNames = ['terminal1', 'terminal2', 'terminal3'];
            // 创建多个终端
            terminalNames.forEach(name => terminalManager.createTerminal(name));
            // 获取所有终端名称
            const allTerminalNames = terminalManager.getAllTerminalNames();
            // 验证结果
            expect(allTerminalNames).toHaveLength(terminalNames.length);
            terminalNames.forEach(name => {
                expect(allTerminalNames).toContain(name);
            });
        });
        it('应该返回空数组当没有创建终端时', () => {
            const allTerminalNames = terminalManager.getAllTerminalNames();
            expect(allTerminalNames).toEqual([]);
        });
    });
    describe('hasTerminal方法', () => {
        it('应该返回true当终端存在时', () => {
            const terminalName = 'test-terminal';
            terminalManager.createTerminal(terminalName);
            expect(terminalManager.hasTerminal(terminalName)).toBe(true);
        });
        it('应该返回false当终端不存在时', () => {
            const nonExistentTerminal = 'non-existent-terminal';
            expect(terminalManager.hasTerminal(nonExistentTerminal)).toBe(false);
        });
    });
    describe('disposeAllTerminals方法', () => {
        it('应该销毁所有已创建的终端', () => {
            const terminalNames = ['terminal1', 'terminal2', 'terminal3'];
            const terminals = [];
            // 创建多个终端
            terminalNames.forEach(name => {
                terminals.push(terminalManager.createTerminal(name));
            });
            // 销毁所有终端
            terminalManager.disposeAllTerminals();
            // 验证所有终端都已被销毁
            terminals.forEach(terminal => {
                expect(terminal.isDisposed()).toBe(true);
            });
        });
        it('执行disposeAllTerminals后，getAllTerminalNames应该返回空数组', () => {
            const terminalNames = ['terminal1', 'terminal2', 'terminal3'];
            // 创建多个终端
            terminalNames.forEach(name => terminalManager.createTerminal(name));
            // 销毁所有终端
            terminalManager.disposeAllTerminals();
            // 验证getAllTerminalNames返回空数组
            expect(terminalManager.getAllTerminalNames()).toEqual([]);
        });
    });
});
//# sourceMappingURL=terminalManager.test.js.map