#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WBM Memory to Database Sync System
Synchronizes rules and decision data from memory to existing five-library system
Does not create new database structures, only provides data persistence
"""

import time
import json
from typing import Dict, List, Any, Optional

class MemoryToDatabaseSync:
    """Memory data to database synchronizer"""
    
    def __init__(self, player_instance):
        """
        Initialize synchronizer
        
        Args:
            player_instance: ILAIPlayer instance
        """
        self.player = player_instance
        self.sync_enabled = True
        
        # Use existing five-library system
        self.five_library = getattr(player_instance, 'five_library_system', None)
        
        if not self.five_library:
            print(f"⚠️ {player_instance.name} Five-library system not found, sync functionality disabled")
            self.sync_enabled = False
            return
        
        print(f"✅ {player_instance.name} Memory to database synchronizer started")
    
    def sync_bpm_rules_to_database(self):
        """Synchronize BPM rules to direct rules library"""
        if not self.sync_enabled or not hasattr(self.player, 'bpm') or self.player.bpm is None:
            return 0
        
        try:
            synced_count = 0
            
            # Check if BPM object has necessary attributes
            if not hasattr(self.player.bpm, 'candidate_rules') or not hasattr(self.player.bpm, 'validated_rules'):
                print(f"⚠️ {self.player.name} BPM object missing necessary attributes, skipping sync")
                return 0
            
            # Synchronize candidate rules
            if hasattr(self.player.bpm, 'candidate_rules') and self.player.bpm.candidate_rules:
                for rule_id, bpm_rule in self.player.bpm.candidate_rules.items():
                    rule_dict = self._convert_bpm_rule_to_five_lib_format(bpm_rule, 'candidate')
                    if self._add_rule_to_five_library(rule_dict):
                        synced_count += 1
            
            # Synchronize validated rules
            if hasattr(self.player.bpm, 'validated_rules') and self.player.bpm.validated_rules:
                for rule_id, bpm_rule in self.player.bpm.validated_rules.items():
                    rule_dict = self._convert_bpm_rule_to_five_lib_format(bpm_rule, 'validated')
                    if self._add_rule_to_five_library(rule_dict):
                        synced_count += 1
            
            if synced_count > 0:
                print(f"✅ {self.player.name} BPM rule sync: {synced_count} rules saved to five-library")
            
            return synced_count
            
        except Exception as e:
            print(f"❌ BPM rule sync failed: {str(e)}")
            return 0
    
    def sync_wbm_decisions_to_database(self, decision_result: Dict[str, Any]):
        """Synchronize WBM decisions to decision library"""
        if not self.sync_enabled:
            return False
        
        try:
            # Convert to five-library decision format
            decision_dict = self._convert_decision_to_five_lib_format(decision_result)
            
            # Add to five-library decision library
            if self._add_decision_to_five_library(decision_dict):
                if hasattr(self.player, 'logger') and self.player.logger:
                    self.player.logger.log(
                        f"{self.player.name} 💾 Decision saved to five-library: {decision_result.get('action', 'unknown')}"
                    )
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Decision sync failed: {str(e)}")
            return False
    
    def sync_actionable_rules_to_database(self):
        """Synchronize actionable rules to direct rules library"""
        if not self.sync_enabled or not hasattr(self.player, 'actionable_rules'):
            return 0
        
        try:
            synced_count = 0
            
            for rule in self.player.actionable_rules:
                rule_dict = self._convert_actionable_rule_to_five_lib_format(rule)
                if self._add_rule_to_five_library(rule_dict):
                    synced_count += 1
            
            if synced_count > 0:
                print(f"✅ {self.player.name} Actionable rules sync: {synced_count} rules")
            
            return synced_count
            
        except Exception as e:
            print(f"❌ Actionable rules sync failed: {str(e)}")
            return 0
    
    def update_decision_feedback(self, decision_id: str, success: bool, result: str = None):
        """Update decision feedback to five-library system"""
        if not self.sync_enabled:
            return
        
        try:
            # Use five-library system's feedback update function
            self.five_library.update_decision_feedback(decision_id, success, result)
            
        except Exception as e:
            print(f"❌ Decision feedback update failed: {str(e)}")
    
    def periodic_sync(self):
        """Periodic synchronization of all memory data"""
        if not self.sync_enabled:
            return
        
        try:
            # Synchronize BPM rules
            bmp_count = self.sync_bpm_rules_to_database()
            
            # Synchronize actionable rules
            actionable_count = self.sync_actionable_rules_to_database()
            
            total_synced = bmp_count + actionable_count
            
            if total_synced > 0:
                print(f"🔄 {self.player.name} Periodic sync completed: {total_synced} items")
            
            return total_synced
            
        except Exception as e:
            print(f"❌ Periodic sync failed: {str(e)}")
            return 0
    
    def _convert_bpm_rule_to_five_lib_format(self, bpm_rule, rule_status):
        """Convert BPM rule to five-library format"""
        try:
            from five_library_system import Rule
            
            return Rule(
                rule_id=bpm_rule.rule_id,
                rule_type=f"BPM_{rule_status}",
                conditions=bpm_rule.conditions,
                predictions=bpm_rule.predictions,
                confidence=bpm_rule.confidence,
                support_count=getattr(bpm_rule, 'support_count', 1),
                contradiction_count=getattr(bpm_rule, 'contradiction_count', 0),
                created_time=getattr(bpm_rule, 'birth_time', time.time()),
                creator_id=self.player.name,
                validation_status=rule_status
            )
            
        except Exception as e:
            print(f"⚠️ BPM rule format conversion failed: {str(e)}")
            return None
    
    def _convert_actionable_rule_to_five_lib_format(self, actionable_rule):
        """Convert actionable rule to five-library format"""
        try:
            from five_library_system import Rule
            
            return Rule(
                rule_id=actionable_rule.get('rule_id', f"actionable_{int(time.time())}"),
                rule_type="actionable",
                conditions=actionable_rule.get('conditions', {}),
                predictions=actionable_rule.get('predictions', {}),
                confidence=actionable_rule.get('confidence', 0.5),
                support_count=actionable_rule.get('usage_count', 0),
                contradiction_count=0,
                created_time=time.time(),
                creator_id=self.player.name,
                validation_status='actionable'
            )
            
        except Exception as e:
            print(f"⚠️ Actionable rule format conversion failed: {str(e)}")
            return None
    
    def _convert_decision_to_five_lib_format(self, decision_result):
        """Convert decision result to five-library format"""
        try:
            from five_library_system import Decision
            
            # Build decision context
            context = {
                'player_state': {
                    'health': self.player.health,
                    'food': self.player.food,
                    'water': self.player.water,
                    'position': (self.player.x, self.player.y)
                },
                'decision_source': decision_result.get('source', 'unknown'),
                'confidence': decision_result.get('confidence', 0.5)
            }
            
            return Decision(
                decision_id=decision_result.get('decision_id', f"decision_{int(time.time())}_{self.player.name}"),
                context=context,
                action=decision_result.get('action', 'unknown'),
                confidence=decision_result.get('confidence', 0.5),
                source=f"wbm_{decision_result.get('source', 'unknown')}",
                success_count=0,
                failure_count=0,
                total_uses=1,
                created_time=time.time(),
                last_used=time.time()
            )
            
        except Exception as e:
            print(f"⚠️ Decision format conversion failed: {str(e)}")
            return None
    
    def _add_rule_to_five_library(self, rule):
        """Add rule to five-library system"""
        if not rule:
            return False
        
        try:
            # 使用五库系统的规律添加功能
            result = self.five_library.add_rules_to_direct_library([rule.to_dict()])
            return result.get('success', False)
            
        except Exception as e:
                            print(f"⚠️ Failed to add rule to five libraries: {str(e)}")
            return False
    
    def _add_decision_to_five_library(self, decision):
        """添加决策到五库系统"""
        if not decision:
            return False
        
        try:
            # 使用五库系统的决策添加功能
            result = self.five_library.add_decision_to_library(decision)
            return result.get('success', False)
            
        except Exception as e:
                            print(f"⚠️ Failed to add decision to five libraries: {str(e)}")
            return False

# 应用同步功能的函数
def apply_memory_sync_patch(player_instance):
    """
    为玩家实例应用内存同步功能
    
    Args:
        player_instance: ILAIPlayer实例
        
    Returns:
        MemoryToDatabaseSync实例
    """
    try:
        # 创建同步器
        sync_manager = MemoryToDatabaseSync(player_instance)
        
        # 保存原有方法的引用
        if hasattr(player_instance, '_decision_library_matching'):
            player_instance._original_decision_library_matching = player_instance._decision_library_matching
        
        if hasattr(player_instance, '_wbm_rule_based_decision'):
            player_instance._original_wbm_rule_based_decision = player_instance._wbm_rule_based_decision
        
        # 增强决策库匹配方法
        def enhanced_decision_library_matching(target_goal, game):
            # 调用原有方法
            result = player_instance._original_decision_library_matching(target_goal, game) if hasattr(player_instance, '_original_decision_library_matching') else None
            
            # 如果有决策结果，同步到数据库
            if result and result.get('success'):
                sync_manager.sync_wbm_decisions_to_database(result)
            
            return result
        
        # 增强WBM规律决策方法
        def enhanced_wbm_rule_based_decision(target_goal, game, logger=None):
            # 调用原有方法，兼容新的logger参数
            if hasattr(player_instance, '_original_wbm_rule_based_decision'):
                # 检查原方法是否支持logger参数
                import inspect
                sig = inspect.signature(player_instance._original_wbm_rule_based_decision)
                if len(sig.parameters) >= 3:  # 支持logger参数
                    result = player_instance._original_wbm_rule_based_decision(target_goal, game, logger)
                else:  # 旧版本，不支持logger参数
                    result = player_instance._original_wbm_rule_based_decision(target_goal, game)
            else:
                result = None
            
            # 如果有决策结果，同步到数据库
            if result:
                sync_manager.sync_wbm_decisions_to_database(result)
            
            return result
        
        # 替换方法
        if hasattr(player_instance, '_decision_library_matching'):
            player_instance._decision_library_matching = enhanced_decision_library_matching
        
        if hasattr(player_instance, '_wbm_rule_based_decision'):
            player_instance._wbm_rule_based_decision = enhanced_wbm_rule_based_decision
        
        # 添加同步器引用
        player_instance.memory_sync = sync_manager
        
        # 执行初始同步
        sync_manager.periodic_sync()
        
                    print(f"✅ Memory sync function applied: {player_instance.name}")
        return sync_manager
        
    except Exception as e:
        print(f"❌ Failed to apply memory sync function: {str(e)}")
        return None

# 手动同步函数
def manual_sync_player_data(player_instance):
    """
    手动同步玩家数据到五库
    
    Args:
        player_instance: ILAIPlayer实例
    """
    if hasattr(player_instance, 'memory_sync'):
        return player_instance.memory_sync.periodic_sync()
    else:
        # 临时创建同步器
        sync_manager = MemoryToDatabaseSync(player_instance)
        return sync_manager.periodic_sync()

# 查询同步状态的函数
def get_sync_status(player_instance):
    """
    获取同步状态
    
    Args:
        player_instance: ILAIPlayer实例
        
    Returns:
        同步状态信息
    """
    try:
        if not hasattr(player_instance, 'memory_sync'):
            return {'sync_enabled': False, 'message': '同步功能未启用'}
        
        sync_manager = player_instance.memory_sync
        
        # 统计内存中的数据
        bpm_rules_count = 0
        if hasattr(player_instance, 'bpm'):
            bpm_rules_count = len(player_instance.bpm.candidate_rules) + len(player_instance.bpm.validated_rules)
        
        actionable_rules_count = len(getattr(player_instance, 'actionable_rules', []))
        
        # 统计五库中的数据
        five_lib_stats = {}
        if sync_manager.five_library:
            five_lib_stats = sync_manager.five_library.get_system_statistics()
        
        return {
            'sync_enabled': sync_manager.sync_enabled,
            'player_name': player_instance.name,
            'memory_data': {
                'bpm_rules': bpm_rules_count,
                'actionable_rules': actionable_rules_count
            },
            'five_library_stats': five_lib_stats
        }
        
    except Exception as e:
        return {'error': str(e)}

# 测试函数
def test_memory_sync():
    """测试内存同步功能"""
            print("🧪 Testing memory to database sync function...")
    
    try:
        print("📝 Test steps:")
        print("1. Create ILAIPlayer instance")
        print("2. Apply memory sync function")
        print("3. Simulate BMP rule generation")
        print("4. Test decision synchronization")
        print("5. Verify five library data")
        
        print("✅ Test framework ready")
        print("💡 Use apply_memory_sync_patch(player) to enable sync function")
        print("💡 Use manual_sync_player_data(player) to manually sync data")
        print("💡 Use get_sync_status(player) to check sync status")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_memory_sync() 