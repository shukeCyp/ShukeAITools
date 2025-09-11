# -*- coding: utf-8 -*-
"""
清影图生视频API路由
"""

import os
import time
import platform
import subprocess
import threading
import requests
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
                'failure_reason': task.failure_reason,  # 失败原因类型
                'error_message': task.error_message,  # 详细错误信息
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
        # 统计所有任务（与即梦保持一致）
        total_tasks = QingyingImage2VideoTask.select().count()
        pending_tasks = QingyingImage2VideoTask.select().where(QingyingImage2VideoTask.status == 0).count()
        processing_tasks = QingyingImage2VideoTask.select().where(QingyingImage2VideoTask.status == 1).count()
        completed_tasks = QingyingImage2VideoTask.select().where(QingyingImage2VideoTask.status == 2).count()
        failed_tasks = QingyingImage2VideoTask.select().where(QingyingImage2VideoTask.status == 3).count()
        
        # 获取今日任务统计
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_tasks = QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.create_at >= today_start
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
        # 获取请求数据
        data = request.get_json()
        generation_mode = data.get('generation_mode', 'fast')
        frame_rate = data.get('frame_rate', '30')
        resolution = data.get('resolution', '720p')
        duration = data.get('duration', '5s')
        ai_audio = data.get('ai_audio', False)
        
        print(f"清影导入文件夹任务，参数: {generation_mode}, {frame_rate}, {resolution}, {duration}, {ai_audio}")
        
        def select_folder_and_import():
            try:
                # 调用原生文件夹选择对话框
                folder_path = None
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    result = subprocess.run([
                        'osascript', '-e',
                        'tell application "Finder" to set folder_path to (choose folder with prompt "选择包含图片的文件夹") as string',
                        '-e',
                        'return POSIX path of folder_path'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                        
                elif system == "Windows":  # Windows
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Add-Type -AssemblyName System.Windows.Forms; $folder = New-Object System.Windows.Forms.FolderBrowserDialog; $folder.Description = "选择包含图片的文件夹"; $folder.ShowNewFolderButton = $true; if ($folder.ShowDialog() -eq "OK") { $folder.SelectedPath } else { "" }'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                        
                elif system == "Linux":  # Linux
                    result = subprocess.run([
                        'zenity', '--file-selection', '--directory',
                        '--title=选择包含图片的文件夹'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                
                if not folder_path:
                    print("用户取消了文件夹选择")
                    return
                
                print(f"选择的文件夹: {folder_path}")
                
                if not os.path.exists(folder_path):
                    print(f"文件夹不存在: {folder_path}")
                    return
                
                # 支持的图片格式
                supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                
                created_count = 0
                import shutil
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
                        
                        shutil.copy2(source_path, dest_path)
                        
                        # 创建任务
                        task = QingyingImage2VideoTask.create(
                            prompt="",
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
                
                print(f"成功导入 {created_count} 个图片任务")
                
            except Exception as e:
                print(f"处理文件夹失败: {str(e)}")
        
        # 在后台线程中执行文件选择和导入
        thread = threading.Thread(target=select_folder_and_import)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '开始选择文件夹并导入，请在弹出的对话框中选择包含图片的文件夹'
        })
        
    except Exception as e:
        current_app.logger.error(f"导入文件夹任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500

@qingying_img2video_bp.route('/tasks/batch-add', methods=['POST'])
def batch_add_tasks():
    """批量添加图生视频任务"""
    try:
        # 检查是否有图片文件
        if 'images' not in request.files:
            return jsonify({
                'success': False,
                'message': '请选择要上传的图片'
            }), 400

        files = request.files.getlist('images')
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                'success': False,
                'message': '请选择要上传的图片'
            }), 400

        # 获取配置参数
        generation_mode = request.form.get('generation_mode', 'fast')
        frame_rate = request.form.get('frame_rate', '30')
        resolution = request.form.get('resolution', '720p')
        duration = request.form.get('duration', '5s')
        ai_audio = request.form.get('ai_audio', 'false').lower() == 'true'

        # 创建临时目录保存上传的图片
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tmp', 'qingying_batch_upload')
        os.makedirs(tmp_dir, exist_ok=True)

        created_tasks = []
        failed_files = []

        for i, file in enumerate(files):
            try:
                if file.filename == '':
                    continue

                if not allowed_file(file.filename):
                    failed_files.append(f"{file.filename}: 不支持的文件格式")
                    continue

                # 保存上传的图片
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
                file_path = os.path.join(tmp_dir, unique_filename)
                file.save(file_path)

                # 获取对应的提示词
                prompt = request.form.get(f'prompts[{i}]', '')

                # 创建任务
                task = QingyingImage2VideoTask.create(
                    prompt=prompt,
                    generation_mode=generation_mode,
                    frame_rate=frame_rate,
                    resolution=resolution,
                    duration=duration,
                    ai_audio=ai_audio,
                    image_path=file_path,
                    status=0,
                    create_at=datetime.now(),
                    update_at=datetime.now()
                )

                # 提交任务到全局任务管理器
                if hasattr(global_task_manager, 'qingying_img2video_manager'):
                    global_task_manager.qingying_img2video_manager.submit_task(task.id)

                created_tasks.append(task.id)
                print(f"创建清影图生视频任务: {task.id}, 图片: {filename}, 提示词: {prompt}")

            except Exception as e:
                failed_files.append(f"{file.filename}: {str(e)}")
                print(f"处理文件 {file.filename} 失败: {str(e)}")

        # 构建响应消息
        message_parts = []
        if created_tasks:
            message_parts.append(f"成功创建 {len(created_tasks)} 个任务")
        if failed_files:
            message_parts.append(f"失败 {len(failed_files)} 个文件")

        return jsonify({
            'success': True,
            'message': ', '.join(message_parts) if message_parts else '没有创建任何任务',
            'data': {
                'created_count': len(created_tasks),
                'failed_count': len(failed_files),
                'created_task_ids': created_tasks,
                'failed_files': failed_files
            }
        })

    except Exception as e:
        print(f"批量添加任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_img2video_bp.route('/tasks/batch-delete', methods=['POST'])
def batch_delete_tasks():
    """批量删除任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请提供要删除的任务ID列表'
            }), 400
        
        # 删除任务
        deleted_count = 0
        for task_id in task_ids:
            try:
                task = QingyingImage2VideoTask.get_or_none(QingyingImage2VideoTask.id == task_id)
                if task:
                    # 删除图片文件
                    if task.image_path and os.path.exists(task.image_path):
                        try:
                            os.remove(task.image_path)
                        except Exception as e:
                            print(f"删除图片文件失败: {e}")
                    
                    task.delete_instance()
                    deleted_count += 1
            except Exception as e:
                print(f"删除任务 {task_id} 失败: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个任务',
            'data': {
                'deleted_count': deleted_count
            }
        })
        
    except Exception as e:
        print(f"批量删除任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@qingying_img2video_bp.route('/tasks/batch-download', methods=['POST'])
def batch_download_videos():
    """批量下载清影图生视频"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请提供要下载的任务ID列表'
            }), 400
        
        # 获取任务信息
        tasks = list(QingyingImage2VideoTask.select().where(
            QingyingImage2VideoTask.id.in_(task_ids),
            QingyingImage2VideoTask.status == 2  # 只下载已完成的任务
        ))
        
        if not tasks:
            return jsonify({
                'success': False,
                'message': '没有找到可下载的已完成任务'
            }), 400
        
        # 收集所有视频URL
        all_videos = []
        for task in tasks:
            if task.video_url:
                all_videos.append({
                    'task_id': task.id,
                    'url': task.video_url,
                    'filename': f'qingying_task_{task.id}_video.mp4'
                })
        
        if not all_videos:
            return jsonify({
                'success': False,
                'message': '选中的任务没有视频可下载'
            }), 400
        
        # 在后台线程中选择文件夹并下载
        def download_in_background():
            try:
                # 调用原生文件夹选择对话框
                download_dir = None
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    result = subprocess.run([
                        'osascript', '-e',
                        'tell application "Finder" to set folder_path to (choose folder with prompt "选择视频保存文件夹") as string',
                        '-e',
                        'return POSIX path of folder_path'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        download_dir = result.stdout.strip()
                        
                elif system == "Windows":  # Windows
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Add-Type -AssemblyName System.Windows.Forms; $folder = New-Object System.Windows.Forms.FolderBrowserDialog; $folder.Description = "选择视频保存文件夹"; $folder.ShowNewFolderButton = $true; if ($folder.ShowDialog() -eq "OK") { $folder.SelectedPath } else { "" }'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        download_dir = result.stdout.strip()
                        
                elif system == "Linux":  # Linux
                    result = subprocess.run([
                        'zenity', '--file-selection', '--directory',
                        '--title=选择视频保存文件夹'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        download_dir = result.stdout.strip()
                
                if not download_dir:
                    print("用户取消了文件夹选择")
                    return
                
                print(f"选择的下载目录: {download_dir}")
                
                # 创建批量下载文件夹
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                batch_folder = os.path.join(download_dir, f"qingying_videos_{timestamp}")
                os.makedirs(batch_folder, exist_ok=True)
                
                success_count = 0
                error_count = 0
                
                # 下载每个视频
                for video_info in all_videos:
                    try:
                        response = requests.get(video_info['url'], timeout=60)
                        response.raise_for_status()
                        
                        file_path = os.path.join(batch_folder, video_info['filename'])
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        success_count += 1
                        print(f"下载成功: {video_info['filename']}")
                        
                    except Exception as e:
                        error_count += 1
                        print(f"下载失败 {video_info['filename']}: {str(e)}")
                
                print(f"批量下载完成: 成功 {success_count} 个，失败 {error_count} 个")
                print(f"文件保存位置: {batch_folder}")
                
            except Exception as e:
                print(f"批量下载过程出错: {str(e)}")
        
        # 在后台线程中执行下载
        download_thread = threading.Thread(target=download_in_background)
        download_thread.daemon = True
        download_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'开始下载 {len(all_videos)} 个视频，请选择下载文件夹',
            'data': {
                'total_videos': len(all_videos),
                'tasks_count': len(tasks)
            }
        })
        
    except Exception as e:
        print(f"清影批量下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量下载失败: {str(e)}'
        }), 500 