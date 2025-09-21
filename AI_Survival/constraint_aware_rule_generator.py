#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
约束感知的候选规律生成器 (Constraint-Aware Rule Generator)

基于论文中的C₂/C₃约束条件，设计约束驱动的生成策略：
- C₂约束：至少一个可控因子（A或T）
- C₃约束：至少一个上下文因子（E、O、C）

核心原则：先验证约束，再生成组合，避免生成-过滤的低效模式
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from itertools import combinations
import time

# 导入基础类型
from scene_symbolization_mechanism import EOCATR_Tuple


class ElementType(Enum):
    """EOCATR元素类型"""
    E = "environment"     # 环境 - 上下文因子
    O = "object"         # 对象 - 上下文因子  
    C = "characteristics" # 特征 - 上下文因子
    A = "action"         # 动作 - 可控因子
    T = "tool"           # 工具 - 可控因子
    R = "result"         # 结果 - 必须包含


class ConstraintValidator:
    """约束验证器"""
    
    @staticmethod
    def is_valid_combination(element_types: Set[ElementType]) -> bool:
        """
        验证元素组合是否满足C₂/C₃约束
        
        Args:
            element_types: 元素类型集合
            
        Returns:
            bool: 是否满足约束条件
        """
        # 必须包含结果R
        if ElementType.R not in element_types:
            return False
            
        # C₂约束：至少一个可控因子（A或T）
        controllable_factors = {ElementType.A, ElementType.T}
        has_controllable = bool(element_types & controllable_factors)
        
        # C₃约束：至少一个上下文因子（E、O、C）
        contextual_factors = {ElementType.E, ElementType.O, ElementType.C}
        has_contextual = bool(element_types & contextual_factors)
        
        return has_controllable and has_contextual
    
    @staticmethod
    def get_constraint_violation_reason(element_types: Set[ElementType]) -> Optional[str]:
        """获取约束违反的具体原因"""
        if ElementType.R not in element_types:
            return "缺少结果元素R"
            
        controllable_factors = {ElementType.A, ElementType.T}
        contextual_factors = {ElementType.E, ElementType.O, ElementType.C}
        
        has_controllable = bool(element_types & controllable_factors)
        has_contextual = bool(element_types & contextual_factors)
        
        if not has_controllable and not has_contextual:
            return "同时违反C₂约束(无可控因子)和C₃约束(无上下文因子)"
        elif not has_controllable:
            return "违反C₂约束：缺少可控因子(A或T)"
        elif not has_contextual:
            return "违反C₃约束：缺少上下文因子(E、O、C)"
        
        return None


@dataclass
class ValidCombination:
    """有效的元素组合"""
    elements: Set[ElementType]
    pattern_name: str
    complexity_level: int  # 组合复杂度：2=双元素, 3=三元素, 等等
    priority: float = 1.0  # 生成优先级
    
    def __post_init__(self):
        """计算复杂度等级"""
        # R是必需的，不计入复杂度
        non_result_elements = self.elements - {ElementType.R}
        self.complexity_level = len(non_result_elements)


