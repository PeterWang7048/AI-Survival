#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动翻译集成模块 - 无缝集成到游戏主程序
Auto Translation Integration - Seamless integration into main game program
"""

import os
import threading
import time
from typing import Optional

# 全局翻译监控器实例
_global_translation_monitor: Optional['EnhancedTranslationMonitor'] = None

def start_auto_translation(enable_translation=True, silent_mode=True):
    """
    启动自动翻译系统
    
    Args:
        enable_translation: 是否启用翻译功能
        silent_mode: 是否静默模式（减少日志输出）
    """
    global _global_translation_monitor
    
    if not enable_translation:
        if not silent_mode:
            print("🔇 翻译系统已禁用")
        return None
    
    try:
        # 导入增强版翻译监控器
        from enhanced_translation_monitor import EnhancedTranslationMonitor
        
        # 创建监控器实例
        _global_translation_monitor = EnhancedTranslationMonitor()
        
        # 启动监控
        _global_translation_monitor.start_monitoring()
        
        if not silent_mode:
            print("✅ 增强版翻译系统已启动")
        
        return _global_translation_monitor
        
    except ImportError as e:
        if not silent_mode:
            print(f"⚠️ 增强版翻译模块未找到: {e}")
        # 回退到原来的翻译系统
        try:
            from log_translation_monitor import LogTranslationMonitor
            _global_translation_monitor = LogTranslationMonitor()
            
            # 在后台线程中启动监控
            def start_monitoring_thread():
                try:
                    if not silent_mode:
                        print("🌍 启动日志翻译系统...")
                    
                    # 首先进行批量翻译（处理现有文件）
                    _global_translation_monitor.batch_translate_all()
                    
                    # 然后启动实时监控
                    _global_translation_monitor.start_monitoring()
                    
                    if not silent_mode:
                        print("✅ 翻译系统已在后台运行")
                        
                except Exception as e:
                    if not silent_mode:
                        print(f"⚠️ 翻译系统启动失败: {str(e)}")
            
            # 启动后台线程
            monitor_thread = threading.Thread(target=start_monitoring_thread)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return _global_translation_monitor
            
        except ImportError:
            if not silent_mode:
                print("⚠️ 翻译模块未找到，跳过翻译功能")
            return None
            
    except Exception as e:
        if not silent_mode:
            print(f"❌ 翻译系统初始化失败: {str(e)}")
        return None

def stop_auto_translation(silent_mode=True):
    """
    停止自动翻译系统
    
    Args:
        silent_mode: 是否静默模式
    """
    global _global_translation_monitor
    
    if _global_translation_monitor is None:
        return
    
    try:
        if not silent_mode:
            print("🛑 正在停止翻译系统...")
        
        _global_translation_monitor.stop_monitoring()
        _global_translation_monitor = None
        
        if not silent_mode:
            print("✅ 翻译系统已停止")
            
    except Exception as e:
        if not silent_mode:
            print(f"⚠️ 停止翻译系统时出错: {str(e)}")

def get_translation_status():
    """获取翻译系统状态"""
    global _global_translation_monitor
    
    if _global_translation_monitor is None:
        return {
            'active': False,
            'message': '翻译系统未启动'
        }
    
    try:
        # 检查是否是增强版监控器
        if hasattr(_global_translation_monitor, 'get_status'):
            status = _global_translation_monitor.get_status()
            return {
                'active': status['is_running'],
                'stats': status['stats'],
                'message': f"增强版翻译系统运行中 - 已翻译 {status['stats']['files_translated']} 个文件"
            }
        else:
            # 原版监控器
            stats = _global_translation_monitor.get_statistics()
            return {
                'active': True,
                'stats': stats,
                'message': f"翻译系统运行中 - 已翻译 {stats['files_translated']} 个文件"
            }
    except:
        return {
            'active': False,
            'message': '翻译系统状态未知'
        }

# 便捷的自动启动函数，用于集成到main.py
def auto_start_translation_on_game_start():
    """
    游戏启动时自动启动翻译系统
    这个函数设计为在游戏开始时调用
    """
    # 检查是否有配置文件指定翻译选项
    translation_enabled = True
    
    # 尝试从配置文件读取设置
    try:
        if os.path.exists('translation_config.txt'):
            with open('translation_config.txt', 'r') as f:
                setting = f.read().strip().lower()
                translation_enabled = setting in ['true', '1', 'yes', 'enabled']
    except:
        pass
    
    # 启动翻译系统
    return start_auto_translation(
        enable_translation=translation_enabled,
        silent_mode=True  # 游戏启动时使用静默模式
    )

def auto_stop_translation_on_game_end():
    """
    游戏结束时自动停止翻译系统
    这个函数设计为在游戏结束时调用
    """
    stop_auto_translation(silent_mode=True)

def create_translation_config(enable_translation=True):
    """
    创建翻译配置文件
    
    Args:
        enable_translation: 是否启用翻译
    """
    try:
        with open('translation_config.txt', 'w') as f:
            f.write('true' if enable_translation else 'false')
        print(f"✅ 翻译配置已保存: {'启用' if enable_translation else '禁用'}")
    except Exception as e:
        print(f"⚠️ 保存翻译配置失败: {str(e)}")

def main():
    """
    测试自动翻译集成功能
    """
    print("🧪 测试自动翻译集成...")
    
    # 测试启动
    monitor = start_auto_translation(enable_translation=True, silent_mode=False)
    
    if monitor:
        print("✅ 翻译系统启动成功")
        
        # 等待一些时间让系统工作
        time.sleep(5)
        
        # 检查状态
        status = get_translation_status()
        print(f"📊 系统状态: {status['message']}")
        
        # 测试停止
        stop_auto_translation(silent_mode=False)
        print("✅ 测试完成")
    else:
        print("❌ 翻译系统启动失败")

if __name__ == "__main__":
    main() 