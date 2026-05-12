@echo off
echo ========================================
echo   Campus Safety - Windows Server 2019
echo ========================================
echo.

net session >nul 2>nul
if %errorLevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    pause
    exit /b 1
)

set PROJECT_DIR=C:\www\campus_safety

echo [Step 1/8] Checking software...
echo.

python --version >nul 2>nul
if %errorLevel% neq 0 (
    echo [!] Python not installed
    pause
    exit /b 1
)
echo [OK] Python
python --version

node --version >nul 2>nul
if %errorLevel% neq 0 (
    echo [!] Node.js not installed
    pause
    exit /b 1
)
echo [OK] Node.js
node --version

reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>nul
if %errorLevel% neq 0 (
    echo [!] VC++ Redistributable not installed
    pause
    exit /b 1
)
echo [OK] VC++ Redistributable

if exist C:\nginx\nginx.exe (
    echo [OK] Nginx
) else (
    echo [!] Nginx not found at C:\nginx\nginx.exe
    pause
    exit /b 1
)

if exist C:\Windows\nssm.exe (
    echo [OK] NSSM
) else (
    echo [!] NSSM not found at C:\Windows\nssm.exe
    pause
    exit /b 1
)

echo.
echo [Step 2/8] Creating directories...
if not exist "C:\www" mkdir "C:\www"
if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"
if not exist "%PROJECT_DIR%\backend" mkdir "%PROJECT_DIR%\backend"
if not exist "%PROJECT_DIR%\web-admin" mkdir "%PROJECT_DIR%\web-admin"
if not exist "%PROJECT_DIR%\backend\logs" mkdir "%PROJECT_DIR%\backend\logs"
echo [OK] Done

echo.
echo [Step 3/8] File check...
echo   backend dir:
if exist "%PROJECT_DIR%\backend\manage.py" (echo   [OK] manage.py found) else (echo   [!] manage.py NOT found)
echo   frontend dist:
if exist "%PROJECT_DIR%\web-admin\dist\index.html" (echo   [OK] dist found) else (echo   [!] dist NOT found)
echo   deploy files:
if exist "%PROJECT_DIR%\deploy\windows\.env.production" (echo   [OK] .env.production found) else (echo   [!] .env.production NOT found)
echo   Press any key to continue...
pause >nul

echo.
echo [Step 4/8] Setup .env...
if exist "%PROJECT_DIR%\deploy\windows\.env.production" (
    copy /Y "%PROJECT_DIR%\deploy\windows\.env.production" "%PROJECT_DIR%\backend\.env"
    echo [OK] .env copied to backend\.env
    echo.
    echo ############################################
    echo   NOW EDIT: %PROJECT_DIR%\backend\.env
    echo   - DJANGO_SECRET_KEY
    echo   - DJANGO_ALLOWED_HOSTS
    echo   - CORS_ORIGINS
    echo ############################################
    echo.
    echo   Press any key after editing .env...
    pause >nul
) else (
    echo [!] .env.production not found, skipping
)

echo.
echo [Step 5/8] Python environment...
cd /d "%PROJECT_DIR%\backend"

if not exist "venv" (
    python -m venv venv
    echo [OK] venv created
) else (
    echo [OK] venv exists
)

call venv\Scripts\activate.bat
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Dependencies installed

echo.
echo [Step 6/8] Database init...
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput
echo [OK] Database ready

echo.
echo [Step 7/8] Create superuser...
echo.
python manage.py createsuperuser

echo.
echo [Step 8/8] Register Windows service...
echo.

echo import sys > "%PROJECT_DIR%\backend\run_production.py"
echo sys.path.insert(0, r'%PROJECT_DIR%\backend') >> "%PROJECT_DIR%\backend\run_production.py"
echo. >> "%PROJECT_DIR%\backend\run_production.py"
echo if __name__ == '__main__': >> "%PROJECT_DIR%\backend\run_production.py"
echo     from waitress import serve >> "%PROJECT_DIR%\backend\run_production.py"
echo     from campus_safety.wsgi import application >> "%PROJECT_DIR%\backend\run_production.py"
echo     print('=' * 50) >> "%PROJECT_DIR%\backend\run_production.py"
echo     print('Campus Safety API Server Starting') >> "%PROJECT_DIR%\backend\run_production.py"
echo     print('Listen: 0.0.0.0:8000') >> "%PROJECT_DIR%\backend\run_production.py"
echo     print('Threads: 4') >> "%PROJECT_DIR%\backend\run_production.py"
echo     print('=' * 50) >> "%PROJECT_DIR%\backend\run_production.py"
echo     serve(application, host='0.0.0.0', port=8000, threads=4, url_scheme='http') >> "%PROJECT_DIR%\backend\run_production.py"

C:\Windows\nssm.exe stop CampusSafetyAPI >nul 2>nul
C:\Windows\nssm.exe remove CampusSafetyAPI confirm >nul 2>nul

C:\Windows\nssm.exe install CampusSafetyAPI "%PROJECT_DIR%\backend\venv\Scripts\python.exe" "%PROJECT_DIR%\backend\run_production.py"
C:\Windows\nssm.exe set CampusSafetyAPI AppDirectory "%PROJECT_DIR%\backend"
C:\Windows\nssm.exe set CampusSafetyAPI DisplayName "Campus Safety API Server"
C:\Windows\nssm.exe set CampusSafetyAPI Description "Campus Safety Backend API (Waitress)"
C:\Windows\nssm.exe set CampusSafetyAPI Start SERVICE_AUTO_START
C:\Windows\nssm.exe set CampusSafetyAPI AppStdout "%PROJECT_DIR%\backend\logs\access.log"
C:\Windows\nssm.exe set CampusSafetyAPI AppStderr "%PROJECT_DIR%\backend\logs\error.log"
C:\Windows\nssm.exe set CampusSafetyAPI AppRotateFiles 1
C:\Windows\nssm.exe set CampusSafetyAPI AppRotateBytes 10485760
echo [OK] Service registered

echo.
echo ========================================
echo   Deploy Complete!
echo ========================================
echo.
echo   Next steps:
echo   1. nssm start CampusSafetyAPI
echo   2. Visit http://your-ip:8000/api/ to verify
echo   3. Copy nginx-campus-safety.conf to C:\nginx\conf\nginx.conf
echo   4. Edit C:\nginx\conf\nginx.conf (replace IP)
echo   5. Start: cd C:\nginx ^&^& nginx.exe
echo   6. Visit http://your-ip/ and login
echo.
pause
