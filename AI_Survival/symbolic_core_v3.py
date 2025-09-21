#!/usr/bin/env python3
"""
符号核心系统 V3版本
统一的符号表示和管理系统
"""

import json
import hashlib
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime
import inspect

# 配置日志系统
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === 兼容性包装类：为了与BPM系统兼容 ===
class EnumCompatWrapper:
    """枚举兼容包装器，提供.value属性"""
    def __init__(self, content: str):
        self.value = content
        self.content = content
    
    def __str__(self):
        return self.content

class ResultCompatWrapper:
    """结果兼容包装器，提供success属性"""
    def __init__(self, content: str):
        self.content = content
        # 从内容中推断success状态
        self.success = "成功" in content or "success" in content.lower()
    
    def __str__(self):
        return self.content

class CharacteristicsCompatWrapper:
    """特征兼容包装器，提供distance等属性"""
    def __init__(self, content: str):
        self.content = content
        # 从内容中解析特征
        self.distance = 1.0  # 默认距离
        self.edible = "可食用" in content
        self.poisonous = "有毒" in content
        self.dangerous = "危险" in content
        self.nutrition_value = 10  # 默认营养值
        
        # 尝试从内容中提取距离信息
        if "近距离" in content:
            self.distance = 1.0
        elif "中距离" in content:
            self.distance = 5.0
        elif "远距离" in content:
            self.distance = 10.0
    
    def __str__(self):
        return self.content

class SymbolType(Enum):
    """符号类型枚举"""
    ENVIRONMENT = "Environment"  # 环境
    OBJECT = "Object"           # 对象  
    CHARACTER = "Character"     # 对象特征
    ACTION = "Action"           # 行动
    TOOL = "Tool"              # 工具
    RESULT = "Result"          # 结果

class AbstractionLevel(Enum):
    """抽象层级枚举"""
    CONCRETE = 1      # 具体层：老虎、石头
    CATEGORY = 2      # 类别层：猛兽、工具  
    CONCEPT = 3       # 概念层：危险、资源
    ABSTRACT = 4      # 抽象层：威胁、机会