class ConstraintAwareCombinationGenerator:
    """约束感知的组合生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.validator = ConstraintValidator()
        self.generation_stats = {
            'total_valid_combinations': 0,
            'combinations_by_complexity': {},
            'invalid_combinations_avoided': 0
        }
        self.valid_combinations = self._generate_all_valid_combinations()
        self.generation_stats['total_valid_combinations'] = len(self.valid_combinations)
        self.generation_stats['combinations_by_complexity'] = self._count_by_complexity()
        
    def _generate_all_valid_combinations(self) -> List[ValidCombination]:
        """生成所有符合约束的有效组合"""
        valid_combinations = []
        
        # 所有可能的元素类型（除了R，R是必须的）
        available_elements = [ElementType.E, ElementType.O, ElementType.C, 
                            ElementType.A, ElementType.T]
        
        # 生成从2到5个元素的所有组合（+R = 3到6个元素）
        for size in range(2, 6):  # 2, 3, 4, 5个非R元素
            for element_combo in combinations(available_elements, size):
                element_set = set(element_combo) | {ElementType.R}
                
                # 验证约束条件
                if self.validator.is_valid_combination(element_set):
                    pattern_name = self._generate_pattern_name(element_set)
                    priority = self._calculate_priority(element_set)
                    
                    valid_combinations.append(ValidCombination(
                        elements=element_set,
                        pattern_name=pattern_name,
                        complexity_level=size,
                        priority=priority
                    ))
                else:
                    self.generation_stats['invalid_combinations_avoided'] += 1
        
        # 按优先级和复杂度排序
        valid_combinations.sort(key=lambda x: (x.priority, -x.complexity_level), reverse=True)
        
        return valid_combinations
    
    def _generate_pattern_name(self, elements: Set[ElementType]) -> str:
        """生成模式名称"""
        # 按固定顺序排列元素
        order = [ElementType.E, ElementType.O, ElementType.C, ElementType.A, ElementType.T, ElementType.R]
        pattern_parts = [elem.value[0].upper() for elem in order if elem in elements]
        return "-".join(pattern_parts)
    
    def _calculate_priority(self, elements: Set[ElementType]) -> float:
        """计算生成优先级"""
        priority = 1.0
        
        # 工具使用规律优先级更高
        if ElementType.T in elements:
            priority += 0.3
            
        # 包含更多上下文信息的规律优先级更高
        contextual_count = len(elements & {ElementType.E, ElementType.O, ElementType.C})
        priority += contextual_count * 0.1
        
        # 复杂度适中的规律优先级更高（避免过简或过复杂）
        complexity = len(elements) - 1  # 减去R
        if complexity == 3:  # 三元素+R的组合
            priority += 0.2
        elif complexity == 2:  # 双元素+R的组合
            priority += 0.1
            
        return priority
    
    def _count_by_complexity(self) -> Dict[int, int]:
        """按复杂度统计组合数量"""
        counts = {}
        for combo in self.valid_combinations:
            level = combo.complexity_level
            counts[level] = counts.get(level, 0) + 1
        return counts
    
    def get_valid_combinations_for_complexity(self, max_complexity: int = 5) -> List[ValidCombination]:
        """获取指定复杂度范围内的有效组合"""
        return [combo for combo in self.valid_combinations 
                if combo.complexity_level <= max_complexity]
    
    def generate_rules_from_experience(self, experience: EOCATR_Tuple, 
                                     max_complexity: int = 4) -> List[Dict[str, Any]]:
        """
        从经验生成符合约束的候选规律
        
        Args:
            experience: EOCATR经验
            max_complexity: 最大复杂度限制
            
        Returns:
            List[Dict]: 候选规律列表
        """
        start_time = time.time()
        candidate_rules = []
        
        # 获取经验中的可用元素
        available_elements = self._extract_available_elements(experience)
        
        # 只生成符合约束且在经验中有对应元素的组合
        valid_combinations = self.get_valid_combinations_for_complexity(max_complexity)
        
        for combination in valid_combinations:
            # 检查经验是否包含该组合所需的所有元素
            if self._experience_supports_combination(experience, combination, available_elements):
                rule = self._create_candidate_rule(experience, combination, available_elements)
                if rule:
                    candidate_rules.append(rule)
        
        generation_time = (time.time() - start_time) * 1000
        
        return {
            'rules': candidate_rules,
            'generation_time_ms': generation_time,
            'total_combinations_checked': len(valid_combinations),
            'rules_generated': len(candidate_rules)
        }
    
    def _extract_available_elements(self, experience: EOCATR_Tuple) -> Dict[ElementType, Any]:
        """从经验中提取可用元素"""
        available = {}
        
        if experience.environment is not None:
            available[ElementType.E] = experience.environment
        if experience.object is not None:
            available[ElementType.O] = experience.object
        if experience.character is not None:
            available[ElementType.C] = experience.character
        if experience.action is not None:
            available[ElementType.A] = experience.action
        if experience.tool is not None:
            available[ElementType.T] = experience.tool
        if experience.result is not None:
            available[ElementType.R] = experience.result
            
        return available
    
    def _experience_supports_combination(self, experience: EOCATR_Tuple, 
                                       combination: ValidCombination,
                                       available_elements: Dict[ElementType, Any]) -> bool:
        """检查经验是否支持该组合"""
        required_elements = combination.elements
        available_element_types = set(available_elements.keys())
        
        # 经验必须包含组合要求的所有元素类型
        return required_elements.issubset(available_element_types)
    
    def _create_candidate_rule(self, experience: EOCATR_Tuple, 
                             combination: ValidCombination,
                             available_elements: Dict[ElementType, Any]) -> Optional[Dict[str, Any]]:
        """创建候选规律"""
        try:
            # 构建条件部分（除R之外的所有元素）
            condition_elements = combination.elements - {ElementType.R}
            conditions = {}
            
            for elem_type in condition_elements:
                if elem_type in available_elements:
                    element_value = available_elements[elem_type]
                    # 提取元素内容，处理不同的数据类型
                    if hasattr(element_value, 'content'):
                        element_content = element_value.content
                    elif hasattr(element_value, 'value'):
                        element_content = element_value.value
                    else:
                        element_content = str(element_value)
                    conditions[elem_type.value] = element_content
            
            # 构建结果部分
            result_element = available_elements.get(ElementType.R)
            if not result_element:
                return None
            
            # 提取结果内容
            if hasattr(result_element, 'content'):
                expected_result = result_element.content
            elif hasattr(result_element, 'value'):
                expected_result = result_element.value
            else:
                expected_result = str(result_element)
                
            rule = {
                'pattern_name': combination.pattern_name,
                'complexity_level': combination.complexity_level,
                'priority': combination.priority,
                'conditions': conditions,
                'expected_result': expected_result,
                'element_types': [elem.value for elem in combination.elements],
                'satisfies_constraints': True,  # 保证满足约束
                'generation_method': 'constraint_aware',
                'confidence': self._calculate_initial_confidence(combination),
                'rule_id': self._generate_rule_id(combination, conditions)
            }
            
            return rule
            
        except Exception as e:
            print(f"创建候选规律时出错: {e}")
            return None
    
    def _calculate_initial_confidence(self, combination: ValidCombination) -> float:
        """计算初始置信度"""
        base_confidence = 0.5
        
        # 基于复杂度调整
        if combination.complexity_level == 2:
            base_confidence += 0.1  # 简单规律更可信
        elif combination.complexity_level == 3:
            base_confidence += 0.2  # 三元规律平衡性好
        elif combination.complexity_level >= 4:
            base_confidence -= 0.1  # 复杂规律需要更多验证
            
        # 基于优先级调整
        base_confidence += (combination.priority - 1.0) * 0.2
        
        return max(0.1, min(0.9, base_confidence))
    
    def _generate_rule_id(self, combination: ValidCombination, conditions: Dict[str, Any]) -> str:
        """生成规律ID"""
        import hashlib
        
        content = f"{combination.pattern_name}_{str(sorted(conditions.items()))}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"RULE_{combination.pattern_name}_{hash_value}"
    
    def print_generation_summary(self):
        """打印生成策略总结"""
        print("=" * 60)
        print("约束感知候选规律生成器 - 总结报告")
        print("=" * 60)
        print(f"✅ 符合约束的有效组合: {self.generation_stats['total_valid_combinations']}个")
        print(f"🚫 避免生成的无效组合: {self.generation_stats['invalid_combinations_avoided']}个")
        print("\n📊 按复杂度分布:")
        for complexity, count in sorted(self.generation_stats['combinations_by_complexity'].items()):
            print(f"   {complexity}元素+R: {count}个组合")
        
        print("\n🎯 生成策略优势:")
        print("   • 零过滤：只生成符合约束的组合")
        print("   • 高效率：避免无效计算")
        print("   • 可预测：结果完全符合论文约束")
        print("   • 可扩展：易于添加新的约束条件")


def main():
    """测试函数"""
    print("测试约束感知候选规律生成器...")
    
    generator = ConstraintAwareCombinationGenerator()
    generator.print_generation_summary()
    
    print("\n🔍 有效组合示例:")
    for i, combo in enumerate(generator.valid_combinations[:10]):
        print(f"   {i+1}. {combo.pattern_name} (复杂度: {combo.complexity_level}, 优先级: {combo.priority:.2f})")


if __name__ == "__main__":
    main()
