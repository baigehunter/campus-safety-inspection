# 校园安全管理平台

## 项目概述
校园安全综合管理平台，实现校园安全数字化、可视化、闭环化管理。
- **电脑Web端**: 总管理后台（学校领导/安全管理员使用）
- **手机移动端**: 巡检端（保安/巡检员/班主任使用）

## 技术栈
- **后端**: Python 3.14 + Django 6.0 + Django REST Framework + MySQL 8.0
- **Web管理后台**: Vue3 + Element Plus + Vite + ECharts
- **移动端**: uniapp (微信小程序)

## 项目结构
```
campus_safety/
├── backend/          # Django后端API
│   ├── campus_safety/    # 项目配置
│   ├── safety/           # 核心业务模块
│   └── manage.py
├── web-admin/        # Vue3管理后台
│   ├── src/
│   │   ├── api/         # API接口
│   │   ├── views/       # 页面组件
│   │   ├── stores/      # 状态管理
│   │   └── router/      # 路由配置
│   └── package.json
└── miniprogram/      # 微信小程序
    ├── src/
    │   ├── pages/       # 页面
    │   └── utils/       # 工具函数
    └── package.json
```

## 快速启动

### 1. 后端启动
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install django djangorestframework django-cors-headers mysqlclient djangorestframework-simplejwt django-filter xlwt

# 配置数据库 (修改 campus_safety/settings.py 中的 DATABASES)
# 创建MySQL数据库: CREATE DATABASE campus_safety CHARACTER SET utf8mb4;

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动服务
python manage.py runserver 0.0.0.0:8000
```

### 2. Web管理后台启动
```bash
cd web-admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 微信小程序启动
```bash
cd miniprogram

# 安装依赖
npm install

# 使用HBuilderX或微信开发者工具打开项目
# 或运行: npm run dev:mp-weixin
```

## 核心功能

### Web管理后台
- 数据监控大屏（巡检统计、隐患统计、图表展示）
- 用户权限管理（多角色权限分级）
- 校园区域管理
- 巡检点位管理
- 巡检记录查询审核
- 安全隐患整改闭环管理
- 自动报表台账导出
- 操作日志查询

### 移动端小程序
- 账号登录
- 日常定点安全巡检拍照上报
- 安全隐患一键上报
- 整改任务接收处理
- 整改拍照复查提交
- 个人巡检历史记录查询

## 数据库表结构
- `safety_user` - 用户角色权限表
- `campus_area` - 校园区域信息表
- `inspection_point` - 巡检点位明细表
- `inspection_record` - 日常巡检记录表
- `hazard_report` - 安全隐患上报表
- `rectify_task` - 整改任务指派表
- `rectify_record` - 整改复查验收表
- `system_log` - 系统操作日志表

## API接口列表
| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | POST /api/login/ | 用户登录 |
| 用户 | GET/POST /api/users/ | 用户列表/创建 |
| 区域 | GET/POST /api/areas/ | 区域列表/创建 |
| 点位 | GET/POST /api/points/ | 点位列表/创建 |
| 巡检 | GET/POST /api/records/ | 巡检记录 |
| 隐患 | GET/POST /api/hazards/ | 隐患列表/上报 |
| 整改 | GET/POST /api/tasks/ | 整改任务 |
| 统计 | GET /api/dashboard/stats/ | 仪表盘统计 |
| 日志 | GET /api/logs/ | 操作日志 |

## 开发进度
- [x] 需求分析和技术选型
- [x] 项目基础结构搭建
- [x] 数据库模型设计
- [x] 后端API接口开发
- [x] Web管理后台前端开发
- [x] 微信小程序移动端开发
- [ ] 双端联调测试
- [ ] 项目部署上线

## 注意事项
1. 首次运行需配置MySQL数据库
2. 后端默认运行在 http://localhost:8000
3. Web前端默认运行在 http://localhost:5173
4. 小程序需在微信开发者工具中运行