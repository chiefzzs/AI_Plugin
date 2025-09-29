// terminalManager.ts
/**
 * 终端管理器类，负责创建、复用和销毁VSCode终端，以及执行命令
 */
import * as vscode from 'vscode';
import { Logger } from './logger';

export class TerminalManager {
  private terminals: Map<string, vscode.Terminal> = new Map();

  /**
   * 创建或复用终端
   * @param name 终端名称
   * @returns 创建或复用的终端实例
   */
  public createTerminal(name: string): vscode.Terminal {
    let terminal = this.terminals.get(name);

    if (!terminal) {
      terminal = vscode.window.createTerminal({
        name: name,
        isTransient: false
      });
      this.terminals.set(name, terminal);
      Logger.debug(`Created new terminal: ${name}`);
    } else {
      Logger.debug(`Reusing existing terminal: ${name}`);
    }

    return terminal;
  }

  /**
   * 在指定终端执行命令
   * @param terminalName 终端名称
   * @param command 要执行的命令
   * @returns Promise<void>，表示命令已发送
   */
  public async executeCommand(terminalName: string, command: string): Promise<string> {
    const terminal = this.createTerminal(terminalName);

    Logger.debug(`Executing command in terminal ${terminalName}: ${command}`);

    terminal.show();
    void terminal.sendText(command);

    // 在实际应用中，VSCode终端的输出捕获较为复杂
    // 这里简化处理，返回命令已执行的确认信息
    // 注意：在实际项目中，您可能需要使用任务或其他方式来获取命令执行结果
    return new Promise((resolve) => {
      setTimeout(() => {
        Logger.debug(`Command execution completed in terminal ${terminalName}`);
        resolve(`Command executed: ${command}`);
      }, 1000);
    });
  }

  /**
   * 销毁指定的终端
   * @param name 终端名称
   */
  public disposeTerminal(name: string): void {
    const terminal = this.terminals.get(name);
    if (terminal) {
      terminal.dispose();
      this.terminals.delete(name);
      Logger.debug(`Disposed terminal: ${name}`);
    } else {
      Logger.warn(`Terminal not found: ${name}`);
    }
  }

  /**
   * 获取所有已创建的终端名称
   * @returns 终端名称数组
   */
  public getAllTerminalNames(): string[] {
    return Array.from(this.terminals.keys());
  }

  /**
   * 检查终端是否存在
   * @param name 终端名称
   * @returns 终端是否存在
   */
  public hasTerminal(name: string): boolean {
    return this.terminals.has(name);
  }

  /**
   * 清空所有终端
   */
  public disposeAllTerminals(): void {
    for (const terminal of this.terminals.values()) {
      terminal.dispose();
    }
    this.terminals.clear();
    Logger.debug('Disposed all terminals');
  }
}