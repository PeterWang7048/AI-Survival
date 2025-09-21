#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动运行游戏模拟的脚本
通过临时修改main.py来自动开始游戏
"""

import shutil
import os
import subprocess
import sys
import glob
import time

def backup_main_py():
    """备份原始main.py文件"""
    if os.path.exists("main.py.bak"):
        print("备份文件已存在，跳过备份")
    else:
        shutil.copy("main.py", "main.py.bak")
        print("已备份main.py为main.py.bak")

def restore_main_py():
    """恢复原始main.py文件"""
    if os.path.exists("main.py.bak"):
        shutil.copy("main.py.bak", "main.py")
        print("已恢复main.py")
    else:
        print("未找到备份文件，无法恢复")

def modify_main_py():
    """修改main.py文件，添加自动开始游戏的代码"""
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 在文件末尾的mainloop调用之前添加自动开始游戏的代码
    if "root.mainloop()" in content:
        new_content = content.replace(
            "root.mainloop()",
            "# 自动开始游戏\n    root.after(1000, app.start_game)\n    root.mainloop()"
        )
        
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("成功修改main.py，添加了自动开始游戏的代码")
    else:
        print("未找到合适的位置添加自动开始代码")
        return False
    
    return True

def get_latest_log_file():
    """获取最新的日志文件"""
    log_files = glob.glob("game_*.log")
    if not log_files:
        return None
    
    # 按修改时间排序，获取最新的日志文件
    latest_log = max(log_files, key=os.path.getmtime)
    return latest_log

def run_game():
    """运行修改后的游戏"""
    # 使用subprocess运行游戏
    print("开始运行游戏...")
    process = subprocess.Popen([sys.executable, "main.py"])
    
    # 等待游戏运行一段时间，确保模拟完成
    # 这个时间需要足够长，以确保游戏模拟能完成
    try:
        process.wait(timeout=300)  # 等待最多300秒
        print("游戏已完成运行")
    except subprocess.TimeoutExpired:
        print("游戏运行超时，强制终止")
        process.terminate()

def main():
    # 1. 备份原始main.py
    backup_main_py()
    
    try:
        # 2. 修改main.py
        if modify_main_py():
            # 记录运行前最新的日志文件
            old_log = get_latest_log_file()
            
            # 3. 运行游戏
            run_game()
            
            # 4. 获取最新的日志文件
            new_log = get_latest_log_file()
            
            # 检查是否生成了新的日志
            if new_log and (old_log != new_log):
                print(f"成功生成新的日志文件: {new_log}")
            else:
                print("可能没有生成新的日志文件")
        
    finally:
        # 5. 恢复原始main.py
        restore_main_py()

if __name__ == "__main__":
    main() 