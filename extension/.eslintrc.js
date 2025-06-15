/* eslint-env node */
/* global module */
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module'
  },
  plugins: [
    '@typescript-eslint'
  ],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended'
  ],
  env: {
    node: true,
    es2022: true,
    commonjs: true,
    browser: false
  },
  globals: {
    NodeJS: 'readonly',
    setInterval: 'readonly',
    clearInterval: 'readonly',
    setTimeout: 'readonly',
    clearTimeout: 'readonly',
    console: 'readonly',
    require: 'readonly',
    exports: 'writable',
    module: 'writable',
    global: 'readonly'
  },
  ignorePatterns: [
    'out/',
    'node_modules/',
    '*.js.map',
    '.vscode-test/'
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
    'no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      args: 'after-used'
    }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'no-console': 'off',
    'no-undef': 'off'
  }
};
