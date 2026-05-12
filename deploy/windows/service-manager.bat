@echo off
chcp 65001 >nul
echo ========================================
echo   服务管理工具
echo ========================================
echo.
echo 请选择操作:
echo   1. 启动所有服务
echo   2. 停止所有服务
echo   3. 重启所有服务
echo   4. 查看服务状态
echo   5. 退出
echo.
set /p choice=请输入选项 (1-5):

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" exit /b 0
goto end

:start
echo.
echo [启动服务]
nssm start CampusSafetyAPI
echo 启动 Nginx...
cd /d C:\nginx
start nginx
echo [√] 所有服务已启动
goto end

:stop
echo.
echo [停止服务]
nssm stop CampusSafetyAPI
echo 停止 Nginx...
nginx -s quit
echo [√] 所有服务已停止
goto end

:restart
echo.
echo [重启服务]
nssm restart CampusSafetyAPI
nginx -s reload
echo [√] 所有服务已重启
goto end

:status
echo.
echo [服务状态]
echo.
echo --- CampusSafetyAPI (Django) ---
sc query CampusSafetyAPI | findstr "STATE"
echo.
echo --- Nginx ---
tasklist /FI "IMAGENAME eq nginx.exe" 2>nul | find /I "nginx.exe" >nul
if %errorLevel%==0 (
    echo 状态: 运行中
) else (
    echo 状态: 已停止
)
echo.
goto end

:end
echo.
pause
