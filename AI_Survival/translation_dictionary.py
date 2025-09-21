#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译词典 - 中英文术语对照系统
Translation Dictionary - Chinese-English Technical Terms Mapping
"""

import json
import re
from typing import Dict, List, Tuple

class TranslationDictionary:
    def __init__(self):
        # 初始化所有术语词典
        self.system_components = self._build_system_components()
        self.decision_terms = self._build_decision_terms()
        self.action_terms = self._build_action_terms()
        self.status_terms = self._build_status_terms()
        self.bmp_terms = self._build_bmp_terms()
        self.player_terms = self._build_player_terms()
        self.format_terms = self._build_format_terms()
        self.context_patterns = self._build_context_patterns()
        
        # 合并所有词典
        self.complete_dictionary = self._merge_dictionaries()
        
    def _build_system_components(self) -> Dict[str, str]:
        """系统组件术语"""
        return {
            # 核心系统
            "五库系统": "Five-Library System",
            "直接经验库": "Direct Experience Library",
            "总经验库": "Total Experience Library", 
            "直接规律库": "Direct Rules Library",
            "总规律库": "Total Rules Library",
            "决策库": "Decision Library",
            
            # 技术组件
            "EOCATR": "EOCATR",
            "WBM": "WBM (Wooden Bridge Model)",
            "BPM": "BMP (Blooming and Pruning Model)",
            "CDL": "CDL (Curiosity-Driven Learning)",
            "DMHA": "DMHA (Dynamic Multi-Head Attention)",
            "SSM": "SSM (Scene Symbolization Mechanism)",
            
            # 全局系统
            "全局知识同步器": "Global Knowledge Synchronizer",
            "全局知识同步网络": "Global Knowledge Sync Network",
        }
    
    def _build_decision_terms(self) -> Dict[str, str]:
        """决策相关术语"""
        return {
            # 决策过程
            "状态评估": "Status Assessment",
            "决策阶段": "Decision Phase",
            "决策制定": "Decision Making",
            "决策制定开始": "Decision Making Started",
            "决策制定完成": "Decision Making Completed",
            "决策来源": "Decision Source",
            "决策评价": "Decision Evaluation",
            
            # 决策层级
            "本能层": "Instinct Layer",
            "本能层激活": "Instinct Layer Activated",
            "CDL层": "CDL Layer",
            "CDL层激活": "CDL Layer Activated", 
            "层确定目标": "Layer Target Determined",
            
            # 决策类型
            "好奇心驱动探索": "Curiosity-Driven Exploration",
            "目标导向决策": "Goal-Oriented Decision",
            "本能决策": "Instinct Decision",
            "进入目标导向决策模式": "Entering Goal-Oriented Decision Mode",
        }
    
    def _build_action_terms(self) -> Dict[str, str]:
        """行动相关术语"""
        return {
            # 行动描述
            "行动详情": "Action Details",
            "移动": "Movement",
            "位置": "Position",
            "状态": "Status",
            "健康": "Health",
            "食物": "Food",
            "水": "Water",
            
            # 策略类型
            "利用": "Exploit",
            "探索": "Explore",
            "利用:选择Q值最大的动物": "Exploit: Select Max Q-value Action",
            "探索:随机选择动物": "Explore: Random Action Selection",
            "值最大的动物": "Max Q-value Action",
            
            # 执行状态
            "执行": "Execute",
            "首个行动": "First Action",
            "步": "Step",
            "天": "Day",
            "回合": "Round",
        }
    
    def _build_status_terms(self) -> Dict[str, str]:
        """状态相关术语"""
        return {
            # 状态评估
            "充足安全": "Abundant & Safe",
            "紧急状态": "Emergency State",
            "环境安全": "Environment Safe",
            "资源充足": "Resources Abundant",
            "资源充足，环境安全": "Resources Abundant, Environment Safe",
            
            # 威胁状态
            "威胁接近": "Threat Approaching",
            "本能逃离威胁成功": "Instinct Threat Escape Successful",
            "本能层触发条件满足": "Instinct Layer Trigger Condition Met",
            
            # 数值状态
            "新颖性": "Novelty",
            "好奇心": "Curiosity", 
            "置信度": "Confidence",
            "紧急度": "Urgency",
            "效用": "Utility",
            "成本": "Cost",
            "成功": "Success",
        }
    
    def _build_bmp_terms(self) -> Dict[str, str]:
        """BMP系统术语"""
        return {
            # 规律相关
            "规律": "Rule",
            "规律类型": "Rule Type",
            "规律类型分布": "Rule Type Distribution",
            "规律检索": "Rule Retrieval", 
            "规律接头": "Rule Connection",
            "规律生成": "Rule Generation",
            "规律验证": "Rule Validation",
            
            # BMP特有
            "去重效果": "Deduplication Effect",
            "原始规律": "Original Rules",
            "个原始规律": "Original Rules",
            "个唯一规律": "Unique Rules",
            "怒放阶段已激活": "Blooming Phase Activated",
            "种组合规律": "Rule Combinations",
            "基础规律": "Basic Rules",
            "直接规律": "Direct Rules",
            "总规律": "Total Rules",
            
            # 规律描述
            "开阔地-无结果": "Open Field - No Result",
            "未知-无结果": "Unknown - No Result", 
            "移动-无结果": "Movement - No Result",
            "探索-无结果": "Exploration - No Result",
            "开阔地-移动": "Open Field - Movement",
            "开阔地-探索": "Open Field - Exploration",
            "未知-移动": "Unknown - Movement",
            "未知-探索": "Unknown - Exploration",
        }
    
    def _build_player_terms(self) -> Dict[str, str]:
        """玩家相关术语"""
        return {
            # 模型类型
            "玩家": "Player",
            "加载已有模型": "Loading Existing Model",
            "已注册到全局知识同步网络": "Registered to Global Knowledge Sync Network",
            
            # 经验相关
            "添加经验": "Add Experience",
            "添加经验到五库系统": "Add Experience to Five-Library System",
            "经验状态": "Experience Status",
            "经验同步": "Experience Synchronization",
            "经验已分享给": "Experience Shared with",
            "分享经验给": "Share Experience with",
            "当前数量": "Current Count",
            "触发门槛": "Trigger Threshold",
            
            # 发现相关
            "发现": "Discovered",
            "发现新颖": "Discovered Novel",
            "发现正在执行的长链计划": "Found Executing Long-chain Plan",
            "个新奇目标": "Novel Targets",
            "新奇度": "Novelty Score",
            "个新颖知识项目": "Novel Knowledge Items",
        }
    
    def _build_format_terms(self) -> Dict[str, str]:
        """格式相关术语"""
        return {
            # 存储相关
            "五库经验存储成功": "Five-Library Experience Storage Successful",
            "保存跳过": "Save Skipped",
            "符号化跳过": "Symbolization Skipped",
            "距离上次": "Since Last",
            "需等待": "Need to Wait",
            "回合，需等待": "Rounds, Need to Wait",
            
            # 链相关
            "长链": "Long Chain",
            "长链计划": "Long-chain Plan",
            "长链第": "Long Chain Step",
            "新长链计划启动": "New Long-chain Plan Started",
            "启动新长链计划": "Start New Long-chain Plan",
            "开启新的长链决策计划": "Open New Long-chain Decision Plan",
            "长链执行管理": "Long-chain Execution Management",
            "新计划第": "New Plan Step",
            "检查长链计划第": "Check Long-chain Plan Step",
            
            # 数量描述
            "条": "Items",
            "个": "Count",
            "次": "Times",
            "点声望": "Reputation Points",
            "个用户": "Users",
            "总计": "Total",
        }
    
    def _build_context_patterns(self) -> Dict[str, str]:
        """上下文模式翻译"""
        return {
            # 常见组合
            "转换:": "Conversion:",
            "获取:": "Retrieved:",
            "原因:": "Reason:",
            "目标:": "Target:",
            "评估:": "Assessment:",
            "推理:": "Reasoning:",
            "从": "From",
            "条,": "Items,",
            "天)": " Days)",
            "回合)": " Rounds)",
            "天执行:": "Day Execution:",
            "天:": " Day:",
            
            # 链式描述
            "链构建:": "Chain Building:",
            "条决策链": "Decision Chains",
            "个兼容规律": "Compatible Rules",
            "最佳链效用": "Best Chain Utility",
            "过滤后": "Filtered",
            "生成": "Generated",
            
            # 状态描述
            "等待更多经验:": "Waiting for More Experience:",
            "状态检从": "Status Check From",
            "对象已初始化": "Object Initialized",
            "集成:生成": "Integration: Generated",
            "条件检查:": "Condition Check:",
            "启动决策评价": "Start Decision Evaluation",
        }
    
    def _build_general_terms(self) -> Dict[str, str]:
        """通用术语词典 - 补充遗漏的术语"""
        return {
            "已启动": "started",
            "回合开始": "Round Start",
            "启动": "Starting",
            "最高": "highest",
            "直接": "direct",
            "目标类型": "target type",
            "需要": "requires",
            "规划": "planning",
            "新": "New",
            "开阔地": "Open Field",
            "未知": "Unknown",
            "添加": "Add",
            "经验": "Experience",
            "优秀": "Excellent",
            "结束": "End",
            "改变": "Change",
            "Position改变": "Position Change",
            "Round结束": "Round End",
            "第": "Round",
            "回合": "Round",
            "使用目录": "using directory",
            "，": ", ",
            "第1": "Round 1",
            "第2": "Round 2",
            "第3": "Round 3",
            "第4": "Round 4",
            "第5": "Round 5",
            "距离": "Distance",
            "石头": "Stone",
            "记录": "Record",
            "可执行": "Executable",
            "模型": "Model",
            "保存": "Save",
            "获得": "gained",
            "基于": "based on",
            "进行": "perform",
            "挖掘": "mining",
            "已分享给": "shared with",
            "模型已保存": "Model Saved",
            "记录植物采集": "Record Plant Collection",
            "记录五库采集": "Record Five-Library Collection",
            "Add可Executable": "Add Executable",
            "并同From": "and from",
            "Rule已分享给": "Rule shared with",
            "Users": "Users",
            "个": " ",
            "Days": "Days",
            "天": "Days",
            "本轮": "this round",
            "了": "",
            "并同From": "and from",
            "并同Step": "and step",
            "并同": "and",
            "游戏": "Game",
            "正在": "Processing",
            "最终": "Final",
            "排名": "Rank",
            "生存": "Survival",
            "数": "Count",
            "声誉": "Reputation",
            "血量": "Health",
            "率": "Rate",
            "植物": "Plants",
            "采集植物": "Collected Plants",
            "遭遇动物": "Encountered Animals",
            "击杀动物": "Killed Animals",
            "大树": "Big Trees",
            "山洞": "Caves",
            "颖": "Novel",
            "算力消耗": "Computing Cost",
            "反应时间": "Response Time",
            "Execute": "Execute",
            "生存Days": "Survival Days",
            "Explore率": "Exploration Rate",
            "Discovered植物": "Discovered Plants",
            "Discovered大树": "Discovered Big Trees",
            "Explore山洞": "Explored Caves",
            "New颖Discovered": "Novel Discoveries",
        }
    
    def _merge_dictionaries(self) -> Dict[str, str]:
        """合并所有词典"""
        complete_dict = {}
        
        # 按优先级合并（后面的会覆盖前面的）
        dicts_to_merge = [
            self.system_components,
            self.decision_terms,
            self.action_terms,
            self.status_terms,
            self.bmp_terms,
            self.player_terms,
            self.format_terms,
            self.context_patterns,
            self._build_general_terms()  # 添加通用术语
        ]
        
        for d in dicts_to_merge:
            complete_dict.update(d)
        
        return complete_dict
    
    def get_translation(self, chinese_text: str) -> str:
        """获取中文文本的英文翻译"""
        # 直接匹配
        if chinese_text in self.complete_dictionary:
            return self.complete_dictionary[chinese_text]
        
        # 部分匹配（找最长匹配）
        best_match = ""
        best_translation = chinese_text
        
        for chinese_term, english_term in self.complete_dictionary.items():
            if chinese_term in chinese_text and len(chinese_term) > len(best_match):
                best_match = chinese_term
                best_translation = chinese_text.replace(chinese_term, english_term)
        
        return best_translation
    
    def save_dictionary(self, filepath: str = "complete_translation_dictionary.json"):
        """保存完整词典到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.complete_dictionary, f, ensure_ascii=False, indent=2)
        print(f"💾 完整翻译词典已保存到: {filepath}")
    
    def get_statistics(self) -> Dict[str, int]:
        """获取词典统计信息"""
        return {
            "system_components": len(self.system_components),
            "decision_terms": len(self.decision_terms),
            "action_terms": len(self.action_terms),
            "status_terms": len(self.status_terms),
            "bmp_terms": len(self.bmp_terms),
            "player_terms": len(self.player_terms),
            "format_terms": len(self.format_terms),
            "context_patterns": len(self.context_patterns),
            "total_terms": len(self.complete_dictionary)
        }

def main():
    """主函数 - 创建和保存翻译词典"""
    print("🏗️ 创建完整翻译词典...")
    
    # 创建词典实例
    translator = TranslationDictionary()
    
    # 保存到文件
    translator.save_dictionary()
    
    # 显示统计信息
    stats = translator.get_statistics()
    print("\n📊 词典统计:")
    for category, count in stats.items():
        print(f"  {category}: {count} 个术语")
    
    print(f"\n🎯 总计: {stats['total_terms']} 个翻译对照")
    
    # 测试几个翻译
    print("\n🧪 翻译测试:")
    test_terms = [
        "状态评估",
        "五库系统", 
        "行动详情",
        "利用:选择Q值最大的动物",
        "充足安全"
    ]
    
    for term in test_terms:
        translation = translator.get_translation(term)
        print(f"  {term} → {translation}")

if __name__ == "__main__":
    main() 