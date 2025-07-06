#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
五库系统 (Five Library System)
实现ILAI婴儿模型的知识同步和规律生成机制

五库架构：
1. 直接经验库 (Direct Experience Library) - direct_experiences.db
2. 总经验库 (Total Experience Library) - total_experiences.db  
3. 直接规律库 (Direct Rules Library) - direct_rules.db
4. 总规律库 (Total Rules Library) - total_rules.db
5. 决策库 (Decision Library) - decisions.db
"""

import sqlite3
import json
import hashlib
import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入对象属性配置
try:
    from object_attributes_config import (
        ANIMAL_CHARACTERISTICS, PLANT_CHARACTERISTICS, TOOL_CHARACTERISTICS, 
        ENVIRONMENT_TYPES, TARGET_TYPE_MAPPING, calculate_tool_effectiveness,
        get_best_tool_for_target, get_object_attributes, get_all_object_names
    )
    OBJECT_CONFIG_AVAILABLE = True
except ImportError:
    OBJECT_CONFIG_AVAILABLE = False
    logger.warning("Object attribute configuration file not found, will use default configuration")

@dataclass
class EOCATRExperience:
    """EOCATR经验数据结构"""
    environment: str
    object: str
    characteristics: str
    action: str
    tools: str
    result: str
    player_id: str
    timestamp: float
    success: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'environment': self.environment,
            'object': self.object,
            'characteristics': self.characteristics,
            'action': self.action,
            'tools': self.tools,
            'result': self.result,
            'player_id': self.player_id,
            'timestamp': self.timestamp,
            'success': self.success,
            'metadata': json.dumps(self.metadata)
        }
    
    def generate_hash(self) -> str:
        """生成经验内容哈希用于去重"""
        # 使用核心内容生成哈希，排除时间戳和玩家ID
        content = (
            f"{self.environment}|{self.object}|{self.characteristics}|"
            f"{self.action}|{self.tools}|{self.result}"
        )
        return hashlib.md5(content.encode('utf-8')).hexdigest()

@dataclass
class Rule:
    """规律数据结构"""
    rule_id: str
    rule_type: str  # CN1, CN2
    conditions: Dict
    predictions: Dict
    confidence: float
    support_count: int
    contradiction_count: int
    created_time: float
    creator_id: str
    validation_status: str = 'pending'  # pending, validated, rejected
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'rule_id': self.rule_id,
            'rule_type': self.rule_type,
            'conditions': json.dumps(self.conditions),
            'predictions': json.dumps(self.predictions),
            'confidence': self.confidence,
            'support_count': self.support_count,
            'contradiction_count': self.contradiction_count,
            'created_time': self.created_time,
            'creator_id': self.creator_id,
            'validation_status': self.validation_status
        }
    
    def generate_hash(self) -> str:
        """生成规律内容哈希用于去重"""
        content = f"{self.rule_type}|{json.dumps(self.conditions, sort_keys=True)}|{json.dumps(self.predictions, sort_keys=True)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

@dataclass
class Decision:
    """决策数据结构"""
    decision_id: str
    context: Dict  # 决策上下文
    action: str
    confidence: float
    source: str  # 'decision_library', 'wbm_generated'
    success_count: int = 0
    failure_count: int = 0
    total_uses: int = 0
    created_time: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'decision_id': self.decision_id,
            'context': json.dumps(self.context),
            'action': self.action,
            'confidence': self.confidence,
            'source': self.source,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'total_uses': self.total_uses,
            'created_time': self.created_time,
            'last_used': self.last_used
        }
    
    def generate_hash(self) -> str:
        """生成决策内容哈希"""
        content = f"{json.dumps(self.context, sort_keys=True)}|{self.action}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """执行查询"""
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新操作"""
        with self.lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount

class FiveLibrarySystem:
    """五库系统核心实现"""
    
    def __init__(self, base_path: str = "five_libraries"):
        """
        初始化五库系统
        
        Args:
            base_path: 五库文件存储基础路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # 五库数据库路径
        self.db_paths = {
            'direct_experiences': self.base_path / "direct_experiences.db",
            'total_experiences': self.base_path / "total_experiences.db",
            'direct_rules': self.base_path / "direct_rules.db",
            'total_rules': self.base_path / "total_rules.db",
            'decisions': self.base_path / "decisions.db"
        }
        
        # 数据库管理器
        self.db_managers = {
            name: DatabaseManager(str(path)) 
            for name, path in self.db_paths.items()
        }
        
        # 缓存系统
        self.cache = {
            'experience_hashes': set(),
            'rule_hashes': set(),
            'decision_hashes': set(),
            'last_cache_update': 0
        }
        
        # ✅ 新增：同步状态跟踪
        self.sync_tracker = {
            'synced_experience_hashes': set(),  # 已同步的经验哈希
            'pending_sync_hashes': set(),       # 待同步的经验哈希
            'last_sync_check': 0,               # 上次同步检查时间
            'sync_batch_size': 100,  # 性能优化: 大幅增加批量大小  # 性能优化: 增加批量大小
            'sync_interval': 300  # 性能优化: 减少同步频率（5分钟）   # 性能优化: 减少同步频率（秒）
        }
        
        # 对象属性系统
        self.object_config_enabled = OBJECT_CONFIG_AVAILABLE
        if self.object_config_enabled:
            logger.info("Object attribute configuration system enabled")
            logger.info(f"Loaded {len(get_all_object_names())} object attribute configurations")
        else:
            logger.warning("Object attribute configuration system not enabled, using basic validation")
        
        # 系统锁
        self.system_lock = threading.Lock()
        
        # 初始化五库数据库
        self._initialize_five_libraries()
        
        # ✅ 新增：初始化同步状态
        self._initialize_sync_tracker()
        
        # 🔧 优化的日志记录器
        try:
            from five_library_log_optimization import OptimizedSyncLogger
            self.sync_logger = OptimizedSyncLogger(
                aggregate_interval=30,  # 30秒聚合
                max_individual_logs=3   # 每窗口最多3条个别日志
            )
            logger.info("🚀 Five library system log optimization enabled")
        except ImportError:
            self.sync_logger = None
            logger.info("⚠️ Log optimization module not found, using standard logging")
        
        logger.info(f"🏛️ Five library system initialization completed")
        logger.info(f"📁 Storage path: {self.base_path}")
        for name, path in self.db_paths.items():
            logger.info(f"   {name}: {path.name}")
    
    def _initialize_five_libraries(self):
        """初始化五库数据库结构"""
        
        # 1. 直接经验库
        self._init_direct_experiences_db()
        
        # 2. 总经验库
        self._init_total_experiences_db()
        
        # 3. 直接规律库
        self._init_direct_rules_db()
        
        # 4. 总规律库
        self._init_total_rules_db()
        
        # 5. 决策库
        self._init_decisions_db()
        
        logger.info("✅ Five library database structure initialization completed")
    
    def _init_direct_experiences_db(self):
        """初始化直接经验库"""
        db_manager = self.db_managers['direct_experiences']
        
        # 创建直接经验表
        db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS direct_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                environment TEXT NOT NULL,
                object TEXT NOT NULL,
                characteristics TEXT NOT NULL,
                action TEXT NOT NULL,
                tools TEXT NOT NULL,
                result TEXT NOT NULL,
                player_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                success INTEGER NOT NULL,
                metadata TEXT,
                occurrence_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                first_discovered_by TEXT,
                first_discovered_time REAL,
                last_seen_time REAL,
                discoverers TEXT DEFAULT '[]',
                avg_success_rate REAL DEFAULT 0.0,
                created_time REAL DEFAULT (julianday('now')),
                synced_to_total INTEGER DEFAULT 0
            )
        """)
        
        # 创建索引
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_hash ON direct_experiences(content_hash)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_player ON direct_experiences(player_id)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_action ON direct_experiences(action)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_sync ON direct_experiences(synced_to_total)")
    
    def _init_total_experiences_db(self):
        """初始化总经验库"""
        db_manager = self.db_managers['total_experiences']
        
        # 创建总经验表
        db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS total_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                environment TEXT NOT NULL,
                object TEXT NOT NULL,
                characteristics TEXT NOT NULL,
                action TEXT NOT NULL,
                tools TEXT NOT NULL,
                result TEXT NOT NULL,
                success INTEGER NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                first_discovered_by TEXT,
                first_discovered_time REAL,
                last_seen_time REAL,
                discoverers TEXT,  -- JSON array of player_ids
                avg_success_rate REAL,
                confidence REAL DEFAULT 0.5,
                created_time REAL DEFAULT (julianday('now')),
                updated_time REAL DEFAULT (julianday('now'))
            )
        """)
        
        # 创建索引
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_hash ON total_experiences(content_hash)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_action ON total_experiences(action)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_confidence ON total_experiences(confidence)")
    
    def _init_direct_rules_db(self):
        """初始化直接规律库"""
        db_manager = self.db_managers['direct_rules']
        
        # 创建直接规律表
        db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS direct_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                rule_type TEXT NOT NULL,  -- CN1, CN2
                conditions TEXT NOT NULL,  -- JSON
                predictions TEXT NOT NULL,  -- JSON
                confidence REAL NOT NULL,
                support_count INTEGER DEFAULT 0,
                contradiction_count INTEGER DEFAULT 0,
                validation_count INTEGER DEFAULT 0,
                created_time REAL NOT NULL,
                creator_id TEXT NOT NULL,
                validation_status TEXT DEFAULT 'pending',
                synced_to_total INTEGER DEFAULT 0,
                last_sync_time REAL DEFAULT 0,
                last_validated REAL DEFAULT 0
            )
        """)
        
        # 创建索引
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_rule_id ON direct_rules(rule_id)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_rule_hash ON direct_rules(content_hash)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_rule_type ON direct_rules(rule_type)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_rule_confidence ON direct_rules(confidence)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_direct_rule_sync ON direct_rules(synced_to_total)")
    
    def _init_total_rules_db(self):
        """初始化总规律库"""
        db_manager = self.db_managers['total_rules']
        
        # 创建总规律表
        db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS total_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                rule_type TEXT NOT NULL,  -- CN1, CN2
                conditions TEXT NOT NULL,  -- JSON
                predictions TEXT NOT NULL,  -- JSON
                confidence REAL NOT NULL,
                support_count INTEGER DEFAULT 0,
                contradiction_count INTEGER DEFAULT 0,
                validation_count INTEGER DEFAULT 0,
                occurrence_count INTEGER DEFAULT 1,
                discoverers TEXT DEFAULT '[]',  -- JSON array of player_ids
                validation_status TEXT DEFAULT 'pending',
                created_time REAL NOT NULL,
                last_updated REAL NOT NULL,
                last_validated REAL DEFAULT 0
            )
        """)
        
        # 创建索引
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_rule_id ON total_rules(rule_id)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_rule_hash ON total_rules(content_hash)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_rule_type ON total_rules(rule_type)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_total_rule_confidence ON total_rules(confidence)")
    
    def _init_decisions_db(self):
        """初始化决策库"""
        db_manager = self.db_managers['decisions']
        
        # 创建决策表
        db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                context TEXT NOT NULL,  -- JSON
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL,  -- 'decision_library', 'wbm_generated'
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                total_uses INTEGER DEFAULT 0,
                created_time REAL NOT NULL,
                last_used REAL NOT NULL,
                avg_success_rate REAL DEFAULT 0.0,
                emrs_score REAL DEFAULT 0.0,
                updated_time REAL DEFAULT (julianday('now'))
            )
        """)
        
        # 创建索引
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_decision_id ON decisions(decision_id)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_decision_hash ON decisions(content_hash)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_decision_confidence ON decisions(confidence)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_decision_action ON decisions(action)")
        db_manager.execute_update("CREATE INDEX IF NOT EXISTS idx_decision_last_used ON decisions(last_used)")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """获取五库系统统计信息"""
        stats = {}
        
        try:
            # 直接经验库统计
            result = self.db_managers['direct_experiences'].execute_query("SELECT COUNT(*) as count FROM direct_experiences")
            stats['direct_experiences'] = result[0]['count'] if result else 0
            
            # 总经验库统计
            result = self.db_managers['total_experiences'].execute_query("SELECT COUNT(*) as count FROM total_experiences")
            stats['total_experiences'] = result[0]['count'] if result else 0
            
            # 直接规律库统计
            result = self.db_managers['direct_rules'].execute_query("SELECT COUNT(*) as count FROM direct_rules")
            stats['direct_rules'] = result[0]['count'] if result else 0
            
            # 总规律库统计
            result = self.db_managers['total_rules'].execute_query("SELECT COUNT(*) as count FROM total_rules")
            stats['total_rules'] = result[0]['count'] if result else 0
            
            # 决策库统计
            result = self.db_managers['decisions'].execute_query("SELECT COUNT(*) as count FROM decisions")
            stats['decisions'] = result[0]['count'] if result else 0
            
            # 缓存统计
            stats['cache_experience_hashes'] = len(self.cache['experience_hashes'])
            stats['cache_rule_hashes'] = len(self.cache['rule_hashes'])
            stats['cache_decision_hashes'] = len(self.cache['decision_hashes'])
            
            # 高置信度统计
            result = self.db_managers['decisions'].execute_query("SELECT COUNT(*) as count FROM decisions WHERE confidence >= 0.7")
            stats['high_confidence_decisions'] = result[0]['count'] if result else 0
            
            result = self.db_managers['total_rules'].execute_query("SELECT COUNT(*) as count FROM total_rules WHERE confidence >= 0.6")
            stats['validated_rules'] = result[0]['count'] if result else 0
            
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {str(e)}")
        
        return stats
    
    def _update_cache(self):
        """更新缓存"""
        current_time = time.time()
        if current_time - self.cache['last_cache_update'] < 60:  # 1分钟内不重复更新
            return
        
        try:
            # 更新经验哈希缓存
            result = self.db_managers['total_experiences'].execute_query("SELECT content_hash FROM total_experiences")
            self.cache['experience_hashes'] = {row['content_hash'] for row in result}
            
            # 更新规律哈希缓存
            result = self.db_managers['total_rules'].execute_query("SELECT content_hash FROM total_rules")
            self.cache['rule_hashes'] = {row['content_hash'] for row in result}
            
            # 更新决策哈希缓存
            result = self.db_managers['decisions'].execute_query("SELECT content_hash FROM decisions")
            self.cache['decision_hashes'] = {row['content_hash'] for row in result}
            
            self.cache['last_cache_update'] = current_time
            
        except Exception as e:
            logger.error(f"❌ 更新缓存失败: {str(e)}")

    # ==================== EOCATR经验处理模块 ====================
    
    def validate_eocatr_experience(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        验证EOCATR经验的完整性和有效性
        
        Args:
            experience: EOCATR经验对象
            
        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'normalized_experience': None
        }
        
        try:
            # 1. 必填字段检查
            required_fields = ['environment', 'object', 'characteristics', 'action', 'tools', 'result', 'player_id']
            for field in required_fields:
                value = getattr(experience, field, None)
                if not value or (isinstance(value, str) and not value.strip()):
                    validation_result['errors'].append(f"必填字段 '{field}' 为空或无效")
                    validation_result['is_valid'] = False
            
            # 2. 数据类型检查
            if not isinstance(experience.timestamp, (int, float)) or experience.timestamp <= 0:
                validation_result['errors'].append("timestamp 必须是正数")
                validation_result['is_valid'] = False
            
            if not isinstance(experience.success, bool):
                validation_result['errors'].append("success 必须是布尔值")
                validation_result['is_valid'] = False
            
            if not isinstance(experience.metadata, dict):
                validation_result['errors'].append("metadata 必须是字典类型")
                validation_result['is_valid'] = False
            
            # 3. 字段长度检查
            max_lengths = {
                'environment': 100,
                'object': 100, 
                'characteristics': 200,
                'action': 100,
                'tools': 100,
                'result': 200,
                'player_id': 50
            }
            
            for field, max_len in max_lengths.items():
                value = getattr(experience, field, '')
                if len(str(value)) > max_len:
                    validation_result['warnings'].append(f"字段 '{field}' 长度超过建议值 {max_len}")
            
            # 4. 内容规范化
            if validation_result['is_valid']:
                normalized_exp = self._normalize_eocatr_experience(experience)
                validation_result['normalized_experience'] = normalized_exp
            
            # 5. 业务逻辑检查
            if validation_result['is_valid']:
                business_check = self._validate_business_logic(experience)
                validation_result['warnings'].extend(business_check.get('warnings', []))
                if business_check.get('errors'):
                    validation_result['errors'].extend(business_check['errors'])
                    validation_result['is_valid'] = False
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"验证过程异常: {str(e)}")
        
        return validation_result
    
    def _normalize_eocatr_experience(self, experience: EOCATRExperience) -> EOCATRExperience:
        """
        规范化EOCATR经验数据
        
        Args:
            experience: 原始经验对象
            
        Returns:
            规范化后的经验对象
        """
        # 创建规范化的经验副本
        normalized = EOCATRExperience(
            environment=str(experience.environment).strip().lower(),
            object=str(experience.object).strip().lower(),
            characteristics=str(experience.characteristics).strip().lower(),
            action=str(experience.action).strip().lower(),
            tools=str(experience.tools).strip().lower(),
            result=str(experience.result).strip(),  # result保持原始大小写
            player_id=str(experience.player_id).strip(),
            timestamp=float(experience.timestamp),
            success=bool(experience.success),
            metadata=dict(experience.metadata) if experience.metadata else {}
        )
        
        # 添加规范化时间戳
        normalized.metadata['normalized_time'] = time.time()
        normalized.metadata['original_timestamp'] = experience.timestamp
        
        return normalized
    
    def _validate_business_logic(self, experience: EOCATRExperience) -> Dict[str, List[str]]:
        """
        验证业务逻辑规则
        
        Args:
            experience: 经验对象
            
        Returns:
            包含errors和warnings的字典
        """
        result = {'errors': [], 'warnings': []}
        
        # 1. 环境-对象组合合理性检查
        valid_combinations = {
            'forest': ['tree', 'strawberry', 'mushroom', 'animal', 'water'],
            'cave': ['crystal', 'ore', 'bat', 'treasure'],
            'river': ['fish', 'water', 'stone'],
            'mountain': ['ore', 'crystal', 'eagle', 'snow']
        }
        
        env = str(experience.environment).lower()
        obj = str(experience.object).lower()
        
        if env in valid_combinations and obj not in valid_combinations[env]:
            result['warnings'].append(f"环境 '{env}' 中出现 '{obj}' 可能不常见")
        
        # 2. 行动-工具组合检查
        action_tool_pairs = {
            'collect': ['basket', 'bag', 'hands'],
            'attack': ['sword', 'bow', 'magic', 'hands'],
            'explore': ['torch', 'map', 'compass', 'none'],
            'craft': ['hammer', 'anvil', 'workbench', 'hands']
        }
        
        action = str(experience.action).lower()
        tool = str(experience.tools).lower()
        
        if action in action_tool_pairs and tool not in action_tool_pairs[action]:
            result['warnings'].append(f"行动 '{action}' 使用工具 '{tool}' 可能不合适")
        
        # 3. 结果合理性检查
        if experience.success:
            if 'fail' in str(experience.result).lower() or 'error' in str(experience.result).lower():
                result['warnings'].append("成功标记为True但结果描述包含失败信息")
        else:
            if 'success' in str(experience.result).lower():
                result['warnings'].append("成功标记为False但结果描述包含成功信息")
        
        # 4. 时间戳合理性检查
        current_time = time.time()
        if experience.timestamp > current_time + 3600:  # 未来1小时以上
            result['errors'].append("时间戳不能是未来时间")
        elif experience.timestamp < current_time - 86400 * 365:  # 1年以前
            result['warnings'].append("时间戳过于久远")
        
        return result
    
    def check_experience_duplication(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        检查经验是否重复
        
        Args:
            experience: 经验对象
            
        Returns:
            去重检查结果
        """
        duplication_result = {
            'is_duplicate': False,
            'duplicate_source': None,  # 'direct', 'total', 'cache'
            'existing_record': None,
            'content_hash': None,
            'similarity_score': 0.0
        }
        
        try:
            # 生成内容哈希
            content_hash = experience.generate_hash()
            duplication_result['content_hash'] = content_hash
            
            # 1. 首先检查缓存
            self._update_cache()
            if content_hash in self.cache['experience_hashes']:
                duplication_result['is_duplicate'] = True
                duplication_result['duplicate_source'] = 'cache'
                return duplication_result
            
            # 2. 检查总经验库
            total_result = self.db_managers['total_experiences'].execute_query(
                "SELECT * FROM total_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if total_result:
                duplication_result['is_duplicate'] = True
                duplication_result['duplicate_source'] = 'total'
                duplication_result['existing_record'] = dict(total_result[0])
                return duplication_result
            
            # 3. 检查直接经验库
            direct_result = self.db_managers['direct_experiences'].execute_query(
                "SELECT * FROM direct_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if direct_result:
                duplication_result['is_duplicate'] = True
                duplication_result['duplicate_source'] = 'direct'
                duplication_result['existing_record'] = dict(direct_result[0])
                return duplication_result
            
            # 4. 模糊相似度检查（可选）
            similarity_check = self._check_experience_similarity(experience)
            duplication_result['similarity_score'] = similarity_check['max_similarity']
            
            if similarity_check['max_similarity'] > 0.9:  # 90%相似度阈值
                duplication_result['is_duplicate'] = True
                duplication_result['duplicate_source'] = 'similarity'
                duplication_result['existing_record'] = similarity_check['most_similar_record']
            
        except Exception as e:
            logger.error(f"❌ 去重检查失败: {str(e)}")
        
        return duplication_result
    
    def _check_experience_similarity(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        检查经验相似度
        
        Args:
            experience: 经验对象
            
        Returns:
            相似度检查结果
        """
        similarity_result = {
            'max_similarity': 0.0,
            'most_similar_record': None,
            'similar_records': []
        }
        
        try:
            # 查询相同action的经验进行相似度比较
            similar_experiences = self.db_managers['total_experiences'].execute_query(
                "SELECT * FROM total_experiences WHERE action = ? LIMIT 50", 
                (experience.action,)
            )
            
            for record in similar_experiences:
                similarity = self._calculate_experience_similarity(experience, record)
                
                if similarity > similarity_result['max_similarity']:
                    similarity_result['max_similarity'] = similarity
                    similarity_result['most_similar_record'] = dict(record)
                
                if similarity > 0.7:  # 70%以上相似度记录
                    similarity_result['similar_records'].append({
                        'record': dict(record),
                        'similarity': similarity
                    })
        
        except Exception as e:
            logger.error(f"❌ 相似度检查失败: {str(e)}")
        
        return similarity_result
    
    def _calculate_experience_similarity(self, exp1: EOCATRExperience, exp2_record) -> float:
        """
        计算两个经验的相似度
        
        Args:
            exp1: 经验对象1
            exp2_record: 经验记录2（数据库记录，可能是sqlite3.Row或dict）
            
        Returns:
            相似度分数 (0.0-1.0)
        """
        try:
            # 字段权重
            field_weights = {
                'environment': 0.2,
                'object': 0.2,
                'characteristics': 0.15,
                'action': 0.25,
                'tools': 0.1,
                'result': 0.1
            }
            
            total_similarity = 0.0
            
            for field, weight in field_weights.items():
                val1 = str(getattr(exp1, field, '')).lower().strip()
                
                # 兼容sqlite3.Row和dict两种类型
                if hasattr(exp2_record, 'keys'):  # dict-like
                    val2 = str(exp2_record.get(field, '') if hasattr(exp2_record, 'get') else exp2_record[field]).lower().strip()
                else:  # sqlite3.Row
                    val2 = str(exp2_record[field] if field in exp2_record.keys() else '').lower().strip()
                
                if val1 == val2:
                    field_similarity = 1.0
                elif val1 in val2 or val2 in val1:
                    field_similarity = 0.7
                else:
                    field_similarity = 0.0
                
                total_similarity += field_similarity * weight
            
            return total_similarity
            
        except Exception as e:
            logger.error(f"❌ 相似度计算失败: {str(e)}")
            return 0.0
    
    def format_experience_for_storage(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        格式化经验数据用于存储
        
        Args:
            experience: 经验对象
            
        Returns:
            格式化后的存储数据
        """
        try:
            # 基础数据转换
            storage_data = experience.to_dict()
            
            # 添加存储相关字段
            storage_data['content_hash'] = experience.generate_hash()
            storage_data['storage_timestamp'] = time.time()
            
            # 处理metadata
            if isinstance(storage_data['metadata'], str):
                # 如果已经是JSON字符串，验证其有效性
                try:
                    json.loads(storage_data['metadata'])
                except json.JSONDecodeError:
                    storage_data['metadata'] = json.dumps({})
            else:
                storage_data['metadata'] = json.dumps(storage_data['metadata'])
            
            # 数据类型转换
            storage_data['success'] = int(storage_data['success'])
            storage_data['timestamp'] = float(storage_data['timestamp'])
            
            return storage_data
            
        except Exception as e:
            logger.error(f"❌ 经验格式化失败: {str(e)}")
            return {}

    # ==================== 去重同步模块 ====================
    
    def add_experience_to_direct_library(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        添加经验到直接经验库
        
        Args:
            experience: EOCATR经验对象
            
        Returns:
            添加结果字典
        """
        add_result = {
            'success': False,
            'action': None,  # 'added', 'updated', 'rejected'
            'reason': None,
            'experience_id': None,
            'content_hash': None,
            'sync_required': False
        }
        
        try:
            # 1. 验证经验
            validation_result = self.validate_eocatr_experience(experience)
            if not validation_result['is_valid']:
                add_result['action'] = 'rejected'
                add_result['reason'] = f"验证失败: {', '.join(validation_result['errors'])}"
                # 即使验证失败，也尝试生成content_hash用于调试
                try:
                    add_result['content_hash'] = experience.generate_hash()
                except:
                    add_result['content_hash'] = None
                return add_result
            
            # 使用规范化后的经验
            normalized_exp = validation_result['normalized_experience']
            content_hash = normalized_exp.generate_hash()
            add_result['content_hash'] = content_hash
            
            # 2. 检查直接经验库中是否已存在
            existing_direct = self.db_managers['direct_experiences'].execute_query(
                "SELECT * FROM direct_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if existing_direct:
                # 更新现有记录
                record_id = existing_direct[0]['id']
                self.db_managers['direct_experiences'].execute_update("""
                    UPDATE direct_experiences 
                    SET occurrence_count = occurrence_count + 1,
                        success_count = success_count + ?,
                        last_seen_time = ?,
                        discoverers = CASE 
                            WHEN discoverers LIKE '%"' || ? || '"%' THEN discoverers
                            ELSE json_insert(discoverers, '$[#]', ?)
                        END,
                        avg_success_rate = CAST(success_count + ? AS FLOAT) / (occurrence_count + 1)
                    WHERE id = ?
                """, (
                    int(normalized_exp.success), normalized_exp.timestamp, 
                    normalized_exp.player_id, normalized_exp.player_id,
                    int(normalized_exp.success), record_id
                ))
                
                add_result['success'] = True
                add_result['action'] = 'updated'
                add_result['experience_id'] = record_id
                add_result['sync_required'] = True
                
            else:
                # 添加新记录
                storage_data = self.format_experience_for_storage(normalized_exp)
                
                result = self.db_managers['direct_experiences'].execute_update("""
                    INSERT INTO direct_experiences 
                    (content_hash, environment, object, characteristics, action, tools, result,
                     player_id, timestamp, success, metadata, occurrence_count, success_count,
                     first_discovered_by, first_discovered_time, last_seen_time, discoverers, avg_success_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    storage_data['content_hash'],
                    storage_data['environment'], storage_data['object'], storage_data['characteristics'],
                    storage_data['action'], storage_data['tools'], storage_data['result'],
                    storage_data['player_id'], storage_data['timestamp'], storage_data['success'],
                    storage_data['metadata'], 1, int(normalized_exp.success),
                    storage_data['player_id'], storage_data['timestamp'], storage_data['timestamp'],
                    f'["{storage_data["player_id"]}"]', float(normalized_exp.success)
                ))
                
                add_result['success'] = True
                add_result['action'] = 'added'
                add_result['experience_id'] = result
                add_result['sync_required'] = True
            
            # 3. 更新缓存
            self.cache['experience_hashes'].add(content_hash)
            
            # 🔧 优化: 降低重复日志的级别
            if add_result['action'] == 'added':
                logger.info(f"✨ New experience added to direct library: {content_hash[:16]}...")
            else:
                logger.debug(f"🔄 Experience updated: {content_hash[:16]}... ({add_result.get('occurrence_count', 1)}th time)")
            
        except Exception as e:
            add_result['action'] = 'rejected'
            add_result['reason'] = f"添加失败: {str(e)}"
            # 确保content_hash字段存在，即使在异常情况下
            if 'content_hash' not in add_result:
                try:
                    add_result['content_hash'] = normalized_exp.generate_hash() if 'normalized_exp' in locals() else None
                except:
                    add_result['content_hash'] = None
            logger.error(f"❌ 添加经验到直接库失败: {str(e)}")
        
        # ✅ 修改：智能同步机制
        if add_result['success'] and add_result.get('content_hash'):
            self._smart_sync_experience(add_result['content_hash'], add_result['action'])

        return add_result
    
    def sync_experience_to_total_library(self, content_hash: str) -> Dict[str, Any]:
        """
        将经验从直接经验库同步到总经验库
        
        Args:
            content_hash: 经验内容哈希
            
        Returns:
            同步结果字典
        """
        sync_result = {
            'success': False,
            'action': None,  # 'merged', 'updated', 'created', 'skipped'
            'reason': None,
            'total_occurrence_count': 0,
            'total_success_count': 0,
            'discoverer_count': 0
        }
        
        try:
            # 1. 获取直接经验库中的记录
            direct_records = self.db_managers['direct_experiences'].execute_query(
                "SELECT * FROM direct_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if not direct_records:
                sync_result['action'] = 'skipped'
                sync_result['reason'] = '直接经验库中未找到记录'
                return sync_result
            
            direct_record = direct_records[0]
            
            # 2. 检查总经验库中是否已存在
            total_records = self.db_managers['total_experiences'].execute_query(
                "SELECT * FROM total_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if total_records:
                # 合并到现有记录
                total_record = total_records[0]
                
                # 解析发现者列表
                try:
                    direct_discoverers = json.loads(direct_record['discoverers'])
                    total_discoverers = json.loads(total_record['discoverers'])
                except (json.JSONDecodeError, TypeError):
                    direct_discoverers = [direct_record['first_discovered_by']]
                    total_discoverers = [total_record['first_discovered_by']]
                
                # 合并发现者列表
                merged_discoverers = list(set(direct_discoverers + total_discoverers))
                
                # 计算合并后的统计数据
                new_occurrence_count = total_record['occurrence_count'] + direct_record['occurrence_count']
                new_success_count = total_record['success_count'] + direct_record['success_count']
                new_avg_success_rate = new_success_count / new_occurrence_count if new_occurrence_count > 0 else 0.0
                
                # 更新总经验库记录
                self.db_managers['total_experiences'].execute_update("""
                    UPDATE total_experiences 
                    SET occurrence_count = ?,
                        success_count = ?,
                        last_seen_time = CASE 
                            WHEN ? > last_seen_time THEN ? 
                            ELSE last_seen_time 
                        END,
                        discoverers = ?,
                        avg_success_rate = ?,
                        confidence = CASE 
                            WHEN ? >= 10 THEN 0.9
                            WHEN ? >= 5 THEN 0.8
                            WHEN ? >= 3 THEN 0.7
                            ELSE 0.6
                        END
                    WHERE content_hash = ?
                """, (
                    new_occurrence_count, new_success_count,
                    direct_record['last_seen_time'], direct_record['last_seen_time'],
                    json.dumps(merged_discoverers), new_avg_success_rate,
                    new_occurrence_count, new_occurrence_count, new_occurrence_count,
                    content_hash
                ))
                
                sync_result['action'] = 'merged'
                sync_result['total_occurrence_count'] = new_occurrence_count
                sync_result['total_success_count'] = new_success_count
                sync_result['discoverer_count'] = len(merged_discoverers)
                
            else:
                # 创建新的总经验库记录
                confidence = 0.9 if direct_record['occurrence_count'] >= 10 else \
                           0.8 if direct_record['occurrence_count'] >= 5 else \
                           0.7 if direct_record['occurrence_count'] >= 3 else 0.6
                
                self.db_managers['total_experiences'].execute_update("""
                    INSERT INTO total_experiences 
                    (content_hash, environment, object, characteristics, action, tools, result,
                     success, occurrence_count, success_count, first_discovered_by, 
                     first_discovered_time, last_seen_time, discoverers, avg_success_rate, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    direct_record['content_hash'],
                    direct_record['environment'], direct_record['object'], direct_record['characteristics'],
                    direct_record['action'], direct_record['tools'], direct_record['result'],
                    direct_record['success'], direct_record['occurrence_count'], direct_record['success_count'],
                    direct_record['first_discovered_by'], direct_record['first_discovered_time'],
                    direct_record['last_seen_time'], direct_record['discoverers'],
                    direct_record['avg_success_rate'], confidence
                ))
                
                sync_result['action'] = 'created'
                sync_result['total_occurrence_count'] = direct_record['occurrence_count']
                sync_result['total_success_count'] = direct_record['success_count']
                
                # 解析发现者数量
                try:
                    discoverers = json.loads(direct_record['discoverers'])
                    sync_result['discoverer_count'] = len(discoverers)
                except (json.JSONDecodeError, TypeError):
                    sync_result['discoverer_count'] = 1
            
            sync_result['success'] = True
            
            # 🔧 优化: 使用智能日志记录
            if hasattr(self, 'sync_logger'):
                self.sync_logger.log_sync_result(sync_result, content_hash)
            else:
                # 降级处理：只记录重要信息
                if sync_result['action'] in ['failed', 'created']:
                    logger.info(f"✅ Experience sync: {sync_result['action']} - {content_hash[:16]}...")
                else:
                    logger.debug(f"✅ Experience sync: {sync_result['action']} - {content_hash[:16]}...")
            
        except Exception as e:
            sync_result['action'] = 'failed'
            sync_result['reason'] = f"同步失败: {str(e)}"
            logger.error(f"❌ 经验同步失败: {str(e)}")
        
        return sync_result
    
    def batch_sync_experiences(self, limit: int = 100) -> Dict[str, Any]:
        """
        批量同步直接经验库到总经验库
        
        Args:
            limit: 每次同步的最大记录数
            
        Returns:
            批量同步结果
        """
        batch_result = {
            'success': False,
            'total_processed': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'sync_details': [],
            'summary': {}
        }
        
        try:
            # 获取需要同步的经验（按最后更新时间排序）
            pending_experiences = self.db_managers['direct_experiences'].execute_query("""
                SELECT content_hash, last_seen_time 
                FROM direct_experiences 
                ORDER BY last_seen_time DESC 
                LIMIT ?
            """, (limit,))
            
            batch_result['total_processed'] = len(pending_experiences)
            
            # 统计计数器
            action_counts = {'merged': 0, 'created': 0, 'skipped': 0, 'failed': 0}
            
            for record in pending_experiences:
                content_hash = record['content_hash']
                sync_result = self.sync_experience_to_total_library(content_hash)
                
                if sync_result['success']:
                    batch_result['successful_syncs'] += 1
                    action_counts[sync_result['action']] += 1
                else:
                    batch_result['failed_syncs'] += 1
                    action_counts['failed'] += 1
                
                batch_result['sync_details'].append({
                    'content_hash': content_hash[:16] + '...',
                    'action': sync_result['action'],
                    'success': sync_result['success'],
                    'reason': sync_result.get('reason'),
                    'occurrence_count': sync_result.get('total_occurrence_count', 0),
                    'discoverer_count': sync_result.get('discoverer_count', 0)
                })
            
            batch_result['summary'] = action_counts
            batch_result['success'] = batch_result['failed_syncs'] == 0
            
            logger.info(f"📊 Batch sync completed: {batch_result['successful_syncs']}/{batch_result['total_processed']} successful")
            
        except Exception as e:
            batch_result['reason'] = f"批量同步失败: {str(e)}"
            logger.error(f"❌ 批量同步失败: {str(e)}")
        
        return batch_result
    
    def resolve_sync_conflicts(self, content_hash: str) -> Dict[str, Any]:
        """
        解决同步冲突
        
        Args:
            content_hash: 冲突的经验哈希
            
        Returns:
            冲突解决结果
        """
        conflict_result = {
            'success': False,
            'conflict_type': None,  # 'data_mismatch', 'timestamp_conflict', 'discoverer_conflict'
            'resolution_action': None,  # 'merge_favor_total', 'merge_favor_direct', 'manual_review'
            'details': {}
        }
        
        try:
            # 获取直接库和总库的记录
            direct_record = self.db_managers['direct_experiences'].execute_query(
                "SELECT * FROM direct_experiences WHERE content_hash = ?", (content_hash,)
            )
            total_record = self.db_managers['total_experiences'].execute_query(
                "SELECT * FROM total_experiences WHERE content_hash = ?", (content_hash,)
            )
            
            if not direct_record or not total_record:
                conflict_result['conflict_type'] = 'missing_record'
                conflict_result['resolution_action'] = 'manual_review'
                return conflict_result
            
            direct_rec = direct_record[0]
            total_rec = total_record[0]
            
            # 检查数据不匹配
            core_fields = ['environment', 'object', 'characteristics', 'action', 'tools', 'result']
            data_mismatches = []
            
            for field in core_fields:
                if direct_rec[field] != total_rec[field]:
                    data_mismatches.append({
                        'field': field,
                        'direct_value': direct_rec[field],
                        'total_value': total_rec[field]
                    })
            
            if data_mismatches:
                conflict_result['conflict_type'] = 'data_mismatch'
                conflict_result['details']['mismatches'] = data_mismatches
                conflict_result['resolution_action'] = 'manual_review'
                return conflict_result
            
            # 检查时间戳冲突
            if direct_rec['first_discovered_time'] < total_rec['first_discovered_time']:
                conflict_result['conflict_type'] = 'timestamp_conflict'
                conflict_result['resolution_action'] = 'merge_favor_direct'
                conflict_result['details']['time_diff'] = total_rec['first_discovered_time'] - direct_rec['first_discovered_time']
            
            # 检查发现者冲突
            try:
                direct_discoverers = set(json.loads(direct_rec['discoverers']))
                total_discoverers = set(json.loads(total_rec['discoverers']))
                
                if direct_discoverers != total_discoverers:
                    conflict_result['conflict_type'] = 'discoverer_conflict'
                    conflict_result['resolution_action'] = 'merge_favor_total'
                    conflict_result['details']['direct_discoverers'] = list(direct_discoverers)
                    conflict_result['details']['total_discoverers'] = list(total_discoverers)
                    conflict_result['details']['unique_to_direct'] = list(direct_discoverers - total_discoverers)
                    conflict_result['details']['unique_to_total'] = list(total_discoverers - direct_discoverers)
            
            except (json.JSONDecodeError, TypeError):
                conflict_result['conflict_type'] = 'discoverer_format_error'
                conflict_result['resolution_action'] = 'manual_review'
            
            # 如果没有发现冲突，标记为成功
            if not conflict_result['conflict_type']:
                conflict_result['success'] = True
                conflict_result['resolution_action'] = 'no_conflict'
            
        except Exception as e:
            conflict_result['conflict_type'] = 'resolution_error'
            conflict_result['details']['error'] = str(e)
            logger.error(f"❌ 冲突解决失败: {str(e)}")
        
        return conflict_result
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """
        获取同步统计信息
        
        Returns:
            同步统计数据
        """
        stats = {
            'direct_library': {},
            'total_library': {},
            'sync_status': {},
            'performance_metrics': {}
        }
        
        try:
            # 直接经验库统计
            direct_stats = self.db_managers['direct_experiences'].execute_query("""
                SELECT 
                    COUNT(*) as total_experiences,
                    SUM(occurrence_count) as total_occurrences,
                    SUM(success_count) as total_successes,
                    AVG(avg_success_rate) as avg_success_rate,
                    COUNT(DISTINCT first_discovered_by) as unique_discoverers,
                    MIN(first_discovered_time) as earliest_discovery,
                    MAX(last_seen_time) as latest_activity
                FROM direct_experiences
            """)[0]
            
            stats['direct_library'] = dict(direct_stats)
            
            # 总经验库统计
            total_stats = self.db_managers['total_experiences'].execute_query("""
                SELECT 
                    COUNT(*) as total_experiences,
                    SUM(occurrence_count) as total_occurrences,
                    SUM(success_count) as total_successes,
                    AVG(avg_success_rate) as avg_success_rate,
                    AVG(confidence) as avg_confidence,
                    COUNT(DISTINCT first_discovered_by) as unique_discoverers,
                    MIN(first_discovered_time) as earliest_discovery,
                    MAX(last_seen_time) as latest_activity
                FROM total_experiences
            """)[0]
            
            stats['total_library'] = dict(total_stats)
            
            # 同步状态分析
            # 检查有多少直接库记录还未在总库中
            try:
                unsynced_count = self.db_managers['direct_experiences'].execute_query("""
                    SELECT COUNT(*) as count
                    FROM direct_experiences d
                    WHERE d.content_hash NOT IN (
                        SELECT content_hash FROM total_experiences
                    )
                """)[0]['count']
            except Exception:
                # 如果跨库查询失败，使用简单方法
                direct_hashes = set(row['content_hash'] for row in self.db_managers['direct_experiences'].execute_query(
                    "SELECT content_hash FROM direct_experiences"
                ))
                total_hashes = set(row['content_hash'] for row in self.db_managers['total_experiences'].execute_query(
                    "SELECT content_hash FROM total_experiences"
                ))
                unsynced_count = len(direct_hashes - total_hashes)
            
            stats['sync_status'] = {
                'unsynced_experiences': unsynced_count,
                'sync_coverage': 1.0 - (unsynced_count / max(stats['direct_library']['total_experiences'], 1)),
                'needs_sync': unsynced_count > 0
            }
            
            # 性能指标
            stats['performance_metrics'] = {
                'direct_to_total_ratio': stats['direct_library']['total_experiences'] / max(stats['total_library']['total_experiences'], 1),
                'occurrence_efficiency': stats['total_library']['total_occurrences'] / max(stats['direct_library']['total_occurrences'], 1),
                'discovery_consolidation': stats['total_library']['unique_discoverers'] / max(stats['direct_library']['unique_discoverers'], 1)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取同步统计失败: {str(e)}")
            stats['error'] = str(e)
        
        return stats

    # ==================== BPM怒放模块 ====================
    
    def generate_candidate_rules_from_experiences(self, min_support: int = 3, min_confidence: float = 0.6) -> Dict[str, Any]:
        """
        从总经验库生成候选规律
        
        Args:
            min_support: 最小支持度（经验出现次数）
            min_confidence: 最小置信度
            
        Returns:
            规律生成结果
        """
        generation_result = {
            'success': False,
            'cn1_rules_generated': 0,
            'cn2_rules_generated': 0,
            'total_rules_generated': 0,
            'processing_time': 0.0,
            'rule_details': [],
            'statistics': {}
        }
        
        start_time = time.time()
        
        try:
            # 获取高质量经验数据
            high_quality_experiences = self.db_managers['total_experiences'].execute_query("""
                SELECT * FROM total_experiences 
                WHERE occurrence_count >= ? AND confidence >= ?
                ORDER BY occurrence_count DESC, avg_success_rate DESC
            """, (min_support, min_confidence))
            
            logger.info(f"🔍 找到 {len(high_quality_experiences)} 条高质量经验用于规律生成")
            
            # 生成CN1规律（单条件预测）
            cn1_rules = self._generate_cn1_rules(high_quality_experiences, min_support, min_confidence)
            generation_result['cn1_rules_generated'] = len(cn1_rules)
            
            # 生成CN2规律（多条件预测）
            cn2_rules = self._generate_cn2_rules(high_quality_experiences, min_support, min_confidence)
            generation_result['cn2_rules_generated'] = len(cn2_rules)
            
            # 合并所有规律
            all_rules = cn1_rules + cn2_rules
            generation_result['total_rules_generated'] = len(all_rules)
            generation_result['rule_details'] = all_rules
            
            # 计算统计信息
            generation_result['statistics'] = self._calculate_rule_generation_stats(all_rules, high_quality_experiences)
            
            generation_result['success'] = True
            generation_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 规律生成完成: CN1={len(cn1_rules)}, CN2={len(cn2_rules)}, 总计={len(all_rules)}")
            
        except Exception as e:
            generation_result['error'] = str(e)
            logger.error(f"❌ 规律生成失败: {str(e)}")
        
        return generation_result
    
    def _generate_cn1_rules(self, experiences: List, min_support: int, min_confidence: float) -> List[Dict]:
        """
        生成CN1规律（单条件预测）
        
        Args:
            experiences: 经验数据列表
            min_support: 最小支持度
            min_confidence: 最小置信度
            
        Returns:
            CN1规律列表
        """
        cn1_rules = []
        
        # 定义可能的条件字段和预测字段
        condition_fields = ['environment', 'object', 'characteristics', 'action', 'tools']
        prediction_fields = ['result', 'success']
        
        # 为每个条件字段生成规律
        for condition_field in condition_fields:
            # 统计条件值的分布
            condition_stats = {}
            
            for exp in experiences:
                condition_value = exp[condition_field]
                if condition_value not in condition_stats:
                    condition_stats[condition_value] = {
                        'total_count': 0,
                        'success_count': 0,
                        'results': {},
                        'experiences': []
                    }
                
                stats = condition_stats[condition_value]
                stats['total_count'] += exp['occurrence_count']
                stats['success_count'] += exp['success_count']
                stats['experiences'].append(exp)
                
                # 统计结果分布
                result = exp['result']
                if result not in stats['results']:
                    stats['results'][result] = {'count': 0, 'success_rate': 0.0}
                stats['results'][result]['count'] += exp['occurrence_count']
                stats['results'][result]['success_rate'] = exp['avg_success_rate']
            
            # 为每个条件值生成规律
            for condition_value, stats in condition_stats.items():
                if stats['total_count'] >= min_support:
                    # 生成成功率预测规律
                    success_rate = stats['success_count'] / stats['total_count'] if stats['total_count'] > 0 else 0.0
                    
                    if success_rate >= min_confidence or success_rate <= (1 - min_confidence):
                        cn1_rule = self._create_cn1_rule(
                            condition_field, condition_value, 'success', success_rate >= 0.5,
                            success_rate, stats['total_count'], stats['experiences']
                        )
                        cn1_rules.append(cn1_rule)
                    
                    # 生成最可能结果预测规律
                    if stats['results']:
                        most_common_result = max(stats['results'].items(), key=lambda x: x[1]['count'])
                        result_name, result_stats = most_common_result
                        result_confidence = result_stats['count'] / stats['total_count']
                        
                        if result_confidence >= min_confidence:
                            cn1_rule = self._create_cn1_rule(
                                condition_field, condition_value, 'result', result_name,
                                result_confidence, stats['total_count'], stats['experiences']
                            )
                            cn1_rules.append(cn1_rule)
        
        return cn1_rules
    
    def _generate_cn2_rules(self, experiences: List, min_support: int, min_confidence: float) -> List[Dict]:
        """
        生成CN2规律（多条件预测）
        
        Args:
            experiences: 经验数据列表
            min_support: 最小支持度
            min_confidence: 最小置信度
            
        Returns:
            CN2规律列表
        """
        cn2_rules = []
        
        # 定义条件字段组合
        condition_combinations = [
            ['environment', 'object'],
            ['environment', 'action'],
            ['object', 'action'],
            ['action', 'tools'],
            ['environment', 'object', 'action'],
            ['object', 'characteristics', 'action'],
            ['environment', 'action', 'tools']
        ]
        
        prediction_fields = ['result', 'success']
        
        # 为每个条件组合生成规律
        for condition_fields in condition_combinations:
            # 统计条件组合的分布
            combination_stats = {}
            
            for exp in experiences:
                # 创建条件组合键
                condition_key = tuple(exp[field] for field in condition_fields)
                
                if condition_key not in combination_stats:
                    combination_stats[condition_key] = {
                        'total_count': 0,
                        'success_count': 0,
                        'results': {},
                        'experiences': []
                    }
                
                stats = combination_stats[condition_key]
                stats['total_count'] += exp['occurrence_count']
                stats['success_count'] += exp['success_count']
                stats['experiences'].append(exp)
                
                # 统计结果分布
                result = exp['result']
                if result not in stats['results']:
                    stats['results'][result] = {'count': 0, 'success_rate': 0.0}
                stats['results'][result]['count'] += exp['occurrence_count']
                stats['results'][result]['success_rate'] = exp['avg_success_rate']
            
            # 为每个条件组合生成规律
            for condition_values, stats in combination_stats.items():
                if stats['total_count'] >= min_support:
                    # 创建条件字典
                    conditions = dict(zip(condition_fields, condition_values))
                    
                    # 生成成功率预测规律
                    success_rate = stats['success_count'] / stats['total_count'] if stats['total_count'] > 0 else 0.0
                    
                    if success_rate >= min_confidence or success_rate <= (1 - min_confidence):
                        cn2_rule = self._create_cn2_rule(
                            conditions, 'success', success_rate >= 0.5,
                            success_rate, stats['total_count'], stats['experiences']
                        )
                        cn2_rules.append(cn2_rule)
                    
                    # 生成最可能结果预测规律
                    if stats['results']:
                        most_common_result = max(stats['results'].items(), key=lambda x: x[1]['count'])
                        result_name, result_stats = most_common_result
                        result_confidence = result_stats['count'] / stats['total_count']
                        
                        if result_confidence >= min_confidence:
                            cn2_rule = self._create_cn2_rule(
                                conditions, 'result', result_name,
                                result_confidence, stats['total_count'], stats['experiences']
                            )
                            cn2_rules.append(cn2_rule)
        
        return cn2_rules
    
    def _create_cn1_rule(self, condition_field: str, condition_value: str, prediction_field: str, 
                        prediction_value, confidence: float, support_count: int, experiences: List) -> Dict:
        """
        创建CN1规律
        
        Args:
            condition_field: 条件字段名
            condition_value: 条件值
            prediction_field: 预测字段名
            prediction_value: 预测值
            confidence: 置信度
            support_count: 支持度
            experiences: 支持该规律的经验列表
            
        Returns:
            CN1规律字典
        """
        conditions = {condition_field: condition_value}
        predictions = {prediction_field: prediction_value}
        
        rule_id = f"CN1_{hashlib.md5(f'{conditions}_{predictions}'.encode()).hexdigest()[:12]}"
        
        # 计算额外统计信息
        discoverers = set()
        first_discovery_time = float('inf')
        last_seen_time = 0.0
        
        for exp in experiences:
            try:
                exp_discoverers = json.loads(exp['discoverers'])
                discoverers.update(exp_discoverers)
            except (json.JSONDecodeError, TypeError):
                discoverers.add(exp['first_discovered_by'])
            
            first_discovery_time = min(first_discovery_time, exp['first_discovered_time'])
            last_seen_time = max(last_seen_time, exp['last_seen_time'])
        
        return {
            'rule_id': rule_id,
            'rule_type': 'CN1',
            'conditions': conditions,
            'predictions': predictions,
            'confidence': confidence,
            'support_count': support_count,
            'contradiction_count': 0,  # 初始为0，后续验证时更新
            'created_time': time.time(),
            'creator_id': 'BPM_SYSTEM',
            'validation_status': 'pending',
            'discoverers': list(discoverers),
            'first_discovered_time': first_discovery_time if first_discovery_time != float('inf') else time.time(),
            'last_seen_time': last_seen_time,
            'supporting_experiences': len(experiences),
            'content_hash': hashlib.md5(f'{conditions}_{predictions}'.encode()).hexdigest()
        }
    
    def _create_cn2_rule(self, conditions: Dict, prediction_field: str, prediction_value, 
                        confidence: float, support_count: int, experiences: List) -> Dict:
        """
        创建CN2规律
        
        Args:
            conditions: 条件字典
            prediction_field: 预测字段名
            prediction_value: 预测值
            confidence: 置信度
            support_count: 支持度
            experiences: 支持该规律的经验列表
            
        Returns:
            CN2规律字典
        """
        predictions = {prediction_field: prediction_value}
        
        rule_id = f"CN2_{hashlib.md5(f'{conditions}_{predictions}'.encode()).hexdigest()[:12]}"
        
        # 计算额外统计信息
        discoverers = set()
        first_discovery_time = float('inf')
        last_seen_time = 0.0
        
        for exp in experiences:
            try:
                exp_discoverers = json.loads(exp['discoverers'])
                discoverers.update(exp_discoverers)
            except (json.JSONDecodeError, TypeError):
                discoverers.add(exp['first_discovered_by'])
            
            first_discovery_time = min(first_discovery_time, exp['first_discovered_time'])
            last_seen_time = max(last_seen_time, exp['last_seen_time'])
        
        return {
            'rule_id': rule_id,
            'rule_type': 'CN2',
            'conditions': conditions,
            'predictions': predictions,
            'confidence': confidence,
            'support_count': support_count,
            'contradiction_count': 0,  # 初始为0，后续验证时更新
            'created_time': time.time(),
            'creator_id': 'BPM_SYSTEM',
            'validation_status': 'pending',
            'discoverers': list(discoverers),
            'first_discovered_time': first_discovery_time if first_discovery_time != float('inf') else time.time(),
            'last_seen_time': last_seen_time,
            'supporting_experiences': len(experiences),
            'content_hash': hashlib.md5(f'{conditions}_{predictions}'.encode()).hexdigest()
        }
    
    def _calculate_rule_generation_stats(self, rules: List[Dict], experiences: List) -> Dict:
        """
        计算规律生成统计信息
        
        Args:
            rules: 生成的规律列表
            experiences: 原始经验数据
            
        Returns:
            统计信息字典
        """
        stats = {
            'total_experiences_processed': len(experiences),
            'total_rules_generated': len(rules),
            'cn1_rules': len([r for r in rules if r['rule_type'] == 'CN1']),
            'cn2_rules': len([r for r in rules if r['rule_type'] == 'CN2']),
            'avg_confidence': 0.0,
            'avg_support': 0.0,
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'support_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'prediction_types': {'success': 0, 'result': 0},
            'unique_discoverers': set(),
            'coverage_rate': 0.0
        }
        
        if not rules:
            return stats
        
        # 计算平均值
        total_confidence = sum(rule['confidence'] for rule in rules)
        total_support = sum(rule['support_count'] for rule in rules)
        
        stats['avg_confidence'] = total_confidence / len(rules)
        stats['avg_support'] = total_support / len(rules)
        
        # 计算分布
        for rule in rules:
            # 置信度分布
            if rule['confidence'] >= 0.8:
                stats['confidence_distribution']['high'] += 1
            elif rule['confidence'] >= 0.6:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
            
            # 支持度分布
            if rule['support_count'] >= 10:
                stats['support_distribution']['high'] += 1
            elif rule['support_count'] >= 5:
                stats['support_distribution']['medium'] += 1
            else:
                stats['support_distribution']['low'] += 1
            
            # 预测类型统计
            for pred_field in rule['predictions'].keys():
                if pred_field in stats['prediction_types']:
                    stats['prediction_types'][pred_field] += 1
            
            # 收集发现者
            stats['unique_discoverers'].update(rule['discoverers'])
        
        # 转换set为数量
        stats['unique_discoverers'] = len(stats['unique_discoverers'])
        
        # 计算覆盖率（有多少经验被规律覆盖）
        covered_experiences = set()
        for rule in rules:
            covered_experiences.add(rule['content_hash'])
        
        stats['coverage_rate'] = len(covered_experiences) / max(len(experiences), 1)
        
        return stats
    
    def add_rules_to_direct_library(self, rules: List[Dict]) -> Dict[str, Any]:
        """添加规律列表到直接规律库"""
        if not rules:
            return {
                'success': False,
                'added_count': 0,
                'reason': 'empty_rules_list'
            }
        
        db_manager = self.db_managers['direct_rules']
        added_rules = []
        duplicate_rules = []
        error_rules = []
        
        for rule in rules:
            try:
                # 验证规律数据完整性
                required_fields = ['rule_id', 'rule_type', 'conditions', 'predictions', 'confidence']
                missing_fields = [field for field in required_fields if field not in rule]
                
                if missing_fields:
                    error_rules.append({
                        'rule': rule,
                        'error': f'missing_fields: {missing_fields}'
                    })
                    continue
                
                # 生成内容哈希
                content_hash = Rule(
                    rule_id=rule['rule_id'],
                    rule_type=rule['rule_type'], 
                    conditions=rule['conditions'],
                    predictions=rule['predictions'],
                    confidence=rule['confidence'],
                    support_count=rule.get('support_count', 0),
                    contradiction_count=rule.get('contradiction_count', 0),
                    created_time=time.time(),
                    creator_id=rule.get('creator_id', 'system')
                ).generate_hash()
                
                # 检查重复
                existing = db_manager.execute_query(
                    "SELECT rule_id FROM direct_rules WHERE content_hash = ?",
                    (content_hash,)
                )
                
                if existing:
                    duplicate_rules.append(rule['rule_id'])
                    continue
                
                # 插入规律
                db_manager.execute_update("""
                    INSERT INTO direct_rules (
                        rule_id, content_hash, rule_type, conditions, predictions, 
                        confidence, support_count, contradiction_count, validation_count,
                        created_time, creator_id, validation_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule['rule_id'],
                    content_hash,
                    rule['rule_type'],
                    json.dumps(rule['conditions']),
                    json.dumps(rule['predictions']),
                    rule['confidence'],
                    rule.get('support_count', 0),
                    rule.get('contradiction_count', 0),
                    rule.get('validation_count', 0),
                    time.time(),
                    rule.get('creator_id', 'system'),
                    rule.get('validation_status', 'pending')
                ))
                
                added_rules.append(rule['rule_id'])
                
            except Exception as e:
                error_rules.append({
                    'rule': rule.get('rule_id', 'unknown'),
                    'error': str(e)
                })
        
        # 更新缓存
        if added_rules:
            self._update_cache()
        
        result = {
            'success': len(added_rules) > 0,
            'added_count': len(added_rules),
            'duplicate_count': len(duplicate_rules),
            'error_count': len(error_rules),
            'added_rules': added_rules,
            'duplicate_rules': duplicate_rules,
            'error_rules': error_rules,
            'timestamp': time.time()
        }
        
        if len(added_rules) > 0:
            logger.info(f"✅ Successfully added {len(added_rules)} rules to direct rule library")
        if len(duplicate_rules) > 0:
            logger.info(f"⚠️ Skipped {len(duplicate_rules)} duplicate rules")
        if len(error_rules) > 0:
            logger.warning(f"❌ {len(error_rules)} rules failed to add")
        
        return result
    
    def add_rule(self, rule_type: str = None, conditions: Dict = None, predictions: Dict = None, 
                 confidence: float = 0.7, creator_id: str = "system", rule_dict: Dict = None, 
                 **kwargs) -> Dict[str, Any]:
        """
        添加单个规律到直接规律库
        
        支持两种调用方式：
        1. 传递字典: add_rule(rule_dict=rule_data)
        2. 传递参数: add_rule(rule_type="E-A-R", conditions={...}, predictions={...})
        """
        try:
            # 方式1：如果传递了rule_dict，使用字典方式
            if rule_dict:
                return self.add_rules_to_direct_library([rule_dict])
            
            # 方式2：从关键字参数构建规律字典
            if rule_type and conditions and predictions:
                import time
                rule_id = f"{rule_type}_{int(time.time() * 1000)}_{hash(str(conditions)) % 10000}"
                
                rule_data = {
                    'rule_id': rule_id,
                    'rule_type': rule_type,
                    'conditions': conditions,
                    'predictions': predictions,
                    'confidence': confidence,
                    'support_count': kwargs.get('support_count', 1),
                    'contradiction_count': kwargs.get('contradiction_count', 0),
                    'created_time': time.time(),
                    'creator_id': creator_id,
                    'validation_status': kwargs.get('validation_status', 'pending')
                }
                
                return self.add_rules_to_direct_library([rule_data])
            
            # 参数不足
            return {
                'success': False,
                'error': 'Missing required parameters: rule_type, conditions, predictions or rule_dict',
                'rules_added': 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add rule: {str(e)}',
                'rules_added': 0
            }
    
    def get_rule_generation_summary(self) -> Dict[str, Any]:
        """
        获取规律生成摘要信息
        
        Returns:
            规律生成摘要
        """
        summary = {
            'direct_rules_count': 0,
            'total_rules_count': 0,
            'rule_types': {'CN1': 0, 'CN2': 0},
            'validation_status': {'pending': 0, 'validated': 0, 'rejected': 0},
            'confidence_levels': {'high': 0, 'medium': 0, 'low': 0},
            'recent_activity': [],
            'top_rules': []
        }
        
        try:
            # 直接规律库统计
            direct_rules = self.db_managers['direct_rules'].execute_query(
                "SELECT * FROM direct_rules ORDER BY created_time DESC"
            )
            summary['direct_rules_count'] = len(direct_rules)
            
            # 总规律库统计
            total_rules = self.db_managers['total_rules'].execute_query(
                "SELECT * FROM total_rules ORDER BY created_time DESC"
            )
            summary['total_rules_count'] = len(total_rules)
            
            # 分析直接规律库
            for rule in direct_rules:
                # 规律类型统计
                rule_type = rule['rule_type']
                if rule_type in summary['rule_types']:
                    summary['rule_types'][rule_type] += 1
                
                # 验证状态统计
                status = rule['validation_status']
                if status in summary['validation_status']:
                    summary['validation_status'][status] += 1
                
                # 置信度等级统计
                confidence = rule['confidence']
                if confidence >= 0.8:
                    summary['confidence_levels']['high'] += 1
                elif confidence >= 0.6:
                    summary['confidence_levels']['medium'] += 1
                else:
                    summary['confidence_levels']['low'] += 1
            
            # 最近活动（最近10条）
            recent_rules = direct_rules[:10]
            for rule in recent_rules:
                summary['recent_activity'].append({
                    'rule_id': rule['rule_id'],
                    'rule_type': rule['rule_type'],
                    'confidence': rule['confidence'],
                    'support_count': rule['support_count'],
                    'created_time': rule['created_time'],
                    'status': rule['validation_status']
                })
            
            # 顶级规律（按置信度和支持度排序）
            top_rules = sorted(direct_rules, key=lambda x: (x['confidence'], x['support_count']), reverse=True)[:5]
            for rule in top_rules:
                summary['top_rules'].append({
                    'rule_id': rule['rule_id'],
                    'rule_type': rule['rule_type'],
                    'confidence': rule['confidence'],
                    'support_count': rule['support_count'],
                    'conditions': rule['conditions'],
                    'predictions': rule['predictions']
                })
        
        except Exception as e:
            summary['error'] = str(e)
            logger.error(f"❌ 获取规律摘要失败: {str(e)}")
        
        return summary

    # ==================== 规律验证模块 ====================
    
    def validate_rules_against_experience(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        使用新经验验证现有规律
        
        Args:
            experience: 新的EOCATR经验
            
        Returns:
            验证结果
        """
        validation_result = {
            'success': False,
            'experience_hash': None,
            'matched_rules': [],
            'validated_rules': 0,
            'contradicted_rules': 0,
            'updated_rules': 0,
            'validation_details': [],
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 验证经验
            exp_validation = self.validate_eocatr_experience(experience)
            if not exp_validation['is_valid']:
                validation_result['error'] = f"经验验证失败: {exp_validation['errors']}"
                return validation_result
            
            normalized_exp = exp_validation['normalized_experience']
            validation_result['experience_hash'] = normalized_exp.generate_hash()
            
            # 获取所有待验证的规律
            pending_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT * FROM direct_rules 
                WHERE validation_status = 'pending' OR validation_status = 'validated'
                ORDER BY confidence DESC, support_count DESC
            """)
            
            logger.info(f"🔍 开始验证 {len(pending_rules)} 条规律")
            
            # 逐一验证规律
            for rule in pending_rules:
                match_result = self._match_rule_with_experience(rule, normalized_exp)
                
                if match_result['is_match']:
                    validation_result['matched_rules'].append(rule['rule_id'])
                    
                    # 执行验证
                    verify_result = self._verify_rule_prediction(rule, normalized_exp, match_result)
                    
                    if verify_result['is_correct']:
                        validation_result['validated_rules'] += 1
                        self._update_rule_validation_success(rule, verify_result)
                    else:
                        validation_result['contradicted_rules'] += 1
                        self._update_rule_validation_failure(rule, verify_result)
                    
                    validation_result['updated_rules'] += 1
                    validation_result['validation_details'].append({
                        'rule_id': rule['rule_id'],
                        'rule_type': rule['rule_type'],
                        'is_match': True,
                        'is_correct': verify_result['is_correct'],
                        'prediction_field': verify_result['prediction_field'],
                        'expected_value': verify_result['expected_value'],
                        'actual_value': verify_result['actual_value'],
                        'confidence_before': rule['confidence'],
                        'confidence_after': verify_result.get('new_confidence', rule['confidence'])
                    })
            
            validation_result['success'] = True
            validation_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 规律验证完成: 匹配={len(validation_result['matched_rules'])}, 验证={validation_result['validated_rules']}, 矛盾={validation_result['contradicted_rules']}")
            
        except Exception as e:
            validation_result['error'] = str(e)
            logger.error(f"❌ 规律验证失败: {str(e)}")
        
        return validation_result
    
    def _match_rule_with_experience(self, rule: dict, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        检查规律是否与经验匹配
        
        Args:
            rule: 规律记录
            experience: 经验对象
            
        Returns:
            匹配结果
        """
        match_result = {
            'is_match': False,
            'matched_conditions': [],
            'match_score': 0.0,
            'total_conditions': 0
        }
        
        try:
            # 解析规律条件
            conditions = json.loads(rule['conditions'])
            match_result['total_conditions'] = len(conditions)
            
            matched_count = 0
            
            # 检查每个条件
            for field, expected_value in conditions.items():
                actual_value = getattr(experience, field, None)
                
                if actual_value is not None and str(actual_value).lower() == str(expected_value).lower():
                    matched_count += 1
                    match_result['matched_conditions'].append({
                        'field': field,
                        'expected': expected_value,
                        'actual': actual_value,
                        'match': True
                    })
                else:
                    match_result['matched_conditions'].append({
                        'field': field,
                        'expected': expected_value,
                        'actual': actual_value,
                        'match': False
                    })
            
            # 计算匹配分数
            match_result['match_score'] = matched_count / len(conditions) if conditions else 0.0
            match_result['is_match'] = match_result['match_score'] == 1.0  # 要求完全匹配
            
        except Exception as e:
            logger.error(f"❌ 规律匹配失败: {str(e)}")
        
        return match_result
    
    def _verify_rule_prediction(self, rule: dict, experience: EOCATRExperience, match_result: dict) -> Dict[str, Any]:
        """
        验证规律的预测是否正确
        
        Args:
            rule: 规律记录
            experience: 经验对象
            match_result: 匹配结果
            
        Returns:
            验证结果
        """
        verify_result = {
            'is_correct': False,
            'prediction_field': None,
            'expected_value': None,
            'actual_value': None,
            'confidence_impact': 0.0,
            'new_confidence': rule['confidence']
        }
        
        try:
            # 解析规律预测
            predictions = json.loads(rule['predictions'])
            
            # 检查每个预测
            correct_predictions = 0
            total_predictions = len(predictions)
            
            for field, expected_value in predictions.items():
                verify_result['prediction_field'] = field
                verify_result['expected_value'] = expected_value
                
                if field == 'success':
                    actual_value = experience.success
                    verify_result['actual_value'] = actual_value
                    
                    # 布尔值比较
                    if isinstance(expected_value, bool):
                        is_correct = actual_value == expected_value
                    else:
                        is_correct = actual_value == (str(expected_value).lower() == 'true')
                    
                elif field == 'result':
                    actual_value = experience.result
                    verify_result['actual_value'] = actual_value
                    
                    # 字符串比较（可以是部分匹配）
                    is_correct = (str(expected_value).lower() in str(actual_value).lower() or 
                                str(actual_value).lower() in str(expected_value).lower())
                
                else:
                    # 其他字段的直接比较
                    actual_value = getattr(experience, field, None)
                    verify_result['actual_value'] = actual_value
                    is_correct = str(actual_value).lower() == str(expected_value).lower()
                
                if is_correct:
                    correct_predictions += 1
            
            # 计算验证结果
            verify_result['is_correct'] = correct_predictions == total_predictions
            
            # 计算置信度影响
            current_confidence = rule['confidence']
            support_count = rule['support_count']
            
            if verify_result['is_correct']:
                # 验证成功，轻微提升置信度
                confidence_boost = 0.05 * (1 - current_confidence)  # 越接近1提升越小
                verify_result['new_confidence'] = min(0.99, current_confidence + confidence_boost)
                verify_result['confidence_impact'] = confidence_boost
            else:
                # 验证失败，降低置信度
                confidence_penalty = 0.1 * current_confidence  # 按比例降低
                verify_result['new_confidence'] = max(0.01, current_confidence - confidence_penalty)
                verify_result['confidence_impact'] = -confidence_penalty
            
        except Exception as e:
            logger.error(f"❌ 规律预测验证失败: {str(e)}")
        
        return verify_result
    
    def _update_rule_validation_success(self, rule: dict, verify_result: dict):
        """
        更新规律验证成功的统计
        
        Args:
            rule: 规律记录
            verify_result: 验证结果
        """
        try:
            self.db_managers['direct_rules'].execute_update("""
                UPDATE direct_rules 
                SET support_count = support_count + 1,
                    confidence = ?,
                    last_validated = ?,
                    validation_count = validation_count + 1,
                    validation_status = CASE 
                        WHEN validation_count + 1 >= 3 AND confidence >= 0.7 THEN 'validated'
                        ELSE validation_status
                    END
                WHERE rule_id = ?
            """, (
                verify_result['new_confidence'],
                time.time(),
                rule['rule_id']
            ))
            
            logger.debug(f"✅ 规律 {rule['rule_id']} 验证成功更新")
            
        except Exception as e:
            logger.error(f"❌ 更新规律验证成功失败: {str(e)}")
    
    def _update_rule_validation_failure(self, rule: dict, verify_result: dict):
        """
        更新规律验证失败的统计
        
        Args:
            rule: 规律记录
            verify_result: 验证结果
        """
        try:
            self.db_managers['direct_rules'].execute_update("""
                UPDATE direct_rules 
                SET contradiction_count = contradiction_count + 1,
                    confidence = ?,
                    last_validated = ?,
                    validation_count = validation_count + 1,
                    validation_status = CASE 
                        WHEN contradiction_count + 1 >= 3 OR confidence < 0.3 THEN 'rejected'
                        ELSE validation_status
                    END
                WHERE rule_id = ?
            """, (
                verify_result['new_confidence'],
                time.time(),
                rule['rule_id']
            ))
            
            logger.debug(f"⚠️ 规律 {rule['rule_id']} 验证失败更新")
            
        except Exception as e:
            logger.error(f"❌ 更新规律验证失败失败: {str(e)}")
    
    def batch_validate_rules(self, experiences: List[EOCATRExperience]) -> Dict[str, Any]:
        """
        批量验证规律
        
        Args:
            experiences: 经验列表
            
        Returns:
            批量验证结果
        """
        batch_result = {
            'success': False,
            'total_experiences': len(experiences),
            'processed_experiences': 0,
            'total_validations': 0,
            'total_contradictions': 0,
            'updated_rules': set(),
            'validation_summary': {},
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            for i, experience in enumerate(experiences):
                validation_result = self.validate_rules_against_experience(experience)
                
                if validation_result['success']:
                    batch_result['processed_experiences'] += 1
                    batch_result['total_validations'] += validation_result['validated_rules']
                    batch_result['total_contradictions'] += validation_result['contradicted_rules']
                    batch_result['updated_rules'].update(validation_result['matched_rules'])
                
                # 每处理10个经验输出一次进度
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 批量验证进度: {i + 1}/{len(experiences)}")
            
            # 生成验证摘要
            batch_result['validation_summary'] = self._generate_validation_summary()
            batch_result['updated_rules'] = list(batch_result['updated_rules'])
            batch_result['success'] = True
            batch_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 批量验证完成: 处理={batch_result['processed_experiences']}, 验证={batch_result['total_validations']}, 矛盾={batch_result['total_contradictions']}")
            
        except Exception as e:
            batch_result['error'] = str(e)
            logger.error(f"❌ 批量验证失败: {str(e)}")
        
        return batch_result
    
    def _generate_validation_summary(self) -> Dict[str, Any]:
        """
        生成验证摘要
        
        Returns:
            验证摘要
        """
        summary = {
            'rule_status_distribution': {},
            'confidence_distribution': {},
            'validation_metrics': {},
            'top_validated_rules': [],
            'problematic_rules': []
        }
        
        try:
            # 规律状态分布
            status_stats = self.db_managers['direct_rules'].execute_query("""
                SELECT validation_status, COUNT(*) as count
                FROM direct_rules
                GROUP BY validation_status
            """)
            
            for stat in status_stats:
                summary['rule_status_distribution'][stat['validation_status']] = stat['count']
            
            # 置信度分布
            confidence_stats = self.db_managers['direct_rules'].execute_query("""
                SELECT 
                    CASE 
                        WHEN confidence >= 0.8 THEN 'high'
                        WHEN confidence >= 0.6 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level,
                    COUNT(*) as count
                FROM direct_rules
                GROUP BY confidence_level
            """)
            
            for stat in confidence_stats:
                summary['confidence_distribution'][stat['confidence_level']] = stat['count']
            
            # 验证指标
            metrics = self.db_managers['direct_rules'].execute_query("""
                SELECT 
                    AVG(confidence) as avg_confidence,
                    AVG(support_count) as avg_support,
                    AVG(contradiction_count) as avg_contradictions,
                    AVG(validation_count) as avg_validations,
                    COUNT(*) as total_rules
                FROM direct_rules
            """)[0]
            
            summary['validation_metrics'] = dict(metrics)
            
            # 顶级验证规律
            top_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT rule_id, rule_type, confidence, support_count, contradiction_count, validation_status
                FROM direct_rules
                WHERE validation_status = 'validated'
                ORDER BY confidence DESC, support_count DESC
                LIMIT 5
            """)
            
            summary['top_validated_rules'] = [dict(rule) for rule in top_rules]
            
            # 问题规律
            problem_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT rule_id, rule_type, confidence, support_count, contradiction_count, validation_status
                FROM direct_rules
                WHERE validation_status = 'rejected' OR (contradiction_count > support_count AND contradiction_count > 0)
                ORDER BY contradiction_count DESC, confidence ASC
                LIMIT 5
            """)
            
            summary['problematic_rules'] = [dict(rule) for rule in problem_rules]
            
        except Exception as e:
            summary['error'] = str(e)
            logger.error(f"❌ 生成验证摘要失败: {str(e)}")
        
        return summary
    
    def get_rule_validation_report(self, rule_id: str = None) -> Dict[str, Any]:
        """
        获取规律验证报告
        
        Args:
            rule_id: 特定规律ID，如果为None则返回全局报告
            
        Returns:
            验证报告
        """
        report = {
            'success': False,
            'report_type': 'specific' if rule_id else 'global',
            'rule_details': None,
            'validation_history': [],
            'performance_metrics': {},
            'recommendations': []
        }
        
        try:
            if rule_id:
                # 特定规律报告
                rule_details = self.db_managers['direct_rules'].execute_query(
                    "SELECT * FROM direct_rules WHERE rule_id = ?", (rule_id,)
                )
                
                if not rule_details:
                    report['error'] = f"规律 {rule_id} 不存在"
                    return report
                
                rule = rule_details[0]
                report['rule_details'] = dict(rule)
                
                # 计算性能指标
                total_tests = rule['support_count'] + rule['contradiction_count']
                success_rate = rule['support_count'] / total_tests if total_tests > 0 else 0.0
                
                report['performance_metrics'] = {
                    'success_rate': success_rate,
                    'total_tests': total_tests,
                    'support_count': rule['support_count'],
                    'contradiction_count': rule['contradiction_count'],
                    'current_confidence': rule['confidence'],
                    'validation_count': rule['validation_count'],
                    'status': rule['validation_status']
                }
                
                # 生成建议
                report['recommendations'] = self._generate_rule_recommendations(rule)
                
            else:
                # 全局报告
                report['validation_summary'] = self._generate_validation_summary()
                
                # 全局性能指标
                global_metrics = self.db_managers['direct_rules'].execute_query("""
                    SELECT 
                        COUNT(*) as total_rules,
                        AVG(confidence) as avg_confidence,
                        SUM(support_count) as total_supports,
                        SUM(contradiction_count) as total_contradictions,
                        COUNT(CASE WHEN validation_status = 'validated' THEN 1 END) as validated_rules,
                        COUNT(CASE WHEN validation_status = 'rejected' THEN 1 END) as rejected_rules,
                        COUNT(CASE WHEN validation_status = 'pending' THEN 1 END) as pending_rules
                    FROM direct_rules
                """)[0]
                
                report['performance_metrics'] = dict(global_metrics)
                
                # 计算全局成功率
                total_tests = global_metrics['total_supports'] + global_metrics['total_contradictions']
                global_success_rate = global_metrics['total_supports'] / total_tests if total_tests > 0 else 0.0
                report['performance_metrics']['global_success_rate'] = global_success_rate
                
                # 生成全局建议
                report['recommendations'] = self._generate_global_recommendations(global_metrics)
            
            report['success'] = True
            
        except Exception as e:
            report['error'] = str(e)
            logger.error(f"❌ 获取验证报告失败: {str(e)}")
        
        return report
    
    def _generate_rule_recommendations(self, rule: dict) -> List[str]:
        """
        为特定规律生成建议
        
        Args:
            rule: 规律记录
            
        Returns:
            建议列表
        """
        recommendations = []
        
        confidence = rule['confidence']
        support_count = rule['support_count']
        contradiction_count = rule['contradiction_count']
        validation_count = rule['validation_count']
        status = rule['validation_status']
        
        # 基于置信度的建议
        if confidence < 0.3:
            recommendations.append("⚠️ 置信度过低，建议考虑删除此规律")
        elif confidence < 0.6:
            recommendations.append("📊 置信度较低，需要更多验证数据")
        elif confidence > 0.9:
            recommendations.append("✅ 置信度很高，可以优先使用")
        
        # 基于支持度的建议
        if support_count < 3:
            recommendations.append("📈 支持度不足，需要更多正面验证")
        elif support_count > 10:
            recommendations.append("🎯 支持度充足，规律较为可靠")
        
        # 基于矛盾的建议
        if contradiction_count > support_count:
            recommendations.append("❌ 矛盾过多，建议重新评估规律条件")
        elif contradiction_count == 0 and validation_count > 5:
            recommendations.append("🌟 无矛盾且验证充分，规律质量优秀")
        
        # 基于状态的建议
        if status == 'pending' and validation_count < 3:
            recommendations.append("⏳ 需要更多验证才能确定规律有效性")
        elif status == 'rejected':
            recommendations.append("🗑️ 规律已被拒绝，建议从系统中移除")
        elif status == 'validated':
            recommendations.append("✅ 规律已验证，可以安全使用")
        
        return recommendations
    
    def _generate_global_recommendations(self, metrics: dict) -> List[str]:
        """
        生成全局建议
        
        Args:
            metrics: 全局指标
            
        Returns:
            建议列表
        """
        recommendations = []
        
        total_rules = metrics.get('total_rules', 0)
        avg_confidence = metrics.get('avg_confidence', 0.0)
        global_success_rate = metrics.get('global_success_rate', 0.0)
        validated_rules = metrics.get('validated_rules', 0)
        rejected_rules = metrics.get('rejected_rules', 0)
        pending_rules = metrics.get('pending_rules', 0)
        
        # 基于规律数量的建议
        if total_rules < 10:
            recommendations.append("📊 规律数量较少，建议增加更多经验数据以生成规律")
        elif total_rules > 1000:
            recommendations.append("🗂️ 规律数量较多，建议定期清理低质量规律")
        
        # 基于平均置信度的建议
        if avg_confidence < 0.5:
            recommendations.append("⚠️ 平均置信度偏低，建议提高规律生成阈值")
        elif avg_confidence > 0.8:
            recommendations.append("✅ 平均置信度良好，规律质量较高")
        
        # 基于成功率的建议
        if global_success_rate < 0.6:
            recommendations.append("📉 全局成功率偏低，建议优化规律生成算法")
        elif global_success_rate > 0.8:
            recommendations.append("🎯 全局成功率良好，验证机制有效")
        
        # 基于验证状态的建议
        pending_ratio = pending_rules / total_rules if total_rules > 0 else 0
        if pending_ratio > 0.7:
            recommendations.append("⏳ 待验证规律过多，建议增加验证频率")
        
        rejected_ratio = rejected_rules / total_rules if total_rules > 0 else 0
        if rejected_ratio > 0.3:
            recommendations.append("🗑️ 拒绝规律过多，建议优化规律生成条件")
        
        validated_ratio = validated_rules / total_rules if total_rules > 0 else 0
        if validated_ratio > 0.5:
            recommendations.append("✅ 验证规律比例良好，系统运行稳定")
        
        return recommendations

    # ==================== 规律同步模块 ====================
    
    def sync_rule_to_total_library(self, rule_hash: str) -> Dict[str, Any]:
        """
        将单个规律从直接库同步到总库
        
        Args:
            rule_hash: 规律内容哈希
            
        Returns:
            同步结果
        """
        sync_result = {
            'success': False,
            'rule_hash': rule_hash,
            'action': None,  # 'created', 'updated', 'merged'
            'rule_id': None,
            'sync_details': {},
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 从直接库获取规律
            direct_rule = self.db_managers['direct_rules'].execute_query(
                "SELECT * FROM direct_rules WHERE content_hash = ?", (rule_hash,)
            )
            
            if not direct_rule:
                sync_result['error'] = f"直接库中未找到规律 {rule_hash}"
                return sync_result
            
            rule = direct_rule[0]
            sync_result['rule_id'] = rule['rule_id']
            
            # 检查总库中是否存在相同规律
            existing_rule = self.db_managers['total_rules'].execute_query(
                "SELECT * FROM total_rules WHERE content_hash = ?", (rule_hash,)
            )
            
            if existing_rule:
                # 规律已存在，执行合并更新
                merge_result = self._merge_rule_to_total(rule, existing_rule[0])
                sync_result['action'] = 'merged'
                sync_result['sync_details'] = merge_result
            else:
                # 规律不存在，创建新记录
                create_result = self._create_rule_in_total(rule)
                sync_result['action'] = 'created'
                sync_result['sync_details'] = create_result
            
            # 更新直接库的同步状态
            self.db_managers['direct_rules'].execute_update(
                "UPDATE direct_rules SET synced_to_total = 1, last_sync_time = ? WHERE rule_id = ?",
                (time.time(), rule['rule_id'])
            )
            
            sync_result['success'] = True
            sync_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 规律同步成功: {rule['rule_id'][:8]}... → {sync_result['action']}")
            
        except Exception as e:
            sync_result['error'] = str(e)
            logger.error(f"❌ 规律同步失败: {str(e)}")
        
        return sync_result
    
    def _merge_rule_to_total(self, direct_rule: dict, total_rule: dict) -> Dict[str, Any]:
        """
        合并规律到总库
        
        Args:
            direct_rule: 直接库规律
            total_rule: 总库规律
            
        Returns:
            合并结果
        """
        merge_result = {
            'merged_fields': [],
            'statistics_updated': False,
            'discoverers_merged': False
        }
        
        try:
            # 确保规律对象是字典格式
            if hasattr(direct_rule, 'keys'):
                direct_dict = dict(direct_rule)
            else:
                direct_dict = direct_rule
                
            if hasattr(total_rule, 'keys'):
                total_dict = dict(total_rule)
            else:
                total_dict = total_rule
            
            # 合并统计数据
            new_support_count = total_dict['support_count'] + direct_dict['support_count']
            new_contradiction_count = total_dict['contradiction_count'] + direct_dict['contradiction_count']
            new_validation_count = total_dict['validation_count'] + direct_dict['validation_count']
            
            # 计算新的置信度（加权平均）
            total_tests_old = total_dict['support_count'] + total_dict['contradiction_count']
            total_tests_new = direct_dict['support_count'] + direct_dict['contradiction_count']
            total_tests_combined = total_tests_old + total_tests_new
            
            if total_tests_combined > 0:
                # 基于测试次数的加权平均
                weight_old = total_tests_old / total_tests_combined
                weight_new = total_tests_new / total_tests_combined
                new_confidence = (total_dict['confidence'] * weight_old + 
                                direct_dict['confidence'] * weight_new)
            else:
                # 如果没有测试数据，使用简单平均
                new_confidence = (total_dict['confidence'] + direct_dict['confidence']) / 2
            
            # 合并发现者列表
            total_discoverers = set(json.loads(total_dict.get('discoverers', '[]')))
            direct_discoverers = {direct_dict['creator_id']}
            merged_discoverers = list(total_discoverers.union(direct_discoverers))
            
            # 确定验证状态（取更严格的状态）
            status_priority = {'rejected': 0, 'pending': 1, 'validated': 2}
            current_status = total_dict['validation_status']
            new_status = direct_dict['validation_status']
            
            if status_priority.get(new_status, 1) < status_priority.get(current_status, 1):
                final_status = new_status
            else:
                final_status = current_status
            
            # 更新总库记录
            self.db_managers['total_rules'].execute_update("""
                UPDATE total_rules 
                SET support_count = ?,
                    contradiction_count = ?,
                    validation_count = ?,
                    confidence = ?,
                    discoverers = ?,
                    validation_status = ?,
                    occurrence_count = occurrence_count + 1,
                    last_updated = ?,
                    last_validated = CASE 
                        WHEN ? > last_validated THEN ? 
                        ELSE last_validated 
                    END
                WHERE rule_id = ?
            """, (
                new_support_count,
                new_contradiction_count,
                new_validation_count,
                new_confidence,
                json.dumps(merged_discoverers),
                final_status,
                time.time(),
                direct_dict.get('last_validated', 0),
                direct_dict.get('last_validated', 0),
                total_dict['rule_id']
            ))
            
            merge_result['merged_fields'] = [
                'support_count', 'contradiction_count', 'validation_count',
                'confidence', 'discoverers', 'validation_status'
            ]
            merge_result['statistics_updated'] = True
            merge_result['discoverers_merged'] = len(merged_discoverers) > len(total_discoverers)
            
            logger.debug(f"🔄 规律合并完成: {total_dict['rule_id'][:8]}...")
            
        except Exception as e:
            merge_result['error'] = str(e)
            logger.error(f"❌ 规律合并失败: {str(e)}")
        
        return merge_result
    
    def _create_rule_in_total(self, direct_rule: dict) -> Dict[str, Any]:
        """
        在总库中创建新规律
        
        Args:
            direct_rule: 直接库规律
            
        Returns:
            创建结果
        """
        create_result = {
            'new_rule_id': None,
            'fields_copied': [],
            'created_successfully': False
        }
        
        try:
            # 确保direct_rule是字典格式
            if hasattr(direct_rule, 'keys'):
                rule_dict = dict(direct_rule)
            else:
                rule_dict = direct_rule
            
            # 生成新的规律ID
            new_rule_id = f"TOTAL_{rule_dict['rule_type']}_{uuid.uuid4().hex[:12]}"
            
            # 准备插入数据
            insert_data = (
                new_rule_id,
                rule_dict['rule_type'],
                rule_dict['conditions'],
                rule_dict['predictions'],
                rule_dict['confidence'],
                rule_dict['support_count'],
                rule_dict['contradiction_count'],
                rule_dict['validation_count'],
                rule_dict['content_hash'],
                json.dumps([rule_dict['creator_id']]),  # 发现者列表
                1,  # occurrence_count
                rule_dict['created_time'],
                time.time(),  # last_updated
                rule_dict.get('last_validated', 0),
                rule_dict['validation_status']
            )
            
            # 插入总库
            self.db_managers['total_rules'].execute_update("""
                INSERT INTO total_rules (
                    rule_id, rule_type, conditions, predictions, confidence,
                    support_count, contradiction_count, validation_count, content_hash,
                    discoverers, occurrence_count, created_time, last_updated,
                    last_validated, validation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_data)
            
            create_result['new_rule_id'] = new_rule_id
            create_result['fields_copied'] = [
                'rule_type', 'conditions', 'predictions', 'confidence',
                'support_count', 'contradiction_count', 'validation_count',
                'content_hash', 'validation_status'
            ]
            create_result['created_successfully'] = True
            
            logger.debug(f"➕ 新规律创建: {new_rule_id[:8]}...")
            
        except Exception as e:
            create_result['error'] = str(e)
            logger.error(f"❌ 规律创建失败: {str(e)}")
        
        return create_result
    
    def batch_sync_rules_to_total(self, limit: int = 50) -> Dict[str, Any]:
        """
        批量同步规律到总库
        
        Args:
            limit: 每次同步的最大规律数量
            
        Returns:
            批量同步结果
        """
        batch_result = {
            'success': False,
            'total_processed': 0,
            'created_count': 0,
            'merged_count': 0,
            'failed_count': 0,
            'sync_details': [],
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 获取未同步的规律
            unsynced_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT content_hash, rule_id 
                FROM direct_rules 
                WHERE synced_to_total = 0 
                ORDER BY confidence DESC, support_count DESC
                LIMIT ?
            """, (limit,))
            
            logger.info(f"🔄 开始批量同步 {len(unsynced_rules)} 条规律")
            
            # 逐个同步
            for rule_info in unsynced_rules:
                sync_result = self.sync_rule_to_total_library(rule_info['content_hash'])
                
                batch_result['total_processed'] += 1
                
                if sync_result['success']:
                    if sync_result['action'] == 'created':
                        batch_result['created_count'] += 1
                    elif sync_result['action'] == 'merged':
                        batch_result['merged_count'] += 1
                else:
                    batch_result['failed_count'] += 1
                
                batch_result['sync_details'].append({
                    'rule_id': rule_info['rule_id'],
                    'action': sync_result.get('action', 'failed'),
                    'success': sync_result['success'],
                    'error': sync_result.get('error')
                })
                
                # 每处理10个规律输出一次进度
                if batch_result['total_processed'] % 10 == 0:
                    logger.info(f"📊 同步进度: {batch_result['total_processed']}/{len(unsynced_rules)}")
            
            batch_result['success'] = True
            batch_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 批量同步完成: 处理={batch_result['total_processed']}, 创建={batch_result['created_count']}, 合并={batch_result['merged_count']}, 失败={batch_result['failed_count']}")
            
        except Exception as e:
            batch_result['error'] = str(e)
            logger.error(f"❌ 批量同步失败: {str(e)}")
        
        return batch_result
    
    def sync_all_direct_rules_to_total(self) -> Dict[str, int]:
        """
        批量同步所有直接规律到总规律库
        
        Returns:
            同步统计结果
        """
        sync_result = {
            'rules_synced': 0,
            'rules_updated': 0,
            'rules_failed': 0,
            'total_processed': 0
        }
        
        try:
            # 获取所有未同步的直接规律
            unsynced_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT content_hash, rule_id 
                FROM direct_rules 
                WHERE synced_to_total = 0 
                ORDER BY confidence DESC, support_count DESC
            """)
            
            logger.info(f"🔄 开始同步所有直接规律: {len(unsynced_rules)} 条")
            
            for rule_info in unsynced_rules:
                try:
                    # 使用现有的单个规律同步方法
                    single_sync_result = self.sync_rule_to_total_library(rule_info['content_hash'])
                    
                    sync_result['total_processed'] += 1
                    
                    if single_sync_result['success']:
                        if single_sync_result['action'] == 'created':
                            sync_result['rules_synced'] += 1
                        elif single_sync_result['action'] == 'merged':
                            sync_result['rules_updated'] += 1
                    else:
                        sync_result['rules_failed'] += 1
                        
                except Exception as e:
                    sync_result['rules_failed'] += 1
                    logger.error(f"❌ 同步规律失败 {rule_info['rule_id']}: {str(e)}")
            
            logger.info(f"✅ 规律同步完成: 新增={sync_result['rules_synced']}, 更新={sync_result['rules_updated']}, 失败={sync_result['rules_failed']}")
            
        except Exception as e:
            logger.error(f"❌ 批量同步规律失败: {str(e)}")
            sync_result['error'] = str(e)
        
        return sync_result
    
    def get_recent_experiences(self, limit: int = 5) -> List[Dict]:
        """
        获取最近的直接经验
        
        Args:
            limit: 返回的经验数量限制
            
        Returns:
            最近的经验列表
        """
        try:
            recent_experiences = self.db_managers['direct_experiences'].execute_query("""
                SELECT * FROM direct_experiences 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(exp) for exp in recent_experiences]
            
        except Exception as e:
            logger.error(f"❌ 获取最近经验失败: {str(e)}")
            return []
    
    def get_recent_rules(self, limit: int = 5) -> List[Dict]:
        """
        获取最近的直接规律
        
        Args:
            limit: 返回的规律数量限制
            
        Returns:
            最近的规律列表
        """
        try:
            recent_rules = self.db_managers['direct_rules'].execute_query("""
                SELECT * FROM direct_rules 
                ORDER BY created_time DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(rule) for rule in recent_rules]
            
        except Exception as e:
            logger.error(f"❌ 获取最近规律失败: {str(e)}")
            return []
    
    def get_rule_sync_statistics(self) -> Dict[str, Any]:
        """
        获取规律同步统计信息
        
        Returns:
            同步统计信息
        """
        stats = {
            'success': False,
            'direct_library': {},
            'total_library': {},
            'sync_status': {},
            'quality_metrics': {},
            'sync_recommendations': []
        }
        
        try:
            # 直接库统计
            direct_stats = self.db_managers['direct_rules'].execute_query("""
                SELECT 
                    COUNT(*) as total_rules,
                    COUNT(CASE WHEN synced_to_total = 1 THEN 1 END) as synced_rules,
                    COUNT(CASE WHEN synced_to_total = 0 THEN 1 END) as unsynced_rules,
                    AVG(confidence) as avg_confidence,
                    AVG(support_count) as avg_support,
                    COUNT(CASE WHEN validation_status = 'validated' THEN 1 END) as validated_rules
                FROM direct_rules
            """)[0]
            
            stats['direct_library'] = dict(direct_stats)
            
            # 总库统计
            total_stats = self.db_managers['total_rules'].execute_query("""
                SELECT 
                    COUNT(*) as total_rules,
                    AVG(confidence) as avg_confidence,
                    AVG(support_count) as avg_support,
                    AVG(occurrence_count) as avg_occurrence,
                    COUNT(CASE WHEN validation_status = 'validated' THEN 1 END) as validated_rules,
                    SUM(occurrence_count) as total_occurrences
                FROM total_rules
            """)[0]
            
            stats['total_library'] = dict(total_stats)
            
            # 同步状态分析
            sync_rate = (direct_stats['synced_rules'] / direct_stats['total_rules'] 
                        if direct_stats['total_rules'] > 0 else 0)
            
            stats['sync_status'] = {
                'sync_rate': sync_rate,
                'pending_sync': direct_stats['unsynced_rules'],
                'sync_efficiency': sync_rate * 100,
                'total_vs_direct_ratio': (total_stats['total_rules'] / direct_stats['total_rules'] 
                                        if direct_stats['total_rules'] > 0 else 0)
            }
            
            # 质量指标对比
            stats['quality_metrics'] = {
                'confidence_improvement': (total_stats['avg_confidence'] - direct_stats['avg_confidence']
                                         if direct_stats['avg_confidence'] > 0 else 0),
                'support_consolidation': (total_stats['avg_support'] / direct_stats['avg_support']
                                        if direct_stats['avg_support'] > 0 else 1),
                'validation_rate_direct': (direct_stats['validated_rules'] / direct_stats['total_rules']
                                         if direct_stats['total_rules'] > 0 else 0),
                'validation_rate_total': (total_stats['validated_rules'] / total_stats['total_rules']
                                        if total_stats['total_rules'] > 0 else 0)
            }
            
            # 生成同步建议
            stats['sync_recommendations'] = self._generate_sync_recommendations(stats)
            
            stats['success'] = True
            
        except Exception as e:
            stats['error'] = str(e)
            logger.error(f"❌ 获取同步统计失败: {str(e)}")
        
        return stats
    
    def _generate_sync_recommendations(self, stats: dict) -> List[str]:
        """
        生成同步建议
        
        Args:
            stats: 统计信息
            
        Returns:
            建议列表
        """
        recommendations = []
        
        try:
            sync_status = stats.get('sync_status', {})
            direct_lib = stats.get('direct_library', {})
            total_lib = stats.get('total_library', {})
            quality = stats.get('quality_metrics', {})
            
            # 基于同步率的建议
            sync_rate = sync_status.get('sync_rate', 0)
            if sync_rate < 0.5:
                recommendations.append("⚠️ 同步率过低，建议立即执行批量同步")
            elif sync_rate < 0.8:
                recommendations.append("📊 同步率中等，建议定期执行同步")
            else:
                recommendations.append("✅ 同步率良好，保持当前同步频率")
            
            # 基于待同步数量的建议
            pending_sync = sync_status.get('pending_sync', 0)
            if pending_sync > 50:
                recommendations.append(f"🔄 待同步规律过多({pending_sync}条)，建议增加同步频率")
            elif pending_sync > 20:
                recommendations.append(f"📈 有{pending_sync}条规律待同步，建议近期执行同步")
            
            # 基于质量改进的建议
            confidence_improvement = quality.get('confidence_improvement', 0)
            if confidence_improvement > 0.1:
                recommendations.append("🎯 总库置信度显著提升，同步机制有效")
            elif confidence_improvement < -0.05:
                recommendations.append("⚠️ 总库置信度下降，建议检查合并算法")
            
            # 基于库大小比例的建议
            ratio = sync_status.get('total_vs_direct_ratio', 0)
            if ratio < 0.3:
                recommendations.append("📊 总库规律过少，建议加强同步和去重")
            elif ratio > 0.9:
                recommendations.append("🗂️ 总库规律接近直接库，去重效果良好")
            
            # 基于验证率的建议
            validation_rate_total = quality.get('validation_rate_total', 0)
            if validation_rate_total < 0.2:
                recommendations.append("📋 总库验证率偏低，建议加强规律验证")
            elif validation_rate_total > 0.5:
                recommendations.append("✅ 总库验证率良好，规律质量较高")
            
        except Exception as e:
            recommendations.append(f"❌ 生成建议时出错: {str(e)}")
        
        return recommendations
    
    def resolve_rule_sync_conflicts(self, content_hash: str) -> Dict[str, Any]:
        """
        解决规律同步冲突
        
        Args:
            content_hash: 规律内容哈希
            
        Returns:
            冲突解决结果
        """
        conflict_result = {
            'success': False,
            'conflict_type': None,
            'resolution_action': None,
            'details': {}
        }
        
        try:
            # 获取直接库和总库中的规律
            direct_rule = self.db_managers['direct_rules'].execute_query(
                "SELECT * FROM direct_rules WHERE content_hash = ?", (content_hash,)
            )
            
            total_rule = self.db_managers['total_rules'].execute_query(
                "SELECT * FROM total_rules WHERE content_hash = ?", (content_hash,)
            )
            
            if not direct_rule:
                conflict_result['error'] = "直接库中未找到规律"
                return conflict_result
            
            if not total_rule:
                conflict_result['error'] = "总库中未找到规律，无冲突"
                return conflict_result
            
            direct_rule = direct_rule[0]
            total_rule = total_rule[0]
            
            # 检测冲突类型
            conflicts = []
            
            # 置信度冲突
            conf_diff = abs(direct_rule['confidence'] - total_rule['confidence'])
            if conf_diff > 0.2:
                conflicts.append('confidence_mismatch')
            
            # 验证状态冲突
            if direct_rule['validation_status'] != total_rule['validation_status']:
                conflicts.append('status_mismatch')
            
            # 统计数据异常
            if (direct_rule['support_count'] > total_rule['support_count'] or
                direct_rule['contradiction_count'] > total_rule['contradiction_count']):
                conflicts.append('statistics_inconsistency')
            
            if not conflicts:
                conflict_result['success'] = True
                conflict_result['conflict_type'] = 'no_conflict'
                conflict_result['resolution_action'] = 'none_needed'
                return conflict_result
            
            # 解决冲突
            conflict_result['conflict_type'] = conflicts
            
            if 'statistics_inconsistency' in conflicts:
                # 重新合并统计数据
                merge_result = self._merge_rule_to_total(direct_rule, total_rule)
                conflict_result['resolution_action'] = 'statistics_remerged'
                conflict_result['details'] = merge_result
            
            elif 'status_mismatch' in conflicts:
                # 采用更保守的状态
                status_priority = {'rejected': 0, 'pending': 1, 'validated': 2}
                if (status_priority.get(direct_rule['validation_status'], 1) < 
                    status_priority.get(total_rule['validation_status'], 1)):
                    
                    self.db_managers['total_rules'].execute_update(
                        "UPDATE total_rules SET validation_status = ? WHERE rule_id = ?",
                        (direct_rule['validation_status'], total_rule['rule_id'])
                    )
                    conflict_result['resolution_action'] = 'status_updated'
            
            elif 'confidence_mismatch' in conflicts:
                # 重新计算置信度
                merge_result = self._merge_rule_to_total(direct_rule, total_rule)
                conflict_result['resolution_action'] = 'confidence_recalculated'
                conflict_result['details'] = merge_result
            
            conflict_result['success'] = True
            
            logger.info(f"🔧 冲突解决完成: {content_hash[:8]}... - {conflict_result['resolution_action']}")
            
        except Exception as e:
            conflict_result['error'] = str(e)
            logger.error(f"❌ 冲突解决失败: {str(e)}")
        
        return conflict_result

    def close(self):
        """关闭五库系统"""
        logger.info("🔒 五库系统已关闭")

    # ==================== 决策库管理模块 ====================
    
    def generate_decision_from_context(self, context: Dict[str, Any], source: str = 'rule_based') -> Dict[str, Any]:
        """
        基于上下文生成决策
        
        Args:
            context: 决策上下文
            source: 决策来源 ('rule_based', 'experience_based', 'hybrid')
            
        Returns:
            决策生成结果
        """
        decision_result = {
            'success': False,
            'decision': None,
            'confidence': 0.0,
            'reasoning': [],
            'alternatives': [],
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 验证上下文
            if not context or not isinstance(context, dict):
                decision_result['error'] = "无效的决策上下文"
                return decision_result
            
            # 根据来源选择决策生成策略
            if source == 'rule_based':
                decision_result = self._generate_rule_based_decision(context)
            elif source == 'experience_based':
                decision_result = self._generate_experience_based_decision(context)
            elif source == 'hybrid':
                decision_result = self._generate_hybrid_decision(context)
            else:
                decision_result['error'] = f"不支持的决策来源: {source}"
                return decision_result
            
            decision_result['processing_time'] = time.time() - start_time
            
            # 如果生成成功，添加到决策库
            if decision_result['success'] and decision_result['decision']:
                add_result = self.add_decision_to_library(decision_result['decision'])
                decision_result['added_to_library'] = add_result['success']
                decision_result['decision_id'] = add_result.get('decision_id')
            
            logger.info(f"✅ 决策生成完成: {source} - 置信度{decision_result['confidence']:.3f}")
            
        except Exception as e:
            decision_result['error'] = str(e)
            logger.error(f"❌ 决策生成失败: {str(e)}")
        
        return decision_result
    
    def _generate_rule_based_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于规律生成决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策结果
        """
        result = {
            'success': False,
            'decision': None,
            'confidence': 0.0,
            'reasoning': [],
            'alternatives': []
        }
        
        try:
            # 查找匹配的规律
            matching_rules = self._find_matching_rules(context)
            
            if not matching_rules:
                result['reasoning'].append("未找到匹配的规律")
                return result
            
            # 按置信度排序规律
            matching_rules.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 选择最佳规律
            best_rule = matching_rules[0]
            predictions = json.loads(best_rule['predictions'])
            
            # 生成决策
            if 'result' in predictions:
                action = f"执行以获得: {predictions['result']}"
            elif 'success' in predictions:
                success_prob = predictions['success']
                if success_prob:
                    action = "执行该行动（高成功概率）"
                else:
                    action = "避免该行动（低成功概率）"
            else:
                action = "基于规律执行推荐行动"
            
            # 创建决策对象
            decision = Decision(
                decision_id=f"RULE_{uuid.uuid4().hex[:12]}",
                context=context,
                action=action,
                confidence=best_rule['confidence'],
                source='rule_based'
            )
            
            result['success'] = True
            result['decision'] = decision
            result['confidence'] = best_rule['confidence']
            result['reasoning'].append(f"基于规律 {best_rule['rule_id'][:8]}...")
            result['reasoning'].append(f"规律置信度: {best_rule['confidence']:.3f}")
            result['reasoning'].append(f"规律支持度: {best_rule['support_count']}")
            
            # 添加备选方案
            for rule in matching_rules[1:3]:  # 最多3个备选
                alt_predictions = json.loads(rule['predictions'])
                if 'result' in alt_predictions:
                    alt_action = f"备选: 执行以获得 {alt_predictions['result']}"
                else:
                    alt_action = "备选: 基于次优规律的行动"
                
                result['alternatives'].append({
                    'action': alt_action,
                    'confidence': rule['confidence'],
                    'rule_id': rule['rule_id']
                })
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ 基于规律的决策生成失败: {str(e)}")
        
        return result
    
    def _generate_experience_based_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于经验生成决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策结果
        """
        result = {
            'success': False,
            'decision': None,
            'confidence': 0.0,
            'reasoning': [],
            'alternatives': []
        }
        
        try:
            # 查找相似经验
            similar_experiences = self._find_similar_experiences(context)
            
            if not similar_experiences:
                result['reasoning'].append("未找到相似的历史经验")
                return result
            
            # 分析经验模式
            action_stats = {}
            for exp in similar_experiences:
                action = exp['action']
                if action not in action_stats:
                    action_stats[action] = {
                        'total_count': 0,
                        'success_count': 0,
                        'avg_success_rate': 0.0,
                        'results': []
                    }
                
                stats = action_stats[action]
                stats['total_count'] += exp['occurrence_count']
                stats['success_count'] += exp['success_count']
                stats['results'].append(exp['result'])
                stats['avg_success_rate'] = stats['success_count'] / stats['total_count']
            
            # 选择最佳行动
            if action_stats:
                best_action = max(action_stats.items(), key=lambda x: x[1]['avg_success_rate'])
                action_name, action_data = best_action
                
                # 创建决策对象
                decision = Decision(
                    decision_id=f"EXP_{uuid.uuid4().hex[:12]}",
                    context=context,
                    action=f"执行行动: {action_name}",
                    confidence=action_data['avg_success_rate'],
                    source='experience_based'
                )
                
                result['success'] = True
                result['decision'] = decision
                result['confidence'] = action_data['avg_success_rate']
                result['reasoning'].append(f"基于 {len(similar_experiences)} 条相似经验")
                result['reasoning'].append(f"行动 '{action_name}' 成功率: {action_data['avg_success_rate']:.3f}")
                result['reasoning'].append(f"历史执行次数: {action_data['total_count']}")
                
                # 添加备选方案
                sorted_actions = sorted(action_stats.items(), key=lambda x: x[1]['avg_success_rate'], reverse=True)
                for action_name, action_data in sorted_actions[1:3]:
                    result['alternatives'].append({
                        'action': f"备选: {action_name}",
                        'confidence': action_data['avg_success_rate'],
                        'experience_count': action_data['total_count']
                    })
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ 基于经验的决策生成失败: {str(e)}")
        
        return result
    
    def _generate_hybrid_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        混合策略生成决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策结果
        """
        result = {
            'success': False,
            'decision': None,
            'confidence': 0.0,
            'reasoning': [],
            'alternatives': []
        }
        
        try:
            # 获取基于规律的决策
            rule_result = self._generate_rule_based_decision(context)
            
            # 获取基于经验的决策
            exp_result = self._generate_experience_based_decision(context)
            
            # 混合决策逻辑
            if rule_result['success'] and exp_result['success']:
                # 两种方法都成功，选择置信度更高的
                if rule_result['confidence'] >= exp_result['confidence']:
                    primary_result = rule_result
                    secondary_result = exp_result
                    primary_source = "规律"
                    secondary_source = "经验"
                else:
                    primary_result = exp_result
                    secondary_result = rule_result
                    primary_source = "经验"
                    secondary_source = "规律"
                
                # 计算混合置信度
                weight_primary = 0.7
                weight_secondary = 0.3
                hybrid_confidence = (primary_result['confidence'] * weight_primary + 
                                   secondary_result['confidence'] * weight_secondary)
                
                # 创建混合决策
                decision = Decision(
                    decision_id=f"HYBRID_{uuid.uuid4().hex[:12]}",
                    context=context,
                    action=primary_result['decision'].action,
                    confidence=hybrid_confidence,
                    source='hybrid'
                )
                
                result['success'] = True
                result['decision'] = decision
                result['confidence'] = hybrid_confidence
                result['reasoning'].append(f"混合决策: 主要基于{primary_source}")
                result['reasoning'].extend(primary_result['reasoning'])
                result['reasoning'].append(f"辅助验证: {secondary_source}置信度{secondary_result['confidence']:.3f}")
                
                # 合并备选方案
                result['alternatives'].extend(primary_result['alternatives'])
                if secondary_result['decision']:
                    result['alternatives'].append({
                        'action': f"备选({secondary_source}): {secondary_result['decision'].action}",
                        'confidence': secondary_result['confidence'],
                        'source': secondary_source
                    })
                
            elif rule_result['success']:
                # 只有规律方法成功
                result = rule_result
                result['reasoning'].append("仅基于规律生成（无匹配经验）")
                
            elif exp_result['success']:
                # 只有经验方法成功
                result = exp_result
                result['reasoning'].append("仅基于经验生成（无匹配规律）")
                
            else:
                # 两种方法都失败
                result['reasoning'].append("规律和经验方法均未找到匹配结果")
                result['reasoning'].extend(rule_result.get('reasoning', []))
                result['reasoning'].extend(exp_result.get('reasoning', []))
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ 混合决策生成失败: {str(e)}")
        
        return result
    
    def _find_matching_rules(self, context: Dict[str, Any]) -> List[dict]:
        """
        查找匹配上下文的规律
        
        Args:
            context: 决策上下文
            
        Returns:
            匹配的规律列表
        """
        matching_rules = []
        
        try:
            # 从总规律库查找
            all_rules = self.db_managers['total_rules'].execute_query("""
                SELECT * FROM total_rules 
                WHERE validation_status != 'rejected'
                ORDER BY confidence DESC, support_count DESC
            """)
            
            for rule in all_rules:
                conditions = json.loads(rule['conditions'])
                
                # 检查条件匹配
                match_score = 0
                total_conditions = len(conditions)
                
                for key, value in conditions.items():
                    if key in context and context[key] == value:
                        match_score += 1
                
                # 如果匹配度超过阈值，添加到结果
                if total_conditions > 0 and match_score / total_conditions >= 0.8:
                    rule_dict = dict(rule)
                    rule_dict['match_score'] = match_score / total_conditions
                    matching_rules.append(rule_dict)
            
        except Exception as e:
            logger.error(f"❌ 查找匹配规律失败: {str(e)}")
        
        return matching_rules
    
    def _find_similar_experiences(self, context: Dict[str, Any]) -> List[dict]:
        """
        查找相似的历史经验
        
        Args:
            context: 决策上下文
            
        Returns:
            相似经验列表
        """
        similar_experiences = []
        
        try:
            # 从总经验库查找
            all_experiences = self.db_managers['total_experiences'].execute_query("""
                SELECT * FROM total_experiences 
                WHERE occurrence_count >= 2
                ORDER BY avg_success_rate DESC, occurrence_count DESC
            """)
            
            for exp in all_experiences:
                similarity_score = 0
                total_fields = 0
                
                # 计算相似度
                for field in ['environment', 'object', 'characteristics', 'action', 'tools']:
                    if field in context:
                        total_fields += 1
                        if exp[field] == context[field]:
                            similarity_score += 1
                
                # 如果相似度超过阈值，添加到结果
                if total_fields > 0 and similarity_score / total_fields >= 0.6:
                    exp_dict = dict(exp)
                    exp_dict['similarity_score'] = similarity_score / total_fields
                    similar_experiences.append(exp_dict)
            
        except Exception as e:
            logger.error(f"❌ 查找相似经验失败: {str(e)}")
        
        return similar_experiences
    
    def add_decision_to_library(self, decision: Decision) -> Dict[str, Any]:
        """
        添加决策到决策库
        
        Args:
            decision: 决策对象
            
        Returns:
            添加结果
        """
        add_result = {
            'success': False,
            'decision_id': None,
            'action': None,  # 'added', 'updated'
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 生成内容哈希
            content_hash = decision.generate_hash()
            
            # 检查是否已存在
            existing_decision = self.db_managers['decisions'].execute_query(
                "SELECT * FROM decisions WHERE content_hash = ?", (content_hash,)
            )
            
            if existing_decision:
                # 更新现有决策
                existing = existing_decision[0]
                self.db_managers['decisions'].execute_update("""
                    UPDATE decisions 
                    SET total_uses = total_uses + 1,
                        last_used = ?,
                        updated_time = ?
                    WHERE decision_id = ?
                """, (time.time(), time.time(), existing['decision_id']))
                
                add_result['action'] = 'updated'
                add_result['decision_id'] = existing['decision_id']
                
            else:
                # 添加新决策
                decision_data = decision.to_dict()
                decision_data['content_hash'] = content_hash
                
                self.db_managers['decisions'].execute_update("""
                    INSERT INTO decisions (
                        decision_id, content_hash, context, action, confidence,
                        source, success_count, failure_count, total_uses,
                        created_time, last_used, avg_success_rate, emrs_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision.decision_id,
                    content_hash,
                    decision_data['context'],
                    decision.action,
                    decision.confidence,
                    decision.source,
                    decision.success_count,
                    decision.failure_count,
                    decision.total_uses,
                    decision.created_time,
                    decision.last_used,
                    0.0,  # avg_success_rate
                    0.0   # emrs_score
                ))
                
                add_result['action'] = 'added'
                add_result['decision_id'] = decision.decision_id
            
            add_result['success'] = True
            add_result['processing_time'] = time.time() - start_time
            
            logger.debug(f"✅ 决策{add_result['action']}: {add_result['decision_id'][:8]}...")
            
        except Exception as e:
            add_result['error'] = str(e)
            logger.error(f"❌ 添加决策失败: {str(e)}")
        
        return add_result
    
    def query_decisions(self, context: Dict[str, Any] = None, limit: int = 10) -> Dict[str, Any]:
        """
        查询决策库
        
        Args:
            context: 查询上下文（可选）
            limit: 返回结果数量限制
            
        Returns:
            查询结果
        """
        query_result = {
            'success': False,
            'decisions': [],
            'total_count': 0,
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            if context:
                # 基于上下文的相似度查询
                all_decisions = self.db_managers['decisions'].execute_query("""
                    SELECT * FROM decisions 
                    ORDER BY confidence DESC, avg_success_rate DESC, total_uses DESC
                """)
                
                scored_decisions = []
                for decision in all_decisions:
                    decision_context = json.loads(decision['context'])
                    similarity = self._calculate_context_similarity(context, decision_context)
                    
                    if similarity >= 0.3:  # 相似度阈值
                        decision_dict = dict(decision)
                        decision_dict['similarity_score'] = similarity
                        scored_decisions.append(decision_dict)
                
                # 按相似度和置信度排序
                scored_decisions.sort(key=lambda x: (x['similarity_score'], x['confidence']), reverse=True)
                query_result['decisions'] = scored_decisions[:limit]
                
            else:
                # 通用查询
                decisions = self.db_managers['decisions'].execute_query("""
                    SELECT * FROM decisions 
                    ORDER BY confidence DESC, avg_success_rate DESC, total_uses DESC
                    LIMIT ?
                """, (limit,))
                
                query_result['decisions'] = [dict(d) for d in decisions]
            
            query_result['total_count'] = len(query_result['decisions'])
            query_result['success'] = True
            query_result['processing_time'] = time.time() - start_time
            
            logger.debug(f"✅ 决策查询完成: 返回{query_result['total_count']}条结果")
            
        except Exception as e:
            query_result['error'] = str(e)
            logger.error(f"❌ 决策查询失败: {str(e)}")
        
        return query_result
    
    def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """
        计算上下文相似度
        
        Args:
            context1: 上下文1
            context2: 上下文2
            
        Returns:
            相似度分数 (0-1)
        """
        if not context1 or not context2:
            return 0.0
        
        all_keys = set(context1.keys()) | set(context2.keys())
        if not all_keys:
            return 0.0
        
        matching_keys = 0
        for key in all_keys:
            if key in context1 and key in context2:
                if context1[key] == context2[key]:
                    matching_keys += 1
        
        return matching_keys / len(all_keys)
    
    def update_decision_feedback(self, decision_id: str, success: bool, result: str = None) -> Dict[str, Any]:
        """
        更新决策反馈
        
        Args:
            decision_id: 决策ID
            success: 是否成功
            result: 执行结果（可选）
            
        Returns:
            更新结果
        """
        update_result = {
            'success': False,
            'decision_id': decision_id,
            'updated_metrics': {},
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # 获取现有决策
            decision = self.db_managers['decisions'].execute_query(
                "SELECT * FROM decisions WHERE decision_id = ?", (decision_id,)
            )
            
            if not decision:
                update_result['error'] = f"决策 {decision_id} 不存在"
                return update_result
            
            decision = decision[0]
            
            # 更新统计数据
            new_total_uses = decision['total_uses'] + 1
            if success:
                new_success_count = decision['success_count'] + 1
                new_failure_count = decision['failure_count']
            else:
                new_success_count = decision['success_count']
                new_failure_count = decision['failure_count'] + 1
            
            # 计算新的平均成功率
            new_avg_success_rate = new_success_count / new_total_uses if new_total_uses > 0 else 0.0
            
            # 计算EMRS分数（经验-记忆-推理-成功率）
            confidence_weight = 0.3
            usage_weight = 0.2
            success_weight = 0.5
            
            normalized_usage = min(new_total_uses / 10.0, 1.0)  # 归一化使用次数
            new_emrs_score = (decision['confidence'] * confidence_weight + 
                            normalized_usage * usage_weight + 
                            new_avg_success_rate * success_weight)
            
            # 更新数据库
            self.db_managers['decisions'].execute_update("""
                UPDATE decisions 
                SET success_count = ?,
                    failure_count = ?,
                    total_uses = ?,
                    avg_success_rate = ?,
                    emrs_score = ?,
                    last_used = ?,
                    updated_time = ?
                WHERE decision_id = ?
            """, (
                new_success_count,
                new_failure_count,
                new_total_uses,
                new_avg_success_rate,
                new_emrs_score,
                time.time(),
                time.time(),
                decision_id
            ))
            
            update_result['success'] = True
            update_result['updated_metrics'] = {
                'total_uses': new_total_uses,
                'success_count': new_success_count,
                'failure_count': new_failure_count,
                'avg_success_rate': new_avg_success_rate,
                'emrs_score': new_emrs_score
            }
            update_result['processing_time'] = time.time() - start_time
            
            logger.info(f"✅ 决策反馈更新: {decision_id[:8]}... - 成功率{new_avg_success_rate:.3f}")
            
        except Exception as e:
            update_result['error'] = str(e)
            logger.error(f"❌ 决策反馈更新失败: {str(e)}")
        
        return update_result
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """
        获取决策库统计信息
        
        Returns:
            统计信息
        """
        stats = {
            'success': False,
            'total_decisions': 0,
            'by_source': {},
            'performance_metrics': {},
            'top_decisions': [],
            'recommendations': []
        }
        
        try:
            # 基本统计
            total_result = self.db_managers['decisions'].execute_query(
                "SELECT COUNT(*) as count FROM decisions"
            )
            stats['total_decisions'] = total_result[0]['count'] if total_result else 0
            
            # 按来源分类统计
            source_stats = self.db_managers['decisions'].execute_query("""
                SELECT source, 
                       COUNT(*) as count,
                       AVG(confidence) as avg_confidence,
                       AVG(avg_success_rate) as avg_success_rate,
                       AVG(emrs_score) as avg_emrs_score
                FROM decisions 
                GROUP BY source
            """)
            
            for stat in source_stats:
                stats['by_source'][stat['source']] = dict(stat)
            
            # 性能指标
            performance = self.db_managers['decisions'].execute_query("""
                SELECT AVG(confidence) as avg_confidence,
                       AVG(avg_success_rate) as avg_success_rate,
                       AVG(emrs_score) as avg_emrs_score,
                       AVG(total_uses) as avg_usage,
                       COUNT(CASE WHEN avg_success_rate >= 0.7 THEN 1 END) as high_performance_count,
                       COUNT(CASE WHEN total_uses >= 5 THEN 1 END) as well_tested_count
                FROM decisions
            """)[0]
            
            # 处理None值
            performance_dict = dict(performance)
            for key, value in performance_dict.items():
                if value is None:
                    performance_dict[key] = 0.0
            
            stats['performance_metrics'] = performance_dict
            
            # 顶级决策
            top_decisions = self.db_managers['decisions'].execute_query("""
                SELECT decision_id, action, confidence, avg_success_rate, emrs_score, total_uses
                FROM decisions 
                ORDER BY emrs_score DESC, avg_success_rate DESC
                LIMIT 5
            """)
            
            stats['top_decisions'] = [dict(d) for d in top_decisions]
            
            # 生成建议
            stats['recommendations'] = self._generate_decision_recommendations(stats)
            
            stats['success'] = True
            
        except Exception as e:
            stats['error'] = str(e)
            logger.error(f"❌ 获取决策统计失败: {str(e)}")
        
        return stats
    
    def _generate_decision_recommendations(self, stats: dict) -> List[str]:
        """
        生成决策库建议
        
        Args:
            stats: 统计信息
            
        Returns:
            建议列表
        """
        recommendations = []
        
        try:
            total_decisions = stats.get('total_decisions', 0)
            performance = stats.get('performance_metrics', {})
            
            # 基于决策数量的建议
            if total_decisions < 10:
                recommendations.append("📊 决策库规模较小，建议增加更多决策生成")
            elif total_decisions > 1000:
                recommendations.append("🗂️ 决策库规模较大，建议定期清理低效决策")
            
            # 基于性能指标的建议
            avg_success_rate = performance.get('avg_success_rate', 0)
            if avg_success_rate < 0.5:
                recommendations.append("⚠️ 平均成功率偏低，建议优化决策生成算法")
            elif avg_success_rate > 0.8:
                recommendations.append("✅ 平均成功率良好，决策质量较高")
            
            # 基于使用情况的建议
            avg_usage = performance.get('avg_usage', 0)
            if avg_usage < 2:
                recommendations.append("📈 决策使用频率较低，建议加强决策推荐")
            
            # 基于来源分布的建议
            by_source = stats.get('by_source', {})
            if len(by_source) == 1:
                recommendations.append("🔄 决策来源单一，建议启用混合决策策略")
            
            # 基于高性能决策比例的建议
            high_perf_count = performance.get('high_performance_count', 0)
            if total_decisions > 0:
                high_perf_ratio = high_perf_count / total_decisions
                if high_perf_ratio < 0.3:
                    recommendations.append("🎯 高性能决策比例偏低，建议加强决策验证")
                elif high_perf_ratio > 0.7:
                    recommendations.append("🏆 高性能决策比例良好，系统运行稳定")
            
        except Exception as e:
            recommendations.append(f"❌ 生成建议时出错: {str(e)}")
        
        return recommendations

    def close(self):
        """关闭系统资源"""
        # 清理缓存
        self.cache.clear()
        logger.info("🔒 五库系统已关闭")

    # ========== 对象属性验证和工具有效性分析 ==========
    
    def validate_object_attributes(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        验证经验中的对象属性是否符合配置
        
        Args:
            experience: EOCATR经验对象
            
        Returns:
            验证结果字典
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': [],
            'object_info': {},
            'tool_effectiveness': None
        }
        
        if not self.object_config_enabled:
            result['warnings'].append("对象属性配置系统未启用，跳过验证")
            return result
        
        try:
            # 验证对象是否存在
            object_attrs = get_object_attributes(experience.object)
            if not object_attrs:
                result['errors'].append(f"未知对象: {experience.object}")
                result['valid'] = False
            else:
                result['object_info'] = object_attrs
                
                # 验证特征是否匹配
                if experience.characteristics:
                    self._validate_object_characteristics(experience, object_attrs, result)
                
                # 验证环境兼容性
                if experience.environment:
                    self._validate_environment_compatibility(experience, result)
            
            # 分析工具有效性
            if experience.tools and experience.object:
                self._analyze_tool_effectiveness(experience, result)
            
            # 生成改进建议
            self._generate_attribute_suggestions(experience, result)
            
        except Exception as e:
            result['errors'].append(f"对象属性验证失败: {str(e)}")
            result['valid'] = False
            logger.error(f"对象属性验证异常: {e}")
        
        return result
    
    def _validate_object_characteristics(self, experience: EOCATRExperience, object_attrs: Dict, result: Dict):
        """验证对象特征"""
        characteristics = experience.characteristics.split(',') if ',' in experience.characteristics else [experience.characteristics]
        
        for char in characteristics:
            char = char.strip()
            if char:
                # 检查特征是否在对象属性中
                found = False
                for attr_name, attr_value in object_attrs.items():
                    if isinstance(attr_value, str) and char in attr_value:
                        found = True
                        break
                    elif str(attr_value) == char:
                        found = True
                        break
                
                if not found:
                    result['warnings'].append(f"特征 '{char}' 可能不匹配对象 '{experience.object}'")
    
    def _validate_environment_compatibility(self, experience: EOCATRExperience, result: Dict):
        """验证环境兼容性"""
        if experience.environment in ENVIRONMENT_TYPES:
            env_info = ENVIRONMENT_TYPES[experience.environment]
            result['object_info']['environment_info'] = env_info
            
            # 检查环境安全性
            if env_info['safety'] < 0.3:
                result['warnings'].append(f"环境 '{experience.environment}' 安全性较低 ({env_info['safety']:.1f})")
        else:
            result['warnings'].append(f"未知环境类型: {experience.environment}")
    
    def _analyze_tool_effectiveness(self, experience: EOCATRExperience, result: Dict):
        """分析工具有效性"""
        tools = experience.tools.split(',') if ',' in experience.tools else [experience.tools]
        tool_analysis = {}
        
        for tool in tools:
            tool = tool.strip()
            if tool and tool != 'None':
                effectiveness = calculate_tool_effectiveness(tool, experience.object)
                tool_analysis[tool] = {
                    'effectiveness': effectiveness,
                    'rating': self._get_effectiveness_rating(effectiveness)
                }
                
                # 建议更好的工具
                best_tool, best_effectiveness = get_best_tool_for_target(experience.object)
                if best_tool != tool and best_effectiveness > effectiveness + 0.1:
                    result['suggestions'].append(
                        f"对于 '{experience.object}'，'{best_tool}' (有效性: {best_effectiveness:.2f}) "
                        f"可能比 '{tool}' (有效性: {effectiveness:.2f}) 更有效"
                    )
        
        result['tool_effectiveness'] = tool_analysis
    
    def _get_effectiveness_rating(self, effectiveness: float) -> str:
        """获取有效性评级"""
        if effectiveness >= 0.8:
            return "优秀"
        elif effectiveness >= 0.6:
            return "良好"
        elif effectiveness >= 0.4:
            return "一般"
        else:
            return "较差"
    
    def _generate_attribute_suggestions(self, experience: EOCATRExperience, result: Dict):
        """生成属性改进建议"""
        if not result['errors']:
            # 基于对象类型生成建议
            object_attrs = result.get('object_info', {})
            category = object_attrs.get('category', '')
            
            if category == 'predator':
                result['suggestions'].append("面对猛兽时建议使用长矛等高穿透力武器")
            elif category == 'bird':
                result['suggestions'].append("捕捉鸟类建议使用弓箭等高精确度武器")
            elif category == 'underground_plant':
                result['suggestions'].append("挖掘地下植物建议使用铁锹等挖掘工具")
    
    def get_tool_effectiveness_report(self, tool_name: str = None, target_name: str = None) -> Dict[str, Any]:
        """
        获取工具有效性报告
        
        Args:
            tool_name: 工具名称（可选）
            target_name: 目标名称（可选）
            
        Returns:
            工具有效性报告
        """
        if not self.object_config_enabled:
            return {'error': '对象属性配置系统未启用'}
        
        report = {
            'timestamp': time.time(),
            'tool_analysis': {},
            'target_analysis': {},
            'recommendations': []
        }
        
        try:
            if tool_name:
                # 分析特定工具对所有目标的有效性
                report['tool_analysis'][tool_name] = {}
                for target in TARGET_TYPE_MAPPING.keys():
                    effectiveness = calculate_tool_effectiveness(tool_name, target)
                    report['tool_analysis'][tool_name][target] = {
                        'effectiveness': effectiveness,
                        'rating': self._get_effectiveness_rating(effectiveness)
                    }
            
            if target_name:
                # 分析所有工具对特定目标的有效性
                report['target_analysis'][target_name] = {}
                for tool in TOOL_CHARACTERISTICS.keys():
                    effectiveness = calculate_tool_effectiveness(tool, target_name)
                    report['target_analysis'][target_name][tool] = {
                        'effectiveness': effectiveness,
                        'rating': self._get_effectiveness_rating(effectiveness)
                    }
                
                # 推荐最佳工具
                best_tool, best_effectiveness = get_best_tool_for_target(target_name)
                report['recommendations'].append(
                    f"对于 '{target_name}'，推荐使用 '{best_tool}' (有效性: {best_effectiveness:.2f})"
                )
            
            if not tool_name and not target_name:
                # 生成完整的工具-目标兼容性矩阵
                from object_attributes_config import get_tool_target_compatibility_matrix
                report['compatibility_matrix'] = get_tool_target_compatibility_matrix()
        
        except Exception as e:
            report['error'] = f"生成工具有效性报告失败: {str(e)}"
            logger.error(f"工具有效性报告异常: {e}")
        
        return report
    
    def analyze_experience_with_attributes(self, experience: EOCATRExperience) -> Dict[str, Any]:
        """
        使用对象属性系统分析经验
        
        Args:
            experience: EOCATR经验对象
            
        Returns:
            分析结果
        """
        analysis = {
            'experience_hash': experience.generate_hash(),
            'attribute_validation': self.validate_object_attributes(experience),
            'learning_insights': [],
            'optimization_suggestions': []
        }
        
        if not self.object_config_enabled:
            analysis['warning'] = "对象属性配置系统未启用"
            return analysis
        
        try:
            # 分析学习洞察
            self._extract_learning_insights(experience, analysis)
            
            # 生成优化建议
            self._generate_optimization_suggestions(experience, analysis)
            
        except Exception as e:
            analysis['error'] = f"经验属性分析失败: {str(e)}"
            logger.error(f"经验属性分析异常: {e}")
        
        return analysis
    
    def _extract_learning_insights(self, experience: EOCATRExperience, analysis: Dict):
        """提取学习洞察"""
        insights = []
        
        # 成功/失败模式分析
        if experience.success:
            insights.append(f"成功经验: 在{experience.environment}环境中使用{experience.tools}对{experience.object}执行{experience.action}")
        else:
            insights.append(f"失败经验: 在{experience.environment}环境中使用{experience.tools}对{experience.object}执行{experience.action}失败")
        
        # 工具选择洞察
        tool_effectiveness = analysis['attribute_validation'].get('tool_effectiveness', {})
        for tool, info in tool_effectiveness.items():
            if info['effectiveness'] > 0.8:
                insights.append(f"工具选择优秀: {tool}对{experience.object}的有效性为{info['effectiveness']:.2f}")
            elif info['effectiveness'] < 0.4:
                insights.append(f"工具选择需改进: {tool}对{experience.object}的有效性仅为{info['effectiveness']:.2f}")
        
        analysis['learning_insights'] = insights
    
    def _generate_optimization_suggestions(self, experience: EOCATRExperience, analysis: Dict):
        """生成优化建议"""
        suggestions = []
        
        # 基于属性验证结果生成建议
        validation = analysis['attribute_validation']
        suggestions.extend(validation.get('suggestions', []))
        
        # 基于成功率生成建议
        if not experience.success:
            suggestions.append("考虑尝试不同的工具或在不同环境中执行相同行动")
        
        # 基于对象类型生成建议
        object_attrs = validation.get('object_info', {})
        if object_attrs:
            category = object_attrs.get('category', '')
            if category == 'predator' and experience.action == 'collect':
                suggestions.append("警告: 尝试收集猛兽可能很危险，建议先使用武器")
            elif category in ['ground_plant', 'underground_plant', 'tree_plant'] and experience.action == 'attack':
                suggestions.append("提示: 对植物使用攻击行动可能不如使用收集行动有效")
        
        analysis['optimization_suggestions'] = suggestions

    # ============================================================================
    # EOCATR矩阵配置管理器 (新增)
    # ============================================================================
    
    def initialize_eocatr_matrix_config(self) -> Dict[str, List[str]]:
        """
        初始化完整EOCATR矩阵配置
        基于最终确认的矩阵规格
        
        Returns:
            完整的EOCATR矩阵配置字典
        """
        return {
            'environments': [
                'bush', 'cave', 'forest', 'open_field', 'plain', 'river', 'big_tree'
            ],
            'objects': [
                'berry', 'bear', 'dove', 'fish', 'mushroom', 'potato', 
                'strawberry', 'tiger', 'toxic_mushroom', 'toxic_strawberry', 'water_source'
            ],
            'attributes': [
                'red_color', 'green_color', 'blue_color', 'yellow_color', 'brown_color',
                'black_color', 'white_color', 'round_shape', 'long_shape', 'umbrella_shape',
                'irregular_shape', 'soft_texture', 'hard_texture', 'medium_texture',
                'sweet_smell', 'bad_smell', 'no_smell', 'earth_smell', 'x_coordinate',
                'y_coordinate', 'environment_type', 'vision_range', 'alive_status',
                'collected_status', 'visible_status', 'food_value', 'toxic_property',
                'hp_value', 'damage_value', 'stationary_move', 'slow_move', 'fast_move',
                'no_attack', 'passive_attack', 'active_attack', 'collectable',
                'not_collectable', 'no_escape', 'easy_escape'
            ],
            'actions': [
                'up', 'down', 'left', 'right', 'move_up', 'move_down', 'move_left',
                'move_right', 'climb', 'collect', 'gather', 'harvest', 'forage',
                'attack', 'hunt', 'defend', 'explore', 'explore_new_area', 'search',
                'investigate', 'examine', 'discover', 'observe', 'interact',
                'communicate', 'trade', 'help', 'craft', 'make_tool', 'repair', 'rest', 'mine'
            ],
            'tools': [
                'spear', 'stone', 'bow', 'basket', 'shovel', 'stick', 'net', 'pickaxe', 'hands', 'none'
            ],
            'results': [
                'success', 'failure', 'hp_increase_5', 'hp_increase_10', 'hp_decrease_5',
                'hp_decrease_8', 'hp_decrease_15', 'hp_decrease_30', 'food_increase_5',
                'food_increase_15', 'food_increase_20', 'food_increase_25', 'food_increase_30',
                'food_increase_50', 'food_increase_60', 'water_increase_10', 'water_increase_15',
                'position_change_x_plus_1', 'position_change_x_minus_1', 'position_change_y_plus_1',
                'position_change_y_minus_1', 'position_change_climb_tree', 'vision_enhancement',
                'discover_new_area', 'discover_resource', 'gain_experience', 'map_expansion',
                'gain_item', 'lose_item', 'stay_alive', 'death', 'poisoned'
            ]
        }

    def trigger_systematic_eocatr_rule_generation(self) -> Dict[str, Any]:
        """
        触发系统性EOCATR规律生成
        协调BPM进行完整矩阵规律生成
        
        Returns:
            生成触发结果和配置信息
        """
        try:
            # 获取EOCATR矩阵配置
            matrix_config = self.initialize_eocatr_matrix_config()
            
            # 计算预期规律数量
            expected_counts = {
                'EAR': len(matrix_config['environments']) * len(matrix_config['actions']) * len(matrix_config['results']),
                'ETR': len(matrix_config['environments']) * len(matrix_config['tools']) * len(matrix_config['results']),
                'OAR': len(matrix_config['objects']) * len(matrix_config['actions']) * len(matrix_config['results']),
                'OTR': len(matrix_config['objects']) * len(matrix_config['tools']) * len(matrix_config['results']),
                'CAR': len(matrix_config['attributes']) * len(matrix_config['actions']) * len(matrix_config['results']),
                'CTR': len(matrix_config['attributes']) * len(matrix_config['tools']) * len(matrix_config['results'])
            }
            
            total_expected = sum(expected_counts.values())
            
            # 记录配置信息到决策库
            config_decision = Decision(
                decision_id=f"EOCATR_CONFIG_{int(time.time())}",
                context={
                    'action_type': 'eocatr_matrix_config',
                    'matrix_dimensions': {key: len(values) for key, values in matrix_config.items()},
                    'expected_rule_counts': expected_counts,
                    'total_expected_rules': total_expected
                },
                action='initialize_eocatr_matrix',
                confidence=1.0,
                source='five_library_system'
            )
            
            # 添加到决策库
            self.add_decision_to_library(config_decision)
            
            logger.info(f"EOCATR matrix configuration ready, expected to generate {total_expected} basic rules")
            
            return {
                'status': 'success',
                'message': f'EOCATR matrix configuration ready, expected to generate {total_expected} basic rules',
                'matrix_config': matrix_config,
                'expected_counts': expected_counts,
                'total_expected': total_expected,
                'config_decision_id': config_decision.decision_id
            }
            
        except Exception as e:
            error_msg = f'EOCATR规律生成触发失败: {str(e)}'
            logger.error(error_msg)
            
            return {
                'status': 'error',
                'message': error_msg,
                'error_detail': str(e)
            }

    def get_eocatr_matrix_statistics(self) -> Dict[str, Any]:
        """
        获取EOCATR矩阵统计信息
        
        Returns:
            矩阵配置和使用统计
        """
        try:
            matrix_config = self.initialize_eocatr_matrix_config()
            
            # 计算矩阵维度
            matrix_dimensions = {key: len(values) for key, values in matrix_config.items()}
            
            # 计算理论规律数量
            theoretical_counts = {
                'EAR': matrix_dimensions['environments'] * matrix_dimensions['actions'] * matrix_dimensions['results'],
                'ETR': matrix_dimensions['environments'] * matrix_dimensions['tools'] * matrix_dimensions['results'],
                'OAR': matrix_dimensions['objects'] * matrix_dimensions['actions'] * matrix_dimensions['results'],
                'OTR': matrix_dimensions['objects'] * matrix_dimensions['tools'] * matrix_dimensions['results'],
                'CAR': matrix_dimensions['attributes'] * matrix_dimensions['actions'] * matrix_dimensions['results'],
                'CTR': matrix_dimensions['attributes'] * matrix_dimensions['tools'] * matrix_dimensions['results']
            }
            
            total_theoretical = sum(theoretical_counts.values())
            
            # 查询已存储的EOCATR相关决策
            eocatr_decisions = self.query_decisions(
                context={'action_type': 'eocatr_matrix_config'}, 
                limit=10
            )
            
            # 统计直接经验库中的EOCATR经验
            try:
                direct_experiences_count = self.db_managers['direct_experiences'].execute_query(
                    "SELECT COUNT(*) as count FROM experiences"
                )[0]['count']
            except:
                # 如果表不存在，使用0
                direct_experiences_count = 0
            
            return {
                'matrix_dimensions': matrix_dimensions,
                'theoretical_rule_counts': theoretical_counts,
                'total_theoretical_rules': total_theoretical,
                'eocatr_config_decisions': len(eocatr_decisions.get('decisions', [])),
                'direct_experiences_count': direct_experiences_count,
                'configuration_timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'error': f'获取EOCATR矩阵统计失败: {str(e)}',
                'configuration_timestamp': time.time()
            }

    def validate_eocatr_matrix_completeness(self, bmp_statistics: Dict = None) -> Dict[str, Any]:
        """
        验证EOCATR矩阵完整性
        
        Args:
            bmp_statistics: BPM系统的统计信息（可选）
            
        Returns:
            完整性验证结果
        """
        try:
            # 获取理论期望
            matrix_stats = self.get_eocatr_matrix_statistics()
            total_theoretical = matrix_stats['total_theoretical_rules']
            theoretical_counts = matrix_stats['theoretical_rule_counts']
            
            validation_result = {
                'total_theoretical_rules': total_theoretical,
                'theoretical_breakdown': theoretical_counts,
                'completeness_check': {
                    'status': 'pending',
                    'coverage_percentage': 0.0,
                    'missing_rule_types': [],
                    'implemented_rule_types': []
                }
            }
            
            if bmp_statistics:
                # 如果提供了BPM统计信息，进行详细对比
                bmp_systematic = bmp_statistics.get('systematic_eocatr_rules', {})
                bmp_total_systematic = bmp_systematic.get('candidate', 0) + bmp_systematic.get('validated', 0)
                
                coverage_percentage = (bmp_total_systematic / total_theoretical) * 100 if total_theoretical > 0 else 0
                
                validation_result['completeness_check'] = {
                    'status': 'completed',
                    'coverage_percentage': coverage_percentage,
                    'bmp_systematic_rules': bmp_total_systematic,
                    'coverage_assessment': 'excellent' if coverage_percentage > 90 else 
                                         'good' if coverage_percentage > 70 else
                                         'moderate' if coverage_percentage > 50 else 'low'
                }
                
                # 分析各类型覆盖情况
                bmp_by_type = bmp_systematic.get('by_type', {})
                for rule_type in ['conditional', 'tool_effectiveness', 'causal']:
                    type_count = bmp_by_type.get(rule_type, {})
                    total_type_count = type_count.get('candidate', 0) + type_count.get('validated', 0)
                    
                    if total_type_count > 0:
                        validation_result['completeness_check']['implemented_rule_types'].append(rule_type)
                    else:
                        validation_result['completeness_check']['missing_rule_types'].append(rule_type)
            
            return validation_result
            
        except Exception as e:
            return {
                'error': f'EOCATR矩阵完整性验证失败: {str(e)}',
                'validation_timestamp': time.time()
            }

    def _initialize_sync_tracker(self):
        """初始化同步状态跟踪器"""
        try:
            # 获取总经验库中所有已同步的经验哈希
            total_hashes = self.db_managers['total_experiences'].execute_query(
                "SELECT content_hash FROM total_experiences"
            )
            
            for record in total_hashes:
                self.sync_tracker['synced_experience_hashes'].add(record['content_hash'])
            
            logger.info(f"📊 Sync tracker initialized: {len(self.sync_tracker['synced_experience_hashes'])} experiences synced")
            
        except Exception as e:
            logger.warning(f"⚠️ Sync tracker initialization failed: {e}")

    def _smart_sync_experience(self, content_hash: str, action: str):
        """
        智能同步经验：只同步真正需要同步的经验
        
        Args:
            content_hash: 经验内容哈希
            action: 操作类型 ('added', 'updated')
        """
        try:
            # 1. 检查是否已经同步过
            if content_hash in self.sync_tracker['synced_experience_hashes']:
                # 如果是更新操作，检查是否需要重新同步
                if action == 'updated':
                    # 检查更新是否显著（例如occurrence_count变化超过阈值）
                    if self._should_resync_updated_experience(content_hash):
                        logger.debug(f"🔄 经验需要重新同步: {content_hash[:16]}...")
                        self._add_to_pending_sync(content_hash)
                    else:
                        logger.debug(f"⏭️ 跳过重复同步: {content_hash[:16]}...")
                        return
                else:
                    logger.debug(f"⏭️ 经验已同步，跳过: {content_hash[:16]}...")
                    return
            
            # 2. 新经验或需要重新同步的经验
            if action == 'added':
                # 立即同步新经验
                sync_result = self.sync_experience_to_total_library(content_hash)
                if sync_result['success']:
                    self.sync_tracker['synced_experience_hashes'].add(content_hash)
                    logger.debug(f"✅ 新经验立即同步: {sync_result['action']} - {content_hash[:16]}...")
                else:
                    logger.warning(f"❌ New experience sync failed: {content_hash[:16]}...")
            else:
                # 更新的经验加入待同步队列
                self._add_to_pending_sync(content_hash)
            
            # 3. 检查是否需要批量同步
            self._check_and_perform_batch_sync()
            
        except Exception as e:
            logger.warning(f"⚠️ Smart sync failed: {e}")
    
    def _should_resync_updated_experience(self, content_hash: str) -> bool:
        """
        判断更新的经验是否需要重新同步
        
        Args:
            content_hash: 经验内容哈希
            
        Returns:
            是否需要重新同步
        """
        try:
            # 获取直接经验库中的记录
            direct_record = self.db_managers['direct_experiences'].execute_query(
                "SELECT occurrence_count, last_seen_time FROM direct_experiences WHERE content_hash = ?", 
                (content_hash,)
            )
            
            # 获取总经验库中的记录
            total_record = self.db_managers['total_experiences'].execute_query(
                "SELECT occurrence_count, last_seen_time FROM total_experiences WHERE content_hash = ?", 
                (content_hash,)
            )
            
            if not direct_record or not total_record:
                return True  # 如果记录不存在，需要同步
            
            direct_count = direct_record[0]['occurrence_count']
            total_count = total_record[0]['occurrence_count']
            
            # 如果occurrence_count差异超过5，或者时间差异超过1小时，则需要重新同步
            count_diff = abs(direct_count - total_count)
            time_diff = abs(direct_record[0]['last_seen_time'] - total_record[0]['last_seen_time'])
            
            return count_diff >= 5 or time_diff >= 3600
            
        except Exception as e:
            logger.debug(f"检查重新同步需求失败: {e}")
            return False  # 出错时不重新同步，避免过度同步
    
    def _add_to_pending_sync(self, content_hash: str):
        """将经验哈希添加到待同步队列"""
        self.sync_tracker['pending_sync_hashes'].add(content_hash)
        logger.debug(f"📋 添加到待同步队列: {content_hash[:16]}... (队列长度: {len(self.sync_tracker['pending_sync_hashes'])})")
    
    def _check_and_perform_batch_sync(self):
        """检查并执行批量同步"""
        current_time = time.time()
        pending_count = len(self.sync_tracker['pending_sync_hashes'])
        time_since_last_sync = current_time - self.sync_tracker['last_sync_check']
        
        # 条件1：待同步队列达到批量大小
        # 条件2：距离上次同步超过间隔时间且有待同步项目
        should_sync = (
            pending_count >= self.sync_tracker['sync_batch_size'] or
            (time_since_last_sync >= self.sync_tracker['sync_interval'] and pending_count > 0)
        )
        
        if should_sync:
            logger.info(f"🚀 Batch sync: {pending_count} experiences")  # Simplified log
            self._perform_batch_sync()
            self.sync_tracker['last_sync_check'] = current_time
    
    def _perform_batch_sync(self):
        """执行批量同步"""
        if not self.sync_tracker['pending_sync_hashes']:
            return
        
        sync_count = 0
        failed_count = 0
        
        # 复制待同步集合，避免在迭代时修改
        pending_hashes = self.sync_tracker['pending_sync_hashes'].copy()
        self.sync_tracker['pending_sync_hashes'].clear()
        
        for content_hash in pending_hashes:
            try:
                sync_result = self.sync_experience_to_total_library(content_hash)
                if sync_result['success']:
                    self.sync_tracker['synced_experience_hashes'].add(content_hash)
                    sync_count += 1
                else:
                    failed_count += 1
                    # 失败的重新加入待同步队列
                    self.sync_tracker['pending_sync_hashes'].add(content_hash)
                    
            except Exception as e:
                failed_count += 1
                logger.warning(f"批量同步失败: {content_hash[:16]}... - {e}")
                # 失败的重新加入待同步队列
                self.sync_tracker['pending_sync_hashes'].add(content_hash)
        
        logger.info(f"📊 Sync completed: {sync_count} successful/{failed_count} failed")  # Simplified log

# 测试函数
def test_five_library_system():
    """测试五库系统基础功能"""
    print("🧪 测试五库系统基础功能")
    
    # 创建系统实例
    system = FiveLibrarySystem()
    
    # 获取统计信息
    stats = system.get_system_statistics()
    print(f"📊 系统统计: {stats}")
    
    # 测试数据库连接
    for name, db_manager in system.db_managers.items():
        try:
            result = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            table_count = len(result)
            print(f"✅ {name}: {table_count} 个表")
        except Exception as e:
            print(f"❌ {name}: 连接失败 - {str(e)}")
    
    print("✅ 五库系统基础测试完成")

if __name__ == "__main__":
    test_five_library_system() 