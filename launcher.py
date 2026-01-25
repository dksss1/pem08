import sys
import os

# Ensure the root directory is in sys.path so we can import 'backend' and 'desktop_app'
# This is crucial for PyInstaller analysis to find them as top-level packages
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from desktop_app.main import run_app

if __name__ == "__main__":
    run_app()
