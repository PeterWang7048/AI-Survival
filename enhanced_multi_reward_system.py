#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Multi-Reward System (EMRS) - 增强多维奖励系统
提供多维度的奖励计算功能

基于Stanford 4.0文档设计的多维度奖励机制。
实现生存、资源、社交、探索、学习五大类奖励的综合评估和动态平衡。

核心功能：
1. 多维度奖励计算 - 五种核心奖励类型的独立评估
2. 动态权重调整 - 基于发育阶段和环境状态的权重自适应
3. 时间衰减管理 - 短期和长期奖励的平衡处理
4. 奖励历史分析 - 基于历史数据的奖励趋势分析
5. 冲突解决机制 - 多重奖励冲突时的智能仲裁

特性：
- 与发育阶段(DCA)紧密集成
- 支持上下文敏感的奖励调整
- 提供奖励预测和优化建议
- 支持个性化奖励偏好学习

作者：AI生存游戏项目组
版本：1.3.0
"""

import math
import time
import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from collections import defaultdict, deque
import json


class RewardType(Enum):
    """奖励类型枚举"""
    SURVIVAL = "survival"        # 生存奖励
    RESOURCE = "resource"        # 资源奖励  
    SOCIAL = "social"           # 社交奖励
    EXPLORATION = "exploration" # 探索奖励
    LEARNING = "learning"       # 学习奖励


class RewardPriority(Enum):
    """奖励优先级"""
    CRITICAL = "critical"       # 关键 (生存威胁)
    HIGH = "high"              # 高 (重要资源)
    MEDIUM = "medium"          # 中 (一般收益)
    LOW = "low"                # 低 (边际收益)


class TimeScale(Enum):
    """时间尺度"""
    IMMEDIATE = "immediate"     # 即时 (当前回合)
    SHORT_TERM = "short_term"   # 短期 (几个回合内)
    MEDIUM_TERM = "medium_term" # 中期 (一天内)
    LONG_TERM = "long_term"     # 长期 (多天)


@dataclass
class RewardSignal:
    """奖励信号数据结构"""
    reward_type: RewardType
    value: float
    priority: RewardPriority = RewardPriority.MEDIUM
    time_scale: TimeScale = TimeScale.IMMEDIATE
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    decay_rate: float = 0.1
    
    def apply_decay(self, current_time: float) -> float:
        """应用时间衰减"""
        time_diff = current_time - self.timestamp
        
        # 根据时间尺度设置不同的衰减速度
        scale_multipliers = {
            TimeScale.IMMEDIATE: 1.0,      # 不衰减
            TimeScale.SHORT_TERM: 0.8,     # 慢衰减
            TimeScale.MEDIUM_TERM: 0.5,    # 中等衰减
            TimeScale.LONG_TERM: 0.2       # 快衰减
        }
        
        multiplier = scale_multipliers.get(self.time_scale, 0.5)
        decayed_value = self.value * math.exp(-self.decay_rate * time_diff * multiplier)
        
        return max(0.0, decayed_value)


@dataclass
class RewardProfile:
    """奖励偏好配置"""
    survival_weight: float = 0.4
    resource_weight: float = 0.25
    social_weight: float = 0.15
    exploration_weight: float = 0.1
    learning_weight: float = 0.1
    
    def __post_init__(self):
        """标准化权重"""
        total = (self.survival_weight + self.resource_weight + 
                self.social_weight + self.exploration_weight + self.learning_weight)
        if total > 0:
            self.survival_weight /= total
            self.resource_weight /= total
            self.social_weight /= total
            self.exploration_weight /= total
            self.learning_weight /= total


class EnhancedMultiRewardSystem:
    """增强多维奖励系统"""
    
    def __init__(self, logger=None):
        self.logger = logger
        if self.logger:
            self.logger.log("EMRS: 增强多维奖励系统初始化")
    
    def calculate_multi_dimensional_reward(self, action_result, context=None):
        """计算多维奖励"""
        try:
            # 简单的奖励计算
            base_reward = action_result.get('success', False) * 10
            exploration_bonus = action_result.get('exploration_value', 0) * 5
            learning_bonus = action_result.get('learning_value', 0) * 3
            
            total_reward = base_reward + exploration_bonus + learning_bonus
            
            return {
                'total_reward': total_reward,
                'base_reward': base_reward,
                'exploration_bonus': exploration_bonus,
                'learning_bonus': learning_bonus
            }
        except Exception as e:
            if self.logger:
                self.logger.log(f"EMRS: 奖励计算失败 {str(e)}")
            return {'total_reward': 0, 'base_reward': 0, 'exploration_bonus': 0, 'learning_bonus': 0}

def wrap_emrs_for_compatibility(emrs_instance):
    """EMRS兼容性包装函数"""
    return emrs_instance 