#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taxi环境完整ILAI系统
整合E-A-R符号化、分阶段MR、BMP、WBM和五库系统
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
import time
import numpy as np

# 导入Taxi专用组件
from taxi_ear_symbolizer import TaxiEARSymbolizer, TaxiEARExperience
from taxi_staged_multi_reward import TaxiStagedMultiReward, RewardComponents
from taxi_five_libraries import TaxiFiveLibraries, TaxiDecision
from taxi_simple_bmp_wbm import TaxiSimpleBMP, TaxiPathWBM
# 优化器相关导入已移除 - 恢复纯净ILAI系统

@dataclass
class TaxiILAIDecisionResult:
    """Taxi ILAI决策结果"""
    selected_action: str
    confidence: float
    decision_source: str
    reasoning_chain: List[str]
    decision_time: float
    stage: str
    reward_components: Optional[RewardComponents] = None

class TaxiILAISystem:
    """Taxi环境完整ILAI系统"""
    
    def __init__(self, base_dir: str = "taxi_five_libraries"):
        # 初始化所有组件
        self.ear_symbolizer = TaxiEARSymbolizer()
        self.five_libraries = TaxiFiveLibraries(base_dir)
        self.multi_reward = TaxiStagedMultiReward()
        self.bmp = TaxiSimpleBMP(self.five_libraries)
        self.wbm = TaxiPathWBM(self.five_libraries, self.bmp)
        
        # 优化器已移除 - 恢复纯净ILAI系统
        
        # ILAI系统配置
        self.config = {
            # 🔧 优化后的权重配置：平衡规则学习与探索
            "rule_based_weight": 0.8,      # 进一步提高规则权重
            "path_based_weight": 0.0,      # 🛑 保持禁用WBM路径规划
            "curiosity_weight": 0.2,       # 降低好奇心权重，避免过度探索
            
            # 学习配置
            "learning_threshold": 0.6,     # 学习阈值
            "confidence_threshold": 0.5,   # 置信度阈值
            "exploration_rate": 0.2,       # 探索率
            
            # 阶段切换配置
            "stage1_focus": "pickup",      # 阶段1专注于接客
            "stage2_focus": "dropoff",     # 阶段2专注于送客
            
            # 动作映射
            "action_space": {
                0: "下", 1: "上", 2: "右", 3: "左", 4: "pickup", 5: "dropoff"
            }
        }
        
        # 当前状态跟踪
        self.current_episode = 0
        self.current_step = 0
        self.current_path = None
        self.last_decision = None
        
        # 性能统计
        self.performance_stats = {
            "total_decisions": 0,
            "rule_based_decisions": 0,
            "path_based_decisions": 0,
            "curiosity_based_decisions": 0,
            "random_fallback_decisions": 0,
            "successful_pickups": 0,
            "successful_dropoffs": 0,
            "completed_episodes": 0
        }
        
    def make_decision(self, observation: int, available_actions: List[int] = None) -> TaxiILAIDecisionResult:
        """做出智能决策"""
        start_time = time.time()
        
        # 符号化当前状态
        current_environment = self.ear_symbolizer.symbolize_environment(observation)
        current_stage = self.ear_symbolizer.get_current_stage(observation)
        
        # 初始化推理链
        reasoning_chain = [f"当前状态: {current_environment}", f"当前阶段: {current_stage}"]
        
        # 可用动作（如果未提供，使用所有动作）
        if available_actions is None:
            available_actions = list(range(6))
        
        available_action_names = [self.config["action_space"][a] for a in available_actions]
        reasoning_chain.append(f"可用动作: {available_action_names}")
        
        # 多策略决策
        decision_candidates = []
        
        # 1. 基于规律的决策
        rule_decision = self._make_rule_based_decision(current_environment, current_stage, available_action_names)
        if rule_decision:
            decision_candidates.append({
                "action": rule_decision["action"],
                "confidence": rule_decision["confidence"] * self.config["rule_based_weight"],
                "source": "rule_based",
                "reasoning": rule_decision["reasoning"]
            })
        
        # 2. 基于路径的决策
        path_decision = self._make_path_based_decision(current_environment, current_stage, available_action_names)
        if path_decision:
            decision_candidates.append({
                "action": path_decision["action"],
                "confidence": path_decision["confidence"] * self.config["path_based_weight"],
                "source": "path_based", 
                "reasoning": path_decision["reasoning"]
            })
        
        # 3. 基于好奇心的决策
        curiosity_decision = self._make_curiosity_based_decision(observation, available_action_names)
        if curiosity_decision:
            decision_candidates.append({
                "action": curiosity_decision["action"],
                "confidence": curiosity_decision["confidence"] * self.config["curiosity_weight"],
                "source": "curiosity_based",
                "reasoning": curiosity_decision["reasoning"]
            })
        
        # 4. 随机兜底决策
        if not decision_candidates:
            random_action = random.choice(available_action_names)
            decision_candidates.append({
                "action": random_action,
                "confidence": 0.3,
                "source": "random_fallback",
                "reasoning": [f"所有策略均失败，随机选择动作: {random_action}"]
            })
        
        # 优化器已移除 - 恢复直接决策机制
        # 选择最佳决策
        if decision_candidates:
            best_decision = max(decision_candidates, key=lambda d: d["confidence"])
        else:
            # 兜底：随机选择
            random_action = random.choice(available_action_names)
            best_decision = {
                "action": random_action,
                "confidence": 0.3,
                "source": "random_fallback",
                "reasoning": [f"所有策略均失败，随机选择动作: {random_action}"]
            }
        
        # 更新推理链
        reasoning_chain.extend(best_decision["reasoning"])
        reasoning_chain.append(f"最终选择: {best_decision['action']} (置信度: {best_decision['confidence']:.2f})")
        
        # 创建决策结果
        decision_time = time.time() - start_time
        
        result = TaxiILAIDecisionResult(
            selected_action=best_decision["action"],
            confidence=best_decision["confidence"],
            decision_source=best_decision["source"],
            reasoning_chain=reasoning_chain,
            decision_time=decision_time,
            stage=current_stage
        )
        
        # 记录决策到五库
        self._record_decision(result, observation)
        
        # 更新统计
        self.performance_stats["total_decisions"] += 1
        self.performance_stats[f"{best_decision['source']}_decisions"] += 1
        
        self.last_decision = result
        return result
    
    def select_action(self, state: int) -> int:
        """实验脚本兼容接口：选择动作并返回整数动作ID"""
        # 动作名称到整数的映射
        action_name_to_id = {
            "下": 0, "上": 1, "右": 2, "左": 3, "pickup": 4, "dropoff": 5
        }
        
        # 调用核心决策方法
        decision_result = self.make_decision(state)
        
        # 转换动作名称为整数
        action_name = decision_result.selected_action
        action_id = action_name_to_id.get(action_name, 0)  # 默认返回0（下）
        
        # 存储详细决策结果供日志使用
        self.last_decision_result = decision_result
        
        return action_id
    
    def learn_from_outcome(self, old_observation: int, action_name: str, 
                          new_observation: int, reward: float, done: bool):
        """从结果中学习"""
        
        # 将动作名转换为动作索引
        action_index = None
        for idx, name in self.config["action_space"].items():
            if name == action_name:
                action_index = idx
                break
        
        if action_index is None:
            print(f"警告：未知动作 {action_name}")
            return
        
        # 创建E-A-R经验
        experience = self.ear_symbolizer.create_experience(
            old_observation, action_index, new_observation, reward, done
        )
        
        # 确定学习阶段
        stage = self.ear_symbolizer.get_current_stage(old_observation)
        
        # 添加经验到五库
        self.five_libraries.add_experience(experience, stage)
        
        # 优化器已移除 - 恢复直接学习机制
        # 通过BMP生成规律
        try:
            generated_rule = self.bmp.generate_rule_from_experience(experience, stage)
            if generated_rule:
                print(f"🌸 BMP生成规律: {generated_rule.environment_pattern} → {generated_rule.action_pattern} → {generated_rule.result_pattern}")
        except Exception as e:
            print(f"BMP规律生成失败: {e}")
        
        # 计算多元奖励
        reward_components = self.multi_reward.calculate_stage_reward(
            experience, old_observation, new_observation
        )
        
        # 如果有上次决策记录，更新其奖励组件
        if self.last_decision:
            self.last_decision.reward_components = reward_components
        
        # 更新性能统计
        if experience.result == "pickup成功":
            self.performance_stats["successful_pickups"] += 1
        elif experience.result == "dropoff成功":
            self.performance_stats["successful_dropoffs"] += 1
        
        # 优化器决策后处理已移除
        
        if done:
            self.performance_stats["completed_episodes"] += 1
            self.current_episode += 1
            self.current_step = 0
            self.current_path = None
            # 优化器回合重置已移除
        else:
            self.current_step += 1
    
    def _make_rule_based_decision(self, environment: str, stage: str, available_actions: List[str]) -> Optional[Dict]:
        """基于规律的决策"""
        
        # 获取适用规律
        applicable_rules = self.bmp.get_applicable_rules(environment, stage)
        
        if not applicable_rules:
            return None
        
        # 筛选可用动作的规律
        valid_rules = [rule for rule in applicable_rules 
                      if rule.action_pattern in available_actions]
        
        if not valid_rules:
            return None
        
        # 选择最佳规律
        best_rule = max(valid_rules, key=lambda r: r.confidence)
        
        reasoning = [
            f"找到{len(applicable_rules)}条适用规律",
            f"其中{len(valid_rules)}条动作可执行",
            f"选择最佳规律: {best_rule.environment_pattern} → {best_rule.action_pattern} → {best_rule.result_pattern}",
            f"规律置信度: {best_rule.confidence:.2f}, 支持度: {best_rule.support}"
        ]
        
        return {
            "action": best_rule.action_pattern,
            "confidence": best_rule.confidence,
            "reasoning": reasoning
        }
    
    def _make_path_based_decision(self, environment: str, stage: str, available_actions: List[str]) -> Optional[Dict]:
        """基于路径的决策（恢复到修复前的简单版本）"""
        
        # 确定目标类型
        target_type = self.config["stage1_focus"] if stage == "stage1" else self.config["stage2_focus"]
        
        # 获取或生成路径
        if not self.current_path:
            self.current_path = self.wbm.plan_path_to_target(environment, target_type, stage)
            
        if not self.current_path:
            return None
        
        # 获取下一步动作（简单版本：总是获取第一个动作）
        next_action = self.wbm.get_next_action_from_path(self.current_path, 0)
        
        if not next_action or next_action not in available_actions:
            # 路径无效，清除
            self.current_path = None
            return None
        
        reasoning = [
            f"使用路径规划: {self.current_path.path_id}",
            f"目标类型: {target_type}",
            f"路径置信度: {self.current_path.confidence:.2f}",
            f"选择动作: {next_action}"
        ]
        
        return {
            "action": next_action,
            "confidence": self.current_path.confidence,
            "reasoning": reasoning
        }
    
    def _make_curiosity_based_decision(self, observation: int, available_actions: List[str]) -> Optional[Dict]:
        """基于好奇心的决策（智能版）"""
        
        # 获取当前状态信息
        current_environment = self.ear_symbolizer.symbolize_environment(observation)
        current_stage = self.ear_symbolizer.get_current_stage(observation)
        
        # 计算每个动作的综合得分（新颖性 + 启发式）
        action_scores = {}
        
        for action_name in available_actions:
            # 1. 新颖性得分
            state_action_key = (observation, action_name)
            visit_count = self.multi_reward.action_pair_count.get(state_action_key, 0)
            novelty_score = 1.0 / (1.0 + visit_count)
            
            # 2. 启发式得分
            heuristic_score = self._calculate_action_heuristic(current_environment, action_name, current_stage)
            
            # 3. 综合得分
            total_score = novelty_score * 0.6 + heuristic_score * 0.4
            action_scores[action_name] = {
                'total': total_score,
                'novelty': novelty_score,
                'heuristic': heuristic_score
            }
        
        # 选择综合得分最高的动作
        if not action_scores:
            return None
        
        best_action = max(action_scores.keys(), key=lambda a: action_scores[a]['total'])
        best_score_data = action_scores[best_action]
        
        # 只有得分足够高才推荐
        if best_score_data['total'] < 0.3:
            return None
        
        # 构建得分展示文本
        score_text = [(a, f"{s['total']:.2f}") for a, s in action_scores.items()]
        
        reasoning = [
            f"智能好奇心决策",
            f"综合得分评估: {score_text}",
            f"选择最佳动作: {best_action} (得分: {best_score_data['total']:.2f}, 新颖性: {best_score_data['novelty']:.2f}, 启发式: {best_score_data['heuristic']:.2f})"
        ]
        
        return {
            "action": best_action,
            "confidence": best_score_data['total'],
            "reasoning": reasoning
        }
    
    def _calculate_action_heuristic(self, environment: str, action: str, stage: str) -> float:
        """计算动作的启发式得分"""
        heuristic_score = 0.5  # 基础得分
        
        # 解析环境信息
        if "pickup_" in environment:
            parts = environment.split("_")
            if len(parts) >= 8:
                pickup_status = parts[1]  # R, G, Y, B, or InCar
                dropoff_location = parts[3]  # R, G, Y, B
                taxi_position = f"taxi_at_{parts[5]}_{parts[6]}"
                
                # 阶段1：未接客，优先接客相关动作
                if pickup_status != "InCar":
                    if action == "pickup":
                        heuristic_score = 0.9  # 接客动作高分
                    elif action in ["上", "下", "左", "右"]:
                        # 移动动作根据是否靠近接客点给分
                        if "靠近" in environment:  # 简化判断
                            heuristic_score = 0.7
                        else:
                            heuristic_score = 0.4
                    else:
                        heuristic_score = 0.2  # dropoff在此阶段不适合
                
                # 阶段2：已接客，优先送客相关动作
                elif pickup_status == "InCar":
                    if action == "dropoff":
                        heuristic_score = 0.9  # 送客动作高分
                    elif action in ["上", "下", "左", "右"]:
                        # 移动动作根据是否靠近目的地给分
                        if "靠近目的地" in environment:
                            heuristic_score = 0.8
                        else:
                            heuristic_score = 0.5
                    else:
                        heuristic_score = 0.2  # pickup在此阶段不适合
        
        # 避免明显不好的动作
        if "撞墙" in environment and action in ["上", "下", "左", "右"]:
            heuristic_score = 0.1  # 撞墙动作低分
        
        return heuristic_score
    
    def _record_decision(self, result: TaxiILAIDecisionResult, observation: int):
        """记录决策到五库"""
        
        decision_id = f"decision_{self.current_episode}_{self.current_step}_{int(time.time()*1000)%10000}"
        environment = self.ear_symbolizer.symbolize_environment(observation)
        
        decision = TaxiDecision(
            decision_id=decision_id,
            environment=environment,
            action=result.selected_action,
            confidence=result.confidence,
            source=result.decision_source,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            rule_id=None,  # 可以在具体策略中填充
            path_id=self.current_path.path_id if self.current_path else None,
            stage=result.stage
        )
        
        self.five_libraries.add_decision(decision)
    
    def explain_decision(self, result: TaxiILAIDecisionResult) -> str:
        """生成决策解释"""
        explanation = f"🚕 Taxi ILAI决策解释\n"
        explanation += f"{'='*30}\n"
        explanation += f"🎯 选择动作: {result.selected_action}\n"
        explanation += f"🎲 决策置信度: {result.confidence:.2f}\n"
        explanation += f"🔍 决策来源: {result.decision_source}\n"
        explanation += f"⭐ 当前阶段: {result.stage}\n"
        explanation += f"⏱️ 决策用时: {result.decision_time:.4f}秒\n"
        
        explanation += f"\n🧠 推理过程:\n"
        for i, reason in enumerate(result.reasoning_chain, 1):
            explanation += f"   {i}. {reason}\n"
        
        if result.reward_components:
            explanation += f"\n💰 奖励分解:\n"
            explanation += f"   基础奖励: {result.reward_components.base_reward:.2f}\n"
            explanation += f"   导航奖励: {result.reward_components.navigation_reward:.2f}\n"
            explanation += f"   任务奖励: {result.reward_components.task_reward:.2f}\n"
            explanation += f"   效率奖励: {result.reward_components.efficiency_reward:.2f}\n"
            explanation += f"   探索奖励: {result.reward_components.exploration_reward:.2f}\n"
            explanation += f"   总奖励: {result.reward_components.total_reward:.2f}\n"
        
        return explanation
    
    def get_comprehensive_statistics(self) -> Dict:
        """获取综合统计信息"""
        
        # 获取各组件统计
        five_libs_stats = self.five_libraries.get_statistics()
        bmp_stats = self.bmp.get_statistics()
        wbm_stats = self.wbm.get_statistics()
        mr_stats = self.multi_reward.get_stage_statistics()
        symbolizer_stats = self.ear_symbolizer.get_statistics_summary()
        
        # 优化器统计已移除
        
        # 组合统计
        comprehensive_stats = {
            "performance": self.performance_stats,
            "five_libraries": five_libs_stats,
            "bmp": bmp_stats,
            "wbm": wbm_stats,
            "multi_reward": mr_stats,
            "symbolizer": symbolizer_stats,
            "system_info": {
                "current_episode": self.current_episode,
                "current_step": self.current_step,
                "has_active_path": self.current_path is not None
            }
        }
        
        return comprehensive_stats
    
    # 优化器摘要方法已移除 - 系统恢复纯净状态

