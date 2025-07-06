"""
规律验证系统（Rule Validation System）

实现BPM中的规律验证机制，包括：
1. 主动验证策略 - 识别和选择需要验证的规律
2. 置信度更新算法 - 基于验证结果动态调整置信度
3. 冒险验证机制 - 在安全范围内进行探索性验证
4. 验证结果处理 - 分类处理验证成功/失败/部分成功的情况

基于用户提出的"适当冒险验证"理念，如通过遭遇大黑熊得出的规律需要在遇到野猪时验证。

作者：AI生存游戏项目组
版本：1.0.0
"""

import time
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, deque
from eocar_combination_generator import CandidateRule, CombinationType
from scene_symbolization_mechanism import (
    EOCATR_Tuple, SymbolicEnvironment, SymbolicObjectCategory, 
    SymbolicAction, SymbolicCharacteristics, SymbolicResult, SymbolicTool
)


class ValidationStrategy(Enum):
    """验证策略枚举"""
    PASSIVE = "passive"              # 被动验证：等待自然情况验证
    ACTIVE_SAFE = "active_safe"      # 主动安全验证：在安全情况下验证
    ACTIVE_RISKY = "active_risky"    # 主动冒险验证：适度冒险验证
    OPPORTUNISTIC = "opportunistic"  # 机会验证：遇到相似情况时验证
    SYSTEMATIC = "systematic"        # 系统验证：有计划地验证关键规律


class ValidationResult(Enum):
    """验证结果枚举"""
    SUCCESS = "success"              # 验证成功：预期结果与实际结果一致
    FAILURE = "failure"              # 验证失败：预期结果与实际结果完全不符
    PARTIAL = "partial"              # 部分验证：结果部分符合预期
    INCONCLUSIVE = "inconclusive"    # 结果不明确：无法确定验证结果
    ERROR = "error"                  # 验证错误：验证过程中出现问题


class RiskLevel(Enum):
    """风险等级枚举"""
    SAFE = "safe"                    # 安全：预期无负面后果
    LOW = "low"                      # 低风险：可能有轻微负面后果
    MEDIUM = "medium"                # 中等风险：可能有中等负面后果
    HIGH = "high"                    # 高风险：可能有严重负面后果
    CRITICAL = "critical"            # 极高风险：可能危及生存


@dataclass
class ValidationAttempt:
    """验证尝试记录"""
    attempt_id: str                   # 尝试ID
    rule_id: str                      # 被验证规律ID
    timestamp: float                  # 验证时间
    strategy: ValidationStrategy      # 使用的验证策略
    risk_level: RiskLevel            # 风险等级
    
    # 验证上下文
    context_eocar: EOCATR_Tuple       # 验证时的EOCATR情况
    expected_result: Dict[str, Any]   # 预期结果
    actual_result: Dict[str, Any]     # 实际结果
    
    # 验证结果
    validation_result: ValidationResult  # 验证结果
    confidence_before: float         # 验证前置信度
    confidence_after: float          # 验证后置信度
    confidence_change: float         # 置信度变化
    
    # 验证质量
    reliability_score: float = 0.0   # 验证可靠性得分
    relevance_score: float = 0.0     # 验证相关性得分
    impact_score: float = 0.0        # 验证影响得分
    
    def calculate_validation_quality(self) -> float:
        """计算验证质量综合得分"""
        return (self.reliability_score * 0.4 + 
                self.relevance_score * 0.4 + 
                self.impact_score * 0.2)


@dataclass
class ValidationPlan:
    """验证计划"""
    plan_id: str                     # 计划ID
    target_rules: List[str]          # 目标规律ID列表
    strategy: ValidationStrategy     # 验证策略
    priority: float = 0.5            # 优先级 (0.0-1.0)
    
    # 计划参数
    max_risk_level: RiskLevel = RiskLevel.MEDIUM  # 最大可接受风险
    expected_attempts: int = 1       # 预期验证次数
    timeout_hours: float = 24.0      # 计划超时时间（小时）
    
    # 计划状态
    created_time: float = field(default_factory=time.time)
    status: str = "pending"          # pending/active/completed/cancelled
    progress: float = 0.0            # 进度 (0.0-1.0)
    
    def is_expired(self) -> bool:
        """检查计划是否已过期"""
        return (time.time() - self.created_time) / 3600 > self.timeout_hours


