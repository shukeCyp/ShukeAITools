# -*- coding: utf-8 -*-
"""
清影图生视频API路由
"""

import os
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid

from backend.models.models import QingyingImage2VideoTask, QingyingAccount
from backend.core.global_task_manager import global_task_manager

# 创建蓝图
qingying_img2video_bp = Blueprint('qingying_img2video', __name__, url_prefix='/api/v1/qingying/img2video')

def allowed_file(filename):
    """检查文件类型是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@qingying_img2video_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取图生视频任务列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询任务列表（按创建时间倒序）
        tasks_query = QingyingImage2VideoTask.select().order_by(QingyingImage2VideoTask.create_at.desc())
        total_count = tasks_query.count()
        
        tasks = list(tasks_query.offset(offset).limit(page_size))
        
        # 构建返回数据
        task_list = []
        for task in tasks:
            # 获取关联的账号信息
            account = None
            if task.account_id:
                try:
                    account = QingyingAccount.get_by_id(task.account_id)
                except QingyingAccount.DoesNotExist:
                    account = None
            
            task_data = {
                'id': task.id,
                'prompt': task.prompt,
                'generation_mode': task.generation_mode,
                'frame_rate': task.frame_rate,
                'resolution': task.resolution,
                'duration': task.duration,
                'ai_audio': task.ai_audio,
                'status': task.status,
                'status_text': task.get_status_text(),
                'image_path': task.image_path,
                'video_url': task.video_url,
                'create_at': task.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                'update_at': task.update_at.strftime('%Y-%m-%d %H:%M:%S'),
                'account_nickname': account.nickname if account else None,
                'account_id': task.account_id
            }
            task_list.append(task_data)
        
        return jsonify({
            'success': True,
            'data': task_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_count,
                'pages': (total_count + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取清影图生视频任务列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取任务列表失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/stats', methods=['GET'])
def get_stats():
    """获取任务统计信息"""
    try:
        # 获取今日任务统计
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        total_tasks = QingyingImage2VideoTask.select().count()
        today_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start
        ).count()
        
        # 按状态统计今日任务
        pending_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start,
            QingyingImage2VideoTask.status == 0
        ).count()
        
        processing_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start,
            QingyingImage2VideoTask.status == 1
        ).count()
        
        completed_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start,
            QingyingImage2VideoTask.status == 2
        ).count()
        
        failed_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start,
            QingyingImage2VideoTask.status == 3
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_tasks': total_tasks,
                'today_tasks': today_tasks,
                'pending_tasks': pending_tasks,
                'processing_tasks': processing_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取清影图生视频统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks', methods=['POST'])
def create_task():
    """创建新的图生视频任务"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择要上传的图片'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '请选择要上传的图片'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '不支持的图片格式，请上传PNG、JPG、JPEG、GIF、BMP或WebP格式的图片'
            }), 400
        
        # 获取表单数据
        prompt = request.form.get('prompt', '').strip()
        generation_mode = request.form.get('generation_mode', 'fast')
        frame_rate = request.form.get('frame_rate', '30')
        resolution = request.form.get('resolution', '720p')
        duration = request.form.get('duration', '5s')
        ai_audio = request.form.get('ai_audio', 'false').lower() == 'true'
        
        if not prompt:
            return jsonify({
                'success': False,
                'message': '请输入提示词'
            }), 400
        
        # 保存上传的图片
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # 确保tmp目录存在
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        
        file_path = os.path.join(tmp_dir, unique_filename)
        file.save(file_path)
        
        # 创建任务记录
        task = QingyingImage2VideoTask.create(
            prompt=prompt,
            generation_mode=generation_mode,
            frame_rate=frame_rate,
            resolution=resolution,
            duration=duration,
            ai_audio=ai_audio,
            image_path=file_path,
            status=0,  # 排队中
            create_at=datetime.now(),
            update_at=datetime.now()
        )
        
        # 提交任务到全局任务管理器
        if hasattr(global_task_manager, 'qingying_img2video_manager'):
            global_task_manager.qingying_img2video_manager.submit_task(task.id)
        
        return jsonify({
            'success': True,
            'message': '图生视频任务创建成功',
            'data': {
                'task_id': task.id,
                'status': task.status,
                'status_text': task.get_status_text()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"创建清影图生视频任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建任务失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除指定任务"""
    try:
        task = QingyingImage2VideoTask.get_by_id(task_id)
        
        # 删除关联的图片文件
        if task.image_path and os.path.exists(task.image_path):
            try:
                os.remove(task.image_path)
            except Exception as e:
                current_app.logger.warning(f"删除图片文件失败: {str(e)}")
        
        task.delete_instance()
        
        return jsonify({
            'success': True,
            'message': '任务删除成功'
        })
        
    except QingyingImage2VideoTask.DoesNotExist:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除清影图生视频任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除任务失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/delete-before-today', methods=['DELETE'])
def delete_tasks_before_today():
    """删除今日前的所有任务"""
    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # 查询今日前的任务
        tasks_to_delete = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at < today_start
        )
        
        deleted_count = 0
        for task in tasks_to_delete:
            # 删除关联的图片文件
            if task.image_path and os.path.exists(task.image_path):
                try:
                    os.remove(task.image_path)
                except Exception as e:
                    current_app.logger.warning(f"删除图片文件失败: {str(e)}")
            
            task.delete_instance()
            deleted_count += 1
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个今日前的任务'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除今日前任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除今日前任务失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/retry/<int:task_id>', methods=['POST'])
def retry_task(task_id):
    """重试指定任务"""
    try:
        task = QingyingImage2VideoTask.get_by_id(task_id)
        
        # 重置任务状态
        task.status = 0  # 排队中
        task.account_id = None
        task.video_url = None
        task.update_at = datetime.now()
        task.save()
        
        # 重新提交任务到全局任务管理器
        if hasattr(global_task_manager, 'qingying_img2video_manager'):
            global_task_manager.qingying_img2video_manager.submit_task(task.id)
        
        return jsonify({
            'success': True,
            'message': '任务重试成功'
        })
        
    except QingyingImage2VideoTask.DoesNotExist:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    except Exception as e:
        current_app.logger.error(f"重试清影图生视频任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'重试任务失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/batch-retry', methods=['POST'])
def batch_retry_tasks():
    """批量重试失败的任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请选择要重试的任务'
            }), 400
        
        retry_count = 0
        for task_id in task_ids:
            try:
                task = QingyingImage2VideoTask.get_by_id(task_id)
                
                # 重置任务状态
                task.status = 0  # 排队中
                task.account_id = None
                task.video_url = None
                task.update_at = datetime.now()
                task.save()
                
                # 重新提交任务到全局任务管理器
                if hasattr(global_task_manager, 'qingying_img2video_manager'):
                    global_task_manager.qingying_img2video_manager.submit_task(task.id)
                
                retry_count += 1
                
            except QingyingImage2VideoTask.DoesNotExist:
                current_app.logger.warning(f"任务 {task_id} 不存在，跳过")
                continue
        
        return jsonify({
            'success': True,
            'message': f'成功重试 {retry_count} 个任务'
        })
        
    except Exception as e:
        current_app.logger.error(f"批量重试清影图生视频任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量重试失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/import-folder', methods=['POST'])
def import_folder_tasks():
    """从文件夹导入图片任务"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', '')
        generation_mode = data.get('generation_mode', 'fast')
        frame_rate = data.get('frame_rate', '30')
        resolution = data.get('resolution', '720p')
        duration = data.get('duration', '5s')
        ai_audio = data.get('ai_audio', False)
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({
                'success': False,
                'message': '文件夹路径不存在'
            }), 400
        
        # 支持的图片格式
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        created_count = 0
        for filename in os.listdir(folder_path):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                source_path = os.path.join(folder_path, filename)
                
                # 复制文件到tmp目录
                file_ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
                
                tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tmp')
                os.makedirs(tmp_dir, exist_ok=True)
                
                dest_path = os.path.join(tmp_dir, unique_filename)
                
                import shutil
                shutil.copy2(source_path, dest_path)
                
                # 创建任务
                task = QingyingImage2VideoTask.create(
                    prompt=f"根据图片 {filename} 生成视频",
                    generation_mode=generation_mode,
                    frame_rate=frame_rate,
                    resolution=resolution,
                    duration=duration,
                    ai_audio=ai_audio,
                    image_path=dest_path,
                    status=0,
                    create_at=datetime.now(),
                    update_at=datetime.now()
                )
                
                # 提交任务到全局任务管理器
                if hasattr(global_task_manager, 'qingying_img2video_manager'):
                    global_task_manager.qingying_img2video_manager.submit_task(task.id)
                
                created_count += 1
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {created_count} 个图片任务'
        })
        
    except Exception as e:
        current_app.logger.error(f"导入文件夹任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/import-excel', methods=['POST'])
def import_excel_tasks():
    """从Excel导入任务"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'Excel文件路径不存在'
            }), 400
        
        import pandas as pd
        
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': 'Excel文件为空'
            }), 400
        
        # 检查必要的列
        if df.shape[1] < 2:
            return jsonify({
                'success': False,
                'message': 'Excel文件必须至少有2列（A列：图片路径，B列：提示词）'
            }), 400
        
        created_count = 0
        for index, row in df.iterrows():
            try:
                image_path = str(row.iloc[0]).strip()  # A列：图片路径
                prompt = str(row.iloc[1]).strip()     # B列：提示词
                
                if not image_path or not prompt or image_path == 'nan' or prompt == 'nan':
                    continue
                
                if not os.path.exists(image_path):
                    current_app.logger.warning(f"图片文件不存在: {image_path}")
                    continue
                
                # 复制文件到tmp目录
                file_ext = image_path.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
                
                tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tmp')
                os.makedirs(tmp_dir, exist_ok=True)
                
                dest_path = os.path.join(tmp_dir, unique_filename)
                
                import shutil
                shutil.copy2(image_path, dest_path)
                
                # 创建任务
                task = QingyingImage2VideoTask.create(
                    prompt=prompt,
                    generation_mode='fast',
                    frame_rate='30',
                    resolution='720p',
                    duration='5s',
                    ai_audio=False,
                    image_path=dest_path,
                    status=0,
                    create_at=datetime.now(),
                    update_at=datetime.now()
                )
                
                # 提交任务到全局任务管理器
                if hasattr(global_task_manager, 'qingying_img2video_manager'):
                    global_task_manager.qingying_img2video_manager.submit_task(task.id)
                
                created_count += 1
                
            except Exception as e:
                current_app.logger.warning(f"处理第 {index + 1} 行时出错: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {created_count} 个任务'
        })
        
    except Exception as e:
        current_app.logger.error(f"导入Excel任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500 