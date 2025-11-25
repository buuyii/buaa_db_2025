"""
API视图模块
处理所有HTTP请求，调用存储过程
"""

import hashlib
import json
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from .db_utils import call_procedure, execute_query, execute_query_one
from .errors import ErrorCode, create_response


def require_login(func):
    """装饰器：要求用户登录"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.USER_NOT_LOGGED_IN,
                error_msg="用户未登录"
            ))
        request.user_id = user_id
        return func(request, *args, **kwargs)
    return wrapper


def hash_password(password: str) -> str:
    """简单的密码哈希（实际项目中应使用更安全的方法）"""
    return hashlib.sha256(password.encode()).hexdigest()


# ==================== 用户相关API ====================

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """用户注册"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="用户名和密码不能为空"
            ))
        
        password_hash = hash_password(password)
        success, result, error_code, error_msg = call_procedure(
            'proc_register_user_base',
            [username, password_hash],
            ['p_userid', 'p_err_code', 'p_err_msg']
        )
        if success:
            # 自动登录
            request.session['user_id'] = result['p_userid']
            request.session['username'] = username
            return JsonResponse(create_response(
                True,
                data={'user_id': result['p_userid'], 'username': username}
            ))
        else:
            return JsonResponse(create_response(
                False,
                error_code=error_code,
                error_msg=error_msg
            ))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """用户登录"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="用户名和密码不能为空"
            ))
        
        password_hash = hash_password(password)
        user = execute_query_one(
            "SELECT id, username, display_name, phone FROM users WHERE username = %s AND password_hash = %s AND cancelled = 0",
            [username, password_hash]
        )
        
        if user:
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            return JsonResponse(create_response(
                True,
                data=user
            ))
        else:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.INVALID_CREDENTIALS,
                error_msg="用户名或密码错误"
            ))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    """用户登出"""
    request.session.flush()
    return JsonResponse(create_response(True, data={'message': '登出成功'}))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_user_info(request):
    """获取当前用户信息"""
    user_id = request.user_id
    user = execute_query_one(
        "SELECT id, username, display_name, phone, created_at FROM users WHERE id = %s AND cancelled = 0",
        [user_id]
    )
    
    if user:
        return JsonResponse(create_response(True, data=user))
    else:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.USER_NOT_EXISTS,
            error_msg="用户不存在"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def update_user_info(request):
    """修改用户信息"""
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        password = data.get('password')
        phone = data.get('phone')
        display_name = data.get('display_name')
        
        if not password or not phone or not display_name:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="所有字段都不能为空"
            ))
        
        password_hash = hash_password(password)
        success, result, error_code, error_msg = call_procedure(
            'proc_alter_user_info',
            [user_id, password_hash, phone, display_name],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


# ==================== 好友相关API ====================

@csrf_exempt
@require_http_methods(["POST"])
@require_login
def send_friend_request(request):
    """发送好友请求"""
    try:
        data = json.loads(request.body)
        sender_id = request.user_id
        receiver_id = data.get('receiver_id')
        message = data.get('message', '')
        
        if not receiver_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="接收者ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_send_friend_req',
            [sender_id, receiver_id, message],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def respond_friend_request(request):
    """响应好友请求"""
    try:
        data = json.loads(request.body)
        receiver_id = request.user_id
        sender_id = data.get('sender_id')
        response = data.get('response')  # 'accept' or 'reject'
        
        if not sender_id or response not in ['accept', 'reject']:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="参数错误"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_respond_friend_req',
            [receiver_id, sender_id, response],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def delete_friend(request):
    """删除好友"""
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="好友ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_del_friend',
            [user_id, friend_id],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def block_user(request):
    """屏蔽用户"""
    try:
        data = json.loads(request.body)
        blocker_id = request.user_id
        blocked_id = data.get('blocked_id')
        
        if not blocked_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="被屏蔽用户ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_block',
            [blocker_id, blocked_id],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_friend_list(request):
    """获取好友列表"""
    user_id = request.user_id
    friends = execute_query(
        """
        SELECT 
            CASE 
                WHEN f.user1_id = %s THEN f.user2_id 
                ELSE f.user1_id 
            END as friend_id,
            u.username, u.display_name, u.phone,
            f.conversation_id, f.created_at
        FROM friends f
        JOIN users u ON (u.id = CASE WHEN f.user1_id = %s THEN f.user2_id ELSE f.user1_id END)
        JOIN conversations c ON c.id = f.conversation_id
        WHERE (f.user1_id = %s OR f.user2_id = %s) AND c.is_active = 1
        """,
        [user_id, user_id, user_id, user_id]
    )
    
    return JsonResponse(create_response(True, data=friends))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_friend_requests(request):
    """获取好友请求列表"""
    user_id = request.user_id
    
    # 收到的请求
    received = execute_query(
        """
        SELECT fr.sender_id, u.username, u.display_name, fr.message, fr.status, fr.updated_at
        FROM friend_requests fr
        JOIN users u ON u.id = fr.sender_id
        WHERE fr.receiver_id = %s
        ORDER BY fr.updated_at DESC
        """,
        [user_id]
    )
    
    # 发送的请求
    sent = execute_query(
        """
        SELECT fr.receiver_id, u.username, u.display_name, fr.message, fr.status, fr.updated_at
        FROM friend_requests fr
        JOIN users u ON u.id = fr.receiver_id
        WHERE fr.sender_id = %s
        ORDER BY fr.updated_at DESC
        """,
        [user_id]
    )
    
    return JsonResponse(create_response(True, data={
        'received': received,
        'sent': sent
    }))


# ==================== 消息相关API ====================

@csrf_exempt
@require_http_methods(["POST"])
@require_login
def send_message(request):
    """发送消息"""
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        
        if not conversation_id or not message:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="会话ID和消息内容不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_send_message',
            [user_id, conversation_id, message],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_messages(request):
    """获取会话消息列表"""
    user_id = request.user_id
    conversation_id = request.GET.get('conversation_id')
    
    if not conversation_id:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.NULL_ELEMENT,
            error_msg="会话ID不能为空"
        ))
    
    messages = execute_query(
        """
        SELECT m.id, m.sender_id, u.username, u.display_name, m.content, m.created_at
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE m.conversation_id = %s
        ORDER BY m.created_at ASC
        """,
        [conversation_id]
    )
    
    return JsonResponse(create_response(True, data=messages))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_conversation_list(request):
    """获取会话列表"""
    user_id = request.user_id
    
    # 私聊会话
    private_conversations = execute_query(
        """
        SELECT 
            c.id as conversation_id,
            c.type,
            c.updated_at,
            CASE 
                WHEN f.user1_id = %s THEN f.user2_id 
                ELSE f.user1_id 
            END as other_user_id,
            u.username as other_username,
            u.display_name as other_display_name
        FROM conversations c
        JOIN friends f ON f.conversation_id = c.id
        JOIN users u ON (u.id = CASE WHEN f.user1_id = %s THEN f.user2_id ELSE f.user1_id END)
        WHERE (f.user1_id = %s OR f.user2_id = %s) AND c.type = 'private' AND c.is_active = 1
        ORDER BY c.updated_at DESC
        """,
        [user_id, user_id, user_id, user_id]
    )
    
    # 群聊会话
    group_conversations = execute_query(
        """
        SELECT 
            c.id as conversation_id,
            c.type,
            c.updated_at,
            g.id as group_id,
            g.group_name,
            g.number_of_members
        FROM conversations c
        JOIN chatgroups g ON g.conversation_id = c.id
        JOIN group_members gm ON gm.group_id = g.id
        WHERE gm.uid = %s AND c.type = 'group' AND c.is_active = 1
        ORDER BY c.updated_at DESC
        """,
        [user_id]
    )
    
    return JsonResponse(create_response(True, data={
        'private': private_conversations,
        'group': group_conversations
    }))


# ==================== 群组相关API ====================

@csrf_exempt
@require_http_methods(["POST"])
@require_login
def create_group(request):
    """创建群组"""
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        group_name = data.get('group_name')
        limitation = data.get('limitation', 20)
        
        if not group_name:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="群组名称不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_create_group',
            [user_id, group_name, limitation],
            ['p_group_id', 'p_err_code', 'p_err_msg']
        )
        
        if success:
            return JsonResponse(create_response(
                True,
                data={'group_id': result['p_group_id']}
            ))
        else:
            return JsonResponse(create_response(
                False,
                error_code=error_code,
                error_msg=error_msg
            ))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def invite_to_group(request):
    """邀请入群"""
    try:
        data = json.loads(request.body)
        user_id = request.user_id
        invitee_id = data.get('invitee_id')
        group_id = data.get('group_id')
        
        if not invitee_id or not group_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="被邀请者ID和群组ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_invite_into_group',
            [user_id, invitee_id, group_id],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def modify_group_option(request):
    """修改群组设置"""
    try:
        data = json.loads(request.body)
        modifier_id = request.user_id
        group_id = data.get('group_id')
        group_name = data.get('group_name')
        limitation = data.get('limitation')
        allow_new_member = data.get('allow_new_member')
        
        if not group_id or not group_name or limitation is None or allow_new_member is None:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="所有参数都不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_modify_group_option',
            [modifier_id, group_id, group_name, limitation, allow_new_member],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def modify_member_permission(request):
    """修改成员权限"""
    try:
        data = json.loads(request.body)
        modifier_id = request.user_id
        member_id = data.get('member_id')
        group_id = data.get('group_id')
        permission = data.get('permission')
        
        if not member_id or not group_id or permission is None:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="所有参数都不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_modify_member_permission',
            [modifier_id, member_id, group_id, permission],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def exit_group(request):
    """退出群组"""
    try:
        data = json.loads(request.body)
        requestor_id = request.user_id
        target_id = data.get('target_id', requestor_id)  # 默认是自己
        group_id = data.get('group_id')
        
        if not group_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="群组ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_exit_group',
            [requestor_id, target_id, group_id],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["POST"])
@require_login
def dissolve_group(request):
    """解散群组"""
    try:
        data = json.loads(request.body)
        requestor_id = request.user_id
        group_id = data.get('group_id')
        
        if not group_id:
            return JsonResponse(create_response(
                False,
                error_code=ErrorCode.NULL_ELEMENT,
                error_msg="群组ID不能为空"
            ))
        
        success, result, error_code, error_msg = call_procedure(
            'proc_dissolve_group',
            [requestor_id, group_id],
            ['p_err_code', 'p_err_msg']
        )
        
        return JsonResponse(create_response(success, error_code=error_code, error_msg=error_msg))
    except Exception as e:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.UNKNOWN_ERROR,
            error_msg=f"请求处理异常: {str(e)}"
        ))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_group_list(request):
    """获取用户所在的群组列表"""
    user_id = request.user_id
    groups = execute_query(
        """
        SELECT 
            g.id as group_id,
            g.conversation_id,
            g.group_name,
            g.owner_id,
            u.username as owner_username,
            g.number_of_members,
            g.limitation,
            g.allow_new_member,
            gm.permission,
            g.updated_at
        FROM chatgroups g
        JOIN group_members gm ON gm.group_id = g.id
        JOIN users u ON u.id = g.owner_id
        JOIN conversations c ON c.id = g.conversation_id
        WHERE gm.uid = %s AND c.is_active = 1
        ORDER BY g.updated_at DESC
        """,
        [user_id]
    )
    
    return JsonResponse(create_response(True, data=groups))


@csrf_exempt
@require_http_methods(["GET"])
@require_login
def get_group_members(request):
    """获取群组成员列表"""
    group_id = request.GET.get('group_id')
    
    if not group_id:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.NULL_ELEMENT,
            error_msg="群组ID不能为空"
        ))
    
    members = execute_query(
        """
        SELECT 
            gm.uid,
            u.username,
            u.display_name,
            gm.nickname,
            gm.permission,
            gm.updated_at
        FROM group_members gm
        JOIN users u ON u.id = gm.uid
        WHERE gm.group_id = %s
        ORDER BY gm.permission DESC, gm.updated_at ASC
        """,
        [group_id]
    )
    
    return JsonResponse(create_response(True, data=members))


# ==================== 辅助API ====================

@csrf_exempt
@require_http_methods(["GET"])
def search_users(request):
    """搜索用户（用于添加好友等）"""
    keyword = request.GET.get('keyword', '')
    
    if not keyword:
        return JsonResponse(create_response(
            False,
            error_code=ErrorCode.NULL_ELEMENT,
            error_msg="搜索关键词不能为空"
        ))
    
    users = execute_query(
        """
        SELECT id, username, display_name, phone
        FROM users
        WHERE (username LIKE %s OR display_name LIKE %s) AND cancelled = 0
        LIMIT 20
        """,
        [f'%{keyword}%', f'%{keyword}%']
    )
    
    return JsonResponse(create_response(True, data=users))

