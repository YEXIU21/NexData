"""
Build script for creating standalone EXE
NexData v3.1 - Professional Data Analysis Tool
Shopify Edition - Enhanced UX Edition

Usage: python build_exe.py [--debug]
"""

import sys
import os
import shutil
from datetime import datetime

# Check if PyInstaller is installed
try:
    import PyInstaller.__main__
except ImportError:
    print("❌ ERROR: PyInstaller not found!")
    print("Install it with: pip install pyinstaller")
    sys.exit(1)

# Configuration
APP_NAME = "NexData"
APP_VERSION = "3.1"
DEBUG_MODE = "--debug" in sys.argv

# Get absolute paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_script = os.path.join(base_dir, 'main.py')
icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
dist_path = os.path.join(base_dir, 'dist')
build_path = os.path.join(base_dir, 'build')

# Verify main script exists
if not os.path.exists(main_script):
    print(f"❌ ERROR: Main script not found: {main_script}")
    sys.exit(1)

# Clean old build artifacts
if os.path.exists(dist_path):
    print("🧹 Cleaning old dist folder...")
    shutil.rmtree(dist_path, ignore_errors=True)

if os.path.exists(build_path):
    print("🧹 Cleaning old build folder...")
    shutil.rmtree(build_path, ignore_errors=True)

print(f"""
╔══════════════════════════════════════════════════════╗
║         NexData v{APP_VERSION} - EXE Builder                ║
║      Professional Data Analysis Tool Builder         ║
╚══════════════════════════════════════════════════════╝

📦 Building standalone executable...
""")

# PyInstaller arguments
args = [
    main_script,
    '--onefile',                          # Single EXE file
    '--windowed',                         # No console window
    f'--name={APP_NAME}',                 # EXE name
    '--clean',                            # Clean cache
    f'--distpath={dist_path}',
    f'--workpath={build_path}',
    f'--specpath={base_dir}',
    
    # Hidden imports for all dependencies
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=matplotlib.backends.backend_tkagg',
    '--hidden-import=seaborn',
    '--hidden-import=openpyxl',
    '--hidden-import=xlrd',
    '--hidden-import=scipy',
    '--hidden-import=scipy.stats',
    '--hidden-import=requests',
    '--hidden-import=psutil',
    '--hidden-import=pptx',
    '--hidden-import=PIL',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    '--hidden-import=tkinter.scrolledtext',
    
    # Collect all data files from packages
    '--collect-all=matplotlib',
    '--collect-all=seaborn',
    '--collect-data=pandas',
    
    # Exclude unnecessary packages to reduce size
    '--exclude-module=pytest',
    '--exclude-module=sphinx',
    '--exclude-module=jupyter',
]

# Add icon if exists
if os.path.exists(icon_path):
    args.append(f'--icon={icon_path}')
    print(f"🎨 Using icon: {icon_path}")
else:
    print(f"⚠️  Warning: Icon not found at {icon_path}")

# Debug mode
if DEBUG_MODE:
    args.append('--debug=all')
    args.append('--console')
    print("🔍 DEBUG MODE ENABLED - Console will be shown")

# Print build info
print(f"""
Build Configuration:
───────────────────────────────────────────────────────
• App Name:     {APP_NAME} v{APP_VERSION}
• Main Script:  {os.path.basename(main_script)}
• Output Dir:   {dist_path}
• Mode:         {'DEBUG' if DEBUG_MODE else 'RELEASE'}
• Console:      {'Yes' if DEBUG_MODE else 'No'}
───────────────────────────────────────────────────────

⏳ Building... This may take 3-5 minutes...
""")

# Run PyInstaller
try:
    start_time = datetime.now()
    PyInstaller.__main__.run(args)
    end_time = datetime.now()
    build_time = (end_time - start_time).seconds
    
    # Get EXE info
    exe_path = os.path.join(dist_path, f'{APP_NAME}.exe')
    if os.path.exists(exe_path):
        exe_size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        
        print(f"""
╔══════════════════════════════════════════════════════╗
║               ✅ BUILD SUCCESSFUL!                    ║
╚══════════════════════════════════════════════════════╝

Build Information:
───────────────────────────────────────────────────────
• EXE Location:  {exe_path}
• File Size:     {exe_size_mb:.2f} MB
• Build Time:    {build_time} seconds
• Version:       {APP_VERSION}
───────────────────────────────────────────────────────

What's Included in this Build:
✓ NexData v3.1 Professional Data Analysis Tool
✓ Shopify Edition - Enhanced UX Edition
✓ 60+ Data Analysis Features
✓ AI-Powered Insights
✓ Progress Bars for Large Files
✓ Keyboard Shortcuts (Ctrl+O, Ctrl+E, etc.)
✓ Auto-Save & Crash Recovery
✓ Tooltips System
✓ All dependencies bundled

Distribution:
───────────────────────────────────────────────────────
✅ Ready to distribute!
✅ No Python installation required
✅ Runs on any Windows 64-bit system
✅ Self-contained executable

Next Steps:
───────────────────────────────────────────────────────
1. Test the EXE: {exe_path}
2. Distribute to users
3. No additional setup required!

💡 Tip: The EXE is portable and can run from any location.
        """)
    else:
        print("\n❌ ERROR: EXE file was not created!")
        print(f"Expected location: {exe_path}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ BUILD FAILED!")
    print(f"Error: {e}")
    sys.exit(1)
