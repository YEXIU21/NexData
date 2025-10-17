@echo off
echo.
echo ============================================================
echo       NexData v3.1 - Professional EXE Builder
echo       Shopify Edition - Enhanced UX Edition
echo ============================================================
echo.
echo This will create a standalone executable file...
echo No Python installation required for end users!
echo.
echo Build process will take 3-5 minutes...
echo.
pause

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Starting build process...
echo.

REM Run the Python build script
python build_exe.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo                  BUILD COMPLETE!
echo ============================================================
echo.
echo EXE Location: ..\dist\NexData.exe
echo.
echo You can now distribute NexData.exe to users!
echo No Python installation required on their systems.
echo.
pause
