"""
经验存储系统（Experience Storage System）

基于斯坦福4.0文档的多层次经验存储架构，包括：
1. 直接经验库：存储智能体直接交互获得的经验
2. 间接经验库：存储从他人分享、观察学习等获得的经验
3. 规律库：存储从经验中提取和验证的规律

作者：AI生存游戏项目组
版本：1.3.0
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from enum import Enum
from collections import defaultdict, deque
import threading
import os


class ExperienceType(Enum):
    """经验类型枚举"""
    DIRECT = "direct"           # 直接经验：智能体直接交互获得
    INDIRECT = "indirect"       # 间接经验：从他人学习获得
    OBSERVED = "observed"       # 观察经验：观察他人行为获得
    SIMULATED = "simulated"     # 模拟经验：通过模拟推理获得
    TRANSFERRED = "transferred" # 迁移经验：从相似情境迁移获得


class ExperienceSource(Enum):
    """经验来源枚举"""
    SELF_ACTION = "self_action"         # 自身行动结果
    PEER_SHARING = "peer_sharing"       # 同伴分享
    EXPERT_TEACHING = "expert_teaching" # 专家教授
    OBSERVATION = "observation"         # 观察学习
    SIMULATION = "simulation"           # 仿真实验
    TRANSFER = "transfer"               # 经验迁移
    LITERATURE = "literature"           # 文献知识


class ExperienceReliability(Enum):
    """经验可靠性等级"""
    VERY_LOW = "very_low"       # 非常低 (0.0-0.2)
    LOW = "low"                 # 低 (0.2-0.4)
    MEDIUM = "medium"           # 中等 (0.4-0.6)
    HIGH = "high"               # 高 (0.6-0.8)
    VERY_HIGH = "very_high"     # 非常高 (0.8-1.0)


@dataclass
class ExperienceMetadata:
    """经验元数据"""
    experience_id: str              # 经验唯一标识
    timestamp: float               # 时间戳
    source: ExperienceSource       # 来源
    reliability: float = 0.5       # 可靠性 (0.0-1.0)
    context_tags: List[str] = field(default_factory=list)  # 上下文标签
    emotional_valence: float = 0.0  # 情感效价 (-1.0到1.0)
    importance_score: float = 0.5   # 重要性评分 (0.0-1.0)
    sharing_allowed: bool = True    # 是否允许分享
    
    def get_reliability_level(self) -> ExperienceReliability:
        """获取可靠性等级"""
        if self.reliability < 0.2:
            return ExperienceReliability.VERY_LOW
        elif self.reliability < 0.4:
            return ExperienceReliability.LOW
        elif self.reliability < 0.6:
            return ExperienceReliability.MEDIUM
        elif self.reliability < 0.8:
            return ExperienceReliability.HIGH
        else:
            return ExperienceReliability.VERY_HIGH


@dataclass
class ExperienceEntry:
    """经验条目基类"""
    metadata: ExperienceMetadata
    context: Dict[str, Any]        # 情境上下文
    action: Dict[str, Any]         # 行动信息
    result: Dict[str, Any]         # 结果信息
    outcome_quality: float = 0.0   # 结果质量 (-1.0到1.0)
    
    # 学习属性
    access_count: int = 0          # 访问次数
    last_accessed: float = 0.0     # 最后访问时间
    reference_count: int = 0       # 被引用次数
    
    # 验证状态
    verified: bool = False         # 是否已验证
    verification_attempts: int = 0  # 验证尝试次数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'metadata': asdict(self.metadata),
            'context': self.context,
            'action': self.action,
            'result': self.result,
            'outcome_quality': self.outcome_quality,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'reference_count': self.reference_count,
            'verified': self.verified,
            'verification_attempts': self.verification_attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建经验条目"""
        metadata_data = data.get('metadata', {})
        metadata = ExperienceMetadata(
            experience_id=metadata_data.get('experience_id', ''),
            timestamp=metadata_data.get('timestamp', time.time()),
            source=ExperienceSource(metadata_data.get('source', 'self_action')),
            reliability=metadata_data.get('reliability', 0.5),
            context_tags=metadata_data.get('context_tags', []),
            emotional_valence=metadata_data.get('emotional_valence', 0.0),
            importance_score=metadata_data.get('importance_score', 0.5),
            sharing_allowed=metadata_data.get('sharing_allowed', True)
        )
        
        return cls(
            metadata=metadata,
            context=data.get('context', {}),
            action=data.get('action', {}),
            result=data.get('result', {}),
            outcome_quality=data.get('outcome_quality', 0.0),
            access_count=data.get('access_count', 0),
            last_accessed=data.get('last_accessed', 0.0),
            reference_count=data.get('reference_count', 0),
            verified=data.get('verified', False),
            verification_attempts=data.get('verification_attempts', 0)
        )


