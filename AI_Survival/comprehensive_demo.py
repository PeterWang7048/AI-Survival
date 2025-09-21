#!/usr/bin/env python3
"""
PPP系统完整学习循环演示
展示：经验收集 → BPM怒放 → 规律验证 → 知识同步 → 决策应用
"""

import time
from typing import List, Dict
from scene_symbolization_mechanism import (
    EOCATR_Tuple, SymbolicEnvironment, SymbolicObjectCategory, 
    SymbolicCharacteristics, SymbolicAction, SymbolicTool, SymbolicResult
)
from blooming_and_pruning_model import BloomingAndPruningModel

class ComprehensiveDemo:
    """PPP系统完整演示类"""
    
    def __init__(self):
        self.bpm = BloomingAndPruningModel(logger=self)
        self.simulation_step = 0
        self.log_messages = []
    
    def log(self, message: str):
        """日志记录"""
        timestamp = f"[Step {self.simulation_step:03d}]"
        full_message = f"{timestamp} {message}"
        self.log_messages.append(full_message)
        print(full_message)
    
    def create_learning_scenario(self) -> List[EOCATR_Tuple]:
        """创建一个完整的学习场景：从新手到专家"""
        
        experiences = []
        base_time = time.time()
        
        # === 阶段1：新手探索（失败较多） ===
        self.log("🌱 阶段1：新手探索阶段")
        
        # 徒手攻击失败
        experiences.append(EOCATR_Tuple(
            environment=SymbolicEnvironment.FOREST,
            object_category=SymbolicObjectCategory.DANGEROUS_ANIMAL,
            characteristics=SymbolicCharacteristics(distance=2.0, dangerous=True),
            action=SymbolicAction.ATTACK,
            tool=SymbolicTool.NONE,
            result=SymbolicResult(success=False, reward=-20.0, hp_change=-30),
            timestamp=base_time + 1,
            source="direct"
        ))
        
        # 发现植物成功
        experiences.append(EOCATR_Tuple(
            environment=SymbolicEnvironment.FOREST,
            object_category=SymbolicObjectCategory.EDIBLE_PLANT,
            characteristics=SymbolicCharacteristics(distance=1.5, edible=True, nutrition_value=10),
            action=SymbolicAction.GATHER,
            tool=SymbolicTool.NONE,
            result=SymbolicResult(success=True, reward=10.0, food_change=10),
            timestamp=base_time + 2,
            source="direct"
        ))
        
        # === 阶段2：工具发现与学习 ===
        self.log("🔧 阶段2：工具学习阶段")
        
        # 石头攻击（部分成功）
        experiences.append(EOCATR_Tuple(
            environment=SymbolicEnvironment.FOREST,
            object_category=SymbolicObjectCategory.DANGEROUS_ANIMAL,
            characteristics=SymbolicCharacteristics(distance=2.5, dangerous=True),
            action=SymbolicAction.ATTACK,
            tool=SymbolicTool.STONE,
            result=SymbolicResult(success=True, reward=5.0, hp_change=-10, tool_effectiveness=0.3),
            timestamp=base_time + 3,
            source="direct"
        ))
        
        # 长矛攻击（高效）
        experiences.append(EOCATR_Tuple(
            environment=SymbolicEnvironment.FOREST,
            object_category=SymbolicObjectCategory.DANGEROUS_ANIMAL,
            characteristics=SymbolicCharacteristics(distance=3.0, dangerous=True),
            action=SymbolicAction.ATTACK,
            tool=SymbolicTool.SPEAR,
            result=SymbolicResult(success=True, reward=30.0, hp_change=0, tool_effectiveness=0.9),
            timestamp=base_time + 4,
            source="direct"
        ))
        
        # === 阶段3：专家级应用 ===
        self.log("⭐ 阶段3：专家应用阶段")
        
        # 重复长矛攻击成功
        for i in range(3):
            experiences.append(EOCATR_Tuple(
                environment=SymbolicEnvironment.FOREST,
                object_category=SymbolicObjectCategory.DANGEROUS_ANIMAL,
                characteristics=SymbolicCharacteristics(distance=2.8 + i*0.2, dangerous=True),
                action=SymbolicAction.ATTACK,
                tool=SymbolicTool.SPEAR,
                result=SymbolicResult(success=True, reward=25.0 + i*2, hp_change=0, tool_effectiveness=0.85 + i*0.05),
                timestamp=base_time + 5 + i,
                source="direct"
            ))
        
        # 篮子收集（工具专业化）
        experiences.append(EOCATR_Tuple(
            environment=SymbolicEnvironment.FOREST,
            object_category=SymbolicObjectCategory.EDIBLE_PLANT,
            characteristics=SymbolicCharacteristics(distance=1.0, edible=True, nutrition_value=15),
            action=SymbolicAction.GATHER,
            tool=SymbolicTool.BASKET,
            result=SymbolicResult(success=True, reward=18.0, food_change=15, tool_effectiveness=0.8),
            timestamp=base_time + 8,
            source="direct"
        ))
        
        return experiences
    
    def demonstrate_complete_cycle(self):
        """演示完整的学习循环"""
        
        print("=" * 80)
        print("🎯 PPP系统完整学习循环演示")
        print("=" * 80)
        
        # === 步骤1：经验收集 ===
        self.simulation_step = 1
        self.log("📊 步骤1：经验收集")
        experiences = self.create_learning_scenario()
        self.log(f"收集到 {len(experiences)} 个经验")
        
        # === 步骤2：BPM怒放 ===
        self.simulation_step = 2
        self.log("🌸 步骤2：BPM怒放阶段")
        generated_rules = self.bpm.bloom(experiences)
        self.log(f"怒放生成 {len(generated_rules)} 条候选规律")
        
        # 分析规律类型
        rule_types = {}
        for rule in generated_rules:
            rule_type = rule.rule_type.value
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
        
        for rule_type, count in rule_types.items():
            self.log(f"  {rule_type}: {count}条")
        
        # === 步骤3：规律验证 ===
        self.simulation_step = 3
        self.log("✅ 步骤3：规律验证阶段")
        validated_rule_ids = self.bpm.validation_phase(experiences)
        self.log(f"验证通过 {len(validated_rule_ids)} 条规律")
        
        # === 步骤4：规律剪枝 ===
        self.simulation_step = 4
        self.log("✂️ 步骤4：规律剪枝阶段")
        pruned_rule_ids = self.bpm.pruning_phase()
        self.log(f"剪枝移除 {len(pruned_rule_ids)} 条规律")
        
        # === 步骤5：展示学习成果 ===
        self.simulation_step = 5
        self.log("🏆 步骤5：学习成果展示")
        
        # 显示高质量规律
        all_rules = self.bpm.get_all_rules()
        high_quality_rules = [r for r in all_rules if r.confidence > 0.7]
        
        self.log(f"高质量规律 (置信度>0.7): {len(high_quality_rules)}条")
        
        for i, rule in enumerate(high_quality_rules[:3], 1):
            self.log(f"  规律{i}: {rule.pattern}")
            self.log(f"    类型: {rule.rule_type.value}, 置信度: {rule.confidence:.3f}")
        
        # === 步骤6：系统统计 ===
        self.simulation_step = 6
        self.log("📈 步骤6：系统性能统计")
        
        stats = self.bpm.get_statistics()
        self.log(f"  总规律数: {stats['total_rules']}")
        self.log(f"  候选规律: {stats['candidate_rules']}")
        self.log(f"  已验证规律: {stats['validated_rules']}")
        self.log(f"  平均置信度: {stats['average_confidence']:.3f}")
        
        # === 总结 ===
        print("\n" + "=" * 80)
        print("🎉 学习循环演示完成")
        print("=" * 80)
        print(f"📊 处理经验: {len(experiences)}个")
        print(f"🌸 生成规律: {len(generated_rules)}条")  
        print(f"✅ 验证规律: {len(validated_rule_ids)}条")
        print(f"✂️ 剪枝规律: {len(pruned_rule_ids)}条")
        print(f"🏆 高质量规律: {len(high_quality_rules)}条")
        
        return {
            'experiences': len(experiences),
            'generated_rules': len(generated_rules),
            'validated_rules': len(validated_rule_ids),
            'pruned_rules': len(pruned_rule_ids),
            'high_quality_rules': len(high_quality_rules),
            'rule_types': rule_types,
            'final_stats': stats
        }

if __name__ == "__main__":
    demo = ComprehensiveDemo()
    results = demo.demonstrate_complete_cycle()
    
    print(f"\n📋 演示结果摘要:")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}") 