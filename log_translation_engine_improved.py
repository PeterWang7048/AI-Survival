#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版日志翻译引擎 - 修复格式保护和翻译质量问题
Improved Log Translation Engine - Fix format protection and translation quality issues
"""

import re
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from translation_dictionary import TranslationDictionary

class ImprovedLogTranslationEngine:
    def __init__(self, dictionary_path: str = "complete_translation_dictionary.json"):
        """初始化改进版翻译引擎"""
        self.dictionary = TranslationDictionary()
        self.translation_cache = {}
        self.format_patterns = self._build_improved_format_patterns()
        
        # 加载词典
        if os.path.exists(dictionary_path):
            self.load_dictionary(dictionary_path)
        
        # 统计信息
        self.stats = {
            'lines_processed': 0,
            'lines_translated': 0,
            'translations_used': 0,
            'format_preservations': 0,
            'errors_fixed': 0
        }
    
    def _build_improved_format_patterns(self) -> Dict[str, str]:
        """构建改进的格式保护模式"""
        return {
            # 时间戳模式 - 完整匹配
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            # 玩家ID模式 - 精确匹配
            'player_id': r'\b([A-Z]+\d+)\b',
            # 状态格式 - 完整匹配
            'status_format': r'(HP\d+/F\d+/W\d+)',
            # 坐标格式 - 完整匹配
            'coordinates': r'(\(\d+,\s*\d+\))',
            # 位置变化格式 - 完整匹配
            'position_change': r'(\d+,\d+->+\d+,\d+)',
            # 小数格式 - 完整匹配
            'decimal_numbers': r'(\d+\.\d+)',
            # Hash格式 - 完整匹配
            'hash_format': r'([a-f0-9]{32})',
            # Emoji保护
            'emoji': r'([\U0001F300-\U0001F9FF])',
            # 箭头符号
            'arrows': r'(->)',
            # 分隔符
            'separators': r'(\|)',
            # 括号内容保护
            'parentheses_content': r'(\([^)]*\))',
        }
    
    def load_dictionary(self, filepath: str):
        """加载翻译词典"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                custom_dict = json.load(f)
            self.dictionary.complete_dictionary.update(custom_dict)
            print(f"📚 已加载翻译词典: {len(custom_dict)} 个术语")
        except Exception as e:
            print(f"⚠️ 加载词典失败: {e}")
    
    def protect_formats(self, text: str) -> Tuple[str, Dict[str, str]]:
        """改进的格式保护 - 使用唯一标识符避免嵌套"""
        protected_text = text
        protection_map = {}
        
        # 按优先级顺序处理格式保护
        protection_order = [
            'timestamp', 'hash_format', 'status_format', 'coordinates', 
            'position_change', 'decimal_numbers', 'player_id', 'emoji',
            'arrows', 'separators'
        ]
        
        for pattern_name in protection_order:
            if pattern_name not in self.format_patterns:
                continue
                
            pattern = self.format_patterns[pattern_name]
            matches = list(re.finditer(pattern, protected_text))
            
            for i, match in enumerate(matches):
                match_text = match.group(1)
                # 使用更安全的占位符格式
                placeholder = f"§{pattern_name}_{i}§"
                
                # 检查是否已经被保护
                if placeholder not in protection_map:
                    protected_text = protected_text.replace(match_text, placeholder, 1)
                    protection_map[placeholder] = match_text
                    self.stats['format_preservations'] += 1
        
        return protected_text, protection_map
    
    def restore_formats(self, text: str, protection_map: Dict[str, str]) -> str:
        """恢复被保护的格式"""
        restored_text = text
        
        # 按长度排序，优先恢复长占位符
        sorted_placeholders = sorted(protection_map.keys(), key=len, reverse=True)
        
        for placeholder in sorted_placeholders:
            original = protection_map[placeholder]
            restored_text = restored_text.replace(placeholder, original)
        
        return restored_text
    
    def translate_chinese_segments(self, text: str) -> str:
        """改进的中文片段翻译"""
        # 先检查缓存
        if text in self.translation_cache:
            return self.translation_cache[text]
        
        translated_text = text
        
        # 使用词典进行翻译（按长度排序，优先匹配长词）
        terms_by_length = sorted(self.dictionary.complete_dictionary.items(), 
                                key=lambda x: len(x[0]), reverse=True)
        
        for chinese_term, english_term in terms_by_length:
            if chinese_term in translated_text:
                # 避免翻译占位符内容
                if not re.search(r'§[^§]*§', chinese_term):
                    translated_text = translated_text.replace(chinese_term, english_term)
                    self.stats['translations_used'] += 1
        
        # 缓存结果
        self.translation_cache[text] = translated_text
        return translated_text
    
    def smart_translate_line(self, line: str) -> str:
        """智能翻译单行日志"""
        original_line = line.strip()
        if not original_line:
            return original_line
        
        # 检查是否包含中文
        if not re.search(r'[\u4e00-\u9fff]', original_line):
            return original_line
        
        try:
            # 步骤1: 保护格式
            protected_line, protection_map = self.protect_formats(original_line)
            
            # 步骤2: 翻译中文内容
            translated_line = self.translate_chinese_segments(protected_line)
            
            # 步骤3: 恢复格式
            final_line = self.restore_formats(translated_line, protection_map)
            
            return final_line
            
        except Exception as e:
            print(f"⚠️ 翻译行时出错: {str(e)}")
            return original_line
    
    def translate_log_file(self, input_file: str, output_file: str = None) -> bool:
        """翻译整个日志文件"""
        if not os.path.exists(input_file):
            print(f"❌ 输入文件不存在: {input_file}")
            return False
        
        # 确定输出文件名
        if output_file is None:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_en{ext}"
        
        print(f"🔄 开始翻译日志文件: {input_file}")
        print(f"📝 输出文件: {output_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f_in:
                lines = f_in.readlines()
            
            translated_lines = []
            
            for i, line in enumerate(lines):
                self.stats['lines_processed'] += 1
                
                # 翻译行
                translated_line = self.smart_translate_line(line.rstrip())
                
                # 如果翻译有变化，计数
                if translated_line != line.rstrip():
                    self.stats['lines_translated'] += 1
                
                translated_lines.append(translated_line + '\n')
                
                # 进度显示
                if (i + 1) % 1000 == 0:
                    print(f"📊 已处理 {i + 1}/{len(lines)} 行")
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f_out:
                f_out.writelines(translated_lines)
            
            print(f"✅ 翻译完成!")
            print(f"📊 处理统计:")
            print(f"  总行数: {self.stats['lines_processed']}")
            print(f"  翻译行数: {self.stats['lines_translated']}")
            print(f"  使用翻译: {self.stats['translations_used']} 次")
            print(f"  格式保护: {self.stats['format_preservations']} 次")
            
            return True
            
        except Exception as e:
            print(f"❌ 翻译失败: {str(e)}")
            return False
    
    def test_translation_quality(self, test_cases: List[str] = None) -> Dict:
        """测试翻译质量"""
        if test_cases is None:
            test_cases = [
                "2025-01-06 01:38:54 ILAI1 🔍 状态评估: 充足安全 | 健康:100 食物:99 水:99",
                "ILAI1 🧠 CDL层激活: 启动好奇心驱动探索",
                "DQN2 行动详情: 移动 | 位置:29,37->28,37 | 状态HP100/F99/W99",
                "ILAI1 🌉 WBM决策制定开始 - 目标: cdl_exploration (紧急度: 0.70)",
                "ILAI1 🌸 BPM规律类型分布: 原始规律 8 个, 去重效果: 优秀",
                "ILAI1 添加经验到五库系统: EOCATR格式经验成功存储"
            ]
        
        print("🧪 改进版翻译质量测试:")
        print("=" * 80)
        
        results = {
            'total_tests': len(test_cases),
            'successful_translations': 0,
            'format_preservations': 0,
            'test_results': []
        }
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试 {i+1}:")
            print(f"原文: {test_case}")
            
            translated = self.smart_translate_line(test_case)
            print(f"译文: {translated}")
            
            # 简单检查翻译质量
            has_chinese = re.search(r'[\u4e00-\u9fff]', translated)
            has_placeholder_error = '§' in translated
            
            if not has_chinese and not has_placeholder_error:
                results['successful_translations'] += 1
                results['format_preservations'] += 1
                print("✅ 翻译成功")
            else:
                print("❌ 翻译问题")
                if has_chinese:
                    print("  - 仍含中文")
                if has_placeholder_error:
                    print("  - 占位符错误")
            
            results['test_results'].append({
                'original': test_case,
                'translated': translated,
                'success': not has_chinese and not has_placeholder_error
            })
        
        print(f"\n📊 测试总结:")
        print(f"  总测试数: {results['total_tests']}")
        print(f"  成功翻译: {results['successful_translations']}")
        print(f"  格式保护: {results['format_preservations']}")
        print(f"  成功率: {results['successful_translations']/results['total_tests']*100:.1f}%")
        
        return results

def main():
    """测试改进版翻译引擎"""
    print("🚀 改进版日志翻译引擎测试...")
    
    engine = ImprovedLogTranslationEngine()
    
    # 执行质量测试
    test_results = engine.test_translation_quality()
    
    print("\n🤖 改进版翻译引擎已就绪!")
    print(f"📚 词典包含 {len(engine.dictionary.complete_dictionary)} 个术语")
    
    # 显示使用方法
    print("\n📖 使用方法:")
    print("  engine.translate_log_file('game_xxx.log')  # 翻译单个文件")
    print("  engine.batch_translate_logs()             # 批量翻译所有文件")

if __name__ == "__main__":
    main() 