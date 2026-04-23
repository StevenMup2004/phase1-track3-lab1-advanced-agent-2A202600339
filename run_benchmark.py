from __future__ import annotations
import json
from pathlib import Path
import typer
from rich import print
from src.reflexion_lab.agents import ReActAgent, ReflexionAgent
from src.reflexion_lab.reporting import build_report, save_report
from src.reflexion_lab.utils import load_dataset, save_jsonl
app = typer.Typer(add_completion=False)

@app.command()
def main(dataset: str = "data/hotpot_100_diverse.json", out_dir: str = "outputs/sample_run", reflexion_attempts: int = 3) -> None:
    examples = load_dataset(dataset)
    print(f"[bold cyan]Loaded {len(examples)} examples from {dataset}[/bold cyan]")

    react = ReActAgent()
    reflexion = ReflexionAgent(max_attempts=reflexion_attempts)

    print("[bold yellow]Running ReAct agent...[/bold yellow]")
    react_records = []
    for i, example in enumerate(examples):
        print(f"  ReAct [{i+1}/{len(examples)}] {example.qid}")
        react_records.append(react.run(example))

    print("[bold yellow]Running Reflexion agent...[/bold yellow]")
    reflexion_records = []
    for i, example in enumerate(examples):
        print(f"  Reflexion [{i+1}/{len(examples)}] {example.qid}")
        reflexion_records.append(reflexion.run(example))

    all_records = react_records + reflexion_records
    out_path = Path(out_dir)
    save_jsonl(out_path / "react_runs.jsonl", react_records)
    save_jsonl(out_path / "reflexion_runs.jsonl", reflexion_records)
    report = build_report(all_records, dataset_name=Path(dataset).name, mode="live")
    json_path, md_path = save_report(report, out_path)
    print(f"[green]Saved[/green] {json_path}")
    print(f"[green]Saved[/green] {md_path}")
    print(json.dumps(report.summary, indent=2))

if __name__ == "__main__":
    app()
