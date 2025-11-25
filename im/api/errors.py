"""
统一错误码定义
用于将存储过程返回的不统一错误码映射到统一的错误码
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """统一错误码枚举"""
    SUCCESS = 0
    USER_EXISTS = 1001
    USER_NOT_EXISTS = 1002
    USER_NOT_LOGGED_IN = 1003
    INVALID_CREDENTIALS = 1004
    NULL_ELEMENT = 1005
    
    ALREADY_FRIENDS = 2001
    NOT_FRIENDS = 2002
    BLOCKED = 2003
    SHOULD_UNBLOCK_FIRSTLY = 2004
    CANNOT_SEND_TO_SELF = 2005
    REQUEST_ALREADY_SENT = 2006
    NO_SUCH_PENDING_REQUEST = 2007
    ALREADY_BLOCKED = 2008
    
    CONVERSATION_NOT_EXISTS = 3001
    NOT_CONVERSATION_MEMBER = 3002
    PERMISSION_DENIED = 3003
    
    GROUP_NOT_EXISTS = 4001
    GROUP_FULL = 4002
    GROUP_NOT_ALLOW_NEW_MEMBER = 4003
    INVITER_NOT_IN_GROUP = 4004
    INVITEE_ALREADY_IN_GROUP = 4005
    MEMBER_NOT_IN_GROUP = 4006
    OWNER_SHOULD_TRANSFERRED = 4007
    INVALID_LIMITATION = 4008
    
    SQL_EXCEPTION = 5000
    UNKNOWN_ERROR = 5999


# 错误码到错误消息的映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.USER_EXISTS: "用户已存在",
    ErrorCode.USER_NOT_EXISTS: "用户不存在",
    ErrorCode.USER_NOT_LOGGED_IN: "用户未登录",
    ErrorCode.INVALID_CREDENTIALS: "用户名或密码错误",
    ErrorCode.NULL_ELEMENT: "参数不能为空",
    ErrorCode.ALREADY_FRIENDS: "已经是好友",
    ErrorCode.NOT_FRIENDS: "不是好友",
    ErrorCode.BLOCKED: "已被对方屏蔽",
    ErrorCode.SHOULD_UNBLOCK_FIRSTLY: "需要先解除屏蔽",
    ErrorCode.CANNOT_SEND_TO_SELF: "不能向自己发送请求",
    ErrorCode.REQUEST_ALREADY_SENT: "请求已发送",
    ErrorCode.NO_SUCH_PENDING_REQUEST: "没有待处理的好友请求",
    ErrorCode.ALREADY_BLOCKED: "已经屏蔽",
    ErrorCode.CONVERSATION_NOT_EXISTS: "会话不存在或未激活",
    ErrorCode.NOT_CONVERSATION_MEMBER: "不是会话成员",
    ErrorCode.PERMISSION_DENIED: "权限不足",
    ErrorCode.GROUP_NOT_EXISTS: "群组不存在",
    ErrorCode.GROUP_FULL: "群组已满",
    ErrorCode.GROUP_NOT_ALLOW_NEW_MEMBER: "群组不允许新成员",
    ErrorCode.INVITER_NOT_IN_GROUP: "邀请者不在群组中",
    ErrorCode.INVITEE_ALREADY_IN_GROUP: "被邀请者已在群组中",
    ErrorCode.MEMBER_NOT_IN_GROUP: "成员不在群组中",
    ErrorCode.OWNER_SHOULD_TRANSFERRED: "群主需要先转移所有权",
    ErrorCode.INVALID_LIMITATION: "群组人数限制无效",
    ErrorCode.SQL_EXCEPTION: "数据库异常",
    ErrorCode.UNKNOWN_ERROR: "未知错误",
}


def map_sql_error_code(sql_err_code: int, sql_err_msg: str) -> tuple[ErrorCode, str]:
    """
    将存储过程返回的错误码映射到统一错误码
    
    Args:
        sql_err_code: 存储过程返回的错误码
        sql_err_msg: 存储过程返回的错误消息
    
    Returns:
        (统一错误码, 错误消息)
    """
    # 如果SQL返回成功
    if sql_err_code == 0:
        return ErrorCode.SUCCESS, ERROR_MESSAGES[ErrorCode.SUCCESS]
    
    # 如果SQL返回500，表示SQL异常
    if sql_err_code == 500:
        return ErrorCode.SQL_EXCEPTION, ERROR_MESSAGES[ErrorCode.SQL_EXCEPTION]
    
    # 根据错误消息进行映射（因为错误码不统一，主要依赖错误消息）
    sql_err_msg_lower = sql_err_msg.lower() if sql_err_msg else ""
    
    # 用户相关错误
    if "user exists" in sql_err_msg_lower:
        return ErrorCode.USER_EXISTS, ERROR_MESSAGES[ErrorCode.USER_EXISTS]
    if "user not exists" in sql_err_msg_lower:
        return ErrorCode.USER_NOT_EXISTS, ERROR_MESSAGES[ErrorCode.USER_NOT_EXISTS]
    if "null element" in sql_err_msg_lower:
        return ErrorCode.NULL_ELEMENT, ERROR_MESSAGES[ErrorCode.NULL_ELEMENT]
    
    # 好友相关错误
    if "already friends" in sql_err_msg_lower:
        return ErrorCode.ALREADY_FRIENDS, ERROR_MESSAGES[ErrorCode.ALREADY_FRIENDS]
    if "not friends" in sql_err_msg_lower:
        return ErrorCode.NOT_FRIENDS, ERROR_MESSAGES[ErrorCode.NOT_FRIENDS]
    if "blocked" in sql_err_msg_lower and "already" not in sql_err_msg_lower:
        return ErrorCode.BLOCKED, ERROR_MESSAGES[ErrorCode.BLOCKED]
    if "already blocked" in sql_err_msg_lower:
        return ErrorCode.ALREADY_BLOCKED, ERROR_MESSAGES[ErrorCode.ALREADY_BLOCKED]
    if "should unblock" in sql_err_msg_lower:
        return ErrorCode.SHOULD_UNBLOCK_FIRSTLY, ERROR_MESSAGES[ErrorCode.SHOULD_UNBLOCK_FIRSTLY]
    if "cannot send friend request to oneself" in sql_err_msg_lower or "to oneself" in sql_err_msg_lower:
        return ErrorCode.CANNOT_SEND_TO_SELF, ERROR_MESSAGES[ErrorCode.CANNOT_SEND_TO_SELF]
    if "request already sent" in sql_err_msg_lower:
        return ErrorCode.REQUEST_ALREADY_SENT, ERROR_MESSAGES[ErrorCode.REQUEST_ALREADY_SENT]
    if "no such pending request" in sql_err_msg_lower:
        return ErrorCode.NO_SUCH_PENDING_REQUEST, ERROR_MESSAGES[ErrorCode.NO_SUCH_PENDING_REQUEST]
    
    # 会话相关错误
    if "conversation not exists" in sql_err_msg_lower or "not active" in sql_err_msg_lower:
        return ErrorCode.CONVERSATION_NOT_EXISTS, ERROR_MESSAGES[ErrorCode.CONVERSATION_NOT_EXISTS]
    if "not conversation member" in sql_err_msg_lower:
        return ErrorCode.NOT_CONVERSATION_MEMBER, ERROR_MESSAGES[ErrorCode.NOT_CONVERSATION_MEMBER]
    if "permission denied" in sql_err_msg_lower:
        return ErrorCode.PERMISSION_DENIED, ERROR_MESSAGES[ErrorCode.PERMISSION_DENIED]
    
    # 群组相关错误
    if "group is full" in sql_err_msg_lower:
        return ErrorCode.GROUP_FULL, ERROR_MESSAGES[ErrorCode.GROUP_FULL]
    if "does not allow new member" in sql_err_msg_lower:
        return ErrorCode.GROUP_NOT_ALLOW_NEW_MEMBER, ERROR_MESSAGES[ErrorCode.GROUP_NOT_ALLOW_NEW_MEMBER]
    if "inviter is not in group" in sql_err_msg_lower:
        return ErrorCode.INVITER_NOT_IN_GROUP, ERROR_MESSAGES[ErrorCode.INVITER_NOT_IN_GROUP]
    if "invitee is in group" in sql_err_msg_lower:
        return ErrorCode.INVITEE_ALREADY_IN_GROUP, ERROR_MESSAGES[ErrorCode.INVITEE_ALREADY_IN_GROUP]
    if "someone not in group" in sql_err_msg_lower or "not in group" in sql_err_msg_lower:
        return ErrorCode.MEMBER_NOT_IN_GROUP, ERROR_MESSAGES[ErrorCode.MEMBER_NOT_IN_GROUP]
    if "owner should transferred" in sql_err_msg_lower:
        return ErrorCode.OWNER_SHOULD_TRANSFERRED, ERROR_MESSAGES[ErrorCode.OWNER_SHOULD_TRANSFERRED]
    if "no less than number of members" in sql_err_msg_lower or "no more than 200" in sql_err_msg_lower:
        return ErrorCode.INVALID_LIMITATION, ERROR_MESSAGES[ErrorCode.INVALID_LIMITATION]
    if "no such group" in sql_err_msg_lower:
        return ErrorCode.GROUP_NOT_EXISTS, ERROR_MESSAGES[ErrorCode.GROUP_NOT_EXISTS]
    
    # 默认返回原始错误消息
    return ErrorCode.UNKNOWN_ERROR, sql_err_msg or ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR]


def create_response(success: bool, data=None, error_code: ErrorCode = None, error_msg: str = None):
    """
    创建统一的API响应格式
    
    Args:
        success: 是否成功
        data: 返回数据
        error_code: 错误码
        error_msg: 错误消息
    
    Returns:
        dict: 统一格式的响应
    """
    if success:
        return {
            "success": True,
            "data": data,
            "error_code": ErrorCode.SUCCESS,
            "error_msg": ERROR_MESSAGES[ErrorCode.SUCCESS]
        }
    else:
        return {
            "success": False,
            "data": None,
            "error_code": error_code or ErrorCode.UNKNOWN_ERROR,
            "error_msg": error_msg or ERROR_MESSAGES[error_code or ErrorCode.UNKNOWN_ERROR]
        }