@dataclass
class SymbolicElement:
    """统一符号元素基础类"""
    symbol_id: str                    # 符号唯一标识
    symbol_type: SymbolType          # 符号类型
    content: str                     # 符号内容
    abstraction_level: AbstractionLevel  # 抽象层级
    semantic_tags: List[str]         # 语义标签
    frequency: int = 0               # 使用频率
    quality_score: float = 0.0       # 质量分数
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
        if self.updated_time is None:
            self.updated_time = datetime.now()
        if not self.symbol_id:
            self.symbol_id = self._generate_id()

    def _generate_id(self) -> str:
        """生成符号唯一标识"""
        content_hash = hashlib.md5(
            f"{self.symbol_type.value}_{self.content}_{self.abstraction_level.value}".encode()
        ).hexdigest()[:8]
        return f"{self.symbol_type.value[:3].upper()}_{content_hash}"

    def update_usage(self, quality_delta: float = 0.0):
        """更新使用统计"""
        self.frequency += 1
        self.quality_score += quality_delta
        self.updated_time = datetime.now()
        
        logger.info(f"Symbol usage updated: {self.symbol_id} - frequency:{self.frequency}, quality:{self.quality_score:.3f}")

    def get_semantic_similarity(self, other: 'SymbolicElement') -> float:
        """计算与另一个符号的语义相似度"""
        if not isinstance(other, SymbolicElement):
            return 0.0
            
        # 类型匹配权重
        type_match = 1.0 if self.symbol_type == other.symbol_type else 0.3
        
        # 抽象层级距离权重  
        level_diff = abs(self.abstraction_level.value - other.abstraction_level.value)
        level_match = max(0.1, 1.0 - level_diff * 0.3)
        
        # 语义标签重叠权重
        common_tags = set(self.semantic_tags) & set(other.semantic_tags)
        all_tags = set(self.semantic_tags) | set(other.semantic_tags)
        tag_match = len(common_tags) / len(all_tags) if all_tags else 0.0
        
        # 内容相似度权重(简单字符匹配)
        content_match = 0.5 if self.content == other.content else 0.0
        
        similarity = (type_match * 0.3 + level_match * 0.2 + 
                     tag_match * 0.3 + content_match * 0.2)
        
        return min(1.0, similarity)
    
    def __hash__(self):
        """实现哈希方法，使SymbolicElement可以用于集合和字典"""
        return hash((self.symbol_type, self.content, self.abstraction_level, tuple(sorted(self.semantic_tags))))
    
    def __eq__(self, other):
        """实现相等比较方法"""
        if not isinstance(other, SymbolicElement):
            return False
        return (self.symbol_type == other.symbol_type and 
                self.content == other.content and 
                self.abstraction_level == other.abstraction_level and 
                set(self.semantic_tags) == set(other.semantic_tags))

    # === 兼容性属性：为了与BPM系统兼容 ===
    @property
    def value(self):
        """兼容性属性：返回content作为value，与枚举兼容"""
        return self.content
    
    @property
    def success(self):
        """兼容性属性：为结果类型元素提供success属性"""
        if self.symbol_type == SymbolType.RESULT:
            return "成功" in self.content or "success" in self.content.lower()
        return False
    
    @property
    def reward(self):
        """兼容性属性：为结果类型元素提供reward属性"""
        if self.symbol_type == SymbolType.RESULT:
            # 从内容中尝试提取奖励值，如果没有则根据成功状态给默认值
            if "成功" in self.content or "success" in self.content.lower():
                return 1.0  # 成功的默认奖励
            else:
                return -0.1  # 失败的默认奖励
        return 0.0
    
    @property
    def hp_change(self):
        """兼容性属性：为结果类型元素提供hp_change属性"""
        if self.symbol_type == SymbolType.RESULT:
            # 从内容或语义标签中提取血量变化信息
            content_lower = self.content.lower()
            
            # 检查语义标签中的血量变化信息
            for tag in self.semantic_tags:
                if "血量变化" in tag:
                    try:
                        # 提取数字，如"血量变化-5"
                        import re
                        match = re.search(r'血量变化([-+]?\d+)', tag)
                        if match:
                            return int(match.group(1))
                    except:
                        pass
                elif "hp" in tag.lower() and ("+" in tag or "-" in tag):
                    try:
                        # 提取HP变化，如"hp-5"或"hp+3"
                        import re
                        match = re.search(r'hp([-+]?\d+)', tag.lower())
                        if match:
                            return int(match.group(1))
                    except:
                        pass
            
            # 从内容中推断血量变化
            if any(word in content_lower for word in ["受伤", "伤害", "损失", "hurt", "damage", "injured"]):
                return -5  # 默认受伤扣血
            elif any(word in content_lower for word in ["治疗", "恢复", "heal", "recover"]):
                return 5   # 默认治疗加血
            elif any(word in content_lower for word in ["死亡", "killed", "死了", "杀死", "被杀", "丧命"]):
                return -100  # 死亡大量扣血
            elif "成功" in content_lower or "success" in content_lower:
                return 0   # 成功但没有特殊说明，无血量变化
            else:
                return 0   # 默认无血量变化
        
        return 0  # 非结果类型元素默认无血量变化
    
    @property
    def food_change(self):
        """兼容性属性：为结果类型元素提供food_change属性"""
        if self.symbol_type == SymbolType.RESULT:
            # 从内容或语义标签中提取食物变化信息
            content_lower = self.content.lower()
            
            # 检查语义标签
            for tag in self.semantic_tags:
                if "食物变化" in tag:
                    try:
                        import re
                        match = re.search(r'食物变化([-+]?\d+)', tag)
                        if match:
                            return int(match.group(1))
                    except:
                        pass
            
            # 从内容推断
            if any(word in content_lower for word in ["吃", "eat", "食用", "消耗食物"]):
                return 10  # 吃东西增加食物值
            elif any(word in content_lower for word in ["饥饿", "hungry", "食物不足"]):
                return -5  # 饥饿减少食物值
        
        return 0
    
    @property
    def water_change(self):
        """兼容性属性：为结果类型元素提供water_change属性"""
        if self.symbol_type == SymbolType.RESULT:
            # 从内容或语义标签中提取水分变化信息
            content_lower = self.content.lower()
            
            # 检查语义标签
            for tag in self.semantic_tags:
                if "水分变化" in tag:
                    try:
                        import re
                        match = re.search(r'水分变化([-+]?\d+)', tag)
                        if match:
                            return int(match.group(1))
                    except:
                        pass
            
            # 从内容推断
            if any(word in content_lower for word in ["喝", "drink", "饮用", "补充水分"]):
                return 10  # 喝水增加水分值
            elif any(word in content_lower for word in ["口渴", "thirsty", "缺水"]):
                return -5  # 口渴减少水分值
        
        return 0

