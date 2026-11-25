"""Package module entry point delegating to the root CLI runner."""

from __future__ import annotations

from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from main import main

if __name__ == "__main__":
    raise SystemExit(main())
