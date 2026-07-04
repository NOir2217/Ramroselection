@echo off
echo ===================================================
echo   Installing Dependencies for Ramro Selection
echo ===================================================
echo.

:: 1. Install Backend Dependencies
echo [1/2] Installing backend Python dependencies...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: "python" command not found in your PATH. 
    echo Trying "py" command...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python is not installed or not added to your environment PATH variables.
        echo Please install Python and try again.
        echo.
    ) else (
        echo Installing via py -m pip...
        py -m pip install -r requirements.txt
    )
) else (
    echo Installing via pip...
    pip install -r requirements.txt
)

echo.

:: 2. Install Frontend Dependencies
echo [2/2] Installing frontend Node.js dependencies...
if exist "frontend" (
    cd frontend
    npm --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Node.js/npm is not installed or not added to your environment PATH variables.
        echo Please install Node.js and try again to set up the frontend dependencies.
    ) else (
        echo Running npm install in frontend...
        npm install
    )
    cd ..
) else (
    echo ERROR: "frontend" directory not found!
)

echo.
echo ===================================================
echo   Installation process completed!
echo ===================================================
pause