@dataclass  
class EOCATR_Tuple:
    """统一的EOCATR元组表示"""
    environment: Optional[SymbolicElement] = None    # E: 环境
    object: Optional[SymbolicElement] = None         # O: 对象
    character: Optional[SymbolicElement] = None      # C: 对象特征
    action: Optional[SymbolicElement] = None         # A: 行动
    tool: Optional[SymbolicElement] = None           # T: 工具
    result: Optional[SymbolicElement] = None         # R: 结果
    
    tuple_id: str = ""                               # 元组唯一标识
    confidence: float = 1.0                         # 置信度
    created_time: Optional[datetime] = None

    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
        if not self.tuple_id:
            self.tuple_id = self._generate_tuple_id()

    def _generate_tuple_id(self) -> str:
        """生成元组唯一标识"""
        elements = [self.environment, self.object, self.character, 
                   self.action, self.tool, self.result]
        content_str = "_".join([elem.symbol_id if elem else "NULL" for elem in elements])
        return f"TUPLE_{hashlib.md5(content_str.encode()).hexdigest()[:12]}"

    def get_non_null_elements(self) -> List[SymbolicElement]:
        """获取非空元素列表"""
        elements = []
        for elem in [self.environment, self.object, self.character, 
                    self.action, self.tool, self.result]:
            if elem is not None:
                elements.append(elem)
        return elements

    def get_element_by_type(self, symbol_type: SymbolType) -> Optional[SymbolicElement]:
        """根据类型获取元素"""
        type_mapping = {
            SymbolType.ENVIRONMENT: self.environment,
            SymbolType.OBJECT: self.object,
            SymbolType.CHARACTER: self.character,
            SymbolType.ACTION: self.action,
            SymbolType.TOOL: self.tool,
            SymbolType.RESULT: self.result
        }
        return type_mapping.get(symbol_type)

    def set_element_by_type(self, symbol_type: SymbolType, element: SymbolicElement):
        """根据类型设置元素"""
        if symbol_type == SymbolType.ENVIRONMENT:
            self.environment = element
        elif symbol_type == SymbolType.OBJECT:
            self.object = element
        elif symbol_type == SymbolType.CHARACTER:
            self.character = element
        elif symbol_type == SymbolType.ACTION:
            self.action = element
        elif symbol_type == SymbolType.TOOL:
            self.tool = element
        elif symbol_type == SymbolType.RESULT:
            self.result = element

    def is_tool_usage(self) -> bool:
        """判断是否为工具使用经验"""
        if self.tool is None:
            return False
        
        # 检查工具内容是否表示实际工具使用（非"无工具"、"none"等）
        tool_content = self.tool.content.lower() if self.tool.content else ""
        non_tool_indicators = ["无工具", "none", "无", "徒手", "bare_hands", "empty"]
        
        # 如果工具内容包含非工具指示词，则不是工具使用
        for indicator in non_tool_indicators:
            if indicator in tool_content:
                return False
        
        # 如果有明确的工具内容，则认为是工具使用
        return len(tool_content.strip()) > 0

    # === 兼容性属性：为了与BPM系统兼容 ===
    @property
    def object_category(self):
        """兼容性属性：返回object的枚举兼容对象"""
        if self.object is None:
            return None
        return EnumCompatWrapper(self.object.content)
    
    @property
    def characteristics(self):
        """兼容性属性：返回character的兼容对象"""
        if self.character is None:
            return None
        return CharacteristicsCompatWrapper(self.character.content)
    
    # === 兼容性方法：为BPM系统提供枚举兼容访问 ===
    def get_environment_compat(self):
        """获取环境的兼容包装器"""
        if self.environment is None:
            return None
        return EnumCompatWrapper(self.environment.content)
    
    def get_action_compat(self):
        """获取动作的兼容包装器"""
        if self.action is None:
            return None
        return EnumCompatWrapper(self.action.content)
    
    def get_tool_compat(self):
        """获取工具的兼容包装器"""
        if self.tool is None:
            return None
        return EnumCompatWrapper(self.tool.content)
    
    def get_result_compat(self):
        """获取结果的兼容包装器"""
        if self.result is None:
            return None
        return ResultCompatWrapper(self.result.content)

    def is_semantically_compatible(self, other: 'EOCATR_Tuple') -> bool:
        """检查与另一个元组的语义兼容性"""
        if not isinstance(other, EOCATR_Tuple):
            return False
        
        # 检查每个位置的元素兼容性
        my_elements = self.get_non_null_elements()
        other_elements = other.get_non_null_elements()
        
        compatibility_scores = []
        for my_elem in my_elements:
            for other_elem in other_elements:
                if my_elem.symbol_type == other_elem.symbol_type:
                    similarity = my_elem.get_semantic_similarity(other_elem)
                    compatibility_scores.append(similarity)
        
        # 平均兼容性得分
        avg_compatibility = sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.0
        return avg_compatibility > 0.5

    # === BMP兼容性属性：为了与BPM系统兼容 ===
    @property
    def success(self):
        """兼容性属性：判断经验是否成功"""
        if self.result is None:
            return False
        return self.result.success

    @property
    def reward(self):
        """兼容性属性：获取经验奖励"""
        if self.result is None:
            return 0.0
        return self.result.reward

    @property
    def player_id(self):
        """兼容性属性：获取玩家ID"""
        # 从环境信息中提取玩家ID，或返回默认值
        return getattr(self, '_player_id', 'unknown_player')
    
    @property
    def experience_id(self):
        """兼容性属性：获取经验ID"""
        # 使用tuple_id作为经验ID
        return getattr(self, 'tuple_id', 'unknown_experience')

