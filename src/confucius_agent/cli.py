"""
Command Line Interface for Confucius Agent
Provides global CLI tools after pip install
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="confucius-agent")
def main():
    """
    🎭 Confucius Agent - AI Coding Assistant with Ralph Wiggum Loop
    
    An autonomous coding agent that iterates until task completion,
    with hierarchical memory and persistent learning through notes.
    """
    pass


@main.command()
@click.argument("task")
@click.option("--workspace", "-w", default=".", help="Workspace root directory")
@click.option("--model", "-m", default="claude-sonnet-4-20250514", help="LLM model to use")
@click.option("--completion", "-c", default="TASK_COMPLETE", help="Completion signal string")
@click.option("--max-iter", "-i", default=20, type=int, help="Maximum iterations")
@click.option("--notes/--no-notes", default=True, help="Enable/disable note-taking")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(task: str, workspace: str, model: str, completion: str, max_iter: int, notes: bool, verbose: bool):
    """
    Run the agent on a task.
    
    Example:
        confucius run "Fix the failing tests in auth.py"
    """
    from . import create_agent
    
    console.print(Panel.fit(
        f"[bold cyan]🎭 Confucius Agent[/bold cyan]\n"
        f"Task: {task}\n"
        f"Workspace: {Path(workspace).resolve()}\n"
        f"Model: {model}",
        title="Starting Agent"
    ))
    
    try:
        agent = create_agent(
            workspace=workspace,
            model=model,
            completion_promise=completion,
            max_iterations=max_iter,
            enable_notes=notes,
        )
        
        result = agent.run_ralph_loop(task)
        
        if result["success"]:
            console.print("\n[bold green]✅ Task completed successfully![/bold green]")
        else:
            console.print("\n[bold yellow]⚠️ Task did not complete[/bold yellow]")
        
        console.print(f"\nIterations: {result['ralph_iterations']}")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("command")
@click.option("--completion", "-c", default="DONE", help="Completion promise string")
@click.option("--max-iter", "-i", default=20, type=int, help="Maximum iterations")
@click.option("--delay", "-d", default=2, type=int, help="Delay between iterations (seconds)")
@click.option("--verbose", "-v", is_flag=True, help="Show command output")
def loop(command: str, completion: str, max_iter: int, delay: int, verbose: bool):
    """
    Run a command in a Ralph loop until completion.
    
    This is a simpler version that just loops a shell command,
    without the full AI agent capabilities.
    
    Example:
        confucius loop "npm test" --completion "All tests passed"
    """
    import subprocess
    import time
    
    console.print(Panel.fit(
        f"[bold cyan]🎭 Ralph Loop[/bold cyan]\n"
        f"Command: {command}\n"
        f"Completion: '{completion}'\n"
        f"Max iterations: {max_iter}",
        title="Starting Loop"
    ))
    
    iteration = 0
    completed = False
    
    while iteration < max_iter and not completed:
        iteration += 1
        console.print(f"\n[bold magenta][{iteration}/{max_iter}] Executing...[/bold magenta]")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stdout + result.stderr
            
            if verbose:
                console.print(output)
            
            if completion in output:
                completed = True
                console.print(f"\n[bold green]✅ Completion found: '{completion}'[/bold green]")
                break
            
            console.print(f"[yellow]⏳ Waiting {delay}s...[/yellow]")
            time.sleep(delay)
            
        except subprocess.TimeoutExpired:
            console.print("[red]Command timed out[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    if completed:
        console.print(f"\n[bold green]🎉 Completed after {iteration} iterations![/bold green]")
        sys.exit(0)
    else:
        console.print(f"\n[bold yellow]⚠️ Max iterations reached[/bold yellow]")
        sys.exit(1)


@main.command()
@click.option("--workspace", "-w", default=".", help="Workspace to search")
@click.option("--query", "-q", default="", help="Search query")
@click.option("--type", "-t", "note_type", default=None, help="Note type filter")
def notes(workspace: str, query: str, note_type: Optional[str]):
    """
    Search and list notes from past sessions.
    
    Example:
        confucius notes --query "auth bug"
        confucius notes --type failure
    """
    from .notes import NoteStore, NoteType
    
    notes_path = Path(workspace) / ".confucius" / "notes"
    
    if not notes_path.exists():
        console.print("[yellow]No notes found in this workspace[/yellow]")
        return
    
    store = NoteStore(notes_path)
    
    type_filter = None
    if note_type:
        try:
            type_filter = NoteType(note_type)
        except ValueError:
            console.print(f"[red]Invalid note type: {note_type}[/red]")
            return
    
    results = store.search_notes(query=query, note_type=type_filter)
    
    if not results:
        console.print("[yellow]No matching notes found[/yellow]")
        return
    
    console.print(f"\n[bold]Found {len(results)} notes:[/bold]\n")
    
    for note in results:
        console.print(Panel(
            f"[dim]{note.path}[/dim]\n\n{note.content[:200]}...",
            title=f"[cyan]{note.title}[/cyan]",
            subtitle=f"[dim]{note.note_type.value}[/dim]"
        ))


@main.command()
@click.argument("path", required=False)
def init(path: Optional[str]):
    """
    Initialize Confucius agent in a workspace.
    
    Creates .confucius directory with config and notes structure.
    
    Example:
        confucius init ./my-project
    """
    workspace = Path(path or ".").resolve()
    confucius_dir = workspace / ".confucius"
    
    # Create directory structure
    (confucius_dir / "notes").mkdir(parents=True, exist_ok=True)
    (confucius_dir / "traces").mkdir(parents=True, exist_ok=True)
    
    # Create default config
    config_content = """# Confucius Agent Configuration

