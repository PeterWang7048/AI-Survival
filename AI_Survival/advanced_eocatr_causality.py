"""
高级EOCATR因果关系网络系统
体现复杂的多层因果联系、条件因果网络和规律间的相互作用
"""

import sqlite3
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import itertools

class AdvancedCausalityType(Enum):
    """高级因果关系类型"""
    # 基础因果类型
    ENABLING = "enabling"              # 使能关系：E+O+C → 使得 A+T 成为可能
    DETERMINISTIC = "deterministic"    # 决定关系：A+T → 必然导致 R
    PROBABILISTIC = "probabilistic"    # 概率关系：E+O+C+A+T → 概率导致 R
    CONDITIONAL = "conditional"        # 条件关系：如果 E+O+C，则 A+T 有效
    INHIBITING = "inhibiting"          # 抑制关系：某些组合阻止结果发生
    
    # 高级因果类型
    SYNERGISTIC = "synergistic"        # 协同关系：多个元素组合产生增强效果
    ALTERNATIVE = "alternative"        # 替代关系：多种路径达到同样结果
    SEQUENTIAL = "sequential"          # 序列关系：必须按特定顺序发生
    COMPETITIVE = "competitive"        # 竞争关系：多个选项相互排斥
    FEEDBACK = "feedback"              # 反馈关系：结果影响前置条件
    EMERGENT = "emergent"              # 涌现关系：整体效果大于部分之和

@dataclass
class CausalElement:
    """高级因果元素"""
    element_type: str  # E, O, C, A, T, R
    value: str
    weight: float = 1.0          # 在因果关系中的权重
    necessity: float = 1.0       # 必要性程度 0-1
    activation_threshold: float = 0.5  # 激活阈值
    temporal_order: int = 0      # 时间顺序 (用于序列因果)
    mutual_exclusions: List[str] = field(default_factory=list)  # 互斥元素

@dataclass
class CausalPattern:
    """因果模式"""
    pattern_id: str
    pattern_type: str            # 简单、复合、网络
    causality_relations: List['CausalRelation']
    pattern_strength: float      # 整体模式强度
    emergence_factor: float = 1.0  # 涌现因子
    
    def get_pattern_complexity(self) -> float:
        """计算模式复杂度"""
        base_complexity = len(self.causality_relations)
        # 考虑关系间的交互
        interaction_complexity = sum([
            rel.get_interaction_complexity() for rel in self.causality_relations
        ])
        return base_complexity + interaction_complexity * 0.1

