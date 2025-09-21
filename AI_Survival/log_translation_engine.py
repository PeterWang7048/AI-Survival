#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志翻译引擎 - 智能中英文日志翻译系统
Log Translation Engine - Intelligent Chinese-English Log Translation System
"""

import re
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from translation_dictionary import TranslationDictionary

class LogTranslationEngine:
    def __init__(self, dictionary_path: str = "complete_translation_dictionary.json"):
        """初始化翻译引擎"""
        self.dictionary = TranslationDictionary()
        self.translation_cache = {}
        self.format_patterns = self._build_format_patterns()
        
        # 🆕 系统通知过滤模式
        self.system_notification_patterns = [
            r"🌍.*日志翻译系统.*启动",
            r"🌍.*日志翻译系统.*停止", 
            r"⚠️.*翻译系统.*失败",
            r"🌍.*强制翻译.*日志文件",
            r"🌍.*翻译系统.*处理"
        ]
        
        # 加载词典
        if os.path.exists(dictionary_path):
            self.load_dictionary(dictionary_path)
        
        # 统计信息
        self.stats = {
            'lines_processed': 0,
            'lines_translated': 0,
            'translations_used': 0,
            'format_preservations': 0,
            'system_notifications_filtered': 0  # 新增：过滤的系统通知数量
        }
    
    def _build_format_patterns(self) -> Dict[str, str]:
        """构建格式保护模式"""
        return {
            # 时间戳模式
            'timestamp': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            # 玩家ID模式
            'player_id': r'([A-Z]+\d+)',
            # 状态格式
            'status': r'(HP\d+/F\d+/W\d+)',
            # 坐标格式
            'coordinates': r'(\(\d+,\s*\d+\))',
            # 数字格式
            'numbers': r'(\d+\.\d+)',
            # 整数
            'integers': r'(\d+)',
            # Emoji
            'emoji': r'([\U0001F300-\U0001F9FF])',
            # 箭头
            'arrows': r'(->)',
            # 分隔符
            'separators': r'(\|)',
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
    
    def protect_formats(self, text: str) -> Tuple[str, List[str]]:
        """保护文本中的格式，返回保护后的文本和保护的内容"""
        protected_text = text
        protected_items = []
        
        for pattern_name, pattern in self.format_patterns.items():
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                placeholder = f"__{pattern_name.upper()}{i}__"
                protected_text = protected_text.replace(match, placeholder, 1)
                protected_items.append((placeholder, match))
                self.stats['format_preservations'] += 1
        
        return protected_text, protected_items
    
    def restore_formats(self, text: str, protected_items: List[Tuple[str, str]]) -> str:
        """恢复被保护的格式"""
        restored_text = text
        for placeholder, original in protected_items:
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
    
    def translate_chinese_segments(self, text: str) -> str:
        """翻译文本中的中文片段"""
        # 先检查缓存
        if text in self.translation_cache:
            return self.translation_cache[text]
        
        translated_text = text
        
        # 使用词典进行翻译（按长度排序，优先匹配长词）
        terms_by_length = sorted(self.dictionary.complete_dictionary.items(), 
                                key=lambda x: len(x[0]), reverse=True)
        
        for chinese_term, english_term in terms_by_length:
            if chinese_term in translated_text:
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
        
        # 🆕 方案A: 过滤系统通知
        for pattern in self.system_notification_patterns:
            if re.search(pattern, original_line):
                self.stats['system_notifications_filtered'] += 1
                return ""  # 返回空字符串，让这行在英文版中消失
        
        # 检查是否包含中文
        if not re.search(r'[\u4e00-\u9fff]', original_line):
            return original_line
        
        # 步骤1: 保护格式
        protected_line, protected_items = self.protect_formats(original_line)
        
        # 步骤2: 翻译中文内容
        translated_line = self.translate_chinese_segments(protected_line)
        
        # 步骤3: 恢复格式
        final_line = self.restore_formats(translated_line, protected_items)
        
        return final_line
    
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
                
                # 🆕 只有非空行才添加到结果中（过滤掉系统通知）
                if translated_line.strip():
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
            if self.stats['system_notifications_filtered'] > 0:
                print(f"  🔄 过滤系统通知: {self.stats['system_notifications_filtered']} 行")
            
            return True
            
        except Exception as e:
            print(f"❌ 翻译失败: {str(e)}")
            return False
    
    def batch_translate_logs(self, pattern: str = "game_*.log") -> List[str]:
        """批量翻译日志文件"""
        import glob
        
        log_files = glob.glob(pattern)
        if not log_files:
            print(f"❌ 未找到匹配的日志文件: {pattern}")
            return []
        
        print(f"📁 找到 {len(log_files)} 个日志文件")
        
        translated_files = []
        
        for log_file in log_files:
            print(f"\n🔄 翻译: {log_file}")
            
            # 重置统计信息
            self.stats = {
                'lines_processed': 0,
                'lines_translated': 0,
                'translations_used': 0,
                'format_preservations': 0,
                'system_notifications_filtered': 0
            }
            
            output_file = log_file.replace('.log', '_en.log')
            
            if self.translate_log_file(log_file, output_file):
                translated_files.append(output_file)
                print(f"✅ 完成: {output_file}")
            else:
                print(f"❌ 失败: {log_file}")
        
        return translated_files
    
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
        
        print("🧪 翻译质量测试:")
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
            
            # 检查是否保持了格式
            formats_preserved = True
            for pattern in self.format_patterns.values():
                if re.search(pattern, test_case):
                    if not re.search(pattern, translated):
                        formats_preserved = False
                        break
            
            if formats_preserved:
                results['format_preservations'] += 1
            
            if translated != test_case:
                results['successful_translations'] += 1
            
            results['test_results'].append({
                'original': test_case,
                'translated': translated,
                'format_preserved': formats_preserved
            })
        
        print(f"\n📊 测试总结:")
        print(f"  总测试数: {results['total_tests']}")
        print(f"  成功翻译: {results['successful_translations']}")
        print(f"  格式保护: {results['format_preservations']}")
        
        return results

def main():
    """主函数 - 翻译引擎测试"""
    print("🚀 日志翻译引擎启动...")
    
    # 创建翻译引擎
    engine = LogTranslationEngine()
    
    # 测试翻译质量
    print("\n🧪 执行翻译质量测试...")
    test_results = engine.test_translation_quality()
    
    # 询问是否进行批量翻译
    print(f"\n🤖 翻译引擎已就绪!")
    print(f"📚 词典包含 {len(engine.dictionary.complete_dictionary)} 个术语")
    
    # 查找日志文件
    import glob
    log_files = glob.glob("game_*.log")
    
    if log_files:
        print(f"\n📁 发现 {len(log_files)} 个日志文件:")
        for log_file in log_files:
            print(f"  - {log_file}")
        
        print(f"\n💡 使用方式:")
        print(f"  engine.translate_log_file('game_xxx.log')  # 翻译单个文件")
        print(f"  engine.batch_translate_logs()             # 批量翻译所有文件")
    else:
        print("\n❌ 未找到日志文件")

if __name__ == "__main__":
    main() 