# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models.models import JimengAccount

# 创建蓝图
jimeng_accounts_bp = Blueprint('jimeng_accounts', __name__, url_prefix='/api/jimeng/accounts')

@jimeng_accounts_bp.route('', methods=['GET'])
def get_accounts():
    """获取所有账号"""
    print("获取即梦账号列表")
    try:
        accounts = list(JimengAccount.select())
        data = []
        for account in accounts:
            data.append({
                'id': account.id,
                'account': account.account,
                'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': account.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        print("成功获取账号列表，总数: {}".format(len(data)))
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        print("获取账号列表失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取账号列表失败: {}'.format(str(e))
        }), 500

@jimeng_accounts_bp.route('', methods=['POST'])
def add_accounts():
    """批量添加账号"""
    try:
        data = request.get_json()
        accounts_text = data.get('accounts_text', '')
        
        if not accounts_text.strip():
            return jsonify({
                'success': False,
                'message': '请提供账号信息'
            }), 400
            
        print("开始批量添加即梦账号")
        
        lines = accounts_text.strip().split('\n')
        added_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '----' in line:
                parts = line.split('----')
                if len(parts) >= 2:
                    account = parts[0].strip()
                    password = parts[1].strip()
                    
                    if account and password:
                        JimengAccount.create(
                            account=account,
                            password=password
                        )
                        added_count += 1
                        print("添加账号: {}".format(account))
        
        print("批量添加完成，成功添加 {} 个账号".format(added_count))
        return jsonify({
            'success': True,
            'message': '成功添加 {} 个账号'.format(added_count),
            'added_count': added_count
        })
        
    except Exception as e:
        print("批量添加账号失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '添加失败: {}'.format(str(e))
        }), 500

@jimeng_accounts_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """删除指定账号"""
    try:
        print("删除即梦账号，ID: {}".format(account_id))
        account = JimengAccount.get(JimengAccount.id == account_id)
        deleted_account = account.account
        account.delete_instance()
        
        print("成功删除账号: {}".format(deleted_account))
        return jsonify({
            'success': True,
            'message': '已成功删除账号: {}'.format(deleted_account)
        })
        
    except JimengAccount.DoesNotExist:
        print("删除失败：账号不存在，ID: {}".format(account_id))
        return jsonify({
            'success': False,
            'message': '账号不存在'
        }), 404
        
    except Exception as e:
        print("删除账号异常，ID: {}, 错误: {}".format(account_id, str(e)))
        return jsonify({
            'success': False,
            'message': '删除失败: {}'.format(str(e))
        }), 500

@jimeng_accounts_bp.route('/clear', methods=['DELETE'])
def clear_all_accounts():
    """清空所有账号"""
    try:
        print("警告：开始清空所有即梦账号")
        deleted_count = JimengAccount.delete().execute()
        print("已清空所有账号，共删除 {} 个".format(deleted_count))
        return jsonify({
            'success': True,
            'message': '已清空所有账号，共删除 {} 个'.format(deleted_count),
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print("清空所有账号异常: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '清空失败: {}'.format(str(e))
        }), 500

@jimeng_accounts_bp.route('/usage-stats', methods=['GET'])
def get_account_usage_stats():
    """获取账号使用情况统计"""
    try:
        from datetime import date
        from backend.models.models import JimengText2ImgTask
        
        today = date.today()
        accounts = list(JimengAccount.select())
        
        stats = []
        for account in accounts:
            # 统计今日使用次数
            today_text2img = JimengText2ImgTask.select().where(
                (JimengText2ImgTask.account_id == account.id) &
                (JimengText2ImgTask.status.in_([1, 2])) &  # 处理中或已完成
                (JimengText2ImgTask.create_at >= today)
            ).count()
            
            # 统计总使用次数
            total_text2img = JimengText2ImgTask.select().where(
                (JimengText2ImgTask.account_id == account.id) &
                (JimengText2ImgTask.status == 2)  # 已完成
            ).count()
            
            stats.append({
                'id': account.id,
                'account': account.account,
                'today_text2img': today_text2img,
                'today_limit': 10,
                'today_remaining': max(0, 10 - today_text2img),
                'total_text2img': total_text2img,
                'status': 'available' if today_text2img < 10 else 'limit_reached',
                'last_used': None  # 可以后续添加最后使用时间
            })
        
        return jsonify({
            'success': True,
            'data': {
                'accounts': stats,
                'summary': {
                    'total_accounts': len(accounts),
                    'available_accounts': len([s for s in stats if s['status'] == 'available']),
                    'total_today_usage': sum(s['today_text2img'] for s in stats),
                    'total_remaining': sum(s['today_remaining'] for s in stats)
                }
            },
            'message': '获取账号使用统计成功'
        })
        
    except Exception as e:
        print("获取账号使用统计失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取统计失败: {}'.format(str(e))
        }), 500