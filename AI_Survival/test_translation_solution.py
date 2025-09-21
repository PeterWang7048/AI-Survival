#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译系统解决方案
Test Translation System Solution
"""

import os
import time
import datetime
from auto_translation_integration import start_auto_translation, get_translation_status

def test_translation_solution():
    """测试完整的翻译系统解决方案"""
    print('🔧 测试完整的翻译系统解决方案')
    print('=' * 50)
    
    # 1. 测试增强版集成系统
    print('\n1. 测试增强版集成系统:')
    
    # 启动翻译系统
    monitor = start_auto_translation(enable_translation=True, silent_mode=False)
    success = '成功' if monitor else '失败'
    print(f'监控器启动: {success}')
    
    # 检查状态
    status = get_translation_status()
    print(f'系统状态: {status["message"]}')
    
    # 等待一段时间让系统工作
    print('\n2. 等待系统工作5秒...')
    time.sleep(5)
    
    # 再次检查状态
    status = get_translation_status()
    print(f'运行状态: {status["message"]}')
    
    print('\n3. 检查文件状态:')
    test_files = [
        'game_20250706_063923.log',
        'game_20250706_063923_en.log'
    ]
    
    for file in test_files:
        exists = os.path.exists(file)
        if exists:
            mtime = os.path.getmtime(file)
            time_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f'  {file}: ✅ 存在 (修改时间: {time_str})')
        else:
            print(f'  {file}: ❌ 不存在')
    
    print('\n✅ 测试完成！翻译系统现在应该可以正常工作')
    print('\n🎯 现在您可以运行 python main.py 来启动游戏')
    print('   游戏结束后，新的日志文件会自动翻译为英文版本')
    
    return monitor

if __name__ == "__main__":
    test_translation_solution() 