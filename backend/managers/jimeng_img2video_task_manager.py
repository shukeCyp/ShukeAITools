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

class JimengImg2VideoTaskManager:
    def __init__(self, max_workers=3):
        """初始化图生视频任务管理器"""
        self.max_workers = max_workers
        self.running = False
        self.scan_thread = None
        self.scan_interval = 5  # 扫描间隔（秒）
        self.global_executor = None
        
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
                    try:
                        # 更新任务状态为处理中
                        task.status = 1  # 生成中
                        task.save()
                        
                        print(f"准备提交图生视频任务到全局线程池: {task.id}")
                        
                        # 提交任务到全局线程池
                        future = self.global_executor.submit_task(
                            platform_name="即梦图生视频",
                            task_callable=self._process_task,
                            task_id=task.id,
                            task_type="图生视频",
                            prompt=task.prompt,
                            task=task
                        )
                        
                        print(f"图生视频任务提交成功: {task.id}, Future: {future}")
                    except Exception as e:
                        # 恢复任务状态
                        task.status = 0  # 排队中
                        task.save()
                        print(f"提交图生视频任务失败: {str(e)}")
                
                # 休眠一段时间再继续扫描
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"扫描图生视频任务时出错: {str(e)}")
                time.sleep(5)  # 出错后等待一段时间再继续
    
    def _process_task(self, task):
        """处理单个任务"""
        try:
            # 确保任务状态为处理中
            if task.status != 1:
                task.status = 1  # 生成中
                task.save()
            
            # 获取可用账号
            account = self._get_available_account("图生视频")
            if not account:
                # 没有可用账号，任务失败
                task.status = 3  # 失败
                task.save()
                return {'success': False, 'message': '没有可用账号', 'task_id': task.id}
            
            # 调用图生视频函数
            from backend.utils.jimeng_image2video import image2video
            result = image2video(
                prompt=task.prompt,
                model=task.model,
                second=task.second,
                image_path=task.image_path,
                account=account.account,
                password=account.password,
                cookies=account.cookies
            )
            
            # 更新账号使用记录
            self._update_account_usage(account.id, "图生视频")
            
            # 处理结果
            if result['code'] == 200:
                # 任务成功
                task.status = 2  # 已完成
                task.video_url = result['data']
                task.account_id = account.id
                task.save()
                
                return {
                    'success': True,
                    'message': '任务完成',
                    'task_id': task.id,
                    'video_url': result['data']
                }
            elif result['code'] in [603, 604]:
                # 任务ID等待超时或视频URL等待超时，需要创建空任务记录账号使用情况
                print(f"错误码 {result['code']}，创建空任务记录账号使用情况")
                self._create_empty_task_record(account.id)
                
                # 任务失败
                task.status = 3  # 失败
                task.account_id = account.id
                task.save()
                
                return {
                    'success': False,
                    'message': result['message'],
                    'task_id': task.id
                }
            else:
                # 其他错误情况下，如果是异常，也创建空任务
                if result['code'] == 500:
                    print(f"异常情况，创建空任务记录账号使用情况")
                    self._create_empty_task_record(account.id)
                
                # 任务失败
                task.status = 3  # 失败
                task.account_id = account.id
                task.save()
                
                return {
                    'success': False,
                    'message': result['message'],
                    'task_id': task.id
                }
        except Exception as e:
            # 任务异常
            task.status = 3  # 失败
            task.save()
            
            return {
                'success': False,
                'message': f'任务异常: {str(e)}',
                'task_id': task.id
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