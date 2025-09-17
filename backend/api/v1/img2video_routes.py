# -*- coding: utf-8 -*-
"""
即梦图生视频API路由
"""

import os
import json
import requests
import asyncio
import pandas as pd
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.models.models import JimengImg2VideoTask
import subprocess
import platform
import threading
from urllib.parse import urlparse

# 创建蓝图
jimeng_img2video_bp = Blueprint('jimeng_img2video', __name__, url_prefix='/api/jimeng/img2video')

@jimeng_img2video_bp.route('/tasks', methods=['GET'])
def get_img2video_tasks():
    """获取图生视频任务列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        status = request.args.get('status', None)
        
        print("获取图生视频任务列表，页码: {}, 每页数量: {}, 状态: {}".format(page, page_size, status))
        
        # 构建查询 - 过滤掉空任务
        query = JimengImg2VideoTask.select()
        if status is not None:
            query = query.where(JimengImg2VideoTask.status == status)
        
        # 分页
        total = query.count()
        tasks = query.order_by(JimengImg2VideoTask.create_at.desc()).paginate(page, page_size)
        
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'prompt': task.prompt,
                'model': task.model,
                'second': task.second,
                'status': task.status,
                'status_text': task.get_status_text(),
                'account_id': task.account_id,
                'image_path': task.image_path,
                'video_url': task.video_url,
                'failure_reason': task.failure_reason,  # 失败原因类型
                'error_message': task.error_message,  # 详细错误信息
                'create_at': task.create_at.strftime('%Y-%m-%d %H:%M:%S') if task.create_at else None,
                'update_at': task.update_at.strftime('%Y-%m-%d %H:%M:%S') if task.update_at else None
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
        print(f"获取图生视频任务列表失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks', methods=['POST'])
def create_img2video_task():
    """创建图生视频任务"""
    try:
        data = request.get_json()
        
        # 单个任务创建
        if 'prompt' in data and 'image_path' in data:
            task = JimengImg2VideoTask.create(
                prompt=data['prompt'],
                model=data.get('model', 'Video 3.0'),
                second=data.get('second', 5),
                image_path=data['image_path'],
                status=0
            )
            
            print(f"创建图生视频任务: {task.id}")
            return jsonify({'success': True, 'data': {'task_id': task.id}})
        
        # 批量任务创建
        elif 'tasks' in data:
            tasks = data['tasks']
            created_tasks = []
            
            for task_data in tasks:
                task = JimengImg2VideoTask.create(
                    prompt=task_data.get('prompt', ''),
                    model=task_data.get('model', 'Video 3.0'),
                    second=task_data.get('second', 5),
                    image_path=task_data['image_path'],
                    status=0
                )
                created_tasks.append(task.id)
            
            print(f"批量创建图生视频任务: {len(created_tasks)}个")
            return jsonify({'success': True, 'data': {'task_ids': created_tasks}})
        
        else:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
            
    except Exception as e:
        print(f"创建图生视频任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_img2video_task(task_id):
    """删除图生视频任务"""
    try:
        task = JimengImg2VideoTask.get_by_id(task_id)
        task.delete_instance()
        
        print(f"删除图生视频任务: {task_id}")
        return jsonify({'success': True, 'message': '任务删除成功'})
        
    except JimengImg2VideoTask.DoesNotExist:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    except Exception as e:
        print(f"删除图生视频任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks/<int:task_id>/retry', methods=['POST'])
def retry_img2video_task(task_id):
    """重试图生视频任务"""
    try:
        task = JimengImg2VideoTask.get_by_id(task_id)
        task.update_status(0)  # 重置为排队状态
        
        print(f"重试图生视频任务: {task_id}")
        return jsonify({'success': True, 'message': '任务已重新加入队列'})
        
    except JimengImg2VideoTask.DoesNotExist:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    except Exception as e:
        print(f"重试图生视频任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks/batch-retry', methods=['POST'])
def batch_retry_img2video_tasks():
    """批量重试失败的图生视频任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if task_ids:
            # 如果提供了特定的任务ID列表，只重试这些任务
            tasks = JimengImg2VideoTask.select().where(
                JimengImg2VideoTask.id.in_(task_ids),
                JimengImg2VideoTask.status == 3  # 只重试失败的任务
            )
            retry_count = 0
            for task in tasks:
                task.update_status(0)  # 重置为排队状态
                retry_count += 1
        else:
            # 如果没有提供任务ID，重试所有失败的任务
            tasks = JimengImg2VideoTask.select().where(
                JimengImg2VideoTask.status == 3  # 只重试失败的任务
            )
            retry_count = 0
            for task in tasks:
                task.update_status(0)  # 重置为排队状态
                retry_count += 1
        
        print(f"批量重试图生视频任务: {retry_count}个")
        return jsonify({
            'success': True,
            'message': f'已重新加入队列 {retry_count} 个任务',
            'data': {
                'retry_count': retry_count
            }
        })
        
    except Exception as e:
        print(f"批量重试图生视频任务失败: {str(e)}")
        return jsonify({'success': False, 'message': f'批量重试失败: {str(e)}'}), 500