@dataclass
class CausalRelation:
    """高级因果关系"""
    relation_id: str
    causality_type: AdvancedCausalityType
    antecedent: List[CausalElement]      # 前件（原因）
    consequent: List[CausalElement]      # 后件（结果）
    strength: float                      # 因果关系强度 0-1
    confidence: float                    # 置信度 0-1
    support_count: int                   # 支持证据数量
    contradiction_count: int             # 反驳证据数量
    
    # 高级属性
    temporal_delay: float = 0.0          # 时间延迟
    context_dependencies: List[str] = field(default_factory=list)  # 上下文依赖
    moderating_factors: Dict[str, float] = field(default_factory=dict)  # 调节因子
    threshold_conditions: Dict[str, float] = field(default_factory=dict)  # 阈值条件
    
    def get_interaction_complexity(self) -> float:
        """获取交互复杂度"""
        base = len(self.antecedent) * len(self.consequent)
        context_factor = len(self.context_dependencies) * 0.2
        moderation_factor = len(self.moderating_factors) * 0.3
        threshold_factor = len(self.threshold_conditions) * 0.1
        return base + context_factor + moderation_factor + threshold_factor
    
    def evaluate_activation(self, context: Dict[str, Any]) -> float:
        """评估因果关系激活程度"""
        # 检查前件匹配
        antecedent_activation = self._evaluate_element_set(self.antecedent, context)
        
        # 检查上下文依赖
        context_satisfaction = self._evaluate_context_dependencies(context)
        
        # 应用调节因子
        moderation_effect = self._apply_moderating_factors(context)
        
        # 检查阈值条件
        threshold_satisfaction = self._evaluate_threshold_conditions(context)
        
        # 综合计算激活程度
        base_activation = antecedent_activation * context_satisfaction
        moderated_activation = base_activation * moderation_effect
        final_activation = moderated_activation * threshold_satisfaction
        
        return min(1.0, final_activation)
    
    def _evaluate_element_set(self, elements: List[CausalElement], context: Dict[str, Any]) -> float:
        """评估元素集合匹配度"""
        if not elements:
            return 1.0
        
        total_weight = sum(elem.weight for elem in elements)
        if total_weight == 0:
            return 0.0
        
        activated_weight = 0.0
        for element in elements:
            context_value = context.get(element.element_type.lower(), '')
            match_degree = self._calculate_match_degree(element.value, context_value)
            
            if match_degree >= element.activation_threshold:
                activated_weight += element.weight * match_degree
        
        return activated_weight / total_weight
    
    def _calculate_match_degree(self, target_value: str, context_value: str) -> float:
        """计算匹配程度"""
        if target_value == context_value:
            return 1.0
        elif target_value in context_value or context_value in target_value:
            return 0.8
        elif len(set(target_value.split()) & set(context_value.split())) > 0:
            return 0.6
        else:
            return 0.0
    
    def _evaluate_context_dependencies(self, context: Dict[str, Any]) -> float:
        """评估上下文依赖满足度"""
        if not self.context_dependencies:
            return 1.0
        
        satisfied_count = 0
        for dependency in self.context_dependencies:
            if dependency in context and context[dependency]:
                satisfied_count += 1
        
        return satisfied_count / len(self.context_dependencies)
    
    def _apply_moderating_factors(self, context: Dict[str, Any]) -> float:
        """应用调节因子"""
        if not self.moderating_factors:
            return 1.0
        
        moderation_effect = 1.0
        for factor, weight in self.moderating_factors.items():
            factor_value = context.get(factor, 0.5)  # 默认中性值
            moderation_effect *= (1.0 + (factor_value - 0.5) * weight)
        
        return max(0.1, min(2.0, moderation_effect))  # 限制在合理范围内
    
    def _evaluate_threshold_conditions(self, context: Dict[str, Any]) -> float:
        """评估阈值条件"""
        if not self.threshold_conditions:
            return 1.0
        
        for condition, threshold in self.threshold_conditions.items():
            context_value = context.get(condition, 0.0)
            if context_value < threshold:
                return 0.0  # 任何阈值条件不满足都会阻止激活
        
        return 1.0
    
    def to_advanced_expression(self) -> str:
        """转换为高级规律表达式"""
        ante_str = " ∧ ".join([f"{elem.element_type}:{elem.value}[w:{elem.weight:.1f},n:{elem.necessity:.1f}]" 
                              for elem in self.antecedent])
        cons_str = " ∧ ".join([f"{elem.element_type}:{elem.value}[w:{elem.weight:.1f}]" 
                              for elem in self.consequent])
        
        # 添加时间延迟信息
        delay_str = f"[延迟:{self.temporal_delay:.1f}s]" if self.temporal_delay > 0 else ""
        
        # 添加调节因子信息
        mod_str = ""
        if self.moderating_factors:
            mod_list = [f"{k}:{v:.1f}" for k, v in self.moderating_factors.items()]
            mod_str = f"[调节:{','.join(mod_list)}]"
        
        # 生成表达式
        if self.causality_type == AdvancedCausalityType.SYNERGISTIC:
            return f"({ante_str}) ⊕ 协同 ({cons_str}){delay_str}{mod_str}"
        elif self.causality_type == AdvancedCausalityType.SEQUENTIAL:
            return f"({ante_str}) ⟹ 序列 ({cons_str}){delay_str}{mod_str}"
        elif self.causality_type == AdvancedCausalityType.FEEDBACK:
            return f"({ante_str}) ⟲ 反馈 ({cons_str}){delay_str}{mod_str}"
        elif self.causality_type == AdvancedCausalityType.EMERGENT:
            return f"({ante_str}) ⟐ 涌现 ({cons_str}){delay_str}{mod_str}"
        else:
            return f"({ante_str}) →[{self.strength:.2f}] ({cons_str}){delay_str}{mod_str}"

