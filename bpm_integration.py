"""
BPM集成模块（BPM Integration Module）

将新开发的BPM核心模块集成到主游戏系统中：
1. EOCAR组合生成器（模块1）
2. 规律验证系统（模块2）
3. 与现有BPM系统的兼容性处理

作者：AI生存游戏项目组
版本：1.0.0
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 导入新开发的BPM核心模块
from eocar_combination_generator import EOCARCombinationGenerator, CandidateRule, CombinationType
from rule_validation_system import RuleValidationSystem, ValidationStrategy, ValidationResult

# 导入现有模块
from symbolic_core_v3 import EOCATR_Tuple
from blooming_and_pruning_model import BloomingAndPruningModel


class BPMIntegrationManager:
    """BPM集成管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        
        # 初始化新的BPM核心模块
        self.eocar_generator = EOCARCombinationGenerator(logger)
        self.validation_system = RuleValidationSystem(logger)
        
        # 规律存储
        self.active_rules: List[CandidateRule] = []
        self.rule_id_map: Dict[str, CandidateRule] = {}
        
        # 缓存和性能
        self.eocar_experience_cache: List[EOCATR_Tuple] = []
        self.cache_size_limit = 50
        
        # 统计信息
        self.integration_stats = {
            'total_rules_generated': 0,
            'total_validations_performed': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'rules_activated': 0,
            'last_generation_time': 0.0,
            'last_validation_time': 0.0
        }
        
        if self.logger:
            self.logger.log("BPM集成管理器已初始化")
    
    def process_eocar_experience(self, eocar_experience: EOCATR_Tuple) -> List[CandidateRule]:
        """
        处理新的EOCATR经验，生成候选规律
        
        Args:
            eocar_experience: EOCATR经验元组
            
        Returns:
            List[CandidateRule]: 新生成的候选规律列表
        """
        
        # 添加到缓存
        self.eocar_experience_cache.append(eocar_experience)
        
        # 控制缓存大小
        if len(self.eocar_experience_cache) > self.cache_size_limit:
            self.eocar_experience_cache = self.eocar_experience_cache[-self.cache_size_limit:]
        
        # 生成候选规律
        new_rules = self.eocar_generator.generate_candidate_rules([eocar_experience])
        
        # 过滤和去重
        filtered_rules = self._filter_new_rules(new_rules)
        
        # 添加到活跃规律列表
        for rule in filtered_rules:
            self.active_rules.append(rule)
            self.rule_id_map[rule.rule_id] = rule
        
        # 更新统计信息
        self.integration_stats['total_rules_generated'] += len(filtered_rules)
        self.integration_stats['last_generation_time'] = time.time()
        
        if self.logger and filtered_rules:
            self.logger.log(f"从EOCATR经验生成了{len(filtered_rules)}个新规律")
        
        return filtered_rules
    
    def validate_rule_opportunity(self, current_eocar: EOCATR_Tuple, 
                                 player_state: Optional[Dict[str, Any]] = None) -> Optional[Tuple[CandidateRule, ValidationStrategy]]:
        """
        检查当前情况下是否有规律验证机会
        
        Args:
            current_eocar: 当前EOCATR情况
            player_state: 玩家状态（健康值、食物、水等）
            
        Returns:
            Optional[Tuple[CandidateRule, ValidationStrategy]]: 验证建议或None
        """
        
        if not self.active_rules:
            return None
        
        # 获取验证建议
        suggestions = self.validation_system.get_validation_suggestions(
            current_eocar, self.active_rules, player_state
        )
        
        if suggestions:
            return suggestions[0]  # 返回最优建议
        
        return None
    
    def execute_rule_validation(self, rule: CandidateRule, context: EOCATR_Tuple, 
                               actual_result: Dict[str, Any], 
                               strategy: ValidationStrategy = ValidationStrategy.OPPORTUNISTIC):
        """
        执行规律验证
        
        Args:
            rule: 要验证的规律
            context: 验证上下文
            actual_result: 实际执行结果
            strategy: 验证策略
        """
        
        # 执行验证
        attempt = self.validation_system.validate_rule(rule, context, actual_result, strategy)
        
        # 更新统计信息
        self.integration_stats['total_validations_performed'] += 1
        self.integration_stats['last_validation_time'] = time.time()
        
        if attempt.validation_result == ValidationResult.SUCCESS:
            self.integration_stats['successful_validations'] += 1
        elif attempt.validation_result == ValidationResult.FAILURE:
            self.integration_stats['failed_validations'] += 1
        
        if self.logger:
            self.logger.log(f"规律验证完成: {rule.rule_id}, 结果: {attempt.validation_result.value}")
        
        return attempt
    
    def get_applicable_rules(self, current_context: EOCATR_Tuple, 
                           min_confidence: float = 0.3) -> List[CandidateRule]:
        """
        获取适用于当前上下文的规律
        
        Args:
            current_context: 当前EOCATR上下文
            min_confidence: 最小置信度阈值
            
        Returns:
            List[CandidateRule]: 适用的规律列表
        """
        
        applicable_rules = []
        
        for rule in self.active_rules:
            if rule.confidence >= min_confidence:
                # 计算上下文相关性
                relevance = self.validation_system.confidence_updater._calculate_context_relevance(
                    rule, current_context
                )
                
                if relevance > 0.5:  # 相关性阈值
                    applicable_rules.append(rule)
                    # 更新激活统计
                    rule.activation_count += 1
                    rule.last_activation = time.time()
        
        # 按置信度排序
        applicable_rules.sort(key=lambda r: r.confidence, reverse=True)
        
        self.integration_stats['rules_activated'] += len(applicable_rules)
        
        return applicable_rules
    
    def suggest_action_based_on_rules(self, current_context: EOCATR_Tuple, 
                                    available_actions: List[str]) -> Optional[str]:
        """
        基于规律建议行动
        
        Args:
            current_context: 当前EOCATR上下文
            available_actions: 可用行动列表
            
        Returns:
            Optional[str]: 建议的行动或None
        """
        
        applicable_rules = self.get_applicable_rules(current_context)
        
        if not applicable_rules:
            return None
        
        # 选择置信度最高的规律
        best_rule = applicable_rules[0]
        
        # 从规律条件中提取建议的行动
        for condition in best_rule.condition_elements:
            if "动作=" in condition:
                suggested_action = condition.split("=")[1]
                if suggested_action in available_actions:
                    if self.logger:
                        self.logger.log(f"基于规律{best_rule.rule_id}建议行动: {suggested_action}")
                    return suggested_action
        
        return None
    
    def batch_process_eocar_experiences(self, eocar_experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """
        批量处理EOCATR经验
        
        Args:
            eocar_experiences: EOCATR经验列表
            
        Returns:
            List[CandidateRule]: 生成的候选规律列表
        """
        
        if not eocar_experiences:
            return []
        
        # 批量生成规律
        new_rules = self.eocar_generator.generate_candidate_rules(eocar_experiences)
        
        # 过滤和去重
        filtered_rules = self._filter_new_rules(new_rules)
        
        # 添加到活跃规律列表
        for rule in filtered_rules:
            self.active_rules.append(rule)
            self.rule_id_map[rule.rule_id] = rule
        
        # 更新统计信息
        self.integration_stats['total_rules_generated'] += len(filtered_rules)
        self.integration_stats['last_generation_time'] = time.time()
        
        if self.logger:
            self.logger.log(f"批量处理{len(eocar_experiences)}个经验，生成{len(filtered_rules)}个规律")
        
        return filtered_rules
    
    def cleanup_old_rules(self, max_age_hours: float = 48.0, min_confidence: float = 0.1):
        """
        清理旧的和低质量的规律
        
        Args:
            max_age_hours: 最大年龄（小时）
            min_confidence: 最小置信度
        """
        
        current_time = time.time()
        original_count = len(self.active_rules)
        
        # 过滤规律
        self.active_rules = [
            rule for rule in self.active_rules
            if ((current_time - rule.generation_time) / 3600 < max_age_hours and 
                rule.confidence >= min_confidence)
        ]
        
        # 更新映射
        self.rule_id_map = {rule.rule_id: rule for rule in self.active_rules}
        
        removed_count = original_count - len(self.active_rules)
        
        if self.logger and removed_count > 0:
            self.logger.log(f"清理了{removed_count}个旧规律，剩余{len(self.active_rules)}个规律")
    
    def _filter_new_rules(self, new_rules: List[CandidateRule]) -> List[CandidateRule]:
        """过滤新规律，去除重复和低质量规律"""
        
        filtered_rules = []
        existing_conditions = set()
        
        # 收集现有规律的条件
        for rule in self.active_rules:
            condition_key = f"{rule.combination_type.value}:{rule.condition_text}"
            existing_conditions.add(condition_key)
        
        # 过滤新规律
        for rule in new_rules:
            condition_key = f"{rule.combination_type.value}:{rule.condition_text}"
            
            # 检查重复
            if condition_key not in existing_conditions:
                # 检查质量阈值
                if rule.calculate_quality_score() > 0.3:  # 质量阈值
                    filtered_rules.append(rule)
                    existing_conditions.add(condition_key)
        
        return filtered_rules
    
    def integrate_with_legacy_bpm(self, legacy_bmp: BloomingAndPruningModel):
        """
        与现有BPM系统集成
        
        Args:
            legacy_bmp: 现有的BPM模型
        """
        
        try:
            # 从现有BPM获取候选规律
            if hasattr(legacy_bmp, 'candidate_rules'):
                for legacy_rule in legacy_bmp.candidate_rules:
                    # 转换为新格式
                    converted_rule = self._convert_legacy_rule(legacy_rule)
                    if converted_rule:
                        self.active_rules.append(converted_rule)
                        self.rule_id_map[converted_rule.rule_id] = converted_rule
            
            if self.logger:
                self.logger.log("与现有BPM系统集成完成")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"BPM集成错误: {e}")
    
    def _convert_legacy_rule(self, legacy_rule) -> Optional[CandidateRule]:
        """将现有规律转换为新格式"""
        
        try:
            # 基本转换逻辑
            converted_rule = CandidateRule(
                rule_id=f"legacy_{getattr(legacy_rule, 'id', int(time.time()))}",
                combination_type=CombinationType.E_O_C_A_R,  # 默认全组合
                condition_elements=[str(legacy_rule)],
                condition_text=str(legacy_rule),
                expected_result={'success': True},  # 默认预期
                confidence=getattr(legacy_rule, 'confidence', 0.5),
                abstraction_level=1
            )
            
            return converted_rule
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"规律转换失败: {e}")
            return None
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        
        stats = self.integration_stats.copy()
        
        # 添加当前状态信息
        stats.update({
            'active_rules_count': len(self.active_rules),
            'cached_experiences_count': len(self.eocar_experience_cache),
            'average_rule_confidence': self._calculate_average_confidence(),
            'rule_type_distribution': self._get_rule_type_distribution(),
            'validation_success_rate': self._calculate_validation_success_rate()
        })
        
        return stats
    
    def _calculate_average_confidence(self) -> float:
        """计算平均规律置信度"""
        if not self.active_rules:
            return 0.0
        
        total_confidence = sum(rule.confidence for rule in self.active_rules)
        return total_confidence / len(self.active_rules)
    
    def _get_rule_type_distribution(self) -> Dict[str, int]:
        """获取规律类型分布"""
        distribution = defaultdict(int)
        
        for rule in self.active_rules:
            distribution[rule.combination_type.value] += 1
        
        return dict(distribution)
    
    def _calculate_validation_success_rate(self) -> float:
        """计算验证成功率"""
        total_validations = self.integration_stats['total_validations_performed']
        if total_validations == 0:
            return 0.0
        
        successful_validations = self.integration_stats['successful_validations']
        return successful_validations / total_validations
    
    def export_rules_for_analysis(self) -> List[Dict[str, Any]]:
        """导出规律用于分析"""
        
        exported_rules = []
        
        for rule in self.active_rules:
            rule_data = {
                'rule_id': rule.rule_id,
                'combination_type': rule.combination_type.value,
                'condition_text': rule.condition_text,
                'confidence': rule.confidence,
                'quality_score': rule.calculate_quality_score(),
                'validation_attempts': rule.validation_attempts,
                'validation_successes': rule.validation_successes,
                'success_rate': rule.get_success_rate(),
                'activation_count': rule.activation_count,
                'generation_time': rule.generation_time,
                'abstraction_level': rule.abstraction_level
            }
            exported_rules.append(rule_data)
        
        return exported_rules


