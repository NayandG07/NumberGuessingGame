#!/usr/bin/env python3
import sys
import os
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.x"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3:
        print("ERROR: Python 3.x is required. You are using Python {}.{}".format(
            version.major, version.minor))
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_tkinter():
    """Check if Tkinter is available"""
    print("Checking Tkinter availability...")
    try:
        import tkinter
        print("✓ Tkinter is available")
        return True
    except ImportError:
        print("ERROR: Tkinter is not available.")
        print("Please install Tkinter:")
        if platform.system() == "Linux":
            print("  For Debian/Ubuntu: sudo apt-get install python3-tk")
            print("  For Fedora: sudo dnf install python3-tkinter")
            print("  For Arch: sudo pacman -S tk")
        elif platform.system() == "Darwin":  # macOS
            print("  Install Python with Homebrew: brew install python-tk")
            print("  Or download Python from python.org which includes Tkinter")
        elif platform.system() == "Windows":
            print("  Download Python from python.org with Tcl/Tk option enabled")
        return False

def check_required_modules():
    """Check if all required modules are available"""
    required_modules = ['random', 'time', 'json', 'datetime', 'os', 'sys', 'traceback']
    print("Checking required modules...")
    all_available = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ Module {module} is available")
        except ImportError:
            print(f"ERROR: Module {module} is not available")
            all_available = False
    return all_available

def create_directories():
    """Create necessary directories"""
    print("Creating necessary directories...")
    for directory in ['data', 'avatars']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Directory '{directory}' created")
        else:
            print(f"✓ Directory '{directory}' already exists")
    return True

def main():
    print("=== Number Guessing Game Installation ===")
    
    python_ok = check_python_version()
    tkinter_ok = check_tkinter()
    modules_ok = check_required_modules()
    dirs_ok = create_directories()
    
    print("\n=== Installation Summary ===")
    if python_ok and tkinter_ok and modules_ok and dirs_ok:
        print("All requirements are met! You can run the game using:")
        print("  python Final_fixed_game.py")
    else:
        print("Some requirements are not met. Please fix the issues mentioned above.")
    
    print("\nThank you for installing Number Guessing Game!")

if __name__ == "__main__":
    main() 