class AdvancedEOCATRCausalityNetwork:
    """高级EOCATR因果关系网络"""
    
    def __init__(self, network_id: str):
        self.network_id = network_id
        self.causal_patterns: List[CausalPattern] = []
        self.element_registry: Dict[str, Set[str]] = {}  # 元素类型 -> 值集合
        self.network_metrics = {
            'total_complexity': 0.0,
            'emergence_potential': 0.0,
            'network_density': 0.0
        }
    
    def add_causal_pattern(self, pattern: CausalPattern):
        """添加因果模式"""
        self.causal_patterns.append(pattern)
        self._update_element_registry(pattern)
        self._update_network_metrics()
    
    def _update_element_registry(self, pattern: CausalPattern):
        """更新元素注册表"""
        for relation in pattern.causality_relations:
            for element in relation.antecedent + relation.consequent:
                if element.element_type not in self.element_registry:
                    self.element_registry[element.element_type] = set()
                self.element_registry[element.element_type].add(element.value)
    
    def _update_network_metrics(self):
        """更新网络指标"""
        if not self.causal_patterns:
            return
        
        # 计算总复杂度
        total_complexity = sum(pattern.get_pattern_complexity() for pattern in self.causal_patterns)
        self.network_metrics['total_complexity'] = total_complexity
        
        # 计算涌现潜力
        emergence_factors = [pattern.emergence_factor for pattern in self.causal_patterns]
        self.network_metrics['emergence_potential'] = sum(emergence_factors) / len(emergence_factors)
        
        # 计算网络密度
        total_relations = sum(len(pattern.causality_relations) for pattern in self.causal_patterns)
        unique_elements = sum(len(values) for values in self.element_registry.values())
        if unique_elements > 1:
            max_possible_relations = unique_elements * (unique_elements - 1)
            self.network_metrics['network_density'] = total_relations / max_possible_relations
    
    def find_causal_chains(self, start_element: str, end_element: str) -> List[List[CausalRelation]]:
        """查找因果链"""
        chains = []
        visited = set()
        
        def dfs(current_element: str, target_element: str, current_chain: List[CausalRelation]):
            if current_element == target_element and current_chain:
                chains.append(current_chain.copy())
                return
            
            if current_element in visited:
                return
            
            visited.add(current_element)
            
            # 查找以当前元素为前件的关系
            for pattern in self.causal_patterns:
                for relation in pattern.causality_relations:
                    for ante_elem in relation.antecedent:
                        if ante_elem.value == current_element:
                            for cons_elem in relation.consequent:
                                current_chain.append(relation)
                                dfs(cons_elem.value, target_element, current_chain)
                                current_chain.pop()
            
            visited.remove(current_element)
        
        dfs(start_element, end_element, [])
        return chains
    
    def evaluate_network_coherence(self) -> float:
        """评估网络一致性"""
        if not self.causal_patterns:
            return 0.0
        
        # 检查冲突关系
        conflicts = 0
        total_comparisons = 0
        
        for i, pattern1 in enumerate(self.causal_patterns):
            for j, pattern2 in enumerate(self.causal_patterns[i+1:], i+1):
                total_comparisons += 1
                if self._patterns_conflict(pattern1, pattern2):
                    conflicts += 1
        
        if total_comparisons == 0:
            return 1.0
        
        return 1.0 - (conflicts / total_comparisons)
    
    def _patterns_conflict(self, pattern1: CausalPattern, pattern2: CausalPattern) -> bool:
        """检查两个模式是否冲突"""
        # 简化的冲突检测：相同前件，不同后件
        for rel1 in pattern1.causality_relations:
            for rel2 in pattern2.causality_relations:
                if self._relations_have_same_antecedent(rel1, rel2):
                    if not self._relations_have_compatible_consequent(rel1, rel2):
                        return True
        return False
    
    def _relations_have_same_antecedent(self, rel1: CausalRelation, rel2: CausalRelation) -> bool:
        """检查两个关系是否有相同前件"""
        ante1_values = {f"{elem.element_type}:{elem.value}" for elem in rel1.antecedent}
        ante2_values = {f"{elem.element_type}:{elem.value}" for elem in rel2.antecedent}
        return len(ante1_values & ante2_values) >= 0.7 * min(len(ante1_values), len(ante2_values))
    
    def _relations_have_compatible_consequent(self, rel1: CausalRelation, rel2: CausalRelation) -> bool:
        """检查两个关系是否有兼容后件"""
        cons1_values = {f"{elem.element_type}:{elem.value}" for elem in rel1.consequent}
        cons2_values = {f"{elem.element_type}:{elem.value}" for elem in rel2.consequent}
        return len(cons1_values & cons2_values) > 0

