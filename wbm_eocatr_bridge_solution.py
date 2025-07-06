"""
WBM-EOCATR桥接解决方案
===================

目标：
1. 结构化，基于EOCATR，清晰方便计算
2. BMP机制产生的规律首尾可连接
3. 基于初始状态和目标决策，确定起点和终点
4. 可以实现长链决策
5. 给出通用的组合规律，建立决策，即搭桥的方法

核心创新：
- EOCATR规律标准化接口
- 状态转换链式推理
- 目标导向的桥梁构建
- 通用组合模式库
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
import time
import json

# ===== 第一部分：EOCATR标准化结构 =====

class EOCATRElement(Enum):
    """EOCATR元素类型"""
    ENVIRONMENT = "E"  # 环境
    OBJECT = "O"       # 对象
    CONDITION = "C"    # 条件
    ACTION = "A"       # 动作
    TOOL = "T"         # 工具
    RESULT = "R"       # 结果

@dataclass
class StructuredEOCATR:
    """结构化EOCATR表示"""
    environment: Dict[str, Any] = field(default_factory=dict)  # E
    objects: Dict[str, Any] = field(default_factory=dict)      # O
    conditions: Dict[str, Any] = field(default_factory=dict)   # C
    actions: Dict[str, Any] = field(default_factory=dict)      # A
    tools: Dict[str, Any] = field(default_factory=dict)        # T
    results: Dict[str, Any] = field(default_factory=dict)      # R
    
    def get_input_signature(self) -> str:
        """获取输入签名（E+O+C）"""
        elements = []
        if self.environment:
            elements.append(f"E:{','.join(str(v) for v in self.environment.values())}")
        if self.objects:
            elements.append(f"O:{','.join(str(v) for v in self.objects.values())}")
        if self.conditions:
            elements.append(f"C:{','.join(str(v) for v in self.conditions.values())}")
        return "|".join(elements)
    
    def get_output_signature(self) -> str:
        """获取输出签名（A+T+R）"""
        elements = []
        if self.actions:
            elements.append(f"A:{','.join(str(v) for v in self.actions.values())}")
        if self.tools:
            elements.append(f"T:{','.join(str(v) for v in self.tools.values())}")
        if self.results:
            elements.append(f"R:{','.join(str(v) for v in self.results.values())}")
        return "|".join(elements)

@dataclass
class StandardizedRule:
    """标准化规律"""
    rule_id: str
    rule_type: str
    eocatr: StructuredEOCATR
    confidence: float
    usage_count: int = 0
    success_count: int = 0
    
    # 连接接口
    input_signature: str = ""
    output_signature: str = ""
    
    def __post_init__(self):
        """初始化后生成签名"""
        self.input_signature = self.eocatr.get_input_signature()
        self.output_signature = self.eocatr.get_output_signature()
    
    def can_connect_to(self, next_rule: 'StandardizedRule') -> Tuple[bool, float]:
        """检查能否连接到下一个规律"""
        # 输出与输入的语义匹配
        return self._semantic_match(self.output_signature, next_rule.input_signature)
    
    def _semantic_match(self, output_sig: str, input_sig: str) -> Tuple[bool, float]:
        """语义匹配算法"""
        if not output_sig or not input_sig:
            return False, 0.0
        
        # 解析签名
        output_elements = self._parse_signature(output_sig)
        input_elements = self._parse_signature(input_sig)
        
        # 计算匹配度
        matches = 0
        total = max(len(output_elements), len(input_elements))
        
        for out_elem in output_elements:
            for in_elem in input_elements:
                if self._elements_compatible(out_elem, in_elem):
                    matches += 1
                    break
        
        if total == 0:
            return False, 0.0
        
        match_score = matches / total
        can_connect = match_score >= 0.3  # 30%以上匹配度才能连接
        
        return can_connect, match_score
    
    def _parse_signature(self, signature: str) -> List[Tuple[str, str]]:
        """解析签名为(类型, 值)列表"""
        elements = []
        for part in signature.split("|"):
            if ":" in part:
                elem_type, values = part.split(":", 1)
                for value in values.split(","):
                    elements.append((elem_type, value.strip()))
        return elements
    
    def _elements_compatible(self, elem1: Tuple[str, str], elem2: Tuple[str, str]) -> bool:
        """检查两个元素是否兼容"""
        type1, value1 = elem1
        type2, value2 = elem2
        
        # 类型兼容性
        compatible_types = {
            "R": ["E", "O", "C"],  # 结果可以作为环境、对象、条件的输入
            "A": ["C"],            # 动作可以作为条件的输入
            "T": ["O"],            # 工具可以作为对象的输入
        }
        
        if type1 in compatible_types and type2 in compatible_types[type1]:
            # 值兼容性（简化版）
            return self._values_compatible(value1, value2)
        
        return False
    
    def _values_compatible(self, value1: str, value2: str) -> bool:
        """检查两个值是否兼容"""
        # 完全匹配
        if value1.lower() == value2.lower():
            return True
        
        # 包含关系
        if value1.lower() in value2.lower() or value2.lower() in value1.lower():
            return True
        
        # 语义相关性（简化版）
        semantic_groups = [
            ["老虎", "熊", "野猪", "猛兽", "危险动物"],
            ["兔子", "松鼠", "小动物", "无害动物"],
            ["苹果", "浆果", "蘑菇", "植物", "食物"],
            ["森林", "树林", "丛林", "环境"],
            ["攻击", "战斗", "对抗", "动作"],
            ["采集", "收集", "获取", "动作"],
            ["受伤", "死亡", "危险", "结果"],
            ["安全", "成功", "满足", "结果"]
        ]
        
        for group in semantic_groups:
            if any(word in value1.lower() for word in group) and \
               any(word in value2.lower() for word in group):
                return True
        
        return False

# ===== 第二部分：状态转换链式推理 =====

@dataclass
class GameState:
    """游戏状态"""
    environment: Dict[str, Any] = field(default_factory=dict)
    objects: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def matches_eocatr_input(self, eocatr: StructuredEOCATR) -> bool:
        """检查状态是否匹配EOCATR输入"""
        # 环境匹配
        for key, value in eocatr.environment.items():
            if key not in self.environment or self.environment[key] != value:
                return False
        
        # 对象匹配
        for key, value in eocatr.objects.items():
            if key not in self.objects or self.objects[key] != value:
                return False
        
        # 条件匹配
        for key, value in eocatr.conditions.items():
            if key not in self.conditions or self.conditions[key] != value:
                return False
        
        return True
    
    def apply_eocatr_output(self, eocatr: StructuredEOCATR) -> 'GameState':
        """应用EOCATR输出，生成新状态"""
        new_state = GameState(
            environment=self.environment.copy(),
            objects=self.objects.copy(),
            conditions=self.conditions.copy(),
            timestamp=time.time()
        )
        
        # 应用动作结果
        for key, value in eocatr.actions.items():
            new_state.conditions[f"action_{key}"] = value
        
        # 应用工具结果
        for key, value in eocatr.tools.items():
            new_state.objects[f"tool_{key}"] = value
        
        # 应用最终结果
        for key, value in eocatr.results.items():
            if key.startswith("env_"):
                new_state.environment[key[4:]] = value
            elif key.startswith("obj_"):
                new_state.objects[key[4:]] = value
            else:
                new_state.conditions[key] = value
        
        return new_state

class StateTransitionChain:
    """状态转换链"""
    
    def __init__(self):
        self.chain_cache = {}  # 缓存已计算的链
    
    def build_transition_chain(self, 
                             start_state: GameState,
                             target_state: GameState,
                             available_rules: List[StandardizedRule],
                             max_depth: int = 5) -> Optional[List[StandardizedRule]]:
        """构建状态转换链"""
        # 生成缓存键
        cache_key = self._generate_cache_key(start_state, target_state)
        if cache_key in self.chain_cache:
            return self.chain_cache[cache_key]
        
        # 使用A*搜索算法
        result = self._a_star_search(start_state, target_state, available_rules, max_depth)
        
        # 缓存结果
        self.chain_cache[cache_key] = result
        return result
    
    def _a_star_search(self,
                      start_state: GameState,
                      target_state: GameState,
                      available_rules: List[StandardizedRule],
                      max_depth: int) -> Optional[List[StandardizedRule]]:
        """A*搜索算法实现"""
        from heapq import heappush, heappop
        
        # 搜索节点：(f_score, g_score, current_state, rule_path)
        open_set = [(0, 0, start_state, [])]
        closed_set = set()
        
        while open_set:
            f_score, g_score, current_state, rule_path = heappop(open_set)
            
            # 检查是否达到目标
            if self._state_matches_target(current_state, target_state):
                return rule_path
            
            # 检查深度限制
            if len(rule_path) >= max_depth:
                continue
            
            # 生成状态键用于去重
            state_key = self._generate_state_key(current_state)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)
            
            # 尝试所有可用规律
            for rule in available_rules:
                if current_state.matches_eocatr_input(rule.eocatr):
                    # 应用规律生成新状态
                    new_state = current_state.apply_eocatr_output(rule.eocatr)
                    new_path = rule_path + [rule]
                    
                    # 计算代价
                    new_g_score = g_score + self._calculate_rule_cost(rule)
                    h_score = self._heuristic_distance(new_state, target_state)
                    new_f_score = new_g_score + h_score
                    
                    heappush(open_set, (new_f_score, new_g_score, new_state, new_path))
        
        return None  # 未找到路径
    
    def _state_matches_target(self, current_state: GameState, target_state: GameState) -> bool:
        """检查当前状态是否匹配目标状态"""
        # 检查关键条件是否满足
        for key, value in target_state.conditions.items():
            if key not in current_state.conditions:
                return False
            if current_state.conditions[key] != value:
                return False
        
        # 检查关键对象是否存在
        for key, value in target_state.objects.items():
            if key not in current_state.objects:
                return False
            # 对象可以是部分匹配
            if not self._objects_compatible(current_state.objects[key], value):
                return False
        
        return True
    
    def _objects_compatible(self, obj1: Any, obj2: Any) -> bool:
        """检查对象兼容性"""
        if obj1 == obj2:
            return True
        
        # 数值兼容性
        if isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
            return abs(obj1 - obj2) <= 0.1
        
        # 字符串包含关系
        if isinstance(obj1, str) and isinstance(obj2, str):
            return obj1.lower() in obj2.lower() or obj2.lower() in obj1.lower()
        
        return False
    
    def _calculate_rule_cost(self, rule: StandardizedRule) -> float:
        """计算规律使用代价"""
        base_cost = 1.0
        confidence_bonus = rule.confidence * 0.5
        usage_bonus = min(rule.usage_count * 0.1, 1.0)
        
        return base_cost - confidence_bonus - usage_bonus
    
    def _heuristic_distance(self, current_state: GameState, target_state: GameState) -> float:
        """启发式距离函数"""
        distance = 0.0
        
        # 条件差异
        for key, value in target_state.conditions.items():
            if key not in current_state.conditions:
                distance += 2.0
            elif current_state.conditions[key] != value:
                distance += 1.0
        
        # 对象差异
        for key, value in target_state.objects.items():
            if key not in current_state.objects:
                distance += 1.5
            elif not self._objects_compatible(current_state.objects[key], value):
                distance += 0.5
        
        return distance
    
    def _generate_cache_key(self, start_state: GameState, target_state: GameState) -> str:
        """生成缓存键"""
        start_key = self._generate_state_key(start_state)
        target_key = self._generate_state_key(target_state)
        return f"{start_key}->{target_key}"
    
    def _generate_state_key(self, state: GameState) -> str:
        """生成状态键"""
        elements = []
        
        # 环境键
        env_items = sorted(state.environment.items())
        if env_items:
            elements.append(f"E:{','.join(f'{k}={v}' for k, v in env_items)}")
        
        # 对象键
        obj_items = sorted(state.objects.items())
        if obj_items:
            elements.append(f"O:{','.join(f'{k}={v}' for k, v in obj_items)}")
        
        # 条件键
        cond_items = sorted(state.conditions.items())
        if cond_items:
            elements.append(f"C:{','.join(f'{k}={v}' for k, v in cond_items)}")
        
        return "|".join(elements)

# ===== 第三部分：目标导向桥梁构建 =====

class GoalType(Enum):
    """目标类型"""
    SURVIVAL = "survival"
    RESOURCE_ACQUISITION = "resource_acquisition"
    THREAT_AVOIDANCE = "threat_avoidance"
    EXPLORATION = "exploration"

@dataclass
class StructuredGoal:
    """结构化目标"""
    goal_type: GoalType
    target_state: GameState
    priority: float = 1.0
    urgency: float = 1.0
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_importance(self) -> float:
        """计算目标重要性"""
        return self.priority * self.urgency

class GoalOrientedBridge:
    """目标导向桥梁构建器"""
    
    def __init__(self):
        self.transition_chain = StateTransitionChain()
        self.success_patterns = {}  # 成功模式缓存
    
    def build_bridge(self,
                    start_state: GameState,
                    goal: StructuredGoal,
                    available_rules: List[StandardizedRule]) -> Optional[List[StandardizedRule]]:
        """构建目标导向桥梁"""
        
        # 1. 检查是否有缓存的成功模式
        pattern_key = self._generate_pattern_key(start_state, goal)
        if pattern_key in self.success_patterns:
            cached_pattern = self.success_patterns[pattern_key]
            if self._pattern_applicable(cached_pattern, available_rules):
                return cached_pattern
        
        # 2. 构建状态转换链
        rule_chain = self.transition_chain.build_transition_chain(
            start_state, goal.target_state, available_rules
        )
        
        if rule_chain:
            # 3. 优化链条
            optimized_chain = self._optimize_chain(rule_chain, goal)
            
            # 4. 缓存成功模式
            self.success_patterns[pattern_key] = optimized_chain
            
            return optimized_chain
        
        return None
    
    def _optimize_chain(self, rule_chain: List[StandardizedRule], goal: StructuredGoal) -> List[StandardizedRule]:
        """优化规律链"""
        if len(rule_chain) <= 2:
            return rule_chain
        
        # 移除冗余规律
        optimized = []
        for i, rule in enumerate(rule_chain):
            # 检查是否可以跳过当前规律
            if i == 0 or i == len(rule_chain) - 1:
                # 保留第一个和最后一个
                optimized.append(rule)
            else:
                # 检查跳过当前规律是否仍能连接
                prev_rule = optimized[-1] if optimized else rule_chain[i-1]
                next_rule = rule_chain[i+1]
                
                can_skip, _ = prev_rule.can_connect_to(next_rule)
                if not can_skip:
                    optimized.append(rule)
        
        return optimized
    
    def _generate_pattern_key(self, start_state: GameState, goal: StructuredGoal) -> str:
        """生成模式键"""
        start_key = self.transition_chain._generate_state_key(start_state)
        goal_key = self.transition_chain._generate_state_key(goal.target_state)
        return f"{goal.goal_type.value}:{start_key}->{goal_key}"
    
    def _pattern_applicable(self, pattern: List[StandardizedRule], available_rules: List[StandardizedRule]) -> bool:
        """检查模式是否适用"""
        available_ids = {rule.rule_id for rule in available_rules}
        pattern_ids = {rule.rule_id for rule in pattern}
        return pattern_ids.issubset(available_ids)

# ===== 第四部分：通用组合模式库 =====

class CombinationPattern(Enum):
    """组合模式类型"""
    SEQUENTIAL = "sequential"      # 顺序组合
    PARALLEL = "parallel"         # 并行组合
    CONDITIONAL = "conditional"   # 条件组合
    LOOP = "loop"                # 循环组合
    FALLBACK = "fallback"        # 回退组合

@dataclass
class PatternTemplate:
    """模式模板"""
    pattern_type: CombinationPattern
    rule_slots: List[str]  # 规律槽位
    connection_requirements: List[Tuple[str, str]]  # 连接要求
    success_conditions: Dict[str, Any]  # 成功条件
    
    def instantiate(self, rules: Dict[str, StandardizedRule]) -> Optional[List[StandardizedRule]]:
        """实例化模式"""
        # 检查所有槽位是否都有对应规律
        for slot in self.rule_slots:
            if slot not in rules:
                return None
        
        # 检查连接要求
        for from_slot, to_slot in self.connection_requirements:
            if from_slot not in rules or to_slot not in rules:
                return None
            
            can_connect, _ = rules[from_slot].can_connect_to(rules[to_slot])
            if not can_connect:
                return None
        
        # 返回实例化的规律序列
        return [rules[slot] for slot in self.rule_slots]

class UniversalCombinationLibrary:
    """通用组合规律库"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, PatternTemplate]:
        """初始化模式库"""
        patterns = {}
        
        # 生存基础模式：感知威胁 -> 评估危险 -> 选择行动
        patterns["survival_basic"] = PatternTemplate(
            pattern_type=CombinationPattern.SEQUENTIAL,
            rule_slots=["threat_detection", "danger_assessment", "action_selection"],
            connection_requirements=[
                ("threat_detection", "danger_assessment"),
                ("danger_assessment", "action_selection")
            ],
            success_conditions={"safety": True}
        )
        
        # 资源获取模式：发现资源 -> 评估可行性 -> 执行获取
        patterns["resource_acquisition"] = PatternTemplate(
            pattern_type=CombinationPattern.SEQUENTIAL,
            rule_slots=["resource_detection", "feasibility_check", "acquisition_action"],
            connection_requirements=[
                ("resource_detection", "feasibility_check"),
                ("feasibility_check", "acquisition_action")
            ],
            success_conditions={"resource_obtained": True}
        )
        
        # 探索模式：选择方向 -> 移动 -> 观察环境
        patterns["exploration"] = PatternTemplate(
            pattern_type=CombinationPattern.LOOP,
            rule_slots=["direction_selection", "movement", "environment_observation"],
            connection_requirements=[
                ("direction_selection", "movement"),
                ("movement", "environment_observation"),
                ("environment_observation", "direction_selection")  # 循环
            ],
            success_conditions={"exploration_complete": True}
        )
        
        # 条件行动模式：检查条件 -> [条件A:行动A | 条件B:行动B]
        patterns["conditional_action"] = PatternTemplate(
            pattern_type=CombinationPattern.CONDITIONAL,
            rule_slots=["condition_check", "action_a", "action_b"],
            connection_requirements=[
                ("condition_check", "action_a"),
                ("condition_check", "action_b")
            ],
            success_conditions={"action_executed": True}
        )
        
        return patterns
    
    def find_applicable_patterns(self, 
                               available_rules: List[StandardizedRule],
                               goal: StructuredGoal) -> List[Tuple[str, List[StandardizedRule]]]:
        """寻找适用的模式"""
        applicable_patterns = []
        
        for pattern_name, pattern_template in self.patterns.items():
            # 尝试为每个槽位分配规律
            slot_assignments = self._assign_rules_to_slots(
                pattern_template, available_rules, goal
            )
            
            if slot_assignments:
                instantiated_rules = pattern_template.instantiate(slot_assignments)
                if instantiated_rules:
                    applicable_patterns.append((pattern_name, instantiated_rules))
        
        return applicable_patterns
    
    def _assign_rules_to_slots(self,
                             pattern: PatternTemplate,
                             available_rules: List[StandardizedRule],
                             goal: StructuredGoal) -> Optional[Dict[str, StandardizedRule]]:
        """为槽位分配规律"""
        assignments = {}
        
        # 基于规律类型和目标类型进行启发式分配
        for slot in pattern.rule_slots:
            best_rule = self._find_best_rule_for_slot(slot, available_rules, goal)
            if best_rule:
                assignments[slot] = best_rule
            else:
                return None  # 无法为某个槽位找到合适的规律
        
        return assignments
    
    def _find_best_rule_for_slot(self,
                               slot: str,
                               available_rules: List[StandardizedRule],
                               goal: StructuredGoal) -> Optional[StandardizedRule]:
        """为特定槽位找到最佳规律"""
        slot_keywords = {
            "threat_detection": ["危险", "威胁", "敌人", "老虎", "熊"],
            "danger_assessment": ["评估", "判断", "安全", "危险"],
            "action_selection": ["选择", "决定", "行动", "动作"],
            "resource_detection": ["发现", "找到", "资源", "食物", "植物"],
            "feasibility_check": ["可行", "能否", "检查", "条件"],
            "acquisition_action": ["获取", "采集", "收集", "拿取"],
            "direction_selection": ["方向", "选择", "路径"],
            "movement": ["移动", "前进", "靠近", "远离"],
            "environment_observation": ["观察", "查看", "环境", "周围"],
            "condition_check": ["检查", "条件", "如果", "判断"],
            "action_a": ["行动", "动作", "执行"],
            "action_b": ["行动", "动作", "执行"]
        }
        
        keywords = slot_keywords.get(slot, [])
        best_rule = None
        best_score = 0.0
        
        for rule in available_rules:
            score = self._calculate_slot_rule_match_score(rule, keywords, goal)
            if score > best_score:
                best_score = score
                best_rule = rule
        
        return best_rule if best_score > 0.3 else None
    
    def _calculate_slot_rule_match_score(self,
                                       rule: StandardizedRule,
                                       keywords: List[str],
                                       goal: StructuredGoal) -> float:
        """计算规律与槽位的匹配分数"""
        score = 0.0
        
        # 检查规律的EOCATR内容是否包含关键词
        rule_content = self._extract_rule_content(rule)
        
        for keyword in keywords:
            if keyword in rule_content.lower():
                score += 0.3
        
        # 目标相关性加分
        goal_content = self._extract_goal_content(goal)
        if any(word in rule_content.lower() for word in goal_content):
            score += 0.2
        
        # 置信度加分
        score += rule.confidence * 0.3
        
        # 使用历史加分
        if rule.usage_count > 0:
            success_rate = rule.success_count / rule.usage_count
            score += success_rate * 0.2
        
        return min(score, 1.0)
    
    def _extract_rule_content(self, rule: StandardizedRule) -> str:
        """提取规律内容"""
        content_parts = []
        
        eocatr = rule.eocatr
        for attr_name in ['environment', 'objects', 'conditions', 'actions', 'tools', 'results']:
            attr_dict = getattr(eocatr, attr_name)
            for key, value in attr_dict.items():
                content_parts.append(f"{key}:{value}")
        
        return " ".join(content_parts)
    
    def _extract_goal_content(self, goal: StructuredGoal) -> List[str]:
        """提取目标内容关键词"""
        keywords = [goal.goal_type.value]
        
        # 从目标状态提取关键词
        for attr_name in ['environment', 'objects', 'conditions']:
            attr_dict = getattr(goal.target_state, attr_name)
            for key, value in attr_dict.items():
                keywords.extend([str(key), str(value)])
        
        return keywords

