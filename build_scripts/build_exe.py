"""
Build script for creating standalone EXE
Professional Data Analysis Tool - Shopify Edition

Usage: python build_exe.py
"""

import PyInstaller.__main__
import os

# Get absolute paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from build_scripts
main_script = os.path.join(base_dir, 'src', 'main.py')
icon_path = os.path.join(base_dir, 'assets', 'icon.ico')  # Optional

# PyInstaller arguments
args = [
    main_script,
    '--onefile',                          # Single EXE file
    '--windowed',                         # No console window
    '--name=DataAnalystTool',             # EXE name
    '--clean',                            # Clean cache
    f'--distpath={os.path.join(base_dir, "dist")}',
    f'--workpath={os.path.join(base_dir, "build")}',
    f'--specpath={base_dir}',
    '--add-data=data;data',               # Include sample data
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=seaborn',
    '--hidden-import=openpyxl',
    '--hidden-import=PIL',
    '--hidden-import=sklearn',            # If used in future
    '--collect-all=matplotlib',
    '--collect-all=seaborn',
]

# Add icon if exists
if os.path.exists(icon_path):
    args.append(f'--icon={icon_path}')

print("Building standalone EXE...")
print(f"Main script: {main_script}")
print(f"Output directory: {os.path.join(base_dir, 'dist')}")
print("\nThis may take a few minutes...\n")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\n✅ Build complete!")
print(f"📦 EXE location: {os.path.join(base_dir, 'dist', 'DataAnalystTool.exe')}")
print("\n💡 You can now distribute the EXE file independently!")
