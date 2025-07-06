#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化BMP规律生成器
直接从EOCATR经验生成 E-A-R, E-T-R, O-A-R, O-T-R, C-A-R, C-T-R 格式的规律
"""

import time
import json
from typing import List, Dict, Any
from collections import defaultdict
from eocatr_unified_format import UnifiedEOCATR, SimpleRule, generate_all_simple_rules_from_experience

class SimplifiedBMPGenerator:
    """简化的BMP规律生成器"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.rule_storage: Dict[str, SimpleRule] = {}  # 规律存储
        self.rule_statistics: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))  # 统计信息
        
        if self.logger:
            self.logger.log("🔥 简化BMP规律生成器已初始化")
    
    def process_experience_batch(self, experiences: List[UnifiedEOCATR]) -> List[SimpleRule]:
        """处理一批EOCATR经验，生成并合并规律"""
        if self.logger:
            self.logger.log(f"🔥 BMP开始处理 {len(experiences)} 个EOCATR经验")
        
        all_new_rules = []
        
        # 为每个经验生成所有可能的规律
        for exp in experiences:
            exp_rules = generate_all_simple_rules_from_experience(exp)
            all_new_rules.extend(exp_rules)
            
            if self.logger:
                self.logger.log(f"🔥 经验 {exp.experience_id[:8]} 生成了 {len(exp_rules)} 个规律")
        
        # 按类型分组并合并规律
        merged_rules = self._merge_similar_rules(all_new_rules)
        
        # 保存到规律存储
        for rule in merged_rules:
            self.rule_storage[rule.rule_id] = rule
        
        if self.logger:
            self.logger.log(f"🔥 BMP处理完成，生成 {len(merged_rules)} 个最终规律")
        
        return merged_rules
    
    def _merge_similar_rules(self, rules: List[SimpleRule]) -> List[SimpleRule]:
        """合并相似的规律"""
        # 按规律签名分组
        rule_groups = defaultdict(list)
        
        for rule in rules:
            # 生成规律签名：类型+条件+动作/工具
            signature = f"{rule.rule_type}|{rule.condition_element}|{rule.action_or_tool}"
            rule_groups[signature].append(rule)
        
        merged_rules = []
        
        for signature, group_rules in rule_groups.items():
            if len(group_rules) == 1:
                # 单个规律直接加入
                merged_rules.append(group_rules[0])
            else:
                # 多个相同签名的规律需要合并
                merged_rule = self._merge_rule_group(group_rules)
                merged_rules.append(merged_rule)
                
                if self.logger:
                    self.logger.log(f"🔥 合并规律组: {signature} ({len(group_rules)} -> 1)")
        
        return merged_rules
    
    def _merge_rule_group(self, rules: List[SimpleRule]) -> SimpleRule:
        """合并一组相同签名的规律"""
        if not rules:
            return None
        
        # 使用第一个规律作为基础
        base_rule = rules[0]
        
        # 统计成功和总数
        total_support = sum(rule.support_count for rule in rules)
        total_count = sum(rule.total_count for rule in rules)
        success_count = sum(rule.support_count for rule in rules if rule.success_rate > 0.5)
        
        # 计算新的成功率和置信度
        new_success_rate = success_count / total_count if total_count > 0 else 0.0
        new_confidence = new_success_rate * (total_count / (total_count + 1))  # 考虑样本数量
        
        # 确定预期结果（取多数）
        result_counts = defaultdict(int)
        for rule in rules:
            result_counts[rule.expected_result] += rule.support_count
        
        expected_result = max(result_counts.keys(), key=result_counts.get) if result_counts else base_rule.expected_result
        
        # 创建合并后的规律
        merged_rule = SimpleRule(
            rule_id=f"MERGED_{base_rule.rule_type}_{int(time.time())}",
            rule_type=base_rule.rule_type,
            condition_element=base_rule.condition_element,
            condition_type=base_rule.condition_type,
            condition_subtype=base_rule.condition_subtype,
            action_or_tool=base_rule.action_or_tool,
            action_tool_type=base_rule.action_tool_type,
            expected_result=expected_result,
            success_rate=new_success_rate,
            confidence=new_confidence,
            support_count=total_support,
            total_count=total_count,
            player_id=base_rule.player_id
        )
        
        return merged_rule
    
    def get_rules_by_type(self, rule_type: str) -> List[SimpleRule]:
        """按类型获取规律"""
        return [rule for rule in self.rule_storage.values() if rule.rule_type == rule_type]
    
    def get_applicable_rules(self, current_context: Dict[str, Any]) -> List[SimpleRule]:
        """获取适用于当前上下文的规律"""
        applicable_rules = []
        
        environment = current_context.get('environment', '')
        object_name = current_context.get('object', '')
        characteristics = current_context.get('characteristics', {})
        
        for rule in self.rule_storage.values():
            if self._is_rule_applicable(rule, environment, object_name, characteristics):
                applicable_rules.append(rule)
        
        # 按置信度排序
        applicable_rules.sort(key=lambda r: r.confidence, reverse=True)
        
        if self.logger:
            self.logger.log(f"🔥 找到 {len(applicable_rules)} 个适用规律")
        
        return applicable_rules
    
    def _is_rule_applicable(self, rule: SimpleRule, environment: str, 
                           object_name: str, characteristics: Dict[str, Any]) -> bool:
        """判断规律是否适用于当前上下文"""
        if rule.condition_type == "environment":
            return rule.condition_element == environment
        elif rule.condition_type == "object":
            return rule.condition_element == object_name
        elif rule.condition_type == "characteristic":
            # 根据特征子类型检查
            if rule.condition_subtype == "c1":
                return rule.condition_element == characteristics.get('c1_distance_category', '')
            elif rule.condition_subtype == "c2":
                return rule.condition_element == characteristics.get('c2_danger_type', '')
            elif rule.condition_subtype == "c3":
                return rule.condition_element == characteristics.get('c3_resource_type', '')
            # 可以继续添加更多特征子类型
        
        return False
    
    def get_best_action_for_context(self, environment: str, object_name: str, 
                                   characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """为给定上下文获取最佳动作建议"""
        context = {
            'environment': environment,
            'object': object_name,
            'characteristics': characteristics
        }
        
        applicable_rules = self.get_applicable_rules(context)
        
        if not applicable_rules:
            if self.logger:
                self.logger.log("🔥 未找到适用规律，返回默认建议")
            return {
                'action': 'explore',
                'tool': 'no_tool',
                'confidence': 0.1,
                'source': 'default'
            }
        
        # 选择置信度最高的规律
        best_rule = applicable_rules[0]
        
        if best_rule.action_tool_type == "action":
            recommended_action = best_rule.action_or_tool
            recommended_tool = "no_tool"
        else:
            recommended_action = "use_tool"  # 使用工具的通用动作
            recommended_tool = best_rule.action_or_tool
        
        result = {
            'action': recommended_action,
            'tool': recommended_tool,
            'confidence': best_rule.confidence,
            'expected_result': best_rule.expected_result,
            'source': f'rule_{best_rule.rule_type}',
            'rule_id': best_rule.rule_id
        }
        
        if self.logger:
            self.logger.log(f"🔥 推荐动作: {result}")
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取规律统计信息"""
        stats = {
            'total_rules': len(self.rule_storage),
            'rules_by_type': defaultdict(int),
            'average_confidence': 0.0,
            'high_confidence_rules': 0,  # 置信度 > 0.7
            'medium_confidence_rules': 0,  # 置信度 0.3-0.7
            'low_confidence_rules': 0   # 置信度 < 0.3
        }
        
        if not self.rule_storage:
            return stats
        
        total_confidence = 0.0
        
        for rule in self.rule_storage.values():
            stats['rules_by_type'][rule.rule_type] += 1
            total_confidence += rule.confidence
            
            if rule.confidence > 0.7:
                stats['high_confidence_rules'] += 1
            elif rule.confidence > 0.3:
                stats['medium_confidence_rules'] += 1
            else:
                stats['low_confidence_rules'] += 1
        
        stats['average_confidence'] = total_confidence / len(self.rule_storage)
        
        return stats
    
    def export_rules_to_dict(self) -> List[Dict[str, Any]]:
        """导出规律为字典列表"""
        return [rule.to_dict() for rule in self.rule_storage.values()]
    
    def import_rules_from_dict(self, rules_data: List[Dict[str, Any]]):
        """从字典列表导入规律"""
        for rule_data in rules_data:
            rule = SimpleRule.from_dict(rule_data)
            self.rule_storage[rule.rule_id] = rule
        
        if self.logger:
            self.logger.log(f"🔥 导入了 {len(rules_data)} 个规律")
    
    def save_to_file(self, filepath: str = "simplified_bmp_rules.json") -> bool:
        """保存规律到文件"""
        try:
            save_data = {
                'metadata': {
                    'version': '1.0',
                    'timestamp': time.time(),
                    'total_rules': len(self.rule_storage),
                    'format': 'simplified_bmp'
                },
                'rules': self.export_rules_to_dict(),
                'statistics': self.get_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            if self.logger:
                self.logger.log(f"🔥 规律已保存到: {filepath}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 保存规律失败: {str(e)}")
            return False
    
    def load_from_file(self, filepath: str = "simplified_bmp_rules.json") -> bool:
        """从文件加载规律"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            rules_data = save_data.get('rules', [])
            self.import_rules_from_dict(rules_data)
            
            if self.logger:
                self.logger.log(f"🔥 从文件加载了 {len(rules_data)} 个规律")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ 加载规律失败: {str(e)}")
            return False
    
    # === 兼容性方法：支持旧BMP接口 ===
    
    def process_experience(self, latest_experience, historical_batch=None):
        """兼容旧BMP的process_experience方法"""
        experiences = [latest_experience]
        if historical_batch:
            experiences.extend(historical_batch)
        return self.process_experience_batch(experiences)
    
    def validation_phase(self, validation_experiences):
        """兼容旧BMP的validation_phase方法"""
        validated_rule_ids = []
        
        for exp in validation_experiences:
            # 生成规律并检查与现有规律的匹配
            from eocatr_unified_format import generate_all_simple_rules_from_experience
            exp_rules = generate_all_simple_rules_from_experience(exp)
            
            for new_rule in exp_rules:
                for existing_rule_id, existing_rule in self.rule_storage.items():
                    # 检查规律类型和条件是否匹配
                    if (new_rule.rule_type == existing_rule.rule_type and 
                        new_rule.condition_element == existing_rule.condition_element):
                        # 更新现有规律的证据
                        existing_rule.total_count += 1
                        if new_rule.expected_result == existing_rule.expected_result:
                            existing_rule.support_count += 1
                        
                        # 重新计算置信度
                        existing_rule.confidence = existing_rule.support_count / existing_rule.total_count
                        validated_rule_ids.append(existing_rule_id)
                        break
        
        if self.logger and validated_rule_ids:
            self.logger.log(f"🔥 BMP验证阶段：验证了 {len(validated_rule_ids)} 个规律")
        
        return list(set(validated_rule_ids))  # 去重
    
    def pruning_phase(self):
        """兼容旧BMP的pruning_phase方法"""
        pruned_rule_ids = []
        min_confidence_threshold = 0.3
        
        rules_to_remove = []
        for rule_id, rule in self.rule_storage.items():
            if rule.confidence < min_confidence_threshold or rule.total_count < 2:
                rules_to_remove.append(rule_id)
                pruned_rule_ids.append(rule_id)
        
        # 移除低质量规律
        for rule_id in rules_to_remove:
            del self.rule_storage[rule_id]
        
        if self.logger and pruned_rule_ids:
            self.logger.log(f"🔥 BMP剪枝阶段：移除了 {len(pruned_rule_ids)} 个低质量规律")
        
        return pruned_rule_ids
    
    def get_all_validated_rules(self):
        """兼容旧BMP的get_all_validated_rules方法"""
        # 返回所有置信度较高的规律
        validated_rules = []
        for rule in self.rule_storage.values():
            if rule.confidence > 0.5:
                # 转换为旧BMP期望的格式
                mock_rule = type('MockRule', (), {
                    'rule_id': rule.rule_id,
                    'rule_type': type('RuleType', (), {'value': rule.rule_type or 'unknown'}),
                    'pattern': f"{rule.condition_element} -> {rule.expected_result}",
                    'confidence': rule.confidence,
                    'conditions': rule.condition_element,
                    'predictions': rule.expected_result
                })()
                validated_rules.append(mock_rule)
        
        return validated_rules
    
    @property
    def validated_rules(self):
        """兼容旧BMP的validated_rules属性"""
        return {rule.rule_id: rule for rule in self.get_all_validated_rules()}

    def generate_all_rules_from_experience(self, experience):
        """
        从单个经验生成所有规律的方法(用于兼容性)
        这是process_experience的别名方法
        """
        if isinstance(experience, list):
            return self.process_experience_batch(experience)
        else:
            return self.process_experience_batch([experience])

# === 测试和演示函数 ===

def test_simplified_bmp():
    """测试简化BMP生成器"""
    from eocatr_unified_format import create_unified_eocatr, CharacteristicsMulti
    
    # 创建测试日志
    class TestLogger:
        def log(self, message):
            print(f"[TEST] {message}")
    
    logger = TestLogger()
    generator = SimplifiedBMPGenerator(logger)
    
    # 创建测试经验
    experiences = []
    
    # 经验1: 在开阔地用篮子收集可食植物 - 成功
    characteristics1 = {
        'c1_distance': 2.0,
        'c1_distance_category': '近距离',
        'c2_safety_level': 0.8,
        'c2_danger_type': '无',
        'c3_resource_value': 0.9,
        'c3_resource_type': '食物'
    }
    exp1 = create_unified_eocatr("open_field", "edible_plant", "gather", "basket", "success", 
                                characteristics1, "player1", True, 10.0)
    experiences.append(exp1)
    
    # 经验2: 在开阔地徒手收集可食植物 - 部分成功
    characteristics2 = {
        'c1_distance': 1.5,
        'c1_distance_category': '近距离', 
        'c2_safety_level': 0.8,
        'c2_danger_type': '无',
        'c3_resource_value': 0.7,
        'c3_resource_type': '食物'
    }
    exp2 = create_unified_eocatr("open_field", "edible_plant", "gather", "bare_hands", "partial_success",
                                characteristics2, "player1", True, 5.0)
    experiences.append(exp2)
    
    # 经验3: 在森林中避开危险的掠食者 - 成功
    characteristics3 = {
        'c1_distance': 8.0,
        'c1_distance_category': '中距离',
        'c2_safety_level': 0.2,
        'c2_danger_type': '严重',
        'c3_resource_value': 0.0,
        'c3_resource_type': '威胁'
    }
    exp3 = create_unified_eocatr("forest", "predator", "avoid", "no_tool", "success",
                                characteristics3, "player1", True, 1.0)
    experiences.append(exp3)
    
    # 处理经验生成规律
    print("\n=== 开始处理经验 ===")
    generated_rules = generator.process_experience_batch(experiences)
    
    print(f"\n=== 生成规律总览 ===")
    print(f"总计生成 {len(generated_rules)} 个规律")
    
    # 按类型展示规律
    rule_types = set(rule.rule_type for rule in generated_rules)
    for rule_type in sorted(rule_types):
        type_rules = [rule for rule in generated_rules if rule.rule_type == rule_type]
        print(f"\n{rule_type} 规律 ({len(type_rules)} 个):")
        for rule in type_rules:
            print(f"  - {rule.condition_element} -> {rule.action_or_tool} -> {rule.expected_result}")
            print(f"    置信度: {rule.confidence:.3f}, 成功率: {rule.success_rate:.3f}")
    
    # 测试规律应用
    print(f"\n=== 测试规律应用 ===")
    test_context = {
        'environment': 'open_field',
        'object': 'edible_plant',
        'characteristics': {
            'c1_distance_category': '近距离',
            'c2_danger_type': '无',
            'c3_resource_type': '食物'
        }
    }
    
    recommendation = generator.get_best_action_for_context(
        test_context['environment'],
        test_context['object'],
        test_context['characteristics']
    )
    
    print(f"上下文: {test_context}")
    print(f"推荐结果: {recommendation}")
    
    # 显示统计信息
    print(f"\n=== 统计信息 ===")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_simplified_bmp() 