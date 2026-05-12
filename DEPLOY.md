# 校园安全管理平台 — 部署文档

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| 操作系统 | Windows Server 2019 | 64位 |
| Python | 3.13.5 | 需勾选 Add Python to PATH |
| Node.js | 24.15.0 | 用于构建前端 |
| Nginx | 1.30.0 | 反向代理 + 静态文件服务 |
| NSSM | 2.24 | Windows 服务管理器 |
| VC++ Redist | 2015-2022 | Pillow 等 C 扩展需要 |

---

## 一、服务器准备

### 1.1 防火墙开放端口

```cmd
netsh advfirewall firewall add rule name="HTTP" dir=in action=allow protocol=TCP localport=80
netsh advfirewall firewall add rule name="HTTPS" dir=in action=allow protocol=TCP localport=443
```

### 1.2 安装基础软件

#### Python 3.13.5
```
下载: https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe
安装时勾选:
  [√] Add Python to PATH
  [√] Install pip

验证: python --version   # 应显示 Python 3.13.5
```

#### Node.js 24.15.0
```
下载: https://nodejs.org/dist/v24.15.0/node-v24.15.0-x64.msi
默认安装即可

验证: node --version     # 应显示 v24.15.0
```

#### Visual C++ Redistributable
```
下载: https://aka.ms/vs/17/release/vc_redist.x64.exe
安装: 双击运行，按提示完成

验证: reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version
```

如果不安装 VC++，Pillow 等库的 C 扩展加载会报 DLL 错误。

#### Nginx 1.30.0
```
1. 下载: https://nginx.org/download/nginx-1.30.0.zip
2. 解压到 C:\nginx
3. 验证: C:\nginx\nginx.exe -v
```

#### NSSM 2.24
```
1. 下载: https://nssm.cc/release/nssm-2.24.zip
2. 解压，将 nssm-2.24\win64\nssm.exe 复制到 C:\Windows
3. 验证: nssm version
```

---

## 二、开发机构建前端

在你的开发机上执行（**不是在服务器上**）：

```cmd
cd campus_safety\web-admin
npm install
npm run build
```

构建产物在 `web-admin\dist\` 目录下（约 2.6 MB）。

> 也可直接在服务器上构建（已安装 Node.js），但在开发机上构建更省事。

---

## 三、复制文件到服务器

将以下目录/文件复制到服务器 `C:\www\campus_safety\`：

```
C:\www\campus_safety\
├── backend\                    ← 整个 backend 目录
│   ├── manage.py
│   ├── requirements.txt
│   ├── campus_safety\          (settings.py, urls.py, wsgi.py)
│   ├── safety\                 (models.py, views.py, serializers.py, ...)
│   └── migrations\
├── web-admin\
│   └── dist\                   ← 第二步构建产物
└── deploy\
    └── windows\
        ├── install.bat
        ├── service-manager.bat
        ├── build-frontend.bat
        ├── nginx-campus-safety.conf
        └── .env.production
```

**注意**：
- 不要把开发机的 `db.sqlite3` 复制到服务器（服务器会重建）
- 不要把 `backend\venv\` 目录复制过去（服务器上重建）

---

## 四、配置 .env 文件

### 4.1 生成强随机密钥

在服务器上执行：
```cmd
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

复制输出的密钥字符串（不含 `#` 符号）。

### 4.2 编辑 .env

打开 `C:\www\campus_safety\deploy\windows\.env.production`，修改以下内容：

```ini
# ===== 必填项 =====

# 粘贴第三步生成的密钥
DJANGO_SECRET_KEY=粘贴你的强随机密钥

# 生产环境（重要！）
DJANGO_DEBUG=False

# 服务器域名和IP，多个用逗号分隔
# 如无域名只填IP: DJANGO_ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1
DJANGO_ALLOWED_HOSTS=你的域名.com,你的服务器IP,localhost,127.0.0.1

# 前端访问地址
CORS_ORIGINS=http://你的域名.com,http://你的服务器IP
```

`.env` 文件中的值**不要加引号**，除非值本身包含 `#` 符号。

---

## 五、运行部署脚本

在服务器上**以管理员身份**打开 cmd：

```cmd
cd C:\www\campus_safety\deploy\windows
install.bat
```

脚本会自动完成：
1. 检查基础软件是否就绪
2. 创建项目目录结构
3. 将 `.env.production` 复制为 `backend\.env`（然后**暂停让你编辑**）
4. 创建 Python 虚拟环境并安装依赖
5. 运行数据库迁移
6. 提示创建超级管理员账户
7. 将后端注册为 Windows 服务 `CampusSafetyAPI`

在步骤 4 暂停时，请确认 `C:\www\campus_safety\backend\.env` 中所有必填项已修改，**尤其是** `ALLOWED_HOSTS` 和 `CORS_ORIGINS`。

---

## 六、配置 Nginx

```cmd
:: 复制配置
copy C:\www\campus_safety\deploy\windows\nginx-campus-safety.conf C:\nginx\conf\nginx.conf
```

打开 `C:\nginx\conf\nginx.conf`，将所有的 `your-domain.com` 替换为你的实际域名或 IP：

```
server_name 你的域名或IP;
```

---

## 七、启动服务

```cmd
:: 1. 启动后端 Windows 服务
nssm start CampusSafetyAPI

:: 2. 检查后端状态
sc query CampusSafetyAPI

:: 3. 启动 Nginx
cd C:\nginx
nginx.exe

:: 4. 检查 Nginx 是否启动
tasklist /FI "IMAGENAME eq nginx.exe"
```

