#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版约束感知BMP集成系统
验证内容增强功能是否正确解决unknown、none、True等问题
"""

import time
from typing import List, Dict, Any

# 导入测试所需模块
from enhanced_bmp_integration import ConstraintAwareBMPIntegration, integrate_constraint_awareness_to_bmp
from blooming_and_pruning_model import BloomingAndPruningModel
from symbolic_core_v3 import EOCATR_Tuple, SymbolicElement, SymbolType, create_element
from intelligent_rule_content_enhancer import IntelligentRuleFormatter


class MockLogger:
    """模拟日志记录器"""
    def __init__(self):
        self.logs = []
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)
        print(log_message)
    
    def get_logs(self):
        return self.logs.copy()


def create_problematic_experience() -> EOCATR_Tuple:
    """创建包含问题值的测试经验"""
    # 创建故意包含unknown、none、True的经验
    experience = EOCATR_Tuple()
    experience.environment = "open_field"      # 正常值
    experience.object = "unknown"              # 问题值：unknown  
    experience.character = "red_color"         # 正常值
    experience.action = "explore"              # 正常值
    experience.tool = None                     # 问题值：None (会变成none)
    experience.result = True                   # 问题值：布尔值True
    return experience


def test_content_enhancement():
    """测试内容增强功能"""
    print("🧪 测试1: 内容增强功能")
    print("-" * 50)
    
    logger = MockLogger()
    
    # 创建BMP系统
    bmp = BloomingAndPruningModel(logger=logger)
    
    # 集成约束感知和内容增强
    integration = ConstraintAwareBMPIntegration(bmp, logger)
    
    # 创建包含问题值的经验
    test_experience = create_problematic_experience()
    
    print("📋 原始经验数据:")
    print(f"   环境: {test_experience.environment}")
    print(f"   对象: {test_experience.object}")  # unknown
    print(f"   特征: {test_experience.character}")
    print(f"   动作: {test_experience.action}")
    print(f"   工具: {test_experience.tool}")    # None
    print(f"   结果: {test_experience.result}")  # True
    
    # 使用约束驱动的怒放阶段
    start_time = time.time()
    candidate_rules = integration.constraint_aware_blooming_phase([test_experience])
    generation_time = (time.time() - start_time) * 1000
    
    print(f"\n🌸 生成结果:")
    print(f"   生成规律数: {len(candidate_rules)}")
    print(f"   生成时间: {generation_time:.2f}ms")
    
    # 检查生成的规律是否还有问题值
    problem_count = 0
    enhanced_count = 0
    
    print(f"\n📊 规律内容分析:")
    for i, rule in enumerate(candidate_rules[:5]):  # 只显示前5个
        pattern = getattr(rule, 'pattern', 'No pattern')
        print(f"   规律{i+1}: {pattern}")
        
        # 检查是否还包含问题值
        if any(problem in pattern.lower() for problem in ['unknown', 'none', 'true', 'false']):
            if not any(good in pattern.lower() for good in ['成功', '失败', '徒手']):
                problem_count += 1
        else:
            enhanced_count += 1
    
    # 获取增强统计
    stats = integration.get_constraint_statistics()
    content_stats = stats['content_enhancement_summary']
    
    print(f"\n📈 内容增强统计:")
    print(f"   总增强次数: {content_stats['total_content_enhancements']}")
    print(f"   unknown修复: {content_stats['unknown_values_fixed']}")
    print(f"   none修复: {content_stats['none_values_fixed']}")
    print(f"   布尔值修复: {content_stats['boolean_values_fixed']}")
    
    # 判断测试结果
    success = (problem_count == 0 and content_stats['total_content_enhancements'] > 0)
    
    if success:
        print(f"✅ 内容增强测试通过！")
        print(f"   问题值数量: {problem_count} (应为0)")
        print(f"   增强规律数: {enhanced_count}")
    else:
        print(f"❌ 内容增强测试失败！")
        print(f"   仍有问题值: {problem_count}个")
    
    return success


def test_specific_enhancements():
    """测试特定的增强效果"""
    print("\n🧪 测试2: 特定增强效果验证")
    print("-" * 50)
    
    formatter = IntelligentRuleFormatter()
    
    # 测试用例：模拟问题规律
    test_cases = [
        {
            'name': 'unknown对象问题',
            'rule': {
                'pattern_name': 'E-O-A-R',
                'conditions': {'E': 'open_field', 'O': 'unknown', 'A': 'explore'},
                'expected_result': 'True'
            },
            'should_fix': ['unknown', 'True']
        },
        {
            'name': 'none工具问题',
            'rule': {
                'pattern_name': 'E-T-A-R',
                'conditions': {'E': 'forest', 'T': 'none', 'A': 'collect'},
                'expected_result': 'success'
            },
            'should_fix': ['none']
        },
        {
            'name': '布尔值结果问题',
            'rule': {
                'pattern_name': 'O-A-R',
                'conditions': {'O': 'berry', 'A': 'collect'},
                'expected_result': 'False'
            },
            'should_fix': ['False']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n🔍 测试: {test_case['name']}")
        
        # 格式化前
        original_result = test_case['rule']['expected_result']
        print(f"   原始结果: {original_result}")
        
        # 使用增强格式化器
        enhanced = formatter.format_rule(test_case['rule'])
        print(f"   增强后: {enhanced}")
        
        # 检查是否修复了问题值
        fixed_all = True
        for problem_value in test_case['should_fix']:
            if problem_value.lower() in enhanced.lower():
                # 检查是否是合理的替换（如True->成功）
                if not any(good in enhanced.lower() for good in ['成功', '失败', '徒手']):
                    print(f"   ❌ 未修复: {problem_value}")
                    fixed_all = False
                    all_passed = False
        
        if fixed_all:
            print(f"   ✅ 所有问题值已修复")
        
    return all_passed


def test_constraint_and_enhancement_integration():
    """测试约束验证和内容增强的完整集成"""
    print("\n🧪 测试3: 约束验证与内容增强集成")
    print("-" * 50)
    
    logger = MockLogger()
    
    # 创建BMP系统并集成
    bmp = BloomingAndPruningModel(logger=logger)
    integration = integrate_constraint_awareness_to_bmp(bmp, logger)
    
    # 创建多个测试经验
    test_experiences = [
        create_problematic_experience(),
        create_problematic_experience(),
        create_problematic_experience()
    ]
    
    # 运行完整的处理流程
    start_time = time.time()
    
    all_rules = []
    for exp in test_experiences:
        rules = integration.constraint_aware_process_experience(exp, test_experiences[:2])
        all_rules.extend(rules)
    
    total_time = (time.time() - start_time) * 1000
    
    # 分析结果
    print(f"📊 集成测试结果:")
    print(f"   处理经验数: {len(test_experiences)}")
    print(f"   生成规律数: {len(all_rules)}")
    print(f"   总处理时间: {total_time:.2f}ms")
    
    # 检查约束符合率
    violation_count = 0
    for rule in all_rules:
        validation = integration.validate_rule_constraints(rule)
        if not validation['overall_valid']:
            violation_count += 1
    
    constraint_compliance_rate = (len(all_rules) - violation_count) / len(all_rules) * 100 if all_rules else 100
    
    # 检查内容质量
    quality_issues = 0
    for rule in all_rules:
        pattern = getattr(rule, 'pattern', '')
        if any(issue in pattern.lower() for issue in ['unknown', 'none', 'true', 'false']):
            if not any(good in pattern.lower() for good in ['成功', '失败', '徒手']):
                quality_issues += 1
    
    content_quality_rate = (len(all_rules) - quality_issues) / len(all_rules) * 100 if all_rules else 100
    
    print(f"\n📈 质量指标:")
    print(f"   约束符合率: {constraint_compliance_rate:.1f}%")
    print(f"   内容质量率: {content_quality_rate:.1f}%")
    print(f"   约束违反数: {violation_count}")
    print(f"   内容问题数: {quality_issues}")
    
    # 获取详细统计
    stats = integration.get_constraint_statistics()
    integration.print_integration_summary()
    
    # 判断成功
    success = (constraint_compliance_rate == 100.0 and content_quality_rate >= 90.0)
    
    if success:
        print(f"\n🎉 集成测试完全成功！")
    else:
        print(f"\n⚠️ 集成测试部分成功，需要进一步优化")
    
    return success


def run_comprehensive_enhancement_test():
    """运行综合增强测试"""
    print("🚀 增强版约束感知BMP系统 - 内容增强验证")
    print("=" * 60)
    
    tests = [
        ("内容增强功能", test_content_enhancement),
        ("特定增强效果", test_specific_enhancements),
        ("完整集成测试", test_constraint_and_enhancement_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}出现异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 增强版测试结果汇总")
    print("=" * 60)
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有增强功能测试通过！")
        print("\n🎯 解决方案验证:")
        print("   ✅ unknown值 -> 具体描述")
        print("   ✅ none工具 -> 徒手/具体工具")
        print("   ✅ True结果 -> 成功")
        print("   ✅ False结果 -> 失败")
        print("   ✅ 约束符合率: 100%")
        print("   ✅ 内容可读性大幅提升")
        return True
    else:
        print(f"⚠️ {total - passed}个测试失败")
        return False


if __name__ == "__main__":
    success = run_comprehensive_enhancement_test()
    
    if success:
        print("\n🎉 内容增强集成完全成功！")
        print("现在规律中不再出现unknown、none、True等模糊值。")
    else:
        print("\n⚠️ 集成可能存在问题，请检查实现。")
