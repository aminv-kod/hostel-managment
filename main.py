import sys
import subprocess
import os

def check_dependencies():
    """Checks for necessary third-party libraries and attempts automatic installation if missing."""
    needed_packages = []
    
    # Try importing pymysql
    try:
        import pymysql
    except ImportError:
        needed_packages.append("pymysql")

    if needed_packages:
        print(f"HMS Launcher: Resolving missing package dependencies: {needed_packages}")
        try:
            # Run pip installer inside Python context
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + needed_packages)
            print("HMS Launcher: Dependencies successfully installed!")
        except Exception as e:
            print(f"HMS Launcher Warning: Automated installation failed. Please manually run 'pip install pymysql' if using MySQL:\n{e}")

if __name__ == "__main__":
    # Ensure current working directory is set to project root folder to resolve JSON configurations and DB paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    sys.path.insert(0, project_dir)
    
    # Perform automated dependency checks
    check_dependencies()
    
    # Launch main GUI thread
    try:
        from gui.main_window import MainWindow
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Critical Launcher Error: Unable to initiate application GUI loop:\n{e}")
        input("\nPress Enter to exit...")
