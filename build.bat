@echo off
echo Building Data Analyst Tool - Standalone EXE
echo.
echo This will create a single executable file...
echo.

pyinstaller --onefile --windowed --name=DataAnalystTool --clean --add-data="data;data" --hidden-import=pandas --hidden-import=numpy --hidden-import=matplotlib --hidden-import=seaborn --hidden-import=openpyxl --collect-all=matplotlib --collect-all=seaborn src/main.py

echo.
echo ===================================
echo Build Complete!
echo ===================================
echo.
echo EXE file location: dist\DataAnalystTool.exe
echo.
pause
