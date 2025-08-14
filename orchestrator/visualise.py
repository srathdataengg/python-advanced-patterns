from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


def mermaid_from_config(cfg: Dict[str, Any], latest_status: Dict[str, str]) -> str:
    """
    Build a simple Mermaid graph where each pipeline is a node.
    Color nodes by latest status: SUCCESS=green, FAILED=red, RUNNING=yellow, default=gray.
    """
    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("graph LR")
    lines.append("  classDef success fill:#d4f8d4,stroke:#0a0,stroke-width:1px;")
    lines.append("  classDef failed fill:#ffd6d6,stroke:#a00,stroke-width:1px;")
    lines.append("  classDef running fill:#fff3bf,stroke:#aa0,stroke-width:1px;")
    lines.append("  classDef pending fill:#eee,stroke:#999,stroke-width:1px;")

    for p in cfg.get("pipelines", []):
        name = p["name"]
        label = f'{name}({name})'
        lines.append(f"  {label}")
        status = (latest_status.get(name) or "PENDING").upper()
        cls = "pending"
        if status == "SUCCESS":
            cls = "success"
        elif status == "FAILED":
            cls = "failed"
        elif status == "RUNNING":
            cls = "running"
        lines.append(f"  class {name} {cls};")

    # (Optional) Add faux edges if you want a linear flow
    # for i in range(len(cfg.get('pipelines', [])) - 1):
    #     a = cfg['pipelines'][i]['name']
    #     b = cfg['pipelines'][i+1]['name']
    #     lines.append(f"  {a} --> {b}")

    lines.append("```")
    return "\n".join(lines)


def write_mermaid(md_text: str, out_path: str = "docs/ingestion_dag.md") -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md_text, encoding="utf-8")
    logger.info(f"Mermaid DAG written to {out_path}")
