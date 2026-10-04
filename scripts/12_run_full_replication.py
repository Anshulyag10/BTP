from pathlib import Path

from replication.pipeline import run

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    run(ROOT / "config" / "experiments.json", ROOT, mode="PAPER_REPLICATION")
