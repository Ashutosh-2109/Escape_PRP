import subprocess
import sys

def install(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"Failed to install {package}. Error: {e}")

if __name__ == "__main__":
    requirements = ["pygame>=2.6.0", "pytmx>=3.25"]
    for req in requirements:
        install(req)
    print("\nAll dependencies installed successfully!")
