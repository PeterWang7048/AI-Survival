#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试词典修复方案的可行性
Test Dictionary Fix Feasibility
"""

import os
import json
from log_translation_engine import LogTranslationEngine

def test_dictionary_fix():
    """测试词典修复方案"""
    print("🧪 测试词典修复方案")
    print("=" * 50)
    
    # 1. 创建翻译引擎
    print("\n1. 创建翻译引擎...")
    engine = LogTranslationEngine()
    
    # 2. 测试当前翻译效果
    print("\n2. 测试当前翻译效果:")
    test_line = "🌍 日志翻译系统已自动启动"
    current_result = engine.smart_translate_line(test_line)
    print(f"   原文: {test_line}")
    print(f"   现在: {current_result}")
    
    # 3. 检查词典中相关的条目
    print("\n3. 检查词典中相关的条目:")
    related_terms = []
    for chinese, english in engine.dictionary.complete_dictionary.items():
        if any(word in chinese for word in ["启动", "翻译", "系统", "日志", "自动"]):
            related_terms.append((chinese, english))
    
    print(f"   找到 {len(related_terms)} 个相关条目:")
    for chinese, english in related_terms[:10]:  # 显示前10个
        print(f"     \"{chinese}\" -> \"{english}\"")
    
    # 4. 模拟添加完整句子翻译
    print("\n4. 模拟添加完整句子翻译:")
    
    # 临时添加到词典中
    engine.dictionary.complete_dictionary["日志翻译系统已自动启动"] = "Log Translation System Started Automatically"
    
    # 重新测试
    new_result = engine.smart_translate_line(test_line)
    print(f"   添加后: {new_result}")
    
    # 5. 测试各种变体
    print("\n5. 测试各种变体:")
    
    test_cases = [
        "🌍 日志翻译系统已自动启动",
        "日志翻译系统已自动启动",
        "🌍 日志翻译系统已自动启动（测试）",
        "第1天: 日志翻译系统已自动启动",
    ]
    
    for test_case in test_cases:
        result = engine.smart_translate_line(test_case)
        success = "✅" if "Log Translation System Started Automatically" in result else "❌"
        print(f"   {success} \"{test_case}\" -> \"{result}\"")
    
    # 6. 分析翻译引擎的匹配过程
    print("\n6. 分析翻译引擎的匹配过程:")
    
    # 按长度排序的词典条目
    terms_by_length = sorted(engine.dictionary.complete_dictionary.items(), 
                            key=lambda x: len(x[0]), reverse=True)
    
    print("   按长度排序的前10个条目:")
    for i, (chinese, english) in enumerate(terms_by_length[:10]):
        print(f"     {i+1}. \"{chinese}\" ({len(chinese)}字符) -> \"{english}\"")
    
    # 7. 结论
    print("\n7. 结论:")
    if "Log Translation System Started Automatically" in new_result:
        print("   ✅ 方案1可行！添加完整句子翻译可以解决问题")
        print("   📝 建议将以下条目添加到词典中:")
        print("     \"日志翻译系统已自动启动\": \"Log Translation System Started Automatically\"")
    else:
        print("   ❌ 方案1可能有问题，需要进一步分析")
        print("   🔍 可能的原因:")
        print("     - 格式保护机制干扰")
        print("     - 字符串匹配边界问题")
        print("     - 其他翻译规则覆盖")

def check_current_dictionary():
    """检查当前词典内容"""
    print("\n📚 检查当前词典内容:")
    
    # 检查JSON文件
    if os.path.exists("complete_translation_dictionary.json"):
        with open("complete_translation_dictionary.json", "r", encoding="utf-8") as f:
            dictionary = json.load(f)
        
        print(f"   JSON词典包含 {len(dictionary)} 个条目")
        
        # 查找相关条目
        related = {k: v for k, v in dictionary.items() if "启动" in k or "翻译" in k or "系统" in k}
        print(f"   相关条目 {len(related)} 个:")
        for k, v in list(related.items())[:5]:
            print(f"     \"{k}\" -> \"{v}\"")
    else:
        print("   ❌ 未找到complete_translation_dictionary.json")

if __name__ == "__main__":
    test_dictionary_fix()
    check_current_dictionary() 