#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一EOCATR格式系统
实现完整的E-O-C-A-T-R格式标准化
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

class EnvironmentType(Enum):
    """环境类型枚举"""
    OPEN_FIELD = "open_field"
    FOREST = "forest" 
    WATER_AREA = "water_area"
    MOUNTAIN = "mountain"
    CAVE = "cave"

class ObjectType(Enum):
    """对象类型枚举"""
    EDIBLE_PLANT = "edible_plant"
    WATER_SOURCE = "water_source"
    PREDATOR = "predator"
    PREY = "prey"
    TOOL_MATERIAL = "tool_material"
    SHELTER_MATERIAL = "shelter_material"

class ActionType(Enum):
    """动作类型枚举"""
    GATHER = "gather"
    DRINK = "drink"
    MOVE = "move"
    AVOID = "avoid"
    ATTACK = "attack"
    REST = "rest"
    EXPLORE = "explore"

class ToolType(Enum):
    """工具类型枚举"""
    BASKET = "basket"
    SPEAR = "spear"
    STONE = "stone"
    NO_TOOL = "no_tool"
    BARE_HANDS = "bare_hands"

class ResultType(Enum):
    """结果类型枚举"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"

@dataclass
class CharacteristicsMulti:
    """多维特征结构 - 支持C1,C2,C3等多个属性"""
    # C1: 距离特征
    distance: float = 1.0
    distance_category: str = "近距离"  # 近距离、中距离、远距离
    
    # C2: 安全特征  
    safety_level: float = 0.5  # 0.0(极危险) - 1.0(极安全)
    danger_type: str = "无"  # 无、轻微、中等、严重
    
    # C3: 资源特征
    resource_value: float = 0.5  # 0.0(无价值) - 1.0(极高价值)
    resource_type: str = "未知"  # 食物、水源、工具、材料
    
    # C4: 可获得性特征
    accessibility: float = 0.5  # 0.0(无法获得) - 1.0(容易获得)
    effort_required: str = "中等"  # 容易、中等、困难、极难
    
    # C5: 状态特征
    freshness: float = 1.0  # 新鲜度/完整度
    condition: str = "良好"  # 良好、一般、较差、损坏
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'c1_distance': self.distance,
            'c1_distance_category': self.distance_category,
            'c2_safety_level': self.safety_level,
            'c2_danger_type': self.danger_type,
            'c3_resource_value': self.resource_value,
            'c3_resource_type': self.resource_type,
            'c4_accessibility': self.accessibility,
            'c4_effort_required': self.effort_required,
            'c5_freshness': self.freshness,
            'c5_condition': self.condition
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载数据"""
        self.distance = data.get('c1_distance', 1.0)
        self.distance_category = data.get('c1_distance_category', '近距离')
        self.safety_level = data.get('c2_safety_level', 0.5)
        self.danger_type = data.get('c2_danger_type', '无')
        self.resource_value = data.get('c3_resource_value', 0.5)
        self.resource_type = data.get('c3_resource_type', '未知')
        self.accessibility = data.get('c4_accessibility', 0.5)
        self.effort_required = data.get('c4_effort_required', '中等')
        self.freshness = data.get('c5_freshness', 1.0)
        self.condition = data.get('c5_condition', '良好')

