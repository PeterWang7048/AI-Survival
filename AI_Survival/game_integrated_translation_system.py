#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏集成翻译系统 - 确保在游戏整个生命周期中都保持活跃
Game Integrated Translation System - Ensure active throughout game lifecycle
"""

import os
import time
import threading
import subprocess
import signal
from datetime import datetime
from typing import Optional, Dict, Any
from enhanced_translation_monitor import EnhancedTranslationMonitor

class GameIntegratedTranslationSystem:
    """与游戏完全集成的翻译系统"""
    
    def __init__(self):
        """初始化游戏集成翻译系统"""
        self.monitor: Optional[EnhancedTranslationMonitor] = None
        self.is_active = False
        self.background_thread = None
        self.last_check_time = None
        self.translation_stats = {
            'files_translated': 0,
            'last_translation': None,
            'errors': 0,
            'start_time': None
        }
        
        print("🎮 游戏集成翻译系统已初始化")
    
    def start_with_game(self, game_settings: Dict[str, Any]):
        """随游戏启动翻译系统"""
        if not game_settings.get('enable_translation', True):
            print("🔇 翻译系统已禁用")
            return False
        
        try:
            # 创建增强版监控器
            self.monitor = EnhancedTranslationMonitor()
            self.is_active = True
            self.translation_stats['start_time'] = datetime.now()
            
            # 启动监控
            self.monitor.start_monitoring()
            
            # 启动游戏专用的后台监控线程
            self.background_thread = threading.Thread(target=self._game_lifecycle_monitor)
            self.background_thread.daemon = False  # 非守护线程，确保不被游戏主线程影响
            self.background_thread.start()
            
            print("🎮 游戏集成翻译系统已启动")
            return True
            
        except Exception as e:
            print(f"❌ 游戏集成翻译系统启动失败: {e}")
            return False
    
    def stop_with_game(self):
        """随游戏停止翻译系统"""
        if not self.is_active:
            return
        
        try:
            print("🛑 正在停止游戏集成翻译系统...")
            
            # 停止监控
            self.is_active = False
            if self.monitor:
                self.monitor.stop_monitoring()
            
            # 等待后台线程结束
            if self.background_thread:
                self.background_thread.join(timeout=10)
            
            # 执行最后一次翻译检查
            self._final_translation_check()
            
            print("✅ 游戏集成翻译系统已停止")
            
        except Exception as e:
            print(f"⚠️ 停止翻译系统时出错: {e}")
    
    def _game_lifecycle_monitor(self):
        """游戏生命周期监控线程"""
        print("👀 游戏生命周期监控线程已启动")
        
        check_interval = 3.0  # 每3秒检查一次
        last_log_files = set()
        
        while self.is_active:
            try:
                self.last_check_time = datetime.now()
                
                # 检查新的日志文件
                current_log_files = self._get_current_log_files()
                new_files = current_log_files - last_log_files
                
                if new_files:
                    print(f"📝 发现 {len(new_files)} 个新日志文件")
                    for new_file in new_files:
                        self._translate_new_file(new_file)
                
                last_log_files = current_log_files
                
                # 检查是否有未翻译的文件
                self._check_untranslated_files()
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ 游戏生命周期监控错误: {e}")
                self.translation_stats['errors'] += 1
                time.sleep(5)  # 错误后等待5秒
    
    def _get_current_log_files(self) -> set:
        """获取当前的日志文件集合"""
        import glob
        log_files = glob.glob('game_*.log')
        # 只返回中文日志文件
        return {f for f in log_files if not f.endswith('_en.log')}
    
    def _translate_new_file(self, file_path: str):
        """翻译新文件"""
        try:
            en_file = file_path.replace('.log', '_en.log')
            
            # 检查是否已经翻译过
            if os.path.exists(en_file):
                # 检查文件修改时间
                if os.path.getmtime(file_path) <= os.path.getmtime(en_file):
                    return  # 已经是最新的翻译
            
            print(f"🔄 正在翻译新文件: {file_path}")
            
            if self.monitor:
                success = self.monitor._translate_file(file_path)
                if success:
                    self.translation_stats['files_translated'] += 1
                    self.translation_stats['last_translation'] = datetime.now()
                    print(f"✅ 翻译完成: {en_file}")
                else:
                    print(f"❌ 翻译失败: {file_path}")
                    self.translation_stats['errors'] += 1
            
        except Exception as e:
            print(f"❌ 翻译新文件时出错: {e}")
            self.translation_stats['errors'] += 1
    
    def _check_untranslated_files(self):
        """检查未翻译的文件"""
        try:
            import glob
            log_files = glob.glob('game_*.log')
            chinese_files = [f for f in log_files if not f.endswith('_en.log')]
            
            for chinese_file in chinese_files:
                en_file = chinese_file.replace('.log', '_en.log')
                
                # 检查是否需要翻译
                if not os.path.exists(en_file):
                    print(f"🔍 发现未翻译的文件: {chinese_file}")
                    self._translate_new_file(chinese_file)
                elif os.path.getmtime(chinese_file) > os.path.getmtime(en_file):
                    print(f"🔄 发现需要更新的文件: {chinese_file}")
                    self._translate_new_file(chinese_file)
                    
        except Exception as e:
            print(f"⚠️ 检查未翻译文件时出错: {e}")
    
    def _final_translation_check(self):
        """最后一次翻译检查"""
        print("🔍 执行最后一次翻译检查...")
        
        try:
            self._check_untranslated_files()
            
            # 显示统计信息
            stats = self.translation_stats
            print(f"\n📊 翻译统计:")
            print(f"  已翻译文件: {stats['files_translated']}")
            print(f"  错误次数: {stats['errors']}")
            print(f"  最后翻译: {stats['last_translation']}")
            
        except Exception as e:
            print(f"⚠️ 最后翻译检查失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'is_active': self.is_active,
            'last_check_time': self.last_check_time,
            'translation_stats': self.translation_stats.copy(),
            'monitor_status': self.monitor.get_status() if self.monitor else None
        }
    
    def force_translate_all(self):
        """强制翻译所有文件"""
        print("🔄 强制翻译所有文件...")
        
        try:
            if self.monitor:
                self.monitor.batch_translate_existing_files()
            else:
                # 创建临时监控器
                temp_monitor = EnhancedTranslationMonitor()
                temp_monitor.batch_translate_existing_files()
                
            print("✅ 强制翻译完成")
            
        except Exception as e:
            print(f"❌ 强制翻译失败: {e}")

# 全局实例
_game_translation_system: Optional[GameIntegratedTranslationSystem] = None

def get_game_translation_system() -> GameIntegratedTranslationSystem:
    """获取游戏翻译系统实例"""
    global _game_translation_system
    if _game_translation_system is None:
        _game_translation_system = GameIntegratedTranslationSystem()
    return _game_translation_system

def start_game_translation_system(game_settings: Dict[str, Any]):
    """启动游戏翻译系统"""
    system = get_game_translation_system()
    return system.start_with_game(game_settings)

def stop_game_translation_system():
    """停止游戏翻译系统"""
    global _game_translation_system
    if _game_translation_system:
        _game_translation_system.stop_with_game()

def force_translate_all_logs():
    """强制翻译所有日志"""
    system = get_game_translation_system()
    system.force_translate_all()

def main():
    """测试游戏集成翻译系统"""
    print("🧪 测试游戏集成翻译系统...")
    
    # 模拟游戏设置
    game_settings = {'enable_translation': True}
    
    # 启动系统
    system = GameIntegratedTranslationSystem()
    
    try:
        # 启动
        system.start_with_game(game_settings)
        
        # 运行15秒进行测试
        print("\n🕐 系统将运行15秒钟...")
        for i in range(15):
            time.sleep(1)
            if (i + 1) % 5 == 0:
                status = system.get_status()
                print(f"📊 状态更新: 已翻译 {status['translation_stats']['files_translated']} 个文件")
        
        print("\n✅ 测试完成")
        
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        system.stop_with_game()
        print("👋 测试结束!")

if __name__ == "__main__":
    main() 