---

## 八、验证部署

### 8.1 验证后端 API

```
浏览器打开: http://服务器IP:8000/api/
应显示 Django REST Framework API 根页面
```

### 8.2 验证登录

```
浏览器打开: http://服务器IP/
应显示登录页面
使用安装时创建的超级管理员账户登录
```

### 8.3 命令行测试登录

```cmd
curl -X POST http://服务器IP:8000/api/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"你的密码\"}"
```

如果返回包含 `access` 和 `refresh` 的 JSON，则后端登录正常。

---

## 九、HTTPS 配置（微信小程序需要）

微信小程序要求后端 API 必须使用 HTTPS。

### 9.1 申请 SSL 证书

可使用 Let's Encrypt 免费证书，推荐 Windows 上的自动化工具：

```
下载 win-acme: https://www.win-acme.com/
```

按向导申请证书，记下证书路径（通常为 `C:\ProgramData\win-acme\...`）。

### 9.2 配置 Nginx HTTPS

编辑 `C:\nginx\conf\nginx.conf`，取消 443 端口 server 块的注释，并填入证书路径：

```nginx
server {
    listen 443 ssl;
    server_name 你的域名.com;

    ssl_certificate     C:/ssl/证书文件.pem;
    ssl_certificate_key C:/ssl/私钥文件.key;

    # ... 其余配置保持不变
}
```

### 9.3 重载 Nginx

```cmd
C:\nginx\nginx.exe -s reload
```

---

## 十、日常运维

### 日志查看

```cmd
:: 后端访问日志
type C:\www\campus_safety\backend\logs\access.log

:: 后端错误日志
type C:\www\campus_safety\backend\logs\error.log

:: Nginx 日志
type C:\nginx\logs\access.log
type C:\nginx\logs\error.log
```

### 服务管理

```cmd
nssm start CampusSafetyAPI     # 启动
nssm stop CampusSafetyAPI      # 停止
nssm restart CampusSafetyAPI   # 重启
sc query CampusSafetyAPI       # 查看状态
```

或使用 `deploy\windows\service-manager.bat` 交互式管理。

### 更新代码

```cmd
:: 1. 停止服务
nssm stop CampusSafetyAPI

:: 2. 替换 backend 文件

:: 3. 更新依赖（如有新增）
cd C:\www\campus_safety\backend
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate

:: 4. 重新构建前端（开发机执行）
cd web-admin && npm run build

:: 5. 替换 web-admin\dist 目录

:: 6. 启动服务
nssm start CampusSafetyAPI
```

---

## 十一、常见问题排查

### 登录时显示"无法连接服务器"

1. 检查 Nginx 是否启动：`tasklist /FI "IMAGENAME eq nginx.exe"`
2. 检查后端服务：`sc query CampusSafetyAPI`
3. 检查防火墙是否开放 80 端口

### 登录时显示"请求被服务器拒绝(400)"

**这是 ALLOWED_HOSTS 配置问题**——最常见的部署故障。

确认 `C:\www\campus_safety\backend\.env` 中：
```
DJANGO_ALLOWED_HOSTS=实际IP或域名,localhost,127.0.0.1
```
确认 `DJANGO_DEBUG=False`（DEBUG=True 时不检查 ALLOWED_HOSTS，但生产环境不应开启）。

### 浏览器控制台看到 CORS 错误

确认 `.env` 中：
```
CORS_ORIGINS=http://你的前端地址
```
地址必须包含 `http://` 或 `https://` 前缀，且与浏览器访问地址完全一致。

### 登录成功但页面反复跳回登录页

Token 生成或验证失败。检查：
1. `.env` 中 `DJANGO_SECRET_KEY` 是否包含 `#` 符号（会被当作注释截断）
2. 后端日志中是否有 JWT 相关报错

### DLL load failed / 找不到指定的程序

缺少 VC++ Redistributable。执行：
```
https://aka.ms/vs/17/release/vc_redist.x64.exe
```

### 静态文件 404（CSS/JS 加载不出来）

```cmd
cd C:\www\campus_safety\backend
call venv\Scripts\activate
python manage.py collectstatic --noinput
```

---

## 部署检查清单

| 检查项 | 命令或方法 |
|--------|-----------|
| [ ] Python 3.13.5 | `python --version` |
| [ ] Node.js 24.15 | `node --version` |
| [ ] VC++ Redist | `reg query HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64 /v Version` |
| [ ] Nginx 1.30 | `C:\nginx\nginx.exe -v` |
| [ ] NSSM 2.24 | `nssm version` |
| [ ] .env 已修改 | 查看 `C:\www\campus_safety\backend\.env` |
| [ ] ALLOWED_HOSTS 含域名/IP | 查看 `.env` |
| [ ] CORS_ORIGINS 含前端地址 | 查看 `.env` |
| [ ] SECRET_KEY 已替换 | 查看 `.env`，不应含 `#` |
| [ ] DEBUG=False | 查看 `.env` |
| [ ] 后端服务运行中 | `sc query CampusSafetyAPI` → RUNNING |
| [ ] Nginx 运行中 | `tasklist /FI "IMAGENAME eq nginx.exe"` |
| [ ] 防火墙开放80端口 | 浏览器访问 `http://IP/` |
| [ ] 前端构建产物存在 | 查看 `C:\www\campus_safety\web-admin\dist\index.html` |
| [ ] 可正常登录 | 打开网页，输入管理员账户测试 |
