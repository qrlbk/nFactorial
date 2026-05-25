#!/usr/bin/env python3
"""Root-level CLI shim: python run_pipeline.py input.txt"""

from app.cli.run_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())
