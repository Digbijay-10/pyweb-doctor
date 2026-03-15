import * as vscode from 'vscode';
import fetch from 'node-fetch';

let panel: vscode.WebviewPanel | undefined;

export function activate(context: vscode.ExtensionContext) {

	const fixCmd = vscode.commands.registerCommand(
		'stacksage.fixCode',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showInformationMessage('No editor');
				return;
			}

			let selection = editor.selection;
			let text = editor.document.getText(selection);

			if (!text) {

				const fullRange = new vscode.Range(
					editor.document.positionAt(0),
					editor.document.positionAt(editor.document.getText().length)
				);

				selection = new vscode.Selection(
					fullRange.start,
					fullRange.end
				);

				text = editor.document.getText(selection);
			}

			if (!text) {
				vscode.window.showInformationMessage('No code found');
				return;
			}

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/fix",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: text
						})
					}
				);

				const data: any = await res.json();

				const reply = data.result || "";

				await editor.edit(editBuilder => {
					editBuilder.replace(selection, reply);
				});

			} catch {
				vscode.window.showErrorMessage("Backend not running");
			}

		}
	);

	context.subscriptions.push(fixCmd);



	const reverseCmd = vscode.commands.registerCommand(
		'stacksage.reverseDebug',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showInformationMessage('No editor');
				return;
			}

			const code = editor.document.getText();

			if (!code) {
				vscode.window.showInformationMessage('No code found');
				return;
			}

			const expected = await vscode.window.showInputBox({
				prompt: "Enter expected output"
			});

			if (!expected) return;

			const timeComplexity = await vscode.window.showInputBox({
				prompt: "Required time complexity"
			});

			const spaceComplexity = await vscode.window.showInputBox({
				prompt: "Required space complexity"
			});

			const optimize = await vscode.window.showInputBox({
				prompt: "Optimization goal"
			});

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/reverse",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: code,
							expected: expected,
							time: timeComplexity || "",
							space: spaceComplexity || "",
							optimize: optimize || ""
						})
					}
				);

				const data: any = await res.json();

				const fixed = data.fixed || "";
				const explanation = data.explanation || "";

				const fullRange = new vscode.Range(
					editor.document.positionAt(0),
					editor.document.positionAt(editor.document.getText().length)
				);

				await editor.edit(editBuilder => {
					editBuilder.replace(fullRange, fixed);
				});

				if (!panel) {

					panel = vscode.window.createWebviewPanel(
						'stacksagePanel',
						'StackSage',
						vscode.ViewColumn.Beside,
						{ enableScripts: true }
					);

					panel.onDidDispose(() => {
						panel = undefined;
					});
				}

				panel.webview.html = `
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body { background:#1e1e1e;color:#e0e0e0;font-family:Segoe UI;padding:12px;}
h2{color:#4fc3f7}
#content{background:#252526;padding:14px;border-radius:8px}
</style>
</head>
<body>
<h2>Explanation</h2>
<div id="content"></div>
<script>
const text = ${JSON.stringify(explanation)};
document.getElementById("content").innerHTML = marked.parse(text);
</script>
</body>
</html>
`;

			} catch {
				vscode.window.showErrorMessage("Reverse debug failed");
			}

		}
	);

	context.subscriptions.push(reverseCmd);



	const explainCmd = vscode.commands.registerCommand(
		'stacksage.showExplanation',
		async () => {

			const editor = vscode.window.activeTextEditor;

			if (!editor) return;

			const code = editor.document.getText();

			try {

				const res = await fetch(
					"http://127.0.0.1:8080/explain",
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json"
						},
						body: JSON.stringify({
							code: code,
							error: ""
						})
					}
				);

				const data: any = await res.json();

				const explanation = data.explanation || "";

				if (!panel) {

					panel = vscode.window.createWebviewPanel(
						'stacksagePanel',
						'StackSage',
						vscode.ViewColumn.Beside,
						{ enableScripts: true }
					);

				}

				panel.webview.html = `
<html>
<body style="background:#1e1e1e;color:white;padding:12px">
<pre>${explanation}</pre>
</body>
</html>
`;

			} catch {
				vscode.window.showErrorMessage("Explain failed");
			}

		}
	);

	context.subscriptions.push(explainCmd);
}

export function deactivate() {}