def create_advanced_causality_from_eocatr(eocatr_data: Dict[str, Any]) -> AdvancedEOCATRCausalityNetwork:
    """从EOCATR数据创建高级因果网络"""
    network_id = f"network_{eocatr_data.get('rule_id', 'unknown')}"
    network = AdvancedEOCATRCausalityNetwork(network_id)
    
    # 提取基本信息
    environment = eocatr_data.get('environment', '')
    obj = eocatr_data.get('object', '')
    condition = eocatr_data.get('condition', '')
    action = eocatr_data.get('action', '')
    tool = eocatr_data.get('tool', '')
    result = eocatr_data.get('result', '')
    success_rate = eocatr_data.get('success_rate', 0.5)
    
    # 创建高级因果关系
    relations = []
    
    # 1. 协同关系：环境和对象协同使能行动
    if environment and obj and action:
        synergistic_relation = CausalRelation(
            relation_id=f"{network_id}_synergistic",
            causality_type=AdvancedCausalityType.SYNERGISTIC,
            antecedent=[
                CausalElement("E", environment, weight=1.0, necessity=0.8, activation_threshold=0.6),
                CausalElement("O", obj, weight=1.0, necessity=0.9, activation_threshold=0.7)
            ],
            consequent=[
                CausalElement("A", action, weight=1.0, necessity=1.0)
            ],
            strength=0.85,
            confidence=eocatr_data.get('confidence', 0.5),
            support_count=eocatr_data.get('usage_count', 0),
            contradiction_count=0,
            moderating_factors={'condition_quality': 0.3, 'tool_availability': 0.2}
        )
        relations.append(synergistic_relation)
    
    # 2. 序列关系：行动必须在工具准备后进行
    if action and tool and result:
        sequential_relation = CausalRelation(
            relation_id=f"{network_id}_sequential",
            causality_type=AdvancedCausalityType.SEQUENTIAL,
            antecedent=[
                CausalElement("T", tool, weight=1.0, necessity=0.7, temporal_order=1),
                CausalElement("A", action, weight=1.0, necessity=1.0, temporal_order=2)
            ],
            consequent=[
                CausalElement("R", result, weight=1.0, necessity=1.0, temporal_order=3)
            ],
            strength=success_rate,
            confidence=eocatr_data.get('confidence', 0.5),
            support_count=eocatr_data.get('success_count', 0),
            contradiction_count=max(0, eocatr_data.get('usage_count', 0) - eocatr_data.get('success_count', 0)),
            temporal_delay=1.0,
            threshold_conditions={'skill_level': 0.3}
        )
        relations.append(sequential_relation)
    
    # 3. 涌现关系：完整EOCATR组合产生涌现效果
    if all([environment, obj, condition, action, tool, result]):
        emergent_relation = CausalRelation(
            relation_id=f"{network_id}_emergent",
            causality_type=AdvancedCausalityType.EMERGENT,
            antecedent=[
                CausalElement("E", environment, weight=0.8, necessity=0.6),
                CausalElement("O", obj, weight=1.0, necessity=0.8),
                CausalElement("C", condition, weight=0.6, necessity=0.4),
                CausalElement("A", action, weight=1.0, necessity=1.0),
                CausalElement("T", tool, weight=0.7, necessity=0.5)
            ],
            consequent=[
                CausalElement("R", result, weight=1.0, necessity=1.0)
            ],
            strength=success_rate * 1.2,  # 涌现效应增强
            confidence=eocatr_data.get('confidence', 0.5),
            support_count=eocatr_data.get('success_count', 0),
            contradiction_count=0,
            context_dependencies=['environmental_stability', 'resource_availability'],
            moderating_factors={'experience_level': 0.4, 'environmental_favorability': 0.3}
        )
        relations.append(emergent_relation)
    
    # 创建因果模式
    pattern = CausalPattern(
        pattern_id=f"pattern_{network_id}",
        pattern_type="复合涌现模式",
        causality_relations=relations,
        pattern_strength=success_rate,
        emergence_factor=1.3 if len(relations) >= 3 else 1.0
    )
    
    network.add_causal_pattern(pattern)
    return network

