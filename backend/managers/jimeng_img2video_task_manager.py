# -*- coding: utf-8 -*-
"""
即梦图生视频任务管理器
"""

import asyncio
import threading
import time
import random
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
from backend.models.models import JimengImg2VideoTask, JimengAccount
from backend.utils.jimeng_image2video import image2video
from colorama import Fore, Style
# 移除这里的导入，避免循环依赖
# from backend.core.global_task_manager import global_task_manager

class JimengImg2VideoTaskManager:
    def __init__(self, max_workers=3):
        """初始化图生视频任务管理器"""
        self.max_workers = max_workers
        self.running = False
        self.scan_thread = None
        self.scan_interval = 5  # 扫描间隔（秒）
        self.global_executor = None
        self._lock = threading.Lock()  # 添加锁对象用于线程安全
        self.processing_tasks = {}  # 记录处理中的任务
        self.active_futures = {}  # 记录活跃的Future对象
        self.stats = {
            'total': 0,
            'pending': 0,
            'processing': 0,
            'successful': 0,
            'failed': 0,
            'error_count': 0
        }
        
        print(f"即梦图生视频任务管理器初始化，最大线程数: {max_workers}")
    
    def set_global_executor(self, global_task_manager):
        """设置全局线程池"""
        self.global_executor = global_task_manager
        print(f"即梦图生视频任务管理器已设置全局线程池")
    
    def start(self):
        """启动任务管理器"""
        if self.running:
            return True
        
        # 检查是否设置了全局线程池
        if not self.global_executor:
            print(f"即梦图生视频任务管理器启动失败：未设置全局线程池")
            return False
        
        # 启动扫描线程
        self.running = True
        print("开始扫描即梦图生视频任务...")
        self.scan_thread = threading.Thread(target=self._scan_and_process_tasks)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        print(f"即梦图生视频任务扫描线程已启动")
        print(f"即梦图生视频任务管理器启动成功")
        return True
    
    def stop(self):
        """停止任务管理器"""
        if not self.running:
            return True
        
        # 停止扫描线程
        self.running = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=5)
        
        # 重置状态
        self.scan_thread = None
        
        print(f"即梦图生视频任务管理器已停止")
        return True
    
    def get_status(self):
        """获取任务管理器状态"""
        status = {
            'status': 'running' if self.running else 'stopped',
            'active_threads': self.global_executor.get_active_thread_count() if self.global_executor else 0,
            'max_threads': self.max_workers
        }
        return status
    
    def get_summary(self):
        """获取任务统计信息"""
        # 统计时过滤掉空任务
        base_query = JimengImg2VideoTask.select().where(JimengImg2VideoTask.is_empty_task == False)
        total_tasks = base_query.count()
        queued_tasks = base_query.where(JimengImg2VideoTask.status == 0).count()  # 排队中
        processing_tasks = base_query.where(JimengImg2VideoTask.status == 1).count()  # 生成中
        completed_tasks = base_query.where(JimengImg2VideoTask.status == 2).count()  # 已完成
        failed_tasks = base_query.where(JimengImg2VideoTask.status == 3).count()  # 失败
        
        return {
            'total': total_tasks,
            'queued': queued_tasks,
            'processing': processing_tasks,
            'completed': completed_tasks,
            'failed': failed_tasks
        }
    
    def get_thread_details(self):
        """获取线程详细信息"""
        if not self.global_executor:
            return []
        
        # 从全局任务管理器获取线程信息
        return self.global_executor.get_thread_details()
    
    def _scan_and_process_tasks(self):
        """扫描并处理任务的线程函数"""
        while self.running:
            try:
                # 获取排队中的任务
                pending_tasks = list(JimengImg2VideoTask.select().where(
                    JimengImg2VideoTask.status == 0  # 排队中
                ).order_by(JimengImg2VideoTask.create_at))
                
                # 处理任务
                for task in pending_tasks:
                    if not self.running:
                        break
                    
                    # 提交任务到线程池
                    self._submit_task_to_pool(task)
                
                # 休眠一段时间再继续扫描
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"扫描图生视频任务时出错: {str(e)}")
                time.sleep(5)  # 出错后等待一段时间再继续
    
    def _submit_task_to_pool(self, task):
        """提交任务到全局线程池"""
        try:
            if not self.global_executor:
                print(f"无法提交任务：全局线程池未设置")
                return
                
            # 更新任务状态为处理中
            task.status = 1  # 生成中
            task.save()
            
            print(f"准备提交图生视频任务到全局线程池: {task.id}")
            
            # 通过全局任务管理器提交任务，以便正确跟踪线程状态
            from backend.core.global_task_manager import global_task_manager
            future = global_task_manager.submit_task(
                "即梦图生视频",
                self._process_task,
                task,
                task_id=task.id,
                task_type="图生视频",
                prompt=task.prompt
            )
            
            # 记录处理信息
            with self._lock:
                self.processing_tasks[task.id] = {
                    'future': future,
                    'start_time': datetime.now(),
                    'status': 'starting',
                    'task': task
                }
                self.active_futures[task.id] = future
            
            # 添加完成回调
            future.add_done_callback(lambda f: self._on_task_completed(task.id, f))
            
            print(f"图生视频任务提交成功: {task.id}, Future: {future}")
            return True
        except Exception as e:
            # 恢复任务状态
            task.status = 0  # 排队中
            task.save()
            print(f"提交图生视频任务失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _on_task_completed(self, task_id, future):
        """任务完成回调"""
        try:
            # 清理任务记录
            with self._lock:
                if task_id in self.processing_tasks:
                    del self.processing_tasks[task_id]
                if task_id in self.active_futures:
                    del self.active_futures[task_id]
                    
            print(f"即梦图生视频任务执行完成，任务ID: {task_id}")
            
        except Exception as e:
            print(f"处理任务完成回调时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _process_task(self, task):
        """处理单个任务"""
        try:
            # 更新处理状态
            with self._lock:
                if task.id in self.processing_tasks:
                    self.processing_tasks[task.id]['status'] = 'processing'
            
            print(f"开始处理即梦图生视频任务，ID: {task.id}")
            
            # 更新任务状态为处理中
            task.status = 1
            task.update_at = datetime.now()
            task.save()
            
            # 执行具体的任务处理逻辑
            result = self._execute_img2video_task(task)
            
            if result['success']:
                # 任务成功
                if 'video_url' in result and result['video_url']:
                    task.video_url = result['video_url']
                
                if 'account_id' in result:
                    task.account_id = result['account_id']
                
                task.status = 2  # 已完成
                task.update_at = datetime.now()
                task.save()
                
                print(f"即梦图生视频任务完成，ID: {task.id}")
                with self._lock:
                    self.stats['successful'] += 1
            else:
                # 任务失败，根据错误类型决定是否创建空任务记录账号使用情况
                if 'account_id' in result and result.get('should_create_empty_task', False):
                    print(f"创建空任务记录账号 {result['account_id']} 的使用情况")
                    self._create_empty_task_record(result['account_id'])
                    
                task.status = 3  # 失败
                task.update_at = datetime.now()
                task.save()
                
                print(f"即梦图生视频任务失败，ID: {task.id}，原因: {result.get('error', '未知错误')}")
                with self._lock:
                    self.stats['failed'] += 1
            
            return result
            
        except Exception as e:
            # 任务异常
            task.status = 3  # 失败
            task.update_at = datetime.now()
            task.save()
            
            print(f"处理即梦图生视频任务异常，ID: {task.id}，错误: {str(e)}")
            with self._lock:
                self.stats['failed'] += 1
                self.stats['error_count'] += 1
            
            return {'success': False, 'error': f'任务异常: {str(e)}', 'task_id': task.id}
    
    def _execute_img2video_task(self, task):
        """
        执行即梦图生视频任务的具体逻辑
        
        参数:
            task: JimengImg2VideoTask 对象
        
        返回值:
            Dict: 执行结果
        """
        try:
            # 获取可用账号
            account = self._get_available_account("图生视频")
            if not account:
                # 没有可用账号，任务失败
                return {'success': False, 'message': '没有可用账号', 'task_id': task.id}
            
            # 获取浏览器隐藏配置
            from backend.utils.config_util import get_hide_window
            headless = get_hide_window()
            
            # 调用图生视频函数
            import asyncio
            result = asyncio.run(image2video(
                image_path=task.image_path,
                prompt=task.prompt,
                username=account.account,
                password=account.password,
                model=task.model,
                second=task.second,
                headless=headless,
                cookies=account.cookies
            ))
            
            # 更新账号使用记录
            self._update_account_usage(account.id, "图生视频")
            
            # 处理结果
            if result['code'] == 200:
                # 任务成功
                return {
                    'success': True,
                    'video_url': result['data'],
                    'account_id': account.id,
                    'task_id': task.id
                }
            elif result['code'] in [603, 604]:
                # 任务ID等待超时或视频URL等待超时，需要创建空任务记录账号使用情况
                print(f"错误码 {result['code']}，创建空任务记录账号使用情况")
                return {
                    'success': False,
                    'error': result['message'],
                    'account_id': account.id,
                    'task_id': task.id,
                    'should_create_empty_task': True
                }
            else:
                # 其他错误情况下，如果是异常，也创建空任务
                should_create_empty_task = result['code'] == 500
                if should_create_empty_task:
                    print(f"异常情况，创建空任务记录账号使用情况")
                
                return {
                    'success': False,
                    'error': result['message'],
                    'account_id': account.id,
                    'task_id': task.id,
                    'should_create_empty_task': should_create_empty_task
                }
        except Exception as e:
            print(f"执行图生视频任务异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'任务执行异常: {str(e)}'
            }
    
    def _get_available_account(self, task_type="图生视频"):
        """获取可用账号"""
        try:
            # 获取所有账号
            accounts = list(JimengAccount.select())
            if not accounts:
                print("没有配置的即梦账号")
                return None
            
            # 获取今天的日期
            today = date.today()
            
            # 获取每个账号的今日使用情况
            account_usage = []
            daily_limit = 2  # 图生视频每天2次
            
            for account in accounts:
                # 统计今日使用次数 - 包括空任务
                today_usage = JimengImg2VideoTask.select().where(
                    (JimengImg2VideoTask.account_id == account.id) &
                    (JimengImg2VideoTask.create_at >= today)
                ).count()
                
                # 如果未达到使用上限，加入可用账号列表
                if today_usage < daily_limit:
                    account_usage.append({
                        'account': account,
                        'usage': today_usage
                    })
            
            # 随机选择一个使用次数最少的账号
            if account_usage:
                min_usage = min(item['usage'] for item in account_usage)
                min_usage_accounts = [item for item in account_usage if item['usage'] == min_usage]
                selected_item = random.choice(min_usage_accounts)
                selected_account = selected_item['account']
                
                return selected_account
            else:
                print(f"所有账号今日{task_type}使用次数已达上限")
                return None
        except Exception as e:
            print(f"获取可用账号失败: {str(e)}")
            return None
    
    def _create_empty_task_record(self, account_id):
        """创建空任务记录账号使用情况"""
        try:
            empty_task = JimengImg2VideoTask.create(
                prompt="[空任务-记录账号使用]",
                model="Video 3.0",
                second=5,
                image_path="",
                status=2,  # 已完成
                account_id=account_id,
                is_empty_task=True  # 标记为空任务
            )
            return empty_task
        except Exception as e:
            print(f"创建空任务记录失败: {str(e)}")
            return None
    
    def _update_account_usage(self, account_id, task_type="图生视频"):
        """更新账号使用记录"""
        try:
            print(f"更新账号 {account_id} 的 {task_type} 使用记录")
            # 这里可以添加更新账号使用记录的逻辑
            pass
        except Exception as e:
            print(f"更新账号使用记录失败: {str(e)}")
            pass 