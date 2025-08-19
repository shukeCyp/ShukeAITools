# -*- coding: utf-8 -*-
"""
全局任务管理器 - 汇总所有平台的任务状态和个数
"""

from datetime import datetime
from typing import Dict, List
from enum import Enum

from backend.managers.jimeng_task_manager import JimengTaskManager
from backend.managers.runway_task_manager import RunwayTaskManager
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
        
        # 初始化所有平台任务管理器
        self._init_platform_managers()
    
    def _init_platform_managers(self):
        """初始化所有平台任务管理器"""
        # 即梦国际版任务管理器
        self.platform_managers['jimeng'] = JimengTaskManager()
        
        # Runway任务管理器
        self.platform_managers['runway'] = RunwayTaskManager()
        
        # TODO: 未来可以添加更多平台
        # self.platform_managers['other_platform'] = OtherTaskManager()
        
        self.stats['total_platforms'] = len(self.platform_managers)
        print(f"📋 全局任务管理器初始化了 {self.stats['total_platforms']} 个平台")
    
    def start(self) -> bool:
        """启动全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.RUNNING:
            print("全局任务管理器已经在运行中")
            return False
            
        print("🚀 启动全局任务管理器...")
        self.status = GlobalTaskManagerStatus.RUNNING
        self.stats['start_time'] = datetime.now()
        
        # 启动所有平台任务管理器
        success_count = 0
        for platform_name, manager in self.platform_managers.items():
            try:
                if manager.start():
                    success_count += 1
                    print(f"✅ {platform_name}平台启动成功")
                else:
                    print(f"❌ {platform_name}平台启动失败")
            except Exception as e:
                print(f"❌ {platform_name}平台启动异常: {str(e)}")
        
        self.stats['running_platforms'] = success_count
        
        if success_count > 0:
            print(f"✅ 全局任务管理器启动成功，运行中的平台: {success_count}/{self.stats['total_platforms']}")
            return True
        else:
            print("❌ 全局任务管理器启动失败，没有成功启动的平台")
            self.status = GlobalTaskManagerStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """停止全局任务管理器"""
        if self.status == GlobalTaskManagerStatus.STOPPED:
            print("全局任务管理器已经停止")
            return False
            
        print("🛑 正在停止全局任务管理器...")
        self.status = GlobalTaskManagerStatus.STOPPED
        
        # 停止所有平台任务管理器
        success_count = 0
        for platform_name, manager in self.platform_managers.items():
            try:
                if manager.stop():
                    success_count += 1
                    print(f"✅ {platform_name}平台停止成功")
                else:
                    print(f"⚠️ {platform_name}平台已经停止")
            except Exception as e:
                print(f"❌ {platform_name}平台停止异常: {str(e)}")
        
        self.stats['running_platforms'] = 0
        print(f"✅ 全局任务管理器已停止，成功停止 {success_count} 个平台")
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
                    print(f"❌ {platform_name}平台暂停异常: {str(e)}")
            
            print(f"⏸️ 全局任务管理器已暂停，成功暂停 {success_count} 个平台")
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
                    print(f"❌ {platform_name}平台恢复异常: {str(e)}")
            
            print(f"▶️ 全局任务管理器已恢复，成功恢复 {success_count} 个平台")
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
        """获取所有平台的线程详细信息"""
        all_threads = []
        
        for platform_name, manager in self.platform_managers.items():
            try:
                if hasattr(manager, 'get_thread_details'):
                    platform_threads = manager.get_thread_details()
                    all_threads.extend(platform_threads)
            except Exception as e:
                print(f"获取{platform_name}线程详情失败: {str(e)}")
        
        return all_threads


# 全局任务管理器实例
global_task_manager = GlobalTaskManager() 