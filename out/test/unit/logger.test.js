"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// logger.test.ts
/**
 * Logger类的单元测试
 */
const logger_1 = require("../../src/utils/logger");
// 保存原始的console方法，用于测试后恢复
const originalConsoleLog = console.log;
const originalConsoleInfo = console.info;
const originalConsoleWarn = console.warn;
const originalConsoleError = console.error;
describe('Logger', () => {
    let consoleLogs = [];
    let consoleInfos = [];
    let consoleWarns = [];
    let consoleErrors = [];
    beforeEach(() => {
        // 清空记录
        consoleLogs = [];
        consoleInfos = [];
        consoleWarns = [];
        consoleErrors = [];
        // 模拟console方法
        console.log = (...args) => consoleLogs.push(args);
        console.info = (...args) => consoleInfos.push(args);
        console.warn = (...args) => consoleWarns.push(args);
        console.error = (...args) => consoleErrors.push(args);
    });
    afterEach(() => {
        // 恢复原始console方法
        console.log = originalConsoleLog;
        console.info = originalConsoleInfo;
        console.warn = originalConsoleWarn;
        console.error = originalConsoleError;
    });
    describe('debug方法', () => {
        it('应该调用console.log并正确格式化消息', () => {
            const message = 'Test debug message';
            logger_1.Logger.debug(message);
            expect(consoleLogs.length).toBe(1);
            expect(consoleLogs[0][0]).toMatch(/\[.*\] \[DEBUG\] Test debug message/);
        });
        it('应该支持附加数据参数', () => {
            const message = 'Test with data';
            const data = { key: 'value' };
            logger_1.Logger.debug(message, data);
            expect(consoleLogs.length).toBe(1);
            expect(consoleLogs[0][0]).toMatch(/\[.*\] \[DEBUG\] Test with data/);
            expect(consoleLogs[0][1]).toEqual(data);
        });
    });
    describe('info方法', () => {
        it('应该调用console.info并正确格式化消息', () => {
            const message = 'Test info message';
            logger_1.Logger.info(message);
            expect(consoleInfos.length).toBe(1);
            expect(consoleInfos[0][0]).toMatch(/\[.*\] \[INFO\] Test info message/);
        });
        it('应该支持附加数据参数', () => {
            const message = 'Info with data';
            const data = { key: 'info_value' };
            logger_1.Logger.info(message, data);
            expect(consoleInfos.length).toBe(1);
            expect(consoleInfos[0][1]).toEqual(data);
        });
    });
    describe('warn方法', () => {
        it('应该调用console.warn并正确格式化消息', () => {
            const message = 'Test warning message';
            logger_1.Logger.warn(message);
            expect(consoleWarns.length).toBe(1);
            expect(consoleWarns[0][0]).toMatch(/\[.*\] \[WARN\] Test warning message/);
        });
        it('应该支持附加数据参数', () => {
            const message = 'Warning with data';
            const data = { warning: 'true' };
            logger_1.Logger.warn(message, data);
            expect(consoleWarns.length).toBe(1);
            expect(consoleWarns[0][1]).toEqual(data);
        });
    });
    describe('error方法', () => {
        it('应该调用console.error并正确格式化消息', () => {
            const message = 'Test error message';
            logger_1.Logger.error(message);
            expect(consoleErrors.length).toBe(1);
            expect(consoleErrors[0][0]).toMatch(/\[.*\] \[ERROR\] Test error message/);
        });
        it('应该支持附加数据参数', () => {
            const message = 'Error with data';
            const data = { error: 'true', code: 500 };
            logger_1.Logger.error(message, data);
            expect(consoleErrors.length).toBe(1);
            expect(consoleErrors[0][1]).toEqual(data);
        });
    });
    describe('多级别日志同时调用', () => {
        it('应该正确处理不同级别的日志调用', () => {
            logger_1.Logger.debug('Debug message');
            logger_1.Logger.info('Info message');
            logger_1.Logger.warn('Warning message');
            logger_1.Logger.error('Error message');
            expect(consoleLogs.length).toBe(1);
            expect(consoleInfos.length).toBe(1);
            expect(consoleWarns.length).toBe(1);
            expect(consoleErrors.length).toBe(1);
        });
    });
});
//# sourceMappingURL=logger.test.js.map