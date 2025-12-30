"""Run script for Todo Manager application."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from src.cli.console import run

if __name__ == "__main__":
    run()
