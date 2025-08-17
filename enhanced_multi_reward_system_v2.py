#!/usr/bin/env python3
"""
EMRS v2.0 - Enhanced Multi-Reward System Version 2.0
Five-Dimensional Evaluation System with DMHA Integration
"""

import time
import random
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class FiveDimensionalScore:
    survival: float = 0.0
    resource: float = 0.0
    social: float = 0.0
    exploration: float = 0.0
    learning: float = 0.0
    total: float = 0.0
    
    def __post_init__(self):
        self.total = (self.survival + self.resource + self.social + 
                     self.exploration + self.learning) / 5.0

class EnhancedMultiRewardSystemV2:
    def __init__(self, logger=None, development_stage='child'):
        self.logger = logger
        self.name = "EMRS v2.0 Five-Dimensional Evaluation System"
        self.version = "2.0.0"
        self.development_stage = development_stage
        
        # Base weights aligned with DMHA attention weights
        self.base_weights = {
            'survival': 0.30,      # Corresponds to DMHA danger attention
            'resource': 0.25,      # Corresponds to DMHA resource attention
            'social': 0.15,        # Corresponds to DMHA social attention
            'exploration': 0.20,   # Corresponds to DMHA exploration attention
            'learning': 0.10       # Independent dimension
        }
        
        # Development stage modifiers
        self.stage_modifiers = {
            'infant': {'survival': 1.5, 'resource': 1.2, 'social': 0.8, 'exploration': 1.0, 'learning': 1.3},
            'child': {'survival': 1.3, 'resource': 1.0, 'social': 1.0, 'exploration': 1.2, 'learning': 1.2},
            'adolescent': {'survival': 1.1, 'resource': 0.9, 'social': 1.3, 'exploration': 1.1, 'learning': 1.0},
            'adult': {'survival': 1.0, 'resource': 1.0, 'social': 1.2, 'exploration': 0.9, 'learning': 0.8}
        }
        
        # Statistics
        self.evaluation_count = 0
        self.total_reward_sum = 0.0
        self.dimension_usage = {'survival': 0, 'resource': 0, 'social': 0, 'exploration': 0, 'learning': 0}
        
        if self.logger:
            self.logger.log(f"✅ {self.name} v{self.version} 初始化成功")
    
    def calculate_multi_dimensional_reward(self, action_result: Dict[str, Any], 
                                         context: Dict[str, Any] = None, 
                                         development_stage: str = None) -> Dict[str, Any]:
        """Main interface method - calculates five-dimensional rewards"""
        try:
            self.evaluation_count += 1
            
            if development_stage:
                self.development_stage = development_stage
            
            action = action_result.get('action', 'unknown')
            
            if context is None:
                context = {}
            
            # Extract context information from action_result
            context.update({
                'hp': action_result.get('health', action_result.get('hp', 100)),
                'food': action_result.get('food', 50),
                'water': action_result.get('water', 50),
                'position': action_result.get('position', (0, 0)),
                'survival_days': action_result.get('survival_days', 1)
            })
            
            # Get DMHA focus information
            dmha_focus = context.get('dmha_focus', action_result.get('dmha_focus'))
            
            # Perform five-dimensional evaluation
            five_dim_score = self.evaluate_decision(action, context, action_result, dmha_focus)
            
            # Calculate weighted score based on development stage
            weighted_score = self.get_weighted_score(five_dim_score)
            
            # Build detailed reward information
            detailed_rewards = {
                'survival': five_dim_score.survival,
                'resource': five_dim_score.resource,
                'social': five_dim_score.social,
                'exploration': five_dim_score.exploration,
                'learning': five_dim_score.learning
            }
            
            # Build reward breakdown
            reward_breakdown = {}
            for dim, value in detailed_rewards.items():
                percentage = (value / five_dim_score.total * 100) if five_dim_score.total > 0 else 0
                reward_breakdown[dim] = {
                    'value': value,
                    'percentage': percentage,
                    'weight': self.base_weights[dim]
                }
            
            # Update statistics
            self.total_reward_sum += weighted_score
            dominant_dim = max(detailed_rewards.items(), key=lambda x: x[1])[0]
            self.dimension_usage[dominant_dim] += 1
            
            # Build result (compatible with existing interface)
            result = {
                'total_reward': weighted_score,
                'base_reward': five_dim_score.total,
                'exploration_bonus': five_dim_score.exploration,
                'learning_bonus': five_dim_score.learning,
                'detailed_rewards': detailed_rewards,
                'reward_breakdown': reward_breakdown,
                'five_dimensional_score': five_dim_score,
                'development_stage': self.development_stage,
                'dmha_focus': dmha_focus,
                'system_version': self.version
            }
            
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ EMRS v2.0 评价失败: {str(e)}")
            # Return safe default values
            return {
                'total_reward': 0.1,  # Basic survival reward
                'base_reward': 0.1,
                'exploration_bonus': 0.0,
                'learning_bonus': 0.0,
                'detailed_rewards': {'survival': 0.1, 'resource': 0.0, 'social': 0.0, 'exploration': 0.0, 'learning': 0.0},
                'reward_breakdown': {},
                'error': str(e),
                'system_version': self.version
            }
    
    def evaluate_decision(self, action: str, context: Dict[str, Any], 
                         result: Dict[str, Any] = None, 
                         dmha_focus: str = None) -> FiveDimensionalScore:
        """Evaluate decision using five dimensions"""
        
        # 1. Survival evaluation (corresponds to DMHA danger attention)
        survival_score = self._evaluate_survival(action, context, result)
        
        # 2. Resource evaluation (corresponds to DMHA resource attention)
        resource_score = self._evaluate_resource(action, context, result)
        
        # 3. Social evaluation (corresponds to DMHA social attention)
        social_score = self._evaluate_social(action, context, result)
        
        # 4. Exploration evaluation (corresponds to DMHA exploration attention)
        exploration_score = self._evaluate_exploration(action, context, result)
        
        # 5. Learning evaluation (independent dimension)
        learning_score = self._evaluate_learning(action, context, result)
        
        # Create five-dimensional score object
        five_dim_score = FiveDimensionalScore(
            survival=survival_score,
            resource=resource_score,
            social=social_score,
            exploration=exploration_score,
            learning=learning_score
        )
        
        # Apply DMHA focus adjustment if present
        if dmha_focus:
            five_dim_score = self._apply_dmha_focus_adjustment(five_dim_score, dmha_focus)
        
        return five_dim_score
    
    def _evaluate_survival(self, action: str, context: Dict[str, Any], 
                          result: Dict[str, Any] = None) -> float:
        """Evaluate survival reward (0-1) - corresponds to DMHA danger attention"""
        score = 0.3  # Base score
        
        hp = context.get('hp', context.get('health', 100))
        threats = context.get('nearby_threats', [])
        
        # HP protection evaluation
        hp_ratio = hp / 100.0
        if action in ['rest', 'heal'] and hp_ratio < 0.7:
            score += 0.4  # Low HP rest/heal
        elif action in ['attack', 'fight'] and hp_ratio < 0.3:
            score -= 0.3  # Low HP combat risk
        
        # Threat response evaluation
        if threats:
            if action in ['escape', 'flee', 'move']:
                score += 0.4  # Escape from threats
            elif action in ['attack', 'fight'] and len(threats) > 1:
                score -= 0.2  # Multiple threat combat risk
        
        # Basic survival reward
        if hp > 0:
            score += 0.1  # Staying alive
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_resource(self, action: str, context: Dict[str, Any], 
                          result: Dict[str, Any] = None) -> float:
        """Evaluate resource reward (0-1) - corresponds to DMHA resource attention"""
        score = 0.3
        
        food = context.get('food', 50)
        water = context.get('water', 50)
        resources_nearby = context.get('resources_nearby', 0)
        
        # Resource acquisition evaluation
        if action in ['collect', 'gather', 'hunt', 'fish']:
            if resources_nearby > 0:
                score += 0.4  # Resources available for collection
            if food < 30 or water < 30:
                score += 0.3  # Urgent resource need
        
        # Resource consumption evaluation
        if action == 'eat' and food < 40:
            score += 0.3  # Eating when hungry
        elif action == 'drink' and water < 40:
            score += 0.3  # Drinking when thirsty
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_social(self, action: str, context: Dict[str, Any], 
                        result: Dict[str, Any] = None) -> float:
        """Evaluate social reward (0-1) - corresponds to DMHA social attention"""
        score = 0.2
        
        other_players = context.get('other_players', [])
        
        # Social interaction evaluation
        if action in ['share', 'help', 'cooperate', 'communicate']:
            if other_players:
                score += 0.4  # Social actions with others present
        
        # Cooperation evaluation
        if action in ['trade', 'exchange', 'alliance']:
            score += 0.3  # Cooperative behaviors
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_exploration(self, action: str, context: Dict[str, Any], 
                             result: Dict[str, Any] = None) -> float:
        """Evaluate exploration reward (0-1) - corresponds to DMHA exploration attention"""
        score = 0.3
        
        position = context.get('position', (0, 0))
        explored_areas = context.get('explored_areas', set())
        
        # Exploration behavior evaluation
        if action in ['explore', 'move', 'scout', 'investigate']:
            if position not in explored_areas:
                score += 0.4  # Exploring new areas
            else:
                score += 0.1  # Re-exploring known areas
        
        # Movement direction evaluation
        if action in ['move_up', 'move_down', 'move_left', 'move_right', 'up', 'down', 'left', 'right']:
            score += 0.2  # Movement has exploration value
        
        # Exploration timing evaluation
        hp = context.get('hp', 100)
        if action in ['explore', 'move'] and hp > 60:
            score += 0.2  # Safe exploration when healthy
        
        return max(0.0, min(1.0, score))
    
    def _evaluate_learning(self, action: str, context: Dict[str, Any], 
                          result: Dict[str, Any] = None) -> float:
        """Evaluate learning reward (0-1) - independent dimension"""
        score = 0.2
        
        # Skill practice evaluation
        if action in ['attack', 'collect', 'craft', 'build', 'hunt', 'fish']:
            score += 0.3  # Skill practice has learning value
        
        # Observation learning evaluation
        if action in ['observe', 'analyze', 'study', 'collect_information']:
            score += 0.2  # Observation learning
        
        # Experimentation evaluation
        if action in ['experiment', 'try_new_method', 'test']:
            score += 0.4  # Experimentation has high learning value
        
        return max(0.0, min(1.0, score))
    
    def _apply_dmha_focus_adjustment(self, score: FiveDimensionalScore, 
                                   dmha_focus: str) -> FiveDimensionalScore:
        """Apply DMHA focus adjustment to enhance corresponding dimension"""
        focus_mapping = {
            'danger': 'survival',
            'resource': 'resource', 
            'social': 'social',
            'exploration': 'exploration'
        }
        
        emphasized_dimension = focus_mapping.get(dmha_focus)
        
        if emphasized_dimension:
            adjustment_factor = 1.2  # 20% enhancement
            
            if emphasized_dimension == 'survival':
                score.survival *= adjustment_factor
            elif emphasized_dimension == 'resource':
                score.resource *= adjustment_factor
            elif emphasized_dimension == 'social':
                score.social *= adjustment_factor
            elif emphasized_dimension == 'exploration':
                score.exploration *= adjustment_factor
            
            # Recalculate total score
            score.total = (score.survival + score.resource + score.social + 
                          score.exploration + score.learning) / 5.0
        
        return score
    
    def get_weighted_score(self, score: FiveDimensionalScore) -> float:
        """Calculate development stage weighted total score"""
        stage_modifier = self.stage_modifiers.get(self.development_stage, 
                                                 self.stage_modifiers['child'])
        
        weighted_total = (
            score.survival * self.base_weights['survival'] * stage_modifier['survival'] +
            score.resource * self.base_weights['resource'] * stage_modifier['resource'] +
            score.social * self.base_weights['social'] * stage_modifier['social'] +
            score.exploration * self.base_weights['exploration'] * stage_modifier['exploration'] +
            score.learning * self.base_weights['learning'] * stage_modifier['learning']
        )
        
        return weighted_total
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        avg_reward = self.total_reward_sum / self.evaluation_count if self.evaluation_count > 0 else 0.0
        
        return {
            'system_name': self.name,
            'version': self.version,
            'development_stage': self.development_stage,
            'total_evaluations': self.evaluation_count,
            'average_reward': avg_reward,
            'dimension_usage': self.dimension_usage.copy(),
            'base_weights': self.base_weights.copy(),
            'stage_modifiers': self.stage_modifiers[self.development_stage].copy()
        }

def wrap_emrs_for_compatibility(emrs_instance):
    """Wrapper for EMRS compatibility"""
    return emrs_instance 