#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速游戏测试 - 验证翻译系统修复效果
Quick Game Test - Verify Translation System Fix
"""

import os
import sys
import time
import glob
import subprocess
from datetime import datetime

def run_quick_game_test():
    """运行快速游戏测试"""
    print("🎮 快速游戏测试 - 验证翻译系统修复效果")
    print("=" * 60)
    
    # 记录测试前的状态
    print("\n1. 📊 记录测试前的状态:")
    before_logs = glob.glob('game_*.log')
    before_chinese = [f for f in before_logs if not f.endswith('_en.log')]
    before_english = [f for f in before_logs if f.endswith('_en.log')]
    
    print(f"   测试前中文日志: {len(before_chinese)} 个")
    print(f"   测试前英文日志: {len(before_english)} 个")
    
    if before_chinese:
        latest_before = max(before_chinese, key=os.path.getmtime)
        print(f"   最新的中文日志: {latest_before}")
    
    # 创建一个快速的游戏配置
    print("\n2. 🚀 启动快速游戏测试...")
    
    # 修改main.py来运行一个超快速的游戏
    backup_main_py()
    
    try:
        # 修改main.py进行快速测试
        modify_main_py_for_quick_test()
        
        # 运行游戏
        print("   🎮 运行游戏...")
        start_time = time.time()
        
        # 使用subprocess运行游戏
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 等待游戏结束，最多等待30秒
        stdout, stderr = process.communicate(timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ✅ 游戏结束，耗时: {duration:.1f}秒")
        
        # 等待额外的5秒让翻译系统处理
        print("   ⏰ 等待5秒让翻译系统处理...")
        time.sleep(5)
        
    except subprocess.TimeoutExpired:
        print("   ⏰ 游戏超时，强制结束")
        process.kill()
        
    except Exception as e:
        print(f"   ❌ 游戏运行失败: {e}")
        
    finally:
        # 恢复原始main.py
        restore_main_py()
    
    # 检查结果
    print("\n3. 📊 检查测试结果:")
    
    after_logs = glob.glob('game_*.log')
    after_chinese = [f for f in after_logs if not f.endswith('_en.log')]
    after_english = [f for f in after_logs if f.endswith('_en.log')]
    
    print(f"   测试后中文日志: {len(after_chinese)} 个")
    print(f"   测试后英文日志: {len(after_english)} 个")
    
    # 找到新生成的日志
    new_chinese = set(after_chinese) - set(before_chinese)
    new_english = set(after_english) - set(before_english)
    
    print(f"   新生成中文日志: {len(new_chinese)} 个")
    print(f"   新生成英文日志: {len(new_english)} 个")
    
    if new_chinese:
        new_log = list(new_chinese)[0]
        english_log = new_log.replace('.log', '_en.log')
        
        print(f"\n4. 🔍 检查新日志文件:")
        print(f"   新中文日志: {new_log}")
        
        if os.path.exists(english_log):
            print(f"   对应英文日志: {english_log} ✅")
            
            # 检查文件大小和时间
            chinese_size = os.path.getsize(new_log)
            english_size = os.path.getsize(english_log)
            chinese_time = os.path.getmtime(new_log)
            english_time = os.path.getmtime(english_log)
            
            print(f"   中文文件大小: {chinese_size:,} 字节")
            print(f"   英文文件大小: {english_size:,} 字节")
            print(f"   时间差: {english_time - chinese_time:.1f} 秒")
            
            if english_time > chinese_time:
                print("   ✅ 英文版在中文版之后生成 - 翻译系统正常工作！")
            else:
                print("   ⚠️ 英文版时间异常")
                
        else:
            print(f"   对应英文日志: 不存在 ❌")
            print("   ❌ 翻译系统未能及时处理新日志")
            
            # 尝试手动翻译
            print("\n   🔧 尝试手动翻译:")
            try:
                from enhanced_translation_monitor import EnhancedTranslationMonitor
                monitor = EnhancedTranslationMonitor()
                result = monitor._translate_file(new_log)
                if result:
                    print("   ✅ 手动翻译成功")
                else:
                    print("   ❌ 手动翻译失败")
            except Exception as e:
                print(f"   ❌ 手动翻译异常: {e}")
    
    else:
        print("\n4. ❌ 没有检测到新的日志文件")
        print("   可能游戏没有正常运行或日志没有生成")
    
    print(f"\n5. 📋 测试结论:")
    if new_chinese and len(new_chinese) == len(new_english):
        print("   🎉 测试成功！翻译系统修复有效！")
        print("   ✅ 新生成的日志文件都有对应的英文翻译")
    elif new_chinese:
        print("   ⚠️ 测试部分成功，但翻译系统可能仍有问题")
        print("   📝 建议进一步优化翻译系统")
    else:
        print("   ❌ 测试失败，没有生成新的日志文件")

def backup_main_py():
    """备份原始main.py"""
    if os.path.exists('main.py') and not os.path.exists('main_backup.py'):
        import shutil
        shutil.copy2('main.py', 'main_backup.py')
        print("   📋 已备份原始main.py")

def restore_main_py():
    """恢复原始main.py"""
    if os.path.exists('main_backup.py'):
        import shutil
        shutil.copy2('main_backup.py', 'main.py')
        os.remove('main_backup.py')
        print("   📋 已恢复原始main.py")

def modify_main_py_for_quick_test():
    """修改main.py进行快速测试"""
    print("   🔧 修改main.py进行快速测试...")
    
    # 读取原始文件
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换游戏持续时间为超短时间
    content = content.replace(
        'game_duration = tk.IntVar(value=30)',
        'game_duration = tk.IntVar(value=3)'  # 3天游戏
    )
    
    # 替换地图大小为超小地图
    content = content.replace(
        'map_width = tk.IntVar(value=15)',
        'map_width = tk.IntVar(value=5)'
    )
    content = content.replace(
        'map_height = tk.IntVar(value=15)',
        'map_height = tk.IntVar(value=5)'
    )
    
    # 替换玩家数量为1个
    content = content.replace(
        'player_count = tk.IntVar(value=4)',
        'player_count = tk.IntVar(value=1)'
    )
    
    # 添加自动开始游戏的代码
    if 'auto_start_game = True' not in content:
        content = content.replace(
            'if __name__ == "__main__":',
            'auto_start_game = True\n\nif __name__ == "__main__":'
        )
    
    # 写回修改后的内容
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   ✅ main.py已修改为快速测试模式")

if __name__ == "__main__":
    run_quick_game_test() 