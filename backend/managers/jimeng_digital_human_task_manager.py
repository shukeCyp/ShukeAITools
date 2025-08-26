# -*- coding: utf-8 -*-
"""
即梦数字人任务管理器
"""

import time
import asyncio
import threading
import random
from datetime import datetime, date
from backend.models.models import JimengDigitalHumanTask, JimengAccount
from backend.utils.jimeng_ditigal_human import generate_digital_human
from backend.utils.config_util import get_hide_window

# 扫描间隔配置
TASK_PROCESSOR_INTERVAL = 5  # 任务扫描间隔（秒）

class JimengDigitalHumanTaskManager:
    """即梦数字人任务管理器"""
    
    def __init__(self):
        self.is_running = False
        self.global_executor = None
        self.scan_thread = None
        
    def set_global_executor(self, executor):
        """设置全局线程池执行器"""
        self.global_executor = executor
        
    def start(self):
        """启动任务管理器"""
        print("启动即梦数字人任务管理器")
        self.is_running = True
        
        # 启动扫描线程
        if not self.scan_thread or not self.scan_thread.is_alive():
            self.scan_thread = threading.Thread(target=self._task_processor_loop, daemon=True)
            self.scan_thread.start()
            print("数字人任务扫描线程已启动")
        
    def stop(self):
        """停止任务管理器"""
        print("停止即梦数字人任务管理器")
        self.is_running = False
        
        # 等待扫描线程结束
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=5)
            print("数字人任务扫描线程已停止")
    
    def _task_processor_loop(self):
        """任务处理循环"""
        print("数字人任务扫描线程已启动")
        
        while self.is_running:
            try:
                # 扫描待处理任务
                self._scan_and_process_tasks()
                
                # 等待下次扫描
                time.sleep(TASK_PROCESSOR_INTERVAL)
                
            except Exception as e:
                print(f"数字人任务扫描异常: {str(e)}")
                time.sleep(10)  # 出错时等待更长时间
        
        print("数字人任务扫描线程已结束")
    
    def get_status(self):
        """获取管理器状态"""
        if not self.global_executor:
            return {
                'running': self.is_running,
                'active_threads': 0,
                'thread_pool_alive': False
            }
            
        active_threads = len(getattr(self.global_executor, '_threads', []))
        return {
            'running': self.is_running,
            'active_threads': active_threads,
            'thread_pool_alive': True
        }
    
    def get_summary(self):
        """获取任务汇总统计"""
        try:
            pending = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 0).count()
            processing = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 1).count()
            completed = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 2).count()
            failed = JimengDigitalHumanTask.select().where(JimengDigitalHumanTask.status == 3).count()
            total = pending + processing + completed + failed
            
            return {
                'pending': pending,
                'processing': processing,
                'completed': completed,
                'failed': failed,
                'total': total
            }
        except Exception as e:
            print(f"获取数字人任务汇总失败: {str(e)}")
            return {
                'pending': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'total': 0
            }
    
    def pause(self):
        """暂停任务管理器"""
        # 数字人任务管理器暂停功能可以简单实现
        return True
    
    def resume(self):
        """恢复任务管理器"""
        # 数字人任务管理器恢复功能可以简单实现
        return True
    
    def get_thread_details(self):
        """获取线程详情"""
        # 数字人任务管理器不再管理自己的线程池，统一由全局管理器管理
        return []
    
    def _scan_and_process_tasks(self):
        """扫描并处理数字人任务"""
        if not self.is_running:
            return
            
        try:
            # 获取待处理的任务
            pending_tasks = list(JimengDigitalHumanTask.select().where(
                JimengDigitalHumanTask.status == 0  # 排队中
            ).limit(10))
            
            for task in pending_tasks:
                if not self.is_running:
                    break
                    
                # 检查是否有可用账号
                available_account = self._get_available_account()
                if not available_account:
                    print("没有可用的即梦账号，跳过数字人任务处理")
                    break
                
                # 动态导入全局任务管理器并提交任务
                from backend.core.global_task_manager import global_task_manager
                global_task_manager.submit_task(
                    platform_name="即梦数字人",
                    task_callable=self._process_task,
                    task_id=task.id,
                    task=task,
                    account=available_account,
                    task_type="数字人生成",
                    prompt=f"数字人任务 ID:{task.id}"
                )
                
                print(f"提交数字人任务 {task.id} 到全局线程池")
                
        except Exception as e:
            print(f"扫描数字人任务异常: {str(e)}")
    
    def _get_available_account(self):
        """获取可用的即梦账号"""
        try:
            # 获取有Cookie的账号
            accounts = list(JimengAccount.select())
            
            if not accounts:
                print("没有配置的即梦账号")
                return None
                
            from datetime import date
            today = date.today()
            
            # 检查账号今日数字人使用情况
            available_accounts = []
            for account in accounts:
                # 统计今日数字人使用次数
                today_usage = JimengDigitalHumanTask.select().where(
                    (JimengDigitalHumanTask.account_id == account.id) &
                    (JimengDigitalHumanTask.create_at >= today)
                ).count()
                
                # 数字人每日限制为1个
                if today_usage < 1:
                    available_accounts.append({
                        'account': account,
                        'usage': today_usage
                    })
                print(f"账号: {account.account}，今日已使用: {today_usage}/1")
            
            if available_accounts:
                # 随机选择一个使用次数最少的账号
                min_usage = min(item['usage'] for item in available_accounts)
                min_usage_accounts = [item for item in available_accounts if item['usage'] == min_usage]
                selected_item = random.choice(min_usage_accounts)
                selected_account = selected_item['account']
                
                print(f"选择账号: {selected_account.account}，今日已使用: {selected_item['usage']}/1")
                return selected_account
            else:
                print("所有账号今日数字人使用次数已达上限")
                return None
                
        except Exception as e:
            print(f"获取可用账号异常: {str(e)}")
            return None
    def _process_task(self, task, account):
        """处理单个数字人任务"""
        try:
            print(f"开始处理数字人任务 {task.id}，使用账号: {account.account}")
            
            # 更新任务状态为生成中
            task.status = 1  # 生成中
            task.start_time = datetime.now()
            task.account_id = account.id
            task.save()
            
            # 获取浏览器隐藏配置
            headless = get_hide_window()
            
            # 调用数字人生成函数
            result = asyncio.run(generate_digital_human(
                image_path=task.image_path,
                audio_path=task.audio_path,
                username=account.account,
                password=account.password,
                headless=headless,
                cookies=account.cookies
            ))
            
            # 处理结果
            if result["code"] == 200:
                # 生成成功
                task.status = 2  # 已完成
                task.video_url = result["data"]
                print(f"数字人任务 {task.id} 生成成功")
            elif result["code"] in [603, 604]:
                # 创建空任务记录使用情况
                self._create_empty_task_record(task, account, result["message"])
                # 任务失败
                task.status = 3  # 失败
                print(f"数字人任务 {task.id} 生成失败: {result['message']}")
            else:
                # 其他错误
                task.status = 3  # 失败
                print(f"数字人任务 {task.id} 生成失败: {result['message']}")
                
            task.save()
            
        except Exception as e:
            print(f"处理数字人任务异常，任务ID: {task.id}, 错误: {str(e)}")
            # 更新任务状态为失败
            task.status = 3  # 失败
            task.save()
    
    def _create_empty_task_record(self, original_task, account, error_message):
        """创建空任务记录（用于记录账号使用但未成功的情况）"""
        try:
            empty_task = JimengDigitalHumanTask.create(
                image_path=original_task.image_path,
                audio_path=original_task.audio_path,
                status=3,  # 失败
                account_id=account.id,
                start_time=datetime.now(),
                is_empty_task=True
            )
            print(f"创建空数字人任务记录，用于记录账号 {account.account} 的使用情况")
        except Exception as e:
            print(f"创建空任务记录失败: {str(e)}")

# 创建全局实例
digital_human_manager = JimengDigitalHumanTaskManager() 