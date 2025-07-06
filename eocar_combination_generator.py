"""
EOCAR组合生成器（EOCAR Combination Generator）

基于EOCATR经验进行组合分析，生成候选规律的核心模块。
实现了15种EOCAR元素组合类型（C41+C42+C43+C44），通过属性泛化生成高质量候选规律。

主要功能：
1. EOCAR元素组合分析
2. 属性分解与泛化
3. 候选规律生成
4. 规律质量评估

作者：AI生存游戏项目组
版本：1.0.0
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, Counter
from scene_symbolization_mechanism import (
    EOCATR_Tuple, SymbolicEnvironment, SymbolicObjectCategory, 
    SymbolicAction, SymbolicCharacteristics, SymbolicResult, SymbolicTool
)


class CombinationType(Enum):
    """EOCATR组合类型枚举（包含工具T的完整组合）"""
    # 单元素+结果 (5种)
    E_R = "environment_result"        # 环境->结果
    O_R = "object_result"            # 对象->结果
    C_R = "characteristics_result"    # 特征->结果
    A_R = "action_result"            # 动作->结果
    T_R = "tool_result"              # 工具->结果
    
    # 双元素+结果 (10种)
    E_O_R = "environment_object_result"           # 环境+对象->结果
    E_C_R = "environment_characteristics_result"  # 环境+特征->结果
    E_A_R = "environment_action_result"           # 环境+动作->结果
    E_T_R = "environment_tool_result"             # 环境+工具->结果
    O_C_R = "object_characteristics_result"       # 对象+特征->结果
    O_A_R = "object_action_result"               # 对象+动作->结果
    O_T_R = "object_tool_result"                 # 对象+工具->结果
    C_A_R = "characteristics_action_result"       # 特征+动作->结果
    C_T_R = "characteristics_tool_result"         # 特征+工具->结果
    A_T_R = "action_tool_result"                 # 动作+工具->结果
    
    # 三元素+结果 (10种)
    E_O_C_R = "environment_object_characteristics_result"  # 环境+对象+特征->结果
    E_O_A_R = "environment_object_action_result"           # 环境+对象+动作->结果
    E_O_T_R = "environment_object_tool_result"             # 环境+对象+工具->结果
    E_C_A_R = "environment_characteristics_action_result"  # 环境+特征+动作->结果
    E_C_T_R = "environment_characteristics_tool_result"    # 环境+特征+工具->结果
    E_A_T_R = "environment_action_tool_result"             # 环境+动作+工具->结果
    O_C_A_R = "object_characteristics_action_result"       # 对象+特征+动作->结果
    O_C_T_R = "object_characteristics_tool_result"         # 对象+特征+工具->结果
    O_A_T_R = "object_action_tool_result"                  # 对象+动作+工具->结果
    C_A_T_R = "characteristics_action_tool_result"         # 特征+动作+工具->结果
    
    # 四元素+结果 (5种)
    E_O_C_A_R = "environment_object_characteristics_action_result"  # 环境+对象+特征+动作->结果
    E_O_C_T_R = "environment_object_characteristics_tool_result"    # 环境+对象+特征+工具->结果
    E_O_A_T_R = "environment_object_action_tool_result"             # 环境+对象+动作+工具->结果
    E_C_A_T_R = "environment_characteristics_action_tool_result"    # 环境+特征+动作+工具->结果
    O_C_A_T_R = "object_characteristics_action_tool_result"         # 对象+特征+动作+工具->结果
    
    # 全元素+结果 (1种)
    E_O_C_A_T_R = "full_eocatr_result"            # 完整EOCATR->结果


@dataclass
class CandidateRule:
    """候选规律数据类"""
    rule_id: str                      # 规律ID
    combination_type: CombinationType  # 组合类型
    condition_elements: List[str]     # 条件元素列表
    condition_text: str               # 条件文本描述
    expected_result: Dict[str, Any]   # 预期结果
    
    # 生成信息
    source_experiences: List[str] = field(default_factory=list)  # 源经验ID
    generation_time: float = field(default_factory=time.time)    # 生成时间
    abstraction_level: int = 0        # 抽象层次 (0=具体, 1=属性泛化, 2=高度抽象)
    
    # 质量指标
    confidence: float = 0.1           # 初始置信度
    support_count: int = 1            # 支持经验数量
    contradict_count: int = 0         # 矛盾经验数量
    generalization_score: float = 0.0 # 泛化得分
    
    # 验证状态
    validation_attempts: int = 0      # 验证尝试次数
    validation_successes: int = 0     # 验证成功次数
    last_validation: float = 0.0      # 最后验证时间
    status: str = "candidate"         # 状态: candidate/validated/rejected
    
    # 使用统计
    activation_count: int = 0         # 规律激活次数
    last_activation: float = 0.0      # 最后激活时间
    
    def get_success_rate(self) -> float:
        """获取验证成功率"""
        if self.validation_attempts == 0:
            return 0.0
        return self.validation_successes / self.validation_attempts
    
    def get_support_ratio(self) -> float:
        """获取支持比例"""
        total = self.support_count + self.contradict_count
        if total == 0:
            return 0.0
        return self.support_count / total
    
    def calculate_quality_score(self) -> float:
        """计算规律质量综合得分"""
        base_score = self.confidence * 0.4
        support_score = self.get_support_ratio() * 0.3
        validation_score = self.get_success_rate() * 0.2
        generalization_score = min(self.generalization_score, 1.0) * 0.1
        
        return base_score + support_score + validation_score + generalization_score


class AttributeExtractor:
    """属性提取器"""
    
    def __init__(self):
        # 预定义的属性映射
        self.environment_attributes = {
            SymbolicEnvironment.FOREST: ["植被茂密区域", "野生动物栖息地", "隐蔽环境"],
            SymbolicEnvironment.OPEN_FIELD: ["开阔地带", "视野良好区域", "暴露环境"],
            SymbolicEnvironment.WATER_AREA: ["水源区域", "湿润环境", "补给点"],
            SymbolicEnvironment.DANGEROUS_ZONE: ["高危区域", "威胁密集区", "警戒区域"],
            SymbolicEnvironment.SAFE_ZONE: ["安全区域", "庇护所", "低威胁区"],
            SymbolicEnvironment.RESOURCE_RICH: ["资源丰富区", "补给充足区", "收获区"],
            SymbolicEnvironment.RESOURCE_SPARSE: ["资源稀少区", "贫瘠区域", "生存困难区"]
        }
        
        self.object_attributes = {
            SymbolicObjectCategory.DANGEROUS_ANIMAL: ["大型动物", "肉食动物", "攻击性动物", "威胁生物"],
            SymbolicObjectCategory.HARMLESS_ANIMAL: ["小型动物", "草食动物", "温和动物", "无害生物"],
            SymbolicObjectCategory.EDIBLE_PLANT: ["食物来源", "营养提供者", "可采集资源", "植物类食物"],
            SymbolicObjectCategory.POISONOUS_PLANT: ["有毒植物", "危险植物", "不可食用植物", "有害资源"],
            SymbolicObjectCategory.WATER_SOURCE: ["液体资源", "生存必需品", "补给来源", "水分提供者"],
            SymbolicObjectCategory.FELLOW_PLAYER: ["同类智能体", "合作对象", "社交目标", "友方单位"],
            SymbolicObjectCategory.OTHER_PLAYER: ["异类智能体", "竞争对象", "观察目标", "未知意图单位"]
        }
        
        self.action_attributes = {
            SymbolicAction.MOVE: ["位置变化", "空间行为", "基础行动"],
            SymbolicAction.ATTACK: ["攻击性行为", "主动行动", "高风险行为"],
            SymbolicAction.AVOID: ["防御性行为", "被动行动", "安全行为"],
            SymbolicAction.EAT: ["消耗行为", "营养获取", "资源利用"],
            SymbolicAction.DRINK: ["补给行为", "水分获取", "生存行为"],
            SymbolicAction.GATHER: ["收集行为", "资源获取", "采集行为"],
            SymbolicAction.EXPLORE: ["探索行为", "信息获取", "主动行为"],
            SymbolicAction.INTERACT: ["社交行为", "交流行为", "互动行为"],
            SymbolicAction.REST: ["恢复行为", "被动行为", "维护行为"]
        }
        
        # 添加工具属性映射
        self.tool_attributes = {
            SymbolicTool.NONE: ["无工具", "徒手", "自然能力"],
            SymbolicTool.STONE: ["石制工具", "硬质工具", "原始工具", "投掷武器"],
            SymbolicTool.STICK: ["木制工具", "棍棒", "延伸工具", "近战武器"],
            SymbolicTool.SPEAR: ["长矛工具", "尖锐工具", "远程武器", "狩猎工具"],
            SymbolicTool.BOW: ["弓箭工具", "远程工具", "精准武器", "狩猎装备"],
            SymbolicTool.BASKET: ["容器工具", "存储工具", "收集工具", "携带装置"],
            SymbolicTool.SHOVEL: ["挖掘工具", "土工工具", "建造工具", "劳动装备"]
        }
    
    def extract_environment_attributes(self, env) -> List[str]:
        """提取环境属性"""
        if env is None:
            return []
        
        # 使用环境内容作为键
        env_content = getattr(env, 'content', str(env))
        return self.environment_attributes.get(env_content, [])
    
    def extract_object_attributes(self, obj, characteristics) -> List[str]:
        """提取对象属性"""
        attributes = []
        
        if obj is not None:
            # 使用对象内容作为键
            obj_content = getattr(obj, 'content', str(obj))
            attributes = self.object_attributes.get(obj_content, []).copy()
        
        # 基于特征添加动态属性
        if characteristics is not None:
            if getattr(characteristics, 'dangerous', False):
                attributes.extend(["危险实体", "威胁源"])
            if getattr(characteristics, 'edible', False):
                attributes.extend(["可食用实体", "营养源"])
            
            size = getattr(characteristics, 'size', None)
            if size == "large":
                attributes.extend(["大型实体", "显著目标"])
            elif size == "small":
                attributes.extend(["小型实体", "微小目标"])
        
        return list(set(attributes))  # 去重
    
    def extract_action_attributes(self, action) -> List[str]:
        """提取动作属性"""
        if action is None:
            return []
        
        # 使用动作内容作为键
        action_content = getattr(action, 'content', str(action))
        return self.action_attributes.get(action_content, [])
    
    def extract_tool_attributes(self, tool) -> List[str]:
        """提取工具属性"""
        if tool is None:
            return ["无工具", "徒手", "自然能力"]
        
        # 使用工具内容作为键
        tool_content = getattr(tool, 'content', str(tool))
        return self.tool_attributes.get(tool_content, [])
    
    def extract_characteristics_attributes(self, characteristics) -> List[str]:
        """提取特征属性"""
        attributes = []
        
        if characteristics is None:
            return attributes
        
        # 物理特征
        size = getattr(characteristics, 'size', None)
        if size:
            attributes.append(f"{size}型实体")
        
        if getattr(characteristics, 'dangerous', False):
            attributes.append("危险特征")
        if getattr(characteristics, 'edible', False):
            attributes.append("可食用特征")
        
        # 距离特征
        distance = getattr(characteristics, 'distance', 0)
        if distance > 0:
            if distance < 2:
                attributes.append("近距离")
            elif distance < 5:
                attributes.append("中距离")
            else:
                attributes.append("远距离")
        
        # 可见性
        visibility = getattr(characteristics, 'visibility', None)
        if visibility == "hidden":
            attributes.append("隐蔽特征")
        elif visibility == "visible":
            attributes.append("可见特征")
        
        return attributes


class EOCARCombinationGenerator:
    """EOCAR组合生成器主类"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.attribute_extractor = AttributeExtractor()
        self.generated_rules: List[CandidateRule] = []
        self.rule_counter = 0
        
        # 统计信息
        self.generation_stats = {
            'total_rules_generated': 0,
            'rules_by_combination_type': defaultdict(int),
            'rules_by_abstraction_level': defaultdict(int),
            'generation_time_ms': 0.0
        }
    
    def generate_candidate_rules(self, eocar_experiences: List[EOCATR_Tuple]) -> List[CandidateRule]:
        """
        从EOCATR经验列表生成候选规律
        
        Args:
            eocar_experiences: EOCATR经验列表
            
        Returns:
            List[CandidateRule]: 生成的候选规律列表
        """
        start_time = time.time()
        
        if not eocar_experiences:
            return []
        
        all_candidate_rules = []
        
        # 为每个经验生成候选规律
        for experience in eocar_experiences:
            experience_rules = self._generate_rules_from_single_experience(experience)
            all_candidate_rules.extend(experience_rules)
        
        # 去重和质量过滤
        filtered_rules = self._filter_and_deduplicate_rules(all_candidate_rules)
        
        # 更新统计信息
        generation_time = (time.time() - start_time) * 1000
        self.generation_stats['generation_time_ms'] = generation_time
        self.generation_stats['total_rules_generated'] += len(filtered_rules)
        
        if self.logger:
            self.logger.log(f"从{len(eocar_experiences)}个EOCATR经验生成了{len(filtered_rules)}个候选规律")
        
        return filtered_rules
    
    def _generate_rules_from_single_experience(self, experience: EOCATR_Tuple) -> List[CandidateRule]:
        """从单个EOCATR经验生成候选规律"""
        rules = []
        
        # 提取属性
        env_attrs = self.attribute_extractor.extract_environment_attributes(experience.environment)
        obj_attrs = self.attribute_extractor.extract_object_attributes(
            experience.object_category, experience.characteristics
        )
        action_attrs = self.attribute_extractor.extract_action_attributes(experience.action)
        char_attrs = self.attribute_extractor.extract_characteristics_attributes(experience.characteristics)
        tool_attrs = self.attribute_extractor.extract_tool_attributes(experience.tool)
        
        # 生成所有组合类型的规律（包含工具T）
        for combination_type in CombinationType:
            combination_rules = self._generate_combination_rules(
                combination_type, experience, env_attrs, obj_attrs, action_attrs, char_attrs, tool_attrs
            )
            rules.extend(combination_rules)
        
        return rules
    
    def _generate_combination_rules(self, combination_type: CombinationType, experience: EOCATR_Tuple,
                                  env_attrs: List[str], obj_attrs: List[str], 
                                  action_attrs: List[str], char_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """为特定组合类型生成规律"""
        rules = []
        
        # 单元素+结果 (5种)
        if combination_type == CombinationType.E_R:
            rules.extend(self._generate_e_r_rules(experience, env_attrs))
        elif combination_type == CombinationType.O_R:
            rules.extend(self._generate_o_r_rules(experience, obj_attrs))
        elif combination_type == CombinationType.C_R:
            rules.extend(self._generate_c_r_rules(experience, char_attrs))
        elif combination_type == CombinationType.A_R:
            rules.extend(self._generate_a_r_rules(experience, action_attrs))
        elif combination_type == CombinationType.T_R:
            rules.extend(self._generate_t_r_rules(experience, tool_attrs))
        
        # 双元素+结果 (10种)
        elif combination_type == CombinationType.E_O_R:
            rules.extend(self._generate_e_o_r_rules(experience, env_attrs, obj_attrs))
        elif combination_type == CombinationType.E_C_R:
            rules.extend(self._generate_e_c_r_rules(experience, env_attrs, char_attrs))
        elif combination_type == CombinationType.E_A_R:
            rules.extend(self._generate_e_a_r_rules(experience, env_attrs, action_attrs))
        elif combination_type == CombinationType.E_T_R:
            rules.extend(self._generate_e_t_r_rules(experience, env_attrs, tool_attrs))
        elif combination_type == CombinationType.O_C_R:
            rules.extend(self._generate_o_c_r_rules(experience, obj_attrs, char_attrs))
        elif combination_type == CombinationType.O_A_R:
            rules.extend(self._generate_o_a_r_rules(experience, obj_attrs, action_attrs))
        elif combination_type == CombinationType.O_T_R:
            rules.extend(self._generate_o_t_r_rules(experience, obj_attrs, tool_attrs))
        elif combination_type == CombinationType.C_A_R:
            rules.extend(self._generate_c_a_r_rules(experience, char_attrs, action_attrs))
        elif combination_type == CombinationType.C_T_R:
            rules.extend(self._generate_c_t_r_rules(experience, char_attrs, tool_attrs))
        elif combination_type == CombinationType.A_T_R:
            rules.extend(self._generate_a_t_r_rules(experience, action_attrs, tool_attrs))
        
        # 三元素+结果 (10种)
        elif combination_type == CombinationType.E_O_C_R:
            rules.extend(self._generate_e_o_c_r_rules(experience, env_attrs, obj_attrs, char_attrs))
        elif combination_type == CombinationType.E_O_A_R:
            rules.extend(self._generate_e_o_a_r_rules(experience, env_attrs, obj_attrs, action_attrs))
        elif combination_type == CombinationType.E_O_T_R:
            rules.extend(self._generate_e_o_t_r_rules(experience, env_attrs, obj_attrs, tool_attrs))
        elif combination_type == CombinationType.E_C_A_R:
            rules.extend(self._generate_e_c_a_r_rules(experience, env_attrs, char_attrs, action_attrs))
        elif combination_type == CombinationType.E_C_T_R:
            rules.extend(self._generate_e_c_t_r_rules(experience, env_attrs, char_attrs, tool_attrs))
        elif combination_type == CombinationType.E_A_T_R:
            rules.extend(self._generate_e_a_t_r_rules(experience, env_attrs, action_attrs, tool_attrs))
        elif combination_type == CombinationType.O_C_A_R:
            rules.extend(self._generate_o_c_a_r_rules(experience, obj_attrs, char_attrs, action_attrs))
        elif combination_type == CombinationType.O_C_T_R:
            rules.extend(self._generate_o_c_t_r_rules(experience, obj_attrs, char_attrs, tool_attrs))
        elif combination_type == CombinationType.O_A_T_R:
            rules.extend(self._generate_o_a_t_r_rules(experience, obj_attrs, action_attrs, tool_attrs))
        elif combination_type == CombinationType.C_A_T_R:
            rules.extend(self._generate_c_a_t_r_rules(experience, char_attrs, action_attrs, tool_attrs))
        
        # 四元素+结果 (5种)
        elif combination_type == CombinationType.E_O_C_A_R:
            rules.extend(self._generate_e_o_c_a_r_rules(experience, env_attrs, obj_attrs, char_attrs, action_attrs))
        elif combination_type == CombinationType.E_O_C_T_R:
            rules.extend(self._generate_e_o_c_t_r_rules(experience, env_attrs, obj_attrs, char_attrs, tool_attrs))
        elif combination_type == CombinationType.E_O_A_T_R:
            rules.extend(self._generate_e_o_a_t_r_rules(experience, env_attrs, obj_attrs, action_attrs, tool_attrs))
        elif combination_type == CombinationType.E_C_A_T_R:
            rules.extend(self._generate_e_c_a_t_r_rules(experience, env_attrs, char_attrs, action_attrs, tool_attrs))
        elif combination_type == CombinationType.O_C_A_T_R:
            rules.extend(self._generate_o_c_a_t_r_rules(experience, obj_attrs, char_attrs, action_attrs, tool_attrs))
        
        # 全元素+结果 (1种)
        elif combination_type == CombinationType.E_O_C_A_T_R:
            rules.extend(self._generate_full_eocatr_rules(experience, env_attrs, obj_attrs, char_attrs, action_attrs, tool_attrs))
        
        # 更新统计
        self.generation_stats['rules_by_combination_type'][combination_type.value] += len(rules)
        
        return rules
    
    def _generate_e_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str]) -> List[CandidateRule]:
        """生成环境->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查环境是否存在
        if experience.environment is None:
            return rules
        
        # 基础规律：具体环境->结果
        rule = self._create_candidate_rule(
            CombinationType.E_R,
            [f"环境={experience.environment.content}"],
            f"在{experience.environment.content}环境中",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 属性泛化规律
        for env_attr in env_attrs:
            rule = self._create_candidate_rule(
                CombinationType.E_R,
                [f"环境属性={env_attr}"],
                f"在{env_attr}中",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_o_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str]) -> List[CandidateRule]:
        """生成对象->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查对象是否存在
        if experience.object is None:
            return rules
        
        # 基础规律：具体对象->结果
        rule = self._create_candidate_rule(
            CombinationType.O_R,
            [f"对象={experience.object.content}"],
            f"遇到{experience.object.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 属性泛化规律
        for obj_attr in obj_attrs:
            rule = self._create_candidate_rule(
                CombinationType.O_R,
                [f"对象属性={obj_attr}"],
                f"遇到{obj_attr}",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_c_r_rules(self, experience: EOCATR_Tuple, char_attrs: List[str]) -> List[CandidateRule]:
        """生成特征->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 基于特征属性生成规律
        for char_attr in char_attrs:
            rule = self._create_candidate_rule(
                CombinationType.C_R,
                [f"特征={char_attr}"],
                f"面对{char_attr}时",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_a_r_rules(self, experience: EOCATR_Tuple, action_attrs: List[str]) -> List[CandidateRule]:
        """生成动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查动作是否存在
        if experience.action is None:
            return rules
        
        # 基础规律：具体动作->结果
        rule = self._create_candidate_rule(
            CombinationType.A_R,
            [f"动作={experience.action.content}"],
            f"执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 属性泛化规律
        for action_attr in action_attrs:
            rule = self._create_candidate_rule(
                CombinationType.A_R,
                [f"动作属性={action_attr}"],
                f"执行{action_attr}",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_t_r_rules(self, experience: EOCATR_Tuple, tool_attrs: List[str]) -> List[CandidateRule]:
        """生成工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查工具是否存在
        if experience.tool is None:
            # 无工具的情况
            rule = self._create_candidate_rule(
                CombinationType.T_R,
                ["工具=无工具"],
                "不使用工具时",
                result_summary,
                experience,
                abstraction_level=0
            )
            rules.append(rule)
        else:
            # 基础规律：具体工具->结果
            rule = self._create_candidate_rule(
                CombinationType.T_R,
                [f"工具={experience.tool.content}"],
                f"使用{experience.tool.content}工具时",
                result_summary,
                experience,
                abstraction_level=0
            )
            rules.append(rule)
        
        # 属性泛化规律
        for tool_attr in tool_attrs:
            rule = self._create_candidate_rule(
                CombinationType.T_R,
                [f"工具属性={tool_attr}"],
                f"使用{tool_attr}时",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_e_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.environment is None or experience.tool is None:
            return rules
        
        # 基础规律：具体环境+具体工具->结果
        rule = self._create_candidate_rule(
            CombinationType.E_T_R,
            [f"环境={experience.environment.content}", f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 环境属性+具体工具
        for env_attr in env_attrs:
            rule = self._create_candidate_rule(
                CombinationType.E_T_R,
                [f"环境属性={env_attr}", f"工具={experience.tool.content}"],
                f"在{env_attr}中使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_o_t_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.object is None or experience.tool is None:
            return rules
        
        # 基础规律：具体对象+具体工具->结果
        rule = self._create_candidate_rule(
            CombinationType.O_T_R,
            [f"对象={experience.object.content}", f"工具={experience.tool.content}"],
            f"对{experience.object.content}使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 对象属性+具体工具
        for obj_attr in obj_attrs:
            rule = self._create_candidate_rule(
                CombinationType.O_T_R,
                [f"对象属性={obj_attr}", f"工具={experience.tool.content}"],
                f"对{obj_attr}使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_c_t_r_rules(self, experience: EOCATR_Tuple, char_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成特征+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.tool is None:
            return rules
        
        # 特征属性+具体工具
        for char_attr in char_attrs:
            rule = self._create_candidate_rule(
                CombinationType.C_T_R,
                [f"特征={char_attr}", f"工具={experience.tool.content}"],
                f"面对{char_attr}时使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_a_t_r_rules(self, experience: EOCATR_Tuple, action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.action is None or experience.tool is None:
            return rules
        
        # 基础规律：具体动作+具体工具->结果
        rule = self._create_candidate_rule(
            CombinationType.A_T_R,
            [f"动作={experience.action.content}", f"工具={experience.tool.content}"],
            f"执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_o_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查环境和对象是否存在
        if experience.environment is None or experience.object is None:
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}"],
            f"在{experience.environment.content}遇到{experience.object.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 环境泛化+对象泛化组合
        for env_attr in env_attrs[:2]:  # 限制组合数量
            for obj_attr in obj_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.E_O_R,
                    [f"环境属性={env_attr}", f"对象属性={obj_attr}"],
                    f"在{env_attr}遇到{obj_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_e_c_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], char_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+特征->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 环境+特征组合
        for env_attr in env_attrs[:2]:
            for char_attr in char_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.E_C_R,
                    [f"环境属性={env_attr}", f"特征={char_attr}"],
                    f"在{env_attr}面对{char_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_e_a_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查环境和动作是否存在
        if experience.environment is None or experience.action is None:
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_A_R,
            [f"环境={experience.environment.content}", f"动作={experience.action.content}"],
            f"在{experience.environment.content}执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 属性泛化组合
        for env_attr in env_attrs[:2]:
            for action_attr in action_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.E_A_R,
                    [f"环境属性={env_attr}", f"动作属性={action_attr}"],
                    f"在{env_attr}执行{action_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_o_c_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], char_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+特征->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 对象+特征组合
        for obj_attr in obj_attrs[:2]:
            for char_attr in char_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.O_C_R,
                    [f"对象属性={obj_attr}", f"特征={char_attr}"],
                    f"遇到{obj_attr}且具有{char_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_o_a_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 检查对象和动作是否存在
        if experience.object is None or experience.action is None:
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.O_A_R,
            [f"对象={experience.object.content}", f"动作={experience.action.content}"],
            f"对{experience.object.content}执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 属性泛化组合
        for obj_attr in obj_attrs[:2]:
            for action_attr in action_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.O_A_R,
                    [f"对象属性={obj_attr}", f"动作属性={action_attr}"],
                    f"对{obj_attr}执行{action_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_c_a_r_rules(self, experience: EOCATR_Tuple, char_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成特征+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 特征+动作组合
        for char_attr in char_attrs[:2]:
            for action_attr in action_attrs[:2]:
                rule = self._create_candidate_rule(
                    CombinationType.C_A_R,
                    [f"特征={char_attr}", f"动作属性={action_attr}"],
                    f"面对{char_attr}时执行{action_attr}",
                    result_summary,
                    experience,
                    abstraction_level=2
                )
                rules.append(rule)
        
        return rules
    
    def _generate_e_o_c_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], 
                               obj_attrs: List[str], char_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+特征->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 基础三元组规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_C_R,
            [f"环境={experience.environment.content}", 
             f"对象={experience.object.content}", 
             f"特征=具体特征"],
            f"在{experience.environment.content}遇到具有特定特征的{experience.object.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 限制高度组合以控制规律数量
        if env_attrs and obj_attrs and char_attrs:
            rule = self._create_candidate_rule(
                CombinationType.E_O_C_R,
                [f"环境属性={env_attrs[0]}", 
                 f"对象属性={obj_attrs[0]}", 
                 f"特征={char_attrs[0]}"],
                f"在{env_attrs[0]}遇到{char_attrs[0]}的{obj_attrs[0]}",
                result_summary,
                experience,
                abstraction_level=2
            )
            rules.append(rule)
        
        return rules
    
    def _generate_e_o_a_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], 
                               obj_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 基础三元组规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_A_R,
            [f"环境={experience.environment.content}", 
             f"对象={experience.object.content}", 
             f"动作={experience.action.content}"],
            f"在{experience.environment.content}对{experience.object.content}执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_c_a_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], 
                               char_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+特征+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 基础三元组规律（总是生成）
        rule = self._create_candidate_rule(
            CombinationType.E_C_A_R,
            [f"环境={experience.environment.content}", 
             f"特征=具体特征", 
             f"动作={experience.action.content}"],
            f"在{experience.environment.content}面对具体特征时执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        # 限制组合数量的属性泛化规律
        if env_attrs and char_attrs and action_attrs:
            rule = self._create_candidate_rule(
                CombinationType.E_C_A_R,
                [f"环境属性={env_attrs[0]}", 
                 f"特征={char_attrs[0]}", 
                 f"动作属性={action_attrs[0]}"],
                f"在{env_attrs[0]}面对{char_attrs[0]}时执行{action_attrs[0]}",
                result_summary,
                experience,
                abstraction_level=2
            )
            rules.append(rule)
        
        return rules
    
    def _generate_o_c_a_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], 
                               char_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+特征+动作->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 基础三元组规律
        rule = self._create_candidate_rule(
            CombinationType.O_C_A_R,
            [f"对象={experience.object.content}", 
             f"特征=具体特征", 
             f"动作={experience.action.content}"],
            f"对具有特定特征的{experience.object.content}执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_o_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.environment is None or experience.object is None or experience.tool is None:
            return rules
        
        # 基础规律：具体环境+具体对象+具体工具->结果
        rule = self._create_candidate_rule(
            CombinationType.E_O_T_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}", f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中对{experience.object.content}使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_c_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], char_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+特征+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.environment is None or experience.tool is None:
            return rules
        
        # 限制组合数量
        if len(env_attrs) > 0 and len(char_attrs) > 0:
            rule = self._create_candidate_rule(
                CombinationType.E_C_T_R,
                [f"环境属性={env_attrs[0]}", f"特征={char_attrs[0]}", f"工具={experience.tool.content}"],
                f"在{env_attrs[0]}中面对{char_attrs[0]}时使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_e_a_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.environment is None or experience.action is None or experience.tool is None:
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_A_T_R,
            [f"环境={experience.environment.content}", f"动作={experience.action.content}", f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_o_c_t_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], char_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+特征+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.object is None or experience.tool is None:
            return rules
        
        # 限制组合数量
        if len(obj_attrs) > 0 and len(char_attrs) > 0:
            rule = self._create_candidate_rule(
                CombinationType.O_C_T_R,
                [f"对象属性={obj_attrs[0]}", f"特征={char_attrs[0]}", f"工具={experience.tool.content}"],
                f"对{obj_attrs[0]}在{char_attrs[0]}情况下使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_o_a_t_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.object is None or experience.action is None or experience.tool is None:
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.O_A_T_R,
            [f"对象={experience.object.content}", f"动作={experience.action.content}", f"工具={experience.tool.content}"],
            f"对{experience.object.content}执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_c_a_t_r_rules(self, experience: EOCATR_Tuple, char_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成特征+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if experience.action is None or experience.tool is None:
            return rules
        
        # 限制组合数量
        if len(char_attrs) > 0 and len(action_attrs) > 0:
            rule = self._create_candidate_rule(
                CombinationType.C_A_T_R,
                [f"特征={char_attrs[0]}", f"动作属性={action_attrs[0]}", f"工具={experience.tool.content}"],
                f"面对{char_attrs[0]}时进行{action_attrs[0]}并使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_e_o_c_a_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str], char_attrs: List[str], action_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+特征+动作->结果规律（重命名的原full_eocar方法）"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.environment is None or experience.object is None or 
            experience.action is None):
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_C_A_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}", 
             f"动作={experience.action.content}"],
            f"在{experience.environment.content}环境中对{experience.object.content}执行{experience.action.content}行动",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_o_c_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str], char_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+特征+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.environment is None or experience.object is None or 
            experience.tool is None):
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_C_T_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}", 
             f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中对{experience.object.content}使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_o_a_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+对象+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.environment is None or experience.object is None or 
            experience.action is None or experience.tool is None):
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_A_T_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}", 
             f"动作={experience.action.content}", f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中对{experience.object.content}执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_e_c_a_t_r_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], char_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成环境+特征+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.environment is None or experience.action is None or 
            experience.tool is None):
            return rules
        
        # 限制组合数量
        if len(env_attrs) > 0 and len(char_attrs) > 0 and len(action_attrs) > 0:
            rule = self._create_candidate_rule(
                CombinationType.E_C_A_T_R,
                [f"环境属性={env_attrs[0]}", f"特征={char_attrs[0]}", 
                 f"动作属性={action_attrs[0]}", f"工具={experience.tool.content}"],
                f"在{env_attrs[0]}中面对{char_attrs[0]}时进行{action_attrs[0]}并使用{experience.tool.content}工具",
                result_summary,
                experience,
                abstraction_level=1
            )
            rules.append(rule)
        
        return rules
    
    def _generate_o_c_a_t_r_rules(self, experience: EOCATR_Tuple, obj_attrs: List[str], char_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成对象+特征+动作+工具->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.object is None or experience.action is None or 
            experience.tool is None):
            return rules
        
        # 基础规律
        rule = self._create_candidate_rule(
            CombinationType.O_C_A_T_R,
            [f"对象={experience.object.content}", f"动作={experience.action.content}", 
             f"工具={experience.tool.content}"],
            f"对{experience.object.content}执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_full_eocatr_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], obj_attrs: List[str], char_attrs: List[str], action_attrs: List[str], tool_attrs: List[str]) -> List[CandidateRule]:
        """生成完整EOCATR->结果规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        if (experience.environment is None or experience.object is None or 
            experience.action is None or experience.tool is None):
            return rules
        
        # 基础规律：完整EOCATR
        rule = self._create_candidate_rule(
            CombinationType.E_O_C_A_T_R,
            [f"环境={experience.environment.content}", f"对象={experience.object.content}", 
             f"动作={experience.action.content}", f"工具={experience.tool.content}"],
            f"在{experience.environment.content}环境中对{experience.object.content}执行{experience.action.content}行动并使用{experience.tool.content}工具",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _generate_full_eocar_rules(self, experience: EOCATR_Tuple, env_attrs: List[str], 
                                  obj_attrs: List[str], char_attrs: List[str], 
                                  action_attrs: List[str]) -> List[CandidateRule]:
        """生成完整EOCAR规律"""
        rules = []
        result_summary = self._summarize_result(experience.result)
        
        # 完整的具体规律
        rule = self._create_candidate_rule(
            CombinationType.E_O_C_A_R,
            [f"环境={experience.environment.content}", 
             f"对象={experience.object.content}", 
             f"特征=具体特征", 
             f"动作={experience.action.content}"],
            f"在{experience.environment.content}对具有特定特征的{experience.object.content}执行{experience.action.content}",
            result_summary,
            experience,
            abstraction_level=0
        )
        rules.append(rule)
        
        return rules
    
    def _create_candidate_rule(self, combination_type: CombinationType, condition_elements: List[str],
                              condition_text: str, expected_result: Dict[str, Any], 
                                                             source_experience: EOCATR_Tuple, abstraction_level: int = 0) -> CandidateRule:
        """创建候选规律"""
        self.rule_counter += 1
        
        # 计算初始置信度（基于抽象层次）
        base_confidence = 0.8 if abstraction_level == 0 else 0.6 if abstraction_level == 1 else 0.4
        
        # 计算泛化得分（抽象层次越高，泛化得分越高）
        generalization_score = abstraction_level * 0.3
        
        rule = CandidateRule(
            rule_id=f"rule_{self.rule_counter}_{combination_type.value}",
            combination_type=combination_type,
            condition_elements=condition_elements,
            condition_text=condition_text,
            expected_result=expected_result,
            source_experiences=[source_experience.tuple_id],
            abstraction_level=abstraction_level,
            confidence=base_confidence,
            generalization_score=generalization_score
        )
        
        # 更新统计
        self.generation_stats['rules_by_abstraction_level'][abstraction_level] += 1
        
        return rule
    
    def _summarize_result(self, result) -> Dict[str, Any]:
        """总结结果信息"""
        if result is None:
            return {'success': False, 'reward': 0.0, 'content': '无结果'}
        
        # 对于SymbolicElement类型的result
        if hasattr(result, 'content'):
            return {
                'success': hasattr(result, 'success') and result.success,
                'reward': getattr(result, 'reward', 0.0),
                'content': result.content,
                'tags': getattr(result, 'semantic_tags', [])
            }
        
        # 兼容旧的result格式
        return {
            'success': getattr(result, 'success', False),
            'reward': getattr(result, 'reward', 0.0),
            'hp_change': getattr(result, 'hp_change', 0),
            'food_change': getattr(result, 'food_change', 0),
            'water_change': getattr(result, 'water_change', 0),
            'experience_gained': getattr(result, 'experience_gained', 0)
        }
    
    def _filter_and_deduplicate_rules(self, rules: List[CandidateRule]) -> List[CandidateRule]:
        """过滤和去重规律"""
        if not rules:
            return []
        
        # 按条件文本去重
        seen_conditions = set()
        unique_rules = []
        
        for rule in rules:
            condition_key = f"{rule.combination_type.value}:{rule.condition_text}"
            if condition_key not in seen_conditions:
                seen_conditions.add(condition_key)
                unique_rules.append(rule)
        
        # 按质量得分排序，保留质量较高的规律
        unique_rules.sort(key=lambda r: r.calculate_quality_score(), reverse=True)
        
        # 限制数量以控制计算复杂度
        max_rules = 50  # 每次最多返回50个规律
        return unique_rules[:max_rules]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        return {
            'generation_stats': dict(self.generation_stats),
            'total_rules_in_memory': len(self.generated_rules),
            'rule_counter': self.rule_counter
        }


# 测试函数
def test_eocar_combination_generator():
    """测试EOCATR组合生成器"""
    import sys
    import os
    
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    print("=== EOCAR组合生成器测试 ===")
    
    # 创建测试日志器
    class TestLogger:
        def log(self, message):
            print(f"[LOG] {message}")
    
    # 创建生成器
    generator = EOCARCombinationGenerator(logger=TestLogger())
    
    # 创建测试EOCATR经验
    test_experience = EOCATR_Tuple(
        environment=SymbolicEnvironment.FOREST,
        object_category=SymbolicObjectCategory.DANGEROUS_ANIMAL,
        characteristics=SymbolicCharacteristics(
            distance=2.0,
            size="large",
            dangerous=True,
            activity_state="moving"
        ),
        action=SymbolicAction.AVOID,
        tool=SymbolicTool.NONE,  # 添加工具字段
        result=SymbolicResult(
            success=True,
            reward=0.5,
            hp_change=0,
            experience_gained=True
        ),
        timestamp=time.time(),
        confidence=0.9,
        importance=0.8
    )
    
    # 生成候选规律
    candidate_rules = generator.generate_candidate_rules([test_experience])
    
    print(f"\n生成了 {len(candidate_rules)} 个候选规律:")
    
    # 按组合类型统计
    type_counts = defaultdict(int)
    for rule in candidate_rules:
        type_counts[rule.combination_type.value] += 1
    
    print("\n各组合类型生成数量:")
    for combo_type, count in sorted(type_counts.items()):
        print(f"  {combo_type}: {count}")
    
    # 显示前10个规律示例
    print("\n前10个候选规律示例:")
    for i, rule in enumerate(candidate_rules[:10]):
        print(f"{i+1}. [{rule.combination_type.value}] {rule.condition_text}")
        print(f"   预期结果: {rule.expected_result}")
        print(f"   质量得分: {rule.calculate_quality_score():.3f}")
        print()
    
    # 显示统计信息
    stats = generator.get_statistics()
    print("生成统计:")
    for key, value in stats['generation_stats'].items():
        print(f"  {key}: {value}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_eocar_combination_generator() 