[agent]
model = "claude-sonnet-4-20250514"
max_iterations = 20
completion_promise = "TASK_COMPLETE"

[notes]
enabled = true
path = ".confucius/notes"

[extensions]
bash = true
file_edit = true
file_read = true
file_search = true
planning = true
"""
    
    (confucius_dir / "config.toml").write_text(config_content)
    
    # Add to gitignore
    gitignore = workspace / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".confucius/traces" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Confucius Agent\n.confucius/traces/\n")
    
    console.print(f"[bold green]✅ Initialized Confucius agent in {workspace}[/bold green]")
    console.print(f"\nCreated:\n  {confucius_dir}/\n  ├── config.toml\n  ├── notes/\n  └── traces/")


# Standalone ralph-loop command
@click.command()
@click.argument("command")
@click.option("--completion", "-c", default="DONE", help="Completion promise")
@click.option("--max-iter", "-i", default=20, type=int, help="Max iterations")
@click.option("--delay", "-d", default=2, type=int, help="Delay seconds")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def ralph_loop(command: str, completion: str, max_iter: int, delay: int, verbose: bool):
    """
    🎭 Ralph Loop - Run command until completion promise found.
    
    Example:
        ralph-loop "npm test" --completion "All tests passed"
    """
    import subprocess
    import time
    
    print(f"🎭 Ralph Loop Starting...")
    print(f"Command: {command}")
    print(f"Completion: '{completion}'")
    print(f"Max iterations: {max_iter}")
    print("=" * 60)
    
    iteration = 0
    completed = False
    
    while iteration < max_iter and not completed:
        iteration += 1
        print(f"\n[{iteration}/{max_iter}] Executing...")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stdout + result.stderr
            
            if verbose:
                print(output)
            
            if completion in output:
                completed = True
                print(f"\n✅ Completion found: '{completion}'")
                break
            
            print(f"⏳ Waiting {delay}s...")
            time.sleep(delay)
            
        except subprocess.TimeoutExpired:
            print("⚠️ Command timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    if completed:
        print(f"🎉 Completed after {iteration} iterations!")
        sys.exit(0)
    else:
        print(f"⚠️ Max iterations ({max_iter}) reached")
        sys.exit(1)


if __name__ == "__main__":
    main()
