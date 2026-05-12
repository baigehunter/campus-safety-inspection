@echo off
chcp 65001 >nul
echo ========================================
echo   校园安全管理平台 - Windows Server 2012 部署脚本
echo   适用: Windows Server 2012 / 2012 R2
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 请以管理员身份运行此脚本！
    pause
    exit /b 1
)

:: 设置项目路径
set PROJECT_DIR=C:\www\campus_safety

echo ============================================
echo   重要：Windows Server 2012 版本说明
echo ============================================
echo.
echo   Windows Server 2012（非R2）→ 使用 Python 3.8.19
echo   Windows Server 2012 R2    → 可使用 Python 3.11.9
echo.
echo   前端（Vue/小程序）请在开发机上构建后复制 dist 到服务器
echo   服务器上不需要安装 Node.js
echo.
echo 按任意键继续...
pause >nul

echo.
echo [步骤 1/7] 检查已安装软件...
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Python 未安装
    echo.
    echo     Server 2012 非R2: 下载 Python 3.8.19
    echo     https://www.python.org/ftp/python/3.8.19/python-3.8.19-amd64.exe
    echo.
    echo     Server 2012 R2: 下载 Python 3.11.9
    echo     https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo.
    echo     安装时务必勾选:
    echo     [√] Add Python to PATH
    echo     [√] pip
    echo     [√] py launcher
) else (
    echo [√] Python 已安装
    python --version
)

:: 检查 Nginx
nginx -v >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Nginx 未安装
    echo     请从 https://nginx.org/en/download.html 下载
    echo     解压到 C:\nginx 目录
) else (
    echo [√] Nginx 已安装
)

:: 检查 NSSM
nssm version >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] NSSM 未安装
    echo     请从 https://nssm.cc/download 下载
    echo     将 nssm.exe 复制到 C:\Windows\System32
) else (
    echo [√] NSSM 已安装
)

echo.
echo 按任意键继续...
pause >nul

echo.
echo [步骤 2/7] 创建项目目录...
if not exist "C:\www" mkdir "C:\www"
if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"
if not exist "%PROJECT_DIR%\backend" mkdir "%PROJECT_DIR%\backend"
if not exist "%PROJECT_DIR%\web-admin" mkdir "%PROJECT_DIR%\web-admin"
if not exist "%PROJECT_DIR%\backend\logs" mkdir "%PROJECT_DIR%\backend\logs"
if not exist "%PROJECT_DIR%\backend\media" mkdir "%PROJECT_DIR%\backend\media"
echo [√] 目录创建完成

echo.
echo [步骤 3/7] 请将文件复制到服务器:
echo.
echo   后端代码复制到:
echo     %PROJECT_DIR%\backend\
echo     (包含 manage.py, campus_safety/, safety/, requirements.txt 等)
echo.
echo   前端构建产物复制到:
echo     %PROJECT_DIR%\web-admin\dist\
echo     (在开发机上运行 npm run build 后复制整个 dist 目录)
echo.
echo   环境配置复制到:
echo     %PROJECT_DIR%\backend\.env
echo     (从 deploy\windows\.env.production 复制并修改)
echo.
echo 按任意键继续（请先完成文件复制）...
pause >nul

echo.
echo [步骤 4/7] 配置生产环境变量...
if exist "%PROJECT_DIR%\backend\.env" (
    echo [√] 已找到 .env 文件
    echo.
    echo [!] 请确认 .env 中以下配置已正确填写:
    echo     - DJANGO_SECRET_KEY: 强随机密钥（至少50位）
    echo     - DJANGO_DEBUG: 设为 False
    echo     - DJANGO_ALLOWED_HOSTS: 服务器域名和IP
    echo     - CORS_ORIGINS: 前端访问地址
    echo.
    echo 按任意键继续...
    pause >nul
) else (
    echo [!] 未找到 .env 文件！
    echo     请将 deploy\windows\.env.production 复制到 %PROJECT_DIR%\backend\.env
    echo     并修改其中的配置项
    echo.
    echo 按任意键继续（请先创建 .env 文件）...
    pause >nul
)

echo.
echo [步骤 5/7] 配置后端 Python 环境...
cd /d "%PROJECT_DIR%\backend"

:: 创建虚拟环境
if not exist "venv" (
    python -m venv venv
    echo [√] 虚拟环境创建完成
) else (
    echo [√] 虚拟环境已存在
)

:: 激活虚拟环境并安装依赖
call venv\Scripts\activate
echo 正在安装 Python 依赖（可能需要几分钟）...
pip install --upgrade pip
pip install Django==4.2.11
pip install djangorestframework==3.15.1
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.3.1
pip install django-filter==24.2
pip install PyJWT==2.8.0
pip install Pillow==10.2.0
pip install waitress==2.1.2
pip install python-dotenv==1.0.1
:: cryptography 需要编译，先尝试预编译包，失败则跳过（JWT 用 PyJWT 即可）
pip install cryptography==41.0.7 2>nul || echo [!] cryptography 安装失败，不影响核心功能
:: MySQL 驱动（可选，使用 MySQL 时取消注释）
:: pip install mysqlclient==2.2.4
echo [√] 依赖安装完成

echo.
echo [步骤 6/7] 初始化数据库...
python manage.py migrate
python manage.py collectstatic --noinput
echo [√] 数据库初始化完成

echo.
echo [步骤 7/7] 创建管理员账户并注册服务...
echo.
echo 请创建管理员账户:
python manage.py createsuperuser

echo.
echo 正在注册 Windows 服务...

:: 创建 Waitress 启动脚本
(
echo import sys
echo sys.path.insert(0, r'%PROJECT_DIR%\backend'^)
echo.
echo if __name__ == '__main__':
echo     from waitress import serve
echo     from campus_safety.wsgi import application
echo     print('Starting production server on 0.0.0.0:8000...'^)
echo     serve(application, host='0.0.0.0', port=8000, threads=4^)
) > "%PROJECT_DIR%\backend\run_production.py"

:: 注册服务
nssm install CampusSafetyAPI "%PROJECT_DIR%\backend\venv\Scripts\python.exe" "%PROJECT_DIR%\backend\run_production.py"
nssm set CampusSafetyAPI AppDirectory "%PROJECT_DIR%\backend"
nssm set CampusSafetyAPI DisplayName "Campus Safety API Server"
nssm set CampusSafetyAPI Description "校园安全管理平台后端API服务（Waitress）"
nssm set CampusSafetyAPI Start SERVICE_AUTO_START
nssm set CampusSafetyAPI AppStdout "%PROJECT_DIR%\backend\logs\access.log"
nssm set CampusSafetyAPI AppStderr "%PROJECT_DIR%\backend\logs\error.log"
echo [√] 服务注册完成

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 后续步骤:
echo 1. 启动后端服务: nssm start CampusSafetyAPI
echo 2. 配置Nginx: 将 nginx-campus-safety.conf 内容复制到 Nginx 配置
echo 3. 启动Nginx: cd C:\nginx ^&^& start nginx
echo 4. 访问: http://服务器IP
echo.
pause
