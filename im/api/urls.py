"""
API路由配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 用户相关
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('user/info', views.get_user_info, name='user_info'),
    path('user/update', views.update_user_info, name='update_user_info'),
    
    # 好友相关
    path('friend/request', views.send_friend_request, name='send_friend_request'),
    path('friend/respond', views.respond_friend_request, name='respond_friend_request'),
    path('friend/delete', views.delete_friend, name='delete_friend'),
    path('friend/block', views.block_user, name='block_user'),
    path('friend/list', views.get_friend_list, name='friend_list'),
    path('friend/requests', views.get_friend_requests, name='friend_requests'),
    
    # 消息相关
    path('message/send', views.send_message, name='send_message'),
    path('message/list', views.get_messages, name='message_list'),
    path('conversation/list', views.get_conversation_list, name='conversation_list'),
    
    # 群组相关
    path('group/create', views.create_group, name='create_group'),
    path('group/invite', views.invite_to_group, name='invite_to_group'),
    path('group/modify', views.modify_group_option, name='modify_group_option'),
    path('group/permission', views.modify_member_permission, name='modify_member_permission'),
    path('group/exit', views.exit_group, name='exit_group'),
    path('group/dissolve', views.dissolve_group, name='dissolve_group'),
    path('group/list', views.get_group_list, name='group_list'),
    path('group/members', views.get_group_members, name='group_members'),
    
    # 辅助
    path('search/users', views.search_users, name='search_users'),
]

