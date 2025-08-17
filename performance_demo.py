#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算力开销和反应时间统计系统演示
Performance Tracking System Demo

演示如何使用性能统计系统来监控AI智能体的算力消耗和反应时间
"""

import time
import random
import threading
from user_performance_tracker import (
    UserPerformanceTracker,
    get_performance_tracker,
    start_operation_tracking,
    end_operation_tracking,
    track_performance,
    generate_all_reports,
    export_all_data
)

def simulate_ai_decision_making(user_id: str, complexity: int = 1):
    """模拟AI决策过程"""
    
    # 开始性能追踪
    start_operation_tracking(user_id, "decision_making", complexity)
    
    # 模拟决策计算时间
    decision_time = random.uniform(0.1, 2.0) * complexity
    time.sleep(decision_time)
    
    # 模拟决策结果
    actions = ["explore", "collect", "attack", "flee", "rest"]
    chosen_action = random.choice(actions)
    
    # 模拟成功率
    success = random.random() > 0.1  # 90%成功率
    
    # 结束性能追踪
    if success:
        end_operation_tracking(user_id, success=True, result_data={
            'chosen_action': chosen_action,
            'decision_confidence': random.uniform(0.5, 1.0)
        })
    else:
        end_operation_tracking(user_id, success=False, error="决策超时或失败")
    
    return chosen_action if success else None

def simulate_learning_process(user_id: str):
    """模拟学习过程"""
    
    start_operation_tracking(user_id, "learning", complexity=3)
    
    # 模拟学习时间
    learning_time = random.uniform(0.5, 3.0)
    time.sleep(learning_time)
    
    # 模拟学习结果
    rules_learned = random.randint(0, 5)
    
    end_operation_tracking(user_id, success=True, result_data={
        'rules_learned': rules_learned,
        'learning_efficiency': random.uniform(0.6, 1.0)
    })
    
    return rules_learned

def simulate_rule_generation(user_id: str):
    """模拟规律生成过程"""
    
    start_operation_tracking(user_id, "rule_generation", complexity=5)
    
    # 模拟BMP处理时间
    processing_time = random.uniform(1.0, 4.0)
    time.sleep(processing_time)
    
    # 模拟生成结果
    rules_generated = random.randint(1, 10)
    
    end_operation_tracking(user_id, success=True, result_data={
        'rules_generated': rules_generated,
        'generation_method': 'BMP_blooming'
    })
    
    return rules_generated

@track_performance("complex_reasoning", complexity=4, user_id="ILAI_Auto")
def simulate_complex_reasoning():
    """使用装饰器自动追踪的复杂推理过程"""
    
    # 模拟复杂推理
    reasoning_time = random.uniform(2.0, 5.0)
    time.sleep(reasoning_time)
    
    # 模拟可能的异常
    if random.random() < 0.05:  # 5%几率出错
        raise Exception("推理过程中出现错误")
    
    return {
        'reasoning_result': 'optimal_strategy',
        'confidence': random.uniform(0.7, 1.0)
    }

def run_multi_user_simulation():
    """运行多用户性能模拟"""
    
    print("🚀 开始多用户性能模拟...")
    
    # 创建多个AI用户
    users = ['ILAI_Alpha', 'ILAI_Beta', 'ILAI_Gamma', 'RILAI_Test', 'DQN_Agent']
    
    # 为每个用户模拟操作
    for user_id in users:
        print(f"\n👤 模拟用户: {user_id}")
        
        # 模拟多轮操作
        for round_num in range(1, 6):
            print(f"  回合 {round_num}:")
            
            # 决策制定
            action = simulate_ai_decision_making(user_id, complexity=random.randint(1, 3))
            print(f"    决策: {action}")
            
            # 学习过程 
            if round_num % 2 == 0:  # 每两轮学习一次
                rules = simulate_learning_process(user_id)
                print(f"    学习: {rules} 个新规律")
            
            # 规律生成
            if round_num % 3 == 0:  # 每三轮生成规律
                generated = simulate_rule_generation(user_id)
                print(f"    生成: {generated} 个候选规律")
            
            # 短暂间隔
            time.sleep(0.1)
    
    # 额外的复杂推理测试
    print("\n🧠 复杂推理测试:")
    for i in range(3):
        try:
            result = simulate_complex_reasoning()
            print(f"  推理 {i+1}: 成功 - {result['reasoning_result']}")
        except Exception as e:
            print(f"  推理 {i+1}: 失败 - {str(e)}")

def demonstrate_performance_analysis():
    """演示性能分析功能"""
    
    print("\n" + "="*60)
    print("📊 性能分析演示")
    print("="*60)
    
    # 获取所有用户的性能总结
    from user_performance_tracker import _performance_trackers
    
    if not _performance_trackers:
        print("⚠️ 没有性能数据可供分析")
        return
    
    print(f"\n📈 已监控 {len(_performance_trackers)} 个用户")
    
    for user_id, tracker in _performance_trackers.items():
        print(f"\n👤 {user_id} 性能总结:")
        summary = tracker.get_performance_summary()
        
        if "error" not in summary:
            print(f"   总操作数: {summary['total_operations']}")
            print(f"   平均响应时间: {summary['average_execution_time']:.3f} 秒")
            print(f"   效率评分: {summary['efficiency_score']:.1f}/10")
            print(f"   性能趋势: {summary['performance_trend']}")
            
            # 显示操作类型统计
            print("   操作类型分析:")
            for op_type, stats in summary['operation_statistics'].items():
                print(f"     {op_type}: {stats['count']}次, 平均{stats['avg_time']:.3f}秒")
            
            # 资源使用情况
            res_stats = summary['resource_statistics']
            print(f"   资源使用: 内存{res_stats['peak_memory_mb']:.1f}MB, CPU{res_stats['avg_cpu_percent']:.1f}%")
            
            # 性能警告
            warnings = summary['performance_warnings']
            if warnings:
                print("   ⚠️ 性能警告:")
                for warning in warnings:
                    print(f"     • {warning}")
            else:
                print("   ✅ 性能良好")

def demonstrate_report_generation():
    """演示报告生成功能"""
    
    print("\n" + "="*60)
    print("📄 报告生成演示")
    print("="*60)
    
    # 为所有用户生成详细报告
    reports = generate_all_reports()
    
    print(f"\n📋 已为 {len(reports)} 个用户生成详细报告")
    
    # 导出原始数据
    exported_files = export_all_data('json')
    
    print(f"\n💾 已导出 {len(exported_files)} 个数据文件:")
    for user_id, filename in exported_files.items():
        print(f"   {user_id}: {filename}")

def demonstrate_real_time_monitoring():
    """演示实时监控功能"""
    
    print("\n" + "="*60)
    print("⏱️ 实时监控演示")
    print("="*60)
    
    # 创建一个用户进行实时监控
    user_id = "RealTime_Test"
    tracker = get_performance_tracker(user_id)
    
    print(f"\n🎯 开始监控用户: {user_id}")
    
    # 模拟实时操作
    for i in range(5):
        print(f"\n⚡ 操作 {i+1}:")
        
        # 开始操作
        tracker.start_operation("real_time_decision", complexity=random.randint(1, 4))
        print("  📊 开始性能监控...")
        
        # 模拟操作时间
        operation_time = random.uniform(0.5, 2.0)
        print(f"  🔄 执行中... (预计 {operation_time:.1f}秒)")
        time.sleep(operation_time)
        
        # 结束操作
        metric = tracker.end_operation(success=random.random() > 0.1)
        
        print(f"  ✅ 操作完成: {metric.execution_time:.3f}秒")
        print(f"  💾 内存使用: {metric.memory_usage:.1f}MB")
        print(f"  🖥️ CPU使用: {metric.cpu_usage:.1f}%")
        
        # 显示当前统计
        summary = tracker.get_performance_summary()
        if "error" not in summary:
            print(f"  📈 当前效率评分: {summary['efficiency_score']:.1f}/10")

def main():
    """主演示函数"""
    
    print("🎮 AI生存竞赛 - 算力开销与反应时间统计系统演示")
    print("=" * 80)
    
    print("\n📋 演示内容:")
    print("1. 多用户性能模拟")
    print("2. 性能分析功能")
    print("3. 报告生成功能")
    print("4. 实时监控功能")
    
    input("\n按回车键开始演示...")
    
    # 1. 多用户性能模拟
    run_multi_user_simulation()
    
    # 2. 性能分析
    demonstrate_performance_analysis()
    
    # 3. 报告生成
    demonstrate_report_generation()
    
    # 4. 实时监控
    demonstrate_real_time_monitoring()
    
    print("\n" + "="*80)
    print("🎉 演示完成！")
    print("\n💡 使用建议:")
    print("1. 在实际游戏中，性能数据将自动收集")
    print("2. 可以随时调用 quick_performance_report() 查看性能")
    print("3. 定期导出数据用于深度分析")
    print("4. 根据性能报告优化AI算法和参数")
    
    print("\n📁 生成的文件:")
    print("- performance_report_*.txt: 详细性能报告")
    print("- performance_data_*.json: 原始性能数据") 
    print("- 可用于进一步分析和可视化")

if __name__ == "__main__":
    main() 