#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
data_format_unifier.py
数据格式统一化模块

解决AI生存系统中的数据格式不一致问题，提供统一的数据格式规范和转换接口。
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union, Tuple
import json
import time

# === 统一数据格式枚举定义 ===

class ActionType(Enum):
    """统一动作类型枚举"""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down" 
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_TO = "move_to"
    COLLECT = "collect"
    DRINK = "drink"
    ATTACK = "attack"
    FLEE = "flee"
    EXPLORE = "explore"
    WAIT = "wait"
    SHARE_INFO = "share_info"
    COOPERATE = "cooperate"
    UNKNOWN = "unknown"

class StateType(Enum):
    """统一状态类型枚举"""
    HEALTH = "health"
    FOOD = "food"
    WATER = "water"
    POSITION = "position"
    PHASE = "phase"
    DEVELOPMENT_STAGE = "development_stage"
    SURVIVAL_DAYS = "survival_days"
    REPUTATION = "reputation"

class ExperienceType(Enum):
    """统一经验类型枚举"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    INFERRED = "inferred"
    OBSERVED = "observed"
    SIMULATED = "simulated"

class DataSourceType(Enum):
    """数据来源类型枚举"""
    PLAYER_ACTION = "player_action"
    ENVIRONMENT_CHANGE = "environment_change"
    AI_MODULE = "ai_module"
    INTERACTION = "interaction"
    SYSTEM_EVENT = "system_event"

# === 统一数据结构定义 ===

@dataclass
class UnifiedPosition:
    """统一位置数据结构"""
    x: float
    y: float
    z: float = 0.0  # 为3D扩展预留
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}
    
    def distance_to(self, other: 'UnifiedPosition') -> float:
        """计算到另一个位置的距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

@dataclass
class UnifiedAction:
    """统一动作数据结构"""
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0
    source: DataSourceType = DataSourceType.PLAYER_ACTION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "source": self.source.value
        }

@dataclass
class UnifiedState:
    """统一状态数据结构"""
    values: Dict[StateType, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_value(self, state_type: StateType, default: Any = None) -> Any:
        """获取状态值"""
        return self.values.get(state_type, default)
    
    def set_value(self, state_type: StateType, value: Any):
        """设置状态值"""
        self.values[state_type] = value
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "values": {k.value: v for k, v in self.values.items()},
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class UnifiedResult:
    """统一结果数据结构"""
    success: bool
    effects: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, float] = field(default_factory=dict)
    side_effects: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def add_reward(self, reward_type: str, value: float):
        """添加奖励"""
        self.rewards[reward_type] = value
    
    def get_total_reward(self) -> float:
        """获取总奖励"""
        return sum(self.rewards.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "effects": self.effects,
            "rewards": self.rewards,
            "side_effects": self.side_effects,
            "timestamp": self.timestamp
        }

@dataclass
class UnifiedExperience:
    """统一经验数据结构"""
    experience_id: str
    action: UnifiedAction
    state_before: UnifiedState
    state_after: UnifiedState
    result: UnifiedResult
    experience_type: ExperienceType = ExperienceType.DIRECT
    importance: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "action": self.action.to_dict(),
            "state_before": self.state_before.to_dict(),
            "state_after": self.state_after.to_dict(),
            "result": self.result.to_dict(),
            "experience_type": self.experience_type.value,
            "importance": self.importance,
            "context": self.context,
            "tags": self.tags
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

# === 数据格式转换器类 ===

