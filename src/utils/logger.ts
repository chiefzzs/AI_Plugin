// logger.ts
/**
 * 日志工具类，提供不同级别的日志记录功能
 */
export class Logger {
  /**
   * 私有方法，用于记录日志
   * @param level 日志级别
   * @param message 日志消息
   * @param data 可选的附加数据
   */
  private static log(level: 'debug' | 'info' | 'warn' | 'error', message: string, data?: unknown): void {
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
  public static debug(message: string, data?: unknown): void {
    this.log('debug', message, data);
  }

  /**
   * 记录信息级别的日志
   * @param message 日志消息
   * @param data 可选的附加数据
   */
  public static info(message: string, data?: unknown): void {
    this.log('info', message, data);
  }

  /**
   * 记录警告级别的日志
   * @param message 日志消息
   * @param data 可选的附加数据
   */
  public static warn(message: string, data?: unknown): void {
    this.log('warn', message, data);
  }

  /**
   * 记录错误级别的日志
   * @param message 日志消息
   * @param data 可选的附加数据
   */
  public static error(message: string, data?: unknown): void {
    this.log('error', message, data);
  }
}