#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Curiosity-Driven Learning (CDL) - 好奇心驱动学习模块
实现好奇心驱动的探索和学习机制
"""

import random
import time
from typing import Dict, List, Any, Optional

class ContextState:
    """上下文状态类"""
    def __init__(self, symbolized_scene, agent_internal_state, environmental_factors, social_context, timestamp):
        self.symbolized_scene = symbolized_scene
        self.agent_internal_state = agent_internal_state
        self.environmental_factors = environmental_factors
        self.social_context = social_context
        self.timestamp = timestamp

class CuriosityDrivenLearning:
    """好奇心驱动学习系统"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.known_contexts = []
        self.current_curiosity = 0.5
        self.evaluation_count = 0
        self.last_action_type = None
        self.action_history = []
        if logger: 
            logger.log("🧠 CDL系统初始化完成")
    
    def evaluate_novelty_and_curiosity(self, context_state):
        """评估新颖性和好奇心程度"""
        self.evaluation_count += 1
        
        # 计算基础新颖性分数
        novelty = 0.9 if len(self.known_contexts) < 10 else random.uniform(0.7, 0.95)
        
        # 获取智能体状态
        agent_state = context_state.agent_internal_state
        food = agent_state.get('food', 100)
        water = agent_state.get('water', 100)
        health = agent_state.get('health', 100)
        
        # 获取环境信息
        symbolized_scene = context_state.symbolized_scene or []
        has_nearby_plants = any(entity.get('type') in ['Strawberry', 'Mushroom'] for entity in symbolized_scene)
        
        # 智能决策逻辑
        suggested_action = self._determine_smart_action(novelty, food, water, health, has_nearby_plants)
        
        curiosity_score = novelty * 0.8
        should_explore = novelty > 0.8
        
        # 记录行动历史
        self.action_history.append(suggested_action)
        if len(self.action_history) > 20:
            self.action_history = self.action_history[-20:]
        
        result = {
            "novelty_score": novelty,
            "curiosity_score": curiosity_score,
            "average_curiosity": 0.5,
            "should_explore": should_explore,
            "suggested_action": suggested_action
        }
        
        if self.logger:
            self.logger.log(f"🔍 CDL评估#{self.evaluation_count}: 新颖性={novelty:.2f}, 建议={suggested_action} (食物={food}, 水={water}, 附近植物={has_nearby_plants})")
        
        return result
    
    def _determine_smart_action(self, novelty, food, water, health, has_nearby_plants):
        """智能决定建议行动"""
        
        # 1. 如果资源不足，优先信息收集（包括攻击动物获取食物）
        if food < 80 or water < 80:
            if random.random() < 0.7:  # 70%概率选择信息收集
                return "collect_information"
        
        # 2. 如果食物严重不足，强制建议攻击行为
        if food < 50:
            if random.random() < 0.8:  # 80%概率建议攻击
                return "collect_information"  # 通过信息收集执行攻击
        
        # 3. 如果附近有植物，有机会进行信息收集
        if has_nearby_plants and random.random() < 0.6:  # 60%概率
            return "collect_information"
        
        # 4. 避免连续相同行动，增加多样性
        recent_actions = self.action_history[-5:] if len(self.action_history) >= 5 else self.action_history
        if recent_actions and len(set(recent_actions)) == 1:  # 最近5次都是同一行动
            last_action = recent_actions[0]
            if last_action == "explore":
                return "collect_information"
            elif last_action == "collect_information":
                return "explore"
        
        # 5. 基于新颖性的默认决策
        if novelty > 0.9:
            return "novelty_seeking"
        elif novelty > 0.85:
            # 在探索和信息收集之间随机选择
            return random.choice(["explore", "collect_information"])
        elif novelty > 0.8:
            return "explore"
        else:
            return "collect_information"
    
    def update_context(self, context_state):
        """更新上下文历史"""
        context_str = str(context_state.agent_internal_state) + str(context_state.environmental_factors)
        self.known_contexts.append(context_str)
        if len(self.known_contexts) > 50:
            self.known_contexts = self.known_contexts[-50:]
        
        if self.logger and self.evaluation_count % 10 == 0:  # 减少日志频率
            self.logger.log(f"📝 CDL上下文更新: 已知上下文数量={len(self.known_contexts)}")
    
    def evaluate_context_novelty(self, context_state):
        """评估上下文新颖性"""
        return 0.9
    
    def generate_exploration_strategy(self, context_state, novelty_score):
        """生成探索策略"""
        return {"priority": "high", "action_type": "explore"} 