from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from agent_debate.graph import build_graph

app = typer.Typer(help="Decision Support Debate — three-agent decision analysis.")
console = Console()

DEFAULT_MODEL = "gemini-3-flash-preview"

DECISION_ICONS = {
    "go": "[green]✅ GO[/green]",
    "no_go": "[red]❌ NO GO[/red]",
    "conditional_go": "[yellow]⚠️  CONDITIONAL GO[/yellow]",
}
WINNER_LABELS = {
    "pro": "[green]PRO[/green]",
    "con": "[red]CON[/red]",
    "tie": "[yellow]TIE[/yellow]",
}


@app.command("version", hidden=True)
def _version() -> None:
    """Show version."""
    from agent_debate import __version__

    typer.echo(__version__)


@app.command("debate")
def debate(
    decision: str = typer.Argument(..., help="The decision to evaluate."),
    context: str = typer.Option(
        "", "--context", "-c", help="Additional context for the decision."
    ),
    model: str = typer.Option(
        DEFAULT_MODEL, "--model", "-m", help="Gemini model ID to use."
    ),
    save_json: Optional[Path] = typer.Option(
        None, "--save-json", help="Save full result to JSON file."
    ),
) -> None:
    """Run a three-agent debate (PRO / CON / JUDGE) on a decision."""
    console.print(
        Panel(f"[bold]{decision}[/bold]", title="Decision under debate", expand=False)
    )

    with console.status("[bold cyan]Running debate…[/bold cyan]", spinner="dots"):
        try:
            graph = build_graph()
            result = graph.invoke(
                {
                    "decision": decision,
                    "context": context,
                    "model": model,
                    "pro_arguments": [],
                    "con_arguments": [],
                    "verdict": {},
                }
            )
        except Exception as exc:
            console.print(
                Panel(
                    str(exc),
                    title="Debate failed",
                    border_style="red",
                    expand=False,
                )
            )
            raise typer.Exit(code=1) from exc

    pro_args = result["pro_arguments"]
    con_args = result["con_arguments"]
    verdict = result["verdict"]

    # --- PRO arguments ---
    console.print("\n[bold green]PRO Arguments[/bold green]")
    for i, arg in enumerate(pro_args, 1):
        console.print(
            Panel(
                f"[bold]{arg['claim']}[/bold]\n"
                f"[dim]Reasoning:[/dim] {arg['reasoning']}\n"
                f"[dim]Evidence:[/dim] {arg['evidence']}\n"
                f"[dim]Risk:[/dim] {arg['risk']}\n"
                f"[dim]Confidence:[/dim] {arg['confidence']:.0%}",
                title=f"PRO #{i}",
                border_style="green",
                expand=False,
            )
        )

    # --- CON arguments ---
    console.print("\n[bold red]CON Arguments[/bold red]")
    for i, arg in enumerate(con_args, 1):
        console.print(
            Panel(
                f"[bold]{arg['claim']}[/bold]\n"
                f"[dim]Reasoning:[/dim] {arg['reasoning']}\n"
                f"[dim]Evidence:[/dim] {arg['evidence']}\n"
                f"[dim]Risk:[/dim] {arg['risk']}\n"
                f"[dim]Confidence:[/dim] {arg['confidence']:.0%}",
                title=f"CON #{i}",
                border_style="red",
                expand=False,
            )
        )

    # --- Scorecard ---
    console.print("\n[bold cyan]Scorecard[/bold cyan]")
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("Criterion", style="cyan")
    table.add_column("Weight", justify="right")
    table.add_column("PRO", justify="right", style="green")
    table.add_column("CON", justify="right", style="red")
    table.add_column("Rationale")
    for row in verdict["scorecard"]:
        table.add_row(
            row["criterion"],
            f"{row['weight']:.0%}",
            f"{row['pro_score']:.1f}",
            f"{row['con_score']:.1f}",
            row["rationale"],
        )
    console.print(table)

    # --- Verdict ---
    decision_label = DECISION_ICONS.get(verdict["decision"], verdict["decision"])
    winner_label = WINNER_LABELS.get(verdict["winner"], verdict["winner"])
    console.print(
        Panel(
            f"Decision: {decision_label}   Winner: {winner_label}   Confidence: {verdict['confidence']:.0%}\n\n"
            f"{verdict['summary']}",
            title="[bold]JUDGE Verdict[/bold]",
            border_style="cyan",
        )
    )

    def _bullet_list(items: list[str]) -> str:
        return "\n".join(f"• {item}" for item in items)

    console.print(
        Panel(
            _bullet_list(verdict["key_risks"]),
            title="Key Risks",
            border_style="yellow",
            expand=False,
        )
    )
    console.print(
        Panel(
            _bullet_list(verdict["assumptions_to_verify"]),
            title="Assumptions to Verify",
            border_style="magenta",
            expand=False,
        )
    )
    console.print(
        Panel(
            _bullet_list(verdict["next_48h_actions"]),
            title="Next 48h Actions",
            border_style="blue",
            expand=False,
        )
    )

    if verdict.get("needs_more_info") and verdict.get("clarifying_questions"):
        console.print(
            Panel(
                _bullet_list(verdict["clarifying_questions"]),
                title="Clarifying Questions",
                border_style="dim",
                expand=False,
            )
        )

    if save_json:
        payload = {
            "decision": decision,
            "context": context,
            "model": model,
            "pro_arguments": pro_args,
            "con_arguments": con_args,
            "verdict": verdict,
        }
        try:
            save_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        except OSError as exc:
            console.print(
                Panel(
                    f"Could not save JSON to {save_json}: {exc}",
                    title="Save failed",
                    border_style="red",
                    expand=False,
                )
            )
            raise typer.Exit(code=1) from exc
        console.print(f"\n[dim]Full result saved to {save_json}[/dim]")