@jimeng_img2video_bp.route('/tasks/batch-delete', methods=['POST'])
def batch_delete_img2video_tasks():
    """批量删除图生视频任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({'success': False, 'message': '未提供任务ID'}), 400
        
        # 删除任务
        deleted_count = JimengImg2VideoTask.delete().where(JimengImg2VideoTask.id.in_(task_ids)).execute()
        
        print(f"批量删除图生视频任务: {deleted_count}个")
        return jsonify({'success': True, 'message': f'成功删除 {deleted_count} 个任务'})
        
    except Exception as e:
        print(f"批量删除图生视频任务失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks/import-folder', methods=['POST'])
def import_folder_tasks():
    """从文件夹导入图片任务"""
    try:
        # 获取请求数据
        data = request.get_json()
        model = data.get('model', 'Video 3.0')  # 默认为Video 3.0
        second = data.get('second', 5)  # 默认为5秒
        use_prompt = data.get('usePrompt', False)  # 是否使用提示词
        prompt = data.get('prompt', '')  # 提示词内容
        
        print(f"导入文件夹任务，模型: {model}, 时长: {second}秒, 使用提示词: {use_prompt}, 提示词: {prompt}")
        
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
                
                # 扫描文件夹中的图片文件
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
                image_files = []
                
                for filename in os.listdir(folder_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in image_extensions:
                        image_files.append(os.path.join(folder_path, filename))
                
                print(f"找到 {len(image_files)} 张图片")
                
                # 创建任务
                created_count = 0
                for image_path in image_files:
                    try:
                        # 根据usePrompt参数决定是否使用提示词
                        task_prompt = prompt if use_prompt else ''
                        
                        task = JimengImg2VideoTask.create(
                            prompt=task_prompt,  # 根据usePrompt参数决定提示词
                            model=model,  # 使用传入的模型参数
                            second=second,  # 使用传入的时长参数
                            image_path=image_path,
                            status=0
                        )
                        created_count += 1
                    except Exception as e:
                        print(f"创建任务失败 {image_path}: {str(e)}")
                
                print(f"成功创建 {created_count} 个图生视频任务，模型: {model}, 时长: {second}秒, 提示词: {task_prompt}")
                
            except Exception as e:
                print(f"文件夹导入失败: {str(e)}")
        
        # 在后台线程中执行文件夹选择和导入
        import_thread = threading.Thread(target=select_folder_and_import)
        import_thread.daemon = True
        import_thread.start()
        
        return jsonify({'success': True, 'message': '正在打开文件夹选择对话框，请选择包含图片的文件夹'})
        
    except Exception as e:
        print(f"导入文件夹失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@jimeng_img2video_bp.route('/tasks/batch-add', methods=['POST'])
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
        model = request.form.get('model', 'Video 3.0')
        second = int(request.form.get('second', 5))

        # 支持的图片格式
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        # 创建临时目录保存上传的图片
        import uuid
        from werkzeug.utils import secure_filename
        
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tmp', 'batch_upload')
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
                task = JimengImg2VideoTask.create(
                    prompt=prompt,
                    model=model,
                    second=second,
                    image_path=file_path,
                    status=0
                )
                created_tasks.append(task.id)
                print(f"创建图生视频任务: {task.id}, 图片: {filename}, 提示词: {prompt}")

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

@jimeng_img2video_bp.route('/tasks/batch-download', methods=['POST'])
def batch_download_videos():
    """批量下载任务视频"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请提供要下载的任务ID列表'
            }), 400
        
        # 获取任务信息
        tasks = list(JimengImg2VideoTask.select().where(
            JimengImg2VideoTask.id.in_(task_ids),
            JimengImg2VideoTask.status == 2  # 只下载已完成的任务
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
                    'filename': f'task_{task.id}_video.mp4'
                })
        
        if not all_videos:
            return jsonify({
                'success': False,
                'message': '选中的任务没有视频可下载'
            }), 400
        
        # 在后台线程中选择文件夹并下载
        def download_in_background():
            try:
                # 使用系统原生对话框选择文件夹
                download_dir = None
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    try:
                        print("正在调用macOS文件选择器...")
                        # 使用osascript调用macOS原生文件选择器
                        applescript = '''
                        tell application "Finder"
                            activate
                            set selectedFolder to choose folder with prompt "选择视频下载文件夹" default location (path to downloads folder)
                            return POSIX path of selectedFolder
                        end tell
                        '''
                        result = subprocess.run([
                            'osascript', '-e', applescript
                        ], capture_output=True, text=True, timeout=60)
                        
                        print(f"文件选择器返回码: {result.returncode}")
                        print(f"文件选择器输出: {result.stdout}")
                        print(f"文件选择器错误: {result.stderr}")
                        
                        if result.returncode == 0 and result.stdout.strip():
                            download_dir = result.stdout.strip()
                            print(f"用户选择了文件夹: {download_dir}")
                        elif result.returncode == 1:
                            print("用户取消了文件夹选择")
                            return
                        else:
                            print(f"文件选择器异常退出，返回码: {result.returncode}")
                    except subprocess.TimeoutExpired:
                        print("文件选择器超时，用户可能没有响应")
                        return
                    except Exception as e:
                        print(f"macOS文件选择器失败: {str(e)}")
                        
                elif system == "Windows":  # Windows
                    try:
                        # 使用PowerShell调用Windows文件选择器
                        ps_script = """
                        Add-Type -AssemblyName System.Windows.Forms
                        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
                        $folderBrowser.Description = "选择视频下载文件夹"
                        $folderBrowser.SelectedPath = [Environment]::GetFolderPath("MyDocuments")
                        $result = $folderBrowser.ShowDialog()
                        if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
                            Write-Output $folderBrowser.SelectedPath
                        }
                        """
                        result = subprocess.run(['powershell', '-Command', ps_script], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode == 0 and result.stdout.strip():
                            download_dir = result.stdout.strip()
                    except Exception as e:
                        print(f"Windows文件选择器失败: {str(e)}")
                        
                else:  # Linux
                    try:
                        # 尝试使用zenity
                        result = subprocess.run([
                            'zenity', '--file-selection', '--directory', 
                            '--title=选择视频下载文件夹'
                        ], capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            download_dir = result.stdout.strip()
                    except Exception as e:
                        print(f"Linux文件选择器失败: {str(e)}")
                
                # 如果原生对话框失败，使用默认下载目录
                if not download_dir:
                    download_dir = os.path.expanduser("~/Downloads")
                    print(f"文件选择器失败，使用默认下载目录: {download_dir}")
                
                # 确保目录存在
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir, exist_ok=True)
                
                print(f"开始下载 {len(all_videos)} 个视频到: {download_dir}")
                
                # 创建以当前时间命名的子文件夹
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                batch_folder = os.path.join(download_dir, f"jimeng_videos_{timestamp}")
                os.makedirs(batch_folder, exist_ok=True)
                
                # 准备下载信息
                file_infos = []
                for video_info in all_videos:
                    file_infos.append({
                        'url': video_info['url'],
                        'file_path': os.path.join(batch_folder, video_info['filename']),
                        'filename': video_info['filename']
                    })
                
                # 使用带重试机制的批量下载
                from utils.download_util import batch_download_files
                download_result = batch_download_files(
                    file_infos=file_infos,
                    max_retries=5,
                    delay_between_downloads=1.0,
                    timeout=60
                )
                
                success_count = download_result['success_count']
                error_count = download_result['failed_count']
                
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
        print(f"批量下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量下载失败: {str(e)}'
        }), 500