@dataclass
class UnifiedEOCATR:
    """统一的EOCATR经验格式"""
    # 六大核心要素
    environment: EnvironmentType
    object: ObjectType
    characteristics: CharacteristicsMulti
    action: ActionType
    tool: ToolType
    result: ResultType
    
    # 结果详情
    success: bool = True
    reward: float = 0.0
    
    # 元数据
    experience_id: str = ""
    player_id: str = ""
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0
    
    def __post_init__(self):
        if not self.experience_id:
            self.experience_id = self.generate_experience_id()
    
    def generate_experience_id(self) -> str:
        """生成经验唯一ID"""
        content = f"{self.environment.value}_{self.object.value}_{self.action.value}_{self.tool.value}_{self.result.value}_{int(self.timestamp)}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"EXP_{hash_value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'experience_id': self.experience_id,
            'environment': self.environment.value,
            'object': self.object.value,
            'characteristics': self.characteristics.to_dict(),
            'action': self.action.value,
            'tool': self.tool.value,
            'result': self.result.value,
            'success': self.success,
            'reward': self.reward,
            'player_id': self.player_id,
            'timestamp': self.timestamp,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedEOCATR':
        """从字典创建EOCATR经验"""
        characteristics = CharacteristicsMulti()
        if 'characteristics' in data:
            characteristics.from_dict(data['characteristics'])
        
        return cls(
            environment=EnvironmentType(data['environment']),
            object=ObjectType(data['object']),
            characteristics=characteristics,
            action=ActionType(data['action']),
            tool=ToolType(data['tool']),
            result=ResultType(data['result']),
            success=data.get('success', True),
            reward=data.get('reward', 0.0),
            experience_id=data.get('experience_id', ''),
            player_id=data.get('player_id', ''),
            timestamp=data.get('timestamp', time.time()),
            confidence=data.get('confidence', 1.0)
        )

@dataclass
class SimpleRule:
    """简化的规律格式 - 支持E-A-R, E-T-R, O-A-R, O-T-R, C-A-R, C-T-R"""
    rule_id: str
    rule_type: str  # 'E-A-R', 'E-T-R', 'O-A-R', 'O-T-R', 'C1-A-R', 'C1-T-R', 'C2-A-R', etc.
    
    # 条件部分
    condition_element: str  # 环境、对象或特征值
    condition_type: str     # 'environment', 'object', 'characteristic'
    
    # 动作/工具部分  
    action_or_tool: str     # 动作或工具
    action_tool_type: str   # 'action' or 'tool'
    
    # 结果部分
    expected_result: str    # 预期结果
    
    # 可选字段
    condition_subtype: str = ""  # 对于特征：'c1', 'c2', 'c3'等
    
    success_rate: float = 0.0
    confidence: float = 0.0
    
    # 统计信息
    support_count: int = 0
    total_count: int = 0
    
    # 元数据
    created_time: float = field(default_factory=time.time)
    player_id: str = ""
    
    @property
    def pattern_elements(self):
        """BMP兼容性：提供pattern_elements属性用于旧代码兼容"""
        # 创建模拟的pattern_elements，用简单的content属性类包装
        class PatternElement:
            def __init__(self, content):
                self.content = content
        
        # 根据规律类型构建模式元素
        elements = []
        elements.append(PatternElement(self.condition_element))
        elements.append(PatternElement(self.action_or_tool))
        elements.append(PatternElement(self.expected_result))
        return elements
    
    @property
    def pattern(self):
        """BMP兼容性：提供pattern属性用于旧代码兼容"""
        return f"{self.condition_element} + {self.action_or_tool} → {self.expected_result}"
    
    @property
    def generation_method(self):
        """BMP兼容性：提供generation_method属性用于旧代码兼容"""
        return f"simplified_{self.rule_type.lower().replace('-', '_')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'rule_id': self.rule_id,
            'rule_type': self.rule_type,
            'condition_element': self.condition_element,
            'condition_type': self.condition_type,
            'condition_subtype': self.condition_subtype,
            'action_or_tool': self.action_or_tool,
            'action_tool_type': self.action_tool_type,
            'expected_result': self.expected_result,
            'success_rate': self.success_rate,
            'confidence': self.confidence,
            'support_count': self.support_count,
            'total_count': self.total_count,
            'created_time': self.created_time,
            'player_id': self.player_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimpleRule':
        """从字典创建规律"""
        return cls(
            rule_id=data['rule_id'],
            rule_type=data['rule_type'],
            condition_element=data['condition_element'],
            condition_type=data['condition_type'],
            condition_subtype=data.get('condition_subtype', ''),
            action_or_tool=data['action_or_tool'],
            action_tool_type=data['action_tool_type'],
            expected_result=data['expected_result'],
            success_rate=data.get('success_rate', 0.0),
            confidence=data.get('confidence', 0.0),
            support_count=data.get('support_count', 0),
            total_count=data.get('total_count', 0),
            created_time=data.get('created_time', time.time()),
            player_id=data.get('player_id', '')
        )

@dataclass  
class SimpleDecision:
    """简化的决策格式 - R1(E-T-R) 或 R1(E-T-R)+R2(C-A-R)"""
    decision_id: str
    
    # 决策组成（可以是单条规律或两条规律的组合）
    primary_rule: SimpleRule
    
    # 决策结果
    recommended_action: str
    
    # 可选字段
    secondary_rule: Optional[SimpleRule] = None
    recommended_tool: str = "no_tool"
    expected_outcome: str = ""
    combined_confidence: float = 0.0
    
    # 元数据
    context: Dict[str, Any] = field(default_factory=dict)
    created_time: float = field(default_factory=time.time)
    player_id: str = ""
    
    def to_format_string(self) -> str:
        """生成格式化的决策字符串"""
        if self.secondary_rule is None:
            return f"R1({self.primary_rule.rule_type})"
        else:
            return f"R1({self.primary_rule.rule_type})+R2({self.secondary_rule.rule_type})"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'decision_id': self.decision_id,
            'primary_rule': self.primary_rule.to_dict(),
            'secondary_rule': self.secondary_rule.to_dict() if self.secondary_rule else None,
            'recommended_action': self.recommended_action,
            'recommended_tool': self.recommended_tool,
            'expected_outcome': self.expected_outcome,
            'combined_confidence': self.combined_confidence,
            'context': self.context,
            'created_time': self.created_time,
            'player_id': self.player_id,
            'format_string': self.to_format_string()
        }

