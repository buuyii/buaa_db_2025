"""
数据库工具模块
封装存储过程调用方法
"""

from django.db import connection
from typing import Any, Dict, List, Tuple, Optional
from .errors import ErrorCode, map_sql_error_code, create_response


def call_procedure(
    proc_name: str,
    in_params: List[Any],
    out_params: List[str]
) -> Tuple[bool, Optional[Dict], ErrorCode, str]:
    """
    调用存储过程
    
    Args:
        proc_name: 存储过程名称
        in_params: 输入参数列表
        out_params: 输出参数名称列表（按顺序）
    
    Returns:
        (是否成功, 返回数据字典, 错误码, 错误消息)
    """
    try:
        with connection.cursor() as cursor:
            # 构建参数列表（输入参数 + 输出参数占位符）
            params = list(in_params) + [None] * len(out_params)

            # 调用存储过程
            cursor.callproc(proc_name, params)

            # 读取所有结果集，避免连接残留未读结果
            while True:
                try:
                    cursor.fetchall()
                except Exception:
                    pass
                if cursor.nextset():
                    continue
                break

            result = {}
            if out_params:
                # MySQLdb 会将 OUT 参数存储为 @_procname_index
                start_idx = len(in_params)
                select_items = []
                for offset, param_name in enumerate(out_params):
                    idx = start_idx + offset
                    select_items.append(f"@_{proc_name}_{idx} AS {param_name}")

                select_sql = "SELECT " + ", ".join(select_items)
                cursor.execute(select_sql)
                row = cursor.fetchone()
                if row is not None:
                    for offset, param_name in enumerate(out_params):
                        result[param_name] = row[offset]

            err_code = result.get('p_err_code', 0)
            err_msg = result.get('p_err_msg', '')

            error_code, error_msg = map_sql_error_code(err_code, err_msg)

            if error_code == ErrorCode.SUCCESS:
                result.pop('p_err_code', None)
                result.pop('p_err_msg', None)
                return True, result, error_code, error_msg
            else:
                return False, None, error_code, error_msg

    except Exception as e:
        return False, None, ErrorCode.SQL_EXCEPTION, f"数据库调用异常: {str(e)}"


def execute_query(query: str, params: List[Any] = None) -> List[Dict]:
    """
    执行查询SQL
    
    Args:
        query: SQL查询语句
        params: 参数列表
    
    Returns:
        查询结果列表（字典格式）
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def execute_query_one(query: str, params: List[Any] = None) -> Optional[Dict]:
    """
    执行查询SQL，返回单条记录
    
    Args:
        query: SQL查询语句
        params: 参数列表
    
    Returns:
        单条记录（字典格式）或None
    """
    results = execute_query(query, params)
    return results[0] if results else None

