from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the paper's simulation figures and tables"
    )
    parser.add_argument("--config", type=Path, default=Path("config/experiments.json"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use the paper's 500/300 outer repetitions.",
    )
    parser.add_argument(
        "--mode",
        choices=("DEBUG", "VALIDATION", "PAPER_REPLICATION"),
        default=None,
        help="Select a diagnostic run, validation-only run, or reviewed paper-scale run.",
    )
    args = parser.parse_args()
    if args.full and args.mode:
        parser.error("use either --full or --mode, not both")
    run(args.config, args.root, args.full, args.mode)


if __name__ == "__main__":
    main()
