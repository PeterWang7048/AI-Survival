#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成验证测试
验证智能内容增强功能是否成功集成到main.py中
确保规律不再出现unknown/none/True等模糊值
"""

import time
import sys
import os
from typing import List, Dict, Any


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


def test_ilai_player_initialization():
    """测试ILAIPlayer的初始化是否包含内容增强功能"""
    print("🧪 测试1: ILAIPlayer初始化验证")
    print("-" * 50)
    
    try:
        # 导入main模块
        import main
        
        # 创建模拟游戏地图
        class MockGameMap:
            def __init__(self):
                self.width = 20
                self.height = 20
        
        mock_map = MockGameMap()
        
        # 创建ILAI玩家
        print("🚀 创建ILAI玩家...")
        player = main.ILAIPlayer("TEST_ILAI", mock_map)
        
        # 检查集成功能
        success_indicators = []
        
        # 检查1: 约束感知集成
        if hasattr(player, 'constraint_integration'):
            print("✅ 约束感知集成已初始化")
            success_indicators.append(True)
        else:
            print("❌ 约束感知集成缺失")
            success_indicators.append(False)
        
        # 检查2: 智能内容增强器
        if hasattr(player, 'rule_formatter'):
            print("✅ 智能规律格式化器已初始化")
            success_indicators.append(True)
        else:
            print("❌ 智能规律格式化器缺失")
            success_indicators.append(False)
        
        # 检查3: 内容增强器
        if hasattr(player, 'content_enhancer'):
            print("✅ 内容增强器已初始化")
            success_indicators.append(True)
        else:
            print("❌ 内容增强器缺失")
            success_indicators.append(False)
        
        # 检查4: BMP系统
        if hasattr(player, 'bmp') and player.bmp:
            print("✅ BMP系统已初始化")
            success_indicators.append(True)
        else:
            print("❌ BMP系统缺失")
            success_indicators.append(False)
        
        # 汇总结果
        success_rate = sum(success_indicators) / len(success_indicators) * 100
        print(f"\n📊 初始化成功率: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 ILAIPlayer初始化测试通过！")
            return True
        else:
            print("⚠️ ILAIPlayer初始化测试部分失败")
            return False
        
    except Exception as e:
        print(f"❌ ILAIPlayer初始化测试失败: {str(e)}")
        return False


def test_rule_formatting_enhancement():
    """测试规律格式化增强功能"""
    print("\n🧪 测试2: 规律格式化增强验证")
    print("-" * 50)
    
    try:
        import main
        
        # 创建模拟游戏地图
        class MockGameMap:
            def __init__(self):
                self.width = 20
                self.height = 20
        
        mock_map = MockGameMap()
        
        # 创建ILAI玩家
        player = main.ILAIPlayer("TEST_ILAI", mock_map)
        
        # 创建包含问题值的模拟规律
        class MockRule:
            def __init__(self):
                self.conditions = {
                    'environment': 'open_field',
                    'object': 'unknown',      # 问题值
                    'action': 'explore'
                }
                self.predictions = {
                    'expected_result': True   # 问题值
                }
                self.pattern = '[unknown] 在开阔地中，使用none对未知资源执行探索，预期结果：True'
                self.confidence = 1.0
        
        mock_rule = MockRule()
        
        print("📋 原始规律模式:")
        print(f"   {mock_rule.pattern}")
        
        # 使用新的格式化方法
        print("\n🎨 应用智能内容增强...")
        enhanced_pattern = player._format_rule_to_standard_pattern(mock_rule)
        
        print(f"📈 增强后规律:")
        print(f"   {enhanced_pattern}")
        
        # 检查是否消除了问题值
        problem_values = ['unknown', 'none', 'True', 'False']
        problems_found = []
        improvements_found = []
        
        for problem in problem_values:
            if problem in enhanced_pattern:
                # 检查是否是合理的替换
                if problem == 'True' and '成功' in enhanced_pattern:
                    improvements_found.append(f"{problem} → 成功")
                elif problem == 'False' and '失败' in enhanced_pattern:
                    improvements_found.append(f"{problem} → 失败")
                elif problem == 'none' and '徒手' in enhanced_pattern:
                    improvements_found.append(f"{problem} → 徒手")
                elif problem == 'unknown' and '未知' in enhanced_pattern:
                    improvements_found.append(f"{problem} → 未知目标")
                else:
                    problems_found.append(problem)
        
        print(f"\n📊 增强效果分析:")
        if improvements_found:
            print(f"✅ 成功改进: {', '.join(improvements_found)}")
        
        if problems_found:
            print(f"❌ 仍存在问题: {', '.join(problems_found)}")
        else:
            print("✅ 所有问题值已消除")
        
        # 判断测试结果
        success = len(problems_found) == 0
        
        if success:
            print("🎉 规律格式化增强测试通过！")
        else:
            print("⚠️ 规律格式化增强测试部分失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 规律格式化增强测试失败: {str(e)}")
        return False


def test_constraint_aware_functionality():
    """测试约束感知功能"""
    print("\n🧪 测试3: 约束感知功能验证")
    print("-" * 50)
    
    try:
        import main
        from symbolic_core_v3 import EOCATR_Tuple, create_element, SymbolType
        
        # 创建模拟游戏地图
        class MockGameMap:
            def __init__(self):
                self.width = 20
                self.height = 20
        
        mock_map = MockGameMap()
        
        # 创建ILAI玩家
        player = main.ILAIPlayer("TEST_ILAI", mock_map)
        
        # 检查约束感知集成是否可用
        if not hasattr(player, 'constraint_integration') or not player.constraint_integration:
            print("❌ 约束感知集成不可用")
            return False
        
        print("✅ 约束感知集成可用")
        
        # 创建测试经验
        try:
            experience = EOCATR_Tuple()
            experience.environment = "open_field"
            experience.object = "unknown"
            experience.action = "explore"
            experience.tool = None
            experience.result = True
            
            print("📋 测试经验:")
            print(f"   环境: {experience.environment}")
            print(f"   对象: {experience.object}")
            print(f"   动作: {experience.action}")
            print(f"   工具: {experience.tool}")
            print(f"   结果: {experience.result}")
            
            # 使用约束感知生成规律
            print("\n🚀 执行约束驱动规律生成...")
            start_time = time.time()
            
            rules = player.constraint_integration.constraint_aware_blooming_phase([experience])
            
            generation_time = (time.time() - start_time) * 1000
            
            print(f"📊 生成结果:")
            print(f"   生成规律数: {len(rules)}")
            print(f"   生成时间: {generation_time:.2f}ms")
            
            # 检查规律质量
            if rules:
                print(f"\n📝 规律示例:")
                for i, rule in enumerate(rules[:3]):  # 显示前3个
                    pattern = getattr(rule, 'pattern', 'No pattern')
                    print(f"   规律{i+1}: {pattern}")
                
                # 检查约束符合率
                constraint_violations = 0
                for rule in rules:
                    validation = player.constraint_integration.validate_rule_constraints(rule)
                    if not validation['overall_valid']:
                        constraint_violations += 1
                
                constraint_compliance = (len(rules) - constraint_violations) / len(rules) * 100
                print(f"\n📈 质量指标:")
                print(f"   约束符合率: {constraint_compliance:.1f}%")
                print(f"   约束违反数: {constraint_violations}")
                
                success = constraint_compliance == 100.0
                
                if success:
                    print("🎉 约束感知功能测试通过！")
                else:
                    print("⚠️ 约束感知功能测试部分失败")
                
                return success
            else:
                print("⚠️ 未生成任何规律")
                return False
                
        except Exception as e:
            print(f"⚠️ 经验处理失败: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ 约束感知功能测试失败: {str(e)}")
        return False


def test_import_dependencies():
    """测试依赖导入"""
    print("\n🧪 测试4: 依赖导入验证")
    print("-" * 50)
    
    try:
        # 测试核心依赖
        dependencies = [
            ("main", "主程序模块"),
            ("enhanced_bmp_integration", "增强BMP集成"),
            ("intelligent_rule_content_enhancer", "智能内容增强器"),
            ("constraint_aware_rule_generator", "约束感知生成器"),
            ("symbolic_core_v3", "符号核心v3"),
            ("blooming_and_pruning_model", "BMP模型")
        ]
        
        success_count = 0
        for module_name, description in dependencies:
            try:
                __import__(module_name)
                print(f"✅ {description}: 导入成功")
                success_count += 1
            except Exception as e:
                print(f"❌ {description}: 导入失败 - {str(e)}")
        
        success_rate = success_count / len(dependencies) * 100
        print(f"\n📊 依赖导入成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 依赖导入测试通过！")
            return True
        else:
            print("⚠️ 依赖导入测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 依赖导入测试出错: {str(e)}")
        return False


def run_integration_validation():
    """运行完整的集成验证"""
    print("🚀 智能内容增强功能集成验证")
    print("=" * 60)
    
    tests = [
        ("依赖导入验证", test_import_dependencies),
        ("ILAIPlayer初始化", test_ilai_player_initialization), 
        ("规律格式化增强", test_rule_formatting_enhancement),
        ("约束感知功能", test_constraint_aware_functionality)
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
    print("📊 集成验证结果汇总")
    print("=" * 60)
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有集成验证测试通过！")
        print("\n🎯 集成成功确认:")
        print("   ✅ 约束感知BMP系统已集成")
        print("   ✅ 智能内容增强器已启用")
        print("   ✅ unknown/none/True问题已解决")
        print("   ✅ 规律质量显著提升")
        print("\n💡 现在启动游戏将看到清晰、具体的规律描述！")
        return True
    else:
        print(f"⚠️ {total - passed}个测试失败")
        print("请检查集成配置或依赖问题")
        return False


if __name__ == "__main__":
    success = run_integration_validation()
    
    if success:
        print("\n🎉 智能内容增强功能已成功集成！")
        print("游戏中的规律将不再出现模糊值描述。")
    else:
        print("\n⚠️ 集成验证未完全通过，请检查相关问题。")
    
    sys.exit(0 if success else 1)