# ===== 第五部分：整合接口 =====

class EnhancedWBMSystem:
    """增强的WBM系统"""
    
    def __init__(self):
        self.bridge_builder = GoalOrientedBridge()
        self.pattern_library = UniversalCombinationLibrary()
        self.rule_converter = RuleConverter()
    
    def make_decision(self,
                     current_state: GameState,
                     goal: StructuredGoal,
                     available_rules: List[StandardizedRule]) -> Dict[str, Any]:
        """做出决策"""
        
        # 1. 尝试直接桥梁构建
        bridge_chain = self.bridge_builder.build_bridge(
            current_state, goal, available_rules
        )
        
        if bridge_chain:
            return {
                "success": True,
                "method": "direct_bridge",
                "rule_chain": bridge_chain,
                "actions": self._extract_actions_from_chain(bridge_chain),
                "confidence": self._calculate_chain_confidence(bridge_chain)
            }
        
        # 2. 尝试模式匹配
        applicable_patterns = self.pattern_library.find_applicable_patterns(
            available_rules, goal
        )
        
        if applicable_patterns:
            best_pattern_name, best_pattern_rules = max(
                applicable_patterns,
                key=lambda x: self._calculate_pattern_score(x[1], goal)
            )
            
            return {
                "success": True,
                "method": "pattern_matching",
                "pattern_name": best_pattern_name,
                "rule_chain": best_pattern_rules,
                "actions": self._extract_actions_from_chain(best_pattern_rules),
                "confidence": self._calculate_chain_confidence(best_pattern_rules)
            }
        
        # 3. 回退到简单规律匹配
        simple_rule = self._find_simple_applicable_rule(current_state, available_rules)
        if simple_rule:
            return {
                "success": True,
                "method": "simple_matching",
                "rule_chain": [simple_rule],
                "actions": self._extract_actions_from_chain([simple_rule]),
                "confidence": simple_rule.confidence
            }
        
        # 4. 无法决策
        return {
            "success": False,
            "method": "none",
            "rule_chain": [],
            "actions": [],
            "confidence": 0.0
        }
    
    def _extract_actions_from_chain(self, rule_chain: List[StandardizedRule]) -> List[str]:
        """从规律链提取行动序列"""
        actions = []
        for rule in rule_chain:
            rule_actions = rule.eocatr.actions
            for action_key, action_value in rule_actions.items():
                actions.append(f"{action_key}:{action_value}")
        return actions
    
    def _calculate_chain_confidence(self, rule_chain: List[StandardizedRule]) -> float:
        """计算链条置信度"""
        if not rule_chain:
            return 0.0
        
        # 使用几何平均数
        confidence_product = 1.0
        for rule in rule_chain:
            confidence_product *= rule.confidence
        
        return confidence_product ** (1.0 / len(rule_chain))
    
    def _calculate_pattern_score(self, pattern_rules: List[StandardizedRule], goal: StructuredGoal) -> float:
        """计算模式分数"""
        base_score = self._calculate_chain_confidence(pattern_rules)
        
        # 目标相关性加分
        goal_keywords = self.pattern_library._extract_goal_content(goal)
        relevance_bonus = 0.0
        
        for rule in pattern_rules:
            rule_content = self.pattern_library._extract_rule_content(rule)
            if any(keyword in rule_content.lower() for keyword in goal_keywords):
                relevance_bonus += 0.1
        
        return base_score + relevance_bonus
    
    def _find_simple_applicable_rule(self, 
                                   current_state: GameState, 
                                   available_rules: List[StandardizedRule]) -> Optional[StandardizedRule]:
        """找到简单适用的规律"""
        for rule in available_rules:
            if current_state.matches_eocatr_input(rule.eocatr):
                return rule
        return None