def demonstrate_advanced_causality():
    """演示高级因果关系网络"""
    print("=== 高级EOCATR因果关系网络演示 ===\n")
    
    # 从数据库加载EOCATR规律
    conn = sqlite3.connect('five_libraries/eocatr_rules_final.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT rule_id, environment, object, condition, action, tool, result, 
           confidence, success_rate, usage_count, success_count
    FROM eocatr_rules LIMIT 2
    ''')
    
    eocatr_rules = cursor.fetchall()
    columns = ['rule_id', 'environment', 'object', 'condition', 'action', 'tool', 'result', 
               'confidence', 'success_rate', 'usage_count', 'success_count']
    
    print("🕸️ 高级EOCATR因果关系网络分析:")
    
    for rule_data in eocatr_rules:
        rule_dict = dict(zip(columns, rule_data))
        
        print(f"\n📋 规律: {rule_dict['rule_id']}")
        print(f"   原始EOCATR: E:{rule_dict['environment']}|O:{rule_dict['object']}|C:{rule_dict['condition']}|A:{rule_dict['action']}|T:{rule_dict['tool']}|R:{rule_dict['result']}")
        
        # 创建高级因果网络
        network = create_advanced_causality_from_eocatr(rule_dict)
        
        print(f"   高级因果关系网络:")
        for pattern in network.causal_patterns:
            print(f"     模式类型: {pattern.pattern_type}")
            print(f"     模式复杂度: {pattern.get_pattern_complexity():.2f}")
            print(f"     涌现因子: {pattern.emergence_factor:.2f}")
            
            for i, relation in enumerate(pattern.causality_relations):
                print(f"       {i+1}. {relation.to_advanced_expression()}")
                
                # 测试激活
                test_context = {
                    'e': rule_dict['environment'],
                    'o': rule_dict['object'],
                    'c': rule_dict['condition'],
                    'skill_level': 0.7,
                    'experience_level': 0.6,
                    'environmental_favorability': 0.8
                }
                activation = relation.evaluate_activation(test_context)
                print(f"          激活程度: {activation:.2f}")
        
        # 网络指标
        print(f"   网络指标:")
        for metric, value in network.network_metrics.items():
            print(f"     {metric}: {value:.3f}")
        
        # 网络一致性
        coherence = network.evaluate_network_coherence()
        print(f"     网络一致性: {coherence:.3f}")
    
    conn.close()
    
    # 展示高级因果网络的优势
    print(f"\n🚀 高级因果网络的突破性优势:")
    advantages = [
        "🧠 智能激活: 根据上下文动态计算因果关系激活程度",
        "🔗 复合因果: 支持协同、序列、涌现等复杂因果类型",
        "⏰ 时序建模: 包含时间延迟和序列约束",
        "🎛️ 调节机制: 考虑环境因子对因果关系的调节作用",
        "🏗️ 网络结构: 构建完整的因果关系网络而非孤立规律",
        "📊 量化评估: 提供网络复杂度、一致性等量化指标",
        "🌟 涌现效应: 建模系统级的涌现行为和非线性效应",
        "🔄 反馈循环: 支持结果对前置条件的反馈影响"
    ]
    
    for advantage in advantages:
        print(f"   {advantage}")
    
    print(f"\n💡 这种表示方式将EOCATR从'简单因果'升级为'智能因果网络'，")
    print(f"   真正体现了规律作为'EOCATR元素间稳定联系'的本质！")

if __name__ == "__main__":
    demonstrate_advanced_causality() 