# === 格式转换工具函数 ===

def create_unified_eocatr(environment: str, object_name: str, action: str, 
                         tool: str = "no_tool", result: str = "success",
                         characteristics: Dict[str, Any] = None,
                         player_id: str = "", success: bool = True,
                         reward: float = 0.0) -> UnifiedEOCATR:
    """创建统一EOCATR经验的便捷函数"""
    
    # 构建多维特征
    chars = CharacteristicsMulti()
    if characteristics:
        chars.from_dict(characteristics)
    
    return UnifiedEOCATR(
        environment=EnvironmentType(environment),
        object=ObjectType(object_name),
        characteristics=chars,
        action=ActionType(action),
        tool=ToolType(tool),
        result=ResultType(result),
        success=success,
        reward=reward,
        player_id=player_id
    )

def generate_all_simple_rules_from_experience(experience: UnifiedEOCATR) -> List[SimpleRule]:
    """从单个EOCATR经验生成所有可能的简单规律"""
    rules = []
    base_time = time.time()
    
    # E-A-R 规律
    rules.append(SimpleRule(
        rule_id=f"EAR_{int(base_time)}_{len(rules)}",
        rule_type="E-A-R",
        condition_element=getattr(experience.environment, "value", "unknown"),
        condition_type="environment", 
        action_or_tool=getattr(experience.action, "value", "unknown"),
        action_tool_type="action",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # E-T-R 规律
    rules.append(SimpleRule(
        rule_id=f"ETR_{int(base_time)}_{len(rules)}",
        rule_type="E-T-R",
        condition_element=getattr(experience.environment, "value", "unknown"),
        condition_type="environment",
        action_or_tool=getattr(experience.tool, "value", "unknown"),
        action_tool_type="tool", 
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # O-A-R 规律
    rules.append(SimpleRule(
        rule_id=f"OAR_{int(base_time)}_{len(rules)}",
        rule_type="O-A-R",
        condition_element=getattr(experience.object, "value", "unknown"),
        condition_type="object",
        action_or_tool=getattr(experience.action, "value", "unknown"),
        action_tool_type="action",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # O-T-R 规律
    rules.append(SimpleRule(
        rule_id=f"OTR_{int(base_time)}_{len(rules)}",
        rule_type="O-T-R",
        condition_element=getattr(experience.object, "value", "unknown"),
        condition_type="object",
        action_or_tool=getattr(experience.tool, "value", "unknown"),
        action_tool_type="tool",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C1-A-R 规律 (距离特征)
    c1_element = "normal"
    if hasattr(experience, 'characteristics') and experience.characteristics:
        c1_element = getattr(experience.characteristics, 'distance_category', 'normal')
    elif hasattr(experience, 'character') and experience.character:
        c1_element = getattr(experience.character, 'content', 'normal')
    
    rules.append(SimpleRule(
        rule_id=f"C1AR_{int(base_time)}_{len(rules)}",
        rule_type="C1-A-R",
        condition_element=c1_element,
        condition_type="characteristic",
        condition_subtype="c1",
        action_or_tool=getattr(experience.action, "value", "unknown"),
        action_tool_type="action",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C1-T-R 规律 (距离特征)
    rules.append(SimpleRule(
        rule_id=f"C1TR_{int(base_time)}_{len(rules)}",
        rule_type="C1-T-R",
        condition_element=c1_element,
        condition_type="characteristic",
        condition_subtype="c1",
        action_or_tool=getattr(experience.tool, "value", "unknown"),
        action_tool_type="tool",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C2-A-R 规律 (安全特征)
    c2_element = "normal"
    if hasattr(experience, 'characteristics') and experience.characteristics:
        c2_element = getattr(experience.characteristics, 'danger_type', 'normal')
    elif hasattr(experience, 'character') and experience.character:
        c2_element = getattr(experience.character, 'content', 'normal')
    
    rules.append(SimpleRule(
        rule_id=f"C2AR_{int(base_time)}_{len(rules)}",
        rule_type="C2-A-R",
        condition_element=c2_element,
        condition_type="characteristic",
        condition_subtype="c2",
        action_or_tool=getattr(experience.action, "value", "unknown"),
        action_tool_type="action",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C2-T-R 规律 (安全特征)
    rules.append(SimpleRule(
        rule_id=f"C2TR_{int(base_time)}_{len(rules)}",
        rule_type="C2-T-R",
        condition_element=c2_element,
        condition_type="characteristic",
        condition_subtype="c2",
        action_or_tool=getattr(experience.tool, "value", "unknown"),
        action_tool_type="tool",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C3-A-R 规律 (资源特征)
    c3_element = "normal"
    if hasattr(experience, 'characteristics') and experience.characteristics:
        c3_element = getattr(experience.characteristics, 'resource_type', 'normal')
    elif hasattr(experience, 'character') and experience.character:
        c3_element = getattr(experience.character, 'content', 'normal')
    
    rules.append(SimpleRule(
        rule_id=f"C3AR_{int(base_time)}_{len(rules)}",
        rule_type="C3-A-R",
        condition_element=c3_element,
        condition_type="characteristic",
        condition_subtype="c3",
        action_or_tool=getattr(experience.action, "value", "unknown"),
        action_tool_type="action",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    # C3-T-R 规律 (资源特征)
    rules.append(SimpleRule(
        rule_id=f"C3TR_{int(base_time)}_{len(rules)}",
        rule_type="C3-T-R",
        condition_element=c3_element,
        condition_type="characteristic",
        condition_subtype="c3",
        action_or_tool=getattr(experience.tool, "value", "unknown"),
        action_tool_type="tool",
        expected_result=getattr(experience.result, "value", "unknown"),
        success_rate=1.0 if getattr(experience, 'success', True) else 0.0,
        confidence=getattr(experience, 'confidence', 1.0),
        support_count=1,
        total_count=1,
        player_id=getattr(experience, 'player_id', 'unknown')
    ))
    
    return rules

def create_simple_decision(primary_rule: SimpleRule, secondary_rule: SimpleRule = None,
                          player_id: str = "", context: Dict[str, Any] = None) -> SimpleDecision:
    """创建简单决策的便捷函数"""
    decision_id = f"DEC_{int(time.time())}_{primary_rule.rule_id[:8]}"
    
    # 确定推荐动作和工具
    if primary_rule.action_tool_type == "action":
        recommended_action = primary_rule.action_or_tool
        recommended_tool = secondary_rule.action_or_tool if secondary_rule and secondary_rule.action_tool_type == "tool" else "no_tool"
    else:
        recommended_action = secondary_rule.action_or_tool if secondary_rule and secondary_rule.action_tool_type == "action" else "explore"
        recommended_tool = primary_rule.action_or_tool
    
    # 计算组合置信度
    combined_confidence = primary_rule.confidence
    if secondary_rule:
        combined_confidence = (primary_rule.confidence + secondary_rule.confidence) / 2.0
    
    return SimpleDecision(
        decision_id=decision_id,
        primary_rule=primary_rule,
        secondary_rule=secondary_rule,
        recommended_action=recommended_action,
        recommended_tool=recommended_tool,
        expected_outcome=primary_rule.expected_result,
        combined_confidence=combined_confidence,
        context=context or {},
        player_id=player_id
    ) 