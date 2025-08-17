#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一决策系统
实现标准化的决策格式和WBM集成
"""

import time
import json
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from eocatr_unified_format import SimpleRule, SimpleDecision, create_simple_decision
from simplified_bmp_generator import SimplifiedBMPGenerator

class UnifiedDecisionSystem:
    """统一的决策系统"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.decision_storage: Dict[str, SimpleDecision] = {}  # 决策存储
        self.bmp_generator: SimplifiedBMPGenerator = SimplifiedBMPGenerator(logger)  # BMP规律生成器
        self.decision_history: List[Dict[str, Any]] = []  # 决策历史
        
        if self.logger:
            self.logger.log("🎯 统一决策系统已初始化")
    
    def make_decision(self, current_context: Dict[str, Any]) -> SimpleDecision:
        """
        为当前上下文做出决策
        决策流程：
        1. 查找历史决策库匹配
        2. 如果没有匹配，使用WBM规律生成决策
        3. 将新决策保存到决策库
        """
        if self.logger:
            self.logger.log(f"🎯 开始决策过程，上下文: {current_context}")
        
        # 步骤1: 查找历史决策库匹配
        matched_decision = self._find_matching_decision(current_context)
        if matched_decision:
            if self.logger:
                self.logger.log(f"🎯 找到匹配的历史决策: {matched_decision.to_format_string()}")
            return matched_decision
        
        # 步骤2: 使用WBM规律生成新决策
        wbm_decision = self._generate_wbm_decision(current_context)
        if wbm_decision:
            # 保存新决策到决策库
            self.decision_storage[wbm_decision.decision_id] = wbm_decision
            
            if self.logger:
                self.logger.log(f"🎯 WBM生成新决策: {wbm_decision.to_format_string()}")
            return wbm_decision
        
        # 步骤3: 兜底决策
        fallback_decision = self._create_fallback_decision(current_context)
        
        if self.logger:
            self.logger.log(f"🎯 使用兜底决策: {fallback_decision.to_format_string()}")
        
        return fallback_decision
    
    def _find_matching_decision(self, context: Dict[str, Any]) -> Optional[SimpleDecision]:
        """在决策库中查找匹配的决策"""
        if not self.decision_storage:
            return None
        
        best_match = None
        best_similarity = 0.0
        similarity_threshold = 0.7  # 相似度阈值
        
        for decision in self.decision_storage.values():
            similarity = self._calculate_context_similarity(context, decision.context)
            
            if similarity > best_similarity and similarity >= similarity_threshold:
                best_similarity = similarity
                best_match = decision
        
        if self.logger and best_match:
            self.logger.log(f"🎯 决策库匹配成功，相似度: {best_similarity:.3f}")
        
        return best_match
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """计算两个上下文的相似度"""
        if not context1 or not context2:
            return 0.0
        
        # 关键字段权重
        weights = {
            'environment': 0.3,
            'object': 0.3,
            'characteristics': 0.4
        }
        
        total_similarity = 0.0
        total_weight = 0.0
        
        for key, weight in weights.items():
            if key in context1 and key in context2:
                if key == 'characteristics':
                    # 特征字典的详细比较
                    char_sim = self._calculate_characteristics_similarity(
                        context1[key], context2[key]
                    )
                    total_similarity += char_sim * weight
                else:
                    # 简单字符串比较
                    if context1[key] == context2[key]:
                        total_similarity += weight
                
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0.0
    
    def _calculate_characteristics_similarity(self, chars1: Dict[str, Any], chars2: Dict[str, Any]) -> float:
        """计算特征字典的相似度"""
        if not chars1 or not chars2:
            return 0.0
        
        # 关键特征权重
        char_weights = {
            'c1_distance_category': 0.3,
            'c2_danger_type': 0.4,
            'c3_resource_type': 0.3
        }
        
        similarity = 0.0
        total_weight = 0.0
        
        for key, weight in char_weights.items():
            if key in chars1 and key in chars2:
                if chars1[key] == chars2[key]:
                    similarity += weight
                total_weight += weight
        
        return similarity / total_weight if total_weight > 0 else 0.0
    
    def _generate_wbm_decision(self, context: Dict[str, Any]) -> Optional[SimpleDecision]:
        """使用WBM方法生成决策（基于规律组合）"""
        environment = context.get('environment', '')
        object_name = context.get('object', '')
        characteristics = context.get('characteristics', {})
        
        if self.logger:
            self.logger.log(f"🎯 WBM决策生成：环境={environment}, 对象={object_name}")
        
        # 获取适用的规律
        applicable_rules = self.bmp_generator.get_applicable_rules(context)
        
        if not applicable_rules:
            if self.logger:
                self.logger.log("🎯 WBM：未找到适用规律")
            return None
        
        # 按置信度分组规律
        action_rules = [rule for rule in applicable_rules if rule.action_tool_type == "action"]
        tool_rules = [rule for rule in applicable_rules if rule.action_tool_type == "tool"]
        
        if self.logger:
            self.logger.log(f"🎯 WBM：找到 {len(action_rules)} 个动作规律，{len(tool_rules)} 个工具规律")
        
        # 选择最佳规律组合
        if action_rules and tool_rules:
            # 组合决策：动作规律 + 工具规律
            primary_rule = action_rules[0]  # 最高置信度的动作规律
            secondary_rule = tool_rules[0]  # 最高置信度的工具规律
            
            decision = create_simple_decision(
                primary_rule=primary_rule,
                secondary_rule=secondary_rule,
                player_id=context.get('player_id', ''),
                context=context
            )
            
            if self.logger:
                self.logger.log(f"🎯 WBM组合决策: {decision.to_format_string()}")
            
        elif action_rules:
            # 单一动作决策
            primary_rule = action_rules[0]
            
            decision = create_simple_decision(
                primary_rule=primary_rule,
                player_id=context.get('player_id', ''),
                context=context
            )
            
            if self.logger:
                self.logger.log(f"🎯 WBM单一决策: {decision.to_format_string()}")
            
        else:
            # 如果只有工具规律，也可以生成决策
            primary_rule = tool_rules[0] if tool_rules else None
            
            if primary_rule:
                decision = create_simple_decision(
                    primary_rule=primary_rule,
                    player_id=context.get('player_id', ''),
                    context=context
                )
                
                if self.logger:
                    self.logger.log(f"🎯 WBM工具决策: {decision.to_format_string()}")
            else:
                return None
        
        return decision
    
    def _create_fallback_decision(self, context: Dict[str, Any]) -> SimpleDecision:
        """创建兜底决策"""
        # 创建一个基础的探索规律
        fallback_rule = SimpleRule(
            rule_id=f"FALLBACK_{int(time.time())}",
            rule_type="FALLBACK",
            condition_element="any",
            condition_type="fallback",
            action_or_tool="explore",
            action_tool_type="action",
            expected_result="explore_result",
            success_rate=0.5,
            confidence=0.1,
            support_count=1,
            total_count=1,
            player_id=context.get('player_id', '')
        )
        
        return create_simple_decision(
            primary_rule=fallback_rule,
            player_id=context.get('player_id', ''),
            context=context
        )
    
    def update_decision_result(self, decision_id: str, success: bool, 
                              actual_result: str, reward: float = 0.0):
        """更新决策结果，用于学习和优化"""
        if decision_id in self.decision_storage:
            decision = self.decision_storage[decision_id]
            
            # 记录决策历史
            history_record = {
                'decision_id': decision_id,
                'success': success,
                'actual_result': actual_result,
                'reward': reward,
                'timestamp': time.time(),
                'format_string': decision.to_format_string()
            }
            
            self.decision_history.append(history_record)
            
            # 更新规律的成功率统计
            self._update_rule_statistics(decision.primary_rule, success)
            if decision.secondary_rule:
                self._update_rule_statistics(decision.secondary_rule, success)
            
            if self.logger:
                self.logger.log(f"🎯 决策结果更新: {decision_id[:8]} -> 成功={success}, 奖励={reward}")
    
    def _update_rule_statistics(self, rule: SimpleRule, success: bool):
        """更新规律的统计信息"""
        rule.total_count += 1
        if success:
            rule.support_count += 1
        
        # 重新计算成功率和置信度
        rule.success_rate = rule.support_count / rule.total_count
        rule.confidence = rule.success_rate * (rule.total_count / (rule.total_count + 1))
        
        # 更新BMP生成器中的规律
        if rule.rule_id in self.bmp_generator.rule_storage:
            self.bmp_generator.rule_storage[rule.rule_id] = rule
    
    def add_experiences_to_bmp(self, experiences: List) -> List[SimpleRule]:
        """将新经验添加到BMP生成器中"""
        return self.bmp_generator.process_experience_batch(experiences)
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        total_decisions = len(self.decision_storage)
        total_history = len(self.decision_history)
        
        if total_history == 0:
            return {
                'total_decisions': total_decisions,
                'total_executed': 0,
                'success_rate': 0.0,
                'decision_types': {},
                'average_confidence': 0.0
            }
        
        # 统计决策类型
        decision_types = defaultdict(int)
        total_confidence = 0.0
        successful_decisions = 0
        
        for decision in self.decision_storage.values():
            decision_types[decision.to_format_string()] += 1
            total_confidence += decision.combined_confidence
        
        for record in self.decision_history:
            if record['success']:
                successful_decisions += 1
        
        return {
            'total_decisions': total_decisions,
            'total_executed': total_history,
            'success_rate': successful_decisions / total_history,
            'decision_types': dict(decision_types),
            'average_confidence': total_confidence / total_decisions if total_decisions > 0 else 0.0,
            'bmp_rule_stats': self.bmp_generator.get_statistics()
        }
    
    def export_decision_library(self) -> List[Dict[str, Any]]:
        """导出决策库"""
        return [decision.to_dict() for decision in self.decision_storage.values()]
    
    def import_decision_library(self, decisions_data: List[Dict[str, Any]]):
        """导入决策库"""
        for decision_data in decisions_data:
            # 重建SimpleDecision对象
            primary_rule = SimpleRule.from_dict(decision_data['primary_rule'])
            secondary_rule = None
            if decision_data.get('secondary_rule'):
                secondary_rule = SimpleRule.from_dict(decision_data['secondary_rule'])
            
            decision = SimpleDecision(
                decision_id=decision_data['decision_id'],
                primary_rule=primary_rule,
                secondary_rule=secondary_rule,
                recommended_action=decision_data['recommended_action'],
                recommended_tool=decision_data.get('recommended_tool', 'no_tool'),
                expected_outcome=decision_data.get('expected_outcome', ''),
                combined_confidence=decision_data.get('combined_confidence', 0.0),
                context=decision_data.get('context', {}),
                created_time=decision_data.get('created_time', time.time()),
                player_id=decision_data.get('player_id', '')
            )
            
            self.decision_storage[decision.decision_id] = decision
        
        if self.logger:
            self.logger.log(f"🎯 导入了 {len(decisions_data)} 个决策")
    
    def save_to_file(self, filepath: str = "unified_decisions.json") -> bool:
        """保存决策库到文件"""
        try:
            save_data = {
                'metadata': {
                    'version': '1.0',
                    'timestamp': time.time(),
                    'total_decisions': len(self.decision_storage),
                    'total_history': len(self.decision_history),
                    'format': 'unified_decision_system'
                },
                'decisions': self.export_decision_library(),
                'decision_history': self.decision_history,
                'statistics': self.get_decision_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            if self.logger:
                self.logger.log(f"🎯 决策库已保存到: {filepath}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 保存决策库失败: {str(e)}")
            return False
    
    def load_from_file(self, filepath: str = "unified_decisions.json") -> bool:
        """从文件加载决策库"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            decisions_data = save_data.get('decisions', [])
            self.import_decision_library(decisions_data)
            
            # 加载决策历史
            if 'decision_history' in save_data:
                self.decision_history = save_data['decision_history']
            
            if self.logger:
                self.logger.log(f"🎯 从文件加载了 {len(decisions_data)} 个决策")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 加载决策库失败: {str(e)}")
            return False

# === 测试函数 ===

def test_unified_decision_system():
    """测试统一决策系统"""
    from eocatr_unified_format import create_unified_eocatr
    
    # 创建测试日志
    class TestLogger:
        def log(self, message):
            print(f"[TEST] {message}")
    
    logger = TestLogger()
    decision_system = UnifiedDecisionSystem(logger)
    
    # 先添加一些经验到BMP生成器
    experiences = []
    
    # 创建测试经验
    characteristics1 = {
        'c1_distance': 2.0,
        'c1_distance_category': '近距离',
        'c2_safety_level': 0.8,
        'c2_danger_type': '无',
        'c3_resource_value': 0.9,
        'c3_resource_type': '食物'
    }
    exp1 = create_unified_eocatr("open_field", "edible_plant", "gather", "basket", "success", 
                                characteristics1, "player1", True, 10.0)
    experiences.append(exp1)
    
    characteristics2 = {
        'c1_distance': 8.0,
        'c1_distance_category': '中距离',
        'c2_safety_level': 0.2,
        'c2_danger_type': '严重',
        'c3_resource_value': 0.0,
        'c3_resource_type': '威胁'
    }
    exp2 = create_unified_eocatr("forest", "predator", "avoid", "no_tool", "success",
                                characteristics2, "player1", True, 1.0)
    experiences.append(exp2)
    
    # 添加经验到BMP
    print("\n=== 添加经验到BMP ===")
    rules = decision_system.add_experiences_to_bmp(experiences)
    print(f"BMP生成了 {len(rules)} 个规律")
    
    # 测试决策生成
    print("\n=== 测试决策生成 ===")
    
    # 测试上下文1: 类似已有经验
    test_context1 = {
        'environment': 'open_field',
        'object': 'edible_plant',
        'characteristics': {
            'c1_distance_category': '近距离',
            'c2_danger_type': '无',
            'c3_resource_type': '食物'
        },
        'player_id': 'player1'
    }
    
    decision1 = decision_system.make_decision(test_context1)
    print(f"决策1: {decision1.to_format_string()}")
    print(f"推荐动作: {decision1.recommended_action}, 工具: {decision1.recommended_tool}")
    print(f"置信度: {decision1.combined_confidence:.3f}")
    
    # 模拟决策执行结果
    decision_system.update_decision_result(decision1.decision_id, True, "success", 8.0)
    
    # 测试上下文2: 相似情况（应该匹配已有决策）
    test_context2 = {
        'environment': 'open_field',
        'object': 'edible_plant',
        'characteristics': {
            'c1_distance_category': '近距离',
            'c2_danger_type': '无',
            'c3_resource_type': '食物'
        },
        'player_id': 'player1'
    }
    
    decision2 = decision_system.make_decision(test_context2)
    print(f"\n决策2: {decision2.to_format_string()}")
    print(f"决策ID相同: {decision1.decision_id == decision2.decision_id}")
    
    # 测试上下文3: 完全不同的情况
    test_context3 = {
        'environment': 'mountain',
        'object': 'water_source',
        'characteristics': {
            'c1_distance_category': '远距离',
            'c2_danger_type': '轻微',
            'c3_resource_type': '水源'
        },
        'player_id': 'player1'
    }
    
    decision3 = decision_system.make_decision(test_context3)
    print(f"\n决策3: {decision3.to_format_string()}")
    print(f"推荐动作: {decision3.recommended_action}, 工具: {decision3.recommended_tool}")
    
    # 显示统计信息
    print(f"\n=== 决策系统统计 ===")
    stats = decision_system.get_decision_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    test_unified_decision_system() 