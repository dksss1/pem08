import PyInstaller.__main__
import os
import shutil
import fnmatch

def build():
    print("Building Competitor Monitor...")
    
    # Clean up previous build
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Define PyInstaller arguments
    args = [
        "launcher.py",  # Entry point
        "--name=CompetitorMonitor",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--log-level=WARN",
        
        # Include backend package explicitly (though imports should find it)
        # We don't use --add-data for code unless necessary.
        # But we do need to handle potential hidden imports if PyInstaller misses them.
        "--hidden-import=backend",
        "--hidden-import=backend.services",
        "--hidden-import=backend.services.openai_service",
        "--hidden-import=backend.services.parser_service",
        "--hidden-import=backend.config",
        "--hidden-import=backend.models.schemas",
        
        # Exclude unused PyQt6 modules to reduce size
        "--exclude-module=PyQt6.QtDBus",
        "--exclude-module=PyQt6.QtDesigner",
        "--exclude-module=PyQt6.QtNetwork",
        "--exclude-module=PyQt6.QtNfc",
        "--exclude-module=PyQt6.QtOpenGL",
        "--exclude-module=PyQt6.QtPdf",
        "--exclude-module=PyQt6.QtQml",
        "--exclude-module=PyQt6.QtQuick",
        "--exclude-module=PyQt6.QtQuick3D",
        "--exclude-module=PyQt6.QtSensors",
        "--exclude-module=PyQt6.QtSql",
        "--exclude-module=PyQt6.QtSvg",
        "--exclude-module=PyQt6.QtTest",
        "--exclude-module=PyQt6.QtXml",
        "--exclude-module=PyQt6.QtHelp",
        
        # Exclude dev/testing libraries
        "--exclude-module=pytest",
        "--exclude-module=_pytest",
        "--exclude-module=anyio.testing",
        "--exclude-module=bs4.tests",
    ]
    
    PyInstaller.__main__.run(args)
    
    # Post-build: Copy .env file if it exists
    if os.path.exists(".env"):
        shutil.copy(".env", "dist/.env")
        print("Copied .env to dist/")
    else:
        print("WARNING: .env not found in root. User must create it in dist/")

    # Post-build: prune unnecessary files from dist
    dist_app_dir = os.path.join("dist", "CompetitorMonitor")
    if os.path.isdir(dist_app_dir):
        print("Pruning dist/CompetitorMonitor ...")
        remove_dirnames = {
            "__pycache__", "tests", "testing", "test", "examples", "example", "docs", "samples", ".cache"
        }
        remove_patterns = ["*.pyc", "*.pyo", "*.spec"]
        # Remove *-dist-info metadata folders anywhere
        for root, dirs, files in os.walk(dist_app_dir, topdown=True):
            # Prune directory names
            dirs[:] = [d for d in dirs if d not in remove_dirnames and not d.endswith(".dist-info")]
            # Delete dist-info folders explicitly if found
            for d in list(dirs):
                if d.endswith(".dist-info"):
                    full = os.path.join(root, d)
                    try:
                        shutil.rmtree(full)
                        print(f"Removed: {full}")
                        dirs.remove(d)
                    except Exception as e:
                        print(f"WARN: failed to remove {full}: {e}")
            # Delete matching files
            for f in files:
                if any(fnmatch.fnmatch(f, pat) for pat in remove_patterns):
                    full = os.path.join(root, f)
                    try:
                        os.remove(full)
                        print(f"Removed: {full}")
                    except Exception as e:
                        print(f"WARN: failed to remove {full}: {e}")

    # Report final size
    try:
        import pathlib
        base = pathlib.Path("dist")
        total = sum(p.stat().st_size for p in base.rglob("*"))
        print(f"Final dist size: {total} bytes")
    except Exception:
        pass

    print("Build complete. executable is in dist/CompetitorMonitor.exe")

if __name__ == "__main__":
    build()
