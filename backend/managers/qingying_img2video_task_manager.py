# -*- coding: utf-8 -*-
"""
清影图生视频任务管理器
"""

import asyncio
import time
import threading
from datetime import datetime
from backend.utils.config_util import get_hide_window
from backend.models.models import QingyingImage2VideoTask, QingyingAccount
from backend.utils.qingying_image2video import QingyingImage2VideoExecutor

def run_async_safe(coro):
    """安全地运行异步协程，处理事件循环冲突"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，在新线程中创建新的事件循环
            import threading
            result = None
            exception = None
            
            def run_in_thread():
                nonlocal result, exception
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result = new_loop.run_until_complete(coro)
                    new_loop.close()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            return result
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # 如果没有事件循环，直接使用 asyncio.run
        return asyncio.run(coro)

class QingyingImg2VideoTaskManager:
    """清影图生视频任务管理器"""
    
    def __init__(self):
        self.running = False
        self.worker_thread = None
        self.global_executor = None
        self.task_queue = []
        self.processing_tasks = set()
        # 账号并发控制：账号ID -> 当前处理任务数
        self.account_task_count = {}
        
    def start(self):
        """启动任务管理器"""
        if self.running:
            print("清影图生视频任务管理器已在运行中")
            return False
            
        self.running = True
        # 启动时重置账号计数器，确保计数正确
        self.reset_account_counters()
        self.worker_thread = threading.Thread(target=self._task_processor_loop, daemon=True)
        self.worker_thread.start()
        print("清影图生视频任务管理器已启动")
        return True
    
    def stop(self):
        """停止任务管理器"""
        if not self.running:
            print("清影图生视频任务管理器已停止")
            return False
            
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join()
        print("清影图生视频任务管理器已停止")
        return True
    
    def set_global_executor(self, executor):
        """设置全局线程池执行器"""
        self.global_executor = executor
    
    def submit_task(self, task_id):
        """提交任务到队列"""
        if task_id not in self.task_queue and task_id not in self.processing_tasks:
            self.task_queue.append(task_id)
            print(f"清影图生视频任务 {task_id} 已加入队列")
    
    def _task_processor_loop(self):
        """任务处理循环"""
        # 初始延迟，等待数据库和其他组件初始化完成
        time.sleep(5.0)
        
        while self.running:
            try:
                # 扫描待处理任务
                self._scan_pending_tasks()
                
                # 处理队列中的任务
                if self.task_queue and self.global_executor:
                    task_id = self.task_queue.pop(0)
                    if task_id not in self.processing_tasks:
                        self.processing_tasks.add(task_id)
                        # 使用全局线程池处理任务
                        future = self.global_executor.submit(self._process_task, task_id)
                        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))
                
                time.sleep(2)  # 每2秒检查一次
                
            except Exception as e:
                print(f"清影图生视频任务处理循环出错: {str(e)}")
                time.sleep(5)
    
    def _scan_pending_tasks(self):
        """扫描数据库中的待处理任务"""
        try:
            # 查找状态为0（排队中）的任务
            pending_tasks = QingyingImage2VideoTask.select().where(
                QingyingImage2VideoTask.status == 0
            )
            
            for task in pending_tasks:
                if task.id not in self.task_queue and task.id not in self.processing_tasks:
                    self.task_queue.append(task.id)
                    
        except Exception as e:
            print(f"扫描清影图生视频待处理任务失败: {str(e)}")
    
    def _process_task(self, task_id):
        """处理单个任务"""
        account_id = None
        try:
            # 获取任务信息
            task = QingyingImage2VideoTask.get_by_id(task_id)
            
            print(f"开始处理清影图生视频任务: {task_id}")
            
            # 更新任务状态为处理中
            task.status = 1
            task.update_at = datetime.now()
            task.save()
            
            # 获取可用的清影账号
            account = self._get_available_account()
            if not account:
                print(f"清影图生视频任务 {task_id}: 没有可用的账号")
                task.status = 0  # 排队中
                task.update_at = datetime.now()
                task.save()
                return
            
            # 记录使用的账号ID，用于后续清理
            account_id = account.id
            
            # 关联账号
            task.account_id = account.id
            task.save()
            
            print(f"清影图生视频任务 {task_id}: 使用账号 {account.nickname}")
            headless = get_hide_window()
            
            try:
                # 创建清影图生视频执行器
                executor = QingyingImage2VideoExecutor(headless=headless)
                
                # 执行任务
                result = run_async_safe(executor.execute(
                    image_path=task.image_path,
                    prompt=task.prompt,
                    cookies=account.cookies,
                    generation_mode=task.generation_mode,
                    frame_rate=task.frame_rate,
                    resolution=task.resolution,
                    duration=task.duration,
                    ai_audio=task.ai_audio
                ))
                
                # 处理结果
                if result.code == 200:
                    # 成功
                    data = result.data or {}
                    task.video_url = data.get('video_url', '')
                    task.status = 2  # 已完成
                    print(f"清影图生视频任务 {task_id}: 生成成功")
                    print(f"视频URL: {task.video_url}")
                else:
                    # 失败 - 检查是否需要重试
                    error_code = result.code
                    error_message = result.message
                    
                    if error_code in [600, 900]:
                        # 设置失败状态和原因
                        task.set_failure(error_code, error_message)
                        
                        # 检查是否可以重试
                        if task.can_retry():
                            # 重试任务，重新进入排队状态
                            if task.retry_task():
                                print(f"清影图生视频任务 {task_id}: 重试，重试次数: {task.retry_count}/{task.max_retry}")
                                # 任务重新排队，不需要更新状态
                            else:
                                print(f"清影图生视频任务 {task_id}: 重试失败，已达最大重试次数")
                                # task.retry_task()已经设置了失败状态
                        else:
                            print(f"清影图生视频任务 {task_id}: 不可重试 - {error_message}")
                            # task.set_failure()已经设置了失败状态
                    else:
                        # 非600/900错误，直接设置失败
                        task.status = 3  # 失败
                        task.update_at = datetime.now()
                        task.save()
                        print(f"清影图生视频任务 {task_id}: 生成失败 - {error_message}")
                
                # 只有非重试情况才需要手动更新时间
                if task.status != 0:  # 如果不是重新排队状态
                    task.update_at = datetime.now()
                    task.save()
                
            except Exception as process_error:
                print(f"清影图生视频任务 {task_id} 处理过程出错: {str(process_error)}")
                # 异常情况通常是网络或系统错误，可以考虑重试
                task.set_failure(900, f'处理异常: {str(process_error)}')
                
                # 检查是否可以重试
                if task.can_retry():
                    # 重试任务，重新进入排队状态
                    if task.retry_task():
                        print(f"清影图生视频任务 {task_id}: 异常后重试，重试次数: {task.retry_count}/{task.max_retry}")
                    else:
                        print(f"清影图生视频任务 {task_id}: 异常后重试失败，已达最大重试次数")
                else:
                    print(f"清影图生视频任务 {task_id}: 异常后不可重试")
                
                raise  # 重新抛出异常，确保外层的finally块能执行
            
        except QingyingImage2VideoTask.DoesNotExist:
            print(f"清影图生视频任务 {task_id} 不存在")
        except Exception as e:
            print(f"处理清影图生视频任务 {task_id} 时出错: {str(e)}")
            try:
                task = QingyingImage2VideoTask.get_by_id(task_id)
                task.status = 3  # 失败
                task.update_at = datetime.now()
                task.save()
            except:
                pass
        finally:
            # 确保无论任务成功还是失败，都减少账号任务计数
            if account_id:
                current_count = self.account_task_count.get(account_id, 0)
                if current_count > 0:
                    self.account_task_count[account_id] = current_count - 1
                    print(f"任务 {task_id} 完成，减少账号 {account_id} 任务计数，当前: {self.account_task_count[account_id]}")
                else:
                    print(f"警告: 账号 {account_id} 任务计数已为0，无法减少")
    
    def _get_available_account(self):
        """获取可用的清影账号（支持并发，每个账号最多同时处理4个任务）"""
        try:
            # 查找有cookies的清影账号
            accounts = QingyingAccount.select().where(
                QingyingAccount.cookies.is_null(False),
                QingyingAccount.cookies != ''
            )
            
            if accounts.count() > 0:
                # 查找并发数未满的账号
                available_accounts = []
                for account in accounts:
                    current_count = self.account_task_count.get(account.id, 0)
                    if current_count < 4:  # 每个账号最多同时处理4个任务
                        available_accounts.append(account)
                
                if available_accounts:
                    # 选择并发数最少的账号
                    selected_account = min(available_accounts, 
                                         key=lambda acc: self.account_task_count.get(acc.id, 0))
                    
                    # 增加该账号的任务计数
                    self.account_task_count[selected_account.id] = self.account_task_count.get(selected_account.id, 0) + 1
                    
                    print(f"选择账号 {selected_account.nickname}，当前并发数: {self.account_task_count[selected_account.id]}")
                    return selected_account
                else:
                    print("所有清影账号都已达到最大并发数（4个任务）")
            
            return None
            
        except Exception as e:
            print(f"获取可用清影账号失败: {str(e)}")
            return None
    
    def _on_task_complete(self, task_id, future):
        """任务完成回调"""
        self.processing_tasks.discard(task_id)
        
        # 注意：账号任务计数的减少已经在_process_task的finally块中处理了
        # 这里不再重复减少，避免计数错误
        
        if future.exception():
            print(f"清影图生视频任务 {task_id} 执行出错: {future.exception()}")
            try:
                task = QingyingImage2VideoTask.get_by_id(task_id)
                task.status = 3  # 失败
                task.update_at = datetime.now()
                task.save()
            except:
                pass
        else:
            print(f"清影图生视频任务 {task_id} 处理完成")
    
    def reset_account_counters(self):
        """重置账号任务计数器（用于修复计数不一致问题）"""
        try:
            print("重置清影账号任务计数器...")
            
            # 清空当前计数
            self.account_task_count.clear()
            
            # 根据数据库中正在处理的任务重新计算
            processing_tasks = QingyingImage2VideoTask.select().where(
                QingyingImage2VideoTask.status == 1,  # 处理中的任务
                QingyingImage2VideoTask.account_id.is_null(False)
            )
            
            for task in processing_tasks:
                if task.account_id:
                    self.account_task_count[task.account_id] = self.account_task_count.get(task.account_id, 0) + 1
            
            print(f"重置完成，当前账号任务计数: {self.account_task_count}")
            
        except Exception as e:
            print(f"重置账号任务计数器失败: {str(e)}")
    
    def get_status(self):
        """获取管理器状态"""
        return {
            'running': self.running,
            'queue_size': len(self.task_queue),
            'processing_count': len(self.processing_tasks),
            'total_pending': len(self.task_queue) + len(self.processing_tasks),
            'account_task_count': dict(self.account_task_count)
        } 