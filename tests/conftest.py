"""Shared pytest fixtures for headless baseball pipeline testing."""

from __future__ import annotations

from pathlib import Path
import sys

_START_DIR = (
    Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd().resolve()
)
for _candidate in (_START_DIR, *_START_DIR.parents):
    if (_candidate / "OOP_Workflow" / "main.py").is_file() and (
        _candidate / "OOP_Workflow"
    ).is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

BATTING_COLUMNS = [
    "playerID",
    "yearID",
    "stint",
    "teamID",
    "lgID",
    "G",
    "AB",
    "R",
    "H",
    "2B",
    "3B",
    "HR",
    "RBI",
    "SB",
    "CS",
    "BB",
    "SO",
    "IBB",
    "HBP",
    "SH",
    "SF",
    "GIDP",
]

FIELDING_COLUMNS = [
    "playerID",
    "yearID",
    "stint",
    "teamID",
    "lgID",
    "POS",
    "G",
    "GS",
    "InnOuts",
    "PO",
    "A",
    "E",
    "DP",
    "PB",
    "WP",
    "SB",
    "CS",
    "ZR",
]

SALARIES_COLUMNS = ["yearID", "teamID", "lgID", "playerID", "salary"]


@pytest.fixture
def synthetic_raw_data_dir(tmp_path: Path) -> Path:
    """Create minimal valid Batting, Fielding, and Salaries CSVs in tmp_path."""
    raw_dir = tmp_path / "raw_data"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 12 players in 2015 across AL and NL (6 teams) + 2 rows in 2014 + 1 pre-2000 row.
    # Batting metrics are intentionally varied so correlations are non-NaN.
    records = [
        # playerID, yearID, teamID, lgID, POS, G, AB, R, H, 2B, 3B, HR, RBI, SB, BB, SO, salary
        ("play01", 2015, "NYA", "AL", "OF", 145, 550, 92, 168, 34, 4, 31, 98, 12, 65, 110, 18_500_000),
        ("play02", 2015, "BOS", "AL", "1B", 138, 510, 80, 152, 29, 1, 27, 90, 4, 72, 104, 14_200_000),
        ("play03", 2015, "SEA", "AL", "2B", 150, 580, 88, 175, 36, 5, 22, 79, 24, 54, 96, 12_000_000),
        ("play04", 2015, "NYA", "AL", "SS", 128, 460, 61, 124, 21, 3, 14, 58, 18, 41, 89, 7_500_000),
        ("play05", 2015, "BOS", "AL", "3B", 118, 420, 52, 108, 19, 2, 11, 49, 6, 35, 92, 4_200_000),
        ("play06", 2015, "SEA", "AL", "C", 96, 330, 34, 81, 15, 0, 9, 39, 1, 28, 76, 1_800_000),
        ("play07", 2015, "LAN", "NL", "OF", 152, 565, 96, 178, 38, 6, 33, 105, 16, 79, 118, 21_000_000),
        ("play08", 2015, "CHN", "NL", "3B", 144, 530, 84, 156, 31, 2, 26, 88, 9, 68, 132, 15_400_000),
        ("play09", 2015, "SFN", "NL", "SS", 140, 505, 71, 142, 27, 4, 15, 67, 14, 49, 84, 9_800_000),
        ("play10", 2015, "LAN", "NL", "2B", 122, 440, 59, 119, 22, 3, 10, 46, 21, 38, 72, 6_100_000),
        ("play11", 2015, "CHN", "NL", "1B", 110, 390, 48, 99, 18, 1, 13, 52, 3, 44, 95, 3_300_000),
        ("play12", 2015, "SFN", "NL", "OF", 88, 280, 31, 68, 11, 2, 5, 29, 11, 22, 64, 950_000),
        ("play01", 2014, "NYA", "AL", "OF", 140, 525, 86, 158, 30, 3, 28, 91, 10, 60, 105, 17_000_000),
        ("play07", 2014, "LAN", "NL", "OF", 148, 545, 91, 170, 35, 5, 29, 97, 15, 73, 112, 19_500_000),
        ("hist98", 1998, "NYA", "AL", "OF", 130, 480, 75, 140, 25, 2, 20, 75, 8, 50, 90, 5_000_000),
    ]

    batting_rows = []
    fielding_rows = []
    salary_rows = []

    for idx, (pid, yr, tm, lg, pos, g, ab, r, h, b2, b3, hr, rbi, sb, bb, so, sal) in enumerate(records):
        batting_rows.append(
            {
                "playerID": pid,
                "yearID": yr,
                "stint": 1,
                "teamID": tm,
                "lgID": lg,
                "G": g,
                "AB": ab,
                "R": r,
                "H": h,
                "2B": b2,
                "3B": b3,
                "HR": hr,
                "RBI": rbi,
                "SB": sb,
                "CS": idx % 5,
                "BB": bb,
                "SO": so,
                "IBB": idx % 4,
                "HBP": idx % 6,
                "SH": idx % 3,
                "SF": (idx + 1) % 5,
                "GIDP": (idx + 2) % 10,
            }
        )
        fielding_rows.append(
            {
                "playerID": pid,
                "yearID": yr,
                "stint": 1,
                "teamID": tm,
                "lgID": lg,
                "POS": pos,
                "G": g,
                "GS": max(g - 5, 0),
                "InnOuts": g * 24,
                "PO": 120 + idx * 7,
                "A": 15 + idx * 3,
                "E": idx % 7,
                "DP": 5 + idx,
                "PB": 2.0 if pos == "C" else None,
                "WP": 3.0 if pos == "P" else None,
                "SB": 10.0 if pos == "C" else None,
                "CS": 4.0 if pos == "C" else None,
                "ZR": None,
            }
        )
        salary_rows.append(
            {
                "yearID": yr,
                "teamID": tm,
                "lgID": lg,
                "playerID": pid,
                "salary": sal,
            }
        )

    pd.DataFrame(batting_rows, columns=BATTING_COLUMNS).to_csv(
        raw_dir / "Batting.csv", index=False
    )
    pd.DataFrame(fielding_rows, columns=FIELDING_COLUMNS).to_csv(
        raw_dir / "Fielding.csv", index=False
    )
    pd.DataFrame(salary_rows, columns=SALARIES_COLUMNS).to_csv(
        raw_dir / "Salaries.csv", index=False
    )

    return raw_dir
