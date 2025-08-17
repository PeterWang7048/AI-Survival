#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版翻译监控器 - 确保游戏运行期间持续监控新文件
Enhanced Translation Monitor - Ensure continuous monitoring during game runtime
"""

import os
import time
import glob
import threading
from datetime import datetime
from typing import Set, Optional
from log_translation_engine import LogTranslationEngine
from log_translation_monitor import LogTranslationMonitor

class EnhancedTranslationMonitor:
    """增强版翻译监控器"""
    
    def __init__(self, watch_directory: str = "."):
        """初始化增强版监控器"""
        self.watch_directory = watch_directory
        self.engine = LogTranslationEngine()
        self.processed_files: Set[str] = set()
        self.is_running = False
        self.monitor_thread = None
        
        # 配置
        self.config = {
            'check_interval': 2.0,  # 每2秒检查一次
            'log_pattern': 'game_*.log',
            'exclude_pattern': '*_en.log',
            'max_file_age': 3600,  # 1小时内的文件
        }
        
        # 统计信息
        self.stats = {
            'files_monitored': 0,
            'files_translated': 0,
            'translation_errors': 0,
            'start_time': None,
            'last_check': None,
            'last_translation': None
        }
        
        print("🚀 增强版翻译监控器已初始化")
    
    def start_monitoring(self):
        """启动监控"""
        if self.is_running:
            print("⚠️ 监控器已在运行")
            return
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        # 首先进行批量翻译
        self.batch_translate_existing_files()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("🔍 增强版翻译监控器已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("🛑 增强版翻译监控器已停止")
    
    def batch_translate_existing_files(self):
        """批量翻译现有文件"""
        print("🔄 开始批量翻译现有文件...")
        
        # 获取所有中文日志文件
        log_files = glob.glob(os.path.join(self.watch_directory, self.config['log_pattern']))
        chinese_files = [f for f in log_files if not f.endswith('_en.log')]
        
        print(f"📁 找到 {len(chinese_files)} 个中文日志文件")
        
        translated_count = 0
        for log_file in chinese_files:
            if self._should_translate_file(log_file):
                if self._translate_file(log_file):
                    translated_count += 1
                    self.stats['files_translated'] += 1
            else:
                print(f"⏭️ 跳过已翻译的文件: {log_file}")
        
        print(f"✅ 批量翻译完成，翻译了 {translated_count} 个文件")
    
    def _monitor_loop(self):
        """监控循环"""
        print("👀 开始实时监控新文件...")
        
        while self.is_running:
            try:
                self.stats['last_check'] = datetime.now()
                
                # 检查新文件
                self._check_for_new_files()
                
                # 等待下次检查
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                print(f"❌ 监控循环错误: {e}")
                self.stats['translation_errors'] += 1
                time.sleep(5)  # 错误后等待5秒再重试
    
    def _check_for_new_files(self):
        """检查新文件"""
        # 获取所有中文日志文件
        log_files = glob.glob(os.path.join(self.watch_directory, self.config['log_pattern']))
        chinese_files = [f for f in log_files if not f.endswith('_en.log')]
        
        for log_file in chinese_files:
            # 检查是否是新文件或需要重新翻译的文件
            if self._is_new_or_modified_file(log_file):
                if self._should_translate_file(log_file):
                    print(f"📝 发现新文件: {log_file}")
                    if self._translate_file(log_file):
                        self.stats['files_translated'] += 1
                        self.stats['last_translation'] = datetime.now()
                        print(f"✅ 成功翻译: {log_file}")
                    else:
                        self.stats['translation_errors'] += 1
                        print(f"❌ 翻译失败: {log_file}")
    
    def _is_new_or_modified_file(self, file_path: str) -> bool:
        """检查文件是否是新文件或已修改"""
        try:
            # 检查文件是否已处理过
            if file_path in self.processed_files:
                # 检查文件修改时间
                file_mtime = os.path.getmtime(file_path)
                en_file = file_path.replace('.log', '_en.log')
                
                if os.path.exists(en_file):
                    en_mtime = os.path.getmtime(en_file)
                    # 如果中文文件比英文文件新，则需要重新翻译
                    return file_mtime > en_mtime
                else:
                    # 英文文件不存在，需要翻译
                    return True
            else:
                # 未处理过的文件
                return True
                
        except Exception as e:
            print(f"⚠️ 检查文件状态失败: {e}")
            return True
    
    def _should_translate_file(self, file_path: str) -> bool:
        """检查文件是否应该被翻译"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件年龄
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > self.config['max_file_age']:
                return False
            
            # 检查是否已有英文版本
            en_file = file_path.replace('.log', '_en.log')
            if os.path.exists(en_file):
                # 比较文件修改时间
                return os.path.getmtime(file_path) > os.path.getmtime(en_file)
            
            return True
            
        except Exception as e:
            print(f"⚠️ 检查翻译条件失败: {e}")
            return False
    
    def _translate_file(self, file_path: str) -> bool:
        """翻译文件"""
        try:
            # 标记为已处理
            self.processed_files.add(file_path)
            
            # 生成输出文件名
            output_file = file_path.replace('.log', '_en.log')
            
            # 执行翻译
            print(f"🔄 开始翻译: {file_path}")
            success = self.engine.translate_log_file(file_path, output_file)
            
            if success:
                print(f"✅ 翻译完成: {output_file}")
                return True
            else:
                print(f"❌ 翻译失败: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 翻译过程出错: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取监控状态"""
        return {
            'is_running': self.is_running,
            'stats': self.stats.copy(),
            'processed_files': len(self.processed_files),
            'last_check': self.stats['last_check'].isoformat() if self.stats['last_check'] else None,
            'last_translation': self.stats['last_translation'].isoformat() if self.stats['last_translation'] else None,
        }
    
    def print_status(self):
        """打印状态信息"""
        status = self.get_status()
        print("\n📊 增强版翻译监控器状态:")
        print(f"   运行状态: {'🟢 运行中' if status['is_running'] else '🔴 已停止'}")
        print(f"   已处理文件: {status['processed_files']}")
        print(f"   已翻译文件: {status['stats']['files_translated']}")
        print(f"   翻译错误: {status['stats']['translation_errors']}")
        print(f"   最后检查: {status['last_check']}")
        print(f"   最后翻译: {status['last_translation']}")

def main():
    """测试增强版翻译监控器"""
    print("🧪 测试增强版翻译监控器...")
    
    # 创建监控器
    monitor = EnhancedTranslationMonitor()
    
    try:
        # 启动监控
        monitor.start_monitoring()
        
        # 运行10秒钟进行测试
        print("\n🕐 监控器将运行10秒钟...")
        for i in range(10):
            time.sleep(1)
            if (i + 1) % 3 == 0:
                monitor.print_status()
        
        print("\n✅ 测试完成")
        
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        monitor.stop_monitoring()
        print("👋 再见!")

if __name__ == "__main__":
    main() 