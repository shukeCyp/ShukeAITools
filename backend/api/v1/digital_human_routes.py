"""
即梦数字人任务管理API
"""

import os
import tempfile
import uuid
import platform
import subprocess
import threading
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from backend.models.models import JimengDigitalHumanTask, JimengAccount

# 创建蓝图
jimeng_digital_human_bp = Blueprint('jimeng_digital_human', __name__, url_prefix='/api/jimeng/digital-human')

@jimeng_digital_human_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取数字人任务列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status_filter = request.args.get('status', 'all')
        
        # 构建查询
        query = JimengDigitalHumanTask.select()
        
        if status_filter != 'all':
            try:
                status_value = int(status_filter)
                query = query.where(JimengDigitalHumanTask.status == status_value)
            except ValueError:
                pass
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        tasks = (query.order_by(JimengDigitalHumanTask.create_at.desc())
                .paginate(page, per_page))
        
        # 转换为字典列表
        task_list = []
        for task in tasks:
            # 获取账号信息
            account_info = None
            if task.account_id:
                try:
                    account = JimengAccount.get_by_id(task.account_id)
                    account_info = account.account
                except:
                    account_info = f"账号ID:{task.account_id}"
            
            task_dict = {
                'id': task.id,
                'image_path': task.image_path,
                'audio_path': task.audio_path,
                'status': task.status,
                'account_id': task.account_id,
                'account_info': account_info,
                'create_at': task.create_at.isoformat() if task.create_at else None,
                'start_time': task.start_time.isoformat() if task.start_time else None,
                'video_url': task.video_url,

            }
            task_list.append(task_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'tasks': task_list,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        print(f"获取数字人任务列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取任务列表失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks', methods=['POST'])
def create_task():
    """创建数字人任务"""
    try:
        # 检查文件上传
        if 'image' not in request.files or 'audio' not in request.files:
            return jsonify({
                'success': False,
                'message': '请同时上传图片和音频文件'
            }), 400
        
        image_file = request.files['image']
        audio_file = request.files['audio']
        
        if image_file.filename == '' or audio_file.filename == '':
            return jsonify({
                'success': False,
                'message': '请选择有效的图片和音频文件'
            }), 400
        
        # 创建tmp目录（在后端根目录下）
        import os
        from pathlib import Path
        
        # 获取后端根目录
        backend_root = Path(__file__).parent.parent.parent  # 从api/v1/ 向上两级到backend/
        tmp_dir = backend_root / 'tmp'
        tmp_dir.mkdir(exist_ok=True)
        
        # 生成唯一文件名
        image_ext = os.path.splitext(image_file.filename)[1]
        audio_ext = os.path.splitext(audio_file.filename)[1]
        
        unique_id = str(uuid.uuid4())
        image_filename = f"{unique_id}_image{image_ext}"
        audio_filename = f"{unique_id}_audio{audio_ext}"
        
        # 保存文件到tmp目录
        image_path = tmp_dir / image_filename
        audio_path = tmp_dir / audio_filename
        
        image_file.save(str(image_path))
        audio_file.save(str(audio_path))
        
        print(f"保存图片文件: {image_path}")
        print(f"保存音频文件: {audio_path}")
        
        # 创建任务记录
        task = JimengDigitalHumanTask.create(
            image_path=str(image_path),
            audio_path=str(audio_path),
            status=0,  # 排队中
            create_at=datetime.now()
        )
        
        return jsonify({
            'success': True,
            'message': '数字人任务创建成功',
            'data': {
                'task_id': task.id
            }
        })
        
    except Exception as e:
        print(f"创建数字人任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建任务失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除数字人任务"""
    try:
        task = JimengDigitalHumanTask.get_by_id(task_id)
        
        # 删除文件
        try:
            if task.image_path and os.path.exists(task.image_path):
                os.remove(task.image_path)
            if task.audio_path and os.path.exists(task.audio_path):
                os.remove(task.audio_path)
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
        
        # 删除任务记录
        task.delete_instance()
        
        return jsonify({
            'success': True,
            'message': '任务删除成功'
        })
        
    except JimengDigitalHumanTask.DoesNotExist:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    except Exception as e:
        print(f"删除数字人任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'删除任务失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/<int:task_id>/retry', methods=['POST'])
def retry_task(task_id):
    """重试数字人任务"""
    try:
        task = JimengDigitalHumanTask.get_by_id(task_id)
        
        # 重置任务状态
        task.status = 0  # 排队中
        task.account_id = None
        task.start_time = None
        task.video_url = None
        task.save()
        
        return jsonify({
            'success': True,
            'message': '任务已重新排队'
        })
        
    except JimengDigitalHumanTask.DoesNotExist:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    except Exception as e:
        print(f"重试数字人任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'重试任务失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/batch-retry', methods=['POST'])
def batch_retry_tasks():
    """批量重试失败任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            # 重试所有失败的任务
            failed_tasks = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 3)
        else:
            # 重试指定的任务
            failed_tasks = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.id.in_(task_ids))
        
        retry_count = 0
        for task in failed_tasks:
            task.status = 0  # 排队中
            task.account_id = None
            task.start_time = None
            task.video_url = None
            task.save()
            retry_count += 1
        
        return jsonify({
            'success': True,
            'message': f'已重试 {retry_count} 个任务'
        })
        
    except Exception as e:
        print(f"批量重试数字人任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量重试失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/batch-delete', methods=['POST'])
def batch_delete_tasks():
    """批量删除任务"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请选择要删除的任务'
            }), 400
        
        # 获取要删除的任务
        tasks = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.id.in_(task_ids))
        
        delete_count = 0
        for task in tasks:
            # 删除文件
            try:
                if task.image_path and os.path.exists(task.image_path):
                    os.remove(task.image_path)
                if task.audio_path and os.path.exists(task.audio_path):
                    os.remove(task.audio_path)
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
            
            # 删除任务记录
            task.delete_instance()
            delete_count += 1
        
        return jsonify({
            'success': True,
            'message': f'已删除 {delete_count} 个任务'
        })
        
    except Exception as e:
        print(f"批量删除数字人任务失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量删除失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/batch-download', methods=['POST'])
def batch_download_videos():
    """批量下载数字人视频"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({
                'success': False,
                'message': '请选择要下载的任务'
            }), 400
        
        print(f"数字人批量下载任务，任务ID: {task_ids}")
        
        def select_folder_and_download():
            try:
                # 调用原生文件夹选择对话框
                folder_path = None
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    result = subprocess.run([
                        'osascript', '-e',
                        'tell application "Finder" to set folder_path to (choose folder with prompt "选择视频保存文件夹") as string',
                        '-e',
                        'return POSIX path of folder_path'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                        
                elif system == "Windows":  # Windows
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Add-Type -AssemblyName System.Windows.Forms; $folder = New-Object System.Windows.Forms.FolderBrowserDialog; $folder.Description = "选择视频保存文件夹"; $folder.ShowNewFolderButton = $true; if ($folder.ShowDialog() -eq "OK") { $folder.SelectedPath } else { "" }'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                        
                elif system == "Linux":  # Linux
                    result = subprocess.run([
                        'zenity', '--file-selection', '--directory',
                        '--title=选择视频保存文件夹'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        folder_path = result.stdout.strip()
                
                if not folder_path:
                    print("用户取消了文件夹选择")
                    return
                
                print(f"选择的保存文件夹: {folder_path}")
                
                if not os.path.exists(folder_path):
                    print(f"文件夹不存在: {folder_path}")
                    return
                
                # 获取要下载的任务
                tasks = JimengDigitalHumanTask.select().where(
                    JimengDigitalHumanTask.id.in_(task_ids),
                    JimengDigitalHumanTask.status == 2,  # 已完成
                    JimengDigitalHumanTask.video_url.is_null(False)  # 有视频URL
                )
                
                download_count = 0
                import requests
                import shutil
                
                for task in tasks:
                    try:
                        if task.video_url:
                            # 构造文件名
                            filename = f"digital_human_task_{task.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                            file_path = os.path.join(folder_path, filename)
                            
                            # 下载视频
                            response = requests.get(task.video_url, stream=True, timeout=30)
                            if response.status_code == 200:
                                with open(file_path, 'wb') as f:
                                    shutil.copyfileobj(response.raw, f)
                                print(f"已下载: {filename}")
                                download_count += 1
                            else:
                                print(f"下载失败，任务ID {task.id}: HTTP {response.status_code}")
                                
                    except Exception as e:
                        print(f"下载任务 {task.id} 失败: {str(e)}")
                
                print(f"批量下载完成，成功下载 {download_count} 个视频")
                
            except Exception as e:
                print(f"批量下载处理失败: {str(e)}")
        
        # 在后台线程中执行文件选择和下载
        thread = threading.Thread(target=select_folder_and_download)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '开始选择保存文件夹并下载，请在弹出的对话框中选择保存位置'
        })
        
    except Exception as e:
        print(f"批量下载数字人视频失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量下载失败: {str(e)}'
        }), 500

@jimeng_digital_human_bp.route('/tasks/delete-before-today', methods=['DELETE'])
def delete_tasks_before_today():
    """删除今日前的所有数字人任务"""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # 获取今日开始时间（凌晨0点）
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today_start = datetime.now(beijing_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询今日前的任务
        before_today_tasks = JimengDigitalHumanTask.select().where(
            JimengDigitalHumanTask.create_at < today_start
        )
        
        count = before_today_tasks.count()
        
        if count == 0:
            return jsonify({
                'success': True,
                'message': '没有今日前的任务需要删除',
                'data': {'deleted_count': 0}
            })
        
        # 删除任务
        deleted_count = JimengDigitalHumanTask.delete().where(
            JimengDigitalHumanTask.create_at < today_start
        ).execute()
        
        print(f"删除了 {deleted_count} 个今日前的数字人任务")
        
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

@jimeng_digital_human_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取数字人任务统计"""
    try:
        today = date.today()
        
        # 获取统计数据
        total = JimengDigitalHumanTask.select().count()
        today_count = JimengDigitalHumanTask.select().where(
            JimengDigitalHumanTask.create_at >= today
        ).count()
        in_progress = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 1).count()
        completed = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 2).count()
        failed = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 3).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'today': today_count,
                'in_progress': in_progress,
                'completed': completed,
                'failed': failed
            }
        })
        
    except Exception as e:
        print(f"获取数字人任务统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500 