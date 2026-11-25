"""Pytest configuration for MTM606 test suite."""

import sys
from pathlib import Path

# Add web-app directory to sys.path
web_app_dir = Path(__file__).resolve().parent.parent / "web-app"
if str(web_app_dir) not in sys.path:
    sys.path.insert(0, str(web_app_dir))
