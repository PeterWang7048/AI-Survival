#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一知识决策系统
整合经验→候选规律→正式规律→场景决策的完整流程
"""

import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
from enum import Enum
from collections import defaultdict, Counter

class RuleStatus(Enum):
    """规律状态"""
    CANDIDATE = "candidate"      # 候选规律
    VALIDATED = "validated"      # 已验证规律
    FORMAL = "formal"           # 正式规律
    DEPRECATED = "deprecated"    # 已废弃规律

class GoalType(Enum):
    """目标类型"""
    SURVIVAL = "survival"        # 生存目标
    RESOURCE = "resource"        # 资源获取
    EXPLORATION = "exploration"  # 探索目标
    COMBAT = "combat"           # 战斗目标
    SOCIAL = "social"           # 社交目标

@dataclass
class Experience:
    """经验数据结构"""
    experience_id: str
    environment: str
    object: str
    characteristics: str
    action: str
    tools: str
    result: str
    success: bool
    timestamp: float
    player_id: str
    
    def to_elements(self) -> Dict[str, List[str]]:
        """分解为元素"""
        condition_elements = []
        result_elements = []
        
        # 分解条件元素
        condition_elements.append(f"ENV:{self.environment}")
        condition_elements.append(f"OBJ:{self.object}")
        
        # 分解复合属性
        if '_' in self.characteristics:
            chars = self.characteristics.split('_')
            for char in chars:
                condition_elements.append(f"CHAR:{char}")
        else:
            condition_elements.append(f"CHAR:{self.characteristics}")
        
        condition_elements.append(f"ACT:{self.action}")
        condition_elements.append(f"TOOL:{self.tools}")
        
        # 分解结果元素
        if '_' in self.result:
            results = self.result.split('_')
            for result in results:
                result_elements.append(f"RESULT:{result}")
        else:
            result_elements.append(f"RESULT:{self.result}")
        
        return {
            'conditions': condition_elements,
            'results': result_elements
        }
    
    def generate_hash(self) -> str:
        """生成经验哈希"""
        content = f"{self.environment}|{self.object}|{self.characteristics}|{self.action}|{self.tools}|{self.result}"
        return hashlib.md5(content.encode()).hexdigest()

@dataclass
class Rule:
    """规律数据结构"""
    rule_id: str
    rule_type: str              # single_element, double_element
    conditions: List[str]       # 条件元素列表
    result: str                 # 结果
    confidence: float           # 置信度
    support_count: int          # 支持度
    status: RuleStatus          # 规律状态
    applicable_goals: List[GoalType]  # 适用目标
    created_time: float
    last_validated: float
    validation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def get_effectiveness(self) -> float:
        """计算规律有效性"""
        if self.validation_count == 0:
            return self.confidence
        return self.success_count / self.validation_count
    
    def is_applicable_to_goal(self, goal: GoalType) -> bool:
        """检查是否适用于目标"""
        return goal in self.applicable_goals
    
    def matches_scenario(self, scenario_elements: List[str]) -> float:
        """计算与场景的匹配度"""
        matched = 0
        for condition in self.conditions:
            if condition in scenario_elements:
                matched += 1
        return matched / len(self.conditions) if self.conditions else 0.0

@dataclass
class Scenario:
    """场景数据结构"""
    scenario_id: str
    current_elements: List[str]  # 当前场景元素
    goal: GoalType              # 目标类型
    priority: float             # 优先级
    constraints: List[str] = field(default_factory=list)  # 约束条件
    
    def to_dict(self) -> Dict:
        return {
            'scenario_id': self.scenario_id,
            'current_elements': self.current_elements,
            'goal': self.goal.value,
            'priority': self.priority,
            'constraints': self.constraints
        }

class UnifiedKnowledgeDecisionSystem:
    """统一知识决策系统"""
    
    def __init__(self):
        self.experiences: Dict[str, Experience] = {}
        self.candidate_rules: Dict[str, Rule] = {}
        self.formal_rules: Dict[str, Rule] = {}
        self.rule_performance: Dict[str, Dict] = {}
        
        # 规律生成配置
        self.min_support = 2
        self.min_confidence = 0.6
        self.validation_threshold = 5
        
    def add_experience(self, experience: Experience) -> Dict[str, Any]:
        """添加经验并自动生成候选规律"""
        result = {
            'experience_added': False,
            'candidate_rules_generated': 0,
            'formal_rules_promoted': 0
        }
        
        # 1. 添加经验
        exp_hash = experience.generate_hash()
        if exp_hash not in self.experiences:
            self.experiences[exp_hash] = experience
            result['experience_added'] = True
            
            print(f"📝 添加新经验: {experience.environment} + {experience.object} → {experience.result}")
            
            # 2. 生成候选规律
            candidate_rules = self._generate_candidate_rules_from_experience(experience)
            result['candidate_rules_generated'] = len(candidate_rules)
            
            # 3. 验证和提升规律
            promoted = self._validate_and_promote_rules()
            result['formal_rules_promoted'] = promoted
            
        return result
    
    def _generate_candidate_rules_from_experience(self, experience: Experience) -> List[Rule]:
        """从经验生成候选规律"""
        elements = experience.to_elements()
        conditions = elements['conditions']
        results = elements['results']
        
        candidate_rules = []
        
        # 生成单元素规律
        for condition in conditions:
            for result in results:
                rule_id = f"single_{hashlib.md5(f'{condition}→{result}'.encode()).hexdigest()[:8]}"
                
                if rule_id not in self.candidate_rules:
                    rule = Rule(
                        rule_id=rule_id,
                        rule_type="single_element",
                        conditions=[condition],
                        result=result,
                        confidence=0.5,  # 初始置信度
                        support_count=1,
                        status=RuleStatus.CANDIDATE,
                        applicable_goals=self._infer_applicable_goals(condition, result),
                        created_time=time.time(),
                        last_validated=time.time()
                    )
                    self.candidate_rules[rule_id] = rule
                    candidate_rules.append(rule)
                    print(f"   🌱 生成单元素候选规律: {condition} → {result}")
                else:
                    # 更新支持度
                    self.candidate_rules[rule_id].support_count += 1
        
        # 生成双元素规律
        from itertools import combinations
        for condition_pair in combinations(conditions, 2):
            for result in results:
                rule_id = f"double_{hashlib.md5(f'{condition_pair[0]}+{condition_pair[1]}→{result}'.encode()).hexdigest()[:8]}"
                
                if rule_id not in self.candidate_rules:
                    rule = Rule(
                        rule_id=rule_id,
                        rule_type="double_element",
                        conditions=list(condition_pair),
                        result=result,
                        confidence=0.6,  # 双元素规律初始置信度稍高
                        support_count=1,
                        status=RuleStatus.CANDIDATE,
                        applicable_goals=self._infer_applicable_goals_multi(condition_pair, result),
                        created_time=time.time(),
                        last_validated=time.time()
                    )
                    self.candidate_rules[rule_id] = rule
                    candidate_rules.append(rule)
                    print(f"   🌿 生成双元素候选规律: ({condition_pair[0]} + {condition_pair[1]}) → {result}")
                else:
                    # 更新支持度
                    self.candidate_rules[rule_id].support_count += 1
        
        return candidate_rules
    
    def _infer_applicable_goals(self, condition: str, result: str) -> List[GoalType]:
        """推断规律适用的目标类型"""
        goals = []
        
        # 基于结果推断目标
        if "受伤" in result or "死亡" in result or "危险" in result:
            goals.append(GoalType.SURVIVAL)
        if "食物" in result or "水" in result or "资源" in result:
            goals.append(GoalType.RESOURCE)
        if "探索" in result or "发现" in result or "新区域" in result:
            goals.append(GoalType.EXPLORATION)
        if "攻击" in result or "战斗" in result or "击败" in result:
            goals.append(GoalType.COMBAT)
        if "交流" in result or "合作" in result or "声誉" in result:
            goals.append(GoalType.SOCIAL)
        
        # 基于条件推断目标
        if "老虎" in condition or "危险" in condition:
            goals.append(GoalType.SURVIVAL)
        if "草莓" in condition or "河流" in condition:
            goals.append(GoalType.RESOURCE)
        
        return goals if goals else [GoalType.SURVIVAL]  # 默认生存目标
    
    def _infer_applicable_goals_multi(self, conditions: tuple, result: str) -> List[GoalType]:
        """推断多元素规律适用的目标类型"""
        goals = set()
        for condition in conditions:
            goals.update(self._infer_applicable_goals(condition, result))
        return list(goals)
    
    def _validate_and_promote_rules(self) -> int:
        """验证候选规律并提升为正式规律"""
        promoted_count = 0
        
        for rule_id, rule in list(self.candidate_rules.items()):
            # 检查是否满足提升条件
            if (rule.support_count >= self.min_support and 
                rule.confidence >= self.min_confidence and
                rule.validation_count >= self.validation_threshold):
                
                # 提升为正式规律
                rule.status = RuleStatus.FORMAL
                self.formal_rules[rule_id] = rule
                del self.candidate_rules[rule_id]
                promoted_count += 1
                
                print(f"   🏆 规律提升为正式规律: {' + '.join(rule.conditions)} → {rule.result}")
        
        return promoted_count
    
    def find_applicable_rules(self, scenario: Scenario) -> List[Dict[str, Any]]:
        """根据场景查找适用的规律"""
        applicable_rules = []
        
        # 搜索正式规律
        for rule_id, rule in self.formal_rules.items():
            if rule.is_applicable_to_goal(scenario.goal):
                match_score = rule.matches_scenario(scenario.current_elements)
                if match_score > 0:
                    applicable_rules.append({
                        'rule': rule,
                        'match_score': match_score,
                        'effectiveness': rule.get_effectiveness(),
                        'type': 'formal',
                        'recommendation_score': match_score * rule.get_effectiveness()
                    })
        
        # 搜索候选规律（如果正式规律不足）
        if len(applicable_rules) < 3:
            for rule_id, rule in self.candidate_rules.items():
                if rule.is_applicable_to_goal(scenario.goal):
                    match_score = rule.matches_scenario(scenario.current_elements)
                    if match_score > 0:
                        applicable_rules.append({
                            'rule': rule,
                            'match_score': match_score,
                            'effectiveness': rule.get_effectiveness(),
                            'type': 'candidate',
                            'recommendation_score': match_score * rule.get_effectiveness() * 0.8  # 候选规律权重降低
                        })
        
        # 按推荐分数排序
        applicable_rules.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return applicable_rules
    
    def make_decision(self, scenario: Scenario, top_k: int = 5) -> Dict[str, Any]:
        """基于场景做出决策"""
        print(f"\n🎯 场景决策分析")
        print(f"场景: {scenario.scenario_id}")
        print(f"目标: {scenario.goal.value}")
        print(f"当前元素: {scenario.current_elements}")
        
        # 查找适用规律
        applicable_rules = self.find_applicable_rules(scenario)
        
        decision_result = {
            'scenario': scenario.to_dict(),
            'applicable_rules_count': len(applicable_rules),
            'recommendations': [],
            'decision_confidence': 0.0
        }
        
        if applicable_rules:
            # 生成推荐
            for i, rule_info in enumerate(applicable_rules[:top_k]):
                rule = rule_info['rule']
                recommendation = {
                    'rank': i + 1,
                    'rule_id': rule.rule_id,
                    'rule_type': rule.rule_type,
                    'conditions': rule.conditions,
                    'predicted_result': rule.result,
                    'match_score': rule_info['match_score'],
                    'effectiveness': rule_info['effectiveness'],
                    'recommendation_score': rule_info['recommendation_score'],
                    'rule_status': rule_info['type']
                }
                decision_result['recommendations'].append(recommendation)
                
                print(f"\n推荐 {i+1}: {' + '.join(rule.conditions)} → {rule.result}")
                print(f"   匹配度: {rule_info['match_score']:.2f}")
                print(f"   有效性: {rule_info['effectiveness']:.2f}")
                print(f"   推荐分数: {rule_info['recommendation_score']:.2f}")
                print(f"   规律状态: {rule_info['type']}")
            
            # 计算决策置信度
            if decision_result['recommendations']:
                decision_result['decision_confidence'] = decision_result['recommendations'][0]['recommendation_score']
        
        else:
            print("❌ 未找到适用的规律")
        
        return decision_result
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            'experiences_count': len(self.experiences),
            'candidate_rules_count': len(self.candidate_rules),
            'formal_rules_count': len(self.formal_rules),
            'total_rules_count': len(self.candidate_rules) + len(self.formal_rules),
            'goal_distribution': self._get_goal_distribution(),
            'rule_type_distribution': self._get_rule_type_distribution()
        }
    
    def _get_goal_distribution(self) -> Dict[str, int]:
        """获取目标分布"""
        goal_count = defaultdict(int)
        for rule in list(self.candidate_rules.values()) + list(self.formal_rules.values()):
            for goal in rule.applicable_goals:
                goal_count[goal.value] += 1
        return dict(goal_count)
    
    def _get_rule_type_distribution(self) -> Dict[str, int]:
        """获取规律类型分布"""
        type_count = defaultdict(int)
        for rule in list(self.candidate_rules.values()) + list(self.formal_rules.values()):
            type_count[rule.rule_type] += 1
        return dict(type_count)

def demonstrate_unified_system():
    """演示统一系统"""
    print("🚀 统一知识决策系统演示")
    print("=" * 80)
    
    # 创建系统
    system = UnifiedKnowledgeDecisionSystem()
    
    # 添加经验
    experiences = [
        Experience(
            experience_id="exp_001",
            environment="森林",
            object="老虎",
            characteristics="尖牙_凶猛_快速",
            action="靠近",
            tools="无武器",
            result="受伤_血量-20_经验+5",
            success=False,
            timestamp=time.time(),
            player_id="player_001"
        ),
        Experience(
            experience_id="exp_002",
            environment="森林",
            object="草莓",
            characteristics="红色_成熟_甜美",
            action="采集",
            tools="篮子",
            result="获取食物_食物+5_经验+2",
            success=True,
            timestamp=time.time(),
            player_id="player_001"
        ),
        Experience(
            experience_id="exp_003",
            environment="水域",
            object="河流",
            characteristics="清澈_流动_深度适中",
            action="饮水",
            tools="无工具",
            result="获取水_水分+10_口渴-5",
            success=True,
            timestamp=time.time(),
            player_id="player_001"
        )
    ]
    
    print("\n📝 添加经验并生成规律:")
    for exp in experiences:
        result = system.add_experience(exp)
        print(f"经验添加结果: 新经验={result['experience_added']}, 候选规律={result['candidate_rules_generated']}, 正式规律={result['formal_rules_promoted']}")
    
    # 显示系统统计
    stats = system.get_system_statistics()
    print(f"\n📊 系统统计:")
    print(f"经验数: {stats['experiences_count']}")
    print(f"候选规律数: {stats['candidate_rules_count']}")
    print(f"正式规律数: {stats['formal_rules_count']}")
    print(f"目标分布: {stats['goal_distribution']}")
    print(f"规律类型分布: {stats['rule_type_distribution']}")
    
    # 场景决策演示
    scenarios = [
        Scenario(
            scenario_id="scenario_001",
            current_elements=["ENV:森林", "OBJ:老虎", "CHAR:凶猛"],
            goal=GoalType.SURVIVAL,
            priority=1.0
        ),
        Scenario(
            scenario_id="scenario_002", 
            current_elements=["ENV:森林", "OBJ:草莓", "TOOL:篮子"],
            goal=GoalType.RESOURCE,
            priority=0.8
        )
    ]
    
    print(f"\n🎯 场景决策演示:")
    for scenario in scenarios:
        decision = system.make_decision(scenario)
        print(f"\n场景 {scenario.scenario_id} 决策完成:")
        print(f"找到 {decision['applicable_rules_count']} 条适用规律")
        print(f"决策置信度: {decision['decision_confidence']:.2f}")

if __name__ == "__main__":
    demonstrate_unified_system() 