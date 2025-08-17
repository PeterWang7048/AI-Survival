#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
木桥模型 (Wooden Bridge Model, WBM)

基于Stanford 4.0文档设计的目标驱动规律应用机制。
实现智能体在特定目标驱动下，选择、组合并应用已学习规律以构建解决方案的核心策略。

核心思想：
- "对岸" = 智能体的目标（觅食、避险、探索等）
- "木头" = 已掌握的规律（认知规律、行动规律E-O-RA）
- "搭桥" = 选择、组合规律构建解决方案
- "过桥" = 执行方案并验证有效性

首尾搭接机制（新增）：
- "规律接头" = 规律之间的连接点，具有语义类别和抽象大小
- "首尾衔接" = 规律间通过接头相连，形成连续的推理链
- "双向逼近" = 从当前状态和目标状态同时出发，中间会合

作者：AI生存游戏项目组
版本：1.5.0 - 新增规律接头机制
"""

import math
import time
import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from enum import Enum
from collections import defaultdict, deque
import json

# 导入符号化系统支持
try:
    from symbolic_core_v3 import SymbolicElement, SymbolType, AbstractionLevel
except ImportError:
    # 提供基础兼容支持
    from enum import Enum
    class SymbolType(Enum):
        ENVIRONMENT = "Environment"
        OBJECT = "Object"
        CONDITION = "Condition"
        ACTION = "Action"
        TOOL = "Tool"
        RESULT = "Result"
    
    class AbstractionLevel(Enum):
        CONCRETE = 1
        CATEGORY = 2
        CONCEPT = 3
        ABSTRACT = 4

# ============================================================================
# 规律接头机制 (Rule Interface System)
# ============================================================================

@dataclass
class RuleInterface:
    """
    规律接头 - 实现规律间的首尾搭接
    
    核心概念：
    - 形状：语义类别（如环境、动物、植物等）
    - 大小：抽象层级（黑熊＜熊＜猛兽＜动物＜资源）
    - 镜像：语义反向对接（靠近↔远离）
    """
    element: Any                         # 接头元素（可以是字符串或SymbolicElement）
    semantic_category: str               # 语义类别：动物、植物、环境、动作等
    abstraction_size: int                # 抽象大小：1=具体 → 5=抽象
    interface_type: str                  # 接头类型：head（头部）或 tail（尾部）
    mirror_semantics: Optional[str] = None  # 镜像语义（如 "靠近"的镜像是"远离"）
    
    def __post_init__(self):
        """初始化后处理"""
        if self.abstraction_size < 1:
            self.abstraction_size = 1
        elif self.abstraction_size > 5:
            self.abstraction_size = 5
    
    def get_element_content(self) -> str:
        """获取元素内容字符串"""
        if hasattr(self.element, 'content'):
            return self.element.content
        elif hasattr(self.element, 'name'):
            return self.element.name
        else:
            return str(self.element)
    
    def can_connect_to(self, other: 'RuleInterface') -> Tuple[bool, float]:
        """
        检查能否与另一个接头连接
        
        连接规则：
        1. 语义类别必须相同或相关
        2. 下一规律的头部抽象大小 <= 当前规律的尾部抽象大小
        3. 镜像语义可以实现反向连接
        
        Returns:
            (can_connect, connection_strength)
        """
        # 规则1：语义类别检查
        category_compatible = self._check_category_compatibility(other)
        if not category_compatible:
            return False, 0.0
        
        # 规则2：抽象大小检查（正向连接）
        size_compatible = False
        connection_strength = 0.0
        
        if self.interface_type == "tail" and other.interface_type == "head":
            # 正向连接：tail → head
            if other.abstraction_size <= self.abstraction_size:
                size_compatible = True
                # 连接强度：相同大小最强，差距越大强度越弱
                size_diff = self.abstraction_size - other.abstraction_size
                connection_strength = max(0.1, 1.0 - size_diff * 0.2)
        
        # 规则3：镜像语义检查
        mirror_compatible = self._check_mirror_compatibility(other)
        if mirror_compatible:
            connection_strength = max(connection_strength, 0.7)  # 镜像连接有固定强度
            size_compatible = True
        
        # 内容相似度加成
        content_similarity = self._calculate_content_similarity(other)
        connection_strength += content_similarity * 0.3
        connection_strength = min(1.0, connection_strength)
        
        return size_compatible, connection_strength
    
    def _check_category_compatibility(self, other: 'RuleInterface') -> bool:
        """检查语义类别兼容性（增强版）"""
        # 相同类别
        if self.semantic_category == other.semantic_category:
            return True
        
        # 🔧 修复：增加跨类别兼容性规则
        cross_category_compatibility = {
            # 环境 → 动作：环境可以触发动作
            ("环境", "动作"): True,
            ("动作", "环境"): True,
            
            # 动物 → 动作：动物可以触发动作 
            ("动物", "动作"): True,
            ("动作", "动物"): True,
            
            # 植物 → 动作：植物可以触发动作
            ("植物", "动作"): True,
            ("动作", "植物"): True,
            
            # 动作 → 结果：动作可以产生结果
            ("动作", "结果"): True,
            ("结果", "动作"): True,
            
            # 环境 → 结果：环境可以影响结果
            ("环境", "结果"): True,
            ("结果", "环境"): True,
            
            # 特征 → 动作：特征可以影响动作选择
            ("特征", "动作"): True,
            ("动作", "特征"): True,
            
            # 通用类别兼容
            ("通用", "动作"): True,
            ("动作", "通用"): True,
            ("通用", "环境"): True,
            ("环境", "通用"): True,
        }
        
        # 检查跨类别兼容性
        category_pair = (self.semantic_category, other.semantic_category)
        if category_pair in cross_category_compatibility:
            return cross_category_compatibility[category_pair]
        
        # 相关类别映射（原有逻辑保留）
        related_categories = {
            "动物": ["猛兽", "草食动物", "危险动物", "无害动物"],
            "植物": ["可食植物", "有毒植物", "地面植物", "地下植物", "树上植物"],
            "动作": ["移动", "攻击", "采集", "躲避", "互动", "探索", "收集", "逃跑"],
            "环境": ["森林", "开阔地", "水域", "安全区", "危险区", "forest"],
            "特征": ["危险特征", "外观特征", "大小特征", "行为特征"],
            "结果": ["安全", "食物", "水分", "受伤", "死亡"]
        }
        
        for main_category, sub_categories in related_categories.items():
            if (self.semantic_category == main_category and other.semantic_category in sub_categories) or \
               (other.semantic_category == main_category and self.semantic_category in sub_categories) or \
               (self.semantic_category in sub_categories and other.semantic_category in sub_categories):
                return True
        
        return False
    
    def _check_mirror_compatibility(self, other: 'RuleInterface') -> bool:
        """检查镜像语义兼容性"""
        if not self.mirror_semantics or not other.mirror_semantics:
            return False
        
        # 预定义的镜像对
        mirror_pairs = {
            "靠近": "远离",
            "远离": "靠近", 
            "攻击": "防御",
            "防御": "攻击",
            "收集": "丢弃",
            "丢弃": "收集",
            "进入": "离开",
            "离开": "进入"
        }
        
        return (self.mirror_semantics == other.get_element_content() or 
                other.mirror_semantics == self.get_element_content() or
                mirror_pairs.get(self.mirror_semantics) == other.get_element_content())
    
    def _calculate_content_similarity(self, other: 'RuleInterface') -> float:
        """计算内容相似度"""
        self_content = self.get_element_content().lower()
        other_content = other.get_element_content().lower()
        
        # 简单字符串相似度
        if self_content == other_content:
            return 1.0
        
        # 包含关系
        if self_content in other_content or other_content in self_content:
            return 0.7
        
        # 共同词汇
        self_words = set(self_content.split())
        other_words = set(other_content.split())
        common_words = self_words & other_words
        
        if common_words:
            return len(common_words) / max(len(self_words), len(other_words))
        
        return 0.0

@dataclass
class EnhancedRule:
    """
    增强规律类 - 支持接头机制的规律
    """
    base_rule: 'Rule'                    # 原始规律
    head_interface: RuleInterface        # 头部接头
    tail_interface: RuleInterface        # 尾部接头
    rule_semantic_type: str = "general"  # 规律语义类型
    
    def get_rule_id(self) -> str:
        """获取规律ID"""
        return self.base_rule.rule_id
    
    def get_confidence(self) -> float:
        """获取置信度"""
        return self.base_rule.confidence
    
    def can_chain_to(self, next_rule: 'EnhancedRule') -> Tuple[bool, float]:
        """检查能否连接到下一个规律"""
        return self.tail_interface.can_connect_to(next_rule.head_interface)

class RuleChainBuilder:
    """
    规律链构建器 - 实现首尾搭接的核心逻辑
    """
    
    def __init__(self, logger=None):
        self.logger = logger
        self.semantic_hierarchy = self._build_semantic_hierarchy()
        self.mirror_semantics = self._build_mirror_semantics()
    
    def _build_semantic_hierarchy(self) -> Dict[str, int]:
        """构建语义层级关系"""
        return {
            # 动物层级
            "老虎": 1, "黑熊": 1, "野猪": 1, "兔子": 1,
            "猛兽": 2, "草食动物": 2, "小动物": 2,
            "危险动物": 2, "无害动物": 2,
            "动物": 3, "生物": 4, "资源": 5,
            
            # 植物层级
            "苹果": 1, "浆果": 1, "毒蘑菇": 1,
            "可食植物": 2, "有毒植物": 2,
            "植物": 3, "食物": 4,
            
            # 特征层级
            "尖牙利爪": 1, "条纹": 1, "大": 1, "小": 1,
            "危险特征": 2, "外观特征": 2, "大小特征": 2,
            "特征": 3,
            
            # 动作层级
            "靠近": 1, "远离": 1, "攻击": 1, "采集": 1, "躲避": 1,
            "移动": 2, "交互": 2, "获取": 2,
            "行为": 3, "动作": 4,
            
            # 环境层级
            "森林": 1, "河流": 1, "山洞": 1,
            "自然环境": 2, "安全区": 2, "危险区": 2,
            "环境": 3, "地点": 4,
            
            # 结果层级
            "受伤": 1, "死亡": 1, "饱食": 1, "解渴": 1,
            "伤害": 2, "满足": 2, "收获": 2,
            "状态变化": 3, "结果": 4
        }
    
    def _build_mirror_semantics(self) -> Dict[str, str]:
        """构建镜像语义映射"""
        return {
            "靠近": "远离", "远离": "靠近",
            "攻击": "防御", "防御": "攻击", 
            "收集": "丢弃", "丢弃": "收集",
            "进入": "离开", "离开": "进入",
            "上升": "下降", "下降": "上升",
            "增加": "减少", "减少": "增加"
        }
    
    def enhance_rule(self, rule: 'Rule') -> EnhancedRule:
        """将普通规律转换为增强规律（支持接头）"""
        head_interface = self._extract_head_interface(rule)
        tail_interface = self._extract_tail_interface(rule)
        
        return EnhancedRule(
            base_rule=rule,
            head_interface=head_interface,
            tail_interface=tail_interface,
            rule_semantic_type=self._determine_rule_semantic_type(rule)
        )
    
    def _extract_head_interface(self, rule: 'Rule') -> RuleInterface:
        """从规律中提取头部接头"""
        # 头部通常是规律的条件部分
        conditions = rule.conditions
        condition_elements = rule.condition_elements
        
        # 🔧 类型安全检查：确保conditions是字典
        if not isinstance(conditions, dict):
            if isinstance(conditions, list):
                # 如果是列表，转换为字典
                conditions = {f"condition_{i}": item for i, item in enumerate(conditions)}
            else:
                # 其他类型，转换为字符串
                conditions = {"condition": str(conditions)}
        
        # 🔧 类型安全检查：确保condition_elements是列表
        if not isinstance(condition_elements, list):
            if condition_elements is None:
                condition_elements = []
            elif isinstance(condition_elements, dict):
                condition_elements = [f"{k}={v}" for k, v in condition_elements.items()]
            else:
                condition_elements = [str(condition_elements)]
        
        # 按优先级查找关键字段
        priority_keys = ['object', 'category', 'features', 'characteristics', 'environment']
        
        element = None
        category = "通用"
        
        # 首先从conditions字典中查找
        for key in priority_keys:
            if key in conditions:
                element = conditions[key]
                category = self._determine_semantic_category(element)
                break
        
        # 如果conditions字典中没找到，从condition_elements中提取
        if element is None and condition_elements:
            for cond_elem in condition_elements:
                if '=' in cond_elem:
                    key, value = cond_elem.split('=', 1)
                    if key in priority_keys:
                        element = value
                        category = self._determine_semantic_category(element)
                        break
        
        # 如果还是没找到，使用第一个条件
        if element is None and conditions:
            first_key = list(conditions.keys())[0]
            element = conditions[first_key]
            category = self._determine_semantic_category(element)
        elif element is None and condition_elements:
            # 使用第一个condition_element
            first_elem = condition_elements[0]
            if '=' in first_elem:
                element = first_elem.split('=', 1)[1]
            else:
                element = first_elem
            category = self._determine_semantic_category(element)
        
        # 如果还是没有，使用默认值
        if element is None:
            element = "未知"
            category = "通用"
        
        size = self.semantic_hierarchy.get(str(element).lower(), 3)
        mirror = self.mirror_semantics.get(str(element).lower())
        
        return RuleInterface(
            element=element,
            semantic_category=category,
            abstraction_size=size,
            interface_type="head",
            mirror_semantics=mirror
        )
    
    def _extract_tail_interface(self, rule: 'Rule') -> RuleInterface:
        """从规律中提取尾部接头"""
        # 尾部通常是规律的结果部分
        predictions = rule.predictions
        expected_result = rule.expected_result
        
        # 🔧 类型安全检查：确保predictions是字典
        if not isinstance(predictions, dict):
            if isinstance(predictions, list):
                # 如果是列表，转换为字典
                predictions = {f"prediction_{i}": item for i, item in enumerate(predictions)}
            else:
                # 其他类型，转换为字符串
                predictions = {"prediction": str(predictions)}
        
        # 🔧 类型安全检查：确保expected_result是字典
        if not isinstance(expected_result, dict):
            if isinstance(expected_result, list):
                # 如果是列表，转换为字典
                expected_result = {f"result_{i}": item for i, item in enumerate(expected_result)}
            elif expected_result is None:
                expected_result = {}
            else:
                # 其他类型，转换为字符串
                expected_result = {"result": str(expected_result)}
        
        # 按优先级查找关键字段
        priority_keys = ['result', 'action', 'category', 'characteristics', 'features']
        
        element = None
        category = "结果"
        
        # 首先从predictions字典中查找
        for key in priority_keys:
            if key in predictions:
                element = predictions[key]
                if key == 'action':
                    category = "动作"
                elif key in ['category', 'characteristics', 'features']:
                    category = self._determine_semantic_category(element)
                else:
                    category = self._determine_semantic_category(element)
                break
        
        # 如果predictions中没找到，从expected_result中查找
        if element is None and expected_result:
            for key in priority_keys:
                if key in expected_result:
                    element = expected_result[key]
                if key == 'action':
                    category = "动作"
                elif key in ['category', 'characteristics', 'features']:
                    category = self._determine_semantic_category(element)
                else:
                    category = self._determine_semantic_category(element)
                break
        
        # 如果没找到，使用第一个预测
        if element is None and predictions:
            first_key = list(predictions.keys())[0]
            element = predictions[first_key]
            category = self._determine_semantic_category(element)
        elif element is None and expected_result:
            first_key = list(expected_result.keys())[0]
            element = expected_result[first_key]
            category = self._determine_semantic_category(element)
        
        # 如果还是没有，使用默认值
        if element is None:
            element = "未知"
            category = "结果"
        
        size = self.semantic_hierarchy.get(str(element).lower(), 3)
        mirror = self.mirror_semantics.get(str(element).lower())
        
        return RuleInterface(
            element=element,
            semantic_category=category,
            abstraction_size=size,
            interface_type="tail",
            mirror_semantics=mirror
        )
    
    def _determine_semantic_category(self, element: Any) -> str:
        """确定元素的语义类别"""
        element_str = str(element).lower()
        
        # 动物相关
        if any(animal in element_str for animal in ["老虎", "熊", "野猪", "兔子", "动物", "猛兽"]):
            return "动物"
        
        # 植物相关
        if any(plant in element_str for plant in ["植物", "苹果", "浆果", "蘑菇", "食物"]):
            return "植物"
        
        # 动作相关
        if any(action in element_str for action in ["靠近", "远离", "攻击", "采集", "移动", "躲避"]):
            return "动作"
        
        # 环境相关
        if any(env in element_str for env in ["森林", "河流", "山洞", "环境", "地点"]):
            return "环境"
        
        # 特征相关
        if any(feature in element_str for feature in ["尖牙", "利爪", "条纹", "大", "小", "特征"]):
            return "特征"
        
        # 结果相关
        if any(result in element_str for result in ["受伤", "死亡", "安全", "满足", "结果"]):
            return "结果"
        
        return "通用"
    
    def _determine_rule_semantic_type(self, rule: 'Rule') -> str:
        """确定规律的语义类型"""
        if hasattr(rule, 'rule_type'):
            return rule.rule_type
        
        # 根据规律内容推断
        conditions_str = str(rule.condition_elements).lower()
        predictions_str = str(rule.predictions).lower()
        full_text = conditions_str + " " + predictions_str
        
        if any(word in full_text for word in ["危险", "攻击", "逃跑", "受伤"]):
            return "survival"
        elif any(word in full_text for word in ["食物", "采集", "收集", "吃"]):
            return "food"
        elif any(word in full_text for word in ["水", "喝", "饮用"]):
            return "water"
        elif any(word in full_text for word in ["工具", "石头", "武器"]):
            return "tool"
        else:
            return "general"
    
    def build_rule_chain(self, enhanced_rules: List[EnhancedRule], 
                        start_state: Dict[str, Any],
                        target_state: Dict[str, Any],
                        direction: str = "forward") -> Optional[List[EnhancedRule]]:
        """
        构建规律链
        
        Args:
            enhanced_rules: 增强规律列表
            start_state: 起始状态
            target_state: 目标状态  
            direction: "forward", "backward", "bidirectional"
        """
        if direction == "forward":
            return self._build_forward_chain(enhanced_rules, start_state, target_state)
        elif direction == "backward":
            return self._build_backward_chain(enhanced_rules, start_state, target_state)
        elif direction == "bidirectional":
            return self._build_bidirectional_chain(enhanced_rules, start_state, target_state)
        else:
            if self.logger:
                self.logger.log(f"未知的链构建方向: {direction}")
            return None
    
    def _build_forward_chain(self, enhanced_rules: List[EnhancedRule],
                            start_state: Dict[str, Any],
                            target_state: Dict[str, Any]) -> Optional[List[EnhancedRule]]:
        """正向构建规律链：从当前状态到目标状态"""
        if self.logger:
            self.logger.log(f"🔗 正向链构建开始 | 可用规律: {len(enhanced_rules)} | 起始状态: {start_state} | 目标状态: {target_state}")
        
        chain = []
        current_state = start_state.copy()
        remaining_rules = enhanced_rules.copy()
        
        max_chain_length = 8  # 增加到8，允许更长的规律链  # 防止无限循环
        
        iteration = 0
        while len(chain) < max_chain_length and not self._state_matches_target(current_state, target_state):
            iteration += 1
            if self.logger:
                self.logger.log(f"🔗 正向链构建第{iteration}轮 | 当前链长度: {len(chain)} | 剩余规律: {len(remaining_rules)}")
            
            best_rule = None
            best_score = 0.0
            applicable_rules_count = 0
            
            for rule in remaining_rules:
                if self._rule_applicable_to_state(rule, current_state):
                    applicable_rules_count += 1
                    score = self._calculate_rule_target_relevance(rule, target_state)
                    
                    # 如果已有链，检查接头兼容性
                    if chain:
                        can_connect, connection_strength = chain[-1].can_chain_to(rule)
                        if not can_connect:
                            if self.logger:
                                self.logger.log(f"  ❌ 规律 {rule.get_rule_id()} 接头不兼容 (连接强度: {connection_strength})")
                            continue
                        score *= connection_strength
                        if self.logger:
                            self.logger.log(f"  ✅ 规律 {rule.get_rule_id()} 可连接 (评分: {score:.3f}, 连接强度: {connection_strength:.3f})")
                    else:
                        if self.logger:
                            self.logger.log(f"  🎯 首个规律候选 {rule.get_rule_id()} (评分: {score:.3f})")
                    
                    if score > best_score:
                        best_rule = rule
                        best_score = score
                else:
                    if self.logger:
                        self.logger.log(f"  ❌ 规律 {rule.get_rule_id()} 不适用于当前状态")
            
            if self.logger:
                self.logger.log(f"🔗 第{iteration}轮结果 | 适用规律: {applicable_rules_count} | 最佳规律: {best_rule.get_rule_id() if best_rule else 'None'} | 最佳评分: {best_score:.3f}")
            
            if best_rule is None:
                if self.logger:
                    self.logger.log(f"❌ 正向链构建终止: 无可用规律")
                break
            
            chain.append(best_rule)
            remaining_rules.remove(best_rule)
            old_state = current_state.copy()
            current_state = self._apply_rule_to_state(current_state, best_rule.base_rule)
            
            if self.logger:
                self.logger.log(f"✅ 正向链构建: 添加规律 {best_rule.get_rule_id()} | 当前链长度: {len(chain)}")
                self.logger.log(f"  状态变化: {old_state} → {current_state}")
        
        if self.logger:
            if chain:
                self.logger.log(f"🎉 正向链构建完成 | 最终链长度: {len(chain)} | 目标匹配: {self._state_matches_target(current_state, target_state)}")
            else:
                self.logger.log(f"❌ 正向链构建失败: 无法构建任何链")
        
        return chain if chain else None
    
    def _build_backward_chain(self, enhanced_rules: List[EnhancedRule],
                             start_state: Dict[str, Any], 
                             target_state: Dict[str, Any]) -> Optional[List[EnhancedRule]]:
        """反向构建规律链：从目标状态到当前状态"""
        # 反向链构建的简化实现
        # 实际应用中需要更复杂的逆向推理逻辑
        return self._build_forward_chain(enhanced_rules, start_state, target_state)
    
    def _build_bidirectional_chain(self, enhanced_rules: List[EnhancedRule],
                                  start_state: Dict[str, Any],
                                  target_state: Dict[str, Any]) -> Optional[List[EnhancedRule]]:
        """双向构建规律链：从两端同时逼近"""
        # 双向逼近的简化实现
        # 实际应用中需要实现前向和后向链的合并逻辑
        return self._build_forward_chain(enhanced_rules, start_state, target_state)
    
    def _rule_applicable_to_state(self, rule: EnhancedRule, state: Dict[str, Any]) -> bool:
        """检查规律是否适用于当前状态（放宽条件）"""
        conditions = rule.base_rule.condition_elements
        
        # 如果没有条件，认为总是适用
        if not conditions:
            return True
        
        # 检查是否有任何条件键在状态中匹配
        matches = 0
        total_conditions = len(conditions)
        
        for key, expected_value in (conditions.items() if isinstance(conditions, dict) else enumerate(conditions) if isinstance(conditions, list) else []):
            if key in state:
                # 如果值完全匹配
                if state[key] == expected_value:
                    matches += 1
                # 如果值包含关系匹配
                elif isinstance(state[key], str) and isinstance(expected_value, str):
                    if expected_value.lower() in state[key].lower() or state[key].lower() in expected_value.lower():
                        matches += 1
                # 布尔值推断匹配
                elif self._boolean_inference_match(key, expected_value, state):
                    matches += 1
        
        # 放宽适用性：匹配率>=30%或通过语义相关性检查
        match_rate = matches / total_conditions if total_conditions > 0 else 1.0
        if match_rate >= 0.3:
            return True
        
        # 如果没有直接匹配，检查语义相关性
        return self._check_semantic_applicability(rule, state)
    
    def _boolean_inference_match(self, key: str, expected_value: Any, state: Dict[str, Any]) -> bool:
        """布尔推断匹配"""
        # 威胁相关推断
        if key == "threat" and expected_value == "存在":
            return state.get("threats_nearby", False) or self._has_potential_threat(state)
        elif key == "category" and "危险" in str(expected_value):
            return state.get("threats_nearby", False)
        elif key == "proximity" and "近距离" in str(expected_value):
            return state.get("threats_nearby", False)
        
        # 健康状态推断
        if key == "health_level":
            health = state.get("health", 100)
            if "低" in str(expected_value) or "low" in str(expected_value).lower():
                return health < 50
            elif "中" in str(expected_value) or "medium" in str(expected_value).lower():
                return 30 <= health <= 70
        
        # 食物相关推断
        if key == "object" and "食物" in str(expected_value):
            food_level = state.get("food", 100)
            return food_level < 80  # 食物不满时可能需要寻找食物
        
        return False
    
    def _has_potential_threat(self, state: Dict[str, Any]) -> bool:
        """检查是否有潜在威胁"""
        # 健康状况差可能意味着有威胁
        health = state.get("health", 100)
        if health < 50:
            return True
        
        # 工具不足可能意味着面临威胁
        tools = state.get("tools", [])
        if len(tools) == 0:
            return True
        
        return False
    
    def _check_semantic_applicability(self, rule: EnhancedRule, state: Dict[str, Any]) -> bool:
        """检查语义相关性的适用性（更宽松）"""
        rule_semantic = rule.rule_semantic_type
        
        # 生存规律：在健康较低或有威胁时适用
        if rule_semantic == "survival":
            health = state.get("health", 100)
            threats = state.get("threats_nearby", False)
            return health < 70 or threats or self._has_potential_threat(state)
        
        # 认知规律：几乎总是适用
        elif rule_semantic == "cognitive":
            return True
        
        # 动作规律：适用性更广
        elif rule_semantic in ["action", "food", "water", "tool"]:
            return True
        
        # 更宽松的语义匹配逻辑
        if rule_semantic == "identification":
            # 识别规律适用于有对象或遭遇的状态
            return any(key in state for key in ["object", "encounter", "target", "observed", "position", "health"])
        elif rule_semantic == "classification":
            # 分类规律适用于有特征或特性的状态
            return any(key in state for key in ["features", "characteristics", "features_observed", "category", "tools"])
        elif rule_semantic == "outcome":
            # 结果规律适用于有动作或威胁的状态
            return any(key in state for key in ["action", "threat", "category", "proximity", "health", "food", "water"])
        
        # 其他类型默认适用
        return True
    
    def _calculate_rule_target_relevance(self, rule: EnhancedRule, target_state: Dict[str, Any]) -> float:
        """计算规律与目标状态的相关性（改进算法）"""
        relevance = 0.0
        
        # 检查规律结果与目标的匹配度
        predictions = rule.base_rule.predictions
        
        # 直接匹配
        direct_matches = 0
        for key, value in (target_state.items() if isinstance(target_state, dict) else enumerate(target_state) if isinstance(target_state, list) else []):
            if key in predictions:
                if predictions[key] == value:
                    relevance += 1.0
                    direct_matches += 1
                else:
                    # 语义相似匹配
                    if self._semantic_similarity(predictions[key], value) > 0.5:
                        relevance += 0.6
                        direct_matches += 1
        
        # 语义推断匹配
        semantic_matches = self._calculate_semantic_relevance(rule, target_state)
        relevance += semantic_matches
        
        # 如果没有直接匹配，基于规律类型给予基础相关性
        if direct_matches == 0:
            base_relevance = self._get_base_relevance_by_type(rule, target_state)
            relevance += base_relevance
        
        # 规律置信度加成
        relevance *= rule.get_confidence()
        
        # 确保最小相关性
        return max(relevance, 0.1)  # 最小基础相关性
    
    def _semantic_similarity(self, value1: Any, value2: Any) -> float:
        """计算语义相似度"""
        str1 = str(value1).lower()
        str2 = str(value2).lower()
        
        # 相同内容
        if str1 == str2:
            return 1.0
        
        # 包含关系
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # 预定义的语义相似对
        similar_pairs = {
            ("安全", "safe"): 0.9,
            ("健康", "health"): 0.9,
            ("营养", "nutrition"): 0.8,
            ("危险", "danger"): 0.9,
            ("远离", "avoid"): 0.8,
            ("采集", "collect"): 0.8,
        }
        
        for (term1, term2), similarity in similar_pairs.items():
            if (term1 in str1 and term2 in str2) or (term2 in str1 and term1 in str2):
                return similarity
        
        return 0.0
    
    def _calculate_semantic_relevance(self, rule: EnhancedRule, target_state: Dict[str, Any]) -> float:
        """计算语义推断相关性"""
        relevance = 0.0
        predictions = rule.base_rule.predictions
        
        # 健康相关推断
        if "health" in target_state:
            target_health = target_state["health"]
            if "安全" in str(predictions.values()) or "健康" in str(predictions.values()):
                if isinstance(target_health, (int, float)) and target_health > 50:
                    relevance += 0.5
                elif "好" in str(target_health) or "high" in str(target_health).lower():
                    relevance += 0.5
        
        # 安全相关推断
        if "safe" in target_state and target_state["safe"]:
            if any("安全" in str(v) or "远离" in str(v) for v in predictions.values()):
                relevance += 0.6
        
        # 生存规律对生存目标的相关性
        if rule.rule_semantic_type == "survival":
            if any(key in target_state for key in ["health", "safe", "survival"]):
                relevance += 0.4
        
        return relevance
    
    def _get_base_relevance_by_type(self, rule: EnhancedRule, target_state: Dict[str, Any]) -> float:
        """根据规律类型获取基础相关性"""
        rule_type = rule.rule_semantic_type
        
        # 生存规律对生存相关目标有基础相关性
        if rule_type == "survival":
            if any(key in target_state for key in ["health", "safe", "survival"]):
                return 0.3
        
        # 动作规律对所有目标都有基础相关性
        elif rule_type == "action":
            return 0.2
        
        # 认知规律提供基础理解能力
        elif rule_type == "cognitive":
            return 0.15
        
        return 0.1
    
    def _state_matches_target(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> bool:
        """检查当前状态是否匹配目标状态"""
        for key, target_value in ((target_state.items() if isinstance(target_state, dict) else enumerate(target_state) if isinstance(target_state, list) else []) if isinstance(target_state, dict) else enumerate(target_state) if isinstance(target_state, list) else []):
            if key not in current_state or current_state[key] != target_value:
                return False
        return True
    
    def _apply_rule_to_state(self, state: Dict[str, Any], rule: 'Rule') -> Dict[str, Any]:
        """将规律应用到状态，产生新状态"""
        new_state = state.copy()
        
        # 应用规律的预测到状态 - 类型安全处理
        if isinstance(rule.predictions, dict):
            for key, value in rule.predictions.items():
                new_state[key] = value
        elif isinstance(rule.predictions, list):
            for i, value in enumerate(rule.predictions):
                new_state[f"prediction_{i}"] = value
        else:
            # 其他类型转换为单一值
            new_state["prediction"] = str(rule.predictions)
        
        return new_state

# ============================================================================
# 原有木桥模型类保持不变，添加接头机制支持
# ============================================================================

class GoalType(Enum):
    """目标类型枚举"""
    SURVIVAL = "survival"           # 生存目标
    RESOURCE_ACQUISITION = "resource_acquisition"  # 资源获取
    THREAT_AVOIDANCE = "threat_avoidance"  # 威胁规避
    EXPLORATION = "exploration"     # 探索目标
    SOCIAL_INTERACTION = "social_interaction"  # 社交互动
    LEARNING = "learning"          # 学习目标


class ReasoningStrategy(Enum):
    """推理策略枚举"""
    SIMPLE_MATCHING = "simple_matching"           # 简单规律匹配
    MULTI_RULE_COMBINATION = "multi_rule_combination"  # 多规律组合
    HIERARCHICAL_DECOMPOSITION = "hierarchical_decomposition"  # 分层分解
    ANALOGICAL_REASONING = "analogical_reasoning"  # 类比推理
    CAUSAL_CHAINING = "causal_chaining"          # 因果链推理
    ENHANCED_CHAINING = "enhanced_chaining"      # 增强规律链推理（新接头机制）


class BridgeQuality(Enum):
    """桥梁质量评估"""
    EXCELLENT = "excellent"     # 优秀（成功率>90%）
    GOOD = "good"              # 良好（成功率>70%）
    ACCEPTABLE = "acceptable"   # 可接受（成功率>50%）
    POOR = "poor"              # 较差（成功率>30%）
    FAILED = "failed"          # 失败（成功率<=30%）


@dataclass
class Goal:
    """目标数据结构"""
    goal_type: GoalType
    description: str
    priority: float = 1.0
    urgency: float = 1.0
    complexity: float = 0.5
    deadline: Optional[float] = None
    sub_goals: List['Goal'] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    creation_time: float = 0.0
    
    def calculate_importance(self) -> float:
        """计算目标重要性"""
        time_pressure = 1.0
        if self.deadline and self.deadline > self.creation_time:
            remaining_time = self.deadline - time.time()
            time_pressure = max(0.1, 1.0 / (remaining_time + 1))
        
        return self.priority * self.urgency * time_pressure


@dataclass
class Rule:
    """规律数据结构"""
    rule_id: str
    rule_type: str  # "cognitive" or "action"
    conditions: Dict[str, Any]
    predictions: Dict[str, Any]
    confidence: float
    usage_count: int = 0
    success_count: int = 0
    applicable_contexts: List[str] = field(default_factory=list)
    creation_time: float = 0.0
    last_used: float = 0.0
    
    # === 新增：兼容性属性 ===
    condition_elements: List[str] = field(default_factory=list)  # 条件元素列表，用于验证系统
    expected_result: Dict[str, Any] = field(default_factory=dict)  # 预期结果，验证系统需要
    abstraction_level: int = 1     # 抽象层次，验证系统需要
    generation_time: float = field(default_factory=time.time)  # 生成时间，验证系统需要
    validation_attempts: int = 0   # 验证尝试次数，验证系统需要
    
    def __post_init__(self):
        """初始化后处理，确保兼容性属性正确设置"""
        # 如果condition_elements为空，从conditions生成
        if not self.condition_elements and self.conditions:
            self._generate_condition_elements()
        
        # 如果expected_result为空，从predictions生成（类型安全版本）
        if not self.expected_result and self.predictions:
            # 🔧 类型安全处理：根据predictions的实际类型进行处理
            if isinstance(self.predictions, dict):
                self.expected_result = self.predictions.copy()
            elif isinstance(self.predictions, list):
                # 列表转字典
                self.expected_result = {f"result_{i}": item for i, item in enumerate(self.predictions)}
            else:
                # 其他类型转字典
                self.expected_result = {"result": str(self.predictions)}
    
    def _generate_condition_elements(self):
        """从conditions生成condition_elements列表（类型安全版本）"""
        elements = []
        
        # 🔧 类型安全处理：根据conditions的实际类型进行处理
        if isinstance(self.conditions, dict):
            # 字典类型：正常处理
            for key, value in self.conditions.items():
                if isinstance(value, str):
                    elements.append(f"{key}={value}")
                elif isinstance(value, (int, float)):
                    elements.append(f"{key}={value}")
                elif isinstance(value, bool):
                    elements.append(f"{key}={str(value).lower()}")
                else:
                    elements.append(f"{key}={str(value)}")
        elif isinstance(self.conditions, list):
            # 列表类型：直接转换为字符串元素
            for i, item in enumerate(self.conditions):
                elements.append(f"condition_{i}={str(item)}")
        else:
            # 其他类型：转换为单个元素
            elements.append(f"condition={str(self.conditions)}")
            
        self.condition_elements = elements
    
    def get_success_rate(self) -> float:
        """获取规律成功率"""
        if self.usage_count == 0:
            return 0.5  # 默认成功率
        return self.success_count / self.usage_count
    
    def is_applicable_to_context(self, context: Dict[str, Any]) -> bool:
        """检查规律是否适用于当前上下文"""
        if isinstance(self.conditions, dict):
            for key, value in self.conditions.items():
                if key not in context:
                    return False
                if context[key] != value:
                    return False
        elif isinstance(self.conditions, list):
            # 列表类型的处理
            for i, condition in enumerate(self.conditions):
                condition_key = f"condition_{i}"
                if condition_key not in context:
                    return False
                if context[condition_key] != condition:
                    return False
        else:
            # 其他类型的处理
            condition_key = "condition"
            if condition_key not in context:
                return False
            if context[condition_key] != self.conditions:
                return False
        return True


@dataclass
class DailyAction:
    """每日行动数据结构"""
    day: int                                    # 第几天
    action: str                                # 具体动作
    reasoning: str                             # 行动推理
    expected_state_change: Dict[str, Any]      # 预期状态变化
    risk_assessment: List[str]                 # 风险评估
    fallback_actions: List[str]                # 备选动作
    confidence: float                          # 置信度
    execution_result: Optional[Dict[str, Any]] = None  # 执行结果

@dataclass
class MultiDayPlan:
    """多日计划数据结构"""
    plan_id: str                              # 计划ID
    goal: Goal                               # 目标
    bridge_plan: 'BridgePlan'               # 基础桥梁计划
    daily_actions: List[DailyAction]         # 每日行动列表
    creation_time: float                     # 创建时间
    current_day: int                         # 当前执行到第几天
    total_days: int                          # 总计划天数
    current_state: Dict[str, Any]            # 当前状态
    is_emergency_plan: bool = False          # 是否为紧急计划
    original_plan_id: Optional[str] = None   # 原计划ID（紧急计划时）
    emergency_reason: Optional[str] = None   # 紧急原因
    
    def get_action_for_day(self, day: int) -> Optional[DailyAction]:
        """获取指定天数的行动"""
        for action in self.daily_actions:
            if action.day == day:
                return action
        return None
    
    def get_expected_state_for_day(self, day: int) -> Optional[Dict[str, Any]]:
        """获取指定天数的预期状态"""
        action = self.get_action_for_day(day)
        return action.expected_state_change if action else None
    
    def copy(self) -> 'MultiDayPlan':
        """创建计划副本"""
        return MultiDayPlan(
            plan_id=f"{self.plan_id}_copy_{int(time.time())}",
            goal=self.goal,
            bridge_plan=self.bridge_plan,
            daily_actions=self.daily_actions.copy(),
            creation_time=self.creation_time,
            current_day=self.current_day,
            total_days=self.total_days,
            current_state=self.current_state.copy(),
            is_emergency_plan=self.is_emergency_plan,
            original_plan_id=self.original_plan_id,
            emergency_reason=self.emergency_reason
        )

@dataclass
class PlanAdjustmentResult:
    """计划调整结果数据结构"""
    needs_adjustment: bool                    # 是否需要调整
    adjustment_reason: str                    # 调整原因
    new_plan: Optional[MultiDayPlan]         # 新计划
    original_plan: MultiDayPlan              # 原计划

@dataclass
class BridgePlan:
    """桥梁方案数据结构"""
    plan_id: str
    goal: Goal
    rules_used: List[Rule]
    reasoning_strategy: ReasoningStrategy
    action_sequence: List[str]
    expected_success_rate: float
    expected_cost: float
    estimated_time: float
    risk_factors: List[str] = field(default_factory=list)
    contingency_plans: List['BridgePlan'] = field(default_factory=list)
    
    def calculate_utility(self) -> float:
        """计算方案效用"""
        success_utility = self.expected_success_rate * self.goal.calculate_importance()
        cost_penalty = self.expected_cost * 0.1
        time_penalty = self.estimated_time * 0.05
        risk_penalty = len(self.risk_factors) * 0.1
        
        return success_utility - cost_penalty - time_penalty - risk_penalty



# ===== EOCATR转换器 - 解决WBM决策失败问题 =====
import os
import json

class EOCATRToWBMConverter:
    """EOCATR六元组到WBM格式转换器 - 集成版"""
    
    def __init__(self):
        self.converted_cache = {}
        print("🔄 WBM integrated EOCATR converter activated")
    
    def convert_eocatr_rules_to_wbm(self, eocatr_rules: list) -> list:
        """批量转换EOCATR规律为WBM格式"""
        wbm_rules = []
        
        for rule in eocatr_rules:
            try:
                # 构建WBM Rule对象的conditions
                conditions = {
                    'environment_type': rule.get('environment', 'unknown'),
                    'objects_present': rule.get('objects', 'unknown'),
                    'context_state': rule.get('context', 'normal'),
                    'available_tools': rule.get('tools', '').split(',') if rule.get('tools') else [],
                    'resource_level': 'sufficient'
                }
                
                # 构建WBM Rule对象的predictions
                predictions = {
                    'action_type': rule.get('action', 'explore'),
                    'expected_result': rule.get('result', 'success'),
                    'success_probability': rule.get('confidence', 0.8),
                    'estimated_duration': 1,
                    'resource_cost': {'energy': 1, 'time': 1}
                }
                
                # 创建WBM Rule对象
                wbm_rule = {
                    'rule_id': f"eocatr_converted_{hash(str(rule)) % 10000}",
                    'rule_type': 'converted_eocatr',
                    'conditions': conditions,
                    'predictions': predictions,
                    'confidence': rule.get('confidence', 0.8),
                    'usage_count': 0,
                    'last_used': None,
                    'metadata': {
                        'source': 'eocatr_conversion',
                        'original_eocatr': rule
                    }
                }
                
                wbm_rules.append(wbm_rule)
                
            except Exception as e:
                print(f"⚠️ Failed to convert rule: {e}")
                continue
        
        print(f"🔄 EOCATR conversion completed: {len(eocatr_rules)} -> {len(wbm_rules)}")
        return wbm_rules
    
    def get_eocatr_rules_from_five_libraries(self) -> list:
        """从五库系统获取EOCATR规律"""
        rules = []
        
        # 从多个数据库源获取规律
        possible_dbs = [
            "five_libraries/total_rules.db",
            "five_libraries/direct_rules.db"
        ]
        
        for db_path in possible_dbs:
            if not os.path.exists(db_path):
                continue
                
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 获取规律数据
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                for table_name_tuple in tables:
                    table_name = table_name_tuple[0]
                    
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 50;")
                        rows = cursor.fetchall()
                        
                        if rows:
                            cursor.execute(f"PRAGMA table_info({table_name});")
                            columns = cursor.fetchall()
                            column_names = [col[1] for col in columns]
                            
                            for row in rows:
                                rule_dict = dict(zip(column_names, row))
                                
                                # 尝试转换为EOCATR格式
                                eocatr_rule = self._convert_rule_to_eocatr(rule_dict)
                                if eocatr_rule:
                                    rules.append(eocatr_rule)
                    
                    except Exception:
                        continue
                
                conn.close()
                
            except Exception as e:
                continue
        
        # 如果没找到规律，使用默认规律
        if not rules:
            rules = self._get_default_eocatr_rules()
        
        return rules[:50]  # 限制数量避免性能问题
    
    def _convert_rule_to_eocatr(self, rule_dict: dict) -> dict:
        """将规律转换为EOCATR格式"""
        try:
            # 尝试从WBM格式解析
            if 'conditions' in rule_dict and 'predictions' in rule_dict:
                conditions_str = rule_dict.get('conditions', '{}')
                predictions_str = rule_dict.get('predictions', '{}')
                
                if isinstance(conditions_str, str):
                    conditions = json.loads(conditions_str) if conditions_str else {}
                else:
                    conditions = conditions_str or {}
                    
                if isinstance(predictions_str, str):
                    predictions = json.loads(predictions_str) if predictions_str else {}
                else:
                    predictions = predictions_str or {}
                
                return {
                    'environment': conditions.get('environment_type', 'unknown'),
                    'objects': conditions.get('objects_present', 'unknown'),
                    'context': conditions.get('context_state', 'normal'),
                    'action': predictions.get('action_type', 'explore'),
                    'tools': ','.join(conditions.get('available_tools', [])),
                    'result': predictions.get('expected_result', 'success'),
                    'confidence': rule_dict.get('confidence', 0.8)
                }
            
            # 直接EOCATR格式
            if all(key in rule_dict for key in ['environment', 'objects', 'context', 'action']):
                return {
                    'environment': rule_dict.get('environment', 'unknown'),
                    'objects': rule_dict.get('objects', 'unknown'),
                    'context': rule_dict.get('context', 'normal'),
                    'action': rule_dict.get('action', 'explore'),
                    'tools': rule_dict.get('tools', ''),
                    'result': rule_dict.get('result', 'success'),
                    'confidence': rule_dict.get('confidence', 0.8)
                }
            
            return None
            
        except Exception:
            return None
    
    def _get_default_eocatr_rules(self) -> list:
        """获取默认EOCATR规律"""
        return [
            {
                'environment': 'forest', 'objects': 'tree', 'context': 'exploration',
                'action': 'collect_wood', 'tools': 'axe', 'result': 'wood_collected', 'confidence': 0.9
            },
            {
                'environment': 'river', 'objects': 'water', 'context': 'thirsty',
                'action': 'drink_water', 'tools': 'container', 'result': 'thirst_quenched', 'confidence': 0.95
            },
            {
                'environment': 'cave', 'objects': 'shelter', 'context': 'night',
                'action': 'seek_shelter', 'tools': 'torch', 'result': 'safe_rest', 'confidence': 0.85
            }
        ]

# 全局转换器实例
EOCATR_CONVERTER = EOCATRToWBMConverter()

# ===== 修改WBM决策逻辑，整合EOCATR转换器 =====

def get_enhanced_rules_with_eocatr(self, goal: str, urgency: float) -> list:
    """
    增强版规律获取方法 - 整合EOCATR转换器
    解决WBM无法构建有效决策链的核心问题
    """
    enhanced_rules = []
    
    try:
        # 1. 获取EOCATR规律
        eocatr_rules = EOCATR_CONVERTER.get_eocatr_rules_from_five_libraries()
        
        if self.logger:
            self.logger.log(f"🔧 EOCATR获取: 原始规律{len(eocatr_rules)}条")
        
        # 2. 转换为WBM格式
        wbm_rules = EOCATR_CONVERTER.convert_eocatr_rules_to_wbm(eocatr_rules)
        enhanced_rules.extend(wbm_rules)
        
        if self.logger:
            self.logger.log(f"✅ EOCATR转换: WBM规律{len(wbm_rules)}条")
        
        # 3. 根据目标和紧急度过滤
        filtered_rules = []
        for rule in enhanced_rules:
            relevance_score = self._calculate_rule_relevance(rule, goal, urgency)
            if relevance_score > 0.1:  # 相关性阈值
                filtered_rules.append(rule)
        
        if self.logger:
            self.logger.log(f"🎯 目标过滤: 相关规律{len(filtered_rules)}条")
        
        return filtered_rules
        
    except Exception as e:
        if self.logger:
            self.logger.log(f"❌ EOCATR增强检索失败: {str(e)}")
        return enhanced_rules
    
def _calculate_rule_relevance(self, rule, goal: str, urgency: float) -> float:
    """计算规律与目标的相关性"""
    try:
        relevance = 0.0
        rule_text = str(rule.get('conditions', '')) + str(rule.get('predictions', ''))
        
        # 目标关键词匹配
        goal_keywords = {
            'threat_avoidance': ['threat', 'danger', 'escape', 'flee', 'safe'],
            'food_acquisition': ['food', 'eat', 'collect', 'hunt', 'plant'],
            'water_acquisition': ['water', 'drink', 'river', 'puddle'],
            'exploration': ['explore', 'move', 'discover', 'unknown'],
            'skill_development': ['skill', 'learn', 'practice', 'improve']
        }
        
        for goal_type, keywords in goal_keywords.items():
            if goal_type in goal.lower():
                for keyword in keywords:
                    if keyword in rule_text.lower():
                        relevance += 0.3
                        break
        
        # 紧急度加权
        if urgency > 0.7:
            relevance *= 1.5
        
        return min(1.0, relevance)
        
    except Exception:
        return 0.1  # 默认低相关性

class WoodenBridgeModel:
    """木桥模型主类 - 支持规律接头机制的首尾搭接"""
    
    def __init__(self, logger=None, config=None):
        self.logger = logger
        self.config = config or self._default_config()
        
        # 目标管理
        self.current_goals = []          # 当前活跃目标
        self.goal_history = []           # 目标历史
        self.goal_priorities = {}        # 目标优先级映射
        
        # 规律库（从BPM和经验中获取）
        self.available_rules = []        # 可用规律列表
        self.rule_effectiveness = {}     # 规律效果记录
        
        # 规律接头机制（新增）
        self.rule_chain_builder = RuleChainBuilder(logger=logger)  # 规律链构建器
        self.enhanced_rules_cache = {}   # 增强规律缓存
        self.successful_chains = []      # 成功的规律链
        self.chain_performance = {}      # 规律链性能记录
        
        # 桥梁建造记录
        self.bridge_history = []         # 桥梁建造历史
        self.successful_bridges = []     # 成功的桥梁方案
        self.failed_bridges = []         # 失败的桥梁方案
        
        # 推理策略管理
        self.strategy_performance = defaultdict(lambda: {'success': 0, 'total': 0})
        self.preferred_strategies = {}   # 不同目标类型的偏好策略
        
        # 元推理能力（内嵌式）
        self.reasoning_patterns = {}     # 推理模式记录
        self.strategy_adaptation = {}    # 策略适应性记录
        
        # 性能统计
        self.performance_stats = {
            'total_bridges_built': 0,
            'successful_bridges': 0,
            'goal_achievement_rate': 0.0,
            'average_bridge_quality': 0.0,
            'strategy_diversity': 0.0,
            'reasoning_efficiency': 0.0,
            # 新增接头机制统计
            'chain_connections_attempted': 0,
            'chain_connections_successful': 0,
            'average_chain_length': 0.0,
            'interface_compatibility_rate': 0.0
        }
        
        if self.logger:
            self.logger.log("WBM木桥模型已初始化（支持规律接头机制）")
        
        # === 绑定EOCATR增强方法 ===
        self.get_enhanced_rules_with_eocatr = lambda goal, urgency: get_enhanced_rules_with_eocatr(self, goal, urgency)
        self._calculate_rule_relevance = lambda rule, goal, urgency: _calculate_rule_relevance(self, rule, goal, urgency)
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置参数"""
        return {
            'max_goals': 5,                    # 最大同时处理目标数
            'max_rules_per_bridge': 10,       # 每座桥最大规律数
            'min_confidence_threshold': 0.3,   # 最小置信度阈值
            'goal_timeout': 100.0,             # 目标超时时间
            'enable_contingency_planning': True, # 启用应急预案
            'enable_analogical_reasoning': True, # 启用类比推理
            'bridge_quality_threshold': 0.6,   # 桥梁质量阈值
            'max_reasoning_depth': 5,          # 最大推理深度
            'strategy_adaptation_rate': 0.1,   # 策略适应率
        }
    
    def establish_goal(self, goal_type: GoalType, description: str,
                      priority: float = 1.0, urgency: float = 1.0,
                      context: Dict[str, Any] = None) -> Goal:
        """阶段1：目标确立与表征"""
        goal = Goal(
            goal_type=goal_type,
            description=description,
            priority=priority,
            urgency=urgency,
            complexity=self._assess_goal_complexity(goal_type, context or {}),
            context=context or {},
            creation_time=time.time()
        )
        
        # 目标分解（如果需要）
        if goal.complexity > 0.7:
            goal.sub_goals = self._decompose_goal(goal)
        
        # 添加到活跃目标列表
        if len(self.current_goals) >= self.config['max_goals']:
            # 移除优先级最低的目标
            self.current_goals.sort(key=lambda g: g.calculate_importance())
            removed_goal = self.current_goals.pop(0)
            if self.logger:
                self.logger.log(f"WBM移除低优先级目标: {removed_goal.description}")
        
        self.current_goals.append(goal)
        self.goal_history.append(goal)
        
        if self.logger:
            self.logger.log(f"WBM确立目标: {description} (优先级:{priority:.2f}, 复杂度:{goal.complexity:.2f})")
        
        return goal
    
    def build_enhanced_bridge_with_chains(self, goal: Goal, available_rules: List[Rule],
                                        start_state: Dict[str, Any] = None,
                                        target_state: Dict[str, Any] = None,
                                        direction: str = "forward") -> Optional[BridgePlan]:
        """
        使用规律接头机制构建增强桥梁
        
        这是WBM 1.5.0的核心新功能：首尾搭接规律链构建
        
        Args:
            goal: 目标
            available_rules: 可用规律列表
            start_state: 起始状态
            target_state: 目标状态
            direction: 构建方向 ("forward", "backward", "bidirectional")
        """
        if self.logger:
            self.logger.log(f"🔧 WBM增强桥梁构建开始 | 可用规律数: {len(available_rules)} | 目标: {goal.description}")
        
        if not available_rules:
            if self.logger:
                self.logger.log(f"❌ WBM增强桥梁构建失败: 无可用规律")
            return None
        
        # 1. 转换为增强规律
        enhanced_rules = self._get_or_create_enhanced_rules(available_rules)
        if self.logger:
            self.logger.log(f"🔧 WBM增强规律转换完成 | 增强规律数: {len(enhanced_rules)}")
        
        # 2. 构建目标状态（如果未提供）
        if target_state is None:
            target_state = self._extract_target_state_from_goal(goal)
        if self.logger:
            self.logger.log(f"🎯 WBM目标状态: {target_state}")
        
        # 3. 构建起始状态（如果未提供）
        if start_state is None:
            start_state = self._extract_start_state_from_context(goal.context)
        if self.logger:
            self.logger.log(f"🏁 WBM起始状态: {start_state}")
        
        # 4. 使用规律链构建器构建规律链
        if self.logger:
            self.logger.log(f"🔗 WBM开始构建规律链 | 方向: {direction}")
        
        rule_chain = self.rule_chain_builder.build_rule_chain(
            enhanced_rules, start_state, target_state, direction
        )
        
        if not rule_chain:
            if self.logger:
                self.logger.log(f"❌ WBM无法构建规律链：{goal.description}")
            return None
        
        if self.logger:
            self.logger.log(f"✅ WBM规律链构建成功 | 链长度: {len(rule_chain)}")
            for i, rule in enumerate(rule_chain):
                self.logger.log(f"  链节点{i+1}: {rule.get_rule_id()} (置信度: {rule.get_confidence()})")
        
        # 5. 统计接头连接信息
        self._record_chain_statistics(rule_chain)
        
        # 6. 将规律链转换为桥梁计划
        bridge_plan = self._convert_rule_chain_to_bridge_plan(goal, rule_chain, direction)
        
        if self.logger:
            self.logger.log(
                f"🌉 WBM构建增强桥梁（规律链）成功: {goal.description} | "
                f"链长度: {len(rule_chain)} | "
                f"方向: {direction} | "
                f"预期成功率: {bridge_plan.expected_success_rate:.2f} | "
                f"动作序列: {bridge_plan.action_sequence}"
            )
        
        return bridge_plan
    
    def _get_or_create_enhanced_rules(self, rules: List[Rule]) -> List[EnhancedRule]:
        """获取或创建增强规律"""
        enhanced_rules = []
        
        if self.logger:
            self.logger.log(f"🔧 开始创建增强规律 | 输入规律数: {len(rules)}")
        
        for i, rule in enumerate(rules):
            rule_id = rule.rule_id
            
            # 检查缓存
            if rule_id in self.enhanced_rules_cache:
                enhanced_rules.append(self.enhanced_rules_cache[rule_id])
                if self.logger:
                    self.logger.log(f"  {i+1}. 使用缓存增强规律: {rule_id}")
            else:
                # 创建新的增强规律
                if self.logger:
                    self.logger.log(f"  {i+1}. 创建新增强规律: {rule_id}")
                    self.logger.log(f"    原始规律条件: {rule.conditions}")
                    self.logger.log(f"    原始规律预测: {rule.predictions}")
                
                enhanced_rule = self.rule_chain_builder.enhance_rule(rule)
                self.enhanced_rules_cache[rule_id] = enhanced_rule
                enhanced_rules.append(enhanced_rule)
                
                if self.logger:
                    self.logger.log(f"    ✅ 增强规律创建成功: {rule_id}")
                    self.logger.log(f"    头部接头: {enhanced_rule.head_interface.semantic_category}:{enhanced_rule.head_interface.get_element_content()} (抽象度:{enhanced_rule.head_interface.abstraction_size})")
                    self.logger.log(f"    尾部接头: {enhanced_rule.tail_interface.semantic_category}:{enhanced_rule.tail_interface.get_element_content()} (抽象度:{enhanced_rule.tail_interface.abstraction_size})")
                    self.logger.log(f"    规律语义类型: {enhanced_rule.rule_semantic_type}")
        
        if self.logger:
            self.logger.log(f"🔧 增强规律创建完成 | 输出增强规律数: {len(enhanced_rules)}")
        
        return enhanced_rules
    
    def _extract_target_state_from_goal(self, goal: Goal) -> Dict[str, Any]:
        """从目标中提取目标状态"""
        target_state = {}
        
        # 根据目标类型确定目标状态
        if goal.goal_type == GoalType.SURVIVAL:
            target_state = {"status": "safe", "health": "good"}
        elif goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            if "食物" in goal.description or "food" in goal.description.lower():
                target_state = {"food_level": "high", "status": "fed"}
            elif "水" in goal.description or "water" in goal.description.lower():
                target_state = {"water_level": "high", "status": "hydrated"}
            else:
                target_state = {"resources": "acquired"}
        elif goal.goal_type == GoalType.THREAT_AVOIDANCE:
            target_state = {"threat_level": "low", "status": "safe"}
        elif goal.goal_type == GoalType.EXPLORATION:
            target_state = {"knowledge": "expanded", "area": "explored"}
        else:
            target_state = {"goal_achieved": True}
        
        # 从目标上下文中添加更多信息
        if goal.context:
            target_state.update(goal.context.get('target_state', {}))
        
        return target_state
    
    def _extract_start_state_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """从上下文中提取起始状态"""
        start_state = context.get('current_state', {})
        
        # 如果没有提供起始状态，使用默认值
        if not start_state:
            start_state = {
                "location": "current",
                "status": "active",
                "resources": "current_level"
            }
        
        return start_state
    
    def _record_chain_statistics(self, rule_chain: List[EnhancedRule]):
        """记录规律链统计信息"""
        self.performance_stats['chain_connections_attempted'] += len(rule_chain) - 1
        
        # 计算成功连接数
        successful_connections = 0
        for i in range(len(rule_chain) - 1):
            can_connect, strength = rule_chain[i].can_chain_to(rule_chain[i + 1])
            if can_connect:
                successful_connections += 1
        
        self.performance_stats['chain_connections_successful'] += successful_connections
        
        # 更新平均链长度
        total_chains = len(self.successful_chains) + 1
        current_avg = self.performance_stats['average_chain_length']
        self.performance_stats['average_chain_length'] = (
            (current_avg * (total_chains - 1) + len(rule_chain)) / total_chains
        )
        
        # 更新接头兼容性率
        total_attempted = self.performance_stats['chain_connections_attempted']
        total_successful = self.performance_stats['chain_connections_successful']
        
        if total_attempted > 0:
            self.performance_stats['interface_compatibility_rate'] = total_successful / total_attempted
    
    def _convert_rule_chain_to_bridge_plan(self, goal: Goal, rule_chain: List[EnhancedRule], 
                                         direction: str) -> BridgePlan:
        """将规律链转换为桥梁计划"""
        # 提取基础规律
        base_rules = [enhanced_rule.base_rule for enhanced_rule in rule_chain]
        
        # 生成动作序列
        action_sequence = []
        for enhanced_rule in rule_chain:
            rule_actions = self._rule_to_actions(enhanced_rule.base_rule, goal)
            action_sequence.extend(rule_actions)
        
        # 计算成功率（考虑接头连接强度）
        base_success_rate = self._calculate_combined_success_rate(base_rules)
        connection_strength_avg = self._calculate_average_connection_strength(rule_chain)
        adjusted_success_rate = base_success_rate * connection_strength_avg
        
        # 计算成本和时间
        estimated_cost = sum(self._calculate_action_cost(action) for action in action_sequence)
        estimated_time = len(action_sequence) * 1.5  # 基础时间估算
        
        # 创建桥梁计划
        plan_id = f"chain_bridge_{int(time.time())}_{len(rule_chain)}"
        
        bridge_plan = BridgePlan(
            plan_id=plan_id,
            goal=goal,
            rules_used=base_rules,
            reasoning_strategy=ReasoningStrategy.ENHANCED_CHAINING,  # 使用增强链策略
            action_sequence=action_sequence,
            expected_success_rate=adjusted_success_rate,
            expected_cost=estimated_cost,
            estimated_time=estimated_time
        )
        
        # 添加规律链特有信息
        bridge_plan.risk_factors = self._assess_chain_risks(rule_chain)
        
        return bridge_plan
    
    def _calculate_average_connection_strength(self, rule_chain: List[EnhancedRule]) -> float:
        """计算规律链的平均连接强度"""
        if len(rule_chain) <= 1:
            return 1.0
        
        total_strength = 0.0
        connection_count = 0
        
        for i in range(len(rule_chain) - 1):
            can_connect, strength = rule_chain[i].can_chain_to(rule_chain[i + 1])
            if can_connect:
                total_strength += strength
                connection_count += 1
        
        return total_strength / connection_count if connection_count > 0 else 0.5
    
    def _assess_chain_risks(self, rule_chain: List[EnhancedRule]) -> List[str]:
        """评估规律链风险"""
        risks = []
        
        # 检查链长度风险
        if len(rule_chain) > 4:
            risks.append("规律链过长，执行风险增加")
        
        # 检查连接强度风险
        weak_connections = 0
        for i in range(len(rule_chain) - 1):
            can_connect, strength = rule_chain[i].can_chain_to(rule_chain[i + 1])
            if can_connect and strength < 0.5:
                weak_connections += 1
        
        if weak_connections > 0:
            risks.append(f"存在{weak_connections}个弱连接")
        
        # 检查语义一致性风险
        semantic_types = set(rule.rule_semantic_type for rule in rule_chain)
        if len(semantic_types) > 3:
            risks.append("规律链语义类型过于分散")
        
        # 检查置信度风险
        low_confidence_rules = [rule for rule in rule_chain if rule.get_confidence() < 0.4]
        if low_confidence_rules:
            risks.append(f"包含{len(low_confidence_rules)}个低置信度规律")
        
        return risks
    
    def _assess_goal_complexity(self, goal_type: GoalType, context: Dict[str, Any]) -> float:
        """评估目标复杂度"""
        base_complexity = {
            GoalType.SURVIVAL: 0.8,
            GoalType.RESOURCE_ACQUISITION: 0.4,
            GoalType.THREAT_AVOIDANCE: 0.7,
            GoalType.EXPLORATION: 0.3,
            GoalType.SOCIAL_INTERACTION: 0.6,
            GoalType.LEARNING: 0.5
        }.get(goal_type, 0.5)
        
        # 基于上下文调整复杂度
        context_factors = len(context.get('obstacles', []))
        resource_scarcity = context.get('resource_scarcity', 0.0)
        time_pressure = context.get('time_pressure', 0.0)
        
        complexity_adjustment = (context_factors * 0.1 + 
                               resource_scarcity * 0.2 + 
                               time_pressure * 0.15)
        
        return min(1.0, base_complexity + complexity_adjustment)
    
    def _decompose_goal(self, goal: Goal) -> List[Goal]:
        """目标分解"""
        sub_goals = []
        
        if goal.goal_type == GoalType.SURVIVAL:
            # 生存目标分解为资源获取和威胁规避
            sub_goals.append(Goal(
                goal_type=GoalType.RESOURCE_ACQUISITION,
                description="获取生存必需资源",
                priority=goal.priority * 0.8,
                urgency=goal.urgency,
                context=goal.context
            ))
            sub_goals.append(Goal(
                goal_type=GoalType.THREAT_AVOIDANCE,
                description="规避生存威胁",
                priority=goal.priority * 0.9,
                urgency=goal.urgency,
                context=goal.context
            ))
        
        elif goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            # 资源获取分解为搜索和采集
            sub_goals.append(Goal(
                goal_type=GoalType.EXPLORATION,
                description="搜索资源位置",
                priority=goal.priority * 0.6,
                urgency=goal.urgency * 0.8,
                context=goal.context
            ))
        
        return sub_goals
    
    def build_bridge(self, goal: Goal, available_rules: List[Rule]) -> Optional[BridgePlan]:
        """阶段2：解决方案构建与预期评估（"搭桥"与"风险评估"）"""
        if not available_rules:
            if self.logger:
                self.logger.log(f"WBM无可用规律构建桥梁：{goal.description}")
            return None
        
        # 更新可用规律
        self.available_rules = available_rules
        
        # 选择推理策略
        reasoning_strategy = self._select_reasoning_strategy(goal, available_rules)
        
        # 构建桥梁方案
        bridge_plan = self._construct_bridge_plan(goal, reasoning_strategy)
        
        if bridge_plan:
            # 风险评估
            self._assess_bridge_risks(bridge_plan)
            
            # 创建应急预案
            if self.config['enable_contingency_planning']:
                bridge_plan.contingency_plans = self._create_contingency_plans(bridge_plan)
            
            if self.logger:
                self.logger.log(
                    f"WBM构建桥梁：{goal.description} | "
                    f"策略:{reasoning_strategy.value} | "
                    f"预期成功率:{bridge_plan.expected_success_rate:.2f} | "
                    f"规律数:{len(bridge_plan.rules_used)}"
                )
        
        return bridge_plan
    
    def _select_reasoning_strategy(self, goal: Goal, available_rules: List[Rule]) -> ReasoningStrategy:
        """选择推理策略（内嵌元推理）"""
        # 基于目标复杂度选择基础策略
        if goal.complexity < 0.3:
            base_strategy = ReasoningStrategy.SIMPLE_MATCHING
        elif goal.complexity < 0.5:
            base_strategy = ReasoningStrategy.ENHANCED_CHAINING  # 优先使用新的增强链推理
        elif goal.complexity < 0.7:
            base_strategy = ReasoningStrategy.MULTI_RULE_COMBINATION
        else:
            base_strategy = ReasoningStrategy.HIERARCHICAL_DECOMPOSITION
        
        # 基于历史表现调整策略
        goal_type_key = goal.goal_type.value
        if goal_type_key in self.preferred_strategies:
            preferred = self.preferred_strategies[goal_type_key]
            # 如果偏好策略表现更好，则使用偏好策略
            base_perf = self.strategy_performance[base_strategy.value]
            pref_perf = self.strategy_performance[preferred.value]
            
            if (pref_perf['total'] > 5 and 
                pref_perf['success'] / pref_perf['total'] > 
                base_perf['success'] / max(base_perf['total'], 1)):
                base_strategy = preferred
        
        # 基于可用规律数量和质量调整
        high_quality_rules = [r for r in available_rules if r.confidence > 0.7]
        if len(high_quality_rules) < 3 and goal.complexity > 0.5:
            # 高质量规律不足，使用类比推理
            base_strategy = ReasoningStrategy.ANALOGICAL_REASONING
        
        return base_strategy
    
    def _construct_bridge_plan(self, goal: Goal, strategy: ReasoningStrategy) -> Optional[BridgePlan]:
        """构建桥梁方案"""
        if strategy == ReasoningStrategy.SIMPLE_MATCHING:
            return self._simple_rule_matching(goal)
        elif strategy == ReasoningStrategy.MULTI_RULE_COMBINATION:
            return self._multi_rule_combination(goal)
        elif strategy == ReasoningStrategy.HIERARCHICAL_DECOMPOSITION:
            return self._hierarchical_decomposition(goal)
        elif strategy == ReasoningStrategy.ANALOGICAL_REASONING:
            return self._analogical_reasoning(goal)
        elif strategy == ReasoningStrategy.CAUSAL_CHAINING:
            return self._causal_chaining(goal)
        elif strategy == ReasoningStrategy.ENHANCED_CHAINING:
            return self.build_enhanced_bridge_with_chains(goal, self.available_rules)
        else:
            return self._simple_rule_matching(goal)  # 默认策略
    
    def _simple_rule_matching(self, goal: Goal) -> Optional[BridgePlan]:
        """简单规律匹配"""
        # 寻找最匹配的单个规律
        applicable_rules = [
            rule for rule in self.available_rules
            if self._is_rule_applicable_to_goal(rule, goal) and rule.confidence > self.config['min_confidence_threshold']
        ]
        
        if not applicable_rules:
            # 如果没有适用规律，创建备用方案
            return self._create_fallback_plan(goal, ReasoningStrategy.SIMPLE_MATCHING)
        
        # 选择置信度最高的规律
        best_rule = max(applicable_rules, key=lambda r: r.confidence * r.get_success_rate())
        
        # 构建简单行动序列
        action_sequence = self._rule_to_actions(best_rule, goal)
        
        return BridgePlan(
            plan_id=f"simple_{time.time()}",
            goal=goal,
            rules_used=[best_rule],
            reasoning_strategy=ReasoningStrategy.SIMPLE_MATCHING,
            action_sequence=action_sequence,
            expected_success_rate=best_rule.confidence * best_rule.get_success_rate(),
            expected_cost=1.0,  # 简单方案成本低
            estimated_time=2.0
        )
    
    def _is_rule_applicable_to_goal(self, rule: Rule, goal: Goal) -> bool:
        """检查规律是否适用于目标"""
        # 检查规律的适用上下文是否匹配目标类型
        if goal.goal_type.value in rule.applicable_contexts:
            return True
        
        # 检查规律条件是否部分匹配目标上下文
        matching_conditions = 0
        total_conditions = len(rule.condition_elements)
        
        if total_conditions == 0:
            return True  # 没有条件限制的规律总是适用
        
        for condition_key, condition_value in enumerate(rule.condition_elements):
            # 简化匹配逻辑：检查关键条件
            if condition_key in goal.context:
                if goal.context[condition_key] == condition_value:
                    matching_conditions += 1
            elif condition_key == "goal_type" and condition_value == goal.goal_type.value:
                matching_conditions += 1
            elif condition_key == "priority_level":
                if (condition_value == "high" and goal.priority > 0.7) or \
                   (condition_value == "medium" and 0.3 <= goal.priority <= 0.7) or \
                   (condition_value == "low" and goal.priority < 0.3):
                    matching_conditions += 1
        
        # 如果至少一半的条件匹配，认为规律适用
        return matching_conditions >= (total_conditions / 2)
    
    def _multi_rule_combination(self, goal: Goal) -> Optional[BridgePlan]:
        """多规律组合"""
        applicable_rules = [
            rule for rule in self.available_rules
            if self._is_rule_applicable_to_goal(rule, goal) and rule.confidence > self.config['min_confidence_threshold']
        ]
        
        if len(applicable_rules) < 1:
            # 如果没有适用规律，创建备用方案
            return self._create_fallback_plan(goal, ReasoningStrategy.MULTI_RULE_COMBINATION)
        
        # 如果只有一个规律，使用简单匹配
        if len(applicable_rules) == 1:
            return self._simple_rule_matching(goal)
        
        # 选择最佳规律组合（贪心算法）
        selected_rules = []
        remaining_rules = applicable_rules.copy()
        
        # 首先选择最相关的规律
        best_rule = max(remaining_rules, 
                      key=lambda r: self._evaluate_rule_contribution(r, [], goal))
        selected_rules.append(best_rule)
        remaining_rules.remove(best_rule)
        
        # 继续添加互补规律
        while len(selected_rules) < self.config['max_rules_per_bridge'] and remaining_rules:
            best_addition = max(remaining_rules, 
                              key=lambda r: self._evaluate_rule_contribution(r, selected_rules, goal))
            
            # 只有当添加规律能显著提升效果时才添加
            contribution = self._evaluate_rule_contribution(best_addition, selected_rules, goal)
            if contribution > 0.3:  # 最小贡献阈值
                selected_rules.append(best_addition)
                remaining_rules.remove(best_addition)
            else:
                break
        
        # 构建组合行动序列
        action_sequence = self._combine_rules_to_actions(selected_rules, goal)
        
        return BridgePlan(
            plan_id=f"multi_{time.time()}",
            goal=goal,
            rules_used=selected_rules,
            reasoning_strategy=ReasoningStrategy.MULTI_RULE_COMBINATION,
            action_sequence=action_sequence,
            expected_success_rate=self._calculate_combined_success_rate(selected_rules),
            expected_cost=len(selected_rules) * 0.5,
            estimated_time=len(selected_rules) * 1.5
        )
    
    def _hierarchical_decomposition(self, goal: Goal) -> Optional[BridgePlan]:
        """分层分解推理"""
        if not goal.sub_goals:
            goal.sub_goals = self._decompose_goal(goal)
        
        if not goal.sub_goals:
            return self._multi_rule_combination(goal)
        
        # 为每个子目标构建子方案
        sub_plans = []
        all_rules_used = []
        total_cost = 0.0
        total_time = 0.0
        
        for sub_goal in goal.sub_goals:
            sub_plan = self._multi_rule_combination(sub_goal)
            if sub_plan:
                sub_plans.append(sub_plan)
                all_rules_used.extend(sub_plan.rules_used)
                total_cost += sub_plan.expected_cost
                total_time += sub_plan.estimated_time
        
        if not sub_plans:
            # 如果无法生成子方案，创建备用方案
            return self._create_fallback_plan(goal, ReasoningStrategy.HIERARCHICAL_DECOMPOSITION)
        
        # 合并子方案的行动序列
        combined_actions = []
        for sub_plan in sub_plans:
            combined_actions.extend(sub_plan.action_sequence)
        
        # 计算分层方案的整体成功率
        sub_success_rates = [plan.expected_success_rate for plan in sub_plans]
        overall_success_rate = np.prod(sub_success_rates) if sub_success_rates else 0.0
        
        return BridgePlan(
            plan_id=f"hierarchical_{time.time()}",
            goal=goal,
            rules_used=all_rules_used,
            reasoning_strategy=ReasoningStrategy.HIERARCHICAL_DECOMPOSITION,
            action_sequence=combined_actions,
            expected_success_rate=overall_success_rate,
            expected_cost=total_cost,
            estimated_time=total_time * 0.8  # 并行执行可能节省时间
        )
    
    def _analogical_reasoning(self, goal: Goal) -> Optional[BridgePlan]:
        """类比推理"""
        # 寻找类似的成功桥梁案例
        similar_bridges = self._find_similar_successful_bridges(goal)
        
        if not similar_bridges:
            # 如果没有类比案例，创建一个基础方案
            return self._create_fallback_plan(goal, ReasoningStrategy.ANALOGICAL_REASONING)
        
        # 选择最相似的成功案例
        best_analogy = max(similar_bridges, key=lambda b: self._calculate_similarity(goal, b.goal))
        
        # 适配类比案例到当前目标
        adapted_rules = self._adapt_rules_from_analogy(best_analogy.rules_used, goal)
        adapted_actions = self._adapt_actions_from_analogy(best_analogy.action_sequence, goal)
        
        # 调整预期成功率（类比通常不如直接匹配准确）
        analogical_success_rate = best_analogy.expected_success_rate * 0.8
        
        return BridgePlan(
            plan_id=f"analogical_{time.time()}",
            goal=goal,
            rules_used=adapted_rules,
            reasoning_strategy=ReasoningStrategy.ANALOGICAL_REASONING,
            action_sequence=adapted_actions,
            expected_success_rate=analogical_success_rate,
            expected_cost=best_analogy.expected_cost * 1.2,  # 类比可能增加成本
            estimated_time=best_analogy.estimated_time
        )
    
    def _create_fallback_plan(self, goal: Goal, strategy: ReasoningStrategy) -> BridgePlan:
        """创建备用方案，确保总能生成有效的桥梁方案"""
        # 生成基础行动序列
        fallback_actions = self._generate_fallback_actions(goal)
        
        # 创建虚拟规律（代表内置行为模式）
        fallback_rule = Rule(
            rule_id=f"fallback_{goal.goal_type.value}_{time.time()}",
            rule_type="action",
            conditions={"goal_type": goal.goal_type.value},
            predictions={"action": fallback_actions[0] if fallback_actions else "observe"},
            confidence=0.5,  # 中等置信度
            applicable_contexts=[goal.goal_type.value]
        )
        
        return BridgePlan(
            plan_id=f"fallback_{strategy.value}_{time.time()}",
            goal=goal,
            rules_used=[fallback_rule],
            reasoning_strategy=strategy,
            action_sequence=fallback_actions,
            expected_success_rate=0.4,  # 基础成功率
            expected_cost=1.0,
            estimated_time=2.0
        )
    
    def _generate_fallback_actions(self, goal: Goal) -> List[str]:
        """为不同目标类型生成备用行动序列"""
        fallback_actions = {
            GoalType.SURVIVAL: ["assess_threats", "secure_resources"],
            GoalType.RESOURCE_ACQUISITION: ["search", "collect"],
            GoalType.THREAT_AVOIDANCE: ["detect_danger", "escape"],
            GoalType.EXPLORATION: ["move", "observe"],
            GoalType.SOCIAL_INTERACTION: ["approach", "communicate"],
            GoalType.LEARNING: ["observe", "experiment"]
        }
        
        return fallback_actions.get(goal.goal_type, ["observe", "move"])
    
    def _causal_chaining(self, goal: Goal) -> Optional[BridgePlan]:
        """因果链推理"""
        # 构建从当前状态到目标状态的因果链
        current_state = goal.context.get('current_state', {})
        target_state = goal.context.get('target_state', {})
        
        if not current_state or not target_state:
            return self._multi_rule_combination(goal)
        
        # 寻找因果规律
        causal_rules = [rule for rule in self.available_rules if rule.rule_type == "causal"]
        
        if not causal_rules:
            return self._multi_rule_combination(goal)
        
        # 构建因果链
        causal_chain = self._build_causal_chain(current_state, target_state, causal_rules)
        
        if not causal_chain:
            # 如果无法构建因果链，创建备用方案
            return self._create_fallback_plan(goal, ReasoningStrategy.CAUSAL_CHAINING)
        
        # 将因果链转换为行动序列
        action_sequence = self._causal_chain_to_actions(causal_chain, goal)
        
        # 计算因果链的可靠性
        chain_reliability = np.prod([rule.confidence for rule in causal_chain])
        
        return BridgePlan(
            plan_id=f"causal_{time.time()}",
            goal=goal,
            rules_used=causal_chain,
            reasoning_strategy=ReasoningStrategy.CAUSAL_CHAINING,
            action_sequence=action_sequence,
            expected_success_rate=chain_reliability,
            expected_cost=len(causal_chain) * 0.7,
            estimated_time=len(causal_chain) * 2.0
        )
    
    def execute_bridge(self, bridge_plan: BridgePlan) -> Dict[str, Any]:
        """阶段3：方案选择与实践检验（"择桥而行"与"过桥检验"）"""
        if not bridge_plan:
            return {"success": False, "reason": "无可执行方案"}
        
        execution_result = {
            "success": False,
            "actions_completed": 0,
            "total_actions": len(bridge_plan.action_sequence),
            "execution_time": 0.0,
            "obstacles_encountered": [],
            "actual_cost": 0.0,
            "bridge_quality": BridgeQuality.FAILED
        }
        
        start_time = time.time()
        
        # 逐步执行行动序列
        for i, action in enumerate(bridge_plan.action_sequence):
            action_success = self._execute_single_action(action, bridge_plan.goal)
            execution_result["actions_completed"] += 1
            execution_result["actual_cost"] += self._calculate_action_cost(action)
            
            if not action_success:
                # 行动失败，检查是否有应急预案
                if bridge_plan.contingency_plans:
                    contingency_result = self._try_contingency_plans(bridge_plan.contingency_plans, i)
                    if contingency_result["success"]:
                        action_success = True
                        execution_result["obstacles_encountered"].append(f"行动{i}失败但应急预案成功")
                    else:
                        execution_result["obstacles_encountered"].append(f"行动{i}失败，应急预案也失败")
                        break
                else:
                    execution_result["obstacles_encountered"].append(f"行动{i}失败，无应急预案")
                    break
        
        execution_result["execution_time"] = time.time() - start_time
        execution_result["success"] = execution_result["actions_completed"] == execution_result["total_actions"]
        
        # 评估桥梁质量
        execution_result["bridge_quality"] = self._evaluate_bridge_quality(execution_result, bridge_plan)
        
        # 记录执行结果
        self.bridge_history.append({
            "bridge_plan": bridge_plan,
            "execution_result": execution_result,
            "timestamp": time.time()
        })
        
        if execution_result["success"]:
            self.successful_bridges.append(bridge_plan)
        else:
            self.failed_bridges.append(bridge_plan)
        
        # 更新性能统计
        self._update_performance_stats(bridge_plan, execution_result)
        
        if self.logger:
            quality = execution_result["bridge_quality"].value
            success_str = "成功" if execution_result["success"] else "失败"
            self.logger.log(
                f"WBM桥梁执行{success_str}: {bridge_plan.goal.description} | "
                f"质量:{quality} | 完成度:{execution_result['actions_completed']}/{execution_result['total_actions']}"
            )
        
        return execution_result
    
    def evaluate_and_adapt(self, bridge_plan: BridgePlan, execution_result: Dict[str, Any]) -> None:
        """阶段4：结果评估与知识调整"""
        success = execution_result["success"]
        bridge_quality = execution_result["bridge_quality"]
        
        # 更新规律效果记录
        for rule in bridge_plan.rules_used:
            rule.usage_count += 1
            if success:
                rule.success_count += 1
            rule.last_used = time.time()
            
            # 记录规律效果
            rule_id = rule.rule_id
            if rule_id not in self.rule_effectiveness:
                self.rule_effectiveness[rule_id] = {"success": 0, "total": 0, "quality_sum": 0}
            
            self.rule_effectiveness[rule_id]["total"] += 1
            if success:
                self.rule_effectiveness[rule_id]["success"] += 1
            
            # 记录质量分数
            quality_scores = {
                BridgeQuality.EXCELLENT: 1.0,
                BridgeQuality.GOOD: 0.8,
                BridgeQuality.ACCEPTABLE: 0.6,
                BridgeQuality.POOR: 0.3,
                BridgeQuality.FAILED: 0.0
            }
            self.rule_effectiveness[rule_id]["quality_sum"] += quality_scores[bridge_quality]
        
        # 更新推理策略表现
        strategy = bridge_plan.reasoning_strategy.value
        self.strategy_performance[strategy]["total"] += 1
        if success:
            self.strategy_performance[strategy]["success"] += 1
        
        # 更新偏好策略
        goal_type = bridge_plan.goal.goal_type.value
        if success and bridge_quality in [BridgeQuality.EXCELLENT, BridgeQuality.GOOD]:
            self.preferred_strategies[goal_type] = bridge_plan.reasoning_strategy
        
        # 学习推理模式
        self._learn_reasoning_patterns(bridge_plan, execution_result)
        
        if self.logger:
            success_rate = self.rule_effectiveness.get(bridge_plan.rules_used[0].rule_id, {}).get("success", 0) / max(1, self.rule_effectiveness.get(bridge_plan.rules_used[0].rule_id, {}).get("total", 1))
            self.logger.log(f"WBM知识调整: 策略{strategy}表现更新，主要规律成功率:{success_rate:.2f}")
    
    def trigger_learning(self, failed_goal: Goal) -> Dict[str, Any]:
        """阶段5：知识不足与触发新一轮学习（"寻找更多木头"）"""
        learning_needs = {
            "missing_rules": [],
            "weak_rules": [],
            "exploration_suggestions": [],
            "social_learning_opportunities": []
        }
        
        # 分析失败原因
        failure_analysis = self._analyze_goal_failure(failed_goal)
        
        # 识别缺失的规律类型
        missing_rule_types = self._identify_missing_rules(failed_goal, failure_analysis)
        learning_needs["missing_rules"] = missing_rule_types
        
        # 识别需要强化的弱规律
        weak_rules = self._identify_weak_rules(failed_goal)
        learning_needs["weak_rules"] = weak_rules
        
        # 生成探索建议
        exploration_suggestions = self._generate_exploration_suggestions(failed_goal)
        learning_needs["exploration_suggestions"] = exploration_suggestions
        
        # 生成社交学习机会
        social_opportunities = self._generate_social_learning_opportunities(failed_goal)
        learning_needs["social_learning_opportunities"] = social_opportunities
        
        if self.logger:
            self.logger.log(
                f"WBM触发学习: {failed_goal.description} | "
                f"缺失规律:{len(missing_rule_types)} | "
                f"弱规律:{len(weak_rules)} | "
                f"探索建议:{len(exploration_suggestions)}"
            )
        
        return learning_needs
    
    # 辅助方法
    def _rule_to_actions(self, rule: Rule, goal: Goal) -> List[str]:
        """将规律转换为行动序列 - 🔧 重构：基于规律内容的智能动作生成"""
        actions = []
        
        # 1. 优先从规律的预测结果中提取动作
        if isinstance(rule.predictions, dict):
            # 直接动作预测
            if "action" in rule.predictions:
                action = rule.predictions["action"]
                if isinstance(action, str) and action.strip():
                    actions.append(action)
            
            # 从预期结果推导动作
            if "expected_result" in rule.predictions:
                result = rule.predictions["expected_result"]
                derived_action = self._derive_action_from_expected_result(result, goal)
                if derived_action:
                    actions.append(derived_action)
            
            # 从工具使用推导动作
            if "action_or_tool" in rule.predictions:
                tool_action = rule.predictions["action_or_tool"]
                contextual_action = self._contextualize_tool_action(tool_action, rule.conditions, goal)
                if contextual_action:
                    actions.append(contextual_action)
        
        # 2. 从规律条件中推导反应性动作
        if isinstance(rule.conditions, dict):
            condition_based_actions = self._derive_actions_from_conditions(rule.conditions, goal)
            actions.extend(condition_based_actions)
        
        # 3. 基于规律类型的语义推理
        semantic_actions = self._derive_semantic_actions(rule, goal)
        actions.extend(semantic_actions)
        
        # 4. 如果仍然没有动作，进行智能回退
        if not actions:
            fallback_action = self._intelligent_fallback_action(rule, goal)
            if fallback_action:
                actions.append(fallback_action)
        
        # 5. 去重并验证动作有效性
        valid_actions = []
        seen_actions = set()
        for action in actions:
            if action and action not in seen_actions and self._is_valid_action(action):
                valid_actions.append(action)
                seen_actions.add(action)
        
        return valid_actions if valid_actions else ["observe_and_assess"]
    
    def _derive_action_from_expected_result(self, expected_result: Any, goal: Goal) -> Optional[str]:
        """从预期结果推导动作"""
        if not expected_result:
            return None
        
        result_str = str(expected_result).lower()
        
        # 结果→动作映射（基于因果关系）
        result_action_mapping = {
            "success": "execute_optimal_strategy",
            "safety": "move_to_safe_location", 
            "food": "collect_food_resource",
            "water": "collect_water_resource",
            "shelter": "build_temporary_shelter",
            "escape": "execute_escape_route",
            "hide": "find_concealed_position",
            "avoid": "maintain_safe_distance",
            "gather": "collect_available_resources",
            "hunt": "track_and_pursue_target",
            "flee": "retreat_from_danger",
            "climb": "ascend_to_higher_ground",
            "swim": "navigate_water_obstacle"
        }
        
        # 查找匹配的结果类型
        for result_key, action in result_action_mapping.items():
            if result_key in result_str:
                return action
        
        return None
    
    def _contextualize_tool_action(self, tool_action: Any, conditions: Dict[str, Any], goal: Goal) -> Optional[str]:
        """将工具动作上下文化为具体行动"""
        if not tool_action:
            return None
        
        tool_str = str(tool_action).lower()
        
        # 基于条件上下文化工具使用
        if isinstance(conditions, dict):
            # 环境上下文
            if "condition_element" in conditions:
                element = str(conditions["condition_element"]).lower()
                if "water" in element and "gather" in tool_str:
                    return "collect_water_from_source"
                elif "forest" in element and "gather" in tool_str:
                    return "forage_in_forest"
                elif "open_field" in element and "gather" in tool_str:
                    return "search_open_area"
            
            # 植物采集上下文
            if "plant_type" in conditions:
                plant_type = str(conditions["plant_type"]).lower()
                if "ground_plant" in plant_type:
                    return "harvest_ground_vegetation"
                elif "tree" in plant_type:
                    return "climb_and_collect_fruit"
        
        # 通用工具动作映射
        tool_action_mapping = {
            "gather": "collect_nearby_resources",
            "hunt": "track_potential_prey", 
            "build": "construct_shelter_structure",
            "climb": "scale_vertical_obstacle",
            "swim": "cross_water_body",
            "dig": "excavate_underground_resource"
        }
        
        for tool_key, action in tool_action_mapping.items():
            if tool_key in tool_str:
                return action
        
        return None
    
    def _derive_actions_from_conditions(self, conditions: Dict[str, Any], goal: Goal) -> List[str]:
        """从规律条件推导反应性动作"""
        actions = []
        
        for key, value in conditions.items():
            key_str = str(key).lower()
            value_str = str(value).lower()
            
            # 威胁相关条件
            if "threat" in key_str or "danger" in key_str:
                if "true" in value_str or "nearby" in value_str:
                    actions.append("assess_threat_level")
                    actions.append("identify_escape_routes")
            
            # 资源相关条件
            elif "resource" in key_str or "food" in key_str or "water" in key_str:
                if "available" in value_str or "present" in value_str:
                    actions.append("evaluate_resource_quality")
                    actions.append("plan_resource_extraction")
            
            # 环境相关条件
            elif "environment" in key_str or "location" in key_str:
                actions.append("survey_environmental_features")
                if "forest" in value_str:
                    actions.append("navigate_forest_terrain")
                elif "water" in value_str:
                    actions.append("assess_water_safety")
            
            # 动物相关条件
            elif "animal" in key_str:
                if "dangerous" in value_str or "predator" in value_str:
                    actions.append("maintain_defensive_posture")
                elif "prey" in value_str:
                    actions.append("evaluate_hunting_opportunity")
        
        return actions
    
    def _derive_semantic_actions(self, rule: Rule, goal: Goal) -> List[str]:
        """基于规律语义类型推导动作"""
        actions = []
        
        # 分析规律ID中的语义信息
        rule_id = rule.rule_id.lower()
        
        # E-A-R规律（Environment-Action-Result）
        if "e-a-r" in rule_id:
            actions.append("analyze_environment_action_relationship")
        
        # 植物采集规律
        elif "plant_collection" in rule_id:
            if "barehanded" in rule_id:
                actions.append("collect_plant_manually")
            else:
                actions.append("use_tool_for_plant_collection")
        
        # 动物相关规律
        elif "animal" in rule_id:
            if "hunt" in rule_id:
                actions.append("execute_hunting_strategy")
            elif "avoid" in rule_id:
                actions.append("implement_avoidance_tactics")
        
        # 环境导航规律
        elif "navigation" in rule_id or "movement" in rule_id:
            actions.append("execute_movement_strategy")
        
        # 生存规律
        elif "survival" in rule_id:
            actions.append("implement_survival_protocol")
        
        return actions
    
    def _intelligent_fallback_action(self, rule: Rule, goal: Goal) -> Optional[str]:
        """智能回退动作生成 - 基于规律和目标的深度分析"""
        
        # 分析规律的核心语义
        rule_semantic = self._analyze_rule_semantics(rule)
        goal_context = goal.context if hasattr(goal, 'context') else {}
        
        # 基于规律语义和目标类型的智能匹配
        semantic_goal_mapping = {
            ("threat", GoalType.THREAT_AVOIDANCE): "execute_threat_mitigation_strategy",
            ("resource", GoalType.RESOURCE_ACQUISITION): "implement_resource_gathering_plan",
            ("exploration", GoalType.EXPLORATION): "conduct_systematic_exploration",
            ("environment", GoalType.EXPLORATION): "survey_environmental_conditions",
            ("survival", GoalType.SURVIVAL): "activate_survival_protocols",
            ("social", GoalType.SOCIAL_INTERACTION): "initiate_social_engagement"
        }
        
        # 查找最佳匹配
        for (semantic, goal_type), action in semantic_goal_mapping.items():
            if semantic in rule_semantic and goal.goal_type == goal_type:
                return action
        
        # 通用智能回退
        if goal.goal_type == GoalType.THREAT_AVOIDANCE:
            return "assess_and_respond_to_threats"
        elif goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            return "search_for_available_resources"
        elif goal.goal_type == GoalType.EXPLORATION:
            return "explore_immediate_surroundings"
        else:
            return "observe_and_plan_next_action"
    
    def _analyze_rule_semantics(self, rule: Rule) -> str:
        """分析规律的核心语义"""
        # 综合分析规律ID、条件和预测
        semantic_indicators = []
        
        # 从规律ID提取语义
        rule_id_lower = rule.rule_id.lower()
        if "threat" in rule_id_lower or "danger" in rule_id_lower:
            semantic_indicators.append("threat")
        if "resource" in rule_id_lower or "food" in rule_id_lower or "water" in rule_id_lower:
            semantic_indicators.append("resource")
        if "plant" in rule_id_lower or "animal" in rule_id_lower:
            semantic_indicators.append("environment")
        if "exploration" in rule_id_lower or "navigate" in rule_id_lower:
            semantic_indicators.append("exploration")
        
        # 从条件提取语义
        if isinstance(rule.conditions, dict):
            for key, value in rule.conditions.items():
                key_str = str(key).lower()
                value_str = str(value).lower()
                if "threat" in key_str or "danger" in key_str:
                    semantic_indicators.append("threat")
                elif "resource" in key_str:
                    semantic_indicators.append("resource")
                elif "environment" in key_str:
                    semantic_indicators.append("environment")
        
        # 返回最主要的语义
        if semantic_indicators:
            return max(set(semantic_indicators), key=semantic_indicators.count)
        return "general"
    
    def _is_valid_action(self, action: str) -> bool:
        """验证动作是否有效"""
        if not action or not isinstance(action, str):
            return False
        
        # 检查动作格式
        action = action.strip()
        if len(action) < 3:  # 太短的动作无效
            return False
        
        # 排除无意义的动作
        invalid_actions = {"", "none", "null", "undefined", "error"}
        if action.lower() in invalid_actions:
            return False
        
        return True
    
    def _evaluate_rule_contribution(self, rule: Rule, existing_rules: List[Rule], goal: Goal) -> float:
        """评估规律对目标的贡献度"""
        base_score = rule.confidence * rule.get_success_rate()
        
        # 考虑与现有规律的互补性
        complementarity = 1.0
        for existing_rule in existing_rules:
            if self._rules_are_redundant(rule, existing_rule):
                complementarity *= 0.5  # 冗余规律降低贡献
        
        # 考虑与目标的相关性
        relevance = self._calculate_rule_goal_relevance(rule, goal)
        
        return base_score * complementarity * relevance
    
    def _calculate_combined_success_rate(self, rules: List[Rule]) -> float:
        """计算组合规律的成功率"""
        if not rules:
            return 0.0
        
        # 简化计算：加权平均，考虑规律间的协同效应
        individual_rates = [rule.confidence * rule.get_success_rate() for rule in rules]
        base_rate = sum(individual_rates) / len(individual_rates)
        
        # 多规律协同可能有额外收益，但也有失败风险
        synergy_bonus = min(0.2, len(rules) * 0.05)
        coordination_risk = max(0.1, len(rules) * 0.02)
        
        return max(0.0, min(1.0, base_rate + synergy_bonus - coordination_risk))
    
    def _combine_rules_to_actions(self, rules: List[Rule], goal: Goal) -> List[str]:
        """组合多个规律生成行动序列"""
        all_actions = []
        for rule in rules:
            rule_actions = self._rule_to_actions(rule, goal)
            all_actions.extend(rule_actions)
        
        # 去重并排序
        unique_actions = list(dict.fromkeys(all_actions))  # 保持顺序的去重
        
        # 基于目标类型优化行动顺序
        optimized_actions = self._optimize_action_sequence(unique_actions, goal)
        
        return optimized_actions
    
    def _optimize_action_sequence(self, actions: List[str], goal: Goal) -> List[str]:
        """优化行动序列"""
        # 简化实现：基于行动优先级重新排序
        action_priorities = {
            "assess_threats": 10,
            "detect_danger": 10,
            "escape": 9,
            "secure_resources": 8,
            "search": 7,
            "collect": 6,
            "approach": 5,
            "communicate": 4,
            "observe": 3,
            "experiment": 2,
            "move": 1
        }
        
        # 按优先级排序
        sorted_actions = sorted(actions, key=lambda a: action_priorities.get(a, 0), reverse=True)
        
        return sorted_actions
    
    def get_bridge_statistics(self) -> Dict[str, Any]:
        """获取桥梁建造统计"""
        total_bridges = len(self.bridge_history)
        successful_bridges = len(self.successful_bridges)
        
        strategy_stats = {}
        for strategy, perf in self.strategy_performance.items():
            if perf['total'] > 0:
                strategy_stats[strategy] = {
                    'usage_count': perf['total'],
                    'success_rate': perf['success'] / perf['total'],
                    'success_count': perf['success']
                }
        
        quality_distribution = defaultdict(int)
        for bridge_record in self.bridge_history:
            quality = bridge_record['execution_result']['bridge_quality']
            quality_distribution[quality.value] += 1
        
        return {
            'total_bridges_built': total_bridges,
            'successful_bridges': successful_bridges,
            'success_rate': successful_bridges / max(total_bridges, 1),
            'strategy_performance': strategy_stats,
            'quality_distribution': dict(quality_distribution),
            'average_rules_per_bridge': np.mean([len(b.rules_used) for b in self.successful_bridges]) if self.successful_bridges else 0,
            'current_active_goals': len(self.current_goals),
            'goal_achievement_rate': self.performance_stats['goal_achievement_rate']
        }
    
    def get_reasoning_insights(self) -> Dict[str, Any]:
        """获取推理洞察"""
        return {
            'preferred_strategies': {k: v.value for k, v in self.preferred_strategies.items()},
            'reasoning_patterns': dict(self.reasoning_patterns),
            'rule_effectiveness_summary': self._summarize_rule_effectiveness(),
            'learning_opportunities': self._identify_current_learning_opportunities(),
            'bridge_quality_trends': self._analyze_bridge_quality_trends()
        }
    
    # 继续辅助方法实现
    def _assess_bridge_risks(self, bridge_plan: BridgePlan) -> None:
        """评估桥梁方案风险"""
        risks = []
        
        # 规律置信度风险
        low_confidence_rules = [r for r in bridge_plan.rules_used if r.confidence < 0.5]
        if low_confidence_rules:
            risks.append(f"存在{len(low_confidence_rules)}个低置信度规律")
        
        # 规律使用历史风险
        untested_rules = [r for r in bridge_plan.rules_used if r.usage_count == 0]
        if untested_rules:
            risks.append(f"存在{len(untested_rules)}个未测试规律")
        
        # 复杂度风险
        if len(bridge_plan.rules_used) > 5:
            risks.append("规律组合过于复杂，协调风险高")
        
        # 时间压力风险
        if bridge_plan.goal.deadline and bridge_plan.estimated_time > (bridge_plan.goal.deadline - time.time()):
            risks.append("估计执行时间超过目标截止时间")
        
        bridge_plan.risk_factors = risks
    
    def _create_contingency_plans(self, main_plan: BridgePlan) -> List[BridgePlan]:
        """创建应急预案"""
        contingency_plans = []
        
        # 简化版应急预案：尝试不同的推理策略
        alternative_strategies = [s for s in ReasoningStrategy if s != main_plan.reasoning_strategy]
        
        for alt_strategy in alternative_strategies[:2]:  # 最多创建2个应急预案
            alt_plan = self._construct_bridge_plan(main_plan.goal, alt_strategy)
            if alt_plan and alt_plan.expected_success_rate > 0.3:
                alt_plan.plan_id = f"contingency_{alt_strategy.value}_{time.time()}"
                contingency_plans.append(alt_plan)
        
        return contingency_plans
    
    def _execute_single_action(self, action: str, goal: Goal) -> bool:
        """执行单个行动（模拟）"""
        # 模拟行动执行，基于行动类型和目标上下文决定成功率
        success_probabilities = {
            "assess_threats": 0.8,
            "detect_danger": 0.7,
            "escape": 0.6,
            "secure_resources": 0.5,
            "search": 0.7,
            "collect": 0.8,
            "approach": 0.6,
            "communicate": 0.5,
            "observe": 0.9,
            "experiment": 0.4,
            "move": 0.8
        }
        
        base_prob = success_probabilities.get(action, 0.5)
        
        # 基于目标上下文调整成功率
        difficulty = goal.context.get('difficulty', 0.5)
        adjusted_prob = base_prob * (1.0 - difficulty * 0.3)
        
        return random.random() < adjusted_prob
    
    def _calculate_action_cost(self, action: str) -> float:
        """计算行动成本"""
        action_costs = {
            "assess_threats": 0.1,
            "detect_danger": 0.2,
            "escape": 0.5,
            "secure_resources": 0.8,
            "search": 0.3,
            "collect": 0.4,
            "approach": 0.2,
            "communicate": 0.3,
            "observe": 0.1,
            "experiment": 0.6,
            "move": 0.2
        }
        return action_costs.get(action, 0.3)
    
    def _try_contingency_plans(self, contingency_plans: List[BridgePlan], failed_action_index: int) -> Dict[str, Any]:
        """尝试应急预案"""
        for plan in contingency_plans:
            # 简化实现：尝试从失败点继续执行应急预案
            remaining_actions = plan.action_sequence[failed_action_index:]
            success_count = 0
            
            for action in remaining_actions:
                if self._execute_single_action(action, plan.goal):
                    success_count += 1
                else:
                    break
            
            if success_count == len(remaining_actions):
                return {"success": True, "plan_used": plan.plan_id}
        
        return {"success": False, "reason": "所有应急预案均失败"}
    
    def _evaluate_bridge_quality(self, execution_result: Dict[str, Any], bridge_plan: BridgePlan) -> BridgeQuality:
        """评估桥梁质量"""
        success_rate = execution_result["actions_completed"] / max(execution_result["total_actions"], 1)
        
        if success_rate >= 0.9:
            return BridgeQuality.EXCELLENT
        elif success_rate >= 0.7:
            return BridgeQuality.GOOD
        elif success_rate >= 0.5:
            return BridgeQuality.ACCEPTABLE
        elif success_rate >= 0.3:
            return BridgeQuality.POOR
        else:
            return BridgeQuality.FAILED
    
    def _update_performance_stats(self, bridge_plan: BridgePlan, execution_result: Dict[str, Any]) -> None:
        """更新性能统计"""
        self.performance_stats['total_bridges_built'] += 1
        
        if execution_result['success']:
            self.performance_stats['successful_bridges'] += 1
        
        # 更新目标达成率
        total_goals = len(self.goal_history)
        achieved_goals = sum(1 for record in self.bridge_history if record['execution_result']['success'])
        self.performance_stats['goal_achievement_rate'] = achieved_goals / max(total_goals, 1)
        
        # 更新平均桥梁质量
        quality_scores = {
            BridgeQuality.EXCELLENT: 1.0,
            BridgeQuality.GOOD: 0.8,
            BridgeQuality.ACCEPTABLE: 0.6,
            BridgeQuality.POOR: 0.3,
            BridgeQuality.FAILED: 0.0
        }
        
        total_quality = sum(quality_scores[record['execution_result']['bridge_quality']] 
                          for record in self.bridge_history)
        self.performance_stats['average_bridge_quality'] = total_quality / max(len(self.bridge_history), 1)
    
    def _learn_reasoning_patterns(self, bridge_plan: BridgePlan, execution_result: Dict[str, Any]) -> None:
        """学习推理模式"""
        pattern_key = f"{bridge_plan.goal.goal_type.value}_{bridge_plan.reasoning_strategy.value}"
        
        if pattern_key not in self.reasoning_patterns:
            self.reasoning_patterns[pattern_key] = {
                'usage_count': 0,
                'success_count': 0,
                'average_quality': 0.0,
                'typical_rule_count': 0,
                'common_obstacles': []
            }
        
        pattern = self.reasoning_patterns[pattern_key]
        pattern['usage_count'] += 1
        
        if execution_result['success']:
            pattern['success_count'] += 1
        
        # 更新平均质量
        quality_scores = {
            BridgeQuality.EXCELLENT: 1.0,
            BridgeQuality.GOOD: 0.8,
            BridgeQuality.ACCEPTABLE: 0.6,
            BridgeQuality.POOR: 0.3,
            BridgeQuality.FAILED: 0.0
        }
        
        current_quality = quality_scores[execution_result['bridge_quality']]
        pattern['average_quality'] = ((pattern['average_quality'] * (pattern['usage_count'] - 1) + 
                                     current_quality) / pattern['usage_count'])
        
        # 更新典型规律数量
        pattern['typical_rule_count'] = ((pattern['typical_rule_count'] * (pattern['usage_count'] - 1) + 
                                        len(bridge_plan.rules_used)) / pattern['usage_count'])
        
        # 记录常见障碍
        for obstacle in execution_result.get('obstacles_encountered', []):
            if obstacle not in pattern['common_obstacles']:
                pattern['common_obstacles'].append(obstacle)
    
    def _analyze_goal_failure(self, failed_goal: Goal) -> Dict[str, Any]:
        """分析目标失败原因"""
        # 查找相关的失败桥梁
        related_failures = [
            record for record in self.bridge_history
            if (record['bridge_plan'].goal.goal_type == failed_goal.goal_type and
                not record['execution_result']['success'])
        ]
        
        failure_patterns = {
            'common_failure_points': [],
            'insufficient_rules': 0,
            'execution_failures': 0,
            'planning_failures': 0
        }
        
        for failure in related_failures:
            result = failure['execution_result']
            completion_rate = result['actions_completed'] / max(result['total_actions'], 1)
            
            if completion_rate < 0.3:
                failure_patterns['planning_failures'] += 1
            elif completion_rate < 0.8:
                failure_patterns['execution_failures'] += 1
            
            if len(failure['bridge_plan'].rules_used) < 2:
                failure_patterns['insufficient_rules'] += 1
        
        return failure_patterns
    
    def _identify_missing_rules(self, failed_goal: Goal, failure_analysis: Dict[str, Any]) -> List[str]:
        """识别缺失的规律类型"""
        missing_rules = []
        
        # 基于目标类型确定可能缺失的规律
        goal_rule_requirements = {
            GoalType.SURVIVAL: ['threat_detection', 'resource_management', 'risk_assessment'],
            GoalType.RESOURCE_ACQUISITION: ['search_strategy', 'collection_technique', 'efficiency_optimization'],
            GoalType.THREAT_AVOIDANCE: ['danger_recognition', 'escape_planning', 'safety_assessment'],
            GoalType.EXPLORATION: ['navigation', 'observation_technique', 'curiosity_management'],
            GoalType.SOCIAL_INTERACTION: ['communication_protocol', 'social_reading', 'cooperation_strategy'],
            GoalType.LEARNING: ['information_processing', 'pattern_recognition', 'knowledge_integration']
        }
        
        required_rules = goal_rule_requirements.get(failed_goal.goal_type, [])
        
        # 检查现有规律是否覆盖需求
        existing_rule_types = set()
        for rule in self.available_rules:
            if rule.is_applicable_to_context(failed_goal.context):
                existing_rule_types.add(rule.rule_type)
        
        for required_rule in required_rules:
            if required_rule not in existing_rule_types:
                missing_rules.append(required_rule)
        
        return missing_rules
    
    def _identify_weak_rules(self, failed_goal: Goal) -> List[str]:
        """识别需要强化的弱规律"""
        weak_rules = []
        
        for rule_id, effectiveness in self.rule_effectiveness.items():
            if effectiveness['total'] > 3:  # 有足够使用经验
                success_rate = effectiveness['success'] / effectiveness['total']
                if success_rate < 0.4:  # 成功率过低
                    weak_rules.append(rule_id)
        
        return weak_rules
    
    def _generate_exploration_suggestions(self, failed_goal: Goal) -> List[str]:
        """生成探索建议"""
        suggestions = []
        
        # 基于失败原因生成探索建议
        if failed_goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            suggestions.extend([
                "探索新的资源位置",
                "学习更高效的收集技术",
                "观察其他智能体的资源获取行为"
            ])
        elif failed_goal.goal_type == GoalType.THREAT_AVOIDANCE:
            suggestions.extend([
                "识别新的威胁类型",
                "学习更有效的逃脱路径",
                "提高威胁检测敏感度"
            ])
        elif failed_goal.goal_type == GoalType.EXPLORATION:
            suggestions.extend([
                "尝试新的导航策略",
                "扩大探索范围",
                "提高环境观察能力"
            ])
        
        return suggestions
    
    def _generate_social_learning_opportunities(self, failed_goal: Goal) -> List[str]:
        """生成社交学习机会"""
        opportunities = []
        
        # 基于目标类型生成社交学习建议
        if failed_goal.goal_type in [GoalType.SURVIVAL, GoalType.RESOURCE_ACQUISITION]:
            opportunities.extend([
                "观察成功个体的行为策略",
                "参与合作性任务",
                "寻找经验丰富的导师"
            ])
        elif failed_goal.goal_type == GoalType.SOCIAL_INTERACTION:
            opportunities.extend([
                "练习基础沟通技能",
                "参与群体活动",
                "学习社交规范"
            ])
        
        return opportunities
    
    def _find_similar_successful_bridges(self, goal: Goal) -> List[BridgePlan]:
        """寻找类似的成功桥梁案例"""
        similar_bridges = []
        
        for bridge in self.successful_bridges:
            similarity = self._calculate_similarity(goal, bridge.goal)
            if similarity > 0.6:  # 相似度阈值
                similar_bridges.append(bridge)
        
        return similar_bridges
    
    def _calculate_similarity(self, goal1: Goal, goal2: Goal) -> float:
        """计算两个目标的相似度"""
        # 目标类型相似度
        type_similarity = 1.0 if goal1.goal_type == goal2.goal_type else 0.3
        
        # 复杂度相似度
        complexity_diff = abs(goal1.complexity - goal2.complexity)
        complexity_similarity = max(0.0, 1.0 - complexity_diff)
        
        # 上下文相似度
        context_similarity = self._calculate_context_similarity(goal1.context, goal2.context)
        
        return (type_similarity * 0.5 + complexity_similarity * 0.2 + context_similarity * 0.3)
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """计算上下文相似度"""
        if not context1 and not context2:
            return 1.0
        if not context1 or not context2:
            return 0.0
        
        common_keys = set(context1.keys()) & set(context2.keys())
        total_keys = set(context1.keys()) | set(context2.keys())
        
        if not total_keys:
            return 1.0
        
        key_overlap = len(common_keys) / len(total_keys)
        
        # 计算共同键值的相似度
        value_similarity = 0.0
        for key in common_keys:
            if context1[key] == context2[key]:
                value_similarity += 1.0
            elif isinstance(context1[key], (int, float)) and isinstance(context2[key], (int, float)):
                diff = abs(context1[key] - context2[key])
                max_val = max(abs(context1[key]), abs(context2[key]), 1.0)
                value_similarity += max(0.0, 1.0 - diff / max_val)
        
        if common_keys:
            value_similarity /= len(common_keys)
        
        return (key_overlap * 0.6 + value_similarity * 0.4)
    
    def _adapt_rules_from_analogy(self, source_rules: List[Rule], target_goal: Goal) -> List[Rule]:
        """从类比中适配规律"""
        adapted_rules = []
        
        for rule in source_rules:
            # 创建适配的规律副本
            adapted_rule = Rule(
                rule_id=f"adapted_{rule.rule_id}_{time.time()}",
                rule_type=rule.rule_type,
                conditions=self._adapt_conditions(rule.condition_elements, target_goal.context),
                predictions=self._adapt_predictions(rule.predictions, target_goal.context),
                confidence=rule.confidence * 0.8,  # 类比规律置信度降低
                applicable_contexts=rule.applicable_contexts
            )
            adapted_rules.append(adapted_rule)
        
        return adapted_rules
    
    def _adapt_conditions(self, original_conditions: Dict[str, Any], target_context: Dict[str, Any]) -> Dict[str, Any]:
        """适配规律条件"""
        adapted_conditions = original_conditions.copy()
        
        # 简化实现：将原始条件中的值替换为目标上下文中的对应值
        for key in adapted_conditions:
            if key in target_context:
                adapted_conditions[key] = target_context[key]
        
        return adapted_conditions
    
    def _adapt_predictions(self, original_predictions: Dict[str, Any], target_context: Dict[str, Any]) -> Dict[str, Any]:
        """适配规律预测"""
        adapted_predictions = original_predictions.copy()
        
        # 简化实现：保持预测结构，但调整具体值
        if isinstance(adapted_predictions, dict):
            for key, value in adapted_predictions.items():
                if isinstance(value, (int, float)) and key in target_context:
                    if isinstance(target_context[key], (int, float)):
                        # 按比例调整数值预测
                        adapted_predictions[key] = value * (target_context[key] / max(abs(value), 1.0))
        
        return adapted_predictions
    
    def _adapt_actions_from_analogy(self, source_actions: List[str], target_goal: Goal) -> List[str]:
        """从类比中适配行动序列"""
        # 简化实现：直接使用源行动序列，但可能基于目标类型进行微调
        adapted_actions = source_actions.copy()
        
        # 基于目标类型添加特定行动
        if target_goal.goal_type == GoalType.THREAT_AVOIDANCE and "assess_threats" not in adapted_actions:
            adapted_actions.insert(0, "assess_threats")
        elif target_goal.goal_type == GoalType.EXPLORATION and "observe" not in adapted_actions:
            adapted_actions.append("observe")
        
        return adapted_actions
    
    def _build_causal_chain(self, current_state: Dict[str, Any], 
                           target_state: Dict[str, Any], 
                           causal_rules: List[Rule]) -> List[Rule]:
        """构建因果链"""
        # 简化实现：使用广度优先搜索构建因果链
        from collections import deque
        
        queue = deque([(current_state, [])])
        visited = set()
        max_depth = self.config['max_reasoning_depth']
        
        while queue and len(queue[0][1]) < max_depth:
            state, chain = queue.popleft()
            
            state_key = str(sorted(state.items()))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            # 检查是否达到目标状态
            if self._state_matches_target(state, target_state):
                return chain
            
            # 尝试应用每个因果规律
            for rule in causal_rules:
                if rule.is_applicable_to_context(state):
                    new_state = self._apply_rule_to_state(state, rule)
                    new_chain = chain + [rule]
                    queue.append((new_state, new_chain))
        
        return []  # 未找到因果链
    
    def _state_matches_target(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> bool:
        """检查当前状态是否匹配目标状态"""
        for key, target_value in ((target_state.items() if isinstance(target_state, dict) else enumerate(target_state) if isinstance(target_state, list) else []) if isinstance(target_state, dict) else enumerate(target_state) if isinstance(target_state, list) else []):
            if key not in current_state or current_state[key] != target_value:
                return False
        return True
    
    def _apply_rule_to_state(self, state: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
        """将规律应用到状态，产生新状态"""
        new_state = state.copy()
        
        # 应用规律的预测到状态 - 类型安全处理
        if isinstance(rule.predictions, dict):
            for key, value in rule.predictions.items():
                new_state[key] = value
        elif isinstance(rule.predictions, list):
            for i, value in enumerate(rule.predictions):
                new_state[f"prediction_{i}"] = value
        else:
            # 其他类型转换为单一值
            new_state["prediction"] = str(rule.predictions)
        
        return new_state
    
    def _causal_chain_to_actions(self, causal_chain: List[Rule], goal: Goal) -> List[str]:
        """将因果链转换为行动序列"""
        actions = []
        
        for rule in causal_chain:
            rule_actions = self._rule_to_actions(rule, goal)
            actions.extend(rule_actions)
        
        return actions
    
    def _rules_are_redundant(self, rule1: Rule, rule2: Rule) -> bool:
        """检查两个规律是否冗余"""
        # 简化实现：检查条件和预测的重叠度
        condition_overlap = len(set(rule1.conditions.keys()) & set(rule2.conditions.keys()))
        prediction_overlap = len(set(rule1.predictions.keys()) & set(rule2.predictions.keys()))
        
        total_conditions = len(set(rule1.conditions.keys()) | set(rule2.conditions.keys()))
        total_predictions = len(set(rule1.predictions.keys()) | set(rule2.predictions.keys()))
        
        if total_conditions == 0 and total_predictions == 0:
            return True
        
        overlap_ratio = ((condition_overlap + prediction_overlap) / 
                        max(total_conditions + total_predictions, 1))
        
        return overlap_ratio > 0.8
    
    def _calculate_rule_goal_relevance(self, rule: Rule, goal: Goal) -> float:
        """计算规律与目标的相关性"""
        # 基于规律类型和目标类型的匹配度
        relevance_matrix = {
            GoalType.SURVIVAL: {'threat_detection': 1.0, 'resource_management': 0.9, 'action': 0.7},
            GoalType.RESOURCE_ACQUISITION: {'resource_management': 1.0, 'search_strategy': 0.9, 'action': 0.8},
            GoalType.THREAT_AVOIDANCE: {'threat_detection': 1.0, 'danger_recognition': 0.9, 'action': 0.8},
            GoalType.EXPLORATION: {'navigation': 1.0, 'observation_technique': 0.9, 'cognitive': 0.7},
            GoalType.SOCIAL_INTERACTION: {'communication_protocol': 1.0, 'social_reading': 0.9, 'cognitive': 0.6},
            GoalType.LEARNING: {'information_processing': 1.0, 'pattern_recognition': 0.9, 'cognitive': 0.8}
        }
        
        goal_relevance = relevance_matrix.get(goal.goal_type, {})
        return goal_relevance.get(rule.rule_type, 0.5)
    
    def _summarize_rule_effectiveness(self) -> Dict[str, Any]:
        """总结规律效果"""
        if not self.rule_effectiveness:
            return {}
        
        summary = {
            'total_rules_evaluated': len(self.rule_effectiveness),
            'high_performing_rules': 0,
            'low_performing_rules': 0,
            'average_success_rate': 0.0,
            'most_effective_rule': None,
            'least_effective_rule': None
        }
        
        success_rates = []
        best_rule = {'rule_id': None, 'success_rate': 0.0}
        worst_rule = {'rule_id': None, 'success_rate': 1.0}
        
        for rule_id, effectiveness in self.rule_effectiveness.items():
            if effectiveness['total'] > 0:
                success_rate = effectiveness['success'] / effectiveness['total']
                success_rates.append(success_rate)
                
                if success_rate > 0.7:
                    summary['high_performing_rules'] += 1
                elif success_rate < 0.3:
                    summary['low_performing_rules'] += 1
                
                if success_rate > best_rule['success_rate']:
                    best_rule = {'rule_id': rule_id, 'success_rate': success_rate}
                
                if success_rate < worst_rule['success_rate']:
                    worst_rule = {'rule_id': rule_id, 'success_rate': success_rate}
        
        if success_rates:
            summary['average_success_rate'] = sum(success_rates) / len(success_rates)
        
        summary['most_effective_rule'] = best_rule
        summary['least_effective_rule'] = worst_rule
        
        return summary
    
    def _identify_current_learning_opportunities(self) -> List[str]:
        """识别当前学习机会"""
        opportunities = []
        
        # 基于失败模式识别学习机会
        recent_failures = [record for record in self.bridge_history[-10:] 
                          if not record['execution_result']['success']]
        
        if len(recent_failures) > 3:
            opportunities.append("最近失败率过高，需要加强基础规律学习")
        
        # 基于规律效果识别学习机会
        weak_rules = self._identify_weak_rules(Goal(GoalType.LEARNING, "评估", context={}))
        if weak_rules:
            opportunities.append(f"需要强化{len(weak_rules)}个弱规律")
        
        # 基于策略表现识别学习机会
        underperforming_strategies = []
        for strategy, perf in self.strategy_performance.items():
            if perf['total'] > 3 and perf['success'] / perf['total'] < 0.4:
                underperforming_strategies.append(strategy)
        
        if underperforming_strategies:
            opportunities.append(f"需要改进{len(underperforming_strategies)}个推理策略")
        
        return opportunities
    
    def _analyze_bridge_quality_trends(self) -> Dict[str, Any]:
        """分析桥梁质量趋势"""
        if len(self.bridge_history) < 5:
            return {"insufficient_data": True}
        
        recent_qualities = []
        for record in self.bridge_history[-10:]:
            quality = record['execution_result']['bridge_quality']
            quality_scores = {
                BridgeQuality.EXCELLENT: 1.0,
                BridgeQuality.GOOD: 0.8,
                BridgeQuality.ACCEPTABLE: 0.6,
                BridgeQuality.POOR: 0.3,
                BridgeQuality.FAILED: 0.0
            }
            recent_qualities.append(quality_scores[quality])
        
        # 计算趋势
        if len(recent_qualities) >= 5:
            early_avg = sum(recent_qualities[:5]) / 5
            late_avg = sum(recent_qualities[-5:]) / 5
            trend = late_avg - early_avg
        else:
            trend = 0.0
        
        return {
            "recent_average_quality": sum(recent_qualities) / len(recent_qualities),
            "quality_trend": trend,
            "trend_description": "improving" if trend > 0.1 else "declining" if trend < -0.1 else "stable",
            "best_recent_quality": max(recent_qualities),
            "worst_recent_quality": min(recent_qualities)
        } 

    def generate_multi_day_plan(self, goal: Goal, available_rules: List[Rule], 
                               current_state: Dict[str, Any], 
                               max_days: int = 5) -> Optional[MultiDayPlan]:
        """
        生成多日行动计划（长链决策）
        
        Args:
            goal: 目标
            available_rules: 可用规律
            current_state: 当前状态
            max_days: 最大规划天数
            
        Returns:
            MultiDayPlan: 多日计划对象，包含每日具体行动
        """
        if self.logger:
            self.logger.log(f"🗓️ WBM开始生成多日计划 | 目标: {goal.description} | 最大天数: {max_days}")
        
        try:
            # 1. 使用增强链推理生成基础桥梁计划
            target_state = self._extract_target_state_from_goal(goal)
            
            bridge_plan = self.build_enhanced_bridge_with_chains(
                goal=goal,
                available_rules=available_rules,
                start_state=current_state,
                target_state=target_state
            )
            
            if not bridge_plan:
                if self.logger:
                    self.logger.log("❌ 无法生成基础桥梁计划，多日计划失败")
                return None
            
            # 2. 将桥梁计划转换为多日计划
            daily_actions = self._convert_bridge_plan_to_daily_actions(
                bridge_plan, current_state, max_days
            )
            
            if not daily_actions:
                if self.logger:
                    self.logger.log("❌ 无法转换为多日行动，计划失败")
                return None
            
            # 3. 创建多日计划对象
            multi_day_plan = MultiDayPlan(
                plan_id=f"multiday_{int(time.time())}",
                goal=goal,
                bridge_plan=bridge_plan,
                daily_actions=daily_actions,
                creation_time=time.time(),
                current_day=1,
                total_days=len(daily_actions),
                current_state=current_state.copy()
            )
            
            # 4. 记录详细的决策日志
            self._log_multi_day_plan_creation(multi_day_plan)
            
            if self.logger:
                self.logger.log(f"✅ 多日计划生成成功 | 计划ID: {multi_day_plan.plan_id} | 总天数: {multi_day_plan.total_days}")
            
            return multi_day_plan
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 多日计划生成异常: {str(e)}")
            return None
    
    def _convert_bridge_plan_to_daily_actions(self, bridge_plan: BridgePlan, 
                                            current_state: Dict[str, Any], 
                                            max_days: int) -> List[DailyAction]:
        """将桥梁计划转换为每日具体行动"""
        daily_actions = []
        simulated_state = current_state.copy()
        
        if self.logger:
            self.logger.log(f"🔄 开始转换桥梁计划为每日行动 | 动作序列长度: {len(bridge_plan.action_sequence)}")
        
        for day, action in enumerate(bridge_plan.action_sequence[:max_days], 1):
            # 为每个动作生成详细的每日行动
            daily_action = DailyAction(
                day=day,
                action=action,
                reasoning=self._generate_action_reasoning(action, bridge_plan.goal, simulated_state),
                expected_state_change=self._predict_action_state_change(action, simulated_state),
                risk_assessment=self._assess_action_risks(action, simulated_state),
                fallback_actions=self._generate_fallback_actions_for_day(action, bridge_plan.goal),
                confidence=self._calculate_action_confidence(action, bridge_plan.rules_used)
            )
            
            daily_actions.append(daily_action)
            
            # 更新模拟状态以便下一天的规划
            simulated_state = self._simulate_state_after_action(simulated_state, daily_action)
            
            if self.logger:
                self.logger.log(f"  第{day}天: {action} | 推理: {daily_action.reasoning}")
        
        return daily_actions
    
    def _generate_action_reasoning(self, action: str, goal: Goal, state: Dict[str, Any]) -> str:
        """为动作生成推理解释"""
        reasoning_templates = {
            "move_up": "向北移动，探索新区域寻找目标资源",
            "move_down": "向南移动，继续搜索或接近目标", 
            "move_left": "向西移动，扩大搜索范围",
            "move_right": "向东移动，系统性探索区域",
            "drink_water": "补充水分，解决口渴问题",
            "collect_plant": "收集植物，获取食物资源",
            "attack_animal": "攻击动物，获取肉类食物",
            "flee": "逃离危险，保护自身安全",
            "explore": "探索未知区域，寻找资源或机会"
        }
        
        base_reasoning = reasoning_templates.get(action, f"执行{action}以推进目标")
        
        # 根据当前状态和目标调整推理
        if goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            if "水" in goal.description or "water" in goal.description.lower():
                if "move" in action:
                    return f"{base_reasoning}，寻找水源位置"
                elif action == "drink_water":
                    return "到达水源，补充水分解决口渴危机"
            elif "食物" in goal.description or "food" in goal.description.lower():
                if "move" in action:
                    return f"{base_reasoning}，寻找食物来源"
                elif "collect" in action:
                    return "收集发现的食物，补充营养"
        
        return base_reasoning
    
    def _predict_action_state_change(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """预测动作执行后的状态变化"""
        changes = {}
        current_pos = state.get('position', (0, 0))
        
        if action == "move_up":
            changes['position'] = (current_pos[0], current_pos[1] - 1)
        elif action == "move_down":
            changes['position'] = (current_pos[0], current_pos[1] + 1)
        elif action == "move_left":
            changes['position'] = (current_pos[0] - 1, current_pos[1])
        elif action == "move_right":
            changes['position'] = (current_pos[0] + 1, current_pos[1])
        elif action == "drink_water":
            changes['water'] = min(100, state.get('water', 0) + 40)
            changes['thirst_satisfied'] = True
        elif action == "collect_plant":
            changes['food'] = min(100, state.get('food', 0) + 25)
        
        return changes
    
    def _assess_action_risks(self, action: str, state: Dict[str, Any]) -> List[str]:
        """评估动作的风险因素"""
        risks = []
        
        if "move" in action:
            risks.append("移动可能遇到未知威胁")
            if state.get('health', 100) < 50:
                risks.append("健康状况较差，移动风险增加")
        
        if action == "attack_animal":
            risks.append("攻击动物有受伤风险")
            risks.append("可能遭遇更强大的动物")
        
        if state.get('water', 100) < 20 and action != "drink_water":
            risks.append("严重脱水状态下执行其他动作风险很高")
        
        return risks
    
    def _generate_fallback_actions_for_day(self, primary_action: str, goal: Goal) -> List[str]:
        """为每日行动生成备选方案"""
        fallback_actions = []
        
        if "move" in primary_action:
            # 移动动作的备选方案
            fallback_actions = ["explore", "stay_put", "observe_surroundings"]
        elif primary_action == "drink_water":
            fallback_actions = ["search_water", "move_towards_water", "conserve_energy"]
        elif primary_action == "collect_plant":
            fallback_actions = ["search_food", "hunt_animal", "explore_for_resources"]
        
        return fallback_actions
    
    def _calculate_action_confidence(self, action: str, rules_used: List[Rule]) -> float:
        """计算动作的置信度"""
        if not rules_used:
            return 0.5
        
        # 基于相关规律的平均置信度
        relevant_confidences = [rule.confidence for rule in rules_used 
                              if self._is_rule_relevant_to_action(rule, action)]
        
        if relevant_confidences:
            return sum(relevant_confidences) / len(relevant_confidences)
        else:
            return sum(rule.confidence for rule in rules_used) / len(rules_used)
    
    def _is_rule_relevant_to_action(self, rule: Rule, action: str) -> bool:
        """判断规律是否与动作相关"""
        rule_text = str(rule.predictions).lower()
        action_lower = action.lower()
        
        if action_lower in rule_text:
            return True
        
        if "move" in action_lower and "position_change" in rule_text:
            return True
        
        if "water" in action_lower and "water" in rule_text:
            return True
        
        return False
    
    def _simulate_state_after_action(self, current_state: Dict[str, Any], 
                                   daily_action: DailyAction) -> Dict[str, Any]:
        """模拟执行动作后的状态"""
        new_state = current_state.copy()
        new_state.update(daily_action.expected_state_change)
        return new_state
    
    def check_and_adjust_multi_day_plan(self, multi_day_plan: MultiDayPlan, 
                                      current_state: Dict[str, Any],
                                      new_urgent_goals: List[Goal] = None) -> PlanAdjustmentResult:
        """
        检查并调整多日计划（每日执行前调用）
        
        Args:
            multi_day_plan: 当前多日计划
            current_state: 实际当前状态
            new_urgent_goals: 新出现的紧急目标（如躲避老虎）
            
        Returns:
            PlanAdjustmentResult: 调整结果，包含是否需要调整、新计划等
        """
        if self.logger:
            self.logger.log(f"🔍 检查多日计划 | 计划ID: {multi_day_plan.plan_id} | 当前第{multi_day_plan.current_day}天")
        
        adjustment_result = PlanAdjustmentResult(
            needs_adjustment=False,
            adjustment_reason="",
            new_plan=None,
            original_plan=multi_day_plan
        )
        
        # 1. 检查紧急目标（最高优先级）
        if new_urgent_goals:
            urgent_goal = self._find_most_urgent_goal(new_urgent_goals, current_state)
            if urgent_goal and self._is_goal_more_urgent_than_current(urgent_goal, multi_day_plan.goal):
                if self.logger:
                    self.logger.log(f"🚨 发现紧急目标: {urgent_goal.description} | 中断当前计划")
                
                adjustment_result.needs_adjustment = True
                adjustment_result.adjustment_reason = f"紧急目标出现: {urgent_goal.description}"
                
                # 生成紧急应对计划
                emergency_plan = self._generate_emergency_plan(urgent_goal, current_state, multi_day_plan)
                adjustment_result.new_plan = emergency_plan
                
                self._log_plan_interruption(multi_day_plan, urgent_goal)
                return adjustment_result
        
        # 2. 检查当前计划是否仍然可行
        if not self._is_plan_still_feasible(multi_day_plan, current_state):
            if self.logger:
                self.logger.log(f"⚠️ 当前计划不再可行，需要重新规划")
            
            adjustment_result.needs_adjustment = True
            adjustment_result.adjustment_reason = "原计划不再可行，环境或状态发生重大变化"
            
            # 基于当前状态重新生成计划
            available_rules = getattr(self, 'available_rules', [])
            new_plan = self.generate_multi_day_plan(
                multi_day_plan.goal, available_rules, current_state
            )
            adjustment_result.new_plan = new_plan
            
            return adjustment_result
        
        # 3. 检查是否需要微调
        if self._should_fine_tune_plan(multi_day_plan, current_state):
            if self.logger:
                self.logger.log(f"🔧 计划需要微调")
            
            adjustment_result.needs_adjustment = True
            adjustment_result.adjustment_reason = "基于当前状态进行计划微调"
            
            # 微调计划
            adjusted_plan = self._fine_tune_plan(multi_day_plan, current_state)
            adjustment_result.new_plan = adjusted_plan
            
            return adjustment_result
        
        # 4. 计划正常继续
        if self.logger:
            self.logger.log(f"✅ 计划检查通过，继续执行第{multi_day_plan.current_day}天计划")
        
        return adjustment_result
    
    def _find_most_urgent_goal(self, goals: List[Goal], current_state: Dict[str, Any]) -> Optional[Goal]:
        """找到最紧急的目标"""
        if not goals:
            return None
        
        # 威胁规避目标最紧急
        threat_goals = [g for g in goals if g.goal_type == GoalType.THREAT_AVOIDANCE]
        if threat_goals:
            return max(threat_goals, key=lambda g: g.urgency)
        
        # 其他目标按紧急度排序
        return max(goals, key=lambda g: g.calculate_importance())
    
    def _is_goal_more_urgent_than_current(self, new_goal: Goal, current_goal: Goal) -> bool:
        """判断新目标是否比当前目标更紧急"""
        # 威胁规避总是比其他目标更紧急
        if new_goal.goal_type == GoalType.THREAT_AVOIDANCE:
            return True
        
        # 比较紧急度
        return new_goal.calculate_importance() > current_goal.calculate_importance() * 1.5
    
    def _generate_emergency_plan(self, urgent_goal: Goal, current_state: Dict[str, Any], 
                               original_plan: MultiDayPlan) -> Optional[MultiDayPlan]:
        """生成紧急应对计划"""
        if self.logger:
            self.logger.log(f"🚨 生成紧急计划: {urgent_goal.description}")
        
        # 为紧急目标生成短期计划（1-3天）
        available_rules = getattr(self, 'available_rules', [])
        emergency_plan = self.generate_multi_day_plan(
            urgent_goal, available_rules, current_state, max_days=3
        )
        
        if emergency_plan:
            emergency_plan.is_emergency_plan = True
            emergency_plan.original_plan_id = original_plan.plan_id
            emergency_plan.emergency_reason = urgent_goal.description
        
        return emergency_plan
    
    def _is_plan_still_feasible(self, plan: MultiDayPlan, current_state: Dict[str, Any]) -> bool:
        """检查计划是否仍然可行"""
        # 检查健康状况
        if current_state.get('health', 100) < 20:
            return False
        
        # 检查是否偏离预期状态太多
        expected_state = plan.get_expected_state_for_day(plan.current_day)
        if expected_state:
            deviation = self._calculate_state_deviation(current_state, expected_state)
            if deviation > 0.7:  # 偏离度超过70%
                return False
        
        return True
    
    def _should_fine_tune_plan(self, plan: MultiDayPlan, current_state: Dict[str, Any]) -> bool:
        """判断是否需要微调计划"""
        # 检查是否有更好的机会
        if current_state.get('new_opportunities_discovered', False):
            return True
        
        # 检查资源状况是否发生变化
        if self._resource_status_changed_significantly(plan, current_state):
            return True
        
        return False
    
    def _fine_tune_plan(self, original_plan: MultiDayPlan, current_state: Dict[str, Any]) -> Optional[MultiDayPlan]:
        """微调计划"""
        # 保持原有目标，但调整后续行动
        adjusted_plan = original_plan.copy()
        
        # 重新计算剩余天数的行动
        remaining_days = original_plan.total_days - original_plan.current_day + 1
        if remaining_days > 0:
            available_rules = getattr(self, 'available_rules', [])
            new_sub_plan = self.generate_multi_day_plan(
                original_plan.goal, available_rules, current_state, max_days=remaining_days
            )
            
            if new_sub_plan:
                # 替换剩余天数的计划
                adjusted_plan.daily_actions = (
                    original_plan.daily_actions[:original_plan.current_day-1] + 
                    new_sub_plan.daily_actions
                )
                adjusted_plan.total_days = len(adjusted_plan.daily_actions)
        
        return adjusted_plan
    
    def _calculate_state_deviation(self, actual_state: Dict[str, Any], 
                                 expected_state: Dict[str, Any]) -> float:
        """计算实际状态与预期状态的偏离度"""
        if not expected_state:
            return 0.0
        
        deviations = []
        for key, expected_value in expected_state.items():
            if key in actual_state:
                actual_value = actual_state[key]
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    if expected_value != 0:
                        deviation = abs(actual_value - expected_value) / abs(expected_value)
                        deviations.append(min(deviation, 1.0))
        
        return sum(deviations) / len(deviations) if deviations else 0.0
    
    def _resource_status_changed_significantly(self, plan: MultiDayPlan, 
                                             current_state: Dict[str, Any]) -> bool:
        """检查资源状况是否发生重大变化"""
        # 检查水和食物状况
        current_water = current_state.get('water', 100)
        current_food = current_state.get('food', 100)
        
        # 如果资源严重不足，需要调整计划
        if current_water < 20 or current_food < 20:
            return True
        
        return False
    
    def _log_multi_day_plan_creation(self, plan: MultiDayPlan):
        """记录多日计划创建的详细日志"""
        if not self.logger:
            return
        
        self.logger.log("=" * 80)
        self.logger.log(f"🗓️ ILAI长链决策计划生成 | 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log("=" * 80)
        self.logger.log(f"📋 计划ID: {plan.plan_id}")
        self.logger.log(f"🎯 目标: {plan.goal.description}")
        self.logger.log(f"📊 目标类型: {plan.goal.goal_type.value}")
        self.logger.log(f"⚡ 紧急度: {plan.goal.urgency:.2f} | 优先级: {plan.goal.priority:.2f}")
        self.logger.log(f"📅 计划天数: {plan.total_days}天")
        self.logger.log(f"🌉 桥梁策略: {plan.bridge_plan.reasoning_strategy.value}")
        self.logger.log(f"🎲 预期成功率: {plan.bridge_plan.expected_success_rate:.2f}")
        self.logger.log("")
        
        self.logger.log("📅 详细每日行动计划:")
        for daily_action in plan.daily_actions:
            self.logger.log(f"  第{daily_action.day}天:")
            self.logger.log(f"    🎮 动作: {daily_action.action}")
            self.logger.log(f"    🧠 推理: {daily_action.reasoning}")
            self.logger.log(f"    📊 预期变化: {daily_action.expected_state_change}")
            self.logger.log(f"    🎯 置信度: {daily_action.confidence:.2f}")
            if daily_action.risk_assessment:
                self.logger.log(f"    ⚠️ 风险: {', '.join(daily_action.risk_assessment)}")
            if daily_action.fallback_actions:
                self.logger.log(f"    🔄 备选: {', '.join(daily_action.fallback_actions)}")
            self.logger.log("")
        
        if plan.bridge_plan.rules_used:
            self.logger.log("🧱 使用的规律:")
            for rule in plan.bridge_plan.rules_used:
                self.logger.log(f"  - {rule.rule_id}: {rule.confidence:.2f}置信度")
        
        self.logger.log("=" * 80)
        self.logger.log("💡 ILAI智能体现: 长链决策规划 - 能够预见未来几天的行动需求")
        self.logger.log("🔗 规律链推理: 将多个简单规律连接成复杂的多步策略")
        self.logger.log("⚖️ 风险评估: 每步行动都考虑了可能的风险和备选方案")
        self.logger.log("=" * 80)
    
    def _log_plan_interruption(self, original_plan: MultiDayPlan, urgent_goal: Goal):
        """记录计划中断的日志"""
        if not self.logger:
            return
        
        self.logger.log("=" * 80)
        self.logger.log(f"🚨 ILAI智能中断决策 | 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.log("=" * 80)
        self.logger.log(f"📋 原计划ID: {original_plan.plan_id}")
        self.logger.log(f"⏸️ 中断时间: 第{original_plan.current_day}天")
        self.logger.log(f"🎯 原目标: {original_plan.goal.description}")
        self.logger.log(f"🚨 紧急目标: {urgent_goal.description}")
        self.logger.log(f"⚡ 紧急度对比: {urgent_goal.urgency:.2f} vs {original_plan.goal.urgency:.2f}")
        self.logger.log("")
        self.logger.log("🧠 中断推理:")
        self.logger.log(f"  - 发现紧急情况: {urgent_goal.description}")
        self.logger.log(f"  - 评估威胁等级: {urgent_goal.goal_type.value}")
        self.logger.log(f"  - 决定中断当前计划，优先处理紧急情况")
        self.logger.log(f"  - 这体现了ILAI的动态决策能力和生存智能")
        self.logger.log("=" * 80)
    
    def log_daily_plan_execution(self, plan: MultiDayPlan, executed_action: DailyAction, 
                               execution_result: Dict[str, Any]):
        """记录每日计划执行的详细日志"""
        if not self.logger:
            return
        
        self.logger.log("=" * 60)
        self.logger.log(f"📅 第{executed_action.day}天计划执行 | 计划ID: {plan.plan_id}")
        self.logger.log("=" * 60)
        self.logger.log(f"🎮 执行动作: {executed_action.action}")
        self.logger.log(f"🧠 行动推理: {executed_action.reasoning}")
        self.logger.log(f"📊 预期变化: {executed_action.expected_state_change}")
        self.logger.log(f"📈 实际结果: {execution_result}")
        
        # 分析执行效果
        if execution_result.get('success', False):
            self.logger.log(f"✅ 执行成功 | 按计划推进")
        else:
            self.logger.log(f"❌ 执行失败 | 原因: {execution_result.get('failure_reason', '未知')}")
            if executed_action.fallback_actions:
                self.logger.log(f"🔄 备选方案: {', '.join(executed_action.fallback_actions)}")
        
        # 显示剩余计划
        remaining_days = plan.total_days - executed_action.day
        if remaining_days > 0:
            self.logger.log(f"📝 剩余计划: 还有{remaining_days}天行动")
            next_action = plan.get_action_for_day(executed_action.day + 1)
            if next_action:
                self.logger.log(f"🔮 明天计划: {next_action.action} - {next_action.reasoning}")
        else:
            self.logger.log(f"🎉 计划完成 | 目标: {plan.goal.description}")
        
        self.logger.log("=" * 60)