class SymbolicEncoder:
    """符号编码器 - 将符号转换为标准格式"""
    
    @staticmethod
    def encode_element(element: SymbolicElement) -> Dict[str, Any]:
        """编码单个符号元素"""
        encoded = asdict(element)
        # 处理枚举类型
        encoded['symbol_type'] = element.symbol_type.value
        encoded['abstraction_level'] = element.abstraction_level.value
        # 处理时间类型
        if element.created_time:
            encoded['created_time'] = element.created_time.isoformat()
        if element.updated_time:
            encoded['updated_time'] = element.updated_time.isoformat()
        
        logger.debug(f"符号编码完成: {element.symbol_id}")
        return encoded

    @staticmethod
    def encode_tuple(tuple_obj: EOCATR_Tuple) -> Dict[str, Any]:
        """编码EOCATR元组"""
        encoded = {
            'tuple_id': tuple_obj.tuple_id,
            'confidence': tuple_obj.confidence,
            'created_time': tuple_obj.created_time.isoformat() if tuple_obj.created_time else None,
            'elements': {}
        }
        
        # 编码各个元素
        for field_name, symbol_type in [
            ('environment', SymbolType.ENVIRONMENT),
            ('object', SymbolType.OBJECT), 
            ('character', SymbolType.CHARACTER),
            ('action', SymbolType.ACTION),
            ('tool', SymbolType.TOOL),
            ('result', SymbolType.RESULT)
        ]:
            element = getattr(tuple_obj, field_name)
            if element is not None:
                encoded['elements'][field_name] = SymbolicEncoder.encode_element(element)
        
        logger.debug(f"元组编码完成: {tuple_obj.tuple_id}")
        return encoded

