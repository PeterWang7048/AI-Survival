#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志翻译监控系统 - 自动监控和翻译游戏日志
Log Translation Monitor - Automatic monitoring and translation of game logs
"""

import os
import time
import glob
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log_translation_engine import LogTranslationEngine

class LogTranslationMonitor(FileSystemEventHandler):
    """日志翻译监控器"""
    
    def __init__(self, watch_directory: str = "."):
        """初始化监控器"""
        self.watch_directory = watch_directory
        self.engine = LogTranslationEngine()
        self.processed_files: Set[str] = set()
        self.translation_queue: List[str] = []
        self.is_running = False
        self.observer = None
        self.worker_thread = None
        
        # 配置
        self.config = {
            'auto_translate': True,
            'batch_mode': True,
            'quality_check': True,
            'backup_originals': True,
            'log_pattern': 'game_*.log',
            'exclude_pattern': '*_en.log',
            'check_interval': 5.0,  # 检查间隔(秒)
        }
        
        # 统计信息
        self.stats = {
            'files_monitored': 0,
            'files_translated': 0,
            'translation_errors': 0,
            'start_time': None,
            'last_translation': None
        }
        
        print("🤖 日志翻译监控系统已初始化")
    
    def on_created(self, event):
        """文件创建事件处理"""
        if event.is_directory:
            return
            
        filepath = event.src_path
        if self._should_process_file(filepath):
            print(f"📝 检测到新日志文件: {filepath}")
            self._add_to_queue(filepath)
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
            
        filepath = event.src_path
        if self._should_process_file(filepath):
            print(f"📝 检测到日志文件更新: {filepath}")
            self._add_to_queue(filepath)
    
    def _should_process_file(self, filepath: str) -> bool:
        """检查是否应该处理该文件"""
        filename = os.path.basename(filepath)
        
        # 检查是否匹配模式
        if not self._matches_pattern(filename, self.config['log_pattern']):
            return False
        
        # 排除英文版本
        if self._matches_pattern(filename, self.config['exclude_pattern']):
            return False
        
        # 检查文件是否存在且可读
        if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
            return False
        
        return True
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """检查文件名是否匹配模式"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _add_to_queue(self, filepath: str):
        """添加文件到翻译队列"""
        if filepath not in self.translation_queue:
            self.translation_queue.append(filepath)
            print(f"📋 添加到翻译队列: {filepath}")
    
    def start_monitoring(self):
        """启动监控"""
        if self.is_running:
            print("⚠️ 监控已经在运行")
            return
        
        print(f"🚀 启动日志翻译监控...")
        print(f"📁 监控目录: {self.watch_directory}")
        print(f"🔍 文件模式: {self.config['log_pattern']}")
        
        # 首先处理现有文件
        self._process_existing_files()
        
        # 启动文件监控
        self.observer = Observer()
        self.observer.schedule(self, self.watch_directory, recursive=False)
        self.observer.start()
        
        # 启动工作线程
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        print("✅ 监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_running:
            print("⚠️ 监控没有在运行")
            return
        
        print("🛑 停止日志翻译监控...")
        
        self.is_running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        print("✅ 监控已停止")
    
    def _process_existing_files(self):
        """处理现有的日志文件"""
        print("🔍 扫描现有日志文件...")
        
        log_files = glob.glob(os.path.join(self.watch_directory, self.config['log_pattern']))
        
        for log_file in log_files:
            if self._should_process_file(log_file):
                self._add_to_queue(log_file)
        
        print(f"📋 发现 {len(self.translation_queue)} 个文件需要翻译")
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.is_running:
            try:
                if self.translation_queue:
                    filepath = self.translation_queue.pop(0)
                    self._translate_file(filepath)
                else:
                    time.sleep(self.config['check_interval'])
            except Exception as e:
                print(f"❌ 工作线程错误: {str(e)}")
                self.stats['translation_errors'] += 1
                time.sleep(1)
    
    def _translate_file(self, filepath: str):
        """翻译单个文件"""
        try:
            print(f"🔄 开始翻译: {filepath}")
            
            # 生成输出文件名
            name, ext = os.path.splitext(filepath)
            output_file = f"{name}_en{ext}"
            
            # 检查是否已经翻译过
            if os.path.exists(output_file):
                # 检查文件时间戳
                if os.path.getmtime(filepath) <= os.path.getmtime(output_file):
                    print(f"⏭️ 跳过已翻译的文件: {filepath}")
                    return
            
            # 备份原文件（如果需要）
            if self.config['backup_originals']:
                self._backup_file(filepath)
            
            # 执行翻译
            success = self.engine.translate_log_file(filepath, output_file)
            
            if success:
                self.stats['files_translated'] += 1
                self.stats['last_translation'] = datetime.now()
                print(f"✅ 翻译完成: {output_file}")
                
                # 质量检查
                if self.config['quality_check']:
                    self._quality_check(output_file)
                
            else:
                self.stats['translation_errors'] += 1
                print(f"❌ 翻译失败: {filepath}")
                
        except Exception as e:
            print(f"❌ 翻译过程出错: {str(e)}")
            self.stats['translation_errors'] += 1
    
    def _backup_file(self, filepath: str):
        """备份原文件"""
        backup_dir = os.path.join(self.watch_directory, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"💾 备份文件: {backup_path}")
        except Exception as e:
            print(f"⚠️ 备份失败: {str(e)}")
    
    def _quality_check(self, output_file: str):
        """质量检查翻译结果"""
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件是否为空
            if not content.strip():
                print(f"⚠️ 质量检查: 翻译文件为空 - {output_file}")
                return
            
            # 检查是否还有大量中文（可能翻译不完整）
            chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
            total_chars = len(content)
            
            if chinese_chars > total_chars * 0.3:  # 如果中文字符超过30%
                print(f"⚠️ 质量检查: 翻译可能不完整 - {output_file}")
                print(f"   中文字符占比: {chinese_chars/total_chars:.1%}")
            else:
                print(f"✅ 质量检查通过: {output_file}")
                
        except Exception as e:
            print(f"⚠️ 质量检查失败: {str(e)}")
    
    def batch_translate_all(self):
        """批量翻译所有文件"""
        print("🔄 开始批量翻译所有日志文件...")
        
        # 查找所有日志文件
        log_files = glob.glob(os.path.join(self.watch_directory, self.config['log_pattern']))
        
        if not log_files:
            print("❌ 未找到需要翻译的日志文件")
            return
        
        print(f"📁 找到 {len(log_files)} 个日志文件")
        
        # 添加到队列
        for log_file in log_files:
            if self._should_process_file(log_file):
                self._add_to_queue(log_file)
        
        # 处理队列
        while self.translation_queue:
            filepath = self.translation_queue.pop(0)
            self._translate_file(filepath)
        
        print("✅ 批量翻译完成")
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats['start_time']:
            stats['running_time'] = str(datetime.now() - stats['start_time'])
        
        stats['queue_size'] = len(self.translation_queue)
        stats['is_running'] = self.is_running
        
        return stats
    
    def print_status(self):
        """打印当前状态"""
        stats = self.get_statistics()
        
        print("\n📊 翻译监控系统状态:")
        print("=" * 50)
        print(f"  运行状态: {'🟢 运行中' if stats['is_running'] else '🔴 已停止'}")
        print(f"  监控目录: {self.watch_directory}")
        print(f"  队列大小: {stats['queue_size']}")
        print(f"  已翻译文件数: {stats['files_translated']}")
        print(f"  翻译错误数: {stats['translation_errors']}")
        
        if stats['start_time']:
            print(f"  运行时间: {stats['running_time']}")
        
        if stats['last_translation']:
            print(f"  最后翻译: {stats['last_translation']}")
        
        print("=" * 50)

def main():
    """主函数"""
    print("🚀 日志翻译监控系统启动...")
    
    # 创建监控器
    monitor = LogTranslationMonitor()
    
    # 显示配置
    print("\n⚙️ 当前配置:")
    for key, value in monitor.config.items():
        print(f"  {key}: {value}")
    
    try:
        # 选择运行模式
        print("\n🤖 选择运行模式:")
        print("1. 批量翻译所有现有日志文件")
        print("2. 启动实时监控模式")
        print("3. 批量翻译 + 实时监控")
        
        choice = input("\n请选择 (1/2/3): ").strip()
        
        if choice == "1":
            monitor.batch_translate_all()
        elif choice == "2":
            monitor.start_monitoring()
            print("\n按 Ctrl+C 停止监控...")
            try:
                while True:
                    time.sleep(10)
                    monitor.print_status()
            except KeyboardInterrupt:
                print("\n收到停止信号...")
        elif choice == "3":
            monitor.batch_translate_all()
            monitor.start_monitoring()
            print("\n按 Ctrl+C 停止监控...")
            try:
                while True:
                    time.sleep(10)
                    monitor.print_status()
            except KeyboardInterrupt:
                print("\n收到停止信号...")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        monitor.stop_monitoring()
        print("👋 再见!")

if __name__ == "__main__":
    main() 