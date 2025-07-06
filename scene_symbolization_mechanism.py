"""
场景符号化机制（Scene Symbolization Mechanism, SSM）

实现对环境感知信息的结构化符号化，基于E-O-C-A-T-R格式：
- E (Environment): 环境上下文
- O (Object): 感知对象
- C (Characteristics): 对象特征
- A (Action): 基础动作（攻击、移动、采集等）
- T (Tool): 使用的工具（可选，默认为None）
- R (Result): 动作结果

V3.0兼容版本：使用symbolic_core_v3.py的统一符号系统

作者：AI生存游戏项目组
版本：3.0.0（V3符号系统兼容版）
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# 导入V3符号系统
from symbolic_core_v3 import (
    SymbolicElement, EOCATR_Tuple, SymbolType, AbstractionLevel,
    create_element, create_tuple
)

class SymbolicEnvironment(Enum):
    """环境上下文符号化枚举"""
    OPEN_FIELD = "open_field"          # 开阔地
    FOREST = "forest"                  # 森林
    WATER_AREA = "water_area"          # 水域
    DANGEROUS_ZONE = "dangerous_zone"  # 危险区域
    SAFE_ZONE = "safe_zone"            # 安全区域
    RESOURCE_RICH = "resource_rich"    # 资源丰富区
    RESOURCE_SPARSE = "resource_sparse" # 资源稀少区


class SymbolicObjectCategory(Enum):
    """对象类别符号化枚举"""
    SELF = "self"                      # 自身
    EDIBLE_PLANT = "edible_plant"      # 可食用植物
    POISONOUS_PLANT = "poisonous_plant" # 有毒植物
    WATER_SOURCE = "water_source"      # 水源
    DANGEROUS_ANIMAL = "dangerous_animal" # 危险动物
    HARMLESS_ANIMAL = "harmless_animal"  # 无害动物
    FELLOW_PLAYER = "fellow_player"    # 同类玩家
    OTHER_PLAYER = "other_player"      # 其他类型玩家
    TERRAIN = "terrain"                # 地形
    RESOURCE = "resource"              # 资源
    SHELTER = "shelter"                # 庇护所


class SymbolicAction(Enum):
    """基础动作符号化枚举（不包含工具信息）"""
    MOVE = "move"                      # 移动
    EAT = "eat"                        # 进食
    DRINK = "drink"                    # 饮水
    GATHER = "gather"                  # 收集
    EXPLORE = "explore"                # 探索
    INTERACT = "interact"              # 交互
    AVOID = "avoid"                    # 躲避
    ATTACK = "attack"                  # 攻击（基础动作，工具信息在T字段）
    REST = "rest"                      # 休息
    COMMUNICATE = "communicate"        # 交流


class SymbolicTool(Enum):
    """工具符号化枚举"""
    NONE = "none"                      # 无工具（徒手）
    SPEAR = "spear"                    # 长矛
    STONE = "stone"                    # 石头
    BOW = "bow"                        # 弓箭
    BASKET = "basket"                  # 篮子
    SHOVEL = "shovel"                  # 铲子
    STICK = "stick"                    # 棍子


@dataclass
class SymbolicCharacteristics:
    """符号化特征类"""
    distance: float = 1.0              # 距离
    position: Optional[Dict] = None     # 位置坐标
    
    # 对象属性
    dangerous: bool = False            # 是否危险
    edible: bool = False              # 是否可食用
    poisonous: bool = False           # 是否有毒
    size: str = "medium"              # 大小 (small/medium/large)
    activity_state: str = "static"    # 活动状态
    
    # 资源属性  
    nutrition_value: int = 0          # 营养价值
    water_value: int = 0              # 水分价值
    accessibility: str = "accessible" # 可接近性
    
    # 社交属性
    trustworthiness: float = 0.5      # 可信度
    cooperation_level: str = "neutral" # 合作程度
    player_type: Optional[str] = None  # 玩家类型（用于其他玩家）
    
    # 动态属性
    health_state: str = "normal"      # 健康状态


@dataclass
class SymbolicResult:
    """符号化结果类"""
    success: bool = False             # 是否成功
    reward: float = 0.0               # 奖励值
    
    # 状态变化
    hp_change: int = 0                # 生命值变化
    food_change: int = 0              # 食物变化
    water_change: int = 0             # 水分变化
    
    # 学习与发现
    experience_gained: bool = True     # 是否获得经验
    new_objects_discovered: Optional[List[str]] = None  # 发现的新对象
    new_knowledge: Optional[str] = None               # 新获得的知识
    
    # 工具相关结果
    tool_effectiveness: Optional[float] = None        # 工具效果评分
    tool_durability_change: int = 0                   # 工具耐久度变化


class SymbolicConverter:
    """符号转换器 - 将枚举类型转换为V3 SymbolicElement"""
    
    @staticmethod
    def enum_to_element(enum_value: Enum, symbol_type: SymbolType, 
                       abstraction_level: AbstractionLevel = AbstractionLevel.CONCRETE,
                       semantic_tags: List[str] = None) -> SymbolicElement:
        """将枚举值转换为SymbolicElement"""
        if semantic_tags is None:
            semantic_tags = []
            
        content = enum_value.value if hasattr(enum_value, 'value') else str(enum_value)
        
        return create_element(
            symbol_type=symbol_type,
            content=content,
            abstraction_level=abstraction_level,
            semantic_tags=semantic_tags
        )
    
    @staticmethod
    def characteristics_to_element(characteristics: SymbolicCharacteristics) -> SymbolicElement:
        """将特征转换为SymbolicElement"""
        # 构建特征描述
        features = []
        if characteristics.dangerous:
            features.append("dangerous")
        if characteristics.edible:
            features.append("edible")
        if characteristics.poisonous:
            features.append("poisonous")
        features.append(f"size_{characteristics.size}")
        features.append(f"distance_{characteristics.distance:.1f}")
        
        content = "+".join(features) if features else "normal_feature"
        semantic_tags = features
        
        return create_element(
            symbol_type=SymbolType.CHARACTER,
            content=content,
            abstraction_level=AbstractionLevel.CONCRETE,
            semantic_tags=semantic_tags
        )
    
    @staticmethod
    def result_to_element(result: SymbolicResult) -> SymbolicElement:
        """将结果转换为SymbolicElement"""
        if result.success:
            content = f"success_reward{result.reward:.1f}"
            semantic_tags = ["success", "positive_result"]
        else:
            content = f"failure_reward{result.reward:.1f}"
            semantic_tags = ["failure", "negative_result"]
            
        # Add change information
        if result.hp_change != 0:
            semantic_tags.append(f"hp_change{result.hp_change}")
        if result.food_change != 0:
            semantic_tags.append(f"food_change{result.food_change}")
        if result.water_change != 0:
            semantic_tags.append(f"water_change{result.water_change}")
            
        return create_element(
            symbol_type=SymbolType.RESULT,
            content=content,
            abstraction_level=AbstractionLevel.CONCRETE,
            semantic_tags=semantic_tags
        )


class SceneSymbolizationMechanism:
    """场景符号化机制主类"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.vision_range = 10  # 默认视野范围
        self.last_action_with_tool = None  # 记录上次工具使用
        self.converter = SymbolicConverter()
        
    def symbolize_scene(self, game, player) -> List[EOCATR_Tuple]:
        """
        将游戏场景符号化为E-O-C-A-T-R元组列表（V3兼容版本）
        
        Args:
            game: 游戏对象
            player: 玩家对象
            
        Returns:
            List[EOCATR_Tuple]: 符号化的场景元组列表（V3格式）
        """
        # 🔧 强制调试输出 - 不依赖logger，直接print确保能看到
        print(f"🔧 SSM V3版本被调用：{player.name}，logger状态：{self.logger is not None}")
        
        # 🔧 强制文件写入调试 - 确保能看到SSM被调用
        try:
            with open("ssm_debug.txt", "a", encoding="utf-8") as f:
                f.write(f"🔧 SSM V3版本被调用：{player.name}，工具历史长度：{len(getattr(player, 'tool_usage_history', []))}\n")
        except:
            pass
        
        # 🔧 强制调试日志 - 确认SSM被调用
        if self.logger:
            self.logger.log(f"🔧 SSM V3版本开始执行：{player.name}，工具历史长度：{len(getattr(player, 'tool_usage_history', []))}")
        
        eocatr_tuples = []
        
        # 分析环境上下文
        environment_enum = self._analyze_environment_context(game, player)
        environment_element = self.converter.enum_to_element(
            environment_enum, SymbolType.ENVIRONMENT, 
            AbstractionLevel.CATEGORY, ["environment", "context"]
        )
        
        # 🔧 优先检测并记录工具使用经验
        tool_usage_tuples = self._detect_and_record_tool_usage_v3(game, player, environment_element)
        eocatr_tuples.extend(tool_usage_tuples)
        
        # 符号化自身状态
        self_tuple = self._symbolize_self_v3(player, environment_element)
        eocatr_tuples.append(self_tuple)
        
        # 符号化周围对象
        if hasattr(game, 'game_map'):
            # 符号化植物
            plant_tuples = self._symbolize_plants_v3(game, player, environment_element)
            eocatr_tuples.extend(plant_tuples)
            
            # 符号化动物
            animal_tuples = self._symbolize_animals_v3(game, player, environment_element)
            eocatr_tuples.extend(animal_tuples)
            
            # 符号化水源
            water_tuples = self._symbolize_water_sources_v3(game, player, environment_element)
            eocatr_tuples.extend(water_tuples)
        
        # 符号化其他玩家
        if hasattr(game, 'players'):
            player_tuples = self._symbolize_other_players_v3(game, player, environment_element)
            eocatr_tuples.extend(player_tuples)
        
        # 符号化地形特征
        terrain_tuples = self._symbolize_terrain_v3(game, player, environment_element)
        eocatr_tuples.extend(terrain_tuples)
        
        if self.logger:
            tool_count = len(tool_usage_tuples)
            total_count = len(eocatr_tuples)
            if tool_count > 0:
                self.logger.log(f"SSM V3符号化完成，生成{total_count}个E-O-C-A-T-R元组（含{tool_count}个工具使用记录）")
                # 🔧 新增：详细记录工具EOCATR
                for i, tool_tuple in enumerate(tool_usage_tuples):
                    tool_content = tool_tuple.tool.content if tool_tuple.tool else "no_tool"
                    action_content = tool_tuple.action.content if tool_tuple.action else "no_action"
                    object_content = tool_tuple.object.content if tool_tuple.object else "no_object"
                    self.logger.log(f"🔧 工具EOCATR V3[{i}]：{tool_content}+{action_content}+{object_content}")
            else:
                self.logger.log(f"SSM V3符号化完成，生成{total_count}个E-O-C-A-T-R元组")
        
        return eocatr_tuples

    def _detect_and_record_tool_usage_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """
        🔧 检测并记录工具使用情况（V3版本）
        
        检测玩家当前是否在使用工具，并创建相应的EOCATR记录
        """
        tool_usage_tuples = []
        
        # 🔧 强制调试输出（改为logger确保能看到）
        tool_history_length = len(getattr(player, 'tool_usage_history', []))
        if self.logger:
            self.logger.log(f"🔧 SSM V3工具检测：{player.name}，工具历史长度：{tool_history_length}")
        
        # 🔧 强制文件写入调试 - 详细记录工具检测流程
        try:
            with open("ssm_debug.txt", "a", encoding="utf-8") as f:
                f.write(f"🔧 开始V3工具检测：{player.name}，工具历史长度：{tool_history_length}\n")
        except:
            pass
        
        # 检测是否有工具使用记录
        current_tool_usage = self._get_current_tool_usage(player)
        
        if current_tool_usage:
            tool_name, target_type, action_type, success, effectiveness = current_tool_usage
            
            if self.logger:
                self.logger.log(f"🔧 检测到V3工具使用：{player.name} 使用{tool_name}对{target_type}执行{action_type}")
            
            # 🔧 强制文件写入调试 - 记录检测到的工具使用
            try:
                with open("ssm_debug.txt", "a", encoding="utf-8") as f:
                    f.write(f"🔧 检测到V3工具使用：{player.name} 使用{tool_name}对{target_type}执行{action_type}\n")
            except:
                pass
            
            # 转换为V3符号元素
            tool_element = self.converter.enum_to_element(
                self._map_tool_name_to_symbolic(tool_name), 
                SymbolType.TOOL, 
                AbstractionLevel.CONCRETE,
                ["tool", tool_name]
            )
            
            object_element = self.converter.enum_to_element(
                self._map_target_to_object_category(target_type),
                SymbolType.OBJECT,
                AbstractionLevel.CONCRETE,
                ["target", target_type]
            )
            
            action_element = self.converter.enum_to_element(
                self._map_action_name_to_symbolic(action_type),
                SymbolType.ACTION,
                AbstractionLevel.CONCRETE,
                ["action", action_type]
            )
            
            # 构建特征
            characteristics = SymbolicCharacteristics(
                position={"x": player.x, "y": player.y},
                distance=0.0,  # 工具使用通常是近距离的
                size=self._determine_target_size(target_type),
                dangerous=target_type in ['predator', 'Tiger', 'BlackBear']
            )
            condition_element = self.converter.characteristics_to_element(characteristics)
            
            # 构建结果
            result = SymbolicResult(
                success=success,
                reward=effectiveness if effectiveness else 0.0,
                tool_effectiveness=effectiveness,
                experience_gained=True
            )
            result_element = self.converter.result_to_element(result)
            
            # 创建V3工具使用的EOCATR记录
            tool_eocatr = create_tuple(
                environment=environment_element,
                object=object_element,
                character=condition_element,
                action=action_element,
                tool=tool_element,
                result=result_element
            )
            
            tool_usage_tuples.append(tool_eocatr)
            
            if self.logger:
                self.logger.log(f"🔧 创建工具EOCATR V3: {tool_eocatr.tuple_id}")
        
        return tool_usage_tuples
    
    def _get_current_tool_usage(self, player):
        """
        获取玩家当前的工具使用信息
        从玩家的工具使用历史中获取最新的使用记录
        """
        # 🔧 新增：检查玩家是否有最近的工具使用标记
        if hasattr(player, '_last_tool_used') and player._last_tool_used:
            tool_info = player._last_tool_used
            if self.logger:
                self.logger.log(f"🔧 {player.name} 检测到实时工具使用：{tool_info}")
            
            # 🔧 强制文件写入调试 - 记录检测到实时工具使用
            try:
                with open("ssm_debug.txt", "a", encoding="utf-8") as f:
                    f.write(f"🔧 检测到实时工具使用：{player.name} 工具={tool_info}\n")
            except:
                pass
            
            # 清除标记，避免重复检测
            player._last_tool_used = None
            
            # 🔧 修复：安全的工具信息提取，处理各种数据类型
            try:
                # 安全提取工具名称
                tool_obj = tool_info.get('tool', {})
                if hasattr(tool_obj, 'type'):
                    tool_name = tool_obj.type
                elif hasattr(tool_obj, 'name'):
                    tool_name = tool_obj.name
                elif isinstance(tool_obj, str):
                    tool_name = tool_obj
                elif isinstance(tool_obj, dict):
                    tool_name = tool_obj.get('type', tool_obj.get('name', 'unknown'))
                else:
                    tool_name = str(tool_obj) if tool_obj else 'unknown'
                
                # 安全提取其他信息
                target_type = tool_info.get('target_type', 'unknown')
                success = bool(tool_info.get('success', False))
                damage_or_gain = float(tool_info.get('damage_or_gain', 0))
                
            except Exception as extract_error:
                if self.logger:
                    self.logger.log(f"⚠️ 工具信息提取异常: {str(extract_error)}")
                tool_name = 'unknown'
                target_type = 'unknown'
                success = False
                damage_or_gain = 0
            
            # 确定动作类型
            action_type = 'attack' if any(target in target_type for target in ['predator', 'prey', 'bird', 'Tiger', 'BlackBear', 'Rabbit', 'Boar', 'Pheasant', 'Dove']) else 'gather'
            
            return (tool_name, target_type, action_type, success, damage_or_gain)
        
        if not hasattr(player, 'tool_usage_history') or not player.tool_usage_history:
            if self.logger:
                self.logger.log(f"🔧 {player.name} 没有tool_usage_history属性或为空")
            return None
        
        # 获取最新的工具使用记录
        latest_usage = player.tool_usage_history[-1]
        
        if self.logger:
            self.logger.log(f"🔧 {player.name} 最新工具使用记录：{latest_usage}")
        
        # 🔧 增强的工具使用记录处理
        try:
            # 安全提取工具类型
            tool_type = 'unknown'
            if isinstance(latest_usage, dict):
                tool_type = latest_usage.get('tool_type', 'unknown')
                if not tool_type or tool_type == 'unknown':
                    # 尝试其他可能的字段名
                    tool_type = latest_usage.get('tool', latest_usage.get('tool_name', 'unknown'))
            
            # 安全提取目标类型
            target_type = 'unknown'
            if isinstance(latest_usage, dict):
                target_type = latest_usage.get('target_type', 'unknown')
                if not target_type or target_type == 'unknown':
                    target_type = latest_usage.get('target', 'unknown')
            
            # 安全提取成功状态
            success = False
            if isinstance(latest_usage, dict):
                success_val = latest_usage.get('success', False)
                success = bool(success_val) if success_val is not None else False
            
            # 安全提取伤害或收益
            damage_or_gain = 0
            if isinstance(latest_usage, dict):
                damage_val = latest_usage.get('damage_or_gain', 0)
                try:
                    damage_or_gain = float(damage_val) if damage_val is not None else 0
                except (ValueError, TypeError):
                    damage_or_gain = 0
            
            if self.logger:
                self.logger.log(f"🔧 处理后的工具使用: 工具={tool_type}, 目标={target_type}, 成功={success}, 伤害/收益={damage_or_gain}")
        
        except Exception as process_error:
            if self.logger:
                self.logger.log(f"⚠️ 工具使用记录处理异常: {str(process_error)}")
            tool_type = 'unknown'
            target_type = 'unknown'
            success = False
            damage_or_gain = 0
        
        return (
            tool_type,
            target_type, 
            'attack' if any(target in target_type for target in ['predator', 'prey', 'bird', 'Tiger', 'BlackBear', 'Rabbit', 'Boar', 'Pheasant', 'Dove']) else 'gather',
            success,
            damage_or_gain
        )

    def _map_tool_name_to_symbolic(self, tool_name: str) -> SymbolicTool:
        """将工具名称映射到SymbolicTool枚举"""
        tool_mapping = {
            'Spear': SymbolicTool.SPEAR,
            'Stone': SymbolicTool.STONE, 
            'Bow': SymbolicTool.BOW,
            'Basket': SymbolicTool.BASKET,
            'Shovel': SymbolicTool.SHOVEL,
            'Stick': SymbolicTool.STICK,
            '长矛': SymbolicTool.SPEAR,
            '石头': SymbolicTool.STONE,
            '弓箭': SymbolicTool.BOW,
            '篮子': SymbolicTool.BASKET,
            '铁锹': SymbolicTool.SHOVEL,
            '棍子': SymbolicTool.STICK
        }
        return tool_mapping.get(tool_name, SymbolicTool.NONE)

    def _map_target_to_object_category(self, target_type: str) -> SymbolicObjectCategory:
        """将目标类型映射到对象类别"""
        target_mapping = {
            'predator': SymbolicObjectCategory.DANGEROUS_ANIMAL,
            'prey': SymbolicObjectCategory.HARMLESS_ANIMAL,
            'bird': SymbolicObjectCategory.HARMLESS_ANIMAL,
            'ground_plant': SymbolicObjectCategory.EDIBLE_PLANT,
            'underground_plant': SymbolicObjectCategory.EDIBLE_PLANT,
            'tree_plant': SymbolicObjectCategory.EDIBLE_PLANT,
            'plant': SymbolicObjectCategory.EDIBLE_PLANT,
            'Tiger': SymbolicObjectCategory.DANGEROUS_ANIMAL,
            'BlackBear': SymbolicObjectCategory.DANGEROUS_ANIMAL,
            'Rabbit': SymbolicObjectCategory.HARMLESS_ANIMAL,
            'Boar': SymbolicObjectCategory.HARMLESS_ANIMAL,
            'Pheasant': SymbolicObjectCategory.HARMLESS_ANIMAL,
            'Dove': SymbolicObjectCategory.HARMLESS_ANIMAL
        }
        return target_mapping.get(target_type, SymbolicObjectCategory.RESOURCE)

    def _map_action_name_to_symbolic(self, action_type: str) -> SymbolicAction:
        """将动作类型映射到符号化动作"""
        action_mapping = {
            'attack': SymbolicAction.ATTACK,
            'gather': SymbolicAction.GATHER,
            'collect': SymbolicAction.GATHER,
            'hunt': SymbolicAction.ATTACK,
            'harvest': SymbolicAction.GATHER
        }
        return action_mapping.get(action_type, SymbolicAction.EXPLORE)

    def _determine_target_size(self, target_type: str) -> str:
        """根据目标类型确定大小"""
        large_targets = ['predator', 'Tiger', 'BlackBear', 'Boar']
        small_targets = ['bird', 'Pheasant', 'Dove', 'Rabbit']
        
        if any(target in target_type for target in large_targets):
            return "large"
        elif any(target in target_type for target in small_targets):
            return "small"
        else:
            return "medium"
    
    def _analyze_environment_context(self, game, player) -> SymbolicEnvironment:
        """分析环境上下文"""
        # 基于周围对象数量和类型判断环境
        if not hasattr(game, 'game_map'):
            return SymbolicEnvironment.OPEN_FIELD
        
        dangerous_count = 0
        resource_count = 0
        water_count = 0
        
        # 计算视野范围内的对象
        for animal in getattr(game.game_map, 'animals', []):
            if self._is_in_vision_range(player, animal):
                animal_type = getattr(animal, 'type', '')
                if animal_type in ["Tiger", "BlackBear"]:
                    dangerous_count += 1
        
        for plant in getattr(game.game_map, 'plants', []):
            if self._is_in_vision_range(player, plant):
                resource_count += 1
        
        for water in getattr(game.game_map, 'water_sources', []):
            if self._is_in_vision_range(player, water):
                water_count += 1
        
        # 环境判断逻辑
        if dangerous_count > 1:
            return SymbolicEnvironment.DANGEROUS_ZONE
        elif water_count > 0:
            return SymbolicEnvironment.WATER_AREA
        elif resource_count > 3:
            return SymbolicEnvironment.RESOURCE_RICH
        elif resource_count == 0:
            return SymbolicEnvironment.RESOURCE_SPARSE
        else:
            return SymbolicEnvironment.OPEN_FIELD
    
    def _symbolize_self_v3(self, player, environment_element: SymbolicElement) -> EOCATR_Tuple:
        """符号化自身状态（V3版本）"""
        characteristics = SymbolicCharacteristics(
            position={"x": player.x, "y": player.y},
            distance=0.0,  # 自身距离为0
            health_state=self._determine_health_state(player.health),
            nutrition_value=getattr(player, 'food', 0),
            water_value=getattr(player, 'water', 0)
        )
        
        # 转换为V3元素
        object_element = self.converter.enum_to_element(
            SymbolicObjectCategory.SELF,
            SymbolType.OBJECT,
            AbstractionLevel.CONCRETE,
            ["自身", "玩家"]
        )
        
        condition_element = self.converter.characteristics_to_element(characteristics)
        
        action_element = self.converter.enum_to_element(
            self._determine_primary_action_need(player),
            SymbolType.ACTION,
            AbstractionLevel.CONCRETE,
            ["主要需求"]
        )
        
        result = SymbolicResult(
            success=True,
            reward=0.0,
            hp_change=0,
            food_change=0,
            water_change=0
        )
        result_element = self.converter.result_to_element(result)
        
        return create_tuple(
            environment=environment_element,
            object=object_element,
            character=condition_element,
            action=action_element,
            tool=None,
            result=result_element
        )
    
    def _symbolize_plants_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """符号化植物对象（V3版本）"""
        tuples = []
        
        if not hasattr(game, 'game_map') or not hasattr(game.game_map, 'plants'):
            return tuples
        
        for plant in game.game_map.plants:
            if not self._is_in_vision_range(player, plant):
                continue
                
            distance = self._calculate_distance(player, plant)
            
            # 确定对象类别
            if hasattr(plant, 'poisonous') and plant.poisonous:
                object_category = SymbolicObjectCategory.POISONOUS_PLANT
                semantic_tags = ["plant", "poisonous", plant.__class__.__name__]
            else:
                object_category = SymbolicObjectCategory.EDIBLE_PLANT
                semantic_tags = ["plant", "edible", plant.__class__.__name__]
            
            characteristics = SymbolicCharacteristics(
                position={"x": plant.x, "y": plant.y},
                distance=distance,
                edible=not (hasattr(plant, 'poisonous') and plant.poisonous),
                poisonous=hasattr(plant, 'poisonous') and plant.poisonous,
                size=self._determine_size_category(getattr(plant, 'size', 1.0)),
                nutrition_value=getattr(plant, 'nutrition', 10),
                accessibility=self._determine_accessibility(distance)
            )
            
            # 转换为V3元素
            object_element = self.converter.enum_to_element(
                object_category, SymbolType.OBJECT, AbstractionLevel.CONCRETE, semantic_tags
            )
            condition_element = self.converter.characteristics_to_element(characteristics)
            action_element = self.converter.enum_to_element(
                SymbolicAction.GATHER, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["采集"]
            )
            
            result = SymbolicResult(success=True, reward=characteristics.nutrition_value)
            result_element = self.converter.result_to_element(result)
            
            tuple_obj = create_tuple(
                environment=environment_element,
                object=object_element,
                character=condition_element,
                action=action_element,
                tool=None,
                result=result_element
            )
            
            tuples.append(tuple_obj)
        
        return tuples
    
    def _symbolize_animals_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """符号化动物对象（V3版本）"""
        tuples = []
        
        if not hasattr(game, 'game_map') or not hasattr(game.game_map, 'animals'):
            return tuples
        
        for animal in game.game_map.animals:
            if not self._is_in_vision_range(player, animal):
                continue
                
            distance = self._calculate_distance(player, animal)
            
            # 确定对象类别和特征
            if hasattr(animal, 'dangerous') and animal.dangerous:
                object_category = SymbolicObjectCategory.DANGEROUS_ANIMAL
                semantic_tags = ["animal", "dangerous", animal.__class__.__name__]
                dangerous = True
            else:
                object_category = SymbolicObjectCategory.HARMLESS_ANIMAL  
                semantic_tags = ["animal", "harmless", animal.__class__.__name__]
                dangerous = False
            
            characteristics = SymbolicCharacteristics(
                position={"x": animal.x, "y": animal.y},
                distance=distance,
                dangerous=dangerous,
                size=self._determine_size_category(getattr(animal, 'size', 1.0)),
                activity_state="active",
                accessibility=self._determine_accessibility(distance)
            )
            
            # 转换为V3元素
            object_element = self.converter.enum_to_element(
                object_category, SymbolType.OBJECT, AbstractionLevel.CONCRETE, semantic_tags
            )
            condition_element = self.converter.characteristics_to_element(characteristics)
            
            # 根据危险性确定动作
            if dangerous:
                action_element = self.converter.enum_to_element(
                    SymbolicAction.AVOID, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["躲避"]
                )
                result = SymbolicResult(success=True, reward=-10.0)
            else:
                action_element = self.converter.enum_to_element(
                    SymbolicAction.INTERACT, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["互动"]
                )
                result = SymbolicResult(success=True, reward=5.0)
            
            result_element = self.converter.result_to_element(result)
            
            tuple_obj = create_tuple(
                environment=environment_element,
                object=object_element,
                character=condition_element,
                action=action_element,
                tool=None,
                result=result_element
            )
            
            tuples.append(tuple_obj)
        
        return tuples
    
    def _symbolize_water_sources_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """符号化水源对象（V3版本）"""
        tuples = []
        
        # 简单的水源检测逻辑
        if hasattr(game, 'game_map') and hasattr(game.game_map, 'grid'):
            # 在视野范围内搜索水源
            for dx in range(-self.vision_range, self.vision_range + 1):
                for dy in range(-self.vision_range, self.vision_range + 1):
                    x, y = player.x + dx, player.y + dy
                    if (game.game_map.is_within_bounds(x, y) and 
                        game.game_map.grid[y][x] in ['water', 'river', 'lake']):
                        
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        characteristics = SymbolicCharacteristics(
                            position={"x": x, "y": y},
                            distance=distance,
                            water_value=20,
                            accessibility=self._determine_accessibility(distance)
                        )
                        
                        # 转换为V3元素
                        object_element = self.converter.enum_to_element(
                            SymbolicObjectCategory.WATER_SOURCE, 
                            SymbolType.OBJECT, 
                            AbstractionLevel.CONCRETE, 
                            ["水源", "资源"]
                        )
                        condition_element = self.converter.characteristics_to_element(characteristics)
                        action_element = self.converter.enum_to_element(
                            SymbolicAction.DRINK, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["饮水"]
                        )
                        
                        result = SymbolicResult(success=True, reward=15.0, water_change=20)
                        result_element = self.converter.result_to_element(result)
                        
                        tuple_obj = create_tuple(
                            environment=environment_element,
                            object=object_element,
                            character=condition_element,
                            action=action_element,
                            tool=None,
                            result=result_element
                        )
                        
                        tuples.append(tuple_obj)
        
        return tuples
    
    def _symbolize_other_players_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """符号化其他玩家（V3版本）"""
        tuples = []
        
        if not hasattr(game, 'players'):
            return tuples
        
        for other_player in game.players:
            if other_player == player or not other_player.is_alive():
                continue
                
            distance = self._calculate_distance(player, other_player)
            if distance > self.vision_range:
                continue
            
            # 确定对象类别
            if other_player.__class__.__name__ == player.__class__.__name__:
                object_category = SymbolicObjectCategory.FELLOW_PLAYER
                semantic_tags = ["玩家", "同类", other_player.__class__.__name__]
            else:
                object_category = SymbolicObjectCategory.OTHER_PLAYER
                semantic_tags = ["玩家", "其他", other_player.__class__.__name__]
            
            characteristics = SymbolicCharacteristics(
                position={"x": other_player.x, "y": other_player.y},
                distance=distance,
                player_type=other_player.__class__.__name__,
                trustworthiness=0.5,
                cooperation_level="neutral",
                health_state=self._determine_health_state(other_player.health)
            )
            
            # 转换为V3元素
            object_element = self.converter.enum_to_element(
                object_category, SymbolType.OBJECT, AbstractionLevel.CONCRETE, semantic_tags
            )
            condition_element = self.converter.characteristics_to_element(characteristics)
            action_element = self.converter.enum_to_element(
                SymbolicAction.COMMUNICATE, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["交流"]
            )
            
            result = SymbolicResult(success=True, reward=2.0)
            result_element = self.converter.result_to_element(result)
            
            tuple_obj = create_tuple(
                environment=environment_element,
                object=object_element,
                character=condition_element,
                action=action_element,
                tool=None,
                result=result_element
            )
            
            tuples.append(tuple_obj)
        
        return tuples
    
    def _symbolize_terrain_v3(self, game, player, environment_element: SymbolicElement) -> List[EOCATR_Tuple]:
        """符号化地形特征（V3版本）"""
        tuples = []
        
        current_terrain = self._get_current_terrain(game, player)
        
        characteristics = SymbolicCharacteristics(
            position={"x": player.x, "y": player.y},
            distance=0.0,
            size="large",
            accessibility="accessible"
        )
        
        # 转换为V3元素
        object_element = self.converter.enum_to_element(
            SymbolicObjectCategory.TERRAIN, 
            SymbolType.OBJECT, 
            AbstractionLevel.CONCRETE, 
            ["地形", current_terrain]
        )
        condition_element = self.converter.characteristics_to_element(characteristics)
        action_element = self.converter.enum_to_element(
            SymbolicAction.EXPLORE, SymbolType.ACTION, AbstractionLevel.CONCRETE, ["探索"]
        )
        
        result = SymbolicResult(success=True, reward=1.0)
        result_element = self.converter.result_to_element(result)
        
        tuple_obj = create_tuple(
            environment=environment_element,
            object=object_element,
            character=condition_element,
            action=action_element,
            tool=None,
            result=result_element
        )
        
        tuples.append(tuple_obj)
        
        return tuples
    
    # 工具方法
    def _is_in_vision_range(self, player, target) -> bool:
        """检查目标是否在视野范围内"""
        distance = self._calculate_distance(player, target)
        return distance <= self.vision_range
    
    def _calculate_distance(self, player, target) -> float:
        """计算距离"""
        return math.sqrt((player.x - target.x)**2 + (player.y - target.y)**2)
    
    def _determine_health_state(self, hp: int) -> str:
        """根据HP判断健康状态"""
        if hp >= 80:
            return "normal"
        elif hp >= 40:
            return "damaged"
        else:
            return "critical"
    
    def _determine_primary_action_need(self, player) -> SymbolicAction:
        """根据玩家状态确定主要行动需求"""
        if player.hp < 20:
            return SymbolicAction.EAT
        elif player.water < 10:
            return SymbolicAction.DRINK
        elif player.food < 20:
            return SymbolicAction.GATHER
        else:
            return SymbolicAction.EXPLORE
    
    def _determine_size_category(self, size_value: float) -> str:
        """将数值大小转换为分类"""
        if size_value < 0.5:
            return "small"
        elif size_value < 1.5:
            return "medium"
        else:
            return "large"
    
    def _determine_accessibility(self, distance: float) -> str:
        """根据距离判断可接近性"""
        if distance <= 1:
            return "accessible"
        elif distance <= 3:
            return "reachable"
        else:
            return "distant"
    
    def _get_current_terrain(self, game, player) -> str:
        """获取当前位置的地形类型"""
        # 简化实现，实际应根据游戏地图确定
        return "open_field"


def create_experience_from_eocatr(eocatr: EOCATR_Tuple) -> Dict[str, Any]:
    """将E-O-C-A-T-R元组转换为传统经验格式"""
    experience_key = eocatr.to_experience_key()
    experience_result = {
        'success': eocatr.result.success,
        'reward': eocatr.result.reward,
        'hp_change': eocatr.result.hp_change,
        'food_change': eocatr.result.food_change,
        'water_change': eocatr.result.water_change,
        'new_area': bool(eocatr.result.new_objects_discovered),
        'experience_gained': eocatr.result.experience_gained
    }
    
    return {
        'key': experience_key,
        'result': experience_result,
        'confidence': eocatr.confidence,
        'importance': eocatr.importance,
        'source': eocatr.source,
        'full_eocatr': eocatr.to_dict()
    } 