"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = void 0;
// logger.ts
/**
 * 日志工具类，提供不同级别的日志记录功能
 */
class Logger {
    /**
     * 私有方法，用于记录日志
     * @param level 日志级别
     * @param message 日志消息
     * @param data 可选的附加数据
     */
    static log(level, message, data) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
        switch (level) {
            case 'debug':
                console.log(logMessage, data);
                break;
            case 'info':
                console.info(logMessage, data);
                break;
            case 'warn':
                console.warn(logMessage, data);
                break;
            case 'error':
                console.error(logMessage, data);
                break;
        }
    }
    /**
     * 记录调试级别的日志
     * @param message 日志消息
     * @param data 可选的附加数据
     */
    static debug(message, data) {
        this.log('debug', message, data);
    }
    /**
     * 记录信息级别的日志
     * @param message 日志消息
     * @param data 可选的附加数据
     */
    static info(message, data) {
        this.log('info', message, data);
    }
    /**
     * 记录警告级别的日志
     * @param message 日志消息
     * @param data 可选的附加数据
     */
    static warn(message, data) {
        this.log('warn', message, data);
    }
    /**
     * 记录错误级别的日志
     * @param message 日志消息
     * @param data 可选的附加数据
     */
    static error(message, data) {
        this.log('error', message, data);
    }
}
exports.Logger = Logger;
//# sourceMappingURL=logger.js.map