class SymbolicDecoder:
    """符号解码器 - 将标准格式转换为符号对象"""
    
    @staticmethod
    def decode_element(encoded: Dict[str, Any]) -> SymbolicElement:
        """解码单个符号元素"""
        # 处理枚举类型
        symbol_type = SymbolType(encoded['symbol_type'])
        abstraction_level = AbstractionLevel(encoded['abstraction_level'])
        
        # 处理时间类型
        created_time = None
        if encoded.get('created_time'):
            created_time = datetime.fromisoformat(encoded['created_time'])
        
        updated_time = None
        if encoded.get('updated_time'):
            updated_time = datetime.fromisoformat(encoded['updated_time'])
        
        element = SymbolicElement(
            symbol_id=encoded['symbol_id'],
            symbol_type=symbol_type,
            content=encoded['content'],
            abstraction_level=abstraction_level,
            semantic_tags=encoded['semantic_tags'],
            frequency=encoded.get('frequency', 0),
            quality_score=encoded.get('quality_score', 0.0),
            created_time=created_time,
            updated_time=updated_time
        )
        
        logger.debug(f"符号解码完成: {element.symbol_id}")
        return element

    @staticmethod
    def decode_tuple(encoded: Dict[str, Any]) -> EOCATR_Tuple:
        """解码EOCATR元组"""
        created_time = None
        if encoded.get('created_time'):
            created_time = datetime.fromisoformat(encoded['created_time'])
        
        tuple_obj = EOCATR_Tuple(
            tuple_id=encoded['tuple_id'],
            confidence=encoded.get('confidence', 1.0),
            created_time=created_time
        )
        
        # 解码各个元素
        elements = encoded.get('elements', {})
        for field_name in ['environment', 'object', 'character', 'action', 'tool', 'result']:
            if field_name in elements:
                element = SymbolicDecoder.decode_element(elements[field_name])
                setattr(tuple_obj, field_name, element)
        
        logger.debug(f"元组解码完成: {tuple_obj.tuple_id}")
        return tuple_obj

