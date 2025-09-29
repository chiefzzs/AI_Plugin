// 全局mock vscode模块
const vscodeMock = {
  window: {
    activeTextEditor: null,
    createWebviewPanel: jest.fn(),
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showWarningMessage: jest.fn(),
    createTerminal: jest.fn(),
    terminals: [],
    withProgress: jest.fn((options, callback) => {
      const progress = {
        report: jest.fn()
      };
      return Promise.resolve(callback(progress));
    }),
    onDidWriteTerminalData: jest.fn(() => ({
      dispose: jest.fn()
    }))
  },
  ViewColumn: {
    One: 1,
    Two: 2,
    Three: 3,
    Active: -1,
    Beside: -2
  },
  commands: {
    registerCommand: jest.fn(),
    executeCommand: jest.fn()
  },
  workspace: {
    getConfiguration: jest.fn(() => ({
      get: jest.fn()
    })),
    onDidChangeConfiguration: jest.fn()
  },
  Uri: {
    file: jest.fn((path) => ({
      path,
      fsPath: path,
      toString: jest.fn(() => `file://${path}`)
    })),
    parse: jest.fn((uri) => ({
      path: uri.replace(/^[a-z]+:\/\//, ''),
      fsPath: uri.replace(/^[a-z]+:\/\//, ''),
      toString: jest.fn(() => uri)
    }))
  },
  Disposable: {
    from: jest.fn((disposables) => ({
      dispose: jest.fn(() => {
        disposables.forEach(d => d.dispose?.());
      })
    }))
  }
};

// 全局mock vscode模块
jest.mock('vscode', () => vscodeMock, { virtual: true });

// 将mock暴露给全局，以便在测试中使用
global.vscode = vscodeMock;