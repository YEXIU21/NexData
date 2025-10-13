# Build Scripts

This folder contains all scripts needed to build a standalone EXE file.

## 📦 Building the Application

### Quick Build (Recommended)

**Windows**:
```bash
cd build_scripts
build.bat
```

**Python Script** (Cross-platform):
```bash
cd build_scripts
python build_exe.py
```

### Manual Build

From project root:
```bash
pyinstaller --onefile --windowed --name=DataAnalystTool --clean \
    --add-data="data;data" \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=matplotlib \
    --hidden-import=seaborn \
    --hidden-import=openpyxl \
    --collect-all=matplotlib \
    --collect-all=seaborn \
    src/main.py
```

## 📁 Output

After building, the EXE will be located at:
```
../dist/DataAnalystTool.exe
```

## 📋 Build Files

- **`build.bat`** - Windows batch script for quick builds
- **`build_exe.py`** - Python script (works on all platforms)
- **`README.md`** - This file

## 🔧 Requirements

Before building, ensure:
1. All dependencies installed: `pip install -r requirements.txt`
2. PyInstaller installed (included in requirements.txt)
3. You're in the `build_scripts` directory

## 📊 Build Statistics

- **Build Time**: 2-5 minutes
- **EXE Size**: ~150-200 MB
- **Target**: Windows 64-bit

## 🐛 Troubleshooting

If build fails:
1. Ensure you're in `build_scripts` folder
2. Check all dependencies are installed
3. Try deleting `build/` and `dist/` folders
4. Run with `--debug` flag for more info

## 📚 Documentation

Full build instructions: [../docs/BUILD_INSTRUCTIONS.md](../docs/BUILD_INSTRUCTIONS.md)

---

**Last Updated**: January 2025