class SymbolicRegistry:
    """符号注册表 - 管理所有符号的全局注册"""
    
    def __init__(self):
        self.elements: Dict[str, SymbolicElement] = {}
        self.tuples: Dict[str, EOCATR_Tuple] = {}
        self.type_index: Dict[SymbolType, List[str]] = {t: [] for t in SymbolType}
        self.content_index: Dict[str, List[str]] = {}  # 内容到ID的索引
        
        logger.info("Symbol registry initialization completed")

    def register_element(self, element: SymbolicElement) -> str:
        """注册符号元素"""
        element_id = element.symbol_id
        self.elements[element_id] = element
        
        # 更新类型索引
        if element_id not in self.type_index[element.symbol_type]:
            self.type_index[element.symbol_type].append(element_id)
        
        # 更新内容索引
        content_key = element.content.lower()
        if content_key not in self.content_index:
            self.content_index[content_key] = []
        if element_id not in self.content_index[content_key]:
            self.content_index[content_key].append(element_id)
        
        logger.info(f"Symbol element registered: {element_id} - {element.content}")
        return element_id

    def register_tuple(self, tuple_obj: EOCATR_Tuple) -> str:
        """注册EOCATR元组"""
        # 首先注册元组中的所有元素
        for element in tuple_obj.get_non_null_elements():
            self.register_element(element)
        
        # 注册元组本身
        tuple_id = tuple_obj.tuple_id
        self.tuples[tuple_id] = tuple_obj
        
        logger.info(f"EOCATR tuple registered: {tuple_id}")
        return tuple_id

    def get_element(self, element_id: str) -> Optional[SymbolicElement]:
        """获取符号元素"""
        return self.elements.get(element_id)

    def get_tuple(self, tuple_id: str) -> Optional[EOCATR_Tuple]:
        """获取EOCATR元组"""
        return self.tuples.get(tuple_id)

    def find_elements_by_type(self, symbol_type: SymbolType) -> List[SymbolicElement]:
        """根据类型查找符号元素"""
        element_ids = self.type_index.get(symbol_type, [])
        return [self.elements[eid] for eid in element_ids if eid in self.elements]

    def find_elements_by_content(self, content: str) -> List[SymbolicElement]:
        """根据内容查找符号元素"""
        content_key = content.lower()
        element_ids = self.content_index.get(content_key, [])
        return [self.elements[eid] for eid in element_ids if eid in self.elements]

    def find_similar_elements(self, element: SymbolicElement, threshold: float = 0.5) -> List[Tuple[SymbolicElement, float]]:
        """查找相似的符号元素"""
        similar_elements = []
        
        # 在同类型元素中查找
        candidates = self.find_elements_by_type(element.symbol_type)
        
        for candidate in candidates:
            if candidate.symbol_id != element.symbol_id:
                similarity = element.get_semantic_similarity(candidate)
                if similarity >= threshold:
                    similar_elements.append((candidate, similarity))
        
        # 按相似度排序
        similar_elements.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"找到 {len(similar_elements)} 个相似符号 (阈值: {threshold})")
        return similar_elements

    def get_statistics(self) -> Dict[str, Any]:
        """获取注册表统计信息"""
        stats = {
            'total_elements': len(self.elements),
            'total_tuples': len(self.tuples),
            'elements_by_type': {t.value: len(ids) for t, ids in self.type_index.items()},
            'avg_quality_score': 0.0,
            'avg_frequency': 0.0
        }
        
        if self.elements:
            total_quality = sum(elem.quality_score for elem in self.elements.values())
            total_frequency = sum(elem.frequency for elem in self.elements.values())
            stats['avg_quality_score'] = total_quality / len(self.elements)
            stats['avg_frequency'] = total_frequency / len(self.elements)
        
        return stats

# 全局符号注册表实例
global_registry = SymbolicRegistry()

def create_element(symbol_type: SymbolType, content: str, 
                  abstraction_level: AbstractionLevel = AbstractionLevel.CONCRETE,
                  semantic_tags: List[str] = None) -> SymbolicElement:
    """便捷函数：创建并注册符号元素"""
    if semantic_tags is None:
        semantic_tags = []
        
    element = SymbolicElement(
        symbol_id="",  # 将自动生成
        symbol_type=symbol_type,
        content=content,
        abstraction_level=abstraction_level,
        semantic_tags=semantic_tags
    )
    
    global_registry.register_element(element)
    return element

def create_tuple(**kwargs) -> EOCATR_Tuple:
    """便捷函数：创建并注册EOCATR元组"""
    tuple_obj = EOCATR_Tuple(**kwargs)
    global_registry.register_tuple(tuple_obj)
    return tuple_obj

# 示例用法和测试
if __name__ == "__main__":
    # 创建符号元素示例
    tiger = create_element(SymbolType.OBJECT, "老虎", AbstractionLevel.CONCRETE, ["动物", "危险", "猛兽"])
    forest = create_element(SymbolType.ENVIRONMENT, "森林", AbstractionLevel.CONCRETE, ["自然", "野外"])
    approach = create_element(SymbolType.ACTION, "靠近", AbstractionLevel.CONCRETE, ["移动", "主动"])
    injured = create_element(SymbolType.RESULT, "受伤", AbstractionLevel.CONCRETE, ["负面", "伤害"])
    
    # 创建EOCATR元组示例
    experience_tuple = create_tuple(
        environment=forest,
        object=tiger,
        action=approach,
        result=injured,
        confidence=0.9
    )
    
    # 打印统计信息
    stats = global_registry.get_statistics()
    print(f"符号注册表统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 测试编码解码
    encoded = SymbolicEncoder.encode_tuple(experience_tuple)
    decoded = SymbolicDecoder.decode_tuple(encoded)
    print(f"编码解码测试通过: {decoded.tuple_id == experience_tuple.tuple_id}") 