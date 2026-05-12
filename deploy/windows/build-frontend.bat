@echo off
chcp 65001 >nul
echo ========================================
echo   构建前端项目
echo ========================================
echo.

set PROJECT_DIR=C:\www\campus_safety

echo [1/2] 构建Web管理后台...
cd /d "%PROJECT_DIR%\web-admin"
call npm install
call npm run build
if not exist "%PROJECT_DIR%\web-admin\dist" (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo [√] Web管理后台构建完成

echo.
echo [2/2] 构建微信小程序...
cd /d "%PROJECT_DIR%\miniprogram"
call npm install
call npm run build:mp-weixin
if not exist "%PROJECT_DIR%\miniprogram\dist\build\mp-weixin" (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo [√] 微信小程序构建完成

echo.
echo ========================================
echo   构建完成！
echo ========================================
echo.
echo Web管理后台: %PROJECT_DIR%\web-admin\dist
echo 微信小程序: %PROJECT_DIR%\miniprogram\dist\build\mp-weixin
echo.
echo 请将微信小程序目录导入微信开发者工具进行上传发布
echo.
pause
