



# Performance optimization: Knowledge sharing frequency control
KNOWLEDGE_SHARE_INTERVAL = 5  # Share knowledge every 5 rounds
MAX_SHARES_PER_ROUND = 2      # Maximum 2 shares per round

def should_share_knowledge(player, round_num):
    """Check if knowledge should be shared"""
    # Check sharing interval
    if round_num % KNOWLEDGE_SHARE_INTERVAL != 0:
        return False
    
    # Check sharing count
    if not hasattr(player, 'shares_this_round'):
        player.shares_this_round = 0
    
    if player.shares_this_round >= MAX_SHARES_PER_ROUND:
        return False
    
    return True

def record_knowledge_share(player):
    """Record knowledge sharing"""
    if not hasattr(player, 'shares_this_round'):
        player.shares_this_round = 0
    player.shares_this_round += 1

def reset_round_shares(players):
    """Reset round sharing count"""
    for player in players:
        player.shares_this_round = 0

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Survival Competition System - Main Program
Supports survival competition simulation with multiple AI algorithms including DQN, PPO, and ILAI
"""

import os
import time
import tkinter as tk
# EMRS repair patch import
try:
    from emrs_format_fix import EMRSFormatFixer
except ImportError:
    print("Warning: EMRS repair module not found")
from tkinter import ttk
import random
import numpy as np
from collections import deque
import json
import heapq
import math
import datetime
import logging
from typing import Any, Dict, List, Optional, Union, Tuple

# TensorFlow import
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Import dynamic multi-head attention mechanism
from dynamic_multi_head_attention import DynamicMultiHeadAttention, AttentionContext, AttentionFocus

# Import multi-layer memory system
from multi_layer_memory_system import MultiLayerMemorySystem, MemoryType, MemoryImportance, MemoryItem

# Add new module import at the top of the file
from wooden_bridge_model import WoodenBridgeModel, GoalType, ReasoningStrategy, Rule, Goal

# Import blooming and pruning model
from blooming_and_pruning_model import BloomingAndPruningModel, CandidateRule, RuleType

# Import new BPM integration system
from bpm_integration import BPMIntegrationManager
from eocar_combination_generator import EOCARCombinationGenerator, CombinationType
from rule_validation_system import RuleValidationSystem, ValidationStrategy

# Import SSM scene symbolization mechanism
from scene_symbolization_mechanism import (
    SceneSymbolizationMechanism, 
    create_experience_from_eocatr,
    SymbolicEnvironment,
    SymbolicObjectCategory,
    SymbolicAction
)

# Import V3 symbol system
from symbolic_core_v3 import (
    EOCATR_Tuple as EOCAR_Tuple
)

# Import data format unification module
from data_format_unifier import (
    DataFormatUnifier,
    UnifiedAction,
    UnifiedState,
    UnifiedExperience,
    UnifiedResult,
    ActionType,
    StateType,
    ExperienceType,
    DataFormatValidator,
    create_data_format_unifier,
    quick_convert_action,
    quick_convert_state,
    quick_convert_experience
)

# Import EMRS parameter repair module
from emrs_parameter_fix import (
    EMRSParameterFixer,
    EMRSParameterValidator,
    EMRSParameterMapper,
    EMRSCompatibilityWrapper,
    create_emrs_parameter_fixer,
    quick_fix_emrs_call,
    wrap_emrs_for_compatibility
)

# Import new BPM second module: rule validation system
from rule_validation_system import (
    RuleValidationSystem,
    ValidationStrategy,
    RiskLevel,
    ValidationAttempt,
    ConfidenceUpdater
)

# 导入统一知识决策系统
try:
    from unified_knowledge_decision_system import (
        UnifiedKnowledgeDecisionSystem,
        Experience,
        Scenario,
        GoalType as UnifiedGoalType,  # 重命名以避免冲突
        RuleStatus
    )
    UNIFIED_KNOWLEDGE_AVAILABLE = True
except ImportError:
    print("Warning: Unified knowledge decision system module not found")
    UNIFIED_KNOWLEDGE_AVAILABLE = False

# 导入整合决策系统
try:
    from integrated_decision_system import IntegratedDecisionSystem, DecisionContext
    from simplified_bmp_generator import SimplifiedBMPGenerator
    from unified_decision_system import UnifiedDecisionSystem
    INTEGRATED_DECISION_AVAILABLE = True
except ImportError:
    print("Warning: Integrated decision system module not found")
    INTEGRATED_DECISION_AVAILABLE = False

# 创建模型保存目录
MODELS_DIR = "saved_models"
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# 设置日志记录
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(handler)

# 设置TensorFlow日志级别
tf.get_logger().setLevel('ERROR')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Global settings, all initial parameters controlled by the main panel
settings = {
    "map_width": 100,
    "map_height": 100,
    "map_type": "grassland",  # Options: grassland, desert, forest, mountain
    "seed": 42,
    "resource_abundance": 100,  # Percentage, 1%-1000%
    "resource_regen": 20,       # Days 1 to 100 days
    "game_duration": 30,        # Game duration (rounds, each round is a day) 1 to 10000 days [Changed: 300->30 days]
    "group_hunt_frequency": 30, # Group hunt frequency every X days
    "reasoning_attention": 20,  # Reasoning attention allocation percentage for baby learning AI
    "honesty_true": 33,         # True message sharing percentage
    "honesty_false": 33,        # False message sharing percentage
    "honesty_none": 34,         # No message sharing percentage
    "enable_hierarchical_cognition": True,
    "enable_developmental_cognition": True,
    "enable_dynamic_multihead_attention": True,
    "enable_social_decision": True,
    "enable_diverse_rewards": True,
    "enable_lstm": True,
    "enable_curiosity": True,
    "enable_deep_logical_alignment": True,
    "enable_reinforcement_learning": True,
    "animal_abundance_predator": 50,   # Predator abundance [Changed: 100->50]
    "animal_abundance_prey": 100,      # Prey abundance
    "plant_abundance_edible": 100,     # Edible plant abundance
    "plant_abundance_toxic": 100,      # Toxic plant abundance
}


#
# Logging tool (automatically generates log files after game exit)
#
class Logger:
    def __init__(self):
        self.logs = []
        self.seed_logged = False
        self.predator_count_logged = False

    def log(self, message):
        self.logs.append(message)

    def log_seed(self, seed):
        if not self.seed_logged:
            self.logs.insert(0, f"Map seed: {seed}")
            self.seed_logged = True

    def log_predator_count(self, count):
        if not self.predator_count_logged:
            # Insert predator count after seed
            insert_pos = 1 if self.seed_logged else 0
            self.logs.insert(insert_pos, f"Initial predator count: {count}")
            self.predator_count_logged = True

    def write_log_file(self):
        if self.logs:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.log"
            with open(filename, "w", encoding="utf-8") as f:
                for log in self.logs:
                    f.write(f"{log}\n")
            self.logs = []


logger = Logger()


#
# Map generation class: generates "grid" map and randomly places animals and plants on the map
#
class GameMap:
    def __init__(self, width, height, map_type, seed):
        self.width = width
        self.height = height
        self.map_type = map_type
        random.seed(seed)
        # Generate map grid, each cell stores terrain string
        self.grid = [
            [self.generate_cell() for _ in range(width)] for _ in range(height)
        ]
        self.animals = []  # Animal list
        self.plants = []   # Plant list
        self.populate_animals()
        self.populate_plants()

    def generate_cell(self):
        r = random.random()
        if r < 0.5:
            return "plain"
        elif r < 0.55:
            return "big_tree"
        elif r < 0.75:
            return "bush"
        elif r < 0.9:
            return "rock"
        elif r < 0.95:
            return "cave"
        elif r < 0.98:
            return "river"
        else:
            return "puddle"

    def populate_animals(self):
        # Distribute animals in arbitrary proportions based on animal abundance settings (numbers are simply scaled)
        total_cells = self.width * self.height
        num_predators = total_cells * settings["animal_abundance_predator"] // 10000
        for _ in range(num_predators // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Tiger(x, y))
        for _ in range(num_predators - num_predators // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(BlackBear(x, y))
        num_prey = total_cells * settings["animal_abundance_prey"] // 10000
        for _ in range(num_prey // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Rabbit(x, y))
        for _ in range(num_prey - num_prey // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Boar(x, y))

    def populate_plants(self):
        # Place edible and toxic plants based on plant abundance settings
        total_cells = self.width * self.height
        num_edible = total_cells * settings["plant_abundance_edible"] // 10000
        for _ in range(num_edible // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(Strawberry(x, y))
        for _ in range(num_edible - num_edible // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(Mushroom(x, y))
        num_toxic = total_cells * settings["plant_abundance_toxic"] // 10000
        for _ in range(num_toxic // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(ToxicStrawberry(x, y))
        for _ in range(num_toxic - num_toxic // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(ToxicMushroom(x, y))

    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_predator_count(self):
        """Get the number of predators on the map"""
        return sum(1 for animal in self.animals if hasattr(animal, 'is_predator') and animal.is_predator)

    @property
    def predators(self):
        """Get all predator animals on the map"""
        return [animal for animal in self.animals if hasattr(animal, 'is_predator') and animal.is_predator]


#
# Animal class (partial animal implementation, more animals can be added later as needed)
#
class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.chase_steps = 0  # Chase steps counter
        self.chase_target = None  # Chase target
        self.vision_range = 5  # Default vision range
    
    @property
    def position(self):
        """Return animal's position coordinates"""
        return (self.x, self.y)

    def move(self, game_map, players=None):
        if not self.alive:
            return
            
        if hasattr(self, 'is_predator') and self.is_predator and players:
            # Find nearest player within vision range
            nearest_player = None
            min_dist = float('inf')
            for player in players:
                if player.is_alive():
                    dist = abs(self.x - player.x) + abs(self.y - player.y)
                    if dist <= self.vision_range and dist < min_dist:
                        nearest_player = player
                        min_dist = dist
            
            # If a new target player is found (different from current chase target), reset chase counter
            if nearest_player and (not self.chase_target or nearest_player.name != self.chase_target.name):
                self.chase_target = nearest_player
                self.chase_steps = 0
                logger.log(f"{self.type} spots new target: {nearest_player.name}")
            
            # If there's a chase target and steps limit not exceeded, perform chase
            if self.chase_target and self.chase_steps < 10:
                if self.chase_target.is_alive():
                    # Calculate movement direction
                    dx = 1 if self.chase_target.x > self.x else -1 if self.chase_target.x < self.x else 0
                    dy = 1 if self.chase_target.y > self.y else -1 if self.chase_target.y < self.y else 0
                    
                    # Check if movement is valid
                    new_x = self.x + dx
                    new_y = self.y + dy
                    if game_map.is_within_bounds(new_x, new_y):
                        self.x = new_x
                        self.y = new_y
                        self.chase_steps += 1
                        
                        # If adjacent to player, attack
                        if abs(self.x - self.chase_target.x) <= 1 and abs(self.y - self.chase_target.y) <= 1:
                            self.attack_player(self.chase_target)
                    
                    # If chase steps reach limit, log it
                    if self.chase_steps >= 10:
                        logger.log(f"{self.type} gives up chasing {self.chase_target.name}")
                    return
                else:
                    # If target is dead, reset chase state
                    self.chase_target = None
                    self.chase_steps = 0
            
            # If there's a new chaseable target but current chase has ended, reset chase state
            elif nearest_player:
                self.chase_target = nearest_player
                self.chase_steps = 0
                logger.log(f"{self.type} starts chasing {nearest_player.name}")
                return
        
        # 默认随机移动行为
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_within_bounds(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def attack_player(self, player):
        # 🔧 修复：被动攻击时记录遭遇
        if hasattr(player, 'encountered_animals_count'):
            encounter_key = f"{self.type}_{self.x}_{self.y}_{player.x}_{player.y}"
            if not hasattr(player, '_recorded_encounters'):
                player._recorded_encounters = set()
            
            if encounter_key not in player._recorded_encounters:
                player.encountered_animals_count += 1
                player._recorded_encounters.add(encounter_key)
                logger.log(f"{player.name} encountered {self.type} (passive attack)")
        
        if hasattr(self, 'attack'):
            damage = self.attack
            player.hp = max(0, player.hp - damage)
            logger.log(f"{self.type} attacks {player.name} for {damage} damage")
            if player.hp <= 0:
                player.alive = False
                logger.log(f"{player.name} was killed by {self.type}")


class Tiger(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Tiger"
        self.hp = 500
        self.attack = 50
        self.food = 500
        self.is_predator = True  # 标记为捕食者
        self.vision_range = 8  # 老虎视野范围更大
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "short",
            "sound": "roar",
        }


class BlackBear(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "BlackBear"
        self.hp = 300
        self.attack = 30
        self.food = 300
        self.is_predator = True  # 标记为捕食者
        self.vision_range = 6  # 黑熊视野范围
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "long",
            "sound": "roar",
        }


class Rabbit(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Rabbit"
        self.hp = 10
        self.attack = 0
        self.food = 10
        self.visible_info = {
            "body_type": "large",
            "teeth": "flat",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "short",
            "sound": "roar",
        }


class Boar(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Boar"
        self.hp = 50
        self.attack = 0
        self.food = 50
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "blunt",
            "speed": 2,
            "color": "yellow",
            "fur": "long",
            "sound": "roar",
        }


#
# 植物类
#
class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.alive = True  # 添加alive属性
    
    @property
    def position(self):
        """返回植物的位置坐标"""
        return (self.x, self.y)
        
    def update(self):
        pass  # 植物暂时不需要更新逻辑


class Strawberry(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.food = 5
        self.toxic = False


class Mushroom(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.food = 3
        self.toxic = False


class ToxicStrawberry(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.food = 5
        self.toxic = True


class ToxicMushroom(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.food = 3
        self.toxic = True


#
# 日志记录工具(游戏退出后自动生成日志文件)
#
class Logger:
    def __init__(self):
        self.logs = []
        self.seed_logged = False
        self.predator_count_logged = False

    def log(self, message):
        self.logs.append(message)

    def log_seed(self, seed):
        if not self.seed_logged:
            self.logs.insert(0, f"Map seed: {seed}")
            self.seed_logged = True

    def log_predator_count(self, count):
        if not self.predator_count_logged:
            # 在种子之后插入猛兽数量
            insert_pos = 1 if self.seed_logged else 0
            self.logs.insert(insert_pos, f"Initial predator count: {count}")
            self.predator_count_logged = True

    def write_log_file(self):
        if self.logs:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.log"
            with open(filename, "w", encoding="utf-8") as f:
                for log in self.logs:
                    f.write(f"{log}\n")
            self.logs = []


logger = Logger()


#
# 地图生成类:生成"网格"地图,并在地图上随机放置动物和植"
#
class GameMap:
    def __init__(self, width, height, map_type, seed):
        self.width = width
        self.height = height
        self.map_type = map_type
        random.seed(seed)
        # 生成地图网格,每个格子保存地形字符串
        self.grid = [
            [self.generate_cell() for _ in range(width)] for _ in range(height)
        ]
        self.animals = []  # 动物列表
        self.plants = []   # 植物列表
        self.populate_animals()
        self.populate_plants()

    def generate_cell(self):
        r = random.random()
        if r < 0.5:
            return "plain"
        elif r < 0.55:
            return "big_tree"
        elif r < 0.75:
            return "bush"
        elif r < 0.9:
            return "rock"
        elif r < 0.95:
            return "cave"
        elif r < 0.98:
            return "river"
        else:
            return "puddle"

    def populate_animals(self):
        # 根据设置中动物丰度按任意比例分布(数量经过简单缩放)
        total_cells = self.width * self.height
        num_predators = total_cells * settings["animal_abundance_predator"] // 10000
        for _ in range(num_predators // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Tiger(x, y))
        for _ in range(num_predators - num_predators // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(BlackBear(x, y))
        num_prey = total_cells * settings["animal_abundance_prey"] // 10000
        for _ in range(num_prey // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Rabbit(x, y))
        for _ in range(num_prey - num_prey // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.animals.append(Boar(x, y))

    def populate_plants(self):
        # 根据设置中植物丰度放置无毒和有毒植物
        total_cells = self.width * self.height
        num_edible = total_cells * settings["plant_abundance_edible"] // 10000
        for _ in range(num_edible // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(Strawberry(x, y))
        for _ in range(num_edible - num_edible // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(Mushroom(x, y))
        num_toxic = total_cells * settings["plant_abundance_toxic"] // 10000
        for _ in range(num_toxic // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(ToxicStrawberry(x, y))
        for _ in range(num_toxic - num_toxic // 2):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.plants.append(ToxicMushroom(x, y))

    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_predator_count(self):
        """获取地图上的猛兽数量"""
        return sum(1 for animal in self.animals if hasattr(animal, 'is_predator') and animal.is_predator)

    @property
    def predators(self):
        """获取地图上的所有捕食者动物"""
        return [animal for animal in self.animals if hasattr(animal, 'is_predator') and animal.is_predator]


#
# 动物类(部分动物实现,后期动物可按需加入"""
#
class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.chase_steps = 0  # 追击步数计数
        self.chase_target = None  # 追击目标
        self.vision_range = 5  # 默认视野范围
    
    @property
    def position(self):
        """返回动物的位置坐标"""
        return (self.x, self.y)

    def move(self, game_map, players=None):
        if not self.alive:
            return
            
        if hasattr(self, 'is_predator') and self.is_predator and players:
            # 寻找视野范围内最近的玩家
            nearest_player = None
            min_dist = float('inf')
            for player in players:
                if player.is_alive():
                    dist = abs(self.x - player.x) + abs(self.y - player.y)
                    if dist <= self.vision_range and dist < min_dist:
                        nearest_player = player
                        min_dist = dist
            
            # 如果发现新的目标玩家(与当前追击目标不同),重置追击计数
            if nearest_player and (not self.chase_target or nearest_player.name != self.chase_target.name):
                self.chase_target = nearest_player
                self.chase_steps = 0
                logger.log(f"{self.type} spots new target: {nearest_player.name}")
            
            # 如果有追击目标且未超过步数限制,进行追击
            if self.chase_target and self.chase_steps < 10:
                if self.chase_target.is_alive():
                    # 计算移动方向
                    dx = 1 if self.chase_target.x > self.x else -1 if self.chase_target.x < self.x else 0
                    dy = 1 if self.chase_target.y > self.y else -1 if self.chase_target.y < self.y else 0
                    
                    # 检查移动是否有效
                    new_x = self.x + dx
                    new_y = self.y + dy
                    if game_map.is_within_bounds(new_x, new_y):
                        self.x = new_x
                        self.y = new_y
                        self.chase_steps += 1
                        
                        # 如果与玩家相邻,进行攻击
                        if abs(self.x - self.chase_target.x) <= 1 and abs(self.y - self.chase_target.y) <= 1:
                            self.attack_player(self.chase_target)
                    
                    # 如果追击步数达到上限,记录日志
                    if self.chase_steps >= 10:
                        logger.log(f"{self.type} gives up chasing {self.chase_target.name}")
                    return
                else:
                    # 如果目标已死亡,重置追击状态
                    self.chase_target = None
                    self.chase_steps = 0
            
            # 如果有新的可追击目标但当前追击已结束,重置追击状态
            elif nearest_player:
                self.chase_target = nearest_player
                self.chase_steps = 0
                logger.log(f"{self.type} starts chasing {nearest_player.name}")
                return
        
        # 默认随机移动行为
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_within_bounds(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def attack_player(self, player):
        # 🔧 修复：被动攻击时记录遭遇
        if hasattr(player, 'encountered_animals_count'):
            encounter_key = f"{self.type}_{self.x}_{self.y}_{player.x}_{player.y}"
            if not hasattr(player, '_recorded_encounters'):
                player._recorded_encounters = set()
            
            if encounter_key not in player._recorded_encounters:
                player.encountered_animals_count += 1
                player._recorded_encounters.add(encounter_key)
                logger.log(f"{player.name} encountered {self.type} (passive attack)")
        
        if hasattr(self, 'attack'):
            damage = self.attack
            player.hp = max(0, player.hp - damage)
            logger.log(f"{self.type} attacks {player.name} for {damage} damage")
            if player.hp <= 0:
                player.alive = False
                logger.log(f"{player.name} was killed by {self.type}")


class Tiger(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Tiger"
        self.hp = 500
        self.attack = 50
        self.food = 500
        self.is_predator = True  # 标记为捕食者
        self.vision_range = 8  # 老虎视野范围更大
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "short",
            "sound": "roar",
        }


class BlackBear(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "BlackBear"
        self.hp = 300
        self.attack = 30
        self.food = 300
        self.is_predator = True  # 标记为捕食者
        self.vision_range = 6  # 黑熊视野范围
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "long",
            "sound": "roar",
        }


class Rabbit(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Rabbit"
        self.hp = 10
        self.attack = 0
        self.food = 10
        self.visible_info = {
            "body_type": "large",
            "teeth": "flat",
            "claws": "sharp",
            "speed": 2,
            "color": "yellow",
            "fur": "short",
            "sound": "roar",
        }


class Boar(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "Boar"
        self.hp = 50
        self.attack = 0
        self.food = 50
        self.visible_info = {
            "body_type": "large",
            "teeth": "sharp",
            "claws": "blunt",
            "speed": 2,
            "color": "yellow",
            "fur": "long",
            "sound": "roar",
        }


#
# 植物类
#
class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.alive = True  # 添加alive属性
    
    @property
    def position(self):
        """返回植物的位置坐标"""
        return (self.x, self.y)
        
    def update(self):
        pass  # 植物暂时不需要更新逻辑


class Strawberry(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible_info = {"color": "red", "shape": "round", "hardness": "soft", "smell": "sweet"}
        self.food = 5
        self.toxic = False


class Mushroom(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible_info = {"color": "brown", "shape": "umbrella", "hardness": "soft", "smell": "sweet"}
        self.food = 5
        self.toxic = False


class ToxicStrawberry(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible_info = {"color": "red", "shape": "round", "hardness": "soft", "smell": "sweet"}
        self.food = 5
        self.toxic = True


class ToxicMushroom(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.visible_info = {"color": "red", "shape": "umbrella", "hardness": "soft", "smell": "sweet"}
        self.food = 5
        self.toxic = True


#
# 玩家基类,包含血量、食物、水量、移动、互动、采集与攻击行为"
# 玩家死亡条件:血量≤0或食物、水"
#
class Player:
    def __init__(self, name, player_type, game_map):
        self.name = name
        self.player_type = player_type
        self.hp = 100
        self.food = 100  # 初始食物个00
        self.water = 100  # 初始水分个00
        self.speed = 1
        self.attention = 50
        self.reputation = 100
        # 随机放置至地图内
        self.x = random.randint(0, game_map.width - 1)
        self.y = random.randint(0, game_map.height - 1)
        self.alive = True

        # 成就统计数据
        self.survival_days = 0
        self.collected_plants = 0
        self.killed_animals = 0
        self.damage_dealt = 0
        
        # 🔧 修复：添加真实统计记录变量
        self.explored_cells = set()  # 已探索的格子坐标集合
        self.explored_cells.add((self.x, self.y))  # 初始位置
        self.found_plants_count = 0  # 发现植物数量
        self.encountered_animals_count = 0  # 遭遇动物数量  
        self.found_big_tree_count = 0  # 发现大树次数
        self.explored_cave_count = 0  # 探索洞穴次数
        self.shared_info_count = 0  # 分享信息次数
        self.novelty_discoveries_count = 0  # 新颖发现总数（新经验+新规律）
        self.new_experiences_count = 0  # 新经验数量
        self.new_rules_count = 0  # 新规律数量
        self.kills = 0  # 击杀数量
        self.plants_collected = 0  # 采集植物数量
        self.toxic_plants_collected = 0  # 采集有毒植物数量
        
        # 保存game_map引用用于计算探索率
        self._game_map = game_map

    @property
    def health(self):
        """health属性动态指向hp,解决属性访问问题"""
        return self.hp
    
    @health.setter
    def health(self, value):
        """设置health时同步更新hp"""
        self.hp = value

    def is_alive(self):
        return self.alive

    def move(self, dx, dy, game_map):
        old_x, old_y = self.x, self.y
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map and game_map.is_within_bounds(new_x, new_y):
            self.x, self.y = new_x, new_y
            logger.log(f"{self.name} 行动详情: 移动 | 位置:{old_x},{old_y}->{self.x},{self.y} | 状态HP{self.health}/F{self.food}/W{self.water}")
            
            # 🔧 修复：记录探索的新格子
            if hasattr(self, 'explored_cells'):
                self.explored_cells.add((self.x, self.y))
            
            # 为ILAI和RILAI玩家更新位置跟踪
            if (hasattr(self, 'player_type') and 
                self.player_type in ["ILAI", "RILAI"] and 
                hasattr(self, 'current_pos')):
                self.last_pos = (old_x, old_y)
                self.current_pos = (self.x, self.y)
                if hasattr(self, 'visited_positions'):
                    self.visited_positions.add(self.current_pos)
            
            return True
        return False

    def take_turn(self, game):
        """每回合基础行为"""
        if not self.alive:
            return
            
        # 每回合消耗
        self.food = max(0, self.food - 1)
        self.water = max(0, self.water - 1)
        
        # 检查当前格子是否有水源,自动喝水
        current_cell = game.game_map.grid[self.y][self.x]
        
        # 🔧 修复：记录特殊地形探索
        self._record_exploration(current_cell)
        if current_cell in ["river", "puddle"]:
            old_water = self.water
            self.water = min(100, self.water + 30)
            if self.water > old_water:
                logger.log(f"{self.name} drinks water at {current_cell}")
        
        # 自动采集功能已移除 - 现在需要主动决策采集
        
        # 如果食物或水分为0,减少生命值
        if self.food == 0 or self.water == 0:
            self.hp = max(0, self.hp - 10)
            
        # 检查是否死亡
        if self.hp <= 0:
            self.alive = False
            logger.log(f"{self.name} 死亡")

    def collect_plant(self, plant):
        """采集植物，获得食物（考虑工具效果）"""
        # 🔧 修复：首先记录发现植物
        self._record_plant_discovery(plant)
        
        if not plant.collected and not plant.toxic:
            # 确定植物类型
            if hasattr(plant, 'location_type'):
                if plant.location_type == "ground":
                    plant_type = "ground_plant"
                elif plant.location_type == "underground":
                    plant_type = "underground_plant"
                elif plant.location_type == "tree":
                    plant_type = "tree_plant"
                else:
                    plant_type = "ground_plant"  # 默认
            else:
                plant_type = "ground_plant"  # 旧植物默认为地面植物
            
            # 检查是否有合适的工具
            tool = None
            if hasattr(self, 'get_best_tool_for_target'):
                tool = self.get_best_tool_for_target(plant_type)
            
            # 根据工具情况计算成功率和收益
            if tool:
                success_rate = 0.95  # 有正确工具，95%成功率
                food_multiplier = 1.5  # 有工具获得更多食物
                logger.log(f"{self.name} uses {tool.name} to collect plant")
            else:
                # 特殊植物没有工具难以采集
                if hasattr(plant, 'location_type') and plant.location_type in ["underground", "tree"]:
                    success_rate = 0.1  # 没有工具徒手很难成功
                    food_multiplier = 0.5  # 即使成功也获得很少食物
                elif hasattr(plant, 'has_thorns') and plant.has_thorns:
                    success_rate = 0.2  # 有刺植物徒手困难
                    food_multiplier = 0.7
                else:
                    success_rate = 0.8  # 地面植物徒手较容易
                    food_multiplier = 1.0
                logger.log(f"{self.name} attempts to collect plant bare-handed")
            
            # 尝试采集
            collection_success = random.random() < success_rate
            if collection_success:
                plant.collected = True
                food_gain = int(plant.food * food_multiplier)
                self.food = min(100, self.food + food_gain)
                self.collected_plants += 1
                logger.log(f"{self.name} successfully collected plant and gained {food_gain} food")
            else:
                food_gain = 0
                logger.log(f"{self.name} failed to collect plant")
            
            # 🧠 记录工具使用结果用于学习（ILAI和RILAI）
            if hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"] and tool:
                # 🔧 强制调试输出 - 记录工具使用调用
                try:
                    with open("tool_usage_debug.txt", "a", encoding="utf-8") as f:
                        f.write(f"🔧 {self.name} 调用_record_tool_usage：工具={tool.name}，目标={plant_type}，成功={collection_success}，收益={food_gain}\n")
                except:
                    pass
                
                # 🔧 设置实时工具使用标记，让SSM能够检测到
                if hasattr(self, '_last_tool_used'):
                    self._last_tool_used = (
                        tool.type,
                        plant_type,
                        'gather',
                        collection_success,
                        food_gain
                    )
                
                # 记录工具使用经验
                if hasattr(self, '_record_tool_usage'):
                    self._record_tool_usage(tool, plant_type, collection_success, food_gain)
                
                # 🌟 为ILAI系统添加专门的植物采集经验 - 修复为决策系统可理解的格式
                if hasattr(self, 'add_eocar_experience'):
                    self.add_eocar_experience('collect_plant', {'success': collection_success, 'food_gain': food_gain}, source="direct")
                    logger.log(f"{self.name} 📚 记录植物采集经验: {plant_type} {'成功' if collection_success else '失败'}")
                
                # 🎯 关键修复：添加可执行的决策规律
                if hasattr(self, '_add_actionable_rule_from_experience'):
                    # 获取工具类型，兼容不同的属性名
                    tool_type_attr = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.name
                    
                    rule_conditions = {
                        'plant_type': plant_type,
                        'tool_available': tool_type_attr,
                        'food_level': 'low' if self.food < 50 else 'normal'
                    }
                    rule_predictions = {
                        'action': 'collect_plant',
                        'success_probability': success_rate,
                        'food_gain_expected': food_gain if collection_success else int(food_gain * success_rate),
                        'tool_recommendation': tool_type_attr
                    }
                    self._add_actionable_rule_from_experience(
                        'plant_collection_rule',
                        rule_conditions,
                        rule_predictions,
                        confidence=success_rate
                    )
                
                # 🌟 为ILAI系统添加五库经验
                if hasattr(self, 'add_experience_to_direct_library'):
                    # 获取工具类型，兼容不同的属性名
                    tool_type_attr = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.name
                    
                    context = {
                        'plant_type': plant_type,
                        'tool_used': tool_type_attr,
                        'location': (self.x, self.y),
                        'success_rate': success_rate,
                        'food_multiplier': food_multiplier
                    }
                    self.add_experience_to_direct_library('collect_plant', 
                                                        {'success': collection_success, 'food_gain': food_gain}, 
                                                        context)
                    logger.log(f"{self.name} 📖 记录五库采集经验: {plant_type}")
            
            # 🌟 即使没有工具，ILAI也要记录采集经验
            elif hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"]:
                # 记录无工具采集经验
                if hasattr(self, 'add_eocar_experience'):
                    self.add_eocar_experience('collect_plant_barehanded', {'success': collection_success, 'food_gain': food_gain}, source="direct")
                    logger.log(f"{self.name} 📚 记录徒手采集经验: {plant_type} {'成功' if collection_success else '失败'}")
                
                # 🎯 关键修复：为徒手采集也添加可执行规律
                if hasattr(self, '_add_actionable_rule_from_experience'):
                    rule_conditions = {
                        'plant_type': plant_type,
                        'tool_available': None,
                        'food_level': 'low' if self.food < 50 else 'normal'
                    }
                    rule_predictions = {
                        'action': 'collect_plant_barehanded',
                        'success_probability': success_rate,
                        'food_gain_expected': food_gain if collection_success else int(food_gain * success_rate),
                        'tool_recommendation': 'none',
                        'difficulty': 'high' if plant_type in ["underground", "tree"] else 'medium'
                    }
                    self._add_actionable_rule_from_experience(
                        'plant_collection_barehanded_rule',
                        rule_conditions,
                        rule_predictions,
                        confidence=success_rate
                    )
                
                # 记录五库经验
                if hasattr(self, 'add_experience_to_direct_library'):
                    context = {
                        'plant_type': plant_type,
                        'tool_used': None,
                        'location': (self.x, self.y),
                        'success_rate': success_rate,
                        'collection_method': 'barehanded'
                    }
                    self.add_experience_to_direct_library('collect_plant_barehanded', 
                                                        {'success': collection_success, 'food_gain': food_gain}, 
                                                        context)
                    logger.log(f"{self.name} 📖 记录五库徒手采集经验: {plant_type}")
            
            return collection_success
        else:
            return False

    def encounter_animal(self, animal, game):
        """遇到动物时的记录功能（不再自动攻击或逃跑）"""
        # 🔧 修复：记录遭遇动物
        self._record_animal_encounter(animal)
        
        self.encountered_animals += 1
        logger.log(f"{self.name} encounters {animal.type} at ({self.x},{self.y}) - decision needed")

    def flee(self, animal, game):
        dx = self.x - animal.x
        dy = self.y - animal.y
        if dx != 0:
            dx = int(dx / abs(dx))
        if dy != 0:
            dy = int(dy / abs(dy))
        self.move(dx, dy, game.game_map)
        logger.log(f"{self.name} fled from {animal.type}")

    def action_collect_plant(self, game):
        """主动采集植物行为 - 所有玩家类型都可使用"""
        plants_collected = 0
        for plant in game.game_map.plants:
            if plant.x == self.x and plant.y == self.y and plant.alive and not plant.collected:
                # 🔧 修复：为ILAI玩家添加工具选择机制
                if hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"]:
                    # 确定植物类型
                    plant_type = self._determine_plant_type(plant)
                    # 选择工具
                    selected_tool, context = self._select_and_use_tool_for_action('collect_plant', plant_type)
                    
                    old_food = self.food
                    success = self.collect_plant(plant)
                    benefit = self.food - old_food
                    
                    # 记录工具使用结果
                    if selected_tool:
                        self._record_tool_usage_result(selected_tool, plant_type, 'collect_plant', success, benefit)
                    
                    if success:
                        logger.log(f"{self.name} actively collects plant with {self._last_used_tool} at ({self.x},{self.y})")
                        plants_collected += 1
                else:
                    # 其他玩家类型的原始逻辑
                    old_food = self.food
                    self.collect_plant(plant)
                    if self.food > old_food:
                        logger.log(f"{self.name} actively collects plant at ({self.x},{self.y})")
                        plants_collected += 1
                break
        return plants_collected > 0

    def action_attack_animal(self, game):
        """主动攻击动物行为 - 所有玩家类型都可使用"""
        # 寻找当前位置或相邻位置的动物
        target_animal = None
        min_distance = float('inf')
        
        for animal in game.game_map.animals:
            if animal.alive:
                distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                if distance <= 1 and distance < min_distance:  # 当前位置或相邻1格
                    target_animal = animal
                    min_distance = distance
        
        if target_animal:
            # 🔧 修复：为ILAI玩家添加工具选择机制
            if hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"]:
                # 确定动物类型
                animal_type = self._determine_animal_type(target_animal)
                # 选择工具
                selected_tool, context = self._select_and_use_tool_for_action('attack_animal', animal_type)
                
                old_food = self.food
                damage = self.attack(target_animal)
                benefit = self.food - old_food
                success = damage > 0 or benefit > 0
                
                # 记录工具使用结果
                if selected_tool:
                    self._record_tool_usage_result(selected_tool, animal_type, 'attack_animal', success, benefit)
                
                logger.log(f"{self.name} actively attacks {target_animal.type} with {self._last_used_tool}")
            else:
                # 其他玩家类型的原始逻辑
                logger.log(f"{self.name} actively attacks {target_animal.type}")
                self.attack(target_animal)
            return True
        else:
            logger.log(f"{self.name} attempts to attack but no animal nearby")
            return False

    def attack(self, animal):
        if animal.alive:
            # 确定动物类型
            animal_class = animal.__class__.__name__
            if animal_class in ["Tiger", "BlackBear"]:
                animal_type = "predator"
            elif animal_class in ["Rabbit", "Boar"]:
                animal_type = "prey"
            elif animal_class in ["Pheasant", "Dove"]:
                animal_type = "bird"
            else:
                animal_type = "prey"  # 默认
            
            # 检查是否有合适的工具
            tool = None
            if hasattr(self, 'get_best_tool_for_target'):
                tool = self.get_best_tool_for_target(animal_type)
            
            # 根据工具情况计算伤害和成功率
            if tool:
                # 🔧 真实的工具效果系统：不同工具对不同目标有不同效果
                if hasattr(self, '_calculate_tool_effectiveness'):
                    base_damage, success_rate = self._calculate_tool_effectiveness(tool, animal_type)
                else:
                    base_damage = 15  # 有工具的基础伤害
                    success_rate = 0.8  # 80%命中率
                logger.log(f"{self.name} uses {tool.name} to attack {animal_class}")
            else:
                base_damage = 5   # 徒手伤害很低
                success_rate = 0.3  # 30%命中率，特别是对鸟类很难命中
                if animal_type == "bird":
                    success_rate = 0.05  # 徒手打鸟几乎不可能
                elif animal_type == "predator":
                    success_rate = 0.1   # 徒手打猛兽极度危险
                logger.log(f"{self.name} attempts to attack {animal_class} bare-handed")
            
            # 尝试攻击
            attack_success = random.random() < success_rate
            if attack_success:
                actual_damage = base_damage
                animal.hp -= actual_damage
                self.damage_dealt += actual_damage
                logger.log(f"{self.name} successfully attacked {animal_class} for {actual_damage} damage")
                
                if animal.hp <= 0:
                    animal.alive = False
                    self.killed_animals += 1
                    self.food = min(100, self.food + animal.food)
                    logger.log(f"{self.name} killed {animal_class} and gained {animal.food} food")
            else:
                actual_damage = 0
                logger.log(f"{self.name} missed the attack on {animal_class}")
                # 攻击失败时，猛兽可能反击
                if animal_type == "predator" and random.random() < 0.5:
                    self.hp -= 15
                    logger.log(f"{animal_class} counter-attacks {self.name} for 15 damage")
            
            # 🧠 记录工具使用结果用于学习（ILAI和RILAI）
            if hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"] and tool:
                # 🔧 强制调试输出 - 记录工具使用调用
                try:
                    with open("tool_usage_debug.txt", "a", encoding="utf-8") as f:
                        f.write(f"🔧 {self.name} 调用_record_tool_usage：工具={tool.name}，目标={animal_type}，成功={attack_success}，伤害={actual_damage}\n")
                except:
                    pass
                
                # 🔧 设置实时工具使用标记，让SSM能够检测到
                if hasattr(self, '_last_tool_used'):
                    self._last_tool_used = (
                        tool.type,
                        animal_type,
                        'attack',
                        attack_success,
                        actual_damage
                    )
                
                # 记录工具使用经验
                if hasattr(self, '_record_tool_usage'):
                    self._record_tool_usage(tool, animal_type, attack_success, actual_damage)
                
                # 🌟 为ILAI系统添加专门的动物攻击经验 - 修复为决策系统可理解的格式
                if hasattr(self, 'add_eocar_experience'):
                    self.add_eocar_experience('attack_animal', {'success': attack_success, 'damage': actual_damage}, source="direct")
                    logger.log(f"{self.name} 📚 Record animal attack experience: {animal_class} {'Success' if attack_success else 'Failed'}")
                
                # 🎯 关键修复：添加可执行的战斗决策规律
                if hasattr(self, '_add_actionable_rule_from_experience'):
                    # 获取工具类型，兼容不同的属性名
                    tool_type_attr = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.name
                    
                    rule_conditions = {
                        'animal_type': animal_type,
                        'tool_available': tool_type_attr,
                        'health_level': 'low' if self.health < 50 else 'normal',
                        'target_species': animal_class
                    }
                    rule_predictions = {
                        'action': 'attack_animal',
                        'success_probability': success_rate,
                        'damage_expected': actual_damage if attack_success else int(base_damage * success_rate),
                        'tool_recommendation': tool_type_attr,
                        'risk_level': 'high' if animal_type == 'predator' else 'medium'
                    }
                    self._add_actionable_rule_from_experience(
                        'animal_combat_rule',
                        rule_conditions,
                        rule_predictions,
                        confidence=success_rate
                    )
                
                # 🌟 为ILAI系统添加五库经验
                if hasattr(self, 'add_experience_to_direct_library'):
                    # 获取工具类型，兼容不同的属性名
                    tool_type_attr = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.name
                    
                    context = {
                        'animal_type': animal_type,
                        'tool_used': tool_type_attr,
                        'location': (self.x, self.y),
                        'success_rate': success_rate,
                        'base_damage': base_damage,
                        'target_name': animal_class
                    }
                    self.add_experience_to_direct_library('attack_animal', 
                                                        {'success': attack_success, 'damage': actual_damage}, 
                                                        context)
                    logger.log(f"{self.name} 📖 记录五库攻击经验: {animal_class}")
            
            # 🌟 即使没有工具，ILAI也要记录攻击经验
            elif hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"]:
                # 记录无工具攻击经验
                if hasattr(self, 'add_eocar_experience'):
                    self.add_eocar_experience('attack_animal_barehanded', {'success': attack_success, 'damage': actual_damage}, source="direct")
                    logger.log(f"{self.name} 📚 Record bare-hand attack experience: {animal_class} {'Success' if attack_success else 'Failed'}")
                
                # 🎯 关键修复：为徒手攻击也添加可执行规律
                if hasattr(self, '_add_actionable_rule_from_experience'):
                    rule_conditions = {
                        'animal_type': animal_type,
                        'tool_available': None,
                        'health_level': 'low' if self.health < 50 else 'normal',
                        'target_species': animal_class
                    }
                    rule_predictions = {
                        'action': 'attack_animal_barehanded',
                        'success_probability': success_rate,
                        'damage_expected': actual_damage if attack_success else int(base_damage * success_rate),
                        'tool_recommendation': 'none',
                        'risk_level': 'very_high' if animal_type == 'predator' else 'high'
                    }
                    self._add_actionable_rule_from_experience(
                        'animal_combat_barehanded_rule',
                        rule_conditions,
                        rule_predictions,
                        confidence=success_rate
                    )
                
                # 记录五库经验
                if hasattr(self, 'add_experience_to_direct_library'):
                    context = {
                        'animal_type': animal_type,
                        'tool_used': None,
                        'location': (self.x, self.y),
                        'success_rate': success_rate,
                        'attack_method': 'barehanded',
                        'target_name': animal_class
                    }
                    self.add_experience_to_direct_library('attack_animal_barehanded', 
                                                        {'success': attack_success, 'damage': actual_damage}, 
                                                        context)
                    logger.log(f"{self.name} 📖 记录五库徒手攻击经验: {animal_class}")
            
            return actual_damage
        else:
            return 0
    
    def get_best_tool_for_target(self, target_type):
        """获取对指定目标最有效的工具"""
        # 对于ILAI和RILAI，使用学习到的效果选择工具
        if hasattr(self, 'player_type') and self.player_type in ["ILAI", "RILAI"]:
            selected_tool = self._select_tool_by_learning(target_type)
            return selected_tool
        
        # 其他玩家使用预设映射（如果工具有target_type属性）
        for tool in getattr(self, 'tools', []):
            if hasattr(tool, 'target_type') and tool.target_type == target_type:
                return tool
        return None
    
    def _select_tool_by_learning(self, target_type):
        """基于学习经验选择工具 - 鼓励探索而非直接给出最优解"""
        import random  # 导入随机模块用于探索机制
        
        tools = getattr(self, 'tools', [])
        if not tools:
            return None
        
        # 🧠 核心学习机制：基于历史经验选择工具
        if hasattr(self, 'tool_effectiveness') and self.tool_effectiveness:
            # 计算每个工具对当前目标的学习到的效果
            tool_scores = {}
            for tool in tools:
                tool_key = getattr(tool, 'name', tool.__class__.__name__)
                experience_key = (tool_key, target_type)
                
                if experience_key in self.tool_effectiveness:
                    effectiveness = self.tool_effectiveness[experience_key]
                    # 基于成功率和尝试次数计算分数
                    success_rate = effectiveness.get('effectiveness', 0.5)
                    attempts = effectiveness.get('attempts', 0)
                    
                    # 🎲 增强探索机制 - 更强的探索奖励
                    exploration_bonus = max(0, (15 - attempts) * 0.08)  # 前15次尝试有更高探索奖励
                    # 添加随机性，避免完全确定性选择
                    randomness = (random.random() - 0.5) * 0.2  # ±0.1的随机波动
                    tool_scores[tool] = success_rate + exploration_bonus + randomness
                else:
                    # 未尝试过的工具给予更高探索价值
                    exploration_value = 0.9 + random.random() * 0.2  # 0.9-1.1之间的随机值
                    tool_scores[tool] = exploration_value  # 强烈鼓励尝试新工具
            
            # 选择分数最高的工具
            if tool_scores:
                best_tool = max(tool_scores.keys(), key=lambda t: tool_scores[t])
                return best_tool
        
        # 🎲 如果没有经验数据，使用好奇心驱动的随机选择
        if hasattr(self, 'tool_experiment_counts'):
            # 优先选择尝试次数较少的工具（好奇心机制）
            min_experiments = min(self.tool_experiment_counts.values()) if self.tool_experiment_counts else 0
            least_tried_tools = []
            
            for tool in tools:
                tool_key = getattr(tool, 'name', tool.__class__.__name__)
                experiment_count = self.tool_experiment_counts.get(tool_key, 0)
                if experiment_count <= min_experiments + 2:  # 允许一定的平衡
                    least_tried_tools.append(tool)
            
            if least_tried_tools:
                import random
                selected_tool = random.choice(least_tried_tools)
                # 更新实验计数
                tool_key = getattr(selected_tool, 'name', selected_tool.__class__.__name__)
                self.tool_experiment_counts[tool_key] = self.tool_experiment_counts.get(tool_key, 0) + 1
                return selected_tool
        
        # 🎯 最后备选：随机选择（完全探索）
        import random
        return random.choice(tools)
    
    def _calculate_tool_effectiveness(self, tool, target_type):
        """计算工具对目标的真实效果（物理模拟）"""
        tool_properties = {
            'Spear': {'reach': 3, 'penetration': 4, 'precision': 3, 'speed': 2},
            'Stone': {'reach': 2, 'penetration': 2, 'precision': 2, 'speed': 4}, 
            'Bow': {'reach': 5, 'penetration': 3, 'precision': 5, 'speed': 3},
            'Basket': {'reach': 1, 'penetration': 1, 'precision': 1, 'speed': 1},
            'Shovel': {'reach': 2, 'penetration': 4, 'precision': 2, 'speed': 2},
            'Stick': {'reach': 3, 'penetration': 2, 'precision': 2, 'speed': 3}
        }
        
        target_characteristics = {
            'predator': {'size': 4, 'speed': 3, 'armor': 3, 'aggression': 5},
            'prey': {'size': 2, 'speed': 3, 'armor': 1, 'aggression': 1},
            'bird': {'size': 1, 'speed': 5, 'armor': 1, 'aggression': 1},
            'ground_plant': {'size': 1, 'speed': 0, 'armor': 1, 'aggression': 0},
            'underground_plant': {'size': 2, 'speed': 0, 'armor': 2, 'aggression': 0},
            'tree_plant': {'size': 3, 'speed': 0, 'armor': 2, 'aggression': 0}
        }
        
        # 兼容不同的工具类型属性名
        tool_type_attr = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.__class__.__name__
        
        if tool_type_attr not in tool_properties or target_type not in target_characteristics:
            return 10, 0.5  # 默认值
        
        tool_stats = tool_properties[tool_type_attr]
        target_stats = target_characteristics[target_type]
        
        # 计算匹配度（基于物理原理）
        reach_match = tool_stats['reach'] / max(target_stats['speed'], 1)
        penetration_match = tool_stats['penetration'] / max(target_stats['armor'], 1)
        precision_match = tool_stats['precision'] / max(target_stats['size'], 1)
        speed_match = tool_stats['speed'] / max(target_stats['aggression'], 1)
        
        # 综合匹配度
        total_match = (reach_match + penetration_match + precision_match + speed_match) / 4
        
        # 转换为伤害和成功率
        base_damage = int(10 + total_match * 20)  # 10-30伤害范围
        success_rate = max(0.1, min(0.95, 0.3 + total_match * 0.6))  # 0.1-0.95成功率
        
        return base_damage, success_rate
    
    def _add_actionable_rule_from_experience(self, rule_type, conditions, predictions, confidence=0.7):
        """添加可执行的决策规律，供决策库和WBM系统使用"""
        try:
            import time
            
            # 创建决策规律
            actionable_rule = {
                'rule_id': f"{rule_type}_{int(time.time())}_{random.randint(1000, 9999)}",
                'rule_type': rule_type,
                'conditions': conditions.copy(),
                'predictions': predictions.copy(),
                'confidence': confidence,
                'usage_count': 0,
                'success_count': 0,
                'created_time': time.time(),
                'applicable_contexts': ['resource_acquisition', 'survival']
            }
            
            # 添加到决策规律库
            if not hasattr(self, 'actionable_rules'):
                self.actionable_rules = []
            self.actionable_rules.append(actionable_rule)
            
            # 维护规律库大小
            if len(self.actionable_rules) > 50:  # 限制规律数量
                self.actionable_rules.pop(0)
            
            # 将规律添加到五库系统
            if hasattr(self, 'five_library_system'):
                try:
                    self.five_library_system.add_rule(
                        rule_type=rule_type,
                        conditions=conditions,
                        predictions=predictions,
                        confidence=confidence,
                        source='actionable_experience'
                    )
                except Exception as e:
                    logger.log(f"{self.name} 五库规律添加失败: {str(e)}")
            
            logger.log(f"{self.name} 🎯 添加可执行规律: {rule_type} (置信度: {confidence:.2f})")
            
        except Exception as e:
            logger.log(f"{self.name} 可执行规律添加失败: {str(e)}")
    
    def _find_applicable_rule_for_situation(self, situation_context):
        """根据当前情况查找适用的规律"""
        try:
            if not hasattr(self, 'actionable_rules'):
                return None
            
            best_rule = None
            best_score = 0
            
            for rule in self.actionable_rules:
                # 计算规律匹配分数
                match_score = 0
                rule_conditions = rule.get('conditions', {})
                
                # 检查条件匹配
                for condition, value in rule_conditions.items():
                    if condition in situation_context:
                        if situation_context[condition] == value:
                            match_score += 1
                        elif value is None and situation_context[condition] is None:
                            match_score += 1
                
                # 考虑置信度
                total_score = match_score * rule.get('confidence', 0.5)
                
                if total_score > best_score:
                    best_score = total_score
                    best_rule = rule
            
            # 只返回匹配度足够高的规律
            if best_score >= 0.5:
                return best_rule
            
            return None
            
        except Exception as e:
            logger.log(f"{self.name} 规律查找失败: {str(e)}")
            return None


#
# DQN 玩家——策略决策稍微偏向搜集食物(当低于阈值时主动移动物
#
    # 🔧 修复：添加统计属性的property方法，返回实际统计数据
    @property
    def exploration_rate(self):
        """计算探索率：已探索格子数 / 总格子数"""
        if hasattr(self, '_game_map') and self._game_map:
            total_cells = self._game_map.width * self._game_map.height
            explored_cells = len(getattr(self, 'explored_cells', set()))
            return explored_cells / total_cells if total_cells > 0 else 0
        return 0

    @property
    def found_plants(self):
        """返回发现植物数量"""
        return getattr(self, 'found_plants_count', 0)

    @property
    def encountered_animals(self):
        """返回遭遇动物数量"""
        return getattr(self, 'encountered_animals_count', 0)

    @property
    def found_big_tree(self):
        """返回发现大树次数"""
        return getattr(self, 'found_big_tree_count', 0)

    @property
    def explored_cave(self):
        """返回探索洞穴次数"""
        return getattr(self, 'explored_cave_count', 0)

    @property
    def shared_info(self):
        """返回分享信息次数"""
        return getattr(self, 'shared_info_count', 0)
    @property
    def novelty_discoveries(self):
        """返回新颖发现总数"""
        return getattr(self, 'novelty_discoveries_count', 0)
    
    def increment_novelty_discovery(self, discovery_type='experience'):
        """增加新颖发现计数"""
        if not hasattr(self, 'novelty_discoveries_count'):
            self.novelty_discoveries_count = 0
        if not hasattr(self, 'new_experiences_count'):
            self.new_experiences_count = 0
        if not hasattr(self, 'new_rules_count'):
            self.new_rules_count = 0
            
        self.novelty_discoveries_count += 1
        
        if discovery_type == 'experience':
            self.new_experiences_count += 1
        elif discovery_type == 'rule':
            self.new_rules_count += 1

    def _record_exploration(self, current_cell=None):
        """🔧 修复：记录探索活动"""
        if hasattr(self, 'explored_cells'):
            self.explored_cells.add((self.x, self.y))
        
        # 检查特殊地形
        if current_cell:
            # 🔧 修复：正确匹配地形符号（匹配地图生成的"big_tree"）
            if current_cell in ["big_tree", "tree", "T"] and hasattr(self, 'found_big_tree_count'):
                # 发现大树
                if (self.x, self.y) not in getattr(self, '_found_trees', set()):
                    self.found_big_tree_count += 1
                    if not hasattr(self, '_found_trees'):
                        self._found_trees = set()
                    self._found_trees.add((self.x, self.y))
                    logger.log(f"{self.name} discovered a big tree at ({self.x}, {self.y})")
            
            elif current_cell in ["cave", "C"] and hasattr(self, 'explored_cave_count'):
                # 探索洞穴
                if (self.x, self.y) not in getattr(self, '_explored_caves', set()):
                    self.explored_cave_count += 1
                    if not hasattr(self, '_explored_caves'):
                        self._explored_caves = set()
                    self._explored_caves.add((self.x, self.y))
                    logger.log(f"{self.name} explored a cave at ({self.x}, {self.y})")

    def _record_plant_discovery(self, plant):
        """🔧 修复：记录发现植物（不是采集）"""
        if hasattr(self, 'found_plants_count'):
            plant_id = id(plant)  # 使用植物对象ID确保不重复计数
            if not hasattr(self, '_discovered_plants'):
                self._discovered_plants = set()
            
            if plant_id not in self._discovered_plants:
                self.found_plants_count += 1
                self._discovered_plants.add(plant_id)
                logger.log(f"{self.name} discovered a plant at ({plant.x}, {plant.y})")

    def _record_animal_encounter(self, animal):
        """🔧 修复：记录遭遇动物"""
        if hasattr(self, 'encountered_animals_count'):
            # 避免重复计数同一次遭遇
            encounter_key = f"{animal.type}_{animal.x}_{animal.y}_{self.x}_{self.y}"
            if not hasattr(self, '_recorded_encounters'):
                self._recorded_encounters = set()
            
            if encounter_key not in self._recorded_encounters:
                self.encountered_animals_count += 1
                self._recorded_encounters.add(encounter_key)
                logger.log(f"{self.name} encountered {animal.type} at ({animal.x}, {animal.y})")

    def _record_info_sharing(self, recipients_count=1):
        """🔧 修复：记录信息分享"""
        if hasattr(self, 'shared_info_count'):
            self.shared_info_count += recipients_count
            logger.log(f"{self.name} shared information with {recipients_count} other players")

class DQNPlayer(Player):
    def __init__(self, name, game_map):
        super().__init__(name, "DQN", game_map)

    def take_turn(self, game):
        if self.food < 30:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(directions)
            self.move(dx, dy, game.game_map)
            logger.log(f"{self.name} (DQN) seeks food")
        else:
            super().take_turn(game)


#
# PPO 玩家——策略决策稍微偏向搜集水"
#
class PPOPlayer(Player):
    def __init__(self, name, game_map):
        super().__init__(name, "PPO", game_map)

    def take_turn(self, game):
        if self.water < 30:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(directions)
            self.move(dx, dy, game.game_map)
            logger.log(f"{self.name} (PPO) seeks water")
        else:
            super().take_turn(game)


#
# RL 玩家基类
#
class RLPlayer(Player):
    def __init__(self, name, player_type, game_map):
        super().__init__(name, player_type, game_map)
        # 定义动物空间
        self.actions = {
            0: "up",
            1: "down",
            2: "left",
            3: "right",
            4: "drink",
            5: "collect",
            6: "attack"
        }
        self.num_actions = len(self.actions)
        self.state_size = 78  # 3 (玩家状态 + 5*5*3 (视野范围内的信息)
        self.last_attack_reward = 0  # 记录上一次攻击的奖励

    def get_state(self, game):
        """获取当前状态"""
        state = []
        
        # 添加玩家自身状态(归一化)
        state.extend([
            self.hp/100,  # 生命值
            self.food/100,  # 食物
            self.water/100  # 水分
        ])
        
        # 获取5x5视野范围内的环境信息
        vision_range = 2
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                x, y = self.x + dx, self.y + dy
                if game.game_map.is_within_bounds(x, y):
                    # 地形编码
                    terrain_encoding = {
                        "plain": 0.1,
                        "rock": 0.2,
                        "river": 0.3,
                        "puddle": 0.4
                    }
                    state.append(terrain_encoding.get(game.game_map.grid[y][x], 0))
                    
                    # 检查植物
                    has_plant = False
                    for plant in game.game_map.plants:
                        if plant.x == x and plant.y == y and plant.alive and not plant.collected:
                            state.append(0.6 if plant.toxic else 0.5)
                            has_plant = True
                            break
                    if not has_plant:
                        state.append(0)
                    
                    # 检查动物
                    has_animal = False
                    for animal in game.game_map.animals:
                        if animal.x == x and animal.y == y and animal.alive:
                            # 更细致的动物状态编码
                            if hasattr(animal, 'is_predator') and animal.is_predator:
                                state.append(0.9)  # 捕食者
                            else:
                                # 根据动物血量决定价"
                                health_ratio = animal.hp / animal.food  # 使用food作为最大HP
                                if health_ratio < 0.3:  # 重伤动物
                                    state.append(0.8)
                                elif health_ratio < 0.7:  # 受伤动物
                                    state.append(0.7)
                                else:  # 健全动物
                                    state.append(0.6)
                            has_animal = True
                            break
                    if not has_animal:
                        state.append(0)
                else:
                    # 超出地图范围的格子
                    state.extend([0, 0, 0])
        
        return np.array(state, dtype=np.float32)

    def attack(self, target):
        """重写攻击方法,记录伤害"""
        old_target_hp = target.hp
        super().attack(target)
        damage_dealt = old_target_hp - target.hp
        
        # 根据造成的伤害和目标类型计算奖励
        if not target.alive:  # 击杀
            self.last_attack_reward = 100 if hasattr(target, 'is_predator') and target.is_predator else 50
            self.food += 30  # 击杀获得食物
        elif damage_dealt > 0:  # 造成伤害
            self.last_attack_reward = 20 if hasattr(target, 'is_predator') and target.is_predator else 10
        else:  # 未造成伤害
            self.last_attack_reward = -5

    def execute_action(self, action_name, game):
        """执行动物并返回奖励"""
        old_state = {
            'hp': self.hp,
                'food': self.food,
                'water': self.water,
            'kills': self.killed_animals
        }
        
        reward = 0
        self.last_attack_reward = 0  # 重置攻击奖励
        
        if action_name == "up":
            self.move(0, -1, game.game_map)
        elif action_name == "down":
            self.move(0, 1, game.game_map)
        elif action_name == "left":
            self.move(-1, 0, game.game_map)
        elif action_name == "right":
            self.move(1, 0, game.game_map)
        elif action_name == "drink":
            current_cell = game.game_map.grid[self.y][self.x]
            if current_cell in ["river", "puddle"]:
                self.water = min(100, self.water + 30)
                reward += 20  # 增加饮水奖励
        elif action_name == "collect":
            for plant in game.game_map.plants:
                if plant.x == self.x and plant.y == self.y and plant.alive and not plant.collected:
                    old_food = self.food
                    self.collect_plant(plant)
                    if self.food > old_food:
                        reward += 30  # 增加采集奖励
                    break
        elif action_name == "attack":
            # 检查周围一格范围内的动物
            nearest_animal = None
            nearest_distance = float('inf')
            
            # 寻找最近的动物
            for animal in game.game_map.animals:
                if animal.alive:
                    distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                    if distance <= 1 and distance < nearest_distance:
                        nearest_animal = animal
                        nearest_distance = distance
            
            # 如果找到目标,进行攻击
            if nearest_animal:
                self.attack(nearest_animal)
                reward += self.last_attack_reward
            else:
                reward -= 5  # 惩罚无效的攻击行为
        
        # 计算基础奖励
        base_reward = self.calculate_reward(old_state)
        
        return reward + base_reward

    def calculate_reward(self, old_state):
        """计算奖励"""
        reward = 0.0
        
        # 生存奖励
        if self.alive:
            reward += 0.1
        else:
            return -100.0  # 死亡惩罚
        
        # 状态变化奖励
        hp_change = self.hp - old_state['hp']
        food_change = self.food - old_state['food']
        water_change = self.water - old_state['water']
        kills_change = self.killed_animals - old_state['kills']
        
        # 血量变化奖励
        if hp_change > 0:
            reward += 0.5
        elif hp_change < 0:
            reward -= 0.5
            
        # 食物变化奖励
        if food_change > 0:
            reward += 0.3
        elif food_change < 0:
            reward -= 0.2
            
        # 水分变化奖励
        if water_change > 0:
            reward += 0.3
        elif water_change < 0:
            reward -= 0.2
            
        # 击杀奖励
        if kills_change > 0:
            reward += 5.0
            
        # 状态过低惩罚
        if self.hp < 30:
            reward -= 0.5
        if self.food < 30:
            reward -= 0.5
        if self.water < 30:
            reward -= 0.5
            
        return float(reward)  # 确保返回float类型

    def take_turn(self, game):
        if not self.alive:
            return
            
        # 首先执行父类的take_turn,确保资源消耗
        super().take_turn(game)
        
        # 如果已经死亡,直接返回
        if not self.alive:
            return
            
        try:
            # 获取当前状态
            current_state = self.get_state(game)
            
            # 选择动作
            action = self.select_action(current_state)
            
            # 处理动作格式：确保action_str是动作字符串，action_idx是动作索引
            if isinstance(action, str):
                # action是字符串（来自DQN等），需要转换为索引
                action_str = action
                if action_str in self.actions.values():
                    # 找到对应的索引
                    action_idx = None
                    for idx, act in self.actions.items():
                        if act == action_str:
                            action_idx = idx
                            break
                else:
                    # 无效动作，使用随机动作
                    action_idx = random.choice(list(self.actions.keys()))
                    action_str = self.actions[action_idx]
            else:
                # action是索引（来自PPO等）
                action_idx = action
                if action_idx in self.actions:
                    action_str = self.actions[action_idx]
                else:
                    # 无效索引，使用随机动作
                    action_idx = random.choice(list(self.actions.keys()))
                    action_str = self.actions[action_idx]
            
            # 执行动作
            reward = self.execute_action(action_str, game)
            
            # 获取新状态
            next_state = self.get_state(game)
            
            # 存储经验（使用索引）
            self.remember(current_state, action_idx, reward, next_state, not self.alive)
            
            # 训练网络
            self.train()
        except Exception as e:
            logger.log(f"RL行为执行失败: {str(e)}")
            # 如果AI行为失败,执行随机移动
            try:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                self.move(dx, dy, game.game_map)
            except Exception as fallback_e:
                logger.log(f"RL应急移动也失败: {str(fallback_e)}")
        
    def remember(self, state, action, reward, next_state, done):
        """存储经验 - 兼容DQN和PPO"""
        # 检查是否有网络存在（DQN使用q_network，PPO使用policy_network）
        has_network = hasattr(self, 'q_network') and self.q_network is not None
        has_policy_network = hasattr(self, 'policy_network') and self.policy_network is not None
        
        if has_network or has_policy_network:
            if hasattr(self, 'memory'):
                self.memory.append((state, action, reward, next_state, done))
            elif hasattr(self, 'trajectory'):
                # PPO使用trajectory存储
                pass  # PPO有自己的存储机制
            
    def train(self):
        """训练网络 - 兼容DQN和PPO"""
        # DQN训练
        if hasattr(self, 'q_network') and self.q_network is not None:
            if not hasattr(self, 'memory') or len(self.memory) < getattr(self, 'batch_size', 32):
                return
                
            try:
                batch = random.sample(self.memory, getattr(self, 'batch_size', 32))
                states = np.array([x[0] for x in batch])
                actions = np.array([x[1] for x in batch])
                rewards = np.array([x[2] for x in batch])
                next_states = np.array([x[3] for x in batch])
                dones = np.array([x[4] for x in batch])
                
                # 计算目标Q值
                if hasattr(self, 'target_network') and self.target_network is not None:
                    target_q_values = self.target_network.predict(next_states, verbose=0)
                    max_target_q = np.max(target_q_values, axis=1)
                    targets = rewards + getattr(self, 'gamma', 0.95) * max_target_q * (1 - dones)
                    
                    # 训练网络
                    q_values = self.q_network.predict(states, verbose=0)
                    for i in range(len(batch)):
                        q_values[i][actions[i]] = targets[i]
                    self.q_network.fit(states, q_values, verbose=0)
            except Exception as e:
                logger.log(f"DQN训练失败: {str(e)}")
        
        # PPO训练
        elif hasattr(self, 'policy_network') and self.policy_network is not None:
            # PPO有自己的update_policy方法
            if hasattr(self, 'update_policy'):
                try:
                    self.update_policy()
                except Exception as e:
                    logger.log(f"PPO训练失败: {str(e)}")
        
        # 如果都没有，就什么都不做
        else:
            pass


class DQNPlayer(RLPlayer):
    def __init__(self, name, game_map):
        super().__init__(name, "DQN", game_map)
        self.epsilon = 0.1  # 探索率
        self.gamma = 0.95  # 折扣因子
        self.learning_rate = 0.01  # 将学习率从.001提高从.01
        self.memory = deque(maxlen=10000)  # 经验回放缓冲区
        self.batch_size = 32
        
        # 创建或加载模型
        model_path = os.path.join(MODELS_DIR, f"dqn_model_{name}.keras")
        if os.path.exists(model_path):
            try:
                self.q_network = tf.keras.models.load_model(model_path)
                self.target_network = tf.keras.models.load_model(model_path)
                logger.log(f"DQN玩家 {name} 加载已有模型")
            except Exception as e:
                logger.log(f"加载DQN模型失败: {str(e)}, 创建新模型")
                self.q_network = self.build_network()
                self.target_network = self.build_network()
        else:
            self.q_network = self.build_network()
            self.target_network = self.build_network()
            
    def save_model(self):
        """保存模型"""
        if self.q_network:
            try:
                # 确保模型保存目录存在
                if not os.path.exists(MODELS_DIR):
                    os.makedirs(MODELS_DIR)
                
                model_path = os.path.join(MODELS_DIR, f"dqn_model_{self.name}.keras")
                self.q_network.save(model_path)
                
                # 验证模型是否确实保存成功
                if os.path.exists(model_path):
                    logger.log(f"✅ DQN模型 {self.name} 保存成功: {model_path}")
                else:
                    logger.log(f"⚠️ DQN模型 {self.name} 保存验证失败")
            except Exception as e:
                logger.log(f"❌ 保存DQN模型失败: {str(e)}")
                
    def build_network(self):
        """构建神经网络"""
        try:
            model = Sequential()
            # 增加模型复杂度,添加Dropout以避免过拟合
            model.add(Dense(128, input_dim=self.state_size, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(128, activation='relu'))
            model.add(Dense(self.num_actions, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
            return model
        except Exception as e:
            import traceback
            logger.log(f"{self.name} 构建网络失败: {str(e)}")
            logger.log(traceback.format_exc())
            return None
    
    def select_action(self, state):
        """使用 epsilon-greedy 策略选择动物"""
        try:
            # 确保网络已初始化
            if self.q_network is None:
                logger.log(f"{self.name} Q网络未初始化,尝试初始化...")
                if not self.initialize_networks():
                    logger.log(f"{self.name} 无法初始化网络,回退到ILAI策略")
                    return self._select_ilai_action()
            
            # 以epsilon的概率随机选择动物
            if np.random.rand() <= self.epsilon:
                action_idx = random.randrange(self.num_actions)
                logger.log(f"{self.name} 探索:随机选择动物 {self.actions[action_idx]}")
                return self.actions[action_idx]
            
            # 否则选择Q值最大的动物
            act_values = self.q_network.predict(state.reshape(1, -1), verbose=0)
            action_idx = np.argmax(act_values[0])
            logger.log(f"{self.name} 利用:选择Q值最大的动物 {self.actions[action_idx]}")
            return self.actions[action_idx]
        except Exception as e:
            import traceback
            logger.log(f"{self.name} 选择动物失败: {str(e)}")
            logger.log(traceback.format_exc())
            logger.log(f"{self.name} 回退到ILAI策略")
            return self._select_ilai_action()
    
    def _select_ilai_action(self):
        """回退使用ILAI策略选择动物"""
        # 这里调用原来的ILAI决策逻辑
        try:
            x, y = self.current_pos
            # 检查水量不足时寻找水源
            if self.water < 30:
                water_sources = [resource for resource in self.game_map.resources if resource.type == "water"]
                if water_sources:
                    nearest_water = min(water_sources, key=lambda w: ((w.position[0] - x) ** 2 + (w.position[1] - y) ** 2) ** 0.5)
                    wx, wy = nearest_water.position
                    if (wx, wy) == (x, y):
                        return "drink"
                    elif abs(wx - x) > abs(wy - y):
                        return "right" if wx > x else "left"
                    else:
                        return "down" if wy > y else "up"
            
            # 检查食物不足时寻找食物
            if self.food < 30:
                food_sources = [resource for resource in self.game_map.resources if resource.type == "berry"]
                if food_sources:
                    nearest_food = min(food_sources, key=lambda f: ((f.position[0] - x) ** 2 + (f.position[1] - y) ** 2) ** 0.5)
                    fx, fy = nearest_food.position
                    if (fx, fy) == (x, y):
                        return "collect"
                    elif abs(fx - x) > abs(fy - y):
                        return "right" if fx > x else "left"
                    else:
                        return "down" if fy > y else "up"
            
            # 危险时躲避捕食者
            for predator in self.game_map.predators:
                px, py = predator.position
                distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                if distance < 3:  # 当捕食者距离小于3格时躲避
                    # 向远离捕食者的方向移动
                    if abs(px - x) > abs(py - y):
                        return "left" if px > x else "right"
                    else:
                        return "up" if py > y else "down"
            
            # 默认随机移动
            return random.choice(["up", "down", "left", "right"])
        except Exception as e:
            logger.log(f"{self.name} ILAI决策失败: {str(e)}")
            # 完全失败时随机选择
            return random.choice(["up", "down", "left", "right"])
        
    def take_turn(self, game):
        if not self.alive:
            return
            
        # 首先执行父类的take_turn,确保资源消耗
        super().take_turn(game)
        
        # 如果已经死亡,直接返回
        if not self.alive:
            return
            
        try:
            # 获取当前状态
            current_state = self.get_state(game)
            
            # 选择动作
            action_str = self.select_action(current_state)
            
            # 确保action_str是有效的动作字符串
            if action_str not in self.actions.values():
                logger.log(f"{self.name} 无效动作: {action_str}, 使用默认动作")
                action_str = random.choice(list(self.actions.values()))
            
            # 获取动作索引（从字典值找到对应的键）
            action_idx = None
            for idx, action in self.actions.items():
                if action == action_str:
                    action_idx = idx
                    break
            
            # 如果没找到对应索引，使用随机动作
            if action_idx is None:
                action_idx = random.choice(list(self.actions.keys()))
                action_str = self.actions[action_idx]
            
            # 执行动作
            reward = self.execute_action(action_str, game)
            
            # 获取新状态
            next_state = self.get_state(game)
            
            # 存储经验
            self.remember(current_state, action_idx, reward, next_state, not self.alive)
            
            # 训练网络
            self.train()
        except Exception as e:
            logger.log(f"DQN行为执行失败: {str(e)}")
            # 如果AI行为失败,执行随机移动
            try:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                self.move(dx, dy, game.game_map)
            except Exception as fallback_e:
                logger.log(f"{self.name} 应急移动也失败: {str(fallback_e)}")


class PPOPlayer(RLPlayer):
    def __init__(self, name, game_map):
        super().__init__(name, "PPO", game_map)
        self.gamma = 0.99
        self.clip_ratio = 0.2
        self.policy_learning_rate = 0.003  # 将策略学习率从.0003提高从.003
        self.value_learning_rate = 0.01  # 将价值学习率从.001提高从.01
        
        # 创建或加载模型
        policy_path = os.path.join(MODELS_DIR, f"ppo_policy_{name}.keras")
        value_path = os.path.join(MODELS_DIR, f"ppo_value_{name}.keras")
        
        if os.path.exists(policy_path) and os.path.exists(value_path):
            try:
                self.policy_network = tf.keras.models.load_model(policy_path)
                self.value_network = tf.keras.models.load_model(value_path)
                logger.log(f"PPO玩家 {name} 加载已有模型")
            except Exception as e:
                logger.log(f"加载PPO模型失败: {str(e)}, 创建新模型")
                self.policy_network = self.build_policy_network()
                self.value_network = self.build_value_network()
        else:
            self.policy_network = self.build_policy_network()
            self.value_network = self.build_value_network()
            
        self.trajectory = []
            
    def save_model(self):
        """保存模型"""
        if self.policy_network and self.value_network:
            try:
                # 确保模型保存目录存在
                if not os.path.exists(MODELS_DIR):
                    os.makedirs(MODELS_DIR)
                
                policy_path = os.path.join(MODELS_DIR, f"ppo_policy_{self.name}.keras")
                value_path = os.path.join(MODELS_DIR, f"ppo_value_{self.name}.keras")
                self.policy_network.save(policy_path)
                self.value_network.save(value_path)
                
                # 验证模型是否确实保存成功
                if os.path.exists(policy_path) and os.path.exists(value_path):
                    logger.log(f"✅ PPO模型 {self.name} 保存成功: {policy_path}, {value_path}")
                else:
                    logger.log(f"⚠️ PPO模型 {self.name} 保存验证失败")
            except Exception as e:
                logger.log(f"❌ 保存PPO模型失败: {str(e)}")
                
    def build_policy_network(self):
        """构建策略网络"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(self.num_actions, activation='softmax')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.policy_learning_rate))
        return model
        
    def build_value_network(self):
        """构建价值网络"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.value_learning_rate),
                     loss='mse')
        return model
        
    def select_action(self, state):
        """使用策略网络选择动物"""
        if not self.policy_network:
            return random.randint(0, self.num_actions - 1), 0
            
        try:
            action_probs = self.policy_network.predict(state.reshape(1, -1), verbose=0)[0]
            action = np.random.choice(self.num_actions, p=action_probs)
            log_prob = np.log(action_probs[action])
            return action, log_prob
        except Exception as e:
            logger.log(f"PPO动物选择失败: {str(e)}")
            return random.randint(0, self.num_actions - 1), 0
        
    def take_turn(self, game):
        if not self.alive:
            return
            
        # 首先执行父类的take_turn,确保资源消耗
        super().take_turn(game)
        
        # 如果已经死亡,直接返回
        if not self.alive:
            return
            
        try:
            # 获取当前状态
            current_state = self.get_state(game)
            
            # 选择动作
            action, log_prob = self.select_action(current_state)
            
            # 确保action在有效范围内
            if action < 0 or action >= len(self.actions):
                logger.log(f"{self.name} 无效动作索引: {action}, 使用随机动作")
                action = random.randint(0, len(self.actions) - 1)
                log_prob = 0  # 重置log_prob
            
            # 获取当前状态的价值估计
            if self.value_network:
                try:
                    value = self.value_network.predict(current_state.reshape(1, -1), verbose=0)[0][0]
                except Exception as value_e:
                    logger.log(f"{self.name} 价值网络预测失败: {str(value_e)}")
                    value = 0
            else:
                value = 0
            
            # 执行动作
            action_str = self.actions[action]
            reward = self.execute_action(action_str, game)
            
            # 存储轨迹
            if self.policy_network and self.value_network:
                self.trajectory.append((current_state, action, reward, value, log_prob))
            
                # 每100步更新一次策略
                if len(self.trajectory) >= 100:
                    self.update_policy()
                    self.clear_trajectory()
        except Exception as e:
            logger.log(f"PPO行为执行失败: {str(e)}")
            # 如果AI行为失败,执行随机移动
            try:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                dx, dy = random.choice(directions)
                self.move(dx, dy, game.game_map)
            except Exception as fallback_e:
                logger.log(f"{self.name} 应急移动也失败: {str(fallback_e)}")
            
    def update_policy(self):
        """更新策略网络和价值网络"""
        if not self.policy_network or not self.value_network:
            return
            
        # 检查轨迹是否为空
        if not self.trajectory:
            return
            
        try:
            # 计算优势函数
            returns = []
            advantages = []
            R = 0
            
            # 修复元组解包：轨迹格式是(state, action, reward, value, log_prob)
            for state, action, reward, value, log_prob in reversed(self.trajectory):
                R = reward + self.gamma * R
                advantage = R - value
                returns.append(R)
                advantages.append(advantage)
            returns.reverse()
            advantages.reverse()
            
            # 转换为numpy数组，添加形状验证
            states = np.array([x[0] for x in self.trajectory])
            actions = np.array([x[1] for x in self.trajectory])
            old_log_probs = np.array([x[4] for x in self.trajectory])
            
            # 验证状态形状
            if len(states) == 0 or (len(states) > 0 and len(states[0]) == 0):
                logger.log(f"PPO策略更新跳过: 状态数据为空")
                return
                
            # 确保状态形状正确
            if len(states.shape) == 1:
                # 如果状态是1维的，需要重新调整形状
                logger.log(f"PPO策略更新跳过: 状态形状异常 {states.shape}")
                return
            
            returns = np.array(returns)
            advantages = np.array(advantages)
            
            # 标准化优势函数
            if len(advantages) > 1:
                advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)
            
            # 更新策略网络
            with tf.GradientTape() as tape:
                # 计算新的动作概率
                action_probs = self.policy_network(states)
                new_log_probs = tf.math.log(tf.gather(action_probs, actions, batch_dims=1))
                
                # 计算比率
                ratio = tf.exp(new_log_probs - old_log_probs)
                
                # 计算裁剪后的目标函数
                clip_advantage = tf.clip_by_value(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantages
                policy_loss = -tf.reduce_mean(tf.minimum(ratio * advantages, clip_advantage))
            
            # 更新策略网络
            grads = tape.gradient(policy_loss, self.policy_network.trainable_variables)
            self.policy_network.optimizer.apply_gradients(zip(grads, self.policy_network.trainable_variables))
            
            # 更新价值网络
            self.value_network.fit(states, returns, verbose=0)
            
        except Exception as e:
            logger.log(f"PPO策略更新失败: {str(e)}")
        
    def clear_trajectory(self):
        """清空轨迹"""
        self.trajectory = []


#
# 婴儿学习 AI 玩家(ILAI)——具有层级认知、发育认知、动态多头注意力、社会化决策及逻辑推理机制
# 根据游戏进程(初期、中期、后期)调整决策策略
#
class ILAIPlayer(Player):
    def __init__(self, name, game_map):
        super().__init__(name, "ILAI", game_map)
        # 保存game_map引用,用于移动方法
        self.game_map = game_map
        
        # 设置玩家类型
        self.player_type = "ILAI"
        
        # 首先创建logger实例
        self.logger = Logger()
        logger = self.logger
        
        # 初始化多层次记忆系统(替换原有的简单经验库)
        self.memory_system = MultiLayerMemorySystem()
        
        # === 1.4.0版本新增:木桥模型集成===
        self.wooden_bridge_model = WoodenBridgeModel(logger=logger)
        
        # === 2.0.0版本新增:BMP规律生成系统集成===
        try:
            # 使用完整的BloomingAndPruningModel系统
            self.bpm = BloomingAndPruningModel(logger=logger)
            
            if logger:
                logger.log(f"{name} 🔥 BMP规律生成系统初始化成功")
        except ImportError as e:
            if logger:
                logger.log(f"从{name} BMP模块导入失败: {str(e)}")
            self.bpm = None
        except Exception as e:
            if logger:
                logger.log(f"{name} BMP初始化失败: {str(e)}")
            self.bpm = None
        self.eocar_experiences = []  # EOCATR经验存储
        self.knowledge_evolution_stats = {
            'evolution_cycles': 0,
            'successful_adaptations': 0,
            'failed_adaptations': 0
        }
        
        # === 2.0.1版本新增:BPM集成管理器===
        try:
            self.bmp_integration = BPMIntegrationManager(logger=logger)
            self.bmp_integration_active = True
            
            # BPM集成统计
            self.bmp_integration_stats = {
                'candidate_rules_generated': 0,
                'rules_validated': 0,
                'integration_cycles': 0,
                'last_integration_time': 0.0
            }
            
            if logger:
                logger.log(f"{name} BPM集成管理器初始化成功 - 支持15种EOCAR组合规律生成")
        except ImportError as e:
            if logger:
                logger.log(f"{name} BPM集成管理器导入失败: {str(e)}")
            self.bmp_integration = None
            self.bmp_integration_active = False
        except Exception as e:
            if logger:
                logger.log(f"{name} BPM集成管理器初始化失败: {str(e)}")
            self.bmp_integration = None
            self.bmp_integration_active = False
        
        # === 2.1.0版本新增:规律验证系统集成===
        self.rule_validation_system = RuleValidationSystem(logger=logger)
        self.validation_opportunities = []  # 验证机会队列
        self.validated_rules = []  # 已验证规律库
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'high_confidence_rules': 0,
            'medium_confidence_rules': 0,
            'low_confidence_rules': 0
        }
        
        if logger:
            logger.log(f"ILAI玩家 {name} 已集成规律验证系统")
        
        # === 新增:动态多头注意力机制集成 ===
        self.dmha = DynamicMultiHeadAttention(logger=logger)
        
        # === SSM场景符号化机制集成===
        # 创建SSM实例
        self.ssm = SceneSymbolizationMechanism(logger=logger)
        
        # 经验库升级为E-O-C-A-T-R格式
        self.eocar_experience_base = []  # E-O-C-A-T-R格式的经验库
        self.eocar_indirect_experience_base = []  # 间接E-O-C-A-T-R经验库
        
        # 保持兼容性的传统经验库
        self.direct_experience_base = []  # 直接经验库
        self.indirect_experience_base = []  # 间接经验库
        self.congenital_knowledge = []  # 先天知识库
        self.rule_base = []  # 规则库
        
        # SSM相关时间戳
        self.current_timestamp = 0.0
        
        # 当前E-O-C-A-T-R符号化场景(用于决策)
        self.current_eocar_scene = []
        
        # 设置经验库容量
        self.max_eocar_experiences = 300  # E-O-C-A-T-R经验容量
        
        if logger:
            logger.log(f"ILAI玩家 {name} 已集成SSM场景符号化机制")
        
        # === 数据格式统一化器集成 ===
        # 创建数据格式统一化器实例
        self.data_format_unifier = create_data_format_unifier(logger=logger)
        
        # 统一格式经验库
        self.unified_experiences = []  # 统一格式的经验库
        self.max_unified_experiences = 500  # 统一经验库容量
        
        # 数据格式统计
        self.format_conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'format_types_encountered': set()
        }
        
        if logger:
            logger.log(f"ILAI玩家 {name} 已集成数据格式统一化器")
        
        # === 统一知识决策系统集成 ===
        if UNIFIED_KNOWLEDGE_AVAILABLE:
            try:
                self.unified_knowledge_system = UnifiedKnowledgeDecisionSystem()
                self.ukds_active = True
                
                # 统一知识决策系统相关统计
                self.ukds_stats = {
                    'decisions_made': 0,
                    'rules_generated': 0,
                    'scenarios_analyzed': 0,
                    'successful_predictions': 0,
                    'failed_predictions': 0
                }
                
                if logger:
                    logger.log(f"ILAI玩家 {name} 已集成统一知识决策系统")
            except Exception as e:
                if logger:
                    logger.log(f"ILAI玩家 {name} 统一知识决策系统初始化失败: {str(e)}")
                self.unified_knowledge_system = None
                self.ukds_active = False
        else:
            self.unified_knowledge_system = None
            self.ukds_active = False
        
        # === 五库知识管理系统集成 ===
        try:
            from five_library_system import FiveLibrarySystem
            # 为每个玩家创建独立的数据库文件
            db_path = f"player_{name}_four_library.db"
            self.five_library_system = FiveLibrarySystem()
            self.five_library_system_active = True
            
            if logger:
                logger.log(f"ILAI玩家 {name} 已集成五库知识管理系统(DB: {db_path})")
        except ImportError as e:
            if logger:
                logger.log(f"{self.name} 五库系统导入失败: {str(e)}")
            self.five_library_system = None
            self.five_library_system_active = False
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 五库系统初始化失败: {str(e)}")
            self.five_library_system = None
            self.five_library_system_active = False
        
        # === 统一决策系统集成 ===
        try:
            self.unified_decision_system = UnifiedDecisionSystem(logger=logger)
            self.unified_decision_system.bmp_generator = SimplifiedBMPGenerator(logger=logger)
            self.unified_decision_active = True
            
            if logger:
                logger.log(f"ILAI玩家 {name} 已集成统一决策系统(EOCATR标准化)")
        except Exception as e:
            if logger:
                logger.log(f"ILAI玩家 {name} 统一决策系统初始化失败: {str(e)}")
            self.unified_decision_system = None
            self.unified_decision_active = False
        
        # === 整合决策系统集成 ===
        if INTEGRATED_DECISION_AVAILABLE:
            try:
                # 确保BMP系统已初始化,如果没有则设为None
                bmp_system = getattr(self, 'bpm', None)
                
                self.integrated_decision_system = IntegratedDecisionSystem(
                    five_library_system=self.five_library_system,
                    wooden_bridge_model=self.wooden_bridge_model,
                    bmp_system=bmp_system,
                    logger=logger
                )
                self.integrated_decision_active = True
                
                if logger:
                    logger.log(f"ILAI玩家 {name} 已集成整合决策系统(V3决策库匹配+ WBM规律构建)")
                    logger.log(f"   五库系统: {self.five_library_system is not None}")
                    logger.log(f"   木桥模型: {self.wooden_bridge_model is not None}")
                    logger.log(f"   BMP系统: {bmp_system is not None}")
            except Exception as e:
                if logger:
                    logger.log(f"ILAI玩家 {name} 整合决策系统初始化失败: {str(e)}")
                    import traceback
                    logger.log(traceback.format_exc())
                self.integrated_decision_system = None
                self.integrated_decision_active = False
        else:
            self.integrated_decision_system = None
            self.integrated_decision_active = False
        
        # === 1.3.0版本组件集成 ===
        try:
            from curiosity_driven_learning import CuriosityDrivenLearning
            from enhanced_multi_reward_system import EnhancedMultiRewardSystem
            
            self.curiosity_driven_learning = CuriosityDrivenLearning(logger=logger)
            self.enhanced_multi_reward_system = EnhancedMultiRewardSystem(logger=logger)
            
            # 集成状态跟"
            self.cdl_active = True
            self.emrs_active = True
            
            if logger:
                logger.log(f"{self.name} 成功集成CDL和EMRS系统")
        except ImportError as e:
            if logger:
                logger.log(f"{self.name} CDL/EMRS模块导入失败: {str(e)}")
            self.cdl_active = False
            self.emrs_active = False
        
        # 保留原有的阶段信息
        self.phase = "初期"
        
        # === 木桥模型相关状态===
        self.current_goals = []  # 当前活跃目标
        self.active_bridge_plan = None  # 当前执行的桥梁方法
        self.bridge_execution_state = {
            'current_step': 0,
            'total_steps': 0,
            'step_results': []
        }
        
        # 规律库(从BPM和经验中动态构建)
        self.available_rules = []
        self.rule_performance_tracker = {}
        
        # 发育阶段跟踪(用于CDL和木桥模型)
        self.developmental_stage = 0.0  # 0.0=婴儿期,1.0=成熟期
        self.life_experience_count = 0
        
        # === CDL相关属性===
        self.visited_positions = set()  # 记录访问过的位置,用于CDL探索
        
        # === 保留原有RL相关参数 ===
        # 是否启用强化学习
        self.use_reinforcement_learning = False
        
        # 强化学习相关参数
        self.memory = deque(maxlen=10000)  # 经验回放缓冲区
        self.gamma = 0.95  # 折扣因子
        self.epsilon = 0.2  # 初始探索率
        self.epsilon_min = 0.05  # 最小探索率
        self.epsilon_decay = 0.995  # 探索率衰减
        self.learning_rate = 0.001  # 学习率
        self.batch_size = 32  # 批量学习大小
        self.state_size = 78  # 状态向量大小
        self.num_actions = 7  # 动物数量
        self.train_frequency = 5  # 每执行这么多步骤进行一次训"
        self.target_update_frequency = 20  # 更新目标网络的频"
        self.step_counter = 0  # 记录步数
        self.actions = {
            0: "up",
            1: "down",
            2: "left", 
            3: "right",
            4: "drink",
            5: "collect",
            6: "attack"
        }
        
        # RL状态跟踪
        self.last_action = None
        self.last_state = None
        self.last_reward = 0
        
        # Q网络和目标网络初始为None,延迟初始化
        self.q_network = None
        self.target_network = None
        
        # 初始化EMRS v2.0五维评价系统
        try:
            from enhanced_multi_reward_system_v2 import EnhancedMultiRewardSystemV2
            self.enhanced_multi_reward_system = EnhancedMultiRewardSystemV2(
                logger=logger, 
                development_stage=getattr(self, 'development_stage', 'child')
            )
            self.emrs_active = True
            if logger:
                logger.log(f"{self.name} EMRS v2.0五维评价系统初始化成功")
        except Exception as e:
            if logger:
                logger.log(f"{self.name} EMRS v2.0初始化失败,回退到原系统: {str(e)}")
            try:
                self.enhanced_multi_reward_system = EnhancedMultiRewardSystem(logger=logger)
                self.emrs_active = True
                # 包装EMRS实例以提供兼容性
                self.enhanced_multi_reward_system = wrap_emrs_for_compatibility(self.enhanced_multi_reward_system)
            except Exception as e2:
                if logger:
                    logger.log(f"{self.name} EMRS系统完全初始化失败: {str(e2)}")
                self.emrs_active = False

        # === 社交学习机制初始化===
        # 初始化增强的间接经验库功能(仅限ILAI和RILAI"
        try:
            self.initialize_social_learning()
            if logger:
                logger.log(f"{self.name} 间接经验库功能增强完成")
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 社交学习初始化失败: {str(e)}")

        # === 位置跟踪机制 ===
        # 初始化位置跟踪(社交学习必需)
        self.current_pos = (self.x, self.y)
        self.last_pos = (self.x, self.y)
        self.visited_positions = set()
        self.visited_positions.add(self.current_pos)
        
        if logger:
            logger.log(f"{self.name} 位置跟踪机制已初始化: {self.current_pos}")
        
        # === EOCATR系统性规律生成机制(新增) ===
        self.eocatr_initialized = False
        self.eocatr_generation_stats = {
            'total_generated': 0,
            'generation_time': 0.0,
            'last_generation_timestamp': 0.0
        }
        
        # 初始化系统性EOCATR规律生成
        try:
            if (self.five_library_system_active and self.five_library_system and
                hasattr(self, 'bpm') and self.bpm is not None):
                
                # 1. 五库系统配置EOCATR矩阵
                trigger_result = self.five_library_system.trigger_systematic_eocatr_rule_generation()
                
                if trigger_result['status'] == 'success':
                    # 2. BPM系统生成系统性规律
                    matrix_config = trigger_result['matrix_config']
                    systematic_rules = self.bmp.generate_systematic_eocatr_rules(matrix_config)
                    
                    # 3. 将生成的规律添加到BMP候选规律库
                    for rule in systematic_rules:
                        self.bmp.candidate_rules[rule.rule_id] = rule
                    
                    # 4. 更新统计信息
                    self.eocatr_generation_stats = {
                        'total_generated': len(systematic_rules),
                        'generation_time': trigger_result.get('generation_time', 0.0),
                        'last_generation_timestamp': time.time(),
                        'expected_total': trigger_result['total_expected'],
                        'matrix_config_id': trigger_result['config_decision_id']
                    }
                    
                    self.eocatr_initialized = True
                    
                    if logger:
                        logger.log(f"{self.name} EOCATR系统性规律生成完成")
                        logger.log(f"   生成规律数量: {len(systematic_rules)}")
                        logger.log(f"   预期规律总数: {trigger_result['total_expected']}")
                        logger.log(f"   配置决策ID: {trigger_result['config_decision_id']}")
                        
                        # 获取BMP统计信息进行验证
                        bmp_stats = self.bmp.get_eocatr_generation_statistics()
                        if 'systematic_eocatr_rules' in bmp_stats:
                            sys_stats = bmp_stats['systematic_eocatr_rules']
                            logger.log(f"   BMP系统性规律统从 候从{sys_stats.get('candidate', 0)}, 已验从{sys_stats.get('validated', 0)}")
                        
                        # 五库系统完整性验"
                        completeness = self.five_library_system.validate_eocatr_matrix_completeness(bmp_stats)
                        if 'completeness_check' in completeness:
                            coverage = completeness['completeness_check'].get('coverage_percentage', 0)
                            logger.log(f"   矩阵覆盖率: {coverage:.2f}%")
                else:
                    if logger:
                        logger.log(f"{self.name} EOCATR系统性规律生成触发失败: {trigger_result['message']}")
            else:
                if logger:
                    missing_components = []
                    if not self.five_library_system_active:
                        missing_components.append("五库系统")
                    if not hasattr(self, 'bmp') or self.bmp is None:
                        missing_components.append("BMP系统")
                    
                    logger.log(f"⚠️ {self.name} EOCATR系统性规律生成跳过,缺少组件: {', '.join(missing_components)}")
        except Exception as e:
            if logger:
                logger.log(f"{self.name} EOCATR系统性规律生成失败: {str(e)}")
                import traceback
                logger.log(traceback.format_exc())

        # === WBM内存同步功能集成 ===
        # 启用内存到五库系统的自动同步功能
        try:
            from wbm_memory_to_database_sync import apply_memory_sync_patch
            self.memory_sync = apply_memory_sync_patch(self)
            if logger:
                logger.log(f"✅ {self.name} WBM内存同步功能已启用")
        except Exception as e:
            if logger:
                logger.log(f"⚠️ {self.name} WBM内存同步功能启用失败: {str(e)}")
            self.memory_sync = None

        # === 🔧 初始化工具系统 ===
        # 初始化工具列表
        self.tools = []
        
        # === 🔧 默认工具装备系统 ===
        # 自动装备所有6种工具，简化学习专注于多规律协作
        self._equip_default_tools()
        
        # 🧠 初始化学习机制数据结构
        self.tool_effectiveness = {}  # 存储工具效果经验: (tool_name, target_type) -> {'effectiveness': float, 'attempts': int}
        self.tool_experiment_counts = {}  # 工具实验次数: tool_name -> count
        self._recorded_encounters = set()  # 避免重复记录遭遇
        
        # === 🗓️ 长链决策记忆管理系统 ===
        # 当前执行的多日计划
        self.current_multi_day_plan = None
        # 当前执行到第几天（从1开始）
        self.plan_current_day = 0
        # 计划制定时的环境状态快照
        self.plan_initial_state = None
        # 每日执行记录
        self.daily_execution_log = []
        # 计划调整历史
        self.plan_adjustment_history = []
        # 计划失败原因记录
        self.plan_failure_reasons = []
        # 计划成功完成次数
        self.plan_completion_stats = {
            'total_started': 0,
            'total_completed': 0,
            'total_interrupted': 0,
            'total_adjusted': 0
        }
        
        if logger:
            logger.log(f"ILAI玩家 {name} 长链决策记忆管理系统已初始化")

    def _equip_default_tools(self):
        """默认装备所有6种工具，简化学习专注于多规律协作"""
        try:
            # 导入工具类
            from animals_plants_tools_expansion import Spear, Stone, Bow, Basket, Shovel, Stick
            
            # 创建所有工具实例并添加到工具库
            default_tools = [
                ("长矛", Spear),    # 用于猛兽(Tiger, BlackBear)
                ("石头", Stone),    # 用于猎物(Rabbit, Boar)  
                ("弓箭", Bow),      # 用于鸟类(Pheasant, Dove)
                ("篮子", Basket),   # 用于地面植物(Strawberry, Mushroom等)
                ("铁锹", Shovel),   # 用于地下植物(Potato, SweetPotato)
                ("棍子", Stick)     # 用于树上植物(Acorn, Chestnut)
            ]
            
            for tool_name_cn, tool_class in default_tools:
                # 创建工具实例
                tool = tool_class()
                # 添加到工具库
                self.tools.append(tool)
            
            if self.logger:
                self.logger.log(f"{self.name} 🔧 已装备所有6种工具：长矛、石头、弓箭、篮子、铁锹、棍子")
            
            # === 🧠 初始化工具效果学习系统 ===
            self._initialize_tool_learning_system()
            
        except ImportError as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具类导入失败: {str(e)}")
            # 如果导入失败，创建简单的工具对象
            self._create_simple_tools()
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具装备失败: {str(e)}")
            self._create_simple_tools()

    def _create_simple_tools(self):
        """创建简单的工具对象（备用方案）"""
        class SimpleTool:
            def __init__(self, name):
                self.name = name
                self.__class__.__name__ = name.replace("Simple", "")
        
        simple_tools = ["长矛", "石头", "弓箭", "篮子", "铁锹", "棍子"]
        for tool_name in simple_tools:
            tool = SimpleTool(tool_name)
            self.tools.append(tool)
        
        if self.logger:
            self.logger.log(f"{self.name} 🔧 已装备简单工具版本：{', '.join(simple_tools)}")
        
        # 初始化基础学习系统
        self.tool_effectiveness = {}
        self.tool_usage_history = []

    def _initialize_tool_learning_system(self):
        """初始化工具效果学习系统"""
        # 工具效果记录：{(tool_type, target_type): {'successes': int, 'attempts': int, 'effectiveness': float}}
        self.tool_effectiveness = {}
        
        # 工具使用历史
        self.tool_usage_history = []
        
        # 实验计数器，确保每种工具都被尝试
        self.tool_experiment_counts = {}
        for tool in self.tools:
            # 兼容不同的工具类型属性名
            tool_type = getattr(tool, 'tool_type', None) or getattr(tool, 'type', None) or tool.__class__.__name__
            self.tool_experiment_counts[tool_type] = 0
        
        if self.logger:
            self.logger.log(f"{self.name} 🧠 工具效果学习系统已初始化")
        
        # === 多步规划系统集成 ===
        # 多步规划状态管理
        self.current_plan = None  # 当前执行的多步计划
        self.current_plan_step = 0  # 当前计划执行到的步骤
        self.plan_execution_history = []  # 计划执行历史
        self.plan_failure_count = 0  # 计划失败次数
        self.last_plan_validation_turn = 0  # 上次计划验证的回合
        
        # 多步规划统计
        self.multi_step_stats = {
            'plans_created': 0,
            'plans_completed': 0,
            'plans_abandoned': 0,
            'average_plan_length': 0.0,
            'plan_success_rate': 0.0
        }
        
        if self.logger:
            self.logger.log(f"{self.name} 🗺️ 多步规划系统已初始化")

    def _select_ilai_action(self):
        """ILAI策略选择动物 - 优先使用V3增强决策"""
        # 首先尝试使用V3增强决策
        if self.five_library_system_active and self.five_library_system:
            try:
                # 获取当前游戏对象
                game = getattr(self, 'current_game', None)
                if not game:
                    # 如果没有存储的游戏对象,尝试从调用栈获取
                    import inspect
                    frame = inspect.currentframe()
                    try:
                        while frame:
                            if 'game' in frame.f_locals and hasattr(frame.f_locals['game'], 'players'):
                                game = frame.f_locals['game']
                                break
                            frame = frame.f_back
                    finally:
                        del frame
                
                if game:
                    v3_action = self._make_v3_enhanced_decision(game)
                    if v3_action and v3_action != self._get_default_exploration_action():
                        if logger:
                            logger.log(f"{self.name} 使用V3增强决策: {v3_action}")
                        return v3_action
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} V3增强决策失败,回退到传统ILAI: {str(e)}")
        
        # 回退使用传统ILAI决策逻辑
        try:
            x, y = self.current_pos
            # 检查水量不足时寻找水源
            if self.water < 30:
                water_sources = [resource for resource in self.game_map.resources if resource.type == "water"]
                if water_sources:
                    nearest_water = min(water_sources, key=lambda w: ((w.position[0] - x) ** 2 + (w.position[1] - y) ** 2) ** 0.5)
                    wx, wy = nearest_water.position
                    if (wx, wy) == (x, y):
                        return "drink"
                    elif abs(wx - x) > abs(wy - y):
                        return "right" if wx > x else "left"
                    else:
                        return "down" if wy > y else "up"
            
            # 检查食物不足时寻找食物
            if self.food < 30:
                food_sources = [resource for resource in self.game_map.resources if resource.type == "berry"]
                if food_sources:
                    nearest_food = min(food_sources, key=lambda f: ((f.position[0] - x) ** 2 + (f.position[1] - y) ** 2) ** 0.5)
                    fx, fy = nearest_food.position
                    if (fx, fy) == (x, y):
                        return "collect"
                    elif abs(fx - x) > abs(fy - y):
                        return "right" if fx > x else "left"
                    else:
                        return "down" if fy > y else "up"
            
            # 危险时躲避捕食者
            for predator in self.game_map.predators:
                px, py = predator.position
                distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                if distance < 3:  # 当捕食者距离小于3格时躲避
                    # 向远离捕食者的方向移动
                    if abs(px - x) > abs(py - y):
                        return "left" if px > x else "right"
                    else:
                        return "up" if py > y else "down"
            
            # 默认随机移动
            return random.choice(["up", "down", "left", "right"])
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ILAI决策失败: {str(e)}")
            # 完全失败时随机选择
            return random.choice(["up", "down", "left", "right"])

    def add_experience_to_direct_library(self, action, result, context=None):
        """添加EOCATR格式经验到五库系统"""
        if not self.five_library_system_active or not self.five_library_system:
            if logger:
                logger.log(f"{self.name} 五库系统未激活, active={getattr(self, 'five_library_system_active', False)}, system={getattr(self, 'five_library_system', None) is not None}")
            return
        
        try:
            from five_library_system import EOCATRExperience
            
            # 安全地获取并转换各个字段为字符串
            def safe_convert_to_string(value, default="unknown"):
                """安全地将任何值转换为字符串"""
                if value is None:
                    return default
                elif isinstance(value, dict):
                    # 如果是字典，尝试提取有意义的信息
                    if 'type' in value:
                        return str(value['type'])
                    elif 'name' in value:
                        return str(value['name'])
                    elif 'value' in value:
                        return str(value['value'])
                    else:
                        # 将字典转换为简化的键值对字符串
                        return "_".join([f"{k}_{v}" for k, v in value.items() if isinstance(v, (str, int, float, bool))][:3])
                elif isinstance(value, (list, tuple)):
                    # 如果是列表或元组，连接成字符串
                    return "_".join([str(item) for item in value if isinstance(item, (str, int, float, bool))][:3])
                else:
                    return str(value)
            
            # 构建完整EOCATR经验对象，确保所有字段都是字符串
            environment_raw = self._get_current_environment_detailed(context)
            object_raw = self._get_current_object_detailed(context)
            characteristics_raw = self._get_current_characteristics_detailed(context)
            tools_raw = self._get_current_tools_detailed(context)
            result_raw = self._enhance_result_detailed(result, action, context)
            
            experience = EOCATRExperience(
                environment=safe_convert_to_string(environment_raw, "开阔地"),
                object=safe_convert_to_string(object_raw, "未知"),
                characteristics=safe_convert_to_string(characteristics_raw, "正常"),
                action=safe_convert_to_string(action, "未知动作"),
                tools=safe_convert_to_string(tools_raw, "无"),
                result=safe_convert_to_string(result_raw, "未知结果"),
                player_id=str(self.name),
                timestamp=float(time.time()),
                success=self._evaluate_action_success(action, result, context),
                metadata={
                    'position': (int(self.x), int(self.y)),
                    'health': int(self.health),
                    'food': int(self.food),
                    'water': int(self.water),
                    'action_type': safe_convert_to_string(self._classify_action_type(action), "Other"),
                    'context_details': str(context) if context else "{}",
                    'decision_source': getattr(self, '_last_decision_source', 'unknown')
                }
            )
            
            # 添加到五库系统
            add_result = self.five_library_system.add_experience_to_direct_library(experience)
            
            if logger:
                # 显示完整的EOCATR格式经验（包含决策来源）
                decision_source = getattr(self, '_last_decision_source', 'unknown')
                eocatr_format = f"E:{experience.environment}, O:{experience.object}, C:{experience.characteristics}, A:{experience.action}, T:{experience.tools}, R:{experience.result}"
                logger.log(f"{self.name} 添加经验到五库系统 [{eocatr_format}] -> {add_result}")
                logger.log(f"{self.name} 🎯 决策来源: {decision_source}")
                if not add_result.get('success'):
                    logger.log(f"{self.name} 五库经验添加结果: {add_result}")
            
            # 🔧 修复：在经验添加后清理工具使用状态
            # 避免下次行动时仍然使用上次的工具记录
            if hasattr(self, 'current_selected_tool'):
                self.current_selected_tool = None
            if hasattr(self, '_last_used_tool'):
                self._last_used_tool = None
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 五库系统经验添加失败: {str(e)}")
                import traceback
                logger.log(f"   错误详情: {traceback.format_exc()}")

    def _make_v3_enhanced_decision(self, game):
        """使用统一决策系统的增强决策方法"""
        # 优先使用统一决策系统
        if hasattr(self, 'unified_decision_active') and self.unified_decision_active and hasattr(self, 'unified_decision_system'):
            try:
                # 构建EOCATR上下文
                current_context = {
                    'environment': self._get_current_environment_detailed(),
                    'object': self._get_current_object_detailed(),
                    'characteristics': self._get_current_characteristics_detailed(),
                    'player_id': self.name,
                    'urgency_level': self._calculate_urgency_level()
                }
                
                # 使用统一决策系统进行决策
                decision = self.unified_decision_system.make_decision(current_context)
                
                if decision and decision.recommended_action:
                    action = decision.recommended_action
                    confidence = decision.combined_confidence
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 统一决策系统建议: {action} (置信度: {confidence:.2f})")
                    
                    return action
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} 统一决策系统失败,回退到五库系统: {str(e)}")
        
        # 次优使用整合决策系统
        if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
            try:
                # 构建决策上下"""
                context = DecisionContext(
                    hp=self.hp,
                    food=self.food,
                    water=self.water,
                    position=(self.x, self.y),
                    day=getattr(game, 'current_day', 1),
                    environment=self._get_current_environment_type(game),
                    threats_nearby=len(self.detect_threats(game.game_map)) > 0,
                    resources_nearby=self._get_nearby_resources(game),
                    urgency_level=self._calculate_urgency_level()
                )
                
                # 使用整合决策系统进行决策
                decision_result = self.integrated_decision_system.make_integrated_decision(context, game)
                
                if decision_result.get('success') and decision_result.get('action'):
                    action = decision_result['action']
                    decision_source = decision_result.get('source', 'unknown')
                    confidence = decision_result.get('confidence', 0)
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 整合决策系统建议行动: {action} (来源: {decision_source}, 置信度: {confidence:.2f})")
                    
                    return action
                    
            except Exception as e:
                if self.logger:
                    self.logger.log(f"{self.name} 整合决策系统失败,回退到五库系统: {str(e)}")
        
        # 回退到原有的五库系统决策
        if not self.five_library_system_active or not self.five_library_system:
            return self._get_default_exploration_action()
        
        try:
            # 获取当前状态
            current_context = {
                'hp': self.hp,
                'food': self.food,
                'water': self.water,
                'position': (self.x, self.y),
                'day': getattr(game, 'current_day', 1)
            }
            
            # 从五库系统获取决策支"
            decision_result = self.five_library_system.generate_decision_from_context(
                context=current_context, 
                source='hybrid'
            )
            
            # 基于五库系统的决策进行行"
            if decision_result.get('success') and decision_result.get('decision'):
                decision = decision_result['decision']
                action = decision.action
                confidence = decision_result.get('confidence', 0)
                decision_id = decision_result.get('decision_id')
                
                if self.logger:
                    self.logger.log(f"{self.name} 五库系统建议行动: {action} (置信度: {confidence:.2f})")
                
                # 记录决策前状态
                pre_decision_state = {
                    'hp': self.hp,
                    'food': self.food, 
                    'water': self.water,
                    'position': (self.x, self.y)
                }
                
                # 执行行动并记录结"
                executed_action = action
                
                # 简化的决策成功性评估(基于生存指标变化"
                try:
                    # 模拟执行后的状态评"
                    decision_success = self._evaluate_decision_success_simple(action, current_context)
                    
                    # 更新决策库反"
                    if decision_id:
                        feedback_result = self.five_library_system.update_decision_feedback(
                            decision_id=decision_id,
                            success=decision_success,
                            result=f"行动:{action}, 上下从hp={self.hp},food={self.food},water={self.water}"
                        )
                        
                        if self.logger and feedback_result.get('success'):
                            self.logger.log(f"{self.name} 决策反馈已更新: {decision_id[:8]}... 成功:{decision_success}")
                
                except Exception as feedback_error:
                    if self.logger:
                        self.logger.log(f"{self.name} 决策反馈更新失败: {str(feedback_error)}")
                
                return executed_action
            
            # 如果没有建议,使用默认探"
            return self._get_default_exploration_action()
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 五库系统决策失败: {str(e)}")
            return self._get_default_exploration_action()
    
    def _get_nearby_resources(self, game):
        """获取附近的资源列表"""
        try:
            resources = []
            # 检查附近的植物
            for plant in game.game_map.plants:
                distance = max(abs(self.x - plant.x), abs(self.y - plant.y))
                if distance <= 3:  # 3格范围内
                    resources.append(plant.__class__.__name__)
            return resources
        except:
            return []
    
    def _calculate_urgency_level(self):
        """计算紧急程度(0.0-1.0)"""
        try:
            # 基于生存指标计算紧急程度
            hp_urgency = max(0, (50 - self.hp) / 50)  # 血量越低越紧急
            food_urgency = max(0, (30 - self.food) / 30)  # 食物越少越紧急
            water_urgency = max(0, (30 - self.water) / 30)  # 水越少越紧急
            # 取最高紧急程度
            return max(hp_urgency, food_urgency, water_urgency)
        except:
            return 0.5  # 默认中等紧急程度
    def _evaluate_decision_success_simple(self, action, context):
        """简化的决策成功性评估"""
        try:
            # 基于行动类型和当前状态的简单评估
            if 'collect' in action.lower() or '收集' in action:
                # 收集行动:如果食物或水较低,认为是好决策
                return context.get('food', 50) < 70 or context.get('water', 50) < 70
            
            elif 'explore' in action.lower() or '探索' in action:
                # 探索行动:如果生存指标较好,认为是好决策
                return context.get('hp', 50) > 30 and context.get('food', 50) > 20
            
            elif 'drink' in action.lower() or '喝水' in action:
                # 喝水行动:如果水分较低,认为是好决策
                return context.get('water', 50) < 50
            
            elif 'rest' in action.lower() or '休息' in action:
                # 休息行动:如果血量较低,认为是好决策
                return context.get('hp', 50) < 60
            
            else:
                # 其他行动:默认50%成功
                import random
                return random.random() > 0.5
                
        except Exception as e:
            # 评估失败时默认为成功
            return True

    def enable_reinforcement_learning(self):
        """启用强化学习组件"""
        # 检查是否已经完全初始化（标志为True且网络已存在）
        if (self.use_reinforcement_learning and 
            self.q_network is not None and 
            self.target_network is not None):
            return True  # 已经完全初始化，返回True
            
        try:
            self.logger.log(f"{self.name} 启用强化学习组件")
            self.use_reinforcement_learning = True
            self.player_type = "RILAI"  # 修改玩家类型
            
            # 初始化网络
            network_init_result = self.initialize_networks()
            if not network_init_result:
                raise Exception("神经网络初始化失败")
            
            # 尝试从磁盘加载已有模型
            self._load_model()
            
            self.logger.log(f"{self.name} 强化学习组件启用成功")
            return True
        except Exception as e:
            import traceback
            self.logger.log(f"{self.name} 启用强化学习组件失败: {str(e)}")
            self.logger.log(traceback.format_exc())
            self.use_reinforcement_learning = False
            self.q_network = None
            self.target_network = None
            return False

    # === 增强间接经验库功从===
    
    def build_network(self):
        """构建神经网络（RILAI强化学习部分）"""
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            
            model = Sequential()
            # 增加模型复杂度，添加Dropout以避免过拟合
            model.add(Dense(128, input_dim=self.state_size, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(128, activation='relu'))
            model.add(Dense(self.num_actions, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
            return model
        except Exception as e:
            import traceback
            self.logger.log(f"{self.name} 构建神经网络失败: {str(e)}")
            self.logger.log(traceback.format_exc())
            return None

    def initialize_networks(self):
        """初始化Q网络和目标网络"""
        if self.q_network is not None and self.target_network is not None:
            return True  # 已初始化
            
        try:
            self.logger.log(f"{self.name} 初始化神经网络...")
            
            # 创建Q网络
            self.q_network = self.build_network()
            if self.q_network is None:
                raise Exception("Q网络创建失败")
            
            # 创建目标网络
            self.target_network = self.build_network()
            if self.target_network is None:
                raise Exception("目标网络创建失败")
            
            # 复制Q网络权重到目标网络
            self.target_network.set_weights(self.q_network.get_weights())
            
            self.logger.log(f"{self.name} 神经网络初始化成功")
            return True
        except Exception as e:
            import traceback
            self.logger.log(f"{self.name} 神经网络初始化失败: {str(e)}")
            self.logger.log(traceback.format_exc())
            self.q_network = None
            self.target_network = None
            return False

    def select_action(self, state):
        """使用 epsilon-greedy 策略选择动作（RILAI强化学习部分）"""
        try:
            # 确保网络已初始化
            if self.q_network is None:
                self.logger.log(f"{self.name} Q网络未初始化,尝试初始化...")
                if not self.initialize_networks():
                    self.logger.log(f"{self.name} 无法初始化网络,回退到ILAI策略")
                    return self._select_ilai_action()
            
            # 以epsilon的概率随机选择动作
            if np.random.rand() <= self.epsilon:
                action_idx = random.randrange(self.num_actions)
                self.logger.log(f"{self.name} RL探索:随机选择动作 {self.actions[action_idx]}")
                return self.actions[action_idx]
            
            # 否则选择Q值最大的动作
            act_values = self.q_network.predict(state.reshape(1, -1), verbose=0)
            action_idx = np.argmax(act_values[0])
            self.logger.log(f"{self.name} RL利用:选择Q值最大的动作 {self.actions[action_idx]}")
            return self.actions[action_idx]
        except Exception as e:
            import traceback
            self.logger.log(f"{self.name} RL选择动作失败: {str(e)}")
            self.logger.log(traceback.format_exc())
            self.logger.log(f"{self.name} 回退到ILAI策略")
            return self._select_ilai_action()
    
    def initialize_social_learning(self):
        """初始化社交学习机制"""
        # 信任网络:记录对其他智能体的信任度
        self.trust_network = {}  # {agent_name: trust_score}
        
        # 社交学习配置
        self.social_learning_config = {
            'communication_range': 5,  # 通信范围
            'min_trust_threshold': 0.3,  # 接受信息的最低信任阈值
            'experience_share_probability': 0.3,  # 分享经验的概率
            'trust_decay_rate': 0.98,  # 信任度衰减率
            'max_shared_experiences': 3,  # 每次最多分享的经验数
        }
        
        # 间接经验质量跟踪
        self.indirect_experience_quality = {}  # {experience_id: quality_metrics}
        
        # 社交学习统计
        self.social_learning_stats = {
            'experiences_shared': 0,
            'experiences_received': 0,
            'trust_updates': 0,
            'successful_applications': 0,
            'failed_applications': 0
        }
        
        if self.logger:
            self.logger.log(f"{self.name} 社交学习机制初始化完成")

    def find_nearby_learners(self, game):
        """寻找附近的学习型智能体(ILAI/RILAI)"""
        if not hasattr(self, 'current_pos'):
            return []
            
        nearby_learners = []
        communication_range = self.social_learning_config['communication_range']
        
        for player in game.players:
            if (player != self and 
                player.is_alive() and 
                hasattr(player, 'indirect_experience_base') and  # 确保是学习型智能体
                                    (isinstance(player, ILAIPlayer) or player.player_type in ["ILAI", "RILAI"])):
                
                # 计算距离
                if hasattr(player, 'current_pos'):
                    distance = max(abs(self.current_pos[0] - player.current_pos[0]),
                                 abs(self.current_pos[1] - player.current_pos[1]))
                    
                    if distance <= communication_range:
                        nearby_learners.append((player, distance))
        
        # 按距离排序,优先与近距离智能体交互
        nearby_learners.sort(key=lambda x: x[1])
        return [player for player, _ in nearby_learners]

    def select_experiences_to_share(self):
        """选择有价值的经验进行分享"""
        experiences_to_share = []
        max_share = self.social_learning_config['max_shared_experiences']
        
        # 从直接经验库中选择高价值经验
        if self.direct_experience_base:
            # 计算每个经验的分享价值
            scored_experiences = []
            for exp in self.direct_experience_base[-20:]:  # 只考虑最近的20个经验
                score = self._calculate_experience_share_value(exp)
                if score > 0.5:  # 只分享高价值经验
                    scored_experiences.append((exp, score))
            
            # 按分享价值排序
            scored_experiences.sort(key=lambda x: x[1], reverse=True)
            
            # 选择前N个经验分享
            for exp, score in scored_experiences[:max_share]:
                exp_to_share = exp.copy()
                exp_to_share['share_value'] = score
                exp_to_share['source'] = self.name
                exp_to_share['timestamp'] = len(self.direct_experience_base)
                experiences_to_share.append(exp_to_share)
        
        return experiences_to_share

    def _calculate_experience_share_value(self, experience):
        """计算经验的分享价值"""
        base_value = 0.0
        
        # 成功经验更有价值
        if experience.get('result', {}).get('success', False):
            base_value += 0.4
        
        # 稀有经验(很少遇到的情况)更有价值
        object_type = experience.get('object', '')
        action_type = experience.get('action', '')
        
        # 计算该类型经验的稀有度
        similar_count = sum(1 for exp in self.direct_experience_base 
                          if exp.get('object') == object_type and exp.get('action') == action_type)
        
        if similar_count <= 3:  # 稀有经"
            base_value += 0.3
        elif similar_count <= 10:  # 较稀有经验
            base_value += 0.2
        
        # 近期经验更有价值
        recent_bonus = 0.1 if experience.get('timestamp', 0) > len(self.direct_experience_base) - 10 else 0
        base_value += recent_bonus
        
        # 涉及危险情况的经验更有价值
        if 'danger' in str(experience.get('context', '')).lower():
            base_value += 0.2
        
        return min(base_value, 1.0)  # 最大值为1.0

    def share_information_with(self, nearby_learners):
        """与附近的学习型智能体分享信息"""
        if not nearby_learners:
            return
        
        # 🚀 性能优化：知识分享频率控制
        if not hasattr(self, 'last_knowledge_share_round'):
            self.last_knowledge_share_round = 0
        if not hasattr(self, 'knowledge_share_count_this_round'):
            self.knowledge_share_count_this_round = 0
        
        current_round = getattr(self, 'current_round', 1)
        
        # 重置每回合的分享计数
        if current_round != self.last_knowledge_share_round:
            self.knowledge_share_count_this_round = 0
            self.last_knowledge_share_round = current_round
        
        # 每5回合才允许分享，每回合最多2次
        if current_round % 5 != 0 or self.knowledge_share_count_this_round >= 2:
            return
        
        self.knowledge_share_count_this_round += 1
        
        # 检查是否应该分享信息
        import random
        if random.random() > self.social_learning_config['experience_share_probability']:
            return
        
        experiences_to_share = self.select_experiences_to_share()
        if not experiences_to_share:
            return
        
        shared_count = 0
        for learner in nearby_learners:
            if shared_count >= len(experiences_to_share):
                break
                
            # 选择与该智能体分享的经验
            for experience in experiences_to_share:
                if hasattr(learner, 'receive_information'):
                    learner.receive_information(self, experience)
                    shared_count += 1
                    
                    # 修复:使用全局logger而不是self.logger
                    if logger:
                        logger.log(f"{self.name} 从{learner.name} 分享经验: {experience.get('object', '')}+{experience.get('action', '')}")
        
        # 更新统计
        self.social_learning_stats['experiences_shared'] += shared_count
        
        # 🔧 修复：记录信息分享统计
        if shared_count > 0:
            self._record_info_sharing(shared_count)
            
            # 知识分享统计已在方法开头更新

    def receive_information(self, sender, information):
        """接收其他智能体分享的信息"""
        # 确保发送者是学习型智能体
        if not (isinstance(sender, ILAIPlayer) or sender.player_type in ["ILAI", "RILAI"]):
            return
        
        # 评估信息可信度
        credibility = self._evaluate_information_credibility(sender, information)
        
        # 如果可信度足够高,添加到间接经验库
        min_trust = self.social_learning_config['min_trust_threshold']
        if credibility >= min_trust:
            # 添加发送者和可信度信息
            enhanced_info = information.copy()
            enhanced_info['source'] = sender.name
            enhanced_info['credibility'] = credibility
            enhanced_info['received_timestamp'] = len(self.indirect_experience_base)
            enhanced_info['verification_status'] = 'pending'
            
            # 检查重复
            if not self._is_duplicate_information(enhanced_info):
                self.indirect_experience_base.append(enhanced_info)
                
                # 限制间接经验库大小
                if len(self.indirect_experience_base) > 200:
                    # 移除最旧的低可信度经验
                    self.indirect_experience_base.sort(key=lambda x: (x.get('credibility', 0), x.get('received_timestamp', 0)))
                    self.indirect_experience_base = self.indirect_experience_base[50:]  # 保留高质量的150个经验
                # 更新统计
                self.social_learning_stats['experiences_received'] += 1
                
                # 修复:使用全局logger而不是self.logger
                if logger:
                    logger.log(f"{self.name} 接受来自 {sender.name} 的经验,可信度: {credibility:.2f}")
            
            # 更新对发送者的信任度
            self._update_trust_score(sender.name, credibility)

    def _evaluate_information_credibility(self, sender, information):
        """评估接收信息的可信度"""
        base_credibility = 0.5  # 基础可信度
        # 基于历史信任度
        trust_score = self.trust_network.get(sender.name, 0.5)
        base_credibility = 0.3 * base_credibility + 0.7 * trust_score
        
        # 基于发送者的生存表现
        if hasattr(sender, 'health') and hasattr(sender, 'food') and hasattr(sender, 'water'):
            survival_score = (sender.health + sender.food + sender.water) / 300.0  # 假设最大值各个00
            base_credibility += 0.1 * survival_score
        
        # 基于信息内容的合理"
        content_credibility = self._assess_information_content(information)
        base_credibility = 0.7 * base_credibility + 0.3 * content_credibility
        
        # 基于信息的具体程度(越具体可信度越高"
        if information.get('context') and information.get('result'):
            base_credibility += 0.1
        
        return max(0.0, min(1.0, base_credibility))

    def _assess_information_content(self, information):
        """评估信息内容的合理性"""
        credibility = 0.5
        
        # 检查信息结构完整"""
        required_fields = ['object', 'action', 'context', 'result']
        present_fields = sum(1 for field in required_fields if field in information)
        credibility += 0.1 * (present_fields / len(required_fields))
        
        # 检查结果的合理"
        result = information.get('result', {})
        if isinstance(result, dict):
            # 成功率不应该异常"
            if result.get('success') and information.get('share_value', 0) < 0.9:
                credibility += 0.1
            
            # 检查数值的合理"
            health_change = result.get('health_change', 0)
            if -50 <= health_change <= 50:  # 合理的健康变化范"
                credibility += 0.1
        
        return max(0.0, min(1.0, credibility))

    def _is_duplicate_information(self, new_info):
        """检查是否为重复信息"""
        for existing_info in self.indirect_experience_base:
            if (existing_info.get('object') == new_info.get('object') and
                existing_info.get('action') == new_info.get('action') and
                existing_info.get('source') == new_info.get('source')):
                
                # 如果新信息可信度更高,允许更"""
                if new_info.get('credibility', 0) > existing_info.get('credibility', 0):
                    self.indirect_experience_base.remove(existing_info)
                    return False
                return True
        return False

    def _update_trust_score(self, agent_name, interaction_result):
        """更新对特定智能体的信任度"""
        current_trust = self.trust_network.get(agent_name, 0.5)
        
        # 基于交互结果调整信任度
        if interaction_result > 0.7:
            # 高质量信息,增加信任
            new_trust = current_trust + 0.1 * (1.0 - current_trust)
        elif interaction_result > 0.5:
            # 中等质量信息,小幅增加信"""
            new_trust = current_trust + 0.05 * (1.0 - current_trust)
        else:
            # 低质量信息,降低信任
            new_trust = current_trust * 0.9
        
        self.trust_network[agent_name] = max(0.1, min(1.0, new_trust))
        self.social_learning_stats['trust_updates'] += 1

    def decay_trust_scores(self):
        """定期衰减信任度(模拟时间对信任的影响)"""
        decay_rate = self.social_learning_config['trust_decay_rate']
        for agent_name in self.trust_network:
            self.trust_network[agent_name] *= decay_rate
            self.trust_network[agent_name] = max(0.1, self.trust_network[agent_name])

    def get_relevant_indirect_experiences(self, context_filter=None, min_credibility=0.6):
        """获取相关的间接经验"""
        relevant_experiences = []
        
        for exp in self.indirect_experience_base:
            # 检查可信度
            if exp.get('credibility', 0) < min_credibility:
                continue
            
            # 检查上下文匹配
            if context_filter:
                if not self._matches_context(exp, context_filter):
                    continue
            
            relevant_experiences.append(exp)
        
        # 按可信度和时间排"""
        relevant_experiences.sort(
            key=lambda x: (x.get('credibility', 0), x.get('received_timestamp', 0)),
            reverse=True
        )
        
        return relevant_experiences

    def _matches_context(self, experience, context_filter):
        """检查经验是否匹配给定上下文"""
        exp_context = experience.get('context', {})
        
        if isinstance(context_filter, dict) and isinstance(exp_context, dict):
            # 检查关键字段匹"""
            for key, value in context_filter.items():
                if key in exp_context and exp_context[key] != value:
                    return False
            return True
        
        # 简单字符串匹配
        return str(context_filter).lower() in str(exp_context).lower()

    def integrate_indirect_experiences_in_decision(self, current_context):
        """在决策过程中整合间接经验"""
        if not self.indirect_experience_base:
            return {}
        
        # 获取相关的间接经"""
        relevant_experiences = self.get_relevant_indirect_experiences(current_context)
        
        if not relevant_experiences:
            return {}
        
        # 统计间接经验的行动偏"
        action_preferences = {}
        total_weight = 0
        
        for exp in relevant_experiences[:10]:  # 只考虑个0个最相关的经"
            action = exp.get('action', '')
            credibility = exp.get('credibility', 0)
            success = exp.get('result', {}).get('success', False)
            
            # 计算权重(可信度 × 成功率)
            weight = credibility * (1.5 if success else 0.5)
            
            if action in action_preferences:
                action_preferences[action] += weight
            else:
                action_preferences[action] = weight
            
            total_weight += weight
        
        # 归一化权"
        if total_weight > 0:
            for action in action_preferences:
                action_preferences[action] /= total_weight
        
        return action_preferences

    def perform_social_learning_update(self, game):
        """执行社交学习更新(每回合调用)"""
        if not hasattr(self, 'trust_network'):
            self.initialize_social_learning()
        
        # 寻找附近的学习型智能体
        nearby_learners = self.find_nearby_learners(game)
        
        # 分享信息
        if nearby_learners:
            self.share_information_with(nearby_learners)
        
        # 定期衰减信任度
        if len(self.direct_experience_base) % 10 == 0:  # 每10个经验周期执行一次
            self.decay_trust_scores()

    def get_social_learning_statistics(self):
        """获取社交学习统计信息"""
        if not hasattr(self, 'social_learning_stats'):
            return {}
        
        stats = self.social_learning_stats.copy()
        stats['indirect_experience_count'] = len(self.indirect_experience_base)
        stats['trust_network_size'] = len(getattr(self, 'trust_network', {}))
        stats['average_trust'] = sum(self.trust_network.values()) / len(self.trust_network) if self.trust_network else 0
        
        return stats
            
    # === 原有方法继续 ===

    def update_phase(self, current_day):
        if current_day <= 20:
            self.phase = "初期"
        elif current_day <= 80:
            self.phase = "中期"
        else:
            self.phase = "后期"

    def act(self):
        """执行动物:混合决策机制,结合RL和规则方法"""
        try:
            # 记录旧位置
            if hasattr(self, 'current_pos'):
                self.last_pos = self.current_pos
            
            # 初始化探索地图(如果不存在)
            if not hasattr(self, 'exploration_map'):
                self.exploration_map = set()
                if hasattr(self, 'current_pos'):
                    self.exploration_map.add(self.current_pos)
            
            # 如果是RILAI玩家且RL组件已启用
            if self.player_type == "RILAI" and self.use_reinforcement_learning:
                # 检查危险状态,决定是否使用ILAI逻辑
                danger_situation = self._check_danger_situation()
                
                if danger_situation:
                    logger.log(f"{self.name} 检测到危险情况,使用ILAI策略")
                    action = self._select_ilai_action()
                    logger.log(f"{self.name} ILAI选择动物: {action}")
                    # 标记决策来源为ILAI
                    self._last_decision_source = "ilai_danger_response"
                else:
                    # 使用RL策略
                    try:
                        # 获取当前状态
                        state = self.get_state()
                        # 选择动物
                        action = self.select_action(state)
                        logger.log(f"{self.name} RL选择动物: {action}")
                        # 标记决策来源为强化学习
                        self._last_decision_source = "reinforcement_learning"
                    except Exception as e:
                        logger.log(f"{self.name} RL行为执行失败: {str(e)}")
                        # 回退到ILAI策略
                        action = self._select_ilai_action()
                        logger.log(f"{self.name} 回退到ILAI,选择动物: {action}")
                        # 标记决策来源为ILAI回退
                        self._last_decision_source = "ilai_fallback"
                
                # 执行选定的动物
                self._execute_action(action)
                
                # 获取新状态和奖励
                next_state = self.get_state()
                reward = self.calculate_reward(action)
                
                # 判断是否游戏结束
                done = self.health <= 0
                
                # 如果上一个状态存在,存储经验
                if hasattr(self, 'last_state') and self.last_state is not None:
                    self.remember(self.last_state, self.last_action, self.last_reward, state, False)
                
                # 更新状态
                self.last_state = state
                self.last_action = action
                self.last_reward = reward
                
                # 训练模型
                if self.step_counter % self.train_frequency == 0:
                    self.replay()
            else:
                # 纯ILAI玩家使用原始策略
                action = self._select_ilai_action()
                # 标记决策来源为ILAI
                self._last_decision_source = "ilai_standard"
                self._execute_action(action)
        except Exception as e:
            import traceback
            logger.log(f"{self.name} 行动失败: {str(e)}")
            logger.log(traceback.format_exc())
            # 应急行动:随机移动
            self._execute_random_move()
    
    def _check_danger_situation(self):
        """检查是否处于危险情况(应该使用ILAI决策)"""
        try:
            # 检查健康状态
            health_danger = self.health < 30
            
            # 检查资源状态
            water_danger = self.water < 20
            food_danger = self.food < 20
            
            # 检查周围是否有捕食者
            predator_danger = False
            if hasattr(self, 'current_pos'):
                x, y = self.current_pos
                for predator in self.game_map.predators:
                    px, py = predator.position
                    distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                    if distance < 3:  # 3格以内有捕食者视为危"""
                        predator_danger = True
                        break
            
            # 任何一项危险都使用ILAI
            return health_danger or water_danger or food_danger or predator_danger
        except Exception as e:
            logger.log(f"{self.name} 检查危险状态失败: {str(e)}")
            return True  # 出错时保守处理为危险
    
    def _execute_action(self, action):
        """执行指定的动物"""
        # 记录行动前状态
        pre_action_state = {
            'health': self.health,
            'food': self.food,
            'water': self.water,
            'position': (self.x, self.y)
        }
        
        action_success = False
        
        try:
            if action == "up":
                old_y = self.y
                self.move_up()
                action_success = (self.y != old_y)
            elif action == "down":
                old_y = self.y
                self.move_down()
                action_success = (self.y != old_y)
            elif action == "left":
                old_x = self.x
                self.move_left()
                action_success = (self.x != old_x)
            elif action == "right":
                old_x = self.x
                self.move_right()
                action_success = (self.x != old_x)
            elif action == "drink":
                old_water = self.water
                self.drink_water()
                action_success = (self.water > old_water)
            elif action == "collect":
                # 使用新的主动采集植物方法
                action_success = self.action_collect_plant(game)
            elif action == "attack":
                # 优先攻击动物，其次攻击敌对玩家
                action_success = self.action_attack_animal(game)
                
                # 如果没有找到动物，尝试攻击敌对玩家
                if not action_success and hasattr(self, 'current_pos'):
                    x, y = self.current_pos
                    enemy = None
                    min_dist = float('inf')
                    
                    for player in getattr(self.game_map, 'players', []):
                        if player != self and self.check_is_enemy(player):
                            if hasattr(player, 'current_pos') and player.current_pos is not None:
                                px, py = player.current_pos
                                dist = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                                if dist < min_dist and dist <= 1:  # 只攻击相邻格子的敌人
                                    min_dist = dist
                                    enemy = player
                    
                    if enemy is not None:
                        old_enemy_health = enemy.health if hasattr(enemy, 'health') else 100
                        self.attack_player(enemy)
                        new_enemy_health = enemy.health if hasattr(enemy, 'health') else 100
                        action_success = (new_enemy_health < old_enemy_health)
            else:
                # 未知动物,随机移动
                self._execute_random_move()
                action_success = False
                
        except Exception as e:
            logger.log(f"{self.name} 执行动物 {action} 失败: {str(e)}")
            # 应急行动:随机移动
            self._execute_random_move()
            action_success = False
        
        # === 2.0.0版本新增:记录EOCATR经验到BPM系统 ===
        try:
            # 记录行动后状态
            post_action_state = {
                'health': self.health,
                'food': self.food,
                'water': self.water,
                'position': (self.x, self.y)
            }
            
            # 计算行动结果
            result = {
                'success': action_success,
                'health_change': post_action_state['health'] - pre_action_state['health'],
                'food_change': post_action_state['food'] - pre_action_state['food'],
                'water_change': post_action_state['water'] - pre_action_state['water'],
                'position_change': (
                    post_action_state['position'][0] - pre_action_state['position'][0],
                    post_action_state['position'][1] - pre_action_state['position'][1]
                )
            }
            
            # 添加EOCATR经验（包含决策来源标识）
            decision_source = getattr(self, '_last_decision_source', 'action_execution')
            self.add_eocar_experience(action, result, source=decision_source)
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 记录EOCATR经验失败: {str(e)}")
    
    def _execute_random_move(self):
        """执行随机移动(应急策略)"""
        try:
            move_action = random.choice(["up", "down", "left", "right"])
            if move_action == "up":
                self.move_up()
            elif move_action == "down":
                self.move_down()
            elif move_action == "left":
                self.move_left()
            elif move_action == "right":
                self.move_right()
        except Exception as e:
            logger.log(f"{self.name} 随机移动也失败了: {str(e)}")
            # 实在没办法了,放弃本回合行动
            pass
    
    def move_up(self):
        """向上移动"""
        old_pos = (self.x, self.y)
        # 使用存储的game_map引用,如果没有则尝试从已知位置推断
        if hasattr(self, 'game_map') and self.game_map:
            success = self.move(0, -1, self.game_map)
        else:
            # 直接更新位置,不进行边界检查(兜底策略)
            self.y = max(0, self.y - 1)
            success = True
        
        # 更新位置跟踪
        if success and (self.x, self.y) != old_pos:
            self.last_pos = old_pos
            self.current_pos = (self.x, self.y)
            if hasattr(self, 'visited_positions'):
                self.visited_positions.add(self.current_pos)
    
    def move_down(self):
        """向下移动"""
        old_pos = (self.x, self.y)
        if hasattr(self, 'game_map') and self.game_map:
            success = self.move(0, 1, self.game_map)
        else:
            self.y = self.y + 1
            success = True
        
        # 更新位置跟踪
        if success and (self.x, self.y) != old_pos:
            self.last_pos = old_pos
            self.current_pos = (self.x, self.y)
            if hasattr(self, 'visited_positions'):
                self.visited_positions.add(self.current_pos)
    
    def move_left(self):
        """向左移动"""
        old_pos = (self.x, self.y)
        if hasattr(self, 'game_map') and self.game_map:
            success = self.move(-1, 0, self.game_map)
        else:
            self.x = max(0, self.x - 1)
            success = True
        
        # 更新位置跟踪
        if success and (self.x, self.y) != old_pos:
            self.last_pos = old_pos
            self.current_pos = (self.x, self.y)
            if hasattr(self, 'visited_positions'):
                self.visited_positions.add(self.current_pos)
    
    def move_right(self):
        """向右移动"""
        old_pos = (self.x, self.y)
        if hasattr(self, 'game_map') and self.game_map:
            success = self.move(1, 0, self.game_map)
        else:
            self.x = self.x + 1
            success = True
        
        # 更新位置跟踪
        if success and (self.x, self.y) != old_pos:
            self.last_pos = old_pos
            self.current_pos = (self.x, self.y)
            if hasattr(self, 'visited_positions'):
                self.visited_positions.add(self.current_pos)
    
    def check_is_enemy(self, player):
        """判断另一个玩家是否是敌人"""
        # 简单实现:信誉低于30的视为敌人
        return player.reputation < 30

    def collect_food(self):
        """兼容性方法：采集食物（已弃用，使用action_collect_plant代替）"""
        logger.log(f"{self.name} attempts to use deprecated collect_food method")
        pass

    def drink_water(self):
        """喝水方法"""
        # 检查当前位置是否有水源
        if hasattr(self, 'game_map') and self.game_map:
            current_cell = self.game_map.grid[self.y][self.x]
            if current_cell in ["river", "puddle"]:
                old_water = self.water
                self.water = min(100, self.water + 30)
                return self.water > old_water
        return False

    def take_turn(self, game):
        """优化的ILAI决策流程 - 资源适应性决策"""
        if not self.is_alive():
            return
        
        # === 多步规划执行逻辑 ===
        # 优先检查是否有正在执行的计划
        if self.current_plan is not None:
            if logger:
                logger.log(f"{self.name} 🗺️ 继续执行多步计划 (步骤 {self.current_plan_step + 1}/{len(self.current_plan.get('steps', []))})")
            
            plan_result = self._execute_next_plan_step(game)
            if plan_result['status'] == 'completed':
                if logger:
                    logger.log(f"{self.name} ✅ 多步计划执行完成")
                self.multi_step_stats['plans_completed'] += 1
                self._reset_plan_state()
                return  # 计划完成，结束本回合
            elif plan_result['status'] == 'failed':
                if logger:
                    logger.log(f"{self.name} ❌ 多步计划执行失败: {plan_result['reason']}")
                self.multi_step_stats['plans_abandoned'] += 1
                self._reset_plan_state()
                # 继续执行正常决策流程
            elif plan_result['status'] == 'continue':
                if logger:
                    logger.log(f"{self.name} ⏭️ 多步计划步骤执行成功，等待下回合继续")
                return  # 本步骤成功，等待下回合
        
        # 检查计划是否仍然有效（环境变化检测）
        if self.current_plan is not None and not self._is_plan_still_valid(game):
            if logger:
                logger.log(f"{self.name} ⚠️ 当前计划已失效，重新规划")
            self.multi_step_stats['plans_abandoned'] += 1
            self._reset_plan_state()
        
        # 🔧 修复：首先执行基础Player行为，包括地形探索记录
        try:
            # 每回合消耗
            self.food = max(0, self.food - 1)
            self.water = max(0, self.water - 1)
            
            # 检查当前格子地形并记录探索
            current_cell = game.game_map.grid[self.y][self.x]
            self._record_exploration(current_cell)
            
            # 检查水源，自动喝水
            if current_cell in ["river", "puddle"]:
                old_water = self.water
                self.water = min(100, self.water + 30)
                if self.water > old_water and logger:
                    logger.log(f"{self.name} drinks water at {current_cell}")
            
            # 如果食物或水分为0,减少生命值
            if self.food == 0 or self.water == 0:
                self.hp = max(0, self.hp - 10)
                
            # 检查是否死亡
            if self.hp <= 0:
                self.alive = False
                if logger:
                    logger.log(f"{self.name} 死亡")
                return
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 基础生存检查异常: {str(e)}")
        
        # === 第一步:判断自身状态===
        self_state = self._analyze_current_state(game)
        
        # 性能优化：减少状态日志频率
        if logger and self.life_experience_count % 5 == 0:  # 每5回合记录一次状态
            logger.log(f"{self.name} 🔍 状态评估: {self_state['status']} | 健康:{self.health} 食物:{self.food} 水:{self.water}")
        
        try:
            # 更新发育阶段
            self.life_experience_count += 1
            self.developmental_stage = min(1.0, self.life_experience_count / 100.0)
            
            # === 第二步:三阶段决策触发机制 ===
            decision_stage = self._determine_decision_stage(game)
            
            if logger:
                logger.log(f"{self.name} 🎯 决策阶段: {decision_stage['stage']} | 原因: {decision_stage['reason']}")
            
            if decision_stage['stage'] == 'instinct':
                # 阶段一: 本能决策阶段 - 直接响应紧急情况
                if logger:
                    logger.log(f"{self.name} ⚡ 本能层激活: {decision_stage['trigger_reason']}")
                
                instinct_action = self._execute_instinct_decision(game, decision_stage['trigger_type'])
                if instinct_action:
                    return  # 本能决策完成，直接返回
                    
            elif decision_stage['stage'] == 'dmha':
                # 阶段二: DMHA决策阶段 - 目标导向决策
                if logger:
                    logger.log(f"{self.name} 🎯 DMHA层激活: 进入目标导向决策模式")
                    
            elif decision_stage['stage'] == 'cdl':
                # 阶段三: CDL决策阶段 - 好奇心驱动探索
                if logger:
                    logger.log(f"{self.name} 🧠 CDL层激活: 启动好奇心驱动探索")
                
                action_result = self._enhanced_cdl_exploration_with_tools(game) or self._execute_cdl_exploration_cycle(game)
                if action_result and action_result.get('action_taken'):
                    return  # CDL成功执行，完成回合
            
            # 如果CDL未执行或失败，继续执行目标导向决策
            if logger:
                logger.log(f"{self.name} 🎯 进入目标导向决策模式")
            
            # === 第三步:三阶段协同目标确定 ===
            # 🔧 第2步修复：使用新的三阶段目标确定机制
            target_goal = self._collaborative_goal_determination(game, decision_stage, self_state)
            
            if logger:
                stage_name = {"instinct": "本能", "dmha": "DMHA", "cdl": "CDL"}[decision_stage['stage']]
                logger.log(f"{self.name} 🎯 {stage_name}层确定目标: {target_goal['type']} (紧急度: {target_goal['urgency']:.2f})")
            
            # === 第四步:决策库匹从===
            # 🔧 修复：初始化action_to_execute变量
            action_to_execute = None
            decision_source = "未确定"
            
            decision_match = self._decision_library_matching(target_goal, game)
            
            if decision_match and decision_match.get('success'):
                if logger:
                    logger.log(f"{self.name} 📚 决策库匹配成功: {decision_match['action']} (匹配度: {decision_match['confidence']:.2f})")
                action_to_execute = decision_match['action']
                decision_source = "决策库匹配"
            else:
                # === 第四点五步:🔧 第4步修复：长链机制执行管理===
                # 长链机制专注于决策方案实施管理，不制定新目标
                long_chain_result = self._long_chain_execution_management(game, target_goal, logger)
                if long_chain_result and long_chain_result.get('action'):
                    action_to_execute = long_chain_result['action']
                    decision_source = long_chain_result.get('source', '长链执行管理')
                    if logger:
                        status = long_chain_result.get('status', 'unknown')
                        logger.log(f"{self.name} 🗓️ 长链执行管理: {status} - 执行 {action_to_execute}")
                
                # === 第五步:WBM机制生成新决策===
                if action_to_execute is None:
                    if logger:
                        logger.log(f"{self.name} 🌉 决策库无匹配,启动WBM规律决策机制")
                    
                    wbm_decision = self._wbm_rule_based_decision(target_goal, game, logger)
                    if wbm_decision and wbm_decision.get('action'):
                        action_to_execute = wbm_decision['action']
                        decision_source = "WBM规律决策"
                        if 'multi_day_plan' in wbm_decision:
                            decision_source = "WBM长链决策"
                        if logger:
                            logger.log(f"{self.name} 🔨 WBM生成决策: {action_to_execute}")
                    else:
                        action_to_execute = self._get_default_exploration_action()
                        decision_source = "默认探索"
                        if logger:
                            logger.log(f"{self.name} ⚠️ WBM决策失败,使用默认探索")
            
            # === 第六步:执行行动并记录状态===
            pre_action_state = self._capture_current_state()
            
            execution_result = self._execute_planned_action(action_to_execute, game)
            
            post_action_state = self._capture_current_state()
            
            # === 第七步:EMRS机制评价决策 ===
            if logger:
                logger.log(f"{self.name} 📊 EMRS启动决策评价")
            
            emrs_evaluation = self._emrs_evaluate_decision(
                action=action_to_execute,
                goal=target_goal,
                pre_state=pre_action_state,
                post_state=post_action_state,
                execution_result=execution_result
            )
            
            if logger:
                score = emrs_evaluation.get('quality_score', 0)
                logger.log(f"{self.name} 📈 EMRS决策评价: {score:.2f} ({'优秀' if score > 0.7 else '良好' if score > 0.4 else '需改进'})")
            
            # === 第八步:SSM机制记录EOCATR经验 ===
            # 🚀 性能优化：SSM符号化频率控制
            if not hasattr(self, 'last_ssm_symbolization_round'):
                self.last_ssm_symbolization_round = 0
            
            current_round = getattr(game, 'current_day', 1)
            
            # 每3回合才进行一次SSM符号化
            if current_round - self.last_ssm_symbolization_round >= 3:
                if logger:
                    logger.log(f"{self.name} 🔤 SSM记录EOCATR经验")
                
                # 🔧 关键修复：调用SSM符号化生成EOCATR元组
                try:
                    self.symbolize_scene(game)
                    self.last_ssm_symbolization_round = current_round
                    if logger:
                        logger.log(f"{self.name} 🔤 SSM符号化完成，生成了{len(self.current_eocar_scene) if hasattr(self, 'current_eocar_scene') else 0}个EOCATR元组")
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} ❌ SSM符号化失败: {str(e)}")
            else:
                if logger:
                    logger.log(f"{self.name} 🔤 SSM符号化跳过 (距离上次{current_round - self.last_ssm_symbolization_round}回合，需等待5回合)")
            
            # 🔧 修复：将SSM生成的EOCATR经验保存到五库系统
            has_scene = hasattr(self, 'current_eocar_scene')
            scene_exists = self.current_eocar_scene if has_scene else None
            scene_count = len(scene_exists) if scene_exists else 0
            if logger:
                logger.log(f"{self.name} 🔧 SSM条件检查: has_scene={has_scene}, scene_count={scene_count}")
            
            if has_scene and scene_exists and scene_count > 0:
                if logger:
                    logger.log(f"{self.name} 🔧 SSM开始调用保存方法，元组数量: {scene_count}")
                try:
                    self._save_eocar_tuples_to_five_libraries(scene_exists)
                    if logger:
                        logger.log(f"{self.name} ✅ SSM成功保存{scene_count}个EOCATR元组")
                except AttributeError as e:
                    if logger:
                        logger.log(f"{self.name} ❌ SSM保存方法不存在: {str(e)}")
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} ❌ SSM保存异常: {str(e)}")
            else:
                if logger:
                    logger.log(f"{self.name} ❌ SSM保存跳过: has_scene={has_scene}, scene_exists={scene_exists is not None}, scene_count={scene_count}")
            
            # 调用现有的add_eocar_experience方法
            eocar_result = {
                'success': execution_result.get('success', False),
                'action_type': action_to_execute,
                'decision_source': decision_source,
                'evaluation': emrs_evaluation
            }
            self.add_eocar_experience(action_to_execute, eocar_result, source="optimized_decision_flow")
            
            # === 第九步:BPM机制生成和验证规从===
            # 性能优化：降低BPM日志频率
            if logger and self.life_experience_count % 3 == 0:
                logger.log(f"{self.name} 🌸 BPM启动规律生成")
            
            # BPM处理 (使用现有的BPM系统)
            if hasattr(self, 'bpm') and self.bpm and len(self.eocar_experiences) > 3:
                try:
                    recent_experiences = self.eocar_experiences[-5:]
                    if recent_experiences:
                        latest_experience = recent_experiences[-1]
                        historical_batch = recent_experiences[:-1] if len(recent_experiences) > 1 else []
                        
                        # 生成新规"
                        new_candidate_rules = self.bpm.process_experience(latest_experience, historical_batch)
                        
                        # 验证规律
                        validation_experiences = self.eocar_experiences[-3:]
                        validated_rule_ids = self.bpm.validation_phase(validation_experiences)
                        
                        # 🔧 自动保存验证通过的规律到五库系统
                        if validated_rule_ids and hasattr(self, 'five_library_system'):
                            saved_rules_count = 0
                            for rule_id in validated_rule_ids:
                                if hasattr(self.bpm, 'validated_rules') and rule_id in self.bpm.validated_rules:
                                    bmp_rule = self.bpm.validated_rules[rule_id]
                                    
                                    # 转换BMP规律格式为五库系统格式
                                    try:
                                        save_result = self.five_library_system.add_rule(
                                            rule_type=bmp_rule.rule_type.value if hasattr(bmp_rule.rule_type, 'value') else str(bmp_rule.rule_type),
                                            conditions=bmp_rule.conditions,
                                            predictions=bmp_rule.predictions,
                                            confidence=bmp_rule.confidence,
                                            support_count=len(bmp_rule.evidence.supporting_experiences) if hasattr(bmp_rule, 'evidence') else 1,
                                            contradiction_count=len(bmp_rule.evidence.contradicting_experiences) if hasattr(bmp_rule, 'evidence') else 0,
                                            creator_id=self.name,
                                            validation_status='validated'
                                        )
                                        
                                        if save_result.get('success', False):
                                            saved_rules_count += 1
                                            if logger:
                                                logger.log(f"  ✅ BMP验证规律已保存到五库: {rule_id}")
                                        else:
                                            if logger:
                                                logger.log(f"  ❌ BMP验证规律保存失败: {rule_id} - {save_result.get('error', 'Unknown error')}")
                                    
                                    except Exception as e:
                                        if logger:
                                            logger.log(f"  ❌ BMP验证规律保存异常: {rule_id} - {str(e)}")
                            
                            if saved_rules_count > 0 and logger:
                                logger.log(f"{self.name} 💾 已保存{saved_rules_count}条BMP验证规律到五库系统")
                        
                        # 剪枝低质量规"
                        pruned_rules = self.bpm.pruning_phase()
                        
                        if logger and (new_candidate_rules or validated_rule_ids):
                            logger.log(f"{self.name} 📋 生成{len(new_candidate_rules)}条候选规律, 验证{len(validated_rule_ids)}条规律")
                            
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} BPM规律处理失败: {str(e)}")
            
            # === 第九点五步:更新多日计划执行结果 ===
            if (hasattr(self, 'current_multi_day_plan') and self.current_multi_day_plan and 
                decision_source in ["WBM长链决策继续", "WBM长链决策"]):
                if logger:
                    logger.log(f"{self.name} 📋 更新多日计划执行结果")
                
                self._update_daily_execution_result(execution_result, logger)
            
            # === 第十步:再次状态判断,完成循环 ===
            final_state = self._analyze_current_state(game)
            if logger:
                logger.log(f"{self.name} 🔄 回合结束状态 {final_state['status']} | 决策来源: {decision_source}")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 从决策流程异常: {str(e)}")
            # 异常情况下的安全行动
            try:
                safe_action = self._get_default_exploration_action()
                self._execute_action(safe_action)
                if logger:
                    logger.log(f"{self.name} 🛡从执行安全行动: {safe_action}")
            except:
                pass
        
        # 记录回合开始状态
        if hasattr(self, 'memory_system') and self.memory_system:
            try:
                self.memory_system.store_memory(
                    content=f"第{game.current_day}天开始,健康:{self.health}, 食物:{self.food}, 从{self.water}",
                    memory_type="episodic",
                    importance=1,
                    tags=["状态", "回合开始", f"第{game.current_day}天"]
                )
            except:
                pass

    def detect_threats(self, game_map):
            if logger:
                logger.log(f"{self.name} take_turn执行失败: {str(e)}")
            # 应急处理:执行随机移动
            self._execute_random_move()
    
    def detect_threats(self, game_map):
        """检测周围的威胁,返回所有威胁对象的列表"""
        threats = []
        threat_detection_range = 10  # 增大威胁检测范"""
        for animal in game_map.animals:
            if animal.alive and animal.type in ["Tiger", "BlackBear"]:
                dist = abs(animal.x - self.x) + abs(animal.y - self.y)
                if dist <= threat_detection_range:
                    # 计算威胁程度(基于距离和动物类型"
                    threat_level = self.calculate_threat_level(animal, dist)
                    if threat_level > 0:
                        threats.append(animal)
        
        return threats

    def calculate_threat_level(self, animal, distance):
        """计算特定威胁的危险程度"""
        base_threat = 100 if animal.type == "Tiger" else 70  # 老虎比黑熊更危险
        distance_factor = max(0, 1 - (distance / 10))  # 距离越近威胁越大
        return base_threat * distance_factor

    def calculate_escape_direction(self, threats, game_map):
        """计算最优逃跑方向"""
        # 计算所有可能的移动方向
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x = self.x + dx
                new_y = self.y + dy
                if game_map.is_within_bounds(new_x, new_y):
                    safety_score = self.evaluate_position_safety(new_x, new_y, threats, game_map)
                    possible_moves.append((dx, dy, safety_score))
        
        if not possible_moves:
            return None
        
        # 选择安全分数最高的移动方向
        best_move = max(possible_moves, key=lambda x: x[2])
        return (best_move[0], best_move[1])

    def evaluate_position_safety(self, x, y, threats, game_map):
        """评估特定位置的安全程度"""
        safety_score = 100
        
        # 考虑与所有威胁的距离
        for threat in threats:
            dist = abs(x - threat.x) + abs(y - threat.y)
            if dist == 0:
                return 0  # 与威胁重叠,完全不安"""
            threat_level = self.calculate_threat_level(threat, dist)
            safety_score -= threat_level
        
        # 考虑地形因素
        if game_map.grid[y][x] in ["big_tree", "bush"]:
            safety_score += 20  # 树木和灌木提供掩"
        elif game_map.grid[y][x] in ["river", "puddle"]:
            safety_score += 10  # 水域提供一定保"
        # 考虑是否靠近地图边缘(可能被困)
        if x <= 1 or x >= game_map.width - 2 or y <= 1 or y >= game_map.height - 2:
            safety_score -= 30
        
        return max(0, safety_score)  # 确保安全分数不为"
    def apply_reasoning(self):
        """使用多层次记忆系统进行推理决策"""
        try:
            # 搜索危险相关的记"""
            danger_memories = self.memory_system.search_memories(
                tags=["危险", "威胁", "攻击", "受伤"],
                memory_types=["episodic", "semantic"],
                max_results=5
            )
            
            # 搜索成功经验的记"
            success_memories = self.memory_system.search_memories(
                tags=["成功", "胜利", "收获", "安全"],
                memory_types=["episodic", "semantic"],
                max_results=5
            )
            
            # 计算危险和成功记忆的权重
            danger_weight = sum(memory.strength for memory in danger_memories)
            success_weight = sum(memory.strength for memory in success_memories)
            
            # 基于记忆强度做决"
            if danger_weight > success_weight * 1.5:  # 危险记忆明显更强
                # 记录推理过程
                self.memory_system.store_memory(
                    content="基于危险记忆选择逃跑策略",
                    memory_type="procedural",
                    importance=3,
                    tags=["推理", "决策", "逃跑"]
                )
                return "flee"
            elif success_weight > danger_weight:  # 成功记忆更强
                # 记录推理过程
                self.memory_system.store_memory(
                    content="基于成功记忆选择攻击策略",
                    memory_type="procedural", 
                    importance=3,
                    tags=["推理", "决策", "攻击"]
                )
                return "attack"
            else:
                # 记忆不足或平衡,使用保守策略
                self.memory_system.store_memory(
                    content="记忆不足,选择保守策略",
                    memory_type="procedural",
                    importance=2,
                    tags=["推理", "决策", "保守"]
                )
                return "flee"  # 默认保守
                
        except Exception as e:
            # 推理失败,记录错误并使用默认策略
            self.memory_system.store_memory(
                content=f"推理过程出错: {str(e)}",
                memory_type="episodic",
                importance=2,
                tags=["错误", "推理", "异常"]
            )
            return "attack"  # 默认攻击

    def find_nearest_animal(self, game_map):
        nearest = None
        min_distance = 999
        for animal in game_map.animals:
            if animal.alive:
                dist = abs(animal.x - self.x) + abs(animal.y - self.y)
                if dist < min_distance:
                    min_distance = dist
                    nearest = animal
        return nearest

    def find_nearest_plant(self, game_map):
        """寻找最近的未被采集的植物"""
        nearest_plant = None
        min_distance = float('inf')
        
        for plant in game_map.plants:
            if plant.alive and not plant.collected and not plant.toxic:
                dist = abs(plant.x - self.x) + abs(plant.y - self.y)
                if dist < min_distance:
                    min_distance = dist
                    nearest_plant = plant
        
        return nearest_plant

    def find_nearest_water(self, game_map):
        """寻找最近的水源(河流或水坑)"""
        nearest_water = None
        min_distance = float('inf')
        
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.grid[y][x] in ["river", "puddle"]:
                    dist = abs(x - self.x) + abs(y - self.y)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_water = (x, y)
        
        return nearest_water

    def find_path_to_water(self, target, game_map):
        """使用A*算法寻找到水源的最佳路径"""
        from heapq import heappush, heappop
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < game_map.width and 
                    0 <= new_y < game_map.height and
                    game_map.grid[new_y][new_x] != "rock"):  # 避开岩石
                    neighbors.append((new_x, new_y))
            return neighbors
        
        start = (self.x, self.y)
        goal = target
        
        frontier = []
        heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # 重建路径
        if goal not in came_from:
            return None
            
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        
        return path[1:] if len(path) > 1 else None

    def get_state(self):
        """获取当前状态表示"""
        try:
            if hasattr(self, 'current_pos') and self.current_pos is not None:
                x, y = self.current_pos
            else:
                x, y = 0, 0  # 默认位置
                
            # 基础信息
            state = [
                self.health / 100.0,  # 血量(归一化)
                self.water / 100.0,   # 水量(归一化)
                self.food / 100.0,    # 食物(归一化)
                x / self.game_map.width,      # x位置(归一化)
                y / self.game_map.height      # y位置(归一化)
            ]
            
            # 邻近资源和敌人信"""
            resource_info = []
            predator_info = []
            
            # 扫描周围10格范"
            scan_radius = 10
            
            # 填充邻近资源信息
            for resource in self.game_map.resources:
                res_x, res_y = resource.position
                distance = ((x - res_x)**2 + (y - res_y)**2)**0.5
                
                if distance <= scan_radius:
                    # 每个资源4个值:相对x,相对y,距离,类型
                    resource_info.append([
                        (res_x - x) / scan_radius,  # 相对x位置(归一化)
                        (res_y - y) / scan_radius,  # 相对y位置(归一化)
                        distance / scan_radius,     # 距离(归一化)
                        0.5 if resource.type == "berry" else 1.0  # 类型(berry=0.5, water=1.0"
                    ])
            
            # 填充最从个邻近资"
            resource_info = resource_info[:5]
            while len(resource_info) < 5:
                resource_info.append([0, 0, 1.0, 0])  # 添加填充"
            # 填充邻近捕食者信"
            for predator in self.game_map.predators:
                pred_x, pred_y = predator.position
                distance = ((x - pred_x)**2 + (y - pred_y)**2)**0.5
                
                if distance <= scan_radius:
                    # 每个捕食者个值:相对x,相对y,距从 健康"
                    predator_info.append([
                        (pred_x - x) / scan_radius,  # 相对x位置(归一化)
                        (pred_y - y) / scan_radius,  # 相对y位置(归一化)
                        distance / scan_radius,      # 距离(归一化)
                        predator.health / 100.0      # 捕食者健康度(归一化)
                    ])
            
            # 填充最从个邻近捕食者
            predator_info = predator_info[:5]
            while len(predator_info) < 5:
                predator_info.append([0, 0, 1.0, 0])  # 添加填充"
            # 邻近玩家信息
            player_info = []
            for player in self.game_map.players:
                if player != self:
                    if hasattr(player, 'current_pos') and player.current_pos is not None:
                        player_x, player_y = player.current_pos
                        distance = ((x - player_x)**2 + (y - player_y)**2)**0.5
                        
                        if distance <= scan_radius:
                            # 每个玩家5个值:相对x, 相对y, 距离, 信誉从 是否为敌"
                            player_info.append([
                                (player_x - x) / scan_radius,      # 相对x位置(归一化)
                                (player_y - y) / scan_radius,      # 相对y位置(归一化)
                                distance / scan_radius,            # 距离(归一化)
                                player.reputation / 100.0,         # 信誉度(归一化)
                                1.0 if self.check_is_enemy(player) else 0.0  # 是否为敌"
                            ])
            
            # 填充最从个邻近玩"
            player_info = player_info[:5]
            while len(player_info) < 5:
                player_info.append([0, 0, 1.0, 0, 0])  # 添加填充"
            # 扁平化数组并添加到状态
            for info in resource_info:
                state.extend(info)  # 添加5个资源,每个4个从= 20个"
            for info in predator_info:
                state.extend(info)  # 添加5个捕食者,每个4个从= 20个"
            for info in player_info:
                state.extend(info)  # 添加5个玩家,每个5个从= 25个"
            # 环境时间和条件信息(从个特征)
            state.extend([
                self.game_map.current_round / self.game_map.max_rounds,  # 当前回合(归一化)
                1.0 if self.water < 30 else 0.0,  # 缺水标志
                1.0 if self.food < 30 else 0.0,   # 缺食物标"
                1.0 if self.health < 30 else 0.0, # 低健康标"
                len(self.game_map.players) / 20.0,  # 存活玩家数(归一化)
                len(self.game_map.predators) / 50.0,  # 捕食者数量(归一化)
                len(self.game_map.resources) / 100.0,  # 资源数量(归一化)
                1.0 if self.health < 50 and (self.water < 30 or self.food < 30) else 0.0  # 危险状态标"
            ])
            
            # 确保状态向量大小符合预"
            assert len(state) == self.state_size, f"状态向量大小不匹配:{len(state)} vs {self.state_size}"
            
            return np.array(state)
        except Exception as e:
            import traceback
            logger.log(f"{self.name} 获取状态失从 {str(e)}")
            logger.log(traceback.format_exc())
            # 返回零向量作为默认状态
            return np.zeros(self.state_size)

    def calculate_reward(self, action):
        """计算执行动物后的奖励"""
        try:
            reward = 0
            
            # 基础奖励:存活奖励
            reward += 0.1
            
            # 健康状态变化奖励
            health_change = self.health - self.last_health if hasattr(self, 'last_health') else 0
            reward += health_change * 0.05  # 健康提高给予奖励,降低给予惩"""
            # 生存资源奖励
            # 如果之前缺水现在改善"
            if hasattr(self, 'last_water') and self.last_water < 30 and self.water >= 30:
                reward += 1.0
            # 如果之前缺食物现在改善了
            if hasattr(self, 'last_food') and self.last_food < 30 and self.food >= 30:
                reward += 1.0
                
            # 收集资源奖励
            if action == "collect" and hasattr(self, 'last_food'):
                food_change = self.food - self.last_food
                if food_change > 0:
                    reward += 0.5
                    
            # 喝水奖励
            if action == "drink" and hasattr(self, 'last_water'):
                water_change = self.water - self.last_water
                if water_change > 0:
                    reward += 0.5
            
            # 躲避捕食者奖励惩罚
            if hasattr(self, 'current_pos') and hasattr(self, 'last_pos'):
                x, y = self.current_pos
                last_x, last_y = self.last_pos
                
                # 计算与最近捕食者的距离变化
                nearest_pred_dist = float('inf')
                nearest_pred_last_dist = float('inf')
                
                for predator in self.game_map.predators:
                    px, py = predator.position
                    curr_dist = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                    last_dist = ((px - last_x) ** 2 + (py - last_y) ** 2) ** 0.5
                    
                    if curr_dist < nearest_pred_dist:
                        nearest_pred_dist = curr_dist
                    if last_dist < nearest_pred_last_dist:
                        nearest_pred_last_dist = last_dist
                
                # 如果原本很近,现在距离增加了,给奖励
                if nearest_pred_last_dist < 5 and nearest_pred_dist > nearest_pred_last_dist:
                    reward += 0.5
                # 如果靠近捕食者,给惩"
                elif nearest_pred_dist < 3:
                    reward -= 0.5
            
            # 战斗奖励/惩罚
            if action == "attack":
                # 攻击敌人成功的奖励在攻击方法中处"
                # 这里给予小惩罚避免无意义攻击
                reward -= 0.1
            
            # 探索奖励
            if hasattr(self, 'exploration_map'):
                if (x, y) not in self.exploration_map:
                    reward += 0.2
                    self.exploration_map.add((x, y))
            
            # 边界探测,避免靠近边"
            if x < 5 or y < 5 or x > self.game_map.width - 5 or y > self.game_map.height - 5:
                reward -= 0.2
            
            # 极端情况的惩"
            if self.health < 20:
                reward -= 0.5  # 健康极低的惩"
            if self.water < 10:
                reward -= 0.3  # 极度缺水的惩"
            if self.food < 10:
                reward -= 0.3  # 极度饥饿的惩"
            # 记录当前状态为下次计算的基础
            self.last_health = self.health
            self.last_water = self.water
            self.last_food = self.food
            self.last_pos = self.current_pos
            
            logger.log(f"{self.name} 执行动物 {action} 获得奖励: {reward}")
            return reward
        except Exception as e:
            logger.log(f"{self.name} 计算奖励失败: {str(e)}")
            return 0.0
    
    def remember(self, state, action, reward, next_state, done):
        """存储经验到回放缓冲区"""
        try:
            action_idx = list(self.actions.keys())[list(self.actions.values()).index(action)]
            self.memory.append((state, action_idx, reward, next_state, done))
            logger.log(f"{self.name} 记忆经验:动物{action}, 奖励={reward}, 完成={done}")
        except Exception as e:
            logger.log(f"{self.name} 存储经验失败: {str(e)}")
    
    def replay(self):
        """训练网络:从记忆中随机抽取批次进行学习率"""
        try:
            if not self.use_reinforcement_learning:
                return
                
            if len(self.memory) < self.batch_size:
                logger.log(f"{self.name} 经验不足,跳过训练")
                return
                
            if self.q_network is None or self.target_network is None:
                logger.log(f"{self.name} 网络未初始化,跳过训练")
                return
            
            # 实现优先经验回放:优先选择奖励大的经验
            experience_list = list(self.memory)
            experience_rewards = np.array([exp[2] for exp in experience_list])
            
            # 正规化奖励为概率(加上偏移量避免负数"
            probs = np.abs(experience_rewards) + 0.01
            probs = probs / probs.sum()
            
            # 按概率抽"
            indices = np.random.choice(
                len(experience_list), 
                size=min(self.batch_size, len(experience_list)), 
                p=probs, 
                replace=False
            )
            
            minibatch = [experience_list[idx] for idx in indices]
            
            # 为批次中的状态和下一状态创建数"
            states = np.array([experience[0] for experience in minibatch])
            next_states = np.array([experience[3] for experience in minibatch])
            
            # 预测当前状态和下一状态的Q"
            q_values = self.q_network.predict(states, verbose=0)
            next_q_values = self.target_network.predict(next_states, verbose=0)
            
            # 更新目标Q"
            for i, (_, action, reward, _, done) in enumerate(minibatch):
                if done:
                    q_values[i, action] = reward
                else:
                    q_values[i, action] = reward + self.gamma * np.max(next_q_values[i])
            
            # 训练Q网络
            self.q_network.fit(states, q_values, verbose=0)
            logger.log(f"{self.name} 完成批次训练,样本数从 {len(minibatch)}")
            
            # 减小探索率
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                
            # 更新步数计数"
            self.step_counter += 1
            
            # 定期更新目标网络
            if self.step_counter % self.target_update_frequency == 0:
                self.target_network.set_weights(self.q_network.get_weights())
                logger.log(f"{self.name} 更新目标网络")
                
            # 定期保存模型
            if self.step_counter % 100 == 0:
                self._save_model()
                
            return True
        except Exception as e:
            import traceback
            logger.log(f"{self.name} 训练网络失败: {str(e)}")
            logger.log(traceback.format_exc())
            return False
            
    def _save_model(self):
        """保存模型到磁盘（内部方法）"""
        try:
            if self.q_network is not None:
                # 使用统一的模型保存目录和格式
                if not os.path.exists(MODELS_DIR):
                    os.makedirs(MODELS_DIR)
                
                model_path = os.path.join(MODELS_DIR, f"rilai_rl_{self.name}.keras")
                self.q_network.save(model_path)
                logger.log(f"{self.name} 强化学习模型已保存: {model_path}")
                return True
            return False
        except Exception as e:
            logger.log(f"{self.name} 保存强化学习模型失败: {str(e)}")
            return False
    
    def save_model(self):
        """保存模型（供游戏主循环调用）"""
        if self.use_reinforcement_learning:
            return self._save_model()
        return True  # ILAI部分不需要保存模型（使用五库系统）
            
    def _load_model(self):
        """从磁盘加载模型"""
        try:
            # 使用统一的模型保存目录和格式
            model_path = os.path.join(MODELS_DIR, f"rilai_rl_{self.name}.keras")
            if os.path.exists(model_path):
                # 加载网络
                self.q_network = tf.keras.models.load_model(model_path)
                # 复制到目标网络
                if self.target_network is not None:
                    self.target_network.set_weights(self.q_network.get_weights())
                logger.log(f"{self.name} 强化学习模型已加载: {model_path}")
                return True
            else:
                logger.log(f"{self.name} 未找到强化学习模型文件: {model_path}")
                return False
        except Exception as e:
            logger.log(f"{self.name} 加载强化学习模型失败: {str(e)}")
            return False

    def _convert_eocatr_action_to_goal_type(self, action):
        """将EOCATR动作转换为WBM目标类型"""
        from wooden_bridge_model import GoalType
        
        action_to_goal_mapping = {
            'hunt': GoalType.RESOURCE_ACQUISITION,
            'gather': GoalType.RESOURCE_ACQUISITION,
            'move': GoalType.EXPLORATION,
            'explore': GoalType.EXPLORATION,
            'observe': GoalType.EXPLORATION,
            'analyze': GoalType.EXPLORATION,
            'seek': GoalType.RESOURCE_ACQUISITION,
            'search': GoalType.EXPLORATION,
            'avoid': GoalType.THREAT_AVOIDANCE,
            'escape': GoalType.THREAT_AVOIDANCE,
            'rest': GoalType.SURVIVAL,
            'heal': GoalType.SURVIVAL
        }
        
        return action_to_goal_mapping.get(action.lower(), GoalType.EXPLORATION)

    def make_decision_with_wooden_bridge(self, game):
        """使用木桥模型进行决策(增强版 - 集成整合决策系统, BPM系统和规律验证)"""
        try:
            # === 最高优先级:整合决策系统===
            # 优先使用整合决策系统进行决策
            if hasattr(self, 'integrated_decision_active') and self.integrated_decision_active and self.integrated_decision_system:
                try:
                    # 构建决策上下"""
                    context = DecisionContext(
                        hp=self.hp,
                        food=self.food,
                        water=self.water,
                        position=(self.x, self.y),
                        day=getattr(game, 'current_day', 1),
                        environment=self._get_current_environment_type(game),
                        threats_nearby=len(self.detect_threats(game.game_map)) > 0,
                        resources_nearby=self._get_nearby_resources(game),
                        urgency_level=self._calculate_urgency_level()
                    )
                    
                    # 使用整合决策系统进行决策
                    decision_result = self.integrated_decision_system.make_integrated_decision(context, game)
                    
                    if decision_result.get('success') and decision_result.get('action'):
                        action = decision_result['action']
                        decision_source = decision_result.get('source', 'unknown')
                        confidence = decision_result.get('confidence', 0)
                        
                        if logger:
                            logger.log(f"{self.name} 🏗从整合决策系统建议行动: {action} (来源: {decision_source}, 置信从 {confidence:.2f})")
                        
                        return action
                        
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} 整合决策系统失败,回退到木桥模从 {str(e)}")
            
            # 🎯 关键修复：优先建立EOCATR目标，再建立常规目标
            self.current_goals = self._establish_current_goals_with_eocatr(game)
            
            # === CDL友好模式 ===
            # 如果资源充足且没有紧急威胁,允许CDL接管决策
            if (self.food > 60 and self.water > 60 and self.health > 70 and 
                not self.detect_threats(game.game_map)):
                # 检查是否有高紧急度的目"
                high_urgency_goals = [g for g in self.current_goals if g.urgency > 0.7] if self.current_goals else []
                if not high_urgency_goals:
                    if logger:
                        logger.log(f"{self.name} 🌉 木桥模型:资源充足无紧急目标,让位给CDL探索")
                    return None  # 返回None让CDL接管
            
            # 如果没有目标,使用探索行"
            if not self.current_goals:
                return self._get_default_exploration_action()
            
            # 选择最重要的目"
            primary_goal = max(self.current_goals, key=lambda g: g.calculate_importance())
            
            # === 新增:获取验证规律的行动建议 ===
            current_context = {
                'health_level': 'low' if self.health < 30 else 'medium' if self.health < 70 else 'high',
                'resource_status': 'depleted' if self.food < 30 or self.water < 30 else 'adequate',
                'environment': self._get_current_environment_type(game),
                'position': (self.x, self.y),
                'threats_nearby': len(self.detect_threats(game.game_map)) > 0
            }
            
            validated_rules_suggestions = self.get_validated_rules_for_action_suggestion(current_context)
            if validated_rules_suggestions:
                # 选择最高置信度的规律建"
                best_rule = max(validated_rules_suggestions, key=lambda x: x.get('confidence', 0.0))
                suggested_action = best_rule.get('action_recommendation', '')
                
                if suggested_action and logger:
                    confidence = best_rule.get('confidence', 0.0)
                    logger.log(f"新BPM系统建议行动: {suggested_action} (置信从 {confidence:.2f})")
                
                # 验证建议的行动是否可执行
                if self._is_action_executable(suggested_action, game):
                    return suggested_action
            
            # 从BPM系统获取候选规"
            # === 增强：从BMP系统获取EOCATR候选规律 ===
            try:
                if hasattr(self, 'bmp') and self.bmp:
                    # 尝试触发EOCATR系统性规律生成
                    eocatr_config = self._build_eocatr_matrix_config(game, primary_goal)
                    systematic_rules = self.bmp.generate_systematic_eocatr_rules(eocatr_config)
                    
                    if systematic_rules:
                        # 筛选与当前目标相关的规律
                        goal_relevant_rules = []
                        for rule in systematic_rules:
                            if self._is_rule_applicable_to_goal(rule, primary_goal):
                                goal_relevant_rules.append(rule)
                        
                        if goal_relevant_rules:
                            # 选择置信度最高的规律
                            best_rule = max(goal_relevant_rules, key=lambda r: r.confidence)
                            
                            # 尝试将BMP规律转换为WBM可执行的行动
                            wbm_action = self._convert_bmp_rule_to_action(best_rule, primary_goal, game)
                            
                            if wbm_action and self._is_action_executable(wbm_action, game):
                                if logger:
                                    logger.log(f"{self.name} 🌸 BMP-EOCATR规律建议行动: {wbm_action} (置信度: {best_rule.confidence:.3f})")
                                return wbm_action
                        
                        if logger:
                            logger.log(f"{self.name} 🌸 BMP生成{len(systematic_rules)}个EOCATR规律，{len(goal_relevant_rules)}个与目标相关")
                
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} BMP-EOCATR规律获取失败: {str(e)}")
            
            # === 多步规划决策 ===
            # 尝试生成多步规划来实现目标
            if primary_goal:
                multi_step_plan = self._generate_multi_step_plan(primary_goal, game)
                if multi_step_plan and len(multi_step_plan.get('steps', [])) > 1:
                    # 创建并激活多步计划
                    self.current_plan = multi_step_plan
                    self.current_plan_step = 0
                    self.plan_failure_count = 0
                    self.multi_step_stats['plans_created'] += 1
                    
                    if logger:
                        steps_count = len(multi_step_plan['steps'])
                        logger.log(f"{self.name} 🗺️ 生成多步计划: {steps_count}步达成目标 '{primary_goal.description}'")
                        for i, step in enumerate(multi_step_plan['steps']):
                            logger.log(f"  步骤{i+1}: {step.get('action', 'unknown')}")
                    
                    # 执行第一步
                    first_step_result = self._execute_next_plan_step(game)
                    if first_step_result['status'] == 'continue':
                        return None  # 第一步成功，等待下回合继续
                    elif first_step_result['status'] == 'completed':
                        self.multi_step_stats['plans_completed'] += 1
                        self._reset_plan_state()
                        return None  # 计划意外地在第一步就完成了
                    else:
                        # 第一步失败，重置计划状态，继续使用默认行动
                        self._reset_plan_state()
            
            # 如果没有可用的行动建议,使用默认的探索行"
            return self._get_default_exploration_action()
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 木桥模型决策失败: {str(e)}")
            return self._select_ilai_action()
    
    def _establish_current_goals_with_eocatr(self, game):
        """建立当前目标(支持EOCATR格式，优先级：EOCATR目标 > 常规目标)"""
        goals = []
        
        # 🎯 CDL简化机制：检查是否存在CDL传递的EOCATR目标
        if hasattr(self, '_pending_cdl_goal') and self._pending_cdl_goal:
            cdl_goal = self._pending_cdl_goal
            
            # 优先处理新的cdl_exploration类型
            if cdl_goal.get('type') == 'cdl_exploration' and 'eocatr_goal' in cdl_goal:
                eocatr_goal = cdl_goal['eocatr_goal']
                
                # 🎯 直接将CDL的EOCATR目标转换为WBM目标
                from wooden_bridge_model import GoalType
                wbm_goal = self.wooden_bridge_model.establish_goal(
                    self._convert_eocatr_action_to_goal_type(eocatr_goal.get('action', 'explore')),
                    f"CDL探索: {eocatr_goal.get('action', 'unknown')} {eocatr_goal.get('object', '')}",
                    priority=min(0.9, cdl_goal.get('urgency', 0.5) + 0.3),  # CDL探索目标高优先级
                    urgency=cdl_goal.get('urgency', 0.5),
                    context={
                        'eocatr_environment': eocatr_goal.get('environment', 'unknown'),
                        'eocatr_object': eocatr_goal.get('object', 'unknown'),
                        'eocatr_action': eocatr_goal.get('action', 'unknown'),
                        'eocatr_expected_result': eocatr_goal.get('expected_result', 'unknown'),
                        'eocatr_tool': eocatr_goal.get('tool', None),
                        'source': 'cdl_simplified',
                        'novelty_score': cdl_goal.get('novelty_score', 0.5),
                        'current_position': (self.x, self.y)
                    }
                )
                goals.append(wbm_goal)
                
                if logger:
                    novelty = cdl_goal.get('novelty_score', 0.0)
                    logger.log(f"{self.name} 🎯 CDL简化目标: {eocatr_goal.get('action')} → {eocatr_goal.get('object')} (新奇度:{novelty:.2f})")
                
                # 🏷️ 记录尝试的行为，用于新奇度跟踪
                self._record_attempted_action(eocatr_goal)
                
                # 清理待处理的CDL目标
                self._pending_cdl_goal = None
                
            # 兼容旧版CDL目标格式
            elif 'eocatr_goal' in cdl_goal:
                eocatr_goal = cdl_goal['eocatr_goal']
                
                from wooden_bridge_model import GoalType
                wbm_goal = self.wooden_bridge_model.establish_goal(
                    self._convert_eocatr_action_to_goal_type(eocatr_goal.get('action', 'explore')),
                    f"EOCATR: {eocatr_goal.get('action', 'unknown')} {eocatr_goal.get('object', '')}",
                    priority=cdl_goal.get('urgency', 0.5) + 0.2,
                    urgency=cdl_goal.get('urgency', 0.5),
                    context={
                        'eocatr_environment': eocatr_goal.get('environment', 'unknown'),
                        'eocatr_object': eocatr_goal.get('object', 'unknown'),
                        'eocatr_action': eocatr_goal.get('action', 'unknown'),
                        'eocatr_expected_result': eocatr_goal.get('expected_result', 'unknown'),
                        'eocatr_tool': eocatr_goal.get('tool', None),
                        'source': 'cdl_legacy',
                        'current_position': (self.x, self.y)
                    }
                )
                goals.append(wbm_goal)
                
                if logger:
                    logger.log(f"{self.name} 🎯 建立EOCATR目标: {eocatr_goal.get('action')} → {eocatr_goal.get('object')}")
                
                self._pending_cdl_goal = None
        
        # 🔄 第二步：建立常规目标（仅在没有CDL探索目标时）
        if not goals:  # 如果没有CDL目标，才建立常规目标
            goals.extend(self._establish_current_goals(game))
        
        return goals
    
    def _establish_current_goals(self, game):
        """建立当前目标(基于环境状态和内在需求)"""
        goals = []
        
        # 基于生存需求确立目"""
        if self.health < 50:
            goals.append(self.wooden_bridge_model.establish_goal(
                GoalType.SURVIVAL,
                "紧急生存需",
                priority=0.9,
                urgency=0.8,
                context={
                    'current_health': self.health,
                    'current_position': (self.x, self.y),
                    'difficulty': 0.7
                }
            ))
        
        if self.water < 30:
            goals.append(self.wooden_bridge_model.establish_goal(
                GoalType.RESOURCE_ACQUISITION,
                "寻找水源",
                priority=0.8,
                urgency=0.9,
                context={
                    'resource_type': 'water',
                    'current_amount': self.water,
                    'current_position': (self.x, self.y)
                }
            ))
        
        if self.food < 30:
            goals.append(self.wooden_bridge_model.establish_goal(
                GoalType.RESOURCE_ACQUISITION,
                "寻找食物",
                priority=0.7,
                urgency=0.8,
                context={
                    'resource_type': 'food',
                    'current_amount': self.food,
                    'current_position': (self.x, self.y)
                }
            ))
        
        # 检查威胁情"
        threats = self.detect_threats(game.game_map)
        if threats:
            goals.append(self.wooden_bridge_model.establish_goal(
                GoalType.THREAT_AVOIDANCE,
                "规避威胁",
                priority=1.0,
                urgency=1.0,
                context={
                    'threats': threats,
                    'current_position': (self.x, self.y),
                    'threat_count': len(threats)
                }
            ))
        
        # 探索目标(当基本需求满足时"
        if self.health > 60 and self.water > 50 and self.food > 50 and not threats:
            goals.append(self.wooden_bridge_model.establish_goal(
                GoalType.EXPLORATION,
                "探索环境",
                priority=0.4,
                urgency=0.3,
                context={
                    'current_position': (self.x, self.y),
                    'exploration_radius': 5,
                    'difficulty': 0.3
                }
            ))
        
        return goals
    
    def _extract_rules_from_experience(self, goal):
        """从BPM经验中提取适用于目标的规律"""
        rules = []
        
        # === 2.0.0版本新增:从BPM系统获取动态生成的规律 ===
        if hasattr(self, 'bpm') and self.bpm and len(self.eocar_experiences) > 5:
            try:
                # 怒放阶段:生成新的候选规"""
                if len(self.eocar_experiences) >= 3:  # 降低怒放门槛从个经"
                    recent_experiences = self.eocar_experiences[-5:]
                    # 修复:使用备份文件中的正确调用方法
                    if recent_experiences:
                        latest_experience = recent_experiences[-1]
                        historical_batch = recent_experiences[:-1] if len(recent_experiences) > 1 else []
                        new_rules = self.bpm.process_experience(latest_experience, historical_batch)
                    else:
                        new_rules = []
                    if new_rules and logger:
                        logger.log(f"{self.name} 🌸 BPM怒放阶段:基于{len(recent_experiences)}个经验生成{len(new_rules)}个候选规律")
                        for i, rule in enumerate(new_rules[:2]):  # 显示从个规"
                            rule_type_content = getattr(rule, "generation_method", "unknown")
                            pattern_str = " + ".join([getattr(elem, "name", str(elem)) for elem in rule.pattern_elements])
                            logger.log(f"  候选规律{i+1}: [{rule_type_content}] {pattern_str[:50]}... (置信从 {rule.confidence:.3f})")
                    elif logger:
                        logger.log(f"{self.name} 🌸 BPM怒放阶段:基于{len(recent_experiences)}个经验,未生成新规律")
                
                # 验证阶段:验证现有规"
                validation_experiences = self.eocar_experiences[-3:] if len(self.eocar_experiences) >= 3 else self.eocar_experiences
                validated_rules = self.bpm.validation_phase(validation_experiences)
                
                # 🔧 修复：将验证通过的规律添加到玩家的validated_rules列表
                if validated_rules:
                    for rule_id in validated_rules:
                        if hasattr(self.bpm, 'validated_rules') and rule_id in self.bpm.validated_rules:
                            bmp_rule = self.bpm.validated_rules[rule_id]
                            # 转换为标准格式并添加到玩家的验证规律列表
                            rule_dict = {
                                'rule_id': rule_id,
                                'rule_type': bmp_rule.rule_type.value if hasattr(bmp_rule.rule_type, 'value') else str(bmp_rule.rule_type),
                                'conditions': bmp_rule.conditions,
                                'predictions': bmp_rule.predictions,
                                'confidence': bmp_rule.confidence,
                                'context': getattr(bmp_rule, 'context', {}),
                                'source': 'bmp_validation'
                            }
                            self._update_validated_rules(rule_dict)
                
                # 🔧 新增：自动保存验证通过的规律到五库系统
                if validated_rules and hasattr(self, 'five_library_system'):
                    saved_rules_count = 0
                    for rule_id in validated_rules:
                        if hasattr(self.bpm, 'validated_rules') and rule_id in self.bpm.validated_rules:
                            bmp_rule = self.bpm.validated_rules[rule_id]
                            
                            # 转换BMP规律格式为五库系统格式
                            try:
                                save_result = self.five_library_system.add_rule(
                                    rule_type=bmp_rule.rule_type.value if hasattr(bmp_rule.rule_type, 'value') else str(bmp_rule.rule_type),
                                    conditions=bmp_rule.conditions,
                                    predictions=bmp_rule.predictions,
                                    confidence=bmp_rule.confidence,
                                    support_count=len(bmp_rule.evidence.supporting_experiences),
                                    contradiction_count=len(bmp_rule.evidence.contradicting_experiences),
                                    creator_id=self.name,
                                    validation_status='validated'
                                )
                                
                                if save_result.get('success', False):
                                    saved_rules_count += 1
                                    if logger:
                                        logger.log(f"  ✅ 规律已保存到五库: {rule_id}")
                                else:
                                    if logger:
                                        logger.log(f"  ❌ 规律保存失败: {rule_id} - {save_result.get('error', 'Unknown error')}")
                            
                            except Exception as e:
                                if logger:
                                    logger.log(f"  ❌ 规律保存异常: {rule_id} - {str(e)}")
                    
                    if saved_rules_count > 0 and logger:
                        logger.log(f"{self.name} 💾 已保存{saved_rules_count}条验证规律到五库系统")
                
                if validated_rules and logger:
                    logger.log(f"{self.name} 📊 BPM验证阶段:验证了{len(validated_rules)}个规律")
                    for rule_id in validated_rules[:2]:  # 显示前个验证规律
                        if hasattr(self.bpm, 'validated_rules') and rule_id in self.bpm.validated_rules:
                            rule = self.bpm.validated_rules[rule_id]
                            logger.log(f"  验证规律: {rule.pattern[:50]}... (置信从 {rule.confidence:.3f})")
                elif logger:
                    logger.log(f"{self.name} 📊 BPM验证阶段:基于{len(validation_experiences)}个经验,无规律通过验证")
                
                # 剪枝阶段:移除低质量规律
                pruned_rules = self.bpm.pruning_phase()
                if pruned_rules and logger:
                    logger.log(f"{self.name} ✂️ BPM剪枝阶段:移除了{len(pruned_rules)}个低质量规律")
                
                # 获取适用于当前目标的规律
                # 创建一个简单的EOCATR元组用于规律匹配
                current_context = {
                    'goal_type': goal.goal_type.value,
                    'health': self.health,
                    'position': (self.x, self.y),
                    'urgency': goal.urgency
                }
                
                # 从BPM获取适用的规律并转换为木桥模型格式
                bmp_rules = self.bpm.get_all_validated_rules()
                for candidate_rule in bmp_rules:
                    if self._is_rule_applicable_to_goal(candidate_rule, goal):
                        # 转换CandidateRule为木桥模型的Rule格式
                        wbm_rule = self._convert_candidate_rule_to_wbm_rule(candidate_rule, goal)
                        if wbm_rule:
                            rules.append(wbm_rule)
                
                # 更新知识演化统计
                if not hasattr(self, 'knowledge_evolution_stats'):
                    self.knowledge_evolution_stats = {
                        'rules_generated': 0, 
                        'rules_validated': 0,
                        'evolution_cycles': 0,
                        'successful_adaptations': 0
                    }
                
                # 安全地增加evolution_cycles计数
                if not hasattr(self, 'knowledge_evolution_stats'):
                    self.knowledge_evolution_stats = {
                        'rules_generated': 0, 
                        'rules_validated': 0,
                        'evolution_cycles': 0,
                        'successful_adaptations': 0,
                        'rules_pruned': 0
                    }
                self.knowledge_evolution_stats['evolution_cycles'] = self.knowledge_evolution_stats.get('evolution_cycles', 0) + 1
                
                if logger:
                    logger.log(f"{self.name} 从BPM获取 {len([r for r in rules if 'bpm_' in r.rule_id])} 个适用规律")
                        
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} BPM规律提取失败: {str(e)}")
        
        # 从多层次记忆系统中提取相关规"
        if hasattr(self, 'memory_system') and self.memory_system:
            try:
                # 获取相关的情景记"
                context_key = f"{goal.goal_type.value}_{goal.description}"
                relevant_memories = self.memory_system.get_relevant_memories(
                    query=context_key,
                    memory_type="episodic",
                    limit=10
                )
                
                # 将记忆转换为规律
                for memory in relevant_memories:
                    rule = self._memory_to_rule(memory, goal)
                    if rule:
                        rules.append(rule)
                        
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} 从记忆系统提取规律失从 {str(e)}")
        
        # === 新增:从间接经验库中提取规律 ===
        # 整合来自其他智能体的高质量经"
        try:
            # 构建当前上下文用于匹配相关间接经"
            current_context = {
                'goal_type': goal.goal_type.value,
                'description': goal.description,
                'health': self.health,
                'food': self.food, 
                'water': self.water,
                'position': (self.x, self.y),
                'urgency': goal.urgency,
                'priority': goal.priority
            }
            
            # 获取相关的间接经验偏"
            indirect_preferences = self.integrate_indirect_experiences_in_decision(current_context)
            
            if indirect_preferences:
                # 将间接经验偏好转换为木桥模型规律
                for action, weight in indirect_preferences.items():
                    if weight > 0.3:  # 只考虑权重较高的行动偏"
                        # 创建基于间接经验的规"
                        from wooden_bridge_model import Rule  # 导入Rule"
                        indirect_rule = Rule(
                            rule_id=f"indirect_{goal.goal_type.value}_{action}_{int(weight*100)}",
                            rule_type="indirect_experience",
                            conditions={
                                'goal_type': goal.goal_type.value,
                                'action_type': action,
                                'confidence': weight
                            },
                            predictions={
                                'action': action,
                                'success_probability': weight,
                                'source': 'indirect_experience'
                            },
                            confidence=weight,
                            usage_count=int(weight * 10),  # 基于权重估算使用次数
                            success_count=int(weight * weight * 10),  # 估算成功次数
                            applicable_contexts=[goal.goal_type.value]
                        )
                        rules.append(indirect_rule)
                        
                        if logger:
                            logger.log(f"{self.name} 从间接经验库提取规律: {action} (权重: {weight:.2f})")
                
            # 获取高可信度的具体间接经"
            relevant_indirect = self.get_relevant_indirect_experiences(
                context_filter=current_context,
                min_credibility=0.7
            )
            
            for indirect_exp in relevant_indirect[:5]:  # 限制最从个间接经"
                try:
                    # 将间接经验转换为规律
                    action = indirect_exp.get('action', '')
                    credibility = indirect_exp.get('credibility', 0)
                    success = indirect_exp.get('result', {}).get('success', False)
                    source = indirect_exp.get('source', 'unknown')
                    
                    if action and credibility > 0.6:
                        from wooden_bridge_model import Rule  # 导入Rule"
                        indirect_rule = Rule(
                            rule_id=f"indirect_exp_{source}_{action}_{int(credibility*100)}",
                            rule_type="indirect_experience",
                            conditions={
                                'context': indirect_exp.get('context', {}),
                                'source_agent': source,
                                'credibility': credibility
                            },
                            predictions={
                                'action': action,
                                'success_probability': credibility * (1.0 if success else 0.5),
                                'source': f'indirect_from_{source}'
                            },
                            confidence=credibility * 0.8,  # 间接经验置信度稍微降"
                            usage_count=1,
                            success_count=1 if success else 0,
                            applicable_contexts=[goal.goal_type.value]
                        )
                        rules.append(indirect_rule)
                        
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} 间接经验转换规律失败: {str(e)}")
                        
            if logger and len([r for r in rules if 'indirect' in r.rule_id]) > 0:
                indirect_count = len([r for r in rules if 'indirect' in r.rule_id])
                logger.log(f"{self.name} 从间接经验库获取 {indirect_count} 个规律")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 间接经验库规律提取失从 {str(e)}")
        
        # 添加基础规律(硬编码的基本生存规律)
        basic_rules = self._get_basic_survival_rules(goal)
        rules.extend(basic_rules)
        
        return rules
    
    def _memory_to_rule(self, memory, goal):
        """将记忆转换为规律"""
        try:
            # 从记忆中提取条件和结"""
            memory_content = memory.get('content', {})
            memory_context = memory.get('context', {})
            memory_outcome = memory.get('outcome', {})
            
            # 构建规律条件
            conditions = {}
            if 'situation' in memory_context:
                conditions['situation'] = memory_context['situation']
            if 'health_level' in memory_context:
                conditions['health_level'] = memory_context['health_level']
            if 'resource_level' in memory_context:
                conditions['resource_level'] = memory_context['resource_level']
            
            # 构建规律预测
            predictions = {}
            if 'action_taken' in memory_content:
                predictions['action'] = memory_content['action_taken']
            if 'success_rate' in memory_outcome:
                predictions['success_probability'] = memory_outcome['success_rate']
            
            # 计算规律置信"
            confidence = memory.get('reliability', 0.5)
            success_count = memory_outcome.get('success_count', 0)
            total_count = memory_outcome.get('total_count', 1)
            
            rule = Rule(
                rule_id=f"memory_{memory.get('id', 'unknown')}_{time.time()}",
                rule_type="experiential",
                conditions=conditions,
                predictions=predictions,
                confidence=confidence,
                usage_count=total_count,
                success_count=success_count,
                applicable_contexts=[goal.goal_type.value]
            )
            
            return rule
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 记忆转规律失从 {str(e)}")
            return None
    
    def _get_basic_survival_rules(self, goal):
        """获取基础生存规律"""
        rules = []
        
        if goal.goal_type == GoalType.SURVIVAL:
            # 生存规律:优先寻找水和食"""
            rules.append(Rule(
                rule_id="survival_water_priority",
                rule_type="action",
                conditions={"health_level": "low", "resource_type": "water"},
                predictions={"action": "search", "priority": "high"},
                confidence=0.8,
                applicable_contexts=["survival"]
            ))
            
            rules.append(Rule(
                rule_id="survival_food_priority",
                rule_type="action", 
                conditions={"health_level": "low", "resource_type": "food"},
                predictions={"action": "collect", "priority": "high"},
                confidence=0.8,
                applicable_contexts=["survival"]
            ))
        
        elif goal.goal_type == GoalType.THREAT_AVOIDANCE:
            # 威胁规避规律
            rules.append(Rule(
                rule_id="threat_escape",
                rule_type="action",
                conditions={"threat_present": True, "threat_distance": "close"},
                predictions={"action": "escape", "direction": "away_from_threat"},
                confidence=0.9,
                applicable_contexts=["threat_avoidance"]
            ))
        
        elif goal.goal_type == GoalType.RESOURCE_ACQUISITION:
            # 资源获取规律
            rules.append(Rule(
                rule_id="resource_search",
                rule_type="action",
                conditions={"resource_needed": True, "resource_available": True},
                predictions={"action": "collect", "success_rate": 0.7},
                confidence=0.7,
                applicable_contexts=["resource_acquisition"]
            ))
        
        elif goal.goal_type == GoalType.EXPLORATION:
            # 探索规律
            rules.append(Rule(
                rule_id="exploration_systematic",
                rule_type="action",
                conditions={"safety_level": "high", "exploration_needed": True},
                predictions={"action": "move", "pattern": "systematic"},
                confidence=0.6,
                applicable_contexts=["exploration"]
            ))
        
        return rules
    
    def _update_rule_performance(self, bridge_plan, execution_result):
        """更新规律性能记录"""
        success = execution_result['success']
        
        for rule in bridge_plan.rules_used:
            rule_id = rule.rule_id
            
            if rule_id not in self.rule_performance_tracker:
                self.rule_performance_tracker[rule_id] = {
                    'usage_count': 0,
                    'success_count': 0,
                    'total_utility': 0.0,
                    'contexts_used': set()
                }
            
            tracker = self.rule_performance_tracker[rule_id]
            tracker['usage_count'] += 1
            
            if success:
                tracker['success_count'] += 1
            
            # 记录使用上下"""
            tracker['contexts_used'].add(bridge_plan.goal.goal_type.value)
            
            # 更新总效"
            utility = bridge_plan.calculate_utility()
            tracker['total_utility'] += utility
            
            # 同步更新内存系统中的规律效果
            if hasattr(self, 'memory_system') and self.memory_system:
                try:
                    # 将utility作为effectiveness_score从-1范围"
                    effectiveness_score = min(1.0, max(0.0, utility / 2.0))  # 将utility缩放从-1范围
                    
                    # 构建outcome字典
                    outcome = {
                        'success': success,
                        'utility': utility,
                        'context': bridge_plan.goal.context,
                        'rule_id': rule_id,
                        'timestamp': time.time()
                    }
                    
                    self.memory_system.update_rule_effectiveness(
                        rule_id=rule_id,
                        effectiveness_score=effectiveness_score,
                        outcome=outcome
                    )
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} 更新记忆系统规律效果失败: {str(e)}")
    
    def _convert_bridge_to_game_action(self, bridge_plan, execution_result):
        """将桥梁方案转换为具体的游戏动物"""
        # 获取桥梁方案的第一个行"""
        if bridge_plan.action_sequence:
            action = bridge_plan.action_sequence[0]
            
            # 将抽象行动映射到具体游戏动物
            action_mapping = {
                "search": "move",  # 搜索转换为移"
                "collect": "collect",  # 收集保持不变
                "escape": "move",  # 逃脱转换为移"
                "assess_threats": "observe",  # 评估威胁转换为观"
                "secure_resources": "collect",  # 确保资源转换为收"
                "approach": "move",  # 接近转换为移"
                "observe": "observe",  # 观察保持不变
                "move": "move",  # 移动保持不变
                "drink": "drink",  # 饮水保持不变
                "attack": "attack"  # 攻击保持不变
            }
            
            mapped_action = action_mapping.get(action, "move")
            
            if logger:
                logger.log(f"{self.name} 木桥方案执行成功,动物 {action} -> {mapped_action}")
            
            return mapped_action
        
        return "move"  # 默认动物
    
    def _process_learning_needs(self, learning_needs, game):
        """处理学习需求(与CDL系统集成)"""
        try:
            if self.cdl_active and hasattr(self, 'curiosity_driven_learning'):
                # 将学习需求转发给CDL系统处理
                from curiosity_driven_learning import ContextState
                
                context_state = ContextState(
                    symbolized_scene=[
                        {'object': 'agent', 'characteristics': {'type': 'self'}},
                        {'object': 'environment', 'characteristics': {'type': 'current'}}
                    ],
                    agent_internal_state={
                        'health': self.health,
                        'food': self.food,
                        'water': self.water,
                        'position': (self.x, self.y)
                    },
                    environmental_factors={
                        'terrain': 'unknown',
                        'weather': 'unknown'
                    },
                    social_context={
                        'entities': [],
                        'missing_rules': learning_needs.get('missing_rules', [])
                    },
                    timestamp=time.time()
                )
                
                # 评估上下文新颖"""
                novelty_score = self.curiosity_driven_learning.evaluate_context_novelty(context_state)
                
                # 生成探索策略
                exploration_strategy = self.curiosity_driven_learning.generate_exploration_strategy(
                    context=context_state,
                    available_actions=['move', 'observe', 'collect', 'search'],
                    development_stage=self.phase.lower() if hasattr(self, 'phase') else 'child'
                )
                
                if logger:
                    logger.log(f"{self.name} CDL处理学习需求,新颖从 {novelty_score:.2f}")
                
                # 基于CDL反馈调整行为
                if exploration_strategy.get('should_explore', False):
                    return self._trigger_exploration_learning(game)
                    
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 处理学习需求失从 {str(e)}")
    
    def _trigger_exploration_learning(self, game):
        """触发探索学习"""
        # 与CDL系统协作进行探索
        exploration_action = "move"  # 默认探索动物
        
        if self.cdl_active and hasattr(self, 'curiosity_driven_learning'):
            try:
                from curiosity_driven_learning import ContextState
                
                context_state = ContextState(
                    agent_internal_state={'position': (self.x, self.y)},
                    environmental_factors={'exploration_needed': True},
                    timestamp=time.time()
                )
                
                exploration_strategy = self.curiosity_driven_learning.generate_exploration_strategy(
                    context=context_state,
                    available_actions=['move', 'observe', 'search'],
                    development_stage=getattr(self, 'phase', 'child').lower()
                )
                
                strategy_type = exploration_strategy.get('strategy', 'random_walk')
                if strategy_type == 'novelty_seeking':
                    exploration_action = "observe"
                elif strategy_type == 'systematic_scan':
                    exploration_action = "search"
                else:
                    exploration_action = "move"
                    
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} CDL探索策略生成失败: {str(e)}")
        
        return exploration_action
    
    def _get_current_game_state(self, game):
        """获取当前游戏状态"""
        return {
            'turn': getattr(game, 'turn', 0),
            'day': getattr(game, 'day', 0),
            'players_alive': len([p for p in game.players if p.is_alive()]),
            'map_size': (game.game_map.width, game.game_map.height),
            'resource_abundance': len(game.game_map.plants),
            'threat_level': len([a for a in game.game_map.animals if hasattr(a, 'is_predator') and a.is_predator])
        }

    def _is_rule_applicable_to_goal(self, candidate_rule, goal):
        """检查BPM候选规律是否适用于当前目标"""
        try:
            # 根据规律类型和目标类型进行匹"""
            rule_type = candidate_rule.rule_type
            goal_type = goal.goal_type
            
            # 类型匹配规则
            type_compatibility = {
                RuleType.SPATIAL: [GoalType.EXPLORATION, GoalType.RESOURCE_ACQUISITION],
                RuleType.CONDITIONAL: [GoalType.SURVIVAL, GoalType.THREAT_AVOIDANCE],
                RuleType.SEQUENTIAL: [GoalType.EXPLORATION, GoalType.LEARNING],
                RuleType.CAUSAL: [GoalType.SURVIVAL, GoalType.THREAT_AVOIDANCE, GoalType.RESOURCE_ACQUISITION]
            }
            
            # 检查规律类型是否与目标类型兼容
            compatible_goals = type_compatibility.get(rule_type, [])
            if goal_type not in compatible_goals:
                return False
            
            # 检查置信度阈"
            if candidate_rule.confidence < 0.3:
                return False
            
            # 检查适用上下文(如果有的话)
            if hasattr(candidate_rule, 'context') and candidate_rule.context:
                # 简单的上下文匹配逻辑
                rule_context = candidate_rule.context
                if 'health_threshold' in rule_context:
                    if self.health < rule_context['health_threshold'] and goal_type != GoalType.SURVIVAL:
                        return False
            
            return True
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 规律适用性检查失从 {str(e)}")
            return False
    
    def _convert_candidate_rule_to_wbm_rule(self, candidate_rule, goal):
        """将BPM的CandidateRule转换为木桥模型的Rule格式"""
        try:
            # 构建条件
            conditions = {}
            if hasattr(candidate_rule, 'antecedent') and candidate_rule.antecedent:
                # 从前件中提取条件
                for key, value in candidate_rule.antecedent.items():
                    conditions[key] = value
            
            # 添加目标相关的条"""
            conditions['goal_type'] = goal.goal_type.value
            conditions['urgency_level'] = 'high' if goal.urgency > 0.7 else 'normal'
            
            # 构建预测
            predictions = {}
            if hasattr(candidate_rule, 'consequent') and candidate_rule.consequent:
                # 从后件中提取预测
                for key, value in candidate_rule.consequent.items():
                    predictions[key] = value
            
            # 如果没有明确的行动预测,根据规律类型推断
            if 'action' not in predictions:
                action_mapping = {
                    RuleType.SPATIAL: 'move',
                    RuleType.CONDITIONAL: 'assess',
                    RuleType.SEQUENTIAL: 'explore',
                    RuleType.CAUSAL: 'execute'
                }
                predictions['action'] = action_mapping.get(candidate_rule.rule_type, 'move')
            
            # 创建木桥模型规律
            wbm_rule = Rule(
                rule_id=f"bpm_{candidate_rule.rule_id}_{int(time.time())}",
                rule_type="bpm_generated",
                conditions=conditions,
                predictions=predictions,
                confidence=candidate_rule.confidence,
                usage_count=getattr(candidate_rule, 'usage_count', 0),
                success_count=getattr(candidate_rule, 'success_count', 0),
                applicable_contexts=[goal.goal_type.value],
                creation_time=time.time()
            )
            
            return wbm_rule
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} BPM规律转换失败: {str(e)}")
            return None
    
    def add_eocar_experience(self, action_taken, result_obtained, source="direct"):
        """添加EOCATR经验到BMP系统(增强版 - 触发知识演化)"""
        import time
        
        # 🔧 动作统一：将left/right/up/down统一为move
        def unify_action_name(action_name):
            """统一动作名称"""
            if action_name in ['left', 'right', 'up', 'down']:
                return 'move'
            return action_name
        
        def enhance_action_data(original_action, position_change=None):
            """增强动作数据，保留原始信息"""
            unified_action = unify_action_name(original_action)
            
            enhanced_data = {
                'type': unified_action,
                'original_action': original_action,
                'target': None,
                'parameters': {}
            }
            
            # 如果是方向性动作，添加方向信息
            if original_action in ['left', 'right', 'up', 'down']:
                enhanced_data['direction'] = original_action
                enhanced_data['parameters']['movement_type'] = 'directional'
                
                # 如果有位置变化信息，也保存下来
                if position_change:
                    enhanced_data['parameters']['position_change'] = position_change
            
            return enhanced_data
        
        # 应用动作统一
        position_change = None
        if isinstance(result_obtained, dict) and 'position_change' in result_obtained:
            position_change = result_obtained['position_change']
            
        if isinstance(action_taken, str):
            enhanced_action_data = enhance_action_data(action_taken, position_change)
        elif isinstance(action_taken, dict) and 'type' in action_taken:
            original_action = action_taken['type']
            enhanced_action_data = action_taken.copy()
            enhanced_action_data['type'] = unify_action_name(original_action)
            enhanced_action_data['original_action'] = original_action
            if original_action in ['left', 'right', 'up', 'down']:
                enhanced_action_data['direction'] = original_action
                enhanced_action_data['parameters'] = enhanced_action_data.get('parameters', {})
                enhanced_action_data['parameters']['movement_type'] = 'directional'
                if position_change:
                    enhanced_action_data['parameters']['position_change'] = position_change
        else:
            enhanced_action_data = action_taken
        
        # 创建经验字典
        if isinstance(action_taken, str):
            # 如果action_taken是字符串,创建完整的经验字典
            experience_dict = {
                'environment': {
                    'position': (self.x, self.y),
                    'health': self.health,
                    'food': self.food,
                    'water': self.water,
                    'timestamp': time.time()
                },
                'observation': {
                    'visible_threats': 0,  # 可以后续增强
                    'visible_resources': 'unknown',
                    'terrain_type': 'unknown'
                },
                'cognition': {
                    'goal_active': len(getattr(self, 'current_goals', [])) > 0,
                    'reasoning_strategy': 'active',
                    'attention_focus': 'survival'
                },
                'action': enhanced_action_data,  # 使用增强的动作数据
                'result': result_obtained if isinstance(result_obtained, dict) else {'success': bool(result_obtained)},
                'source': source,
                'timestamp': time.time()
            }
        else:
            # 如果action_taken已经是字典,直接使用
            experience_dict = action_taken.copy()
            if 'timestamp' not in experience_dict:
                experience_dict['timestamp'] = time.time()
            if 'source' not in experience_dict:
                experience_dict['source'] = source

        # 确保存在eocar_experiences列表
        if not hasattr(self, 'eocar_experiences'):
            self.eocar_experiences = []
            
        # 将字典转换为EOCAR_Tuple对象
        eocar_tuple = self._convert_dict_to_eocar_tuple(experience_dict)
        
        # 添加到EOCATR经验"""
        self.eocar_experiences.append(eocar_tuple)
        
        # === 新增:存储到五库系统 ===
        try:
            self.add_experience_to_direct_library(action_taken, result_obtained, experience_dict)
            if logger:
                logger.log(f"五库经验存储成功: {action_taken}")
        except Exception as e:
            if logger:
                logger.log(f"五库系统经验添加失败: {str(e)}")
        
        # 维护容量限制
        if len(self.eocar_experiences) > getattr(self, 'max_eocar_experiences', 100):
            self.eocar_experiences.pop(0)
            
        # 每当添加新经验时,触发小规模知识演化(降低门槛)
        if hasattr(self, 'bpm') and self.bpm and len(self.eocar_experiences) > 2:
            if len(self.eocar_experiences) % 2 == 0:  # 从个经验触发一"
                # 使用最近的经验进行小规模知识生成(传递EOCAR_Tuple对象"
                recent_experiences = self.eocar_experiences[-3:] if len(self.eocar_experiences) >= 3 else self.eocar_experiences
                try:
                    # 修复:使用备份文件中的正确调用方法
                    if recent_experiences:
                        latest_experience = recent_experiences[-1]
                        historical_batch = recent_experiences[:-1] if len(recent_experiences) > 1 else []
                        new_rules = self.bpm.process_experience(latest_experience, historical_batch)
                    else:
                        new_rules = []
                    
                    if new_rules:
                        if not hasattr(self, 'knowledge_evolution_stats'):
                            self.knowledge_evolution_stats = {
                                'rules_generated': 0, 
                                'rules_validated': 0,
                                'evolution_cycles': 0,
                                'successful_adaptations': 0,
                                'rules_pruned': 0
                            }
                        
                        # 安全地增加rules_generated计数
                        self.knowledge_evolution_stats['rules_generated'] = self.knowledge_evolution_stats.get('rules_generated', 0) + len(new_rules)
                        if logger:
                            logger.log(f"{self.name} 🌸 BPM怒放阶段:基于{len(recent_experiences)}个经验生成{len(new_rules)}个候选规律")
                            for i, rule in enumerate(new_rules[:3]):  # 只显示前3个规"
                                rule_type_content = getattr(rule, "generation_method", "unknown")
                                pattern_str = " + ".join([getattr(elem, "name", str(elem)) for elem in rule.pattern_elements])
                                logger.log(f"  候选规律{i+1}: [{rule_type_content}] {pattern_str[:50]}... (置信从 {rule.confidence:.3f})")
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} BPM怒放阶段失败: {str(e)}")
        
        # === 新增:BPM集成管理器处理 ===
        if hasattr(self, 'bmp_integration') and self.bmp_integration:
            try:
                # 使用新的15种组合规律生成
                new_candidate_rules = self.bmp_integration.process_eocar_experience(eocar_tuple)
                
                if new_candidate_rules:
                    if not hasattr(self, 'bmp_integration_stats'):
                        self.bmp_integration_stats = {
                            'candidate_rules_generated': 0,
                            'rules_validated': 0,
                            'integration_cycles': 0,
                            'last_integration_time': 0.0
                        }
                    
                    self.bmp_integration_stats['candidate_rules_generated'] += len(new_candidate_rules)
                    self.bmp_integration_stats['integration_cycles'] += 1
                    self.bmp_integration_stats['last_integration_time'] = time.time()
                    
                    if logger:
                        logger.log(f"{self.name} 🌸 新BPM集成:生成{len(new_candidate_rules)}个15种组合规律")
                        
                        # 🔥 改进：先进行规律去重，再显示分布
                        type_counts = {}
                        formatted_rules = []
                        seen_patterns = set()  # 用于去重的模式集合
                        
                        for rule in new_candidate_rules:
                            rule_format = self._format_rule_to_standard_pattern(rule)
                            # 确保不是UNKNOWN且没有重复
                            if rule_format != 'UNKNOWN' and rule_format not in seen_patterns:
                                seen_patterns.add(rule_format)
                                type_counts[rule_format] = type_counts.get(rule_format, 0) + 1
                                formatted_rules.append((rule, rule_format))
                        
                        # 如果大部分规律都是UNKNOWN，尝试不同的格式化方法
                        if len(formatted_rules) < len(new_candidate_rules) * 0.3:  # 如果70%以上是UNKNOWN
                            # 使用备用格式化方法，同样进行去重
                            type_counts = {}
                            formatted_rules = []
                            seen_patterns = set()
                            
                            for rule in new_candidate_rules:
                                rule_format = None
                                # 尝试从规律对象直接获取信息
                                if hasattr(rule, 'combination_type'):
                                    rule_format = f"{rule.combination_type.value}"
                                elif hasattr(rule, 'condition_text') and hasattr(rule, 'expected_result'):
                                    rule_format = f"{rule.condition_text} → {rule.expected_result}"
                                else:
                                    # 最后的备用方案 - 使用规律内容而不是序号
                                    rule_format = f"规律_{'_'.join([str(v) for v in rule.conditions.values()][:2])}" if hasattr(rule, 'conditions') else f"规律_{rule.rule_id[:8]}"
                                
                                # 🔥 去重检查
                                if rule_format and rule_format not in seen_patterns:
                                    seen_patterns.add(rule_format)
                                    type_counts[rule_format] = type_counts.get(rule_format, 0) + 1
                                    formatted_rules.append((rule, rule_format))
                        
                        # 显示去重后的规律类型分布
                        unique_rule_count = len(formatted_rules)
                        total_rule_count = len(new_candidate_rules)
                        logger.log(f"   规律类型分布: {dict(list(type_counts.items())[:10])}")  # 显示前10种
                        logger.log(f"   🔥 去重效果: {total_rule_count}个原始规律 -> {unique_rule_count}个唯一规律")
                        
                        # 显示具体的唯一规律
                        display_count = min(len(formatted_rules), 10)  # 显示前10个规律
                        for i in range(display_count):
                            rule, rule_format = formatted_rules[i]
                            logger.log(f"   规律{i+1}: {rule_format}")
                
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} BPM集成管理器处理失败: {str(e)}")
                    import traceback
                    logger.log(f"   错误详情: {traceback.format_exc()}")
        
        # 验证现有规律
        if hasattr(self, 'bpm') and self.bpm and self.eocar_experiences:
            try:
                validated_rules = self.bpm.validation_phase([eocar_tuple])  # 传递EOCAR_Tuple对象
                if validated_rules:
                    if not hasattr(self, 'knowledge_evolution_stats'):
                        self.knowledge_evolution_stats = {
                            'rules_generated': 0, 
                            'rules_validated': 0,
                            'evolution_cycles': 0,
                            'successful_adaptations': 0,
                            'rules_pruned': 0
                        }
                    
                    # 安全地增加rules_validated计数
                    self.knowledge_evolution_stats['rules_validated'] = self.knowledge_evolution_stats.get('rules_validated', 0) + len(validated_rules)
            except Exception as e:
                if logger:
                    logger.log(f"BPM验证阶段失败: {str(e)}")
        
        # === 新增:规律验证系统处从===
        if hasattr(self, 'rule_validation_system') and self.rule_validation_system:
            try:
                # 从BPM系统获取候选规"
                if hasattr(self, 'bpm') and self.bpm:
                    candidate_rules = list(self.bpm.candidate_rules.values()) if hasattr(self.bpm, 'candidate_rules') else []
                    
                    if candidate_rules:
                        # 获取验证建议
                        player_state = {
                            'health': self.health,
                            'food': self.food,
                            'water': self.water,
                            'position': (self.x, self.y)
                        }
                        
                        validation_suggestions = self.rule_validation_system.get_validation_suggestions(
                            eocar_tuple, candidate_rules, player_state
                        )
                        
                        if validation_suggestions:
                            # 处理验证建议
                            for rule, strategy in validation_suggestions[:1]:  # 只处理第一个建"
                                if logger:
                                    logger.log(f"新BPM系统发现验证机会: {rule.rule_id} ({strategy.name})")
                                
                                # 模拟验证结果(基于当前经验)
                                actual_result = {
                                    'success': getattr(eocar_tuple.result, "success", getattr(eocar_tuple.result, "content", str(eocar_tuple.result)) == "success"),
                                    'hp_change': getattr(eocar_tuple.result, "hp_change", 0),
                                    'food_change': getattr(eocar_tuple.result, "food_change", 0),
                                    'water_change': getattr(eocar_tuple.result, "water_change", 0)
                                }
                                
                                # 执行验证
                                validation_attempt = self.rule_validation_system.validate_rule(
                                    rule, eocar_tuple, actual_result, strategy
                                )
                                
                                if validation_attempt:
                                    # 更新统计信息
                                    self.validation_stats['total_validations'] += 1
                                    if validation_attempt.validation_result.name == 'SUCCESS':
                                        self.validation_stats['successful_validations'] += 1
                                    elif validation_attempt.validation_result.name == 'FAILURE':
                                        self.validation_stats['failed_validations'] += 1
                                    
                                    # 更新已验证规律库
                                    rule_dict = {
                                        'rule_id': rule.rule_id,
                                        'confidence': rule.confidence,
                                        'action_recommendation': getattr(rule, 'action_type', 'unknown'),
                                        'context': {
                                            'environment': getattr(eocar_tuple.environment, "content", getattr(eocar_tuple.environment, "name", str(eocar_tuple.environment))),
                                            'object': getattr(eocar_tuple.object, "content", getattr(eocar_tuple.object, "name", str(eocar_tuple.object)))
                                        }
                                    }
                                    self._update_validated_rules(rule_dict)
                                    
                                    if logger:
                                        logger.log(f"新BPM系统更新规律置信从 {rule.rule_id} -> {rule.confidence:.2f}")
                
            except Exception as e:
                if logger:
                    logger.log(f"规律验证系统处理失败: {str(e)}")
        
        if logger:
            action_name = experience_dict.get('action', {}).get('type', action_taken) if isinstance(experience_dict.get('action'), dict) else str(action_taken)
            logger.log(f"{self.name} 添加{source}E-O-C-A-T-R经验: {action_name} -> {result_obtained}")
            
            # 添加BPM系统状态日"
            logger.log(f"{self.name} BPM状态检从 hasattr(bpm)={hasattr(self, 'bpm')}, bpm_obj={getattr(self, 'bpm', None) is not None}")
            logger.log(f"{self.name} EOCATR经验状态 当前数量={len(self.eocar_experiences)}, 触发门槛=5")
            
            if hasattr(self, 'bpm') and self.bpm:
                logger.log(f"{self.name} 从BPM对象已初始化")
                if len(self.eocar_experiences) >= 5:
                    # 计算新经验模式数"
                    unique_patterns = set()
                    for exp in self.eocar_experiences[-5:]:  # 检查最从个经"
                        if hasattr(exp, 'action') and hasattr(exp.action, 'content'):
                            unique_patterns.add(exp.action.content)
                        elif isinstance(exp, dict) and 'action' in exp:
                            action_type = exp['action'].get('type', 'unknown') if isinstance(exp['action'], dict) else str(exp['action'])
                            unique_patterns.add(action_type)
                    
                    # 检查是否达到BMP触发阈值
                    bmp_threshold = 5  # 使用正确的BMP触发阈值
                    if len(unique_patterns) >= bmp_threshold:
                        logger.log(f"{self.name} 🚨 BPM触发条件满足: 发现{len(unique_patterns)}种新经验模式 (门槛:{bmp_threshold})")
                    # 实际执行BMP绽放阶段
                    try:
                        recent_experiences = self.eocar_experiences[-10:] if len(self.eocar_experiences) >= 10 else self.eocar_experiences
                        # 修复:使用备份文件中的正确调用方法
                        if recent_experiences:
                            latest_experience = recent_experiences[-1]
                            historical_batch = recent_experiences[:-1] if len(recent_experiences) > 1 else []
                            new_rules = self.bpm.process_experience(latest_experience, historical_batch)
                        else:
                            new_rules = []
                        if new_rules:
                            logger.log(f"{self.name} 🌸 BMP怒放阶段:基于{len(recent_experiences)}个经验生成{len(new_rules)}个候选规律")
                            for i, rule in enumerate(new_rules[:3]):  # 显示从个规"
                                rule_type_content = getattr(rule, "generation_method", "unknown")
                                # 🔧 修复：安全地访问pattern_elements
                                pattern_parts = []
                                if hasattr(rule, 'pattern_elements') and rule.pattern_elements:
                                    for elem in rule.pattern_elements:
                                        if hasattr(elem, 'content'):
                                            pattern_parts.append(str(getattr(elem, "name", str(elem))))
                                        elif isinstance(elem, str):
                                            pattern_parts.append(elem)
                                        else:
                                            pattern_parts.append(str(elem))
                                pattern_str = " + ".join(pattern_parts) if pattern_parts else "无模式"
                                logger.log(f"  候选规律{i+1}: [{rule_type_content}] {pattern_str[:50]}... (置信从 {rule.confidence:.3f})")
                        else:
                            logger.log(f"{self.name} 🌸 BMP怒放阶段:基于{len(recent_experiences)}个经验,未生成新规律")
                    except Exception as e:
                        logger.log(f"{self.name} 从BMP怒放阶段执行失败: {str(e)}")
                else:
                    logger.log(f"{self.name} 从BPM等待更多经验: {len(self.eocar_experiences)} < 5")
            else:
                logger.log(f"{self.name} 从BPM对象未初始化或为None")

    def _format_rule_to_standard_pattern(self, rule) -> str:
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
                if hasattr(element, 'content'):
                    element_content = element.content.lower()
                    element_type = getattr(element, 'symbol_type', None)
                    
                    if element_type:
                        type_name = element_type.value.lower() if hasattr(element_type, 'value') else str(element_type).lower()
                        if 'environment' in type_name:
                            content['environment'] = element.content
                        elif 'object' in type_name:
                            content['object'] = element.content
                        elif 'character' in type_name:
                            content['characteristics'].append(element.content)
                        elif 'action' in type_name:
                            content['action'] = element.content
                        elif 'tool' in type_name:
                            content['tool'] = element.content
                        elif 'result' in type_name:
                            content['result'] = element.content
        
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
        
        # 结果 - 直接使用具体结果，不使用抽象的"result"
        if content['result'] and content['result'] != 'result':
            pattern_parts.append(content['result'])
            type_parts.append('R')
        else:
            # 如果没有具体结果，使用"无结果"而不是推断
            pattern_parts.append('无结果')
            type_parts.append('R')
        
        # 生成最终格式：实际内容-类型标识
        if len(pattern_parts) >= 2:
            content_pattern = '-'.join(pattern_parts)
            type_pattern = '-'.join(type_parts)
            return f"{content_pattern} ({type_pattern})"
        else:
            return 'UNKNOWN'
    


    def _convert_dict_to_eocar_tuple(self, experience_dict) -> 'EOCAR_Tuple':
        """将字典格式的经验转换为EOCAR_Tuple对象,支持多种输入格式"""
        try:
            from symbolic_core_v3 import (
                EOCATR_Tuple as EOCAR_Tuple, 
                SymbolicElement, SymbolType, AbstractionLevel
            )
            
            # 🔧 数据类型检查和转换
            if isinstance(experience_dict, str):
                # 如果输入是字符串,尝试转换为基本结构
                experience_dict = {
                    'action': {'type': experience_dict, 'content': experience_dict},
                    'result': {'success': True, 'content': '执行动物'}
                }
            elif not isinstance(experience_dict, dict):
                # 如果输入不是字典也不是字符串,转换为字符串再处理
                experience_dict = {
                    'action': {'type': str(experience_dict), 'content': str(experience_dict)},
                    'result': {'success': False, 'content': '未知结果'}
                }
            
            # 创建环境符号元素 - 使用字符串而不是字"""
            env_data = experience_dict.get('environment', {})
            if isinstance(env_data, dict):
                # 如果是字典,转换为字符串
                position = env_data.get('position', (self.x, self.y))
                health = env_data.get('health', self.health)
                
                # 根据健康状态和位置确定环境类型
                if health < 30:
                    env_content = "危险区域"
                elif hasattr(self, 'game_map') and self.game_map:
                    env_content = "开阔地"
                else:
                    env_content = "未知区域"
            else:
                # 如果已经是字符串,直接使"
                env_content = str(env_data)
            
            # 简化环境处理,避免复杂的字典操"
            water_nearby = False
            if isinstance(env_data, dict):
                for water in getattr(self.game_map, 'water_sources', []):
                    if abs(water.x - position[0]) <= 1 and abs(water.y - position[1]) <= 1:
                        water_nearby = True
                        break
                if water_nearby:
                    env_content = "水源区域"
                elif health < 30:
                    env_content = "危险区域"
                else:
                    env_content = "开阔地"
            else:
                env_content = "开阔地"
                env_tags = ["开", "中", "探索"]
            
           
            # 确保env_tags在所有分支中都有定义
            if "env_tags" not in locals():
                if water_nearby:
                    env_tags = ["水源", "资源", "补给", "重要"]
                elif health < 30:
                    env_tags = ["危险", "威胁", "警戒", "避免"]
                else:
                    env_tags = ["开", "中", "探索", "安全"]

            environment = SymbolicElement(
                symbol_id="",
                symbol_type=SymbolType.ENVIRONMENT,
                content=env_content,
                abstraction_level=AbstractionLevel.CATEGORY,
                semantic_tags=env_tags
            )
            
            # 创建对象符号元素
            # 🔧 安全的字段提"
            if isinstance(experience_dict, dict):
                action_data = experience_dict.get('action', {})
                if isinstance(action_data, dict):
                    obj = experience_dict.get('object', action_data.get('type', 'unknown'))
                else:
                    obj = experience_dict.get('object', 'unknown')
            else:
                obj = 'unknown'
                
            if obj == 'plant' or obj == 'edible_plant':
                obj_content = "可食用植"
                obj_tags = ["植物", "可食", "营养", "资源"]
            elif obj == 'dangerous_animal':
                obj_content = "危险动物"
                obj_tags = ["动物", "危险", "威胁", "猎食者"]
            elif obj == 'water':
                obj_content = "水源"
                obj_tags = ["", "资源", "生存必需", "补给"]
            elif obj == 'poisonous_plant':
                obj_content = "有毒植物"
                obj_tags = ["植物", "有毒", "危险", "陷阱"]
            else:
                obj_content = "未知资源"
                obj_tags = ["未知", "资源", "探索"]
            
            object_elem = SymbolicElement(
                symbol_id="",
                symbol_type=SymbolType.OBJECT,
                content=obj_content,
                abstraction_level=AbstractionLevel.CATEGORY,
                semantic_tags=obj_tags
            )
            
            # 创建对象特征符号元素
            # 🔧 安全的特征数据提"
            if isinstance(experience_dict, dict):
                char_data = experience_dict.get('characteristics', {})
                if isinstance(char_data, dict):
                    distance = char_data.get('distance', 1.0)
                    edible = char_data.get('edible', obj in ['plant', 'edible_plant'])
                    poisonous = char_data.get('poisonous', obj == 'poisonous_plant')
                    dangerous = char_data.get('dangerous', obj == 'dangerous_animal')
                else:
                    distance = 1.0
                    edible = obj in ['plant', 'edible_plant']
                    poisonous = obj == 'poisonous_plant'
                    dangerous = obj == 'dangerous_animal'
            else:
                distance = 1.0
                edible = False
                poisonous = False
                dangerous = False
            
            # 构建特征描述
            char_features = []
            if distance <= 1:
                char_features.append("近距离")
            elif distance <= 3:
                char_features.append("中距离")
            else:
                char_features.append("远距离")
                
            if edible:
                char_features.extend(["可食", "营养丰富"])
            if poisonous:
                char_features.extend(["有毒", "危险"])
            if dangerous:
                char_features.extend(["攻击", "威胁"])
                
            # 🔧 安全的营养值提"
            if isinstance(char_data, dict):
                nutrition_value = char_data.get('nutrition_value', 10)
            else:
                nutrition_value = 10
                
            if nutrition_value > 15:
                char_features.append("高营养")
            elif nutrition_value > 5:
                char_features.append("中等营养")
            else:
                char_features.append("低营养")
            
            character_elem = SymbolicElement(
                symbol_id="",
                symbol_type=SymbolType.CHARACTER,
                content=", ".join(char_features),
                abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=char_features
            )
            
            # 创建动物符号元素
            # 🔧 安全的动物数据提"
            if isinstance(experience_dict, dict):
                action_data = experience_dict.get('action', {})
                if isinstance(action_data, dict):
                    action_type = action_data.get('type', 'unknown')
                else:
                    action_type = experience_dict.get('action', 'unknown')
            else:
                action_type = 'unknown'
            if action_type in ['collect', 'gather']:
                action_content = "收集资源"
                action_tags = ["收集", "获取", "资源", "主动"]
            elif action_type == 'drink':
                action_content = "饮水"
                action_tags = ["饮水", "补给", "生存", "恢复"]
            elif action_type in ['escape', 'avoid']:
                action_content = "逃避"
                action_tags = ["逃避", "防御", "安全", "被动"]
            elif action_type == 'attack':
                action_content = "攻击"
                action_tags = ["攻击", "战斗", "主动", "风险"]
            elif action_type in ['move', 'move_up', 'move_down', 'move_left', 'move_right']:
                action_content = "移动"
                action_tags = ["移动", "位置变化", "探索", "基础"]
            else:
                action_content = "探索"
                action_tags = ["探索", "发现", "学习", "主动"]
            
            action_elem = SymbolicElement(
                symbol_id="",
                symbol_type=SymbolType.ACTION,
                content=action_content,
                abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=action_tags
            )
            
            # 创建工具符号元素(可选)
            # 🔧 安全的工具数据提"
            if isinstance(experience_dict, dict):
                tool_data = experience_dict.get('tool', {})
                if isinstance(tool_data, dict):
                    tool_content = tool_data.get('name', '徒手')
                else:
                    tool_content = '徒手'
            else:
                tool_data = {}
                tool_content = '徒手'
                
            if tool_data or action_type in ['attack', 'collect']:
                tool_tags = ["工具", "辅助", "效率"]
                if tool_content == '徒手':
                    tool_tags.extend(["基础", "无装备"])
                else:
                    tool_tags.extend(["装备", "增强"])
                    
                tool_elem = SymbolicElement(
                    symbol_id="",
                    symbol_type=SymbolType.TOOL,
                    content=tool_content,
                    abstraction_level=AbstractionLevel.CONCRETE,
                    semantic_tags=tool_tags
                )
            else:
                tool_elem = None
            
            # 创建结果符号元素
            # 🔧 安全的结果数据提"
            if isinstance(experience_dict, dict):
                result_data = experience_dict.get('result', {})
                if isinstance(result_data, dict):
                    success = result_data.get('success', False)
                    reward = result_data.get('reward', 0.0)
                    hp_change = result_data.get('hp_change', result_data.get('health_change', 0))
                    food_change = result_data.get('food_change', 0)
                    water_change = result_data.get('water_change', 0)
                else:
                    success = False
                    reward = 0.0
                    hp_change = 0
                    food_change = 0
                    water_change = 0
            else:
                success = False
                reward = 0.0
                hp_change = 0
                food_change = 0
                water_change = 0
            
            result_features = []
            if success:
                result_features.append("成功")
            else:
                result_features.append("失败")
                
            if reward > 0:
                result_features.append("正向奖励")
            elif reward < 0:
                result_features.append("负向惩罚")
            else:
                result_features.append("中性结果")
                
            if hp_change > 0:
                result_features.append("血量增加")
            elif hp_change < 0:
                result_features.append("血量减少")
                
            if food_change > 0:
                result_features.append("食物增加")
            elif food_change < 0:
                result_features.append("食物减少")
                
            if water_change > 0:
                result_features.append("水分增加")
            elif water_change < 0:
                result_features.append("水分减少")
            
            result_elem = SymbolicElement(
                symbol_id="",
                symbol_type=SymbolType.RESULT,
                content=", ".join(result_features),
                abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=result_features
            )
            
            # 创建EOCATR_Tuple
            # 🔧 安全的置信度提取
            if isinstance(experience_dict, dict):
                confidence = experience_dict.get('confidence', 1.0)
            else:
                confidence = 1.0
                
            eocar_tuple = EOCAR_Tuple(
                environment=environment,
                object=object_elem,
                character=character_elem,
                action=action_elem,
                tool=tool_elem,
                result=result_elem,
                confidence=confidence
            )
            
            return eocar_tuple
            
        except Exception as e:
            if logger:
                logger.log(f"EOCAR转换失败: {str(e)}")
            # 返回一个默认的EOCAR_Tuple
            from symbolic_core_v3 import (
                EOCATR_Tuple as EOCAR_Tuple, 
                SymbolicElement, SymbolType, AbstractionLevel
            )
            
            # 创建默认符号元素
            default_env = SymbolicElement(
                symbol_id="", symbol_type=SymbolType.ENVIRONMENT,
                content="开阔地", abstraction_level=AbstractionLevel.CATEGORY,
                semantic_tags=["开", "中", "探索"]
            )
            default_obj = SymbolicElement(
                symbol_id="", symbol_type=SymbolType.OBJECT,
                content="未知资源", abstraction_level=AbstractionLevel.CATEGORY,
                semantic_tags=["未知", "资源", "探索"]
            )
            default_char = SymbolicElement(
                symbol_id="", symbol_type=SymbolType.CHARACTER,
                content="中距从 未知特征", abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=["中距", "未知特征"]
            )
            default_action = SymbolicElement(
                symbol_id="", symbol_type=SymbolType.ACTION,
                content="探索", abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=["探索", "发现", "学习率", "主动"]
            )
            default_result = SymbolicElement(
                symbol_id="", symbol_type=SymbolType.RESULT,
                content="中性结", abstraction_level=AbstractionLevel.CONCRETE,
                semantic_tags=["中性结"]
            )
            
            return EOCAR_Tuple(
                environment=default_env,
                object=default_obj,
                character=default_char,
                action=default_action,
                tool=None,
                result=default_result,
                confidence=0.5
            )

    def get_bpm_statistics(self) -> dict:
        """获取BPM系统的统计信息"""
        try:
            if hasattr(self, 'bpm') and self.bpm:
                bpm_stats = self.bpm.get_statistics()
                bpm_stats.update(self.knowledge_evolution_stats)
                return bpm_stats
            return {}
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 获取BPM统计失败: {str(e)}")
            return {}
    
    def get_knowledge_quality_report(self) -> dict:
        """获取知识质量报告"""
        try:
            if hasattr(self, 'bpm') and self.bmp:
                bmp_stats = self.bmp.get_statistics()
                
                # 确保knowledge_evolution_stats存在且有必要的键
                if not hasattr(self, 'knowledge_evolution_stats'):
                    self.knowledge_evolution_stats = {
                        'rules_generated': 0, 
                        'rules_validated': 0,
                        'evolution_cycles': 0,
                        'successful_adaptations': 0
                    }
                
                # 安全获取统计数据
                evolution_cycles = self.knowledge_evolution_stats.get('evolution_cycles', 1)
                successful_adaptations = self.knowledge_evolution_stats.get('successful_adaptations', 0)
                
                return {
                    'total_experiences': len(self.eocar_experiences),
                    'total_rules': bmp_stats['current_candidate_rules'] + bmp_stats['current_validated_rules'],
                    'rule_validation_rate': bmp_stats['total_rules_validated'] / max(bmp_stats['total_rules_generated'], 1),
                    'rule_survival_rate': 1 - (bmp_stats['total_rules_pruned'] / max(bmp_stats['total_rules_generated'], 1)),
                    'average_confidence': bmp_stats['average_rule_confidence'],
                    'rule_distribution': bmp_stats['rule_types_distribution'],
                    'quality_distribution': bmp_stats['quality_score_distribution'],
                    'evolution_cycles': evolution_cycles,
                    'successful_adaptations': successful_adaptations,
                    'rules_per_cycle': bmp_stats['total_rules_generated'] / max(evolution_cycles, 1),
                    'knowledge_growth_rate': len(self.eocar_experiences) / max(evolution_cycles, 1)
                }
            return {}
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 获取知识质量报告失败: {str(e)}")
            return {}

    def _get_default_exploration_action(self) -> str:
        """获取默认的探索行动"""
        return random.choice(["up", "down", "left", "right"])
    
    def _build_attention_context(self, game) -> AttentionContext:
        """构建DMHA注意力上下文"""
        # 获取周围资源
        resources_nearby = []
        for plant in game.game_map.plants:
            distance = abs(plant.x - self.x) + abs(plant.y - self.y)  # 曼哈顿距"""
            if distance <= 5:  # 视野范围大
                # 使用植物类型名称而不是name属"
                plant_type = plant.__class__.__name__
                value = 2.0 if plant_type in ["Strawberry", "Mushroom"] else 0.5
                resources_nearby.append({
                    'distance': distance,
                    'value': value,
                    'type': plant_type
                })
        
        # 获取危险动物
        dangers_detected = []
        for animal in game.game_map.animals:
            distance = abs(animal.x - self.x) + abs(animal.y - self.y)
            if distance <= 5:  # 视野范围大
                # 使用动物类型名称
                animal_type = animal.__class__.__name__
                if animal_type in ["Tiger", "BlackBear"]:
                    threat_level = 3.0 if animal_type == "Tiger" else 2.5
                    dangers_detected.append({
                        'distance': distance,
                        'threat_level': threat_level,
                        'type': animal_type
                    })
        
        # 获取社交实体(其他玩家)
        social_entities = []
        for player in game.players:
            if player != self and player.is_alive():
                distance = abs(player.x - self.x) + abs(player.y - self.y)
                if distance <= 5:  # 视野范围大
                    social_value = 1.5 if distance < 3 else 1.0
                    social_entities.append({
                        'distance': distance,
                        'social_value': social_value,
                        'type': player.player_type
                    })
        
        # 获取未探索区"
        unexplored_areas = []
        if not hasattr(self, 'visited_positions'):
            self.visited_positions = set()
        
        self.visited_positions.add((self.x, self.y))  # 记录当前位置
        
        for dx in range(-5, 6):  # 视野范围
            for dy in range(-5, 6):
                check_x = self.x + dx
                check_y = self.y + dy
                if (game.game_map.is_within_bounds(check_x, check_y) and 
                    (check_x, check_y) not in self.visited_positions):
                    distance = abs(dx) + abs(dy)  # 曼哈顿距"
                    if distance > 0:
                        novelty = 2.0 if distance > 3 else 1.0
                        unexplored_areas.append({
                            'distance': distance,
                            'novelty': novelty,
                            'type': 'unexplored'
                        })
        
        # 确定发育阶段
        stage = "infant" if self.life_experience_count < 50 else "adult"
        
        # 构建注意力上下文
        context = AttentionContext(
            resources_nearby=resources_nearby,
            dangers_detected=dangers_detected,
            social_entities=social_entities,
            unexplored_areas=unexplored_areas,
            hp=self.health,
            food=self.food,
            water=self.water,
            development_stage=stage,
            recent_experiences=[],  # 简化版"
            current_goals=['survival', 'exploration']
        )
        
        return context
    
    def _is_attention_compatible(self, decision: str, attention_bias: str) -> bool:
        """检查决策是否与注意力偏向兼容"""
        compatibility_map = {
            "专注资源获取": ["gather", "collect", "移动到资源位置"],
            "优先收集资源": ["gather", "collect"],
            "移动到资源位置": ["move", "gather"],
            "立即脱离危险": ["flee", "escape", "avoid"],
            "准备防御或逃跑": ["flee", "escape", "avoid", "attack"],
            "评估威胁等级": ["wait", "observe"],
            "寻求合作": ["share", "cooperate", "communicate"],
            "主动进行社交": ["share", "cooperate"],
            "深度探索新区域": ["explore", "move"],
            "执行探索行动": ["explore", "move"],
            "计划探索路线": ["explore", "move"]
        }
        
        compatible_actions = compatibility_map.get(attention_bias, [])
        return any(action in decision for action in compatible_actions)
    
    def _apply_attention_bias(self, decision: str, attention_bias: str) -> str:
        """应用注意力偏向到决策"""
        attention_enhancements = {
            "专注资源获取": lambda d: d if "gather" in d else "gather",
            "立即脱离危险": lambda d: "flee" if "move" in d else d,
            "深度探索新区域": lambda d: "explore" if "move" in d else d,
            "寻求合作": lambda d: d  # 社交决策暂时保持原样
        }
        
        enhancement_func = attention_enhancements.get(attention_bias)
        if enhancement_func:
            return enhancement_func(decision)
        
        return decision
    
    def get_dmha_statistics(self) -> dict:
        """获取DMHA统计信息"""
        try:
            return self.dmha.get_statistics()
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 获取DMHA统计失败: {str(e)}")
            return {}
    
    def get_dmha_attention_state(self) -> dict:
        """获取当前DMHA注意力状态"""
        try:
            return self.dmha.get_attention_state()
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 获取DMHA注意力状态失败: {str(e)}")
            return {}
    
    def symbolize_scene(self, game):
        """使用SSM进行场景符号化,返回E-O-C-A-T-R元组列表"""
        self.current_timestamp += 1.0  # 增加时间戳
        # 使用SSM进行符号化
        eocar_tuples = self.ssm.symbolize_scene(game, self)
        
        # 为每个元组设置时间戳
        for eocar in eocar_tuples:
            eocar.timestamp = self.current_timestamp
        
        # 保持向后兼容性,转换为传统格"
        traditional_symbols = []
        for eocar in eocar_tuples:
            symbol = {
                "object": eocar.object.content,
                "position": {"x": 0, "y": 0},  # 默认位置,因为新结构中位置信息在character"
                "characteristics": {
                    "distance": 1.0,  # 默认距离
                    "edible": "可食用" in eocar.character.content,
                    "poisonous": "有毒" in eocar.character.content,
                    "dangerous": "危险" in eocar.character.content,
                    "nutrition_value": 10,  # 默认营养"
                    "water_value": 0,  # 默认水分"
                    "player_type": None,  # 默认玩家类型
                    "health_state": "normal"  # 默认健康状态
                }
            }
            traditional_symbols.append(symbol)
        
        if logger:
                            logger.log(f"SSM符号化完成,处理{len(eocar_tuples)}条经验生成{len(eocar_tuples)}个E-O-C-A-T-R元组,{len(traditional_symbols)}个传统符号")
        
        # 存储当前的E-O-C-A-T-R符号化结果用于决策
        self.current_eocar_scene = eocar_tuples
        
        return traditional_symbols

    def _save_eocar_tuples_to_five_libraries(self, eocar_tuples):
        """将SSM生成的EOCATR元组保存到五库系统"""
        try:
            if not self.five_library_system_active or not self.five_library_system:
                if logger:
                    logger.log(f"{self.name} 五库系统未启用，跳过EOCATR保存")
                return
            
            saved_count = 0
            for eocar_tuple in eocar_tuples:
                try:
                    # 构建经验数据字典
                    experience_data = {
                        'environment': eocar_tuple.environment.content if hasattr(eocar_tuple.environment, 'content') else str(eocar_tuple.environment),
                        'object': eocar_tuple.object.content if hasattr(eocar_tuple.object, 'content') else str(eocar_tuple.object),
                        'characteristics': eocar_tuple.character.content if hasattr(eocar_tuple.character, 'content') else str(eocar_tuple.character),
                        'action': eocar_tuple.action.content if hasattr(eocar_tuple.action, 'content') else str(eocar_tuple.action),
                        'tools': eocar_tuple.tool.content if hasattr(eocar_tuple.tool, 'content') else str(eocar_tuple.tool),
                        'result': eocar_tuple.result.content if hasattr(eocar_tuple.result, 'content') else str(eocar_tuple.result),
                        'success': 'success' in str(eocar_tuple.result).lower(),
                        'player_id': self.name,
                        'timestamp': getattr(eocar_tuple, 'timestamp', time.time()),
                        'source': 'ssm_symbolization'
                    }
                    
                    # 创建EOCATRExperience对象
                    from five_library_system import EOCATRExperience
                    experience_obj = EOCATRExperience(
                        environment=experience_data['environment'],
                        object=experience_data['object'],
                        characteristics=experience_data['characteristics'],
                        action=experience_data['action'],
                        tools=experience_data['tools'],
                        result=experience_data['result'],
                        player_id=experience_data['player_id'],
                        timestamp=experience_data['timestamp'],
                        success=experience_data['success'],
                        metadata={'source': experience_data['source']}
                    )
                    
                    # 保存到直接经验库
                    add_result = self.five_library_system.add_experience_to_direct_library(experience_obj)
                    if add_result['success']:
                        saved_count += 1
                    else:
                        if logger:
                            logger.log(f"{self.name} EOCATR保存失败: {add_result.get('reason', '未知原因')}")
                    
                except Exception as e:
                    if logger:
                        logger.log(f"{self.name} 单个EOCATR元组保存失败: {str(e)}")
            
            if logger:
                logger.log(f"{self.name} 💾 SSM成功保存{saved_count}/{len(eocar_tuples)}个EOCATR元组到五库系统")
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ EOCATR元组批量保存失败: {str(e)}")
    
    def add_unified_experience(self, action_data: Any, state_before: dict = None, 
                              state_after: dict = None, result_data: dict = None, 
                              experience_type: str = "direct") -> UnifiedExperience:
        """添加统一格式的经验"""
        try:
            # 生成经验ID
            experience_id = f"{self.name}_exp_{int(time.time() * 1000)}_{len(self.unified_experiences)}"
            
            # 转换动物为统一格式
            unified_action = self.data_format_unifier.convert_action_to_unified(action_data)
            
            # 转换状态为统一格式
            if state_before is None:
                state_before = self._get_current_state_dict()
            if state_after is None:
                state_after = self._get_current_state_dict()
            
            unified_state_before = self.data_format_unifier.convert_state_to_unified(state_before)
            unified_state_after = self.data_format_unifier.convert_state_to_unified(state_after)
            
            # 转换结果为统一格式
            if result_data is None:
                result_data = {"success": True, "effects": {}}
            
            unified_result = UnifiedResult(
                success=result_data.get("success", True),
                effects=result_data.get("effects", {}),
                rewards=result_data.get("rewards", {})
            )
            
            # 创建统一经验
            unified_experience = UnifiedExperience(
                experience_id=experience_id,
                action=unified_action,
                state_before=unified_state_before,
                state_after=unified_state_after,
                result=unified_result,
                experience_type=ExperienceType(experience_type) if experience_type in [e.value for e in ExperienceType] else ExperienceType.DIRECT,
                importance=0.5,
                tags=[experience_type, unified_action.action_type.value]
            )
            
            # 添加到统一经验库
            self.unified_experiences.append(unified_experience)
            
            # 维护容量限制
            if len(self.unified_experiences) > self.max_unified_experiences:
                self.unified_experiences.pop(0)  # 移除最旧的经验
            
            # 更新统计
            self.format_conversion_stats['successful_conversions'] += 1
            self.format_conversion_stats['total_conversions'] += 1
            
            if logger:
                logger.log(f"{self.name} 添加统一经验: {unified_action.action_type.value}")
            
            return unified_experience
            
        except Exception as e:
            self.format_conversion_stats['total_conversions'] += 1
            if logger:
                logger.log(f"{self.name} 统一经验添加失败: {str(e)}")
            
            # 返回默认经验
            return UnifiedExperience(
                experience_id="failed_exp",
                action=UnifiedAction(ActionType.UNKNOWN),
                state_before=UnifiedState(),
                state_after=UnifiedState(),
                result=UnifiedResult(success=False)
            )
    
    def _get_current_state_dict(self) -> dict:
        """获取当前状态的字典表示"""
        return {
            "health": self.health,
            "food": self.food,
            "water": self.water,
            "x": self.x,
            "y": self.y,
            "phase": self.phase,
            "development_stage": self.developmental_stage,
            "survival_days": getattr(self, 'survival_days', 0),
            "reputation": getattr(self, 'reputation', 0)
        }
    
    def convert_legacy_experience_to_unified(self, legacy_exp: dict) -> UnifiedExperience:
        """将传统格式经验转换为统一格式"""
        try:
            # 更新格式统计
            self.format_conversion_stats['format_types_encountered'].add('legacy_dict')
            
            unified_exp = self.data_format_unifier.convert_experience_to_unified(legacy_exp)
            
            # 验证转换结果
            if self.data_format_unifier.validate_unified_data(unified_exp):
                self.format_conversion_stats['successful_conversions'] += 1
                if logger:
                    logger.log(f"{self.name} 成功转换传统经验为统一格式")
            else:
                if logger:
                    logger.log(f"{self.name} 传统经验转换验证失败")
            
            self.format_conversion_stats['total_conversions'] += 1
            return unified_exp
            
        except Exception as e:
            self.format_conversion_stats['total_conversions'] += 1
            if logger:
                logger.log(f"{self.name} 传统经验转换失败: {str(e)}")
            return UnifiedExperience(
                experience_id="conversion_failed",
                action=UnifiedAction(ActionType.UNKNOWN),
                state_before=UnifiedState(),
                state_after=UnifiedState(),
                result=UnifiedResult(success=False)
            )
    
    def convert_eocar_to_unified(self, eocar_tuple) -> UnifiedExperience:
        """将EOCAR格式转换为统一格式"""
        try:
            # 更新格式统计
            self.format_conversion_stats['format_types_encountered'].add('eocar_tuple')
            
            unified_exp = self.data_format_unifier.convert_eocar_to_unified(eocar_tuple)
            
            # 验证转换结果
            if self.data_format_unifier.validate_unified_data(unified_exp):
                self.format_conversion_stats['successful_conversions'] += 1
                if logger:
                    logger.log(f"{self.name} 成功转换EOCATR经验为统一格式")
            
            self.format_conversion_stats['total_conversions'] += 1
            return unified_exp
            
        except Exception as e:
            self.format_conversion_stats['total_conversions'] += 1
            if logger:
                logger.log(f"{self.name} EOCATR经验转换失败: {str(e)}")
            return UnifiedExperience(
                experience_id="eocar_conversion_failed",
                action=UnifiedAction(ActionType.UNKNOWN),
                state_before=UnifiedState(),
                state_after=UnifiedState(),
                result=UnifiedResult(success=False)
            )
    
    def get_unified_experiences_by_action(self, action_type: ActionType) -> List[UnifiedExperience]:
        """根据动物类型获取统一格式经验库"""
        return [exp for exp in self.unified_experiences if exp.action.action_type == action_type]
    
    def get_unified_experiences_by_success(self, success: bool) -> List[UnifiedExperience]:
        """根据成功状态获取统一格式经验库"""
        return [exp for exp in self.unified_experiences if exp.result.success == success]
    
    def get_data_format_statistics(self) -> dict:
        """获取数据格式统计信息"""
        unifier_stats = self.data_format_unifier.get_conversion_statistics()
        
        return {
            "unified_experiences_count": len(self.unified_experiences),
            "max_unified_capacity": self.max_unified_experiences,
            "local_conversion_stats": self.format_conversion_stats,
            "unifier_conversion_stats": unifier_stats,
            "format_types_encountered": list(self.format_conversion_stats['format_types_encountered']),
            "conversion_success_rate": (
                self.format_conversion_stats['successful_conversions'] / 
                max(self.format_conversion_stats['total_conversions'], 1)
            )
        }
    
    def validate_data_format_consistency(self) -> dict:
        """验证数据格式一致性"""
        validation_results = {
            "total_checked": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "validation_errors": [],
            "consistency_score": 0.0
        }
        
        try:
            # 检查统一经验库
            for i, exp in enumerate(self.unified_experiences):
                validation_results["total_checked"] += 1
                
                if self.data_format_unifier.validate_unified_data(exp):
                    validation_results["valid_count"] += 1
                else:
                    validation_results["invalid_count"] += 1
                    validation_results["validation_errors"].append(f"经验{i}: 格式无效")
            
            # 计算一致性分"
            if validation_results["total_checked"] > 0:
                validation_results["consistency_score"] = (
                    validation_results["valid_count"] / validation_results["total_checked"]
                )
            
            if logger:
                logger.log(f"{self.name} 数据格式一致性检查完从 {validation_results['consistency_score']:.2f}")
            
        except Exception as e:
            validation_results["validation_errors"].append(f"验证过程错误: {str(e)}")
            if logger:
                logger.log(f"{self.name} 数据格式验证失败: {str(e)}")
        
        return validation_results

    def _build_emrs_action_result(self, action, previous_state):
        """构建EMRS系统所需的action_result参数"""
        current_state = self._get_current_state_dict()
        
        action_result = {
            'action_type': str(action),
            'success': True,  # 默认成功,具体根据实际情况调整
        }
        
        # 计算状态变化
        if previous_state:
            health_change = current_state.get('health', 100) - previous_state.get('health', 100)
            food_change = current_state.get('food', 50) - previous_state.get('food', 50)
            water_change = current_state.get('water', 50) - previous_state.get('water', 50)
            
            if health_change != 0:
                action_result['health_change'] = health_change
            if food_change > 0:
                action_result['food_gained'] = food_change
            if water_change > 0:
                action_result['water_gained'] = water_change
        
        # 根据动物类型添加特定信息
        if action == 'collect':
            action_result['resource_collected'] = True
            action_result['food_gained'] = action_result.get('food_gained', 5)
        elif action == 'attack':
            action_result['damage_dealt'] = 10
            action_result['combat_success'] = True
        elif action == 'flee':
            action_result['escape_success'] = True
            action_result['safety_gained'] = True
        elif action in ['move_up', 'move_down', 'move_left', 'move_right']:
            action_result['exploration_progress'] = 1
            action_result['new_areas_discovered'] = 1 if (self.x, self.y) not in self.visited_positions else 0
        
        return action_result
    
    def _build_emrs_context(self, game):
        """构建EMRS系统所需的context参数"""
        return {
            'current_health': self.health,
            'current_food': self.food,
            'current_water': self.water,
            'position': (self.x, self.y),
            'phase': self.phase,
            'development_stage': getattr(self, 'developmental_stage', 'child'),
            'current_day': getattr(game, 'current_day', 1),
            'threats_nearby': len(self.detect_threats(game.game_map)),
            'resources_nearby': len([plant for plant in game.game_map.plants if 
                                   abs(plant.x - self.x) + abs(plant.y - self.y) <= 2]),
            'survival_days': self.survival_days,
            'reputation': getattr(self, 'reputation', 0),
            'energy_level': (self.health + self.food + self.water) / 3.0
        }
    
    def _get_current_development_stage(self):
        """获取当前发育阶段"""
        if hasattr(self, 'developmental_stage'):
            return self.developmental_stage
        elif hasattr(self, 'age'):
            if self.age < 10:
                return 'infant'
            elif self.age < 50:
                return 'child'
            elif self.age < 150:
                return 'adolescent'
            else:
                return 'adult'
        else:
            return 'child'

    def _update_validated_rules(self, updated_rule):
        """更新已验证规律库"""
        try:
            rule_id = updated_rule.get('rule_id', '')
            confidence = updated_rule.get('confidence', 0.0)
            
            # 查找并更新现有规"""
            for i, existing_rule in enumerate(self.validated_rules):
                if existing_rule.get('rule_id') == rule_id:
                    self.validated_rules[i] = updated_rule
                    break
            else:
                # 如果是新规律,添加到库中
                self.validated_rules.append(updated_rule)
            
            # 更新置信度统"
            if confidence >= 0.8:
                self.validation_stats['high_confidence_rules'] += 1
            elif confidence >= 0.5:
                self.validation_stats['medium_confidence_rules'] += 1
            else:
                self.validation_stats['low_confidence_rules'] += 1
            
            # 限制规律库大小,保留高置信度规律
            if len(self.validated_rules) > 100:
                self.validated_rules.sort(key=lambda x: x.get('confidence', 0.0), reverse=True)
                self.validated_rules = self.validated_rules[:80]  # 保留80个高置信度规律
        except Exception as e:
            if logger:
                logger.log(f"更新已验证规律库失败: {str(e)}")

    def get_validated_rules_for_action_suggestion(self, current_context=None):
        """获取用于行动建议的高置信度规律"""
        try:
            if not hasattr(self, 'validated_rules') or not self.validated_rules:
                return []
            
            # 筛选高置信度规律
            high_confidence_rules = [
                rule for rule in self.validated_rules 
                if rule.get('confidence', 0.0) >= 0.7
            ]
            
            # 如果有上下文,进一步筛选相关规"
            if current_context:
                relevant_rules = []
                for rule in high_confidence_rules:
                    # 简单的上下文匹配(可以后续增强"
                    rule_context = rule.get('context', {})
                    if self._is_context_relevant(rule_context, current_context):
                        relevant_rules.append(rule)
                return relevant_rules
            
            return high_confidence_rules
            
        except Exception as e:
            if logger:
                logger.log(f"获取验证规律失败: {str(e)}")
            return []

    def _is_context_relevant(self, rule_context, current_context):
        """判断规律上下文是否与当前上下文相关"""
        try:
            # 简单的相关性检"""
            if not rule_context or not current_context:
                return False
            
            # 检查健康状态相关"
            rule_health = rule_context.get('health_level', '')
            current_health = current_context.get('health_level', '')
            if rule_health and current_health and rule_health == current_health:
                return True
            
            # 检查资源状态相关"
            rule_resources = rule_context.get('resource_status', '')
            current_resources = current_context.get('resource_status', '')
            if rule_resources and current_resources and rule_resources == current_resources:
                return True
            
            # 检查环境相关"
            rule_environment = rule_context.get('environment', '')
            current_environment = current_context.get('environment', '')
            if rule_environment and current_environment and rule_environment == current_environment:
                return True
            
            return False
            
        except Exception as e:
            if logger:
                logger.log(f"上下文相关性检查失从 {str(e)}")
            return False

    def _get_current_environment_type(self, game):
        """获取当前环境类型"""
        try:
            if not game or not hasattr(game, 'game_map'):
                return 'unknown'
            
            current_cell = game.game_map.grid[self.y][self.x]
            
            # 检查是否在水源附近
            if current_cell in ['river', 'puddle']:
                return 'water_area'
            
            # 检查是否在危险区域(附近有猛兽"""
            threats = self.detect_threats(game.game_map)
            if threats:
                return 'dangerous_zone'
            
            # 检查其他环境类"
            if current_cell == 'cave':
                return 'shelter'
            elif current_cell == 'big_tree':
                return 'forest'
            elif current_cell == 'bush':
                return 'vegetation'
            else:
                return 'open_field'
                
        except Exception as e:
            if logger:
                logger.log(f"获取环境类型失败: {str(e)}")
            return 'unknown'

    def _get_current_environment_detailed(self, context=None):
        """获取当前环境详细信息"""
        try:
            # 基础环境类型
            env_type = getattr(self, '_last_environment_type', 'open_field')
            
            # 从上下文获取更多信息
            if context and isinstance(context, dict):
                if 'environment' in context:
                    env_type = context['environment']
                elif 'position' in context:
                    # 基于位置推断环境
                    x, y = context['position']
                    if hasattr(self, 'game_map'):
                        cell = self.game_map.grid[y][x] if 0 <= x < len(self.game_map.grid[0]) and 0 <= y < len(self.game_map.grid) else 'open_field'
                        if cell == 'river':
                            env_type = 'water_area'
                        elif cell == 'cave':
                            env_type = 'shelter'
                        elif cell == 'big_tree':
                            env_type = 'forest'
                        elif cell == 'bush':
                            env_type = 'vegetation'
                        else:
                            env_type = 'open_field'
            
            return env_type
            
        except Exception as e:
            if logger:
                logger.log(f"获取详细环境信息失败: {str(e)}")
            return 'open_field'

    def _get_current_object_detailed(self, context=None):
        """获取当前对象详细信息"""
        try:
            # 从上下文获取对象信息
            if context and isinstance(context, dict):
                if 'target_object' in context:
                    return context['target_object']
                elif 'collected_object' in context:
                    return context['collected_object']
                elif 'encountered_object' in context:
                    return context['encountered_object']
            
            # 默认返回未知对象
            return 'unknown'
            
        except Exception as e:
            if logger:
                logger.log(f"获取详细对象信息失败: {str(e)}")
            return 'unknown'

    def _get_current_characteristics_detailed(self, context=None):
        """获取当前特征详细信息"""
        try:
            characteristics = []
            
            # 从上下文获取特征信息
            if context and isinstance(context, dict):
                if 'object_characteristics' in context:
                    characteristics.append(context['object_characteristics'])
                if 'environment_characteristics' in context:
                    characteristics.append(context['environment_characteristics'])
                if 'action_characteristics' in context:
                    characteristics.append(context['action_characteristics'])
            
            # 基于当前状态推断特征
            if self.health < 50:
                characteristics.append('low_health')
            if self.food < 30:
                characteristics.append('low_food')
            if self.water < 30:
                characteristics.append('low_water')
            
            return ','.join(characteristics) if characteristics else 'normal'
            
        except Exception as e:
            if logger:
                logger.log(f"获取详细特征信息失败: {str(e)}")
            return 'normal'

    def _get_current_tools_detailed(self, context=None):
        """获取当前工具详细信息 - 修复版本：返回实际使用的单个工具"""
        try:
            # 🔧 核心修复：优先从上下文获取实际使用的工具
            if context and isinstance(context, dict):
                if 'tool_used' in context:
                    return context['tool_used']
                elif 'selected_tool' in context:
                    return context['selected_tool']
                elif 'active_tool' in context:
                    return context['active_tool']
                elif 'current_tool' in context:
                    return context['current_tool']
                elif 'available_tools' in context:
                    tools = context['available_tools']
                    return tools[0] if tools else 'none'
            
            # 🔧 修复：检查是否有当前选中的工具
            if hasattr(self, 'current_selected_tool') and self.current_selected_tool:
                if hasattr(self.current_selected_tool, 'name'):
                    return self.current_selected_tool.name
                elif hasattr(self.current_selected_tool, 'type'):
                    return self.current_selected_tool.type
                else:
                    return str(self.current_selected_tool)
            
            # 🔧 修复：检查是否有最近使用的工具记录
            if hasattr(self, '_last_used_tool') and self._last_used_tool:
                return self._last_used_tool
            
            # 🔧 修复：如果没有具体工具使用记录，返回"none"而不是全工具列表
            # 这样可以避免"全工具套餐"的问题
            return 'none'
            
        except Exception as e:
            if logger:
                logger.log(f"获取详细工具信息失败: {str(e)}")
            return 'none'

    def _enhance_result_detailed(self, result, action, context=None):
        """增强结果详细信息，生成具体的结果描述"""
        try:
            if not result:
                return 'unknown_result'
            
            # 如果result已经是字典，提取具体信息
            if isinstance(result, dict):
                result_parts = []
                
                # 优先处理具体的数值变化
                if 'hp_change' in result and result['hp_change'] != 0:
                    change = result['hp_change']
                    if change > 0:
                        result_parts.append(f"血量+{change}")
                    else:
                        result_parts.append(f"血量{change}")
                
                if 'food_change' in result and result['food_change'] != 0:
                    change = result['food_change']
                    if change > 0:
                        result_parts.append(f"食物+{change}")
                    else:
                        result_parts.append(f"食物{change}")
                
                if 'water_change' in result and result['water_change'] != 0:
                    change = result['water_change']
                    if change > 0:
                        result_parts.append(f"水分+{change}")
                    else:
                        result_parts.append(f"水分{change}")
                
                if 'position_change' in result:
                    pos_change = result['position_change']
                    if pos_change != (0, 0):
                        result_parts.append("位置改变")
                
                # 处理其他变化类型（向后兼容）
                if 'health_change' in result and result['health_change'] != 0:
                    change = result['health_change']
                    if change > 0:
                        result_parts.append(f"血量+{change}")
                    else:
                        result_parts.append(f"血量{change}")
                
                if 'item_gained' in result:
                    result_parts.append(f"获得{result['item_gained']}")
                
                if 'damage_dealt' in result and result['damage_dealt'] > 0:
                    result_parts.append(f"造成{result['damage_dealt']}伤害")
                
                # 如果有具体变化，返回变化描述
                if result_parts:
                    return ','.join(result_parts)
                
                # 如果没有具体变化但有成功状态，返回成功/失败
                if 'success' in result:
                    return 'success' if result['success'] else 'failure'
                
                return 'no_change'
            
            # 如果result是字符串，尝试增强
            result_str = str(result).lower()
            
            # 基于动作类型和结果状态生成具体描述
            action_str = str(action).lower()
            if 'success' in result_str:
                if any(word in action_str for word in ['collect', 'gather', '采集', '收集']):
                    return '获得资源'
                elif any(word in action_str for word in ['move', 'up', 'down', 'left', 'right', '移动']):
                    return '位置改变'
                elif any(word in action_str for word in ['attack', '攻击']):
                    return '造成伤害'
                elif any(word in action_str for word in ['drink', '喝水']):
                    return '水分增加'
                elif any(word in action_str for word in ['explore', '探索']):
                    return '发现信息'
                else:
                    return 'success'
            elif 'fail' in result_str:
                return 'failure'
            
            return result_str
            
        except Exception as e:
            if logger:
                logger.log(f"增强结果详细信息失败: {str(e)}")
            return str(result) if result else 'unknown_result'

    def _select_and_use_tool_for_action(self, action, target_type, context=None):
        """为特定行动选择并使用工具 - 新增核心函数"""
        try:
            # 1. 根据目标类型选择最佳工具
            selected_tool = self._select_best_tool_for_target(target_type)
            
            if selected_tool:
                # 2. 设置当前选中的工具
                self.current_selected_tool = selected_tool
                self._last_used_tool = selected_tool.name if hasattr(selected_tool, 'name') else str(selected_tool)
                
                # 3. 更新上下文信息
                if context is None:
                    context = {}
                context['tool_used'] = self._last_used_tool
                context['selected_tool'] = self._last_used_tool
                context['active_tool'] = self._last_used_tool
                
                if self.logger:
                    self.logger.log(f"{self.name} 🔧 选择工具: {self._last_used_tool} 用于 {target_type}")
                
                return selected_tool, context
            else:
                # 4. 没有合适工具时，记录徒手操作
                self.current_selected_tool = None
                self._last_used_tool = 'hand'
                
                if context is None:
                    context = {}
                context['tool_used'] = 'hand'
                context['selected_tool'] = 'hand'
                
                if self.logger:
                    self.logger.log(f"{self.name} ✋ 徒手操作: {action} 针对 {target_type}")
                
                return None, context
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具选择失败: {str(e)}")
            return None, context

    def _select_best_tool_for_target(self, target_type):
        """为目标选择最佳工具 - 智能选择算法"""
        try:
            if not hasattr(self, 'tools') or not self.tools:
                return None
            
            # 🔧 核心修复：基于学习经验选择单个最佳工具
            if hasattr(self, 'tool_effectiveness') and self.tool_effectiveness:
                best_tool = None
                best_effectiveness = -1
                
                for tool in self.tools:
                    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                    key = (tool_name, target_type)
                    
                    if key in self.tool_effectiveness:
                        data = self.tool_effectiveness[key]
                        effectiveness = data.get('effectiveness', 0)
                        attempts = data.get('attempts', 0)
                        
                        # 只考虑有足够尝试次数的工具
                        if attempts >= 2 and effectiveness > best_effectiveness:
                            best_effectiveness = effectiveness
                            best_tool = tool
                
                if best_tool:
                    return best_tool
            
            # 🔧 回退到基于目标类型的预设映射
            tool_target_mapping = {
                'predator': ['Spear', '长矛'],  # 猛兽用长矛
                'prey': ['Stone', '石头'],      # 猎物用石头
                'bird': ['Bow', '弓箭'],        # 鸟类用弓箭
                'ground_plant': ['Basket', '篮子'],      # 地面植物用篮子
                'underground_plant': ['Shovel', '铁锹'], # 地下植物用铁锹
                'tree_plant': ['Stick', '棍子']          # 树上植物用棍子
            }
            
            preferred_tools = tool_target_mapping.get(target_type, [])
            
            # 寻找匹配的工具
            for tool in self.tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                tool_type = getattr(tool, 'type', tool_name)
                
                if tool_name in preferred_tools or tool_type in preferred_tools:
                    return tool
            
            # 🔧 如果没有理想工具，进行探索性选择
            return self._select_tool_for_exploration(target_type)
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具选择算法失败: {str(e)}")
            return None

    def _select_tool_for_exploration(self, target_type):
        """探索性工具选择 - 优先选择尝试次数少的工具"""
        try:
            if not hasattr(self, 'tools') or not self.tools:
                return None
            
            # 统计每个工具对该目标的尝试次数
            tool_attempts = []
            for tool in self.tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                key = (tool_name, target_type)
                attempts = self.tool_effectiveness.get(key, {}).get('attempts', 0)
                tool_attempts.append((tool, attempts))
            
            # 按尝试次数排序，优先选择尝试次数少的
            tool_attempts.sort(key=lambda x: x[1])
            
            # 从尝试次数最少的工具中随机选择一个
            min_attempts = tool_attempts[0][1]
            least_tried_tools = [tool for tool, attempts in tool_attempts if attempts == min_attempts]
            
            import random
            return random.choice(least_tried_tools)
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 探索性工具选择失败: {str(e)}")
            return self.tools[0] if self.tools else None

    def _record_tool_usage_result(self, tool, target_type, action, success, benefit=0):
        """记录工具使用结果 - 用于学习"""
        try:
            if not tool:
                return
            
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            key = (tool_name, target_type)
            
            # 初始化记录
            if key not in self.tool_effectiveness:
                self.tool_effectiveness[key] = {
                    'attempts': 0,
                    'successes': 0,
                    'effectiveness': 0.0,
                    'total_benefit': 0
                }
            
            # 更新记录
            data = self.tool_effectiveness[key]
            data['attempts'] += 1
            if success:
                data['successes'] += 1
                data['total_benefit'] += benefit
            
            # 重新计算效果值
            data['effectiveness'] = data['successes'] / data['attempts'] if data['attempts'] > 0 else 0
            
            # 添加到使用历史
            if not hasattr(self, 'tool_usage_history'):
                self.tool_usage_history = []
            
            self.tool_usage_history.append({
                'tool_name': tool_name,
                'target_type': target_type,
                'action': action,
                'success': success,
                'benefit': benefit,
                'timestamp': len(self.tool_usage_history)
            })
            
            if self.logger:
                self.logger.log(f"{self.name} 🔧 工具使用记录: {tool_name}→{target_type} "
                              f"成功率:{data['effectiveness']:.2f} "
                              f"({data['successes']}/{data['attempts']})")
                              
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具使用记录失败: {str(e)}")

    def _determine_plant_type(self, plant):
        """确定植物类型用于工具选择"""
        try:
            plant_class = plant.__class__.__name__
            
            # 根据植物特性确定类型
            if hasattr(plant, 'location_type'):
                if plant.location_type == "underground":
                    return 'underground_plant'
                elif plant.location_type == "tree":
                    return 'tree_plant'
                else:
                    return 'ground_plant'
            else:
                # 根据植物类名推断
                if plant_class in ['Potato', 'SweetPotato', 'Carrot']:
                    return 'underground_plant'
                elif plant_class in ['Acorn', 'Chestnut', 'Apple']:
                    return 'tree_plant'
                else:
                    return 'ground_plant'
                    
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 植物类型确定失败: {str(e)}")
            return 'ground_plant'

    def _determine_animal_type(self, animal):
        """确定动物类型用于工具选择"""
        try:
            animal_class = animal.__class__.__name__
            
            # 根据动物特性确定类型
            if hasattr(animal, 'is_predator') and animal.is_predator:
                return 'predator'
            elif animal_class in ['Tiger', 'BlackBear']:
                return 'predator'
            elif animal_class in ['Pheasant', 'Dove']:
                return 'bird'
            elif animal_class in ['Rabbit', 'Boar']:
                return 'prey'
            else:
                # 默认根据攻击力判断
                if hasattr(animal, 'attack') and animal.attack > 20:
                    return 'predator'
                else:
                    return 'prey'
                    
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 动物类型确定失败: {str(e)}")
            return 'prey'

    def _evaluate_action_success(self, action, result, context=None):
        """评估动作成功性"""
        try:
            if isinstance(result, dict):
                return result.get('success', True)
            
            result_str = str(result).lower()
            return 'success' in result_str or 'gained' in result_str or 'collected' in result_str
            
        except Exception as e:
            return True

    def _classify_action_type(self, action):
        """分类动作类型"""
        try:
            action_str = str(action).lower()
            
            if any(word in action_str for word in ['collect', 'gather', 'harvest']):
                return 'collection'
            elif any(word in action_str for word in ['move', 'up', 'down', 'left', 'right']):
                return 'movement'
            elif any(word in action_str for word in ['attack', 'hunt', 'fight']):
                return 'combat'
            elif any(word in action_str for word in ['explore', 'search', 'investigate']):
                return 'exploration'
            elif any(word in action_str for word in ['drink', 'eat', 'consume']):
                return 'consumption'
            else:
                return 'other'
                
        except Exception as e:
            return 'unknown'

    def _is_action_executable(self, action, game):
        """检查建议的行动是否可执行"""
        try:
            if not action or not game:
                return False
            
            # 检查移动行"""
            if action in ['move_up', 'move_down', 'move_left', 'move_right']:
                direction_map = {
                    'move_up': (0, -1),
                    'move_down': (0, 1),
                    'move_left': (-1, 0),
                    'move_right': (1, 0)
                }
                dx, dy = direction_map[action]
                new_x, new_y = self.x + dx, self.y + dy
                return game.game_map.is_within_bounds(new_x, new_y)
            
            # 检查饮水行"
            elif action == 'drink_water':
                current_cell = game.game_map.grid[self.y][self.x]
                return current_cell in ['river', 'puddle']
            
            # 检查采集行"
            elif action in ['collect_plant', 'gather_food']:
                for plant in game.game_map.plants:
                    if (plant.x == self.x and plant.y == self.y and 
                        plant.alive and not plant.collected):
                        return True
                return False
            
            # 检查攻击行"
            elif action == 'attack_animal':
                for animal in game.game_map.animals:
                    if (animal.alive and 
                        abs(animal.x - self.x) <= 1 and abs(animal.y - self.y) <= 1):
                        return True
                return False
            
            # 检查逃跑行动
            elif action in ['escape', 'flee']:
                threats = self.detect_threats(game.game_map)
                return len(threats) > 0
            
            # 默认认为其他行动可执"
            return True
            
        except Exception as e:
            if logger:
                logger.log(f"检查行动可执行性失从 {str(e)}")
            return False

    # 在ILAI类中添加CDL探索方法,在_trigger_exploration_learning方法之后添加
    def _execute_cdl_exploration_move(self, game):
        """执行CDL探索性移动"""
        try:
            # 寻找新颖的、未访问过的位置
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            import random
            random.shuffle(directions)
            
            # 初始化访问位置记录(如果不存在)
            if not hasattr(self, 'visited_positions'):
                self.visited_positions = set()
            
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if (game.game_map.is_within_bounds(new_x, new_y) and 
                    (new_x, new_y) not in self.visited_positions):
                    if self.move(dx, dy, game.game_map):
                        if self.logger:
                            self.logger.log(f"{self.name} 🔍 CDL新颖性探索移动到 ({new_x}, {new_y})")
                        return True
            
            # 如果没有完全新的位置,选择访问次数最少的方向
            direction_scores = []
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if game.game_map.is_within_bounds(new_x, new_y):
                    # 计算该方向的"新颖性分数
                    novelty_score = 0
                    if (new_x, new_y) not in self.visited_positions:
                        novelty_score += 10
                    
                    # 检查周围是否有未探索的区域
                    for check_dx in [-1, 0, 1]:
                        for check_dy in [-1, 0, 1]:
                            check_x, check_y = new_x + check_dx, new_y + check_dy
                            if (game.game_map.is_within_bounds(check_x, check_y) and
                                (check_x, check_y) not in self.visited_positions):
                                novelty_score += 1
                    
                    direction_scores.append((dx, dy, novelty_score))
            
            # 选择最高新颖性的方向
            if direction_scores:
                direction_scores.sort(key=lambda x: x[2], reverse=True)
                best_dx, best_dy, _ = direction_scores[0]
                if self.move(best_dx, best_dy, game.game_map):
                    if self.logger:
                        self.logger.log(f"{self.name} 🎯 CDL选择最优探索方法({best_dx}, {best_dy})")
                    return True
            
            return False
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} CDL探索移动失败: {str(e)}")
            return False
    
    def _execute_cdl_info_gathering(self, game):
        """执行CDL信息收集行为 - 🎯 增强：支持生物多样性和工具效能测试"""
        try:
            # 🎯 新增：优先执行高价值探索目标
            high_priority_result = self._execute_high_priority_exploration(game)
            if high_priority_result:
                return high_priority_result
            
            # 优先收集附近的资源或与实体交互
            
            # 🎯 新增:检查附近的动物并尝试攻击(优先级最高)
            for animal in game.game_map.animals:
                if animal.alive and abs(animal.x - self.x) + abs(animal.y - self.y) <= 1:
                    # 只攻击非猛兽类动物(Rabbit, Boar)以避免过高风险
                    if animal.type in ["Rabbit", "Boar"]:
                        old_food = self.food
                        self.attack(animal)
                        if self.food > old_food or not animal.alive:
                            if self.logger:
                                self.logger.log(f"{self.name} 🏹 CDL信息收集:成功攻击{animal.type}")
                            return True
                    # 对于猛兽,只有在食物严重不足时才冒险攻击
                    elif animal.type in ["Tiger", "BlackBear"] and self.food < 50:
                        old_food = self.food
                        self.attack(animal)
                        if self.food > old_food or not animal.alive:
                            if self.logger:
                                self.logger.log(f"{self.name} ⚔️ CDL信息收集:冒险攻击{animal.type}")
                            return True
            
            # 检查附近的植物
            for plant in game.game_map.plants:
                if abs(plant.x - self.x) + abs(plant.y - self.y) <= 1:
                    old_food = self.food
                    self.collect_plant(plant)
                    if self.food > old_food:
                        if self.logger:
                            self.logger.log(f"{self.name} 📊 CDL信息收集:成功采集植物")
                        return True
            
            # 如果在水源位置,补充水分
            current_cell = game.game_map.grid[self.y][self.x]
            if current_cell in ["river", "puddle"] and self.water < 90:
                old_water = self.water
                self.water = min(100, self.water + 30)
                if self.logger:
                    self.logger.log(f"{self.name} 💧 CDL信息收集:补充水分{old_water}->{self.water}")
                return True
            
            # 如果没有直接的收集机会,移动到最近的有价值目标
            best_target = None
            best_distance = float('inf')
            target_type = None
            
            # 🎯 新增:寻找最近的可攻击动物(优先级高于植物)
            for animal in game.game_map.animals:
                if animal.alive:
                    distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                    # 优先考虑安全的猎物
                    if animal.type in ["Rabbit", "Boar"] and distance < best_distance and distance <= 3:
                        best_distance = distance
                        best_target = animal
                        target_type = "animal"
                    # 食物不足时考虑猛兽
                    elif animal.type in ["Tiger", "BlackBear"] and self.food < 40 and distance < best_distance and distance <= 2:
                        best_distance = distance
                        best_target = animal
                        target_type = "predator"
            
            # 寻找最近的植物(作为备选)
            if not best_target:
                for plant in game.game_map.plants:
                    distance = abs(plant.x - self.x) + abs(plant.y - self.y)
                    if distance < best_distance:
                        best_distance = distance
                        best_target = plant
                        target_type = "plant"
            
            # 移动到最佳目标
            if best_target and best_distance <= 5:  # 只有在合理距离内才移动
                dx = 1 if best_target.x > self.x else -1 if best_target.x < self.x else 0
                dy = 1 if best_target.y > self.y else -1 if best_target.y < self.y else 0
                if dx != 0 or dy != 0:
                    if self.move(dx, dy, game.game_map):
                        if self.logger:
                            action_desc = "向动物" if target_type in ["animal", "predator"] else "向植物"
                            self.logger.log(f"{self.name} 🚶 CDL信息收集:{action_desc}移动")
                        return True
            
            return False
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} CDL信息收集失败: {str(e)}")
            return False
    
    def _trigger_knowledge_sync(self):
        """触发知识同步检查- 基于新颖性的同步机制(重构版)"""
        if not hasattr(self, 'global_knowledge_sync') or not self.global_knowledge_sync:
            return 0
        
        sync_count = 0  # 计数本次同步的项目数"""
        try:
            # 🔧 1. 检查五库系统中的新经验(基于新颖性)
            if hasattr(self, 'five_library_system') and self.five_library_system:
                try:
                    # 获取最近的经验进行新颖性检"
                    recent_experiences = self.five_library_system.get_recent_experiences(limit=10)
                    for experience in recent_experiences:
                        # 生成经验哈希检查新颖"
                        exp_hash = self.global_knowledge_sync._generate_experience_hash(experience)
                        
                        # 如果是全新经验(未在全局哈希集合中),触发同"
                        if exp_hash not in self.global_knowledge_sync.synced_experience_hashes:
                            success, msg = self.global_knowledge_sync.sync_new_experience(self, experience)
                            if success:
                                sync_count += 1
                                if logger:
                                    logger.log(f"🌟 {self.name} 发现新颖经验并同从 {msg}")
                                
                                # 🔧 触发BPM怒放阶段(基于新经验发现"
                                self._trigger_bmp_blooming_on_new_experience(experience)
                            break  # 一次只处理一个新经验,避免过度处"
                except Exception as e:
                    if logger:
                        logger.log(f"⚠️ {self.name} 五库经验新颖性检查失从 {str(e)}")
            
            # 🔧 2. 检查五库系统中的新规律(基于新颖性)
            if hasattr(self, 'five_library_system') and self.five_library_system:
                try:
                    # 获取最近的规律进行新颖性检"
                    recent_rules = self.five_library_system.get_recent_rules(limit=5)
                    for rule in recent_rules:
                        # 确定规律类型
                        rule_type = self._classify_rule_type(rule)
                        
                        # 生成规律哈希检查新颖"
                        rule_hash = self.global_knowledge_sync._generate_rule_hash(rule, rule_type)
                        
                        # 如果是全新规律(未在全局哈希集合中),触发同"
                        if rule_hash not in self.global_knowledge_sync.synced_rule_hashes:
                            success, msg = self.global_knowledge_sync.sync_new_rule(self, rule, rule_type)
                            if success:
                                sync_count += 1
                                if logger:
                                    logger.log(f"🏆 {self.name} 发现新颖规律并同从 {msg}")
                            break  # 一次只处理一个新规律
                except Exception as e:
                    if logger:
                        logger.log(f"⚠️ {self.name} 五库规律新颖性检查失从 {str(e)}")
            
            # 🔧 3. 检查EOCATR经验的新颖"
            eocatr_experiences = None
            if hasattr(self, 'eocatr_experiences') and self.eocatr_experiences:
                eocatr_experiences = self.eocatr_experiences
            elif hasattr(self, 'eocar_experiences') and self.eocar_experiences:
                eocatr_experiences = self.eocar_experiences
            
            if eocatr_experiences:
                # 检查最新的EOCATR经验
                latest_experience = eocatr_experiences[-1]
                exp_hash = self.global_knowledge_sync._generate_experience_hash(latest_experience)
                
                if exp_hash not in self.global_knowledge_sync.synced_experience_hashes:
                    success, msg = self.global_knowledge_sync.sync_new_experience(self, latest_experience)
                    if success:
                        sync_count += 1
                        if logger:
                            logger.log(f"🌟 {self.name} 发现新颖EOCATR经验并同步")
                        
                        # 🔧 触发BPM怒放阶段
                        self._trigger_bmp_blooming_on_new_experience(latest_experience)
            
            # 🔧 4. 检查BPM生成的新规律(基于新颖性)
            if hasattr(self, 'bpm') and self.bpm:
                # 尝试多种可能的规律存储属"
                validated_rules = None
                rules_source = None
                
                if hasattr(self.bpm, 'validated_rules') and self.bpm.validated_rules:
                    validated_rules = self.bpm.validated_rules
                    rules_source = 'validated_rules'
                elif hasattr(self.bpm, 'rules') and self.bpm.rules:
                    validated_rules = self.bpm.rules
                    rules_source = 'rules'
                elif hasattr(self.bpm, 'rule_database') and self.bpm.rule_database:
                    validated_rules = self.bpm.rule_database
                    rules_source = 'rule_database'
                
                if validated_rules:
                    # 处理不同的数据结"
                    if isinstance(validated_rules, dict):
                        recent_rules = list(validated_rules.items())[-1:]  # 只检查最新的
                    elif isinstance(validated_rules, list):
                        recent_rules = [(len(validated_rules)-1, validated_rules[-1])]  # 只检查最新的
                    else:
                        recent_rules = []
                    
                    for rule_id, rule_data in recent_rules:
                        # 确定规律类型
                        rule_type = self._classify_rule_type(rule_data)
                        rule_hash = self.global_knowledge_sync._generate_rule_hash(rule_data, rule_type)
                        
                        # 如果是全新规律,触发同步
                        if rule_hash not in self.global_knowledge_sync.synced_rule_hashes:
                            success, msg = self.global_knowledge_sync.sync_new_rule(self, rule_data, rule_type)
                            if success:
                                sync_count += 1
                                if logger:
                                    logger.log(f"🏆 {self.name} 发现新颖BPM规律并同步")
                            break  # 一次只处理一个新规律
            
            # 🎯 记录同步活动统计
            if sync_count > 0:
                # 记录新颖发现
                if hasattr(self, 'increment_novelty_discovery'):
                    for _ in range(sync_count):
                        self.increment_novelty_discovery('experience')
                
                if logger:
                    logger.log(f"📊 {self.name} 本轮发现并同步了 {sync_count} 个新颖知识项目")
            
        except Exception as e:
            if logger:
                logger.log(f"⚠️ {self.name} 新颖性知识同步检查失从 {str(e)}")
        
        return sync_count
    
    def _trigger_bmp_blooming_on_new_experience(self, new_experience):
        """当发现新经验时触发BPM怒放阶段"""
        try:
            if hasattr(self, 'bpm') and self.bpm:
                # 获取历史经验作为上下"""
                historical_experiences = []
                if hasattr(self, 'five_library_system') and self.five_library_system:
                    historical_experiences = self.five_library_system.get_recent_experiences(limit=20)
                
                # 🔧 数据格式转换:确保BPM接收到正确的EOCATR_Tuple格式
                processed_experience = new_experience
                processed_historical = []
                
                # 转换主要经验(支持字符串、字典等多种格式"
                try:
                    processed_experience = self._convert_dict_to_eocar_tuple(new_experience)
                except Exception as conv_e:
                    if logger:
                        logger.log(f"⚠️ {self.name} 经验格式转换失败: {str(conv_e)}, 输入类型: {type(new_experience)}")
                    return  # 转换失败就不处理
                
                # 转换历史经验(支持多种格式)
                for hist_exp in historical_experiences[:10]:  # 限制数量避免过载
                    try:
                        converted_hist = self._convert_dict_to_eocar_tuple(hist_exp)
                        processed_historical.append(converted_hist)
                    except Exception as hist_e:
                        # 转换失败的跳过,但记录日志用于调"
                        if logger and len(processed_historical) == 0:  # 只为第一个失败记录日"
                            logger.log(f"⚠️ {self.name} 历史经验转换失败: 类型{type(hist_exp)}")
                        continue
                
                # 调用BPM处理新经"
                if hasattr(self.bpm, 'process_experience'):
                    # 使用正确格式的数据调用BPM
                    self.bpm.process_experience(processed_experience, processed_historical)
                    if logger:
                        logger.log(f"🌸 {self.name} BPM怒放阶段已激活,基于新经验进行规律挖掘")
                elif hasattr(self.bpm, 'blooming_phase'):
                    # 备用调用方式
                    self.bpm.blooming_phase([processed_experience] + processed_historical)
                    if logger:
                        logger.log(f"🌸 {self.name} BPM怒放阶段已激活(备用方式)")
        except Exception as e:
            if logger:
                logger.log(f"⚠️ {self.name} BPM怒放阶段触发失败: {str(e)}")
    
    def _classify_rule_type(self, rule_data):
        """简单的规律类型分类"""
        rule_str = str(rule_data).lower()
        
        if 'tool' in rule_str and 'target' in rule_str:
            return 'tool_effectiveness_rules'
        elif 'if' in rule_str or 'when' in rule_str:
            return 'causal_rules'
        elif 'behavior' in rule_str or 'action' in rule_str:
            return 'behavioral_rules'
        elif 'environment' in rule_str or 'location' in rule_str:
            return 'environmental_rules'
        else:
            return 'causal_rules'  # 默认分类

    def _determine_decision_stage(self, game):
        """确定当前应该使用的决策阶段"""
        # 获取当前资源状态
        hp = self.hp
        food = self.food
        water = self.water
        
        # 检测威胁距离
        min_threat_distance = self._get_min_threat_distance(game)
        
        # 阶段一：本能决策阶段
        if (hp <= 20 or food <= 20 or water <= 20) or min_threat_distance <= 3:
            trigger_reasons = []
            trigger_type = None
            
            if hp <= 20:
                trigger_reasons.append(f"血量危险({hp})")
                trigger_type = "low_health"
            if food <= 20:
                trigger_reasons.append(f"食物不足({food})")
                trigger_type = "low_food" if not trigger_type else trigger_type
            if water <= 20:
                trigger_reasons.append(f"水分不足({water})")
                trigger_type = "low_water" if not trigger_type else trigger_type
            if min_threat_distance <= 3:
                trigger_reasons.append(f"威胁接近(距离{min_threat_distance})")
                trigger_type = "threat_nearby"
            
            return {
                'stage': 'instinct',
                'reason': '本能层触发条件满足',
                'trigger_reason': ', '.join(trigger_reasons),
                'trigger_type': trigger_type
            }
        
        # 阶段二：DMHA决策阶段
        elif (hp > 20 and hp <= 50) or (food > 20 and food <= 50) or (water > 20 and water <= 50):
            if min_threat_distance > 3:
                return {
                    'stage': 'dmha',
                    'reason': '资源中等，无直接威胁',
                    'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}, 最近威胁距离:{min_threat_distance}',
                    'trigger_type': 'moderate_resources'
                }
        
        # 阶段三：CDL决策阶段
        if hp > 50 and food > 50 and water > 50 and min_threat_distance > 3:
            return {
                'stage': 'cdl',
                'reason': '资源充足，环境安全',
                'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}, 最近威胁距离:{min_threat_distance}',
                'trigger_type': 'abundant_resources'
            }
        
        # 默认使用DMHA阶段
        return {
            'stage': 'dmha',
            'reason': '默认目标导向决策',
            'trigger_reason': f'血量:{hp}, 食物:{food}, 水:{water}, 最近威胁距离:{min_threat_distance}',
            'trigger_type': 'default'
        }
    
    def _get_min_threat_distance(self, game):
        """获取最近威胁的距离"""
        min_distance = float('inf')
        
        for animal in game.game_map.animals:
            if animal.alive and animal.type in ["Tiger", "BlackBear"]:
                distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 999
    
    def _execute_instinct_decision(self, game, trigger_type):
        """执行本能层决策 - 直接响应，不经过复杂机制"""
        try:
            if trigger_type == "threat_nearby":
                # 威胁逃离
                return self._instinct_flee_from_threat(game)
            elif trigger_type == "low_health":
                # 寻找安全地点
                return self._instinct_find_safety(game)
            elif trigger_type == "low_food":
                # 紧急寻找食物
                return self._instinct_find_food(game)
            elif trigger_type == "low_water":
                # 紧急寻找水源
                return self._instinct_find_water(game)
            else:
                # 默认逃离行为
                return self._instinct_flee_from_threat(game)
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 本能决策执行失败: {str(e)}")
            return False
    
    def _instinct_flee_from_threat(self, game):
        """本能逃离威胁"""
        threats = []
        for animal in game.game_map.animals:
            if animal.alive and animal.type in ["Tiger", "BlackBear"]:
                distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                if distance <= 5:  # 扩大检测范围
                    threats.append(animal)
        
        if threats:
            # 计算逃离方向
            escape_direction = self._calculate_escape_direction(threats, game.game_map)
            if escape_direction:
                dx, dy = escape_direction
                if self.move(dx, dy, game.game_map):
                    if logger:
                        logger.log(f"{self.name} 本能逃离威胁成功")
                    return True
        
        # 如果无法逃离，执行随机移动
        self._execute_random_move()
        return True
    
    def _instinct_find_safety(self, game):
        """本能寻找安全地点"""
        # 寻找最近的安全地形
        best_safety_pos = None
        best_safety_score = -1
        
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                new_x, new_y = self.x + dx, self.y + dy
                if game.game_map.is_within_bounds(new_x, new_y):
                    cell_type = game.game_map.grid[new_y][new_x]
                    safety_score = 0
                    
                    if cell_type in ["big_tree", "bush"]:
                        safety_score = 3
                    elif cell_type in ["river", "puddle"]:
                        safety_score = 2
                    elif cell_type == "grass":
                        safety_score = 1
                    
                    if safety_score > best_safety_score:
                        best_safety_score = safety_score
                        best_safety_pos = (new_x, new_y)
        
        if best_safety_pos:
            target_x, target_y = best_safety_pos
            dx = 1 if target_x > self.x else (-1 if target_x < self.x else 0)
            dy = 1 if target_y > self.y else (-1 if target_y < self.y else 0)
            
            if self.move(dx, dy, game.game_map):
                if logger:
                    logger.log(f"{self.name} 本能寻找安全地点")
                return True
        
        return False
    
    def _instinct_find_food(self, game):
        """本能寻找食物"""
        # 寻找最近的食物
        nearest_plant = None
        min_distance = float('inf')
        
        for plant in game.game_map.plants:
            if plant.alive and not plant.collected and not plant.toxic:
                distance = abs(plant.x - self.x) + abs(plant.y - self.y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_plant = plant
        
        if nearest_plant:
            # 直接朝食物移动
            dx = 1 if nearest_plant.x > self.x else (-1 if nearest_plant.x < self.x else 0)
            dy = 1 if nearest_plant.y > self.y else (-1 if nearest_plant.y < self.y else 0)
            
            if self.move(dx, dy, game.game_map):
                if logger:
                    logger.log(f"{self.name} 本能寻找食物")
                
                # 如果到达食物位置，直接采集
                if self.x == nearest_plant.x and self.y == nearest_plant.y:
                    self.collect_plant(nearest_plant)
                return True
        
        return False
    
    def _instinct_find_water(self, game):
        """本能寻找水源"""
        # 寻找最近的水源
        nearest_water = None
        min_distance = float('inf')
        
        for y in range(game.game_map.height):
            for x in range(game.game_map.width):
                if game.game_map.grid[y][x] in ["river", "puddle"]:
                    distance = abs(x - self.x) + abs(y - self.y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_water = (x, y)
        
        if nearest_water:
            target_x, target_y = nearest_water
            dx = 1 if target_x > self.x else (-1 if target_x < self.x else 0)
            dy = 1 if target_y > self.y else (-1 if target_y < self.y else 0)
            
            if self.move(dx, dy, game.game_map):
                if logger:
                    logger.log(f"{self.name} 本能寻找水源")
                return True
        
        return False
    
    def _calculate_escape_direction(self, threats, game_map):
        """计算最优逃跑方向"""
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x = self.x + dx
                new_y = self.y + dy
                if game_map.is_within_bounds(new_x, new_y):
                    safety_score = self._evaluate_position_safety(new_x, new_y, threats, game_map)
                    possible_moves.append((dx, dy, safety_score))
        
        if not possible_moves:
            return None
        
        # 选择安全分数最高的移动方向
        best_move = max(possible_moves, key=lambda x: x[2])
        return (best_move[0], best_move[1])
    
    def _evaluate_position_safety(self, x, y, threats, game_map):
        """评估特定位置的安全程度"""
        safety_score = 100
        
        # 考虑与所有威胁的距离
        for threat in threats:
            dist = abs(x - threat.x) + abs(y - threat.y)
            if dist == 0:
                return 0  # 与威胁重叠，完全不安全
            threat_level = 100 / (dist + 1)  # 距离越近威胁越大
            safety_score -= threat_level
        
        # 考虑地形因素
        if game_map.grid[y][x] in ["big_tree", "bush"]:
            safety_score += 20  # 树木和灌木提供掩护
        elif game_map.grid[y][x] in ["river", "puddle"]:
            safety_score += 10  # 水域提供一定保护
        
        # 考虑是否靠近地图边缘(可能被困)
        if x <= 1 or x >= game_map.width - 2 or y <= 1 or y >= game_map.height - 2:
            safety_score -= 30
        
        return max(0, safety_score)  # 确保安全分数不为负

    def _analyze_current_state(self, game):
        """分析当前状态,判断资源充足性和紧急事件"""
        try:
            # 资源评估
            health_ratio = self.health / 100.0
            food_ratio = self.food / 100.0  
            water_ratio = self.water / 100.0
            
            # 威胁检"""
            threats = self.detect_threats(game.game_map)
            has_immediate_threats = len(threats) > 0
            
            # 资源充足性判从(所有指从> 60%)
            resources_sufficient = (health_ratio > 0.6 and 
                                  food_ratio > 0.6 and 
                                  water_ratio > 0.6)
            
            # 紧急事件判"
            has_emergency = (health_ratio < 0.3 or 
                           food_ratio < 0.2 or 
                           water_ratio < 0.2 or 
                           has_immediate_threats)
            
            # 状态分"
            if resources_sufficient and not has_emergency:
                status = "充足安全"
            elif has_emergency:
                status = "紧急状态"
            else:
                status = "资源不足"
            
            return {
                'status': status,
                'resources_sufficient': resources_sufficient,
                'has_emergency': has_emergency,
                'health_ratio': health_ratio,
                'food_ratio': food_ratio, 
                'water_ratio': water_ratio,
                'threat_count': len(threats),
                'most_urgent_need': self._identify_most_urgent_need()
            }
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 状态分析失从 {str(e)}")
            return {
                'status': "未知",
                'resources_sufficient': False,
                'has_emergency': True,
                'health_ratio': 0.5,
                'food_ratio': 0.5,
                'water_ratio': 0.5,
                'threat_count': 0,
                'most_urgent_need': 'survival'
            }

    def _execute_cdl_exploration_cycle(self, game):
        """执行CDL探索学习循环"""
        try:
            if not (self.cdl_active and hasattr(self, 'curiosity_driven_learning')):
                return None
            
            # 构建CDL上下"""
            from curiosity_driven_learning import ContextState
            
            # 收集环境信息
            nearby_entities = self._collect_nearby_entities(game)
            
            context_state = ContextState(
                symbolized_scene=nearby_entities,
                agent_internal_state={
                    'position': (self.x, self.y),
                    'health': self.health,
                    'food': self.food,
                    'water': self.water,
                    'phase': getattr(self, 'phase', 'exploration'),
                    'developmental_stage': getattr(self, 'developmental_stage', 0.3)
                },
                environmental_factors={
                    'terrain': game.game_map.grid[self.y][self.x],
                    'day': game.current_day,
                    'visited_positions_count': len(getattr(self, 'visited_positions', set()))
                },
                social_context={
                    'nearby_players': [p.name for p in game.players if p != self and abs(p.x - self.x) + abs(p.y - self.y) <= 3]
                },
                timestamp=game.current_day * 24.0
            )
            
            # CDL评估和决"
            cdl_response = self.curiosity_driven_learning.evaluate_novelty_and_curiosity(context_state)
            
            novelty_score = cdl_response.get('novelty_score', 0)
            curiosity_level = cdl_response.get('average_curiosity', 0)
            
            if logger:
                logger.log(f"{self.name} 🧠 CDL评估: 新颖性{novelty_score:.2f}, 好奇心{curiosity_level:.2f}")
            
            # 决定是否执行CDL探索 (降低阈"
            if cdl_response.get('should_explore', False) or novelty_score > 0.5:
                suggested_action = cdl_response.get('suggested_action', 'explore')
                
                # 执行CDL建议的行"
                if suggested_action in ['explore', 'novelty_seeking']:
                    success = self._execute_cdl_exploration_move(game)
                elif suggested_action in ['collect_information', 'uncertainty_reduction']:
                    success = self._execute_cdl_info_gathering(game)
                else:
                    success = self._execute_cdl_exploration_move(game)
                
                if success:
                    # 记录CDL经验
                    self._record_cdl_experience(suggested_action, context_state, True)
                    return {'action_taken': suggested_action, 'success': True}
            
            return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} CDL探索循环失败: {str(e)}")
            return None

    

    def _enhanced_cdl_exploration_with_tools(self, game):
        """增强CDL探索 - 增加工具使用和互动概率"""
        try:
            if not (self.cdl_active and hasattr(self, 'curiosity_driven_learning')):
                return None
            
            # 构建增强上下文
            from curiosity_driven_learning import ContextState
            nearby_entities = self._collect_nearby_entities(game)
            
            # 好奇心权重调节 - 可通过修改这些值来平衡冒险和探索
            curiosity_weights = {
                'tool_usage_curiosity': 0.95,      # 大幅提高工具使用好奇心权重
                'animal_interaction_curiosity': 0.85,  # 大幅提高动物互动好奇心权重  
                'plant_interaction_curiosity': 0.8,   # 大幅提高植物互动好奇心权重
                'exploration_novelty_weight': 0.3,    # 降低纯探索权重，避免过度移动
                'repetition_penalty': 0.3             # 重复行为惩罚权重
            }
            
            context_state = ContextState(
                symbolized_scene=nearby_entities,
                agent_internal_state={
                    'position': (self.x, self.y),
                    'health': self.health,
                    'food': self.food,
                    'water': self.water,
                    'phase': getattr(self, 'phase', 'exploration'),
                    'curiosity_weights': curiosity_weights  # 传递好奇心权重
                },
                environmental_factors={
                    'terrain': game.game_map.grid[self.y][self.x],
                    'day': game.current_day,
                    'visited_positions_count': len(getattr(self, 'visited_positions', set())),
                    'nearby_tools_available': self._check_available_tools(),
                    'nearby_interaction_targets': self._count_interaction_targets(nearby_entities)
                },
                social_context={
                    'nearby_players': [p.name for p in game.players if p != self and abs(p.x - self.x) + abs(p.y - self.y) <= 3]
                },
                timestamp=game.current_day * 24.0
            )
            
            # CDL评估with增强好奇心
            cdl_response = self.curiosity_driven_learning.evaluate_novelty_and_curiosity(context_state)
            
            novelty_score = cdl_response.get('novelty_score', 0)
            curiosity_level = cdl_response.get('average_curiosity', 0)
            
            # 增强决策逻辑
            enhanced_action = self._determine_enhanced_curious_action(
                nearby_entities, curiosity_weights, novelty_score
            )
            
            if enhanced_action:
                if self.logger:
                    self.logger.log(f"{self.name} 🧠 增强CDL决策: {enhanced_action} "
                                  f"(新颖性={novelty_score:.2f}, 好奇心={curiosity_level:.2f})")
                
                success = self._execute_enhanced_action(enhanced_action, game)
                # 记录CDL经验（成功或失败都要记录）
                try:
                    self._record_cdl_experience(enhanced_action, context_state, success)
                except:
                    # 如果_record_cdl_experience不存在，使用简化版本
                    if hasattr(self, 'five_library_system'):
                        result_type = "success" if success else "failure"
                        self.add_experience_to_direct_library(enhanced_action, result_type, {"source": "enhanced_cdl"})
                
                # 成功或失败都返回结果，让调用者知道发生了什么
                if self.logger:
                    status = "成功" if success else "失败"
                    self.logger.log(f"{self.name} 🧠 增强CDL执行{status}: {enhanced_action}")
                
                return {'action_taken': enhanced_action, 'success': success, 'source': 'enhanced_cdl'}
            else:
                if self.logger:
                    self.logger.log(f"{self.name} 🤔 增强CDL未找到合适行动，回退到标准CDL")
            
            # 如果没有找到合适的行动，返回None让旧版CDL接管
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 增强CDL探索失败: {str(e)}")
            return None
    
    def _determine_enhanced_curious_action(self, nearby_entities, curiosity_weights, novelty_score):
        """确定增强好奇心驱动的行动"""
        import random
        
        # 检查最近行动历史，避免重复
        recent_actions = getattr(self, '_recent_cdl_actions', [])
        
        # 优先级行动列表
        priority_actions = []
        
        # 1. 工具使用行动 (高好奇心权重)
        if random.random() < curiosity_weights['tool_usage_curiosity']:
            for entity in nearby_entities:
                if entity.get('distance', 999) <= 1:
                    if entity.get('type') in ['Strawberry', 'Mushroom']:
                        if 'collect_plant_with_tool' not in recent_actions[-5:]:
                            priority_actions.append('collect_plant_with_tool')
                    elif entity.get('type') in ['Rabbit', 'Boar']:
                        if 'attack_animal_with_tool' not in recent_actions[-3:]:
                            priority_actions.append('attack_animal_with_tool')
        
        # 2. 动物互动行动
        if random.random() < curiosity_weights['animal_interaction_curiosity']:
            for entity in nearby_entities:
                if entity.get('distance', 999) <= 2 and entity.get('type') in ['Rabbit', 'Boar']:
                    if 'attack_animal_barehanded' not in recent_actions[-3:]:
                        priority_actions.append('attack_animal_barehanded')
        
        # 3. 植物互动行动
        if random.random() < curiosity_weights['plant_interaction_curiosity']:
            for entity in nearby_entities:
                if entity.get('distance', 999) <= 1 and entity.get('type') in ['Strawberry', 'Mushroom']:
                    if 'collect_plant_barehanded' not in recent_actions[-4:]:
                        priority_actions.append('collect_plant_barehanded')
        
        # 4. 探索性移动 (降低权重，避免过度移动)
        if random.random() < curiosity_weights['exploration_novelty_weight'] and novelty_score > 0.7:
            if 'explore_move' not in recent_actions[-6:]:
                priority_actions.append('explore_move')
        
        # 选择行动并记录历史
        if priority_actions:
            chosen_action = random.choice(priority_actions)
            
            # 更新行动历史
            if not hasattr(self, '_recent_cdl_actions'):
                self._recent_cdl_actions = []
            self._recent_cdl_actions.append(chosen_action)
            if len(self._recent_cdl_actions) > 10:
                self._recent_cdl_actions = self._recent_cdl_actions[-10:]
            
            return chosen_action
        
        return None
    
    def _check_available_tools(self):
        """检查可用工具"""
        # 简化实现，实际可以检查玩家工具库存
        return ['hand', 'stick', 'stone']  # 基础工具
    
    def _count_interaction_targets(self, nearby_entities):
        """统计附近可互动目标"""
        targets = {
            'plants': 0,
            'animals': 0,
            'water_sources': 0
        }
        
        for entity in nearby_entities:
            entity_type = entity.get('type', '')
            if entity_type in ['Strawberry', 'Mushroom']:
                targets['plants'] += 1
            elif entity_type in ['Rabbit', 'Boar', 'Tiger', 'BlackBear']:
                targets['animals'] += 1
            elif entity_type == 'water':
                targets['water_sources'] += 1
        
        return targets
    
    def _execute_enhanced_action(self, action, game):
        """执行增强行动"""
        try:
            if action == 'collect_plant_with_tool':
                return self._execute_tool_plant_collection(game)
            elif action == 'attack_animal_with_tool':
                return self._execute_tool_animal_attack(game)
            elif action == 'collect_plant_barehanded':
                return self._execute_barehanded_plant_collection(game)
            elif action == 'attack_animal_barehanded':
                return self._execute_barehanded_animal_attack(game)
            elif action == 'explore_move':
                return self._execute_cdl_exploration_move(game)
            else:
                return False
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 执行增强行动失败: {str(e)}")
            return False
    
    def _execute_tool_plant_collection(self, game):
        """使用工具采集植物"""
        nearby_plants = [p for p in game.game_map.plants 
                        if abs(p.x - self.x) <= 1 and abs(p.y - self.y) <= 1 and not p.collected]
        
        if nearby_plants:
            plant = nearby_plants[0]
            plant_type = plant.__class__.__name__
            
            # 🔧 关键修复：使用真正的工具选择系统
            best_tool = None
            tool_name = "hand"  # 默认徒手
            
            if hasattr(self, 'get_best_tool_for_target'):
                # 将植物类名转换为工具系统识别的类型
                if plant_type in ['Strawberry', 'Mushroom']:
                    target_type = 'ground_plant'
                elif plant_type in ['Potato', 'SweetPotato']:
                    target_type = 'underground_plant'
                elif plant_type in ['Acorn', 'Chestnut']:
                    target_type = 'tree_fruits'
                else:
                    target_type = 'ground_plant'
                
                best_tool = self.get_best_tool_for_target(target_type)
                if best_tool:
                    tool_name = best_tool.name
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 CDL选择工具: {tool_name} 采集 {plant_type}")
            
            success = self.collect_plant(plant)
            
            if hasattr(self, '_record_tool_usage'):
                # 创建工具对象用于记录
                if best_tool:
                    tool_for_record = best_tool
                else:
                    class SimpleTool:
                        def __init__(self, name):
                            self.name = name
                    tool_for_record = SimpleTool(tool_name)
                
                self._record_tool_usage(tool_for_record, plant_type, success, 5 if success else 0)
            
            if self.logger:
                self.logger.log(f"{self.name} 🔧 CDL工具采集: {plant_type} 使用 {tool_name} {'成功' if success else '失败'}")
            return success
        return False
    
    def _execute_tool_animal_attack(self, game):
        """使用工具攻击动物"""
        nearby_animals = [a for a in game.game_map.animals 
                         if abs(a.x - self.x) <= 2 and abs(a.y - self.y) <= 2 and a.alive 
                         and a.__class__.__name__ in ['Rabbit', 'Boar']]
        
        if nearby_animals:
            animal = nearby_animals[0]
            animal_type = animal.__class__.__name__
            
            # 🔧 关键修复：确保记录遭遇
            if not hasattr(self, '_recorded_encounters'):
                self._recorded_encounters = set()
            
            encounter_key = f"{animal.x}_{animal.y}_{animal.__class__.__name__}_{id(animal)}"
            if encounter_key not in self._recorded_encounters:
                self.encounter_animal(animal, game)
                self._recorded_encounters.add(encounter_key)
            
            # 🔧 关键修复：使用真正的工具选择系统
            best_tool = None
            tool_name = "hand"  # 默认徒手
            
            if hasattr(self, 'get_best_tool_for_target'):
                # 将动物类名转换为工具系统识别的类型
                if animal_type in ['Rabbit', 'Boar']:
                    target_type = 'prey'
                elif animal_type in ['Tiger', 'BlackBear']:
                    target_type = 'predator'
                else:
                    target_type = 'prey'
                
                best_tool = self.get_best_tool_for_target(target_type)
                if best_tool:
                    tool_name = best_tool.name
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 CDL选择工具: {tool_name} 攻击 {animal_type}")
            
            damage = self.attack(animal)
            success = damage > 0
            
            if hasattr(self, '_record_tool_usage'):
                # 创建工具对象用于记录
                if best_tool:
                    tool_for_record = best_tool
                else:
                    class SimpleTool:
                        def __init__(self, name):
                            self.name = name
                    tool_for_record = SimpleTool(tool_name)
                
                self._record_tool_usage(tool_for_record, animal_type, success, damage)
            
            if self.logger:
                self.logger.log(f"{self.name} 🔧 CDL工具攻击: {animal_type} 使用 {tool_name} "
                              f"{'成功' if success else '失败'} 伤害={damage}")
            return success
        return False
    
    def _execute_barehanded_plant_collection(self, game):
        """徒手采集植物"""
        nearby_plants = [p for p in game.game_map.plants 
                        if abs(p.x - self.x) <= 1 and abs(p.y - self.y) <= 1 and not p.collected and not p.toxic]
        
        if nearby_plants:
            plant = nearby_plants[0]
            success = self.collect_plant(plant)
            plant_type = plant.__class__.__name__
            if self.logger:
                self.logger.log(f"{self.name} ✋ CDL徒手采集: {plant_type} {'成功' if success else '失败'}")
            return success
        return False
    
    def _execute_barehanded_animal_attack(self, game):
        """徒手攻击动物"""
        nearby_animals = [a for a in game.game_map.animals 
                         if abs(a.x - self.x) <= 1 and abs(a.y - self.y) <= 1 and a.alive 
                         and a.__class__.__name__ in ['Rabbit', 'Boar']]
        
        if nearby_animals:
            animal = nearby_animals[0]
            animal_type = animal.__class__.__name__
            
            # 🔧 关键修复：确保记录遭遇
            if not hasattr(self, '_recorded_encounters'):
                self._recorded_encounters = set()
            
            encounter_key = f"{animal.x}_{animal.y}_{animal.__class__.__name__}_{id(animal)}"
            if encounter_key not in self._recorded_encounters:
                self.encounter_animal(animal, game)
                self._recorded_encounters.add(encounter_key)
            
            damage = self.attack(animal)
            success = damage > 0
            if self.logger:
                self.logger.log(f"{self.name} ✋ CDL徒手攻击: {animal_type} {'成功' if success else '失败'} 伤害={damage}")
            return success
        return False

    def _collaborative_goal_determination(self, game, decision_stage, current_state):
        """🔧 第2步修复：三阶段协同目标确定机制"""
        try:
            stage = decision_stage['stage']
            
            if stage == 'instinct':
                # 本能阶段：与生存本能协同
                return self._instinct_goal_determination(decision_stage, current_state)
            elif stage == 'dmha':
                # DMHA阶段：与注意力机制协同
                return self._dmha_goal_determination(game, current_state)
            elif stage == 'cdl':
                # CDL阶段：与好奇心机制协同
                return self._cdl_goal_determination(game, current_state)
            else:
                # 默认使用DMHA
                return self._dmha_goal_determination(game, current_state)
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 协同目标确定失败: {str(e)}")
            return {
                'type': 'survival',
                'urgency': 0.7,
                'context': current_state,
                'source': 'fallback'
            }
    
    def _instinct_goal_determination(self, decision_stage, current_state):
        """本能阶段目标确定：与生存本能协同"""
        trigger_type = decision_stage.get('trigger_type', 'unknown')
        
        # 基于触发类型确定紧急目标
        if trigger_type == 'threat_nearby':
            return {
                'type': 'threat_avoidance',
                'urgency': 1.0,
                'context': current_state,
                'source': 'instinct',
                'description': f"威胁规避 (距离≤3)"
            }
        elif trigger_type == 'low_health':
            return {
                'type': 'health_recovery',
                'urgency': 0.95,
                'context': current_state,
                'source': 'instinct',
                'description': f"紧急治疗 (血量≤20)"
            }
        elif trigger_type == 'low_water':
            return {
                'type': 'water_acquisition',
                'urgency': 0.9,
                'context': current_state,
                'source': 'instinct',
                'description': f"紧急寻水 (水分≤20)"
            }
        elif trigger_type == 'low_food':
            return {
                'type': 'food_acquisition',
                'urgency': 0.85,
                'context': current_state,
                'source': 'instinct',
                'description': f"紧急觅食 (食物≤20)"
            }
        else:
            return {
                'type': 'survival',
                'urgency': 0.8,
                'context': current_state,
                'source': 'instinct',
                'description': "综合生存威胁"
            }
    
    def _dmha_goal_determination(self, game, current_state):
        """DMHA阶段目标确定：与注意力机制协同"""
        try:
            # 构建注意力上下文
            attention_context = self._build_attention_context(game)
            
            # DMHA处理获取注意力焦点
            if hasattr(self, 'dmha') and self.dmha:
                attention_output = self.dmha.process_attention(attention_context)
                dominant_focus = attention_output.get('dominant_focus', 'resource')
                attention_score = attention_output.get('attention_score', 0.5)
            else:
                dominant_focus = 'resource'
                attention_score = 0.5
            
            # 基于注意力焦点确定目标
            if dominant_focus == 'resource':
                # 资源管理目标
                if self.water < 35:
                    goal_type = 'water_acquisition'
                    urgency = 0.7
                    description = "资源管理-水源获取"
                elif self.food < 35:
                    goal_type = 'food_acquisition'
                    urgency = 0.65
                    description = "资源管理-食物获取"
                else:
                    goal_type = 'resource_optimization'
                    urgency = 0.5
                    description = "资源优化配置"
            elif dominant_focus == 'exploration':
                goal_type = 'environment_exploration'
                urgency = 0.4
                description = "环境探索"
            elif dominant_focus == 'social':
                goal_type = 'social_interaction'
                urgency = 0.3
                description = "社交互动"
            else:
                goal_type = 'resource_acquisition'
                urgency = 0.6
                description = "默认资源获取"
            
            return {
                'type': goal_type,
                'urgency': urgency,
                'context': current_state,
                'source': 'dmha',
                'dmha_focus': dominant_focus,
                'attention_score': attention_score,
                'description': description
            }
            
        except Exception as e:
            return {
                'type': 'resource_acquisition',
                'urgency': 0.6,
                'context': current_state,
                'source': 'dmha_fallback',
                'description': "DMHA异常兜底"
            }
    
    def _cdl_goal_determination(self, game, current_state):
        """CDL阶段目标确定：直接生成EOCATR探索目标"""
        try:
            # 🎯 简化CDL：直接寻找最新奇的EOCATR目标
            novelty_targets = self._find_novel_eocatr_targets(game)
            
            if novelty_targets:
                # 选择新奇度最高的目标
                best_target = max(novelty_targets, key=lambda x: x['novelty_score'])
                
                eocatr_goal = {
                    'environment': best_target['environment'],
                    'object': best_target['object'],
                    'characteristics': best_target.get('characteristics', ['unknown']),
                    'action': best_target['action'],
                    'tool': best_target.get('tool', None),
                    'expected_result': best_target['expected_result']
                }
                
                description = f"CDL探索: {best_target['action']} {best_target['object']} (新奇度:{best_target['novelty_score']:.2f})"
                
                cdl_goal = {
                    'type': 'cdl_exploration',  # 新的统一类型
                    'urgency': min(0.8, 0.3 + best_target['novelty_score'] * 0.5),  # 基于新奇度动态计算紧急度
                    'context': current_state,
                    'source': 'cdl_direct',
                    'novelty_score': best_target['novelty_score'],
                    'description': description,
                    'eocatr_goal': eocatr_goal  # 直接包含EOCATR目标
                }
                
                # 传递给WBM系统
                self._pending_cdl_goal = cdl_goal
                
                if logger:
                    logger.log(f"{self.name} CDL直接目标: {best_target['action']} → {best_target['object']} (新奇度:{best_target['novelty_score']:.2f})")
                
                return cdl_goal
            else:
                # 没有新奇目标时，默认随机探索
                default_eocatr = self._get_default_exploration_eocatr(game)
                
                cdl_goal = {
                    'type': 'cdl_exploration',
                    'urgency': 0.3,
                    'context': current_state,
                    'source': 'cdl_default',
                    'novelty_score': 0.1,
                    'description': "CDL默认探索",
                    'eocatr_goal': default_eocatr
                }
                
                self._pending_cdl_goal = cdl_goal
                
                if logger:
                    logger.log(f"{self.name} CDL默认探索: {default_eocatr['action']} → {default_eocatr['object']}")
                
                return cdl_goal
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} CDL目标确定失败: {str(e)}")
            return {
                'type': 'cdl_exploration',
                'urgency': 0.3,
                'context': current_state,
                'source': 'cdl_fallback',
                'description': "CDL异常兜底"
            }

    def _find_high_priority_exploration_targets(self, game):
        """🎯 新增：寻找高优先级探索目标（生物多样性和工具效能测试）"""
        try:
            high_priority_targets = []
            
            # 🦋 1. 生物多样性探索 - 最高优先级
            biodiversity_targets = self._find_biodiversity_targets(game)
            high_priority_targets.extend(biodiversity_targets)
            
            # 🔧 2. 工具效能测试 - 高优先级  
            tool_efficiency_targets = self._find_tool_efficiency_targets(game)
            high_priority_targets.extend(tool_efficiency_targets)
            
            # 按优先级排序
            high_priority_targets.sort(key=lambda x: x['priority_score'], reverse=True)
            
            if logger and high_priority_targets:
                logger.log(f"{self.name} 🎯 发现{len(high_priority_targets)}个高优先级目标，最高优先级: {high_priority_targets[0]['priority_score']:.2f}")
            
            return high_priority_targets[:5]  # 返回前5个最高优先级目标
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找高优先级目标失败: {str(e)}")
            return []

    def _find_biodiversity_targets(self, game):
        """🦋 寻找生物多样性探索目标"""
        try:
            biodiversity_targets = []
            
            # 检测视野中的动植物
            nearby_entities = self._collect_nearby_entities(game, max_distance=3)
            
            # 获取已探索的生物种类
            if not hasattr(self, 'explored_species'):
                self.explored_species = set()
            
            for entity in nearby_entities:
                entity_type = entity.get('type', 'unknown')
                distance = entity.get('distance', 999)
                
                # 动物探索 - 超高优先级
                if entity_type in ['Rabbit', 'Boar', 'Tiger', 'BlackBear'] and distance <= 2:
                    species_key = f"{entity_type}_{entity.get('x', 0)}_{entity.get('y', 0)}"
                    
                    if species_key not in self.explored_species:
                        # 根据动物类型确定探索方式和工具
                        if entity_type in ['Rabbit', 'Boar']:
                            action = 'hunt_with_tool'
                            tools = ['长矛', '弓箭', '石头']
                            priority = 0.95  # 猎物最高优先级
                        else:  # Tiger, BlackBear
                            action = 'observe_safely'
                            tools = []
                            priority = 0.85  # 危险动物观察优先级
                        
                        biodiversity_targets.append({
                            'type': 'biodiversity_exploration',
                            'environment': f"{game.game_map.grid[entity.get('y', 0)][entity.get('x', 0)]}",
                            'object': entity_type.lower(),
                            'characteristics': ['animal', 'species_' + entity_type.lower()],
                            'action': action,
                            'tool': tools[0] if tools else None,
                            'expected_result': f'learn_species_{entity_type.lower()}',
                            'priority_score': priority,
                            'target_position': (entity.get('x', 0), entity.get('y', 0)),
                            'species_key': species_key
                        })
                
                # 植物探索 - 高优先级
                elif entity_type in ['Strawberry', 'Mushroom', 'Tree'] and distance <= 1:
                    species_key = f"{entity_type}_{entity.get('x', 0)}_{entity.get('y', 0)}"
                    
                    if species_key not in self.explored_species:
                        if entity_type in ['Strawberry', 'Mushroom']:
                            action = 'gather_with_tool'
                            tools = ['篮子', '铁锹']
                            priority = 0.80
                        else:  # Tree
                            action = 'examine_resource'
                            tools = ['铁锹', '棍子']
                            priority = 0.75
                        
                        biodiversity_targets.append({
                            'type': 'biodiversity_exploration',
                            'environment': f"{game.game_map.grid[entity.get('y', 0)][entity.get('x', 0)]}",
                            'object': entity_type.lower(),
                            'characteristics': ['plant', 'species_' + entity_type.lower()],
                            'action': action,
                            'tool': tools[0] if tools else None,
                            'expected_result': f'learn_species_{entity_type.lower()}',
                            'priority_score': priority,
                            'target_position': (entity.get('x', 0), entity.get('y', 0)),
                            'species_key': species_key
                        })
            
            return biodiversity_targets
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找生物多样性目标失败: {str(e)}")
            return []

    def _find_tool_efficiency_targets(self, game):
        """🔧 寻找工具效能测试目标"""
        try:
            tool_efficiency_targets = []
            
            # 获取AI的工具装备
            available_tools = getattr(self, 'tools', [])
            if not available_tools:
                return []
            
            # 获取已测试的工具组合
            if not hasattr(self, 'tested_tool_combinations'):
                self.tested_tool_combinations = set()
            
            # 检测视野中可以测试工具的目标
            nearby_entities = self._collect_nearby_entities(game, max_distance=2)
            
            for tool in available_tools:
                tool_name = getattr(tool, 'name', str(tool))
                
                # 测试工具对不同目标的效能
                for entity in nearby_entities:
                    entity_type = entity.get('type', 'unknown')
                    combo_key = f"{tool_name}_{entity_type}"
                    
                    if combo_key not in self.tested_tool_combinations:
                        # 动物工具测试
                        if entity_type in ['Rabbit', 'Boar', 'Tiger', 'BlackBear']:
                            # 根据工具类型确定测试方式
                            if tool_name in ['长矛', '弓箭']:
                                action = 'test_hunting_tool'
                                priority = 0.90
                            elif tool_name in ['石头']:
                                action = 'test_ranged_tool'
                                priority = 0.85
                            else:
                                continue  # 不适合的工具跳过
                            
                            tool_efficiency_targets.append({
                                'type': 'tool_efficiency_testing',
                                'environment': f"{game.game_map.grid[entity.get('y', 0)][entity.get('x', 0)]}",
                                'object': entity_type.lower(),
                                'characteristics': ['target', 'tool_test'],
                                'action': action,
                                'tool': tool_name,
                                'expected_result': f'test_{tool_name}_on_{entity_type.lower()}',
                                'priority_score': priority,
                                'target_position': (entity.get('x', 0), entity.get('y', 0)),
                                'combo_key': combo_key
                            })
                        
                        # 植物工具测试
                        elif entity_type in ['Strawberry', 'Mushroom', 'Tree']:
                            if tool_name in ['篮子', '铁锹']:
                                action = 'test_gathering_tool'
                                priority = 0.75
                            elif tool_name in ['棍子']:
                                action = 'test_utility_tool'
                                priority = 0.70
                            else:
                                continue
                            
                            tool_efficiency_targets.append({
                                'type': 'tool_efficiency_testing',
                                'environment': f"{game.game_map.grid[entity.get('y', 0)][entity.get('x', 0)]}",
                                'object': entity_type.lower(),
                                'characteristics': ['resource', 'tool_test'],
                                'action': action,
                                'tool': tool_name,
                                'expected_result': f'test_{tool_name}_on_{entity_type.lower()}',
                                'priority_score': priority,
                                'target_position': (entity.get('x', 0), entity.get('y', 0)),
                                'combo_key': combo_key
                            })
            
            return tool_efficiency_targets
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找工具效能目标失败: {str(e)}")
            return []

    def _find_novel_eocatr_targets(self, game):
        """🎯 CDL简化核心：寻找新奇的EOCATR探索目标"""
        try:
            novelty_targets = []
            
            # 🔍 1. 寻找未探索的位置
            unexplored_locations = self._find_unexplored_locations(game)
            for location in unexplored_locations:
                novelty_targets.append({
                    'environment': location,
                    'object': 'area',
                    'action': 'move',
                    'expected_result': 'explore_new_area',
                    'novelty_score': 0.8  # 新位置高新奇度
                })
            
            # 🌱 2. 寻找未交互的动植物
            novel_creatures = self._find_novel_creatures(game)
            for creature in novel_creatures:
                novelty_targets.append({
                    'environment': 'current_area',
                    'object': creature['name'],
                    'characteristics': creature.get('characteristics', ['unknown']),
                    'action': 'interact',
                    'expected_result': 'learn_about_creature',
                    'novelty_score': 0.7  # 新生物中等新奇度
                })
            
            # 🔧 3. 寻找未使用的工具
            novel_tools = self._find_novel_tools(game)
            for tool in novel_tools:
                novelty_targets.append({
                    'environment': 'current_area',
                    'object': tool['target_object'],
                    'action': 'use',
                    'tool': tool['name'],
                    'expected_result': tool['expected_result'],
                    'novelty_score': 0.6  # 新工具中等新奇度
                })
            
            # 🎯 4. 寻找未尝试的行为组合
            novel_actions = self._find_novel_actions(game)
            for action_combo in novel_actions:
                novelty_targets.append({
                    'environment': action_combo['environment'],
                    'object': action_combo['object'],
                    'action': action_combo['action'],
                    'tool': action_combo.get('tool', None),
                    'expected_result': action_combo['expected_result'],
                    'novelty_score': 0.5  # 新行为组合低新奇度
                })
            
            # 按新奇度排序
            novelty_targets.sort(key=lambda x: x['novelty_score'], reverse=True)
            
            if logger and novelty_targets:
                logger.log(f"{self.name} 发现{len(novelty_targets)}个新奇目标，最高新奇度: {novelty_targets[0]['novelty_score']:.2f}")
            
            return novelty_targets[:10]  # 返回前10个最新奇的目标
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找新奇目标失败: {str(e)}")
            return []

    def _get_default_exploration_eocatr(self, game):
        """获取默认的探索EOCATR目标"""
        try:
            # 简单的默认探索行为
            default_actions = [
                {
                    'environment': 'current_area',
                    'object': 'surroundings',
                    'action': 'observe',
                    'expected_result': 'gather_information'
                },
                {
                    'environment': 'nearby_area',
                    'object': 'area',
                    'action': 'move',
                    'expected_result': 'explore_vicinity'
                },
                {
                    'environment': 'current_area',
                    'object': 'ground',
                    'action': 'search',
                    'expected_result': 'find_resources'
                }
            ]
            
            # 随机选择一个默认行为
            import random
            return random.choice(default_actions)
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 获取默认探索目标失败: {str(e)}")
            return {
                'environment': 'current_area',
                'object': 'surroundings',
                'action': 'observe',
                'expected_result': 'basic_exploration'
            }

    def _find_unexplored_locations(self, game):
        """寻找未探索的位置"""
        try:
            if not hasattr(self, 'visited_positions'):
                self.visited_positions = set()
            
            unexplored = []
            current_x, current_y = self.x, self.y
            
            # 检查周围8个方向的位置
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:  # 跳过当前位置
                        continue
                    
                    new_x, new_y = current_x + dx, current_y + dy
                    
                    # 检查边界
                    if (0 <= new_x < len(game.game_map.grid[0]) and 
                        0 <= new_y < len(game.game_map.grid)):
                        
                        pos = (new_x, new_y)
                        if pos not in self.visited_positions:
                            terrain = game.game_map.grid[new_y][new_x]
                            unexplored.append(f"{terrain}_at_{new_x}_{new_y}")
            
            return unexplored[:3]  # 返回最多3个未探索位置
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找未探索位置失败: {str(e)}")
            return []

    def _find_novel_creatures(self, game):
        """寻找未交互的动植物"""
        try:
            if not hasattr(self, 'interacted_creatures'):
                self.interacted_creatures = set()
            
            novel_creatures = []
            nearby_entities = self._collect_nearby_entities(game)
            
            for entity in nearby_entities:
                creature_id = f"{entity['type']}_{entity.get('x', 0)}_{entity.get('y', 0)}"
                
                if creature_id not in self.interacted_creatures:
                    if entity['type'] in ['Rabbit', 'Boar', 'Strawberry', 'Mushroom', 'Tree']:
                        novel_creatures.append({
                            'name': entity['type'].lower(),
                            'characteristics': self._get_creature_characteristics(entity['type']),
                            'id': creature_id
                        })
            
            return novel_creatures[:3]  # 返回最多3个新生物
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找新生物失败: {str(e)}")
            return []

    def _find_novel_tools(self, game):
        """寻找未使用的工具"""
        try:
            if not hasattr(self, 'used_tools'):
                self.used_tools = set()
            
            novel_tools = []
            available_tools = ['stone', 'stick', 'berry', 'water']  # 简化的工具列表
            
            for tool in available_tools:
                if tool not in self.used_tools:
                    target_object, expected_result = self._get_tool_usage(tool)
                    if target_object:
                        novel_tools.append({
                            'name': tool,
                            'target_object': target_object,
                            'expected_result': expected_result
                        })
            
            return novel_tools[:2]  # 返回最多2个新工具
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找新工具失败: {str(e)}")
            return []

    def _find_novel_actions(self, game):
        """寻找未尝试的行为组合"""
        try:
            if not hasattr(self, 'tried_actions'):
                self.tried_actions = set()
            
            novel_actions = []
            basic_actions = ['observe', 'search', 'move', 'gather']
            objects = ['ground', 'trees', 'water', 'rocks']
            
            for action in basic_actions:
                for obj in objects:
                    action_combo = f"{action}_{obj}"
                    if action_combo not in self.tried_actions:
                        novel_actions.append({
                            'environment': 'current_area',
                            'object': obj,
                            'action': action,
                            'expected_result': f"{action}_result_from_{obj}"
                        })
            
            return novel_actions[:3]  # 返回最多3个新行为组合
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 寻找新行为失败: {str(e)}")
            return []

    def _get_creature_characteristics(self, creature_type):
        """获取生物特征"""
        characteristics_map = {
            'Rabbit': ['small', 'fast', 'edible'],
            'Boar': ['large', 'dangerous', 'edible'],
            'Strawberry': ['plant', 'edible', 'sweet'],
            'Mushroom': ['plant', 'edible', 'nutritious'],
            'Tree': ['large', 'resource', 'shelter']
        }
        return characteristics_map.get(creature_type, ['unknown'])

    def _get_tool_usage(self, tool):
        """获取工具用途"""
        usage_map = {
            'stone': ('rabbit', 'hunting_success'),
            'stick': ('ground', 'digging_result'),
            'berry': ('self', 'nutrition_gain'),
            'water': ('self', 'hydration_gain')
        }
        return usage_map.get(tool, (None, None))

    def _record_attempted_action(self, eocatr_goal):
        """记录尝试的行为，用于新奇度跟踪"""
        try:
            # 初始化跟踪集合
            if not hasattr(self, 'visited_positions'):
                self.visited_positions = set()
            if not hasattr(self, 'interacted_creatures'):
                self.interacted_creatures = set()
            if not hasattr(self, 'used_tools'):
                self.used_tools = set()
            if not hasattr(self, 'tried_actions'):
                self.tried_actions = set()
            if not hasattr(self, 'explored_species'):
                self.explored_species = set()
            if not hasattr(self, 'tested_tool_combinations'):
                self.tested_tool_combinations = set()
            
            action = eocatr_goal.get('action', '')
            obj = eocatr_goal.get('object', '')
            tool = eocatr_goal.get('tool', None)
            
            # 记录位置探索
            if action == 'move':
                self.visited_positions.add((self.x, self.y))
            
            # 记录生物交互
            if action == 'interact' and obj:
                creature_id = f"{obj}_{self.x}_{self.y}"
                self.interacted_creatures.add(creature_id)
            
            # 🦋 新增：记录生物多样性探索
            if hasattr(eocatr_goal, 'species_key'):
                self.explored_species.add(eocatr_goal['species_key'])
            
            # 🔧 新增：记录工具效能测试
            if hasattr(eocatr_goal, 'combo_key'):
                self.tested_tool_combinations.add(eocatr_goal['combo_key'])
            
            # 记录工具使用
            if tool:
                self.used_tools.add(tool)
            
            # 记录行为组合
            if action and obj:
                action_combo = f"{action}_{obj}"
                self.tried_actions.add(action_combo)
                
            if logger:
                logger.log(f"{self.name} 🏷️ 记录尝试: {action} {obj} {f'with {tool}' if tool else ''}")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 记录行为失败: {str(e)}")

    def _convert_abstract_goal_to_eocatr(self, abstract_goal, game):
        """目标转换器：将CDL抽象目标转换为WBM可理解的EOCATR格式"""
        try:
            goal_type = abstract_goal.get('type', 'survival')
            current_terrain = game.game_map.grid[self.y][self.x]
            nearby_entities = self._collect_nearby_entities(game)
            
            # 收集上下文信息
            context = {
                'food_level': self.food,
                'water_level': self.water,
                'health_level': self.health,
                'terrain': current_terrain,
                'nearby_entities': nearby_entities,
                'position': (self.x, self.y)
            }
            
            # 根据不同抽象目标类型进行具象化转换
            if goal_type == 'skill_development':
                return self._convert_skill_development_goal(context)
            elif goal_type == 'knowledge_acquisition':
                return self._convert_knowledge_acquisition_goal(context)
            elif goal_type == 'environment_exploration':
                return self._convert_exploration_goal(context)
            else:
                return self._convert_survival_goal(context)
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 目标转换失败: {str(e)}")
            return {
                'environment': 'unknown',
                'object': 'resource',
                'characteristics': ['needed'],
                'action': 'search',
                'tool': None,
                'expected_result': 'survival'
            }
    
    def _convert_skill_development_goal(self, context):
        """将skill_development转换为具体的EOCATR技能目标"""
        if context['food_level'] < 60:
            # 食物不足 → 发展觅食技能
            nearby_prey = [e for e in context['nearby_entities'] 
                          if e.get('type') in ['Rabbit', 'Boar'] and e.get('distance', 999) <= 2]
            nearby_plants = [e for e in context['nearby_entities'] 
                           if e.get('type') in ['Strawberry', 'Mushroom'] and e.get('distance', 999) <= 1]
            
            if nearby_prey:
                target = nearby_prey[0]
                return {
                    'environment': context['terrain'],
                    'object': target['type'].lower(),
                    'characteristics': ['prey', 'edible'],
                    'action': 'hunt',
                    'tool': 'available_weapon',
                    'expected_result': f"food_gain_from_{target['type']}"
                }
            elif nearby_plants:
                target = nearby_plants[0]
                return {
                    'environment': context['terrain'],
                    'object': target['type'].lower(),
                    'characteristics': ['plant', 'edible'],
                    'action': 'gather',
                    'tool': None,
                    'expected_result': f"food_gain_from_{target['type']}"
                }
        
        # 默认：发展移动探索技能
        return {
            'environment': context['terrain'],
            'object': 'unexplored_area',
            'characteristics': ['unknown', 'potential'],
            'action': 'move',
            'tool': None,
            'expected_result': 'area_exploration'
        }
    
    def _convert_knowledge_acquisition_goal(self, context):
        """将knowledge_acquisition转换为具体的EOCATR学习目标"""
        nearby_entities = context['nearby_entities']
        learning_targets = [e for e in nearby_entities if e.get('distance', 999) <= 2]
        
        if learning_targets:
            target = learning_targets[0]
            return {
                'environment': context['terrain'],
                'object': target['type'].lower(),
                'characteristics': ['observable', 'learnable'],
                'action': 'observe',
                'tool': None,
                'expected_result': f"knowledge_about_{target['type']}"
            }
        else:
            return {
                'environment': context['terrain'],
                'object': 'environment',
                'characteristics': ['current', 'observable'],
                'action': 'analyze',
                'tool': None,
                'expected_result': 'environmental_knowledge'
            }
    
    def _convert_exploration_goal(self, context):
        """将environment_exploration转换为具体的EOCATR探索目标"""
        return {
            'environment': 'adjacent_area',
            'object': 'unexplored_terrain',
            'characteristics': ['unknown', 'adjacent'],
            'action': 'move',
            'tool': None,
            'expected_result': 'territory_expansion'
        }
    
    def _convert_survival_goal(self, context):
        """将基础生存目标转换为EOCATR格式"""
        if context['health_level'] < 50:
            return {
                'environment': context['terrain'],
                'object': 'safe_location',
                'characteristics': ['safe', 'protective'],
                'action': 'seek',
                'tool': None,
                'expected_result': 'health_recovery'
            }
        elif context['food_level'] < context['water_level']:
            return {
                'environment': context['terrain'],
                'object': 'food_source',
                'characteristics': ['edible', 'nutritious'],
                'action': 'seek',
                'tool': None,
                'expected_result': 'hunger_relief'
            }
        else:
            return {
                'environment': context['terrain'],
                'object': 'water_source',
                'characteristics': ['drinkable', 'clean'],
                'action': 'seek',
                'tool': None,
                'expected_result': 'thirst_relief'
            }

    def _calculate_environment_novelty(self, game):
        """计算环境新奇度"""
        try:
            # 简化的新奇度计算
            current_pos = (self.x, self.y)
            if not hasattr(self, 'visited_positions'):
                self.visited_positions = set()
            
            # 检查周围区域的探索程度
            explored_count = 0
            total_count = 0
            
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check_pos = (self.x + dx, self.y + dy)
                    total_count += 1
                    if check_pos in self.visited_positions:
                        explored_count += 1
            
            # 新奇度 = 1 - 探索比例
            novelty = 1.0 - (explored_count / total_count) if total_count > 0 else 1.0
            
            # 记录当前位置
            self.visited_positions.add(current_pos)
            
            return novelty
            
        except Exception:
            return 0.5

    def _dmha_calculate_primary_goal(self, game, current_state):
        """DMHA计算主要目标"""
        try:
            # 构建注意力上下文
            attention_context = self._build_attention_context(game)
            
            # DMHA处理
            if hasattr(self, 'dmha') and self.dmha:
                attention_output = self.dmha.process_attention(attention_context)
                dominant_focus = attention_output.get('dominant_focus', 'resource')
            else:
                dominant_focus = 'resource'  # 默认关注资源
            
            # 根据当前状态确定具体目"""
            if current_state['has_emergency']:
                if current_state['health_ratio'] < 0.3:
                    goal_type = 'health_recovery'
                    urgency = 0.9
                elif current_state['threat_count'] > 0:
                    goal_type = 'threat_avoidance'
                    urgency = 1.0
                elif current_state['water_ratio'] < 0.2:
                    goal_type = 'water_acquisition'
                    urgency = 0.8
                else:
                    goal_type = 'food_acquisition'
                    urgency = 0.7
            else:
                # 非紧急情况下根据DMHA焦点确定目标
                if dominant_focus == 'social':
                    goal_type = 'social_interaction'
                    urgency = 0.4
                elif dominant_focus == 'exploration':
                    goal_type = 'environment_exploration'
                    urgency = 0.3
                else:
                    goal_type = current_state['most_urgent_need']
                    urgency = 0.5
            
            return {
                'type': goal_type,
                'urgency': urgency,
                'context': current_state,
                'dmha_focus': dominant_focus
            }
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} DMHA目标计算失败: {str(e)}")
            return {
                'type': 'survival',
                'urgency': 0.7,
                'context': current_state,
                'dmha_focus': 'resource'
            }

    def _decision_library_matching(self, target_goal, game):
        """决策库匹配- 寻找现成的决策"""
        try:
            # 🎯 首先尝试从可执行规律库中查找
            situation_context = {
                'goal_type': target_goal['type'],
                'food_level': 'low' if self.food < 50 else 'normal',
                'health_level': 'low' if self.health < 50 else 'normal',
                'water_level': 'low' if self.water < 50 else 'normal'
            }
            
            # 获取附近的实体信息来增强上下文
            nearby_entities = self._collect_nearby_entities(game)
            for entity in nearby_entities:
                if entity['distance'] <= 1:  # 紧邻的实体
                    entity_type = entity['type']
                    if entity_type in ['Strawberry', 'Mushroom']:
                        situation_context['plant_type'] = 'ground_plant'
                        situation_context['tool_available'] = None  # 简化，后续可以检查实际工具
                    elif entity_type in ['Tiger', 'BlackBear']:
                        situation_context['animal_type'] = 'predator'
                        situation_context['target_species'] = entity_type
                    elif entity_type in ['Rabbit', 'Boar']:
                        situation_context['animal_type'] = 'prey'
                        situation_context['target_species'] = entity_type
            
            # 查找适用的规律
            applicable_rule = self._find_applicable_rule_for_situation(situation_context)
            if applicable_rule:
                predictions = applicable_rule.get('predictions', {})
                action = predictions.get('action', 'explore')
                confidence = applicable_rule.get('confidence', 0.5)
                
                logger.log(f"{self.name} 🎯 找到适用规律: {action} (置信度: {confidence:.2f})")
                return {
                    'success': True,
                    'action': action,
                    'confidence': confidence,
                    'rule_id': applicable_rule.get('rule_id'),
                    'source': 'actionable_rules'
                }
            
            # 🔧 继续原有的五库系统逻辑
            if not (hasattr(self, 'five_library_system') and self.five_library_system):
                return None
            
            # 构建匹配上下"""
            match_context = {
                'goal_type': target_goal['type'],
                'urgency': target_goal['urgency'],
                'hp': self.health,
                'food': self.food,
                'water': self.water,
                'position': (self.x, self.y),
                'day': getattr(game, 'current_day', 1)
            }
            
            # 从五库系统查找匹配决"
            decision_result = self.five_library_system.generate_decision_from_context(
                context=match_context,
                source='decision_library_matching'
            )
            
            if decision_result.get('success') and decision_result.get('decision'):
                decision = decision_result['decision']
                confidence = decision_result.get('confidence', 0)
                
                # 设置匹配阈"
                if confidence > 0.6:  # 匹配度足够高
                    return {
                        'success': True,
                        'action': decision.action,
                        'confidence': confidence,
                        'decision_id': decision_result.get('decision_id'),
                        'source': 'decision_library'
                    }
            
            return {'success': False, 'reason': '无匹配决策或匹配度不足'}
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 决策库匹配失从 {str(e)}")
            return {'success': False, 'reason': f'匹配异常: {str(e)}'}

    def _wbm_rule_based_decision(self, target_goal, game, logger=None):
        """🔧 第3步修复：WBM专注决策方案制定机制
        
        WBM的核心职责：
        1. 从目标出发，从规律库中选择合适的规律
        2. 组合规律形成决策链
        3. 完成决策链评估（BPU评估）
        4. 确定最优决策链方案
        """
        try:
            if logger:
                logger.log(f"{self.name} 🌉 WBM决策制定开始 - 目标: {target_goal.get('type', 'unknown')} (紧急度: {target_goal.get('urgency', 0):.2f})")
            
            # === 第1步：规律检索 ===
            available_rules = self._wbm_retrieve_rules(target_goal, game, logger)
            
            if not available_rules:
                if logger:
                    logger.log(f"{self.name} ❌ WBM无可用规律，跳过决策制定")
                return None
            
            # === 第2步：规律接头机制 ===
            rule_connections = self._wbm_rule_connecting(available_rules, target_goal, logger)
            
            # === 第3步：规律链构建 ===
            decision_chains = self._wbm_chain_building(rule_connections, target_goal, game, logger)
            
            if not decision_chains:
                if logger:
                    logger.log(f"{self.name} ❌ WBM无法构建有效决策链")
                return None
            
            # === 第4步：BPU效用评估 ===
            evaluated_chains = self._wbm_bpu_evaluation(decision_chains, target_goal, game, logger)
            
            # === 第5步：最优方案选择 ===
            optimal_solution = self._wbm_select_optimal_solution(evaluated_chains, target_goal, logger)
            
            if optimal_solution:
                if logger:
                    logger.log(f"{self.name} ✅ WBM决策制定完成: {optimal_solution['action']} (效用: {optimal_solution['utility']:.2f})")
                return optimal_solution
            else:
                if logger:
                    logger.log(f"{self.name} ❌ WBM无有效决策方案")
                return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM决策制定异常: {str(e)}")
            return None
    
    def _wbm_retrieve_rules(self, target_goal, game, logger=None):
        """WBM规律检索：从规律库获取与目标相关的规律（增强版：支持EOCATR转换）"""
        available_rules = []
        
        try:
            # === 增强版规律检索：直接使用EOCATR转换器 ===
            try:
                # 导入EOCATR转换器
                from wooden_bridge_model import EOCATR_CONVERTER
                
                goal_description = target_goal.get('type', 'unknown')
                urgency = target_goal.get('urgency', 0.5)
                
                # 获取EOCATR规律
                eocatr_rules = EOCATR_CONVERTER.get_eocatr_rules_from_five_libraries()
                
                if logger:
                    logger.log(f"{self.name} 🔧 EOCATR获取: 原始规律{len(eocatr_rules)}条")
                
                # 转换为WBM格式
                wbm_rules = EOCATR_CONVERTER.convert_eocatr_rules_to_wbm(eocatr_rules)
                
                # 根据目标和紧急度过滤相关规律
                filtered_rules = []
                for rule in wbm_rules:
                    # 简化过滤：暂时允许所有规律通过，避免兼容性计算问题
                    filtered_rules.append(rule)
                
                available_rules.extend(filtered_rules)
                
                if logger:
                    logger.log(f"{self.name} ✅ EOCATR转换: WBM规律{len(wbm_rules)}条, 过滤后{len(filtered_rules)}条")
                        
            except Exception as enhanced_error:
                if logger:
                    logger.log(f"{self.name} ⚠️ EOCATR增强检索失败，降级到传统方法: {str(enhanced_error)}")
            
            # === 传统规律检索（兜底方案） ===
            # 1. 从直接规律库获取规律
            direct_rules = self._get_rules_from_direct_library(target_goal)
            available_rules.extend(direct_rules)
            
            # 2. 从总规律库获取规律  
            total_rules = self._get_rules_from_total_library(target_goal)
            available_rules.extend(total_rules)
            
            # 3. 补充基础生存规律
            basic_rules = self._get_basic_survival_rules_for_wbm()
            available_rules.extend(basic_rules)
            
            if logger:
                logger.log(f"{self.name} 📚 WBM规律检索: 直接规律{len(direct_rules)}条, 总规律{len(total_rules)}条, 基础规律{len(basic_rules)}条")
                    
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM规律检索失败: {str(e)}")
            # 兜底：使用基础规律
            basic_rules = self._get_basic_survival_rules_for_wbm()
            available_rules.extend(basic_rules)
        
        return available_rules
    
    def _wbm_rule_connecting(self, available_rules, target_goal, logger=None):
        """WBM规律接头机制：分析规律间的兼容性和连接性"""
        connections = []
        
        try:
            # 简化版规律接头：基于目标类型和条件预测的兼容性
            goal_type = target_goal.get('type', 'unknown')
            
            for rule in available_rules:
                # 计算规律与目标的匹配度
                compatibility_score = self._calculate_rule_goal_compatibility(rule, goal_type)
                
                if compatibility_score > 0.3:  # 兼容性阈值
                    connections.append({
                        'rule': rule,
                        'compatibility_score': compatibility_score,
                        'goal_type': goal_type
                    })
            
            # 按兼容性排序
            connections.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            if logger and connections:
                logger.log(f"{self.name} 🔗 WBM规律接头: 发现{len(connections)}个兼容规律")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM规律接头失败: {str(e)}")
        
        return connections
    
    def _wbm_chain_building(self, rule_connections, target_goal, game, logger=None):
        """WBM规律链构建：基于贪心策略构建前向决策链"""
        decision_chains = []
        
        try:
            # 基于贪心策略构建决策链
            for i, connection in enumerate(rule_connections[:5]):  # 限制考虑前5个最兼容的规律
                rule = connection['rule']
                
                # 生成基于此规律的决策链
                chain = self._build_single_rule_chain(rule, target_goal, game)
                
                if chain:
                    decision_chains.append(chain)
            
            if logger and decision_chains:
                logger.log(f"{self.name} ⛓️ WBM链构建: 生成{len(decision_chains)}条决策链")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM链构建失败: {str(e)}")
        
        return decision_chains
    
    def _wbm_bpu_evaluation(self, decision_chains, target_goal, game, logger=None):
        """WBM BPU评估：四维效用空间评估(成功-成本-时间-风险)"""
        evaluated_chains = []
        
        try:
            for chain in decision_chains:
                # 计算BPU四维效用
                success_utility = self._calculate_success_utility(chain, target_goal)
                cost_penalty = self._calculate_cost_penalty(chain, game)
                time_penalty = self._calculate_time_penalty(chain)
                risk_penalty = self._calculate_risk_penalty(chain, game)
                
                # BPU公式：BPU = 成功效用 - λc*成本 - λt*时间 - λr*风险
                # 使用动态权重
                lambda_c = 0.1  # 成本权重
                lambda_t = 0.05  # 时间权重  
                lambda_r = 0.15  # 风险权重
                
                bpu_utility = success_utility - lambda_c * cost_penalty - lambda_t * time_penalty - lambda_r * risk_penalty
                
                evaluated_chains.append({
                    'chain': chain,
                    'bpu_utility': bpu_utility,
                    'success_utility': success_utility,
                    'cost_penalty': cost_penalty,
                    'time_penalty': time_penalty,
                    'risk_penalty': risk_penalty
                })
            
            # 按BPU效用排序
            evaluated_chains.sort(key=lambda x: x['bpu_utility'], reverse=True)
            
            if logger and evaluated_chains:
                best = evaluated_chains[0]
                logger.log(f"{self.name} 📊 WBM BPU评估: 最佳链效用{best['bpu_utility']:.2f} (成功:{best['success_utility']:.2f}, 成本:{best['cost_penalty']:.2f})")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM BPU评估失败: {str(e)}")
        
        return evaluated_chains
    
    def _wbm_select_optimal_solution(self, evaluated_chains, target_goal, logger=None):
        """WBM最优方案选择：选择BPU效用最高的决策方案"""
        if not evaluated_chains:
            return None
        
        try:
            best_chain = evaluated_chains[0]  # BPU效用最高的链
            
            # 提取第一个可执行行动
            chain_data = best_chain['chain']
            action = chain_data.get('action', 'explore')
            
            return {
                'action': action,
                'source': 'wbm_optimal',
                'confidence': min(0.9, best_chain['bpu_utility']),
                'utility': best_chain['bpu_utility'],
                'chain_info': {
                    'success_utility': best_chain['success_utility'],
                    'cost_penalty': best_chain['cost_penalty'],
                    'time_penalty': best_chain['time_penalty'],
                    'risk_penalty': best_chain['risk_penalty']
                }
            }
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ WBM方案选择失败: {str(e)}")
            return None

    def _calculate_rule_goal_compatibility(self, rule, goal_type):
        """计算规律与目标的兼容性分数（增强版：支持CDL目标）"""
        try:
            compatibility = 0.0
            
            # 🔧 修复：CDL探索目标特殊处理
            if goal_type == 'cdl_exploration':
                # CDL探索目标与大多数规律都有基础兼容性
                compatibility += 0.6  # 基础兼容性
                
                # 检查规律是否与探索相关
                rule_conditions = getattr(rule, 'conditions', {})
                rule_predictions = getattr(rule, 'predictions', {})
                rule_text = str(rule_conditions) + str(rule_predictions)
                
                exploration_keywords = ['move', 'explore', 'search', 'discover', 'investigate', 'area', 'location']
                for keyword in exploration_keywords:
                    if keyword in rule_text.lower():
                        compatibility += 0.2
                        break
                        
                # 规律置信度影响
                rule_confidence = getattr(rule, 'confidence', 0.5)
                compatibility = compatibility * (0.7 + 0.3 * rule_confidence)
                
                return min(1.0, compatibility)
            
            # 原有的其他目标类型处理
            rule_conditions = getattr(rule, 'conditions', {})
            rule_predictions = getattr(rule, 'predictions', {})
            
            # 目标类型匹配检查
            if goal_type in str(rule_conditions).lower() or goal_type in str(rule_predictions).lower():
                compatibility += 0.5
            
            # 扩展的关键词匹配
            goal_keywords = {
                'threat_avoidance': ['threat', 'danger', 'escape', 'flee', 'avoid', 'safe', 'hide'],
                'food_acquisition': ['food', 'eat', 'collect', 'hunt', 'gather', 'plant', 'berry'],
                'water_acquisition': ['water', 'drink', 'river', 'puddle', 'thirst', 'hydrate'],
                'environment_exploration': ['explore', 'move', 'discover', 'search', 'area', 'territory'],
                'health_recovery': ['health', 'heal', 'safe', 'rest', 'recover', 'shelter'],
                'resource_acquisition': ['resource', 'collect', 'gather', 'find', 'search'],
                'survival': ['survive', 'live', 'safety', 'protection', 'basic']
            }
            
            keywords = goal_keywords.get(goal_type, [])
            rule_text = str(rule_conditions) + str(rule_predictions)
            
            # 增强关键词匹配
            matched_keywords = 0
            for keyword in keywords:
                if keyword in rule_text.lower():
                    matched_keywords += 1
            
            if matched_keywords > 0:
                compatibility += min(0.4, matched_keywords * 0.15)  # 多关键词匹配给更高分数
            
            # 通用兼容性：任何规律都有基础可用性
            if compatibility == 0:
                compatibility = 0.3  # 提高默认兼容性
            
            # 规律置信度影响
            rule_confidence = getattr(rule, 'confidence', 0.5)
            compatibility = compatibility * (0.5 + 0.5 * rule_confidence)
            
            return min(1.0, compatibility)
            
        except Exception:
            return 0.4  # 提高默认兼容性，确保有规律可用
    
    def _build_single_rule_chain(self, rule, target_goal, game):
        """基于单个规律构建决策链"""
        try:
            # 从规律中提取行动
            action = self._extract_action_from_rule(rule, target_goal)
            
            if action and self._is_action_executable(action, game):
                return {
                    'rule': rule,
                    'action': action,
                    'goal_type': target_goal.get('type', 'unknown'),
                    'confidence': getattr(rule, 'confidence', 0.5)
                }
            return None
            
        except Exception:
            return None
    
    def _calculate_success_utility(self, chain, target_goal):
        """计算成功效用"""
        try:
            base_utility = target_goal.get('urgency', 0.5)
            rule_confidence = chain.get('confidence', 0.5)
            return base_utility * rule_confidence
        except Exception:
            return 0.3
    
    def _calculate_cost_penalty(self, chain, game):
        """计算成本惩罚"""
        try:
            # 简化的成本计算：基于行动类型
            action = chain.get('action', 'explore')
            
            if 'attack' in action:
                return 0.3  # 攻击行为成本高
            elif 'collect' in action:
                return 0.1  # 采集行为成本低
            else:
                return 0.2  # 默认成本
                
        except Exception:
            return 0.2
    
    def _calculate_time_penalty(self, chain):
        """计算时间惩罚"""
        try:
            # 简化的时间计算
            return 0.1  # 大多数行动时间成本相近
        except Exception:
            return 0.1
    
    def _calculate_risk_penalty(self, chain, game):
        """计算风险惩罚"""
        try:
            # 简化的风险计算：基于环境威胁
            threats = self.detect_threats(game.game_map)
            risk_factor = min(0.5, len(threats) * 0.1)
            
            action = chain.get('action', 'explore')
            if 'attack' in action:
                risk_factor += 0.2  # 攻击行为风险高
            
            return risk_factor
            
        except Exception:
            return 0.1

    def _long_chain_execution_management(self, game, target_goal, logger=None):
        """🔧 第4步修复：长链机制执行管理
        
        长链机制的核心职责：
        1. 在每个回合开始，判断上一个决策链是否执行完毕
        2. 如果已结束，开启新的决策链
        3. 如果未结束，继续执行并检查是否需要修改
        """
        try:
            # === 步骤1：检查是否有正在执行的长链计划 ===
            if hasattr(self, 'current_multi_day_plan') and self.current_multi_day_plan:
                if logger:
                    logger.log(f"{self.name} 🗓️ 发现正在执行的长链计划，进行状态检查")
                
                # 继续执行现有计划
                continue_result = self._continue_existing_long_chain(game, logger)
                if continue_result:
                    return continue_result
                else:
                    # 现有计划执行完毕或失败，清除
                    self._clear_current_plan("执行完毕或失败", logger)
            
            # === 步骤2：判断是否需要启动新的长链计划 ===
            if self._should_start_new_long_chain(target_goal, game, logger):
                if logger:
                    logger.log(f"{self.name} 🗓️ 开启新的长链决策计划")
                
                new_plan_result = self._start_new_long_chain(target_goal, game, logger)
                if new_plan_result:
                    return new_plan_result
            
            # === 步骤3：不需要长链规划 ===
            if logger:
                logger.log(f"{self.name} 🗓️ 当前情况不需要长链规划，交由WBM单步决策")
            
            return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ 长链执行管理异常: {str(e)}")
            return None
    
    def _continue_existing_long_chain(self, game, logger=None):
        """继续执行现有长链计划"""
        try:
            plan = self.current_multi_day_plan
            current_day = getattr(self, 'plan_current_day', 0) + 1
            
            if logger:
                logger.log(f"{self.name} 📅 检查长链计划第{current_day}天 (总计{plan.total_days}天)")
            
            # 1. 环境变化检测
            current_state = self._get_current_wbm_state(game)
            environment_changed = self._detect_plan_environment_change(current_state)
            
            if environment_changed:
                if logger:
                    logger.log(f"{self.name} ⚠️ 检测到环境变化: {environment_changed}")
                
                # 检查是否需要中断当前计划
                if self._should_interrupt_plan(environment_changed, plan):
                    if logger:
                        logger.log(f"{self.name} 🛑 环境变化导致计划中断，重新规划")
                    self._clear_current_plan("环境变化中断", logger)
                    return None
            
            # 2. 执行今天的行动
            today_action = plan.get_action_for_day(current_day)
            if today_action:
                self.plan_current_day = current_day
                
                if logger:
                    logger.log(f"{self.name} 🎯 长链第{current_day}天执行: {today_action.action}")
                    logger.log(f"{self.name}    推理: {today_action.reasoning}")
                
                # 记录执行状态
                self._update_daily_execution_log(current_day, today_action, current_state)
                
                # 3. 检查是否完成整个计划
                if current_day >= plan.total_days:
                    if logger:
                        logger.log(f"{self.name} 🎉 长链计划执行完成!")
                    self._complete_long_chain_plan(True, "正常完成", logger)
                
                return {
                    'action': today_action.action,
                    'source': 'long_chain_continue',
                    'status': f'第{current_day}天',
                    'confidence': today_action.confidence,
                    'plan_goal': plan.goal.description if hasattr(plan.goal, 'description') else str(plan.goal)
                }
            
            # 4. 没有找到今天的行动，计划异常
            if logger:
                logger.log(f"{self.name} ❌ 长链计划第{current_day}天无行动，计划异常结束")
            
            self._complete_long_chain_plan(False, "计划异常", logger)
            return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ 继续长链计划异常: {str(e)}")
            self._clear_current_plan("执行异常", logger)
            return None
    
    def _should_start_new_long_chain(self, target_goal, game, logger=None):
        """判断是否应该启动新的长链计划"""
        try:
            goal_type = target_goal.get('type', 'unknown')
            urgency = target_goal.get('urgency', 0.5)
            
            # 1. 低紧急度目标适合长链规划
            if urgency <= 0.6:
                if logger:
                    logger.log(f"{self.name} 🎯 目标紧急度低({urgency:.2f})，适合长链规划")
                return True
            
            # 2. 特定目标类型需要长链规划 - 🎯 更新：新增生物多样性和工具效能测试
            long_chain_goals = [
                'biodiversity_exploration',      # 新增：生物多样性探索 - 最高优先级
                'tool_efficiency_testing',      # 新增：工具效能测试 - 高优先级
                'cdl_exploration',               # 保留：CDL地图探索
                'environment_exploration',       # 废弃但保留兼容性
                'resource_optimization',         # 废弃但保留兼容性
                'skill_development',             # 废弃但保留兼容性
                'knowledge_acquisition'          # 废弃但保留兼容性
            ]
            
            if goal_type in long_chain_goals:
                if logger:
                    logger.log(f"{self.name} 🎯 目标类型({goal_type})需要长链规划")
                return True
            
            # 3. 资源充足时可以进行长链规划
            if self.health > 60 and self.food > 50 and self.water > 50:
                threats = self.detect_threats(game.game_map) if hasattr(self, 'detect_threats') else []
                if len(threats) == 0:
                    if logger:
                        logger.log(f"{self.name} 🎯 资源充足且环境安全，适合长链规划")
                    return True
            
            if logger:
                logger.log(f"{self.name} 🎯 当前条件不适合长链规划")
            return False
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ 长链启动判断异常: {str(e)}")
            return False
    
    def _start_new_long_chain(self, target_goal, game, logger=None):
        """启动新的长链决策计划"""
        try:
            if logger:
                logger.log(f"{self.name} 🚀 启动新长链计划 - 目标: {target_goal.get('type', 'unknown')}")
            
            # 使用WBM进行长链决策制定
            wbm_result = self._wbm_rule_based_decision(target_goal, game, logger)
            
            # 检查WBM是否生成了长链计划
            if wbm_result and wbm_result.get('source') == 'wbm_optimal':
                # 将WBM的单步决策转换为长链计划的起始
                first_action = wbm_result['action']
                
                # 初始化长链计划状态
                self._initialize_long_chain_state(target_goal, first_action)
                
                if logger:
                    logger.log(f"{self.name} ✅ 新长链计划启动: 首个行动 {first_action}")
                
                return {
                    'action': first_action,
                    'source': 'long_chain_start',
                    'status': '新计划第1步',
                    'confidence': wbm_result.get('confidence', 0.5),
                    'plan_goal': target_goal.get('description', target_goal.get('type', 'unknown'))
                }
            
            if logger:
                logger.log(f"{self.name} ❌ WBM未能生成长链计划")
            return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ❌ 启动长链计划异常: {str(e)}")
            return None
    
    def _detect_plan_environment_change(self, current_state):
        """检测影响计划的环境变化"""
        try:
            # 检查健康状况
            health = current_state.get('health', 100)
            if health < 30:
                return "健康状况危急"
            
            # 检查资源状况  
            food = current_state.get('food', 100)
            water = current_state.get('water', 100)
            if food < 20 or water < 20:
                return "资源严重不足"
            
            # 检查威胁情况（简化检查）
            # 这里可以加入更详细的威胁检测逻辑
            
            return None  # 无重大环境变化
            
        except Exception:
            return None
    
    def _should_interrupt_plan(self, environment_change, plan):
        """判断是否应该中断当前计划"""
        # 健康危急或资源严重不足时中断计划
        critical_changes = ["健康状况危急", "资源严重不足", "直接威胁"]
        return environment_change in critical_changes
    
    def _update_daily_execution_log(self, day, action, state):
        """更新每日执行日志"""
        try:
            if not hasattr(self, 'daily_execution_log'):
                self.daily_execution_log = []
            
            # 确保日志列表足够长
            while len(self.daily_execution_log) < day:
                self.daily_execution_log.append({})
            
            execution_record = {
                'day': day,
                'action': action.action,
                'reasoning': action.reasoning,
                'confidence': action.confidence,
                'start_state': state.copy(),
                'timestamp': time.time()
            }
            
            if len(self.daily_execution_log) == day:
                self.daily_execution_log.append(execution_record)
            else:
                self.daily_execution_log[day - 1] = execution_record
                
        except Exception:
            pass  # 静默失败，不影响主流程
    
    def _initialize_long_chain_state(self, target_goal, first_action):
        """初始化长链计划状态"""
        try:
            # 创建简化的长链计划对象
            class SimpleLongChainPlan:
                def __init__(self, goal, total_days, first_action):
                    self.goal = goal
                    self.total_days = total_days
                    self.actions = [first_action]
                    self.start_time = time.time()
                
                def get_action_for_day(self, day):
                    # 简化版：为每天生成合理的行动
                    if day == 1:
                        return SimpleAction(self.actions[0], f"第{day}天: {self.actions[0]}", 0.7)
                    elif day <= self.total_days:
                        # 基于目标类型生成后续行动
                        goal_type = self.goal.get('type', 'explore')
                        if goal_type == 'environment_exploration':
                            action = f'explore_move'
                        elif goal_type == 'resource_optimization':
                            action = f'resource_check'
                        else:
                            action = f'continue_goal'
                        
                        return SimpleAction(action, f"第{day}天: 继续{goal_type}", 0.6)
                    return None
            
            class SimpleAction:
                def __init__(self, action, reasoning, confidence):
                    self.action = action
                    self.reasoning = reasoning
                    self.confidence = confidence
            
            self.current_multi_day_plan = SimpleLongChainPlan(target_goal, 3, first_action)
            
            self.plan_current_day = 0
            self.daily_execution_log = []
            
            # 初始化统计数据
            if not hasattr(self, 'plan_completion_stats'):
                self.plan_completion_stats = {
                    'total_started': 0,
                    'total_completed': 0,
                    'total_interrupted': 0
                }
            
            self.plan_completion_stats['total_started'] += 1
            
        except Exception:
            pass
    
    def _complete_long_chain_plan(self, success, reason, logger=None):
        """完成长链计划"""
        try:
            if logger:
                status = "成功" if success else "失败"
                logger.log(f"{self.name} 📊 长链计划{status}完成: {reason}")
            
            # 更新统计
            if hasattr(self, 'plan_completion_stats'):
                if success:
                    self.plan_completion_stats['total_completed'] += 1
                else:
                    self.plan_completion_stats['total_interrupted'] += 1
            
            # 清除当前计划
            self._clear_current_plan(reason, logger)
            
        except Exception:
            pass
    
    def _clear_current_plan(self, reason, logger=None):
        """清除当前计划"""
        try:
            self.current_multi_day_plan = None
            self.plan_current_day = 0
            
            if logger:
                logger.log(f"{self.name} 🗑️ 长链计划已清除: {reason}")
                
        except Exception:
            pass

    
    def _calculate_decision_weights(self, available_actions, current_context):
        """计算决策权重 - 增加工具使用优先级"""
        weights = {}
        
        for action in available_actions:
            base_weight = 1.0
            
            # 工具使用行为获得更高权重
            if 'tool' in action or 'collect' in action or 'attack' in action:
                base_weight *= 2.5  # 工具使用优先级提升150%
            
            # WBM规律决策获得额外权重
            if current_context.get('decision_source') == 'WBM规律决策':
                base_weight *= 1.8
            
            # 基于资源状态调整权重
            if self.food < 70 and ('collect' in action or 'attack' in action):
                base_weight *= 2.0  # 低食物时优先觅食行为
            
            if self.water < 70 and 'drink' in action:
                base_weight *= 2.0  # 低水分时优先饮水
            
            # 避免重复行为
            recent_actions = getattr(self, '_recent_actions', [])
            if len(recent_actions) >= 3 and all(a == action for a in recent_actions[-3:]):
                base_weight *= 0.3  # 连续相同行为权重降低
            
            weights[action] = base_weight
        
        return weights


    def _emrs_evaluate_decision(self, action, goal, pre_state, post_state, execution_result):
        """EMRS机制评价决策质量"""
        try:
            # 计算状态变"""
            health_change = post_state['health'] - pre_state['health']
            food_change = post_state['food'] - pre_state['food']
            water_change = post_state['water'] - pre_state['water']
            
            # 基础评分
            base_score = 0.5
            
            # 根据目标类型调整评分
            if goal['type'] == 'health_recovery':
                base_score += max(0, health_change / 20.0)  # 健康提升奖励
            elif goal['type'] == 'food_acquisition':
                base_score += max(0, food_change / 15.0)   # 食物获取奖励
            elif goal['type'] == 'water_acquisition':
                base_score += max(0, water_change / 15.0)  # 水分获取奖励
            elif goal['type'] == 'threat_avoidance':
                # 威胁规避:如果成功逃脱(健康未减从则奖励
                if health_change >= 0:
                    base_score += 0.3
            
            # 执行成功性奖励
            if execution_result.get('success', False):
                base_score += 0.2
            
            # 紧急度匹配奖励
            urgency_bonus = goal['urgency'] * 0.1
            base_score += urgency_bonus
            
            # 限制评分范围
            quality_score = max(0.0, min(1.0, base_score))
            
            return {
                'quality_score': quality_score,
                'health_change': health_change,
                'food_change': food_change,
                'water_change': water_change,
                'goal_achievement': quality_score > 0.6
            }
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} EMRS评价失败: {str(e)}")
            return {
                'quality_score': 0.5,
                'health_change': 0,
                'food_change': 0,
                'water_change': 0,
                'goal_achievement': False
            }

    def _identify_most_urgent_need(self):
        """识别最紧急的需求"""
        try:
            health_need = max(0, 70 - self.health)
            food_need = max(0, 50 - self.food) 
            water_need = max(0, 50 - self.water)
            
            if health_need > food_need and health_need > water_need:
                return 'health_recovery'
            elif water_need > food_need:
                return 'water_acquisition'
            elif food_need > 0:
                return 'food_acquisition'
            else:
                return 'exploration'
        except:
            return 'survival'

    def _collect_nearby_entities(self, game, max_distance=3):
        """收集附近的实体信息"""
        try:
            nearby_entities = []
            
            # 收集附近动物
            for animal in game.game_map.animals:
                distance = abs(animal.x - self.x) + abs(animal.y - self.y)
                if distance <= max_distance:
                    nearby_entities.append({
                        'type': animal.type,
                        'x': animal.x,
                        'y': animal.y,
                        'position': (animal.x, animal.y),
                        'distance': distance
                    })
            
            # 收集附近植物
            for plant in game.game_map.plants:
                distance = abs(plant.x - self.x) + abs(plant.y - self.y)
                if distance <= max_distance:
                    nearby_entities.append({
                        'type': plant.__class__.__name__,
                        'x': plant.x,
                        'y': plant.y,
                        'position': (plant.x, plant.y),
                        'distance': distance
                    })
            
            return nearby_entities
        except:
            return []

    def _capture_current_state(self):
        """捕获当前状态快照"""
        return {
            'health': self.health,
            'food': self.food,
            'water': self.water,
            'position': (self.x, self.y)
        }

    def _execute_planned_action(self, action, game):
        """执行计划的行动"""
        try:
            # 执行行动
            if hasattr(self, '_execute_action'):
                self._execute_action(action)
            
            # 返回执行结果
            result = {'success': True, 'action': action}
            return result
        except Exception as e:
            return {'success': False, 'error': str(e), 'action': action}

    def _record_cdl_experience(self, action, context_state, success):
        """记录CDL经验"""
        try:
            cdl_result = {
                'success': success,
                'action_type': action,
                'decision_source': 'cdl_exploration',
                'context': context_state
            }
            self.add_eocar_experience(action, cdl_result, source="cdl_exploration")
        except Exception as e:
            if logger:
                logger.log(f"{self.name} CDL经验记录失败: {str(e)}")

    # ============================================================================
    # WBM木桥模型辅助方法 (新增)
    # ============================================================================
    
    def _get_basic_survival_rules_for_wbm(self):
        """为WBM获取基础生存规律"""
        try:
            from wooden_bridge_model import Rule
            basic_rules = []
            
            # 健康恢复规律
            if self.health < 50:
                health_rule = Rule(
                    rule_id="basic_health_recovery",
                    rule_type="action",
                    conditions={'health_level': 'low', 'environment': 'any'},
                    predictions={'action': 'collect_healing_plant', 'expected_result': 'health_increase'},
                    confidence=0.6
                )
                basic_rules.append(health_rule)
            
            # 食物获取规律
            if self.food < 40:
                food_rule = Rule(
                    rule_id="basic_food_acquisition",
                    rule_type="action", 
                    conditions={'resource_status': 'depleted', 'environment': 'any'},
                    predictions={'action': 'collect_food_plant', 'expected_result': 'food_increase'},
                    confidence=0.7
                )
                basic_rules.append(food_rule)
            
            # 威胁规避规律 - 🔧 修复：移除未定义的context变量
            threat_rule = Rule(
                rule_id="environmental_threat_assessment_and_response",
                rule_type="cognitive_action",
                conditions={
                    'threats_nearby': True,
                    'environment_type': 'unknown',  # 修复：使用固定值
                    'threat_level': 1  # 修复：使用固定值
                },
                predictions={
                    'assessment_action': 'analyze_threat_characteristics',
                    'primary_response': 'implement_context_appropriate_avoidance',
                    'expected_result': 'threat_neutralization_or_avoidance',
                    'secondary_actions': ['secure_escape_route', 'monitor_threat_movement']
                },
                confidence=0.8
            )
            basic_rules.append(threat_rule)
            
            # 探索规律
            explore_rule = Rule(
                rule_id="basic_exploration",
                rule_type="action",
                conditions={'resource_status': 'adequate', 'threats_nearby': False},
                predictions={'action': 'explore_new_area', 'expected_result': 'knowledge_gain'},
                confidence=0.5
            )
            basic_rules.append(explore_rule)
            
            return basic_rules
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.log(f"{self.name} 基础规律生成失败: {str(e)}")
            return []
    
    def _convert_target_goal_to_wbm_goal(self, target_goal):
        """将目标转换为WBM Goal对象"""
        try:
            from wooden_bridge_model import Goal, GoalType
            
            # 根据目标类型转换
            goal_type = GoalType.EXPLORATION  # 默认
            if target_goal.get('type') == 'health_recovery':
                goal_type = GoalType.SURVIVAL
            elif target_goal.get('type') in ['food_acquisition', 'water_acquisition']:
                goal_type = GoalType.RESOURCE_ACQUISITION
            elif target_goal.get('type') == 'threat_avoidance':
                goal_type = GoalType.THREAT_AVOIDANCE
            elif target_goal.get('type') == 'exploration':
                goal_type = GoalType.EXPLORATION
                
            wbm_goal = Goal(
                goal_type=goal_type,
                description=target_goal.get('description', 'Unknown goal'),
                priority=target_goal.get('priority', 0.5),
                urgency=target_goal.get('urgency', 0.5),
                context=target_goal.get('context', {})
            )
            
            return wbm_goal
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 目标转换失败: {str(e)}")
            # 返回默认探索目标
            from wooden_bridge_model import Goal, GoalType
            return Goal(
                goal_type=GoalType.EXPLORATION,
                description="默认探索",
                priority=0.5,
                urgency=0.3
            )
    
    def _get_current_wbm_state(self, game):
        """获取当前WBM状态"""
        try:
            threats = self.detect_threats(game.game_map)
            nearby_resources = self._get_nearby_resources(game)
            
            state = {
                'health': self.health,
                'food': self.food,
                'water': self.water,
                'position': (self.x, self.y),
                'environment': self._get_current_environment_type(game),
                'threats_nearby': len(threats) > 0,
                'threat_count': len(threats),
                'resources_nearby': len(nearby_resources) > 0,
                'resource_count': len(nearby_resources),
                'status': 'critical' if self.health < 30 else 'low' if self.health < 60 else 'good'
            }
            
            return state
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} WBM状态获取失败: {str(e)}")
            return {
                'health': self.health,
                'position': (self.x, self.y),
                'status': 'unknown'
            }
    
    def _extract_wbm_target_state(self, target_goal, game):
        """提取WBM目标状态"""
        try:
            goal_type = target_goal.get('type', 'exploration')
            
            if goal_type == 'health_recovery':
                return {
                    'health': min(100, self.health + 30),
                    'status': 'healthy',
                    'safety': 'secured'
                }
            elif goal_type == 'food_acquisition':
                return {
                    'food': min(100, self.food + 40),
                    'resource_status': 'adequate',
                    'hunger': 'satisfied'
                }
            elif goal_type == 'water_acquisition':
                return {
                    'water': min(100, self.water + 40),
                    'resource_status': 'adequate',
                    'thirst': 'quenched'
                }
            elif goal_type == 'threat_avoidance':
                return {
                    'threats_nearby': False,
                    'safety': 'secured',
                    'status': 'safe'
                }
            else:  # exploration
                return {
                    'knowledge': 'expanded',
                    'area': 'explored',
                    'discovery': 'made'
                }
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} WBM目标状态提取失败: {str(e)}")
            return {'goal_achieved': True}
    
    def _extract_action_from_rule(self, rule, target_goal):
        """从规律中提取行动建议（修复版：确保行动可执行）"""
        try:
            # 从规律的predictions中提取行动
            if hasattr(rule, 'predictions') and rule.predictions:
                if 'action' in rule.predictions:
                    raw_action = rule.predictions['action']
                    # 转换为可执行格式
                    executable_action = self._convert_to_executable_action(raw_action, target_goal)
                    if executable_action:
                        return executable_action
                elif 'move' in rule.predictions:
                    return self._convert_move_to_executable_action(rule.predictions['move'])
                elif 'behavior' in rule.predictions:
                    return self._convert_behavior_to_executable_action(rule.predictions['behavior'])
            
            # 🔧 修复：针对CDL目标类型的专门处理
            goal_type = target_goal.get('type', 'exploration')
            if goal_type == 'cdl_exploration':
                # CDL探索目标直接映射到可执行行动
                return self._get_cdl_exploration_action(target_goal)
            
            # 🔧 修复：增加基于规律类型的多样化动作生成
            if hasattr(rule, 'rule_type'):
                rule_type = rule.rule_type
                
                # 基于规律类型生成可执行动作
                executable_action = self._generate_executable_actions_from_rule_type(rule_type, goal_type, rule)
                if executable_action:
                    return executable_action
            
            # 根据目标类型推断行动（确保可执行）
            if goal_type == 'health_recovery':
                return 'collect_plant'  # 简化为可执行行动
            elif goal_type == 'food_acquisition':
                return 'collect_plant'  # 食物采集
            elif goal_type == 'water_acquisition':
                return 'drink_water'    # 水源补充
            elif goal_type == 'threat_avoidance':
                return 'escape'         # 威胁逃避
            else:
                return 'move_up'        # 默认移动行动
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 规律行动提取失败: {str(e)}")
            return 'move_up'  # 安全的默认行动

    def _convert_to_executable_action(self, raw_action, target_goal):
        """将原始行动转换为可执行的标准格式"""
        try:
            # 行动映射表：原始行动 -> 可执行行动
            action_mapping = {
                # 移动类
                'explore': 'move_up',
                'explore_random_direction': 'move_up', 
                'move': 'move_up',
                'explore_new_area': 'move_right',
                'investigate_object': 'move_down',
                'map_territory': 'move_left',
                
                # 采集类
                'collect': 'collect_plant',
                'gather': 'collect_plant',
                'collect_plant': 'collect_plant',
                'collect_food': 'collect_plant',
                'collect_healing_plant': 'collect_plant',
                'gather_food': 'collect_plant',
                'hunt_animal': 'attack_animal',
                
                # 水源类
                'drink': 'drink_water',
                'drink_water': 'drink_water',
                'find_water': 'drink_water',
                
                # 攻击类
                'attack': 'attack_animal',
                'hunt': 'attack_animal',
                'attack_animal': 'attack_animal',
                
                # 逃跑类
                'flee': 'escape',
                'escape': 'escape',
                'run_away': 'escape',
                'avoid_danger': 'escape'
            }
            
            # 直接映射
            if raw_action in action_mapping:
                return action_mapping[raw_action]
            
            # 模糊匹配
            raw_lower = raw_action.lower()
            for key, value in action_mapping.items():
                if key in raw_lower:
                    return value
            
            # 关键词匹配
            if any(word in raw_lower for word in ['move', 'go', 'walk', 'explore']):
                return 'move_up'
            elif any(word in raw_lower for word in ['collect', 'gather', 'pick']):
                return 'collect_plant'
            elif any(word in raw_lower for word in ['drink', 'water']):
                return 'drink_water'
            elif any(word in raw_lower for word in ['attack', 'hunt', 'kill']):
                return 'attack_animal'
            elif any(word in raw_lower for word in ['flee', 'escape', 'run']):
                return 'escape'
            
            return None
            
        except Exception:
            return None

    def _get_cdl_exploration_action(self, target_goal):
        """获取CDL探索目标的可执行行动"""
        try:
            # 从CDL目标的上下文中提取EOCATR信息
            context = target_goal.get('context', {})
            eocatr_action = context.get('eocatr_action', 'move')
            eocatr_object = context.get('eocatr_object', 'area')
            
            # 基于EOCATR行动类型选择可执行行动
            if eocatr_action == 'move':
                # 随机选择移动方向
                import random
                return random.choice(['move_up', 'move_down', 'move_left', 'move_right'])
            elif eocatr_action == 'interact':
                if 'animal' in eocatr_object or 'rabbit' in eocatr_object:
                    return 'attack_animal'
                else:
                    return 'collect_plant'
            elif eocatr_action == 'use':
                return 'attack_animal'  # 使用工具通常意味着攻击
            elif eocatr_action == 'observe':
                return 'move_up'  # 观察通过移动实现
            elif eocatr_action == 'search':
                return 'collect_plant'  # 搜索通过采集实现
            else:
                return 'move_up'  # 默认移动
                
        except Exception:
            return 'move_up'

    def _generate_executable_actions_from_rule_type(self, rule_type, goal_type, rule):
        """基于规律类型生成可执行动作"""
        try:
            import random
            
            # 规律类型与可执行动作的映射
            rule_action_mapping = {
                'survival': ['collect_plant', 'drink_water', 'move_up'],
                'exploration': ['move_up', 'move_down', 'move_left', 'move_right'],
                'resource_gathering': ['collect_plant', 'attack_animal', 'drink_water'],
                'threat_response': ['escape', 'move_up', 'move_down'],
                'social': ['move_up', 'move_right'],  # 简化为移动
                'environmental': ['collect_plant', 'drink_water'],
                'BMP_validated': ['collect_plant', 'move_up'],
                'BMP_candidate': ['move_left', 'move_right']
            }
            
            # 获取基础动作列表
            base_actions = rule_action_mapping.get(str(rule_type), rule_action_mapping.get('survival', ['move_up']))
            
            # 根据目标类型过滤动作
            if goal_type == 'cdl_exploration':
                # CDL探索偏向移动
                movement_actions = ['move_up', 'move_down', 'move_left', 'move_right']
                filtered_actions = [action for action in base_actions if action in movement_actions]
                if filtered_actions:
                    return random.choice(filtered_actions)
            
            return random.choice(base_actions) if base_actions else 'move_up'
            
        except Exception:
            return 'move_up'

    def _convert_move_to_executable_action(self, move_action):
        """转换移动行动为可执行格式"""
        try:
            move_mapping = {
                'up': 'move_up',
                'down': 'move_down', 
                'left': 'move_left',
                'right': 'move_right',
                'north': 'move_up',
                'south': 'move_down',
                'west': 'move_left',
                'east': 'move_right'
            }
            
            move_str = str(move_action).lower()
            for key, value in move_mapping.items():
                if key in move_str:
                    return value
            
            return 'move_up'  # 默认向上移动
            
        except Exception:
            return 'move_up'

    def _convert_behavior_to_executable_action(self, behavior_action):
        """转换行为描述为可执行格式"""
        try:
            behavior_str = str(behavior_action).lower()
            
            if any(word in behavior_str for word in ['collect', 'gather', 'pick']):
                return 'collect_plant'
            elif any(word in behavior_str for word in ['attack', 'hunt', 'fight']):
                return 'attack_animal'
            elif any(word in behavior_str for word in ['drink', 'water']):
                return 'drink_water'
            elif any(word in behavior_str for word in ['escape', 'flee', 'run']):
                return 'escape'
            elif any(word in behavior_str for word in ['move', 'go', 'walk']):
                return 'move_up'
            else:
                return 'move_up'  # 默认移动
                
        except Exception:
            return 'move_up'
    
    def _generate_diverse_actions_from_rule_type(self, rule_type, goal_type, rule):
        """基于规律类型和目标类型生成多样化动作"""
        try:
            import random
            
            # 规律类型与动作的映射
            rule_action_mapping = {
                'survival': ['explore', 'collect_plant', 'find_shelter', 'search_water'],
                'exploration': ['explore_new_area', 'investigate_object', 'search_resources', 'map_territory'],
                'resource_gathering': ['collect_plant', 'hunt_animal', 'gather_materials', 'search_water'],
                'threat_response': ['flee_from_danger', 'hide_from_predator', 'find_safe_spot', 'climb_tree'],
                'social': ['share_information', 'seek_help', 'form_alliance', 'follow_leader'],
                'environmental': ['adapt_to_weather', 'find_shelter', 'conserve_energy', 'migrate'],
                'BMP_validated': ['apply_learned_pattern', 'use_successful_strategy', 'repeat_effective_action'],
                'BMP_candidate': ['test_new_approach', 'experiment_with_variation', 'try_alternative_method']
            }
            
            # 目标类型修饰符
            goal_modifiers = {
                'threat_avoidance': ['quick_', 'safe_', 'evasive_', 'defensive_'],
                'exploration': ['curious_', 'systematic_', 'bold_', 'careful_'],
                'food_acquisition': ['efficient_', 'targeted_', 'opportunistic_'],
                'water_acquisition': ['urgent_', 'systematic_', 'cautious_'],
                'health_recovery': ['gentle_', 'restorative_', 'healing_']
            }
            
            # 获取基础动作列表
            base_actions = rule_action_mapping.get(rule_type, rule_action_mapping.get('survival', []))
            if not base_actions:
                return None
            
            # 选择一个基础动作
            base_action = random.choice(base_actions)
            
            # 添加目标修饰符
            modifiers = goal_modifiers.get(goal_type, [''])
            if modifiers and modifiers[0]:  # 如果有非空修饰符
                modifier = random.choice(modifiers)
                enhanced_action = f"{modifier}{base_action}"
            else:
                enhanced_action = base_action
            
            return enhanced_action
            
        except Exception as e:
            return None
    
    def _generate_threat_avoidance_action(self, target_goal, rule):
        """生成多样化的威胁规避动作"""
        try:
            import random
            
            # 威胁规避的多样化动作
            threat_actions = [
                'move_away_from_danger',
                'find_safe_hiding_spot', 
                'climb_to_safety',
                'retreat_to_known_area',
                'use_environment_for_cover',
                'create_distraction_and_escape',
                'seek_group_protection',
                'take_defensive_position',
                'use_tools_for_protection',
                'flee_to_water_source',
                'hide_behind_large_object',
                'move_in_zigzag_pattern'
            ]
            
            # 基于上下文选择更合适的动作
            context = target_goal.get('context', {})
            threat_count = context.get('threat_count', 1)
            
            if threat_count > 1:
                # 多威胁情况，优先选择隐藏和防御
                preferred_actions = [
                    'find_safe_hiding_spot',
                    'take_defensive_position', 
                    'seek_group_protection',
                    'use_environment_for_cover'
                ]
                return random.choice(preferred_actions)
            else:
                # 单威胁情况，可以选择更多样化的策略
                return random.choice(threat_actions)
                
        except Exception as e:
            # 🔧 重构：智能回退动作生成
            if hasattr(goal, 'goal_type'):
                if goal.goal_type.value == 'threat_avoidance':
                    return 'assess_and_respond_to_immediate_threats'
                elif goal.goal_type.value == 'resource_acquisition':
                    return 'search_and_evaluate_available_resources'
                elif goal.goal_type.value == 'exploration':
                    return 'conduct_systematic_area_survey'
                else:
                    return 'observe_environment_and_plan_response'
            else:
                return 'analyze_situation_and_determine_optimal_action'

    def _extract_action_from_rule_chain(self, rule_chain, target_goal):
        """从规律链中提取第一个可执行动作"""
        try:
            if not rule_chain:
                return None
            
            # 从第一个规律开始提取动作
            first_rule = rule_chain[0]
            return self._extract_action_from_rule(first_rule, target_goal)
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"规律链动作提取失败: {str(e)}")
            return None

    def _convert_bmp_rule_to_wbm_rule(self, bmp_rule, context):
        """将BMP规律转换为WBM规律格式"""
        try:
            from wooden_bridge_model import Rule
            
            # 如果已经是WBM Rule格式，直接返回
            if hasattr(bmp_rule, '__class__') and bmp_rule.__class__.__name__ == 'Rule':
                return bmp_rule
            
            # 从BMP规律中提取信息
            rule_id = getattr(bmp_rule, 'rule_id', f"converted_{id(bmp_rule)}")
            rule_type = getattr(bmp_rule, 'rule_type', 'survival')
            conditions = getattr(bmp_rule, 'conditions', {})
            predictions = getattr(bmp_rule, 'predictions', {})
            confidence = getattr(bmp_rule, 'confidence', 0.5)
            
            # 创建WBM Rule对象
            wbm_rule = Rule(
                rule_id=rule_id,
                rule_type=rule_type,
                conditions=conditions,
                predictions=predictions,
                confidence=confidence
            )
            
            return wbm_rule
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"BMP规律转换失败: {str(e)}")
            return None

    def _is_basic_rule_applicable(self, rule, current_context, target_goal):
        """检查基础规律是否适用于当前情况"""
        try:
            if not rule or not hasattr(rule, 'conditions'):
                return False
            
            conditions = rule.conditions
            if isinstance(conditions, dict):
                # 检查环境匹配
                if 'environment' in conditions and 'environment' in current_context:
                    if conditions['environment'] != current_context['environment']:
                        return False
                
                # 检查健康状态匹配
                if 'health_level' in conditions and 'health_level' in current_context:
                    if conditions['health_level'] != current_context['health_level']:
                        return False
                
                # 检查目标相关性
                if hasattr(rule, 'target_goals'):
                    if target_goal not in rule.target_goals:
                        return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"基础规律适用性检查失败: {str(e)}")
            return False

    def _extract_action_from_basic_rule(self, rule, target_goal):
        """从基础规律中提取动作"""
        try:
            # 首先尝试使用通用的动作提取方法
            action = self._extract_action_from_rule(rule, target_goal)
            if action and action != 'explore_random_direction':
                return action
            
            # 如果规律有特定的动作映射
            if hasattr(rule, 'action_mapping') and target_goal in rule.action_mapping:
                return rule.action_mapping[target_goal]
            
            # 默认动作映射
            default_actions = {
                'food_acquisition': 'collect_plant',
                'water_acquisition': 'explore',
                'threat_avoidance': 'explore',
                'health_recovery': 'collect_plant',
                'survival': 'explore'
            }
            
            return default_actions.get(target_goal, 'explore')
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"基础规律动作提取失败: {str(e)}")
            return 'explore'
    
    # ============================================================================
    # EOCATR系统状态查询方法 (新增)
    # ============================================================================
    
    def get_eocatr_system_status(self) -> dict:
        """
        获取EOCATR系统完整状态报告
        
        Returns:
            包含系统状态的详细字典
        """
        status_report = {
            'system_initialized': self.eocatr_initialized,
            'generation_timestamp': time.time(),
            'components_status': {},
            'generation_statistics': {},
            'matrix_coverage': {},
            'system_health': 'unknown'
        }
        
        try:
            # 1. 组件状态检查
            status_report['components_status'] = {
                'five_library_system': {
                    'active': self.five_library_system_active,
                    'initialized': self.five_library_system is not None
                },
                'bmp_system': {
                    'active': hasattr(self, 'bmp') and self.bmp is not None,
                    'initialized': hasattr(self, 'bmp')
                },
                'eocatr_generation': {
                    'active': self.eocatr_initialized,
                    'stats_available': hasattr(self, 'eocatr_generation_stats')
                }
            }
            
            # 2. 生成统计信息
            if hasattr(self, 'eocatr_generation_stats'):
                status_report['generation_statistics'] = dict(self.eocatr_generation_stats)
            
            # 3. BMP系统规律统计
            if hasattr(self, 'bmp') and self.bmp is not None:
                try:
                    bmp_stats = self.bmp.get_eocatr_generation_statistics()
                    status_report['bmp_statistics'] = bmp_stats
                except:
                    status_report['bmp_statistics'] = {'error': 'BMP统计查询失败'}
            
            # 4. 五库系统矩阵统计
            if self.five_library_system_active and self.five_library_system:
                try:
                    matrix_stats = self.five_library_system.get_eocatr_matrix_statistics()
                    status_report['matrix_coverage'] = matrix_stats
                    
                    # 完整性验证
                    if hasattr(self, 'bmp') and self.bmp is not None:
                        bmp_stats = status_report.get('bmp_statistics', {})
                        completeness = self.five_library_system.validate_eocatr_matrix_completeness(bmp_stats)
                        status_report['completeness_validation'] = completeness
                except:
                    status_report['matrix_coverage'] = {'error': '五库系统统计查询失败'}
            
            # 5. 系统健康状态评估
            health_score = 0
            max_score = 4
            
            if status_report['components_status']['five_library_system']['active']:
                health_score += 1
            if status_report['components_status']['bmp_system']['active']:
                health_score += 1
            if status_report['components_status']['eocatr_generation']['active']:
                health_score += 1
            if status_report['generation_statistics'].get('total_generated', 0) > 0:
                health_score += 1
            
            health_percentage = (health_score / max_score) * 100
            
            if health_percentage >= 100:
                status_report['system_health'] = 'excellent'
            elif health_percentage >= 75:
                status_report['system_health'] = 'good'
            elif health_percentage >= 50:
                status_report['system_health'] = 'fair'
            elif health_percentage >= 25:
                status_report['system_health'] = 'poor'
            else:
                status_report['system_health'] = 'critical'
            
            status_report['health_score'] = f"{health_score}/{max_score} ({health_percentage:.1f}%)"
            
        except Exception as e:
            status_report['error'] = str(e)
            status_report['system_health'] = 'error'
        
        return status_report
    
    def get_eocatr_rule_coverage_report(self) -> dict:
        """
        获取EOCATR规律覆盖率详细报告
        
        Returns:
            包含规律覆盖情况的详细字典
        """
        coverage_report = {
            'report_timestamp': time.time(),
            'theoretical_total': 0,
            'generated_total': 0,
            'coverage_percentage': 0.0,
            'rule_type_breakdown': {},
            'matrix_dimension_coverage': {},
            'quality_assessment': {}
        }
        
        try:
            # 获取理论规律总数
            if self.five_library_system_active and self.five_library_system:
                matrix_stats = self.five_library_system.get_eocatr_matrix_statistics()
                coverage_report['theoretical_total'] = matrix_stats.get('total_theoretical_rules', 0)
                coverage_report['matrix_dimension_coverage'] = matrix_stats.get('matrix_dimensions', {})
            
            # 获取已生成规律数量
            if hasattr(self, 'eocatr_generation_stats'):
                coverage_report['generated_total'] = self.eocatr_generation_stats.get('total_generated', 0)
            
            # 计算覆盖率
            if coverage_report['theoretical_total'] > 0:
                coverage_report['coverage_percentage'] = (
                    coverage_report['generated_total'] / coverage_report['theoretical_total']
                ) * 100
            
            # BMP规律类型分析
            if hasattr(self, 'bmp') and self.bmp is not None:
                try:
                    bmp_stats = self.bmp.get_eocatr_generation_statistics()
                    if 'systematic_eocatr_rules' in bmp_stats:
                        coverage_report['rule_type_breakdown'] = bmp_stats['systematic_eocatr_rules']
                except:
                    coverage_report['rule_type_breakdown'] = {'error': 'BMP规律分析失败'}
            
            # 质量评估
            coverage_percentage = coverage_report['coverage_percentage']
            if coverage_percentage >= 90:
                coverage_report['quality_assessment'] = {
                    'level': 'excellent',
                    'description': '覆盖率优秀,系统性规律生成完整'
                }
            elif coverage_percentage >= 70:
                coverage_report['quality_assessment'] = {
                    'level': 'good',
                    'description': '覆盖率良好,基本满足决策需求'
                }
            elif coverage_percentage >= 50:
                coverage_report['quality_assessment'] = {
                    'level': 'fair',
                    'description': '覆盖率中等,可能影响决策质量'
                }
            elif coverage_percentage >= 25:
                coverage_report['quality_assessment'] = {
                    'level': 'poor',
                    'description': '覆盖率偏低,需要改进规律生成'
                }
            else:
                coverage_report['quality_assessment'] = {
                    'level': 'critical',
                    'description': '覆盖率极低,系统可能无法正常工作'
                }
            
        except Exception as e:
            coverage_report['error'] = str(e)
            coverage_report['quality_assessment'] = {
                'level': 'error',
                'description': f'报告生成失败: {str(e)}'
            }
        
        return coverage_report
    
    def print_eocatr_status_summary(self):
        """
        打印EOCATR系统状态摘要(用于调试和监控)
        """
        if not logger:
            return
        
        try:
            status = self.get_eocatr_system_status()
            coverage = self.get_eocatr_rule_coverage_report()
            
            logger.log(f"\n=== {self.name} EOCATR系统状态摘要 ===")
            logger.log(f"系统初始化: {'✅' if status['system_initialized'] else '❌'}")
            logger.log(f"系统健康度: {status['health_score']} ({status['system_health']})")
            
            logger.log(f"\n组件状态:")
            components = status['components_status']
            logger.log(f"  五库系统: {'✅' if components['five_library_system']['active'] else '❌'}")
            logger.log(f"  BMP系统: {'✅' if components['bmp_system']['active'] else '❌'}")
            logger.log(f"  EOCATR生成: {'✅' if components['eocatr_generation']['active'] else '❌'}")
            
            logger.log(f"\n规律覆盖情况:")
            logger.log(f"  理论总数: {coverage['theoretical_total']:,}")
            logger.log(f"  已生成数: {coverage['generated_total']:,}")
            logger.log(f"  覆盖率: {coverage['coverage_percentage']:.2f}%")
            logger.log(f"  质量评估: {coverage['quality_assessment']['level']} - {coverage['quality_assessment']['description']}")
            
            if 'generation_statistics' in status and status['generation_statistics']:
                stats = status['generation_statistics']
                logger.log(f"\n生成统计:")
                logger.log(f"  配置ID: {stats.get('matrix_config_id', 'N/A')}")
                logger.log(f"  生成时间: {stats.get('generation_time', 0):.3f}秒")
                logger.log(f"  上次生成: {time.strftime('%H:%M:%S', time.localtime(stats.get('last_generation_timestamp', 0)))}")
            
        except Exception as e:
            logger.log(f"❌ {self.name} EOCATR状态摘要生成失败: {str(e)}")

    def _build_eocatr_matrix_config(self, game, goal) -> Dict:
        """构建EOCATR矩阵配置"""
        try:
            # 收集当前环境信息
            environments = [self._get_current_environment_type(game)]
            
            # 收集可见的对象
            objects = []
            nearby_resources = self._get_nearby_resources(game)
            for resource in nearby_resources:
                objects.append(resource.get('type', 'unknown'))
            
            # 收集威胁对象
            threats = self.detect_threats(game.game_map)
            for threat in threats:
                objects.append(threat.get('type', 'unknown'))
            
            # 基于目标类型确定特征
            attributes = []
            if hasattr(goal, 'goal_type'):
                if goal.goal_type.value == 'survival':
                    attributes.extend(['血量低', '危险', '紧急'])
                elif goal.goal_type.value == 'resource_acquisition':
                    attributes.extend(['距离近', '营养丰富', '可食用'])
                elif goal.goal_type.value == 'exploration':
                    attributes.extend(['未探索', '新颖', '安全'])
                elif goal.goal_type.value == 'threat_avoidance':
                    attributes.extend(['危险', '距离近', '威胁高'])
            
            # 基于当前状态添加特征
            if self.health < 30:
                attributes.append('血量低')
            if self.food < 30:
                attributes.append('营养缺乏')
            if self.water < 30:
                attributes.append('缺水')
            
            # 定义可能的行动
            actions = ['移动', '采集', '攻击', '逃避', '观察', '探索']
            
            # 定义可能的工具
            tools = ['无工具', '石头', '木棍', '陷阱']
            
            # 定义可能的结果
            results = ['成功', '失败', '获得食物', '受到伤害', '成功逃脱', '发现信息']
            
            return {
                'environments': environments,
                'objects': list(set(objects)) if objects else ['未知对象'],
                'attributes': list(set(attributes)) if attributes else ['未知特征'],
                'actions': actions,
                'tools': tools,
                'results': results
            }
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 构建EOCATR配置失败: {str(e)}")
            return {
                'environments': ['开阔地'],
                'objects': ['草莓', '蘑菇'],
                'attributes': ['距离近', '安全'],
                'actions': ['移动', '采集'],
                'tools': ['无工具'],
                'results': ['成功', '失败']
            }

    def _convert_bmp_rule_to_action(self, rule, goal, game) -> str:
        """将BMP规律转换为WBM可执行的行动"""
        try:
            # 从规律的预测中提取行动建议
            if hasattr(rule, 'predictions') and rule.predictions:
                # 查找行动相关的预测
                for key, value in rule.predictions.items():
                    if 'action' in key.lower() or 'move' in key.lower():
                        return str(value)
            
            # 从规律的条件中推断行动
            if hasattr(rule, 'conditions') and rule.conditions:
                for key, value in rule.conditions.items():
                    if key == 'action':
                        return str(value)
            
            # 从规律的模式中提取行动
            if hasattr(rule, 'pattern') and rule.pattern:
                pattern_lower = rule.pattern.lower()
                if '采集' in pattern_lower or 'collect' in pattern_lower:
                    return 'gather'
                elif '攻击' in pattern_lower or 'attack' in pattern_lower:
                    return 'attack'
                elif '逃避' in pattern_lower or 'flee' in pattern_lower:
                    return 'flee'
                elif '移动' in pattern_lower or 'move' in pattern_lower:
                    return random.choice(['up', 'down', 'left', 'right'])
                elif '探索' in pattern_lower or 'explore' in pattern_lower:
                    return random.choice(['up', 'down', 'left', 'right'])
                elif '观察' in pattern_lower or 'observe' in pattern_lower:
                    return 'wait'
            
            # 基于目标类型推断行动
            if hasattr(goal, 'goal_type'):
                if goal.goal_type.value == 'resource_acquisition':
                    # 如果有附近的资源，朝资源移动
                    nearby_resources = self._get_nearby_resources(game)
                    if nearby_resources:
                        return 'gather'
                    else:
                        return random.choice(['up', 'down', 'left', 'right'])
                elif goal.goal_type.value == 'threat_avoidance':
                    return 'flee'
                elif goal.goal_type.value == 'exploration':
                    return random.choice(['up', 'down', 'left', 'right'])
            
            # 默认返回探索行动
            return random.choice(['up', 'down', 'left', 'right'])
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} BMP规律转换行动失败: {str(e)}")
            return random.choice(['up', 'down', 'left', 'right'])


#
# 游戏主控制类
#
    def add_eocatr_experience_to_unified_system(self, action, result, context=None):
        """添加EOCATR格式经验到统一系统"""
        try:
            from eocatr_unified_format import create_unified_eocatr
            
            # 构建EOCATR经验
            eocatr_experience = create_unified_eocatr(
                environment=context.get('environment') if context else self._get_current_environment_detailed(),
                object_name=context.get('object') if context else self._get_current_object_detailed(),
                action=action,
                tool=context.get('tool', 'no_tool') if context else 'no_tool',
                result=result,
                characteristics=context.get('characteristics') if context else self._get_current_characteristics_detailed(),
                player_id=self.name,
                success='success' in result.lower() if isinstance(result, str) else True,
                reward=context.get('reward', 1.0) if context else 1.0
            )
            
            # 添加到BMP生成器
            if hasattr(self, 'unified_decision_system') and self.unified_decision_system:
                rules = self.unified_decision_system.add_experiences_to_bmp([eocatr_experience])
                
                if self.logger and rules:
                    self.logger.log(f"{self.name} EOCATR经验生成了 {len(rules)} 个新规律")
            
            # 同时添加到五库系统
            if hasattr(self, 'five_library_system') and self.five_library_system:
                self.five_library_system.add_experience_to_direct_library(
                    action=action,
                    result=result,
                    context=context or {}
                )
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} EOCATR经验处理失败: {str(e)}")

    def _record_tool_usage(self, tool, target_type, success, damage_or_gain=0):
        """记录工具使用情况并更新学习经验 - 支持真实学习机制"""
        # 🧠 更新工具学习数据（核心学习机制）
        self._update_tool_learning_data(tool, target_type, success, damage_or_gain)
        
        # 保持原有统计功能
        if not hasattr(self, 'tool_usage_stats'):
            self.tool_usage_stats = {}
        
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {
                'total_uses': 0,
                'successful_uses': 0,
                'target_types': {},
                'total_gain': 0
            }
        
        stats = self.tool_usage_stats[tool_name]
        stats['total_uses'] += 1
        
        if success:
            stats['successful_uses'] += 1
            stats['total_gain'] += damage_or_gain
        
        if target_type not in stats['target_types']:
            stats['target_types'][target_type] = {'uses': 0, 'successes': 0}
        
        stats['target_types'][target_type]['uses'] += 1
        if success:
            stats['target_types'][target_type]['successes'] += 1
        
        # 统一日志格式
        success_rate = (stats['successful_uses'] / stats['total_uses']) * 100
        if hasattr(self, 'logger') and self.logger:
            self.logger.log(f"📚 记录{tool_name}{'攻击' if 'animal' in target_type else '采集'}: {target_type} {'成功' if success else '失败'}")
        
        # 写入工具使用调试文件
        debug_file = f"logs/ilai_{self.name}/tool_usage_debug.txt"
        import os
        os.makedirs(os.path.dirname(debug_file), exist_ok=True)
        
        with open(debug_file, "a", encoding="utf-8") as f:
            f.write(f"🔧 {self.name} 工具使用: {tool_name} 对 {target_type} "
                   f"成功={success} 收益/伤害={damage_or_gain} "
                   f"总成功率={success_rate:.1f}%\n")
    
    def _update_tool_learning_data(self, tool, target_type, success, damage_or_gain):
        """更新工具学习数据 - 核心学习机制"""
        try:
            tool_name = getattr(tool, 'name', tool.__class__.__name__)
            
            # 创建经验键
            experience_key = (tool_name, target_type)
            
            # 初始化或更新工具效果数据
            if experience_key not in self.tool_effectiveness:
                self.tool_effectiveness[experience_key] = {
                    'successes': 0,
                    'attempts': 0,
                    'total_damage_or_gain': 0,
                    'effectiveness': 0.5  # 初始假设50%成功率
                }
            
            # 更新统计数据
            data = self.tool_effectiveness[experience_key]
            data['attempts'] += 1
            if success:
                data['successes'] += 1
            data['total_damage_or_gain'] += damage_or_gain
            
            # 重新计算效果率
            data['effectiveness'] = data['successes'] / data['attempts']
            
            # 更新实验计数
            if tool_name not in self.tool_experiment_counts:
                self.tool_experiment_counts[tool_name] = 0
            self.tool_experiment_counts[tool_name] += 1
            
            # 🎓 学习日志
            if self.logger and data['attempts'] % 5 == 0:  # 每5次尝试记录一次学习进度
                effectiveness_percent = data['effectiveness'] * 100
                self.logger.log(f"🎓 {self.name} 学习进度: {tool_name}对{target_type}效果率{effectiveness_percent:.1f}% ({data['successes']}/{data['attempts']})")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️ {self.name} 工具学习数据更新失败: {str(e)}")
    
    def _execute_next_plan_step(self, game):
        """执行多步计划的下一个步骤"""
        try:
            if self.current_plan is None or 'steps' not in self.current_plan:
                return {'status': 'failed', 'reason': '无效的计划结构'}
            
            steps = self.current_plan['steps']
            if self.current_plan_step >= len(steps):
                return {'status': 'completed', 'reason': '所有步骤已完成'}
            
            current_step = steps[self.current_plan_step]
            action = current_step.get('action', '')
            
            if logger:
                logger.log(f"{self.name} 🎯 执行计划步骤 {self.current_plan_step + 1}: {action}")
            
            # 执行当前步骤的行动
            execution_result = self._execute_planned_action(action, game)
            
            # 记录执行结果
            step_result = {
                'step_index': self.current_plan_step,
                'action': action,
                'success': execution_result.get('success', False),
                'result': execution_result,
                'timestamp': time.time()
            }
            self.plan_execution_history.append(step_result)
            
            # 检查步骤是否成功
            if execution_result.get('success', False):
                self.current_plan_step += 1
                
                # 检查是否完成了所有步骤
                if self.current_plan_step >= len(steps):
                    return {'status': 'completed', 'reason': '计划执行成功'}
                else:
                    return {'status': 'continue', 'reason': '步骤成功，继续下一步'}
            else:
                # 步骤失败，检查是否可以重试
                self.plan_failure_count += 1
                if self.plan_failure_count >= 3:  # 最多重试3次
                    return {'status': 'failed', 'reason': f'步骤执行失败次数过多: {action}'}
                else:
                    return {'status': 'continue', 'reason': f'步骤失败但可重试: {action}'}
                    
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 计划步骤执行异常: {str(e)}")
            return {'status': 'failed', 'reason': f'执行异常: {str(e)}'}
    
    def _is_plan_still_valid(self, game):
        """检查当前计划是否仍然有效"""
        try:
            if self.current_plan is None:
                return False
            
            # 检查计划的前提条件是否仍然满足
            plan_goal = self.current_plan.get('goal', {})
            goal_type = plan_goal.get('type', '')
            
            # 根据目标类型检查有效性
            if goal_type == 'find_food':
                # 如果食物已经充足，计划可能不再必要
                if self.food > 70:
                    return False
            elif goal_type == 'find_water':
                # 如果水分已经充足，计划可能不再必要
                if self.water > 70:
                    return False
            elif goal_type == 'avoid_danger':
                # 检查威胁是否仍然存在
                min_threat_distance = self._get_min_threat_distance(game)
                if min_threat_distance > 10:  # 威胁已经远离
                    return False
            
            # 检查计划是否已经过时（超过5个回合）
            plan_age = time.time() - self.current_plan.get('created_time', 0)
            if plan_age > 300:  # 5分钟（假设每回合1分钟）
                return False
            
            return True
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 计划有效性检查异常: {str(e)}")
            return False
    
    def _reset_plan_state(self):
        """重置计划状态"""
        try:
            if self.current_plan is not None and logger:
                logger.log(f"{self.name} 🔄 重置多步计划状态")
            
            self.current_plan = None
            self.current_plan_step = 0
            self.plan_failure_count = 0
            
            # 更新统计信息
            if len(self.plan_execution_history) > 0:
                total_plans = self.multi_step_stats['plans_created']
                completed_plans = self.multi_step_stats['plans_completed']
                self.multi_step_stats['plan_success_rate'] = completed_plans / total_plans if total_plans > 0 else 0.0
                
                # 计算平均计划长度
                if self.plan_execution_history:
                    total_steps = sum(len(plan.get('steps', [])) for plan in [self.current_plan] if plan)
                    self.multi_step_stats['average_plan_length'] = total_steps / total_plans if total_plans > 0 else 0.0
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 计划状态重置异常: {str(e)}")
    
    def _generate_multi_step_plan(self, goal, game):
        """基于BPU算法生成多步规划来实现目标"""
        try:
            if logger:
                logger.log(f"{self.name} 🌉 BPU开始造桥: 目标 {goal}")
            
            # 第1步: 定义起点和终点
            current_state = self._get_current_state_for_planning(game)
            goal_condition = self._extract_goal_condition(goal)
            
            if logger:
                logger.log(f"{self.name} 🎯 起点状态: {current_state}")
                logger.log(f"{self.name} 🏁 目标条件: {goal_condition}")
            
            # 第2步: 收集所有可用的"建材"（规律）
            available_rules = self._collect_relevant_rules(goal, current_state)
            
            if not available_rules:
                if logger:
                    logger.log(f"{self.name} ❌ 没有找到相关规律，回退到简单计划")
                return self._generate_fallback_plan(goal, game)
            
            if logger:
                logger.log(f"{self.name} 🧱 收集到 {len(available_rules)} 条相关规律")
            
            # 第3步: 基于规律的图搜索算法（BPU造桥核心）
            candidate_plans = self._bpu_bridge_search(current_state, goal_condition, available_rules)
            
            if not candidate_plans:
                if logger:
                    logger.log(f"{self.name} ❌ BPU搜索未找到有效路径，回退到简单计划")
                return self._generate_fallback_plan(goal, game)
            
            # 第4步: 使用BPU公式评估所有候选计划
            best_plan = self._evaluate_plans_with_bpu(candidate_plans, goal)
            
            if best_plan:
                if logger:
                    logger.log(f"{self.name} 🏆 BPU选择最优计划: {len(best_plan['steps'])}步, 效用分: {best_plan.get('bpu_score', 0):.2f}")
                return best_plan
            
            return None
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} ⚠️ BPU多步计划生成失败: {str(e)}")
                import traceback
                logger.log(f"详细错误: {traceback.format_exc()}")
            return self._generate_fallback_plan(goal, game)
    
    def _generate_water_seeking_plan(self, game):
        """生成寻找水源的多步计划"""
        steps = []
        
        # 步骤1: 探索附近寻找水源
        steps.append({'action': 'move_up', 'description': '向北探索寻找水源'})
        steps.append({'action': 'move_right', 'description': '向东继续搜索'})
        steps.append({'action': 'move_down', 'description': '向南搜索水源'})
        
        # 如果在河流或池塘附近，添加饮水步骤
        current_cell = game.game_map.grid[self.y][self.x] if hasattr(game, 'game_map') else 'unknown'
        if current_cell in ['river', 'puddle']:
            steps.append({'action': 'drink_water', 'description': '在水源处饮水'})
        
        return steps
    
    def _generate_food_seeking_plan(self, game):
        """生成寻找食物的多步计划"""
        steps = []
        
        # 步骤1: 系统性搜索食物
        steps.append({'action': 'move_left', 'description': '向西搜索食物'})
        steps.append({'action': 'collect_plant', 'description': '收集发现的植物'})
        steps.append({'action': 'move_up', 'description': '继续向北搜索'})
        steps.append({'action': 'collect_plant', 'description': '收集更多食物'})
        
        return steps
    
    def _generate_threat_avoidance_plan(self, game):
        """生成威胁规避的多步计划"""
        steps = []
        
        # 检测威胁位置并制定逃跑路线
        threats = self.detect_threats(game.game_map) if hasattr(self, 'detect_threats') else []
        
        if threats:
            # 步骤1: 快速远离威胁
            steps.append({'action': 'move_left', 'description': '快速向西逃离威胁'})
            steps.append({'action': 'move_left', 'description': '继续远离威胁区域'})
            steps.append({'action': 'move_up', 'description': '向安全区域移动'})
            # 步骤2: 寻找安全位置
            steps.append({'action': 'move_up', 'description': '寻找更安全的位置'})
        
        return steps
    
    def _generate_exploration_plan(self, game):
        """生成探索的多步计划"""
        steps = []
        
        # 系统性探索周围区域
        steps.append({'action': 'move_up', 'description': '向北探索未知区域'})
        steps.append({'action': 'move_right', 'description': '向东继续探索'})
        steps.append({'action': 'move_down', 'description': '向南探索新区域'})
        steps.append({'action': 'move_left', 'description': '向西完成区域探索'})
        
        return steps
    
    def _generate_general_survival_plan(self, game):
        """生成通用生存计划"""
        steps = []
        
        # 根据当前状态制定计划
        if self.water < 50:
            steps.extend(self._generate_water_seeking_plan(game))
        
        if self.food < 50:
            steps.extend(self._generate_food_seeking_plan(game))
        
        # 如果没有紧急需求，进行探索
        if not steps:
            steps.extend(self._generate_exploration_plan(game))
        
        return steps
    
    def _get_current_state_for_planning(self, game):
        """获取当前状态用于规划"""
        return {
            'position': (self.x, self.y),
            'health': self.health,
            'food': self.food,
            'water': self.water,
            'current_cell': game.game_map.grid[self.y][self.x] if hasattr(game, 'game_map') else 'unknown',
            'tools': [tool.name for tool in getattr(self, 'tools', [])],
            'nearby_threats': len(self.detect_threats(game.game_map)) if hasattr(self, 'detect_threats') else 0
        }
    
    def _extract_goal_condition(self, goal):
        """从目标中提取完成条件"""
        goal_str = str(goal).lower()
        
        if 'water' in goal_str:
            return {'type': 'water', 'condition': 'water > 90'}
        elif 'food' in goal_str:
            return {'type': 'food', 'condition': 'food > 90'}
        elif 'threat' in goal_str or 'danger' in goal_str:
            return {'type': 'safety', 'condition': 'nearby_threats == 0'}
        elif 'exploration' in goal_str:
            return {'type': 'exploration', 'condition': 'new_area_discovered'}
        else:
            return {'type': 'general', 'condition': 'health > 80 and food > 50 and water > 50'}
    
    def _collect_relevant_rules(self, goal, current_state):
        """收集与目标相关的所有规律"""
        relevant_rules = []
        
        try:
            # 从直接规律库收集规律
            if hasattr(self, 'five_library_system') and self.five_library_system:
                direct_rules = self._get_rules_from_direct_library(goal)
                relevant_rules.extend(direct_rules)
            
            # 从总规律库收集规律
            total_rules = self._get_rules_from_total_library(goal)
            relevant_rules.extend(total_rules)
            
            # 从BPM生成新规律
            bmp_rules = self._get_rules_from_bmp(goal, current_state)
            relevant_rules.extend(bmp_rules)
            
            # 添加基础生存规律
            basic_rules = self._get_basic_survival_rules_for_bpu(goal)
            relevant_rules.extend(basic_rules)
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 规律收集异常: {str(e)}")
        
        return relevant_rules
    
    def _get_rules_from_direct_library(self, goal):
        """从直接规律库获取相关规律"""
        from wooden_bridge_model import Rule
        rules = []
        try:
            # 实际查询direct_rules.db数据库
            import sqlite3
            import os
            
            db_path = "five_libraries/direct_rules.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 查询验证过的规律 - 修复字段名
                cursor.execute("SELECT * FROM direct_rules WHERE validation_status='validated' LIMIT 20")
                db_rules = cursor.fetchall()
                
                # 获取列名
                column_names = [description[0] for description in cursor.description]
                
                for row in db_rules:
                    rule_data = dict(zip(column_names, row))
                    try:
                        # 转换为WBM Rule对象 - 修复字段名
                        import json
                        try:
                            conditions = json.loads(rule_data.get('conditions', '{}'))
                        except:
                            conditions = {}
                        try:
                            predictions = json.loads(rule_data.get('predictions', '{}'))
                        except:
                            predictions = {}
                            
                        wbm_rule = Rule(
                            rule_id=rule_data.get('rule_id', f"direct_rule_{rule_data.get('id', 'unknown')}"),
                            rule_type=rule_data.get('rule_type', 'action'),
                            conditions=conditions,
                            predictions=predictions,
                            confidence=float(rule_data.get('confidence', 0.5))
                        )
                        rules.append(wbm_rule)
                    except Exception as e:
                        if self.logger:
                            self.logger.log(f"{self.name} 转换直接规律失败: {str(e)}")
                
                conn.close()
                
                if self.logger:
                    self.logger.log(f"{self.name} 📋 从直接规律库获取 {len(rules)} 条规律")
            else:
                # 如果数据库不存在，使用模拟规律
                goal_str = str(goal).lower()
                if 'water' in goal_str:
                    rules.extend([
                        Rule(
                            rule_id='direct_water_1',
                            rule_type='action',
                            conditions={'current_cell': 'open_field'},
                            predictions={'water_discovery_chance': 0.7},
                            confidence=0.85
                        ),
                        Rule(
                            rule_id='direct_water_2',
                            rule_type='action', 
                            conditions={'current_cell': 'river'},
                            predictions={'water_gain': 40},
                            confidence=0.95
                        )
                    ])
                elif 'food' in goal_str:
                    rules.extend([
                        Rule(
                            rule_id='direct_food_1',
                            rule_type='action',
                            conditions={'current_cell': 'open_field'},
                            predictions={'food_discovery_chance': 0.6},
                            confidence=0.80
                        ),
                        Rule(
                            rule_id='direct_food_2',
                            rule_type='action',
                            conditions={'nearby_plant': True},
                            predictions={'food_gain': 8},
                            confidence=0.90
                        )
                    ])
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 直接规律库查询失败: {str(e)}")
        
        return rules
    
    def _get_rules_from_total_library(self, goal):
        """从总规律库获取相关规律"""
        from wooden_bridge_model import Rule
        rules = []
        try:
            # 实际查询rule_knowledge.db数据库
            import sqlite3
            import os
            
            db_path = "five_libraries/rule_knowledge.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 查询验证过的规律
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
                        db_rules = cursor.fetchall()
                        
                        column_names = [description[0] for description in cursor.description]
                        
                        for row in db_rules:
                            rule_data = dict(zip(column_names, row))
                            try:
                                # 转换为WBM Rule对象
                                wbm_rule = Rule(
                                    rule_id=rule_data.get('rule_id', f"total_rule_{table_name}_{rule_data.get('id', 'unknown')}"),
                                    rule_type=rule_data.get('rule_type', 'knowledge'),
                                    conditions=eval(rule_data.get('conditions', '{}')) if rule_data.get('conditions') else {},
                                    predictions=eval(rule_data.get('predictions', '{}')) if rule_data.get('predictions') else {},
                                    confidence=float(rule_data.get('confidence', 0.6))
                                )
                                rules.append(wbm_rule)
                            except Exception as e:
                                if self.logger:
                                    self.logger.log(f"{self.name} 转换总规律失败: {str(e)}")
                    except Exception as e:
                        continue
                
                conn.close()
                
                if self.logger and rules:
                    self.logger.log(f"{self.name} 📚 从总规律库获取 {len(rules)} 条规律")
            else:
                # 如果数据库不存在，使用模拟规律
                goal_str = str(goal).lower()
                if 'water' in goal_str:
                    rules.append(Rule(
                        rule_id='total_water_1',
                        rule_type='knowledge',
                        conditions={'position': 'any'},
                        predictions={'water_discovery_strategy': 'find_high_ground'},
                        confidence=0.75
                    ))
                elif 'exploration' in goal_str:
                    rules.append(Rule(
                        rule_id='total_explore_1',
                        rule_type='knowledge',
                        conditions={'position': 'any'},
                        predictions={'exploration_efficiency': 0.3},
                        confidence=0.90
                    ))
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 总规律库查询失败: {str(e)}")
        
        return rules
    
    def _get_rules_from_bmp(self, goal, current_state):
        """从BPM生成相关规律"""
        rules = []
        try:
            if hasattr(self, 'bpm') and self.bpm:
                # 获取BPM的验证规律
                bmp_validated_rules = self.bpm.get_all_validated_rules()
                
                for bmp_rule in bmp_validated_rules:
                    # 使用新的to_wbm_format方法转换格式
                    if hasattr(bmp_rule, 'to_wbm_format'):
                        try:
                            wbm_rule = bmp_rule.to_wbm_format()
                            # 检查规律是否与目标相关
                            if self._is_bmp_rule_relevant_to_goal(wbm_rule, goal):
                                rules.append(wbm_rule)
                                if logger:
                                    logger.log(f"{self.name} 🔄 BMP规律转换成功: {wbm_rule['id']}")
                        except Exception as e:
                            if logger:
                                logger.log(f"{self.name} BMP规律转换失败: {str(e)}")
                    else:
                        # 回退到手动转换
                        wbm_rule = self._manual_convert_bmp_rule(bmp_rule, goal)
                        if wbm_rule:
                            rules.append(wbm_rule)
                
                if logger and rules:
                    logger.log(f"{self.name} 📋 从BMP获取到 {len(rules)} 条相关规律")
                    
        except Exception as e:
            if logger:
                logger.log(f"{self.name} BPM规律生成失败: {str(e)}")
        
        return rules
    
    def _is_bmp_rule_relevant_to_goal(self, wbm_rule, goal):
        """检查BMP规律是否与目标相关"""
        try:
            goal_str = str(goal).lower()
            rule_action = wbm_rule.get('action', '').lower()
            rule_result = str(wbm_rule.get('result', {})).lower()
            
            # 基于目标类型的相关性检查
            if 'water' in goal_str:
                return any(keyword in rule_action or keyword in rule_result 
                          for keyword in ['water', 'drink', 'hydrat', 'river', 'stream'])
            elif 'food' in goal_str:
                return any(keyword in rule_action or keyword in rule_result 
                          for keyword in ['food', 'eat', 'plant', 'forage', 'collect', 'hunt'])
            elif 'explore' in goal_str:
                return any(keyword in rule_action or keyword in rule_result 
                          for keyword in ['move', 'explore', 'search', 'discover', 'wander'])
            elif 'safe' in goal_str or 'threat' in goal_str:
                return any(keyword in rule_action or keyword in rule_result 
                          for keyword in ['flee', 'escape', 'avoid', 'safe', 'hide', 'retreat'])
            else:
                # 默认认为所有规律都可能相关
                return True
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 规律相关性检查失败: {str(e)}")
            return True  # 出错时保守地认为相关
    
    def _manual_convert_bmp_rule(self, bmp_rule, goal):
        """手动转换BMP规律为WBM格式（回退方案）"""
        try:
            # 尝试从BMP规律中提取基本信息
            rule_id = getattr(bmp_rule, 'rule_id', f'bmp_rule_{id(bmp_rule)}')
            pattern = getattr(bmp_rule, 'pattern', '')
            confidence = getattr(bmp_rule, 'confidence', 0.5)
            
            # 简单的动作提取
            action = 'unknown_action'
            if hasattr(bmp_rule, 'conditions'):
                conditions = bmp_rule.conditions
                if isinstance(conditions, dict) and 'action' in conditions:
                    action = conditions['action']
            
            # 从pattern中提取动作（如果可能）
            if action == 'unknown_action' and pattern:
                # 简单的模式匹配
                common_actions = ['move', 'drink', 'eat', 'collect', 'search', 'explore', 'flee', 'attack']
                for act in common_actions:
                    if act in pattern.lower():
                        action = act
                        break
            
            # 构建WBM格式
            wbm_rule = {
                'id': rule_id,
                'condition': getattr(bmp_rule, 'conditions', {}),
                'action': action,
                'result': getattr(bmp_rule, 'predictions', {}),
                'confidence': confidence,
                'source': 'bmp_manual_conversion',
                'original_pattern': pattern
            }
            
            return wbm_rule
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 手动转换BMP规律失败: {str(e)}")
            return None

    def _get_basic_survival_rules_for_bpu(self, goal):
        """获取基础生存规律用于BPU"""
        rules = []
        
        # 基础移动规律
        rules.append({
            'id': 'basic_move_north',
            'condition': {'position': 'any'},
            'action': 'move_up',
            'result': {'position_change': (0, -1)},
            'confidence': 0.95,
            'source': 'basic_knowledge'
        })
        
        rules.append({
            'id': 'basic_move_south',
            'condition': {'position': 'any'},
            'action': 'move_down', 
            'result': {'position_change': (0, 1)},
            'confidence': 0.95,
            'source': 'basic_knowledge'
        })
        
        rules.append({
            'id': 'basic_move_east',
            'condition': {'position': 'any'},
            'action': 'move_right',
            'result': {'position_change': (1, 0)},
            'confidence': 0.95,
            'source': 'basic_knowledge'
        })
        
        rules.append({
            'id': 'basic_move_west',
            'condition': {'position': 'any'},
            'action': 'move_left',
            'result': {'position_change': (-1, 0)},
            'confidence': 0.95,
            'source': 'basic_knowledge'
        })
        
        # 基础资源获取规律
        goal_str = str(goal).lower()
        if 'water' in goal_str:
            rules.extend([
                {
                    'id': 'basic_drink_water',
                    'condition': {'current_cell': 'river'},
                    'action': 'drink_water',
                    'result': {'water_gain': 50},
                    'confidence': 0.98,
                    'source': 'basic_knowledge'
                },
                {
                    'id': 'basic_find_water',
                    'condition': {'position': 'any'},
                    'action': 'search_for_water',
                    'result': {'water_gain': 30},
                    'confidence': 0.70,
                    'source': 'basic_knowledge'
                },
                {
                    'id': 'basic_emergency_water',
                    'condition': {'water_low': True},
                    'action': 'emergency_hydration',
                    'result': {'water_gain': 65},
                    'confidence': 0.85,
                    'source': 'basic_knowledge'
                }
            ])
            
        elif 'food' in goal_str:
            rules.extend([
                {
                    'id': 'basic_collect_plant',
                    'condition': {'nearby_plant': True},
                    'action': 'collect_plant',
                    'result': {'food_gain': 7},
                    'confidence': 0.85,
                    'source': 'basic_knowledge'
                },
                {
                    'id': 'basic_forage',
                    'condition': {'position': 'any'},
                    'action': 'forage_for_food',
                    'result': {'food_gain': 20},
                    'confidence': 0.75,
                    'source': 'basic_knowledge'
                },
                {
                    'id': 'basic_emergency_food',
                    'condition': {'food_low': True},
                    'action': 'emergency_foraging',
                    'result': {'food_gain': 45},
                    'confidence': 0.80,
                    'source': 'basic_knowledge'
                }
            ])
        
        return rules
    
    def _bpu_bridge_search(self, start_state, goal_condition, available_rules):
        """BPU造桥核心算法：基于规律的图搜索"""
        candidate_plans = []
        
        try:
            # 初始化搜索队列（开放列表）
            open_list = [{'state': start_state, 'path': [], 'cost': 0}]
            closed_set = set()
            max_iterations = 50  # 防止无限循环
            max_plan_length = 6   # 最大计划长度
            max_plans = 5        # 最大候选计划数
            
            iteration = 0
            while open_list and len(candidate_plans) < max_plans and iteration < max_iterations:
                iteration += 1
                
                # 选择最有希望的半成品桥（启发式：成本最低）
                current = min(open_list, key=lambda x: x['cost'])
                open_list.remove(current)
                
                current_state = current['state']
                current_path = current['path']
                current_cost = current['cost']
                
                # 避免重复状态
                state_key = self._state_to_key(current_state)
                if state_key in closed_set:
                    continue
                closed_set.add(state_key)
                
                # 检查是否达到目标
                if self._check_goal_achieved(current_state, goal_condition):
                    if len(current_path) > 0:  # 确保有实际步骤
                        candidate_plans.append({
                            'steps': current_path,
                            'final_state': current_state,
                            'total_cost': current_cost,
                            'goal': goal_condition
                        })
                    continue
                
                # 如果路径太长，跳过
                if len(current_path) >= max_plan_length:
                    continue
                
                # 寻找适用的规律（下一块"桥板"）
                applicable_rules = self._find_applicable_rules(current_state, available_rules)
                
                for rule in applicable_rules:
                     # 预测执行规律后的新状态
                     new_state = self._predict_state_after_rule(current_state, rule)
                     # 在新状态中添加当前路径信息用于目标检查
                     new_state['_current_path'] = current_path
                     
                     new_step = {
                         'action': rule['action'],
                         'rule_id': rule['id'],
                         'confidence': rule['confidence'],
                         'description': f"执行规律 {rule['id']}: {rule['action']}"
                     }
                     new_path = current_path + [new_step]
                     new_cost = current_cost + (1.0 / rule['confidence'])  # 置信度越低成本越高
                     
                     # 添加到开放列表
                     open_list.append({
                         'state': new_state,
                         'path': new_path,
                         'cost': new_cost
                     })
            
            if logger and candidate_plans:
                logger.log(f"{self.name} 🔍 BPU搜索完成: 找到 {len(candidate_plans)} 个候选计划")
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} BPU搜索异常: {str(e)}")
        
        return candidate_plans
    
    def _state_to_key(self, state):
        """将状态转换为可哈希的键"""
        try:
            position = state.get('position', (0, 0))
            health = state.get('health', 100)
            food = state.get('food', 100)
            water = state.get('water', 100)
            return f"{position[0]}_{position[1]}_{health//10}_{food//10}_{water//10}"
        except:
            return str(hash(str(state)))
    
    def _check_goal_achieved(self, state, goal_condition):
        """检查目标是否达成"""
        try:
            goal_type = goal_condition.get('type', 'general')
            
            if goal_type == 'water':
                # 如果水量已经很高，考虑是否需要进一步行动
                current_water = state.get('water', 0)
                if current_water >= 95:  # 已经非常充足
                    return True
                elif current_water > 90:  # 充足但可以更好
                    return len(state.get('_current_path', [])) >= 2  # 至少2步后再检查
                else:
                    return False
            elif goal_type == 'food':
                current_food = state.get('food', 0)
                if current_food >= 95:
                    return True
                elif current_food > 90:
                    return len(state.get('_current_path', [])) >= 2
                else:
                    return False
            elif goal_type == 'safety':
                return state.get('nearby_threats', 1) == 0
            elif goal_type == 'exploration':
                return state.get('new_area_discovered', False) or state.get('exploration_progress', 0) >= 1.0
            else:
                return (state.get('health', 0) > 80 and 
                       state.get('food', 0) > 50 and 
                       state.get('water', 0) > 50)
        except:
            return False
    
    def _find_applicable_rules(self, current_state, available_rules):
        """找到在当前状态下适用的规律"""
        applicable = []
        
        for rule in available_rules:
            if self._rule_condition_matches(current_state, rule['condition']):
                applicable.append(rule)
        
        return applicable
    
    def _rule_condition_matches(self, state, condition):
        """检查规律的条件是否与当前状态匹配"""
        try:
            # 简化的条件匹配逻辑
            if condition.get('position') == 'any':
                return True
            
            if 'current_cell' in condition:
                required_cell = condition['current_cell']
                actual_cell = state.get('current_cell', 'unknown')
                # 对于open_field，匹配多种地形
                if required_cell == 'open_field':
                    return actual_cell in ['plain', 'grass', 'open_field']
                return actual_cell == required_cell
            
            if 'nearby_plant' in condition:
                # 简化：假设大部分位置都可能有植物
                return True
            
            # 检查资源条件
            if 'water_low' in condition:
                return state.get('water', 100) < 50
            
            if 'food_low' in condition:
                return state.get('food', 100) < 50
            
            # 检查位置条件
            if 'position' in condition and condition['position'] != 'any':
                pos = condition['position']
                if isinstance(pos, tuple):
                    return state.get('position', (0, 0)) == pos
            
            return True  # 默认匹配
            
        except:
            return False
    
    def _predict_state_after_rule(self, current_state, rule):
        """预测执行规律后的状态"""
        new_state = current_state.copy()
        
        try:
            result = rule.get('result', {})
            
            # 处理位置变化
            if 'position_change' in result:
                pos_change = result['position_change']
                if isinstance(pos_change, tuple):
                    old_pos = new_state.get('position', (0, 0))
                    new_state['position'] = (old_pos[0] + pos_change[0], old_pos[1] + pos_change[1])
            
            # 处理资源变化
            if 'water_gain' in result:
                new_state['water'] = min(100, new_state.get('water', 0) + result['water_gain'])
            
            if 'food_gain' in result:
                new_state['food'] = min(100, new_state.get('food', 0) + result['food_gain'])
            
            # 处理其他状态变化
            if 'new_area_discovered' in result:
                new_state['new_area_discovered'] = result['new_area_discovered']
                
        except Exception as e:
            if logger:
                logger.log(f"{self.name} 状态预测异常: {str(e)}")
        
        return new_state
    
    def _evaluate_plans_with_bpu(self, candidate_plans, goal):
        """使用BPU公式评估候选计划"""
        if not candidate_plans:
            return None
        
        best_plan = None
        best_score = -1
        
        alpha = 0.1  # 成本敏感度系数
        
        for plan in candidate_plans:
            try:
                # 计算置信度乘积 ∏Conf(R_i)
                confidence_product = 1.0
                for step in plan['steps']:
                    confidence_product *= step.get('confidence', 0.5)
                
                # 计算总成本 Cost(P)
                total_cost = len(plan['steps'])  # 步骤数作为基础成本
                
                # BPU公式: BPU(P) = ∏Conf(R_i) / (1 + α·Cost(P))
                bpu_score = confidence_product / (1 + alpha * total_cost)
                
                plan['bpu_score'] = bpu_score
                plan['confidence_product'] = confidence_product
                plan['total_cost'] = total_cost
                
                if bpu_score > best_score:
                    best_score = bpu_score
                    best_plan = plan
                    
                if logger:
                    logger.log(f"{self.name} 📊 计划评估: {len(plan['steps'])}步, 置信度积: {confidence_product:.3f}, 成本: {total_cost}, BPU分: {bpu_score:.3f}")
                    
            except Exception as e:
                if logger:
                    logger.log(f"{self.name} 计划评估异常: {str(e)}")
        
        if best_plan:
            # 转换为标准格式
            return {
                'goal': goal,
                'steps': best_plan['steps'],
                'created_time': time.time(),
                'estimated_duration': len(best_plan['steps']),
                'plan_type': 'bpu_optimized',
                'bpu_score': best_plan['bpu_score'],
                'confidence_product': best_plan['confidence_product'],
                'total_cost': best_plan['total_cost']
            }
        
        return None
    
    def _generate_fallback_plan(self, goal, game):
        """生成回退计划（简化版本）"""
        goal_str = str(goal).lower()
        
        if 'water' in goal_str:
            return self._generate_simple_water_plan()
        elif 'food' in goal_str:
            return self._generate_simple_food_plan()
        else:
            return self._generate_simple_exploration_plan()
    
    def _generate_simple_water_plan(self):
        """生成简单的寻水计划"""
        return {
            'goal': 'water',
            'steps': [
                {'action': 'move_up', 'description': '向北寻找水源', 'confidence': 0.7},
                {'action': 'move_right', 'description': '向东继续搜索', 'confidence': 0.7}
            ],
            'created_time': time.time(),
            'estimated_duration': 2,
            'plan_type': 'fallback_water'
        }
    
    def _generate_simple_food_plan(self):
        """生成简单的寻食计划"""
        return {
            'goal': 'food',
            'steps': [
                {'action': 'move_left', 'description': '向西寻找食物', 'confidence': 0.7},
                {'action': 'collect_plant', 'description': '收集植物', 'confidence': 0.8}
            ],
            'created_time': time.time(),
            'estimated_duration': 2,
            'plan_type': 'fallback_food'
        }
    
    def _generate_simple_exploration_plan(self):
        """生成简单的探索计划"""
        return {
            'goal': 'exploration',
            'steps': [
                {'action': 'move_up', 'description': '向北探索', 'confidence': 0.8},
                {'action': 'move_right', 'description': '向东探索', 'confidence': 0.8}
            ],
            'created_time': time.time(),
            'estimated_duration': 2,
            'plan_type': 'fallback_exploration'
        }
    
    # === WBM长链决策功能 ===
    
    def _should_use_long_chain_planning(self, target_goal, game):
        """判断是否需要使用长链决策规划"""
        # 复杂目标需要长链规划
        complex_goals = ['exploration', 'resource_acquisition', 'threat_avoidance', 'social_interaction']
        if target_goal in complex_goals:
            return True
        
        # 资源紧张时需要长期规划
        if self.health < 50 or self.food < 40 or self.water < 40:
            return True
        
        # 有多个威胁时需要战略规划
        threats = self.detect_threats(game.game_map)
        if len(threats) >= 2:
            return True
        
        return False
    
    def _generate_wbm_long_chain_plan(self, wbm_goal, available_rules, game, logger):
        """生成WBM长链决策计划"""
        try:
            if not hasattr(self, 'wooden_bridge_model') or not self.wooden_bridge_model:
                return None
            
            current_state = self._get_current_wbm_state(game)
            max_days = self._determine_plan_length(wbm_goal, current_state)
            
            if logger:
                logger.log(f"{self.name} 🎯 开始生成WBM长链决策计划: 目标={wbm_goal.description}, 预计天数={max_days}")
            
            # 使用WBM的长链决策功能
            multi_day_plan = self.wooden_bridge_model.generate_multi_day_plan(
                goal=wbm_goal,
                available_rules=available_rules,
                current_state=current_state,
                max_days=max_days
            )
            
            return multi_day_plan
            
        except Exception as e:
            if logger:
                logger.log(f"{self.name} WBM长链计划生成失败: {str(e)}")
            return None
    
    def _determine_plan_length(self, goal, current_state):
        """根据目标和状态确定计划长度"""
        # 根据目标类型确定基础天数
        base_days = {
            'exploration': 4,
            'resource_acquisition': 3,
            'threat_avoidance': 2,
            'social_interaction': 3,
            'survival': 5
        }.get(goal.goal_type.value if hasattr(goal, 'goal_type') else 'survival', 3)
        
        # 根据紧急度调整
        if hasattr(goal, 'urgency'):
            if goal.urgency > 0.8:
                base_days = max(1, base_days - 1)  # 紧急情况缩短计划
            elif goal.urgency < 0.3:
                base_days = min(7, base_days + 2)  # 非紧急情况可以延长计划
        
        # 根据资源状况调整
        health = current_state.get('health', 100)
        if health < 30:
            base_days = min(2, base_days)  # 健康危急时缩短计划
        
        return base_days
    
    def _log_wbm_long_chain_decision(self, multi_day_plan, logger):
        """记录WBM长链决策到正式日志"""
        if not logger or not multi_day_plan:
            return
        
        import time
        logger.log("=" * 80)
        logger.log(f"🗓️ {self.name} ILAI长链决策计划生成 | 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.log("=" * 80)
        logger.log(f"📋 计划ID: {multi_day_plan.plan_id}")
        logger.log(f"🎯 目标: {multi_day_plan.goal.description}")
        logger.log(f"📊 目标类型: {multi_day_plan.goal.goal_type.value}")
        logger.log(f"⚡ 紧急度: {multi_day_plan.goal.urgency:.2f} | 优先级: {multi_day_plan.goal.priority:.2f}")
        logger.log(f"📅 计划天数: {multi_day_plan.total_days}天")
        logger.log(f"🌉 桥梁策略: {multi_day_plan.bridge_plan.reasoning_strategy.value}")
        logger.log(f"🎲 预期成功率: {multi_day_plan.bridge_plan.expected_success_rate:.2f}")
        logger.log("")
        
        logger.log("📅 详细每日行动计划:")
        for daily_action in multi_day_plan.daily_actions:
            logger.log(f"  第{daily_action.day}天:")
            logger.log(f"    🎮 动作: {daily_action.action}")
            logger.log(f"    🧠 推理: {daily_action.reasoning}")
            logger.log(f"    📊 预期变化: {daily_action.expected_state_change}")
            logger.log(f"    🎯 置信度: {daily_action.confidence:.2f}")
            if daily_action.risk_assessment:
                logger.log(f"    ⚠️ 风险: {', '.join(daily_action.risk_assessment)}")
            if daily_action.fallback_actions:
                logger.log(f"    🔄 备选: {', '.join(daily_action.fallback_actions)}")
            logger.log("")
        
        if multi_day_plan.bridge_plan.rules_used:
            logger.log("🧱 使用的规律:")
            for rule in multi_day_plan.bridge_plan.rules_used:
                logger.log(f"  - {rule.rule_id}: {rule.confidence:.2f}置信度")
        
        logger.log("=" * 80)
        logger.log(f"💡 {self.name} ILAI智能体现: 长链决策规划 - 能够预见未来几天的行动需求")
        logger.log("🔗 规律链推理: 将多个简单规律连接成复杂的多步策略")
        logger.log("⚖️ 风险评估: 每步行动都考虑了可能的风险和备选方案")
        logger.log("=" * 80)
    
    def _continue_multi_day_plan(self, game, logger):
        """继续执行多日计划 - 增强版记忆功能"""
        if not hasattr(self, 'current_multi_day_plan') or not self.current_multi_day_plan:
            return None
        
        plan = self.current_multi_day_plan
        previous_day = getattr(self, 'plan_current_day', 0)
        current_day = previous_day + 1
        
        if logger:
            logger.log(f"{self.name} 🗓️ 检查多日计划执行状态: 第{current_day}天 (总计{plan.total_days}天)")
        
        # 1. 检查上一天的执行结果
        if previous_day > 0 and len(self.daily_execution_log) >= previous_day:
            last_execution = self.daily_execution_log[previous_day - 1]
            if logger:
                success_status = "成功" if last_execution.get('success', False) else "失败"
                logger.log(f"{self.name}    第{previous_day}天执行{success_status}: {last_execution.get('action', 'unknown')}")
        
        # 2. 获取当前环境状态并与制定计划时比较
        current_state = self._get_current_wbm_state(game)
        environment_changed = self._detect_environment_change(current_state)
        
        if environment_changed and logger:
            logger.log(f"{self.name} ⚠️ 检测到环境变化: {environment_changed['changes']}")
        
        # 3. 检查计划是否需要调整
        adjustment_result = self.wooden_bridge_model.check_and_adjust_multi_day_plan(
            plan, current_state
        )
        
        if adjustment_result.needs_adjustment:
            if logger:
                logger.log(f"{self.name} 🔄 多日计划需要调整: {adjustment_result.adjustment_reason}")
            
            # 记录调整历史
            self.plan_adjustment_history.append({
                'day': current_day,
                'reason': adjustment_result.adjustment_reason,
                'old_plan_id': plan.plan_id if hasattr(plan, 'plan_id') else 'unknown',
                'timestamp': time.time()
            })
            self.plan_completion_stats['total_adjusted'] += 1
            
            if adjustment_result.new_plan:
                self.current_multi_day_plan = adjustment_result.new_plan
                plan = adjustment_result.new_plan
                current_day = 1  # 重新开始新计划
                if logger:
                    logger.log(f"{self.name} 🔄 已切换到新计划: {plan.goal.description}")
        
        # 4. 执行今天的行动
        today_action = plan.get_action_for_day(current_day)
        if today_action:
            if logger:
                logger.log(f"{self.name} 🗓️ WBM长链决策第{current_day}天执行: {today_action.action}")
                logger.log(f"{self.name}    推理: {today_action.reasoning}")
                logger.log(f"{self.name}    置信度: {today_action.confidence:.2f}")
                if hasattr(today_action, 'expected_changes'):
                    logger.log(f"{self.name}    预期变化: {today_action.expected_changes}")
                
            self.plan_current_day = current_day
            
            # 5. 记录今日计划执行开始
            execution_record = {
                'day': current_day,
                'action': today_action.action,
                'reasoning': today_action.reasoning,
                'confidence': today_action.confidence,
                'start_time': time.time(),
                'planned': True,
                'success': None,  # 将在执行后更新
                'environment_state': current_state.copy()
            }
            
            # 确保日志列表足够长
            while len(self.daily_execution_log) < current_day:
                self.daily_execution_log.append({})
            
            if len(self.daily_execution_log) == current_day:
                self.daily_execution_log.append(execution_record)
            else:
                self.daily_execution_log[current_day - 1] = execution_record
            
            # 6. 检查是否是最后一天
            if current_day >= plan.total_days:
                if logger:
                    logger.log(f"{self.name} 🎉 多日计划即将完成: {plan.goal.description}")
                # 注意：这里不立即清除计划，等执行完成后再清除
            
            return {
                'action': today_action.action,
                'source': 'wbm_long_chain_continue',
                'confidence': today_action.confidence,
                'day': current_day,
                'plan_goal': plan.goal.description if hasattr(plan.goal, 'description') else str(plan.goal)
            }
        
        # 7. 计划执行完毕或出错
        if logger:
            logger.log(f"{self.name} ❌ 多日计划执行异常结束")
        
        self._complete_multi_day_plan(success=False, reason="execution_error", logger=logger)
        return None

    def _detect_environment_change(self, current_state):
        """检测环境变化"""
        if not hasattr(self, 'plan_initial_state') or not self.plan_initial_state:
            return None
            
        initial_state = self.plan_initial_state
        changes = []
        
        # 检查威胁变化
        if current_state.get('threats', []) != initial_state.get('threats', []):
            changes.append("威胁情况变化")
        
        # 检查健康状态变化
        current_health = current_state.get('health', 100)
        initial_health = initial_state.get('health', 100)
        if abs(current_health - initial_health) > 20:
            changes.append(f"健康状态显著变化 ({initial_health}->{current_health})")
        
        # 检查资源状态变化
        current_food = current_state.get('food', 0)
        initial_food = initial_state.get('food', 0)
        if abs(current_food - initial_food) > 5:
            changes.append(f"食物状态变化 ({initial_food}->{current_food})")
            
        current_water = current_state.get('water', 0)
        initial_water = initial_state.get('water', 0)
        if abs(current_water - initial_water) > 5:
            changes.append(f"水分状态变化 ({initial_water}->{current_water})")
        
        # 检查位置变化（如果计划包含位置要求）
        current_pos = (current_state.get('x', 0), current_state.get('y', 0))
        initial_pos = (initial_state.get('x', 0), initial_state.get('y', 0))
        if current_pos != initial_pos:
            distance = abs(current_pos[0] - initial_pos[0]) + abs(current_pos[1] - initial_pos[1])
            if distance > 3:
                changes.append(f"位置大幅变化 {initial_pos}->{current_pos}")
        
        if changes:
            return {
                'changed': True,
                'changes': changes,
                'severity': 'high' if len(changes) > 2 else 'medium'
            }
        
        return None
    
    def _complete_multi_day_plan(self, success=True, reason="completed", logger=None):
        """完成多日计划并更新统计"""
        if hasattr(self, 'current_multi_day_plan') and self.current_multi_day_plan:
            plan = self.current_multi_day_plan
            
            if success:
                self.plan_completion_stats['total_completed'] += 1
                if logger:
                    logger.log(f"{self.name} ✅ 多日计划成功完成: {plan.goal.description if hasattr(plan.goal, 'description') else str(plan.goal)}")
            else:
                self.plan_completion_stats['total_interrupted'] += 1
                self.plan_failure_reasons.append({
                    'plan_goal': plan.goal.description if hasattr(plan.goal, 'description') else str(plan.goal),
                    'reason': reason,
                    'day_reached': getattr(self, 'plan_current_day', 0),
                    'total_days': plan.total_days,
                    'timestamp': time.time()
                })
                
                if logger:
                    logger.log(f"{self.name} ❌ 多日计划中断: {reason}")
        
        # 清除当前计划状态
        self.current_multi_day_plan = None
        self.plan_current_day = 0
        self.plan_initial_state = None
    
    def _update_daily_execution_result(self, execution_result, logger=None):
        """更新当前天的执行结果"""
        if (hasattr(self, 'plan_current_day') and self.plan_current_day > 0 and 
            len(self.daily_execution_log) >= self.plan_current_day):
            
            current_record = self.daily_execution_log[self.plan_current_day - 1]
            current_record.update({
                'success': execution_result.get('success', False),
                'end_time': time.time(),
                'execution_time': time.time() - current_record.get('start_time', time.time()),
                'actual_result': execution_result.get('result', 'unknown'),
                'rewards_gained': execution_result.get('rewards', {}),
                'obstacles_encountered': execution_result.get('obstacles', [])
            })
            
            if logger:
                success_text = "成功" if current_record['success'] else "失败"
                logger.log(f"{self.name} 📋 第{self.plan_current_day}天执行结果: {success_text}")
                
            # 如果是最后一天且成功完成，标记整个计划为完成
            if (self.plan_current_day >= self.current_multi_day_plan.total_days and 
                current_record['success']):
                self._complete_multi_day_plan(success=True, reason="all_days_completed", logger=logger)
    
    def get_long_chain_memory_status(self):
        """获取长链决策记忆状态"""
        return {
            'has_active_plan': self.current_multi_day_plan is not None,
            'current_day': getattr(self, 'plan_current_day', 0),
            'total_days': self.current_multi_day_plan.total_days if self.current_multi_day_plan else 0,
            'plan_goal': (self.current_multi_day_plan.goal.description 
                         if self.current_multi_day_plan and hasattr(self.current_multi_day_plan.goal, 'description') 
                         else None),
            'execution_log_days': len(self.daily_execution_log),
            'adjustments_made': len(self.plan_adjustment_history),
            'completion_stats': self.plan_completion_stats.copy()
        }


class GlobalKnowledgeSync:
    """全局知识同步从- 负责协调所有玩家的知识同步"""
    
    def __init__(self, players=None):
        self.players = players or []
        self.unified_db_dir = "global_five_libraries"  # 使用目录而非文件
        self.sync_interval = 100  # 调整为每100轮同步一次 (性能优化)
        self.last_sync_turn = 0
        self.sync_stats = {
            'total_syncs': 0,
            'experiences_synced': 0,
            'rules_synced': 0,
            'failed_syncs': 0
        }
        
        # 添加去重机制
        self.synced_experience_hashes = set()
        self.synced_rule_hashes = set()
        
        # 初始化统一知识数据库
        try:
            from five_library_system import FiveLibrarySystem
            import os
            
            # 清理旧的冲突文件(如果存在)
            old_file_path = "five_library_system.db"
            if os.path.exists(old_file_path) and os.path.isfile(old_file_path):
                # 备份旧文件
                backup_name = f"{old_file_path}.backup_{int(time.time())}"
                os.rename(old_file_path, backup_name)
                if logger:
                    logger.log(f"🔄 已备份旧数据库文件为: {backup_name}")
            
            # 使用正确的目录路径初始化五库系统
            self.unified_system = FiveLibrarySystem(self.unified_db_dir)
            if logger:
                logger.log(f"🌐 全局知识同步器已启动,使用目录 {self.unified_db_dir}")
                
        except Exception as e:
            if logger:
                logger.log(f"全局知识同步器初始化失败: {e}")
                import traceback
                logger.log(f"详细错误信息: {traceback.format_exc()}")
            self.unified_system = None
    
    def register_player(self, player):
        """注册玩家到全局知识同步网络"""
        if player not in self.players:
            self.players.append(player)
            # 给玩家设置全局同步器引用
            player.global_knowledge_sync = self
            if logger:
                logger.log(f"🌐 {player.name} 已注册到全局知识同步网络")
    
    def sync_new_experience(self, discoverer, experience):
        """同步新发现的经验并给予声誉奖励"""
        try:
            # 生成经验哈希用于去重
            exp_hash = self._generate_experience_hash(experience)
            
            # 检查是否已同步
            if exp_hash in self.synced_experience_hashes:
                return False, "经验已存在"
            
            # 添加到已同步集合
            self.synced_experience_hashes.add(exp_hash)
            
            # 分发给其他ILAI/RILAI玩家
            shared_count = 0
            for player in self.players:
                if (player.name != discoverer.name and 
                    player.player_type in ['ILAI', 'RILAI'] and 
                    player.is_alive()):
                    try:
                        # 添加到玩家的间接经验库
                        if hasattr(player, 'five_library_system') and player.five_library_system:
                            # 使用五库系统添加经验
                            try:
                                # 转换经验格式为EOCATRExperience
                                from five_library_system import EOCATRExperience
                                import time
                                
                                # 🔧 强化数据格式检查和转换
                                if isinstance(experience, dict):
                                    eocar_exp = EOCATRExperience(
                                        environment=experience.get('environment', 'unknown'),
                                        object=experience.get('object', 'unknown'),
                                        characteristics=experience.get('characteristics', 'unknown'),
                                        action=experience.get('action', 'unknown'),
                                        tools=experience.get('tools', 'none'),
                                        result=experience.get('result', 'unknown'),
                                        player_id=player.name,
                                        timestamp=experience.get('timestamp', time.time()),
                                        metadata={'sender': discoverer.name, 'credibility': 0.8, 'source': 'indirect'}
                                    )
                                elif isinstance(experience, str):
                                    # 处理字符串格式的经验
                                    eocar_exp = EOCATRExperience(
                                        environment='unknown',
                                        object='unknown',
                                        characteristics='unknown',
                                        action=experience,
                                        tools='none',
                                        result='unknown',
                                        player_id=player.name,
                                        timestamp=time.time(),
                                        metadata={'sender': discoverer.name, 'credibility': 0.5, 'source': 'indirect', 'original_format': 'string'}
                                    )
                                elif hasattr(experience, 'to_dict'):
                                    # 如果有to_dict方法,先转换为字典
                                    exp_dict = experience.to_dict()
                                    eocar_exp = EOCATRExperience(
                                        environment=exp_dict.get('environment', 'unknown'),
                                        object=exp_dict.get('object', 'unknown'),
                                        characteristics=exp_dict.get('characteristics', 'unknown'),
                                        action=exp_dict.get('action', 'unknown'),
                                        tools=exp_dict.get('tools', 'none'),
                                        result=exp_dict.get('result', 'unknown'),
                                        player_id=player.name,
                                        timestamp=exp_dict.get('timestamp', time.time()),
                                        metadata={'sender': discoverer.name, 'credibility': 0.8, 'source': 'indirect'}
                                    )
                                else:
                                    # 如果已经是EOCATRExperience对象或其他格式,使用getattr
                                    eocar_exp = EOCATRExperience(
                                        environment=getattr(experience, 'environment', 'unknown'),
                                        object=getattr(experience, 'object', 'unknown'),
                                        characteristics=getattr(experience, 'characteristics', 'unknown'),
                                        action=getattr(experience, 'action', str(experience)),
                                        tools=getattr(experience, 'tools', 'none'),
                                        result=getattr(experience, 'result', 'unknown'),
                                        player_id=player.name,
                                        timestamp=getattr(experience, 'timestamp', time.time()),
                                        metadata={'sender': discoverer.name, 'credibility': 0.8, 'source': 'indirect'}
                                    )
                                
                                result = player.five_library_system.add_experience_to_direct_library(eocar_exp)
                                if result.get('success'):
                                    shared_count += 1
                            except Exception as format_error:
                                if logger:
                                    logger.log(f"⚠️ 向{player.name}分发经验格式转换失败: {str(format_error)}")
                    except Exception as e:
                        if logger:
                            logger.log(f"⚠️ 向{player.name}分发经验失败: {str(e)}")
            
            # 给发现者奖励（已移除声誉系统）
            # 新经验发现者将获得其他形式的奖励
            
            # 🔧 修复：记录发现者的信息分享统计
            if hasattr(discoverer, '_record_info_sharing'):
                discoverer._record_info_sharing(shared_count)
            elif hasattr(discoverer, 'shared_info_count'):
                discoverer.shared_info_count += 1
            
            # 更新统计
            self.sync_stats['experiences_synced'] += 1
            
            if shared_count > 0 and logger:
                logger.log(f"🌐 {discoverer.name} 分享经验给{shared_count}个用户")
            
            return True, f"经验已分享给{shared_count}个用户"
            
        except Exception as e:
            if logger:
                logger.log(f"从经验同步失败: {str(e)}")
            return False, f"同步失败: {str(e)}"
    
    def sync_new_rule(self, discoverer, rule, rule_type):
        """同步新发现的规律并给予声誉奖励"""
        try:
            # 生成规律哈希用于去重
            rule_hash = self._generate_rule_hash(rule, rule_type)
            
            # 检查是否已同步
            if rule_hash in self.synced_rule_hashes:
                return False, "规律已存在"
            
            # 添加到已同步集合
            self.synced_rule_hashes.add(rule_hash)
            
            # 分发给其他ILAI/RILAI玩家
            shared_count = 0
            for player in self.players:
                if (player.name != discoverer.name and 
                    player.player_type in ['ILAI', 'RILAI'] and 
                    player.is_alive()):
                    try:
                        # 添加到玩家的间接规律库
                        if hasattr(player, 'five_library_system') and player.five_library_system:
                            # 使用五库系统添加规律
                            try:
                                # 转换规律格式为列表
                                import time
                                if isinstance(rule, dict):
                                    rule_dict = rule.copy()
                                    rule_dict.update({
                                        'rule_type': rule_type,
                                        'source': 'indirect',
                                        'sender': discoverer.name,
                                        'credibility': 0.9,
                                        'player_id': player.name,
                                        'created_time': time.time()
                                    })
                                    rules_list = [rule_dict]
                                else:
                                    # 如果是其他格式,转换为字典
                                    rule_dict = {
                                        'conditions': {'condition': str(rule)},
                                        'predictions': {'expected_outcome': 'unknown'},
                                        'rule_type': rule_type,
                                        'confidence': 0.9,
                                        'support_count': 1,
                                        'contradiction_count': 0,
                                        'validation_count': 0,
                                        'creator_id': discoverer.name,
                                        'created_time': time.time()
                                    }
                                    rules_list = [rule_dict]
                                
                                result = player.five_library_system.add_rules_to_direct_library(rules_list)
                                if result.get('success'):
                                    shared_count += 1
                            except Exception as format_error:
                                if logger:
                                    logger.log(f"⚠️ 向{player.name}分发规律格式转换失败: {str(format_error)}")
                    except Exception as e:
                        if logger:
                            logger.log(f"⚠️ 向{player.name}分发规律失败: {str(e)}")
            
            # 给发现者奖励（已移除声誉系统）
            # 新规律发现者将获得其他形式的奖励
            
            # 🔧 修复：记录发现者的信息分享统计
            if hasattr(discoverer, '_record_info_sharing'):
                discoverer._record_info_sharing(shared_count)
            elif hasattr(discoverer, 'shared_info_count'):
                discoverer.shared_info_count += 1
            
            # 更新统计
            self.sync_stats['rules_synced'] += 1
            
            if shared_count > 0 and logger:
                logger.log(f"🏆 {discoverer.name} 分享规律[{rule_type}]给{shared_count}个用户")
            
            return True, f"规律已分享给{shared_count}个用户"
            
        except Exception as e:
            if logger:
                logger.log(f"从规律同步失败: {str(e)}")
            return False, f"同步失败: {str(e)}"
    
    def _generate_experience_hash(self, experience):
        """生成经验哈希用于去重,支持多种数据格式"""
        import hashlib
        
        # 🔧 强化数据格式处理
        try:
            if hasattr(experience, 'to_dict'):
                exp_dict = experience.to_dict()
            elif isinstance(experience, dict):
                exp_dict = experience
            elif isinstance(experience, str):
                # 处理字符串格式的经验数据
                exp_dict = {'raw': experience, 'action': experience, 'environment': 'unknown'}
            elif hasattr(experience, '__dict__'):
                # 处理对象格式
                exp_dict = experience.__dict__
            else:
                exp_dict = {'raw': str(experience)}
            
            # 安全的字段提取,避免str对象调用get()错误
            if isinstance(exp_dict, dict):
                key_fields = [
                    str(exp_dict.get('action', '')),
                    str(exp_dict.get('environment', '')),
                    str(exp_dict.get('object', '')),
                    str(exp_dict.get('tool', '')),
                    str(exp_dict.get('result', ''))
                ]
            else:
                # 如果仍然不是字典,使用简单的字符串表示
                key_fields = [str(exp_dict)]
            
            return hashlib.md5('|'.join(key_fields).encode()).hexdigest()
            
        except Exception as e:
            # 最后的防错措施
            if logger:
                logger.log(f"⚠️ 经验哈希生成失败,使用默认哈从 {str(e)}, 类型: {type(experience)}")
            return hashlib.md5(str(experience).encode()).hexdigest()
    
    def _generate_rule_hash(self, rule, rule_type):
        """生成规律哈希用于去重,支持多种数据格式"""
        import hashlib
        
        # 🔧 强化数据格式处理
        try:
            if hasattr(rule, 'to_dict'):
                rule_dict = rule.to_dict()
            elif isinstance(rule, dict):
                rule_dict = rule
            elif isinstance(rule, str):
                # 处理字符串格式的规律数据
                rule_dict = {'raw': rule, 'conditions': rule, 'predictions': 'unknown'}
            elif hasattr(rule, '__dict__'):
                # 处理对象格式
                rule_dict = rule.__dict__
            else:
                rule_dict = {'raw': str(rule)}
            
            # 安全的字段提取,避免str对象调用get()错误
            if isinstance(rule_dict, dict):
                key_fields = [
                    rule_type,
                    str(rule_dict.get('conditions', rule_dict.get('condition', ''))),
                    str(rule_dict.get('predictions', rule_dict.get('expected_outcome', '')))
                ]
            else:
                # 如果仍然不是字典,使用简单的字符串表示
                key_fields = [rule_type, str(rule_dict)]
            
            return hashlib.md5('|'.join(key_fields).encode()).hexdigest()
            
        except Exception as e:
            # 最后的防错措施
            if logger:
                logger.log(f"⚠️ 规律哈希生成失败,使用默认哈从 {str(e)}, 类型: {type(rule)}")
            return hashlib.md5(f"{rule_type}|{str(rule)}".encode()).hexdigest()
    
    def auto_sync_to_unified_db(self, current_turn):
        """自动同步到统一数据库"""
        if not self.unified_system or not self.players:
            return
        
        # 检查是否需要同"""
        if current_turn - self.last_sync_turn >= self.sync_interval:
            try:
                synced_count = 0
                for player in self.players:
                    if hasattr(player, 'five_library_system') and player.five_library_system:
                        # 同步个人经验到总库
                        sync_result = player.five_library_system.sync_all_direct_rules_to_total()
                        synced_count += sync_result.get('rules_synced', 0)
                
                self.sync_stats['total_syncs'] += 1
                self.last_sync_turn = current_turn
                
                if logger and synced_count > 0:
                    logger.log(f"🔄 全局知识同步完成: 同步{synced_count}条规律")
                    
            except Exception as e:
                self.sync_stats['failed_syncs'] += 1
                if logger:
                    logger.log(f"全局知识同步失败: {e}")
    

    def get_sync_statistics(self):
        """获取同步统计信息"""
        stats = self.sync_stats.copy()
        stats['registered_players'] = len(self.players)
        stats['unique_experiences'] = len(self.synced_experience_hashes)
        stats['unique_rules'] = len(self.synced_rule_hashes)
        return stats


class Game:
    def __init__(self, settings, canvas, ui_update_callback):
        self.settings = settings
        # 确保所有必需的设置都存在
        default_settings = {
            'group_hunt_frequency': 5,  # 默认5天一次群体狩猎
            'respawn_frequency': 20,    # 默认20天资源重生
            'enable_translation': True,  # 默认启用翻译系统
        }
        
        for key, value in default_settings.items():
            if key not in self.settings:
                self.settings[key] = value
        
        self.canvas = canvas
        self.ui_update_callback = ui_update_callback
        self.current_day = 0
        self.game_over = False
        self.game_map = GameMap(
            settings["map_width"], settings["map_height"], settings["map_type"], settings["seed"]
        )
        logger.log_seed(settings["seed"])
        logger.log_predator_count(self.game_map.get_predator_count())
        self.players = []
        
        # 初始化全局知识同步器(在初始化玩家之前)
        self.global_knowledge_sync = GlobalKnowledgeSync()
        
        # === 🌍 自动启动翻译系统 ===
        self.translation_monitor = None
        if self.settings.get('enable_translation', True):
            try:
                from auto_translation_integration import auto_start_translation_on_game_start
                self.translation_monitor = auto_start_translation_on_game_start()
                if self.translation_monitor:
                    logger.log("🌍 日志翻译系统已自动启动")
            except Exception as e:
                logger.log(f"⚠️ 翻译系统启动失败: {str(e)}")
        
        self.initialize_players()

    def initialize_players(self):
        # 内置 10 个DQN 玩家
        for i in range(10):
            name = f"DQN{i+1}"
            self.players.append(DQNPlayer(name, self.game_map))
        # 内置 10 个PPO 玩家
        for i in range(10):
            name = f"PPO{i+1}"
            self.players.append(PPOPlayer(name, self.game_map))
        # 内置 10 个ILAI 玩家
        for i in range(10):
            name = f"ILAI{i+1}"
            self.players.append(ILAIPlayer(name, self.game_map))
        # 内置 10 个RILAI 玩家(使用ILAIPlayer但启用强化学习)
        for i in range(10):
            name = f"RILAI{i+1}"
            player = ILAIPlayer(name, self.game_map)
            player.player_type = "RILAI"  # 修改玩家类型标识
            player.use_reinforcement_learning = True  # 启用强化学习
            self.players.append(player)
        
        # 注册ILAI和RILAI玩家到全局知识同步网络
        for player in self.players:
            if player.player_type in ['ILAI', 'RILAI']:
                self.global_knowledge_sync.register_player(player)
        
        # 启用性能追踪
        try:
            from game_performance_integration import enable_game_performance_tracking
            enable_game_performance_tracking(self.players)
        except ImportError:
            logger.log("⚠️ 性能追踪模块未找到，跳过性能统计集成")
        except Exception as e:
            logger.log(f"⚠️ 性能追踪启用失败: {str(e)}")

    def run_turn(self):
        if self.game_over:
            return
        logger.log(f"第{self.current_day + 1} 回合开始")
        
        # 动物行动(包括捕食者的追击)
        for animal in self.game_map.animals:
            if animal.alive:
                animal.move(self.game_map, self.players)
        
        # 玩家行动
        for player in self.players:
            if player.is_alive():
                player.take_turn(self)
                player.survival_days = self.current_day + 1
        
        # === 新增：保存AI模型以实现长期记忆 ===
        # 每5回合保存一次模型，减少IO开销，同时在游戏结束时确保保存
        if (self.current_day + 1) % 5 == 0 or self.current_day + 1 >= self.settings["game_duration"]:
            for player in self.players:
                if player.is_alive() and hasattr(player, 'save_model'):
                    try:
                        player.save_model()
                        logger.log(f"💾 {player.name} 模型已保存 (第{self.current_day + 1}天)")
                    except Exception as e:
                        logger.log(f"⚠️ 保存{player.name}的模型失败: {str(e)}")
        
        # 触发知识同步检查(每回合检查ILAI/RILAI玩家)
        for player in self.players:
            if player.player_type in ['ILAI', 'RILAI'] and player.is_alive():
                if hasattr(player, '_trigger_knowledge_sync'):
                    try:
                        sync_count = player._trigger_knowledge_sync()
                        if sync_count > 0:
                            self.global_knowledge_sync.sync_stats['total_syncs'] += sync_count
                    except Exception as e:
                        logger.log(f"⚠️ {player.name} 知识同步失败: {str(e)}")
        
        # 全局知识同步(定期同步)
        self.global_knowledge_sync.auto_sync_to_unified_db(self.current_day)
                
        # 群体狩猎事件(每隔设定天数触发一次)
        if (self.current_day + 1) % self.settings["group_hunt_frequency"] == 0:
            self.group_hunt()
            
        self.respawn_resources()
        self.current_day += 1
        self.ui_update_callback()
        
        if self.current_day >= self.settings["game_duration"] or all(
            not p.is_alive() for p in self.players
        ):
            self.end_game()
        else:
            if self.canvas:
                self.canvas.after(500, self.run_turn)  # 下一回合延时 500ms (性能优化)

    def group_hunt(self):
        # 模拟群体狩猎:若有玩家在猛兽(Tiger 和BlackBear)附近5 格,则共同攻击获取奖励
        for animal in self.game_map.animals:
            if animal.alive and animal.type in ["Tiger", "BlackBear"]:
                participants = []
                for player in self.players:
                    if player.is_alive() and abs(player.x - animal.x) <= 5 and abs(player.y - animal.y) <= 5:
                        participants.append(player)
                if participants:
                    total_damage = sum(p.damage_dealt for p in participants)
                    if total_damage == 0:
                        total_damage = 1
                    # 若累计伤害足够击杀猛兽,则分配食物奖励
                    if animal.hp <= sum(p.damage_dealt for p in participants):
                        animal.alive = False
                        reward = animal.food
                        for p in participants:
                            contribution = p.damage_dealt / total_damage
                            gained_food = min(100 - p.food, round(reward * contribution))  # 确保不超过100上限
                            p.food += gained_food
                            logger.log(
                                f"{p.name} participated in group hunt and gained {gained_food} food"
                            )

    def respawn_resources(self):
        # 每回合检查资源(植物)是否可重生(10天内随机刷新机制,简单模拟)
        for plant in self.game_map.plants:
            if plant.collected and random.random() < 0.01:
                plant.collected = False
                logger.log("A plant has respawned.")

    def end_game(self):
        self.game_over = True
        logger.log("游戏结束")
        
        # === 游戏结束时最终保存所有AI模型 ===
        logger.log("🎯 正在执行最终模型保存...")
        for player in self.players:
            if hasattr(player, 'save_model'):
                try:
                    player.save_model()
                    logger.log(f"✅ {player.name} 最终模型已保存")
                except Exception as e:
                    logger.log(f"❌ 保存{player.name}最终模型失败: {str(e)}")
        
        rankings = self.calculate_rankings()
        
        # 更新表头，在最后添加算力消耗和反应时间
        header = (
            "|排名|玩家|生存天数|血量|食物|水|探索率|发现植物|采集植物|遭遇动物|击杀动物|发现大树|探索山洞|新颖发现|算力消耗|反应时间|"
        )
        logger.log(header)
        
        for rank, player in enumerate(rankings, 1):
            # 获取性能统计数据
            computation_cost = "N/A"
            response_time = "N/A"
            
            # 检查玩家是否有性能追踪器
            if hasattr(player, 'performance_tracker') and player.performance_tracker:
                try:
                    stats = player.performance_tracker.get_performance_summary()
                    # 计算算力消耗（累计CPU使用时间，单位：秒）
                    computation_cost = f"{stats.get('total_execution_time', 0):.2f}s"
                    # 计算平均反应时间（单位：毫秒）
                    avg_response = stats.get('average_execution_time', 0)
                    response_time = f"{avg_response*1000:.0f}ms"
                except Exception as e:
                    # 如果获取性能数据失败，保持默认值
                    if hasattr(player, 'logger') and player.logger:
                        player.logger.log(f"获取{player.name}性能数据失败: {str(e)}")
            
            line = (
                f"|{rank}|{player.name}|{player.survival_days}|"
                f"{player.hp}|{player.food}|{player.water}|{player.exploration_rate}|"
                f"{player.found_plants}|{player.collected_plants}|{player.encountered_animals}|"
                f"{player.killed_animals}|{player.found_big_tree}|{player.explored_cave}|"
                f"{player.novelty_discoveries}|{computation_cost}|{response_time}|"
            )
            logger.log(line)
        
        # 生成性能报告
        try:
            from game_performance_integration import generate_game_performance_report
            generate_game_performance_report()
        except ImportError:
            pass
        except Exception as e:
            logger.log(f"⚠️ 性能报告生成失败: {str(e)}")
        
        # === 🔥 关键修复：先写入日志文件 ===
        logger.write_log_file()
        
        # === 🌍 日志写入后，给翻译系统时间处理新日志 ===
        if self.translation_monitor:
            try:
                print("🌍 日志文件已生成，等待翻译系统处理...")
                
                # 等待3秒钟让翻译系统处理新生成的日志
                import time
                time.sleep(3)
                
                # 强制检查并翻译最新的日志文件
                try:
                    from game_integrated_translation_system import force_translate_all_logs
                    force_translate_all_logs()
                    print("🌍 已强制翻译所有日志文件")
                except Exception as force_e:
                    print(f"⚠️ 强制翻译失败: {str(force_e)}")
                
                # 现在才停止翻译系统
                from auto_translation_integration import auto_stop_translation_on_game_end
                auto_stop_translation_on_game_end()
                print("🌍 日志翻译系统已自动停止")
                
            except Exception as e:
                print(f"⚠️ 翻译系统停止失败: {str(e)}")

    def calculate_rankings(self):
        # 排名依据:优先比较生存天数、血量、食物、水,若相同以姓名字典排序
        alive_players = [p for p in self.players if p.survival_days > 0]
        return sorted(
            alive_players,
            key=lambda p: (
                -p.survival_days,
                -p.hp,
                -p.food,
                -p.water,
                p.name,
            ),
        )


#
# UI 部分 - 使用 tkinter 创建一个左侧控制面板和右侧的地图可视化区域
#
    def _execute_high_priority_exploration(self, game):
        """🎯 新增：执行高优先级探索目标（生物多样性和工具效能测试）"""
        try:
            # 检查是否有待执行的高优先级CDL目标
            if hasattr(self, '_pending_cdl_goal') and self._pending_cdl_goal:
                cdl_goal = self._pending_cdl_goal
                goal_type = cdl_goal.get('type', '')
                
                # 执行生物多样性探索
                if goal_type == 'biodiversity_exploration':
                    return self._execute_biodiversity_exploration(cdl_goal, game)
                
                # 执行工具效能测试
                elif goal_type == 'tool_efficiency_testing':
                    return self._execute_tool_efficiency_testing(cdl_goal, game)
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 高优先级探索执行失败: {str(e)}")
            return False

    def _execute_biodiversity_exploration(self, cdl_goal, game):
        """🦋 执行生物多样性探索"""
        try:
            eocatr_goal = cdl_goal.get('eocatr_goal', {})
            action = eocatr_goal.get('action', '')
            target_object = eocatr_goal.get('object', '')
            target_pos = cdl_goal.get('target_position', None)
            species_key = cdl_goal.get('species_key', None)
            
            if not target_pos:
                return False
            
            # 移动到目标位置
            if (self.x, self.y) != target_pos:
                # 计算移动方向
                dx = 1 if target_pos[0] > self.x else -1 if target_pos[0] < self.x else 0
                dy = 1 if target_pos[1] > self.y else -1 if target_pos[1] < self.y else 0
                
                # 尝试移动
                new_x, new_y = self.x + dx, self.y + dy
                if self._is_valid_position(new_x, new_y, game):
                    self.x, self.y = new_x, new_y
                    if self.logger:
                        self.logger.log(f"{self.name} 🦋 生物多样性探索:移动到目标位置({new_x},{new_y})")
                    return True
            
            # 到达目标位置，执行具体探索行为
            success = False
            if action == 'hunt_with_tool':
                success = self._execute_biodiversity_hunting(target_object, eocatr_goal.get('tool'), game)
            elif action == 'gather_with_tool':
                success = self._execute_biodiversity_gathering(target_object, eocatr_goal.get('tool'), game)
            elif action == 'observe_safely':
                success = self._execute_biodiversity_observation(target_object, game)
            elif action == 'examine_resource':
                success = self._execute_biodiversity_examination(target_object, game)
            
            # 记录探索的物种
            if success and species_key:
                if not hasattr(self, 'explored_species'):
                    self.explored_species = set()
                self.explored_species.add(species_key)
                if self.logger:
                    self.logger.log(f"{self.name} 🦋 已记录探索物种: {species_key}")
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 生物多样性探索执行失败: {str(e)}")
            return False

    def _execute_tool_efficiency_testing(self, cdl_goal, game):
        """🔧 执行工具效能测试"""
        try:
            eocatr_goal = cdl_goal.get('eocatr_goal', {})
            action = eocatr_goal.get('action', '')
            target_object = eocatr_goal.get('object', '')
            tool_name = eocatr_goal.get('tool', '')
            target_pos = cdl_goal.get('target_position', None)
            combo_key = cdl_goal.get('combo_key', None)
            
            if not target_pos or not tool_name:
                return False
            
            # 移动到目标位置
            if (self.x, self.y) != target_pos:
                # 计算移动方向
                dx = 1 if target_pos[0] > self.x else -1 if target_pos[0] < self.x else 0
                dy = 1 if target_pos[1] > self.y else -1 if target_pos[1] < self.y else 0
                
                # 尝试移动
                new_x, new_y = self.x + dx, self.y + dy
                if self._is_valid_position(new_x, new_y, game):
                    self.x, self.y = new_x, new_y
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 工具效能测试:移动到目标位置({new_x},{new_y})")
                    return True
            
            # 到达目标位置，执行工具测试
            success = False
            if action == 'test_hunting_tool':
                success = self._test_hunting_tool_efficiency(target_object, tool_name, game)
            elif action == 'test_ranged_tool':
                success = self._test_ranged_tool_efficiency(target_object, tool_name, game)
            elif action == 'test_gathering_tool':
                success = self._test_gathering_tool_efficiency(target_object, tool_name, game)
            elif action == 'test_utility_tool':
                success = self._test_utility_tool_efficiency(target_object, tool_name, game)
            
            # 记录测试的工具组合
            if success and combo_key:
                if not hasattr(self, 'tested_tool_combinations'):
                    self.tested_tool_combinations = set()
                self.tested_tool_combinations.add(combo_key)
                if self.logger:
                    self.logger.log(f"{self.name} 🔧 已记录工具测试: {combo_key}")
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 工具效能测试执行失败: {str(e)}")
            return False

    # 🦋 生物多样性探索的具体执行函数
    def _execute_biodiversity_hunting(self, target_object, tool_name, game):
        """执行生物多样性狩猎"""
        try:
            # 寻找目标动物
            for animal in game.game_map.animals:
                if (animal.type.lower() == target_object and 
                    animal.alive and 
                    abs(animal.x - self.x) + abs(animal.y - self.y) <= 1):
                    
                    old_food = self.food
                    damage = self.attack(animal)
                    
                    success = damage > 0 or not animal.alive
                    if self.logger:
                        status = "成功" if success else "失败"
                        self.logger.log(f"{self.name} 🦋 生物多样性狩猎: 使用{tool_name}攻击{target_object} {status}")
                    
                    return success
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 生物多样性狩猎失败: {str(e)}")
            return False

    def _execute_biodiversity_gathering(self, target_object, tool_name, game):
        """执行生物多样性采集"""
        try:
            # 寻找目标植物
            for plant in game.game_map.plants:
                if (plant.__class__.__name__.lower() == target_object and 
                    not plant.collected and 
                    abs(plant.x - self.x) + abs(plant.y - self.y) <= 1):
                    
                    old_food = self.food
                    self.collect_plant(plant)
                    
                    success = self.food > old_food
                    if self.logger:
                        status = "成功" if success else "失败"
                        self.logger.log(f"{self.name} 🦋 生物多样性采集: 使用{tool_name}采集{target_object} {status}")
                    
                    return success
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 生物多样性采集失败: {str(e)}")
            return False

    def _execute_biodiversity_observation(self, target_object, game):
        """执行生物多样性观察（安全观察猛兽）"""
        try:
            # 寻找目标动物进行观察
            for animal in game.game_map.animals:
                if (animal.type.lower() == target_object and 
                    animal.alive and 
                    abs(animal.x - self.x) + abs(animal.y - self.y) <= 2):
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 🦋 生物多样性观察: 安全观察{target_object}的行为特征")
                    
                    # 观察成功，获得知识但不进行攻击
                    return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 生物多样性观察失败: {str(e)}")
            return False

    def _execute_biodiversity_examination(self, target_object, game):
        """执行生物多样性检查（检查树木等资源）"""
        try:
            # 寻找目标资源进行检查
            for plant in game.game_map.plants:
                if (plant.__class__.__name__.lower() == target_object and 
                    abs(plant.x - self.x) + abs(plant.y - self.y) <= 1):
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 🦋 生物多样性检查: 检查{target_object}的资源特性")
                    
                    # 检查成功，获得关于资源的信息
                    return True
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 生物多样性检查失败: {str(e)}")
            return False

    # 🔧 工具效能测试的具体执行函数
    def _test_hunting_tool_efficiency(self, target_object, tool_name, game):
        """测试狩猎工具效能"""
        try:
            # 寻找目标动物进行工具测试
            for animal in game.game_map.animals:
                if (animal.type.lower() == target_object and 
                    animal.alive and 
                    abs(animal.x - self.x) + abs(animal.y - self.y) <= 1):
                    
                    old_health = animal.health if hasattr(animal, 'health') else 100
                    damage = self.attack(animal)
                    
                    # 记录工具效能
                    efficiency = damage / 100.0  # 简化的效能计算
                    success = damage > 0
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 狩猎工具测试: {tool_name}对{target_object}造成{damage}伤害，效能{efficiency:.2f}")
                    
                    return success
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 狩猎工具测试失败: {str(e)}")
            return False

    def _test_ranged_tool_efficiency(self, target_object, tool_name, game):
        """测试远程工具效能"""
        try:
            # 寻找目标动物进行远程工具测试
            for animal in game.game_map.animals:
                if (animal.type.lower() == target_object and 
                    animal.alive and 
                    abs(animal.x - self.x) + abs(animal.y - self.y) <= 2):  # 远程工具可以更远距离
                    
                    damage = self.attack(animal)
                    efficiency = damage / 80.0  # 远程工具的效能基准不同
                    success = damage > 0
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 远程工具测试: {tool_name}对{target_object}造成{damage}伤害，效能{efficiency:.2f}")
                    
                    return success
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 远程工具测试失败: {str(e)}")
            return False

    def _test_gathering_tool_efficiency(self, target_object, tool_name, game):
        """测试采集工具效能"""
        try:
            # 寻找目标植物进行采集工具测试
            for plant in game.game_map.plants:
                if (plant.__class__.__name__.lower() == target_object and 
                    not plant.collected and 
                    abs(plant.x - self.x) + abs(plant.y - self.y) <= 1):
                    
                    old_food = self.food
                    self.collect_plant(plant)
                    food_gain = self.food - old_food
                    
                    efficiency = food_gain / 20.0  # 采集工具的效能基准
                    success = food_gain > 0
                    
                    if self.logger:
                        self.logger.log(f"{self.name} 🔧 采集工具测试: {tool_name}采集{target_object}获得{food_gain}食物，效能{efficiency:.2f}")
                    
                    return success
            
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 采集工具测试失败: {str(e)}")
            return False

    def _test_utility_tool_efficiency(self, target_object, tool_name, game):
        """测试通用工具效能"""
        try:
            # 对目标进行通用工具测试
            if self.logger:
                self.logger.log(f"{self.name} 🔧 通用工具测试: 使用{tool_name}对{target_object}进行多功能测试")
            
            # 简化的通用工具测试，总是返回成功
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"{self.name} 通用工具测试失败: {str(e)}")
            return False

    def _is_valid_position(self, x, y, game):
        """检查位置是否有效"""
        try:
            return (0 <= x < len(game.game_map.grid[0]) and 
                    0 <= y < len(game.game_map.grid))
        except:
            return False


class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Survival Game Control Panel")
        self.create_control_panel()
        self.create_canvas()
        self.game = None

    def create_control_panel(self):
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        # Start button
        self.start_button = tk.Button(
            self.control_frame, text="Start Game", command=self.start_game
        )
        self.start_button.pack(pady=5)

        # Map controls
        tk.Label(self.control_frame, text="Map Controls").pack()
        self.map_width_var = tk.IntVar(value=settings["map_width"])
        self.map_height_var = tk.IntVar(value=settings["map_height"])
        map_size_frame = tk.Frame(self.control_frame)
        map_size_frame.pack(pady=2)
        tk.Label(map_size_frame, text="Width").grid(row=0, column=0)
        tk.Button(
            map_size_frame,
            text="-",
            command=lambda: self.adjust("map_width", -5),
        ).grid(row=0, column=1)
        tk.Label(map_size_frame, textvariable=self.map_width_var).grid(row=0, column=2)
        tk.Button(
            map_size_frame,
            text="+",
            command=lambda: self.adjust("map_width", 5),
        ).grid(row=0, column=3)
        tk.Label(map_size_frame, text="Height").grid(row=1, column=0)
        tk.Button(
            map_size_frame,
            text="-",
            command=lambda: self.adjust("map_height", -5),
        ).grid(row=1, column=1)
        tk.Label(map_size_frame, textvariable=self.map_height_var).grid(row=1, column=2)
        tk.Button(
            map_size_frame,
            text="+",
            command=lambda: self.adjust("map_height", 5),
        ).grid(row=1, column=3)

        # Map type selection
        tk.Label(self.control_frame, text="Map Type").pack()
        self.map_type_var = tk.StringVar(value=settings["map_type"])
        map_types = ["Grassland", "Desert", "Forest", "Mountain"]
        self.map_type_menu = tk.OptionMenu(
            self.control_frame, self.map_type_var, *map_types
        )
        self.map_type_menu.pack(pady=2)

        # Map seed input
        tk.Label(self.control_frame, text="Map Seed").pack()
        self.seed_var = tk.IntVar(value=settings["seed"])
        self.seed_entry = tk.Entry(self.control_frame, textvariable=self.seed_var)
        self.seed_entry.pack(pady=2)

        # Resource controls
        tk.Label(self.control_frame, text="Resource Controls").pack()
        self.resource_abundance_var = tk.IntVar(value=settings["resource_abundance"])
        resource_frame = tk.Frame(self.control_frame)
        resource_frame.pack(pady=2)
        tk.Label(resource_frame, text="Abundance(%):").grid(row=0, column=0)
        tk.Button(
            resource_frame,
            text="-",
            command=lambda: self.adjust("resource_abundance", -5),
        ).grid(row=0, column=1)
        tk.Label(resource_frame, textvariable=self.resource_abundance_var).grid(
            row=0, column=2
        )
        tk.Button(
            resource_frame,
            text="+",
            command=lambda: self.adjust("resource_abundance", 5),
        ).grid(row=0, column=3)
        self.resource_regen_var = tk.IntVar(value=settings["resource_regen"])
        tk.Label(resource_frame, text="Regen Cycle(days):").grid(row=1, column=0)
        tk.Button(
            resource_frame,
            text="-",
            command=lambda: self.adjust("resource_regen", -1),
        ).grid(row=1, column=1)
        tk.Label(resource_frame, textvariable=self.resource_regen_var).grid(
            row=1, column=2
        )
        tk.Button(
            resource_frame,
            text="+",
            command=lambda: self.adjust("resource_regen", 1),
        ).grid(row=1, column=3)

        # Duration controls
        tk.Label(self.control_frame, text="Duration Control(days)").pack()
        self.game_duration_var = tk.IntVar(value=settings["game_duration"])
        duration_frame = tk.Frame(self.control_frame)
        duration_frame.pack(pady=2)
        tk.Button(
            duration_frame,
            text="-",
            command=lambda: self.adjust("game_duration", -5),
        ).grid(row=0, column=0)
        tk.Label(duration_frame, textvariable=self.game_duration_var).grid(row=0, column=1)
        tk.Button(
            duration_frame,
            text="+",
            command=lambda: self.adjust("game_duration", 5),
        ).grid(row=0, column=2)

        # Group hunt frequency
        tk.Label(self.control_frame, text="Group Hunt Frequency(%)").pack()
        self.group_hunt_var = tk.IntVar(value=settings["group_hunt_frequency"])
        hunt_frame = tk.Frame(self.control_frame)
        hunt_frame.pack(pady=2)
        tk.Button(
            hunt_frame,
            text="-",
            command=lambda: self.adjust("group_hunt_frequency", -1),
        ).grid(row=0, column=0)
        tk.Label(hunt_frame, textvariable=self.group_hunt_var).grid(row=0, column=1)
        tk.Button(
            hunt_frame,
            text="+",
            command=lambda: self.adjust("group_hunt_frequency", 1),
        ).grid(row=0, column=2)

        # Reasoning attention
        tk.Label(self.control_frame, text="Reasoning Attention(%)").pack()
        self.reasoning_attention_var = tk.IntVar(value=settings["reasoning_attention"])
        reasoning_frame = tk.Frame(self.control_frame)
        reasoning_frame.pack(pady=2)
        tk.Button(
            reasoning_frame,
            text="-",
            command=lambda: self.adjust("reasoning_attention", -5),
        ).grid(row=0, column=0)
        tk.Label(reasoning_frame, textvariable=self.reasoning_attention_var).grid(
            row=0, column=1
        )
        tk.Button(
            reasoning_frame,
            text="+",
            command=lambda: self.adjust("reasoning_attention", 5),
        ).grid(row=0, column=2)

        # Honesty settings (0 means never send messages)
        tk.Label(self.control_frame, text="Honesty(0=never send msg)").pack()
        self.honesty_true_var = tk.IntVar(value=settings["honesty_true"])
        self.honesty_false_var = tk.IntVar(value=settings["honesty_false"])
        self.honesty_none_var = tk.IntVar(value=settings["honesty_none"])
        honesty_frame = tk.Frame(self.control_frame)
        honesty_frame.pack(pady=2)
        tk.Label(honesty_frame, text="True").grid(row=0, column=0)
        tk.Button(
            honesty_frame,
            text="-",
            command=lambda: self.adjust("honesty_true", -5),
        ).grid(row=0, column=1)
        tk.Label(honesty_frame, textvariable=self.honesty_true_var).grid(
            row=0, column=2
        )
        tk.Button(
            honesty_frame,
            text="+",
            command=lambda: self.adjust("honesty_true", 5),
        ).grid(row=0, column=3)
        tk.Label(honesty_frame, text="False").grid(row=1, column=0)
        tk.Button(
            honesty_frame,
            text="-",
            command=lambda: self.adjust("honesty_false", -5),
        ).grid(row=1, column=1)
        tk.Label(honesty_frame, textvariable=self.honesty_false_var).grid(
            row=1, column=2
        )
        tk.Button(
            honesty_frame,
            text="+",
            command=lambda: self.adjust("honesty_false", 5),
        ).grid(row=1, column=3)
        tk.Label(honesty_frame, text="None:").grid(row=2, column=0)
        tk.Button(
            honesty_frame,
            text="-",
            command=lambda: self.adjust("honesty_none", -5),
        ).grid(row=2, column=1)
        tk.Label(honesty_frame, textvariable=self.honesty_none_var).grid(
            row=2, column=2
        )
        tk.Button(
            honesty_frame,
            text="+",
            command=lambda: self.adjust("honesty_none", 5),
        ).grid(row=2, column=3)

        # Infant Learning mechanism control buttons
        tk.Label(self.control_frame, text="Infant Learning Mechanism Control").pack(pady=5)
        self.ilai_vars = {}
        mechanism_list = [
            ("Hierarchical Cognitive Framework", "enable_hierarchical_cognition"),
            ("Developmental Cognitive Framework", "enable_developmental_cognition"),
            ("Dynamic Multi-Head Attention", "enable_dynamic_multihead_attention"),
            ("Social Decision Mechanism", "enable_social_decision"),
            ("Diverse Reward Mechanism", "enable_diverse_rewards"),
            ("Long Short-Term Memory", "enable_lstm"),
            ("Curiosity-Driven Mechanism", "enable_curiosity"),
            ("Deep Logical Alignment", "enable_deep_logical_alignment"),
            ("Reinforcement Learning", "enable_reinforcement_learning"),
        ]
        for text, key in mechanism_list:
            var = tk.BooleanVar(value=settings[key])
            chk = tk.Checkbutton(self.control_frame, text=text, variable=var)
            chk.pack(anchor="w")
            self.ilai_vars[key] = var

        # === 🌍 翻译系统控制 ===
        tk.Label(self.control_frame, text="Translation System Control").pack(pady=5)
        self.translation_var = tk.BooleanVar(value=settings.get("enable_translation", True))
        translation_chk = tk.Checkbutton(
            self.control_frame, 
            text="🌍 Auto English Translation", 
            variable=self.translation_var,
            font=("Arial", 10, "bold")
        )
        translation_chk.pack(anchor="w")
        
        # 添加翻译系统说明
        translation_info = tk.Label(
            self.control_frame, 
            text="Automatically translate Chinese logs to English",
            font=("Arial", 8),
            fg="gray"
        )
        translation_info.pack(anchor="w", padx=20)

        # Animal/Plant abundance buttons
        tk.Label(self.control_frame, text="Animal/Plant Abundance Control").pack(pady=5)
        abundance_frame = tk.Frame(self.control_frame)
        abundance_frame.pack(pady=2)
        tk.Label(abundance_frame, text="Predator:").grid(row=0, column=0)
        self.animal_predator_var = tk.IntVar(
            value=settings["animal_abundance_predator"]
        )
        tk.Button(
            abundance_frame,
            text="-",
            command=lambda: self.adjust("animal_abundance_predator", -5),
        ).grid(row=0, column=1)
        tk.Label(abundance_frame, textvariable=self.animal_predator_var).grid(
            row=0, column=2
        )
        tk.Button(
            abundance_frame,
            text="+",
            command=lambda: self.adjust("animal_abundance_predator", 5),
        ).grid(row=0, column=3)
        tk.Label(abundance_frame, text="Prey:").grid(row=1, column=0)
        self.animal_prey_var = tk.IntVar(value=settings["animal_abundance_prey"])
        tk.Button(
            abundance_frame,
            text="-",
            command=lambda: self.adjust("animal_abundance_prey", -5),
        ).grid(row=1, column=1)
        tk.Label(abundance_frame, textvariable=self.animal_prey_var).grid(
            row=1, column=2
        )
        tk.Button(
            abundance_frame,
            text="+",
            command=lambda: self.adjust("animal_abundance_prey", 5),
        ).grid(row=1, column=3)
        tk.Label(abundance_frame, text="Edible Plant:").grid(row=2, column=0)
        self.plant_edible_var = tk.IntVar(value=settings["plant_abundance_edible"])
        tk.Button(
            abundance_frame,
            text="-",
            command=lambda: self.adjust("plant_abundance_edible", -5),
        ).grid(row=2, column=1)
        tk.Label(abundance_frame, textvariable=self.plant_edible_var).grid(
            row=2, column=2
        )
        tk.Button(
            abundance_frame,
            text="+",
            command=lambda: self.adjust("plant_abundance_edible", 5),
        ).grid(row=2, column=3)
        tk.Label(abundance_frame, text="Toxic Plant:").grid(row=3, column=0)
        self.plant_toxic_var = tk.IntVar(value=settings["plant_abundance_toxic"])
        tk.Button(
            abundance_frame,
            text="-",
            command=lambda: self.adjust("plant_abundance_toxic", -5),
        ).grid(row=3, column=1)
        tk.Label(abundance_frame, textvariable=self.plant_toxic_var).grid(
            row=3, column=2
        )
        tk.Button(
            abundance_frame,
            text="+",
            command=lambda: self.adjust("plant_abundance_toxic", 5),
        ).grid(row=3, column=3)

    def adjust(self, key, delta):
        if key in ["map_width", "map_height"]:
            settings[key] = max(10, settings[key] + delta)
            if key == "map_width":
                self.map_width_var.set(settings[key])
            else:
                self.map_height_var.set(settings[key])
        elif key == "resource_abundance":
            settings[key] = max(1, settings[key] + delta)
            self.resource_abundance_var.set(settings[key])
        elif key == "resource_regen":
            settings[key] = max(1, settings[key] + delta)
            self.resource_regen_var.set(settings[key])
        elif key == "game_duration":
            settings[key] = max(1, settings[key] + delta)
            self.game_duration_var.set(settings[key])
        elif key == "group_hunt_frequency":
            settings[key] = max(1, settings[key] + delta)
            self.group_hunt_var.set(settings[key])
        elif key == "reasoning_attention":
            settings[key] = max(0, settings[key] + delta)
            self.reasoning_attention_var.set(settings[key])
        elif key in ["honesty_true", "honesty_false", "honesty_none"]:
            settings[key] = max(0, settings[key] + delta)
            if key == "honesty_true":
                self.honesty_true_var.set(settings[key])
            elif key == "honesty_false":
                self.honesty_false_var.set(settings[key])
            else:
                self.honesty_none_var.set(settings[key])
        elif key in [
            "animal_abundance_predator",
            "animal_abundance_prey",
            "plant_abundance_edible",
            "plant_abundance_toxic",
        ]:
            settings[key] = max(1, settings[key] + delta)
            if key == "animal_abundance_predator":
                self.animal_predator_var.set(settings[key])
            elif key == "animal_abundance_prey":
                self.animal_prey_var.set(settings[key])
            elif key == "plant_abundance_edible":
                self.plant_edible_var.set(settings[key])
            else:
                self.plant_toxic_var.set(settings[key])

    def create_canvas(self):
        # Create a frame to contain day label and canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create day label
        self.day_label = tk.Label(self.canvas_frame, text="Game Days: 0", font=("Arial", 14, "bold"))
        self.day_label.pack(pady=5)
        
        # Create larger canvas
        self.canvas = tk.Canvas(self.canvas_frame, width=1000, height=1000, bg="white")
        self.canvas.pack()

    def update_canvas(self):
        # 将地图网格、动物、植物和玩家显示到画布上
        self.canvas.delete("all")
        
        if not self.game:
            return
            
        # Update day label
        self.day_label.config(text=f"Game Days: {self.game.current_day}")

        # Calculate scale
        scale = min(1000 / self.game.game_map.width, 1000 / self.game.game_map.height)
        # Draw terrain background
        for i in range(self.game.game_map.height):
            for j in range(self.game.game_map.width):
                cell = self.game.game_map.grid[i][j]
                color = "white"
                if cell == "plain":
                    color = "#e0e0e0"
                elif cell == "big_tree":
                    color = "green"
                elif cell == "bush":
                    color = "darkgreen"
                elif cell == "rock":
                    color = "gray"
                elif cell == "cave":
                    color = "brown"
                elif cell == "river":
                    color = "blue"
                elif cell == "puddle":
                    color = "lightblue"
                self.canvas.create_rectangle(
                    j * scale, i * scale, (j + 1) * scale, (i + 1) * scale, fill=color, outline=""
                )
        # Draw animals: predators in red, prey in orange
        for animal in self.game.game_map.animals:
            if animal.alive:
                x = animal.x * scale
                y = animal.y * scale
                if animal.type in ["Tiger", "BlackBear"]:
                    fill_color = "red"
                else:
                    fill_color = "orange"
                self.canvas.create_oval(x, y, x + scale, y + scale, fill=fill_color)
        # Draw plants
        for plant in self.game.game_map.plants:
            if not plant.collected:
                x = plant.x * scale
                y = plant.y * scale
                fill_color = "pink" if not getattr(plant, "toxic", False) else "purple"
                self.canvas.create_rectangle(x, y, x + scale, y + scale, fill=fill_color)
        # Draw players: DQN in blue, PPO in cyan, ILAI in magenta
        for player in self.game.players:
            if player.is_alive():
                x = player.x * scale
                y = player.y * scale
                if player.player_type == "DQN":
                    fill_color = "blue"
                elif player.player_type == "PPO":
                    fill_color = "cyan"
                elif player.player_type == "ILAI":
                    fill_color = "magenta"
                elif player.player_type == "RL":
                    fill_color = "yellow"
                # Draw player icon
                self.canvas.create_oval(x, y, x + scale, y + scale, fill=fill_color)
                # Display name above player icon
                self.canvas.create_text(x + scale/2, y - 5, text=player.name, 
                                     anchor="s", font=("Arial", max(int(scale/3), 8)), fill="black")

    def start_game(self):
        # Read parameters from UI and update global settings
        settings["map_width"] = self.map_width_var.get()
        settings["map_height"] = self.map_height_var.get()
        settings["map_type"] = self.map_type_var.get()
        settings["seed"] = self.seed_var.get()
        settings["resource_abundance"] = self.resource_abundance_var.get()
        settings["resource_regen"] = self.resource_regen_var.get()
        settings["game_duration"] = self.game_duration_var.get()
        settings["group_hunt_frequency"] = self.group_hunt_var.get()
        settings["reasoning_attention"] = self.reasoning_attention_var.get()
        settings["honesty_true"] = self.honesty_true_var.get()
        settings["honesty_false"] = self.honesty_false_var.get()
        settings["honesty_none"] = self.honesty_none_var.get()
        # === 🌍 读取翻译系统设置 ===
        settings["enable_translation"] = self.translation_var.get()
        for key, var in self.ilai_vars.items():
            settings[key] = var.get()
        # Create game instance
        self.game = Game(settings, self.canvas, self.update_canvas)
        self.start_button.config(state=tk.DISABLED)
        self.game.run_turn()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()
