#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试emoji字符串修复方案
Test Emoji String Fix
"""

from log_translation_engine import LogTranslationEngine

def test_emoji_fix():
    """测试emoji字符串修复方案"""
    print("🧪 测试emoji字符串修复方案")
    print("=" * 50)
    
    # 创建翻译引擎
    engine = LogTranslationEngine()
    
    # 测试原始问题
    test_line = "🌍 日志翻译系统已自动启动"
    print(f"\n1. 原始问题:")
    print(f"   原文: {test_line}")
    print(f"   现在: {engine.smart_translate_line(test_line)}")
    
    # 方案1A：添加包含emoji的完整字符串
    print(f"\n2. 方案1A - 添加包含emoji的完整字符串:")
    engine.dictionary.complete_dictionary["🌍 日志翻译系统已自动启动"] = "🌍 Log Translation System Started Automatically"
    
    result_1a = engine.smart_translate_line(test_line)
    print(f"   添加后: {result_1a}")
    success_1a = "✅ 成功" if "Log Translation System Started Automatically" in result_1a else "❌ 失败"
    print(f"   结果: {success_1a}")
    
    # 重新创建引擎测试方案1B
    print(f"\n3. 方案1B - 添加多个变体:")
    engine2 = LogTranslationEngine()
    
    # 添加多个变体
    engine2.dictionary.complete_dictionary.update({
        "日志翻译系统已自动启动": "Log Translation System Started Automatically",
        "🌍 日志翻译系统已自动启动": "🌍 Log Translation System Started Automatically",
        "日志翻译系统": "Log Translation System",
        "已自动启动": "Started Automatically"
    })
    
    result_1b = engine2.smart_translate_line(test_line)
    print(f"   添加后: {result_1b}")
    success_1b = "✅ 成功" if "Log Translation System Started Automatically" in result_1b else "❌ 失败"
    print(f"   结果: {success_1b}")
    
    # 测试其他相关的系统通知
    print(f"\n4. 测试其他系统通知:")
    test_cases = [
        "🌍 日志翻译系统已自动启动",
        "🌍 日志翻译系统已自动停止",
        "⚠️ 翻译系统启动失败",
        "⚠️ 翻译系统停止失败",
        "🌍 已强制翻译所有日志文件"
    ]
    
    for test_case in test_cases:
        result = engine2.smart_translate_line(test_case)
        is_translated = test_case != result
        status = "✅" if is_translated else "❌"
        print(f"   {status} \"{test_case}\" -> \"{result}\"")
    
    # 分析字符串匹配的细节
    print(f"\n5. 分析字符串匹配细节:")
    
    # 检查字符串的内容
    original = "🌍 日志翻译系统已自动启动"
    print(f"   原字符串长度: {len(original)}")
    print(f"   原字符串编码: {original.encode('utf-8')}")
    
    # 检查匹配过程
    print(f"\n   词典中的匹配项:")
    for key, value in engine2.dictionary.complete_dictionary.items():
        if "日志翻译系统" in key:
            print(f"     \"{key}\" ({len(key)}字符) -> \"{value}\"")
    
    # 结论
    print(f"\n6. 结论:")
    if "Log Translation System Started Automatically" in result_1a:
        print("   ✅ 方案1A可行！")
        print("   📝 推荐的词典条目:")
        print("     \"🌍 日志翻译系统已自动启动\": \"🌍 Log Translation System Started Automatically\"")
    elif "Log Translation System Started Automatically" in result_1b:
        print("   ✅ 方案1B可行！")
        print("   📝 推荐的词典条目:")
        print("     \"日志翻译系统已自动启动\": \"Log Translation System Started Automatically\"")
        print("     \"🌍 日志翻译系统已自动启动\": \"🌍 Log Translation System Started Automatically\"")
    else:
        print("   ❌ 方案1可能需要进一步优化")
        print("   💡 建议考虑其他方案")

if __name__ == "__main__":
    test_emoji_fix() 