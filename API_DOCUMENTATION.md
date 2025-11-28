# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 前缀**: `/api`
- **认证方式**: Bearer Token (JWT)

## 认证接口

### 1. 用户注册

**POST** `/api/auth/register`

注册新用户账户。

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应**:
- `400`: 用户名或邮箱已存在

---

### 2. 用户登录

**POST** `/api/auth/login`

用户登录获取访问令牌。

**请求体** (FormData):
```
username: testuser
password: password123
```

**响应** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**错误响应**:
- `401`: 用户名或密码错误

---

### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的信息。

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应**:
- `401`: 未认证或 Token 无效

---

## 账单接口

### 1. 创建账单

**POST** `/api/bills`

创建新的账单记录。

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "title": "午餐",
  "amount": 50.00,
  "category": "支出",
  "type": "餐饮",
  "description": "公司附近餐厅",
  "bill_date": "2024-01-15"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "午餐",
  "amount": 50.00,
  "category": "支出",
  "type": "餐饮",
  "description": "公司附近餐厅",
  "bill_date": "2024-01-15",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

---

### 2. 获取账单列表

**GET** `/api/bills`

获取当前用户的账单列表，支持分页和筛选。

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `skip` (int, 可选): 跳过记录数，默认 0
- `limit` (int, 可选): 返回记录数，默认 100，最大 1000
- `category` (string, 可选): 分类筛选，值: "收入" 或 "支出"
- `start_date` (date, 可选): 开始日期，格式: YYYY-MM-DD
- `end_date` (date, 可选): 结束日期，格式: YYYY-MM-DD

**示例请求**:
```
GET /api/bills?category=支出&start_date=2024-01-01&end_date=2024-01-31&skip=0&limit=20
```