@jimeng_img2video_bp.route('/stats', methods=['GET'])
def get_img2video_stats():
    """获取图生视频统计信息"""
    try:
        # 统计时过滤掉空任务
        base_query = JimengImg2VideoTask.select()
        total_tasks = base_query.count()
        pending_tasks = base_query.where(JimengImg2VideoTask.status == 0).count()
        processing_tasks = base_query.where(JimengImg2VideoTask.status == 1).count()
        completed_tasks = base_query.where(JimengImg2VideoTask.status == 2).count()
        failed_tasks = base_query.where(JimengImg2VideoTask.status == 3).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'processing_tasks': processing_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks
            }
        })
        
    except Exception as e:
        print(f"获取图生视频统计失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500 

@jimeng_img2video_bp.route('/tasks/delete-before-today', methods=['DELETE'])
def delete_tasks_before_today():
    """删除今日前的所有图生视频任务"""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # 获取今日开始时间（凌晨0点）
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today_start = datetime.now(beijing_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询今日前的任务
        before_today_tasks = JimengImg2VideoTask.select().where(
            JimengImg2VideoTask.create_at < today_start
        )
        
        count = before_today_tasks.count()
        
        if count == 0:
            return jsonify({
                'success': True,
                'message': '没有今日前的任务需要删除',
                'data': {'deleted_count': 0}
            })
        
        # 删除任务
        deleted_count = JimengImg2VideoTask.delete().where(
            JimengImg2VideoTask.create_at < today_start
        ).execute()
        
        print(f"删除了 {deleted_count} 个今日前的图生视频任务")
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 个今日前的任务',
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        print(f"删除今日前任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除今日前任务失败: {str(e)}'
        }), 500

@jimeng_img2video_bp.route('/tasks/batch-create-from-table', methods=['POST'])
def batch_create_tasks_from_table():
    """从表格批量创建图生视频任务"""
    try:
        data = request.get_json()
        if not data or 'tasks' not in data:
            return jsonify({
                'success': False,
                'message': '请提供任务数据'
            }), 400

        tasks_data = data['tasks']
        if not tasks_data or not isinstance(tasks_data, list):
            return jsonify({
                'success': False,
                'message': '任务数据格式错误'
            }), 400

        created_tasks = []
        failed_tasks = []

        for i, task_data in enumerate(tasks_data):
            try:
                # 验证必需字段
                if 'image_path' not in task_data or not task_data['image_path']:
                    failed_tasks.append(f"第 {i+1} 行: 缺少图片路径")
                    continue

                image_path = task_data['image_path'].strip()
                prompt = task_data.get('prompt', '').strip()
                model = task_data.get('model', 'Video 3.0')
                second = int(task_data.get('second', 5))

                # 验证图片路径是否存在
                if not os.path.exists(image_path):
                    failed_tasks.append(f"第 {i+1} 行: 图片文件不存在 - {image_path}")
                    continue

                # 创建任务
                task = JimengImg2VideoTask.create(
                    prompt=prompt,
                    model=model,
                    second=second,
                    image_path=image_path,
                    status=0
                )
                created_tasks.append(task.id)
                print(f"从表格创建图生视频任务: {task.id}, 图片: {image_path}, 提示词: {prompt}, 模型: {model}, 时长: {second}s")

            except Exception as e:
                failed_tasks.append(f"第 {i+1} 行: {str(e)}")
                print(f"处理第 {i+1} 行任务失败: {str(e)}")

        # 返回结果
        result_message = f"成功创建 {len(created_tasks)} 个任务"
        if failed_tasks:
            result_message += f"，{len(failed_tasks)} 个任务创建失败"

        return jsonify({
            'success': True,
            'message': result_message,
            'data': {
                'created_count': len(created_tasks),
                'failed_count': len(failed_tasks),
                'created_task_ids': created_tasks,
                'failed_tasks': failed_tasks
            }
        })

    except Exception as e:
        print(f"表格批量创建任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'表格批量创建任务失败: {str(e)}'
        }), 500 