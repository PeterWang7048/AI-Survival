#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动启动游戏模拟的脚本
"""

import subprocess
import tkinter as tk
import time
import os
import sys
from threading import Thread

def find_button_and_click():
    """
    寻找并点击"开始游戏"按钮
    """
    # 给主程序一些时间加载界面
    time.sleep(5)
    
    # 尝试查找所有的Tkinter窗口
    root = None
    for widget in tk._default_root.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget('text') == "开始游戏":
            print("找到开始游戏按钮，点击...")
            widget.invoke()  # 模拟按钮点击
            return True
    
    # 如果没有找到特定的按钮，尝试点击第一个Button
    for widget in tk._default_root.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.Button):
                    print("找到第一个按钮，点击...")
                    child.invoke()  # 模拟按钮点击
                    return True
    
    print("没有找到任何按钮")
    return False

def main():
    """
    启动主游戏并自动点击开始按钮
    """
    # 启动主游戏
    print("启动游戏...")
    
    # 创建一个独立进程运行main.py
    process = subprocess.Popen([sys.executable, "main.py"])
    
    # 创建一个线程来执行按钮点击
    click_thread = Thread(target=find_button_and_click)
    click_thread.daemon = True
    click_thread.start()
    
    # 等待主程序完成
    process.wait()
    
    print("游戏模拟完成")

if __name__ == "__main__":
    main() 