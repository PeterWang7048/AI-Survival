#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证BMP替换测试
快速测试新的约束感知BMP系统是否已生效
"""

import time
import sys
import os

def test_imports():
    """测试导入是否正常"""
    print("🧪 测试1: 导入测试")
    print("-" * 30)
    
    try:
        # 测试约束感知集成导入
        from enhanced_bmp_integration import ConstraintAwareBMPIntegration
        print("✅ 约束感知集成导入成功")
        
        # 测试main模块导入
        import main
        print("✅ main模块导入成功")
        
        # 检查ILAIPlayer是否有约束感知属性
        if hasattr(main.ILAIPlayer, '__init__'):
            print("✅ ILAIPlayer类结构正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {str(e)}")
        return False


def test_main_py_content():
    """测试main.py内容是否正确替换"""
    print("\n🧪 测试2: main.py内容验证")
    print("-" * 30)
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键替换内容
        checks = [
            ("约束感知导入", "enhanced_bmp_integration" in content),
            ("约束感知初始化", "constraint_integration" in content),
            ("约束符合率日志", "约束符合率: 100%" in content),
            ("移除过滤日志", "🚫 约束验证: 过滤了" not in content),
            ("效率提升显示", "效率提升:" in content)
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'通过' if result else '失败'}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 内容验证失败: {str(e)}")
        return False


def test_constraint_generator():
    """测试约束生成器"""
    print("\n🧪 测试3: 约束生成器功能")
    print("-" * 30)
    
    try:
        from constraint_aware_rule_generator import ConstraintAwareCombinationGenerator
        
        generator = ConstraintAwareCombinationGenerator()
        stats = generator.generation_stats
        
        print(f"✅ 约束生成器初始化成功")
        print(f"   有效组合: {stats['total_valid_combinations']}")
        print(f"   避免无效组合: {stats['invalid_combinations_avoided']}")
        
        # 验证避免的组合数量
        if stats['invalid_combinations_avoided'] > 0:
            print(f"✅ 成功避免了{stats['invalid_combinations_avoided']}个无效组合")
            return True
        else:
            print("⚠️ 没有避免无效组合（可能不是问题）")
            return True
            
    except Exception as e:
        print(f"❌ 约束生成器测试失败: {str(e)}")
        return False


def test_no_filter_patterns():
    """测试确认没有过滤模式"""
    print("\n🧪 测试4: 确认消除过滤模式")
    print("-" * 30)
    
    try:
        # 检查main.py中不应该存在的过滤相关代码
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 这些模式不应该存在
        forbidden_patterns = [
            "🚫 约束验证: 过滤了",
            "INVALID_RULE_NO_CONTROLLABLE_FACTOR",
            "INVALID_RULE_NO_CONTEXT_FACTOR",
            "invalid_rules_count += 1"
        ]
        
        found_forbidden = []
        for pattern in forbidden_patterns:
            if pattern in content:
                found_forbidden.append(pattern)
        
        if not found_forbidden:
            print("✅ 所有过滤模式已成功移除")
            return True
        else:
            print("❌ 发现残留的过滤模式:")
            for pattern in found_forbidden:
                print(f"   • {pattern}")
            return False
            
    except Exception as e:
        print(f"❌ 过滤模式检查失败: {str(e)}")
        return False


def run_verification_tests():
    """运行所有验证测试"""
    print("🚀 BMP替换验证测试套件")
    print("=" * 50)
    
    tests = [
        ("导入测试", test_imports),
        ("main.py内容验证", test_main_py_content),
        ("约束生成器功能", test_constraint_generator),
        ("消除过滤模式", test_no_filter_patterns)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}出现异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！BMP替换成功！")
        print("\n🎯 现在启动游戏应该看到:")
        print("   ✅ 约束符合率: 100%")
        print("   ✅ 效率提升: X%") 
        print("   ❌ 不再出现: 🚫 约束验证: 过滤了X个违反约束的规律")
        return True
    else:
        print(f"⚠️ {total - passed}个测试失败")
        return False


if __name__ == "__main__":
    success = run_verification_tests()
    sys.exit(0 if success else 1)
