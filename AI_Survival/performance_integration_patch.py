#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能追踪集成补丁
将用户算力开销和反应时间统计系统集成到主游戏系统中
"""

import time
from typing import Dict, Any
from user_performance_tracker import (
    get_performance_tracker, 
    start_operation_tracking, 
    end_operation_tracking,
    record_decision_performance,
    track_performance
)

class PerformanceIntegrationPatch:
    """性能追踪集成补丁类"""
    
    def __init__(self):
        self.enabled = True
        self.operation_contexts = {}
        
    def patch_player_class(self, player_class):
        """为玩家类添加性能追踪功能"""
        
        # 保存原始方法
        original_init = player_class.__init__
        original_choose_action = getattr(player_class, 'choose_action', None)
        original_learn_from_experience = getattr(player_class, 'learn_from_experience', None)
        original_wbm_rule_based_decision = getattr(player_class, '_wbm_rule_based_decision', None)
        original_bmp_process = getattr(player_class, '_add_eocar_experience', None)
        
        def patched_init(self, *args, **kwargs):
            """增强的初始化方法"""
            original_init(self, *args, **kwargs)
            
            # 初始化性能追踪器
            user_id = getattr(self, 'name', 'unknown_player')
            self.performance_tracker = get_performance_tracker(user_id)
            
            # 性能统计
            self.performance_stats = {
                'total_decisions': 0,
                'total_learning_cycles': 0,
                'total_rule_generation': 0,
                'session_start': time.time()
            }
            
            print(f"🎯 {user_id} 性能追踪已启用")
        
        def patched_choose_action(self, game, logger=None):
            """增强的动作选择方法"""
            if not self.enabled:
                return original_choose_action(self, game, logger) if original_choose_action else None
            
            user_id = getattr(self, 'name', 'unknown_player')
            
            # 收集决策上下文
            context = {
                'health': getattr(self, 'health', 0),
                'food': getattr(self, 'food', 0),
                'water': getattr(self, 'water', 0),
                'position': (getattr(self, 'x', 0), getattr(self, 'y', 0)),
                'turn': getattr(game, 'current_turn', 0) if game else 0
            }
            
            # 评估决策复杂度
            complexity = self._assess_decision_complexity(game)
            
            # 开始追踪
            start_operation_tracking(user_id, "decision_making", complexity, context)
            
            try:
                # 执行原始决策逻辑
                result = original_choose_action(self, game, logger) if original_choose_action else "explore"
                
                # 记录决策结果
                result_data = {
                    'chosen_action': result,
                    'action_type': type(result).__name__
                }
                
                # 结束追踪
                end_operation_tracking(user_id, success=True, result_data=result_data)
                
                self.performance_stats['total_decisions'] += 1
                
                return result
                
            except Exception as e:
                # 记录失败
                end_operation_tracking(user_id, success=False, error=str(e))
                raise
        
        def patched_learn_from_experience(self, *args, **kwargs):
            """增强的学习方法"""
            if not self.enabled:
                return original_learn_from_experience(self, *args, **kwargs) if original_learn_from_experience else None
            
            user_id = getattr(self, 'name', 'unknown_player')
            
            # 开始学习追踪
            start_operation_tracking(user_id, "learning", complexity=3)
            
            try:
                result = original_learn_from_experience(self, *args, **kwargs) if original_learn_from_experience else None
                end_operation_tracking(user_id, success=True)
                self.performance_stats['total_learning_cycles'] += 1
                return result
            except Exception as e:
                end_operation_tracking(user_id, success=False, error=str(e))
                raise
        
        def patched_wbm_rule_based_decision(self, target_goal, game, logger=None):
            """增强的WBM规律决策方法"""
            if not self.enabled:
                return original_wbm_rule_based_decision(self, target_goal, game, logger) if original_wbm_rule_based_decision else None
            
            user_id = getattr(self, 'name', 'unknown_player')
            
            context = {
                'target_goal': str(target_goal),
                'wbm_rules_count': len(getattr(self, 'actionable_rules', [])),
                'reasoning_strategy': 'wbm_rule_based'
            }
            
            start_operation_tracking(user_id, "wbm_reasoning", complexity=4, context=context)
            
            try:
                result = original_wbm_rule_based_decision(self, target_goal, game, logger) if original_wbm_rule_based_decision else None
                
                result_data = {
                    'decision_result': result,
                    'rule_match_found': result is not None
                }
                
                end_operation_tracking(user_id, success=True, result_data=result_data)
                return result
            except Exception as e:
                end_operation_tracking(user_id, success=False, error=str(e))
                raise
        
        def patched_add_eocar_experience(self, *args, **kwargs):
            """增强的BMP经验处理方法"""
            if not self.enabled:
                return original_bmp_process(self, *args, **kwargs) if original_bmp_process else None
            
            user_id = getattr(self, 'name', 'unknown_player')
            
            start_operation_tracking(user_id, "bmp_processing", complexity=5)
            
            try:
                result = original_bmp_process(self, *args, **kwargs) if original_bmp_process else None
                end_operation_tracking(user_id, success=True)
                self.performance_stats['total_rule_generation'] += 1
                return result
            except Exception as e:
                end_operation_tracking(user_id, success=False, error=str(e))
                raise
        
        def _assess_decision_complexity(self, game):
            """评估决策复杂度"""
            complexity = 1
            
            # 基于环境复杂度
            if hasattr(game, 'grid'):
                nearby_entities = 0
                player_x = getattr(self, 'x', 0)
                player_y = getattr(self, 'y', 0)
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        x, y = player_x + dx, player_y + dy
                        if 0 <= x < len(game.grid) and 0 <= y < len(game.grid[0]):
                            cell = game.grid[x][y]
                            if hasattr(cell, 'content') and cell.content != '空地':
                                nearby_entities += 1
                
                complexity += min(nearby_entities, 3)
            
            # 基于AI组件复杂度
            if hasattr(self, 'bpm') and self.bpm:
                complexity += 2
            if hasattr(self, 'wooden_bridge_model'):
                complexity += 1
            if hasattr(self, 'dmha'):
                complexity += 1
                
            return min(complexity, 10)
        
        def get_performance_summary(self):
            """获取性能总结"""
            user_id = getattr(self, 'name', 'unknown_player')
            tracker = get_performance_tracker(user_id)
            return tracker.get_performance_summary()
        
        def generate_performance_report(self):
            """生成性能报告"""
            user_id = getattr(self, 'name', 'unknown_player')
            tracker = get_performance_tracker(user_id)
            return tracker.generate_performance_report()
        
        def export_performance_data(self, format='json'):
            """导出性能数据"""
            user_id = getattr(self, 'name', 'unknown_player')
            tracker = get_performance_tracker(user_id)
            return tracker.export_raw_data(format)
        
        # 应用补丁
        player_class.__init__ = patched_init
        if original_choose_action:
            player_class.choose_action = patched_choose_action
        if original_learn_from_experience:
            player_class.learn_from_experience = patched_learn_from_experience
        if original_wbm_rule_based_decision:
            player_class._wbm_rule_based_decision = patched_wbm_rule_based_decision
        if original_bmp_process:
            player_class._add_eocar_experience = patched_add_eocar_experience
        
        # 添加新方法
        player_class._assess_decision_complexity = _assess_decision_complexity
        player_class.get_performance_summary = get_performance_summary
        player_class.generate_performance_report = generate_performance_report
        player_class.export_performance_data = export_performance_data
        
        print(f"✅ 性能追踪补丁已应用到 {player_class.__name__}")
        
        return player_class

# 全局补丁实例
performance_patch = PerformanceIntegrationPatch()

def apply_performance_tracking_to_game(game_class):
    """为游戏类添加性能追踪功能"""
    
    original_run_simulation = getattr(game_class, 'run_simulation', None)
    original_run_single_turn = getattr(game_class, 'run_single_turn', None)
    
    def patched_run_simulation(self, *args, **kwargs):
        """增强的游戏运行方法"""
        print("🚀 开始游戏性能监控...")
        
        # 记录游戏开始时间
        game_start_time = time.time()
        
        try:
            result = original_run_simulation(self, *args, **kwargs) if original_run_simulation else None
            
            # 游戏结束后生成性能报告
            game_duration = time.time() - game_start_time
            print(f"\n🎮 游戏总时长: {game_duration:.2f} 秒")
            
            # 为所有玩家生成性能报告
            if hasattr(self, 'players'):
                print("\n📊 生成玩家性能报告...")
                for player in self.players:
                    if hasattr(player, 'generate_performance_report'):
                        report = player.generate_performance_report()
                        print(f"\n{player.name} 性能报告已生成")
            
            return result
            
        except Exception as e:
            print(f"⚠️ 游戏运行异常: {str(e)}")
            raise
    
    def patched_run_single_turn(self, *args, **kwargs):
        """增强的单回合运行方法"""
        turn_start_time = time.time()
        
        try:
            result = original_run_single_turn(self, *args, **kwargs) if original_run_single_turn else None
            
            turn_duration = time.time() - turn_start_time
            
            # 记录回合性能
            if hasattr(self, 'current_turn'):
                if turn_duration > 2.0:  # 如果回合时间超过2秒
                    print(f"⚠️ 回合 {self.current_turn} 耗时较长: {turn_duration:.2f}秒")
            
            return result
            
        except Exception as e:
            print(f"⚠️ 回合运行异常: {str(e)}")
            raise
    
    # 应用补丁
    if original_run_simulation:
        game_class.run_simulation = patched_run_simulation
    if original_run_single_turn:
        game_class.run_single_turn = patched_run_single_turn
    
    print(f"✅ 游戏性能追踪补丁已应用到 {game_class.__name__}")
    
    return game_class

def quick_performance_report(user_id: str = None):
    """快速生成性能报告"""
    if user_id:
        tracker = get_performance_tracker(user_id)
        return tracker.get_performance_summary()
    else:
        # 为所有用户生成报告
        from user_performance_tracker import _performance_trackers
        reports = {}
        for uid, tracker in _performance_trackers.items():
            reports[uid] = tracker.get_performance_summary()
        return reports

def enable_automatic_performance_monitoring():
    """启用自动性能监控"""
    performance_patch.enabled = True
    print("✅ 自动性能监控已启用")

def disable_automatic_performance_monitoring():
    """禁用自动性能监控"""
    performance_patch.enabled = False
    print("⚠️ 自动性能监控已禁用")

# 使用示例函数
def integrate_performance_tracking_to_main():
    """将性能追踪集成到main.py的示例函数"""
    
    print("📋 性能追踪集成指南:")
    print("1. 导入性能追踪模块:")
    print("   from performance_integration_patch import performance_patch")
    print("\n2. 在玩家类定义后应用补丁:")
    print("   performance_patch.patch_player_class(ILAIPlayer)")
    print("\n3. 在游戏类定义后应用补丁:")
    print("   apply_performance_tracking_to_game(Game)")
    print("\n4. 运行游戏时将自动收集性能数据")
    print("\n5. 使用以下命令查看性能报告:")
    print("   quick_performance_report('player_name')")
    
    return """
# 在main.py中添加以下代码:

# 导入性能追踪
from performance_integration_patch import (
    performance_patch, 
    apply_performance_tracking_to_game,
    quick_performance_report
)

# 在ILAIPlayer类定义后添加:
ILAIPlayer = performance_patch.patch_player_class(ILAIPlayer)

# 在Game类定义后添加:
Game = apply_performance_tracking_to_game(Game)

# 在游戏结束后生成总体报告:
def generate_final_performance_report():
    print("\\n" + "="*60)
    print("🎯 最终性能分析报告")
    print("="*60)
    
    all_reports = quick_performance_report()
    for user_id, summary in all_reports.items():
        if "error" not in summary:
            print(f"\\n👤 {user_id}:")
            print(f"   总操作数: {summary['total_operations']}")
            print(f"   平均响应时间: {summary['average_execution_time']:.3f}秒") 
            print(f"   效率评分: {summary['efficiency_score']:.1f}/10")
            print(f"   性能趋势: {summary['performance_trend']}")
"""

if __name__ == "__main__":
    print("🔧 性能追踪集成补丁测试")
    print(integrate_performance_tracking_to_main()) 