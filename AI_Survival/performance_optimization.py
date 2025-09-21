#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏性能优化配置
解决游戏运行缓慢的问题
"""

# ==================== 性能优化配置 ====================

PERFORMANCE_CONFIG = {
    # 🔄 决策流程优化
    "decision_optimization": {
        "enable_decision_caching": True,        # 启用决策缓存
        "cache_duration": 5,                    # 缓存持续时间(回合)
        "skip_redundant_analysis": True,        # 跳过冗余分析
        "simplified_state_check": True,         # 简化状态检查
        "batch_processing": True,               # 批量处理
    },
    
    # 💾 数据库优化
    "database_optimization": {
        "batch_insert_size": 10,                # 批量插入大小
        "auto_sync_interval": 50,               # 自动同步间隔(回合)
        "enable_write_buffering": True,         # 启用写入缓冲
        "lazy_sync": True,                      # 延迟同步
        "compress_old_data": True,              # 压缩旧数据
    },
    
    # 🧠 AI系统优化
    "ai_system_optimization": {
        "reduce_bmp_frequency": True,           # 降低BPM频率
        "bmp_process_interval": 3,              # BPM处理间隔
        "simplify_symbolization": True,        # 简化符号化
        "cache_wbm_results": True,              # 缓存WBM结果
        "limit_rule_generation": True,          # 限制规律生成
    },
    
    # 📝 日志优化
    "logging_optimization": {
        "reduce_log_verbosity": True,           # 降低日志详细度
        "batch_log_writing": True,              # 批量日志写入
        "async_logging": True,                  # 异步日志
        "log_compression": True,                # 日志压缩
        "selective_logging": True,              # 选择性日志
    },
    
    # ⚡ 游戏循环优化
    "game_loop_optimization": {
        "increase_turn_delay": True,            # 增加回合延迟
        "optimized_turn_delay": 500,            # 优化后的延迟(ms)
        "skip_unnecessary_updates": True,       # 跳过不必要的更新
        "reduce_animation_frequency": True,     # 降低动画频率
        "parallel_player_processing": False,    # 并行玩家处理(实验性)
    }
}

# ==================== 轻量级配置 ====================

LIGHTWEIGHT_CONFIG = {
    # 🎯 简化决策
    "simplified_decision": True,               # 使用简化决策
    "disable_long_chain": False,               # 禁用长链决策
    "disable_multi_step": False,               # 禁用多步规划
    "reduce_goal_complexity": True,            # 降低目标复杂度
    
    # 💾 最小化数据库操作
    "minimal_database": True,                  # 最小化数据库操作
    "memory_only_mode": False,                 # 仅内存模式(实验性)
    "disable_auto_sync": False,                # 禁用自动同步
    
    # 🧠 简化AI系统
    "disable_bmp": False,                      # 禁用BMP系统
    "disable_symbolization": False,            # 禁用符号化
    "simple_emrs": True,                       # 简化EMRS评价
    
    # 📝 最小化日志
    "minimal_logging": True,                   # 最小化日志
    "error_only_logging": False,               # 仅错误日志
}

# ==================== 性能监控配置 ====================

PERFORMANCE_MONITORING = {
    "enable_profiling": True,                  # 启用性能分析
    "monitor_turn_time": True,                 # 监控回合时间
    "monitor_memory_usage": True,              # 监控内存使用
    "monitor_database_ops": True,              # 监控数据库操作
    "performance_log_interval": 10,            # 性能日志间隔
}

# ==================== 应用性能优化的函数 ====================

def apply_performance_optimizations(game_instance, config_level="balanced"):
    """
    应用性能优化配置
    
    Args:
        game_instance: 游戏实例
        config_level: 配置级别 ("lightweight", "balanced", "full_performance")
    """
    
    if config_level == "lightweight":
        return apply_lightweight_config(game_instance)
    elif config_level == "balanced":
        return apply_balanced_config(game_instance)
    elif config_level == "full_performance":
        return apply_full_performance_config(game_instance)
    else:
        raise ValueError(f"未知的配置级别: {config_level}")

def apply_lightweight_config(game_instance):
    """应用轻量级配置"""
    optimizations_applied = []
    
    # 1. 增加回合延迟
    if hasattr(game_instance, 'canvas'):
        game_instance.turn_delay = 800  # 增加到800ms
        optimizations_applied.append("增加回合延迟到800ms")
    
    # 2. 简化玩家决策
    for player in game_instance.players:
        if hasattr(player, 'player_type') and player.player_type in ['ILAI', 'RILAI']:
            # 禁用一些复杂功能
            if hasattr(player, 'enable_complex_decision'):
                player.enable_complex_decision = False
                optimizations_applied.append(f"{player.name}: 禁用复杂决策")
            
            # 降低BMP处理频率
            if hasattr(player, 'bmp_process_interval'):
                player.bmp_process_interval = 5
                optimizations_applied.append(f"{player.name}: BMP间隔设为5回合")
    
    # 3. 降低同步频率
    if hasattr(game_instance, 'global_knowledge_sync'):
        game_instance.global_knowledge_sync.sync_interval = 100
        optimizations_applied.append("知识同步间隔增加到100回合")
    
    return optimizations_applied

def apply_balanced_config(game_instance):
    """应用平衡配置"""
    optimizations_applied = []
    
    # 1. 适中的回合延迟
    if hasattr(game_instance, 'canvas'):
        game_instance.turn_delay = 500  # 设为500ms
        optimizations_applied.append("回合延迟设为500ms")
    
    # 2. 优化数据库操作
    for player in game_instance.players:
        if hasattr(player, 'five_library_system') and player.five_library_system:
            # 启用批量处理
            if hasattr(player.five_library_system, 'enable_batch_processing'):
                player.five_library_system.enable_batch_processing = True
                optimizations_applied.append(f"{player.name}: 启用数据库批量处理")
    
    # 3. 适中的同步频率
    if hasattr(game_instance, 'global_knowledge_sync'):
        game_instance.global_knowledge_sync.sync_interval = 75
        optimizations_applied.append("知识同步间隔设为75回合")
    
    return optimizations_applied

def apply_full_performance_config(game_instance):
    """应用完整性能配置"""
    optimizations_applied = []
    
    # 1. 最小回合延迟
    if hasattr(game_instance, 'canvas'):
        game_instance.turn_delay = 300  # 设为300ms
        optimizations_applied.append("回合延迟设为300ms")
    
    # 2. 启用所有优化
    for player in game_instance.players:
        if hasattr(player, 'player_type') and player.player_type in ['ILAI', 'RILAI']:
            # 启用决策缓存
            if not hasattr(player, 'decision_cache'):
                player.decision_cache = {}
                player.cache_expiry = {}
                optimizations_applied.append(f"{player.name}: 启用决策缓存")
            
            # 优化日志记录
            if hasattr(player, 'enable_detailed_logging'):
                player.enable_detailed_logging = False
                optimizations_applied.append(f"{player.name}: 禁用详细日志")
    
    # 3. 最低同步频率
    if hasattr(game_instance, 'global_knowledge_sync'):
        game_instance.global_knowledge_sync.sync_interval = 150
        optimizations_applied.append("知识同步间隔设为150回合")
    
    return optimizations_applied

# ==================== 性能监控函数 ====================

import time
import psutil
import os

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.turn_times = []
        self.memory_usage = []
        self.start_time = time.time()
        self.last_turn_time = time.time()
        
    def start_turn_timing(self):
        """开始计时回合"""
        self.last_turn_time = time.time()
    
    def end_turn_timing(self):
        """结束计时回合"""
        turn_duration = time.time() - self.last_turn_time
        self.turn_times.append(turn_duration)
        
        # 记录内存使用
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.memory_usage.append(memory_mb)
        
        return turn_duration
    
    def get_performance_stats(self):
        """获取性能统计"""
        if not self.turn_times:
            return {"error": "没有性能数据"}
        
        avg_turn_time = sum(self.turn_times) / len(self.turn_times)
        max_turn_time = max(self.turn_times)
        min_turn_time = min(self.turn_times)
        
        current_memory = self.memory_usage[-1] if self.memory_usage else 0
        max_memory = max(self.memory_usage) if self.memory_usage else 0
        
        return {
            "总运行时间": f"{time.time() - self.start_time:.2f}秒",
            "回合数": len(self.turn_times),
            "平均回合时间": f"{avg_turn_time:.3f}秒",
            "最长回合时间": f"{max_turn_time:.3f}秒",
            "最短回合时间": f"{min_turn_time:.3f}秒",
            "当前内存使用": f"{current_memory:.1f}MB",
            "最大内存使用": f"{max_memory:.1f}MB",
            "建议": self._get_performance_suggestions(avg_turn_time, max_memory)
        }
    
    def _get_performance_suggestions(self, avg_turn_time, max_memory):
        """获取性能建议"""
        suggestions = []
        
        if avg_turn_time > 2.0:
            suggestions.append("回合时间过长，建议应用轻量级配置")
        elif avg_turn_time > 1.0:
            suggestions.append("回合时间较长，建议应用平衡配置")
        
        if max_memory > 500:
            suggestions.append("内存使用过高，建议启用数据压缩")
        elif max_memory > 300:
            suggestions.append("内存使用较高，建议定期清理缓存")
        
        if not suggestions:
            suggestions.append("性能表现良好")
        
        return suggestions

# ==================== 使用示例 ====================

def optimize_game_performance(game_instance):
    """优化游戏性能的主函数"""
    print("🚀 开始应用性能优化...")
    
    # 应用平衡配置
    optimizations = apply_performance_optimizations(game_instance, "balanced")
    
    print("✅ 已应用以下优化:")
    for opt in optimizations:
        print(f"   • {opt}")
    
    # 创建性能监控器
    monitor = PerformanceMonitor()
    
    print("\n📊 性能监控已启动")
    print("   建议运行几个回合后检查性能统计")
    
    return monitor

if __name__ == "__main__":
    print("性能优化配置模块")
    print("使用方法: from performance_optimization import optimize_game_performance") 