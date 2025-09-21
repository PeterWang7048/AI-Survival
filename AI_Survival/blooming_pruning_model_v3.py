"""
PPP V3.0 怒放剪枝模型 (BMP) - 智能组合怒放机制
实现分层渐进生成、智能预过滤、镜像对称生成
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from collections import defaultdict

from symbolic_core_v3 import (
    SymbolicElement, EOCATR_Tuple, SymbolType, AbstractionLevel,
    global_registry, create_element, create_tuple
)

# 配置日志系统
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RuleCandidate:
    """规律候选对象"""
    rule_id: str                           # 规律ID
    source_tuple: EOCATR_Tuple            # 源经验元组
    pattern_elements: List[SymbolicElement] # 模式元素
    prediction_element: SymbolicElement    # 预测元素
    generation_layer: int                  # 生成层级(1-3)
    generation_method: str                 # 生成方法
    semantic_score: float = 0.0            # 语义得分
    logical_score: float = 0.0             # 逻辑得分
    mirror_rule_id: Optional[str] = None   # 镜像规律ID
    support_count: int = 0                 # 支持计数
    rejection_count: int = 0               # 反对计数
    confidence: float = 0.0                # 置信度
    created_time: Optional[datetime] = None
    # 兼容性属性：与pattern_elements保持同步
    condition_elements: Optional[List[SymbolicElement]] = None
    # 预测集合属性：存储所有相关预测
    predictions: Optional[List] = None

    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
        if not self.rule_id:
            self.rule_id = self._generate_rule_id()
        # 自动同步condition_elements与pattern_elements
        if self.condition_elements is None:
            self.condition_elements = self.pattern_elements.copy() if self.pattern_elements else []
        # 初始化predictions属性
        if self.predictions is None:
            self.predictions = [self.prediction_element] if self.prediction_element else []

    def _generate_rule_id(self) -> str:
        """生成规律唯一标识"""
        pattern_str = "_".join([elem.symbol_id for elem in self.pattern_elements])
        pred_str = self.prediction_element.symbol_id
        content_hash = f"L{self.generation_layer}_{pattern_str}_{pred_str}"
        import hashlib
        return f"RULE_{hashlib.md5(content_hash.encode()).hexdigest()[:10]}"

    def calculate_total_score(self) -> float:
        """计算综合得分"""
        if self.support_count + self.rejection_count == 0:
            evidence_score = 0.0
        else:
            evidence_score = self.support_count / (self.support_count + self.rejection_count)
        
        return (self.semantic_score * 0.3 + self.logical_score * 0.3 + 
                evidence_score * 0.4)

class EnhancedSemanticValidator:
    """增强语义验证器 - 智能化深层语义理解系统"""
    
    def __init__(self):
        # 基础语义兼容性规则（保持向后兼容）
        self.base_compatibility_rules = {
            # 环境-对象兼容性
            ('森林', '老虎'): 1.0, ('森林', '兔子'): 1.0, ('森林', '石头'): 0.8,
            ('河流', '鱼'): 1.0, ('河流', '老虎'): 0.6, ('河流', '石头'): 0.3,
            ('山洞', '熊'): 1.0, ('山洞', '石头'): 0.9, ('山洞', '鱼'): 0.1,
            
            # 行动-工具兼容性  
            ('攻击', '长矛'): 1.0, ('攻击', '石头'): 0.8, ('攻击', '水'): 0.1,
            ('制作', '石头'): 1.0, ('制作', '木棍'): 1.0, ('制作', '鱼'): 0.2,
            ('移动', '腿'): 1.0, ('移动', '长矛'): 0.3, ('移动', '石头'): 0.1,
            
            # 行动-结果兼容性（因果关系）
            ('攻击', '受伤'): 1.0, ('攻击', '食物'): 0.6, ('攻击', '安全'): 0.2,
            ('制作', '工具'): 1.0, ('制作', '受伤'): 0.3, ('制作', '食物'): 0.1,
            ('移动', '安全'): 0.8, ('移动', '受伤'): 0.3, ('移动', '食物'): 0.2,
            
            # 对象-结果兼容性
            ('老虎', '受伤'): 1.0, ('老虎', '食物'): 0.8, ('老虎', '安全'): 0.2,
            ('兔子', '食物'): 1.0, ('兔子', '受伤'): 0.3, ('兔子', '安全'): 0.9,
            ('石头', '工具'): 1.0, ('石头', '食物'): 0.0, ('石头', '受伤'): 0.6,
        }
        
        # 深层语义关系网络
        self.semantic_network = self._build_semantic_network()
        
        # 上下文感知映射
        self.context_modifiers = self._build_context_modifiers()
        
        # 因果推理链
        self.causal_chains = self._build_causal_chains()
        
        # 时序关系模型
        self.temporal_patterns = self._build_temporal_patterns()
        
        # 学习型语义知识库
        self.learned_semantics = {
            'pattern_frequencies': {},
            'context_weights': {},
            'success_correlations': {},
            'adaptation_history': []
        }
        
        # 多层次验证权重
        self.validation_weights = {
            'lexical_weight': 0.2,      # 词汇层权重
            'conceptual_weight': 0.3,   # 概念层权重
            'logical_weight': 0.25,     # 逻辑层权重
            'pragmatic_weight': 0.25    # 实用层权重
        }
        
        logger.info("增强语义验证器初始化完成 - 支持深层语义理解")

    def _build_semantic_network(self) -> Dict[str, Dict[str, float]]:
        """构建深层语义关系网络"""
        network = {
            # 行动语义网络
            '攻击': {
                'semantic_field': 'aggressive_action',
                'causal_effects': ['伤害', '威胁', '控制', '获取'],
                'required_conditions': ['目标', '能力', '意图'],
                'typical_contexts': ['战斗', '狩猎', '防御', '竞争'],
                'emotional_valence': -0.3,  # 负面倾向
                'intensity_level': 0.9       # 高强度
            },
            '收集': {
                'semantic_field': 'gathering_action',
                'causal_effects': ['获得', '积累', '准备', '丰富'],
                'required_conditions': ['资源', '容器', '时间'],
                'typical_contexts': ['觅食', '准备', '储备', '探索'],
                'emotional_valence': 0.6,   # 正面倾向
                'intensity_level': 0.4      # 中等强度
            },
            '移动': {
                'semantic_field': 'motion_action',
                'causal_effects': ['位置变化', '接近', '逃离', '探索'],
                'required_conditions': ['路径', '能力', '目标'],
                'typical_contexts': ['导航', '追逐', '逃避', '探索'],
                'emotional_valence': 0.0,   # 中性
                'intensity_level': 0.5      # 中等强度
            },
            '制作': {
                'semantic_field': 'creation_action',
                'causal_effects': ['工具', '改变', '新对象', '能力提升'],
                'required_conditions': ['材料', '技能', '工具', '时间'],
                'typical_contexts': ['生产', '修复', '改进', '创新'],
                'emotional_valence': 0.7,   # 正面倾向
                'intensity_level': 0.6      # 中高强度
            },
            
            # 环境语义网络
            '森林': {
                'semantic_field': 'natural_environment',
                'affordances': ['隐蔽', '资源', '危险', '庇护'],
                'typical_inhabitants': ['动物', '植物', '昆虫'],
                'risk_level': 0.6,
                'resource_richness': 0.8
            },
            '河流': {
                'semantic_field': 'water_environment', 
                'affordances': ['饮水', '清洁', '交通', '食物'],
                'typical_inhabitants': ['鱼类', '水鸟', '两栖动物'],
                'risk_level': 0.4,
                'resource_richness': 0.7
            },
            '山洞': {
                'semantic_field': 'shelter_environment',
                'affordances': ['庇护', '储存', '隐藏', '防御'],
                'typical_inhabitants': ['洞穴动物', '蝙蝠'],
                'risk_level': 0.5,
                'resource_richness': 0.3
            },
            
            # 对象语义网络
            '老虎': {
                'semantic_field': 'predator_animal',
                'threat_level': 0.95,
                'predictability': 0.3,
                'typical_behaviors': ['狩猎', '巡视', '休息'],
                'interaction_outcomes': {'攻击': '高风险', '逃避': '明智', '观察': '谨慎'}
            },
            '兔子': {
                'semantic_field': 'prey_animal',
                'threat_level': 0.05,
                'predictability': 0.4,
                'typical_behaviors': ['觅食', '警戒', '逃跑'],
                'interaction_outcomes': {'攻击': '容易', '收集': '食物', '观察': '安全'}
            }
        }
        return network

    def _build_context_modifiers(self) -> Dict[str, Dict[str, float]]:
        """构建上下文感知调节器"""
        return {
            # 危险情境调节器
            'dangerous_context': {
                'keywords': ['战斗', '敌对', '威胁', '攻击', '受伤'],
                'modifiers': {
                    ('攻击', '安全'): -0.4,    # 危险情境下攻击不太可能带来安全
                    ('移动', '安全'): +0.3,     # 危险时移动可能带来安全
                    ('逃跑', '安全'): +0.5,     # 危险时逃跑增加安全性
                    ('隐藏', '安全'): +0.4      # 危险时隐藏增加安全性
                }
            },
            
            # 资源获取情境调节器
            'resource_context': {
                'keywords': ['收集', '获得', '食物', '工具', '材料'],
                'modifiers': {
                    ('收集', '成功'): +0.2,     # 资源情境下收集更可能成功
                    ('制作', '工具'): +0.3,      # 有材料时制作更可能产生工具
                    ('探索', '发现'): +0.25     # 资源搜寻时探索更可能有发现
                }
            },
            
            # 生存基础情境调节器  
            'survival_context': {
                'keywords': ['饥饿', '渴', '疲劳', '寒冷', '受伤'],
                'modifiers': {
                    ('饮用', '成功'): +0.3,     # 基础需求情境下基础行动成功率高
                    ('休息', '恢复'): +0.4,     # 疲劳时休息恢复效果好
                    ('寻找', '食物'): +0.2      # 饥饿时寻找食物动机强
                }
            },
            
            # 探索发现情境调节器
            'exploration_context': {
                'keywords': ['未知', '新', '探索', '发现', '调查'],
                'modifiers': {
                    ('移动', '发现'): +0.3,     # 探索情境下移动更可能有发现
                    ('观察', '信息'): +0.4,     # 探索时观察更可能获得信息
                    ('尝试', '学习'): +0.2      # 探索时尝试促进学习
                }
            }
        }

    def _build_causal_chains(self) -> Dict[str, List[Dict]]:
        """构建因果推理链"""
        return {
            # 攻击因果链
            'attack_chain': [
                {'trigger': '威胁感知', 'action': '攻击准备', 'intermediate': '姿态威胁'},
                {'trigger': '攻击准备', 'action': '攻击执行', 'intermediate': '物理接触'},
                {'trigger': '攻击执行', 'action': '伤害产生', 'result': '受伤'},
                {'trigger': '伤害产生', 'action': '后果处理', 'result': ['逃跑', '反击', '屈服']}
            ],
            
            # 收集因果链  
            'gather_chain': [
                {'trigger': '需求识别', 'action': '目标定位', 'intermediate': '资源发现'},
                {'trigger': '资源发现', 'action': '收集行动', 'intermediate': '获取过程'},
                {'trigger': '获取过程', 'action': '收集完成', 'result': '成功'},
                {'trigger': '收集完成', 'action': '资源利用', 'result': ['制作', '消费', '储存']}
            ],
            
            # 制作因果链
            'craft_chain': [
                {'trigger': '工具需求', 'action': '材料收集', 'intermediate': '原料准备'},
                {'trigger': '原料准备', 'action': '制作过程', 'intermediate': '加工组合'},
                {'trigger': '加工组合', 'action': '工具成型', 'result': '工具'},
                {'trigger': '工具成型', 'action': '功能测试', 'result': ['成功', '失败', '改进']}
            ]
        }

    def _build_temporal_patterns(self) -> Dict[str, Dict]:
        """构建时序关系模型"""
        return {
            # 立即因果（0-1秒）
            'immediate_causation': {
                'time_window': (0, 1),
                'patterns': {
                    ('攻击', '受伤'): 0.95,
                    ('碰撞', '伤害'): 0.90,
                    ('触摸', '感知'): 0.98
                }
            },
            
            # 短期因果（1-10秒）
            'short_term_causation': {
                'time_window': (1, 10),
                'patterns': {
                    ('移动', '到达'): 0.85,
                    ('寻找', '发现'): 0.60,
                    ('呼叫', '回应'): 0.40
                }
            },
            
            # 中期因果（10秒-5分钟）
            'medium_term_causation': {
                'time_window': (10, 300),
                'patterns': {
                    ('制作', '工具'): 0.75,
                    ('收集', '积累'): 0.80,
                    ('探索', '发现'): 0.55
                }
            },
            
            # 长期因果（5分钟以上）
            'long_term_causation': {
                'time_window': (300, float('inf')),
                'patterns': {
                    ('学习', '技能提升'): 0.70,
                    ('练习', '熟练'): 0.65,
                    ('经验积累', '智慧'): 0.60
                }
            }
        }

    def validate_semantic_compatibility(self, elements: List[SymbolicElement]) -> float:
        """多层次语义兼容性验证 - 向后兼容接口"""
        # 执行增强的多层次验证
        enhanced_result = self.validate_multi_level_semantics(elements)
        
        # 返回综合得分以保持向后兼容
        return enhanced_result['overall_score']

    def validate_multi_level_semantics(self, elements: List[SymbolicElement], 
                                     context: Optional[str] = None) -> Dict[str, Any]:
        """多层次语义验证 - 核心增强功能"""
        if len(elements) < 2:
            return {
                'overall_score': 1.0,
                'lexical_score': 1.0,
                'conceptual_score': 1.0,
                'logical_score': 1.0,
                'pragmatic_score': 1.0,
                'confidence': 1.0,
                'context_detected': None
            }
        
        contents = [elem.content for elem in elements]
        
        # 自动检测上下文
        if not context:
            context = self._detect_context(contents)
        
        # 层次1：词汇层语义验证
        lexical_score = self._validate_lexical_level(elements)
        
        # 层次2：概念层语义验证  
        conceptual_score = self._validate_conceptual_level(elements, context)
        
        # 层次3：逻辑层语义验证
        logical_score = self._validate_logical_level(elements)
        
        # 层次4：实用层语义验证
        pragmatic_score = self._validate_pragmatic_level(elements, context)
        
        # 计算综合得分
        overall_score = (
            lexical_score * self.validation_weights['lexical_weight'] +
            conceptual_score * self.validation_weights['conceptual_weight'] +
            logical_score * self.validation_weights['logical_weight'] +
            pragmatic_score * self.validation_weights['pragmatic_weight']
        )
        
        # 计算置信度
        confidence = self._calculate_validation_confidence(
            lexical_score, conceptual_score, logical_score, pragmatic_score
        )
        
        result = {
            'overall_score': overall_score,
            'lexical_score': lexical_score,
            'conceptual_score': conceptual_score,
            'logical_score': logical_score,
            'pragmatic_score': pragmatic_score,
            'confidence': confidence,
            'context_detected': context,
            'element_contents': contents
        }
        
        logger.debug(f"多层次语义验证: {contents} -> 综合:{overall_score:.3f}, "
                    f"词汇:{lexical_score:.3f}, 概念:{conceptual_score:.3f}, "
                    f"逻辑:{logical_score:.3f}, 实用:{pragmatic_score:.3f}, "
                    f"置信度:{confidence:.3f}, 上下文:{context}")
        
        return result

    def _validate_lexical_level(self, elements: List[SymbolicElement]) -> float:
        """词汇层验证：基于词汇共现和基础语义关联"""
        total_score = 0.0
        pair_count = 0
        
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                elem1, elem2 = elements[i], elements[j]
                pair_key = (elem1.content, elem2.content)
                reverse_key = (elem2.content, elem1.content)
                
                # 查找基础兼容性得分
                score = self.base_compatibility_rules.get(pair_key, 
                        self.base_compatibility_rules.get(reverse_key, 0.5))
                
                # 应用学习的频率权重
                frequency_weight = self._get_pattern_frequency_weight(pair_key)
                adjusted_score = score * (0.7 + 0.3 * frequency_weight)
                
                total_score += adjusted_score
                pair_count += 1
        
        return total_score / pair_count if pair_count > 0 else 0.5

    def _validate_conceptual_level(self, elements: List[SymbolicElement], context: Optional[str]) -> float:
        """概念层验证：基于深层语义网络和概念关联"""
        contents = [elem.content for elem in elements]
        total_score = 0.0
        evaluated_pairs = 0
        
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                content1, content2 = contents[i], contents[j]
                
                # 计算因果关联强度
                causal_strength = self._calculate_causal_strength(content1, content2)
                
                # 获取深层语义信息
                semantic1 = self.semantic_network.get(content1, {})
                semantic2 = self.semantic_network.get(content2, {})
                
                if semantic1 or semantic2:
                    # 计算语义场兼容性
                    field_compatibility = self._calculate_semantic_field_compatibility(semantic1, semantic2)
                    
                    # 计算情感价值匹配
                    valence_match = self._calculate_valence_match(semantic1, semantic2)
                    
                    # 概念层得分（权重调整，因果关系更重要）
                    conceptual_score = (field_compatibility * 0.3 + 
                                      causal_strength * 0.5 + 
                                      valence_match * 0.2)
                    
                    total_score += conceptual_score
                    evaluated_pairs += 1
                else:
                    # 对于不在语义网络中的元素，主要基于因果关系
                    conceptual_score = causal_strength * 0.8 + 0.1  # 基础得分
                    total_score += conceptual_score
                    evaluated_pairs += 1
        
        return total_score / evaluated_pairs if evaluated_pairs > 0 else 0.5

    def _validate_logical_level(self, elements: List[SymbolicElement]) -> float:
        """逻辑层验证：检查逻辑一致性和推理有效性"""
        contents = [elem.content for elem in elements]
        
        # 检查直接逻辑矛盾
        contradiction_penalty = 0.0
        contradiction_count = 0
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                if self._check_direct_contradiction(contents[i], contents[j]):
                    contradiction_penalty += 0.5  # 增加惩罚力度
                    contradiction_count += 1
                
        # 检查因果链的逻辑性
        causal_logic_score = self._validate_causal_logic(contents)
        
        # 检查时序合理性
        temporal_logic_score = self._validate_temporal_logic(contents)
        
        # 综合逻辑得分
        base_score = 1.0 - min(contradiction_penalty, 0.95)  # 提高最大惩罚
        
        # 如果有矛盾，大幅降低得分
        if contradiction_count > 0:
            base_score = min(base_score, 0.3)  # 有矛盾时最高只能0.3
        
        logic_score = (base_score * 0.6 + 
                      causal_logic_score * 0.25 + 
                      temporal_logic_score * 0.15)
        
        return max(0.05, logic_score)  # 最低分数降到0.05

    def _validate_pragmatic_level(self, elements: List[SymbolicElement], context: Optional[str]) -> float:
        """实用层验证：基于实际效果和情境适用性"""
        contents = [elem.content for elem in elements]
        
        # 上下文适配得分
        context_fit_score = self._calculate_context_fit(contents, context)
        
        # 实际可行性得分
        feasibility_score = self._calculate_feasibility(contents)
        
        # 预期效果得分
        effectiveness_score = self._calculate_effectiveness(contents)
        
        # 学习经验得分（基于历史成功率）
        experience_score = self._calculate_experience_score(contents)
        
        # 综合实用得分
        pragmatic_score = (context_fit_score * 0.3 + 
                          feasibility_score * 0.25 + 
                          effectiveness_score * 0.25 + 
                          experience_score * 0.2)
        
        return pragmatic_score

    def check_logical_contradiction(self, elements: List[SymbolicElement]) -> bool:
        """检查逻辑矛盾 - 增强版本"""
        result = self.validate_multi_level_semantics(elements)
        
        # 如果逻辑层得分过低，认为存在矛盾
        return result['logical_score'] < 0.3

    # ============================================================================
    # 辅助方法：支持多层次语义验证的具体实现
    # ============================================================================

    def _detect_context(self, contents: List[str]) -> Optional[str]:
        """自动检测语义上下文"""
        for context_name, context_info in self.context_modifiers.items():
            keywords = context_info['keywords']
            matches = sum(1 for content in contents if any(kw in content for kw in keywords))
            if matches >= 2:  # 至少匹配2个关键词才认为检测到上下文
                return context_name
        return None

    def _get_pattern_frequency_weight(self, pair_key: Tuple[str, str]) -> float:
        """获取模式频率权重"""
        frequency = self.learned_semantics['pattern_frequencies'].get(pair_key, 0)
        # 将频率转换为权重（0-1范围）
        return min(1.0, frequency / 10.0)  # 10次以上为满权重

    def _calculate_semantic_field_compatibility(self, semantic1: Dict, semantic2: Dict) -> float:
        """计算语义场兼容性"""
        field1 = semantic1.get('semantic_field', '')
        field2 = semantic2.get('semantic_field', '')
        
        # 定义语义场兼容性矩阵
        field_compatibility = {
            ('aggressive_action', 'predator_animal'): 0.9,
            ('gathering_action', 'prey_animal'): 0.8,
            ('motion_action', 'natural_environment'): 0.9,
            ('creation_action', 'shelter_environment'): 0.7,
            ('natural_environment', 'predator_animal'): 0.8,
            ('water_environment', 'prey_animal'): 0.7
        }
        
        compatibility = field_compatibility.get((field1, field2), 
                        field_compatibility.get((field2, field1), 0.5))
        return compatibility

    def _calculate_causal_strength(self, content1: str, content2: str) -> float:
        """计算因果关联强度"""
        # 检查时序因果模式
        for pattern_name, pattern_info in self.temporal_patterns.items():
            patterns = pattern_info['patterns']
            strength = patterns.get((content1, content2), 
                      patterns.get((content2, content1), 0.0))
            if strength > 0:
                return strength
        
        # 检查强因果关系（直接映射）
        strong_causal_pairs = {
            ('攻击', '受伤'): 0.95,
            ('攻击', '伤害'): 0.95,
            ('碰撞', '受伤'): 0.90,
            ('制作', '工具'): 0.85,
            ('收集', '获得'): 0.80,
            ('饮用', '解渴'): 0.90,
            ('移动', '到达'): 0.75,
            ('逃跑', '安全'): 0.70
        }
        
        causal_strength = strong_causal_pairs.get((content1, content2), 
                         strong_causal_pairs.get((content2, content1), 0.0))
        if causal_strength > 0:
            return causal_strength
        
        # 检查因果链
        for chain_name, chain_steps in self.causal_chains.items():
            for step in chain_steps:
                if (content1 in str(step.get('action', '')) and 
                    content2 in str(step.get('result', ''))):
                    return 0.8
        
        # 检查语义网络中的因果效应
        semantic1 = self.semantic_network.get(content1, {})
        if 'causal_effects' in semantic1:
            for effect in semantic1['causal_effects']:
                if effect in content2 or content2 in effect:
                    return 0.75
        
        return 0.3  # 默认低因果关联

    def _calculate_valence_match(self, semantic1: Dict, semantic2: Dict) -> float:
        """计算情感价值匹配度"""
        valence1 = semantic1.get('emotional_valence', 0.0)
        valence2 = semantic2.get('emotional_valence', 0.0)
        
        # 计算价值差异
        valence_diff = abs(valence1 - valence2)
        
        # 转换为匹配度（差异越小，匹配度越高）
        match_score = 1.0 - (valence_diff / 2.0)  # 2.0是最大可能差异
        return max(0.0, match_score)

    def _check_direct_contradiction(self, content1: str, content2: str) -> bool:
        """检查直接逻辑矛盾"""
        contradictions = [
            ('靠近', '远离'), ('攻击', '逃跑'), ('受伤', '安全'), 
            ('成功', '失败'), ('获得', '失去'), ('前进', '后退'),
            ('主动', '被动'), ('威胁', '安全'), ('危险', '安全')
        ]
        
        for pair in contradictions:
            # 检查完全匹配
            if (content1 == pair[0] and content2 == pair[1]) or \
               (content1 == pair[1] and content2 == pair[0]):
                return True
            # 检查包含关系（更宽松的匹配）
            if (pair[0] in content1 and pair[1] in content2) or \
               (pair[1] in content1 and pair[0] in content2):
                return True
        return False

    def _validate_causal_logic(self, contents: List[str]) -> float:
        """验证因果链逻辑"""
        # 检查是否存在合理的因果序列
        causal_score = 0.5  # 基础得分
        
        for i in range(len(contents) - 1):
            for j in range(i + 1, len(contents)):
                causal_strength = self._calculate_causal_strength(contents[i], contents[j])
                if causal_strength > 0.6:
                    causal_score += 0.2
        
        return min(1.0, causal_score)

    def _validate_temporal_logic(self, contents: List[str]) -> float:
        """验证时序逻辑"""
        # 检查时序关系的合理性
        temporal_score = 0.7  # 基础得分
        
        # 如果包含明显的时序违背，降低得分
        sequential_violations = [
            ('结果', '行动'),  # 结果不应该在行动之前
            ('效果', '原因')   # 效果不应该在原因之前
        ]
        
        for violation in sequential_violations:
            if any(v in ' '.join(contents) for v in violation):
                temporal_score -= 0.2
        
        return max(0.1, temporal_score)

    def _calculate_context_fit(self, contents: List[str], context: Optional[str]) -> float:
        """计算上下文适配度"""
        if not context or context not in self.context_modifiers:
            return 0.6  # 无特定上下文时的中性得分
        
        context_info = self.context_modifiers[context]
        modifiers = context_info['modifiers']
        
        base_score = 0.6
        adjustment = 0.0
        
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                pair_key = (contents[i], contents[j])
                reverse_key = (contents[j], contents[i])
                
                modifier = modifiers.get(pair_key, modifiers.get(reverse_key, 0.0))
                adjustment += modifier
        
        final_score = base_score + adjustment
        return max(0.1, min(1.0, final_score))

    def _calculate_feasibility(self, contents: List[str]) -> float:
        """计算实际可行性"""
        # 基于语义网络中的可行性信息
        feasibility_score = 0.7  # 基础可行性
        
        for content in contents:
            semantic_info = self.semantic_network.get(content, {})
            if 'required_conditions' in semantic_info:
                # 如果有明确的前置条件，检查是否满足
                conditions = semantic_info['required_conditions']
                satisfied_conditions = sum(1 for cond in conditions if any(cond in c for c in contents))
                condition_ratio = satisfied_conditions / len(conditions) if conditions else 1.0
                feasibility_score *= (0.5 + 0.5 * condition_ratio)
        
        return max(0.1, feasibility_score)

    def _calculate_effectiveness(self, contents: List[str]) -> float:
        """计算预期效果得分"""
        effectiveness = 0.6  # 基础效果得分
        
        for content in contents:
            semantic_info = self.semantic_network.get(content, {})
            intensity = semantic_info.get('intensity_level', 0.5)
            effectiveness += intensity * 0.1  # 强度越高，效果越好
        
        return min(1.0, effectiveness)

    def _calculate_experience_score(self, contents: List[str]) -> float:
        """计算基于历史经验的得分"""
        # 从学习的成功关联中获取得分
        experience_score = 0.5  # 基础经验得分
        
        pattern_key = tuple(sorted(contents))
        success_correlation = self.learned_semantics['success_correlations'].get(pattern_key, 0.5)
        
        return success_correlation

    def _calculate_validation_confidence(self, lexical: float, conceptual: float, 
                                       logical: float, pragmatic: float) -> float:
        """计算验证置信度"""
        scores = [lexical, conceptual, logical, pragmatic]
        
        # 平均得分
        avg_score = sum(scores) / len(scores)
        
        # 一致性（得分之间的标准差越小，置信度越高）
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        consistency = 1.0 - min(variance, 1.0)
        
        # 综合置信度
        confidence = (avg_score * 0.7 + consistency * 0.3)
        return confidence

    def learn_from_experience(self, elements: List[SymbolicElement], success: bool):
        """从经验中学习，更新语义知识库"""
        contents = [elem.content for elem in elements]
        
        # 更新模式频率
        for i in range(len(contents)):
            for j in range(i + 1, len(contents)):
                pair_key = (contents[i], contents[j])
                current_freq = self.learned_semantics['pattern_frequencies'].get(pair_key, 0)
                self.learned_semantics['pattern_frequencies'][pair_key] = current_freq + 1
        
        # 更新成功关联
        pattern_key = tuple(sorted(contents))
        current_correlation = self.learned_semantics['success_correlations'].get(pattern_key, 0.5)
        
        # 使用指数移动平均更新成功率
        alpha = 0.1  # 学习率
        new_correlation = current_correlation * (1 - alpha) + (1.0 if success else 0.0) * alpha
        self.learned_semantics['success_correlations'][pattern_key] = new_correlation
        
        # 记录学习历史
        self.learned_semantics['adaptation_history'].append({
            'elements': contents,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持历史记录在合理范围内
        if len(self.learned_semantics['adaptation_history']) > 1000:
            self.learned_semantics['adaptation_history'].pop(0)

# 保持向后兼容性的别名
SemanticValidator = EnhancedSemanticValidator

class BloomingGenerator:
    """怒放生成器 - 实现分层渐进生成策略"""
    
    def __init__(self, semantic_validator: EnhancedSemanticValidator):
        self.semantic_validator = semantic_validator
        self.generation_stats = {
            'layer1_generated': 0,
            'layer2_generated': 0, 
            'layer3_generated': 0,
            'semantic_filtered': 0,
            'logical_filtered': 0,
            'mirror_generated': 0
        }
        logger.info("怒放生成器初始化完成")

    def generate_layer1_rules(self, experience: EOCATR_Tuple) -> List[RuleCandidate]:
        """第1层：动态单元素规律生成 (Cₙ¹) - 增强版"""
        candidates = []
        all_elements = experience.get_non_null_elements()
        result_element = experience.get_element_by_type(SymbolType.RESULT)
        
        # 获取可用于模式的元素（排除result）
        pattern_elements = [e for e in all_elements if e.symbol_type != SymbolType.RESULT]
        n = len(pattern_elements)  # 动态计算可用元素数量
        
        if not result_element:
            logger.warning("未找到result元素，跳过第1层规律生成")
            return candidates
        
        if n == 0:
            logger.warning("没有可用的模式元素，跳过第1层规律生成")
            return candidates
        
        # 数学化的Cₙ¹生成：从n个元素中选择1个，共n种组合
        logger.info(f"第1层：从{n}个元素中生成C{n}¹={n}个单元素规律")
        
        # === 新增：智能元素质量评估和分类 ===
        element_quality_scores = {}
        element_type_distribution = {}
        
        for element in pattern_elements:
            # 计算元素质量得分（考虑content完整性、语义丰富度等）
            quality_score = self._assess_element_quality(element)
            element_quality_scores[element.symbol_id] = quality_score
            
            # 统计类型分布
            element_type = element.symbol_type
            if element_type not in element_type_distribution:
                element_type_distribution[element_type] = 0
            element_type_distribution[element_type] += 1
        
        # 计算类型多样性奖励权重
        diversity_weights = self._calculate_type_diversity_weights(element_type_distribution, n)
        
        # 自适应阈值调整（基于元素数量和质量分布）
        adaptive_threshold = self._calculate_adaptive_threshold_layer1(element_quality_scores, n)
        
        logger.info(f"第1层智能评估：平均元素质量={sum(element_quality_scores.values())/n:.3f}, "
                   f"自适应阈值={adaptive_threshold:.3f}, 类型多样性={len(element_type_distribution)}")
        
        # 按质量排序的元素生成
        sorted_elements = sorted(pattern_elements, 
                               key=lambda e: element_quality_scores[e.symbol_id], 
                               reverse=True)
        
        for element in sorted_elements:
            # 计算增强的语义得分（融合质量评估和多样性权重）
            base_semantic_score = self._calculate_single_element_semantic_score(element, result_element)
            quality_weight = element_quality_scores[element.symbol_id]
            diversity_weight = diversity_weights.get(element.symbol_type, 1.0)
            
            # 综合语义得分 = 基础得分 * 质量权重 * 多样性权重
            enhanced_semantic_score = base_semantic_score * quality_weight * diversity_weight
            
            # 自适应过滤：使用动态阈值
            if enhanced_semantic_score < adaptive_threshold:
                self.generation_stats['semantic_filtered'] += 1
                logger.debug(f"单元素规律因语义得分过低被过滤: {element.content} -> {result_element.content} "
                           f"(得分: {enhanced_semantic_score:.3f} < 阈值: {adaptive_threshold:.3f})")
                continue
            
            # 检查逻辑兼容性
            if self.semantic_validator.check_logical_contradiction([element, result_element]):
                self.generation_stats['logical_filtered'] += 1
                logger.debug(f"单元素规律因逻辑矛盾被过滤: {element.content} -> {result_element.content}")
                continue
            
            candidate = RuleCandidate(
                rule_id="",
                source_tuple=experience,
                pattern_elements=[element],
                prediction_element=result_element,
                generation_layer=1,
                generation_method=f"智能单元素规律_C{n}1_Q{quality_weight:.2f}_D{diversity_weight:.2f}",
                semantic_score=enhanced_semantic_score,
                logical_score=0.9  # 单元素规律逻辑得分较高
            )
            candidates.append(candidate)
            self.generation_stats['layer1_generated'] += 1
            logger.debug(f"生成智能单元素规律: {element.content} -> {result_element.content} "
                        f"(增强得分: {enhanced_semantic_score:.3f}, 质量: {quality_weight:.3f}, 多样性: {diversity_weight:.3f})")
        
        logger.info(f"第1层完成：实际生成 {len(candidates)} 个单元素规律（理论最大值: {n}，"
                   f"语义过滤: {self.generation_stats.get('semantic_filtered', 0)}，"
                   f"逻辑过滤: {self.generation_stats.get('logical_filtered', 0)}）")
        return candidates
    
    def _assess_element_quality(self, element: SymbolicElement) -> float:
        """评估单个元素的质量得分"""
        quality_score = 1.0
        
        # 1. Content完整性检查
        if not element.content or element.content.strip() == "":
            quality_score *= 0.3  # 空内容严重降低质量
        elif len(element.content.strip()) < 3:
            quality_score *= 0.6  # 过短内容降低质量
        
        # 2. 语义丰富度评估
        content = element.content.lower().strip()
        
        # 检查是否为无意义的占位符
        meaningless_patterns = ['none', 'null', 'empty', '无', '空', 'unknown', '未知']
        if any(pattern in content for pattern in meaningless_patterns):
            quality_score *= 0.2
        
        # 检查是否为具体描述
        specific_indicators = ['具体', '详细', '明确', '特定']
        if any(indicator in content for indicator in specific_indicators):
            quality_score *= 1.2
        
        # 3. 类型特异性加权
        type_quality_multipliers = {
            SymbolType.ACTION: 1.2,      # 行动元素通常质量较高
            SymbolType.RESULT: 1.1,      # 结果元素重要性高
            SymbolType.OBJECT: 1.0,      # 对象元素标准质量
            SymbolType.TOOL: 1.1,        # 工具元素较为重要
            SymbolType.ENVIRONMENT: 0.9, # 环境元素质量一般
            SymbolType.CHARACTER: 0.8    # 特征元素质量相对较低
        }
        
        type_multiplier = type_quality_multipliers.get(element.symbol_type, 0.7)
        quality_score *= type_multiplier
        
        # 4. 抽象层级影响
        if hasattr(element, 'abstraction_level'):
            level = element.abstraction_level
            if level == AbstractionLevel.CONCRETE:
                quality_score *= 1.1  # 具体层级质量略高
            elif level == AbstractionLevel.ABSTRACT:
                quality_score *= 0.9  # 抽象层级质量略低
        
        # 确保质量得分在合理范围内
        return max(0.1, min(2.0, quality_score))
    
    def _calculate_type_diversity_weights(self, type_distribution: Dict, total_elements: int) -> Dict:
        """计算类型多样性权重，平衡不同类型元素的生成"""
        weights = {}
        
        # 计算每种类型的理想占比（均匀分布）
        ideal_ratio = 1.0 / len(type_distribution) if type_distribution else 1.0
        
        for symbol_type, count in type_distribution.items():
            actual_ratio = count / total_elements
            
            # 多样性权重：稀少类型获得更高权重
            if actual_ratio < ideal_ratio:
                # 稀少类型：权重提升
                diversity_weight = 1.0 + (ideal_ratio - actual_ratio) * 2.0
            else:
                # 过度代表的类型：权重降低
                diversity_weight = 1.0 - (actual_ratio - ideal_ratio) * 0.5
            
            # 确保权重在合理范围内
            weights[symbol_type] = max(0.5, min(1.5, diversity_weight))
        
        logger.debug(f"类型多样性权重: {weights}")
        return weights
    
    def _calculate_adaptive_threshold_layer1(self, quality_scores: Dict[str, float], n: int) -> float:
        """计算第1层的自适应阈值"""
        if not quality_scores:
            return 0.3  # 默认阈值
        
        # 基于质量分布的自适应阈值
        avg_quality = sum(quality_scores.values()) / len(quality_scores)
        quality_std = (sum((q - avg_quality) ** 2 for q in quality_scores.values()) / len(quality_scores)) ** 0.5
        
        # 基础阈值计算
        base_threshold = 0.3
        
        # 质量调节：平均质量高时适当提高阈值
        quality_adjustment = (avg_quality - 1.0) * 0.2
        
        # 数量调节：元素过少时降低阈值，过多时提高阈值
        if n <= 3:
            quantity_adjustment = -0.1  # 元素少时放宽要求
        elif n >= 8:
            quantity_adjustment = 0.1   # 元素多时严格要求
        else:
            quantity_adjustment = 0.0
        
        # 多样性调节：质量差异大时降低阈值（包容性更强）
        diversity_adjustment = -quality_std * 0.1
        
        adaptive_threshold = base_threshold + quality_adjustment + quantity_adjustment + diversity_adjustment
        
        # 确保阈值在合理范围内
        adaptive_threshold = max(0.1, min(0.7, adaptive_threshold))
        
        return adaptive_threshold

    def generate_layer2_rules(self, experience: EOCATR_Tuple) -> List[RuleCandidate]:
        """第2层：动态二元素规律生成 (Cₙ²) - 增强版"""
        candidates = []
        all_elements = experience.get_non_null_elements()
        result_element = experience.get_element_by_type(SymbolType.RESULT)
        
        if not result_element:
            logger.warning("未找到result元素，跳过第2层规律生成")
            return candidates
        
        # 获取可用于模式的元素（排除result）
        pattern_elements = [e for e in all_elements if e.symbol_type != SymbolType.RESULT]
        n = len(pattern_elements)  # 动态计算可用元素数量
        
        if n < 2:
            logger.warning(f"可用模式元素少于2个(n={n})，跳过第2层规律生成")
            return candidates
        
        # 数学化的Cₙ²生成：从n个元素中选择2个，共C(n,2)种组合
        from itertools import combinations
        max_combinations = n * (n - 1) // 2  # C(n,2)公式
        logger.info(f"第2层：从{n}个元素中生成C{n}²={max_combinations}个二元素规律")
        
        # === 新增：智能元素质量评估和兼容性矩阵 ===
        element_quality_scores = {}
        for element in pattern_elements:
            quality_score = self._assess_element_quality(element)
            element_quality_scores[element.symbol_id] = quality_score
        
        # 构建语义兼容性矩阵
        compatibility_matrix = self._build_semantic_compatibility_matrix(pattern_elements)
        
        # 计算高级过滤策略的动态参数
        filtering_params = self._calculate_advanced_filtering_params(pattern_elements, result_element, n)
        
        logger.info(f"第2层智能评估：平均元素质量={sum(element_quality_scores.values())/n:.3f}, "
                   f"兼容性阈值={filtering_params['compatibility_threshold']:.3f}, "
                   f"多样性加权={filtering_params['diversity_boost']:.3f}")
        
        # 生成所有可能的二元素组合
        all_pairs = list(combinations(pattern_elements, 2))
        
        # === 增强的智能配对评分和排序 ===
        scored_pairs = []
        for pair in all_pairs:
            elem1, elem2 = pair
            
            # 计算增强的语义得分（融合多个维度）
            base_semantic_score = self._calculate_pair_semantic_score(pair, result_element)
            
            # 质量权重组合
            quality_weight = (element_quality_scores[elem1.symbol_id] + 
                            element_quality_scores[elem2.symbol_id]) / 2
            
            # 兼容性权重（从兼容性矩阵获取）
            compatibility_weight = compatibility_matrix.get((elem1.symbol_id, elem2.symbol_id), 0.5)
            
            # 类型协同权重
            synergy_weight = self._calculate_type_synergy_weight(elem1.symbol_type, elem2.symbol_type)
            
            # 多样性权重（奖励不同类型的组合）
            diversity_weight = 1.0 + filtering_params['diversity_boost'] if elem1.symbol_type != elem2.symbol_type else 1.0
            
            # 综合语义得分 = 基础得分 * 质量权重 * 兼容性权重 * 协同权重 * 多样性权重
            enhanced_semantic_score = (base_semantic_score * quality_weight * 
                                     compatibility_weight * synergy_weight * diversity_weight)
            
            # 高级过滤：多维度筛选
            if enhanced_semantic_score < filtering_params['compatibility_threshold']:
                self.generation_stats['semantic_filtered'] += 1
                continue
            
            # 逻辑矛盾检查
            if self.semantic_validator.check_logical_contradiction(list(pair) + [result_element]):
                self.generation_stats['logical_filtered'] += 1
                continue
            
            # 冗余检查：避免生成过于相似的规律
            if self._is_pair_redundant(pair, scored_pairs, threshold=0.8):
                self.generation_stats['semantic_filtered'] += 1
                continue
            
            scored_pairs.append({
                'pair': pair,
                'enhanced_score': enhanced_semantic_score,
                'base_score': base_semantic_score,
                'quality_weight': quality_weight,
                'compatibility_weight': compatibility_weight,
                'synergy_weight': synergy_weight,
                'diversity_weight': diversity_weight
            })
        
        # 按增强语义得分排序，优先生成高得分的组合
        scored_pairs.sort(key=lambda x: x['enhanced_score'], reverse=True)
        
        # === 智能数量控制：基于质量分布动态决定生成数量 ===
        if scored_pairs:
            avg_score = sum(p['enhanced_score'] for p in scored_pairs) / len(scored_pairs)
            score_std = (sum((p['enhanced_score'] - avg_score) ** 2 for p in scored_pairs) / len(scored_pairs)) ** 0.5
            
            # 如果得分分布较为集中且平均质量高，可以生成更多规律
            if score_std < 0.2 and avg_score > 0.6:
                max_generate = min(20, len(scored_pairs))  # 高质量场景增加生成数量
            elif score_std > 0.4:
                max_generate = min(8, len(scored_pairs))   # 质量差异大时减少生成数量
            else:
                max_generate = min(15, len(scored_pairs))  # 标准生成数量
        else:
            max_generate = 0
        
        top_pairs = scored_pairs[:max_generate]
        
        # 生成规律候选
        for pair_info in top_pairs:
            pair = pair_info['pair']
            enhanced_score = pair_info['enhanced_score']
            
            candidate = RuleCandidate(
                rule_id="",
                source_tuple=experience,
                pattern_elements=list(pair),
                prediction_element=result_element,
                generation_layer=2,
                generation_method=(f"智能二元素规律_C{n}2_Q{pair_info['quality_weight']:.2f}_"
                                 f"S{pair_info['synergy_weight']:.2f}_D{pair_info['diversity_weight']:.2f}"),
                semantic_score=enhanced_score,
                logical_score=0.8
            )
            candidates.append(candidate)
            self.generation_stats['layer2_generated'] += 1
            logger.debug(f"生成智能二元素规律: {pair[0].content}+{pair[1].content} -> {result_element.content} "
                        f"(增强得分: {enhanced_score:.3f}, 基础: {pair_info['base_score']:.3f}, "
                        f"质量: {pair_info['quality_weight']:.3f}, 协同: {pair_info['synergy_weight']:.3f})")
        
        logger.info(f"第2层完成：实际生成 {len(candidates)} 个二元素规律（理论最大值: {max_combinations}，"
                   f"筛选后: {len(scored_pairs)}，智能选择: {max_generate}）")
        return candidates
    
    def _build_semantic_compatibility_matrix(self, elements: List[SymbolicElement]) -> Dict[Tuple[str, str], float]:
        """构建元素间的语义兼容性矩阵"""
        matrix = {}
        
        for i, elem1 in enumerate(elements):
            for j, elem2 in enumerate(elements[i+1:], i+1):
                # 计算两个元素的语义兼容性
                compatibility = self.semantic_validator.validate_semantic_compatibility([elem1, elem2])
                
                # 考虑类型兼容性
                type_compatibility = self._get_type_compatibility_score(elem1.symbol_type, elem2.symbol_type)
                
                # 综合兼容性得分
                overall_compatibility = (compatibility * 0.7 + type_compatibility * 0.3)
                
                # 双向存储
                matrix[(elem1.symbol_id, elem2.symbol_id)] = overall_compatibility
                matrix[(elem2.symbol_id, elem1.symbol_id)] = overall_compatibility
        
        return matrix
    
    def _calculate_advanced_filtering_params(self, elements: List[SymbolicElement], 
                                           result_element: SymbolicElement, n: int) -> Dict[str, float]:
        """计算高级过滤策略的动态参数"""
        params = {}
        
        # 基于元素数量调整兼容性阈值
        if n <= 3:
            base_threshold = 0.2  # 元素少时放宽要求
        elif n >= 6:
            base_threshold = 0.4  # 元素多时提高要求
        else:
            base_threshold = 0.3  # 标准要求
        
        # 基于result元素质量调整阈值
        result_quality = self._assess_element_quality(result_element)
        quality_adjustment = (result_quality - 1.0) * 0.1
        
        params['compatibility_threshold'] = max(0.1, min(0.6, base_threshold + quality_adjustment))
        
        # 多样性加权参数
        type_diversity = len(set(elem.symbol_type for elem in elements))
        if type_diversity >= 4:
            params['diversity_boost'] = 0.2  # 高多样性时给予额外奖励
        elif type_diversity == 1:
            params['diversity_boost'] = 0.0  # 单一类型时无多样性奖励
        else:
            params['diversity_boost'] = 0.1  # 中等多样性
        
        return params
    
    def _calculate_type_synergy_weight(self, type1: SymbolType, type2: SymbolType) -> float:
        """计算两种类型之间的协同权重"""
        # 定义类型协同关系矩阵
        synergy_matrix = {
            # 高协同组合（直接因果链）
            (SymbolType.ACTION, SymbolType.TOOL): 1.3,
            (SymbolType.TOOL, SymbolType.ACTION): 1.3,
            (SymbolType.OBJECT, SymbolType.ACTION): 1.2,
            (SymbolType.ACTION, SymbolType.OBJECT): 1.2,
            (SymbolType.ENVIRONMENT, SymbolType.ACTION): 1.1,
            (SymbolType.ACTION, SymbolType.ENVIRONMENT): 1.1,
            
            # 中等协同组合（情境组合）
            (SymbolType.ENVIRONMENT, SymbolType.OBJECT): 1.0,
            (SymbolType.OBJECT, SymbolType.ENVIRONMENT): 1.0,
            (SymbolType.CHARACTER, SymbolType.ACTION): 1.0,
            (SymbolType.ACTION, SymbolType.CHARACTER): 1.0,
            (SymbolType.OBJECT, SymbolType.TOOL): 0.9,
            (SymbolType.TOOL, SymbolType.OBJECT): 0.9,
            
            # 低协同组合（状态组合）
            (SymbolType.CHARACTER, SymbolType.ENVIRONMENT): 0.8,
            (SymbolType.ENVIRONMENT, SymbolType.CHARACTER): 0.8,
            (SymbolType.CHARACTER, SymbolType.OBJECT): 0.8,
            (SymbolType.OBJECT, SymbolType.CHARACTER): 0.8,
            (SymbolType.CHARACTER, SymbolType.TOOL): 0.7,
            (SymbolType.TOOL, SymbolType.CHARACTER): 0.7,
        }
        
        # 同类型组合协同度较低
        if type1 == type2:
            return 0.6
        
        return synergy_matrix.get((type1, type2), 0.8)  # 默认中低协同度
    
    def _get_type_compatibility_score(self, type1: SymbolType, type2: SymbolType) -> float:
        """获取两种类型的兼容性得分"""
        # 直接复用协同权重逻辑，但进行归一化
        synergy = self._calculate_type_synergy_weight(type1, type2)
        # 将协同权重转换为0-1之间的兼容性得分
        return min(1.0, synergy / 1.3)
    
    def _is_pair_redundant(self, new_pair: Tuple[SymbolicElement, SymbolicElement], 
                           existing_pairs: List[Dict], threshold: float = 0.8) -> bool:
        """检查新配对是否与现有配对冗余"""
        new_elem1, new_elem2 = new_pair
        
        for existing_info in existing_pairs:
            exist_elem1, exist_elem2 = existing_info['pair']
            
            # 计算语义相似度
            similarity1 = new_elem1.get_semantic_similarity(exist_elem1)
            similarity2 = new_elem2.get_semantic_similarity(exist_elem2)
            cross_similarity1 = new_elem1.get_semantic_similarity(exist_elem2)
            cross_similarity2 = new_elem2.get_semantic_similarity(exist_elem1)
            
            # 考虑两种排列的相似度
            max_similarity = max(
                (similarity1 + similarity2) / 2,      # 直接对应
                (cross_similarity1 + cross_similarity2) / 2  # 交叉对应
            )
            
            if max_similarity >= threshold:
                return True
        
        return False
    
    def _calculate_pair_semantic_score(self, pair: Tuple[SymbolicElement, SymbolicElement], result_element: SymbolicElement) -> float:
        """计算二元素模式的语义得分"""
        elem1, elem2 = pair
        
        # 使用语义验证器计算三元组兼容性
        compatibility_score = self.semantic_validator.validate_semantic_compatibility([elem1, elem2, result_element])
        
        # 计算类型组合的重要性权重
        type_combination_weights = {
            # 高价值组合（直接因果关系）
            (SymbolType.ACTION, SymbolType.TOOL): 1.0,      # 行动+工具 -> 结果
            (SymbolType.OBJECT, SymbolType.ACTION): 0.95,   # 对象+行动 -> 结果
            (SymbolType.ENVIRONMENT, SymbolType.ACTION): 0.9, # 环境+行动 -> 结果
            (SymbolType.CHARACTER, SymbolType.ACTION): 0.85,  # 特征+行动 -> 结果
            
            # 中等价值组合（情境组合）
            (SymbolType.ENVIRONMENT, SymbolType.OBJECT): 0.8, # 环境+对象 -> 结果
            (SymbolType.OBJECT, SymbolType.TOOL): 0.75,       # 对象+工具 -> 结果
            (SymbolType.ENVIRONMENT, SymbolType.TOOL): 0.7,   # 环境+工具 -> 结果
            
            # 低价值组合（状态组合）
            (SymbolType.CHARACTER, SymbolType.ENVIRONMENT): 0.6, # 特征+环境 -> 结果
            (SymbolType.CHARACTER, SymbolType.OBJECT): 0.6,      # 特征+对象 -> 结果
            (SymbolType.CHARACTER, SymbolType.TOOL): 0.55,       # 特征+工具 -> 结果
        }
        
        # 获取类型组合权重（考虑顺序无关性）
        type_pair = (elem1.symbol_type, elem2.symbol_type)
        reverse_pair = (elem2.symbol_type, elem1.symbol_type)
        weight = type_combination_weights.get(type_pair, type_combination_weights.get(reverse_pair, 0.5))
        
        # 计算个体元素与结果的因果强度
        elem1_result_score = self.semantic_validator.validate_semantic_compatibility([elem1, result_element])
        elem2_result_score = self.semantic_validator.validate_semantic_compatibility([elem2, result_element])
        individual_causality = (elem1_result_score + elem2_result_score) / 2
        
        # 综合得分：兼容性 * 权重 + 个体因果强度 * 0.3
        final_score = compatibility_score * weight + individual_causality * 0.3
        
        # 确保得分在合理范围内
        return max(0.1, min(1.0, final_score))
    
    def _calculate_single_element_semantic_score(self, pattern_element: SymbolicElement, result_element: SymbolicElement) -> float:
        """计算单元素模式的语义得分"""
        # 使用语义验证器计算兼容性
        compatibility_score = self.semantic_validator.validate_semantic_compatibility([pattern_element, result_element])
        
        # 根据元素类型调整得分权重和基础得分
        type_configs = {
            SymbolType.ACTION: {'weight': 1.0, 'base_boost': 0.2},      # 行动元素权重最高，有基础提升
            SymbolType.OBJECT: {'weight': 0.9, 'base_boost': 0.0},      # 对象元素权重较高
            SymbolType.ENVIRONMENT: {'weight': 0.8, 'base_boost': 0.0}, # 环境元素权重中等
            SymbolType.TOOL: {'weight': 0.8, 'base_boost': 0.1},        # 工具元素权重中等，有小幅提升
            SymbolType.CHARACTER: {'weight': 0.7, 'base_boost': 0.0}    # 特征元素权重较低
        }
        
        config = type_configs.get(pattern_element.symbol_type, {'weight': 0.6, 'base_boost': 0.0})
        weight = config['weight']
        base_boost = config['base_boost']
        
        # 计算最终得分：(兼容性得分 + 基础提升) * 权重
        semantic_score = (compatibility_score + base_boost) * weight
        
        # 确保得分在合理范围内
        return max(0.1, min(1.0, semantic_score))
    
    def generate_layer3_rules(self, experience: EOCATR_Tuple, 
                             layer2_success_rate: float = 0.0) -> List[RuleCandidate]:
        """第3层：三元素情境规律生成 (基于前两层成功率动态决定)"""
        candidates = []
        
        # 如果前两层成功率低，不生成第3层
        if layer2_success_rate < 0.3:
            logger.info(f"第2层成功率过低 ({layer2_success_rate:.3f})，跳过第3层生成")
            return candidates
        
        elements = experience.get_non_null_elements()
        result_element = experience.get_element_by_type(SymbolType.RESULT)
        
        if not result_element:
            return candidates
        
        # 获取非结果元素
        pattern_elements = [e for e in elements if e.symbol_type != SymbolType.RESULT]
        
        # 生成三元素组合（限制数量，只选择最有价值的）
        if len(pattern_elements) >= 3:
            from itertools import combinations
            three_combinations = list(combinations(pattern_elements, 3))
            
            # 按语义相关性排序，只取前3个
            scored_combinations = []
            for combo in three_combinations:
                semantic_score = self.semantic_validator.validate_semantic_compatibility(list(combo))
                if semantic_score >= 0.5 and not self.semantic_validator.check_logical_contradiction(list(combo)):
                    scored_combinations.append((combo, semantic_score))
            
            # 排序并取前3个
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
            top_combinations = scored_combinations[:3]
            
            for combo, semantic_score in top_combinations:
                candidate = RuleCandidate(
                    rule_id="",
                    source_tuple=experience,
                    pattern_elements=list(combo),
                    prediction_element=result_element,
                    generation_layer=3,
                    generation_method="三元素情境规律",
                    semantic_score=semantic_score,
                    logical_score=0.7
                )
                candidates.append(candidate)
                self.generation_stats['layer3_generated'] += 1
        
        logger.info(f"第3层生成 {len(candidates)} 个三元素规律")
        return candidates

    def generate_mirror_rules(self, candidates: List[RuleCandidate]) -> List[RuleCandidate]:
        """智能镜像规律生成 - 基于语义相似度和对立性分析"""
        mirror_candidates = []
        
        # 分层处理镜像生成
        for candidate in candidates:
            # 检查是否适合生成镜像
            if self._should_generate_mirror(candidate):
                mirror_candidate = self._create_enhanced_mirror_rule(candidate)
                if mirror_candidate:
                    mirror_candidates.append(mirror_candidate)
                    # 建立双向镜像关系
                    candidate.mirror_rule_id = mirror_candidate.rule_id
                    mirror_candidate.mirror_rule_id = candidate.rule_id
                    self.generation_stats['mirror_generated'] += 1
                    logger.debug(f"生成镜像规律: {candidate.rule_id} -> {mirror_candidate.rule_id}")
                else:
                    logger.debug(f"无法为规律 {candidate.rule_id} 生成有效镜像")
            else:
                logger.debug(f"规律 {candidate.rule_id} 不适合生成镜像")
        
        logger.info(f"智能镜像生成完成：从{len(candidates)}个规律中生成{len(mirror_candidates)}个镜像规律")
        return mirror_candidates
    
    def _should_generate_mirror(self, candidate: RuleCandidate) -> bool:
        """判断是否应该为规律生成镜像"""
        # 高语义得分的规律更值得生成镜像
        if candidate.semantic_score < 0.5:
            return False
        
        # 检查是否包含可镜像的概念
        mirrorable_concepts = {'攻击', '逃跑', '靠近', '远离', '受伤', '安全', '成功', '失败', '获得', '失去', '前进', '后退'}
        
        # 检查模式元素和预测元素
        all_contents = [elem.content for elem in candidate.pattern_elements] + [candidate.prediction_element.content]
        has_mirrorable = any(content in mirrorable_concepts for content in all_contents)
        
        # 对于高层级规律更谨慎
        if candidate.generation_layer >= 3 and candidate.semantic_score < 0.7:
            return False
        
        return has_mirrorable

    def _create_enhanced_mirror_rule(self, original: RuleCandidate) -> Optional[RuleCandidate]:
        """创建增强镜像规律 - 支持多级镜像映射和语义验证"""
        from symbolic_core_v3 import create_element
        
        # 增强的镜像映射规则 - 分类和层次化
        mirror_mappings = {
            # 行动对立
            '攻击': '逃跑', '逃跑': '攻击',
            '靠近': '远离', '远离': '靠近', 
            '前进': '后退', '后退': '前进',
            '追赶': '躲避', '躲避': '追赶',
            
            # 结果对立
            '受伤': '安全', '安全': '受伤',
            '成功': '失败', '失败': '成功',
            '获得': '失去', '失去': '获得',
            '胜利': '失败', '失败': '胜利',
            
            # 状态对立
            '饥饿': '饱腹', '饱腹': '饥饿',
            '疲劳': '精力充沛', '精力充沛': '疲劳',
            '害怕': '勇敢', '勇敢': '害怕',
            
            # 方向对立
            '上': '下', '下': '上',
            '左': '右', '右': '左',
            '北': '南', '南': '北',
            '东': '西', '西': '东'
        }
        
        # 尝试创建镜像模式元素
        mirror_pattern_elements = []
        mirror_success_count = 0
        
        for elem in original.pattern_elements:
            mirror_content = mirror_mappings.get(elem.content)
            if mirror_content:
                # 创建镜像元素，保持语义标签的一致性
                mirror_tags = self._generate_mirror_semantic_tags(elem.semantic_tags, mirror_content)
                mirror_elem = create_element(
                    symbol_type=elem.symbol_type,
                    content=mirror_content,
                    abstraction_level=elem.abstraction_level,
                    semantic_tags=mirror_tags
                )
                mirror_pattern_elements.append(mirror_elem)
                mirror_success_count += 1
            else:
                # 如果无法镜像，使用原元素
                mirror_pattern_elements.append(elem)
        
        # 尝试创建镜像预测元素
        mirror_prediction_content = mirror_mappings.get(original.prediction_element.content)
        if mirror_prediction_content:
            mirror_prediction_tags = self._generate_mirror_semantic_tags(
                original.prediction_element.semantic_tags, 
                mirror_prediction_content
            )
            mirror_prediction_elem = create_element(
                symbol_type=original.prediction_element.symbol_type,
                content=mirror_prediction_content,
                abstraction_level=original.prediction_element.abstraction_level,
                semantic_tags=mirror_prediction_tags
            )
            mirror_success_count += 1
        else:
            # 如果无法镜像预测，尝试生成语义对立预测
            mirror_prediction_elem = self._generate_semantic_opposite_result(original.prediction_element)
            if mirror_prediction_elem:
                mirror_success_count += 1
            else:
                return None
        
        # 验证镜像规律的质量 - 至少要有50%的元素能够镜像
        total_elements = len(original.pattern_elements) + 1  # +1 for prediction
        mirror_ratio = mirror_success_count / total_elements
        
        if mirror_ratio < 0.5:
            logger.debug(f"镜像比例过低 ({mirror_ratio:.3f})，放弃生成镜像规律")
            return None
        
        # 计算镜像规律的语义得分
        mirror_semantic_score = self._calculate_mirror_semantic_score(
            original.semantic_score, mirror_ratio
        )
        
        # 创建镜像规律候选
        mirror_candidate = RuleCandidate(
            rule_id="",
            source_tuple=original.source_tuple,
            pattern_elements=mirror_pattern_elements,
            prediction_element=mirror_prediction_elem,
            generation_layer=original.generation_layer,
            generation_method=f"智能镜像_{original.generation_method}",
            semantic_score=mirror_semantic_score,
            logical_score=original.logical_score * 0.95  # 镜像规律逻辑得分略低
        )
        
        return mirror_candidate
    
    def _generate_mirror_semantic_tags(self, original_tags: List[str], mirror_content: str) -> List[str]:
        """为镜像元素生成相应的语义标签"""
        mirror_tags = []
        
        # 保留非对立性标签
        neutral_tags = []
        for tag in original_tags:
            if not any(opposite in tag for opposite in ['正', '负', '好', '坏', '成功', '失败']):
                neutral_tags.append(tag)
        
        # 添加镜像特定标签
        mirror_tags.extend(neutral_tags)
        mirror_tags.append(f"镜像_{mirror_content}")
        mirror_tags.append("对立概念")
        
        return mirror_tags
    
    def _generate_semantic_opposite_result(self, original_result: SymbolicElement) -> Optional[SymbolicElement]:
        """生成语义对立的结果元素"""
        from symbolic_core_v3 import create_element
        
        # 基于语义标签判断对立概念
        content = original_result.content
        tags = original_result.semantic_tags
        
        # 基于内容的对立推理
        if '成功' in content or '胜利' in content:
            opposite_content = '失败'
        elif '失败' in content:
            opposite_content = '成功'
        elif '受伤' in content or '伤害' in content:
            opposite_content = '安全'
        elif '安全' in content:
            opposite_content = '受伤'
        elif '获得' in content:
            opposite_content = '失去'
        elif '失去' in content:
            opposite_content = '获得'
        else:
            # 如果无法判断对立概念，返回None
            return None
        
        # 创建对立结果元素
        opposite_tags = [tag for tag in tags if '正面' not in tag and '负面' not in tag]
        opposite_tags.append(f"对立_{content}")
        
        return create_element(
            symbol_type=original_result.symbol_type,
            content=opposite_content,
            abstraction_level=original_result.abstraction_level,
            semantic_tags=opposite_tags
        )
    
    def _calculate_mirror_semantic_score(self, original_score: float, mirror_ratio: float) -> float:
        """计算镜像规律的语义得分"""
        # 基础得分：原始得分 * 镜像质量系数
        base_score = original_score * 0.85  # 镜像规律基础上略低于原规律
        
        # 镜像比例奖励：镜像比例越高，得分越高
        ratio_bonus = mirror_ratio * 0.15
        
        # 确保得分在合理范围内
        final_score = base_score + ratio_bonus
        return max(0.1, min(1.0, final_score))

class PruningValidator:
    """智能剪枝验证器 - 多维度质量评估和自适应学习"""
    
    def __init__(self):
        self.validation_history: Dict[str, List[Dict]] = {}
        
        # 动态质量阈值 - 基于经验数量自适应调整
        self.base_quality_thresholds = {
            1: 0.6,  # 第1层基础阈值
            2: 0.7,  # 第2层基础阈值  
            3: 0.8   # 第3层基础阈值
        }
        
        # 验证统计信息
        self.validation_stats = {
            'total_validated': 0,
            'total_passed': 0,
            'total_failed': 0,
            'layer_stats': {},
            'semantic_score_distribution': [],
            'confidence_distribution': []
        }
        
        # 自适应学习参数
        self.learning_window = 100  # 学习窗口大小
        self.threshold_adjustment_factor = 0.05  # 阈值调整因子
        
        logger.info("智能剪枝验证器初始化完成")

    def validate_candidate(self, candidate: RuleCandidate, 
                          experiences: List[EOCATR_Tuple]) -> bool:
        """智能候选规律验证 - 多维度评估和自适应阈值"""
        support_count = 0
        rejection_count = 0
        neutral_count = 0
        evidence_strength_sum = 0.0
        
        # 分批验证，提高效率
        relevant_experiences = [exp for exp in experiences 
                              if exp.tuple_id != candidate.source_tuple.tuple_id]
        
        for exp in relevant_experiences:
            validation_result, evidence_strength = self._validate_against_experience_enhanced(candidate, exp)
            if validation_result == 1:  # 支持
                support_count += 1
                evidence_strength_sum += evidence_strength
            elif validation_result == -1:  # 反对
                rejection_count += 1
                evidence_strength_sum += evidence_strength
            else:  # 中性/不相关
                neutral_count += 1
        
        # 更新候选规律的验证统计
        candidate.support_count = support_count
        candidate.rejection_count = rejection_count
        
        # 计算增强置信度 - 考虑证据强度
        total_evidence = support_count + rejection_count
        if total_evidence > 0:
            base_confidence = support_count / total_evidence
            # 证据强度调整
            avg_evidence_strength = evidence_strength_sum / total_evidence
            candidate.confidence = base_confidence * (0.7 + 0.3 * avg_evidence_strength)
        else:
            # 无直接证据时，基于语义得分给予基础置信度
            candidate.confidence = max(0.3, candidate.semantic_score * 0.6)
        
        # 计算验证质量分数
        validation_quality = self._calculate_validation_quality(
            candidate, support_count, rejection_count, neutral_count, len(relevant_experiences)
        )
        
        # 记录详细验证历史
        validation_record = {
            'rule_id': candidate.rule_id,
            'support_count': support_count,
            'rejection_count': rejection_count,
            'neutral_count': neutral_count,
            'confidence': candidate.confidence,
            'total_score': candidate.calculate_total_score(),
            'validation_quality': validation_quality,
            'evidence_strength_avg': evidence_strength_sum / max(1, total_evidence),
            'validated_time': datetime.now().isoformat()
        }
        
        if candidate.rule_id not in self.validation_history:
            self.validation_history[candidate.rule_id] = []
        self.validation_history[candidate.rule_id].append(validation_record)
        
        # 获取自适应阈值
        adaptive_threshold = self._get_adaptive_threshold(candidate.generation_layer, len(relevant_experiences))
        
        # 判断是否通过验证 - 使用二要素验证模型
        total_score = candidate.calculate_total_score()
        
        # 二要素验证：语义质量(50%) + 实证质量(50%)
        passed, dual_factor_score = self._validate_dual_factor(candidate, relevant_experiences)
        
        # 保留原有的三重验证逻辑作为对比（注释）
        # original_passed = (total_score >= adaptive_threshold and 
        #                   validation_quality >= 0.4 and
        #                   candidate.confidence >= 0.3)
        
        # 更新统计信息
        self._update_validation_stats(candidate, passed, validation_quality)
        
        logger.info(f"智能验证: {candidate.rule_id[:12]}... - 支持:{support_count}, 反对:{rejection_count}, "
                   f"置信度:{candidate.confidence:.3f}, 总分:{total_score:.3f}, "
                   f"质量:{validation_quality:.3f}, 阈值:{adaptive_threshold:.3f}, "
                   f"通过:{'是' if passed else '否'}")
        
        return passed

    def _validate_against_experience_enhanced(self, candidate: RuleCandidate, 
                                           experience: EOCATR_Tuple) -> Tuple[int, float]:
        """增强单个经验验证 - 返回验证结果和证据强度"""
        # 检查模式是否匹配
        pattern_match_score = self._calculate_pattern_match(candidate.pattern_elements, experience)
        
        if pattern_match_score < 0.3:  # 模式不匹配，不相关
            return 0, 0.0
        
        # 检查预测是否正确
        actual_result = experience.get_element_by_type(SymbolType.RESULT)
        if not actual_result:
            return 0, 0.0
        
        # 计算预测准确性
        prediction_accuracy = self._calculate_prediction_accuracy(
            candidate.prediction_element, actual_result
        )
        
        # 证据强度 = 模式匹配度 * 预测准确性
        evidence_strength = pattern_match_score * max(0.1, prediction_accuracy)
        
        if prediction_accuracy >= 0.7:  # 预测正确
            return 1, evidence_strength
        elif prediction_accuracy <= 0.3:  # 预测错误
            return -1, evidence_strength
        else:  # 预测模糊
            return 0, evidence_strength
    
    def _calculate_prediction_accuracy(self, predicted: SymbolicElement, actual: SymbolicElement) -> float:
        """计算预测准确性"""
        if predicted.content == actual.content:
            return 1.0
        
        # 语义相似性检查
        predicted_tags = set(predicted.semantic_tags)
        actual_tags = set(actual.semantic_tags)
        
        if predicted_tags and actual_tags:
            common_tags = predicted_tags & actual_tags
            union_tags = predicted_tags | actual_tags
            semantic_similarity = len(common_tags) / len(union_tags)
            
            # 如果是镜像关系，也算部分正确
            if any('镜像' in tag or '对立' in tag for tag in predicted_tags):
                if self._are_opposite_concepts(predicted.content, actual.content):
                    return 0.6  # 镜像预测给予中等分数
            
            return semantic_similarity
        
        return 0.0
    
    def _are_opposite_concepts(self, content1: str, content2: str) -> bool:
        """检查两个概念是否为对立关系"""
        opposite_pairs = [
            ('成功', '失败'), ('获得', '失去'), ('受伤', '安全'),
            ('攻击', '逃跑'), ('靠近', '远离'), ('前进', '后退')
        ]
        
        for pair in opposite_pairs:
            if (content1 in pair[0] and content2 in pair[1]) or \
               (content1 in pair[1] and content2 in pair[0]):
                return True
        return False
    
    def _calculate_validation_quality(self, candidate: RuleCandidate, 
                                    support_count: int, rejection_count: int, 
                                    neutral_count: int, total_experiences: int) -> float:
        """计算验证质量分数"""
        if total_experiences == 0:
            return 0.0
        
        # 基础质量：有效验证比例
        effective_validation_ratio = (support_count + rejection_count) / total_experiences
        
        # 证据一致性：支持证据的一致性
        total_evidence = support_count + rejection_count
        if total_evidence > 0:
            evidence_consistency = support_count / total_evidence
        else:
            evidence_consistency = 0.5
        
        # 样本充分性：验证样本数量的充分性
        sample_adequacy = min(1.0, total_evidence / 5.0)  # 5个证据样本为充分
        
        # 综合质量分数
        quality_score = (effective_validation_ratio * 0.4 + 
                        evidence_consistency * 0.4 + 
                        sample_adequacy * 0.2)
        
        return quality_score
    
    def _get_adaptive_threshold(self, layer: int, experience_count: int) -> float:
        """获取自适应质量阈值"""
        base_threshold = self.base_quality_thresholds.get(layer, 0.7)
        
        # 基于经验数量调整阈值
        if experience_count < 10:
            # 经验太少，降低阈值
            adjustment = -0.1
        elif experience_count > 50:
            # 经验充足，提高阈值
            adjustment = 0.05
        else:
            adjustment = 0.0
        
        # 基于历史表现调整阈值
        if layer in self.validation_stats.get('layer_stats', {}):
            layer_stats = self.validation_stats['layer_stats'][layer]
            if layer_stats['total_validated'] > 20:  # 有足够的历史数据
                success_rate = layer_stats['total_passed'] / layer_stats['total_validated']
                if success_rate < 0.3:  # 成功率太低，降低阈值
                    adjustment -= 0.05
                elif success_rate > 0.8:  # 成功率太高，提高阈值
                    adjustment += 0.05
        
        final_threshold = max(0.3, min(0.9, base_threshold + adjustment))
        return final_threshold
    
    def _update_validation_stats(self, candidate: RuleCandidate, passed: bool, validation_quality: float):
        """更新验证统计信息"""
        self.validation_stats['total_validated'] += 1
        
        if passed:
            self.validation_stats['total_passed'] += 1
        else:
            self.validation_stats['total_failed'] += 1
        
        # 更新层级统计
        layer = candidate.generation_layer
        if layer not in self.validation_stats['layer_stats']:
            self.validation_stats['layer_stats'][layer] = {
                'total_validated': 0,
                'total_passed': 0,
                'total_failed': 0
            }
        
        self.validation_stats['layer_stats'][layer]['total_validated'] += 1
        if passed:
            self.validation_stats['layer_stats'][layer]['total_passed'] += 1
        else:
            self.validation_stats['layer_stats'][layer]['total_failed'] += 1
        
        # 记录得分分布
        self.validation_stats['semantic_score_distribution'].append(candidate.semantic_score)
        self.validation_stats['confidence_distribution'].append(candidate.confidence)
        
        # 保持分布数据在合理范围内
        if len(self.validation_stats['semantic_score_distribution']) > self.learning_window:
            self.validation_stats['semantic_score_distribution'].pop(0)
        if len(self.validation_stats['confidence_distribution']) > self.learning_window:
            self.validation_stats['confidence_distribution'].pop(0)
    
    def _validate_against_experience(self, candidate: RuleCandidate, 
                                   experience: EOCATR_Tuple) -> int:
        """对单个经验进行验证（保持向后兼容）"""
        result, _ = self._validate_against_experience_enhanced(candidate, experience)
        return result

    def _calculate_pattern_match(self, pattern_elements: List[SymbolicElement], 
                               experience: EOCATR_Tuple) -> float:
        """计算模式匹配度"""
        exp_elements = experience.get_non_null_elements()
        
        matched_scores = []
        for pattern_elem in pattern_elements:
            best_match_score = 0.0
            for exp_elem in exp_elements:
                if exp_elem.symbol_type == pattern_elem.symbol_type:
                    similarity = pattern_elem.get_semantic_similarity(exp_elem)
                    best_match_score = max(best_match_score, similarity)
            matched_scores.append(best_match_score)
        
        # 平均匹配得分
        return sum(matched_scores) / len(matched_scores) if matched_scores else 0.0

    def _validate_dual_factor(self, candidate: RuleCandidate, experiences: List[EOCATR_Tuple]) -> Tuple[bool, float]:
        """
        二要素验证模型：语义质量(50%) + 实证质量(50%)
        替换原有的三重验证条件，解决验证过于严格的问题
        """
        # 要素1：语义质量 (50%权重)
        semantic_quality = candidate.semantic_score * 0.5
        
        # 要素2：实证质量 (50%权重) 
        empirical_quality = self._calculate_empirical_quality(candidate, experiences) * 0.5
        
        # 综合得分
        dual_factor_score = semantic_quality + empirical_quality
        
        # 简化阈值：0.4 (相比原来的三重条件更宽松)
        validation_threshold = 0.4
        
        passed = dual_factor_score >= validation_threshold
        
        # 详细日志
        logger.info(f"二要素验证: 语义={semantic_quality:.3f}, 实证={empirical_quality:.3f}, "
                   f"综合={dual_factor_score:.3f}, 阈值={validation_threshold:.3f}, "
                   f"通过={'是' if passed else '否'}")
        
        return passed, dual_factor_score
    
    def _calculate_empirical_quality(self, candidate: RuleCandidate, experiences: List[EOCATR_Tuple]) -> float:
        """
        计算实证质量：结合证据支持度和经验充分性
        """
        # 基础证据支持度
        total_evidence = candidate.support_count + candidate.rejection_count
        if total_evidence == 0:
            evidence_ratio = 0.5  # 无证据时给予中性分数
        else:
            evidence_ratio = candidate.support_count / total_evidence
        
        # 经验充分性权重 (经验越多，证据越可信)
        experience_weight = min(1.0, len(experiences) / 3.0)  # 3个经验达到100%权重
        
        # 间接经验支持 (如果有的话)
        indirect_support = self._calculate_indirect_support(candidate, experiences)
        
        # 综合实证质量 = 证据支持度 * 经验权重 + 间接支持
        empirical_quality = (evidence_ratio * experience_weight * 0.8) + (indirect_support * 0.2)
        
        return min(1.0, empirical_quality)
    
    def _calculate_indirect_support(self, candidate: RuleCandidate, experiences: List[EOCATR_Tuple]) -> float:
        """计算间接经验支持度"""
        # 这里可以加入社交学习、类比推理等间接证据
        # 暂时返回基础值，为未来扩展保留接口
        return 0.1  # 给予少量间接支持

class BloomingPruningModel:
    """怒放剪枝模型主类 - 协调整个BMP流程"""
    
    def __init__(self):
        self.semantic_validator = EnhancedSemanticValidator()
        self.blooming_generator = BloomingGenerator(self.semantic_validator)
        self.pruning_validator = PruningValidator()
        self.verified_rules: Dict[str, RuleCandidate] = {}
        self.processing_stats = {
            'total_experiences_processed': 0,
            'total_candidates_generated': 0,
            'total_rules_verified': 0,
            'processing_times': []
        }
        logger.info("BPM怒放剪枝模型初始化完成")

    def process_experience(self, experience: EOCATR_Tuple, 
                         historical_experiences: List[EOCATR_Tuple] = None) -> List[RuleCandidate]:
        """处理单个经验，生成并验证规律"""
        start_time = datetime.now()
        
        if historical_experiences is None:
            historical_experiences = []
        
        logger.info(f"开始处理经验: {experience.tuple_id}")
        
        # 第1阶段：分层生成候选规律
        all_candidates = []
        
        # 第1层：单元素规律
        layer1_candidates = self.blooming_generator.generate_layer1_rules(experience)
        all_candidates.extend(layer1_candidates)
        
        # 第2层：二元素规律
        layer2_candidates = self.blooming_generator.generate_layer2_rules(experience)
        all_candidates.extend(layer2_candidates)
        
        # 第3层：三元素规律（基于第2层成功率）
        layer2_success_rate = self._calculate_layer_success_rate(layer2_candidates, historical_experiences)
        layer3_candidates = self.blooming_generator.generate_layer3_rules(experience, layer2_success_rate)
        all_candidates.extend(layer3_candidates)
        
        # 生成镜像规律
        mirror_candidates = self.blooming_generator.generate_mirror_rules(all_candidates)
        all_candidates.extend(mirror_candidates)
        
        logger.info(f"怒放阶段完成，生成 {len(all_candidates)} 个候选规律")
        
        # 第2阶段：剪枝验证
        verified_candidates = []
        if historical_experiences:
            for candidate in all_candidates:
                if self.pruning_validator.validate_candidate(candidate, historical_experiences):
                    verified_candidates.append(candidate)
                    self.verified_rules[candidate.rule_id] = candidate
        else:
            # 如果没有历史经验，所有候选规律都通过（待后续验证）
            verified_candidates = all_candidates
            for candidate in all_candidates:
                self.verified_rules[candidate.rule_id] = candidate
        
        logger.info(f"剪枝阶段完成，验证通过 {len(verified_candidates)} 个规律")
        
        # 更新统计信息
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        self.processing_stats['total_experiences_processed'] += 1
        self.processing_stats['total_candidates_generated'] += len(all_candidates)
        self.processing_stats['total_rules_verified'] += len(verified_candidates)
        self.processing_stats['processing_times'].append(processing_time)
        
        # 记录处理日志
        logger.info(f"经验处理完成: 耗时{processing_time:.3f}秒, "
                   f"生成{len(all_candidates)}个候选, 验证{len(verified_candidates)}个规律")
        
        return verified_candidates

    def _calculate_layer_success_rate(self, layer2_candidates: List[RuleCandidate],
                                    historical_experiences: List[EOCATR_Tuple]) -> float:
        """计算第2层的成功率"""
        if not layer2_candidates or not historical_experiences:
            return 0.5  # 默认成功率
        
        success_count = 0
        for candidate in layer2_candidates:
            if self.pruning_validator.validate_candidate(candidate, historical_experiences):
                success_count += 1
        
        return success_count / len(layer2_candidates)

    def get_top_rules(self, limit: int = 10) -> List[RuleCandidate]:
        """获取评分最高的规律"""
        sorted_rules = sorted(
            self.verified_rules.values(),
            key=lambda r: r.calculate_total_score(),
            reverse=True
        )
        return sorted_rules[:limit]

    def get_rules_by_layer(self, layer: int) -> List[RuleCandidate]:
        """获取指定层级的规律"""
        return [rule for rule in self.verified_rules.values() 
                if rule.generation_layer == layer]

    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        stats = self.processing_stats.copy()
        
        # 添加生成器统计
        stats.update(self.blooming_generator.generation_stats)
        
        # 计算平均处理时间
        if stats['processing_times']:
            stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
            stats['max_processing_time'] = max(stats['processing_times'])
            stats['min_processing_time'] = min(stats['processing_times'])
        
        # 添加规律统计
        stats['verified_rules_count'] = len(self.verified_rules)
        stats['rules_by_layer'] = {
            f'layer_{i}': len(self.get_rules_by_layer(i)) for i in range(1, 4)
        }
        
        # 计算平均质量分数
        if self.verified_rules:
            total_score = sum(rule.calculate_total_score() for rule in self.verified_rules.values())
            stats['avg_rule_quality'] = total_score / len(self.verified_rules)
        
        return stats
    
    def pruning_phase(self) -> List[str]:
        """剪枝阶段：清理低质量规律"""
        pruned_rule_ids = []
        
        # 定义剪枝阈值
        min_confidence_threshold = 0.2
        max_age_days = 30
        
        current_time = datetime.now()
        rules_to_remove = []
        
        for rule_id, rule in self.verified_rules.items():
            should_prune = False
            
            # 置信度过低的规律
            if rule.calculate_total_score() < min_confidence_threshold:
                should_prune = True
                
            # 过期的规律（创建时间过久且表现不佳）
            if rule.created_time:
                age_days = (current_time - rule.created_time).days
                if age_days > max_age_days and rule.calculate_total_score() < 0.5:
                    should_prune = True
            
            # 反对票过多的规律
            if rule.rejection_count > rule.support_count * 2 and rule.rejection_count > 3:
                should_prune = True
            
            if should_prune:
                rules_to_remove.append(rule_id)
                pruned_rule_ids.append(rule_id)
        
        # 移除被剪枝的规律
        for rule_id in rules_to_remove:
            del self.verified_rules[rule_id]
        
        if pruned_rule_ids:
            logger.info(f"剪枝阶段完成：移除 {len(pruned_rule_ids)} 个低质量规律")
        
        return pruned_rule_ids
    
    def validation_phase(self, validation_experiences: List[EOCATR_Tuple]) -> List[str]:
        """验证阶段：将候选规律提升为正式规律"""
        validated_rule_ids = []
        
        if not validation_experiences:
            return validated_rule_ids
        
        # 提升阈值
        promotion_threshold = 0.6
        min_support_count = 2
        
        for rule_id, rule in self.verified_rules.items():
            # 重新验证规律
            validation_result = self.pruning_validator.validate_candidate(rule, validation_experiences)
            
            # 更新支持/反对计数
            if validation_result:
                rule.support_count += 1
            else:
                rule.rejection_count += 1
            
            # 检查是否可以提升为正式规律
            total_score = rule.calculate_total_score()
            if (total_score >= promotion_threshold and 
                rule.support_count >= min_support_count and
                rule.support_count > rule.rejection_count):
                
                validated_rule_ids.append(rule_id)
                # 提升置信度
                rule.confidence = min(0.95, total_score + 0.1)
        
        if validated_rule_ids:
            logger.info(f"验证阶段完成：{len(validated_rule_ids)} 个规律通过验证提升为正式规律")
        
        return validated_rule_ids

# 示例用法和测试
if __name__ == "__main__":
    from symbolic_core_v3 import create_element, create_tuple, SymbolType, AbstractionLevel
    
    # 创建测试经验
    tiger = create_element(SymbolType.OBJECT, "老虎", AbstractionLevel.CONCRETE, ["动物", "危险"])
    forest = create_element(SymbolType.ENVIRONMENT, "森林", AbstractionLevel.CONCRETE, ["自然"])
    approach = create_element(SymbolType.ACTION, "靠近", AbstractionLevel.CONCRETE, ["移动"])
    spear = create_element(SymbolType.TOOL, "长矛", AbstractionLevel.CONCRETE, ["武器"])
    injured = create_element(SymbolType.RESULT, "受伤", AbstractionLevel.CONCRETE, ["负面"])
    
    experience1 = create_tuple(
        environment=forest,
        object=tiger,
        action=approach,
        tool=spear,
        result=injured,
        confidence=0.9
    )
    
    # 创建历史经验
    rabbit = create_element(SymbolType.OBJECT, "兔子", AbstractionLevel.CONCRETE, ["动物", "食物"])
    food = create_element(SymbolType.RESULT, "食物", AbstractionLevel.CONCRETE, ["正面"])
    
    experience2 = create_tuple(
        environment=forest,
        object=rabbit,
        action=approach,
        result=food,
        confidence=0.8
    )
    
    # 创建BPM模型并处理经验
    bpm_model = BloomingPruningModel()
    
    # 处理第一个经验
    rules1 = bpm_model.process_experience(experience1)
    print(f"经验1生成规律: {len(rules1)}个")
    
    # 处理第二个经验（有历史经验进行验证）
    rules2 = bpm_model.process_experience(experience2, [experience1])
    print(f"经验2生成规律: {len(rules2)}个")
    
    # 获取统计信息
    stats = bpm_model.get_processing_statistics()
    print(f"BPM处理统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 获取最佳规律
    top_rules = bpm_model.get_top_rules(5)
    print(f"\n最佳规律TOP5:")
    for i, rule in enumerate(top_rules, 1):
        pattern_str = " + ".join([e.content for e in rule.pattern_elements])
        print(f"{i}. {pattern_str} → {rule.prediction_element.content} "
              f"(L{rule.generation_layer}, 得分:{rule.calculate_total_score():.3f})") 