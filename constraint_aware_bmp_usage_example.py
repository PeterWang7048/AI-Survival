#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
约束感知BMP系统使用示例
演示如何在现有代码中启用约束驱动的规律生成
"""

def example_usage_in_game():
    """在游戏中使用约束感知BMP的示例"""
    
    # 方法1: 自动集成（推荐）
    # 运行apply_constraint_awareness_patch.py后，所有新创建的ILAI/RILAI玩家
    # 将自动使用约束驱动的BMP系统
    
    # 方法2: 手动集成现有BMP实例
    from blooming_and_pruning_model import BloomingAndPruningModel
    from enhanced_bmp_integration import integrate_constraint_awareness_to_bmp
    
    # 现有BMP实例
    bmp = BloomingAndPruningModel()
    
    # 集成约束感知能力
    integration = integrate_constraint_awareness_to_bmp(bmp)
    
    # 现在bmp.blooming_phase将使用约束驱动生成
    # 不再产生违反C₂/C₃约束的规律
    
    print("BMP系统已升级为约束驱动模式")
    
    # 获取统计信息
    stats = integration.get_constraint_statistics()
    print(f"效率提升: {stats['efficiency_summary']['efficiency_improvement_percent']:.1f}%")


def example_check_constraint_compliance():
    """检查规律约束符合性的示例"""
    from enhanced_bmp_integration import ConstraintAwareBMPIntegration
    from blooming_and_pruning_model import BloomingAndPruningModel
    
    bmp = BloomingAndPruningModel()
    integration = ConstraintAwareBMPIntegration(bmp)
    
    # 检查某个规律是否符合约束
    # 假设有一个规律实例
    rule = ...  # 某个CandidateRule实例
    
    constraint_check = integration.validate_rule_constraints(rule)
    
    if constraint_check['overall_valid']:
        print("✅ 规律符合所有约束条件")
    else:
        print(f"❌ 规律违反约束: {constraint_check['violation_reason']}")


if __name__ == "__main__":
    print("约束感知BMP系统使用示例")
    example_usage_in_game()
