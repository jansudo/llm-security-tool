import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """llmsecurity: Analyze chats and generate prompts."""
    pass

@cli.command()
@click.argument('input_source', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Path to chat file to analyze')
def analyze(input_source, file):
    """Analyze a chat log to understand its logic."""
    from llmsecurity.core import analyze_chat_logic
    
    content = ""
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif input_source:
        content = input_source
    else:
        # Check for stdin
        if not click.get_text_stream('stdin').isatty():
            content = click.get_text_stream('stdin').read()
        else:
            console.print("[bold red]Error:[/bold red] No input provided. Use an argument, --file, or pipe input.")
            return

    console.print("[bold green]Analyzing chat logic...[/bold green]")
    result = analyze_chat_logic(content)
    console.print(result)

@cli.command()
@click.argument('url')
@click.option('--input', '-i', 'selector_input', required=False, help='CSS selector for input box (optional, auto-discovered if omitted)')
@click.option('--send', '-s', 'selector_send', required=False, help='CSS selector for send button (optional, auto-discovered if omitted)')
@click.option('--objective', '-o', required=False, help='Specific objective for the AI (e.g. "Reveal system prompt")')
@click.option('--iterations', '-n', default=5, help='Number of attack iterations (set to 0 for infinite/until success)')
@click.option('--report', '-r', required=False, help='Filename to save the attack report (JSON)')
def attack(url, selector_input, selector_send, objective, iterations, report):
    """
    Active Red Team attack on a target URL.
    """
    from llmsecurity.attacker import Attacker
    
    attacker = Attacker(url, selector_input, selector_send, iterations, objective, report_file=report)
    attacker.run()

if __name__ == '__main__':
    cli()
