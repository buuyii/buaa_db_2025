# 项目实现计划

## 项目现状分析

### 已完成部分
1. **数据库设计** (`./document/sql.md`)
   - 8个核心表：users, friend_requests, friends, blocks, conversations, messages, chatgroups, group_members
   - 5个触发器：处理好友关系、群组成员数量、会话状态等
   - 13个存储过程：涵盖用户、好友、消息、群组等核心业务逻辑

2. **Django项目基础**
   - Django 5.2.8 项目已初始化
   - MySQL数据库连接已配置
   - 基本项目结构已建立

### 待实现部分
1. **Django后端API层**
   - 需要创建Django应用（app）
   - 需要封装存储过程调用工具
   - 需要实现RESTful API端点
   - 需要处理会话管理（简单session）

2. **前端界面**
   - 需要创建简单的HTML页面
   - 需要基本的JavaScript交互
   - debug风格，满足演示需求即可

## 实现计划

### 阶段一：Django应用基础架构

#### 1.1 创建Django应用
- 创建 `api` 应用用于处理API请求
- 在 `settings.py` 中注册应用
- 创建基础目录结构

#### 1.2 数据库工具模块
- 创建 `api/db_utils.py`
- 封装存储过程调用方法
- 统一错误处理机制
- 返回标准化的JSON响应

### 阶段二：API端点实现

#### 2.1 用户相关API
- `POST /api/register` - 用户注册（调用 `proc_register_user_base`）
- `POST /api/login` - 用户登录（查询users表验证，设置session）
- `POST /api/logout` - 用户登出
- `POST /api/user/update` - 修改用户信息（调用 `proc_alter_user_info`）
- `GET /api/user/info` - 获取当前用户信息

#### 2.2 好友相关API
- `POST /api/friend/request` - 发送好友请求（调用 `proc_send_friend_req`）
- `POST /api/friend/respond` - 响应好友请求（调用 `proc_respond_friend_req`）
- `POST /api/friend/delete` - 删除好友（调用 `proc_del_friend`）
- `POST /api/friend/block` - 屏蔽用户（调用 `proc_block`）
- `GET /api/friend/list` - 获取好友列表
- `GET /api/friend/requests` - 获取好友请求列表（收到的和发送的）

#### 2.3 消息相关API
- `POST /api/message/send` - 发送消息（调用 `proc_send_message`）
- `GET /api/message/list` - 获取会话消息列表
- `GET /api/conversation/list` - 获取会话列表（私聊和群聊）

#### 2.4 群组相关API
- `POST /api/group/create` - 创建群组（调用 `proc_create_group`）
- `POST /api/group/invite` - 邀请入群（调用 `proc_invite_into_group`）
- `POST /api/group/modify` - 修改群组设置（调用 `proc_modify_group_option`）
- `POST /api/group/permission` - 修改成员权限（调用 `proc_modify_member_permission`）
- `POST /api/group/exit` - 退出群组（调用 `proc_exit_group`）
- `POST /api/group/dissolve` - 解散群组（调用 `proc_dissolve_group`）
- `GET /api/group/list` - 获取用户所在的群组列表
- `GET /api/group/members` - 获取群组成员列表

### 阶段三：前端界面实现

#### 3.1 页面结构
- `index.html` - 登录/注册页面
- `main.html` - 主界面（包含所有功能模块）
- 简单的导航栏和功能区域划分

#### 3.2 功能模块（在main.html中）
- **用户信息模块**：显示当前用户信息，修改信息
- **好友管理模块**：查看好友列表，发送/响应好友请求，删除好友，屏蔽用户
- **消息模块**：选择会话，发送消息，查看消息历史
- **群组管理模块**：创建群组，查看群组列表，邀请成员，修改群组设置，退出/解散群组

#### 3.3 技术选择
- 纯HTML + JavaScript（原生，不使用框架）
- 使用 `fetch` API 进行AJAX请求
- 简单的CSS样式（debug风格，可以使用内联样式）
- 使用Django的session进行简单的用户认证

### 阶段四：配置和优化

#### 4.1 URL配置
- 配置API路由（`/api/*`）
- 配置前端页面路由
- 配置静态文件服务

#### 4.2 中间件和设置
- 配置CORS（如果需要）
- 配置CSRF（开发环境可以放宽）
- 配置静态文件路径

#### 4.3 错误处理
- 统一的错误响应格式
- 前端错误提示

## 技术细节

### 存储过程调用方式
使用Django的数据库连接直接调用存储过程：
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.callproc('proc_name', [param1, param2, ...])
    # 获取OUT参数
    results = cursor.fetchall()
```

### 会话管理
- 使用Django的session框架
- 登录时设置 `request.session['user_id']`
- API请求中验证session

### 前端设计原则
- 简单直接，debug风格
- 使用表单和按钮进行交互
- 使用 `console.log` 和 `alert` 进行调试
- 不追求美观，满足功能演示即可

## 文件结构规划

```
im/
├── api/                    # Django应用
│   ├── __init__.py
│   ├── views.py           # API视图
│   ├── urls.py            # API路由
│   ├── db_utils.py        # 数据库工具
│   └── utils.py           # 辅助工具
├── im/                    # Django项目配置
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── templates/             # HTML模板
│   ├── index.html
│   └── main.html
├── static/                # 静态文件（如果需要）
└── manage.py
```

## 注意事项

1. **业务逻辑在SQL中**：所有业务逻辑都在存储过程中，Django只负责调用和返回结果
2. **简单认证**：使用Django session进行简单的用户认证，不实现复杂的权限系统
3. **错误处理**：存储过程返回的错误码和错误消息需要正确传递给前端
4. **数据验证**：前端和后端都需要进行基本的数据验证
5. **演示优先**：前端界面以满足演示需求为主，不需要追求完美

## 预计实现时间

- 阶段一：30分钟
- 阶段二：2-3小时
- 阶段三：1-2小时
- 阶段四：30分钟

总计：约4-6小时

