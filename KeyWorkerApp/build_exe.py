import os
import subprocess
import sys

def build_exe():
    print("Starting build process...")
    
    # Clean previous builds
    try:
        import shutil
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        print("Cleaned previous builds")
    except:
        pass
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed', 
        '--name', 'AlysonHouseApp',
        '--add-data', 'alyson_house.db;.',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'tkcalendar', 
        '--hidden-import', 'CTkMessagebox',
        '--hidden-import', 'reportlab',
        'main.py'
    ]
    
    print("Running:", ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("Return code:", result.returncode)
    
    if result.returncode == 0:
        print("Build successful!")
        if os.path.exists('dist/AlysonHouseApp.exe'):
            print("Executable created at: dist/AlysonHouseApp.exe")
        else:
            print("Warning: Expected executable not found")
    else:
        print("Build failed!")

if __name__ == "__main__":
    build_exe()