**响应** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "午餐",
    "amount": 50.00,
    "category": "支出",
    "type": "餐饮",
    "description": "公司附近餐厅",
    "bill_date": "2024-01-15",
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "工资",
    "amount": 10000.00,
    "category": "收入",
    "type": "工资",
    "description": "月度工资",
    "bill_date": "2024-01-01",
    "created_at": "2024-01-01T09:00:00",
    "updated_at": "2024-01-01T09:00:00"
  }
]
```

---

### 3. 获取账单详情

**GET** `/api/bills/{bill_id}`

获取指定账单的详细信息。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `bill_id` (int): 账单ID

**响应** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "午餐",
  "amount": 50.00,
  "category": "支出",
  "type": "餐饮",
  "description": "公司附近餐厅",
  "bill_date": "2024-01-15",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

**错误响应**:
- `404`: 账单不存在或不属于当前用户

---

### 4. 更新账单

**PUT** `/api/bills/{bill_id}`

更新指定账单的信息。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `bill_id` (int): 账单ID

**请求体** (所有字段可选):
```json
{
  "title": "晚餐",
  "amount": 80.00,
  "category": "支出",
  "type": "餐饮",
  "description": "更新后的描述",
  "bill_date": "2024-01-16"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "晚餐",
  "amount": 80.00,
  "category": "支出",
  "type": "餐饮",
  "description": "更新后的描述",
  "bill_date": "2024-01-16",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-16T10:00:00"
}
```

**错误响应**:
- `404`: 账单不存在或不属于当前用户

---

### 5. 删除账单

**DELETE** `/api/bills/{bill_id}`

删除指定的账单。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `bill_id` (int): 账单ID

**响应** (204 No Content): 无响应体

**错误响应**:
- `404`: 账单不存在或不属于当前用户

---

### 6. 获取账单统计

**GET** `/api/bills/statistics/summary`

获取账单统计信息，包括总收入、总支出、余额和账单数量。

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `start_date` (date, 可选): 开始日期，格式: YYYY-MM-DD
- `end_date` (date, 可选): 结束日期，格式: YYYY-MM-DD

**示例请求**:
```
GET /api/bills/statistics/summary?start_date=2024-01-01&end_date=2024-01-31
```

**响应** (200 OK):
```json
{
  "total_income": 10000.00,
  "total_expense": 3500.00,
  "balance": 6500.00,
  "count": 25
}
```

---

## 图片接口

### 1. 上传单张图片

**POST** `/api/images/upload`

上传账单图片并自动进行OCR识别（支持支付宝、微信账单）。

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体** (FormData):
- `file`: 图片文件（支持 jpg, jpeg, png, bmp, gif，最大 10MB）
- `auto_create_bill`: boolean (可选，默认true) - 是否自动创建账单

**响应** (201 Created):
```json
{
  "image": {
    "id": 1,
    "bill_id": 1,
    "user_id": 1,
    "filename": "bill_20240115_120000.jpg",
    "file_path": "uploads/1/bill_20240115_120000.jpg",
    "file_size": 245678,
    "mime_type": "image/jpeg",
    "source_type": "alipay",
    "ocr_result": {
      "success": true,
      "bill_type": "alipay",
      "parsed_data": {
        "amount": 50.00,
        "date": "2024-01-15",
        "merchant": "餐厅名称",
        "category": "支出",
        "type": "餐饮"
      }
    },
    "parse_status": "success",
    "parse_error": null,
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00"
  },
  "bill": {
    "id": 1,
    "user_id": 1,
    "title": "餐厅名称",
    "amount": 50.00,
    "category": "支出",
    "type": "餐饮",
    "description": "餐厅名称",
    "bill_date": "2024-01-15",
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00"
  },
  "parsed_data": {
    "amount": 50.00,
    "date": "2024-01-15",
    "merchant": "餐厅名称",
    "category": "支出",
    "type": "餐饮"
  }
}
```

**错误响应**:
- `400`: 文件格式不支持或文件过大
- `500`: OCR识别失败

---

### 2. 批量上传图片

**POST** `/api/images/upload/batch`

批量上传多张图片（最多20张）。

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体** (FormData):
- `files`: 图片文件数组（每个文件最大 10MB）
- `auto_create_bill`: boolean (可选，默认true)

**响应** (201 Created):
```json
{
  "success_count": 2,
  "failed_count": 1,
  "results": [
    {
      "image": { ... },
      "bill": { ... },
      "parsed_data": { ... }
    },
    {
      "image": { ... },
      "bill": { ... },
      "parsed_data": { ... }
    },
    {
      "image": null,
      "bill": null,
      "parsed_data": null
    }
  ]
}
```

**错误响应**:
- `400`: 文件数量超过限制（最多20张）

---

### 3. 获取图片信息

**GET** `/api/images/{image_id}`

获取指定图片的详细信息。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `image_id` (int): 图片ID

**响应** (200 OK):
```json
{
  "id": 1,
  "bill_id": 1,
  "user_id": 1,
  "filename": "bill_20240115_120000.jpg",
  "file_path": "uploads/1/bill_20240115_120000.jpg",
  "file_size": 245678,
  "mime_type": "image/jpeg",
  "source_type": "alipay",
  "ocr_result": { ... },
  "parse_status": "success",
  "parse_error": null,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

**错误响应**:
- `404`: 图片不存在或不属于当前用户

---

### 4. 获取图片文件

**GET** `/api/images/{image_id}/file`

获取图片文件（用于显示）。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `image_id` (int): 图片ID

**响应** (200 OK): 图片文件流

**错误响应**:
- `404`: 图片不存在或文件不存在

---

### 5. 获取账单的所有图片

**GET** `/api/images/bill/{bill_id}/images`

获取指定账单关联的所有图片。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `bill_id` (int): 账单ID

**响应** (200 OK):
```json
[
  {
    "id": 1,
    "bill_id": 1,
    "user_id": 1,
    "filename": "bill_20240115_120000.jpg",
    ...
  },
  {
    "id": 2,
    "bill_id": 1,
    "user_id": 1,
    "filename": "bill_20240115_120001.jpg",
    ...
  }
]
```

**错误响应**:
- `404`: 账单不存在或不属于当前用户

---

### 6. 删除图片

**DELETE** `/api/images/{image_id}`

删除指定的图片。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `image_id` (int): 图片ID

**响应** (204 No Content): 无响应体

**错误响应**:
- `404`: 图片不存在或不属于当前用户

---

### 7. 重新解析图片

**POST** `/api/images/{image_id}/reparse`

重新解析图片（如果首次解析失败）。

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `image_id` (int): 图片ID

**查询参数**:
- `auto_create_bill`: boolean (可选，默认false) - 是否自动创建账单

**响应** (200 OK): 同上传图片接口

**错误响应**:
- `404`: 图片不存在或文件不存在

---

## 数据模型

### User (用户)
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "created_at": "datetime"
}
```

### Bill (账单)
```json
{
  "id": "integer",
  "user_id": "integer",
  "title": "string",
  "amount": "decimal(10,2)",
  "category": "string (收入|支出)",
  "type": "string",
  "description": "string (可选)",
  "bill_date": "date (YYYY-MM-DD)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### BillStatistics (账单统计)
```json
{
  "total_income": "decimal(10,2)",
  "total_expense": "decimal(10,2)",
  "balance": "decimal(10,2)",
  "count": "integer"
}
```

### BillImage (账单图片)
```json
{
  "id": "integer",
  "bill_id": "integer",
  "user_id": "integer",
  "filename": "string",
  "file_path": "string",
  "file_size": "integer",
  "mime_type": "string",
  "source_type": "string (alipay|wechat|manual)",
  "ocr_result": "object (JSON)",
  "parse_status": "string (pending|success|failed)",
  "parse_error": "string (可选)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ImageUploadResponse (图片上传响应)
```json
{
  "image": "BillImage (可选)",
  "bill": "Bill (可选)",
  "parsed_data": {
    "amount": "decimal(10,2)",
    "date": "string (YYYY-MM-DD)",
    "merchant": "string",
    "category": "string (收入|支出)",
    "type": "string"
  }
}
```

---

## 错误响应格式

所有错误响应都遵循以下格式:

```json
{
  "detail": "错误描述信息"
}
```

### 常见 HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功，无响应体
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或 Token 无效
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 认证说明

1. 注册或登录后，会返回 `access_token`
2. 在后续请求中，需要在请求头中添加:
   ```
   Authorization: Bearer {access_token}
   ```
3. Token 默认有效期为 30 分钟（可在配置中修改）
4. Token 过期后需要重新登录获取新的 Token
