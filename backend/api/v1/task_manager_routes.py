# -*- coding: utf-8 -*-
"""
任务管理器API路由
"""
from flask import Blueprint, jsonify, request
from backend.core.global_task_manager import global_task_manager

# 创建蓝图
task_manager_bp = Blueprint('task_manager', __name__, url_prefix='/api/task-manager')

@task_manager_bp.route('/status', methods=['GET'])
def get_task_manager_status():
    """获取全局任务管理器状态"""
    try:
        print("获取全局任务管理器状态")
        status = global_task_manager.get_status()
        
        return jsonify({
            'success': True,
            'data': status,
            'message': '获取全局任务管理器状态成功'
        })
        
    except Exception as e:
        print("获取全局任务管理器状态失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取全局任务管理器状态失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/threads', methods=['GET'])
def get_thread_details():
    """获取所有线程详细信息"""
    try:
        print("获取线程详细信息")
        threads = global_task_manager.get_all_thread_details()
        
        return jsonify({
            'success': True,
            'data': threads,
            'message': '获取线程详细信息成功'
        })
        
    except Exception as e:
        print("获取线程详细信息失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取线程详细信息失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/start', methods=['POST'])
def start_task_manager():
    """启动任务管理器"""
    try:
        print("启动任务管理器")
        success = global_task_manager.start()
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务管理器启动成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务管理器已经在运行或启动失败'
            }), 400
            
    except Exception as e:
        print("启动任务管理器失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '启动任务管理器失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/stop', methods=['POST'])
def stop_task_manager():
    """停止任务管理器"""
    try:
        print("停止任务管理器")
        success = global_task_manager.stop()
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务管理器停止成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务管理器已经停止或停止失败'
            }), 400
            
    except Exception as e:
        print("停止任务管理器失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '停止任务管理器失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/pause', methods=['POST'])
def pause_task_manager():
    """暂停任务管理器"""
    try:
        print("暂停任务管理器")
        success = global_task_manager.pause()
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务管理器暂停成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务管理器不在运行状态，无法暂停'
            }), 400
            
    except Exception as e:
        print("暂停任务管理器失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '暂停任务管理器失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/resume', methods=['POST'])
def resume_task_manager():
    """恢复任务管理器"""
    try:
        print("恢复任务管理器")
        success = global_task_manager.resume()
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务管理器恢复成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务管理器不在暂停状态，无法恢复'
            }), 400
            
    except Exception as e:
        print("恢复任务管理器失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '恢复任务管理器失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/summary', methods=['GET'])
def get_task_summary():
    """获取任务汇总信息"""
    try:
        print("获取任务汇总信息")
        summary = global_task_manager.get_global_summary()
        
        return jsonify({
            'success': True,
            'data': summary,
            'message': '获取任务汇总信息成功'
        })
        
    except Exception as e:
        print("获取任务汇总信息失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取任务汇总信息失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/stats', methods=['GET'])
def get_task_manager_stats():
    """获取任务管理器统计信息"""
    try:
        print("获取任务管理器统计信息")
        status = task_manager.get_status()
        queue_info = task_manager.get_task_queue_info()
        
        # 合并统计信息
        stats = {
            'manager': {
                'status': status.get('status'),
                'uptime': status.get('uptime', 0),
                'processing_count': status.get('processing_count', 0),
                'stats': status.get('stats', {})
            },
            'queue': queue_info
        }
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': '获取统计信息成功'
        })
        
    except Exception as e:
        print("获取统计信息失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取统计信息失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/processing-tasks', methods=['GET'])
def get_processing_tasks():
    """获取正在处理的任务列表"""
    try:
        print("获取正在处理的任务列表")
        status = task_manager.get_status()
        processing_tasks = status.get('processing_tasks', [])
        
        # 获取任务详细信息
        task_details = []
        if processing_tasks:
            from backend.models.models import JimengText2ImgTask
            for task_id in processing_tasks:
                try:
                    task = JimengText2ImgTask.get(JimengText2ImgTask.id == task_id)
                    task_details.append({
                        'id': task.id,
                        'prompt': task.prompt[:100] + '...' if len(task.prompt) > 100 else task.prompt,
                        'model': task.model,
                        'status': task.status,
                        'status_text': task.get_status_text(),
                        'create_at': task.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_at': task.update_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    continue
        
        return jsonify({
            'success': True,
            'data': {
                'processing_count': len(processing_tasks),
                'tasks': task_details
            },
            'message': '获取正在处理的任务列表成功'
        })
        
    except Exception as e:
        print("获取正在处理的任务列表失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '获取正在处理的任务列表失败: {}'.format(str(e))
        }), 500

@task_manager_bp.route('/health', methods=['GET'])
def task_manager_health():
    """任务管理器健康检查"""
    try:
        status = task_manager.get_status()
        is_healthy = status.get('status') in ['running', 'paused']
        
        return jsonify({
            'success': True,
            'data': {
                'healthy': is_healthy,
                'status': status.get('status'),
                'uptime': status.get('uptime', 0),
                'last_scan': status.get('stats', {}).get('last_scan_time'),
                'error_count': status.get('stats', {}).get('error_count', 0)
            },
            'message': '健康检查完成'
        })
        
    except Exception as e:
        print("任务管理器健康检查失败: {}".format(str(e)))
        return jsonify({
            'success': False,
            'message': '健康检查失败: {}'.format(str(e))
        }), 500 