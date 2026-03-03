import argparse
import subprocess
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional, Tuple, Dict, List, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

# Quality tier definitions
TIERS: Dict[int, Tuple[str, Callable[[float], bool]]] = {
    0: ("CRITICAL", lambda s: s < 6.0),
    1: ("NEEDS_WORK", lambda s: 6.0 <= s < 8.0),
    2: ("ACCEPTABLE", lambda s: 8.0 <= s < 9.5),
    3: ("NEAR_PERFECT", lambda s: s >= 9.5),
}

SCORE_RE = re.compile(r"rated at ([\d.]+)/10")

def get_score(path: str) -> Optional[float]:
    """
    Run pylint on a single Python file and extract the numeric score.
    """
    proc = subprocess.run(
        ["pylint", path, "--score=y", "--reports=n"],
        capture_output=True,
        text=True,
    )
    match = SCORE_RE.search(proc.stdout)
    return float(match.group(1)) if match else None

def iter_py_files(root: str) -> List[Path]:
    """
    Collect Python files under a directory or single file.
    Excludes this script itself.
    """
    root_path = Path(root)
    current_script = Path(__file__).resolve()
    files: List[Path] = []

    if root_path.is_file() and root_path.suffix == ".py":
        if root_path.resolve() != current_script:
            files.append(root_path)
    elif root_path.is_dir():
        for file in root_path.rglob("*.py"):
            if file.resolve() != current_script:
                files.append(file)

    return files

def classify_file(file: Path) -> Optional[Tuple[int, Path, float]]:
    """
    Run pylint on a file and return its tier classification.
    """
    score = get_score(str(file))
    if score is None:
        return None

    for tid, (_, rule) in TIERS.items():
        if rule(score):
            return tid, file, score

    return None

def main(path: str, tier_filter: Optional[int]) -> None:
    """
    Parallel scan and quality-tier classification.
    Limits each tier to 10 scripts max.
    """
    buckets: Dict[int, List[Tuple[Path, float]]] = defaultdict(list)
    files = iter_py_files(path)

    workers = os.cpu_count() or 1

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(classify_file, f) for f in files]

        for future in as_completed(futures):
            result = future.result()
            if result is None:
                continue
            tid, file, score = result
            if tier_filter is None or tid == tier_filter:
                buckets[tid].append((file, score))            

    for tid in sorted(TIERS):
        if tier_filter is not None and tid != tier_filter:
            continue

        name, _ = TIERS[tid]
        print(f"\n[{tid}] {name}\n")

        # Sort files by score ascending, limit to max 10
        for file, score in sorted(buckets[tid], key=lambda x: x[1])[:10]:
            print(f"{score:5.2f}  {file}")
        
        # Ensure line break after each tier report
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("--tier", type=int, choices=TIERS.keys())
    args = parser.parse_args()

    print()
    print("PYTHON CODE TIER SCORE    ")

    main(args.path, args.tier)