class DirectExperienceDB:
    """直接经验库：存储智能体直接交互获得的经验"""
    
    def __init__(self, db_path: str = "direct_experiences.db", max_size: int = 10000):
        self.db_path = db_path
        self.max_size = max_size
        self._init_database()
        self.access_cache = deque(maxlen=1000)  # LRU缓存
        
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS direct_experiences (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    context TEXT,
                    action TEXT,
                    result TEXT,
                    outcome_quality REAL,
                    reliability REAL,
                    importance_score REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL DEFAULT 0,
                    verified BOOLEAN DEFAULT FALSE,
                    metadata TEXT
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON direct_experiences(timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_importance ON direct_experiences(importance_score)
            ''')
    
    def add_experience(self, experience: ExperienceEntry) -> bool:
        """添加直接经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO direct_experiences 
                    (id, timestamp, context, action, result, outcome_quality, 
                     reliability, importance_score, access_count, last_accessed, 
                     verified, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    experience.metadata.experience_id,
                    experience.metadata.timestamp,
                    json.dumps(experience.context),
                    json.dumps(experience.action),
                    json.dumps(experience.result),
                    experience.outcome_quality,
                    experience.metadata.reliability,
                    experience.metadata.importance_score,
                    experience.access_count,
                    experience.last_accessed,
                    experience.verified,
                    json.dumps(self._serialize_metadata(experience.metadata))
                ))
            
            # 内存管理：删除最旧的经验
            self._cleanup_old_experiences()
            return True
            
        except Exception as e:
            print(f"添加直接经验失败: {e}")
            return False
    
    def get_experience(self, experience_id: str) -> Optional[ExperienceEntry]:
        """获取指定经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM direct_experiences WHERE id = ?
                ''', (experience_id,))
                row = cursor.fetchone()
                
                if row:
                    # 更新访问统计
                    conn.execute('''
                        UPDATE direct_experiences 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE id = ?
                    ''', (time.time(), experience_id))
                    
                    return self._row_to_experience(row)
                return None
                
        except Exception as e:
            print(f"获取直接经验失败: {e}")
            return None
    
    def search_experiences(self, 
                          context_filter: Dict[str, Any] = None,
                          time_range: Tuple[float, float] = None,
                          min_importance: float = 0.0,
                          limit: int = 100) -> List[ExperienceEntry]:
        """搜索直接经验"""
        try:
            query = "SELECT * FROM direct_experiences WHERE 1=1"
            params = []
            
            if time_range:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend(time_range)
            
            if min_importance > 0:
                query += " AND importance_score >= ?"
                params.append(min_importance)
            
            query += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                experiences = []
                for row in rows:
                    exp = self._row_to_experience(row)
                    if exp and self._matches_context_filter(exp, context_filter):
                        experiences.append(exp)
                
                return experiences
                
        except Exception as e:
            print(f"搜索直接经验失败: {e}")
            return []
    
    def _row_to_experience(self, row) -> ExperienceEntry:
        """将数据库行转换为经验对象"""
        metadata_data = json.loads(row[11])
        metadata = ExperienceMetadata(
            experience_id=metadata_data['experience_id'],
            timestamp=metadata_data['timestamp'],
            source=ExperienceSource(metadata_data['source']),
            reliability=metadata_data['reliability'],
            context_tags=metadata_data['context_tags'],
            emotional_valence=metadata_data['emotional_valence'],
            importance_score=metadata_data['importance_score'],
            sharing_allowed=metadata_data['sharing_allowed']
        )
        
        return ExperienceEntry(
            metadata=metadata,
            context=json.loads(row[2]),
            action=json.loads(row[3]),
            result=json.loads(row[4]),
            outcome_quality=row[5],
            access_count=row[8],
            last_accessed=row[9],
            verified=bool(row[10])
        )
    
    def _matches_context_filter(self, experience: ExperienceEntry, 
                               context_filter: Dict[str, Any]) -> bool:
        """检查经验是否匹配上下文过滤器"""
        if not context_filter:
            return True
        
        for key, value in context_filter.items():
            if key not in experience.context or experience.context[key] != value:
                return False
        return True
    
    def _cleanup_old_experiences(self):
        """清理旧经验以控制内存使用"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM direct_experiences')
                count = cursor.fetchone()[0]
                
                if count > self.max_size:
                    # 删除最旧且重要性最低的经验
                    delete_count = count - self.max_size
                    conn.execute('''
                        DELETE FROM direct_experiences WHERE id IN (
                            SELECT id FROM direct_experiences 
                            ORDER BY importance_score ASC, timestamp ASC 
                            LIMIT ?
                        )
                    ''', (delete_count,))
                    
        except Exception as e:
            print(f"清理旧经验失败: {e}")
    
    def _serialize_metadata(self, metadata: ExperienceMetadata) -> dict:
        """安全序列化元数据，处理枚举类型"""
        metadata_dict = asdict(metadata)
        # 将枚举转换为字符串
        if isinstance(metadata_dict.get('source'), ExperienceSource):
            metadata_dict['source'] = metadata_dict['source'].value
        elif hasattr(metadata_dict.get('source'), 'value'):
            metadata_dict['source'] = metadata_dict['source'].value
        else:
            metadata_dict['source'] = str(metadata_dict.get('source', 'self_action'))
        return metadata_dict

    def store_experience(self, experience_dict: dict) -> bool:
        """兼容性方法：将字典格式经验转换为ExperienceEntry对象然后保存"""
        try:
            # 创建元数据
            metadata = ExperienceMetadata(
                experience_id=experience_dict.get('id', f"exp_{int(time.time())}"),
                timestamp=experience_dict.get('timestamp', time.time()),
                source=ExperienceSource.SELF_ACTION,
                reliability=0.8,  # 直接经验有较高可靠性
                importance_score=experience_dict.get('importance_score', 0.5)
            )
            
            # 处理字符串格式的数据
            context = experience_dict.get('context', {})
            if isinstance(context, str):
                context = {'description': context}
                
            action = experience_dict.get('action', {})
            if isinstance(action, str):
                action = {'action_type': action}
                
            result = experience_dict.get('result', {})
            if isinstance(result, str):
                result = {'outcome': result}
            
            # 创建经验条目
            experience_entry = ExperienceEntry(
                metadata=metadata,
                context=context,
                action=action,
                result=result,
                outcome_quality=experience_dict.get('outcome_quality', 0.0)
            )
            
            return self.add_experience(experience_entry)
            
        except Exception as e:
            print(f"store_experience转换失败: {e}")
            return False


class IndirectExperienceDB:
    """间接经验库：存储从他人分享、观察学习等获得的经验"""
    
    def __init__(self, db_path: str = "indirect_experiences.db", max_size: int = 5000):
        self.db_path = db_path
        self.max_size = max_size
        self._init_database()
        self.trust_network: Dict[str, float] = {}  # 信任网络
        
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS indirect_experiences (
                    id TEXT PRIMARY KEY,
                    source_agent TEXT,
                    trust_score REAL,
                    timestamp REAL,
                    context TEXT,
                    action TEXT,
                    result TEXT,
                    outcome_quality REAL,
                    reliability REAL,
                    verification_status TEXT,
                    metadata TEXT
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_agent ON indirect_experiences(source_agent)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_trust_score ON indirect_experiences(trust_score)
            ''')
    
    def add_shared_experience(self, experience: ExperienceEntry, 
                             source_agent: str, trust_score: float) -> bool:
        """添加来自他人分享的经验"""
        try:
            # 根据信任度调整可靠性
            adjusted_reliability = experience.metadata.reliability * trust_score
            experience.metadata.reliability = min(adjusted_reliability, 1.0)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO indirect_experiences 
                    (id, source_agent, trust_score, timestamp, context, action, 
                     result, outcome_quality, reliability, verification_status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    experience.metadata.experience_id,
                    source_agent,
                    trust_score,
                    experience.metadata.timestamp,
                    json.dumps(experience.context),
                    json.dumps(experience.action),
                    json.dumps(experience.result),
                    experience.outcome_quality,
                    experience.metadata.reliability,
                    'pending',
                    json.dumps(asdict(experience.metadata))
                ))
            
            # 更新信任网络
            self.trust_network[source_agent] = trust_score
            self._cleanup_old_experiences()
            return True
            
        except Exception as e:
            print(f"添加间接经验失败: {e}")
            return False
    
    def get_high_trust_experiences(self, min_trust: float = 0.7, 
                                  limit: int = 100) -> List[ExperienceEntry]:
        """获取高信任度的间接经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM indirect_experiences 
                    WHERE trust_score >= ?
                    ORDER BY trust_score DESC, timestamp DESC
                    LIMIT ?
                ''', (min_trust, limit))
                
                experiences = []
                for row in cursor.fetchall():
                    exp = self._row_to_experience(row)
                    if exp:
                        experiences.append(exp)
                
                return experiences
                
        except Exception as e:
            print(f"获取高信任经验失败: {e}")
            return []
    
    def update_trust_score(self, source_agent: str, new_trust: float):
        """更新对某个智能体的信任度"""
        try:
            self.trust_network[source_agent] = max(0.0, min(1.0, new_trust))
            
            # 更新该智能体相关经验的信任度
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE indirect_experiences 
                    SET trust_score = ? 
                    WHERE source_agent = ?
                ''', (new_trust, source_agent))
                
        except Exception as e:
            print(f"更新信任度失败: {e}")
    
    def _row_to_experience(self, row) -> ExperienceEntry:
        """将数据库行转换为经验对象"""
        try:
            metadata_data = json.loads(row[10])
            metadata = ExperienceMetadata(
                experience_id=metadata_data['experience_id'],
                timestamp=metadata_data['timestamp'],
                source=ExperienceSource(metadata_data['source']),
                reliability=metadata_data['reliability'],
                context_tags=metadata_data['context_tags'],
                emotional_valence=metadata_data['emotional_valence'],
                importance_score=metadata_data['importance_score'],
                sharing_allowed=metadata_data['sharing_allowed']
            )
            
            return ExperienceEntry(
                metadata=metadata,
                context=json.loads(row[4]),
                action=json.loads(row[5]),
                result=json.loads(row[6]),
                outcome_quality=row[7]
            )
        except Exception as e:
            print(f"转换间接经验失败: {e}")
            return None
    
    def _cleanup_old_experiences(self):
        """清理旧的间接经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM indirect_experiences')
                count = cursor.fetchone()[0]
                
                if count > self.max_size:
                    delete_count = count - self.max_size
                    # 优先删除低信任度和旧时间的经验
                    conn.execute('''
                        DELETE FROM indirect_experiences WHERE id IN (
                            SELECT id FROM indirect_experiences 
                            ORDER BY trust_score ASC, timestamp ASC 
                            LIMIT ?
                        )
                    ''', (delete_count,))
                    
        except Exception as e:
            print(f"清理间接经验失败: {e}")


class RuleKnowledgeDB:
    """规律库：存储从经验中提取和验证的规律"""
    
    def __init__(self, db_path: str = "rule_knowledge.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """初始化规律数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    rule_type TEXT,
                    pattern TEXT,
                    conditions TEXT,
                    predictions TEXT,
                    confidence REAL,
                    validation_count INTEGER,
                    success_count INTEGER,
                    created_time REAL,
                    last_updated REAL,
                    source_experiences TEXT,
                    metadata TEXT
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_confidence ON rules(confidence)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_rule_type ON rules(rule_type)
            ''')
    
    def store_rule(self, rule_data: Dict[str, Any]) -> bool:
        """存储规律"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO rules 
                    (id, rule_type, pattern, conditions, predictions, confidence,
                     validation_count, success_count, created_time, last_updated,
                     source_experiences, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule_data['id'],
                    rule_data['rule_type'],
                    rule_data['pattern'],
                    json.dumps(rule_data['conditions']),
                    json.dumps(rule_data['predictions']),
                    rule_data['confidence'],
                    rule_data.get('validation_count', 0),
                    rule_data.get('success_count', 0),
                    rule_data.get('created_time', time.time()),
                    time.time(),
                    json.dumps(rule_data.get('source_experiences', [])),
                    json.dumps(rule_data.get('metadata', {}))
                ))
            return True
            
        except Exception as e:
            print(f"存储规律失败: {e}")
            return False
    
    def get_rules_by_confidence(self, min_confidence: float = 0.5,
                               rule_type: str = None, limit: int = 100) -> List[Dict]:
        """按置信度获取规律"""
        try:
            query = "SELECT * FROM rules WHERE confidence >= ?"
            params = [min_confidence]
            
            if rule_type:
                query += " AND rule_type = ?"
                params.append(rule_type)
            
            query += " ORDER BY confidence DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rules = []
                
                for row in cursor.fetchall():
                    rule = {
                        'id': row[0],
                        'rule_type': row[1],
                        'pattern': row[2],
                        'conditions': json.loads(row[3]),
                        'predictions': json.loads(row[4]),
                        'confidence': row[5],
                        'validation_count': row[6],
                        'success_count': row[7],
                        'created_time': row[8],
                        'last_updated': row[9],
                        'source_experiences': json.loads(row[10]),
                        'metadata': json.loads(row[11])
                    }
                    rules.append(rule)
                
                return rules
                
        except Exception as e:
            print(f"获取规律失败: {e}")
            return []


class ExperienceStorageSystem:
    """经验存储系统主类"""
    
    def __init__(self, base_path: str = "./experience_data/"):
        """初始化经验存储系统"""
        os.makedirs(base_path, exist_ok=True)
        
        # 初始化三个数据库
        self.direct_db = DirectExperienceDB(
            db_path=os.path.join(base_path, "direct_experiences.db")
        )
        self.indirect_db = IndirectExperienceDB(
            db_path=os.path.join(base_path, "indirect_experiences.db")
        )
        self.rule_db = RuleKnowledgeDB(
            db_path=os.path.join(base_path, "rule_knowledge.db")
        )
        
        # 统计信息
        self.stats = {
            'direct_experiences_count': 0,
            'indirect_experiences_count': 0,
            'rules_count': 0,
            'last_updated': time.time()
        }
        
        self._lock = threading.Lock()
    
    def add_direct_experience(self, context: Dict[str, Any], 
                             action: Dict[str, Any], 
                             result: Dict[str, Any],
                             outcome_quality: float = 0.0,
                             importance: float = 0.5) -> str:
        """添加直接经验"""
        with self._lock:
            experience_id = f"direct_{int(time.time() * 1000)}"
            
            metadata = ExperienceMetadata(
                experience_id=experience_id,
                timestamp=time.time(),
                source=ExperienceSource.SELF_ACTION,
                reliability=0.9,  # 直接经验可靠性高
                importance_score=importance
            )
            
            experience = ExperienceEntry(
                metadata=metadata,
                context=context,
                action=action,
                result=result,
                outcome_quality=outcome_quality
            )
            
            success = self.direct_db.add_experience(experience)
            if success:
                self.stats['direct_experiences_count'] += 1
                self._update_stats()
                
            return experience_id if success else None
    
    def add_shared_experience(self, context: Dict[str, Any],
                             action: Dict[str, Any],
                             result: Dict[str, Any],
                             source_agent: str,
                             trust_score: float,
                             outcome_quality: float = 0.0) -> str:
        """添加他人分享的经验"""
        with self._lock:
            experience_id = f"shared_{source_agent}_{int(time.time() * 1000)}"
            
            metadata = ExperienceMetadata(
                experience_id=experience_id,
                timestamp=time.time(),
                source=ExperienceSource.PEER_SHARING,
                reliability=0.6 * trust_score  # 根据信任度调整可靠性
            )
            
            experience = ExperienceEntry(
                metadata=metadata,
                context=context,
                action=action,
                result=result,
                outcome_quality=outcome_quality
            )
            
            success = self.indirect_db.add_shared_experience(experience, source_agent, trust_score)
            if success:
                self.stats['indirect_experiences_count'] += 1
                self._update_stats()
                
            return experience_id if success else None
    
    def get_relevant_experiences(self, 
                                context_filter: Dict[str, Any] = None,
                                include_indirect: bool = True,
                                min_importance: float = 0.3,
                                limit: int = 50) -> List[ExperienceEntry]:
        """获取相关经验"""
        experiences = []
        
        # 获取直接经验
        direct_exp = self.direct_db.search_experiences(
            context_filter=context_filter,
            min_importance=min_importance,
            limit=limit//2
        )
        experiences.extend(direct_exp)
        
        # 获取间接经验（如果需要）
        if include_indirect:
            indirect_exp = self.indirect_db.get_high_trust_experiences(
                min_trust=0.6,
                limit=limit//2
            )
            # 过滤符合条件的间接经验
            for exp in indirect_exp:
                if self.direct_db._matches_context_filter(exp, context_filter):
                    experiences.append(exp)
        
        # 按重要性和时间排序
        experiences.sort(key=lambda x: (x.metadata.importance_score, x.metadata.timestamp), 
                        reverse=True)
        
        return experiences[:limit]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        with self._lock:
            # 实时统计
            try:
                with sqlite3.connect(self.direct_db.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM direct_experiences')
                    direct_count = cursor.fetchone()[0]
                
                with sqlite3.connect(self.indirect_db.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM indirect_experiences')
                    indirect_count = cursor.fetchone()[0]
                
                with sqlite3.connect(self.rule_db.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM rules')
                    rules_count = cursor.fetchone()[0]
                
                return {
                    'direct_experiences': direct_count,
                    'indirect_experiences': indirect_count,
                    'validated_rules': rules_count,
                    'total_experiences': direct_count + indirect_count,
                    'last_updated': self.stats['last_updated'],
                    'storage_efficiency': {
                        'direct_db_size': os.path.getsize(self.direct_db.db_path) if os.path.exists(self.direct_db.db_path) else 0,
                        'indirect_db_size': os.path.getsize(self.indirect_db.db_path) if os.path.exists(self.indirect_db.db_path) else 0,
                        'rules_db_size': os.path.getsize(self.rule_db.db_path) if os.path.exists(self.rule_db.db_path) else 0
                    }
                }
                
            except Exception as e:
                print(f"获取统计信息失败: {e}")
                return self.stats
    
    def _update_stats(self):
        """更新统计信息"""
        self.stats['last_updated'] = time.time()

    def optimize_knowledge_conversion(self):
        """优化知识转化机制"""
        try:
            # 1. 分析经验质量
            self._analyze_experience_quality()
            
            # 2. 增强经验关联
            self._enhance_experience_associations()
            
            # 3. 提取通用模式
            self._extract_common_patterns()
            
            # 4. 生成知识摘要
            self._generate_knowledge_summaries()
            
            if self.logger:
                self.logger.log("知识转化机制优化完成")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"知识转化优化失败: {str(e)}")
    
    def _analyze_experience_quality(self):
        """分析经验质量"""
        try:
            quality_metrics = {
                'high_value_experiences': 0,
                'redundant_experiences': 0,
                'low_quality_experiences': 0,
                'unique_patterns': set()
            }
            
            # 分析直接经验质量
            for exp_id, experience in self.direct_db.items():
                # 评估经验价值
                value_score = self._calculate_experience_value(experience)
                
                if value_score > 0.8:
                    quality_metrics['high_value_experiences'] += 1
                elif value_score < 0.3:
                    quality_metrics['low_quality_experiences'] += 1
                
                # 检查是否为冗余经验
                if self._is_redundant_experience(experience):
                    quality_metrics['redundant_experiences'] += 1
                
                # 提取模式
                pattern = self._extract_experience_pattern(experience)
                if pattern:
                    quality_metrics['unique_patterns'].add(pattern)
            
            self.quality_metrics = quality_metrics
            
            if self.logger:
                self.logger.log(f"经验质量分析: 高价值={quality_metrics['high_value_experiences']}, "
                              f"冗余={quality_metrics['redundant_experiences']}, "
                              f"独特模式={len(quality_metrics['unique_patterns'])}")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"经验质量分析失败: {str(e)}")
    
    def _calculate_experience_value(self, experience: ExperienceEntry) -> float:
        """计算经验价值"""
        try:
            value_score = 0.0
            
            # 基于重要性评分
            value_score += experience.metadata.importance_score * 0.3
            
            # 基于访问频率
            if experience.access_count > 0:
                value_score += min(0.3, experience.access_count * 0.05)
            
            # 基于成功率
            if hasattr(experience, 'outcome_quality') and experience.outcome_quality:
                success = experience.outcome_quality > 0.0
                value_score += 0.2 if success else 0.0
            
            # 基于新颖性
            current_time = time.time()
            age_hours = (current_time - experience.metadata.timestamp) / 3600
            novelty_factor = max(0.0, 1.0 - age_hours / (24 * 7))  # 一周内的新颖性
            value_score += novelty_factor * 0.2
            
            return min(1.0, value_score)
            
        except Exception:
            return 0.5  # 默认中等价值
    
    def _is_redundant_experience(self, experience: ExperienceEntry) -> bool:
        """检查经验是否冗余"""
        try:
            # 简化的冗余检测：检查相似的context和action组合
            similar_count = 0
            
            for other_exp in self.direct_db.items():
                if other_exp.experience_id == experience.experience_id:
                    continue
                
                # 检查context相似性
                context_similarity = self._calculate_context_similarity(
                    experience.context, other_exp.context
                )
                
                # 检查action相似性
                action_similarity = 1.0 if experience.action == other_exp.action else 0.0
                
                if context_similarity > 0.8 and action_similarity > 0.8:
                    similar_count += 1
                    
                    if similar_count >= 3:  # 超过3个相似经验视为冗余
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """计算上下文相似性"""
        try:
            if not context1 or not context2:
                return 0.0
            
            # 获取共同键
            common_keys = set(context1.keys()) & set(context2.keys())
            if not common_keys:
                return 0.0
            
            # 计算值相似性
            similarity_sum = 0.0
            for key in common_keys:
                val1, val2 = context1[key], context2[key]
                
                if val1 == val2:
                    similarity_sum += 1.0
                elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # 数值相似性
                    if val1 != 0 and val2 != 0:
                        similarity_sum += 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2))
                elif isinstance(val1, str) and isinstance(val2, str):
                    # 字符串相似性（简化）
                    similarity_sum += 1.0 if val1.lower() == val2.lower() else 0.0
            
            return similarity_sum / len(common_keys)
            
        except Exception:
            return 0.0
    
    def _extract_experience_pattern(self, experience: ExperienceEntry) -> Optional[str]:
        """提取经验模式"""
        try:
            # 简化的模式提取：action + context关键要素
            pattern_elements = [experience.action]
            
            if experience.context:
                # 提取关键上下文要素
                key_elements = []
                for key, value in experience.context.items():
                    if key in ['health', 'food', 'water', 'position', 'danger_level']:
                        if isinstance(value, (int, float)):
                            # 数值分档
                            if value < 30:
                                level = 'low'
                            elif value > 70:
                                level = 'high'
                            else:
                                level = 'medium'
                            key_elements.append(f"{key}_{level}")
                        else:
                            key_elements.append(f"{key}_{value}")
                
                pattern_elements.extend(sorted(key_elements))
            
            return "|".join(pattern_elements) if pattern_elements else None
            
        except Exception:
            return None
    
    def _enhance_experience_associations(self):
        """增强经验关联"""
        try:
            # 建立经验之间的关联网络
            association_threshold = 0.7
            new_associations = 0
            
            experiences = list(self.direct_db.items())
            
            for i, exp1 in enumerate(experiences):
                for j, exp2 in enumerate(experiences[i+1:], i+1):
                    similarity = self._calculate_experience_similarity(exp1, exp2)
                    
                    if similarity > association_threshold:
                        # 建立双向关联
                        if exp1.experience_id not in self.experience_associations:
                            self.experience_associations[exp1.experience_id] = set()
                        if exp2.experience_id not in self.experience_associations:
                            self.experience_associations[exp2.experience_id] = set()
                        
                        self.experience_associations[exp1.experience_id].add(exp2.experience_id)
                        self.experience_associations[exp2.experience_id].add(exp1.experience_id)
                        new_associations += 1
            
            if self.logger and new_associations > 0:
                self.logger.log(f"建立了{new_associations}个新的经验关联")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"经验关联增强失败: {str(e)}")
    
    def _calculate_experience_similarity(self, exp1: ExperienceEntry, exp2: ExperienceEntry) -> float:
        """计算经验相似性"""
        try:
            similarity_score = 0.0
            
            # 行动相似性 (40%)
            action_sim = 1.0 if exp1.action == exp2.action else 0.0
            similarity_score += action_sim * 0.4
            
            # 上下文相似性 (40%)
            context_sim = self._calculate_context_similarity(exp1.context, exp2.context)
            similarity_score += context_sim * 0.4
            
            # 结果相似性 (20%)
            outcome_sim = 0.0
            if hasattr(exp1, 'outcome_quality') and hasattr(exp2, 'outcome_quality'):
                if exp1.outcome_quality and exp2.outcome_quality:
                    # 简化的结果相似性
                    success1 = exp1.outcome_quality > 0.0
                    success2 = exp2.outcome_quality > 0.0
                    outcome_sim = 1.0 if success1 == success2 else 0.0
            
            similarity_score += outcome_sim * 0.2
            
            return similarity_score
            
        except Exception:
            return 0.0
    
    def _extract_common_patterns(self):
        """提取通用模式"""
        try:
            pattern_frequency = defaultdict(int)
            pattern_success_rate = defaultdict(list)
            
            # 统计模式频率和成功率
            for experience in self.direct_db.items():
                pattern = self._extract_experience_pattern(experience)
                if pattern:
                    pattern_frequency[pattern] += 1
                    
                    # 记录成功率
                    if hasattr(experience, 'outcome_quality') and experience.outcome_quality:
                        success = experience.outcome_quality > 0.0
                        pattern_success_rate[pattern].append(1.0 if success else 0.0)
            
            # 识别高频且高成功率的模式
            valuable_patterns = {}
            min_frequency = 3  # 至少出现3次
            min_success_rate = 0.6  # 至少60%成功率
            
            for pattern, frequency in pattern_frequency.items():
                if frequency >= min_frequency:
                    success_scores = pattern_success_rate[pattern]
                    if success_scores:
                        avg_success = sum(success_scores) / len(success_scores)
                        if avg_success >= min_success_rate:
                            valuable_patterns[pattern] = {
                                'frequency': frequency,
                                'success_rate': avg_success,
                                'confidence': min(1.0, frequency * avg_success / 10)
                            }
            
            self.common_patterns = valuable_patterns
            
            if self.logger:
                self.logger.log(f"识别出{len(valuable_patterns)}个有价值的通用模式")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"通用模式提取失败: {str(e)}")
    
    def _generate_knowledge_summaries(self):
        """生成知识摘要"""
        try:
            summaries = {}
            
            # 按行动类型分组生成摘要
            action_groups = defaultdict(list)
            for experience in self.direct_db.items():
                action_groups[experience.action].append(experience)
            
            for action, experiences in action_groups.items():
                if len(experiences) >= 2:  # 至少2个经验才生成摘要
                    summary = self._create_action_summary(action, experiences)
                    summaries[action] = summary
            
            # 情境摘要
            context_summaries = self._create_context_summaries()
            summaries.update(context_summaries)
            
            self.knowledge_summaries = summaries
            
            if self.logger:
                self.logger.log(f"生成了{len(summaries)}个知识摘要")
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"知识摘要生成失败: {str(e)}")
    
    def _create_action_summary(self, action: str, experiences: List[ExperienceEntry]) -> Dict[str, Any]:
        """创建行动摘要"""
        try:
            summary = {
                'action': action,
                'total_attempts': len(experiences),
                'success_count': 0,
                'common_contexts': [],
                'best_practices': [],
                'risk_factors': []
            }
            
            success_contexts = []
            failure_contexts = []
            
            for exp in experiences:
                if hasattr(exp, 'outcome_quality') and exp.outcome_quality:
                    success = exp.outcome_quality > 0.0
                    if success:
                        summary['success_count'] += 1
                        success_contexts.append(exp.context)
                    else:
                        failure_contexts.append(exp.context)
            
            # 计算成功率
            summary['success_rate'] = summary['success_count'] / summary['total_attempts']
            
            # 分析成功情境的共同点
            if success_contexts:
                common_success_factors = self._find_common_factors(success_contexts)
                summary['best_practices'] = common_success_factors
            
            # 分析失败情境的共同点
            if failure_contexts:
                common_failure_factors = self._find_common_factors(failure_contexts)
                summary['risk_factors'] = common_failure_factors
            
            return summary
            
        except Exception:
            return {'action': action, 'error': 'summary_creation_failed'}
    
    def _find_common_factors(self, contexts: List[Dict]) -> List[str]:
        """找出上下文的共同因素"""
        try:
            if not contexts:
                return []
            
            factor_counts = defaultdict(int)
            total_contexts = len(contexts)
            
            for context in contexts:
                for key, value in context.items():
                    factor_key = f"{key}={value}"
                    factor_counts[factor_key] += 1
            
            # 返回出现频率超过50%的因素
            common_factors = []
            for factor, count in factor_counts.items():
                if count / total_contexts > 0.5:
                    common_factors.append(factor)
            
            return common_factors
            
        except Exception:
            return []
    
    def _create_context_summaries(self) -> Dict[str, Any]:
        """创建情境摘要"""
        try:
            context_summaries = {}
            
            # 基于健康状态的摘要
            health_summary = self._create_health_based_summary()
            if health_summary:
                context_summaries['health_management'] = health_summary
            
            # 基于资源状态的摘要
            resource_summary = self._create_resource_based_summary()
            if resource_summary:
                context_summaries['resource_management'] = resource_summary
            
            return context_summaries
            
        except Exception:
            return {}
    
    def _create_health_based_summary(self) -> Optional[Dict[str, Any]]:
        """创建基于健康状态的摘要"""
        try:
            health_experiences = []
            
            for exp in self.direct_db.items():
                if exp.context and 'health' in exp.context:
                    health_experiences.append(exp)
            
            if len(health_experiences) < 3:
                return None
            
            # 按健康水平分组
            low_health_actions = []
            high_health_actions = []
            
            for exp in health_experiences:
                health = exp.context.get('health', 50)
                if health < 30:
                    low_health_actions.append(exp.action)
                elif health > 70:
                    high_health_actions.append(exp.action)
            
            return {
                'type': 'health_management',
                'low_health_recommendations': list(set(low_health_actions)),
                'high_health_opportunities': list(set(high_health_actions)),
                'total_health_experiences': len(health_experiences)
            }
            
        except Exception:
            return None
    
    def _create_resource_based_summary(self) -> Optional[Dict[str, Any]]:
        """创建基于资源的摘要"""
        try:
            resource_experiences = []
            
            for exp in self.direct_db.items():
                if exp.context and ('food' in exp.context or 'water' in exp.context):
                    resource_experiences.append(exp)
            
            if len(resource_experiences) < 3:
                return None
            
            # 分析资源获取行为
            food_actions = []
            water_actions = []
            
            for exp in resource_experiences:
                if exp.context.get('food', 50) < 30:
                    food_actions.append(exp.action)
                if exp.context.get('water', 50) < 30:
                    water_actions.append(exp.action)
            
            return {
                'type': 'resource_management',
                'food_acquisition_strategies': list(set(food_actions)),
                'water_acquisition_strategies': list(set(water_actions)),
                'total_resource_experiences': len(resource_experiences)
            }
            
        except Exception:
            return None
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        try:
            # 先优化知识转化
            self.optimize_knowledge_conversion()
            
            insights = {
                'timestamp': time.time(),
                'total_experiences': len(self.direct_db),
                'quality_metrics': getattr(self, 'quality_metrics', {}),
                'common_patterns': getattr(self, 'common_patterns', {}),
                'knowledge_summaries': getattr(self, 'knowledge_summaries', {}),
                'learning_effectiveness': self._calculate_learning_effectiveness(),
                'recommendations': self._generate_learning_recommendations()
            }
            
            return insights
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"获取学习洞察失败: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_learning_effectiveness(self) -> Dict[str, float]:
        """计算学习效果"""
        try:
            effectiveness = {
                'pattern_recognition': 0.0,
                'knowledge_retention': 0.0,
                'application_success': 0.0,
                'overall_score': 0.0
            }
            
            # 模式识别能力
            if hasattr(self, 'common_patterns'):
                pattern_count = len(self.common_patterns)
                effectiveness['pattern_recognition'] = min(1.0, pattern_count / 10)
            
            # 知识保持能力
            total_experiences = len(self.direct_db)
            if total_experiences > 0:
                high_value_count = getattr(self, 'quality_metrics', {}).get('high_value_experiences', 0)
                effectiveness['knowledge_retention'] = high_value_count / total_experiences
            
            # 应用成功率
            success_count = 0
            total_count = 0
            for exp in self.direct_db.items():
                if hasattr(exp, 'outcome_quality') and exp.outcome_quality:
                    total_count += 1
                    if exp.outcome_quality > 0.0:
                        success_count += 1
            
            if total_count > 0:
                effectiveness['application_success'] = success_count / total_count
            
            # 综合评分
            effectiveness['overall_score'] = (
                effectiveness['pattern_recognition'] * 0.3 +
                effectiveness['knowledge_retention'] * 0.3 +
                effectiveness['application_success'] * 0.4
            )
            
            return effectiveness
            
        except Exception:
            return {'overall_score': 0.0, 'error': 'calculation_failed'}
    
    def _generate_learning_recommendations(self) -> List[str]:
        """生成学习建议"""
        try:
            recommendations = []
            
            # 基于质量指标的建议
            if hasattr(self, 'quality_metrics'):
                metrics = self.quality_metrics
                
                if metrics.get('redundant_experiences', 0) > 10:
                    recommendations.append("减少冗余经验记录，专注于新情境探索")
                
                if metrics.get('low_quality_experiences', 0) > metrics.get('high_value_experiences', 0):
                    recommendations.append("提高经验质量，增加成功案例的分析")
                
                if len(metrics.get('unique_patterns', set())) < 5:
                    recommendations.append("扩大行为模式多样性，尝试不同的策略")
            
            # 基于学习效果的建议
            effectiveness = self._calculate_learning_effectiveness()
            
            if effectiveness.get('pattern_recognition', 0) < 0.3:
                recommendations.append("加强模式识别训练，增加经验样本量")
            
            if effectiveness.get('application_success', 0) < 0.5:
                recommendations.append("改进行动策略，分析失败原因并调整方法")
            
            if effectiveness.get('knowledge_retention', 0) < 0.4:
                recommendations.append("重复练习重要技能，巩固核心知识")
            
            return recommendations
            
        except Exception:
            return ["学习建议生成失败，请检查系统状态"]


# 全局实例
experience_storage = ExperienceStorageSystem() 