class DataFormatUnifier:
    """数据格式统一化器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.conversion_stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "conversion_types": {}
        }
    
    def log(self, message: str):
        """日志记录"""
        if self.logger:
            self.logger.log(message)
    
    # === 动作转换方法 ===
    
    def convert_action_to_unified(self, action_data: Any) -> UnifiedAction:
        """将各种格式的动作转换为统一格式"""
        try:
            if isinstance(action_data, str):
                return self._convert_string_action(action_data)
            elif isinstance(action_data, int):
                return self._convert_numeric_action(action_data)
            elif isinstance(action_data, dict):
                return self._convert_dict_action(action_data)
            elif hasattr(action_data, 'action_type'):
                return action_data  # 已经是统一格式
            else:
                raise ValueError(f"无法识别的动作格式: {type(action_data)}")
        except Exception as e:
            self.conversion_stats["failed_conversions"] += 1
            self.log(f"动作转换失败: {e}")
            return UnifiedAction(ActionType.UNKNOWN)
    
    def _convert_string_action(self, action_str: str) -> UnifiedAction:
        """转换字符串格式的动作"""
        action_mapping = {
            "up": ActionType.MOVE_UP,
            "down": ActionType.MOVE_DOWN,
            "left": ActionType.MOVE_LEFT,
            "right": ActionType.MOVE_RIGHT,
            "move_up": ActionType.MOVE_UP,
            "move_down": ActionType.MOVE_DOWN,
            "move_left": ActionType.MOVE_LEFT,
            "move_right": ActionType.MOVE_RIGHT,
            "collect": ActionType.COLLECT,
            "drink": ActionType.DRINK,
            "attack": ActionType.ATTACK,
            "flee": ActionType.FLEE,
            "explore": ActionType.EXPLORE,
            "wait": ActionType.WAIT,
            "share": ActionType.SHARE_INFO,
            "cooperate": ActionType.COOPERATE
        }
        
        action_type = action_mapping.get(action_str.lower(), ActionType.UNKNOWN)
        return UnifiedAction(action_type)
    
    def _convert_numeric_action(self, action_num: int) -> UnifiedAction:
        """转换数字格式的动作"""
        numeric_mapping = {
            0: ActionType.MOVE_UP,
            1: ActionType.MOVE_DOWN,
            2: ActionType.MOVE_LEFT,
            3: ActionType.MOVE_RIGHT,
            4: ActionType.DRINK,
            5: ActionType.COLLECT,
            6: ActionType.ATTACK,
            7: ActionType.FLEE,
            8: ActionType.EXPLORE,
            9: ActionType.WAIT
        }
        
        action_type = numeric_mapping.get(action_num, ActionType.UNKNOWN)
        return UnifiedAction(action_type)
    
    def _convert_dict_action(self, action_dict: dict) -> UnifiedAction:
        """转换字典格式的动作"""
        action_type_str = action_dict.get("action", action_dict.get("type", "unknown"))
        action_type = self._convert_string_action(action_type_str).action_type
        
        parameters = action_dict.get("parameters", {})
        confidence = action_dict.get("confidence", 1.0)
        
        return UnifiedAction(
            action_type=action_type,
            parameters=parameters,
            confidence=confidence
        )
    
    # === 状态转换方法 ===
    
    def convert_state_to_unified(self, state_data: Any) -> UnifiedState:
        """将各种格式的状态转换为统一格式"""
        try:
            if isinstance(state_data, dict):
                return self._convert_dict_state(state_data)
            elif isinstance(state_data, list):
                return self._convert_list_state(state_data)
            elif hasattr(state_data, 'values'):
                return state_data  # 已经是统一格式
            else:
                raise ValueError(f"无法识别的状态格式: {type(state_data)}")
        except Exception as e:
            self.conversion_stats["failed_conversions"] += 1
            self.log(f"状态转换失败: {e}")
            return UnifiedState()
    
    def _convert_dict_state(self, state_dict: dict) -> UnifiedState:
        """转换字典格式的状态"""
        unified_state = UnifiedState()
        
        # 映射常见的状态键名
        key_mapping = {
            "hp": StateType.HEALTH,
            "health": StateType.HEALTH,
            "food": StateType.FOOD,
            "water": StateType.WATER,
            "x": "position_x",
            "y": "position_y",
            "position": StateType.POSITION,
            "phase": StateType.PHASE,
            "development_stage": StateType.DEVELOPMENT_STAGE,
            "developmental_stage": StateType.DEVELOPMENT_STAGE,
            "survival_days": StateType.SURVIVAL_DAYS,
            "reputation": StateType.REPUTATION
        }
        
        for key, value in state_dict.items():
            if key in key_mapping:
                state_type = key_mapping[key]
                if isinstance(state_type, StateType):
                    unified_state.set_value(state_type, value)
                else:
                    # 处理特殊情况
                    if key in ["x", "y"]:
                        if StateType.POSITION not in unified_state.values:
                            unified_state.values[StateType.POSITION] = {}
                        unified_state.values[StateType.POSITION][key] = value
            else:
                # 存储到metadata中
                unified_state.metadata[key] = value
        
        return unified_state
    
    def _convert_list_state(self, state_list: list) -> UnifiedState:
        """转换列表格式的状态"""
        unified_state = UnifiedState()
        
        # 假设列表按固定顺序：[health, food, water, x, y, ...]
        if len(state_list) >= 5:
            unified_state.set_value(StateType.HEALTH, state_list[0])
            unified_state.set_value(StateType.FOOD, state_list[1])
            unified_state.set_value(StateType.WATER, state_list[2])
            unified_state.set_value(StateType.POSITION, {"x": state_list[3], "y": state_list[4]})
        
        return unified_state
    
    # === 经验转换方法 ===
    
    def convert_experience_to_unified(self, experience_data: Any, experience_id: str = None) -> UnifiedExperience:
        """将各种格式的经验转换为统一格式"""
        try:
            if experience_id is None:
                experience_id = f"exp_{int(time.time() * 1000)}"
            
            if isinstance(experience_data, dict):
                return self._convert_dict_experience(experience_data, experience_id)
            elif hasattr(experience_data, 'action'):
                return experience_data  # 已经是统一格式
            else:
                raise ValueError(f"无法识别的经验格式: {type(experience_data)}")
        except Exception as e:
            self.conversion_stats["failed_conversions"] += 1
            self.log(f"经验转换失败: {e}")
            # 返回空经验
            return UnifiedExperience(
                experience_id=experience_id or "unknown",
                action=UnifiedAction(ActionType.UNKNOWN),
                state_before=UnifiedState(),
                state_after=UnifiedState(),
                result=UnifiedResult(success=False)
            )
    
    def _convert_dict_experience(self, exp_dict: dict, experience_id: str) -> UnifiedExperience:
        """转换字典格式的经验"""
        action = self.convert_action_to_unified(exp_dict.get("action", {}))
        
        state_before = self.convert_state_to_unified(exp_dict.get("state_before", {}))
        state_after = self.convert_state_to_unified(exp_dict.get("state_after", {}))
        
        result_data = exp_dict.get("result", {})
        result = UnifiedResult(
            success=result_data.get("success", True),
            effects=result_data.get("effects", {}),
            rewards=result_data.get("rewards", {})
        )
        
        return UnifiedExperience(
            experience_id=experience_id,
            action=action,
            state_before=state_before,
            state_after=state_after,
            result=result,
            importance=exp_dict.get("importance", 0.5),
            context=exp_dict.get("context", {}),
            tags=exp_dict.get("tags", [])
        )
    
    # === EOCAR格式兼容性 ===
    
    def convert_eocar_to_unified(self, eocar_tuple) -> UnifiedExperience:
        """将EOCAR_Tuple转换为统一经验格式"""
        try:
            # 转换动作
            action = UnifiedAction(
                action_type=ActionType(eocar_tuple.action.value) if hasattr(eocar_tuple.action, 'value') else ActionType.UNKNOWN,
                timestamp=eocar_tuple.timestamp,
                confidence=eocar_tuple.confidence
            )
            
            # 转换状态（从characteristics提取）
            state_before = UnifiedState()
            if hasattr(eocar_tuple.characteristics, 'position'):
                state_before.set_value(StateType.POSITION, eocar_tuple.characteristics.position)
            
            # 创建状态后（基于结果推断）
            state_after = UnifiedState(values=state_before.values.copy())
            
            # 转换结果
            result = UnifiedResult(
                success=True,  # 假设EOCATR记录的都是成功的经验
                effects=eocar_tuple.result.__dict__ if hasattr(eocar_tuple.result, '__dict__') else {}
            )
            
            return UnifiedExperience(
                experience_id=f"eocar_{eocar_tuple.timestamp}",
                action=action,
                state_before=state_before,
                state_after=state_after,
                result=result,
                experience_type=ExperienceType(eocar_tuple.source) if hasattr(eocar_tuple, 'source') else ExperienceType.DIRECT,
                importance=eocar_tuple.importance if hasattr(eocar_tuple, 'importance') else 0.5
            )
        except Exception as e:
            self.log(f"EOCAR转换失败: {e}")
            return UnifiedExperience(
                experience_id="eocar_failed",
                action=UnifiedAction(ActionType.UNKNOWN),
                state_before=UnifiedState(),
                state_after=UnifiedState(),
                result=UnifiedResult(success=False)
            )
    
    def convert_unified_to_eocar(self, unified_exp: UnifiedExperience):
        """将统一经验格式转换为EOCAR格式（如果需要）"""
        # 这个方法需要导入EOCAR相关类，暂时返回字典格式
        return {
            "action": unified_exp.action.action_type.value,
            "result": unified_exp.result.to_dict(),
            "importance": unified_exp.importance,
            "timestamp": unified_exp.action.timestamp
        }
    
    # === 统计和验证方法 ===
    
    def validate_unified_data(self, data: Union[UnifiedAction, UnifiedState, UnifiedExperience]) -> bool:
        """验证统一格式数据的完整性"""
        try:
            if isinstance(data, UnifiedAction):
                return self._validate_action(data)
            elif isinstance(data, UnifiedState):
                return self._validate_state(data)
            elif isinstance(data, UnifiedExperience):
                return self._validate_experience(data)
            else:
                return False
        except Exception:
            return False
    
    def _validate_action(self, action: UnifiedAction) -> bool:
        """验证动作数据"""
        return (
            isinstance(action.action_type, ActionType) and
            isinstance(action.parameters, dict) and
            isinstance(action.confidence, (int, float)) and
            0 <= action.confidence <= 1
        )
    
    def _validate_state(self, state: UnifiedState) -> bool:
        """验证状态数据"""
        return (
            isinstance(state.values, dict) and
            isinstance(state.metadata, dict) and
            isinstance(state.timestamp, (int, float))
        )
    
    def _validate_experience(self, experience: UnifiedExperience) -> bool:
        """验证经验数据"""
        return (
            isinstance(experience.experience_id, str) and
            self._validate_action(experience.action) and
            self._validate_state(experience.state_before) and
            self._validate_state(experience.state_after) and
            isinstance(experience.result, UnifiedResult)
        )
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """获取转换统计信息"""
        success_rate = 0.0
        if self.conversion_stats["total_conversions"] > 0:
            success_rate = self.conversion_stats["successful_conversions"] / self.conversion_stats["total_conversions"]
        
        return {
            "total_conversions": self.conversion_stats["total_conversions"],
            "successful_conversions": self.conversion_stats["successful_conversions"],
            "failed_conversions": self.conversion_stats["failed_conversions"],
            "success_rate": success_rate,
            "conversion_types": self.conversion_stats["conversion_types"]
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.conversion_stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "conversion_types": {}
        }

# === 全局数据格式验证器 ===

class DataFormatValidator:
    """数据格式验证器"""
    
    @staticmethod
    def is_unified_format(data: Any) -> bool:
        """检查数据是否为统一格式"""
        return isinstance(data, (UnifiedAction, UnifiedState, UnifiedExperience, UnifiedResult))
    
    @staticmethod
    def get_data_format_type(data: Any) -> str:
        """获取数据格式类型"""
        if isinstance(data, UnifiedAction):
            return "unified_action"
        elif isinstance(data, UnifiedState):
            return "unified_state"
        elif isinstance(data, UnifiedExperience):
            return "unified_experience"
        elif isinstance(data, dict):
            return "dictionary"
        elif isinstance(data, list):
            return "list"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "numeric"
        else:
            return "unknown"
    
    @staticmethod
    def suggest_conversion_method(data: Any) -> str:
        """建议转换方法"""
        data_type = DataFormatValidator.get_data_format_type(data)
        
        suggestions = {
            "dictionary": "使用 convert_experience_to_unified() 或 convert_state_to_unified()",
            "list": "使用 convert_state_to_unified() 处理状态列表",
            "string": "使用 convert_action_to_unified() 处理动作字符串",
            "numeric": "使用 convert_action_to_unified() 处理数字动作",
            "unknown": "检查数据类型，可能需要自定义转换方法"
        }
        
        return suggestions.get(data_type, "数据已为统一格式或无需转换")

# === 使用示例和工厂函数 ===

def create_data_format_unifier(logger=None) -> DataFormatUnifier:
    """创建数据格式统一化器实例"""
    return DataFormatUnifier(logger=logger)

def quick_convert_action(action_data: Any) -> UnifiedAction:
    """快速转换动作数据"""
    unifier = DataFormatUnifier()
    return unifier.convert_action_to_unified(action_data)

def quick_convert_state(state_data: Any) -> UnifiedState:
    """快速转换状态数据"""
    unifier = DataFormatUnifier()
    return unifier.convert_state_to_unified(state_data)

def quick_convert_experience(experience_data: Any, experience_id: str = None) -> UnifiedExperience:
    """快速转换经验数据"""
    unifier = DataFormatUnifier()
    return unifier.convert_experience_to_unified(experience_data, experience_id)

if __name__ == "__main__":
    # 简单测试
    unifier = DataFormatUnifier()
    
    # 测试动作转换
    test_actions = [
        "collect",
        5,
        {"action": "move_up", "confidence": 0.8}
    ]
    
    for action in test_actions:
        unified = unifier.convert_action_to_unified(action)
        print(f"原始动作: {action} -> 统一格式: {unified.action_type.value}")
    
    # 测试状态转换
    test_state = {"hp": 80, "food": 60, "water": 70, "x": 10, "y": 15}
    unified_state = unifier.convert_state_to_unified(test_state)
    print(f"统一状态: {unified_state.to_dict()}")
    
    print("数据格式统一化模块测试完成！") 