# Run commands

From the project root, after installing the dependencies:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m replication.cli --mode PAPER_REPLICATION
.\.venv\Scripts\python.exe scripts/02_check_price_curves.py
.\.venv\Scripts\python.exe scripts/03_check_inference.py
.\.venv\Scripts\python.exe scripts/06_debug_mrjd_parameterization.py
.\.venv\Scripts\python.exe scripts/13_compare_with_paper.py
```

The full mode uses 500 repetitions for Pair 1 and 300 for Pair 2. There is no artificial
readiness gate. The outputs and report still state that numerical replication is unverified.
Use DEBUG for four repetitions or VALIDATION for analytical model checks alone.