class RuleConverter:
    """规律转换器：将现有规律转换为标准化格式"""
    
    def convert_legacy_rule(self, legacy_rule: Any) -> StandardizedRule:
        """转换传统规律格式"""
        # 这里需要根据实际的规律格式进行转换
        # 示例实现
        
        eocatr = StructuredEOCATR()
        
        # 从传统规律提取EOCATR信息
        if hasattr(legacy_rule, 'conditions'):
            conditions = legacy_rule.conditions
            if isinstance(conditions, dict):
                for key, value in conditions.items():
                    if 'environment' in key.lower() or 'env' in key.lower():
                        eocatr.environment[key] = value
                    elif 'object' in key.lower() or 'obj' in key.lower():
                        eocatr.objects[key] = value
                    else:
                        eocatr.conditions[key] = value
        
        if hasattr(legacy_rule, 'predictions'):
            predictions = legacy_rule.predictions
            if isinstance(predictions, dict):
                for key, value in predictions.items():
                    if 'action' in key.lower():
                        eocatr.actions[key] = value
                    elif 'tool' in key.lower():
                        eocatr.tools[key] = value
                    else:
                        eocatr.results[key] = value
        
        return StandardizedRule(
            rule_id=getattr(legacy_rule, 'rule_id', f"rule_{id(legacy_rule)}"),
            rule_type=getattr(legacy_rule, 'rule_type', 'unknown'),
            eocatr=eocatr,
            confidence=getattr(legacy_rule, 'confidence', 0.5),
            usage_count=getattr(legacy_rule, 'usage_count', 0),
            success_count=getattr(legacy_rule, 'success_count', 0)
        )

