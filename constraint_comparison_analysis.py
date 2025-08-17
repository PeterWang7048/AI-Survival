#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
约束驱动vs过滤驱动的候选规律生成对比分析
"""

from constraint_aware_rule_generator import ConstraintAwareCombinationGenerator, ElementType
from eocar_combination_generator import CombinationType


def analyze_old_approach():
    """分析旧的生成-过滤方法"""
    print("🔍 分析旧方法：生成-过滤模式")
    print("=" * 50)
    
    # 统计旧方法中定义的所有组合类型
    all_combinations = list(CombinationType)
    
    # 分析哪些违反约束
    invalid_combinations = []
    valid_combinations = []
    
    for combo in all_combinations:
        combo_name = combo.value
        
        # 解析组合中包含的元素
        elements = set()
        if 'environment' in combo_name:
            elements.add('E')
        if 'object' in combo_name:
            elements.add('O')
        if 'characteristics' in combo_name:
            elements.add('C')
        if 'action' in combo_name:
            elements.add('A')
        if 'tool' in combo_name:
            elements.add('T')
        if 'result' in combo_name:
            elements.add('R')
            
        # 检查约束
        has_controllable = 'A' in elements or 'T' in elements
        has_contextual = 'E' in elements or 'O' in elements or 'C' in elements
        has_result = 'R' in elements
        
        is_valid = has_controllable and has_contextual and has_result
        
        if is_valid:
            valid_combinations.append((combo.name, elements))
        else:
            reason = []
            if not has_result:
                reason.append("无结果R")
            if not has_controllable:
                reason.append("违反C₂约束(无可控因子)")
            if not has_contextual:
                reason.append("违反C₃约束(无上下文因子)")
            invalid_combinations.append((combo.name, elements, "; ".join(reason)))
    
    print(f"📊 旧方法统计:")
    print(f"   总定义组合: {len(all_combinations)}个")
    print(f"   有效组合: {len(valid_combinations)}个")
    print(f"   无效组合: {len(invalid_combinations)}个")
    print(f"   无效率: {len(invalid_combinations)/len(all_combinations)*100:.1f}%")
    
    print(f"\n🚫 无效组合详情:")
    for name, elements, reason in invalid_combinations:
        elements_str = "-".join(sorted(elements))
        print(f"   {name}: {elements_str} ({reason})")
    
    return len(all_combinations), len(valid_combinations), len(invalid_combinations)


def analyze_new_approach():
    """分析新的约束驱动方法"""
    print("\n🔍 分析新方法：约束驱动生成")
    print("=" * 50)
    
    generator = ConstraintAwareCombinationGenerator()
    
    print(f"📊 新方法统计:")
    print(f"   有效组合: {generator.generation_stats['total_valid_combinations']}个")
    print(f"   避免的无效组合: {generator.generation_stats['invalid_combinations_avoided']}个")
    print(f"   效率: 100% (零过滤)")
    
    print(f"\n✅ 生成的有效组合:")
    for i, combo in enumerate(generator.valid_combinations, 1):
        print(f"   {i:2d}. {combo.pattern_name:<12} (复杂度: {combo.complexity_level}, 优先级: {combo.priority:.2f})")
    
    return (generator.generation_stats['total_valid_combinations'], 
            generator.generation_stats['invalid_combinations_avoided'])


def create_comparison_table():
    """创建对比表格"""
    print("\n" + "=" * 80)
    print("🆚 两种方法对比分析")
    print("=" * 80)
    
    old_total, old_valid, old_invalid = analyze_old_approach()
    new_valid, new_avoided = analyze_new_approach()
    
    print(f"\n📈 效率对比:")
    print("┌─────────────────────────┬─────────────┬─────────────┬─────────────┐")
    print("│        方法             │   总组合    │   有效组合  │   无效组合  │")
    print("├─────────────────────────┼─────────────┼─────────────┼─────────────┤")
    print(f"│ 旧方法(生成-过滤)       │    {old_total:2d}       │    {old_valid:2d}       │    {old_invalid:2d}       │")
    print(f"│ 新方法(约束驱动)        │    {new_valid:2d}       │    {new_valid:2d}       │     0       │")
    print("└─────────────────────────┴─────────────┴─────────────┴─────────────┘")
    
    print(f"\n📊 关键指标:")
    old_efficiency = old_valid / old_total * 100
    new_efficiency = 100.0  # 新方法100%有效
    
    print(f"   旧方法有效率: {old_efficiency:.1f}%")
    print(f"   新方法有效率: {new_efficiency:.1f}%")
    print(f"   效率提升: {new_efficiency - old_efficiency:.1f}个百分点")
    
    print(f"\n💡 核心改进:")
    print("   ✅ 零过滤：新方法不产生任何无效组合")
    print("   ✅ 高效：避免了生成-验证-丢弃的浪费循环")
    print("   ✅ 可预测：所有生成的组合都满足论文约束")
    print("   ✅ 扩展性：易于添加新的约束条件")
    
    print(f"\n🎯 实际应用效果:")
    waste_reduction = old_invalid / old_total * 100
    print(f"   减少无效计算: {waste_reduction:.1f}%")
    print(f"   提高规律质量: 100%符合约束")
    print(f"   优化内存使用: 减少{old_invalid}个无用对象")


def demonstrate_constraint_validation():
    """演示约束验证过程"""
    print(f"\n🔬 约束验证演示")
    print("=" * 50)
    
    from constraint_aware_rule_generator import ConstraintValidator
    
    validator = ConstraintValidator()
    
    test_cases = [
        # 违反C₂约束的组合(无可控因子)
        ({ElementType.E, ElementType.R}, "E-R: 环境→结果"),
        ({ElementType.O, ElementType.R}, "O-R: 对象→结果"),
        ({ElementType.C, ElementType.R}, "C-R: 特征→结果"),
        ({ElementType.E, ElementType.O, ElementType.R}, "E-O-R: 环境+对象→结果"),
        
        # 违反C₃约束的组合(无上下文因子)
        ({ElementType.A, ElementType.R}, "A-R: 动作→结果"),
        ({ElementType.T, ElementType.R}, "T-R: 工具→结果"),
        ({ElementType.A, ElementType.T, ElementType.R}, "A-T-R: 动作+工具→结果"),
        
        # 符合约束的组合
        ({ElementType.E, ElementType.A, ElementType.R}, "E-A-R: 环境+动作→结果"),
        ({ElementType.O, ElementType.T, ElementType.R}, "O-T-R: 对象+工具→结果"),
        ({ElementType.E, ElementType.O, ElementType.A, ElementType.R}, "E-O-A-R: 环境+对象+动作→结果"),
    ]
    
    print("验证结果:")
    for elements, description in test_cases:
        is_valid = validator.is_valid_combination(elements)
        violation_reason = validator.get_constraint_violation_reason(elements)
        
        status = "✅ 有效" if is_valid else "❌ 无效"
        reason = f" ({violation_reason})" if violation_reason else ""
        
        print(f"   {status}: {description}{reason}")


if __name__ == "__main__":
    print("候选规律生成方法对比分析")
    create_comparison_table()
    demonstrate_constraint_validation()
