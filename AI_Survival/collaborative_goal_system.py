#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协同目标建立系统 (Collaborative Goal Establishment System)
与本能机制、DMHA机制、CDL机制协同工作的目标确定机制

解决问题：
1. 原有目标建立机制过于独立和简化
2. 没有与三层认知架构(本能/DMHA/CDL)形成有效协同
3. 硬编码阈值，忽略认知状态和注意力焦点
"""

import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


class CognitiveStage(Enum):
    """认知阶段枚举"""
    INSTINCT = "instinct"      # 本能阶段：生存优先，简单直接
    DMHA = "dmha"             # DMHA阶段：目标导向，注意力驱动 
    CDL = "cdl"               # CDL阶段：探索导向，好奇心驱动


@dataclass
class CollaborativeGoal:
    """协同目标数据结构"""
    goal_type: str
    description: str
    priority: float           # 目标优先级 (0-1)
    urgency: float           # 目标紧急度 (0-1)
    cognitive_stage: CognitiveStage  # 产生该目标的认知阶段
    context: Dict[str, Any]   # 目标上下文信息
    driver_mechanism: str     # 驱动机制 (instinct/attention/curiosity)
    execution_complexity: str # 执行复杂度 (simple/moderate/complex)


class CollaborativeGoalSystem:
    """协同目标建立系统"""
    
    def __init__(self, player, logger=None):
        self.player = player
        self.logger = logger
        
    def establish_goals(self, game) -> List[CollaborativeGoal]:
        """协同目标建立主入口"""
        # === 第一步：确定当前认知阶段 ===
        decision_stage = self._determine_cognitive_stage(game)
        current_stage = CognitiveStage(decision_stage['stage'])
        
        if self.logger:
            self.logger.log(f"{self.player.name} 🎯 认知阶段: {current_stage.value} ({decision_stage['reason']})")
        
        # === 第二步：基于认知阶段的协同目标生成 ===
        if current_stage == CognitiveStage.INSTINCT:
            goals = self._generate_instinct_goals(decision_stage['trigger_type'], game)
            if self.logger:
                self.logger.log(f"{self.player.name} ⚡ 本能目标: {len(goals)}个紧急生存目标")
                
        elif current_stage == CognitiveStage.DMHA:
            goals = self._generate_dmha_goals(game)
            if self.logger:
                self.logger.log(f"{self.player.name} 🎯 DMHA目标: {len(goals)}个注意力导向目标")
                
        elif current_stage == CognitiveStage.CDL:
            goals = self._generate_cdl_goals(game)
            if self.logger:
                self.logger.log(f"{self.player.name} 🧠 CDL目标: {len(goals)}个探索学习目标")
        
        # === 第三步：跨阶段目标协调 ===
        coordinated_goals = self._coordinate_cross_stage_goals(goals, current_stage, game)
        
        if self.logger:
            self.logger.log(f"{self.player.name} 🔄 目标协调: {len(goals)}个→{len(coordinated_goals)}个")
            for i, goal in enumerate(coordinated_goals[:3]):
                self.logger.log(f"  目标{i+1}: {goal.description} (优先级:{goal.priority:.2f})")
        
        return coordinated_goals
    
    def _determine_cognitive_stage(self, game) -> Dict[str, Any]:
        """确定当前认知阶段"""
        # 获取当前资源状态
        hp = self.player.health
        food = self.player.food  
        water = self.player.water
        
        # 检测威胁距离
        min_threat_distance = self._get_min_threat_distance(game)
        
        # 阶段一：本能决策阶段
        if (hp <= 20 or food <= 20 or water <= 20) or min_threat_distance <= 3:
            trigger_reasons = []
            trigger_type = None
            
            if hp <= 20:
                trigger_reasons.append(f"血量危险({hp})")
                trigger_type = "low_health"
            if food <= 20:
                trigger_reasons.append(f"食物不足({food})")
                trigger_type = "low_food" if not trigger_type else trigger_type
            if water <= 20:
                trigger_reasons.append(f"水分不足({water})")
                trigger_type = "low_water" if not trigger_type else trigger_type
            if min_threat_distance <= 3:
                trigger_reasons.append(f"威胁接近(距离{min_threat_distance})")
                trigger_type = "threat_nearby"
            
            return {
                'stage': 'instinct',
                'reason': '本能层触发条件满足',
                'trigger_reason': ', '.join(trigger_reasons),
                'trigger_type': trigger_type
            }
        
        # 阶段二：DMHA决策阶段
        elif (hp > 20 and hp <= 50) or (food > 20 and food <= 50) or (water > 20 and water <= 50):
            if min_threat_distance > 3:
                return {
                    'stage': 'dmha',
                    'reason': '资源中等，适合注意力导向决策',
                    'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}',
                    'trigger_type': 'moderate_resources'
                }
        
        # 阶段三：CDL决策阶段  
        if hp > 50 and food > 50 and water > 50 and min_threat_distance > 3:
            return {
                'stage': 'cdl',
                'reason': '资源充足，环境安全，适合探索学习',
                'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}',
                'trigger_type': 'abundant_resources'
            }
        
        # 默认使用DMHA阶段
        return {
            'stage': 'dmha',
            'reason': '默认目标导向决策',
            'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}',
            'trigger_type': 'default'
        }
    
    def _generate_instinct_goals(self, trigger_type: str, game) -> List[CollaborativeGoal]:
        """生成本能阶段目标 - 简单、直接、生存导向"""
        goals = []
        
        if trigger_type == "threat_nearby":
            goals.append(CollaborativeGoal(
                goal_type="THREAT_AVOIDANCE",
                description="本能威胁规避",
                priority=1.0,
                urgency=1.0,
                cognitive_stage=CognitiveStage.INSTINCT,
                context={
                    'trigger': trigger_type,
                    'response_type': 'immediate_flee',
                    'current_position': (self.player.x, self.player.y)
                },
                driver_mechanism='survival_instinct',
                execution_complexity='simple'
            ))
        
        elif trigger_type == "low_health":
            goals.append(CollaborativeGoal(
                goal_type="SURVIVAL", 
                description="本能健康恢复",
                priority=0.95,
                urgency=0.9,
                cognitive_stage=CognitiveStage.INSTINCT,
                context={
                    'trigger': trigger_type,
                    'current_health': self.player.health,
                    'response_type': 'find_safety_and_recover'
                },
                driver_mechanism='survival_instinct',
                execution_complexity='simple'
            ))
            
        elif trigger_type == "low_water":
            goals.append(CollaborativeGoal(
                goal_type="RESOURCE_ACQUISITION",
                description="本能水源获取",
                priority=0.9,
                urgency=0.95,
                cognitive_stage=CognitiveStage.INSTINCT,
                context={
                    'resource_type': 'water',
                    'current_amount': self.player.water,
                    'response_type': 'immediate_seek'
                },
                driver_mechanism='survival_instinct',
                execution_complexity='simple'
            ))
            
        elif trigger_type == "low_food":
            goals.append(CollaborativeGoal(
                goal_type="RESOURCE_ACQUISITION",
                description="本能食物获取",
                priority=0.85,
                urgency=0.9,
                cognitive_stage=CognitiveStage.INSTINCT,
                context={
                    'resource_type': 'food',
                    'current_amount': self.player.food,
                    'response_type': 'immediate_seek'
                },
                driver_mechanism='survival_instinct',
                execution_complexity='simple'
            ))
        
        return goals
    
    def _generate_dmha_goals(self, game) -> List[CollaborativeGoal]:
        """生成DMHA阶段目标 - 注意力驱动、权衡优化"""
        goals = []
        
        # 获取DMHA注意力输出
        if hasattr(self.player, 'dmha') and self.player.dmha:
            attention_context = self._build_attention_context(game)
            attention_output = self.player.dmha.process_attention(attention_context)
            dominant_focus = attention_output.get('dominant_focus', 'resource')
            attention_weights = attention_output.get('attention_weights', {})
        else:
            dominant_focus = 'resource'
            attention_weights = {'resource': 0.6, 'social': 0.2, 'exploration': 0.2}
        
        # 基于注意力焦点生成目标
        if dominant_focus == 'resource':
            if self.player.water < 60:  # DMHA阶段使用更高阈值
                goals.append(CollaborativeGoal(
                    goal_type="RESOURCE_ACQUISITION",
                    description="DMHA水资源优化",
                    priority=0.7 * attention_weights.get('resource', 0.6),
                    urgency=0.6,
                    cognitive_stage=CognitiveStage.DMHA,
                    context={
                        'focus': 'resource_optimization',
                        'resource_type': 'water',
                        'optimization_target': 'efficiency',
                        'attention_weight': attention_weights.get('resource', 0.6)
                    },
                    driver_mechanism='attention_focus',
                    execution_complexity='moderate'
                ))
            
            if self.player.food < 60:
                goals.append(CollaborativeGoal(
                    goal_type="RESOURCE_ACQUISITION",
                    description="DMHA食物资源优化",
                    priority=0.65 * attention_weights.get('resource', 0.6),
                    urgency=0.55,
                    cognitive_stage=CognitiveStage.DMHA,
                    context={
                        'focus': 'resource_optimization',
                        'resource_type': 'food',
                        'optimization_target': 'sustainable_gathering',
                        'attention_weight': attention_weights.get('resource', 0.6)
                    },
                    driver_mechanism='attention_focus',
                    execution_complexity='moderate'
                ))
        
        elif dominant_focus == 'social':
            nearby_players = [p for p in game.players if p != self.player and 
                            abs(p.x - self.player.x) + abs(p.y - self.player.y) <= 5]
            if nearby_players:
                goals.append(CollaborativeGoal(
                    goal_type="SOCIAL_INTERACTION",
                    description="DMHA社交互动优化",
                    priority=0.6 * attention_weights.get('social', 0.4),
                    urgency=0.4,
                    cognitive_stage=CognitiveStage.DMHA,
                    context={
                        'focus': 'social_optimization',
                        'nearby_players_count': len(nearby_players),
                        'interaction_type': 'cooperative_or_competitive',
                        'attention_weight': attention_weights.get('social', 0.4)
                    },
                    driver_mechanism='attention_focus',
                    execution_complexity='complex'
                ))
        
        elif dominant_focus == 'exploration':
            goals.append(CollaborativeGoal(
                goal_type="EXPLORATION",
                description="DMHA目标导向探索",
                priority=0.5 * attention_weights.get('exploration', 0.3),
                urgency=0.3,
                cognitive_stage=CognitiveStage.DMHA,
                context={
                    'focus': 'directed_exploration',
                    'exploration_purpose': 'resource_mapping_or_threat_assessment',
                    'attention_weight': attention_weights.get('exploration', 0.3)
                },
                driver_mechanism='attention_focus',
                execution_complexity='moderate'
            ))
        
        return goals
    
    def _generate_cdl_goals(self, game) -> List[CollaborativeGoal]:
        """生成CDL阶段目标 - 好奇心驱动、学习优化"""
        goals = []
        
        if hasattr(self.player, 'curiosity_driven_learning') and self.player.cdl_active:
            try:
                # 构建CDL上下文
                from curiosity_driven_learning import ContextState
                nearby_entities = self._collect_nearby_entities(game)
                
                context_state = ContextState(
                    symbolized_scene=nearby_entities,
                    agent_internal_state={
                        'position': (self.player.x, self.player.y),
                        'health': self.player.health,
                        'food': self.player.food,
                        'water': self.player.water,
                        'phase': 'exploration',
                        'developmental_stage': getattr(self.player, 'developmental_stage', 0.3)
                    },
                    environmental_factors={
                        'terrain': game.game_map.grid[self.player.y][self.player.x],
                        'day': game.current_day,
                        'visited_positions_count': len(getattr(self.player, 'visited_positions', set()))
                    },
                    social_context={
                        'nearby_players': [p.name for p in game.players if p != self.player and 
                                         abs(p.x - self.player.x) + abs(p.y - self.player.y) <= 3]
                    },
                    timestamp=game.current_day * 24.0
                )
                
                # CDL评估好奇心和新颖性
                cdl_response = self.player.curiosity_driven_learning.evaluate_novelty_and_curiosity(context_state)
                novelty_score = cdl_response.get('novelty_score', 0)
                curiosity_level = cdl_response.get('average_curiosity', 0)
                
                # 基于好奇心水平生成目标
                if cdl_response.get('should_explore', False) or novelty_score > 0.4:
                    suggested_action = cdl_response.get('suggested_action', 'explore')
                    
                    if suggested_action in ['explore', 'novelty_seeking']:
                        goals.append(CollaborativeGoal(
                            goal_type="EXPLORATION",
                            description="CDL新颖性探索",
                            priority=0.4,
                            urgency=0.3,
                            cognitive_stage=CognitiveStage.CDL,
                            context={
                                'driver': 'curiosity',
                                'novelty_score': novelty_score,
                                'exploration_type': 'novelty_seeking',
                                'suggested_action': suggested_action
                            },
                            driver_mechanism='curiosity_driven',
                            execution_complexity='complex'
                        ))
                    
                    elif suggested_action in ['collect_information', 'uncertainty_reduction']:
                        goals.append(CollaborativeGoal(
                            goal_type="LEARNING",
                            description="CDL信息收集学习",
                            priority=0.45,
                            urgency=0.35,
                            cognitive_stage=CognitiveStage.CDL,
                            context={
                                'driver': 'uncertainty_reduction',
                                'curiosity_level': curiosity_level,
                                'learning_type': 'environmental_knowledge',
                                'suggested_action': suggested_action
                            },
                            driver_mechanism='curiosity_driven',
                            execution_complexity='complex'
                        ))
                
                # 工具使用学习目标
                if curiosity_level > 0.6:
                    goals.append(CollaborativeGoal(
                        goal_type="LEARNING",
                        description="CDL工具使用学习",
                        priority=0.5,
                        urgency=0.4,
                        cognitive_stage=CognitiveStage.CDL,
                        context={
                            'driver': 'skill_development',
                            'learning_focus': 'tool_usage_optimization',
                            'curiosity_level': curiosity_level
                        },
                        driver_mechanism='curiosity_driven',
                        execution_complexity='complex'
                    ))
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.player.name} CDL目标生成失败: {str(e)}")
                
                # 兜底的基础探索目标
                goals.append(CollaborativeGoal(
                    goal_type="EXPLORATION",
                    description="CDL基础探索",
                    priority=0.4,
                    urgency=0.3,
                    cognitive_stage=CognitiveStage.CDL,
                    context={
                        'driver': 'default_curiosity',
                        'exploration_type': 'general_exploration'
                    },
                    driver_mechanism='curiosity_driven',
                    execution_complexity='moderate'
                ))
        
        return goals
    
    def _coordinate_cross_stage_goals(self, goals: List[CollaborativeGoal], 
                                    current_stage: CognitiveStage, game) -> List[CollaborativeGoal]:
        """跨阶段目标协调 - 确保目标一致性和优先级合理性"""
        if not goals:
            return goals
            
        coordinated_goals = goals.copy()
        
        # 阶段特异性调整
        if current_stage == CognitiveStage.INSTINCT:
            # 本能阶段：确保只有最紧急的目标被保留
            coordinated_goals = [g for g in coordinated_goals if g.urgency >= 0.8]
            # 限制目标数量，本能反应应该简单直接
            coordinated_goals = coordinated_goals[:1]
            
        elif current_stage == CognitiveStage.DMHA:
            # DMHA阶段：基于注意力权重重新排序
            coordinated_goals.sort(key=lambda g: g.priority * g.urgency, reverse=True)
            # 保留前3个最重要的目标
            coordinated_goals = coordinated_goals[:3]
            
        elif current_stage == CognitiveStage.CDL:
            # CDL阶段：确保探索和学习目标占主导
            learning_goals = [g for g in coordinated_goals if 
                            g.goal_type in ["EXPLORATION", "LEARNING"]]
            other_goals = [g for g in coordinated_goals if 
                         g.goal_type not in ["EXPLORATION", "LEARNING"]]
            
            # CDL阶段优先学习目标，但保留少量生存维护目标
            coordinated_goals = learning_goals + other_goals[:1]
        
        # 最终一致性检查
        if len(coordinated_goals) > 5:  # 避免目标过多导致决策混乱
            coordinated_goals = coordinated_goals[:5]
            
        return coordinated_goals
    
    def _get_min_threat_distance(self, game) -> float:
        """获取最近威胁的距离"""
        min_distance = float('inf')
        
        for animal in game.game_map.animals:
            if animal.alive and animal.type in ["Tiger", "BlackBear"]:
                distance = abs(animal.x - self.player.x) + abs(animal.y - self.player.y)
                min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 999
    
    def _build_attention_context(self, game) -> Dict[str, Any]:
        """构建DMHA注意力上下文"""
        nearby_entities = self._collect_nearby_entities(game)
        
        return {
            'environment': {
                'terrain': game.game_map.grid[self.player.y][self.player.x],
                'nearby_entities': nearby_entities,
                'threats_count': len([e for e in nearby_entities if e.get('is_threat', False)])
            },
            'internal_state': {
                'health': self.player.health,
                'food': self.player.food,
                'water': self.player.water,
                'position': (self.player.x, self.player.y)
            },
            'social': {
                'nearby_players': [p.name for p in game.players if p != self.player and 
                                 abs(p.x - self.player.x) + abs(p.y - self.player.y) <= 5]
            }
        }
    
    def _collect_nearby_entities(self, game) -> List[Dict[str, Any]]:
        """收集附近实体信息"""
        entities = []
        
        # 收集附近动物
        for animal in game.game_map.animals:
            if animal.alive:
                distance = abs(animal.x - self.player.x) + abs(animal.y - self.player.y)
                if distance <= 5:  # 5格范围内
                    entities.append({
                        'type': animal.type,
                        'distance': distance,
                        'position': (animal.x, animal.y),
                        'is_threat': animal.type in ["Tiger", "BlackBear"],
                        'is_prey': animal.type in ["Rabbit", "Boar"]
                    })
        
        # 收集附近植物
        for plant in game.game_map.plants:
            if plant.alive and not plant.collected:
                distance = abs(plant.x - self.player.x) + abs(plant.y - self.player.y)
                if distance <= 3:  # 3格范围内
                    entities.append({
                        'type': plant.type,
                        'distance': distance,
                        'position': (plant.x, plant.y),
                        'is_food': not plant.toxic,
                        'is_toxic': plant.toxic
                    })
        
        return entities 