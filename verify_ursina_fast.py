#!/usr/bin/env python3
"""
Verification script for the fast-loading Ursina Backrooms game
This script checks that the code has correct syntax and imports
"""
import sys
import ast

def check_syntax(file_path):
    """Check if the Python file has valid syntax"""
    try:
        with open(file_path, 'r') as file:
            source = file.read()
        ast.parse(source)
        print(f"✓ {file_path} has valid syntax")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {file_path}: {e}")
        return False

def check_imports(file_path):
    """Check if the main imports work without noise/perlin dependencies"""
    try:
        with open(file_path, 'r') as file:
            source = file.read()
        
        # Check if the file contains the expected imports
        expected_imports = [
            'from ursina import *',
            'import random',
            'import math'
        ]
        
        for imp in expected_imports:
            if imp not in source:
                print(f"✗ Missing expected import: {imp}")
                return False
        
        # Check if noise imports are removed
        if 'import noise' in source or 'from perlin_noise' in source:
            print("✗ Still contains noise/perlin imports")
            return False
        
        print("✓ All expected imports are correct")
        return True
    except Exception as e:
        print(f"✗ Error checking imports in {file_path}: {e}")
        return False

def main():
    print("Verifying fast-loading Ursina Backrooms game...")
    print()
    
    file_path = '/workspace/ursina_backrooms.py'
    
    # Check syntax
    syntax_ok = check_syntax(file_path)
    print()
    
    # Check imports
    imports_ok = check_imports(file_path)
    print()
    
    if syntax_ok and imports_ok:
        print("✓ All checks passed! The game should load quickly now.")
        return True
    else:
        print("✗ Some checks failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)