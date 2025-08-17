"""
怒放与剪枝模型（Blooming and Pruning Model, BPM）

模拟神经可塑性的知识动态演化机制，包括：
1. 候选规律生成（"怒放"阶段）
2. 经验驱动验证与剪枝机制  
3. 规律巩固和置信度管理
4. 规律质量评估系统

基于斯坦福4.0文档中的认知架构设计。

作者：AI生存游戏项目组
版本：1.0.0
"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, Counter
from scene_symbolization_mechanism import EOCATR_Tuple, SymbolicAction, SymbolicObjectCategory


class RuleType(Enum):
    """规律类型枚举"""
    CAUSAL = "causal"              # 因果规律 (A导致B)
    CONDITIONAL = "conditional"     # 条件规律 (如果A则B)
    SEQUENTIAL = "sequential"       # 时序规律 (A之后B)
    SPATIAL = "spatial"            # 空间规律 (在位置X做Y)
    ASSOCIATIVE = "associative"    # 关联规律 (A与B同时出现)
    EXCLUSION = "exclusion"        # 排除规律 (A排除B)
    OPTIMIZATION = "optimization"   # 优化规律 (在情况A下，B比C更好)
    TOOL_EFFECTIVENESS = "tool_effectiveness"  # 工具效用规律 (工具X对目标Y的效果Z)


class RuleConfidence(Enum):
    """规律置信度等级"""
    HYPOTHESIS = "hypothesis"      # 假设 (0.0-0.3)
    TENTATIVE = "tentative"       # 试探性 (0.3-0.6)  
    PROBABLE = "probable"         # 可能性 (0.6-0.8)
    CONFIDENT = "confident"       # 确信 (0.8-0.95)
    CERTAIN = "certain"           # 确定 (0.95-1.0)


@dataclass
class RuleEvidence:
    """规律证据数据类"""
    supporting_experiences: List[str] = field(default_factory=list)  # 支持经验
    contradicting_experiences: List[str] = field(default_factory=list)  # 反驳经验
    total_tests: int = 0           # 总测试次数
    successful_tests: int = 0      # 成功测试次数
    last_tested: float = 0.0       # 最后测试时间
    test_contexts: List[str] = field(default_factory=list)  # 测试上下文
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.total_tests == 0:
            return 0.0
        return self.successful_tests / self.total_tests
    
    @property
    def support_ratio(self) -> float:
        """计算支持比例"""
        total_evidence = len(self.supporting_experiences) + len(self.contradicting_experiences)
        if total_evidence == 0:
            return 0.0
        return len(self.supporting_experiences) / total_evidence
    
    @property
    def contradicting_evidence_ratio(self) -> float:
        """计算矛盾证据比例"""
        total_evidence = len(self.supporting_experiences) + len(self.contradicting_experiences)
        if total_evidence == 0:
            return 0.0
        return len(self.contradicting_experiences) / total_evidence


@dataclass 
class CandidateRule:
    """候选规律数据类"""
    # === 核心属性 (无默认值) ===
    rule_id: str
    rule_type: RuleType
    pattern: str
    conditions: Dict[str, Any]
    predictions: Dict[str, Any]

    # === 结构化与兼容性属性 (有默认值) ===
    pattern_elements: List[Any] = field(default_factory=list)
    condition_elements: List[str] = field(default_factory=list)
    expected_result: Dict[str, Any] = field(default_factory=dict)
    abstraction_level: int = 1
    generation_time: float = field(default_factory=time.time)
    validation_attempts: int = 0
    
    # === 演化属性 (有默认值) ===
    confidence: float = 0.1
    strength: float = 0.1
    generalization: float = 0.1
    specificity: float = 0.9
    
    # === 证据和验证 (有默认值) ===
    evidence: RuleEvidence = field(default_factory=RuleEvidence)
    birth_time: float = field(default_factory=time.time)
    last_activation: float = 0.0
    activation_count: int = 0
    
    # === 质量指标 (有默认值) ===
    precision: float = 0.0
    recall: float = 0.0
    utility: float = 0.0
    
    # === 元信息 (有默认值) ===
    parent_rules: List[str] = field(default_factory=list)
    derived_rules: List[str] = field(default_factory=list)
    complexity: int = 1
    # === 验证状态 ===
    status: str = "pending"  # pending | provisional | validated | deprecated | pruned
    
    def __post_init__(self):
        """初始化后处理，确保兼容性属性正确设置"""
        # 如果condition_elements为空，从conditions生成
        if not self.condition_elements and self.conditions:
            self._generate_condition_elements()
        
        # 如果pattern_elements为空，尝试从pattern字符串生成
        if not self.pattern_elements and self.pattern:
            self._generate_pattern_elements_from_pattern()
        
        # 如果expected_result为空，从predictions生成
        if not self.expected_result and self.predictions:
            self.expected_result = self.predictions.copy()
    
    def _generate_pattern_elements_from_pattern(self):
        """(修复版)从pattern字符串生成pattern_elements"""
        try:
            # 🔧 修复导入路径和构造函数
            from symbolic_learning_system import SymbolicElement, SymbolicCategory
            
            parts = []
            if '->' in self.pattern:
                parts = self.pattern.split('->')
            elif '+' in self.pattern:
                parts = self.pattern.split('+')
            else:
                parts = [self.pattern]

            self.pattern_elements = []
            for part in parts:
                if part.strip():
                    # 🔧 修复构造函数参数 - 使用正确的参数名和枚举值
                    element = SymbolicElement(
                        name=part.strip(), 
                        category=SymbolicCategory.ACTION  # 使用默认类别
                    )
                    self.pattern_elements.append(element)
                    
        except ImportError:
            # 如果无法导入，使用简单的字符串列表作为回退
            parts = []
            if '->' in self.pattern:
                parts = self.pattern.split('->')
            elif '+' in self.pattern:
                parts = self.pattern.split('+')
            else:
                parts = [self.pattern]
            self.pattern_elements = [part.strip() for part in parts if part.strip()]
        except Exception as e:
            # 🔧 添加错误处理，防止content属性错误
            if hasattr(self, 'logger') and self.logger:
                self.logger.log(f"生成pattern_elements失败: {str(e)}")
            # 使用字符串作为回退
            self.pattern_elements = [self.pattern] if self.pattern else []
    
    def _generate_condition_elements(self):
        """从conditions字典生成condition_elements列表"""
        elements = []
        for key, value in self.conditions.items():
            if isinstance(value, str):
                elements.append(f"{key}={value}")
            elif isinstance(value, (int, float)):
                elements.append(f"{key}={value}")
            elif isinstance(value, bool):
                elements.append(f"{key}={str(value).lower()}")
            else:
                elements.append(f"{key}={str(value)}")
        self.condition_elements = elements
    
    def get_confidence_level(self) -> RuleConfidence:
        """获取置信度等级"""
        if self.confidence < 0.3:
            return RuleConfidence.HYPOTHESIS
        elif self.confidence < 0.6:
            return RuleConfidence.TENTATIVE
        elif self.confidence < 0.8:
            return RuleConfidence.PROBABLE
        elif self.confidence < 0.95:
            return RuleConfidence.CONFIDENT
        else:
            return RuleConfidence.CERTAIN
    
    def calculate_quality_score(self) -> float:
        """计算规律质量综合得分"""
        # 基础得分基于置信度和证据支持率
        base_score = (self.confidence * 0.4 + self.evidence.support_ratio * 0.3)
        
        # 考虑激活频率和效用
        activation_bonus = min(self.activation_count / 10.0, 0.2)
        utility_bonus = self.utility * 0.1
        
        # 惩罚过度复杂的规律
        complexity_penalty = max(0, (self.complexity - 3) * 0.05)
        
        return base_score + activation_bonus + utility_bonus - complexity_penalty

    def to_wbm_format(self) -> dict:
        """转换为WBM造桥算法需要的格式"""
        try:
            # 从pattern或conditions中提取动作
            action = self._extract_action_from_rule()
            
            # 简化条件为WBM可理解的格式
            wbm_condition = self._simplify_conditions_for_wbm()
            
            # 转换预测结果为状态变化
            wbm_result = self._convert_predictions_to_state_changes()
            
            return {
                'id': self.rule_id,
                'condition': wbm_condition,
                'action': action,
                'result': wbm_result,
                'confidence': self.confidence,
                'source': 'bmp_generated',
                'original_pattern': self.pattern,
                'rule_type': self.rule_type.value if hasattr(self.rule_type, 'value') else str(self.rule_type)
            }
        except Exception as e:
            # 返回安全的默认格式
            return {
                'id': self.rule_id,
                'condition': {'position': 'any'},
                'action': 'explore',
                'result': {'exploration_progress': 0.1},
                'confidence': max(0.1, self.confidence),
                'source': 'bmp_fallback'
            }
    
    def _extract_action_from_rule(self) -> str:
        """从规律中提取可执行动作"""
        # 检查conditions中是否有action
        if isinstance(self.conditions, dict) and 'action' in self.conditions:
            return self.conditions['action']
        
        # 从pattern字符串中提取动作
        if hasattr(self, 'pattern') and self.pattern:
            import re
            # 匹配常见动作模式
            action_patterns = [
                r'(\w+)行动', r'执行(\w+)', r'进行(\w+)', 
                r'使用(\w+)', r'收集(\w+)', r'攻击(\w+)',
                r'移动', r'探索', r'寻找', r'收集', r'攻击', r'逃跑'
            ]
            
            for pattern in action_patterns:
                match = re.search(pattern, self.pattern)
                if match:
                    if match.groups():
                        return match.group(1)
                    else:
                        return match.group(0)
        
        # 根据规律类型推断动作
        if hasattr(self, 'rule_type'):
            type_to_action = {
                'CAUSAL': 'explore',
                'CONDITIONAL': 'conditional_action',
                'SEQUENTIAL': 'sequential_action',
                'SPATIAL': 'move',
                'TOOL_EFFECTIVENESS': 'use_tool'
            }
            rule_type_str = self.rule_type.value if hasattr(self.rule_type, 'value') else str(self.rule_type)
            return type_to_action.get(rule_type_str, 'explore')
        
        return 'explore'  # 默认动作
    
    def _simplify_conditions_for_wbm(self) -> dict:
        """简化条件为WBM可理解的格式"""
        simplified = {}
        
        if isinstance(self.conditions, dict):
            for key, value in self.conditions.items():
                if key in ['environment', 'current_cell', 'position']:
                    simplified[key] = value
                elif key in ['health', 'food', 'water']:
                    # 转换为阈值条件
                    if isinstance(value, (int, float)):
                        if value < 50:
                            simplified[f'{key}_low'] = True
                        elif value > 80:
                            simplified[f'{key}_high'] = True
                elif key in ['nearby_plant', 'nearby_animal', 'nearby_water']:
                    simplified[key] = bool(value)
        
        # 如果没有有效条件，设置默认条件
        if not simplified:
            simplified = {'position': 'any'}
        
        return simplified
    
    def _convert_predictions_to_state_changes(self) -> dict:
        """转换预测结果为状态变化"""
        result = {}
        
        if isinstance(self.predictions, dict):
            for key, value in self.predictions.items():
                if key == 'result':
                    # 解析结果字符串
                    if isinstance(value, str):
                        if 'water' in value.lower():
                            result['water_gain'] = 30
                        elif 'food' in value.lower():
                            result['food_gain'] = 20
                        elif 'discovery' in value.lower():
                            result['new_area_discovered'] = True
                        elif 'damage' in value.lower():
                            result['damage_dealt'] = 25
                elif key in ['water_gain', 'food_gain', 'health_change']:
                    result[key] = value
                elif key in ['success_probability', 'effectiveness']:
                    # 转换为具体收益
                    if isinstance(value, (int, float)) and value > 0.5:
                        result['success_bonus'] = True
        
        # 如果没有有效结果，设置默认结果
        if not result:
            result = {'exploration_progress': 0.1}
        
        return result


class BloomingAndPruningModel:
    """怒放与剪枝模型主类"""
    
    def __init__(self, logger=None, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs) if hasattr(super(), '__init__') else None
        
        # 性能优化: 添加生成频率控制
        self.last_generation_time = 0
        self.generation_interval = 15  # 15秒间隔
        self.min_experience_count = 5  # 最少经验数量
        self.logger = logger
        self.config = config or self._default_config()
        
        # 规律存储
        self.candidate_rules: Dict[str, CandidateRule] = {}  # 候选规律
        self.validated_rules: Dict[str, CandidateRule] = {}  # 已验证规律
        self.pruned_rules: Dict[str, CandidateRule] = {}     # 已剪枝规律
        
        # === 新增：规律去重和质量控制 ===
        self.rule_fingerprints: Set[str] = set()  # 规律指纹集合，用于快速去重
        self.rule_similarity_threshold = 0.95  # 相似度阈值（降低误判）
        self.min_quality_threshold = 0.01  # 最低质量阈值（极度降低）
        self.rule_merge_history: List[Tuple[str, str, float]] = []  # 合并历史
        
        # === 新增：智能内存管理 ===
        self.max_total_rules = config.get('max_total_rules', 1000) if config else 1000  # 最大规律总数
        self.max_candidate_rules = config.get('max_candidate_rules', 500) if config else 500  # 最大候选规律数
        self.max_validated_rules = config.get('max_validated_rules', 300) if config else 300  # 最大已验证规律数
        self.memory_cleanup_threshold = 0.9  # 内存清理阈值（90%满时清理）
        self.lru_access_times: Dict[str, float] = {}  # LRU访问时间记录
        self.memory_pressure_level = 0.0  # 内存压力级别 (0.0-1.0)
        
        # 生成统计
        self.rule_generation_history: List[Tuple[float, int]] = []  # (时间, 生成数量)
        self.pruning_history: List[Tuple[float, str, str]] = []     # (时间, 规律ID, 原因)
        
        # 生成参数
        self.min_support = config.get('min_support', 1) if config else 1  # 最小支持度（降低到1）
        
        # 模式库
        self.pattern_templates: Dict[RuleType, List[str]] = self._initialize_pattern_templates()
        
        # 性能指标
        self.total_rules_generated = 0
        self.total_rules_pruned = 0
        self.total_rules_validated = 0
        self.total_rules_merged = 0  # 新增：合并统计
        self.total_rules_rejected = 0  # 新增：拒绝统计
        
        if self.logger:
            self.logger.log("怒放与剪枝模型已初始化")
    
    def _format_rule_to_standard_pattern(self, rule: CandidateRule) -> str:
        """基于规律的实际EOCATR内容生成具体的经验格式"""
        try:
            # 获取规律的实际经验内容
            condition_elements = getattr(rule, 'condition_elements', [])
            condition_text = getattr(rule, 'condition_text', '')
            pattern = getattr(rule, 'pattern', '')
            
            # 提取规律中的实际EOCATR内容
            actual_content = self._extract_rule_content(rule, condition_elements, condition_text, pattern)
            
            # 根据实际内容生成具体的经验格式
            return self._generate_content_based_pattern(actual_content)
                
        except Exception as e:
            return f"内容格式化失败: {str(e)}"
    
    def _extract_rule_content(self, rule, condition_elements, condition_text, pattern):
        """提取规律中的实际EOCATR内容"""
        content = {
            'environment': None,
            'object': None, 
            'characteristics': [],
            'action': None,
            'tool': None,
            'result': None
        }
        
        # 🔥 优先从规律的conditions字典中提取内容
        if hasattr(rule, 'conditions') and rule.conditions:
            for key, value in rule.conditions.items():
                if 'environment' in key.lower():
                    content['environment'] = value
                elif 'object' in key.lower():
                    content['object'] = value
                elif 'action' in key.lower():
                    content['action'] = value
                elif 'tool' in key.lower():
                    content['tool'] = value
                elif 'characteristic' in key.lower():
                    if isinstance(value, list):
                        content['characteristics'].extend(value)
                    else:
                        content['characteristics'].append(value)
        
        # 🔥 从predictions字典中提取结果信息
        if hasattr(rule, 'predictions') and rule.predictions:
            for key, value in rule.predictions.items():
                if 'result' in key.lower() or 'success' in key.lower():
                    if isinstance(value, bool):
                        content['result'] = 'success' if value else 'failure'
                    else:
                        content['result'] = str(value)
                    break
        
        # 从规律的条件文本和模式中提取实际内容
        all_text = f"{condition_text} {pattern}"
        
        # 尝试从条件元素中提取内容（如果还没有的话）
        if not any([content['environment'], content['object'], content['action']]):
            for element in condition_elements:
                if hasattr(element, 'content') or hasattr(element, 'name'):
                    # 🔧 修复：安全获取element内容
                    element_content = getattr(element, "content", getattr(element, "name", str(element))).lower()
                    element_type = getattr(element, 'symbol_type', None)
                    
                    if element_type:
                        type_name = element_type.value.lower() if hasattr(element_type, 'value') else str(element_type).lower()
                        safe_content = getattr(element, "content", getattr(element, "name", str(element)))
                        if 'environment' in type_name:
                            content['environment'] = safe_content
                        elif 'object' in type_name:
                            content['object'] = safe_content
                        elif 'character' in type_name:
                            content['characteristics'].append(safe_content)
                        elif 'action' in type_name:
                            content['action'] = safe_content
                        elif 'tool' in type_name:
                            content['tool'] = safe_content
                        elif 'result' in type_name:
                            content['result'] = safe_content
        
        # 如果还是没有提取到，尝试从文本中解析
        if not any([content['environment'], content['object'], content['action']]):
            parsed_content = self._parse_content_from_text(all_text)
            for key, value in parsed_content.items():
                if content[key] is None or (key == 'characteristics' and not content[key]):
                    content[key] = value
        
        return content
    
    def _parse_content_from_text(self, text):
        """从文本中解析EOCATR内容"""
        content = {
            'environment': None,
            'object': None, 
            'characteristics': [],
            'action': None,
            'tool': None,
            'result': None
        }
        
        text_lower = text.lower()
        
        # 解析环境 - 支持中英文
        env_keywords = [
            'open_field', 'forest', 'water_source', 'danger_zone', 'safe_area',
            '开阔地', '森林', '水域', '危险区域', '安全区域', '水源区域'
        ]
        for env in env_keywords:
            if env in text_lower:
                content['environment'] = env
                break
        
        # 解析对象 - 支持中英文
        obj_keywords = [
            'berry', 'mushroom', 'tiger', 'rabbit', 'unknown', 'strawberry', 'potato',
            '草莓', '蘑菇', '老虎', '兔子', '野猪', '黑熊', '未知'
        ]
        for obj in obj_keywords:
            if obj in text_lower:
                content['object'] = obj
                break
        
        # 解析特征 - 支持中英文
        char_keywords = [
            'ripe', 'dangerous', 'safe', 'normal', 'toxic', 'near', 'far', 'healthy',
            '成熟', '危险', '安全', '正常', '有毒', '距离近', '距离远', '健康',
            '可食用', '营养丰富', '血量高', '血量低'
        ]
        for char in char_keywords:
            if char in text_lower:
                content['characteristics'].append(char)
        
        # 解析行动 - 支持中英文
        action_keywords = [
            'explore', 'collect', 'move', 'attack', 'flee', 'right', 'left', 'up', 'down',
            '探索', '采集', '移动', '攻击', '逃跑', '观察', '跟踪', '逃避'
        ]
        for action in action_keywords:
            if action in text_lower:
                content['action'] = action
                break
        
        # 解析工具 - 支持中英文
        tool_keywords = [
            'basket', 'spear', 'axe', 'knife', 'rope',
            '篮子', '长矛', '斧头', '刀', '绳子', '石头', '木棍', '陷阱'
        ]
        for tool in tool_keywords:
            if tool in text_lower:
                content['tool'] = tool
                break
        if 'none' in text_lower or '无工具' in text_lower:
            content['tool'] = 'none'
        
        # 解析结果 - 支持中英文，更具体的结果描述
        result_keywords = [
            'success', 'failure', 'discovery', 'escape', 'damage', 'food_gained', 'water_gained',
            'position_changed', 'damage_dealt', 'health+', 'food+', 'water+', 'health-', 'food-', 'water-',
            '成功', '失败', '发现', '逃脱', '伤害', '获得食物', '获得水分', '收集成功', 
            '攻击生效', '效率提升', '受到伤害', '获得奖励', '食物增加', '水分增加', '血量增加',
            '食物减少', '水分减少', '血量减少', '移动成功', '采集成功', '攻击成功', '探索成功',
            '移动失败', '采集失败', '攻击失败', '探索失败', '位置改变', '造成伤害'
        ]
        for result in result_keywords:
            if result in text_lower:
                content['result'] = result
                break
        
        return content
    
    def _generate_content_based_pattern(self, content):
        """根据实际内容生成具体的经验格式"""
        pattern_parts = []
        type_parts = []
        
        # 按照EOCATR顺序检查实际内容
        if content['environment']:
            pattern_parts.append(content['environment'])
            type_parts.append('E')
        
        if content['object']:
            pattern_parts.append(content['object'])
            type_parts.append('O')
        
        if content['characteristics']:
            char_count = len(content['characteristics'])
            if char_count == 1:
                pattern_parts.append(content['characteristics'][0])
                type_parts.append('C1')
            elif char_count == 2:
                pattern_parts.append(','.join(content['characteristics']))
                type_parts.append('C2')
            else:
                pattern_parts.append(','.join(content['characteristics'][:3]))
                type_parts.append('C3')
        
        # A和T至少要有一个
        if content['action'] and content['tool'] and content['tool'] != 'none':
            # 如果同时有行动和工具，优先显示工具
            pattern_parts.append(content['tool'])
            type_parts.append('T')
        elif content['tool'] and content['tool'] != 'none':
            pattern_parts.append(content['tool'])
            type_parts.append('T')
        elif content['action']:
            pattern_parts.append(content['action'])
            type_parts.append('A')
        
        # 结果
        if content['result']:
            pattern_parts.append(content['result'])
            type_parts.append('R')
        else:
            # 如果没有明确结果，使用默认
            pattern_parts.append('result')
            type_parts.append('R')
        
        # 生成最终格式：实际内容-类型标识
        if len(pattern_parts) >= 2:
            content_pattern = '-'.join(pattern_parts)
            type_pattern = '-'.join(type_parts)
            return f"{content_pattern} ({type_pattern})"
        else:
            return 'UNKNOWN'

    def _default_config(self) -> Dict[str, Any]:
        """默认配置 - 平衡版本"""
        return {
            # 怒放参数（平衡设置）
            'max_candidate_rules': 5000,        # 适中的最大候选规律数量
            'generation_threshold': 2,          # 降低生成阈值：2个经验即可触发
            'pattern_diversity_weight': 0.3,    # 适中的多样性权重
            'immediate_rule_generation': True,   # 保持立即生成
            
            # 剪枝参数（适中严格）
            'pruning_confidence_threshold': 0.05,  # 适中的剪枝阈值
            'pruning_age_threshold': 200,          # 适中的保留时间
            'contradicting_evidence_threshold': 0.8,  # 适中的矛盾容忍度
            
            # 验证参数（降低门槛）
            'validation_confidence_threshold': 0.2,   # 进一步降低验证置信度阈值
            'validation_success_rate_threshold': 0.4, # 新增：成功率阈值
            'validation_evidence_threshold': 1,       # 保持低证据要求
            
            # 自动晋升（新增）
            'auto_promotion_enabled': True,
            'auto_promote_repeat_threshold': 4,
            'auto_promote_confidence_threshold': 0.5,
            'auto_promote_max_contradiction_ratio': 0.5,
            
            # 质量控制（宽松但有标准）
            'min_activation_for_validation': 0,       # 无激活次数要求
            'max_complexity': 8,                      # 允许较高复杂度
            'min_quality_threshold': 0.01,            # 非常低的质量阈值
            'enable_single_experience_rules': True,   # 允许单经验规律
            'force_rule_generation': False,           # 不强制生成
        }
    def _initialize_pattern_templates(self) -> Dict[RuleType, List[str]]:
        """初始化模式模板"""
        return {
            RuleType.CAUSAL: [
                "当{condition}时，执行{action}导致{result}",
                "在{environment}中，{object}+{action}→{outcome}",
                "{trigger}引起{consequence}"
            ],
            RuleType.CONDITIONAL: [
                "如果{condition}，则{action}",
                "当{state}满足{threshold}时，选择{action}",
                "在{context}下，避免{negative_action}"
            ],
            RuleType.SEQUENTIAL: [
                "{action1}之后应该{action2}",
                "先{prerequisite}，再{main_action}",
                "{sequence}的最优顺序"
            ],
            RuleType.SPATIAL: [
                "在{location}附近，适合{action}",
                "距离{object} {distance}时，{recommendation}",
                "{spatial_pattern}的行为模式"
            ],
            RuleType.ASSOCIATIVE: [
                "{object1}通常与{object2}一起出现",
                "{pattern}的组合效应",
                "{correlation}的关联性"
            ],
            RuleType.EXCLUSION: [
                "{condition}时，避免{action}",
                "{object}与{incompatible}不能同时处理",
                "{exclusion_pattern}"
            ],
            RuleType.OPTIMIZATION: [
                "在{situation}中，{option1}优于{option2}",
                "{context}下的最优策略是{strategy}",
                "{optimization_rule}"
            ],
            RuleType.TOOL_EFFECTIVENESS: [
                "工具{tool}对{target}的效果是{effect}",
                "在{context}下，工具{tool}对{target}的效果是{effect}",
                "{tool}对{target}的效果是{effect}"
            ]
        }
    
    def bloom(self, eocar_experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """怒放阶段的别名方法"""
        return self.blooming_phase(eocar_experiences)
    
    def blooming_phase(self, eocar_experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """
        怒放阶段：基于经验生成候选规律
        
        🔥 核心策略变更：移除所有阈值限制，立即规律化
        """
        try:
            # 🚀 效率优化：过滤相关经验
            eocar_experiences = self._filter_relevant_experiences_for_blooming(eocar_experiences)
            
            # 🎯 检查新经验充足性
            if not self._has_sufficient_new_experiences(eocar_experiences):
                return []
            
            if not eocar_experiences:
                return []
            
            new_rules = []
            
            # 🔧 预处理：分离工具使用和常规经验
            tool_usage_experiences = [exp for exp in eocar_experiences if exp.is_tool_usage()]
            regular_experiences = [exp for exp in eocar_experiences if not exp.is_tool_usage()]
            
            if self.logger:
                self.logger.log(f"🌸 怒放阶段开始：总经验{len(eocar_experiences)}个（工具使用:{len(tool_usage_experiences)}, 常规:{len(regular_experiences)}）")
            
            # === 🔧 第一优先级：工具使用规律生成 ===
            if tool_usage_experiences:
                if self.logger:
                    self.logger.log(f"🔧 优先处理工具使用经验...")
                
                # 直接调用工具效果规律生成
                tool_rules = self._generate_tool_effectiveness_rules(tool_usage_experiences)
                new_rules.extend(tool_rules)
                
                if self.logger and tool_rules:
                    self.logger.log(f"🔧 工具规律生成: {len(tool_rules)}条规律")
                    for rule in tool_rules[:3]:  # 显示前3条
                        self.logger.log(f"   -> {rule.pattern}")
            
            # === 🔥 核心策略：无阈值模式分组 ===
            # 按模式分组所有经验，但不设置任何限制
            experience_groups = self._group_experiences_by_pattern(eocar_experiences)
            
            if self.logger:
                self.logger.log(f"🔥 经验分组完成：共{len(experience_groups)}个模式组")
                for pattern_key, group_experiences in experience_groups.items():
                    self.logger.log(f"🔥   模式'{pattern_key}': {len(group_experiences)}个经验")
            
            # === 🔥 核心修复：移除阈值限制，每个模式组都生成规律 ===
            group_rule_counts = {}
            for pattern_key, group_experiences in experience_groups.items():
                # 🔥 移除 min_group_size 检查：任何模式组都处理
                try:
                    if self.logger:
                        self.logger.log(f"🔥 处理模式组 '{pattern_key}': {len(group_experiences)}个经验")
                    
                    # 生成规律（无数量限制）
                    group_rules = self._generate_rules_for_pattern(pattern_key, group_experiences)
                    
                    if self.logger:
                        self.logger.log(f"🔥 模式组'{pattern_key}'生成{len(group_rules)}条初始规律")
                    
                    # 🔥 移除质量检查和数量限制，只进行基本去重
                    accepted_rules = []
                    for rule in group_rules:
                        # 只做最基本的重复检查，不做质量筛选
                        if not self._is_obvious_duplicate_simple(rule):
                            accepted_rules.append(rule)
                            if self.logger:
                                self.logger.log(f"🔥 接受规律: {rule.pattern[:50]}...")
                        else:
                            if self.logger:
                                self.logger.log(f"🔥 跳过重复规律: {rule.pattern[:50]}...")
                    
                    new_rules.extend(accepted_rules)
                    group_rule_counts[pattern_key] = len(accepted_rules)
                    
                    if self.logger:
                        self.logger.log(f"🔥 模式组'{pattern_key}'最终接受{len(accepted_rules)}条规律")
                        
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"❌ 模式组'{pattern_key}'规律生成失败: {str(e)}")
                        import traceback
                        self.logger.log(f"❌ 详细错误: {traceback.format_exc()}")
            
            # === 🔥 移除质量控制，直接接受所有规律 ===
            if new_rules:
                # 🔥 只做最基本的去重，不做质量筛选
                final_rules = []
                for rule in new_rules:
                    # 🔥 移除质量检查，直接接受规律
                    if not self._is_obvious_duplicate_simple(rule):
                        final_rules.append(rule)
                        if self.logger:
                            self.logger.log(f"🔥 最终接受规律: {rule.rule_id[:8]}... - {rule.pattern[:30]}...")
                    else:
                        if self.logger:
                            self.logger.log(f"🔥 最终跳过重复: {rule.rule_id[:8]}...")
                
                # 将新规律添加到候选集合
                for rule in final_rules:
                    self.candidate_rules[rule.rule_id] = rule
                    # 🔥 使用内容指纹进行去重跟踪
                    content_fingerprint = self._generate_content_fingerprint(rule)
                    self.rule_fingerprints.add(content_fingerprint)
                    self.total_rules_generated += 1
                
                # 记录生成历史
                self.rule_generation_history.append((time.time(), len(final_rules)))
                
                if self.logger:
                    self.logger.log(f"🔥 新经验立即规律化成功：生成 {len(final_rules)} 个候选规律")
                    
                    # 统计规律类型分布
                    type_counts = {}
                    for rule in final_rules:
                        rule_type = rule.rule_type.value
                        type_counts[rule_type] = type_counts.get(rule_type, 0) + 1
                    
                    # 详细报告各类型规律数量  
                    for rule_type, count in sorted(type_counts.items()):
                        self.logger.log(f"🔥   {rule_type}: {count}条规律")
                    
                    # 特别报告工具规律
                    tool_rule_count = type_counts.get('tool_effectiveness', 0)
                    if tool_rule_count > 0:
                        self.logger.log(f"🔧 工具效用规律: {tool_rule_count}条 ⭐")
                    
                    # 显示前几条规律的内容
                    self.logger.log(f"🔥 前3条生成的规律示例:")
                    for i, rule in enumerate(final_rules[:3]):
                        rule_format = self._format_rule_to_standard_pattern(rule)
                        self.logger.log(f"🔥   {i+1}. {rule_format}")
                
                return final_rules
            else:
                if self.logger:
                    self.logger.log("🔥 警告：即使移除所有阈值限制，仍未生成任何规律")
                    self.logger.log(f"🔥 输入经验数量: {len(eocar_experiences)}")
                    self.logger.log(f"🔥 经验分组数量: {len(experience_groups)}")
                    for pattern_key, group_experiences in experience_groups.items():
                        self.logger.log(f"🔥   模式'{pattern_key}': {len(group_experiences)}个经验")
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 新经验立即规律化发生错误: {str(e)}")
                import traceback
                self.logger.log(f"❌ 详细错误: {traceback.format_exc()}")
            return []
    
    def _group_experiences_by_pattern(self, experiences: List[EOCATR_Tuple]) -> Dict[str, List[EOCATR_Tuple]]:
        """按模式分组经验，进行预处理和分类"""
        pattern_groups = defaultdict(list)
        
        # 🔧 优先处理工具使用经验（新增特殊处理）
        tool_usage_experiences = []
        non_tool_experiences = []
        
        for exp in experiences:
            if exp.is_tool_usage():  # 使用工具的经验
                tool_usage_experiences.append(exp)
                
                # 为工具使用经验创建专门的模式组
                tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                obj_val = exp.object_category.value if exp.object_category and hasattr(exp.object_category, 'value') else 'unknown'
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                tool_pattern_key = f"TOOL_USAGE_{tool_val}_{obj_val}_{act_val}"
                pattern_groups[tool_pattern_key].append(exp)
                
                # 同时保留原有分组逻辑
                basic_pattern = f"{obj_val}+{act_val}+{tool_val}"
                pattern_groups[basic_pattern].append(exp)
            else:
                non_tool_experiences.append(exp)
                # 原有分组逻辑
                obj_val = exp.object_category.value if exp.object_category and hasattr(exp.object_category, 'value') else 'unknown'
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                basic_pattern = f"{obj_val}+{act_val}"
                pattern_groups[basic_pattern].append(exp)
        
        # 💡 环境-动作-工具组合模式（增强的三维模式）
        for exp in experiences:
            env_val = exp.environment.value if exp.environment and hasattr(exp.environment, 'value') else 'unknown'
            act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
            tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
            env_action_tool_pattern = f"ENV_{env_val}+ACT_{act_val}+TOOL_{tool_val}"
            pattern_groups[env_action_tool_pattern].append(exp)
        
        # 💎 结果成功性模式（按成功/失败分组）
        success_pattern_key = "SUCCESS_PATTERNS"
        failure_pattern_key = "FAILURE_PATTERNS"
        
        for exp in experiences:
            if exp.result.success:
                pattern_groups[success_pattern_key].append(exp)
            else:
                pattern_groups[failure_pattern_key].append(exp)
        
        # 🎯 工具效果优化模式（专门用于工具比较）
        if tool_usage_experiences:
            # 按目标类型分组工具使用经验
            tool_targets = defaultdict(list)
            for exp in tool_usage_experiences:
                obj_val = exp.object_category.value if exp.object_category and hasattr(exp.object_category, 'value') else 'unknown'
                target_key = f"TARGET_{obj_val}"
                tool_targets[target_key].append(exp)
            
            # 为每个目标类型创建工具比较模式
            for target_key, target_experiences in tool_targets.items():
                if len(target_experiences) >= 2:  # 至少需要2次经验进行比较
                    comparison_pattern_key = f"TOOL_COMPARISON_{target_key}"
                    pattern_groups[comparison_pattern_key] = target_experiences
        
        # 📍 距离效果模式
        for exp in experiences:
            distance_range = self._get_distance_range(exp.characteristics.distance)
            act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
            tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
            distance_pattern = f"DISTANCE_{distance_range}+{act_val}+{tool_val}"
            pattern_groups[distance_pattern].append(exp)
        
        # 📊 记录分组统计
        if self.logger:
            tool_groups = len([k for k in pattern_groups.keys() if 'TOOL_USAGE' in k])
            total_groups = len(pattern_groups)
            tool_exp_count = len(tool_usage_experiences)
            total_exp_count = len(experiences)
            
            if tool_groups > 0:
                self.logger.log(f"🔧 BPM经验分组完成: {total_groups}个模式组（含{tool_groups}个工具专用组）")
                self.logger.log(f"🔧 工具使用经验：{tool_exp_count}/{total_exp_count} ({tool_exp_count/total_exp_count*100:.1f}%)")
            else:
                self.logger.log(f"🔧 BPM经验分组完成: {total_groups}个模式组（无工具使用记录）")
        
        return dict(pattern_groups)
    
    def _generate_rules_for_pattern(self, pattern_key: str, experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """🔥 重构版本：为特定模式生成规律，移除阈值限制"""
        # 🔥 移除阈值检查：任何数量的经验都应该尝试生成规律
        if self.logger:
            self.logger.log(f"🔥 开始为模式'{pattern_key}'生成规律，经验数: {len(experiences)}")
        
        # 分析经验特征
        common_chars = self._extract_common_characteristics(experiences)
        common_results = self._extract_common_results(experiences)
        
        new_rules = []

        # === 新增：单特征C六族生成（E-C-A-R / E-C-T-R / O-C-A-R / O-C-T-R / C-A-R / C-T-R）===
        try:
            # 从每条经验提取可见特征集合（characteristic_*），逐个生成单特征C候选规律
            for exp in experiences:
                try:
                    # 将 E/O/A/T 取值
                    env_val = exp.get_environment_compat().value if hasattr(exp, 'get_environment_compat') and exp.get_environment_compat() else None
                    obj_val = exp.object_category.value if hasattr(exp, 'object_category') and exp.object_category else None
                    act_val = exp.get_action_compat().value if hasattr(exp, 'get_action_compat') and exp.get_action_compat() else None
                    tool_val = exp.get_tool_compat().value if hasattr(exp, 'get_tool_compat') and exp.get_tool_compat() else None
                    res_val = exp.get_result_compat().content if hasattr(exp, 'get_result_compat') and exp.get_result_compat() else None

                    # 解析 C：支持字符串形式的 "characteristic_x=y;..." 或兼容包装器中的 content
                    c_candidates = []
                    try:
                        raw_c = getattr(exp, 'character', None)
                        raw_content = getattr(raw_c, 'content', None)
                        if isinstance(raw_content, str) and 'characteristic_' in raw_content:
                            for part in raw_content.split(';'):
                                part = part.strip()
                                if not part:
                                    continue
                                if '=' in part:
                                    k, v = part.split('=', 1)
                                    k = k.strip()
                                    v = v.strip()
                                    if k and v:
                                        c_candidates.append((k, v))
                    except Exception:
                        pass

                    # 对每个单特征C生成六族候选
                    for c_key, c_val in c_candidates[:8]:  # 轻度限流：每条经验最多取前8个特征
                        # E-C-A-R
                        if env_val and act_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"ECAR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"在{env_val}中，若{c_key}={c_val}，执行{act_val}→{res_val}",
                                conditions={'environment': env_val, c_key: c_val, 'action': act_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=3
                            ))
                        # E-C-T-R
                        if env_val and tool_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"ECTR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"在{env_val}中，若{c_key}={c_val}，使用{tool_val}→{res_val}",
                                conditions={'environment': env_val, c_key: c_val, 'tool': tool_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=3
                            ))
                        # O-C-A-R
                        if obj_val and act_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"OCAR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"对{obj_val}，若{c_key}={c_val}，执行{act_val}→{res_val}",
                                conditions={'object_category': obj_val, c_key: c_val, 'action': act_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=3
                            ))
                        # O-C-T-R
                        if obj_val and tool_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"OCTR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"对{obj_val}，若{c_key}={c_val}，使用{tool_val}→{res_val}",
                                conditions={'object_category': obj_val, c_key: c_val, 'tool': tool_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=3
                            ))
                        # C-A-R
                        if act_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"CAR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"若{c_key}={c_val}，执行{act_val}→{res_val}",
                                conditions={c_key: c_val, 'action': act_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=2
                            ))
                        # C-T-R
                        if tool_val and res_val:
                            new_rules.append(CandidateRule(
                                rule_id=f"CTR_{int(time.time()*1000000)%1000000}",
                                rule_type=RuleType.CAUSAL,
                                pattern=f"若{c_key}={c_val}，使用{tool_val}→{res_val}",
                                conditions={c_key: c_val, 'tool': tool_val},
                                predictions={'result': res_val, 'expected_success': exp.success},
                                confidence=0.5,
                                complexity=2
                            ))
                except Exception:
                    continue
        except Exception:
            pass
        
        # 根据模式类型生成不同类型的规律（修复版）
        
        # 检查是否包含动作模式（修复：检查实际的动作名称）
        action_patterns = ['GATHER', 'MOVE', 'AVOID', 'ATTACK', 'DRINK', 'EXPLORE', 'collect', 'drink', 'move', 'explore', 'rest']
        has_action_pattern = any(action in pattern_key for action in action_patterns)
        
        if has_action_pattern or "+" in pattern_key:  # 对象+动作组合
            new_rules.extend(self._generate_causal_rules(pattern_key, experiences, common_chars, common_results))
            new_rules.extend(self._generate_conditional_rules(pattern_key, experiences, common_chars))
        
        # 检查结果模式
        if "success" in pattern_key or "failure" in pattern_key:
            new_rules.extend(self._generate_optimization_rules(pattern_key, experiences))
        
        # 检查环境模式
        if "env_" in pattern_key:
            new_rules.extend(self._generate_spatial_rules(experiences))
        
        # 检查时序模式
        if "sequence" in pattern_key or len(experiences) > 5:
            new_rules.extend(self._generate_sequential_rules(experiences))
        
        # === 新增：工具效用规律生成 ===
        if ("tool_usage_" in pattern_key or "tool_effect_" in pattern_key or "tool_type_" in pattern_key or 
            "tool_use" in pattern_key or "tool" in pattern_key.lower()):
            new_rules.extend(self._generate_tool_effectiveness_rules(experiences))
        
        # === 🔥 极度宽松的规律接受策略 ===
        filtered_rules = []
        for rule in new_rules:
            # 🔥 只做最基本的结构检查，移除所有质量和重复限制
            if rule.rule_id and rule.pattern:  # 只要有基本结构就接受
                filtered_rules.append(rule)
                # 添加规律指纹（但不用于拒绝）
                try:
                    self.rule_fingerprints.add(self._generate_rule_fingerprint(rule))
                except:
                    pass  # 指纹生成失败也不影响规律接受
                
                if self.logger:
                    self.logger.log(f"🔥 接受规律: {rule.rule_id[:8]}... - {rule.pattern[:50]}...")
            else:
                if self.logger:
                    self.logger.log(f"🔥 跳过无效规律: rule_id={getattr(rule, 'rule_id', 'None')}, pattern={getattr(rule, 'pattern', 'None')}")
        
        if self.logger:
            self.logger.log(f"🔥 模式'{pattern_key}'最终生成{len(filtered_rules)}条规律")
        
        return filtered_rules
    
    def _passes_quality_check(self, rule: CandidateRule) -> bool:
        """增强的质量检查 - 平衡严格性和包容性"""
        try:
            # 基础结构检查
            if not rule.rule_id or not rule.pattern:
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 缺少基本结构")
                return False
            
            # 计算质量得分
            quality_score = rule.calculate_quality_score()
            
            # 降低质量阈值，提高包容性
            min_threshold = self.config.get('min_quality_threshold', 0.01)
            if quality_score < min_threshold:
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 质量得分{quality_score:.3f} < 阈值{min_threshold}")
                return False
            
            # 置信度检查 - 非常宽松
            if rule.confidence < 0.001:  # 极低阈值
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 置信度过低{rule.confidence:.3f}")
                return False
            
            # 复杂度检查 - 允许更高复杂度
            max_complexity = self.config.get('max_complexity', 10)
            if rule.complexity > max_complexity:
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 复杂度过高{rule.complexity} > {max_complexity}")
                return False
            
            # 条件和预测完整性检查 - 宽松检查
            if not rule.conditions and not rule.predictions:
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 条件和预测都为空")
                return False
            
            # 模式有效性检查 - 更宽松
            if len(rule.pattern.strip()) < 5:  # 降低最小长度要求
                if self.logger:
                    self.logger.log(f"❌ 质量检查失败: 模式过短")
                return False
            
            if self.logger:
                self.logger.log(f"✅ 质量检查通过: {rule.rule_id[:8]} (得分:{quality_score:.3f})")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 质量检查异常: {str(e)}")
            return False

    def _is_obvious_duplicate_simple(self, rule: CandidateRule) -> bool:
        """
        🔥 改进的重复检查：基于内容指纹而不是ID
        检查规律内容是否真正重复
        """
        try:
            # 生成基于内容的指纹（不包含时间戳）
            content_fingerprint = self._generate_content_fingerprint(rule)
            
            # 检查指纹是否已存在
            if content_fingerprint in self.rule_fingerprints:
                if self.logger:
                    self.logger.log(f"🔥 发现重复规律内容: {rule.pattern[:30]}...")
                return True
            
            # 检查与现有规律的相似度
            all_existing_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
            for existing_rule in all_existing_rules:
                if self._is_content_identical(rule, existing_rule):
                    if self.logger:
                        self.logger.log(f"🔥 发现内容相同的规律: {rule.pattern[:30]}...")
                    return True
            
            return False
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 简单重复检查失败: {str(e)}")
            return False  # 异常时不认为重复
    def _is_duplicate_rule(self, rule: CandidateRule) -> bool:
        """检查规律是否为重复规律（增强调试版本）"""
        try:
            # 🚨 FORCE DEBUG
            if self.logger:
                self.logger.log(f"🔥 DUPLICATE CHECK: 检查规律 rule_id={rule.rule_id[:8]}...")
            
            # 生成当前规律的指纹
            current_fingerprint = self._generate_rule_fingerprint(rule)
            if self.logger:
                self.logger.log(f"🔥 DUPLICATE CHECK: 当前指纹={current_fingerprint[:8]}...")
            
            # 快速指纹检查
            if current_fingerprint in self.rule_fingerprints:
                if self.logger:
                    self.logger.log(f"🔥 DUPLICATE CHECK: 指纹重复! 已存在相同指纹")
                return True
            
            if self.logger:
                self.logger.log(f"🔥 DUPLICATE CHECK: 指纹检查通过，开始详细相似度检查...")
                self.logger.log(f"🔥 DUPLICATE CHECK: 现有候选规律数={len(self.candidate_rules)}, 已验证规律数={len(self.validated_rules)}")
            
            # 详细相似度检查
            all_existing_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
            for i, existing_rule in enumerate(all_existing_rules):
                similarity = self._calculate_rule_similarity(rule, existing_rule)
                if self.logger:
                    self.logger.log(f"🔥 DUPLICATE CHECK: 与现有规律{i+1} 相似度={similarity:.3f}, 阈值={self.rule_similarity_threshold}")
                
                if similarity > self.rule_similarity_threshold:
                    if self.logger:
                        self.logger.log(f"🔥 DUPLICATE CHECK: 相似度过高! 认定为重复")
                    return True
            
            if self.logger:
                self.logger.log(f"🔥 DUPLICATE CHECK: 所有检查通过，非重复规律")
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"🔥 DUPLICATE CHECK: 异常={str(e)}")
                self.logger.log(f"重复检查失败: {str(e)}")
            return False

    def _generate_rule_fingerprint(self, rule: CandidateRule) -> str:
        """生成规律的唯一指纹（包含ID确保唯一性）"""
        try:
            # 包含ID的完整指纹，用于LRU等管理
            fingerprint_components = [
                rule.rule_type.value,
                rule.rule_id,  # 保留ID确保绝对唯一
                str(sorted(enumerate(rule.condition_elements))),
                str(sorted(rule.predictions.items())),
                rule.pattern,
                str(rule.confidence),
                str(rule.complexity)
            ]
            
            # 使用哈希生成指纹
            import hashlib
            fingerprint_str = "|".join(fingerprint_components)
            fingerprint = hashlib.md5(fingerprint_str.encode()).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"生成指纹失败: {str(e)}")
            # 确保异常情况下也返回唯一指纹
            return f"error_{rule.rule_id}_{int(time.time() * 1000000)}"
    
    def _generate_content_fingerprint(self, rule: CandidateRule) -> str:
        """生成基于内容的指纹（用于去重）"""
        try:
            # 🔥 只基于规律内容，不包含ID和时间戳
            content_components = [
                rule.rule_type.value,
                str(sorted(rule.condition_elements)),
                str(sorted(rule.predictions.items())),
                rule.pattern.strip().lower(),  # 标准化模式文本
                str(sorted(rule.conditions.items())),
            ]
            
            # 使用哈希生成内容指纹
            import hashlib
            content_str = "|".join(content_components)
            content_fingerprint = hashlib.md5(content_str.encode()).hexdigest()
            
            return content_fingerprint
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"生成内容指纹失败: {str(e)}")
            return f"content_error_{int(time.time() * 1000000)}"
    
    def _is_content_identical(self, rule1: CandidateRule, rule2: CandidateRule) -> bool:
        """检查两个规律的内容是否完全相同"""
        try:
            # 检查核心内容是否相同
            return (
                rule1.rule_type == rule2.rule_type and
                rule1.pattern.strip().lower() == rule2.pattern.strip().lower() and
                sorted(rule1.condition_elements) == sorted(rule2.condition_elements) and
                rule1.predictions == rule2.predictions and
                rule1.conditions == rule2.conditions
            )
        except Exception as e:
            if self.logger:
                self.logger.log(f"内容比较失败: {str(e)}")
            return False

    def _calculate_rule_similarity(self, rule1: CandidateRule, rule2: CandidateRule) -> float:
        """计算两个规律之间的相似度"""
        try:
            if rule1.rule_type != rule2.rule_type:
                return 0.0
            
            # 条件相似度
            conditions_similarity = self._calculate_dict_similarity(rule1.conditions, rule2.conditions)
            
            # 预测相似度
            predictions_similarity = self._calculate_dict_similarity(rule1.predictions, rule2.predictions)
            
            # 模式相似度
            pattern_similarity = self._calculate_text_similarity(rule1.pattern, rule2.pattern)
            
            # 加权平均
            overall_similarity = (
                conditions_similarity * 0.4 +
                predictions_similarity * 0.4 +
                pattern_similarity * 0.2
            )
            
            return overall_similarity
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"相似度计算失败: {str(e)}")
            return 0.0
    
    def _calculate_dict_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """计算两个字典的相似度"""
        if not dict1 and not dict2:
            return 1.0
        if not dict1 or not dict2:
            return 0.0
        
        # 找到共同的键
        common_keys = set(dict1.keys()) & set(dict2.keys())
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        if not all_keys:
            return 1.0
        
        # 计算共同键的比例
        key_similarity = len(common_keys) / len(all_keys)
        
        # 计算共同键的值相似度
        value_similarity = 0.0
        if common_keys:
            for key in common_keys:
                if dict1[key] == dict2[key]:
                    value_similarity += 1.0
                elif isinstance(dict1[key], (int, float)) and isinstance(dict2[key], (int, float)):
                    # 数值类型计算相对差异
                    diff = abs(dict1[key] - dict2[key])
                    max_val = max(abs(dict1[key]), abs(dict2[key]), 1)
                    value_similarity += max(0, 1 - diff / max_val)
            value_similarity /= len(common_keys)
        
        return (key_similarity + value_similarity) / 2
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # 简单的基于词汇重叠的相似度计算
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _attempt_rule_merge(self, new_rule: CandidateRule) -> Optional[CandidateRule]:
        """尝试将新规律与现有规律合并"""
        try:
            best_merge_candidate = None
            best_similarity = 0.0
            merge_threshold = 0.7  # 合并阈值
            
            # 寻找最佳合并候选
            all_existing_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
            
            for existing_rule in all_existing_rules:
                similarity = self._calculate_rule_similarity(new_rule, existing_rule)
                if similarity > merge_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_merge_candidate = existing_rule
            
            # 如果找到合适的合并候选，执行合并
            if best_merge_candidate:
                merged_rule = self._merge_rules(new_rule, best_merge_candidate, best_similarity)
                if merged_rule:
                    self.total_rules_merged += 1
                    self.rule_merge_history.append((new_rule.rule_id, best_merge_candidate.rule_id, best_similarity))
                    
                    # 从原存储中移除被合并的规律
                    if best_merge_candidate.rule_id in self.candidate_rules:
                        del self.candidate_rules[best_merge_candidate.rule_id]
                    elif best_merge_candidate.rule_id in self.validated_rules:
                        del self.validated_rules[best_merge_candidate.rule_id]
                    
                    if self.logger:
                        self.logger.log(f"规律合并: {new_rule.rule_id} + {best_merge_candidate.rule_id} -> {merged_rule.rule_id}")
                    
                    return merged_rule
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"规律合并失败: {str(e)}")
            return None
    
    def _merge_rules(self, rule1: CandidateRule, rule2: CandidateRule, similarity: float) -> Optional[CandidateRule]:
        """合并两个相似的规律"""
        try:
            # 选择质量更高的规律作为基础
            base_rule = rule1 if rule1.calculate_quality_score() > rule2.calculate_quality_score() else rule2
            other_rule = rule2 if base_rule == rule1 else rule1
            
            # 创建合并后的规律（修复合并标签重复问题）
            # 清理基础规律的pattern，移除已有的[合并]标签
            clean_pattern = base_rule.pattern
            if clean_pattern.startswith("[合并]"):
                clean_pattern = clean_pattern.replace("[合并]", "").strip()
            
            # 只在第一次合并时添加[合并]标签
            if not base_rule.pattern.startswith("[合并]"):
                merged_pattern = f"[合并] {clean_pattern}"
            else:
                merged_pattern = base_rule.pattern  # 保持原有的合并标签，不重复添加
            
            merged_rule = CandidateRule(
                rule_id=f"merged_{base_rule.rule_id}_{other_rule.rule_id}_{int(time.time())}",
                rule_type=base_rule.rule_type,
                pattern=merged_pattern,
                conditions=self._merge_dicts(base_rule.condition_elements, other_rule.condition_elements),
                predictions=self._merge_dicts(base_rule.predictions, other_rule.predictions),
                confidence=max(base_rule.confidence, other_rule.confidence),  # 取更高的置信度
                strength=(base_rule.strength + other_rule.strength) / 2,
                generalization=max(base_rule.generalization, other_rule.generalization),
                specificity=min(base_rule.specificity, other_rule.specificity),
                complexity=max(base_rule.complexity, other_rule.complexity),
                parent_rules=[base_rule.rule_id, other_rule.rule_id]
            )
            
            # 合并证据
            merged_rule.evidence.supporting_experiences.extend(base_rule.evidence.supporting_experiences)
            merged_rule.evidence.supporting_experiences.extend(other_rule.evidence.supporting_experiences)
            merged_rule.evidence.contradicting_experiences.extend(base_rule.evidence.contradicting_experiences)
            merged_rule.evidence.contradicting_experiences.extend(other_rule.evidence.contradicting_experiences)
            
            merged_rule.evidence.total_tests = base_rule.evidence.total_tests + other_rule.evidence.total_tests
            merged_rule.evidence.successful_tests = base_rule.evidence.successful_tests + other_rule.evidence.successful_tests
            
            # 合并激活信息
            merged_rule.activation_count = base_rule.activation_count + other_rule.activation_count
            merged_rule.last_activation = max(base_rule.last_activation, other_rule.last_activation)
            
            return merged_rule
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"规律合并操作失败: {str(e)}")
            return None
    
    def _merge_dicts(self, dict1: Dict, dict2: Dict) -> Dict:
        """智能合并两个字典"""
        merged = dict1.copy()
        
        for key, value in dict2.items():
            if key in merged:
                # 如果键已存在，根据值类型进行合并
                if isinstance(value, (int, float)) and isinstance(merged[key], (int, float)):
                    merged[key] = (merged[key] + value) / 2  # 数值取平均
                elif isinstance(value, str) and isinstance(merged[key], str):
                    if value != merged[key]:
                        merged[key] = f"{merged[key]}|{value}"  # 字符串连接
                # 其他类型保持原值
            else:
                merged[key] = value
        
        return merged
    
    def _generate_causal_rules(self, pattern_key: str, experiences: List[EOCATR_Tuple], 
                              common_chars: Dict, common_results: Dict) -> List[CandidateRule]:
        """生成因果规律（增强版本，支持单个经验）"""
        rules = []
        
        if self.logger:
            self.logger.log(f"🔥 CAUSAL RULES: 开始生成因果规律，经验数={len(experiences)}, pattern_key={pattern_key}")
        
        # 分析成功和失败的经验
        successful_experiences = [exp for exp in experiences if exp.result.success]
        failed_experiences = [exp for exp in experiences if not exp.result.success]
        
        if self.logger:
            self.logger.log(f"🔥 CAUSAL RULES: 成功经验={len(successful_experiences)}, 失败经验={len(failed_experiences)}")
        
        # 🚨 修改：从成功经验生成正向规律
        if len(successful_experiences) >= 1:
            if self.logger:
                self.logger.log(f"🔥 CAUSAL RULES: 生成正向因果规律...")
            
            # 生成正向因果规律
            rule_id = f"causal_positive_{pattern_key}_{int(time.time() * 1000000) % 1000000}"  # 确保唯一ID
            
            # 使用首个经验的信息
            first_exp = successful_experiences[0]
            
            conditions = {
                'object_category': first_exp.object_category.value if first_exp.object_category and hasattr(first_exp.object_category, 'value') else 'unknown',
                'action': first_exp.action.value if first_exp.action and hasattr(first_exp.action, 'value') else 'unknown',
                'environment': first_exp.environment.value if first_exp.environment and hasattr(first_exp.environment, 'value') else 'unknown',
                'tool': first_exp.tool.value if first_exp.tool and hasattr(first_exp.tool, 'value') else 'none',  # 🚨 添加工具信息
            }
            
            # 添加公共特征作为条件
            for char_name, char_value in common_chars.items():
                if char_value is not None:
                    conditions[f'characteristic_{char_name}'] = char_value
            
            predictions = {
                'expected_success': True,
                'expected_results': common_results,
                'pattern_key': pattern_key  # 🚨 添加模式键
            }
            
            # 计算置信度：成功率
            confidence = len(successful_experiences) / len(experiences) if experiences else 1.0
            
            pattern_text = f"在{conditions.get('environment', '任何环境')}中，使用{conditions.get('tool', '无工具')}对{conditions.get('object_category', '对象')}执行{conditions.get('action', '动作')}，预期结果：{predictions.get('expected_success', '成功')}"
            
            rule = CandidateRule(
                rule_id=rule_id,
                rule_type=RuleType.CAUSAL,
                pattern=pattern_text,
                conditions=conditions,
                predictions=predictions,
                confidence=confidence,
                complexity=len(conditions) + len(predictions)
            )
            
            # 添加支持证据
            for exp in successful_experiences:
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                rule.evidence.supporting_experiences.append(f"exp_{act_val}_{tool_val}_{int(time.time())}")
            
            for exp in failed_experiences:
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                rule.evidence.contradicting_experiences.append(f"exp_{act_val}_{tool_val}_{int(time.time())}")
            
            if self.logger:
                self.logger.log(f"🔥 CAUSAL RULES: 创建正向规律 {rule_id}, 置信度={confidence:.3f}")
            rules.append(rule)
        
        # 🚨 新增：从失败经验也生成规律（负向因果规律）
        if len(failed_experiences) >= 1:
            if self.logger:
                self.logger.log(f"🔥 CAUSAL RULES: 生成负向因果规律...")
            
            # 生成负向因果规律
            rule_id = f"causal_negative_{pattern_key}_{int(time.time() * 1000000) % 1000000}"
            
            # 使用首个失败经验的信息
            first_exp = failed_experiences[0]
            
            conditions = {
                'object_category': first_exp.object_category.value if first_exp.object_category and hasattr(first_exp.object_category, 'value') else 'unknown',
                'action': first_exp.action.value if first_exp.action and hasattr(first_exp.action, 'value') else 'unknown',
                'environment': first_exp.environment.value if first_exp.environment and hasattr(first_exp.environment, 'value') else 'unknown',
                'tool': first_exp.tool.value if first_exp.tool and hasattr(first_exp.tool, 'value') else 'none',
            }
            
            # 添加公共特征作为条件
            for char_name, char_value in common_chars.items():
                if char_value is not None:
                    conditions[f'characteristic_{char_name}'] = char_value
            
            predictions = {
                'expected_success': False,
                'expected_results': {'failure_type': 'action_ineffective'},
                'pattern_key': pattern_key,
                'avoid_action': True  # 标记为应避免的动作
            }
            
            # 计算置信度：失败率
            confidence = len(failed_experiences) / len(experiences) if experiences else 1.0
            
            pattern_text = f"在{conditions.get('environment', '任何环境')}中，使用{conditions.get('tool', '无工具')}对{conditions.get('object_category', '对象')}执行{conditions.get('action', '动作')}，通常会失败"
            
            rule = CandidateRule(
                rule_id=rule_id,
                rule_type=RuleType.CAUSAL,
                pattern=pattern_text,
                conditions=conditions,
                predictions=predictions,
                confidence=confidence,
                complexity=len(conditions) + len(predictions)
            )
            
            # 添加失败证据
            for exp in failed_experiences:
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                rule.evidence.supporting_experiences.append(f"fail_exp_{act_val}_{tool_val}_{int(time.time())}")
            
            # 成功经验作为反驳证据
            for exp in successful_experiences:
                act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                tool_val = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                rule.evidence.contradicting_experiences.append(f"success_exp_{act_val}_{tool_val}_{int(time.time())}")
            
            if self.logger:
                self.logger.log(f"🔥 CAUSAL RULES: 创建负向规律 {rule_id}, 置信度={confidence:.3f}")
            rules.append(rule)
        
        if self.logger:
            self.logger.log(f"🔥 CAUSAL RULES: 生成 {len(rules)} 个因果规律")
        return rules

    def _generate_conditional_rules(self, pattern_key: str, experiences: List[EOCATR_Tuple], 
                                   common_chars: Dict) -> List[CandidateRule]:
        """生成条件规律"""
        rules = []
        
        # 基于特征阈值生成条件规律
        numeric_characteristics = {}
        for exp in experiences:
            chars = exp.characteristics
            for attr_name in ['distance', 'nutrition_value', 'water_value']:
                attr_value = getattr(chars, attr_name, None)
                if attr_value is not None and isinstance(attr_value, (int, float)):
                    if attr_name not in numeric_characteristics:
                        numeric_characteristics[attr_name] = []
                    numeric_characteristics[attr_name].append((attr_value, exp.result.success))
        
        # 为每个数值特征生成阈值规律
        for char_name, values in numeric_characteristics.items():
            if len(values) >= 3:
                successful_values = [v for v, success in values if success]
                failed_values = [v for v, success in values if not success]
                
                if successful_values and failed_values:
                    # 计算分离阈值
                    threshold = self._calculate_optimal_threshold(successful_values, failed_values)
                    
                    if threshold is not None:
                        rule_id = f"conditional_{pattern_key}_{char_name}_{int(time.time() * 1000) % 10000}"
                        
                        conditions = {
                            'object_category': experiences[0].object_category.value,
                            f'{char_name}_threshold': threshold,
                            'comparison': 'less_than' if successful_values[0] < threshold else 'greater_than'
                        }
                        
                        predictions = {
                            'recommended_action': experiences[0].action.value,
                            'expected_success_rate': len(successful_values) / len(values)
                        }
                        
                        rule = CandidateRule(
                            rule_id=rule_id,
                            rule_type=RuleType.CONDITIONAL,
                            pattern=f"当{char_name}{'小于' if conditions['comparison'] == 'less_than' else '大于'}{threshold}时，对{conditions['object_category']}执行{predictions['recommended_action']}",
                            conditions=conditions,
                            predictions=predictions,
                            confidence=predictions['expected_success_rate'],
                            complexity=2
                        )
                        
                        rules.append(rule)
        
        return rules
    
    def _generate_optimization_rules(self, pattern_key: str, experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """生成优化规律"""
        rules = []
        
        # 按动作分组，比较效果
        actions_results = defaultdict(list)
        for exp in experiences:
            act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
            actions_results[act_val].append(exp.result.reward)
        
        if len(actions_results) >= 2:
            # 找到最佳动作
            action_avg_rewards = {}
            for action, rewards in actions_results.items():
                if rewards:
                    action_avg_rewards[action] = sum(rewards) / len(rewards)
            
            if len(action_avg_rewards) >= 2:
                best_action = max(action_avg_rewards.keys(), key=lambda a: action_avg_rewards[a])
                worst_action = min(action_avg_rewards.keys(), key=lambda a: action_avg_rewards[a])
                
                if action_avg_rewards[best_action] > action_avg_rewards[worst_action]:
                    rule_id = f"optimization_{pattern_key}_{int(time.time() * 1000) % 10000}"
                    
                    conditions = {
                        'context': pattern_key,
                        'object_category': experiences[0].object_category.value,
                        'environment': experiences[0].environment.value
                    }
                    
                    predictions = {
                        'optimal_action': best_action,
                        'suboptimal_action': worst_action,
                        'reward_difference': action_avg_rewards[best_action] - action_avg_rewards[worst_action]
                    }
                    
                    rule = CandidateRule(
                        rule_id=rule_id,
                        rule_type=RuleType.OPTIMIZATION,
                        pattern=f"在{conditions['environment']}中处理{conditions['object_category']}时，{best_action}比{worst_action}更优",
                        conditions=conditions,
                        predictions=predictions,
                        confidence=0.7,  # 初始置信度
                        complexity=3
                    )
                    
                    rules.append(rule)
        
        return rules
    
    def _generate_sequential_rules(self, experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """生成时序规律"""
        rules = []
        
        # 按时间戳排序
        sorted_experiences = sorted(experiences, key=lambda x: x.timestamp)
        
        # 寻找连续的动作序列
        for i in range(len(sorted_experiences) - 1):
            exp1 = sorted_experiences[i]
            exp2 = sorted_experiences[i + 1]
            
            # 检查是否是有意义的序列
            if (exp2.timestamp - exp1.timestamp < 10.0 and  # 时间间隔不超过10单位
                exp1.result.success and exp2.result.success):  # 两个动作都成功
                
                rule_id = f"sequential_{exp1.action.value}_{exp2.action.value}_{int(time.time() * 1000) % 10000}"
                
                conditions = {
                    'first_action': exp1.action.value,
                    'first_object': exp1.object_category.value,
                    'sequence_gap': exp2.timestamp - exp1.timestamp
                }
                
                predictions = {
                    'next_action': exp2.action.value,
                    'next_object': exp2.object_category.value,
                    'combined_reward': exp1.result.reward + exp2.result.reward
                }
                
                rule = CandidateRule(
                    rule_id=rule_id,
                    rule_type=RuleType.SEQUENTIAL,
                    pattern=f"在执行{exp1.action.value}之后，应该执行{exp2.action.value}",
                    conditions=conditions,
                    predictions=predictions,
                    confidence=0.5,  # 时序规律初始置信度较低
                    complexity=4
                )
                
                rules.append(rule)
        
        return rules
    
    def _generate_spatial_rules(self, experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """生成空间规律"""
        rules = []
        
        # 按距离分组分析
        distance_groups = defaultdict(list)
        for exp in experiences:
            distance_range = self._get_distance_range(exp.characteristics.distance)
            distance_groups[distance_range].append(exp)
        
        for distance_range, group_experiences in distance_groups.items():
            if len(group_experiences) >= 3:
                # 分析该距离范围内的最佳动作
                action_success_rates = defaultdict(list)
                for exp in group_experiences:
                    act_val = exp.action.value if exp.action and hasattr(exp.action, 'value') else 'unknown'
                    action_success_rates[act_val].append(exp.result.success)
                
                best_action = None
                best_success_rate = 0
                
                for action, successes in action_success_rates.items():
                    success_rate = sum(successes) / len(successes)
                    if success_rate > best_success_rate:
                        best_success_rate = success_rate
                        best_action = action
                
                if best_action and best_success_rate > 0.6:
                    rule_id = f"spatial_{distance_range}_{best_action}_{int(time.time() * 1000) % 10000}"
                    
                    conditions = {
                        'distance_range': distance_range,
                        'spatial_context': 'distance_based'
                    }
                    
                    predictions = {
                        'recommended_action': best_action,
                        'expected_success_rate': best_success_rate
                    }
                    
                    rule = CandidateRule(
                        rule_id=rule_id,
                        rule_type=RuleType.SPATIAL,
                        pattern=f"在{distance_range}距离范围内，{best_action}是最佳选择",
                        conditions=conditions,
                        predictions=predictions,
                        confidence=best_success_rate,
                        complexity=2
                    )
                    
                    rules.append(rule)
        
        return rules
    
    def _generate_tool_effectiveness_rules(self, experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """生成工具效用规律"""
        rules = []
        
        # 🔧 按工具-目标组合分组分析
        tool_target_combinations = defaultdict(list)
        tool_environment_combinations = defaultdict(list)
        
        for exp in experiences:
            if exp.is_tool_usage():  # 仅处理工具使用记录
                # 工具-目标组合 - 修复：使用兼容的方式获取工具-目标键
                tool_target_key = self._get_tool_target_key_v3(exp)
                if tool_target_key:
                    tool_target_combinations[tool_target_key].append(exp)
                
                # 工具-环境组合 - 修复：使用兼容的方式获取值
                tool_value = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
                env_value = exp.environment.value if exp.environment and hasattr(exp.environment, 'value') else 'unknown'
                tool_env_key = f"{tool_value}_{env_value}"
                tool_environment_combinations[tool_env_key].append(exp)
        
        # === 生成工具-目标匹配规律 ===
        for combination_key, combo_experiences in tool_target_combinations.items():
            if len(combo_experiences) >= 1:  # 🔥 降低阈值：最少1次经验
                try:
                    tool_type, target_type = combination_key.split('_', 1)  # 只分割第一个下划线
                except ValueError:
                    # 如果分割失败，跳过此组合
                    continue
                
                # 计算效果统计
                total_attempts = len(combo_experiences)
                successful_attempts = sum(1 for exp in combo_experiences if self._get_result_success_v3(exp))
                success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0.0
                
                # 计算平均效果值
                avg_effectiveness = 0.0
                effectiveness_count = 0
                for exp in combo_experiences:
                    # 修复：兼容V3结果格式
                    tool_eff = self._get_tool_effectiveness_v3(exp)
                    if tool_eff is not None:
                        avg_effectiveness += tool_eff
                        effectiveness_count += 1
                
                if effectiveness_count > 0:
                    avg_effectiveness /= effectiveness_count
                else:
                    avg_effectiveness = success_rate  # 回退到成功率
                
                # 效果分类
                if avg_effectiveness >= 0.8:
                    effectiveness_category = "高效"
                    effect_level = "high"
                elif avg_effectiveness >= 0.6:
                    effectiveness_category = "中效"
                    effect_level = "medium"
                elif avg_effectiveness >= 0.4:
                    effectiveness_category = "低效"
                    effect_level = "low"
                else:
                    effectiveness_category = "无效"
                    effect_level = "ineffective"
                
                # 🎯 创建工具效用规律
                rule_text = f"工具{tool_type.capitalize()}对{target_type}的效果是{effectiveness_category}"
                rule_id = f"tool_effectiveness_{tool_type}_{target_type}_{effect_level}_{int(time.time())}"
                
                conditions = {
                    'tool_type': tool_type,
                    'target_type': target_type,
                    'context': 'tool_usage'
                }
                
                predictions = {
                    'effectiveness': avg_effectiveness,
                    'success_rate': success_rate,
                    'recommended': avg_effectiveness >= 0.6,
                    'effect_category': effectiveness_category
                }
                
                rule = CandidateRule(
                    rule_id=rule_id,
                    rule_type=RuleType.TOOL_EFFECTIVENESS,
                    pattern=rule_text,
                    conditions=conditions,
                    predictions=predictions,
                    confidence=min(0.9, success_rate + 0.1),
                    complexity=1
                )
                
                # 设置证据信息
                rule.evidence.total_tests = total_attempts
                rule.evidence.successful_tests = successful_attempts
                
                rules.append(rule)
                
                if self.logger:
                    self.logger.log(f"🔧 生成工具效用规律: {rule_text} (效果:{avg_effectiveness:.3f}, 证据:{total_attempts}次)")
        
        # === 生成工具环境适应性规律 ===
        for combination_key, combo_experiences in tool_environment_combinations.items():
            if len(combo_experiences) >= 1:  # 🔥 降低阈值：最少1次经验
                try:
                    tool_type, env_type = combination_key.split('_', 1)  # 只分割第一个下划线
                except ValueError:
                    continue
                
                success_rate = sum(1 for exp in combo_experiences if self._get_result_success_v3(exp)) / len(combo_experiences)
                
                if success_rate >= 0.5:  # 🔥 降低阈值：中等适应性
                    rule_text = f"工具{tool_type.capitalize()}在{env_type}环境中表现良好"
                    
                    rule_id = f"tool_environment_{tool_type}_{env_type}_good_{int(time.time())}"
                    
                    conditions = {
                        'tool_type': tool_type,
                        'environment': env_type,
                        'context': 'environmental_adaptation'
                    }
                    
                    predictions = {
                        'success_rate': success_rate,
                        'environmental_fit': 'good',
                        'recommended_environment': env_type
                    }
                    
                    rule = CandidateRule(
                        rule_id=rule_id,
                        rule_type=RuleType.TOOL_EFFECTIVENESS,
                        pattern=rule_text,
                        conditions=conditions,
                        predictions=predictions,
                        confidence=success_rate,
                        complexity=2
                    )
                    
                    # 设置证据信息
                    rule.evidence.total_tests = len(combo_experiences)
                    rule.evidence.successful_tests = int(success_rate * len(combo_experiences))
                    
                    rules.append(rule)
        
        if self.logger and rules:
            self.logger.log(f"🔧 工具效用规律生成完成: 共{len(rules)}条规律")
        
        return rules
    
    def _get_tool_target_key_v3(self, exp) -> Optional[str]:
        """V3兼容：获取工具-目标键"""
        try:
            # 获取工具值
            tool_value = exp.tool.value if exp.tool and hasattr(exp.tool, 'value') else 'none'
            
            # 获取对象值
            object_value = exp.object.value if hasattr(exp.object, 'value') else getattr(exp.object, "content", getattr(exp.object, "name", str(exp.object)))
            
            # 清理值（移除特殊字符）
            tool_clean = tool_value.replace(" ", "_").replace("-", "_").lower()
            object_clean = object_value.replace(" ", "_").replace("-", "_").lower()
            
            return f"{tool_clean}_{object_clean}"
        except Exception as e:
            if self.logger:
                self.logger.log(f"🔧 获取工具-目标键失败: {str(e)}")
            return None
    
    def _get_result_success_v3(self, exp) -> bool:
        """V3兼容：获取结果成功状态"""
        try:
            # 尝试多种方式获取成功状态
            if hasattr(exp.result, 'success'):
                return exp.result.success
            elif hasattr(exp.result, 'content'):
                content = str(getattr(exp.result, "content", getattr(exp.result, "name", str(exp.result)))).lower()
                return "成功" in content or "success" in content
            else:
                return False
        except Exception:
            return False
    
    def _get_tool_effectiveness_v3(self, exp) -> Optional[float]:
        """V3兼容：获取工具效果值"""
        try:
            # 尝试从结果中获取工具效果
            if hasattr(exp.result, 'tool_effectiveness') and exp.result.tool_effectiveness is not None:
                return exp.result.tool_effectiveness
            elif hasattr(exp.result, 'reward'):
                # 基于奖励值估算效果
                reward = exp.result.reward
                if reward > 0:
                    return min(1.0, reward / 10.0)  # 标准化到0-1
                else:
                    return max(0.0, 0.5 + reward / 20.0)  # 负奖励转换
            else:
                # 基于成功状态给默认值
                return 0.8 if self._get_result_success_v3(exp) else 0.2
        except Exception:
            return None
    
    def pruning_phase(self) -> List[str]:
        """剪枝阶段：移除低质量或过时的规律"""
        try:
            # === 强化内存管理的剪枝策略 ===
            pruned_rule_ids = []
            current_time = time.time()
            
            # 计算内存压力
            self._check_memory_pressure()
            
            # 根据内存压力调整剪枝策略
            if self.memory_pressure_level > 0.8:
                # 高内存压力：更激进的剪枝
                confidence_threshold = self.config['pruning_confidence_threshold'] * 1.5
                age_threshold = self.config['pruning_age_threshold'] * 0.5
            elif self.memory_pressure_level > 0.6:
                # 中等内存压力：标准剪枝
                confidence_threshold = self.config['pruning_confidence_threshold']
                age_threshold = self.config['pruning_age_threshold']
            else:
                # 低内存压力：保守剪枝
                confidence_threshold = self.config['pruning_confidence_threshold'] * 0.5
                age_threshold = self.config['pruning_age_threshold'] * 2
            
            # 候选规律剪枝
            rules_to_prune = []
            for rule_id, rule in self.candidate_rules.items():
                should_prune = False
                prune_reason = ""
                
                # 置信度过低
                if rule.confidence < confidence_threshold:
                    should_prune = True
                    prune_reason = f"置信度过低 ({rule.confidence:.3f} < {confidence_threshold:.3f})"
                
                # 规律过于陈旧且未被激活
                rule_age = current_time - rule.birth_time
                if rule_age > age_threshold and rule.activation_count == 0:
                    should_prune = True
                    prune_reason = f"规律陈旧且未激活 (年龄: {rule_age:.0f}s)"
                
                # 矛盾证据过多
                if rule.evidence.contradicting_evidence_ratio > self.config['contradicting_evidence_threshold']:
                    should_prune = True
                    prune_reason = f"矛盾证据过多 ({rule.evidence.contradicting_evidence_ratio:.2f})"
                
                # 质量分数过低
                quality_score = rule.calculate_quality_score()
                if quality_score < 0.1:
                    should_prune = True
                    prune_reason = f"质量分数过低 ({quality_score:.3f})"
                
                # LRU：长期未访问且内存压力大
                if self.memory_pressure_level > 0.7:
                    last_access = self.lru_access_times.get(rule_id, rule.birth_time)
                    if current_time - last_access > age_threshold * 0.5:
                        should_prune = True
                        prune_reason = f"长期未访问 ({current_time - last_access:.0f}s)"
                
                if should_prune:
                    rules_to_prune.append((rule_id, prune_reason))
            
            # 执行剪枝
            for rule_id, reason in rules_to_prune:
                if rule_id in self.candidate_rules:
                    pruned_rule = self.candidate_rules.pop(rule_id)
                    self.pruned_rules[rule_id] = pruned_rule
                    self.pruning_history.append((current_time, rule_id, reason))
                    pruned_rule_ids.append(rule_id)
                    self.total_rules_pruned += 1
                    
                    # 清理相关数据
                    if rule_id in self.lru_access_times:
                        del self.lru_access_times[rule_id]
            
            # 已验证规律的剪枝（更保守）
            validated_rules_to_prune = []
            for rule_id, rule in self.validated_rules.items():
                # 只有在极端情况下才剪枝已验证规律
                if self.memory_pressure_level > 0.9:
                    quality_score = rule.calculate_quality_score()
                    if quality_score < 0.3 or rule.confidence < 0.2:
                        validated_rules_to_prune.append((rule_id, "内存压力过大且质量低"))
            
            for rule_id, reason in validated_rules_to_prune:
                if rule_id in self.validated_rules:
                    pruned_rule = self.validated_rules.pop(rule_id)
                    self.pruned_rules[rule_id] = pruned_rule
                    self.pruning_history.append((current_time, rule_id, reason))
                    pruned_rule_ids.append(rule_id)
                    self.total_rules_pruned += 1
                    
                    if rule_id in self.lru_access_times:
                        del self.lru_access_times[rule_id]
            
            # 限制已剪枝规律的数量（避免无限增长）
            if len(self.pruned_rules) > 200:
                # 保留最近的100个剪枝规律
                sorted_pruned = sorted(
                    self.pruned_rules.items(),
                    key=lambda x: x[1].birth_time,
                    reverse=True
                )
                self.pruned_rules = dict(sorted_pruned[:100])
            
            if self.logger and pruned_rule_ids:
                self.logger.log(f"剪枝阶段移除 {len(pruned_rule_ids)} 个规律")
            
            return pruned_rule_ids
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"剪枝阶段失败: {str(e)}")
            return []
    
    def _check_memory_pressure(self):
        """检查和计算内存压力级别"""
        try:
            total_rules = len(self.candidate_rules) + len(self.validated_rules)
            
            # 计算内存使用率
            memory_usage_ratio = total_rules / self.max_total_rules
            
            # 计算各类规律的使用率
            candidate_usage_ratio = len(self.candidate_rules) / self.max_candidate_rules
            validated_usage_ratio = len(self.validated_rules) / self.max_validated_rules
            
            # 综合计算内存压力级别
            self.memory_pressure_level = max(memory_usage_ratio, candidate_usage_ratio, validated_usage_ratio)
            
            # 记录高压力情况
            if self.memory_pressure_level > 0.8 and self.logger:
                self.logger.log(f"高内存压力: {self.memory_pressure_level:.2f} "
                              f"(总规律: {total_rules}/{self.max_total_rules}, "
                              f"候选: {len(self.candidate_rules)}/{self.max_candidate_rules}, "
                              f"已验证: {len(self.validated_rules)}/{self.max_validated_rules})")
        
        except Exception as e:
            if self.logger:
                self.logger.log(f"内存压力检查失败: {str(e)}")
            self.memory_pressure_level = 0.0
    
    def _perform_memory_cleanup(self):
        """执行内存清理"""
        try:
            if self.logger:
                self.logger.log("开始执行内存清理...")
            
            initial_count = len(self.candidate_rules) + len(self.validated_rules)
            
            # 1. 清理最少使用的候选规律
            self._cleanup_least_used_candidates(cleanup_ratio=0.3)
            
            # 2. 清理低质量的已验证规律
            self._cleanup_low_quality_validated(cleanup_ratio=0.2)
            
            # 3. 清理过期的剪枝规律
            self._cleanup_old_pruned_rules()
            
            # 4. 清理过期的LRU记录
            self._cleanup_lru_records()
            
            final_count = len(self.candidate_rules) + len(self.validated_rules)
            cleaned_count = initial_count - final_count
            
            if self.logger:
                self.logger.log(f"内存清理完成，释放 {cleaned_count} 个规律")
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"内存清理失败: {str(e)}")
    
    def _cleanup_least_used_candidates(self, cleanup_ratio=0.2):
        """清理最少使用的候选规律"""
        if not self.candidate_rules:
            return
        
        cleanup_count = max(1, int(len(self.candidate_rules) * cleanup_ratio))
        
        # 按照LRU和质量分数排序
        candidates_with_scores = []
        current_time = time.time()
        
        for rule_id, rule in self.candidate_rules.items():
            last_access = self.lru_access_times.get(rule_id, rule.birth_time)
            access_score = 1.0 / (current_time - last_access + 1)  # 越近访问分数越高
            quality_score = rule.calculate_quality_score()
            combined_score = access_score * 0.6 + quality_score * 0.4
            
            candidates_with_scores.append((rule_id, combined_score))
        
        # 按分数排序，移除分数最低的
        candidates_with_scores.sort(key=lambda x: x[1])
        
        for rule_id, _ in candidates_with_scores[:cleanup_count]:
            if rule_id in self.candidate_rules:
                removed_rule = self.candidate_rules.pop(rule_id)
                self.pruned_rules[rule_id] = removed_rule
                
                if rule_id in self.lru_access_times:
                    del self.lru_access_times[rule_id]
                
                self.total_rules_pruned += 1
    
    def _cleanup_low_quality_validated(self, cleanup_ratio=0.1):
        """清理低质量的已验证规律"""
        if not self.validated_rules:
            return
        
        cleanup_count = max(1, int(len(self.validated_rules) * cleanup_ratio))
        
        # 按质量分数排序
        validated_with_scores = []
        for rule_id, rule in self.validated_rules.items():
            quality_score = rule.calculate_quality_score()
            validated_with_scores.append((rule_id, quality_score))
        
        # 移除质量最低的
        validated_with_scores.sort(key=lambda x: x[1])
        
        for rule_id, score in validated_with_scores[:cleanup_count]:
            if score < 0.5:  # 只移除质量确实很低的
                if rule_id in self.validated_rules:
                    removed_rule = self.validated_rules.pop(rule_id)
                    self.pruned_rules[rule_id] = removed_rule
                    
                    if rule_id in self.lru_access_times:
                        del self.lru_access_times[rule_id]
                    
                    self.total_rules_pruned += 1
    
    def _cleanup_old_pruned_rules(self):
        """清理过期的剪枝规律"""
        if len(self.pruned_rules) > 100:
            # 只保留最近100个剪枝规律
            sorted_pruned = sorted(
                self.pruned_rules.items(),
                key=lambda x: x[1].birth_time,
                reverse=True
            )
            self.pruned_rules = dict(sorted_pruned[:100])
    
    def _cleanup_lru_records(self):
        """清理过期的LRU记录"""
        current_time = time.time()
        expired_records = []
        
        for rule_id, last_access in self.lru_access_times.items():
            # 如果规律已不存在，或者很久未访问，清理记录
            if (rule_id not in self.candidate_rules and 
                rule_id not in self.validated_rules) or \
               (current_time - last_access > 86400):  # 24小时未访问
                expired_records.append(rule_id)
        
        for rule_id in expired_records:
            del self.lru_access_times[rule_id]
    
    def _update_lru_access(self, rule_id: str):
        """更新LRU访问时间"""
        self.lru_access_times[rule_id] = time.time()
    
    def get_applicable_rules(self, context: EOCATR_Tuple) -> List[CandidateRule]:
        """获取适用于给定上下文的规律"""
        applicable_rules = []
        
        # 检查已验证规律
        for rule_id, rule in self.validated_rules.items():
            if self._is_rule_applicable(rule, context):
                applicable_rules.append(rule)
                self._update_lru_access(rule_id)  # 更新访问时间
        
        # 检查高置信度的候选规律
        for rule_id, rule in self.candidate_rules.items():
            if (rule.confidence > 0.6 and 
                self._is_rule_applicable(rule, context)):
                applicable_rules.append(rule)
                self._update_lru_access(rule_id)  # 更新访问时间
        
        # 按质量得分排序
        applicable_rules.sort(key=lambda r: r.calculate_quality_score(), reverse=True)
        
        return applicable_rules
    
    def validation_phase(self, new_experiences: List[EOCATR_Tuple]) -> List[str]:
        """验证阶段 - 增强版本"""
        if not new_experiences:
            # 即使无新经验，也进行自动晋升检查
            auto_ids = self._auto_promotion_check()
            if auto_ids and self.logger:
                self.logger.log(f"⚡ 自动晋升: {len(auto_ids)} 个规律基于重复出现与置信度被提升")
            return auto_ids
        
        validated_rule_ids = []
        
        try:
            if self.logger:
                self.logger.log(f"📊 BMP验证阶段开始: {len(new_experiences)}个新经验, {len(self.candidate_rules)}个候选规律")
            
            # 对每个候选规律进行验证
            for rule_id, rule in list(self.candidate_rules.items()):
                try:
                    # 使用新经验验证规律
                    validation_result = self._validate_rule_with_experiences(rule, new_experiences)
                    
                    if validation_result['total_applicable'] > 0:
                        # 更新规律基于验证结果
                        self._update_rule_based_on_validation(rule, validation_result)
                        
                        # 如果验证成功且置信度提高，移到已验证规律
                        success_rate_threshold = self.config.get('validation_success_rate_threshold', 0.5)
                        if (validation_result['success_rate'] >= success_rate_threshold and 
                            rule.confidence >= self.config.get('validation_confidence_threshold', 0.3)):
                            
                            self.validated_rules[rule_id] = rule
                            del self.candidate_rules[rule_id]
                            validated_rule_ids.append(rule_id)
                            
                            if self.logger:
                                self.logger.log(f"✅ 规律验证成功: {rule_id[:8]} (置信度: {rule.confidence:.3f})")
                        
                except Exception as e:
                    if self.logger:
                        self.logger.log(f"❌ 规律验证失败: {rule_id[:8]} - {str(e)}")
                    continue
            
            if self.logger:
                self.logger.log(f"📊 BMP验证阶段完成: 验证了{len(validated_rule_ids)}个规律")
            
            # 验证后补充自动晋升
            auto_ids = self._auto_promotion_check()
            if auto_ids:
                validated_rule_ids.extend(auto_ids)
                if self.logger:
                    self.logger.log(f"⚡ 自动晋升: 额外提升 {len(auto_ids)} 个规律")
            return validated_rule_ids
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ BMP验证阶段异常: {str(e)}")
            return []

    def _auto_promotion_check(self) -> List[str]:
        """基于重复出现与置信度的自动晋升为正式规律"""
        promoted: List[str] = []
        try:
            if not self.config.get('auto_promotion_enabled', True):
                return promoted
            repeat_threshold = self.config.get('auto_promote_repeat_threshold', 4)
            conf_threshold = self.config.get('auto_promote_confidence_threshold', 0.5)
            max_contra_ratio = self.config.get('auto_promote_max_contradiction_ratio', 0.5)

            for rule_id, rule in list(self.candidate_rules.items()):
                try:
                    if rule.activation_count < repeat_threshold:
                        continue
                    if rule.confidence < conf_threshold:
                        continue
                    supp = len(getattr(rule.evidence, 'supporting_experiences', []) or [])
                    contra = len(getattr(rule.evidence, 'contradicting_experiences', []) or [])
                    total_ev = supp + contra
                    contra_ratio = (contra / total_ev) if total_ev > 0 else 0.0
                    if contra_ratio > max_contra_ratio:
                        continue

                    # 晋升
                    self.validated_rules[rule_id] = rule
                    if rule_id in self.candidate_rules:
                        del self.candidate_rules[rule_id]
                    rule.status = 'validated'
                    promoted.append(rule_id)
                    if self.logger:
                        self.logger.log(f"✅ 规则自动晋升: {rule_id[:8]} (activation:{rule.activation_count}, confidence:{rule.confidence:.3f}, contra_ratio:{contra_ratio:.2f})")
                except Exception as inner_e:
                    if self.logger:
                        self.logger.log(f"⚠️ 自动晋升检查异常: {rule_id[:8]} - {str(inner_e)}")
                    continue
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 自动晋升流程异常: {str(e)}")
        return promoted
    def _validate_rule_with_experiences(self, rule: CandidateRule, 
                                       experiences: List[EOCATR_Tuple]) -> Dict[str, Any]:
        """使用经验验证规律"""
        validation_result = {
            'matches': 0,
            'predictions_correct': 0,
            'predictions_wrong': 0,
            'total_applicable': 0,
            'success_rate': 0.0
        }
        
        for exp in experiences:
            # 检查规律是否适用于此经验
            if self._is_rule_applicable(rule, exp):
                validation_result['total_applicable'] += 1
                validation_result['matches'] += 1
                
                # 检查预测是否正确
                if self._check_rule_prediction(rule, exp):
                    validation_result['predictions_correct'] += 1
                else:
                    validation_result['predictions_wrong'] += 1
            else:
                # 轻度泛化：若action、environment匹配但tool不同，给予部分匹配（放宽验证困难）
                try:
                    cond = rule.conditions if isinstance(rule.conditions, dict) else {}
                    act_ok = ('action' not in cond) or (cond.get('action') == getattr(exp.action, 'value', None))
                    env_ok = ('environment' not in cond) or (cond.get('environment') == getattr(exp.environment, 'value', None))
                    if act_ok and env_ok:
                        # 作为弱证据，计入总样本但不加正确计数
                        validation_result['total_applicable'] += 1
                except Exception:
                    pass
        
        # 计算成功率（避免除零）
        if validation_result['total_applicable'] > 0:
            total = validation_result['predictions_correct'] + validation_result['predictions_wrong']
            if total > 0:
                validation_result['success_rate'] = validation_result['predictions_correct'] / total
            else:
                # 没有对错记录但存在弱匹配时，给予最低通过可能的基线（可调）
                validation_result['success_rate'] = 0.4 if validation_result['total_applicable'] > 0 else 0.0
        return validation_result
    
    def _is_rule_applicable(self, rule: CandidateRule, experience: EOCATR_Tuple) -> bool:
        """检查规律是否适用于给定经验（修复：基于 rule.conditions 字典判断）"""
        # 优先使用结构化的 conditions 字典；若不可用则回退为空
        conditions_dict = rule.conditions if isinstance(rule.conditions, dict) else {}

        # 提供安全取值函数，兼容枚举/符号元素
        def _safe_value(x):
            return getattr(x, 'value', getattr(x, 'content', x))

        # 检查基本条件：对象类别/动作/环境
        if 'object_category' in conditions_dict:
            if _safe_value(experience.object_category) != conditions_dict['object_category']:
                return False

        if 'action' in conditions_dict:
            if _safe_value(experience.action) != conditions_dict['action']:
                return False

        if 'environment' in conditions_dict:
            if _safe_value(experience.environment) != conditions_dict['environment']:
                return False

        # 兼容增强BMP的简写键位（E/O/C/A/T）
        shorthand_map = {
            'E': _safe_value(experience.environment),
            'O': _safe_value(experience.object_category),
            'A': _safe_value(experience.action),
            # 'C' 特征集合下方统一处理
            'T': _safe_value(getattr(experience, 'tool', None))
        }
        for key, expected in list(conditions_dict.items()):
            if key in shorthand_map and expected is not None:
                if shorthand_map[key] != expected:
                    return False

        # 检查特征条件与阈值条件
        # 支持 C 为 dict 或 list 的情况：随机抽取一个特征作为代表匹配
        if 'C' in conditions_dict and isinstance(conditions_dict['C'], (dict, list)):
            c_pool = []
            if isinstance(conditions_dict['C'], dict):
                c_pool = list(conditions_dict['C'].items())
            else:
                # list 中每个元素可以是 (name, value) 或 {'name': v}
                for item in conditions_dict['C']:
                    if isinstance(item, tuple) and len(item) == 2:
                        c_pool.append(item)
                    elif isinstance(item, dict) and len(item) == 1:
                        k, v = list(item.items())[0]
                        c_pool.append((k, v))
            if c_pool:
                k, v = random.choice(c_pool)
                exp_val = getattr(experience.characteristics, k, None)
                if exp_val != v:
                    return False

        for cond_name, cond_value in conditions_dict.items():
            if cond_name.startswith('characteristic_'):
                char_name = cond_name.replace('characteristic_', '')
                exp_char_value = getattr(experience.characteristics, char_name, None)
                if exp_char_value != cond_value:
                    return False

            elif cond_name.endswith('_threshold'):
                char_name = cond_name.replace('_threshold', '')
                exp_char_value = getattr(experience.characteristics, char_name, None)
                comparison = conditions_dict.get('comparison', 'greater_than')
                if exp_char_value is not None:
                    if comparison == 'greater_than' and exp_char_value <= cond_value:
                        return False
                    if comparison == 'less_than' and exp_char_value >= cond_value:
                        return False

        # 未设置任何限制条件时，认为适用
        return True
    
    def _check_rule_prediction(self, rule: CandidateRule, experience: EOCATR_Tuple) -> bool:
        """检查规律预测是否正确"""
        predictions = rule.predictions
        
        # 检查成功预测
        if 'expected_success' in predictions:
            if predictions['expected_success'] != experience.result.success:
                return False
        
        # 检查奖励预测（允许一定误差）
        if 'expected_reward' in predictions:
            expected_reward = predictions['expected_reward']
            actual_reward = experience.result.reward
            if abs(expected_reward - actual_reward) > abs(expected_reward) * 0.3:  # 30%误差容忍
                return False
        
        # 检查推荐动作
        if 'recommended_action' in predictions:
            if predictions['recommended_action'] != experience.action.value:
                return False
        
        return True
    
    def _update_rule_based_on_validation(self, rule: CandidateRule, validation_result: Dict[str, Any]):
        """基于验证结果更新规律"""
        if validation_result['total_applicable'] > 0:
            # 更新证据计数
            rule.evidence.total_tests += validation_result['total_applicable']
            rule.evidence.successful_tests += validation_result['predictions_correct']
            rule.evidence.last_tested = time.time()
            
            # 更新supporting_experiences列表（修复：确保支持经验被正确记录）
            if validation_result['predictions_correct'] > 0:
                # 为每个成功预测添加支持经验记录
                for i in range(validation_result['predictions_correct']):
                    experience_id = f"validation_{int(time.time() * 1000)}_{i}"
                    if experience_id not in rule.evidence.supporting_experiences:
                        rule.evidence.supporting_experiences.append(experience_id)
            
            # 更新置信度（修复：使用更合理的更新算法）
            if validation_result['total_applicable'] > 0:
                success_rate = validation_result['predictions_correct'] / validation_result['total_applicable']
                # 贝叶斯更新：当有足够证据时逐渐稳定置信度
                evidence_weight = min(validation_result['total_applicable'] / 10.0, 0.5)
                rule.confidence = rule.confidence * (1 - evidence_weight) + success_rate * evidence_weight
                
                # 确保置信度在合理范围内
                rule.confidence = max(0.0, min(1.0, rule.confidence))
            
            # 更新精确度和召回率
            total_predictions = validation_result['predictions_correct'] + validation_result['predictions_wrong']
            if total_predictions > 0:
                rule.precision = validation_result['predictions_correct'] / total_predictions
            
            # 激活计数
            rule.activation_count += validation_result['matches']
            rule.last_activation = time.time()
            
            # 更新效用值（新增：基于验证结果）
            if validation_result['predictions_correct'] > 0:
                rule.utility = min(1.0, rule.utility + 0.1 * validation_result['predictions_correct'])
    
    # 工具方法
    def _extract_common_characteristics(self, experiences: List[EOCATR_Tuple]) -> Dict[str, Any]:
        """提取公共特征"""
        if not experiences:
            return {}
        
        common_chars = {}
        char_attrs = ['edible', 'poisonous', 'dangerous', 'health_state', 'size', 'accessibility']
        
        for attr in char_attrs:
            values = []
            for exp in experiences:
                value = getattr(exp.characteristics, attr, None)
                if value is not None:
                    values.append(value)
            
            if values:
                # 如果所有值相同，则为公共特征
                if len(set(values)) == 1:
                    common_chars[attr] = values[0]
                # 对于数值类型，计算平均值
                elif all(isinstance(v, (int, float)) for v in values):
                    common_chars[attr] = sum(values) / len(values)
        
        return common_chars
    
    def _extract_common_results(self, experiences: List[EOCATR_Tuple]) -> Dict[str, Any]:
        """提取公共结果"""
        if not experiences:
            return {}
        
        common_results = {}
        
        # 成功率
        successes = [exp.result.success for exp in experiences]
        common_results['success_rate'] = sum(successes) / len(successes)
        
        # 平均奖励
        rewards = [exp.result.reward for exp in experiences if exp.result.reward is not None]
        if rewards:
            common_results['average_reward'] = sum(rewards) / len(rewards)
        
        # 状态变化
        for change_type in ['hp_change', 'food_change', 'water_change']:
            changes = [getattr(exp.result, change_type, 0) for exp in experiences]
            if any(c != 0 for c in changes):
                common_results[change_type] = sum(changes) / len(changes)
        
        return common_results
    
    def _calculate_optimal_threshold(self, positive_values: List[float], 
                                   negative_values: List[float]) -> Optional[float]:
        """计算最优分离阈值"""
        if not positive_values or not negative_values:
            return None
        
        all_values = sorted(positive_values + negative_values)
        best_threshold = None
        best_separation = 0
        
        # 尝试每个可能的分割点
        for i in range(1, len(all_values)):
            threshold = (all_values[i-1] + all_values[i]) / 2
            
            # 计算分离效果
            correct_positive = sum(1 for v in positive_values if v > threshold)
            correct_negative = sum(1 for v in negative_values if v <= threshold)
            total_correct = correct_positive + correct_negative
            total_samples = len(positive_values) + len(negative_values)
            
            separation = total_correct / total_samples
            
            if separation > best_separation:
                best_separation = separation
                best_threshold = threshold
        
        return best_threshold if best_separation > 0.7 else None
    
    def _get_distance_range(self, distance: float) -> str:
        """获取距离范围分类"""
        if distance <= 1:
            return "adjacent"
        elif distance <= 3:
            return "near"
        elif distance <= 7:
            return "medium"
        else:
            return "far"
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        return {
            'total_rules_generated': self.total_rules_generated,
            'total_rules_pruned': self.total_rules_pruned,
            'total_rules_validated': self.total_rules_validated,
            'current_candidate_rules': len(self.candidate_rules),
            'current_validated_rules': len(self.validated_rules),
            'current_pruned_rules': len(self.pruned_rules),
            'rule_types_distribution': self._get_rule_type_distribution(),
            'average_rule_confidence': self._get_average_confidence(),
            'quality_score_distribution': self._get_quality_score_distribution()
        }
    
    def _get_rule_type_distribution(self) -> Dict[str, int]:
        """获取规律类型分布"""
        distribution = defaultdict(int)
        
        for rule in self.candidate_rules.values():
            distribution[rule.rule_type.value] += 1
        
        for rule in self.validated_rules.values():
            distribution[rule.rule_type.value] += 1
        
        return dict(distribution)
    
    def _get_average_confidence(self) -> float:
        """获取平均置信度"""
        all_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
        if not all_rules:
            return 0.0
        
        return sum(rule.confidence for rule in all_rules) / len(all_rules)
    
    def _get_quality_score_distribution(self) -> Dict[str, int]:
        """获取质量得分分布"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        all_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
        
        for rule in all_rules:
            score = rule.calculate_quality_score()
            if score >= 0.7:
                distribution['high'] += 1
            elif score >= 0.4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution

    def get_all_validated_rules(self) -> List[CandidateRule]:
        """获取所有已验证的规律"""
        return list(self.validated_rules.values())
    
    def get_candidate_rules(self) -> List[CandidateRule]:
        """获取所有候选规律"""
        return list(self.candidate_rules.values())
    
    def get_all_rules(self) -> List[CandidateRule]:
        """获取所有规律（候选+已验证）"""
        return list(self.candidate_rules.values()) + list(self.validated_rules.values())
    
    def get_rule_count(self) -> Dict[str, int]:
        """获取规律数量统计"""
        return {
            'candidate_rules': len(self.candidate_rules),
            'validated_rules': len(self.validated_rules),
            'pruned_rules': len(self.pruned_rules),
            'total_rules': len(self.candidate_rules) + len(self.validated_rules)
        }

    # === 新增：规律持久化存储功能 ===
    
    def save_rules_to_file(self, filepath: str = None, include_pruned: bool = False) -> bool:
        """保存规律到文件"""
        try:
            import json
            import os
            from datetime import datetime
            
            if filepath is None:
                # 默认文件路径
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"bpm_rules_{timestamp}.json"
            
            # 准备要保存的数据
            save_data = {
                'metadata': {
                    'version': '1.0',
                    'timestamp': datetime.now().isoformat(),
                    'total_rules_generated': self.total_rules_generated,
                    'total_rules_pruned': self.total_rules_pruned,
                    'total_rules_validated': self.total_rules_validated,
                    'total_rules_merged': self.total_rules_merged,
                    'total_rules_rejected': self.total_rules_rejected
                },
                'config': self.config,
                'candidate_rules': self._serialize_rules(self.candidate_rules),
                'validated_rules': self._serialize_rules(self.validated_rules),
                'rule_fingerprints': list(self.rule_fingerprints),
                'rule_merge_history': self.rule_merge_history,
                'lru_access_times': self.lru_access_times
            }
            
            if include_pruned:
                save_data['pruned_rules'] = self._serialize_rules(self.pruned_rules)
                save_data['pruning_history'] = self.pruning_history
            
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            if self.logger:
                self.logger.log(f"规律已保存到文件: {filepath}")
                self.logger.log(f"保存了 {len(self.candidate_rules)} 个候选规律和 {len(self.validated_rules)} 个已验证规律")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"保存规律到文件失败: {str(e)}")
            return False
    
    def load_rules_from_file(self, filepath: str, merge_mode: str = 'replace') -> bool:
        """从文件加载规律
        
        Args:
            filepath: 文件路径
            merge_mode: 合并模式 ('replace', 'merge', 'append')
        """
        try:
            import json
            import os
            
            if not os.path.exists(filepath):
                if self.logger:
                    self.logger.log(f"文件不存在: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                load_data = json.load(f)
            
            # 检查版本兼容性
            metadata = load_data.get('metadata', {})
            version = metadata.get('version', '1.0')
            
            if version != '1.0':
                if self.logger:
                    self.logger.log(f"版本不兼容: {version} (期望: 1.0)")
                return False
            
            # 根据合并模式处理
            if merge_mode == 'replace':
                # 完全替换
                self.candidate_rules = self._deserialize_rules(load_data.get('candidate_rules', {}))
                self.validated_rules = self._deserialize_rules(load_data.get('validated_rules', {}))
                if 'pruned_rules' in load_data:
                    self.pruned_rules = self._deserialize_rules(load_data['pruned_rules'])
                
                # 恢复其他数据
                self.rule_fingerprints = set(load_data.get('rule_fingerprints', []))
                self.rule_merge_history = load_data.get('rule_merge_history', [])
                self.lru_access_times = load_data.get('lru_access_times', {})
                
                # 恢复统计数据
                self.total_rules_generated = metadata.get('total_rules_generated', 0)
                self.total_rules_pruned = metadata.get('total_rules_pruned', 0)
                self.total_rules_validated = metadata.get('total_rules_validated', 0)
                self.total_rules_merged = metadata.get('total_rules_merged', 0)
                self.total_rules_rejected = metadata.get('total_rules_rejected', 0)
                
            elif merge_mode == 'merge':
                # 智能合并（避免重复）
                loaded_candidate = self._deserialize_rules(load_data.get('candidate_rules', {}))
                loaded_validated = self._deserialize_rules(load_data.get('validated_rules', {}))
                
                merged_count = 0
                # 合并候选规律
                for rule_id, rule in loaded_candidate.items():
                    if not self._is_duplicate_rule(rule):
                        self.candidate_rules[rule_id] = rule
                        self.rule_fingerprints.add(self._generate_rule_fingerprint(rule))
                        merged_count += 1
                
                # 合并已验证规律
                for rule_id, rule in loaded_validated.items():
                    if not self._is_duplicate_rule(rule):
                        self.validated_rules[rule_id] = rule
                        self.rule_fingerprints.add(self._generate_rule_fingerprint(rule))
                        merged_count += 1
                
                if self.logger:
                    self.logger.log(f"智能合并完成，新增 {merged_count} 个规律")
                    
            elif merge_mode == 'append':
                # 简单追加（可能产生重复）
                loaded_candidate = self._deserialize_rules(load_data.get('candidate_rules', {}))
                loaded_validated = self._deserialize_rules(load_data.get('validated_rules', {}))
                
                self.candidate_rules.update(loaded_candidate)
                self.validated_rules.update(loaded_validated)
                
                # 重新生成指纹
                self.rule_fingerprints.clear()
                all_rules = list(self.candidate_rules.values()) + list(self.validated_rules.values())
                for rule in all_rules:
                    self.rule_fingerprints.add(self._generate_rule_fingerprint(rule))
            
            if self.logger:
                self.logger.log(f"规律已从文件加载: {filepath}")
                self.logger.log(f"当前有 {len(self.candidate_rules)} 个候选规律和 {len(self.validated_rules)} 个已验证规律")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"从文件加载规律失败: {str(e)}")
            return False
    
    def _serialize_rules(self, rules_dict: Dict[str, CandidateRule]) -> Dict[str, Dict]:
        """序列化规律字典"""
        serialized = {}
        
        for rule_id, rule in rules_dict.items():
            serialized[rule_id] = {
                'rule_id': rule.rule_id,
                'rule_type': rule.rule_type.value,
                'pattern': rule.pattern,
                'conditions': rule.condition_elements,
                'predictions': rule.predictions,
                'confidence': rule.confidence,
                'strength': rule.strength,
                'generalization': rule.generalization,
                'specificity': rule.specificity,
                'complexity': rule.complexity,
                'birth_time': rule.birth_time,
                'last_activation': rule.last_activation,
                'activation_count': rule.activation_count,
                'precision': rule.precision,
                'recall': rule.recall,
                'utility': rule.utility,
                'parent_rules': rule.parent_rules,
                'derived_rules': rule.derived_rules,
                'evidence': {
                    'supporting_experiences': rule.evidence.supporting_experiences,
                    'contradicting_experiences': rule.evidence.contradicting_experiences,
                    'total_tests': rule.evidence.total_tests,
                    'successful_tests': rule.evidence.successful_tests,
                    'last_tested': rule.evidence.last_tested,
                    'test_contexts': rule.evidence.test_contexts
                }
            }
        
        return serialized
    
    def _deserialize_rules(self, serialized_dict: Dict[str, Dict]) -> Dict[str, CandidateRule]:
        """反序列化规律字典"""
        rules_dict = {}
        
        for rule_id, rule_data in serialized_dict.items():
            try:
                # 重构规律证据
                evidence = RuleEvidence(
                    supporting_experiences=rule_data['evidence']['supporting_experiences'],
                    contradicting_experiences=rule_data['evidence']['contradicting_experiences'],
                    total_tests=rule_data['evidence']['total_tests'],
                    successful_tests=rule_data['evidence']['successful_tests'],
                    last_tested=rule_data['evidence']['last_tested'],
                    test_contexts=rule_data['evidence']['test_contexts']
                )
                
                # 重构规律对象
                rule = CandidateRule(
                    rule_id=rule_data['rule_id'],
                    rule_type=RuleType(rule_data['rule_type']),
                    pattern=rule_data['pattern'],
                    conditions=rule_data['conditions'],
                    predictions=rule_data['predictions'],
                    confidence=rule_data['confidence'],
                    strength=rule_data['strength'],
                    generalization=rule_data['generalization'],
                    specificity=rule_data['specificity'],
                    complexity=rule_data['complexity'],
                    evidence=evidence,
                    birth_time=rule_data['birth_time'],
                    last_activation=rule_data['last_activation'],
                    activation_count=rule_data['activation_count'],
                    precision=rule_data['precision'],
                    recall=rule_data['recall'],
                    utility=rule_data['utility'],
                    parent_rules=rule_data['parent_rules'],
                    derived_rules=rule_data['derived_rules']
                )
                
                rules_dict[rule_id] = rule
                
            except Exception as e:
                if self.logger:
                    self.logger.log(f"反序列化规律失败 {rule_id}: {str(e)}")
                continue
        
        return rules_dict 

    # ============================================================================
    # 系统性EOCATR规律生成器 (新增)
    # ============================================================================
    
    def generate_systematic_eocatr_rules(self, eocatr_matrix_config: Dict) -> List[CandidateRule]:
        """
        系统性生成EOCATR矩阵规律
        基于用户确认的组合策略：E-A-R, E-T-R, O-A-R, O-T-R, C-A-R, C-T-R
        
        Args:
            eocatr_matrix_config: EOCATR矩阵配置字典
            
        Returns:
            生成的系统性规律列表
        """
        if self.logger:
            self.logger.log("开始生成系统性EOCATR规律...")
        
        systematic_rules = []
        generation_start_time = time.time()
        
        try:
            # 1. 环境-行动-结果规律 (E-A-R)
            ear_rules = self._generate_ear_rules(eocatr_matrix_config)
            systematic_rules.extend(ear_rules)
            
            # 2. 环境-工具-结果规律 (E-T-R)  
            etr_rules = self._generate_etr_rules(eocatr_matrix_config)
            systematic_rules.extend(etr_rules)
            
            # 3. 对象-行动-结果规律 (O-A-R)
            oar_rules = self._generate_oar_rules(eocatr_matrix_config)
            systematic_rules.extend(oar_rules)
            
            # 4. 对象-工具-结果规律 (O-T-R)
            otr_rules = self._generate_otr_rules(eocatr_matrix_config)
            systematic_rules.extend(otr_rules)
            
            # 5. 属性-行动-结果规律 (C-A-R)
            car_rules = self._generate_car_rules(eocatr_matrix_config)
            systematic_rules.extend(car_rules)
            
            # 6. 属性-工具-结果规律 (C-T-R)
            ctr_rules = self._generate_ctr_rules(eocatr_matrix_config)
            systematic_rules.extend(ctr_rules)
            
            generation_time = time.time() - generation_start_time
            
            if self.logger:
                self.logger.log(f"BPM系统性生成了 {len(systematic_rules)} 条EOCATR基础规律")
                self.logger.log(f"  E-A-R规律: {len(ear_rules)}条")
                self.logger.log(f"  E-T-R规律: {len(etr_rules)}条")
                self.logger.log(f"  O-A-R规律: {len(oar_rules)}条")
                self.logger.log(f"  O-T-R规律: {len(otr_rules)}条")
                self.logger.log(f"  C-A-R规律: {len(car_rules)}条")
                self.logger.log(f"  C-T-R规律: {len(ctr_rules)}条")
                self.logger.log(f"生成耗时: {generation_time:.2f}秒")
            
            # 更新统计
            self.total_rules_generated += len(systematic_rules)
            
            return systematic_rules
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"系统性EOCATR规律生成失败: {str(e)}")
            return []

    def _generate_ear_rules(self, config: Dict) -> List[CandidateRule]:
        """生成环境-行动-结果规律"""
        rules = []
        environments = config.get('environments', ['开阔地', '森林', '水域', '危险区域'])
        actions = config.get('actions', ['移动', '攻击', '采集', '观察', '逃跑'])
        results = config.get('results', ['成功', '失败', '获得奖励', '受到伤害'])
        
        for env in environments:
            for action in actions:
                for result in results:
                    # 智能置信度计算
                    confidence = self._calculate_intelligent_confidence(env, action, result, 'E-A-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.CONDITIONAL,
                        pattern=f"在{env}环境下执行{action}行动",
                        conditions={'environment': env, 'action': action},
                        predictions={'result': result},
                        confidence=confidence,  # 使用智能置信度
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _generate_etr_rules(self, config: Dict) -> List[CandidateRule]:
        """生成环境-工具-结果规律"""
        rules = []
        environments = config.get('environments', ['开阔地', '森林', '水域'])
        tools = config.get('tools', ['无工具', '石头', '木棍', '陷阱'])
        results = config.get('results', ['成功', '失败', '效率提升', '资源消耗'])
        
        for env in environments:
            for tool in tools:
                for result in results:
                    confidence = self._calculate_intelligent_confidence(env, tool, result, 'E-T-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.TOOL_EFFECTIVENESS,
                        pattern=f"在{env}环境下使用{tool}工具",
                        conditions={'environment': env, 'tool': tool},
                        predictions={'result': result},
                        confidence=confidence,
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _generate_oar_rules(self, config: Dict) -> List[CandidateRule]:
        """生成对象-行动-结果规律"""
        rules = []
        objects = config.get('objects', ['草莓', '蘑菇', '老虎', '兔子', '野猪', '黑熊'])
        actions = config.get('actions', ['采集', '攻击', '逃避', '观察', '跟踪'])
        results = config.get('results', ['获得食物', '受到伤害', '成功逃脱', '发现信息'])
        
        for obj in objects:
            for action in actions:
                for result in results:
                    confidence = self._calculate_intelligent_confidence(obj, action, result, 'O-A-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.CAUSAL,
                        pattern=f"对{obj}对象执行{action}行动",
                        conditions={'object': obj, 'action': action},
                        predictions={'result': result},
                        confidence=confidence,
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _generate_otr_rules(self, config: Dict) -> List[CandidateRule]:
        """生成对象-工具-结果规律"""
        rules = []
        objects = config.get('objects', ['草莓', '蘑菇', '老虎', '兔子'])
        tools = config.get('tools', ['无工具', '石头', '木棍', '陷阱'])
        results = config.get('results', ['收集成功', '攻击生效', '工具损坏', '提升效率'])
        
        for obj in objects:
            for tool in tools:
                for result in results:
                    confidence = self._calculate_intelligent_confidence(obj, tool, result, 'O-T-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.TOOL_EFFECTIVENESS,
                        pattern=f"使用{tool}工具处理{obj}对象",
                        conditions={'object': obj, 'tool': tool},
                        predictions={'result': result},
                        confidence=confidence,
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _generate_car_rules(self, config: Dict) -> List[CandidateRule]:
        """生成属性-行动-结果规律"""
        rules = []
        
        # 支持多维特征分解
        attributes = config.get('attributes', [])
        if not attributes:
            # 默认特征集合
            attributes = [
                '距离近', '距离中', '距离远',
                '可食用', '有毒', '危险',
                '营养丰富', '营养一般', '营养缺乏',
                '血量高', '血量中', '血量低'
            ]
        
        actions = config.get('actions', ['移动', '攻击', '采集', '观察'])
        results = config.get('results', ['成功', '失败', '风险', '收益'])
        
        for attr in attributes:
            for action in actions:
                for result in results:
                    confidence = self._calculate_intelligent_confidence(attr, action, result, 'C-A-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.CONDITIONAL,
                        pattern=f"在{attr}属性下执行{action}行动",
                        conditions={'attribute': attr, 'action': action},
                        predictions={'result': result},
                        confidence=confidence,
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _generate_ctr_rules(self, config: Dict) -> List[CandidateRule]:
        """生成属性-工具-结果规律"""
        rules = []
        attributes = config.get('attributes', [
            '距离近', '距离远', '危险', '安全', '营养丰富', '血量低'
        ])
        tools = config.get('tools', ['无工具', '石头', '木棍', '陷阱'])
        results = config.get('results', ['效果增强', '风险降低', '效率提升', '资源节省'])
        
        for attr in attributes:
            for tool in tools:
                for result in results:
                    confidence = self._calculate_intelligent_confidence(attr, tool, result, 'C-T-R')
                    
                    rule = self._create_systematic_rule(
                        rule_type=RuleType.TOOL_EFFECTIVENESS,
                        pattern=f"在{attr}属性下使用{tool}工具",
                        conditions={'attribute': attr, 'tool': tool},
                        predictions={'result': result},
                        confidence=confidence,
                        complexity=1
                    )
                    rules.append(rule)
        
        return rules

    def _create_systematic_rule(self, rule_type: RuleType, pattern: str, 
                              conditions: Dict, predictions: Dict, 
                              confidence: float, complexity: int) -> CandidateRule:
        """创建系统性规律"""
        rule_id = f"SYS_{rule_type.value}_{hash(pattern) % 10000:04d}"
        
        rule = CandidateRule(
            rule_id=rule_id,
            rule_type=rule_type,
            pattern=pattern,
            conditions=conditions,
            predictions=predictions,
            confidence=confidence,
            complexity=complexity,
            birth_time=time.time()
        )
        
        return rule

    def _calculate_intelligent_confidence(self, element1: str, element2: str, result: str, combination_type: str) -> float:
        """
        智能计算规律的初始置信度
        基于元素组合的合理性评估
        """
        base_confidence = 0.3  # 基础置信度提升到0.3
        
        # 基于组合类型的调整
        type_multipliers = {
            'E-A-R': 0.4,     # 环境-行动组合较为直观
            'E-T-R': 0.35,    # 环境-工具组合中等合理
            'O-A-R': 0.45,    # 对象-行动组合最为直观
            'O-T-R': 0.4,     # 对象-工具组合较为合理
            'C-A-R': 0.35,    # 特征-行动组合需要更多验证
            'C-T-R': 0.35,    # 特征-工具组合需要更多验证
        }
        
        # 基于常识的合理性判断
        reasonableness_bonus = 0.0
        
        # 高合理性组合
        if any(combo in f"{element1}-{element2}-{result}" for combo in [
            "草莓-采集-获得食物", "老虎-攻击-受到伤害", "兔子-采集-获得食物",
            "森林-移动-成功", "危险区域-逃跑-成功逃脱", "距离近-攻击-成功"
        ]):
            reasonableness_bonus = 0.2
        
        # 中等合理性
        elif any(combo in f"{element1}-{element2}-{result}" for combo in [
            "蘑菇-采集-获得食物", "石头-攻击-攻击生效", "开阔地-移动-成功"
        ]):
            reasonableness_bonus = 0.1
        
        # 低合理性（潜在反常识组合）
        elif any(combo in f"{element1}-{element2}-{result}" for combo in [
            "老虎-采集", "草莓-攻击", "有毒-获得食物"
        ]):
            reasonableness_bonus = -0.1
        
        final_confidence = base_confidence + type_multipliers.get(combination_type, 0.3) + reasonableness_bonus
        
        # 确保置信度在合理范围内
        return max(0.2, min(0.8, final_confidence))

    def get_eocatr_generation_statistics(self) -> Dict[str, Any]:
        """获取EOCATR规律生成统计信息"""
        stats = self.get_statistics()
        
        # 统计系统性生成的规律
        systematic_rules = {
            'candidate': 0,
            'validated': 0,
            'by_type': {}
        }
        
        # 候选规律中的系统性规律
        for rule in self.candidate_rules.values():
            if rule.rule_id.startswith('SYS_'):
                systematic_rules['candidate'] += 1
                rule_type = rule.rule_type.value
                if rule_type not in systematic_rules['by_type']:
                    systematic_rules['by_type'][rule_type] = {'candidate': 0, 'validated': 0}
                systematic_rules['by_type'][rule_type]['candidate'] += 1
        
        # 已验证规律中的系统性规律
        for rule in self.validated_rules.values():
            if rule.rule_id.startswith('SYS_'):
                systematic_rules['validated'] += 1
                rule_type = rule.rule_type.value
                if rule_type not in systematic_rules['by_type']:
                    systematic_rules['by_type'][rule_type] = {'candidate': 0, 'validated': 0}
                systematic_rules['by_type'][rule_type]['validated'] += 1
        
        stats['systematic_eocatr_rules'] = systematic_rules
        
        return stats

    # === 新增：process_experience方法（兼容main.py调用）===
    def process_experience(self, experience, historical_experiences=None):
        """
        处理单个经验，生成并验证规律
        这个方法兼容main.py中的调用模式
        
        Args:
            experience: EOCATR_Tuple格式的经验
            historical_experiences: 历史经验列表（可选）
            
        Returns:
            List[CandidateRule]: 生成的候选规律列表
        """
        try:
            if self.logger:
                self.logger.log(f"🌸 BMP开始处理经验: {getattr(experience, 'tuple_id', 'unknown')}")
            
            # 确保输入是EOCATR_Tuple格式
            if not hasattr(experience, 'environment'):
                if self.logger:
                    self.logger.log(f"⚠️ 经验格式不正确，跳过处理")
                return []
            
            # 准备经验列表
            experiences_to_process = [experience]
            if historical_experiences:
                # 限制历史经验数量，避免内存过大
                max_historical = 20
                if len(historical_experiences) > max_historical:
                    historical_experiences = historical_experiences[-max_historical:]
                experiences_to_process.extend(historical_experiences)
            
            # 调用现有的怒放阶段方法生成规律
            new_candidate_rules = self.blooming_phase(experiences_to_process)
            
            # 如果有历史经验，执行验证阶段
            if historical_experiences and len(historical_experiences) > 0:
                validated_rule_ids = self.validation_phase(historical_experiences)
                if self.logger and validated_rule_ids:
                    self.logger.log(f"✅ 验证阶段通过{len(validated_rule_ids)}个规律")
            
            # 执行剪枝阶段（内存管理）
            pruned_rule_ids = self.pruning_phase()
            if self.logger and pruned_rule_ids:
                self.logger.log(f"✂️ 剪枝阶段移除{len(pruned_rule_ids)}个规律")
            
            if self.logger:
                self.logger.log(f"🌸 BMP处理完成: 生成{len(new_candidate_rules)}个候选规律")
            
            return new_candidate_rules
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ BMP经验处理失败: {str(e)}")
            return []
    def _filter_relevant_experiences_for_blooming(self, experiences: List[EOCATR_Tuple], max_experiences: int = 50) -> List[EOCATR_Tuple]:
        """过滤相关经验以提高怒放效率"""
        if len(experiences) <= max_experiences:
            return experiences
        
        # 优先选择最近的经验
        recent_experiences = experiences[-max_experiences//2:]
        
        # 选择多样化的历史经验
        historical_experiences = experiences[:-max_experiences//2]
        if historical_experiences:
            # 按经验模式分组
            pattern_groups = {}
            for exp in historical_experiences:
                pattern = self._get_experience_pattern(exp)
                if pattern not in pattern_groups:
                    pattern_groups[pattern] = []
                pattern_groups[pattern].append(exp)
            
            # 从每组选择最佳经验
            diverse_experiences = []
            remaining_slots = max_experiences - len(recent_experiences)
            per_group_limit = max(1, remaining_slots // max(1, len(pattern_groups)))
            
            for group_experiences in pattern_groups.values():
                # 选择组内最新经验
                best_in_group = group_experiences[-per_group_limit:]
                diverse_experiences.extend(best_in_group)
        
        return recent_experiences + diverse_experiences[:max_experiences-len(recent_experiences)]
    
    def _get_experience_pattern(self, exp) -> str:
        """获取经验模式用于分组"""
        try:
            env = getattr(exp.environment, "content", getattr(exp.environment, "name", "unknown"))
            obj = getattr(exp.object, "content", getattr(exp.object, "name", "unknown"))
            action = getattr(exp.action, "content", getattr(exp.action, "name", "unknown"))
            return f"{env}_{obj}_{action}"
        except:
            return "unknown_pattern"
    
    def _has_sufficient_new_experiences(self, experiences: List[EOCATR_Tuple], min_new_patterns: int = 2) -> bool:
        """检查是否有足够的新经验模式来生成规律"""
        # 放宽策略：至少2条经验即可
        if len(experiences) < 2:
            return False
        
        # 检查经验的多样性
        unique_patterns = set()
        for exp in experiences:
            pattern = self._get_experience_pattern(exp)
            unique_patterns.add(pattern)
        
        # 放宽策略：不同模式至少1个即可（同模式重复也允许）
        if len(unique_patterns) < 1:
            if self.logger:
                self.logger.log(f"BMP：经验模式不足 ({len(unique_patterns)}/{1})，跳过规律生成")
            return False
        
        return True