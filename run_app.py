"""Root runner for ThesisForge AI from Desktop/4vu5h/MTM606."""

import os
import sys
from pathlib import Path

web_app_dir = Path(__file__).resolve().parent / "web-app"
if str(web_app_dir) not in sys.path:
    sys.path.insert(0, str(web_app_dir))

os.chdir(str(web_app_dir))

if __name__ == "__main__":
    import uvicorn
    from backend.main import app

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    print("=" * 60)
    print("   THESISFORGE AI — INVESTMENT COMMITTEE WEB APPLICATION")
    print("=" * 60)
    print(f"Location:         {web_app_dir}")
    print(f"Web Interface:    http://localhost:{port}")
    print(f"Interactive Docs: http://localhost:{port}/docs")
    print(f"Health Endpoint:  http://localhost:{port}/health")
    print("=" * 60)
    uvicorn.run(app, host=host, port=port)
