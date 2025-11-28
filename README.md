# 用户账单管理系统

一个基于 Vue3 + FastAPI + MySQL 的前后端分离的用户账单管理系统。

## 项目结构

```
.
├── backend/              # 后端 FastAPI 项目
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置文件
│   ├── database.py      # 数据库连接
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic 模式
│   ├── auth.py          # 认证相关
│   ├── routers/         # 路由模块
│   │   ├── auth.py      # 认证路由
│   │   └── bills.py     # 账单路由
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端 Vue3 项目
│   ├── src/
│   │   ├── api/         # API 接口
│   │   ├── stores/      # Pinia 状态管理
│   │   ├── router/      # 路由配置
│   │   ├── views/       # 页面组件
│   │   ├── App.vue      # 根组件
│   │   └── main.js      # 入口文件
│   ├── package.json     # 前端依赖
│   └── vite.config.js   # Vite 配置
└── database/
    └── schema.sql       # 数据库表结构
```

## 数据库表结构

### 1. 用户表 (users)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INT | 用户ID | 主键，自增 |
| username | VARCHAR(50) | 用户名 | 唯一，非空 |
| email | VARCHAR(100) | 邮箱 | 唯一，非空 |
| password_hash | VARCHAR(255) | 密码哈希 | 非空 |
| created_at | DATETIME | 创建时间 | 默认当前时间 |
| updated_at | DATETIME | 更新时间 | 自动更新 |

**索引：**
- `idx_username`: 用户名索引
- `idx_email`: 邮箱索引

### 2. 账单表 (bills)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INT | 账单ID | 主键，自增 |
| user_id | INT | 用户ID | 外键，关联 users.id |
| title | VARCHAR(200) | 账单标题 | 非空 |
| amount | DECIMAL(10,2) | 金额 | 非空 |
| category | VARCHAR(50) | 分类 | 非空（收入/支出） |
| type | VARCHAR(50) | 类型 | 非空（餐饮、交通、工资等） |
| description | TEXT | 描述 | 可选 |
| bill_date | DATE | 账单日期 | 非空 |
| created_at | DATETIME | 创建时间 | 默认当前时间 |
| updated_at | DATETIME | 更新时间 | 自动更新 |

**索引：**
- `idx_user_id`: 用户ID索引
- `idx_bill_date`: 账单日期索引
- `idx_category`: 分类索引

**外键：**
- `user_id` → `users.id` (CASCADE 删除)

## 后端接口清单

### 认证相关接口 (`/api/auth`)

#### 1. 用户注册
- **路径**: `POST /api/auth/register`
- **描述**: 注册新用户
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **响应**: `UserResponse` (201)

#### 2. 用户登录
- **路径**: `POST /api/auth/login`
- **描述**: 用户登录，获取访问令牌
- **请求体**: `FormData` (username, password)
- **响应**: 
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

#### 3. 获取当前用户信息
- **路径**: `GET /api/auth/me`
- **描述**: 获取当前登录用户信息
- **认证**: 需要 Bearer Token
- **响应**: `UserResponse`

### 账单相关接口 (`/api/bills`)

#### 1. 创建账单
- **路径**: `POST /api/bills`
- **描述**: 创建新账单
- **认证**: 需要 Bearer Token
- **请求体**:
  ```json
  {
    "title": "string",
    "amount": 0.00,
    "category": "收入|支出",
    "type": "string",
    "description": "string (可选)",
    "bill_date": "YYYY-MM-DD"
  }
  ```
- **响应**: `BillResponse` (201)

#### 2. 获取账单列表
- **路径**: `GET /api/bills`
- **描述**: 获取当前用户的账单列表
- **认证**: 需要 Bearer Token
- **查询参数**:
  - `skip`: int (默认: 0) - 跳过数量
  - `limit`: int (默认: 100) - 返回数量
  - `category`: string (可选) - 分类筛选
  - `start_date`: date (可选) - 开始日期
  - `end_date`: date (可选) - 结束日期
- **响应**: `BillResponse[]`

#### 3. 获取账单详情
- **路径**: `GET /api/bills/{bill_id}`
- **描述**: 获取指定账单的详细信息
- **认证**: 需要 Bearer Token
- **响应**: `BillResponse`

