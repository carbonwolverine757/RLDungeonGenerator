#!/usr/bin/env python3
"""
Installation verification script for RLDungeonGenerator with BearLibTerminal support.
Run this to check if all dependencies are installed correctly.
"""

import sys
import subprocess

def check_module(name, import_name=None):
    """Check if a Python module is installed."""
    if import_name is None:
        import_name = name
    
    try:
        __import__(import_name)
        print(f"? {name:30} installed")
        return True
    except ImportError:
        print(f"? {name:30} NOT installed")
        return False

def main():
    print("=" * 60)
    print("RLDungeonGenerator - Dependency Check")
    print("=" * 60)
    print()
    
    required = {
        "Pillow": "PIL",
        "numpy": "numpy",
    }
    
    optional = {
        "tcod": "tcod",
        "bearlib-terminal": "bearlib",
    }
    
    print("REQUIRED MODULES:")
    print("-" * 60)
    all_required = True
    for package, import_name in required.items():
        if not check_module(package, import_name):
            all_required = False
    
    print()
    print("OPTIONAL MODULES (for rendering):")
    print("-" * 60)
    any_optional = False
    for package, import_name in optional.items():
        if check_module(package, import_name):
            any_optional = True
    
    print()
    print("=" * 60)
    
    if not all_required:
        print("\n? Missing required modules. Install with:")
        print("  pip install -r requirements.txt")
        return 1
    
    if not any_optional:
        print("\n? No rendering backends found. Install one of:")
        print("  pip install tcod")
        print("  pip install bearlib-terminal")
        return 1
    
    print("\n? All dependencies satisfied!")
    print("\nRun the game with:")
    print("  python RLDungeonGenerator.py --renderer bearlib")
    return 0

if __name__ == "__main__":
    sys.exit(main())
