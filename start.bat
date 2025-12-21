@echo off
REM ============================================
REM LLM Council - Quick Start Script
REM ============================================

echo.
echo ========================================
echo   LLM Council - Quick Start
echo ========================================
echo.

echo Checking system status...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnose.ps1" 2>NUL

echo.
echo ========================================
echo   Choose an option:
echo ========================================
echo.
echo 1. Start EVERYTHING (Backend + Frontend + BFF Demo)
echo 2. Start Backend only (Port 8001)
echo 3. Start Frontend only (JWT-based, Port 5173)
echo 4. Start BFF Demo only (Port 5174)
echo 5. Open Applications in Browser
echo 6. Stop ALL servers
echo 7. Run Diagnostics
echo 8. Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto start_bff
if "%choice%"=="5" goto open_browser
if "%choice%"=="6" goto stop_all
if "%choice%"=="7" goto diagnostics
if "%choice%"=="8" goto end

:start_all
echo.
echo Starting all services...
start "Backend (Port 8001)" powershell -NoExit -Command "cd '%~dp0'; uv run python -m backend.main"
timeout /t 3 /nobreak >nul
start "Frontend (Port 5173)" powershell -NoExit -Command "cd '%~dp0frontend'; npm run dev"
timeout /t 2 /nobreak >nul
start "BFF Demo (Port 5174)" powershell -NoExit -Command "cd '%~dp0frontend-bff'; npm run dev"
echo.
echo All services started in separate windows!
echo.
echo - Backend:  http://localhost:8001
echo - Frontend: http://localhost:5173
echo - BFF Demo: http://localhost:5174
echo.
pause
goto end

:start_backend
echo.
echo Starting backend on port 8001...
cd "%~dp0"
uv run python -m backend.main
goto end

:start_frontend
echo.
echo Starting frontend on port 5173...
cd "%~dp0frontend"
npm run dev
goto end

:start_bff
echo.
echo Starting BFF demo on port 5174...
cd "%~dp0frontend-bff"
npm run dev
goto end

:open_browser
echo.
echo Opening applications in browser...
start http://localhost:8001/docs
timeout /t 1 /nobreak >nul
start http://localhost:5173
timeout /t 1 /nobreak >nul
start http://localhost:5174
echo.
echo Opened:
echo - API Docs:  http://localhost:8001/docs
echo - Frontend:  http://localhost:5173
echo - BFF Demo:  http://localhost:5174
echo.
pause
goto end

:stop_all
echo.
echo Stopping all servers...
powershell -Command "Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue"
echo All servers stopped!
echo.
pause
goto end

:diagnostics
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnose.ps1"
echo.
pause
goto end

:end
echo.
echo Goodbye!
