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
        query = JimengImg2VideoTask.select().where(JimengImg2VideoTask.is_empty_task == False)
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
                JimengImg2VideoTask.status == 3,  # 只重试失败的任务
                JimengImg2VideoTask.is_empty_task == False  # 排除空任务
            )
            retry_count = 0
            for task in tasks:
                task.update_status(0)  # 重置为排队状态
                retry_count += 1
        else:
            # 如果没有提供任务ID，重试所有失败的任务
            tasks = JimengImg2VideoTask.select().where(
                JimengImg2VideoTask.status == 3,  # 只重试失败的任务
                JimengImg2VideoTask.is_empty_task == False  # 排除空任务
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
        
        print(f"导入文件夹任务，模型: {model}, 时长: {second}秒")
        
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
                        task = JimengImg2VideoTask.create(
                            prompt='',  # 文件夹导入时提示词为空
                            model=model,  # 使用传入的模型参数
                            second=second,  # 使用传入的时长参数
                            image_path=image_path,
                            status=0
                        )
                        created_count += 1
                    except Exception as e:
                        print(f"创建任务失败 {image_path}: {str(e)}")
                
                print(f"成功创建 {created_count} 个图生视频任务，模型: {model}, 时长: {second}秒")
                
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

@jimeng_img2video_bp.route('/tasks/import-excel', methods=['POST'])
def import_excel_tasks():
    """从Excel文件导入任务"""
    try:
        def select_file_and_import():
            try:
                # 调用原生文件选择对话框
                file_path = None
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    result = subprocess.run([
                        'osascript', '-e',
                        'tell application "Finder" to set file_path to (choose file with prompt "选择Excel文件 (A列:图片路径, B列:提示词)" of type {"xlsx", "xls", "csv"}) as string',
                        '-e',
                        'return POSIX path of file_path'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        file_path = result.stdout.strip()
                        
                elif system == "Windows":  # Windows
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Add-Type -AssemblyName System.Windows.Forms; $file = New-Object System.Windows.Forms.OpenFileDialog; $file.Filter = "Excel文件 (*.xlsx;*.xls;*.csv)|*.xlsx;*.xls;*.csv"; $file.Title = "选择Excel文件 (A列:图片路径, B列:提示词)"; if ($file.ShowDialog() -eq "OK") { $file.FileName } else { "" }'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        file_path = result.stdout.strip()
                        
                elif system == "Linux":  # Linux
                    result = subprocess.run([
                        'zenity', '--file-selection',
                        '--title=选择Excel文件 (A列:图片路径, B列:提示词)',
                        '--file-filter=Excel文件 | *.xlsx *.xls *.csv'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        file_path = result.stdout.strip()
                
                if not file_path:
                    print("用户取消了文件选择")
                    return
                
                print(f"选择的Excel文件: {file_path}")
                
                # 读取Excel文件
                try:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path, header=None)
                    else:
                        df = pd.read_excel(file_path, header=None)
                    
                    print(f"Excel文件读取成功，共 {len(df)} 行数据")
                    
                    # 创建任务
                    created_count = 0
                    for index, row in df.iterrows():
                        try:
                            image_path = str(row[0]) if pd.notna(row[0]) else ''
                            prompt = str(row[1]) if len(row) > 1 and pd.notna(row[1]) else ''
                            
                            if not image_path:
                                continue
                                
                            # 检查图片文件是否存在
                            if not os.path.exists(image_path):
                                print(f"图片文件不存在，跳过: {image_path}")
                                continue
                            
                            task = JimengImg2VideoTask.create(
                                prompt=prompt,
                                model='Video 3.0',
                                second=5,
                                image_path=image_path,
                                status=0
                            )
                            created_count += 1
                            
                        except Exception as e:
                            print(f"创建任务失败 第{index+1}行: {str(e)}")
                    
                    print(f"成功创建 {created_count} 个图生视频任务")
                    
                except Exception as e:
                    print(f"读取Excel文件失败: {str(e)}")
                
            except Exception as e:
                print(f"Excel导入失败: {str(e)}")
        
        # 在后台线程中执行文件选择和导入
        import_thread = threading.Thread(target=select_file_and_import)
        import_thread.daemon = True
        import_thread.start()
        
        return jsonify({'success': True, 'message': '正在打开文件选择对话框，请选择Excel文件'})
        
    except Exception as e:
        print(f"导入Excel失败: {str(e)}")
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
        base_query = JimengImg2VideoTask.select().where(JimengImg2VideoTask.is_empty_task == False)
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