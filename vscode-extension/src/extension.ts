import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

let currentProcess: cp.ChildProcess | null = null;
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Confucius Agent');
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('confucius.runTask', runAgentTask),
        vscode.commands.registerCommand('confucius.ralphLoop', startRalphLoop),
        vscode.commands.registerCommand('confucius.searchNotes', searchNotes),
        vscode.commands.registerCommand('confucius.init', initWorkspace),
        vscode.commands.registerCommand('confucius.stopLoop', stopCurrentLoop)
    );
    
    // Show status bar item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.text = '$(hubot) Confucius';
    statusBar.command = 'confucius.runTask';
    statusBar.tooltip = 'Run Confucius AI Agent';
    statusBar.show();
    context.subscriptions.push(statusBar);
    
    outputChannel.appendLine('Confucius Agent extension activated!');
}

async function runAgentTask() {
    const task = await vscode.window.showInputBox({
        prompt: 'Enter task for the AI agent',
        placeHolder: 'e.g., Fix the failing tests in auth.py',
    });
    
    if (!task) return;
    
    const config = vscode.workspace.getConfiguration('confucius');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const model = config.get<string>('model', 'claude-sonnet-4-20250514');
    const maxIter = config.get<number>('maxIterations', 20);
    const completion = config.get<string>('completionPromise', 'TASK_COMPLETE');
    
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    
    outputChannel.show();
    outputChannel.appendLine(`\n${'='.repeat(60)}`);
    outputChannel.appendLine(`🎭 Running Confucius Agent`);
    outputChannel.appendLine(`Task: ${task}`);
    outputChannel.appendLine(`Workspace: ${workspaceFolder}`);
    outputChannel.appendLine(`${'='.repeat(60)}\n`);
    
    const args = [
        '-m', 'confucius_agent.cli', 'run',
        task,
        '-w', workspaceFolder,
        '-m', model,
        '-c', completion,
        '-i', maxIter.toString(),
        '-v'
    ];
    
    try {
        currentProcess = cp.spawn(pythonPath, args, {
            cwd: workspaceFolder,
            env: process.env
        });
        
        currentProcess.stdout?.on('data', (data) => {
            outputChannel.append(data.toString());
        });
        
        currentProcess.stderr?.on('data', (data) => {
            outputChannel.append(data.toString());
        });
        
        currentProcess.on('close', (code) => {
            if (code === 0) {
                vscode.window.showInformationMessage('✅ Confucius Agent completed successfully!');
            } else {
                vscode.window.showWarningMessage(`⚠️ Agent exited with code ${code}`);
            }
            currentProcess = null;
        });
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to run agent: ${error}`);
    }
}

async function startRalphLoop() {
    const command = await vscode.window.showInputBox({
        prompt: 'Enter command to run in loop',
        placeHolder: 'e.g., npm test',
    });
    
    if (!command) return;
    
    const completion = await vscode.window.showInputBox({
        prompt: 'Enter completion promise string',
        placeHolder: 'e.g., All tests passed',
        value: 'DONE'
    });
    
    if (!completion) return;
    
    const config = vscode.workspace.getConfiguration('confucius');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const maxIter = config.get<number>('maxIterations', 20);
    
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    
    outputChannel.show();
    outputChannel.appendLine(`\n${'='.repeat(60)}`);
    outputChannel.appendLine(`🎭 Starting Ralph Loop`);
    outputChannel.appendLine(`Command: ${command}`);
    outputChannel.appendLine(`Completion: '${completion}'`);
    outputChannel.appendLine(`${'='.repeat(60)}\n`);
    
    const args = [
        '-m', 'confucius_agent.cli', 'loop',
        command,
        '-c', completion,
        '-i', maxIter.toString(),
        '-v'
    ];
    
    try {
        currentProcess = cp.spawn(pythonPath, args, {
            cwd: workspaceFolder,
            shell: true,
            env: process.env
        });
        
        currentProcess.stdout?.on('data', (data) => {
            outputChannel.append(data.toString());
        });
        
        currentProcess.stderr?.on('data', (data) => {
            outputChannel.append(data.toString());
        });
        
        currentProcess.on('close', (code) => {
            if (code === 0) {
                vscode.window.showInformationMessage('🎉 Ralph Loop completed successfully!');
            } else {
                vscode.window.showWarningMessage(`⚠️ Loop exited with code ${code}`);
            }
            currentProcess = null;
        });
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start loop: ${error}`);
    }
}

async function searchNotes() {
    const query = await vscode.window.showInputBox({
        prompt: 'Search notes',
        placeHolder: 'e.g., auth bug fix',
    });
    
    if (!query) return;
    
    const config = vscode.workspace.getConfiguration('confucius');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    
    const args = [
        '-m', 'confucius_agent.cli', 'notes',
        '-w', workspaceFolder,
        '-q', query
    ];
    
    outputChannel.show();
    outputChannel.appendLine(`\n📝 Searching notes for: ${query}\n`);
    
    cp.exec(`${pythonPath} ${args.join(' ')}`, { cwd: workspaceFolder }, (error, stdout, stderr) => {
        if (error) {
            outputChannel.appendLine(`Error: ${error.message}`);
            return;
        }
        outputChannel.appendLine(stdout);
        if (stderr) outputChannel.appendLine(stderr);
    });
}

async function initWorkspace() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }
    
    const config = vscode.workspace.getConfiguration('confucius');
    const pythonPath = config.get<string>('pythonPath', 'python');
    
    const args = ['-m', 'confucius_agent.cli', 'init', workspaceFolder];
    
    cp.exec(`${pythonPath} ${args.join(' ')}`, (error, stdout, stderr) => {
        if (error) {
            vscode.window.showErrorMessage(`Failed to initialize: ${error.message}`);
            return;
        }
        vscode.window.showInformationMessage('✅ Confucius Agent initialized in workspace!');
        outputChannel.appendLine(stdout);
    });
}

function stopCurrentLoop() {
    if (currentProcess) {
        currentProcess.kill();
        currentProcess = null;
        vscode.window.showInformationMessage('🛑 Stopped current loop');
        outputChannel.appendLine('\n🛑 Loop stopped by user\n');
    } else {
        vscode.window.showInformationMessage('No active loop to stop');
    }
}

export function deactivate() {
    if (currentProcess) {
        currentProcess.kill();
    }
}
