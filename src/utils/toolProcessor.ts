/**
 * 工具处理器类，负责与tools目录下的Python工具进行交互
 */
import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';
import { Logger } from './logger';

// 定义工具响应接口
export interface ToolResponse {
  type: 'output' | 'error' | 'complete';
  content: string;
  isError: boolean;
  isEnd: boolean;
  sequenceId: string;
}

// 定义工具处理器的配置接口
interface ToolProcessorConfig {
  toolsDir: string;
  pythonPath?: string;
}

export class ToolProcessor {
  private static instance: ToolProcessor;
  private readonly toolsDir: string;
  private readonly pythonPath: string;
  private activeProcesses: Map<string, child_process.ChildProcess> = new Map();

  /**
   * 私有构造函数，防止外部直接实例化
   */
  private constructor(config: ToolProcessorConfig) {
    this.toolsDir = config.toolsDir;
    this.pythonPath = config.pythonPath || this.findPythonPath();
  }

  /**
   * 获取ToolProcessor单例实例
   * @returns ToolProcessor实例
   */
  public static getInstance(config?: ToolProcessorConfig): ToolProcessor {
    if (!ToolProcessor.instance && config) {
      ToolProcessor.instance = new ToolProcessor(config);
    } else if (!ToolProcessor.instance) {
      throw new Error('ToolProcessor instance not initialized. Call getInstance with config first.');
    }
    return ToolProcessor.instance;
  }

  /**
   * 查找Python可执行文件路径
   * @returns Python可执行文件路径
   */
  private findPythonPath(): string {
    // 在Windows系统上查找Python
    const possiblePaths = [
      'python.exe',
      path.join(global.process.env.SystemRoot || '', 'py.exe'),
      path.join(global.process.env.ProgramFiles || '', 'Python39', 'python.exe'),
      path.join(global.process.env.ProgramFiles || '', 'Python38', 'python.exe'),
      path.join(global.process.env.ProgramFiles || '', 'Python37', 'python.exe'),
      path.join(global.process.env.USERPROFILE || '', 'AppData', 'Local', 'Programs', 'Python', 'Python39', 'python.exe'),
      path.join(global.process.env.USERPROFILE || '', 'AppData', 'Local', 'Programs', 'Python', 'Python38', 'python.exe'),
      path.join(global.process.env.USERPROFILE || '', 'AppData', 'Local', 'Programs', 'Python', 'Python37', 'python.exe')
    ];

    for (const pythonPath of possiblePaths) {
      try {
        // 尝试执行Python命令，检查版本
        const result = child_process.spawnSync(pythonPath, ['--version'], {
          stdio: 'ignore'
        });
        
        if (result.status === 0) {
          Logger.debug(`Found Python at: ${pythonPath}`);
          return pythonPath;
        }
      } catch (error) {
        // 如果执行失败，继续尝试下一个路径
        continue;
      }
    }

    // 如果找不到Python，返回默认路径
    Logger.warn('Python not found, using default path');
    return 'python.exe';
  }

