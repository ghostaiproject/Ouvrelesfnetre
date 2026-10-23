"""Copy the shared rules (alert.py, flair.py) into skill/lambda before deploying."""
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
for f in ("alert.py", "flair.py"):
    shutil.copy(root / f, root / "skill" / "lambda" / f)
    print("copied", f)
