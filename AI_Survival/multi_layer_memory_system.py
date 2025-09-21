#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多层次记忆系统 (Multi-Layer Memory System, MLMS)

基于认知科学理论和Stanford 4.0架构设计的多层次记忆管理系统。
实现了人类认知中的记忆层次结构和动态处理机制。

核心功能：
1. 感觉记忆 (Sensory Memory) - 短暂保存感官输入
2. 短期记忆/工作记忆 (Short-term/Working Memory) - 当前活跃信息处理
3. 长期记忆 (Long-term Memory) - 持久存储，包含：
   - 程序性记忆 (Procedural Memory) - 技能和习惯
   - 陈述性记忆 (Declarative Memory) - 事实和事件
   - 情景记忆 (Episodic Memory) - 个人经历
   - 语义记忆 (Semantic Memory) - 概念和知识

特性：
- 动态记忆衰减 (艾宾浩斯遗忘曲线)
- 记忆整合和巩固机制
- 相关记忆的关联网络
- 重要性评估和选择性保持

作者：AI生存游戏项目组
版本：1.0.0 (版本1.2.0的核心组件)
"""

import math
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import random


class MemoryLayerType(Enum):
    """记忆层次类型枚举"""
    SENSORY = "sensory"          # 感觉记忆
    SHORT_TERM = "short_term"    # 短期记忆
    WORKING = "working"          # 工作记忆
    LONG_TERM = "long_term"      # 长期记忆


class MemoryType(Enum):
    """长期记忆类型枚举"""
    PROCEDURAL = "procedural"    # 程序性记忆
    DECLARATIVE = "declarative"  # 陈述性记忆
    EPISODIC = "episodic"        # 情景记忆
    SEMANTIC = "semantic"        # 语义记忆


class MemoryImportance(Enum):
    """记忆重要性级别"""
    CRITICAL = 5    # 极为重要
    HIGH = 4        # 高重要性
    MEDIUM = 3      # 中等重要性
    LOW = 2         # 低重要性
    TRIVIAL = 1     # 微不足道


@dataclass
class MemoryItem:
    """记忆项的基础数据结构"""
    content: Any                           # 记忆内容
    timestamp: float                       # 时间戳
    memory_type: MemoryType               # 记忆类型
    importance: MemoryImportance          # 重要性级别
    
    # 衰减相关
    initial_strength: float = 1.0         # 初始强度
    current_strength: float = 1.0         # 当前强度
    decay_rate: float = 0.1               # 衰减率
    
    # 使用统计
    access_count: int = 0                 # 访问次数
    last_access_time: float = 0           # 最后访问时间
    
    # 情感相关
    emotional_intensity: float = 0.0      # 情感强度
    emotional_valence: float = 0.0        # 情感价值 (-1负面, 0中性, 1正面)
    
    # 关联信息
    related_memories: Set[str] = field(default_factory=set)  # 相关记忆ID
    tags: List[str] = field(default_factory=list)           # 标签
    context: Dict[str, Any] = field(default_factory=dict)   # 上下文信息
    
    # 巩固状态
    consolidation_level: float = 0.0      # 巩固程度 (0-1)
    rehearsal_count: int = 0              # 复述次数
    
    def __post_init__(self):
        """初始化后处理"""
        if self.last_access_time == 0:
            self.last_access_time = self.timestamp
        # 使用更精确的时间戳和随机数避免ID冲突
        timestamp_ms = int(self.timestamp * 1000000)  # 微秒精度
        random_suffix = random.randint(1000, 9999)
        self.memory_id = f"{self.memory_type.value}_{timestamp_ms}_{random_suffix}"
    
    def calculate_current_strength(self, current_time: float) -> float:
        """根据艾宾浩斯遗忘曲线计算当前记忆强度"""
        time_diff = current_time - self.last_access_time
        
        # 基础衰减计算（艾宾浩斯遗忘曲线变体）
        # 调整衰减率，使其以小时为单位而不是秒
        time_diff_hours = time_diff / 3600.0  # 转换为小时
        forgetting_factor = math.exp(-self.decay_rate * time_diff_hours)
        
        # 重要性修正
        importance_boost = float(self.importance.value) / 5.0
        
        # 情感强度修正
        emotional_boost = min(abs(self.emotional_intensity) * 0.5, 1.0)
        
        # 巩固程度修正
        consolidation_boost = self.consolidation_level * 0.3
        
        # 复述次数修正
        rehearsal_boost = min(self.rehearsal_count * 0.1, 0.5)
        
        # 综合强度计算 - 修正公式，确保重要性等因素正确影响衰减
        base_strength = self.initial_strength * forgetting_factor
        
        # 重要性等因素作为保护因子，减缓衰减
        protection_factor = 1 + (importance_boost + emotional_boost + consolidation_boost + rehearsal_boost) * 0.5
        
        # 应用保护因子
        self.current_strength = base_strength * protection_factor
        
        # 确保强度在合理范围内
        self.current_strength = max(0.0, min(1.0, self.current_strength))
        return self.current_strength
    
    def access(self, current_time: float):
        """访问记忆项，更新统计信息"""
        self.access_count += 1
        self.last_access_time = current_time
        self.rehearsal_count += 1
        
        # 每次访问增加少量巩固
        self.consolidation_level = min(1.0, self.consolidation_level + 0.05)
    
    def add_related_memory(self, memory_id: str):
        """添加相关记忆"""
        self.related_memories.add(memory_id)
    
    def get_memory_strength_category(self) -> str:
        """获取记忆强度分类"""
        if self.current_strength >= 0.8:
            return "very_strong"
        elif self.current_strength >= 0.6:
            return "strong"
        elif self.current_strength >= 0.4:
            return "medium"
        elif self.current_strength >= 0.2:
            return "weak"
        else:
            return "very_weak"


@dataclass
class SensoryMemoryBuffer:
    """感觉记忆缓冲区"""
    capacity: int = 10                    # 容量
    retention_time: float = 2.0           # 保持时间（秒）
    buffer: deque = field(default_factory=deque)
    
    def add(self, sensory_input: Any, current_time: float):
        """添加感觉输入"""
        # 清理过期的感觉记忆
        self.cleanup(current_time)
        
        # 添加新的感觉记忆
        sensory_memory = {
            'content': sensory_input,
            'timestamp': current_time,
            'expires_at': current_time + self.retention_time
        }
        
        self.buffer.append(sensory_memory)
        
        # 保持容量限制
        while len(self.buffer) > self.capacity:
            self.buffer.popleft()
    
    def cleanup(self, current_time: float):
        """清理过期的感觉记忆"""
        while self.buffer and current_time >= self.buffer[0]['expires_at']:
            self.buffer.popleft()
    
    def get_active_memories(self, current_time: float) -> List[Dict]:
        """获取当前活跃的感觉记忆"""
        self.cleanup(current_time)
        return list(self.buffer)


@dataclass
class WorkingMemorySlot:
    """工作记忆槽位"""
    content: Any = None
    activation_level: float = 0.0
    last_update: float = 0.0
    source_memory_id: Optional[str] = None
    
    def is_active(self) -> bool:
        """检查是否活跃"""
        return self.activation_level > 0.1
    
    def decay(self, decay_rate: float = 0.2):
        """衰减激活水平"""
        self.activation_level *= (1 - decay_rate)
        if self.activation_level < 0.1:
            self.activation_level = 0.0
            self.content = None
            self.source_memory_id = None


class MultiLayerMemorySystem:
    """多层次记忆系统主类"""
    
    def __init__(self, logger=None, config=None):
        self.logger = logger
        self.config = config or self._default_config()
        
        # 感觉记忆系统
        self.sensory_memory = SensoryMemoryBuffer(
            capacity=self.config['sensory_memory_capacity'],
            retention_time=self.config['sensory_retention_time']
        )
        
        # 短期记忆系统
        self.short_term_memory = deque(maxlen=self.config['short_term_capacity'])
        self.short_term_retention_time = self.config['short_term_retention_time']
        
        # 工作记忆系统
        self.working_memory_slots = [
            WorkingMemorySlot() for _ in range(self.config['working_memory_slots'])
        ]
        
        # 长期记忆系统（按类型分类）
        self.long_term_memory = {
            MemoryType.PROCEDURAL: {},      # 程序性记忆
            MemoryType.DECLARATIVE: {},     # 陈述性记忆
            MemoryType.EPISODIC: {},        # 情景记忆
            MemoryType.SEMANTIC: {}         # 语义记忆
        }
        
        # 记忆索引系统
        self.memory_index = {
            'by_tags': defaultdict(set),
            'by_importance': defaultdict(set),
            'by_time': {},
            'by_type': defaultdict(set)
        }
        
        # 记忆关联网络
        self.memory_associations = defaultdict(set)
        
        # 性能统计
        self.memory_stats = {
            'total_memories': 0,
            'memories_by_type': defaultdict(int),
            'memories_by_importance': defaultdict(int),
            'consolidation_events': 0,
            'forgotten_memories': 0,
            'retrieval_success_rate': 0.0,
            'average_memory_strength': 0.0
        }
        
        # 当前时间戳
        self.current_time = time.time()
        
        if self.logger:
            self.logger.log("多层次记忆系统已初始化")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置参数"""
        return {
            # 感觉记忆配置
            'sensory_memory_capacity': 10,
            'sensory_retention_time': 2.0,
            
            # 短期记忆配置
            'short_term_capacity': 7,  # 米勒法则：7±2
            'short_term_retention_time': 30.0,
            
            # 工作记忆配置
            'working_memory_slots': 4,  # Baddeley模型
            'working_memory_decay_rate': 0.2,
            
            # 长期记忆配置
            'long_term_capacity': 10000,
            'consolidation_threshold': 0.7,
            'forgetting_threshold': 0.1,
            
            # 整合机制配置
            'association_strength_threshold': 0.5,
            'consolidation_rate': 0.1,
            'rehearsal_benefit': 0.15,
            
            # 衰减机制配置
            'base_decay_rate': 0.1,
            'importance_decay_modifier': {
                MemoryImportance.CRITICAL: 0.02,
                MemoryImportance.HIGH: 0.05,
                MemoryImportance.MEDIUM: 0.1,
                MemoryImportance.LOW: 0.2,
                MemoryImportance.TRIVIAL: 0.3
            }
        }
    
    def update_time(self, new_time: float = None):
        """更新系统时间"""
        self.current_time = new_time if new_time else time.time()
        
        # 更新工作记忆衰减
        for slot in self.working_memory_slots:
            slot.decay(self.config['working_memory_decay_rate'])
    
    def add_sensory_input(self, sensory_data: Any) -> bool:
        """添加感觉输入"""
        try:
            self.sensory_memory.add(sensory_data, self.current_time)
            
            # 检查是否需要转移到短期记忆
            if self._should_transfer_to_short_term(sensory_data):
                self._transfer_to_short_term(sensory_data)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"感觉记忆添加失败: {e}")
            return False
    
    def _should_transfer_to_short_term(self, sensory_data: Any) -> bool:
        """判断是否应该转移到短期记忆"""
        # 这里可以实现注意力过滤机制
        # 简化版本：基于数据类型和内容判断
        if isinstance(sensory_data, dict):
            # 检查是否包含重要信息
            important_keys = ['danger', 'resource', 'social', 'goal']
            return any(key in str(sensory_data).lower() for key in important_keys)
        
        return False
    
    def _transfer_to_short_term(self, data: Any):
        """转移数据到短期记忆"""
        short_term_item = {
            'content': data,
            'timestamp': self.current_time,
            'expires_at': self.current_time + self.short_term_retention_time,
            'activation_level': 1.0
        }
        
        self.short_term_memory.append(short_term_item)
    
    def store_memory(self, content: Any, memory_type: str, 
                    importance: Union[int, MemoryImportance] = 3,
                    emotional_intensity: float = 0.0, emotional_valence: float = 0.0,
                    tags: List[str] = None, context: Dict[str, Any] = None) -> str:
        """存储记忆到长期记忆系统"""
        
        # 处理memory_type参数（支持字符串）
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        
        # 处理importance参数（支持整数）
        if isinstance(importance, int):
            # 将整数转换为MemoryImportance枚举
            importance_map = {1: MemoryImportance.TRIVIAL, 2: MemoryImportance.LOW, 
                            3: MemoryImportance.MEDIUM, 4: MemoryImportance.HIGH, 
                            5: MemoryImportance.CRITICAL}
            importance = importance_map.get(importance, MemoryImportance.MEDIUM)
        
        # 创建记忆项
        memory_item = MemoryItem(
            content=content,
            timestamp=self.current_time,
            memory_type=memory_type,
            importance=importance,
            emotional_intensity=emotional_intensity,
            emotional_valence=emotional_valence,
            tags=tags or [],
            context=context or {},
            decay_rate=self.config['importance_decay_modifier'][importance]
        )
        
        # 存储到对应的长期记忆类型中
        memory_id = memory_item.memory_id
        self.long_term_memory[memory_type][memory_id] = memory_item
        
        # 更新索引
        self._update_memory_index(memory_item)
        
        # 寻找相关记忆并建立关联
        self._build_memory_associations(memory_item)
        
        # 更新统计
        self._update_memory_stats(memory_type, importance)
        
        if self.logger:
            self.logger.log(f"存储{memory_type.value}记忆: {memory_id}")
        
        return memory_id
    
    def _update_memory_index(self, memory_item: MemoryItem):
        """更新记忆索引"""
        memory_id = memory_item.memory_id
        
        # 按标签索引
        for tag in memory_item.tags:
            self.memory_index['by_tags'][tag].add(memory_id)
        
        # 按重要性索引
        self.memory_index['by_importance'][memory_item.importance].add(memory_id)
        
        # 按时间索引
        time_key = int(memory_item.timestamp // 86400)  # 按天分组
        if time_key not in self.memory_index['by_time']:
            self.memory_index['by_time'][time_key] = set()
        self.memory_index['by_time'][time_key].add(memory_id)
        
        # 按类型索引
        self.memory_index['by_type'][memory_item.memory_type].add(memory_id)
    
    def _build_memory_associations(self, new_memory: MemoryItem):
        """建立记忆关联"""
        memory_id = new_memory.memory_id
        
        # 寻找相关记忆
        related_memories = self._find_related_memories(new_memory)
        
        for related_id, similarity_score in related_memories:
            if similarity_score >= self.config['association_strength_threshold']:
                # 建立双向关联
                self.memory_associations[memory_id].add(related_id)
                self.memory_associations[related_id].add(memory_id)
                
                # 在记忆项中也记录关联
                new_memory.add_related_memory(related_id)
                
                # 获取相关记忆并添加反向关联
                for memory_type in self.long_term_memory.values():
                    if related_id in memory_type:
                        memory_type[related_id].add_related_memory(memory_id)
                        break
    
    def _find_related_memories(self, target_memory: MemoryItem) -> List[Tuple[str, float]]:
        """寻找相关记忆"""
        related_memories = []
        
        # 搜索所有类型的长期记忆
        for memory_type, memories in self.long_term_memory.items():
            for memory_id, memory_item in memories.items():
                similarity = self._calculate_memory_similarity(target_memory, memory_item)
                if similarity > 0.3:  # 最低相似度阈值
                    related_memories.append((memory_id, similarity))
        
        # 按相似度排序
        related_memories.sort(key=lambda x: x[1], reverse=True)
        return related_memories[:10]  # 返回最相关的10个记忆
    
    def _calculate_memory_similarity(self, memory1: MemoryItem, memory2: MemoryItem) -> float:
        """计算记忆相似度"""
        similarity_score = 0.0
        
        # 标签相似度
        if memory1.tags and memory2.tags:
            common_tags = set(memory1.tags) & set(memory2.tags)
            all_tags = set(memory1.tags) | set(memory2.tags)
            tag_similarity = len(common_tags) / len(all_tags) if all_tags else 0
            similarity_score += tag_similarity * 0.4
        
        # 时间相似度（时间越近越相似）
        time_diff = abs(memory1.timestamp - memory2.timestamp)
        time_similarity = math.exp(-time_diff / 86400)  # 以天为单位的时间衰减
        similarity_score += time_similarity * 0.2
        
        # 情感相似度
        emotion_diff = abs(memory1.emotional_valence - memory2.emotional_valence)
        emotion_similarity = 1 - (emotion_diff / 2)  # 情感值范围是-1到1
        similarity_score += emotion_similarity * 0.2
        
        # 重要性相似度
        importance_diff = abs(memory1.importance.value - memory2.importance.value)
        importance_similarity = 1 - (importance_diff / 4)  # 重要性范围是1到5
        similarity_score += importance_similarity * 0.1
        
        # 内容相似度（简化版本）
        content_similarity = self._calculate_content_similarity(memory1.content, memory2.content)
        similarity_score += content_similarity * 0.1
        
        return min(1.0, similarity_score)
    
    def _calculate_content_similarity(self, content1: Any, content2: Any) -> float:
        """计算内容相似度（简化版本）"""
        try:
            str1 = str(content1).lower()
            str2 = str(content2).lower()
            
            # 简单的词汇重叠计算
            words1 = set(str1.split())
            words2 = set(str2.split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            common_words = words1 & words2
            all_words = words1 | words2
            
            return len(common_words) / len(all_words)
            
        except Exception:
            return 0.0
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """检索特定记忆"""
        # 在所有长期记忆类型中搜索
        for memory_type, memories in self.long_term_memory.items():
            if memory_id in memories:
                memory_item = memories[memory_id]
                memory_item.access(self.current_time)
                return memory_item
        
        return None
    
    def search_memories(self, query: str = None, tags: List[str] = None, 
                       memory_types: List[str] = None, importance: Union[int, MemoryImportance] = None,
                       time_range: Tuple[float, float] = None, max_results: int = 10) -> List[MemoryItem]:
        """搜索记忆"""
        candidate_ids = set()
        
        # 处理memory_types参数（支持字符串列表）
        if memory_types:
            memory_type_enums = []
            for mt in memory_types:
                if isinstance(mt, str):
                    memory_type_enums.append(MemoryType(mt))
                else:
                    memory_type_enums.append(mt)
        else:
            memory_type_enums = None
        
        # 处理importance参数（支持整数）
        if isinstance(importance, int):
            importance_map = {1: MemoryImportance.TRIVIAL, 2: MemoryImportance.LOW, 
                            3: MemoryImportance.MEDIUM, 4: MemoryImportance.HIGH, 
                            5: MemoryImportance.CRITICAL}
            importance = importance_map.get(importance, MemoryImportance.MEDIUM)
        
        # 根据不同条件收集候选记忆ID
        if tags:
            # 使用并集而不是交集，只要有任何一个标签匹配就包含
            for tag in tags:
                tag_memories = self.memory_index['by_tags'].get(tag, set())
                candidate_ids.update(tag_memories)
        
        if importance:
            importance_memories = self.memory_index['by_importance'].get(importance, set())
            if candidate_ids:
                candidate_ids &= importance_memories  # 如果已有候选，则取交集
            else:
                candidate_ids.update(importance_memories)
        
        if memory_type_enums:
            type_candidate_ids = set()
            for memory_type in memory_type_enums:
                type_memories = self.memory_index['by_type'].get(memory_type, set())
                type_candidate_ids.update(type_memories)
            
            if candidate_ids:
                candidate_ids &= type_candidate_ids  # 如果已有候选，则取交集
            else:
                candidate_ids.update(type_candidate_ids)
        
        # 如果没有特定条件，搜索所有记忆
        if not candidate_ids and not tags and not importance and not memory_type_enums:
            for memories in self.long_term_memory.values():
                candidate_ids.update(memories.keys())
        
        # 过滤和评分
        scored_memories = []
        for memory_id in candidate_ids:
            memory_item = self.retrieve_memory(memory_id)
            if memory_item:
                # 计算记忆强度
                strength = memory_item.calculate_current_strength(self.current_time)
                
                # 时间范围过滤
                if time_range:
                    start_time, end_time = time_range
                    if not (start_time <= memory_item.timestamp <= end_time):
                        continue
                
                # 查询匹配评分
                query_score = 1.0
                if query:
                    query_score = self._calculate_query_match_score(memory_item, query)
                    if query_score == 0.0:
                        continue  # 如果有查询但不匹配，跳过
                
                total_score = strength * query_score
                if total_score > 0.05:  # 降低最低检索阈值
                    scored_memories.append((memory_item, total_score))
        
        # 按评分排序并返回
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in scored_memories[:max_results]]
    
    def _calculate_query_match_score(self, memory_item: MemoryItem, query: str) -> float:
        """计算查询匹配评分"""
        query_lower = query.lower()
        content_str = str(memory_item.content).lower()
        
        # 精确匹配
        if query_lower in content_str:
            return 1.0
        
        # 词汇匹配
        query_words = set(query_lower.split())
        content_words = set(content_str.split())
        
        if query_words & content_words:
            match_ratio = len(query_words & content_words) / len(query_words)
            return match_ratio * 0.8
        
        # 标签匹配
        for tag in memory_item.tags:
            if query_lower in tag.lower():
                return 0.6
        
        return 0.0
    
    def consolidate_memories(self):
        """记忆巩固过程"""
        consolidation_candidates = []
        
        # 收集需要巩固的记忆
        for memory_type, memories in self.long_term_memory.items():
            for memory_id, memory_item in memories.items():
                current_strength = memory_item.calculate_current_strength(self.current_time)
                
                # 巩固条件：强度足够且访问频率较高
                if (current_strength >= self.config['consolidation_threshold'] and 
                    memory_item.access_count >= 3 and 
                    memory_item.consolidation_level < 1.0):
                    consolidation_candidates.append(memory_item)
        
        # 执行巩固过程
        consolidated_count = 0
        for memory_item in consolidation_candidates:
            # 增加巩固程度
            consolidation_boost = self.config['consolidation_rate']
            memory_item.consolidation_level = min(1.0, 
                memory_item.consolidation_level + consolidation_boost)
            
            # 降低衰减率
            memory_item.decay_rate *= 0.8
            
            # 增强相关记忆的关联
            self._strengthen_memory_associations(memory_item)
            
            consolidated_count += 1
        
        self.memory_stats['consolidation_events'] += consolidated_count
        
        if self.logger and consolidated_count > 0:
            self.logger.log(f"巩固了{consolidated_count}个记忆")
    
    def _strengthen_memory_associations(self, memory_item: MemoryItem):
        """加强记忆关联"""
        for related_id in memory_item.related_memories:
            related_memory = self.retrieve_memory(related_id)
            if related_memory:
                # 适度提升相关记忆的强度
                related_memory.current_strength = min(1.0, 
                    related_memory.current_strength + 0.05)
    
    def forget_weak_memories(self):
        """遗忘弱记忆"""
        forgotten_count = 0
        
        for memory_type, memories in self.long_term_memory.items():
            memories_to_remove = []
            
            for memory_id, memory_item in memories.items():
                current_strength = memory_item.calculate_current_strength(self.current_time)
                
                # 遗忘条件：强度太低且不是高重要性记忆
                if (current_strength < self.config['forgetting_threshold'] and
                    memory_item.importance not in [MemoryImportance.CRITICAL, MemoryImportance.HIGH]):
                    memories_to_remove.append(memory_id)
            
            # 删除弱记忆
            for memory_id in memories_to_remove:
                memory_item = memories[memory_id]
                del memories[memory_id]
                self._remove_from_indices(memory_id)
                
                # 更新统计信息
                self.memory_stats['total_memories'] -= 1
                self.memory_stats['memories_by_type'][memory_item.memory_type] -= 1
                self.memory_stats['memories_by_importance'][memory_item.importance] -= 1
                
                forgotten_count += 1
        
        self.memory_stats['forgotten_memories'] += forgotten_count
        
        if self.logger and forgotten_count > 0:
            self.logger.log(f"遗忘了{forgotten_count}个弱记忆")
    
    def _remove_from_indices(self, memory_id: str):
        """从索引中移除记忆"""
        # 从各个索引中移除
        for tag_memories in self.memory_index['by_tags'].values():
            tag_memories.discard(memory_id)
        
        for importance_memories in self.memory_index['by_importance'].values():
            importance_memories.discard(memory_id)
        
        for time_memories in self.memory_index['by_time'].values():
            time_memories.discard(memory_id)
        
        for type_memories in self.memory_index['by_type'].values():
            type_memories.discard(memory_id)
        
        # 从关联网络中移除
        if memory_id in self.memory_associations:
            del self.memory_associations[memory_id]
        
        # 从其他记忆的关联中移除
        for associations in self.memory_associations.values():
            associations.discard(memory_id)
    
    def _update_memory_stats(self, memory_type: MemoryType, importance: MemoryImportance):
        """更新记忆统计信息"""
        self.memory_stats['total_memories'] += 1
        self.memory_stats['memories_by_type'][memory_type] += 1
        self.memory_stats['memories_by_importance'][importance] += 1
    
    def activate_working_memory(self, content: Any, source_memory_id: str = None) -> bool:
        """激活工作记忆"""
        # 寻找空闲槽位或最弱的槽位
        target_slot = None
        min_activation = float('inf')
        
        for slot in self.working_memory_slots:
            if not slot.is_active():
                target_slot = slot
                break
            elif slot.activation_level < min_activation:
                min_activation = slot.activation_level
                target_slot = slot
        
        if target_slot:
            target_slot.content = content
            target_slot.activation_level = 1.0
            target_slot.last_update = self.current_time
            target_slot.source_memory_id = source_memory_id
            return True
        
        return False
    
    def get_working_memory_contents(self) -> List[Any]:
        """获取工作记忆内容"""
        return [slot.content for slot in self.working_memory_slots if slot.is_active()]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        # 计算平均记忆强度
        total_strength = 0.0
        total_memories = 0
        
        for memories in self.long_term_memory.values():
            for memory_item in memories.values():
                strength = memory_item.calculate_current_strength(self.current_time)
                total_strength += strength
                total_memories += 1
        
        if total_memories > 0:
            self.memory_stats['average_memory_strength'] = total_strength / total_memories
        
        # 更新统计
        stats = dict(self.memory_stats)
        stats.update({
            'sensory_memory_count': len(self.sensory_memory.buffer),
            'short_term_memory_count': len(self.short_term_memory),
            'working_memory_active_slots': sum(1 for slot in self.working_memory_slots if slot.is_active()),
            'long_term_memory_by_type': {
                memory_type.value: len(memories) 
                for memory_type, memories in self.long_term_memory.items()
            },
            'memory_associations_count': len(self.memory_associations),
            'current_time': self.current_time
        })
        
        return stats
    
    def perform_memory_maintenance(self):
        """执行记忆维护任务"""
        # 巩固记忆
        self.consolidate_memories()
        
        # 遗忘弱记忆
        self.forget_weak_memories()
        
        # 更新统计信息
        self._update_overall_stats()
    
    def _update_overall_stats(self):
        """更新整体统计信息"""
        total_memories = sum(len(memories) for memories in self.long_term_memory.values())
        self.memory_stats['total_memories'] = total_memories
        
        # 计算平均记忆强度
        total_strength = 0.0
        memory_count = 0
        
        for memories in self.long_term_memory.values():
            for memory_item in memories.values():
                total_strength += memory_item.current_strength
                memory_count += 1
        
        if memory_count > 0:
            self.memory_stats['average_memory_strength'] = total_strength / memory_count
        else:
            self.memory_stats['average_memory_strength'] = 0.0
        
        # 更新关联数量
        total_associations = sum(len(associations) for associations in self.memory_associations.values())
        self.memory_stats['memory_associations_count'] = total_associations // 2  # 除以2因为是双向关联
    
    def update_memories(self, time_passed_hours: float = 1.0):
        """更新记忆系统，处理时间流逝的影响"""
        # 更新当前时间
        self.current_time += time_passed_hours * 3600  # 转换为秒
        
        # 更新所有记忆的强度
        for memory_type, memories in self.long_term_memory.items():
            for memory_item in memories.values():
                memory_item.calculate_current_strength(self.current_time)
        
        # 执行记忆维护
        self.perform_memory_maintenance()
        
        # 更新工作记忆
        self.update_time(self.current_time)
        
        # 清理短期记忆
        self._cleanup_short_term_memory()
    
    def _cleanup_short_term_memory(self):
        """清理过期的短期记忆"""
        current_items = []
        for item in self.short_term_memory:
            if self.current_time < item['expires_at']:
                current_items.append(item)
        
        self.short_term_memory.clear()
        self.short_term_memory.extend(current_items)
    
    def get_relevant_memories(self, query: str, memory_type: str = None, limit: int = 10) -> List[MemoryItem]:
        """
        获取相关记忆的便捷方法（为测试兼容性添加）
        
        Args:
            query: 查询字符串
            memory_type: 记忆类型过滤
            limit: 返回结果限制
            
        Returns:
            相关记忆项列表
        """
        # 将字符串类型转换为MemoryType枚举列表
        memory_types = None
        if memory_type:
            try:
                memory_types = [memory_type]
            except:
                memory_types = None
        
        # 使用现有的search_memories方法
        return self.search_memories(
            query=query,
            memory_types=memory_types,
            max_results=limit
        )

    def export_memory_state(self) -> Dict[str, Any]:
        """导出记忆状态"""
        state = {
            'timestamp': self.current_time,
            'sensory_memory': [
                {
                    'content': str(item['content']),
                    'timestamp': item['timestamp'],
                    'expires_at': item['expires_at']
                }
                for item in self.sensory_memory.buffer
            ],
            'short_term_memory': [
                {
                    'content': str(item['content']),
                    'timestamp': item['timestamp'],
                    'expires_at': item['expires_at'],
                    'activation_level': item['activation_level']
                }
                for item in self.short_term_memory
            ],
            'working_memory': [
                {
                    'content': str(slot.content) if slot.content else None,
                    'activation_level': slot.activation_level,
                    'last_update': slot.last_update,
                    'source_memory_id': slot.source_memory_id
                }
                for slot in self.working_memory_slots
            ],
            'long_term_memory_summary': {
                memory_type.value: {
                    'count': len(memories),
                    'sample_memories': [
                        {
                            'id': memory_id,
                            'content': str(memory_item.content)[:100],
                            'importance': memory_item.importance.value,
                            'current_strength': memory_item.calculate_current_strength(self.current_time),
                            'tags': memory_item.tags
                        }
                        for memory_id, memory_item in list(memories.items())[:3]
                    ]
                }
                for memory_type, memories in self.long_term_memory.items()
            },
            'statistics': self.get_memory_statistics()
        }
        
        return state 

    def update_rule_effectiveness(self, rule_id: str, effectiveness_score: float, outcome: Dict[str, Any] = None):
        """更新规律效果记录
        
        Args:
            rule_id: 规律ID
            effectiveness_score: 效果评分 (0.0-1.0)
            outcome: 行动结果（可选）
        """
        try:
            # 查找相关的规律记忆
            rule_memory = None
            rule_memory_id = None
            
            # 在程序性记忆中查找规律相关记忆
            procedural_memories = self.long_term_memory.get(MemoryType.PROCEDURAL, {})
            for memory_id, memory_item in procedural_memories.items():
                # 检查记忆内容是否包含该规律
                content = memory_item.content
                if isinstance(content, dict) and content.get('rule_id') == rule_id:
                    rule_memory = memory_item
                    rule_memory_id = memory_id
                    break
                elif isinstance(content, str) and rule_id in content:
                    rule_memory = memory_item
                    rule_memory_id = memory_id
                    break
            
            # 如果没找到，创建新的规律效果记忆
            if not rule_memory:
                rule_content = {
                    'rule_id': rule_id,
                    'effectiveness_history': [],
                    'total_applications': 0,
                    'success_count': 0,
                    'average_effectiveness': 0.0
                }
                
                rule_memory_id = self.store_memory(
                    content=rule_content,
                    memory_type='procedural',
                    importance=MemoryImportance.MEDIUM,
                    tags=['rule_effectiveness', rule_id]
                )
                rule_memory = procedural_memories[rule_memory_id]
            
            # 更新规律效果数据
            content = rule_memory.content
            if isinstance(content, dict):
                # 添加新的效果记录
                content['effectiveness_history'].append({
                    'timestamp': self.current_time,
                    'effectiveness_score': effectiveness_score,
                    'outcome': outcome or {}
                })
                
                # 更新统计信息
                content['total_applications'] += 1
                if effectiveness_score > 0.5:
                    content['success_count'] += 1
                
                # 更新平均效果
                history = content['effectiveness_history']
                if history:
                    content['average_effectiveness'] = sum(h['effectiveness_score'] for h in history) / len(history)
                
                # 限制历史记录长度
                if len(content['effectiveness_history']) > 50:
                    content['effectiveness_history'] = content['effectiveness_history'][-50:]
                
                # 根据效果调整记忆重要性
                if content['average_effectiveness'] > 0.8:
                    rule_memory.importance = MemoryImportance.HIGH
                elif content['average_effectiveness'] < 0.3:
                    rule_memory.importance = MemoryImportance.LOW
                
                # 访问记忆以增强其强度
                rule_memory.access(self.current_time)
                
                if self.logger:
                    success_rate = content['success_count'] / content['total_applications'] * 100
                    self.logger.log(f"规律效果更新: {rule_id}, 当前效果:{effectiveness_score:.2f}, 成功率:{success_rate:.1f}%")
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"更新规律效果失败: {str(e)}")
    
    def get_rule_effectiveness_summary(self, rule_id: str = None) -> Dict[str, Any]:
        """获取规律效果摘要
        
        Args:
            rule_id: 特定规律ID，如果为None则返回所有规律摘要
            
        Returns:
            规律效果摘要
        """
        try:
            effectiveness_summary = {}
            
            procedural_memories = self.long_term_memory.get(MemoryType.PROCEDURAL, {})
            
            for memory_id, memory_item in procedural_memories.items():
                content = memory_item.content
                if isinstance(content, dict) and 'rule_id' in content:
                    current_rule_id = content['rule_id']
                    
                    # 如果指定了特定规律ID，只处理该规律
                    if rule_id and current_rule_id != rule_id:
                        continue
                    
                    effectiveness_summary[current_rule_id] = {
                        'total_applications': content.get('total_applications', 0),
                        'success_count': content.get('success_count', 0),
                        'average_effectiveness': content.get('average_effectiveness', 0.0),
                        'memory_strength': memory_item.current_strength,
                        'last_updated': memory_item.last_access_time,
                        'importance_level': memory_item.importance.value
                    }
                    
                    # 计算成功率
                    total_apps = content.get('total_applications', 0)
                    if total_apps > 0:
                        effectiveness_summary[current_rule_id]['success_rate'] = (
                            content.get('success_count', 0) / total_apps
                        )
                    else:
                        effectiveness_summary[current_rule_id]['success_rate'] = 0.0
            
            # 如果指定了特定规律ID但没找到，返回空摘要
            if rule_id and rule_id not in effectiveness_summary:
                return {
                    'rule_id': rule_id,
                    'total_applications': 0,
                    'success_count': 0,
                    'average_effectiveness': 0.0,
                    'success_rate': 0.0,
                    'status': 'not_found'
                }
            
            return effectiveness_summary if not rule_id else effectiveness_summary.get(rule_id, {})
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"获取规律效果摘要失败: {str(e)}")
            return {} 