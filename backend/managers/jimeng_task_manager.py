# -*- coding: utf-8 -*-
"""
即梦平台任务管理器 - 汇总即梦平台任务状态并执行任务
"""

import threading
import time
import asyncio
from datetime import datetime
from typing import Dict, List
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.models.models import JimengText2ImgTask, JimengAccount
from backend.utils.jimeng_text2img import text2image
from backend.utils.config_util import get_automation_max_threads, get_hide_window
from backend.config.settings import TASK_PROCESSOR_INTERVAL, TASK_PROCESSOR_ERROR_WAIT

class JimengTaskManagerStatus(Enum):
    """即梦任务管理器状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class JimengTaskManager:
    """即梦平台任务管理器"""
    
    def __init__(self):
        self.platform_name = "即梦国际版"
        self.status = JimengTaskManagerStatus.STOPPED
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.processing_tasks = {}  # 正在处理的任务ID -> 任务信息
        self.stats = {
            'start_time': None,
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'last_scan_time': None,
            'error_count': 0
        }
        self._lock = threading.Lock()
        self.thread_pool = None  # 线程池
        self.active_futures = {}  # 活跃的Future对象
    
    def start(self) -> bool:
        """启动即梦任务管理器"""
        if self.status == JimengTaskManagerStatus.RUNNING:
            print(f"{self.platform_name}任务管理器已经在运行中")
            return False
            
        print(f"🚀 启动{self.platform_name}任务管理器...")
        self.stop_event.clear()
        self.status = JimengTaskManagerStatus.RUNNING
        self.stats['start_time'] = datetime.now()
        
        # 获取配置的线程数并创建线程池
        max_threads = get_automation_max_threads()
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix="JimengWorker")
        print(f"📊 创建线程池，最大线程数: {max_threads}")
        
        # 启动扫描工作线程
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        print(f"✅ {self.platform_name}任务管理器启动成功")
        return True
    
    def stop(self) -> bool:
        """停止即梦任务管理器"""
        if self.status == JimengTaskManagerStatus.STOPPED:
            print(f"{self.platform_name}任务管理器已经停止")
            return False
            
        print(f"🛑 正在停止{self.platform_name}任务管理器...")
        self.status = JimengTaskManagerStatus.STOPPED
        self.stop_event.set()
        
        # 关闭线程池
        if self.thread_pool:
            print("🔄 正在关闭线程池...")
            self.thread_pool.shutdown(wait=True)
            self.thread_pool = None
            
        # 清空活跃任务
        with self._lock:
            self.active_futures.clear()
            self.processing_tasks.clear()
        
        # 等待扫描工作线程结束
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=10)
            
        print(f"✅ {self.platform_name}任务管理器已停止")
        return True
    
    def pause(self) -> bool:
        """暂停即梦任务管理器"""
        if self.status == JimengTaskManagerStatus.RUNNING:
            self.status = JimengTaskManagerStatus.PAUSED
            print(f"⏸️ {self.platform_name}任务管理器已暂停")
            return True
        return False
    
    def resume(self) -> bool:
        """恢复即梦任务管理器"""
        if self.status == JimengTaskManagerStatus.PAUSED:
            self.status = JimengTaskManagerStatus.RUNNING
            print(f"▶️ {self.platform_name}任务管理器已恢复")
            return True
        return False
    
    def get_summary(self) -> Dict:
        """获取即梦平台任务汇总"""
        try:
            pending_count = JimengText2ImgTask.select().where(
                JimengText2ImgTask.status == 0  # 排队中
            ).count()
            
            processing_count = JimengText2ImgTask.select().where(
                JimengText2ImgTask.status == 1  # 生成中
            ).count()
            
            completed_count = JimengText2ImgTask.select().where(
                JimengText2ImgTask.status == 2  # 已完成
            ).count()
            
            failed_count = JimengText2ImgTask.select().where(
                JimengText2ImgTask.status == 3  # 失败
            ).count()
            
            return {
                'platform': self.platform_name,
                'pending': pending_count,
                'processing': processing_count,
                'completed': completed_count,
                'failed': failed_count,
                'total': pending_count + processing_count + completed_count + failed_count
            }
        except Exception as e:
            print(f"获取{self.platform_name}汇总失败: {str(e)}")
            return {
                'platform': self.platform_name,
                'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'total': 0
            }
    
    def get_status(self) -> Dict:
        """获取即梦任务管理器状态"""
        with self._lock:
            max_threads = get_automation_max_threads()
            active_threads = len([f for f in self.active_futures.values() if not f.done()])
            
            return {
                'platform': self.platform_name,
                'status': self.status.value,
                'processing_count': len(self.processing_tasks),
                'processing_tasks': list(self.processing_tasks.keys()),
                'stats': self.stats.copy(),
                'uptime': (datetime.now() - self.stats['start_time']).total_seconds() 
                         if self.stats['start_time'] else 0,
                'max_threads': max_threads,
                'active_threads': active_threads,
                'thread_pool_alive': self.thread_pool is not None and not self.thread_pool._shutdown
            }
    
    def get_detailed_tasks(self, status: int = None, page: int = 1, page_size: int = 10) -> Dict:
        """获取详细任务列表"""
        try:
            query = JimengText2ImgTask.select()
            if status is not None:
                query = query.where(JimengText2ImgTask.status == status)
            
            total = query.count()
            tasks = query.order_by(JimengText2ImgTask.create_at.desc()).paginate(page, page_size)
            
            task_list = []
            for task in tasks:
                images = task.get_images()
                task_list.append({
                    'id': task.id,
                    'prompt': task.prompt,
                    'model': task.model,
                    'ratio': task.ratio,
                    'quality': task.quality,
                    'status': task.status,
                    'status_text': task.get_status_text(),
                    'account_id': task.account_id,
                    'images': images,
                    'image_count': len(images),
                    'create_at': task.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_at': task.update_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return {
                'platform': self.platform_name,
                'tasks': task_list,
                'pagination': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        except Exception as e:
            print(f"获取{self.platform_name}详细任务失败: {str(e)}")
            return {'platform': self.platform_name, 'tasks': [], 'pagination': {}}
    
    def _worker_loop(self):
        """工作线程主循环"""
        print(f"📋 {self.platform_name}任务扫描线程已启动")
        
        while not self.stop_event.is_set():
            try:
                # 更新扫描时间
                self.stats['last_scan_time'] = datetime.now()
                
                # 如果是暂停状态，跳过扫描
                if self.status == JimengTaskManagerStatus.PAUSED:
                    time.sleep(TASK_PROCESSOR_INTERVAL)
                    continue
                
                # 扫描待处理任务
                self._scan_and_process_tasks()
                
                # 清理已完成的任务记录
                self._cleanup_finished_tasks()
                
                # 等待下次扫描
                time.sleep(TASK_PROCESSOR_INTERVAL)
                
            except Exception as e:
                print(f"❌ {self.platform_name}任务扫描异常: {str(e)}")
                self.stats['error_count'] += 1
                self.status = JimengTaskManagerStatus.ERROR
                time.sleep(TASK_PROCESSOR_ERROR_WAIT)
                self.status = JimengTaskManagerStatus.RUNNING  # 自动恢复
        
        print(f"📋 {self.platform_name}任务扫描线程已结束")
    
    def _scan_and_process_tasks(self):
        """扫描并处理待处理任务"""
        try:
            if not self.thread_pool or self.thread_pool._shutdown:
                return
                
            # 获取配置的最大线程数
            max_threads = get_automation_max_threads()
            
            # 获取当前活跃的任务数量
            with self._lock:
                active_count = len([f for f in self.active_futures.values() if not f.done()])
            
            if active_count >= max_threads:
                return
            
            # 计算可以启动的新任务数量
            available_slots = max_threads - active_count
            
            # 查找排队中的任务
            pending_tasks = JimengText2ImgTask.select().where(
                JimengText2ImgTask.status == 0
            ).order_by(JimengText2ImgTask.create_at).limit(available_slots)
            
            for task in pending_tasks:
                # 检查是否已经在处理中
                if task.id in self.processing_tasks:
                    continue
                
                # 提交任务到线程池
                self._submit_task_to_pool(task)
                
        except Exception as e:
            print(f"{self.platform_name}扫描任务失败: {str(e)}")
    
    def _submit_task_to_pool(self, task):
        """提交任务到线程池"""
        try:
            # 提交任务到线程池
            future = self.thread_pool.submit(self._process_single_task, task)
            
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
            
            print(f"🎯 提交{self.platform_name}任务到线程池，任务ID: {task.id}")
            
        except Exception as e:
            print(f"提交{self.platform_name}任务到线程池失败，错误: {str(e)}")
    
    def _on_task_completed(self, task_id, future):
        """任务完成回调"""
        try:
            with self._lock:
                if task_id in self.processing_tasks:
                    self.processing_tasks[task_id]['status'] = 'finished'
                    self.processing_tasks[task_id]['end_time'] = datetime.now()
                    
                # 从活跃futures中移除
                if task_id in self.active_futures:
                    del self.active_futures[task_id]
                    
            print(f"📋 {self.platform_name}任务执行完成，任务ID: {task_id}")
            
        except Exception as e:
            print(f"处理{self.platform_name}任务完成回调失败: {str(e)}")
    
    def _process_single_task(self, task):
        """处理单个任务"""
        try:
            # 更新处理状态
            with self._lock:
                if task.id in self.processing_tasks:
                    self.processing_tasks[task.id]['status'] = 'processing'
            
            print(f"🔄 开始处理{self.platform_name}任务，ID: {task.id}")
            
            # 更新任务状态为处理中
            task.status = 1
            task.update_at = datetime.now()
            task.save()
            
            # 执行具体的任务处理逻辑 - 这里需要用户自己实现
            result = self._execute_text2img_task(task)
            
            if result['success']:
                # 任务成功
                if 'images' in result and result['images']:
                    task.set_images(result['images'])
                
                if 'account_id' in result:
                    task.account_id = result['account_id']
                
                task.status = 2  # 已完成
                task.update_at = datetime.now()
                task.save()
                
                print(f"✅ {self.platform_name}任务完成，ID: {task.id}")
                with self._lock:
                    self.stats['successful'] += 1
            else:
                # 任务失败
                task.status = 3  # 失败
                task.update_at = datetime.now()
                task.save()
                
                print(f"❌ {self.platform_name}任务失败，ID: {task.id}，原因: {result.get('error', '未知错误')}")
                with self._lock:
                    self.stats['failed'] += 1
            
            with self._lock:
                self.stats['total_processed'] += 1
            
        except Exception as e:
            print(f"❌ 处理{self.platform_name}任务异常，ID: {task.id}，错误: {str(e)}")
            try:
                task.status = 3
                task.update_at = datetime.now()
                task.save()
                with self._lock:
                    self.stats['failed'] += 1
                    self.stats['total_processed'] += 1
            except:
                pass
    
    def _execute_text2img_task(self, task) -> Dict:
        """
        执行即梦文生图任务的具体逻辑
        
        参数:
            task: JimengText2ImgTask 对象
        
        返回值:
            Dict: 执行结果
        """
        
        print(f"🎯 开始执行文生图任务，任务ID: {task.id}")
        print(f"📝 任务参数: prompt='{task.prompt}', model='{task.model}', ratio='{task.ratio}', quality='{task.quality}'")
        
        client = None
        try:
            # 获取可用账号
            available_account = self._get_available_account()
            if not available_account:
                return {'success': False, 'error': '没有可用的即梦账号或账号使用次数已达上限'}
            
            print(f"📧 使用账号: {available_account.account}")
            
            # 获取浏览器隐藏配置
            headless = get_hide_window()
            
            # 直接调用生成图片函数
            image_urls = asyncio.run(text2image(
                prompt=task.prompt,
                username=available_account.account,
                password=available_account.password,
                model=task.model or "Image 3.1",
                aspect_ratio=task.ratio or "1:1",  # 使用ratio字段作为aspect_ratio
                quality=task.quality or "1K",
                headless=headless
            ))
            
            if image_urls and len(image_urls) > 0:
                # 更新账号使用次数
                self._update_account_usage(available_account.id, 'text2img')
                
                return {
                    'success': True, 
                    'images': image_urls,
                    'account_id': available_account.id
                }
            else:
                return {'success': False, 'error': '即梦平台图片生成失败'}
                
        except Exception as e:
            print(f"❌ 即梦任务执行异常: {str(e)}")
            return {'success': False, 'error': f'即梦任务执行异常: {str(e)}'}
        finally:
            # 确保浏览器关闭
            if client:
                try:
                    asyncio.run(client.close())
                except Exception as e:
                    print(f"⚠️ 关闭浏览器异常: {str(e)}")
                    pass
    
    def _get_available_account(self):
        """
        获取可用的即梦账号
        
        规则：
        - 一个账号每天可生成10次图片（40张图片）
        - 优先选择使用次数最少的账号
        """
        try:
            from datetime import date
            today = date.today()
            
            # 查询所有账号
            accounts = list(JimengAccount.select())
            if not accounts:
                print("❌ 没有配置的即梦账号")
                return None
            
            # 查找今日使用次数最少且未达上限的账号
            best_account = None
            min_usage = float('inf')
            
            for account in accounts:
                # 统计今日该账号的文生图任务使用次数
                today_usage = JimengText2ImgTask.select().where(
                    (JimengText2ImgTask.account_id == account.id) &
                    (JimengText2ImgTask.status.in_([1, 2])) &  # 处理中或已完成
                    (JimengText2ImgTask.create_at >= today)
                ).count()
                
                print(f"📊 账号 {account.account} 今日已使用: {today_usage}/10 次")
                
                # 检查是否还有可用次数
                if today_usage < 10 and today_usage < min_usage:
                    min_usage = today_usage
                    best_account = account
            
            if best_account:
                print(f"✅ 选择账号: {best_account.account} (今日已使用: {min_usage}/10)")
                return best_account
            else:
                print("❌ 所有账号今日使用次数已达上限")
                return None
                
        except Exception as e:
            print(f"❌ 获取可用账号失败: {str(e)}")
            return None
    
    def _update_account_usage(self, account_id: int, task_type: str):
        """
        更新账号使用记录
        
        参数:
            account_id: 账号ID
            task_type: 任务类型 ('text2img', 'img2video', 'digital_human')
        """
        try:
            print(f"📝 更新账号 {account_id} 的 {task_type} 使用记录")
            # 这里可以添加更详细的使用记录统计
            # 目前主要通过任务表来统计使用次数
        except Exception as e:
            print(f"❌ 更新账号使用记录失败: {str(e)}")
    
# 已删除_login_and_generate方法，现在直接使用text2image函数

    def _cleanup_finished_tasks(self):
        """清理已完成的任务记录"""
        with self._lock:
            # 清理已完成的处理任务记录
            finished_tasks = [
                task_id for task_id, info in self.processing_tasks.items()
                if info.get('status') == 'finished'
            ]
            
            for task_id in finished_tasks:
                del self.processing_tasks[task_id]
                
            # 清理已完成的futures
            finished_futures = [
                task_id for task_id, future in self.active_futures.items()
                if future.done()
            ]
            
            for task_id in finished_futures:
                if task_id in self.active_futures:
                    del self.active_futures[task_id]
    
    def get_thread_details(self) -> List[Dict]:
        """获取线程详细信息，用于前端显示"""
        max_threads = get_automation_max_threads()
        threads = []
        
        with self._lock:
            active_tasks = {
                task_id: info for task_id, info in self.processing_tasks.items()
                if info.get('status') == 'processing'
            }
            
            # 生成线程信息
            for i in range(1, max_threads + 1):
                thread_info = {
                    'id': i,
                    'status': 'inactive',
                    'task_id': None,
                    'platform': self.platform_name,
                    'task_type': None,
                    'prompt': None,
                    'progress': 0,
                    'start_time': None
                }
                
                # 如果有活跃任务，分配给线程
                if active_tasks:
                    task_id, task_info = active_tasks.popitem()
                    task = task_info.get('task')
                    
                    if task:
                        thread_info.update({
                            'status': 'active',
                            'task_id': task_id,
                            'task_type': '文生图',
                            'prompt': task.prompt,
                            'progress': self._calculate_task_progress(task_info),
                            'start_time': task_info.get('start_time')
                        })
                
                threads.append(thread_info)
                
            # 如果还有未分配的任务，标记额外线程为空闲
            idle_count = len([t for t in threads if t['status'] == 'inactive'])
            if idle_count > 0 and len(self.active_futures) < max_threads:
                # 将一些线程标记为空闲状态
                for thread in threads:
                    if thread['status'] == 'inactive' and idle_count > 0:
                        thread['status'] = 'idle'
                        idle_count -= 1
                        if idle_count <= 0:
                            break
        
        return threads
    
    def _calculate_task_progress(self, task_info) -> int:
        """计算任务进度"""
        if not task_info.get('start_time'):
            return 0
            
        # 基于运行时间估算进度
        elapsed = (datetime.now() - task_info['start_time']).total_seconds()
        # 假设平均任务需要10秒，计算百分比
        progress = min(int((elapsed / 10) * 100), 95)  # 最多95%，避免100%但未完成
        return progress 