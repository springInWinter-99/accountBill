# 快速启动指南

## 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ 或 MySQL 8.0+

## 步骤 1: 数据库设置

1. 创建数据库:
   ```sql
   CREATE DATABASE billing_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. 执行 SQL 脚本创建表结构:
   ```bash
   mysql -u root -p billing_system < database/schema.sql
   ```

## 步骤 2: 后端设置

1. 进入后端目录:
   ```bash
   cd backend
   ```

2. 创建虚拟环境（推荐）:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

4. 配置数据库连接:
   编辑 `backend/config.py` 或创建 `.env` 文件:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=billing_system
   SECRET_KEY=your-secret-key-here
   ```

5. 启动后端服务:
   ```bash
   python main.py
   # 或
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   后端服务将在 `http://localhost:8000` 启动

6. 验证后端:
   访问 `http://localhost:8000/docs` 查看 API 文档

## 步骤 3: 前端设置

1. 进入前端目录:
   ```bash
   cd frontend
   ```

2. 安装依赖:
   ```bash
   npm install
   ```

3. 启动开发服务器:
   ```bash
   npm run dev
   ```

   前端服务将在 `http://localhost:5173` 启动

## 步骤 4: 使用系统

1. 打开浏览器访问 `http://localhost:5173`

2. 注册新用户:
   - 点击"还没有账号？立即注册"
   - 填写用户名、邮箱和密码
   - 提交注册

3. 登录系统:
   - 使用注册的用户名和密码登录

4. 开始使用:
   - 查看账单统计信息
   - 添加新账单（收入或支出）
   - 编辑或删除已有账单
   - 使用筛选功能查看特定时间段的账单

## 常见问题

### 后端无法连接数据库

- 检查 MySQL 服务是否运行
- 确认数据库配置信息正确
- 确认数据库已创建且表结构已导入

### 前端无法连接后端

- 确认后端服务已启动（`http://localhost:8000`）
- 检查 `frontend/vite.config.js` 中的代理配置
- 查看浏览器控制台的错误信息

### Token 过期

- Token 默认有效期为 30 分钟
- 过期后需要重新登录
- 可在 `backend/config.py` 中修改 `ACCESS_TOKEN_EXPIRE_MINUTES`

## 生产环境部署建议

1. **后端**:
   - 使用 Gunicorn + Uvicorn workers
   - 配置反向代理（Nginx）
   - 使用环境变量管理敏感配置
   - 启用 HTTPS

2. **前端**:
   - 运行 `npm run build` 构建生产版本
   - 使用 Nginx 提供静态文件服务
   - 配置正确的 API 代理

3. **数据库**:
   - 使用连接池
   - 定期备份
   - 配置适当的索引

4. **安全**:
   - 修改默认的 SECRET_KEY
   - 限制 CORS 来源
   - 使用强密码策略
   - 启用数据库 SSL 连接