  /**
   * 执行工具命令
   * @param toolName 工具名称（如 'execinfo' 或 'interactive_tool'）
   * @param command 要执行的命令
   * @param sequenceId 序列ID
   * @param onResponse 响应回调函数
   * @param onError 错误回调函数
   * @param onComplete 完成回调函数
   * @returns 进程ID，可用于取消执行
   */
  public executeTool(
    toolName: string,
    command: string,
    sequenceId: string,
    onResponse: (response: ToolResponse) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): string {
    const processId = `${toolName}-${Date.now()}`;
    
    try {
      // 构建工具文件路径
      const toolFileName = toolName.endsWith('.py') ? toolName : `${toolName}.py`;
      const toolPath = path.join(this.toolsDir, toolFileName);
      
      // 构建命令参数
      const inputData = {
        content: command,
        projectDir: vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : global.process.cwd(),
        sequenceId: sequenceId
      };
      
      const jsonInput = JSON.stringify(inputData);
      
      // 启动Python进程
      Logger.debug(`Executing tool: ${toolPath} with input: ${jsonInput}`);
      
      const pythonProcess = child_process.spawn(this.pythonPath, [toolPath, jsonInput], {
        cwd: this.toolsDir,
        env: global.process.env,
        stdio: ['ignore', 'pipe', 'pipe']
      });
      
      // 存储活跃进程
      this.activeProcesses.set(processId, pythonProcess);
      
      // 处理标准输出
      let buffer = '';
      pythonProcess.stdout.on('data', (data: Buffer) => {
        this.handleProcessOutput(data, buffer, onResponse, sequenceId);
      });
      
      // 处理错误输出
      pythonProcess.stderr.on('data', (data: Buffer) => {
        const errorMessage = data.toString('utf8').trim();
        Logger.error(`Tool error: ${errorMessage}`);
        if (onError) {
          onError(new Error(errorMessage));
        } else {
          onResponse({
            type: 'error',
            content: errorMessage,
            isError: true,
            isEnd: false,
            sequenceId: sequenceId
          });
        }
      });
      
      // 处理进程退出
      pythonProcess.on('close', (code: number) => {
        Logger.debug(`Tool process closed with code: ${code}`);
        this.activeProcesses.delete(processId);
        if (onComplete) {
          onComplete();
        }
      });
      
      pythonProcess.on('error', (error: Error) => {
        Logger.error(`Tool process error: ${error.message}`);
        this.activeProcesses.delete(processId);
        if (onError) {
          onError(error);
        }
      });
      
      return processId;
    } catch (error) {
      Logger.error(`Failed to execute tool: ${error instanceof Error ? error.message : String(error)}`);
      if (onError && error instanceof Error) {
        onError(error);
      }
      return '';
    }
  }

  /**
   * 处理进程输出
   * @param data 输出数据
   * @param buffer 缓冲区
   * @param onResponse 响应回调函数
   * @param sequenceId 序列ID
   */
  private handleProcessOutput(
    data: Buffer,
    buffer: string,
    onResponse: (response: ToolResponse) => void,
    sequenceId: string
  ): void {
    let updatedBuffer = buffer + data.toString('utf8');
    
    // 按行处理输出
    const lines = updatedBuffer.split('\n');
    
    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i].trim();
      if (line) {
        try {
          // 尝试解析JSON响应
          const response = JSON.parse(line) as ToolResponse;
          response.sequenceId = sequenceId;
          onResponse(response);
        } catch (error) {
          // 如果不是JSON格式，作为普通文本输出
          onResponse({
            type: 'output',
            content: line,
            isError: false,
            isEnd: false,
            sequenceId: sequenceId
          });
        }
      }
    }
  }

  /**
   * 取消工具执行
   * @param processId 进程ID
   */
  public cancelExecution(processId: string): void {
    const pythonProcess = this.activeProcesses.get(processId);
    if (pythonProcess) {
      Logger.debug(`Cancelling execution: ${processId}`);
      try {
        pythonProcess.kill();
      } catch (error) {
        Logger.error(`Failed to kill process: ${error instanceof Error ? error.message : String(error)}`);
      }
      this.activeProcesses.delete(processId);
    }
  }

  /**
   * 取消所有活跃的工具执行
   */
  public cancelAllExecutions(): void {
    Logger.debug('Cancelling all tool executions');
    for (const [processId, pythonProcess] of this.activeProcesses.entries()) {
      try {
        pythonProcess.kill();
      } catch (error) {
        Logger.error(`Failed to kill process ${processId}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
    this.activeProcesses.clear();
  }

  /**
   * 获取活跃进程数
   */
  public getActiveProcessCount(): number {
    return this.activeProcesses.size;
  }

  /**
   * 检查工具是否存在
   * @param toolName 工具名称
   */
  public async isToolAvailable(toolName: string): Promise<boolean> {
    try {
      const toolFileName = toolName.endsWith('.py') ? toolName : `${toolName}.py`;
      const toolPath = path.join(this.toolsDir, toolFileName);
      
      // 检查文件是否存在
      const exists = await vscode.workspace.fs.stat(vscode.Uri.file(toolPath)).then(() => true, () => false);
      return exists;
    } catch (error) {
      Logger.error(`Failed to check tool availability: ${error instanceof Error ? error.message : String(error)}`);
      return false;
    }
  }
}