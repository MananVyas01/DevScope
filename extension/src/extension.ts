import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
	console.log('DevScope extension is now active!');

	let disposable = vscode.commands.registerCommand('devscope.helloWorld', () => {
		vscode.window.showInformationMessage('Hello World from DevScope!');
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}
