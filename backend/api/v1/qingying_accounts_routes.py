# -*- coding: utf-8 -*-
"""
清影账号管理API路由
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from backend.models.models import QingyingAccount, QingyingImage2VideoTask
from backend.utils.qingying_account_login import login_and_get_cookie

# 创建蓝图
qingying_accounts_bp = Blueprint('qingying_accounts', __name__, url_prefix='/api/v1/qingying/accounts')

@qingying_accounts_bp.route('', methods=['GET'])
def get_accounts():
    """获取所有清影账号"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        cookie_status = request.args.get('cookie_status', None)  # 'has_cookies', 'no_cookies'
        
        print(f"获取清影账号列表，页码: {page}, 每页数量: {page_size}, Cookie状态筛选: {cookie_status}")
        
        # 构建查询
        query = QingyingAccount.select()
        
        # 根据Cookie状态筛选
        if cookie_status == 'has_cookies':
            query = query.where(QingyingAccount.cookies.is_null(False) & (QingyingAccount.cookies != ''))
        elif cookie_status == 'no_cookies':
            query = query.where(QingyingAccount.cookies.is_null(True) | (QingyingAccount.cookies == ''))
        
        # 分页
        total = query.count()
        accounts = query.order_by(QingyingAccount.created_at.desc()).paginate(page, page_size)
        
        data = []
        for account in accounts:
            data.append({
                'id': account.id,
                'nickname': account.nickname,
                'phone': account.phone,
                'has_cookies': bool(account.cookies and account.cookies.strip()),
                'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': account.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        print(f"获取清影账号列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_accounts_bp.route('', methods=['POST'])
def add_account():
    """添加清影账号（通过浏览器登录）"""
    try:
        print("开始添加清影账号，将打开浏览器进行登录...")
        
        # 提交到全局线程池处理
        from backend.core.global_task_manager import global_task_manager
        
        if global_task_manager and global_task_manager.global_executor:
            # 提交账号添加任务到线程池
            future = global_task_manager.global_executor.submit(_process_add_account_task)
            
            print("已提交清影账号添加任务到线程池")
            return jsonify({
                'success': True, 
                'message': '正在打开浏览器，请完成登录操作'
            })
        else:
            return jsonify({
                'success': False, 
                'message': '全局任务管理器未初始化'
            }), 500
        
    except Exception as e:
        print(f"添加清影账号失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def _process_add_account_task():
    """处理添加账号任务"""
    try:
        print("开始处理清影账号添加任务...")
        
        # 调用登录函数获取用户信息
        result = asyncio.run(login_and_get_cookie(headless=False))
        
        if result.get('code') == 200:
            account_data = result.get('data')
            nickname = account_data.get('nickname')
            phone = account_data.get('phone')
            cookies = account_data.get('cookies')
            
            # 检查是否重复
            existing_account = QingyingAccount.select().where(
                (QingyingAccount.nickname == nickname) | (QingyingAccount.phone == phone)
            ).first()
            
            if existing_account:
                print(f"清影账号已存在: {nickname} ({phone})")
                return
            
            # 创建账号
            account = QingyingAccount.create(
                nickname=nickname,
                phone=phone,
                cookies=cookies
            )
            
            print(f"清影账号添加成功: {nickname} ({phone})")
        else:
            print(f"清影账号添加失败: {result.get('message')}")
            
    except Exception as e:
        print(f"处理清影账号添加任务时出错: {str(e)}")

@qingying_accounts_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """删除指定清影账号"""
    try:
        account = QingyingAccount.get_by_id(account_id)
        nickname = account.nickname
        account.delete_instance()
        
        print(f"成功删除清影账号: {nickname}")
        return jsonify({'success': True, 'message': f'成功删除账号: {nickname}'})
        
    except QingyingAccount.DoesNotExist:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    except Exception as e:
        print(f"删除清影账号失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_accounts_bp.route('/clear', methods=['DELETE'])
def clear_all_accounts():
    """清空所有清影账号"""
    try:
        count = QingyingAccount.delete().execute()
        print(f"成功清空所有清影账号，共删除 {count} 个账号")
        return jsonify({'success': True, 'message': f'成功清空所有账号，共删除 {count} 个'})
        
    except Exception as e:
        print(f"清空清影账号失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_accounts_bp.route('/usage-stats', methods=['GET'])
def get_usage_stats():
    """获取清影账号使用统计"""
    try:
        # 总账号数
        total_accounts = QingyingAccount.select().count()
        
        # 有Cookie的账号数
        accounts_with_cookies = QingyingAccount.select().where(
            QingyingAccount.cookies.is_null(False) & (QingyingAccount.cookies != '')
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_accounts': total_accounts,
                'accounts_with_cookies': accounts_with_cookies,
                'accounts_without_cookies': total_accounts - accounts_with_cookies
            }
        })
        
    except Exception as e:
        print(f"获取清影账号使用统计失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_accounts_bp.route('/<int:account_id>/get-cookie', methods=['POST'])
def get_account_cookie(account_id):
    """获取指定账号的Cookie"""
    try:
        # 检查账号是否存在
        account = QingyingAccount.get_by_id(account_id)
        
        print(f"开始获取清影账号 {account.nickname} 的Cookie...")
        
        # 提交到全局线程池处理
        from backend.core.global_task_manager import global_task_manager
        
        if global_task_manager and global_task_manager.global_executor:
            # 提交Cookie获取任务到线程池
            future = global_task_manager.global_executor.submit(
                _process_cookie_task,
                account_id=account_id,
                account_nickname=account.nickname
            )
            
            print(f"已提交清影账号 {account.nickname} 的Cookie获取任务到线程池")
            return jsonify({
                'success': True, 
                'message': f'已开始为账号 {account.nickname} 获取Cookie，请稍后查看结果'
            })
        else:
            return jsonify({
                'success': False, 
                'message': '全局任务管理器未初始化'
            }), 500
        
    except QingyingAccount.DoesNotExist:
        return jsonify({'success': False, 'message': '账号不存在'}), 404
    except Exception as e:
        print(f"获取清影账号Cookie失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

def _process_cookie_task(account_id, account_nickname):
    """处理Cookie获取任务"""
    try:
        print(f"开始处理清影账号 {account_nickname} 的Cookie获取任务...")
        
        # 调用登录函数获取Cookie
        result = asyncio.run(login_and_get_cookie(headless=True))
        
        if result.get('code') == 200:
            account_data = result.get('data')
            cookies = account_data.get('cookies')
            
            # 更新数据库中的Cookie
            account = QingyingAccount.get_by_id(account_id)
            account.cookies = cookies
            account.updated_at = datetime.now()
            account.save()
            
            print(f"清影账号 {account_nickname} Cookie获取成功并已保存")
        else:
            print(f"清影账号 {account_nickname} Cookie获取失败: {result.get('message')}")
            
    except Exception as e:
        print(f"处理清影账号 {account_nickname} Cookie获取任务时出错: {str(e)}") 