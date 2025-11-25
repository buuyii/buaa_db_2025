# IM聊天系统 - Django后端和前端

## 项目结构

```
im/
├── api/                    # Django应用
│   ├── __init__.py
│   ├── views.py           # API视图（所有HTTP请求处理）
│   ├── urls.py            # API路由配置
│   ├── db_utils.py        # 数据库工具（存储过程调用）
│   └── errors.py          # 统一错误码定义
├── im/                    # Django项目配置
│   ├── settings.py        # 项目设置（已配置数据库和模板）
│   ├── urls.py            # 主URL配置
│   └── ...
├── templates/             # HTML模板
│   ├── index.html         # 登录/注册页面
│   └── main.html          # 主界面（所有功能）
└── manage.py
```

## 功能说明

### API端点

所有API端点都在 `/api/` 路径下：

#### 用户相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET /api/user/info` - 获取当前用户信息
- `POST /api/user/update` - 修改用户信息

#### 好友相关
- `POST /api/friend/request` - 发送好友请求
- `POST /api/friend/respond` - 响应好友请求（接受/拒绝）
- `POST /api/friend/delete` - 删除好友
- `POST /api/friend/block` - 屏蔽用户
- `GET /api/friend/list` - 获取好友列表
- `GET /api/friend/requests` - 获取好友请求列表

#### 消息相关
- `POST /api/message/send` - 发送消息
- `GET /api/message/list` - 获取会话消息列表（需要conversation_id参数）
- `GET /api/conversation/list` - 获取会话列表

#### 群组相关
- `POST /api/group/create` - 创建群组
- `POST /api/group/invite` - 邀请入群
- `POST /api/group/modify` - 修改群组设置
- `POST /api/group/permission` - 修改成员权限
- `POST /api/group/exit` - 退出群组
- `POST /api/group/dissolve` - 解散群组
- `GET /api/group/list` - 获取用户所在的群组列表
- `GET /api/group/members` - 获取群组成员列表（需要group_id参数）

#### 辅助
- `GET /api/search/users` - 搜索用户（需要keyword参数）

### 前端页面

- `/` - 登录/注册页面
- `/main/` - 主界面（需要登录）

## 使用方法

### 1. 安装依赖

```bash
pip install django mysqlclient
# 或者
pip install django pymysql
```

如果使用pymysql，需要在 `im/__init__.py` 中添加：
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 2. 运行服务器

```bash
cd im
python manage.py runserver
```

### 3. 访问系统

打开浏览器访问 `http://127.0.0.1:8000/`

## 技术说明

### 存储过程调用

所有业务逻辑都在MySQL存储过程中实现。Django后端通过 `api/db_utils.py` 中的 `call_procedure` 函数调用存储过程。

### 错误码统一

存储过程返回的错误码可能不统一，系统通过 `api/errors.py` 中的 `map_sql_error_code` 函数将SQL错误码映射到统一的错误码枚举。

### 会话管理

使用Django的session框架进行简单的用户认证。登录后，`user_id` 存储在 `request.session['user_id']` 中。

### 前端设计

前端采用简单的debug风格，使用原生JavaScript和fetch API，不依赖任何框架。界面分为：
- 侧边栏导航
- 主内容区域（根据选择的模块显示不同内容）
- 支持保存最多5个“快捷账号”（存储在浏览器LocalStorage中），可在登录页一键登录，在主界面顶部快速切换，方便演示多个用户场景

## 注意事项

1. **业务逻辑在SQL中**：所有业务逻辑都在存储过程中，Django只负责调用和返回结果
2. **简单认证**：使用Django session进行简单的用户认证
3. **错误处理**：存储过程返回的错误码和错误消息会正确传递给前端
4. **演示优先**：前端界面以满足演示需求为主

## 开发说明

### 添加新的API端点

1. 在 `api/views.py` 中添加视图函数
2. 在 `api/urls.py` 中添加路由
3. 如果需要调用存储过程，使用 `call_procedure` 函数
4. 如果需要查询数据，使用 `execute_query` 或 `execute_query_one` 函数

### 错误码处理

所有错误码定义在 `api/errors.py` 中。如果存储过程返回新的错误消息，需要在 `map_sql_error_code` 函数中添加映射规则。

