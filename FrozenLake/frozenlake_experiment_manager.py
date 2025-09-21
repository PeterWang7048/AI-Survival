#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrozenLake论文实验主框架
========================

基于最佳单向优化版本 RegionBasedILAI (72-75%成功率)
完整的6个基线算法对比实验系统

特性:
- 可配置实验次数和回合数
- 详细独立日志记录
- 完整决策过程追踪
- 自动排行榜生成
"""

import os
import time
import numpy as np
import gymnasium as gym
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DecisionResult:
    """统一决策结果接口"""
    selected_action: str
    confidence: float
    decision_source: str
    reasoning: str
    decision_time: float

@dataclass
class ExperimentResult:
    """实验结果记录"""
    agent_name: str
    success_rate: float
    avg_reward: float
    avg_steps: float
    total_episodes: int
    successful_episodes: int
    decision_stats: Dict
    performance_score: float

class PaperExperimentManager:
    """论文实验管理器"""
    
    def __init__(self, num_experiments: int = 20, episodes_per_experiment: int = 300):
        self.num_experiments = num_experiments
        self.episodes_per_experiment = episodes_per_experiment
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 使用指定的日志目录
        self.log_dir = "000log"
        os.makedirs(self.log_dir, exist_ok=True)
        
        print(f"🚀 FrozenLake论文实验管理器启动")
        print(f"📊 实验配置:")
        print(f"  🔢 实验次数: {num_experiments}")
        print(f"  🎮 每次回合数: {episodes_per_experiment}")
        print(f"  📁 日志目录: {self.log_dir}")
        print("=" * 60)
    
    def run_complete_experiments(self, agents: List[Any]):
        """运行完整实验"""
        print(f"🤖 加载{len(agents)}个智能体:")
        for agent in agents:
            print(f"  - {agent.player_name}")
        print()
        
        all_results = []
        
        for exp_id in range(1, self.num_experiments + 1):
            print(f"\n🔬 实验 {exp_id}/{self.num_experiments} 开始...")
            print("-" * 40)
            
            exp_results = self._run_single_experiment(exp_id, agents)
            all_results.extend(exp_results)
            
            print(f"✅ 实验 {exp_id} 完成")
            
            # 显示当前最佳表现
            current_best = max(exp_results, key=lambda x: x.performance_score)
            print(f"  🏆 本轮最佳: {current_best.agent_name} ({current_best.success_rate:.1%})")
        
        # 生成最终报告
        leaderboard = self._generate_final_report(all_results)
        
        return all_results, leaderboard
    
    def _run_single_experiment(self, exp_id: int, agents: List[Any]) -> List[ExperimentResult]:
        """运行单次实验 - 统一日志版本"""
        experiment_results = []
        
        # 创建统一的实验日志文件
        log_file = os.path.join(self.log_dir, f"paper_experiment_{exp_id:02d}_{self.timestamp}.log")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            # 写入实验头部信息
            f.write(f"FrozenLake论文实验统一日志\n")
            f.write(f"{'='*80}\n")
            f.write(f"实验编号: {exp_id}\n")
            f.write(f"智能体数量: {len(agents)}\n")
            f.write(f"每智能体回合数: {self.episodes_per_experiment}\n")
            f.write(f"环境设置: FrozenLake-v1, is_slippery=True\n")
            f.write(f"开始时间: {datetime.now()}\n")
            f.write(f"{'='*80}\n\n")
            
            # 逐个测试智能体
            for agent_idx, agent in enumerate(agents, 1):
                print(f"  🤖 测试 {agent.player_name}...")
                
                f.write(f"{'#'*60}\n")
                f.write(f"智能体 {agent_idx}/{len(agents)}: {agent.player_name}\n")
                f.write(f"{'#'*60}\n\n")
                
                # 运行智能体测试并记录到统一日志
                result = self._test_agent_unified(agent, exp_id, f)
                experiment_results.append(result)
                
                print(f"    📊 成功率: {result.success_rate:.1%} | "
                      f"平均奖励: {result.avg_reward:.3f} | "
                      f"平均步数: {result.avg_steps:.1f}")
                
                # 在日志中添加智能体总结
                f.write(f"\n📊 {agent.player_name} 实验总结:\n")
                f.write(f"  成功率: {result.success_rate:.1%} ({result.successful_episodes}/{result.total_episodes})\n")
                f.write(f"  平均奖励: {result.avg_reward:.4f}\n")
                f.write(f"  平均步数: {result.avg_steps:.2f}\n")
                f.write(f"  决策统计: {result.decision_stats}\n")
                f.write(f"  完成时间: {datetime.now()}\n\n")
            
            # 在日志结尾添加本次实验的排行榜
            self._write_experiment_leaderboard(f, experiment_results, exp_id)
        
        return experiment_results
    
    def _test_agent_unified(self, agent, exp_id: int, f) -> ExperimentResult:
        """测试单个智能体"""
        
        env = gym.make('FrozenLake-v1', is_slippery=True, render_mode=None)
        
        success_count = 0
        total_rewards = []
        total_steps = []
        
        for episode in range(self.episodes_per_experiment):
            # 设置随机种子确保可重现
            episode_seed = exp_id * 1000 + episode + 2000
            state, _ = env.reset(seed=episode_seed)
            
            agent.start_episode(f"exp{exp_id}_ep{episode}")
            
            total_reward = 0
            steps = 0
            prev_action = None
            prev_reward = 0.0
            
            f.write(f"回合 {episode+1:3d}/{self.episodes_per_experiment}:\n")
            f.write(f"  初始状态: {state}\n")
            
            while steps < 200:  # 最大步数限制
                available_actions = ['LEFT', 'DOWN', 'RIGHT', 'UP']
                
                # 智能体决策
                decision = agent.decide_action(
                    observation=state,
                    available_actions=available_actions,
                    prev_action=prev_action,
                    prev_reward=prev_reward,
                    prev_done=False
                )
                
                # 记录决策详情
                f.write(f"    步骤{steps+1:2d}: 状态{state} -> {decision.selected_action} "
                       f"(置信度:{decision.confidence:.2f}, {decision.decision_source})\n")
                f.write(f"           推理: {decision.reasoning}\n")
                
                # 执行动作
                action_map = {'LEFT': 0, 'DOWN': 1, 'RIGHT': 2, 'UP': 3}
                action_int = action_map[decision.selected_action]
                
                prev_action = decision.selected_action
                prev_reward = total_reward
                
                next_state, reward, done, truncated, info = env.step(action_int)
                
                total_reward += reward
                steps += 1
                
                # 记录执行结果
                f.write(f"           结果: {state} -> {next_state}, "
                       f"奖励:{reward}, 完成:{done}, 截断:{truncated}\n")
                
                # 🔥 学术公平ILAI系统的学习机制
                if hasattr(agent, 'learn_from_experience'):
                    agent.learn_from_experience(next_state, prev_action, reward, done, truncated)
                
                state = next_state
                
                if done or truncated:
                    break
            
            # 记录回合结果
            episode_success = reward > 0
            if episode_success:
                success_count += 1
            
            total_rewards.append(total_reward)
            total_steps.append(steps)
            
            f.write(f"  回合结果: {'成功' if episode_success else '失败'}, "
                   f"奖励:{total_reward}, 步数:{steps}\n\n")
            
            # 进度显示(每50回合)
            if (episode + 1) % 50 == 0:
                current_success = success_count / (episode + 1)
                f.write(f"  >>> 进度 {episode+1}/{self.episodes_per_experiment}: "
                       f"当前成功率 {current_success:.1%}\n\n")
        
        # 计算最终统计
        success_rate = success_count / self.episodes_per_experiment
        avg_reward = sum(total_rewards) / len(total_rewards)
        avg_steps = sum(total_steps) / len(total_steps)
        
        env.close()
        
        # 计算性能分数(综合指标)
        performance_score = (
            success_rate * 0.7 +  # 成功率权重70%
            avg_reward * 0.2 +    # 平均奖励权重20%
            (max(0, 200 - avg_steps) / 200) * 0.1  # 效率权重10%
        )
        
        return ExperimentResult(
            agent_name=agent.player_name,
            success_rate=success_rate,
            avg_reward=avg_reward,
            avg_steps=avg_steps,
            total_episodes=self.episodes_per_experiment,
            successful_episodes=success_count,
            decision_stats=agent.get_decision_stats(),
            performance_score=performance_score
        )
    
    def _write_experiment_leaderboard(self, f, experiment_results: List[ExperimentResult], exp_id: int):
        """在日志文件中写入实验排行榜"""
        
        # 按性能排序
        sorted_results = sorted(experiment_results, key=lambda x: x.performance_score, reverse=True)
        
        f.write(f"\n{'='*80}\n")
        f.write(f"🏆 实验 {exp_id} 排行榜 🏆\n")
        f.write(f"{'='*80}\n")
        f.write(f"排名 | {'智能体名称':<25} | {'成功率':<8} | {'平均奖励':<8} | {'平均步数':<8} | {'综合分':<8}\n")
        f.write(f"{'-'*80}\n")
        
        for i, result in enumerate(sorted_results, 1):
            f.write(f"{i:2d}   | {result.agent_name:<25} | "
                   f"{result.success_rate:7.1%} | "
                   f"{result.avg_reward:8.4f} | "
                   f"{result.avg_steps:8.1f} | "
                   f"{result.performance_score:8.4f}\n")
        
        f.write(f"\n📊 实验 {exp_id} 详细分析:\n")
        for i, result in enumerate(sorted_results, 1):
            f.write(f"{i}. {result.agent_name}:\n")
            f.write(f"   成功率: {result.success_rate:.1%} ({result.successful_episodes}/{result.total_episodes})\n")
            f.write(f"   平均奖励: {result.avg_reward:.4f}\n")
            f.write(f"   平均步数: {result.avg_steps:.2f}\n")
            f.write(f"   综合性能分: {result.performance_score:.4f}\n")
            f.write(f"   决策统计: {result.decision_stats}\n\n")
        
        # 找出最佳智能体
        best_result = sorted_results[0]
        f.write(f"🌟 实验 {exp_id} 最佳智能体: {best_result.agent_name}\n")
        f.write(f"   🏆 成功率: {best_result.success_rate:.1%}\n")
        f.write(f"   📈 综合得分: {best_result.performance_score:.4f}\n")
        f.write(f"   ⏱️ 完成时间: {datetime.now()}\n")
        f.write(f"{'='*80}\n")
    
    def _generate_final_report(self, all_results: List[ExperimentResult]) -> List[Dict]:
        """生成最终报告和排行榜"""
        
        # 按智能体分组统计
        agent_stats = defaultdict(list)
        for result in all_results:
            agent_stats[result.agent_name].append(result)
        
        # 生成排行榜
        leaderboard = []
        for agent_name, results in agent_stats.items():
            avg_success_rate = sum(r.success_rate for r in results) / len(results)
            avg_reward = sum(r.avg_reward for r in results) / len(results)
            avg_steps = sum(r.avg_steps for r in results) / len(results)
            avg_performance = sum(r.performance_score for r in results) / len(results)
            
            # 计算标准差
            success_rates = [r.success_rate for r in results]
            success_std = np.std(success_rates) if len(success_rates) > 1 else 0
            
            leaderboard.append({
                'agent_name': agent_name,
                'avg_success_rate': avg_success_rate,
                'success_std': success_std,
                'avg_reward': avg_reward,
                'avg_steps': avg_steps,
                'avg_performance': avg_performance,
                'experiments': len(results)
            })
        
        # 按性能排序
        leaderboard.sort(key=lambda x: x['avg_performance'], reverse=True)
        
        # 写入最终报告到000log目录
        report_file = os.path.join(self.log_dir, f"final_report_{self.timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"FrozenLake完整论文实验最终报告\n")
            f.write(f"{'='*80}\n")
            f.write(f"实验配置:\n")
            f.write(f"  实验次数: {self.num_experiments}\n")
            f.write(f"  每次回合数: {self.episodes_per_experiment}\n")
            f.write(f"  总测试回合: {self.num_experiments * self.episodes_per_experiment}\n")
            f.write(f"  完成时间: {datetime.now()}\n")
            f.write(f"\n{'='*80}\n")
            
            f.write(f"🏆 智能体性能排行榜 🏆\n")
            f.write(f"{'='*80}\n")
            f.write(f"排名 | {'智能体名称':<25} | {'成功率':<12} | {'平均奖励':<8} | {'平均步数':<8} | {'综合分':<8}\n")
            f.write(f"{'-'*80}\n")
            
            for i, stats in enumerate(leaderboard, 1):
                f.write(f"{i:2d}   | {stats['agent_name']:<25} | "
                       f"{stats['avg_success_rate']:6.1%}±{stats['success_std']:4.1%} | "
                       f"{stats['avg_reward']:8.4f} | "
                       f"{stats['avg_steps']:8.1f} | "
                       f"{stats['avg_performance']:8.4f}\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"详细统计分析:\n")
            
            for i, stats in enumerate(leaderboard, 1):
                f.write(f"\n{i}. {stats['agent_name']}:\n")
                f.write(f"   平均成功率: {stats['avg_success_rate']:.1%} ± {stats['success_std']:.1%}\n")
                f.write(f"   平均奖励: {stats['avg_reward']:.4f}\n")
                f.write(f"   平均步数: {stats['avg_steps']:.2f}\n")
                f.write(f"   综合性能分: {stats['avg_performance']:.4f}\n")
                f.write(f"   实验次数: {stats['experiments']}\n")
                cv = stats['success_std']/stats['avg_success_rate'] if stats['avg_success_rate'] > 0 else 0
                f.write(f"   变异系数: {cv:.3f}\n")
        
        # 输出到控制台
        print(f"\n🏆 实验完成！最终排行榜：")
        print("=" * 85)
        print(f"排名 | {'智能体名称':<25} | {'成功率':<12} | {'平均奖励':<8} | {'平均步数':<8} | {'综合分':<8}")
        print("-" * 85)
        
        for i, stats in enumerate(leaderboard, 1):
            print(f"{i:2d}   | {stats['agent_name']:<25} | "
                  f"{stats['avg_success_rate']:6.1%}±{stats['success_std']:4.1%} | "
                  f"{stats['avg_reward']:8.4f} | "
                  f"{stats['avg_steps']:8.1f} | "
                  f"{stats['avg_performance']:8.4f}")
        
        print(f"\n📁 详细日志和报告已保存到: {self.log_dir}")
        print(f"📊 最终报告文件: {report_file}")
        
        # 显示关键发现
        best_agent = leaderboard[0]
        print(f"\n🌟 关键发现:")
        print(f"  🏆 最佳智能体: {best_agent['agent_name']}")
        print(f"  📊 最高成功率: {best_agent['avg_success_rate']:.1%} ± {best_agent['success_std']:.1%}")
        print(f"  🎯 综合性能分: {best_agent['avg_performance']:.4f}")
        
        return leaderboard

def main():
    """主函数 - 用于独立运行"""
    print("🎯 论文实验管理器 - 独立测试模式")
    print("请使用 run_paper_experiment.py 进行完整实验")
    
    # 简单配置示例
    manager = PaperExperimentManager(num_experiments=3, episodes_per_experiment=50)
    print(f"✅ 实验管理器创建成功")
    print(f"📁 日志目录: {manager.log_dir}")
    
    return manager

if __name__ == "__main__":
    manager = main()