# 全局BPM集成管理器实例
_bpm_integration_manager = None


def get_bpm_integration_manager(logger=None) -> BPMIntegrationManager:
    """获取全局BPM集成管理器实例"""
    global _bpm_integration_manager
    
    if _bpm_integration_manager is None:
        _bpm_integration_manager = BPMIntegrationManager(logger)
    
    return _bpm_integration_manager


def integrate_eocar_experience(eocar_experience: EOCATR_Tuple, logger=None) -> List[CandidateRule]:
    """便捷函数：集成EOCATR经验"""
    manager = get_bpm_integration_manager(logger)
    return manager.process_eocar_experience(eocar_experience)


def check_validation_opportunity(current_eocar: EOCATR_Tuple, 
                               player_state: Optional[Dict[str, Any]] = None,
                               logger=None) -> Optional[Tuple[CandidateRule, ValidationStrategy]]:
    """便捷函数：检查验证机会"""
    manager = get_bpm_integration_manager(logger)
    return manager.validate_rule_opportunity(current_eocar, player_state)


def execute_validation(rule: CandidateRule, context: EOCATR_Tuple, 
                      actual_result: Dict[str, Any], logger=None):
    """便捷函数：执行验证"""
    manager = get_bpm_integration_manager(logger)
    return manager.execute_rule_validation(rule, context, actual_result)


def get_rule_based_action_suggestion(current_context: EOCATR_Tuple, 
                                   available_actions: List[str],
                                   logger=None) -> Optional[str]:
    """便捷函数：基于规律获取行动建议"""
    manager = get_bpm_integration_manager(logger)
    return manager.suggest_action_based_on_rules(current_context, available_actions)


def get_bpm_integration_stats(logger=None) -> Dict[str, Any]:
    """便捷函数：获取BPM集成统计信息"""
    manager = get_bpm_integration_manager(logger)
    return manager.get_integration_statistics() 