#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BPM系统与规律数据库集成
自动持久化存储候选规律，提供规律管理和分析功能
"""

import time
from typing import List, Dict, Any, Optional
from rule_database import RuleDatabase
from blooming_and_pruning_model import BloomingAndPruningModel, CandidateRule, RuleType

class BMPDatabaseIntegration:
    """BPM系统与数据库集成管理器"""
    
    def __init__(self, bmp_instance: BloomingAndPruningModel, 
                 db_path: str = "bmp_rules.db", 
                 auto_save: bool = True,
                 sync_interval: int = 10):
        """
        初始化集成管理器
        
        Args:
            bmp_instance: BPM系统实例
            db_path: 数据库文件路径
            auto_save: 是否自动保存新生成的规律
            sync_interval: 同步间隔（秒）
        """
        self.bmp = bmp_instance
        self.rule_db = RuleDatabase(db_path)
        self.auto_save = auto_save
        self.sync_interval = sync_interval
        self.last_sync_time = time.time()
        
        # 保存原始方法的引用
        self.original_blooming_phase = self.bmp.blooming_phase
        self.original_validation_phase = self.bmp.validation_phase
        self.original_pruning_phase = self.bmp.pruning_phase
        
        # 替换BMP方法以添加数据库功能
        self._patch_bpm_methods()
        
        # 从数据库加载现有规律
        self._load_existing_rules()
        
        print(f"✅ BMP数据库集成已启动")
        print(f"   数据库路径: {db_path}")
        print(f"   自动保存: {'启用' if auto_save else '禁用'}")
    
    def _patch_bpm_methods(self):
        """修补BMP方法以添加数据库功能"""
        
        def enhanced_blooming_phase(eocar_experiences: List) -> List[CandidateRule]:
            """增强的怒放阶段，自动保存新规律"""
            # 调用原始方法
            new_rules = self.original_blooming_phase(eocar_experiences)
            
            # 自动保存新规律到数据库
            if self.auto_save and new_rules:
                for rule in new_rules:
                    self.save_rule_to_database(rule, evolution_type="generated", 
                                             reason="BPM怒放阶段生成")
                
                if self.bmp.logger:
                    self.bmp.logger.log(f"数据库已保存 {len(new_rules)} 个新规律")
            
            return new_rules
        
        def enhanced_validation_phase(new_experiences: List) -> List[str]:
            """增强的验证阶段，自动更新规律状态"""
            # 调用原始方法
            validated_rule_ids = self.original_validation_phase(new_experiences)
            
            # 更新数据库中的规律状态
            if validated_rule_ids:
                for rule_id in validated_rule_ids:
                    self.rule_db.validate_rule(rule_id, "BPM验证阶段确认")
                
                if self.bmp.logger:
                    self.bmp.logger.log(f"数据库已更新 {len(validated_rule_ids)} 个验证规律")
            
            return validated_rule_ids
        
        def enhanced_pruning_phase() -> List[str]:
            """增强的修剪阶段，自动记录修剪历史"""
            # 调用原始方法
            pruned_rule_ids = self.original_pruning_phase()
            
            # 更新数据库中的规律状态
            if pruned_rule_ids:
                for rule_id in pruned_rule_ids:
                    self.rule_db.prune_rule(rule_id, "BMP修剪阶段移除")
                
                if self.bmp.logger:
                    self.bmp.logger.log(f"数据库已记录 {len(pruned_rule_ids)} 个修剪规律")
            
            return pruned_rule_ids
        
        # 替换方法
        self.bmp.blooming_phase = enhanced_blooming_phase
        self.bmp.validation_phase = enhanced_validation_phase
        self.bmp.pruning_phase = enhanced_pruning_phase
    
    def _load_existing_rules(self):
        """从数据库加载现有规律到BMP内存中"""
        try:
            # 加载候选规律
            candidate_rules = self.rule_db.query_rules(status='candidate')
            for rule_data in candidate_rules:
                rule = self.rule_db._dict_to_candidate_rule(rule_data)
                if rule:
                    self.bmp.candidate_rules[rule.rule_id] = rule
            
            # 加载验证规律
            validated_rules = self.rule_db.query_rules(status='validated')
            for rule_data in validated_rules:
                rule = self.rule_db._dict_to_candidate_rule(rule_data)
                if rule:
                    self.bmp.validated_rules[rule.rule_id] = rule
            
            total_loaded = len(candidate_rules) + len(validated_rules)
            if total_loaded > 0:
                print(f"✅ 从数据库加载了 {total_loaded} 个规律")
                print(f"   候选规律: {len(candidate_rules)} 个")
                print(f"   验证规律: {len(validated_rules)} 个")
            
        except Exception as e:
            print(f"⚠️ 加载现有规律失败: {str(e)}")
    
    def save_rule_to_database(self, rule: CandidateRule, evolution_type: str = "manual",
                             parent_rule_id: str = None, reason: str = None) -> bool:
        """保存规律到数据库"""
        try:
            success = self.rule_db.save_rule(rule, evolution_type, parent_rule_id, reason)
            if success:
                # 更新统计信息
                self._update_daily_statistics()
            return success
        except Exception as e:
            if self.bmp.logger:
                self.bmp.logger.log(f"保存规律到数据库失败: {str(e)}")
            return False
    
    def sync_memory_to_database(self) -> Dict[str, int]:
        """同步内存中的规律到数据库"""
        try:
            synced_counts = {'candidate': 0, 'validated': 0, 'updated': 0}
            
            # 同步候选规律
            for rule_id, rule in self.bmp.candidate_rules.items():
                existing = self.rule_db.get_rule(rule_id)
                if existing:
                    # 更新现有规律
                    if self.rule_db.update_rule(rule, "sync_update", "内存同步更新"):
                        synced_counts['updated'] += 1
                else:
                    # 保存新规律
                    if self.rule_db.save_rule(rule, "sync_new", reason="内存同步新增"):
                        synced_counts['candidate'] += 1
            
            # 同步验证规律
            for rule_id, rule in self.bmp.validated_rules.items():
                existing = self.rule_db.get_rule(rule_id)
                if existing:
                    if self.rule_db.update_rule(rule, "sync_update", "内存同步更新"):
                        synced_counts['updated'] += 1
                else:
                    if self.rule_db.save_rule(rule, "sync_validated", reason="内存同步验证"):
                        synced_counts['validated'] += 1
            
            self.last_sync_time = time.time()
            
            if self.bmp.logger:
                total_synced = sum(synced_counts.values())
                if total_synced > 0:
                    self.bmp.logger.log(f"同步完成: 候选{synced_counts['candidate']}, "
                                      f"验证{synced_counts['validated']}, "
                                      f"更新{synced_counts['updated']}")
            
            return synced_counts
            
        except Exception as e:
            if self.bmp.logger:
                self.bmp.logger.log(f"同步失败: {str(e)}")
            return {'candidate': 0, 'validated': 0, 'updated': 0}
    
    def auto_sync_check(self):
        """检查是否需要自动同步"""
        current_time = time.time()
        if current_time - self.last_sync_time >= self.sync_interval:
            self.sync_memory_to_database()
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        return self.rule_db.get_statistics()
    
    def query_historical_rules(self, **kwargs) -> List[Dict]:
        """查询历史规律"""
        return self.rule_db.query_rules(**kwargs)
    
    def export_rules_backup(self, output_file: str = None, include_pruned: bool = True) -> bool:
        """导出规律备份"""
        return self.rule_db.export_to_json(output_file, include_pruned)
    
    def import_rules_backup(self, input_file: str, merge_mode: str = 'update') -> bool:
        """导入规律备份"""
        success = self.rule_db.import_from_json(input_file, merge_mode)
        if success:
            # 重新加载规律到内存
            self._load_existing_rules()
        return success
    
    def _update_daily_statistics(self):
        """更新每日统计"""
        try:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 这里可以添加更复杂的统计逻辑
            # 目前简单地记录规律生成事件
            
        except Exception as e:
            print(f"⚠️ 更新统计失败: {str(e)}")
    
    def get_rule_evolution_history(self, rule_id: str) -> List[Dict]:
        """获取规律演化历史"""
        try:
            cursor = self.rule_db.connection.cursor()
            cursor.execute('''
                SELECT * FROM rule_evolution 
                WHERE rule_id = ? 
                ORDER BY timestamp DESC
            ''', (rule_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"❌ 获取演化历史失败: {str(e)}")
            return []
    
    def analyze_rule_performance(self, days: int = 7) -> Dict[str, Any]:
        """分析规律性能"""
        try:
            import datetime
            
            cutoff_time = time.time() - (days * 24 * 3600)
            
            # 查询最近的规律
            recent_rules = self.rule_db.query_rules()
            recent_rules = [r for r in recent_rules if r['birth_time'] >= cutoff_time]
            
            if not recent_rules:
                return {'message': '没有最近的规律数据', 'days': days}
            
            # 计算统计指标
            total_rules = len(recent_rules)
            avg_quality = sum(r['quality_score'] for r in recent_rules) / total_rules
            avg_confidence = sum(r['confidence'] for r in recent_rules) / total_rules
            
            # 按类型分组
            type_counts = {}
            for rule in recent_rules:
                rule_type = rule['rule_type']
                type_counts[rule_type] = type_counts.get(rule_type, 0) + 1
            
            # 按状态分组
            status_counts = {}
            for rule in recent_rules:
                status = rule['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'analysis_period_days': days,
                'total_rules': total_rules,
                'average_quality_score': round(avg_quality, 3),
                'average_confidence': round(avg_confidence, 3),
                'type_distribution': type_counts,
                'status_distribution': status_counts,
                'quality_ranges': {
                    'high_quality': len([r for r in recent_rules if r['quality_score'] >= 0.7]),
                    'medium_quality': len([r for r in recent_rules if 0.4 <= r['quality_score'] < 0.7]),
                    'low_quality': len([r for r in recent_rules if r['quality_score'] < 0.4])
                }
            }
            
        except Exception as e:
            print(f"❌ 性能分析失败: {str(e)}")
            return {'error': str(e)}
    
    def cleanup_old_rules(self, days_threshold: int = 30, quality_threshold: float = 0.1) -> int:
        """清理旧的低质量规律"""
        try:
            cutoff_time = time.time() - (days_threshold * 24 * 3600)
            
            # 查询需要清理的规律
            old_low_quality_rules = self.rule_db.query_rules(
                max_quality=quality_threshold,
                status='candidate'
            )
            
            cleaned_count = 0
            for rule in old_low_quality_rules:
                if rule['birth_time'] < cutoff_time:
                    if self.rule_db.prune_rule(rule['rule_id'], 
                                             f"自动清理：超过{days_threshold}天且质量<{quality_threshold}"):
                        cleaned_count += 1
            
            if self.bmp.logger and cleaned_count > 0:
                self.bmp.logger.log(f"自动清理了 {cleaned_count} 个旧的低质量规律")
            
            return cleaned_count
            
        except Exception as e:
            print(f"❌ 清理规律失败: {str(e)}")
            return 0
    
    def get_top_rules(self, limit: int = 10, sort_by: str = 'quality_score') -> List[Dict]:
        """获取顶级规律"""
        return self.rule_db.query_rules(
            limit=limit,
            order_by=sort_by,
            order_desc=True,
            status='candidate'
        )
    
    def close(self):
        """关闭数据库连接"""
        self.rule_db.close()
        print("✅ BMP数据库集成已关闭")


# 使用示例
if __name__ == "__main__":
    # 创建BMP实例（这里需要真实的BMP实例）
    print("🔧 BMP数据库集成示例")
    
    # 注意：在实际使用中，你需要传入真实的BMP实例
    # bmp_instance = BloomingAndPruningModel(logger=your_logger)
    # integration = BMPDatabaseIntegration(bmp_instance)
    
    # 测试数据库创建
    rule_db = RuleDatabase("test_bpm_rules.db")
    stats = rule_db.get_statistics()
    print(f"\n📊 数据库统计: {stats}")
    
    rule_db.close()
    print("✅ 测试完成") 