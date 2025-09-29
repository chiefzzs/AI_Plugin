module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['./test'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  testMatch: ['**/test/**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts'
  ],
  coverageDirectory: './coverage',
  verbose: true,
  transform: {
    '^.+\.tsx?$': 'ts-jest'
  },
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@test/(.*)$': '<rootDir>/test/$1',
    '^vscode$': '<rootDir>/test/mocks/vscode.js'
  },
  setupFilesAfterEnv: ['./test/setup.js'],
  globals: {
    'ts-jest': {
      isolatedModules: true
    }
  }
};