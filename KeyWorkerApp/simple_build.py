import subprocess
import sys
import os
import shutil
import time

def build_app():
    try:
        print("Starting build process...")
        
        # Clean previous builds with retry
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                for i in range(3):  # Try 3 times
                    try:
                        shutil.rmtree(folder)
                        print(f"Removed old {folder} folder")
                        break
                    except PermissionError:
                        print(f"Folder {folder} in use, waiting...")
                        time.sleep(2)
                        if i == 2:  # Last try
                            print(f"Warning: Could not remove {folder}, continuing...")
            
        # Simple PyInstaller command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--noconsole',
            '--name', 'AlysonHouseApp',
            'main.py'
        ]
        
        print("Running PyInstaller...")
        print("Command:", ' '.join(cmd))
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print("=== STDOUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== STDERR ===") 
            print(result.stderr)
            
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ Build successful!")
            
            # Check if exe was created
            exe_path = os.path.join('dist', 'AlysonHouseApp.exe')
            if os.path.exists(exe_path):
                print(f"✅ Executable created: {exe_path}")
                print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
                
                # Try to copy to desktop location
                dest_dir = r"C:\Users\Home Admin\Dropbox\PC\Desktop\AlysonHouseAppDist"
                if os.path.exists(dest_dir):
                    dest_path = os.path.join(dest_dir, 'AlysonHouseApp.exe')
                    try:
                        shutil.copy2(exe_path, dest_path)
                        print(f"✅ Copied to: {dest_path}")
                    except Exception as e:
                        print(f"❌ Failed to copy to desktop: {e}")
                        print(f"You can manually copy from: {exe_path}")
                else:
                    print(f"❌ Desktop directory not found: {dest_dir}")
                    print(f"Executable is at: {exe_path}")
            else:
                print("❌ Executable not found in dist folder")
        else:
            print("❌ Build failed!")
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    build_app()