# ===== 测试和示例 =====

def create_test_example():
    """创建测试示例"""
    
    # 创建测试规律
    rule1_eocatr = StructuredEOCATR(
        environment={"location": "forest"},
        objects={"animal": "tiger"},
        conditions={"distance": "close"},
        actions={"movement": "retreat"},
        results={"safety": "increased"}
    )
    
    rule1 = StandardizedRule(
        rule_id="avoid_tiger",
        rule_type="survival",
        eocatr=rule1_eocatr,
        confidence=0.9
    )
    
    rule2_eocatr = StructuredEOCATR(
        environment={"location": "forest"},
        conditions={"safety": "increased"},
        actions={"search": "food"},
        objects={"target": "plant"},
        results={"resource": "found"}
    )
    
    rule2 = StandardizedRule(
        rule_id="search_food_safely",
        rule_type="resource",
        eocatr=rule2_eocatr,
        confidence=0.8
    )
    
    # 创建状态和目标
    start_state = GameState(
        environment={"location": "forest"},
        objects={"animal": "tiger"},
        conditions={"distance": "close", "hunger": "high"}
    )
    
    target_state = GameState(
        environment={"location": "forest"},
        conditions={"safety": "high", "resource": "obtained"}
    )
    
    goal = StructuredGoal(
        goal_type=GoalType.SURVIVAL,
        target_state=target_state,
        priority=1.0,
        urgency=0.9
    )
    
    # 测试系统
    wbm_system = EnhancedWBMSystem()
    result = wbm_system.make_decision(start_state, goal, [rule1, rule2])
    
    return result

if __name__ == "__main__":
    # 运行测试
    test_result = create_test_example()
    print("=== WBM-EOCATR桥接系统测试结果 ===")
    print(json.dumps(test_result, indent=2, ensure_ascii=False)) 