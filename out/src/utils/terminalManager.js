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
exports.TerminalManager = void 0;
// terminalManager.ts
/**
 * 终端管理器类，负责创建、复用和销毁VSCode终端，以及执行命令
 */
const vscode = __importStar(require("vscode"));
const logger_1 = require("./logger");
class TerminalManager {
    constructor() {
        this.terminals = new Map();
    }
    /**
     * 创建或复用终端
     * @param name 终端名称
     * @returns 创建或复用的终端实例
     */
    createTerminal(name) {
        let terminal = this.terminals.get(name);
        if (!terminal) {
            terminal = vscode.window.createTerminal({
                name: name,
                isTransient: false
            });
            this.terminals.set(name, terminal);
            logger_1.Logger.debug(`Created new terminal: ${name}`);
        }
        else {
            logger_1.Logger.debug(`Reusing existing terminal: ${name}`);
        }
        return terminal;
    }
    /**
     * 在指定终端执行命令
     * @param terminalName 终端名称
     * @param command 要执行的命令
     * @returns Promise<void>，表示命令已发送
     */
    async executeCommand(terminalName, command) {
        const terminal = this.createTerminal(terminalName);
        logger_1.Logger.debug(`Executing command in terminal ${terminalName}: ${command}`);
        terminal.show();
        void terminal.sendText(command);
        // 在实际应用中，VSCode终端的输出捕获较为复杂
        // 这里简化处理，返回命令已执行的确认信息
        // 注意：在实际项目中，您可能需要使用任务或其他方式来获取命令执行结果
        return new Promise((resolve) => {
            setTimeout(() => {
                logger_1.Logger.debug(`Command execution completed in terminal ${terminalName}`);
                resolve(`Command executed: ${command}`);
            }, 1000);
        });
    }
    /**
     * 销毁指定的终端
     * @param name 终端名称
     */
    disposeTerminal(name) {
        const terminal = this.terminals.get(name);
        if (terminal) {
            terminal.dispose();
            this.terminals.delete(name);
            logger_1.Logger.debug(`Disposed terminal: ${name}`);
        }
        else {
            logger_1.Logger.warn(`Terminal not found: ${name}`);
        }
    }
    /**
     * 获取所有已创建的终端名称
     * @returns 终端名称数组
     */
    getAllTerminalNames() {
        return Array.from(this.terminals.keys());
    }
    /**
     * 检查终端是否存在
     * @param name 终端名称
     * @returns 终端是否存在
     */
    hasTerminal(name) {
        return this.terminals.has(name);
    }
    /**
     * 清空所有终端
     */
    disposeAllTerminals() {
        for (const terminal of this.terminals.values()) {
            terminal.dispose();
        }
        this.terminals.clear();
        logger_1.Logger.debug('Disposed all terminals');
    }
}
exports.TerminalManager = TerminalManager;
//# sourceMappingURL=terminalManager.js.map