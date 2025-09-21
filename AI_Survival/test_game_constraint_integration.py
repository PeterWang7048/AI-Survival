#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试游戏中的约束感知BMP集成
验证实际游戏运行中约束过滤日志是否消失
"""

import subprocess
import time
import os
import sys
from datetime import datetime


def run_game_test():
    """运行游戏测试"""
    print("🎮 启动游戏测试约束感知BMP集成...")
    print("=" * 50)
    
    # 准备启动参数 - 运行较短时间以快速验证
    test_duration = 30  # 秒
    
    print(f"⏱️ 将运行游戏 {test_duration} 秒以验证约束感知集成")
    print("📋 监控指标:")
    print("   • 不应出现: '🚫 约束验证: 过滤了X个违反约束的规律'")
    print("   • 应该出现: '✅ 约束符合率: 100%'")
    print("   • 应该出现: '🚀 效率提升: X%'")
    print("\n⏳ 启动中...")
    
    try:
        # 创建日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"constraint_test_{timestamp}.log"
        
        # 准备启动命令（使用auto_run_game.py进行快速测试）
        if os.path.exists("quick_game_test.py"):
            cmd = [sys.executable, "quick_game_test.py"]
        elif os.path.exists("auto_run_game.py"):
            cmd = [sys.executable, "auto_run_game.py", "--rounds", "5"]
        else:
            cmd = [sys.executable, "main.py"]
        
        # 启动游戏进程
        print(f"🚀 执行: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            universal_newlines=True
        )
        
        # 收集日志并分析
        logs = []
        constraint_violations_found = 0
        constraint_compliance_found = 0
        efficiency_improvements_found = 0
        
        # 读取输出
        start_time = time.time()
        while time.time() - start_time < test_duration:
            try:
                line = process.stdout.readline()
                if line:
                    logs.append(line.strip())
                    print(line.strip())  # 实时显示
                    
                    # 分析关键指标
                    if "🚫 约束验证: 过滤了" in line:
                        constraint_violations_found += 1
                        print(f"❌ 发现约束过滤日志! (第{constraint_violations_found}次)")
                    
                    if "约束符合率: 100%" in line:
                        constraint_compliance_found += 1
                        print(f"✅ 发现约束符合率日志! (第{constraint_compliance_found}次)")
                    
                    if "效率提升:" in line:
                        efficiency_improvements_found += 1
                        print(f"🚀 发现效率提升日志! (第{efficiency_improvements_found}次)")
                
                # 检查进程是否结束
                if process.poll() is not None:
                    break
                    
            except Exception as e:
                print(f"⚠️ 读取日志时出错: {str(e)}")
                break
        
        # 终止进程
        if process.poll() is None:
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
        
        # 保存完整日志
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(logs))
        
        # 分析结果
        print("\n" + "=" * 50)
        print("📊 约束感知BMP集成测试结果")
        print("=" * 50)
        
        print(f"⏱️ 测试时长: {test_duration}秒")
        print(f"📄 日志行数: {len(logs)}")
        print(f"💾 日志文件: {log_file}")
        
        print(f"\n🎯 关键指标:")
        print(f"   ❌ 约束过滤日志: {constraint_violations_found}次")
        print(f"   ✅ 约束符合率日志: {constraint_compliance_found}次")
        print(f"   🚀 效率提升日志: {efficiency_improvements_found}次")
        
        # 判断测试结果
        if constraint_violations_found == 0:
            print(f"\n🎉 成功！没有发现约束过滤日志")
            if constraint_compliance_found > 0:
                print(f"✅ 约束感知系统正常工作")
            success = True
        else:
            print(f"\n❌ 失败！仍然存在约束过滤日志")
            success = False
            
        if efficiency_improvements_found > 0:
            print(f"🚀 效率提升功能正常")
        
        return success, {
            'violations': constraint_violations_found,
            'compliance': constraint_compliance_found,
            'efficiency': efficiency_improvements_found,
            'log_file': log_file
        }
        
    except Exception as e:
        print(f"❌ 游戏测试失败: {str(e)}")
        return False, {'error': str(e)}


def main():
    """主函数"""
    print("🧪 约束感知BMP集成游戏测试")
    print("验证实际游戏中是否消除约束过滤日志")
    print()
    
    success, results = run_game_test()
    
    if success:
        print("\n🎉 约束感知BMP集成测试成功！")
        print("游戏中已不再出现约束过滤日志。")
        if results.get('compliance', 0) > 0:
            print("约束感知系统正常运行。")
    else:
        print("\n⚠️ 约束感知BMP集成测试未完全成功")
        if 'error' in results:
            print(f"错误: {results['error']}")
        else:
            print("请检查是否还有未替换的过滤逻辑。")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
