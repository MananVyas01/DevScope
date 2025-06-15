import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const outputChannel = vscode.window.createOutputChannel('DevScope');
  outputChannel.appendLine('DevScope extension is now active!');
  outputChannel.show();

  let disposable = vscode.commands.registerCommand(
    'devscope.helloWorld',
    () => {
      vscode.window.showInformationMessage('Hello World from DevScope!');
    }
  );

  context.subscriptions.push(disposable);
}

export function deactivate() {}
