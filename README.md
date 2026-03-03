# Python-Code-Tier-Scanner
Parallel pylint score classifier for Python files. Scans a file or directory, assigns quality tiers, and reports up to 10 files per tier.
Scans a file or directory, assigns quality tiers, and reports up to 10 files per tier.

Overview

This script:
-Recursively scans a directory (or evaluates a single file)
-Runs pylint on each .py file
-Extracts the numeric score
-Classifies the file into a predefined quality tier
-Processes files in parallel using all CPU cores
-Limits output to 10 files per tier, sorted by lowest score first
-The script excludes itself automatically.



Quality Tiers
| Tier | Name         | Score Range  |
| ---- | ------------ | ------------ |
| 0    | CRITICAL     | `< 6.0`      |
| 1    | NEEDS_WORK   | `6.0 – <8.0` |
| 2    | ACCEPTABLE   | `8.0 – <9.5` |
| 3    | NEAR_PERFECT | `>= 9.5`     |

Requirements:
- Python 3.8+
- pylint installed and available in PATH

Install pylint if needed:
- pip install pylint

Usage:
- Scan A Directory
  - python script_name.py /path/to/project
- Scan A File
  - python script_name.py my_script.py
- Filter by Tier
  - python script_name.py /path/to/project --tier 0
  - Allowed tier values: 0, 1, 2, 3

Example Output: 
PYTHON CODE TIER SCORE    

[0] CRITICAL

 5.43  project/bad_script.py

[1] NEEDS_WORK

 6.72  project/legacy.py

[2] ACCEPTABLE

 8.91  project/utils.py

[3] NEAR_PERFECT

 9.78  project/core.py

Implementation Details:
- Uses ProcessPoolExecutor for parallel execution.
- Worker count = os.cpu_count().
- Score extracted using regex from pylint output:
- rated at X.YZ/10
- Files sorted by ascending score within each tier.
- Maximum 10 entries displayed per tier.

Notes:
- If pylint fails or produces no score, the file is skipped.
- This tool reports summary classification only. It does not print detailed pylint diagnostics.
- Runtime depends on project size and CPU core count.

Purpose

Designed for rapid, large-scale codebase quality triage.

Useful for:
- Refactoring prioritization
- Legacy code assessment
- CI pre-review audits
- Code quality benchmarking
