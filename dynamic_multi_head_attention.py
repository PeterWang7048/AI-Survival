#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态多头注意力机制 (Dynamic Multi-Head Attention, DMHA)

借鉴Transformer模型的注意力机制，为DHCA架构提供关键决策辅助。
通过并行处理多个独立的注意力焦点，增强模型捕捉和权衡多样化上下文信息的能力。

核心功能：
1. 资源注意力 (Resource Attention)
2. 危险注意力 (Danger Attention) 
3. 社交注意力 (Social Attention)
4. 探索注意力 (Exploration Attention)

基于斯坦福4.0文档中的认知架构设计。

作者：AI生存游戏项目组
版本：1.0.0
"""

import math
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict


class AttentionFocus(Enum):
    """注意力焦点类型枚举"""
    RESOURCE = "resource"          # 资源注意力
    DANGER = "danger"             # 危险注意力  
    SOCIAL = "social"             # 社交注意力
    EXPLORATION = "exploration"    # 探索注意力


@dataclass
class AttentionHead:
    """单个注意力头的数据结构"""
    focus_type: AttentionFocus    # 注意力焦点类型
    weight: float = 0.25          # 注意力权重
    activation: float = 0.0       # 当前激活强度
    sensitivity: float = 1.0      # 敏感度参数
    decay_rate: float = 0.1       # 衰减率
    
    # 历史记录
    activation_history: List[float] = field(default_factory=list)
    decision_impact: float = 0.0   # 对决策的影响力
    success_rate: float = 0.5     # 成功率统计
    
    def update_activation(self, stimulus: float, context_modifier: float = 1.0):
        """更新注意力激活强度"""
        # 计算新的激活值
        raw_activation = stimulus * self.sensitivity * context_modifier
        
        # 使用调整后的sigmoid函数进行归一化 - 增加敏感性
        if raw_activation > 0:
            self.activation = 1 / (1 + math.exp(-raw_activation + 1))  # 减少偏移，增加敏感性
        else:
            self.activation = 0.1  # 设置最小基线激活
        
        # 记录历史
        self.activation_history.append(self.activation)
        
        # 保持历史记录长度限制
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)
    
    def decay_activation(self):
        """自然衰减激活强度"""
        self.activation *= (1 - self.decay_rate)
    
    def get_attention_score(self) -> float:
        """计算综合注意力得分"""
        return self.weight * self.activation * self.sensitivity


@dataclass
class AttentionContext:
    """注意力上下文信息"""
    # 环境状态
    resources_nearby: List[Dict] = field(default_factory=list)  # 附近资源
    dangers_detected: List[Dict] = field(default_factory=list)  # 检测到的危险
    social_entities: List[Dict] = field(default_factory=list)   # 社交实体
    unexplored_areas: List[Dict] = field(default_factory=list)  # 未探索区域
    
    # 内部状态
    hp: float = 100.0
    food: float = 100.0
    water: float = 100.0
    
    # 认知状态
    development_stage: str = "infant"
    recent_experiences: List[str] = field(default_factory=list)
    current_goals: List[str] = field(default_factory=list)


class DynamicMultiHeadAttention:
    """动态多头注意力机制主类"""
    
    def __init__(self, logger=None, config=None):
        self.logger = logger
        self.config = config or self._default_config()
        
        # 初始化注意力头
        self.attention_heads = {
            AttentionFocus.RESOURCE: AttentionHead(
                focus_type=AttentionFocus.RESOURCE,
                weight=0.25,
                sensitivity=1.8,  # 增加资源注意力敏感度
                decay_rate=0.05
            ),
            AttentionFocus.DANGER: AttentionHead(
                focus_type=AttentionFocus.DANGER,
                weight=0.35,  # 危险注意力初始权重较高
                sensitivity=1.5,
                decay_rate=0.03
            ),
            AttentionFocus.SOCIAL: AttentionHead(
                focus_type=AttentionFocus.SOCIAL,
                weight=0.15,
                sensitivity=0.8,
                decay_rate=0.08
            ),
            AttentionFocus.EXPLORATION: AttentionHead(
                focus_type=AttentionFocus.EXPLORATION,
                weight=0.25,
                sensitivity=1.0,
                decay_rate=0.06
            )
        }
        
        # 注意力调制参数
        self.attention_modulation = {
            'stage_modifiers': {
                'infant': {'resource': 1.2, 'danger': 1.5, 'social': 0.8, 'exploration': 1.0},
                'child': {'resource': 1.0, 'danger': 1.3, 'social': 1.0, 'exploration': 1.2},
                'adolescent': {'resource': 0.9, 'danger': 1.1, 'social': 1.3, 'exploration': 1.1},
                'adult': {'resource': 1.0, 'danger': 1.0, 'social': 1.2, 'exploration': 0.9}
            },
            'state_modifiers': {
                'hp_low': {'resource': 1.3, 'danger': 1.4, 'social': 0.7, 'exploration': 0.6},
                'hp_high': {'resource': 0.8, 'danger': 0.9, 'social': 1.1, 'exploration': 1.2},
                'food_low': {'resource': 1.5, 'danger': 1.1, 'social': 0.8, 'exploration': 0.7},
                'water_low': {'resource': 1.4, 'danger': 1.2, 'social': 0.7, 'exploration': 0.6}
            }
        }
        
        # 性能统计
        self.performance_stats = {
            'total_activations': 0,
            'successful_decisions': 0,
            'focus_usage_count': defaultdict(int),
            'average_attention_scores': defaultdict(list)
        }
        
        if self.logger:
            self.logger.log("DMHA动态多头注意力机制已初始化")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置参数"""
        return {
            'attention_threshold': 0.3,      # 注意力激活阈值
            'weight_adjustment_rate': 0.1,   # 权重调整速率
            'max_attention_history': 100,    # 最大历史记录长度
            'enable_adaptive_weights': True, # 启用自适应权重调整
            'focus_interaction_strength': 0.2, # 焦点间相互作用强度
        }
    
    def process_attention(self, context: AttentionContext) -> Dict[str, Any]:
        """处理注意力机制的主入口"""
        # 1. 计算各个注意力焦点的刺激强度
        stimuli = self._calculate_stimuli(context)
        
        # 2. 获取上下文调制因子
        modifiers = self._get_context_modifiers(context)
        
        # 3. 更新各个注意力头的激活
        for focus_type, head in self.attention_heads.items():
            stimulus = stimuli.get(focus_type.value, 0.0)
            modifier = modifiers.get(focus_type.value, 1.0)
            head.update_activation(stimulus, modifier)
        
        # 4. 动态调整注意力权重
        if self.config['enable_adaptive_weights']:
            self._adjust_attention_weights(context)
        
        # 5. 计算注意力输出
        attention_output = self._compute_attention_output()
        
        # 6. 应用注意力间的相互作用
        attention_output = self._apply_attention_interactions(attention_output)
        
        # 7. 更新性能统计
        self._update_performance_stats(attention_output)
        
        # 8. 自然衰减未激活的注意力
        self._apply_natural_decay()
        
        return attention_output
    
    def _calculate_stimuli(self, context: AttentionContext) -> Dict[str, float]:
        """计算各个注意力焦点的刺激强度"""
        stimuli = {}
        
        # 资源注意力刺激
        resource_stimulus = 0.0
        if context.resources_nearby:
            # 根据资源数量和重要性计算刺激
            for resource in context.resources_nearby:
                distance = resource.get('distance', 1.0)
                value = resource.get('value', 1.0)
                resource_stimulus += value / (1 + distance * 0.5)  # 减少距离衰减
        
        # 考虑内部资源状态 - 增强资源需求的影响
        food_need = max(0, (100 - context.food) / 100) * 2.0  # 增强食物需求影响
        water_need = max(0, (100 - context.water) / 100) * 2.0  # 增强水需求影响
        resource_need = food_need + water_need
        resource_stimulus += resource_need
        
        # 当资源严重不足时额外加强刺激
        if context.food < 30 or context.water < 30:
            resource_stimulus += 1.0  # 紧急资源需求
        
        stimuli['resource'] = resource_stimulus
        
        # 危险注意力刺激
        danger_stimulus = 0.0
        if context.dangers_detected:
            for danger in context.dangers_detected:
                distance = danger.get('distance', 1.0)
                threat_level = danger.get('threat_level', 1.0)
                danger_stimulus += threat_level / (0.5 + distance)  # 距离越近刺激越强
        
        # 考虑当前HP状态
        hp_risk = max(0, (100 - context.hp) / 100) * 1.0
        danger_stimulus += hp_risk
        stimuli['danger'] = danger_stimulus
        
        # 社交注意力刺激
        social_stimulus = 0.0
        if context.social_entities:
            for entity in context.social_entities:
                distance = entity.get('distance', 1.0)
                social_value = entity.get('social_value', 1.0)
                social_stimulus += social_value / (1 + distance)
        stimuli['social'] = social_stimulus
        
        # 探索注意力刺激
        exploration_stimulus = 0.0
        if context.unexplored_areas:
            for area in context.unexplored_areas:
                distance = area.get('distance', 1.0)
                novelty = area.get('novelty', 1.0)
                exploration_stimulus += novelty / (1 + distance)
        
        # 基于好奇心和发育阶段的探索驱动
        curiosity_drive = {'infant': 0.5, 'child': 0.8, 'adolescent': 0.6, 'adult': 0.3}
        exploration_stimulus += curiosity_drive.get(context.development_stage, 0.5)
        stimuli['exploration'] = exploration_stimulus
        
        return stimuli
    
    def _get_context_modifiers(self, context: AttentionContext) -> Dict[str, float]:
        """获取上下文调制因子"""
        modifiers = {}
        
        # 发育阶段调制
        stage_mods = self.attention_modulation['stage_modifiers'].get(
            context.development_stage, 
            self.attention_modulation['stage_modifiers']['infant']
        )
        
        # 状态调制
        state_mods = {'resource': 1.0, 'danger': 1.0, 'social': 1.0, 'exploration': 1.0}
        
        # HP状态调制
        if context.hp < 30:
            hp_mods = self.attention_modulation['state_modifiers']['hp_low']
            for key in state_mods:
                state_mods[key] *= hp_mods[key]
        elif context.hp > 80:
            hp_mods = self.attention_modulation['state_modifiers']['hp_high']
            for key in state_mods:
                state_mods[key] *= hp_mods[key]
        
        # 食物状态调制
        if context.food < 30:
            food_mods = self.attention_modulation['state_modifiers']['food_low']
            for key in state_mods:
                state_mods[key] *= food_mods[key]
        
        # 水状态调制
        if context.water < 30:
            water_mods = self.attention_modulation['state_modifiers']['water_low']
            for key in state_mods:
                state_mods[key] *= water_mods[key]
        
        # 综合调制因子
        for focus_type in ['resource', 'danger', 'social', 'exploration']:
            modifiers[focus_type] = stage_mods[focus_type] * state_mods[focus_type]
        
        return modifiers
    
    def _adjust_attention_weights(self, context: AttentionContext):
        """动态调整注意力权重"""
        # 基于成功率调整权重
        total_weight = 0.0
        for head in self.attention_heads.values():
            # 根据成功率调整权重
            if head.success_rate > 0.7:
                head.weight += self.config['weight_adjustment_rate'] * 0.1
            elif head.success_rate < 0.3:
                head.weight -= self.config['weight_adjustment_rate'] * 0.1
            
            # 确保权重在合理范围内
            head.weight = max(0.05, min(0.5, head.weight))
            total_weight += head.weight
        
        # 归一化权重
        if total_weight > 0:
            for head in self.attention_heads.values():
                head.weight /= total_weight
    
    def _compute_attention_output(self) -> Dict[str, Any]:
        """计算注意力输出"""
        output = {
            'attention_scores': {},
            'dominant_focus': None,
            'attention_distribution': {},
            'total_attention': 0.0,
            'focus_recommendations': {}
        }
        
        # 计算各个注意力得分
        total_score = 0.0
        max_score = 0.0
        dominant_focus = None
        
        for focus_type, head in self.attention_heads.items():
            score = head.get_attention_score()
            output['attention_scores'][focus_type.value] = score
            total_score += score
            
            if score > max_score:
                max_score = score
                dominant_focus = focus_type.value
        
        output['total_attention'] = total_score
        output['dominant_focus'] = dominant_focus
        
        # 计算注意力分布
        if total_score > 0:
            for focus_type, score in output['attention_scores'].items():
                output['attention_distribution'][focus_type] = score / total_score
        
        # 生成焦点推荐
        for focus_type, head in self.attention_heads.items():
            if head.activation > self.config['attention_threshold']:
                output['focus_recommendations'][focus_type.value] = {
                    'priority': head.activation,
                    'confidence': head.success_rate,
                    'action_suggestion': self._get_action_suggestion(focus_type, head.activation)
                }
        
        return output
    
    def _apply_attention_interactions(self, attention_output: Dict[str, Any]) -> Dict[str, Any]:
        """应用注意力间的相互作用"""
        scores = attention_output['attention_scores']
        interaction_strength = self.config['focus_interaction_strength']
        
        # 定义注意力间的相互作用规则
        interactions = {
            'danger-resource': -0.3,    # 危险降低资源注意力
            'danger-exploration': -0.4, # 危险降低探索注意力  
            'resource-exploration': -0.2, # 资源获取时降低探索
            'social-exploration': 0.1,   # 社交促进探索
        }
        
        # 应用相互作用
        adjusted_scores = scores.copy()
        
        danger_score = scores.get('danger', 0)
        if danger_score > 0.5:
            # 高危险时抑制其他注意力
            adjusted_scores['resource'] *= (1 + interactions['danger-resource'] * interaction_strength)
            adjusted_scores['exploration'] *= (1 + interactions['danger-exploration'] * interaction_strength)
        
        resource_score = scores.get('resource', 0)
        if resource_score > 0.6:
            # 资源丰富时可以增加探索
            adjusted_scores['exploration'] *= (1 + interactions['resource-exploration'] * interaction_strength)
        
        social_score = scores.get('social', 0)
        if social_score > 0.4:
            # 社交活跃时促进探索
            adjusted_scores['exploration'] *= (1 + interactions['social-exploration'] * interaction_strength)
        
        # 更新输出
        attention_output['attention_scores'] = adjusted_scores
        
        # 重新计算总分和分布
        total_score = sum(adjusted_scores.values())
        attention_output['total_attention'] = total_score
        
        if total_score > 0:
            for focus_type, score in adjusted_scores.items():
                attention_output['attention_distribution'][focus_type] = score / total_score
        
        return attention_output
    
    def _get_action_suggestion(self, focus_type: AttentionFocus, activation: float) -> str:
        """根据注意力焦点生成行动建议"""
        suggestions = {
            AttentionFocus.RESOURCE: {
                0.3: "扫描周围资源",
                0.5: "移动到资源位置", 
                0.7: "优先收集资源",
                0.9: "专注资源获取"
            },
            AttentionFocus.DANGER: {
                0.3: "提高警惕",
                0.5: "评估威胁等级",
                0.7: "准备防御或逃跑",
                0.9: "立即脱离危险"
            },
            AttentionFocus.SOCIAL: {
                0.3: "注意社交机会",
                0.5: "考虑社交互动",
                0.7: "主动进行社交",
                0.9: "寻求合作"
            },
            AttentionFocus.EXPLORATION: {
                0.3: "记录未知区域",
                0.5: "计划探索路线",
                0.7: "执行探索行动",
                0.9: "深度探索新区域"
            }
        }
        
        focus_suggestions = suggestions.get(focus_type, {})
        
        # 找到最接近的激活阈值
        best_threshold = 0.3
        for threshold in sorted(focus_suggestions.keys()):
            if activation >= threshold:
                best_threshold = threshold
        
        return focus_suggestions.get(best_threshold, "保持当前行为")
    
    def _update_performance_stats(self, attention_output: Dict[str, Any]):
        """更新性能统计"""
        self.performance_stats['total_activations'] += 1
        
        # 记录焦点使用统计
        dominant_focus = attention_output.get('dominant_focus')
        if dominant_focus:
            self.performance_stats['focus_usage_count'][dominant_focus] += 1
        
        # 记录平均注意力得分
        for focus_type, score in attention_output['attention_scores'].items():
            self.performance_stats['average_attention_scores'][focus_type].append(score)
            
            # 保持历史记录长度限制
            if len(self.performance_stats['average_attention_scores'][focus_type]) > 100:
                self.performance_stats['average_attention_scores'][focus_type].pop(0)
    
    def _apply_natural_decay(self):
        """应用自然衰减"""
        for head in self.attention_heads.values():
            head.decay_activation()
    
    def update_success_feedback(self, focus_type: str, success: bool):
        """更新成功反馈，用于调整注意力头的成功率"""
        if focus_type in [f.value for f in AttentionFocus]:
            focus_enum = AttentionFocus(focus_type)
            head = self.attention_heads[focus_enum]
            
            # 使用指数移动平均更新成功率
            alpha = 0.1
            head.success_rate = (1 - alpha) * head.success_rate + alpha * (1.0 if success else 0.0)
            
            if success:
                self.performance_stats['successful_decisions'] += 1
    
    def get_attention_state(self) -> Dict[str, Any]:
        """获取当前注意力状态"""
        return {
            'attention_heads': {
                focus.value: {
                    'weight': head.weight,
                    'activation': head.activation,
                    'sensitivity': head.sensitivity,
                    'success_rate': head.success_rate,
                    'recent_average': np.mean(head.activation_history[-10:]) if head.activation_history else 0.0
                }
                for focus, head in self.attention_heads.items()
            },
            'performance_stats': dict(self.performance_stats),
            'config': self.config
        }
    
    def reset_attention(self):
        """重置注意力状态"""
        for head in self.attention_heads.values():
            head.activation = 0.0
            head.activation_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取DMHA统计信息"""
        stats = {
            'total_activations': self.performance_stats['total_activations'],
            'successful_decisions': self.performance_stats['successful_decisions'],
            'success_rate': 0.0,
            'focus_usage_distribution': dict(self.performance_stats['focus_usage_count']),
            'average_attention_scores': {},
            'attention_head_status': {}
        }
        
        # 计算总体成功率
        if self.performance_stats['total_activations'] > 0:
            stats['success_rate'] = self.performance_stats['successful_decisions'] / self.performance_stats['total_activations']
        
        # 计算平均注意力得分
        for focus_type, scores in self.performance_stats['average_attention_scores'].items():
            if scores:
                stats['average_attention_scores'][focus_type] = np.mean(scores)
        
        # 注意力头状态
        for focus, head in self.attention_heads.items():
            stats['attention_head_status'][focus.value] = {
                'current_weight': head.weight,
                'current_activation': head.activation,
                'success_rate': head.success_rate,
                'sensitivity': head.sensitivity
            }
        
        return stats 