# 测试函数
def test_taxi_ilai_system():
    """测试Taxi ILAI系统"""
    print("🚕 测试Taxi ILAI完整系统")
    print("=" * 35)
    
    # 创建ILAI系统
    ilai = TaxiILAISystem("test_taxi_ilai_system")
    ilai.five_libraries.clear_all_data()
    
    # 模拟一个简单的决策-学习循环
    print(f"\n🎯 模拟决策-学习循环:")
    
    # 测试状态：出租车在(3,1)，乘客在Y站点，目的地是R站点
    test_state = 328
    
    # 第1步：做决策
    decision1 = ilai.make_decision(test_state, [0, 1, 2, 3, 4])  # 移动和pickup动作
    print(f"\n决策1:")
    print(f"   选择动作: {decision1.selected_action}")
    print(f"   决策来源: {decision1.decision_source}")
    print(f"   置信度: {decision1.confidence:.2f}")
    
    # 第2步：学习结果
    # 假设选择了"下"动作，移动到更靠近Y站点
    new_state = 428
    reward = -1  # 正常移动奖励
    ilai.learn_from_outcome(test_state, decision1.selected_action, new_state, reward, False)
    
    print(f"\n学习结果:")
    print(f"   经验已添加到五库")
    print(f"   BMP可能生成了新规律")
    
    # 第3步：再次决策（应该能使用学到的规律）
    decision2 = ilai.make_decision(new_state, [0, 1, 2, 3, 4])
    print(f"\n决策2:")
    print(f"   选择动作: {decision2.selected_action}")
    print(f"   决策来源: {decision2.decision_source}")
    print(f"   置信度: {decision2.confidence:.2f}")
    
    # 详细解释
    print(f"\n📖 决策详细解释:")
    print(ilai.explain_decision(decision2))
    
    # 系统统计
    stats = ilai.get_comprehensive_statistics()
    print(f"\n📊 系统综合统计:")
    print(f"   总决策数: {stats['performance']['total_decisions']}")
    print(f"   五库经验数: {stats['five_libraries']['total_experiences']}")
    print(f"   五库规律数: {stats['five_libraries']['total_rules']}")
    print(f"   BMP生成规律数: {stats['bmp']['generated_rules']}")
    print(f"   WBM生成路径数: {stats['wbm']['paths_generated']}")

if __name__ == "__main__":
    test_taxi_ilai_system()
