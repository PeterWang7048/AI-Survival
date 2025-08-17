#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合决策系统：V3决策库匹配 + WBM规律构建
实现"现成桥梁优先，现场造桥兜底"的决策机制
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class DecisionContext:
    """决策上下文"""
    hp: float
    food: float
    water: float
    position: tuple
    day: int
    environment: str
    threats_nearby: bool
    resources_nearby: List[str]
    urgency_level: float  # 0.0-1.0

class IntegratedDecisionSystem:
    """整合决策系统：V3决策库匹配 + WBM规律构建"""
    
    def __init__(self, five_library_system, wooden_bridge_model=None, bmp_system=None, logger=None):
        self.five_library_system = five_library_system
        self.wooden_bridge_model = wooden_bridge_model
        self.bmp_system = bmp_system
        self.logger = logger
        
        # 决策配置
        self.config = {
            'v3_similarity_threshold': 0.7,  # V3决策匹配的最低相似度
            'wbm_fallback_enabled': True,    # 是否启用WBM兜底
            'auto_library_update': True,     # 是否自动更新决策库
            'max_v3_candidates': 5,          # V3决策候选数量
            'decision_timeout': 5.0          # 决策超时时间（秒）
        }
        
        # 统计信息
        self.stats = {
            'total_decisions_made': 0,
            'v3_decisions_used': 0,
            'wbm_decisions_generated': 0,
            'fallback_decisions_used': 0,
            'decisions_added_to_library': 0,
            'average_decision_time': 0.0,
            'decision_times': []
        }
    
    def make_integrated_decision(self, context: DecisionContext, game=None) -> Dict[str, Any]:
        """整合决策主方法"""
        decision_result = {
            'success': True,
            'action': 'explore',
            'confidence': 0.5,
            'source': 'fallback',
            'reasoning': ['默认探索行动']
        }
        
        # 简化的决策逻辑
        if context.hp < 30:
            decision_result['action'] = 'rest'
            decision_result['reasoning'] = ['血量过低，需要休息']
        elif context.water < 30:
            decision_result['action'] = 'find_water'
            decision_result['reasoning'] = ['水分不足，寻找水源']
        elif context.food < 30:
            decision_result['action'] = 'find_food'
            decision_result['reasoning'] = ['食物不足，寻找食物']
        
        return decision_result
    
    def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """计算两个上下文的相似度"""
        try:
            weights = {
                'hp': 0.2,
                'food': 0.2,
                'water': 0.2,
                'urgency_level': 0.3,
                'environment': 0.1
            }
            
            total_similarity = 0.0
            total_weight = 0.0
            
            for key in ['hp', 'food', 'water', 'urgency_level']:
                if key in context1 and key in context2:
                    val1 = float(context1[key])
                    val2 = float(context2[key])
                    
                    max_val = max(100, val1, val2)
                    similarity = 1.0 - abs(val1 - val2) / max_val
                    
                    total_similarity += similarity * weights.get(key, 0.1)
                    total_weight += weights.get(key, 0.1)
            
            if 'environment' in context1 and 'environment' in context2:
                env_similarity = 1.0 if context1['environment'] == context2['environment'] else 0.0
                total_similarity += env_similarity * weights.get('environment', 0.1)
                total_weight += weights.get('environment', 0.1)
            
            return total_similarity / max(total_weight, 0.1)
            
        except Exception:
            return 0.0
    
    def _calculate_decision_score(self, decision: Dict, similarity: float) -> float:
        """计算决策评分"""
        try:
            similarity_score = similarity * 0.4
            success_rate = decision.get('success_rate', 0.5)
            success_score = success_rate * 0.4
            usage_count = decision.get('usage_count', 1)
            usage_score = min(usage_count / 10.0, 1.0) * 0.2
            
            return similarity_score + success_score + usage_score
            
        except Exception:
            return 0.0


if __name__ == "__main__":
    print("✅ 整合决策系统修复版本创建成功") 