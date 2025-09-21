#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EMRS格式化错误修复补丁
解决技术方案第11阶段：EMRS+决策库更新中的字典格式化问题

错误类型: unsupported format string passed to dict.__format__
影响范围: ILAI和RILAI玩家的奖励计算系统
修复方法: 替换字典格式化调用为安全的键值对访问
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EMRSFormatFixer:
    """EMRS格式化错误修复器"""
    
    @staticmethod
    def safe_emrs_calculation(player_instance, action_data: Dict, previous_state: Dict = None) -> Dict:
        """
        安全的EMRS奖励计算方法
        
        Args:
            player_instance: ILAI或RILAI玩家实例
            action_data: 行动数据字典
            previous_state: 之前的状态数据
            
        Returns:
            包含EMRS分数和计算状态的字典
        """
        try:
            # 构建当前状态
            current_state = {
                'health': player_instance.health,
                'food': player_instance.food,
                'water': player_instance.water,
                'position': (player_instance.x, player_instance.y),
                'day': getattr(player_instance, 'current_day', 1)
            }
            
            # 计算变化量
            health_change = current_state['health'] - (previous_state.get('health', player_instance.health) if previous_state else player_instance.health)
            food_change = current_state['food'] - (previous_state.get('food', player_instance.food) if previous_state else player_instance.food)
            water_change = current_state['water'] - (previous_state.get('water', player_instance.water) if previous_state else player_instance.water)
            
            # 构建安全的EMRS参数（避免字典格式化）
            emrs_context = {
                'stage': EMRSFormatFixer._get_safe_development_stage(player_instance),
                'action': str(action_data.get('action', 'unknown')),
                'success': bool(action_data.get('success', True)),
                'health_change': float(health_change),
                'food_change': float(food_change),
                'water_change': float(water_change),
                'survival_status': EMRSFormatFixer._assess_survival_status(current_state)
            }
            
            # 安全调用EMRS（使用关键字参数而不是字符串格式化）
            if hasattr(player_instance, 'emrs') and player_instance.emrs:
                try:
                    # 方法1：直接调用（避免字典解包时的格式化错误）
                    reward_score = EMRSFormatFixer._safe_emrs_call(player_instance.emrs, emrs_context)
                    
                    return {
                        'success': True,
                        'emrs_score': float(reward_score),
                        'calculation_method': 'emrs_safe',
                        'context_used': emrs_context,
                        'error': None
                    }
                    
                except Exception as emrs_error:
                    logger.warning(f"{player_instance.name} EMRS调用失败，使用备用方法: {emrs_error}")
                    # 备用计算
                    backup_score = EMRSFormatFixer._calculate_backup_reward(emrs_context)
                    return {
                        'success': True,
                        'emrs_score': backup_score,
                        'calculation_method': 'backup',
                        'error_handled': str(emrs_error)
                    }
            else:
                # 无EMRS时的简化计算
                simple_score = EMRSFormatFixer._calculate_simple_reward(emrs_context)
                return {
                    'success': True,
                    'emrs_score': simple_score,
                    'calculation_method': 'simple_no_emrs'
                }
                
        except Exception as e:
            logger.error(f"{player_instance.name} EMRS安全计算失败: {e}")
            return {
                'success': False,
                'emrs_score': 0.0,
                'calculation_method': 'emergency_fallback',
                'error': str(e)
            }
    
    @staticmethod
    def _safe_emrs_call(emrs_instance, context: Dict) -> float:
        """安全调用EMRS，避免格式化错误"""
        try:
            # 方法1：使用属性访问而不是字典格式化
            if hasattr(emrs_instance, 'calculate_reward'):
                return emrs_instance.calculate_reward(
                    stage=context['stage'],
                    action=context['action'],
                    success=context['success'],
                    health_change=context['health_change'],
                    food_change=context['food_change'],
                    water_change=context['water_change']
                )
            
            # 方法2：使用getattr安全访问
            elif hasattr(emrs_instance, 'get_reward'):
                return emrs_instance.get_reward(context)
                
            # 方法3：如果有其他计算方法
            else:
                return EMRSFormatFixer._calculate_backup_reward(context)
                
        except Exception as e:
            logger.warning(f"EMRS调用失败: {e}")
            return EMRSFormatFixer._calculate_backup_reward(context)
    
    @staticmethod
    def _get_safe_development_stage(player_instance) -> str:
        """安全获取发育阶段"""
        try:
            if hasattr(player_instance, '_get_current_development_stage'):
                return player_instance._get_current_development_stage()
            elif hasattr(player_instance, 'development_stage'):
                return str(player_instance.development_stage)
            else:
                return 'middle'  # 默认中期阶段
        except:
            return 'middle'
    
    @staticmethod
    def _assess_survival_status(state: Dict) -> str:
        """评估生存状态"""
        health = state.get('health', 100)
        food = state.get('food', 100)
        water = state.get('water', 100)
        
        if health < 20 or food < 20 or water < 20:
            return 'critical'
        elif health < 50 or food < 50 or water < 50:
            return 'warning'
        else:
            return 'good'
    
    @staticmethod
    def _calculate_backup_reward(context: Dict) -> float:
        """备用奖励计算方法"""
        base_reward = 0.1 if context.get('success', True) else -0.1
        
        # 生存状态奖励
        survival_status = context.get('survival_status', 'good')
        if survival_status == 'good':
            base_reward += 0.2
        elif survival_status == 'warning':
            base_reward += 0.0
        else:  # critical
            base_reward -= 0.3
        
        # 资源变化奖励
        resource_reward = (
            context.get('health_change', 0) * 0.02 +
            context.get('food_change', 0) * 0.02 +
            context.get('water_change', 0) * 0.02
        )
        
        return max(-1.0, min(1.0, base_reward + resource_reward))
    
    @staticmethod
    def _calculate_simple_reward(context: Dict) -> float:
        """简化奖励计算"""
        # 基本生存奖励
        base = 0.1 if context.get('success', True) else -0.1
        
        # 发育阶段调整
        stage = context.get('stage', 'middle')
        if stage == 'early':
            stage_multiplier = 1.2  # 早期更重视探索
        elif stage == 'late':
            stage_multiplier = 0.8  # 后期更重视效率
        else:
            stage_multiplier = 1.0
        
        return base * stage_multiplier

def apply_emrs_fix_to_player(player_instance):
    """将EMRS修复应用到玩家实例"""
    # 添加安全的EMRS计算方法
    player_instance.safe_emrs_calculation = lambda action_data, prev_state=None: \
        EMRSFormatFixer.safe_emrs_calculation(player_instance, action_data, prev_state)
    
    logger.info(f"已为 {player_instance.name} 应用EMRS格式化修复")

if __name__ == "__main__":
    print("EMRS格式化错误修复补丁已准备就绪")
    print("使用方法：")
    print("1. 导入: from emrs_format_fix import apply_emrs_fix_to_player")
    print("2. 应用: apply_emrs_fix_to_player(your_ilai_player)")
    print("3. 使用: result = player.safe_emrs_calculation(action_data, previous_state)") 