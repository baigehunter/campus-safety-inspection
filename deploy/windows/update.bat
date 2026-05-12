@echo off
chcp 65001 >nul
echo ========================================
echo   项目更新脚本
echo ========================================
echo.

set PROJECT_DIR=C:\www\campus_safety

echo [1/4] 拉取最新代码...
cd /d "%PROJECT_DIR%"
git pull
echo [√] 代码更新完成

echo.
echo [2/4] 更新后端依赖...
cd /d "%PROJECT_DIR%\backend"
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
echo [√] 后端更新完成

echo.
echo [3/4] 重新构建前端...
cd /d "%PROJECT_DIR%\web-admin"
call npm install
call npm run build

cd /d "%PROJECT_DIR%\miniprogram"
call npm install
call npm run build:mp-weixin
echo [√] 前端构建完成

echo.
echo [4/4] 重启服务...
nssm restart CampusSafetyAPI
nginx -s reload
echo [√] 服务重启完成

echo.
echo ========================================
echo   更新完成！
echo ========================================
echo.
pause
