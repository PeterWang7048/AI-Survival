"""
五库系统日志优化方案
解决经验同步日志过多的问题
"""

import time
import json
import logging
from collections import defaultdict, deque
from typing import Dict, Any, Set
from threading import Lock

class OptimizedSyncLogger:
    """优化的同步日志记录器"""
    
    def __init__(self, aggregate_interval: int = 30, max_individual_logs: int = 5):
        """
        初始化优化日志记录器
        
        Args:
            aggregate_interval: 聚合日志的时间间隔（秒）
            max_individual_logs: 单个时间窗口内最大个别日志数量
        """
        self.aggregate_interval = aggregate_interval
        self.max_individual_logs = max_individual_logs
        
        # 日志聚合数据
        self.sync_stats = {
            'merged': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0
        }
        
        # 重复日志检测
        self.recent_hashes = deque(maxlen=100)  # 最近100个哈希
        self.hash_counts = defaultdict(int)
        
        # 时间窗口管理
        self.last_aggregate_time = time.time()
        self.current_window_logs = 0
        
        # 线程安全
        self.lock = Lock()
        
        # 获取logger
        self.logger = logging.getLogger('five_library_system')
    
    def log_sync_result(self, sync_result: Dict[str, Any], content_hash: str):
        """
        记录同步结果（智能去重和聚合）
        
        Args:
            sync_result: 同步结果
            content_hash: 内容哈希
        """
        with self.lock:
            action = sync_result.get('action', 'unknown')
            
            # 1. 更新统计
            if action in self.sync_stats:
                self.sync_stats[action] += 1
            
            # 2. 检查是否需要输出个别日志
            should_log_individual = self._should_log_individual(content_hash, action)
            
            if should_log_individual:
                self._log_individual_sync(sync_result, content_hash)
                self.current_window_logs += 1
            
            # 3. 检查是否需要输出聚合日志
            self._check_and_output_aggregate()
    
    def _should_log_individual(self, content_hash: str, action: str) -> bool:
        """判断是否应该输出个别日志"""
        # 1. 如果当前窗口已达到最大个别日志数，不输出
        if self.current_window_logs >= self.max_individual_logs:
            return False
        
        # 2. 对于failed和created，总是输出（重要信息）
        if action in ['failed', 'created']:
            return True
        
        # 3. 对于merged和updated，检查是否重复
        hash_short = content_hash[:16]
        self.hash_counts[hash_short] += 1
        
        # 第一次出现总是记录
        if self.hash_counts[hash_short] == 1:
            self.recent_hashes.append(hash_short)
            return True
        
        # 重复出现但频率不高时记录（每5次记录一次）
        if self.hash_counts[hash_short] % 5 == 0:
            return True
        
        return False
    
    def _log_individual_sync(self, sync_result: Dict[str, Any], content_hash: str):
        """输出个别同步日志"""
        action = sync_result.get('action', 'unknown')
        hash_short = content_hash[:16]
        
        if action == 'failed':
            self.logger.error(f"❌ Experience sync failed: {sync_result.get('reason', 'unknown error')} - {hash_short}...")
        elif action == 'created':
            self.logger.info(f"✨ New experience created: {hash_short}... (discoverers: {sync_result.get('discoverer_count', 1)})")
        elif action == 'merged':
            count = self.hash_counts[hash_short]
            if count == 1:
                self.logger.debug(f"🔄 经验合并: {hash_short}... (累计: {sync_result.get('total_occurrence_count', 0)})")
            else:
                self.logger.debug(f"🔄 经验合并: {hash_short}... (第{count}次, 累计: {sync_result.get('total_occurrence_count', 0)})")
    
    def _check_and_output_aggregate(self):
        """检查并输出聚合日志"""
        current_time = time.time()
        
        if current_time - self.last_aggregate_time >= self.aggregate_interval:
            self._output_aggregate_stats()
            self._reset_window()
    
    def _output_aggregate_stats(self):
        """输出聚合统计日志"""
        total_syncs = sum(self.sync_stats.values())
        
        if total_syncs == 0:
            return
        
        # 构建聚合消息
        stats_parts = []
        for action, count in self.sync_stats.items():
            if count > 0:
                if action == 'merged':
                    stats_parts.append(f"合并{count}条")
                elif action == 'created':
                    stats_parts.append(f"新建{count}条")
                elif action == 'updated':
                    stats_parts.append(f"更新{count}条")
                elif action == 'failed':
                    stats_parts.append(f"失败{count}条")
                elif action == 'skipped':
                    stats_parts.append(f"跳过{count}条")
        
        if stats_parts:
            message = f"📊 经验同步汇总({self.aggregate_interval}s): " + ", ".join(stats_parts)
            
            # 根据失败数量决定日志级别
            if self.sync_stats['failed'] > 0:
                self.logger.warning(message)
            else:
                self.logger.info(message)
    
    def _reset_window(self):
        """重置时间窗口"""
        self.last_aggregate_time = time.time()
        self.current_window_logs = 0
        
        # 重置统计（保留一些历史数据用于趋势分析）
        for key in self.sync_stats:
            self.sync_stats[key] = 0
        
        # 清理过期的哈希计数
        self._cleanup_hash_counts()
    
    def _cleanup_hash_counts(self):
        """清理过期的哈希计数"""
        # 只保留最近的哈希计数
        if len(self.hash_counts) > 200:  # 避免内存泄露
            # 保留最近使用的100个
            recent_set = set(self.recent_hashes)
            keys_to_remove = [k for k in self.hash_counts.keys() if k not in recent_set]
            
            for key in keys_to_remove[:len(keys_to_remove)//2]:  # 删除一半旧数据
                del self.hash_counts[key]
    
    def force_aggregate_output(self):
        """强制输出当前聚合统计"""
        with self.lock:
            self._output_aggregate_stats()
            self._reset_window()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        with self.lock:
            return {
                'current_window_stats': self.sync_stats.copy(),
                'unique_hashes_tracked': len(self.hash_counts),
                'recent_hashes_count': len(self.recent_hashes),
                'current_window_logs': self.current_window_logs,
                'time_since_last_aggregate': time.time() - self.last_aggregate_time
            }


class SmartLogFilter:
    """智能日志过滤器"""
    
    def __init__(self):
        self.pattern_counts = defaultdict(int)
        self.suppression_thresholds = {
            '经验同步成功': 10,  # 10次后开始抑制
            '经验已添加到直接经验库': 15,
            '规律同步成功': 8,
        }
        self.suppression_ratios = {
            '经验同步成功': 0.1,  # 只显示10%
            '经验已添加到直接经验库': 0.05,  # 只显示5%
            '规律同步成功': 0.2,  # 只显示20%
        }
    
    def should_log(self, message: str) -> bool:
        """判断是否应该记录日志"""
        # 识别消息模式
        pattern = self._identify_pattern(message)
        
        if pattern not in self.suppression_thresholds:
            return True  # 未识别的模式正常记录
        
        self.pattern_counts[pattern] += 1
        count = self.pattern_counts[pattern]
        
        # 在阈值之前正常记录
        if count <= self.suppression_thresholds[pattern]:
            return True
        
        # 超过阈值后按比例抑制
        ratio = self.suppression_ratios[pattern]
        return (count % int(1 / ratio)) == 0
    
    def _identify_pattern(self, message: str) -> str:
        """识别日志消息的模式"""
        for pattern in self.suppression_thresholds.keys():
            if pattern in message:
                return pattern
        return 'unknown'
    
    def get_suppression_stats(self) -> Dict[str, Dict[str, int]]:
        """获取抑制统计"""
        stats = {}
        for pattern, count in self.pattern_counts.items():
            if pattern in self.suppression_thresholds:
                threshold = self.suppression_thresholds[pattern]
                suppressed = max(0, count - threshold)
                ratio = self.suppression_ratios.get(pattern, 1.0)
                if count > threshold:
                    suppressed = int(suppressed * (1 - ratio))
                
                stats[pattern] = {
                    'total_occurrences': count,
                    'threshold': threshold,
                    'suppressed_count': suppressed,
                    'logged_count': count - suppressed,
                    'suppression_ratio': f"{(suppressed/count*100):.1f}%" if count > 0 else "0%"
                }
        return stats


def create_optimized_five_library_logger() -> OptimizedSyncLogger:
    """创建优化的五库系统日志记录器"""
    return OptimizedSyncLogger(
        aggregate_interval=30,  # 30秒聚合一次
        max_individual_logs=3   # 每个窗口最多3条个别日志
    )


def apply_log_optimization_to_five_library():
    """应用日志优化到五库系统的示例代码"""
    
    # 创建优化的日志记录器
    sync_logger = create_optimized_five_library_logger()
    
    # 在 sync_experience_to_total_library 方法中替换原有日志
    def optimized_sync_logging(sync_result, content_hash):
        """优化的同步日志记录"""
        # 替换原来的 logger.info(f"✅ 经验同步成功: {sync_result['action']} - {content_hash[:16]}...")
        sync_logger.log_sync_result(sync_result, content_hash)
    
    return sync_logger


# 使用示例
if __name__ == "__main__":
    # 创建日志记录器
    sync_logger = create_optimized_five_library_logger()
    
    # 模拟大量同步操作
    print("🧪 测试日志优化效果...")
    
    # 模拟100个同步操作
    for i in range(100):
        sync_result = {
            'success': True,
            'action': 'merged' if i % 3 == 0 else 'created' if i % 10 == 0 else 'updated',
            'total_occurrence_count': i + 1,
            'discoverer_count': 1
        }
        content_hash = f"hash_{i % 20:032d}"  # 模拟一些重复哈希
        
        sync_logger.log_sync_result(sync_result, content_hash)
        
        # 模拟时间流逝
        if i % 30 == 29:
            time.sleep(0.1)  # 小延迟触发聚合
    
    # 强制输出最终统计
    sync_logger.force_aggregate_output()
    
    # 显示统计信息
    stats = sync_logger.get_statistics()
    print(f"\n📊 优化效果统计: {stats}")
    
    print("\n✅ 日志优化测试完成") 