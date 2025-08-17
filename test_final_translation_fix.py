#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最终翻译修复效果
Test Final Translation Fix Effect
"""

import os
import time
import glob
import subprocess
from datetime import datetime

def test_translation_fix():
    """测试翻译系统修复效果"""
    print("🧪 测试翻译系统修复效果")
    print("=" * 60)
    
    # 1. 记录测试前的日志文件状态
    print("\n1. 📊 记录测试前的状态:")
    existing_logs = glob.glob('game_*.log')
    chinese_logs = [f for f in existing_logs if not f.endswith('_en.log')]
    english_logs = [f for f in existing_logs if f.endswith('_en.log')]
    
    print(f"   现有中文日志: {len(chinese_logs)} 个")
    print(f"   现有英文日志: {len(english_logs)} 个")
    
    # 显示最新的几个文件
    if chinese_logs:
        chinese_logs.sort(key=os.path.getmtime, reverse=True)
        print("   最新的中文日志:")
        for i, log in enumerate(chinese_logs[:3]):
            mtime = datetime.fromtimestamp(os.path.getmtime(log)).strftime('%H:%M:%S')
            en_log = log.replace('.log', '_en.log')
            has_en = '✅' if os.path.exists(en_log) else '❌'
            print(f"     {i+1}. {log} ({mtime}) - 英文版: {has_en}")
    
    print("\n2. 🔄 启动翻译系统进行实时监控:")
    
    # 启动增强版翻译系统
    try:
        from game_integrated_translation_system import GameIntegratedTranslationSystem
        
        # 创建翻译系统
        translation_system = GameIntegratedTranslationSystem()
        
        # 启动系统
        game_settings = {'enable_translation': True}
        success = translation_system.start_with_game(game_settings)
        
        if success:
            print("   ✅ 翻译系统启动成功")
            
            # 监控10秒钟
            print("\n3. 👀 监控10秒钟，等待新日志文件...")
            for i in range(10):
                time.sleep(1)
                
                # 检查是否有新的日志文件
                current_logs = glob.glob('game_*.log')
                current_chinese = [f for f in current_logs if not f.endswith('_en.log')]
                
                new_files = set(current_chinese) - set(chinese_logs)
                if new_files:
                    print(f"   📝 发现新文件: {list(new_files)}")
                    break
                
                if (i + 1) % 3 == 0:
                    print(f"   ⏰ 等待中... ({i+1}/10秒)")
            
            # 停止系统
            translation_system.stop_with_game()
            print("   🛑 翻译系统已停止")
            
        else:
            print("   ❌ 翻译系统启动失败")
            
    except Exception as e:
        print(f"   ❌ 翻译系统测试失败: {e}")
    
    print("\n4. 📊 测试结果分析:")
    
    # 重新检查日志文件状态
    final_logs = glob.glob('game_*.log')
    final_chinese = [f for f in final_logs if not f.endswith('_en.log')]
    final_english = [f for f in final_logs if f.endswith('_en.log')]
    
    print(f"   最终中文日志: {len(final_chinese)} 个")
    print(f"   最终英文日志: {len(final_english)} 个")
    
    # 检查每个中文日志是否有对应的英文版本
    print("\n5. 🔍 详细文件检查:")
    missing_translations = []
    
    for chinese_log in final_chinese:
        english_log = chinese_log.replace('.log', '_en.log')
        has_english = os.path.exists(english_log)
        
        if has_english:
            # 检查文件时间
            chinese_time = os.path.getmtime(chinese_log)
            english_time = os.path.getmtime(english_log)
            time_diff = english_time - chinese_time
            
            status = "✅ 有翻译"
            if time_diff < 0:
                status += " (需更新)"
            
        else:
            status = "❌ 缺少翻译"
            missing_translations.append(chinese_log)
        
        mtime = datetime.fromtimestamp(os.path.getmtime(chinese_log)).strftime('%m-%d %H:%M:%S')
        print(f"   {chinese_log} ({mtime}) - {status}")
    
    print(f"\n6. 📋 总结:")
    if missing_translations:
        print(f"   ❌ 发现 {len(missing_translations)} 个未翻译的文件:")
        for missing in missing_translations:
            print(f"      - {missing}")
        
        print(f"\n   🔧 立即补充翻译这些文件:")
        try:
            from enhanced_translation_monitor import EnhancedTranslationMonitor
            monitor = EnhancedTranslationMonitor()
            
            for missing_file in missing_translations:
                result = monitor._translate_file(missing_file)
                if result:
                    print(f"      ✅ 已翻译: {missing_file}")
                else:
                    print(f"      ❌ 翻译失败: {missing_file}")
                    
        except Exception as e:
            print(f"      ❌ 补充翻译失败: {e}")
    else:
        print("   🎉 所有中文日志都有对应的英文翻译！")
    
    print(f"\n✅ 测试完成！翻译系统{'正常工作' if not missing_translations else '需要进一步优化'}")

if __name__ == "__main__":
    test_translation_fix() 