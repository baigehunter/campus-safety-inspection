# 校园安全管理平台 - Windows Server 部署指南

## 目录

1. [环境要求](#1-环境要求)
2. [安装依赖软件](#2-安装依赖软件)
3. [上传项目代码](#3-上传项目代码)
4. [修改配置文件](#4-修改配置文件)
5. [运行部署脚本](#5-运行部署脚本)
6. [配置 Nginx](#6-配置-nginx)
7. [申请 SSL 证书](#7-申请-ssl-证书)
8. [发布微信小程序](#8-发布微信小程序)
9. [常见问题](#9-常见问题)

---

## 1. 环境要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Windows Server | 2016+ | 推荐 2019 或 2022 |
| Python | 3.11 或 3.12 | 不要使用 3.14（未发布） |
| Node.js | 18+ LTS | 推荐 20.x |
| Nginx | 1.24+ | Windows 版本 |
| NSSM | 最新版 | 服务管理工具 |
| MySQL/PostgreSQL | 可选 | 生产环境推荐，开发可用 SQLite |

---

## 2. 安装依赖软件

### 2.1 安装 Python 3.11

1. 下载: https://www.python.org/downloads/release/python-3119/
2. 选择 **Windows installer (64-bit)**
3. 安装时**务必勾选**:
   - ✅ Add Python 3.11 to PATH
   - ✅ Install pip

验证安装:
```cmd
python --version
pip --version
```

### 2.2 安装 Node.js

1. 下载: https://nodejs.org/
2. 选择 **LTS 版本** (推荐 20.x)
3. 一路下一步安装

验证安装:
```cmd
node --version
npm --version
```

### 2.3 安装 Nginx

1. 下载: https://nginx.org/en/download.html
2. 选择 **Stable version** → **nginx/Windows-x.x.x**
3. 解压到 `C:\nginx`
4. 将 `C:\nginx` 添加到系统 PATH

验证安装:
```cmd
nginx -v
```

### 2.4 安装 NSSM

1. 下载: https://nssm.cc/download
2. 解压后将 `nssm.exe` 复制到 `C:\Windows\System32`

验证安装:
```cmd
nssm version
```

---

## 3. 上传项目代码

### 方式一: 远程桌面复制

1. 远程桌面连接服务器
2. 直接复制项目文件夹到 `C:\www\campus_safety`

### 方式二: Git 克隆（推荐）

```cmd
# 安装 Git: https://git-scm.com/download/win
mkdir C:\www
cd C:\www
git clone <你的仓库地址> campus_safety
```

### 目录结构要求

```
C:\www\campus_safety\
├── backend\          # Django 后端
├── miniprogram\      # 微信小程序
├── web-admin\        # Web 管理后台
└── deploy\           # 部署脚本
```

---

## 4. 修改配置文件

### 4.1 修改后端配置

编辑 `C:\www\campus_safety\backend\campus_safety\settings.py`:

```python
# 生产环境设置
DEBUG = False

# 允许的主机（替换为你的域名或IP）
ALLOWED_HOSTS = ['你的域名', '你的服务器IP', 'localhost']

# 跨域设置
CORS_ALLOWED_ORIGINS = [
    "https://你的域名",
]

# 生产环境建议使用 MySQL 或 PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'campus_safety',
#         'USER': 'root',
#         'PASSWORD': '你的密码',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }
```

### 4.2 修改小程序请求地址

编辑 `C:\www\campus_safety\miniprogram\src\utils\request.ts`:

```typescript
function getBaseUrl(): string {
  // 小程序环境 - 使用服务器公网地址
  return 'https://你的域名/api'
}
```

---

## 5. 运行部署脚本

### 5.1 运行主安装脚本

1. 打开 **管理员权限** 的命令提示符
2. 执行:

```cmd
cd C:\www\campus_safety\deploy\windows
install.bat
```

脚本会自动:
- ✅ 检查依赖软件
- ✅ 创建 Python 虚拟环境
- ✅ 安装项目依赖
- ✅ 初始化数据库
- ✅ 创建管理员账户
- ✅ 注册 Windows 服务

### 5.2 构建前端

```cmd
build-frontend.bat
```

---

## 6. 配置 Nginx

### 6.1 编辑 Nginx 配置

1. 打开 `C:\nginx\conf\nginx.conf`
2. 在 `http { }` 块内添加:

```nginx
include conf.d/*.conf;
```

3. 创建目录并复制配置:

```cmd
mkdir C:\nginx\conf\conf.d
copy nginx-campus-safety.conf C:\nginx\conf\conf.d\
```

4. 修改 `nginx-campus-safety.conf` 中的:
   - `your-domain.com` → 你的域名
   - 路径确认正确

### 6.2 测试并启动 Nginx

```cmd
nginx -t
nginx
```

---

## 7. 申请 SSL 证书

微信小程序要求后端必须是 **HTTPS**。

### 7.1 百度云申请免费证书

1. 登录百度云控制台
2. 产品服务 → SSL 证书服务
3. 购买免费证书（有效期1年）
4. 填写域名信息，验证域名所有权
5. 下载 Nginx 格式证书

### 7.2 配置 HTTPS

1. 将证书文件放到 `C:\ssl\`:
   - `campus_safety.pem` (证书)
   - `campus_safety.key` (私钥)

2. 修改 `nginx-campus-safety.conf`:
   - 取消 HTTPS 配置部分的注释
   - 修改证书路径

3. 重载 Nginx:
```cmd
nginx -s reload
```

---

## 8. 发布微信小程序

### 8.1 上传代码

1. 打开微信开发者工具
2. 导入项目: `C:\www\campus_safety\miniprogram\dist\build\mp-weixin`
3. 点击 **上传** 按钮
4. 填写版本号和说明

### 8.2 提交审核

1. 登录微信公众平台
2. 版本管理 → 开发版本 → 提交审核
3. 审核通过后点击 **发布**

### 8.3 配置服务器域名

微信公众平台 → 开发 → 开发管理 → 服务器域名:

- request 合法域名: `https://你的域名`
- uploadFile 合法域名: `https://你的域名`
- downloadFile 合法域名: `https://你的域名`

---

## 9. 常见问题

### Q1: 服务无法启动

检查端口占用:
```cmd
netstat -ano | findstr :8000
netstat -ano | findstr :80
```

### Q2: 数据库迁移失败

手动执行:
```cmd
cd C:\www\campus_safety\backend
venv\Scripts\activate
python manage.py migrate
```

### Q3: 小程序请求失败

1. 确认服务器域名已配置 HTTPS
2. 确认微信公众平台已添加服务器域名白名单
3. 检查 Nginx 日志: `C:\nginx\logs\error.log`

### Q4: 静态文件 404

重新收集静态文件:
```cmd
cd C:\www\campus_safety\backend
venv\Scripts\activate
python manage.py collectstatic
```

---

## 服务管理

使用服务管理工具:
```cmd
service-manager.bat
```

或手动命令:
```cmd
# 启动后端
nssm start CampusSafetyAPI

# 停止后端
nssm stop CampusSafetyAPI

# 重启后端
nssm restart CampusSafetyAPI

# 启动 Nginx
nginx

# 停止 Nginx
nginx -s quit

# 重载 Nginx 配置
nginx -s reload
```

---

## 联系支持

如有问题，请检查日志文件:
- Django 日志: 控制台输出
- Nginx 日志: `C:\nginx\logs\`