#### 4. 更新账单
- **路径**: `PUT /api/bills/{bill_id}`
- **描述**: 更新指定账单信息
- **认证**: 需要 Bearer Token
- **请求体**: `BillUpdate` (所有字段可选)
- **响应**: `BillResponse`

#### 5. 删除账单
- **路径**: `DELETE /api/bills/{bill_id}`
- **描述**: 删除指定账单
- **认证**: 需要 Bearer Token
- **响应**: 204 No Content

#### 6. 获取账单统计
- **路径**: `GET /api/bills/statistics/summary`
- **描述**: 获取账单统计信息（总收入、总支出、余额、数量）
- **认证**: 需要 Bearer Token
- **查询参数**:
  - `start_date`: date (可选) - 开始日期
  - `end_date`: date (可选) - 结束日期
- **响应**:
  ```json
  {
    "total_income": 0.00,
    "total_expense": 0.00,
    "balance": 0.00,
    "count": 0
  }
  ```

## 前端核心组件

### 1. 认证相关组件

#### Login.vue - 登录页面
- **功能**: 用户登录
- **位置**: `src/views/Login.vue`
- **特性**:
  - 表单验证
  - 错误提示
  - 自动跳转

#### Register.vue - 注册页面
- **功能**: 用户注册
- **位置**: `src/views/Register.vue`
- **特性**:
  - 表单验证（用户名、邮箱、密码确认）
  - 密码强度检查
  - 注册成功后跳转登录

### 2. 账单管理组件

#### Bills.vue - 账单管理页面
- **功能**: 账单的增删改查和统计
- **位置**: `src/views/Bills.vue`
- **主要功能**:
  - **统计卡片**: 显示总收入、总支出、余额、账单数量
  - **筛选功能**: 按分类、日期范围筛选
  - **账单列表**: 表格展示所有账单
  - **新增/编辑**: 对话框形式的新增和编辑账单
  - **删除功能**: 带确认的删除操作

### 3. 状态管理

#### auth.js - 认证状态管理
- **位置**: `src/stores/auth.js`
- **功能**:
  - 用户登录/注册
  - Token 管理
  - 用户信息存储
  - 登录状态检查

### 4. API 接口封装

#### axios.js - HTTP 客户端配置
- **位置**: `src/api/axios.js`
- **功能**:
  - 请求拦截器（自动添加 Token）
  - 响应拦截器（处理 401 错误）

#### auth.js - 认证 API
- **位置**: `src/api/auth.js`
- **接口**:
  - `login()` - 登录
  - `register()` - 注册
  - `getCurrentUser()` - 获取当前用户

#### bills.js - 账单 API
- **位置**: `src/api/bills.js`
- **接口**:
  - `getBills()` - 获取账单列表
  - `getBill()` - 获取账单详情
  - `createBill()` - 创建账单
  - `updateBill()` - 更新账单
  - `deleteBill()` - 删除账单
  - `getStatistics()` - 获取统计信息

## 环境配置

### 后端配置

1. 安装依赖:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 配置数据库:
   - 创建 MySQL 数据库
   - 执行 `database/schema.sql` 创建表结构
   - 修改 `backend/config.py` 中的数据库配置

3. 运行后端:
   ```bash
   cd backend
   python main.py
   # 或
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 前端配置

1. 安装依赖:
   ```bash
   cd frontend
   npm install
   ```

2. 运行前端:
   ```bash
   npm run dev
   ```

3. 构建生产版本:
   ```bash
   npm run build
   ```

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Web 框架
- **SQLAlchemy**: ORM 框架
- **PyMySQL**: MySQL 数据库驱动
- **JWT**: 用户认证
- **Pydantic**: 数据验证

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Element Plus**: UI 组件库
- **Axios**: HTTP 客户端
- **Vite**: 构建工具

## 功能特性

- ✅ 用户注册和登录
- ✅ JWT 身份认证
- ✅ 账单的增删改查
- ✅ 账单分类（收入/支出）
- ✅ 账单类型管理
- ✅ 日期筛选
- ✅ 统计信息展示
- ✅ 响应式设计
- ✅ 前后端分离架构

## 注意事项

1. **安全性**: 
   - 生产环境请修改 `SECRET_KEY`
   - 使用环境变量管理敏感配置
   - 启用 HTTPS

2. **数据库**:
   - 定期备份数据库
   - 生产环境使用连接池

3. **CORS**:
   - 根据实际部署情况调整 CORS 配置

## 许可证

MIT License