class ConfidenceUpdater:
    """置信度更新器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # 贝叶斯更新参数
        self.prior_alpha = self.config.get('prior_alpha', 1.0)  # 先验成功次数
        self.prior_beta = self.config.get('prior_beta', 1.0)    # 先验失败次数
        
        # 学习率参数
        self.base_learning_rate = self.config.get('base_learning_rate', 0.1)
        self.success_multiplier = self.config.get('success_multiplier', 1.2)
        self.failure_multiplier = self.config.get('failure_multiplier', 1.5)
        
        # 置信度边界
        self.min_confidence = self.config.get('min_confidence', 0.01)
        self.max_confidence = self.config.get('max_confidence', 0.99)
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            'prior_alpha': 1.0,
            'prior_beta': 1.0,
            'base_learning_rate': 0.1,
            'success_multiplier': 1.2,
            'failure_multiplier': 1.5,
            'min_confidence': 0.01,
            'max_confidence': 0.99,
            'decay_factor': 0.95,  # 时间衰减因子
            'relevance_weight': 0.3,  # 相关性权重
            'reliability_weight': 0.4,  # 可靠性权重
        }
    
    def update_confidence(self, rule: CandidateRule, attempt: ValidationAttempt) -> float:
        """基于验证尝试更新规律置信度"""
        
        # 计算基础更新量
        base_update = self._calculate_base_update(attempt)
        
        # 应用质量调整
        quality_factor = self._calculate_quality_factor(attempt)
        
        # 应用相关性调整
        relevance_factor = self._calculate_relevance_factor(rule, attempt)
        
        # 应用时间衰减
        time_factor = self._calculate_time_factor(rule, attempt)
        
        # 计算最终更新量
        final_update = base_update * quality_factor * relevance_factor * time_factor
        
        # 更新置信度
        new_confidence = rule.confidence + final_update
        
        # 应用边界约束
        new_confidence = max(self.min_confidence, min(self.max_confidence, new_confidence))
        
        return new_confidence
    
    def _calculate_base_update(self, attempt: ValidationAttempt) -> float:
        """计算基础置信度更新量"""
        if attempt.validation_result == ValidationResult.SUCCESS:
            return self.base_learning_rate * self.success_multiplier
        elif attempt.validation_result == ValidationResult.FAILURE:
            return -self.base_learning_rate * self.failure_multiplier
        elif attempt.validation_result == ValidationResult.PARTIAL:
            # 部分验证的更新量取决于部分成功的程度
            partial_success_rate = self._estimate_partial_success_rate(attempt)
            return self.base_learning_rate * (2 * partial_success_rate - 1)
        else:  # INCONCLUSIVE 或 ERROR
            return 0.0
    
    def _estimate_partial_success_rate(self, attempt: ValidationAttempt) -> float:
        """估计部分验证的成功率"""
        expected = attempt.expected_result
        actual = attempt.actual_result
        
        # 简单的相似度计算
        matches = 0
        total = 0
        
        for key in expected:
            if key in actual:
                total += 1
                if expected[key] == actual[key]:
                    matches += 1
                elif isinstance(expected[key], (int, float)) and isinstance(actual[key], (int, float)):
                    # 数值类型按相似度计算
                    diff = abs(expected[key] - actual[key])
                    max_val = max(abs(expected[key]), abs(actual[key]), 1)
                    similarity = 1 - min(diff / max_val, 1)
                    matches += similarity
        
        return matches / total if total > 0 else 0.5
    
    def _calculate_quality_factor(self, attempt: ValidationAttempt) -> float:
        """计算验证质量因子"""
        quality_score = attempt.calculate_validation_quality()
        # 将质量得分转换为乘数因子 (0.5 - 1.5)
        return 0.5 + quality_score
    
    def _calculate_relevance_factor(self, rule: CandidateRule, attempt: ValidationAttempt) -> float:
        """计算验证相关性因子"""
        # 检查验证上下文与规律条件的匹配程度
        relevance = self._calculate_context_relevance(rule, attempt.context_eocar)
        
        # 将相关性转换为乘数因子 (0.3 - 1.2)
        return 0.3 + 0.9 * relevance
    
    def _calculate_context_relevance(self, rule: CandidateRule, context: EOCATR_Tuple) -> float:
        """计算上下文相关性（修复版）"""
        try:
            relevance_scores = []
            
            # 🔧 修复：安全地处理条件元素，避免SymbolicElement哈希问题
            condition_elements = getattr(rule, 'condition_elements', [])
            
            if not condition_elements:
                return 0.5  # 默认相关性
            
            # 检查每个条件元素
            for condition in condition_elements:
                # 🔧 修复：安全地转换条件为字符串
                condition_str = ""
                if hasattr(condition, 'content'):
                    condition_str = str(condition.content)
                elif isinstance(condition, str):
                    condition_str = condition
                else:
                    condition_str = str(condition)
                
                if "环境=" in condition_str:
                    env_name = condition_str.split("=")[1]
                    if hasattr(context.environment, 'value'):
                        context_env = context.environment.value
                    else:
                        context_env = str(context.environment)
                    
                    if env_name == context_env:
                        relevance_scores.append(1.0)
                    else:
                        relevance_scores.append(0.3)
                        
                elif "对象=" in condition_str:
                    obj_name = condition_str.split("=")[1]
                    if hasattr(context.object_category, 'value'):
                        context_obj = context.object_category.value
                    else:
                        context_obj = str(context.object_category)
                        
                    if obj_name == context_obj:
                        relevance_scores.append(1.0)
                    else:
                        relevance_scores.append(0.3)
                        
                elif "动作=" in condition_str:
                    action_name = condition_str.split("=")[1]
                    if hasattr(context.action, 'value'):
                        context_action = context.action.value
                    else:
                        context_action = str(context.action)
                        
                    if action_name == context_action:
                        relevance_scores.append(1.0)
                    else:
                        relevance_scores.append(0.3)
                else:
                    # 属性类条件，给中等相关性
                    relevance_scores.append(0.6)
            
            return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5
            
        except Exception as e:
            # 如果出现任何错误，返回默认相关性
            if hasattr(self, 'logger') and self.logger:
                self.logger.log(f"计算上下文相关性失败: {str(e)}")
            return 0.5
    
    def _calculate_time_factor(self, rule: CandidateRule, attempt: ValidationAttempt) -> float:
        """计算时间衰减因子"""
        time_since_creation = attempt.timestamp - rule.generation_time
        hours_since_creation = time_since_creation / 3600
        
        # 时间衰减：规律越新，验证的影响越大
        decay = self.config['decay_factor'] ** (hours_since_creation / 24)  # 每24小时衰减
        
        return max(0.5, decay)  # 最小保持50%的影响


class RiskAssessor:
    """风险评估器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        
        # 风险评估规则
        self.risk_rules = {
            # 环境风险
            SymbolicEnvironment.DANGEROUS_ZONE: RiskLevel.HIGH,
            SymbolicEnvironment.FOREST: RiskLevel.MEDIUM,
            SymbolicEnvironment.OPEN_FIELD: RiskLevel.LOW,
            SymbolicEnvironment.SAFE_ZONE: RiskLevel.SAFE,
            SymbolicEnvironment.WATER_AREA: RiskLevel.LOW,
            
            # 对象风险
            SymbolicObjectCategory.DANGEROUS_ANIMAL: RiskLevel.HIGH,
            SymbolicObjectCategory.HARMLESS_ANIMAL: RiskLevel.LOW,
            SymbolicObjectCategory.POISONOUS_PLANT: RiskLevel.MEDIUM,
            SymbolicObjectCategory.EDIBLE_PLANT: RiskLevel.SAFE,
            SymbolicObjectCategory.WATER_SOURCE: RiskLevel.SAFE,
            
            # 动作风险
            SymbolicAction.ATTACK: RiskLevel.HIGH,
            SymbolicAction.AVOID: RiskLevel.SAFE,
            SymbolicAction.EXPLORE: RiskLevel.MEDIUM,
            SymbolicAction.EAT: RiskLevel.MEDIUM,
            SymbolicAction.GATHER: RiskLevel.LOW,
            SymbolicAction.DRINK: RiskLevel.SAFE,
        }
    
    def assess_validation_risk(self, rule: CandidateRule, context: EOCATR_Tuple, 
                              player_state: Optional[Dict[str, Any]] = None) -> RiskLevel:
        """评估验证特定规律的风险等级（修复版）"""
        
        risk_factors = []
        
        # 🔧 修复：安全地访问枚举值，避免SymbolicElement哈希问题
        try:
            # 环境风险
            env_key = context.environment if hasattr(context.environment, 'value') else None
            env_risk = self.risk_rules.get(env_key, RiskLevel.MEDIUM)
            risk_factors.append(env_risk.value)
            
            # 对象风险
            obj_key = context.object_category if hasattr(context.object_category, 'value') else None
            obj_risk = self.risk_rules.get(obj_key, RiskLevel.MEDIUM)
            risk_factors.append(obj_risk.value)
            
            # 动作风险
            action_key = context.action if hasattr(context.action, 'value') else None
            action_risk = self.risk_rules.get(action_key, RiskLevel.MEDIUM)
            risk_factors.append(action_risk.value)
        except Exception as e:
            # 如果出现哈希错误，使用默认风险等级
            if self.logger:
                self.logger.log(f"风险评估访问枚举失败: {str(e)}")
            risk_factors.extend([RiskLevel.MEDIUM.value] * 3)
        
        # 特征风险
        char_risk = self._assess_characteristics_risk(context.characteristics)
        risk_factors.append(char_risk.value)
        
        # 玩家状态风险
        if player_state:
            state_risk = self._assess_player_state_risk(player_state)
            risk_factors.append(state_risk.value)
        
        # 规律特定风险
        rule_risk = self._assess_rule_specific_risk(rule)
        risk_factors.append(rule_risk.value)
        
        # 计算综合风险等级
        risk_mapping = {"safe": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        reverse_mapping = {0: RiskLevel.SAFE, 1: RiskLevel.LOW, 2: RiskLevel.MEDIUM, 
                          3: RiskLevel.HIGH, 4: RiskLevel.CRITICAL}
        
        avg_risk = sum(risk_mapping[rf] for rf in risk_factors) / len(risk_factors)
        final_risk_level = reverse_mapping[round(avg_risk)]
        
        if self.logger:
            self.logger.log(f"验证风险评估: {rule.rule_id} -> {final_risk_level.value}")
        
        return final_risk_level
    
    def _assess_characteristics_risk(self, characteristics: SymbolicCharacteristics) -> RiskLevel:
        """评估特征相关风险"""
        if characteristics.dangerous:
            return RiskLevel.HIGH
        elif characteristics.poisonous:
            return RiskLevel.MEDIUM
        elif characteristics.distance and characteristics.distance < 1.0:
            return RiskLevel.MEDIUM  # 近距离接触风险
        else:
            return RiskLevel.LOW
    
    def _assess_player_state_risk(self, player_state: Dict[str, Any]) -> RiskLevel:
        """评估玩家状态相关风险"""
        health = player_state.get('health', 100)
        food = player_state.get('food', 100)
        water = player_state.get('water', 100)
        
        # 生命值低时风险高
        if health < 30:
            return RiskLevel.CRITICAL
        elif health < 50:
            return RiskLevel.HIGH
        elif health < 70:
            return RiskLevel.MEDIUM
        
        # 饥饿或口渴时风险增加
        if food < 20 or water < 20:
            return RiskLevel.HIGH
        elif food < 40 or water < 40:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _assess_rule_specific_risk(self, rule: CandidateRule) -> RiskLevel:
        """评估规律特定风险"""
        # 规律置信度低时风险高
        if rule.confidence < 0.3:
            return RiskLevel.HIGH
        elif rule.confidence < 0.5:
            return RiskLevel.MEDIUM
        
        # 预期负面结果的规律验证风险高
        expected_result = rule.expected_result
        if (expected_result.get('hp_change', 0) < 0 or 
            expected_result.get('success', True) == False):
            return RiskLevel.HIGH
        
        return RiskLevel.LOW


class ValidationPlanner:
    """验证计划器"""
    
    def __init__(self, confidence_updater: ConfidenceUpdater, 
                 risk_assessor: RiskAssessor, logger=None):
        self.confidence_updater = confidence_updater
        self.risk_assessor = risk_assessor
        self.logger = logger
        
        # 验证计划存储
        self.active_plans: Dict[str, ValidationPlan] = {}
        self.completed_plans: List[ValidationPlan] = []
        self.validation_history: List[ValidationAttempt] = []
        
        # 计划生成参数
        self.max_active_plans = 5
        self.plan_counter = 0
    
    def create_validation_plan(self, rules: List[CandidateRule], 
                              strategy: ValidationStrategy = ValidationStrategy.OPPORTUNISTIC,
                              max_risk: RiskLevel = RiskLevel.MEDIUM) -> Optional[ValidationPlan]:
        """创建验证计划"""
        
        if len(self.active_plans) >= self.max_active_plans:
            if self.logger:
                self.logger.log("验证计划已满，无法创建新计划")
            return None
        
        # 选择需要验证的规律
        target_rules = self._select_validation_targets(rules, max_risk)
        
        if not target_rules:
            return None
        
        self.plan_counter += 1
        plan = ValidationPlan(
            plan_id=f"plan_{self.plan_counter}_{strategy.value}",
            target_rules=[rule.rule_id for rule in target_rules],
            strategy=strategy,
            priority=self._calculate_plan_priority(target_rules),
            max_risk_level=max_risk
        )
        
        self.active_plans[plan.plan_id] = plan
        
        if self.logger:
            self.logger.log(f"创建验证计划: {plan.plan_id}, 目标规律数: {len(target_rules)}")
        
        return plan
    
    def _select_validation_targets(self, rules: List[CandidateRule], 
                                  max_risk: RiskLevel) -> List[CandidateRule]:
        """选择需要验证的规律"""
        candidates = []
        
        for rule in rules:
            # 优先选择中等置信度的规律（最需要验证）
            if 0.3 <= rule.confidence <= 0.7:
                candidates.append((rule, self._calculate_validation_priority(rule)))
        
        # 按优先级排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 选择前几个规律
        max_targets = 3
        selected = [rule for rule, _ in candidates[:max_targets]]
        
        return selected
    
    def _calculate_validation_priority(self, rule: CandidateRule) -> float:
        """计算规律验证优先级"""
        priority = 0.0
        
        # 置信度因子：中等置信度优先级最高
        conf_factor = 1 - abs(rule.confidence - 0.5) * 2
        priority += conf_factor * 0.4
        
        # 使用频率因子：激活次数多的规律优先级高
        usage_factor = min(rule.activation_count / 10, 1.0)
        priority += usage_factor * 0.3
        
        # 新鲜度因子：较新的规律优先级高
        age_hours = (time.time() - rule.generation_time) / 3600
        freshness_factor = max(0, 1 - age_hours / 48)  # 48小时内认为新鲜
        priority += freshness_factor * 0.2
        
        # 质量因子：高质量规律优先级高
        quality_factor = rule.calculate_quality_score()
        priority += quality_factor * 0.1
        
        return priority
    
    def _calculate_plan_priority(self, rules: List[CandidateRule]) -> float:
        """计算计划优先级"""
        if not rules:
            return 0.0
        
        avg_priority = sum(self._calculate_validation_priority(rule) for rule in rules) / len(rules)
        return avg_priority
    
    def suggest_validation_action(self, current_context: EOCATR_Tuple, 
                                 available_rules: List[CandidateRule],
                                 player_state: Optional[Dict[str, Any]] = None) -> Optional[Tuple[CandidateRule, ValidationStrategy]]:
        """建议当前情况下的验证行动"""
        
        # 寻找与当前上下文相关的规律
        relevant_rules = self._find_relevant_rules(current_context, available_rules)
        
        if not relevant_rules:
            return None
        
        # 评估每个规律的验证价值和风险
        best_rule = None
        best_strategy = None
        best_score = 0
        
        for rule in relevant_rules:
            # 评估风险
            risk_level = self.risk_assessor.assess_validation_risk(rule, current_context, player_state)
            
            # 计算验证价值
            validation_value = self._calculate_validation_value(rule, risk_level)
            
            if validation_value > best_score:
                best_score = validation_value
                best_rule = rule
                best_strategy = self._select_validation_strategy(rule, risk_level)
        
        if best_rule and best_score > 0.3:  # 阈值
            return (best_rule, best_strategy)
        
        return None
    
    def _find_relevant_rules(self, context: EOCATR_Tuple, 
                           rules: List[CandidateRule]) -> List[CandidateRule]:
        """找到与当前上下文相关的规律"""
        relevant = []
        
        for rule in rules:
            relevance = self.confidence_updater._calculate_context_relevance(rule, context)
            if relevance > 0.5:  # 相关性阈值
                relevant.append(rule)
        
        return relevant
    
    def _calculate_validation_value(self, rule: CandidateRule, risk_level: RiskLevel) -> float:
        """计算验证价值"""
        value = 0.0
        
        # 不确定性价值：置信度越不确定，验证价值越高
        uncertainty = 1 - abs(rule.confidence - 0.5) * 2
        value += uncertainty * 0.4
        
        # 重要性价值：质量得分高的规律验证价值高
        importance = rule.calculate_quality_score()
        value += importance * 0.3
        
        # 风险惩罚：风险越高，价值越低
        risk_penalty = {"safe": 0, "low": 0.1, "medium": 0.3, "high": 0.6, "critical": 0.9}
        value -= risk_penalty.get(risk_level.value, 0.5)
        
        # 验证历史：已验证次数多的规律价值降低
        validation_count = rule.validation_attempts
        history_penalty = min(validation_count / 5, 0.5)
        value -= history_penalty * 0.2
        
        return max(0, value)
    
    def _select_validation_strategy(self, rule: CandidateRule, risk_level: RiskLevel) -> ValidationStrategy:
        """选择验证策略"""
        if risk_level == RiskLevel.SAFE:
            return ValidationStrategy.ACTIVE_SAFE
        elif risk_level == RiskLevel.LOW:
            return ValidationStrategy.ACTIVE_SAFE
        elif risk_level == RiskLevel.MEDIUM:
            return ValidationStrategy.OPPORTUNISTIC
        elif risk_level == RiskLevel.HIGH:
            return ValidationStrategy.PASSIVE
        else:  # CRITICAL
            return ValidationStrategy.PASSIVE


class RuleValidationSystem:
    """规律验证系统主类"""
    
    def __init__(self, logger=None, config: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.config = config or {}
        
        # 组件初始化
        self.confidence_updater = ConfidenceUpdater(config)
        self.risk_assessor = RiskAssessor(logger)
        self.validation_planner = ValidationPlanner(
            self.confidence_updater, self.risk_assessor, logger
        )
        
        # 验证历史
        self.validation_attempts: List[ValidationAttempt] = []
        self.attempt_counter = 0
        
        # 统计信息
        self.stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'error_validations': 0,  # 🔧 新增：错误验证统计
            'risky_validations': 0,
            'avg_confidence_change': 0.0
        }
        
        if self.logger:
            self.logger.log("规律验证系统已初始化")
    
    def validate_rule(self, rule: CandidateRule, context: EOCATR_Tuple, 
                     actual_result: Dict[str, Any], 
                     strategy: ValidationStrategy = ValidationStrategy.OPPORTUNISTIC) -> ValidationAttempt:
        """验证规律（增强错误处理版）"""
        
        attempt_id = f"attempt_{int(time.time())}_{rule.rule_id}"
        
        try:
            # 🔧 增强：安全地评估风险，避免属性访问错误
            try:
                risk_level = self.risk_assessor.assess_validation_risk(rule, context)
            except Exception as risk_error:
                if self.logger:
                    self.logger.log(f"风险评估失败: {str(risk_error)}, 使用默认风险等级")
                risk_level = RiskLevel.MEDIUM  # 默认风险等级
            
            # 🔧 增强：安全地获取预期结果，处理不同的结果格式
            expected_result = {}
            try:
                if hasattr(rule, 'expected_result') and rule.expected_result:
                    if isinstance(rule.expected_result, dict):
                        expected_result = rule.expected_result.copy()
                    else:
                        # 如果expected_result不是字典，尝试转换
                        expected_result = {'success': True, 'hp_change': 0, 'reward': 0.1}
                        if self.logger:
                            self.logger.log(f"规律 {rule.rule_id} 的预期结果格式异常，使用默认值")
                else:
                    expected_result = {'success': True, 'hp_change': 0, 'reward': 0.1}
            except Exception as result_error:
                if self.logger:
                    self.logger.log(f"获取预期结果失败: {str(result_error)}, 使用默认值")
                expected_result = {'success': True, 'hp_change': 0, 'reward': 0.1}
            
            # 🔧 增强：安全地分析验证结果
            try:
                validation_result = self._analyze_validation_result(expected_result, actual_result)
            except Exception as analysis_error:
                if self.logger:
                    self.logger.log(f"验证结果分析失败: {str(analysis_error)}, 标记为错误")
                validation_result = ValidationResult.ERROR
            
            # 创建验证尝试记录
            attempt = ValidationAttempt(
                attempt_id=attempt_id,
                rule_id=rule.rule_id,
                timestamp=time.time(),
                strategy=strategy,
                risk_level=risk_level,
                context_eocar=context,
                expected_result=expected_result,
                actual_result=actual_result,
                validation_result=validation_result,
                confidence_before=rule.confidence,
                confidence_after=rule.confidence,  # 将在下面更新
                confidence_change=0.0  # 将在下面更新
            )
            
            # 🔧 增强：安全地更新置信度
            try:
                new_confidence = self.confidence_updater.update_confidence(rule, attempt)
                attempt.confidence_after = new_confidence
                attempt.confidence_change = new_confidence - rule.confidence
                rule.confidence = new_confidence
            except Exception as confidence_error:
                if self.logger:
                    self.logger.log(f"置信度更新失败: {str(confidence_error)}, 保持原置信度")
                attempt.confidence_after = rule.confidence
                attempt.confidence_change = 0.0
            
            # 🔧 增强：安全地计算验证质量分数
            try:
                attempt.reliability_score = self._calculate_reliability_score(attempt)
                attempt.relevance_score = self.confidence_updater._calculate_relevance_factor(rule, attempt)
                attempt.impact_score = self._calculate_impact_score(attempt)
            except Exception as score_error:
                if self.logger:
                    self.logger.log(f"质量分数计算失败: {str(score_error)}, 使用默认分数")
                attempt.reliability_score = 0.5
                attempt.relevance_score = 0.5
                attempt.impact_score = 0.5
            
            # 更新统计信息
            self._update_stats(attempt)
            
            if self.logger:
                self.logger.log(f"规律验证完成: {rule.rule_id} -> {validation_result.value} "
                              f"(置信度: {rule.confidence:.3f})")
            
            return attempt
            
        except Exception as e:
            # 🔧 增强：全局错误处理，确保系统不会崩溃
            if self.logger:
                self.logger.log(f"规律验证系统处理失败: {str(e)}")
            
            # 创建错误验证尝试记录
            error_attempt = ValidationAttempt(
                attempt_id=attempt_id,
                rule_id=rule.rule_id,
                timestamp=time.time(),
                strategy=strategy,
                risk_level=RiskLevel.CRITICAL,  # 错误情况标记为关键风险
                context_eocar=context,
                expected_result={'success': False, 'hp_change': 0, 'reward': 0},
                actual_result=actual_result,
                validation_result=ValidationResult.ERROR,
                confidence_before=rule.confidence,
                confidence_after=rule.confidence,
                confidence_change=0.0,
                reliability_score=0.0,
                relevance_score=0.0,
                impact_score=0.0
            )
            
            return error_attempt
    
    def _analyze_validation_result(self, expected: Dict[str, Any], 
                                  actual: Dict[str, Any]) -> ValidationResult:
        """分析验证结果"""
        if not expected or not actual:
            return ValidationResult.INCONCLUSIVE
        
        matches = 0
        total = 0
        
        for key in expected:
            if key in actual:
                total += 1
                if expected[key] == actual[key]:
                    matches += 1
                elif isinstance(expected[key], bool) and isinstance(actual[key], bool):
                    # 布尔值必须完全匹配
                    pass
                elif isinstance(expected[key], (int, float)) and isinstance(actual[key], (int, float)):
                    # 数值类型允许一定误差
                    error_rate = abs(expected[key] - actual[key]) / max(abs(expected[key]), 1)
                    if error_rate < 0.2:  # 20%误差内认为匹配
                        matches += 1
        
        if total == 0:
            return ValidationResult.INCONCLUSIVE
        
        match_rate = matches / total
        
        if match_rate >= 0.9:
            return ValidationResult.SUCCESS
        elif match_rate >= 0.6:
            return ValidationResult.PARTIAL
        elif match_rate >= 0.1:
            return ValidationResult.FAILURE
        else:
            return ValidationResult.FAILURE
    
    def _calculate_reliability_score(self, attempt: ValidationAttempt) -> float:
        """计算验证可靠性得分"""
        score = 0.5  # 基础得分
        
        # 风险等级影响可靠性
        risk_bonus = {"safe": 0.3, "low": 0.2, "medium": 0.0, "high": -0.2, "critical": -0.4}
        score += risk_bonus.get(attempt.risk_level.value, 0)
        
        # 上下文完整性
        context = attempt.context_eocar
        if context.confidence > 0.8:
            score += 0.2
        
        # 验证策略影响
        strategy_bonus = {
            ValidationStrategy.SYSTEMATIC: 0.3,
            ValidationStrategy.ACTIVE_SAFE: 0.2,
            ValidationStrategy.OPPORTUNISTIC: 0.1,
            ValidationStrategy.ACTIVE_RISKY: -0.1,
            ValidationStrategy.PASSIVE: 0.0
        }
        score += strategy_bonus.get(attempt.strategy, 0)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_impact_score(self, attempt: ValidationAttempt) -> float:
        """计算验证影响得分"""
        score = 0.0
        
        # 置信度变化幅度
        confidence_change = abs(attempt.confidence_change)
        score += min(confidence_change * 2, 0.5)
        
        # 验证结果的明确性
        if attempt.validation_result in [ValidationResult.SUCCESS, ValidationResult.FAILURE]:
            score += 0.3
        elif attempt.validation_result == ValidationResult.PARTIAL:
            score += 0.1
        
        # 风险承担的勇气奖励
        if (attempt.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH] and 
            attempt.validation_result == ValidationResult.SUCCESS):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _update_stats(self, attempt: ValidationAttempt):
        """更新统计信息（增强版）"""
        try:
            # 更新基础统计
            self.stats['total_validations'] += 1
            
            if attempt.validation_result == ValidationResult.SUCCESS:
                self.stats['successful_validations'] += 1
            elif attempt.validation_result == ValidationResult.FAILURE:
                self.stats['failed_validations'] += 1
            elif attempt.validation_result == ValidationResult.ERROR:
                self.stats['error_validations'] += 1
            
            # 🔧 新增：失败恢复机制统计
            if attempt.validation_result in [ValidationResult.FAILURE, ValidationResult.ERROR]:
                self._handle_validation_failure(attempt)
            
            # 记录验证历史
            self.validation_attempts.append(attempt)
            
            # 限制历史记录大小，避免内存泄漏
            if len(self.validation_attempts) > 1000:
                self.validation_attempts = self.validation_attempts[-500:]  # 保留最近500条
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"统计信息更新失败: {str(e)}")
    
    def _handle_validation_failure(self, attempt: ValidationAttempt):
        """处理验证失败的回退机制"""
        try:
            # 🔧 回退机制1：降低规律置信度
            if hasattr(self, '_failed_rules'):
                if attempt.rule_id not in self._failed_rules:
                    self._failed_rules[attempt.rule_id] = 0
                self._failed_rules[attempt.rule_id] += 1
            else:
                self._failed_rules = {attempt.rule_id: 1}
            
            # 🔧 回退机制2：标记高风险规律
            failure_count = self._failed_rules.get(attempt.rule_id, 0)
            if failure_count >= 3:  # 连续失败3次
                if hasattr(self, '_high_risk_rules'):
                    self._high_risk_rules.add(attempt.rule_id)
                else:
                    self._high_risk_rules = {attempt.rule_id}
                
                if self.logger:
                    self.logger.log(f"规律 {attempt.rule_id} 被标记为高风险（失败次数: {failure_count}）")
            
            # 🔧 回退机制3：调整验证策略
            if failure_count >= 2:
                if hasattr(self, '_strategy_adjustments'):
                    self._strategy_adjustments[attempt.rule_id] = ValidationStrategy.PASSIVE
                else:
                    self._strategy_adjustments = {attempt.rule_id: ValidationStrategy.PASSIVE}
                
                if self.logger:
                    self.logger.log(f"规律 {attempt.rule_id} 验证策略调整为被动验证")
                    
        except Exception as e:
            if self.logger:
                self.logger.log(f"验证失败处理出错: {str(e)}")
    
    def get_recommended_strategy(self, rule_id: str) -> ValidationStrategy:
        """获取推荐的验证策略（考虑历史失败）"""
        try:
            # 检查是否有策略调整
            if hasattr(self, '_strategy_adjustments') and rule_id in self._strategy_adjustments:
                return self._strategy_adjustments[rule_id]
            
            # 检查是否为高风险规律
            if hasattr(self, '_high_risk_rules') and rule_id in self._high_risk_rules:
                return ValidationStrategy.PASSIVE
            
            # 检查失败次数
            if hasattr(self, '_failed_rules'):
                failure_count = self._failed_rules.get(rule_id, 0)
                if failure_count >= 2:
                    return ValidationStrategy.OPPORTUNISTIC
                elif failure_count >= 1:
                    return ValidationStrategy.ACTIVE_SAFE
            
            # 默认策略
            return ValidationStrategy.OPPORTUNISTIC
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"获取推荐策略失败: {str(e)}")
            return ValidationStrategy.PASSIVE  # 出错时使用最安全的策略
    
    def reset_rule_status(self, rule_id: str):
        """重置规律状态（清除失败记录）"""
        try:
            if hasattr(self, '_failed_rules') and rule_id in self._failed_rules:
                del self._failed_rules[rule_id]
            
            if hasattr(self, '_high_risk_rules') and rule_id in self._high_risk_rules:
                self._high_risk_rules.remove(rule_id)
            
            if hasattr(self, '_strategy_adjustments') and rule_id in self._strategy_adjustments:
                del self._strategy_adjustments[rule_id]
            
            if self.logger:
                self.logger.log(f"规律 {rule_id} 状态已重置")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"重置规律状态失败: {str(e)}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            total = self.stats['total_validations']
            if total == 0:
                return {"status": "未开始", "health_score": 0.0}
            
            success_rate = self.stats['successful_validations'] / total
            error_rate = self.stats['error_validations'] / total
            
            # 计算健康分数
            health_score = success_rate * 0.7 + (1 - error_rate) * 0.3
            
            # 确定状态
            if health_score >= 0.8:
                status = "优秀"
            elif health_score >= 0.6:
                status = "良好"
            elif health_score >= 0.4:
                status = "一般"
            else:
                status = "需要关注"
            
            return {
                "status": status,
                "health_score": health_score,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "total_validations": total,
                "high_risk_rules": len(getattr(self, '_high_risk_rules', set())),
                "failed_rules": len(getattr(self, '_failed_rules', {}))
            }
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"获取系统健康状态失败: {str(e)}")
            return {"status": "错误", "health_score": 0.0, "error": str(e)}
    
    def get_validation_suggestions(self, current_context: EOCATR_Tuple,
                                  available_rules: List[CandidateRule],
                                  player_state: Optional[Dict[str, Any]] = None) -> List[Tuple[CandidateRule, ValidationStrategy]]:
        """获取验证建议"""
        suggestions = []
        
        # 获取主要建议
        main_suggestion = self.validation_planner.suggest_validation_action(
            current_context, available_rules, player_state
        )
        
        if main_suggestion:
            suggestions.append(main_suggestion)
        
        # 添加备选建议
        for rule in available_rules[:3]:  # 只考虑前3个规律
            if main_suggestion and rule.rule_id == main_suggestion[0].rule_id:
                continue
                
            relevance = self.confidence_updater._calculate_context_relevance(rule, current_context)
            if relevance > 0.3:
                risk_level = self.risk_assessor.assess_validation_risk(rule, current_context, player_state)
                strategy = self.validation_planner._select_validation_strategy(rule, risk_level)
                suggestions.append((rule, strategy))
        
        return suggestions[:3]  # 最多返回3个建议
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取验证系统统计信息"""
        stats = self.stats.copy()
        
        # 计算成功率
        if stats['total_validations'] > 0:
            stats['success_rate'] = stats['successful_validations'] / stats['total_validations']
            stats['failure_rate'] = stats['failed_validations'] / stats['total_validations']
            stats['risk_taking_rate'] = stats['risky_validations'] / stats['total_validations']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
            stats['risk_taking_rate'] = 0.0
        
        stats['active_plans'] = len(self.validation_planner.active_plans)
        stats['total_attempts'] = len(self.validation_attempts)
        
        return stats 