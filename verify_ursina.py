#!/usr/bin/env python3
"""
Verification script for the Ursina Psycho Backrooms game
This script checks if all imports and dependencies work correctly
"""

def verify_imports():
    """Verify that all required modules can be imported"""
    print("Verifying imports...")
    
    try:
        import ursina
        print("✓ ursina imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ursina: {e}")
        return False
    
    try:
        from ursina.prefabs.first_person_controller import FirstPersonController
        print("✓ FirstPersonController imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FirstPersonController: {e}")
        return False
    
    try:
        import math
        print("✓ math imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import math: {e}")
        return False
    
    try:
        import random
        print("✓ random imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import random: {e}")
        return False
    
    try:
        import noise
        print("✓ noise imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import noise: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    return True

def verify_syntax():
    """Verify that the main game file has correct syntax"""
    print("\nVerifying syntax of ursina_backrooms.py...")
    
    try:
        with open('ursina_backrooms.py', 'r') as f:
            code = f.read()
        
        # Compile the code to check for syntax errors
        compile(code, 'ursina_backrooms.py', 'exec')
        print("✓ Syntax is correct")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except FileNotFoundError:
        print("✗ File not found: ursina_backrooms.py")
        return False
    except Exception as e:
        print(f"✗ Error checking syntax: {e}")
        return False

def verify_classes():
    """Verify that the main classes can be defined (without instantiating)"""
    print("\nVerifying class definitions...")
    
    try:
        # Read the file content
        with open('ursina_backrooms.py', 'r') as f:
            code = f.read()
        
        # Execute the code up to class definitions to verify they're syntactically correct
        # This will check if the classes can be defined properly
        exec(code, {"__name__": "__verify__", "__file__": "ursina_backrooms.py"})
        print("✓ All classes defined correctly")
        return True
    except Exception as e:
        print(f"✗ Error in class definitions: {e}")
        return False

def main():
    """Main verification function"""
    print("Ursina Psycho Backrooms Game - Verification Script")
    print("=" * 50)
    
    success = True
    
    success &= verify_imports()
    success &= verify_syntax()
    success &= verify_classes()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All verifications passed! The game should work correctly.")
        print("\nTo run the game, execute: python ursina_backrooms.py")
    else:
        print("✗ Some verifications failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()