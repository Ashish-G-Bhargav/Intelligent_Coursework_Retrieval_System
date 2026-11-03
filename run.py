#!/usr/bin/env python3
"""
EduRAG Web Server — entry point
Run: python run.py
Then open: http://localhost:8000
"""

import sys
from pathlib import Path

# Make sure src/ is on the path
SRC = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC))

import uvicorn

if __name__ == "__main__":
    print("\nEduRAG -- Intelligent Coursework Retrieval System")
    print("   Server  : http://localhost:8000")
    print("   API docs: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop\n")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(SRC)],
        app_dir=str(SRC),
    )

