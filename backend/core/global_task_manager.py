# -*- coding: utf-8 -*-
"""
全局任务管理器 - 汇总所有平台的任务状态和个数
"""

import threading
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.managers.jimeng_task_manager import JimengTaskManager
from backend.managers.jimeng_img2video_task_manager import JimengImg2VideoTaskManager
from backend.managers.jimeng_digital_human_task_manager import digital_human_manager
from backend.managers.qingying_img2video_task_manager import QingyingImg2VideoTaskManager
from backend.utils.config_util import get_automation_max_threads

class GlobalTaskManagerStatus(Enum):
    """全局任务管理器状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class GlobalTaskManager:
    """全局任务管理器 - 汇总所有平台任务状态"""
    
    def __init__(self):
        self.status = GlobalTaskManagerStatus.STOPPED
        self.platform_managers = {}  # 平台名称 -> 平台任务管理器
        self.stats = {
            'start_time': None,
            'total_platforms': 0,
            'running_platforms': 0
        }
        
        # 全局线程池
        self.global_executor = None
        self.max_threads = 0
        self.active_tasks = {}  # 存储正在执行的任务信息 {thread_id: task_info}
        self._task_id_counter = 0  # 用于分配线程ID
        
        # 初始化所有平台任务管理器
        self._init_platform_managers()
    
    def _init_platform_managers(self):
        """初始化所有平台任务管理器"""
        # 即梦国际版任务管理器
        self.platform_managers['jimeng'] = JimengTaskManager()
        
        # 即梦图生视频任务管理器
        self.platform_managers['jimeng_img2video'] = JimengImg2VideoTaskManager()
        
        # 即梦数字人任务管理器
        self.platform_managers['jimeng_digital_human'] = digital_human_manager
        
        # 清影图生视频任务管理器
        self.qingying_img2video_manager = QingyingImg2VideoTaskManager()
        self.platform_managers['qingying_img2video'] = self.qingying_img2video_manager
        
        # TODO: 未来可以添加更多平台
        # self.platform_managers['runway'] = RunwayTaskManager()
        # self.platform_managers['other_platform'] = OtherTaskManager()
        
        self.stats['total_platforms'] = len(self.platform_managers)
        print(f"全局任务管理器初始化了 {self.stats['total_platforms']} 个平台")
    
    def start(self) -> bool:
        """启动全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.RUNNING:
            print("全局任务管理器已经在运行中")
            return False
            
        print("启动全局任务管理器...")
        self.status = GlobalTaskManagerStatus.RUNNING
        self.stats['start_time'] = datetime.now()
        
        # 创建全局线程池
        self.max_threads = get_automation_max_threads()
        self.global_executor = ThreadPoolExecutor(max_workers=self.max_threads, thread_name_prefix="GlobalWorker")
        print(f"创建全局线程池，最大线程数: {self.max_threads}")
        
        # 等待一段时间确保数据库操作完全完成
        time.sleep(2.0)
        print("开始启动平台任务管理器...")
        
        # 启动所有平台任务管理器（不再让它们创建自己的线程池）
        success_count = 0
        for platform_name, manager in self.platform_managers.items():
            try:
                # 传递全局线程池给各个平台管理器
                if hasattr(manager, 'set_global_executor'):
                    manager.set_global_executor(self.global_executor)
                
                # 在启动每个管理器之间添加小延迟
                time.sleep(0.5)
                
                if manager.start():
                    success_count += 1
                    print(f"{platform_name}平台启动成功")
                else:
                    print(f"{platform_name}平台启动失败")
            except Exception as e:
                print(f"{platform_name}平台启动异常: {str(e)}")
        
        self.stats['running_platforms'] = success_count
        
        if success_count > 0:
            print(f"全局任务管理器启动成功，运行中的平台: {success_count}/{self.stats['total_platforms']}")
            return True
        else:
            print("全局任务管理器启动失败，没有成功启动的平台")
            self.status = GlobalTaskManagerStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """停止全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.STOPPED:
            print("全局任务管理器已经停止")
            return False
            
        print("正在停止全局任务管理器...")
        self.status = GlobalTaskManagerStatus.STOPPED
        
        # 停止所有平台任务管理器
        success_count = 0
        for platform_name, manager in self.platform_managers.items():
            try:
                if manager.stop():
                    success_count += 1
                    print(f"{platform_name}平台停止成功")
                else:
                    print(f"{platform_name}平台已经停止")
            except Exception as e:
                print(f"{platform_name}平台停止异常: {str(e)}")
        
        # 关闭全局线程池
        if self.global_executor:
            self.global_executor.shutdown(wait=True)
            self.global_executor = None
            print("全局线程池已关闭")
        
        self.active_tasks.clear()
        self.stats['running_platforms'] = 0
        print(f"全局任务管理器已停止，成功停止 {success_count} 个平台")
        return True
    
    def pause(self) -> bool:
        """暂停全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.RUNNING:
            self.status = GlobalTaskManagerStatus.PAUSED
            
            # 暂停所有平台任务管理器
            success_count = 0
            for platform_name, manager in self.platform_managers.items():
                try:
                    if manager.pause():
                        success_count += 1
                except Exception as e:
                    print(f"{platform_name}平台暂停异常: {str(e)}")
            
            print(f"全局任务管理器已暂停，成功暂停 {success_count} 个平台")
            return True
        return False
    
    def resume(self) -> bool:
        """恢复全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.PAUSED:
            self.status = GlobalTaskManagerStatus.RUNNING
            
            # 恢复所有平台任务管理器
            success_count = 0
            for platform_name, manager in self.platform_managers.items():
                try:
                    if manager.resume():
                        success_count += 1
                except Exception as e:
                    print(f"{platform_name}平台恢复异常: {str(e)}")
            
            print(f"全局任务管理器已恢复，成功恢复 {success_count} 个平台")
            return True
        return False
    
    def get_global_summary(self) -> Dict:
        """获取全局汇总统计"""
        total_pending = 0
        total_processing = 0
        total_completed = 0
        total_failed = 0
        total_tasks = 0
        
        platform_summaries = {}
        
        for platform_name, manager in self.platform_managers.items():
            try:
                platform_summary = manager.get_summary()
                platform_summaries[platform_name] = platform_summary
                
                # 汇总全局统计
                total_pending += platform_summary.get('pending', 0)
                total_processing += platform_summary.get('processing', 0)
                total_completed += platform_summary.get('completed', 0)
                total_failed += platform_summary.get('failed', 0)
                total_tasks += platform_summary.get('total', 0)
                
            except Exception as e:
                print(f"获取{platform_name}汇总失败: {str(e)}")
                platform_summaries[platform_name] = {
                    'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0, 'total': 0
                }
        
        return {
            'global_total': {
                'pending': total_pending,
                'processing': total_processing,
                'completed': total_completed,
                'failed': total_failed,
                'total': total_tasks
            },
            'platforms': platform_summaries,
            'platform_count': len(self.platform_managers),
            'running_platforms': self.stats['running_platforms']
        }
    
    def get_status(self) -> Dict:
        """获取全局任务管理器状态"""
        max_threads = get_automation_max_threads()
        active_threads = 0
        
        # 统计所有平台的活跃线程数
        for manager in self.platform_managers.values():
            try:
                if hasattr(manager, 'get_status'):
                    manager_status = manager.get_status()
                    active_threads += manager_status.get('active_threads', 0)
            except:
                pass
        
        return {
            'status': self.status.value,
            'uptime': (datetime.now() - self.stats['start_time']).total_seconds() 
                     if self.stats['start_time'] else 0,
            'platform_count': self.stats['total_platforms'],
            'running_platforms': self.stats['running_platforms'],
            'max_threads': max_threads,
            'active_threads': active_threads
        }
    
    def get_platform_manager(self, platform_name: str):
        """获取指定平台的任务管理器"""
        return self.platform_managers.get(platform_name)
    
    def get_platform_list(self) -> List[str]:
        """获取所有平台名称列表"""
        return list(self.platform_managers.keys())
    
    def get_all_thread_details(self) -> List[Dict]:
        """获取全局线程池的线程详细信息"""
        threads = []
        
        if not self.global_executor or self.status != GlobalTaskManagerStatus.RUNNING:
            # 如果全局线程池未启动，返回空列表
            return threads
        
        # 生成统一的线程视图
        for i in range(1, self.max_threads + 1):
            if i in self.active_tasks:
                # 活跃线程
                task_info = self.active_tasks[i]
                thread_info = {
                    'id': i,
                    'status': 'active',
                    'task_id': task_info['task_id'],
                    'platform': task_info['platform'],
                    'task_type': task_info['task_type'],
                    'prompt': task_info['prompt'],
                    'progress': task_info['progress'],
                    'start_time': task_info['start_time']
                }
            else:
                # 空闲线程
                thread_info = {
                    'id': i,
                    'status': 'idle',
                    'task_id': None,
                    'platform': '全局线程池',
                    'task_type': None,
                    'prompt': None,
                    'progress': 0,
                    'start_time': None
                }
            
            threads.append(thread_info)
        
        return threads
    
    def submit_task(self, platform_name: str, task_callable, *args, **kwargs):
        """提交任务到全局线程池"""
        print(f"全局任务管理器收到任务提交请求: platform={platform_name}, task_id={kwargs.get('task_id')}")
        
        if not self.global_executor:
            print("全局线程池未启动")
            raise RuntimeError("全局线程池未启动")
        
        # 分配线程ID
        thread_id = None
        for i in range(1, self.max_threads + 1):
            if i not in self.active_tasks:
                thread_id = i
                break
        
        if thread_id is None:
            print(f"没有可用的线程，当前活跃任务: {len(self.active_tasks)}")
            raise RuntimeError("没有可用的线程")
        
        # 创建任务信息，从参数中提取任务ID
        task_id_value = kwargs.get('task_id')
        if task_id_value is None and len(args) > 0:
            # 如果第一个参数是数字，可能是任务ID
            if isinstance(args[0], (int, str)):
                task_id_value = args[0]
            # 如果第一个参数是任务对象，尝试获取其id属性
            elif hasattr(args[0], 'id'):
                task_id_value = args[0].id
        
        task_info = {
            'task_id': task_id_value or f'task_{self._task_id_counter}',
            'platform': platform_name,
            'task_type': kwargs.get('task_type', '未知'),
            'prompt': kwargs.get('prompt', None),
            'progress': 0,
            'start_time': datetime.now()
        }
        
        self._task_id_counter += 1
        self.active_tasks[thread_id] = task_info
        
        print(f"任务已分配到线程 {thread_id}: {task_info}")
        
        # 提交任务
        future = self.global_executor.submit(self._execute_task_wrapper, thread_id, task_callable, *args, **kwargs)
        print(f"任务已提交到全局线程池，Future: {future}")
        return future
    
    def _execute_task_wrapper(self, thread_id: int, task_callable, *args, **kwargs):
        """任务执行包装器，用于清理线程状态"""
        task_info = self.active_tasks.get(thread_id, {})
        print(f"开始执行任务: 线程{thread_id}, 任务ID={task_info.get('task_id')}, 平台={task_info.get('platform')}")
        
        try:
            # 更新进度为处理中
            if thread_id in self.active_tasks:
                self.active_tasks[thread_id]['progress'] = 50
                print(f"任务进度更新为50%: 线程{thread_id}")
            
            # 执行实际任务
            print(f"调用任务函数: {task_callable.__name__}")
            
            # 获取函数签名，判断它接受哪些参数
            import inspect
            try:
                sig = inspect.signature(task_callable)
                param_names = list(sig.parameters.keys())
                print(f"函数 {task_callable.__name__} 接受参数: {param_names}")
                
                # 构建函数参数
                func_args = []
                func_kwargs = {}
                
                # 处理位置参数
                for i, param_name in enumerate(param_names):
                    if param_name == 'self':
                        continue  # 跳过self参数
                    
                    # 检查是否有同名的关键字参数
                    if param_name in kwargs:
                        func_kwargs[param_name] = kwargs[param_name]
                    # 否则尝试从args中获取
                    elif i-1 < len(args):  # i-1是因为跳过了self
                        func_args.append(args[i-1])
                
                # 调用函数
                if func_kwargs:
                    result = task_callable(*func_args, **func_kwargs)
                else:
                    result = task_callable(*func_args)
                
            except Exception as e:
                print(f"无法解析函数参数: {str(e)}，尝试使用传入的参数")
                
                # 尝试从kwargs中提取函数需要的参数
                if 'account_id' in kwargs and 'account_email' in kwargs:
                    result = task_callable(kwargs['account_id'], kwargs['account_email'])
                else:
                    # 最后尝试直接调用
                    result = task_callable(*args)
                
            print(f"任务函数执行完成: 线程{thread_id}, 结果: {result}")
            
            # 更新进度为完成
            if thread_id in self.active_tasks:
                self.active_tasks[thread_id]['progress'] = 100
                print(f"任务进度更新为100%: 线程{thread_id}")
            
            return result
        except Exception as e:
            print(f"任务执行异常: 线程{thread_id}, 错误: {str(e)}")
            raise
        finally:
            # 清理线程状态
            print(f"清理线程状态: 线程{thread_id}")
            if thread_id in self.active_tasks:
                del self.active_tasks[thread_id]
            else:
                print(f"线程状态已被清理: 线程{thread_id}")


# 全局任务管理器实例
global_task_manager = GlobalTaskManager() 