#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Decision Mechanism Analysis and Survival Capability Comparison
Comprehensive analysis based on game logs and research background
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple
import re
from collections import defaultdict

# Set Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class AIDecisionAnalyzer:
    def __init__(self):
        """Initialize AI decision analyzer"""
        self.user_types = {
            'ILAI': 'Infant Learning AI (ILAI)',
            'RILAI': 'Reinforced Infant Learning AI (RILAI)', 
            'DQN': 'Deep Q-Network (DQN)',
            'PPO': 'Proximal Policy Optimization (PPO)'
        }
        
        # Ranking data based on log analysis
        self.ranking_data = [
            {"rank": 1, "player": "ILAI1", "survival_days": 10, "reputation": 145, "hp": 100, "food": 100, "water": 100},
            {"rank": 2, "player": "ILAI10", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 3, "player": "ILAI4", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 4, "player": "ILAI5", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 5, "player": "ILAI6", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 6, "player": "ILAI8", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 7, "player": "ILAI9", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 8, "player": "RILAI10", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 9, "player": "RILAI2", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 10, "player": "RILAI4", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 11, "player": "RILAI7", "survival_days": 10, "reputation": 140, "hp": 100, "food": 100, "water": 100},
            {"rank": 12, "player": "PPO3", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 96},
            {"rank": 13, "player": "PPO9", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 92},
            {"rank": 14, "player": "DQN8", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 91},
            {"rank": 15, "player": "DQN1", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 90},
            {"rank": 16, "player": "DQN10", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 90},
            {"rank": 17, "player": "PPO10", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 90},
            {"rank": 18, "player": "PPO8", "survival_days": 10, "reputation": 100, "hp": 100, "food": 90, "water": 90},
            {"rank": 19, "player": "DQN6", "survival_days": 10, "reputation": 100, "hp": 40, "food": 90, "water": 90},
            {"rank": 20, "player": "DQN4", "survival_days": 10, "reputation": 100, "hp": 10, "food": 90, "water": 90},
            {"rank": 21, "player": "DQN3", "survival_days": 10, "reputation": 100, "hp": -20, "food": 90, "water": 100},
            {"rank": 22, "player": "PPO7", "survival_days": 8, "reputation": 100, "hp": 0, "food": 92, "water": 100},
            {"rank": 23, "player": "ILAI3", "survival_days": 7, "reputation": 133, "hp": 0, "food": 100, "water": 100},
            {"rank": 24, "player": "RILAI8", "survival_days": 7, "reputation": 128, "hp": 0, "food": 100, "water": 100},
            {"rank": 25, "player": "DQN7", "survival_days": 7, "reputation": 100, "hp": 0, "food": 93, "water": 93},
            {"rank": 26, "player": "DQN2", "survival_days": 6, "reputation": 100, "hp": 0, "food": 94, "water": 94},
            {"rank": 27, "player": "DQN9", "survival_days": 6, "reputation": 100, "hp": 0, "food": 94, "water": 94},
            {"rank": 28, "player": "PPO2", "survival_days": 6, "reputation": 100, "hp": 0, "food": 94, "water": 94},
            {"rank": 29, "player": "ILAI2", "survival_days": 5, "reputation": 120, "hp": 0, "food": 100, "water": 100},
            {"rank": 30, "player": "RILAI5", "survival_days": 5, "reputation": 120, "hp": 0, "food": 100, "water": 100},
            {"rank": 31, "player": "RILAI6", "survival_days": 5, "reputation": 120, "hp": 0, "food": 100, "water": 100},
            {"rank": 32, "player": "PPO1", "survival_days": 5, "reputation": 100, "hp": 0, "food": 95, "water": 95},
            {"rank": 33, "player": "PPO4", "survival_days": 5, "reputation": 100, "hp": 0, "food": 95, "water": 95},
            {"rank": 34, "player": "DQN5", "survival_days": 3, "reputation": 100, "hp": 0, "food": 97, "water": 97},
            {"rank": 35, "player": "PPO5", "survival_days": 3, "reputation": 100, "hp": 0, "food": 97, "water": 97},
            {"rank": 36, "player": "PPO6", "survival_days": 3, "reputation": 100, "hp": 0, "food": 97, "water": 97},
            {"rank": 37, "player": "ILAI7", "survival_days": 2, "reputation": 108, "hp": 0, "food": 100, "water": 100},
            {"rank": 38, "player": "RILAI9", "survival_days": 2, "reputation": 108, "hp": 0, "food": 100, "water": 100},
            {"rank": 39, "player": "RILAI1", "survival_days": 1, "reputation": 104, "hp": 0, "food": 100, "water": 100},
            {"rank": 40, "player": "RILAI3", "survival_days": 1, "reputation": 104, "hp": 0, "food": 100, "water": 100}
        ]
        
        self.df = pd.DataFrame(self.ranking_data)
        self.df['ai_type'] = self.df['player'].str.extract(r'([A-Z]+)')
        
    def analyze_decision_mechanisms(self) -> Dict:
        """Analyze decision mechanisms of various AI types"""
        mechanisms = {
            'ILAI': {
                'Architecture': 'DHCA (Developmental Hierarchical Cognitive Architecture)',
                'Core Modules': [
                    'Instinctive Layer',
                    'Experiential Layer', 
                    'Logical Layer'
                ],
                'Decision Mechanisms': [
                    'Scene Symbolization Mechanism (SSM)',
                    'Blooming and Pruning Model (BPM)',
                    'Wooden Bridge Model (WBM)',
                    'Dynamic Multi-Head Attention (DMHA)',
                    'Curiosity-Driven Learning (CDL)'
                ],
                'Learning Method': 'Experience-based pattern mining and validation',
                'Decision Process': 'Goal-oriented pattern combination and application',
                'Interpretability': 'High - Symbolized decision process',
                'Adaptability': 'Strong - Developmental dynamic adjustment'
            },
            'RILAI': {
                'Architecture': 'DHCA + Reinforcement Learning',
                'Core Modules': [
                    'All ILAI modules retained',
                    'State-Action Value Function (Q-Learning)',
                    'Experience Replay Buffer',
                    'Exploration-Exploitation Balance Strategy'
                ],
                'Decision Mechanisms': [
                    'All ILAI mechanisms',
                    'Q-value optimization',
                    'ε-greedy exploration'
                ],
                'Learning Method': 'Infant learning + Reinforcement learning dual optimization',
                'Decision Process': 'Symbolic reasoning + Value function guidance',
                'Interpretability': 'Medium-High - Partially interpretable',
                'Adaptability': 'Very Strong - Dual learning mechanism'
            },
            'DQN': {
                'Architecture': 'Deep Neural Network',
                'Core Modules': [
                    'Experience Replay Buffer',
                    'Target Network',
                    'Deep Q-Network'
                ],
                'Decision Mechanisms': [
                    'Q-value based greedy selection',
                    'ε-greedy exploration strategy',
                    'Experience replay training'
                ],
                'Learning Method': 'Reward-based value function learning',
                'Decision Process': 'Neural network forward propagation',
                'Interpretability': 'Low - Black box decision',
                'Adaptability': 'Medium - Requires extensive training'
            },
            'PPO': {
                'Architecture': 'Actor-Critic Framework',
                'Core Modules': [
                    'Actor Network (Policy)',
                    'Critic Network (Value)',
                    'Advantage Function Estimation'
                ],
                'Decision Mechanisms': [
                    'Policy gradient optimization',
                    'Clipped policy updates',
                    'Entropy regularization exploration'
                ],
                'Learning Method': 'Policy gradient + Value function learning',
                'Decision Process': 'Probabilistic policy sampling',
                'Interpretability': 'Low - Neural network policy',
                'Adaptability': 'Medium - Stable learning'
            }
        }
        return mechanisms
    
    def calculate_survival_metrics(self) -> Dict:
        """Calculate survival metrics for each AI type"""
        metrics = {}
        
        for ai_type in ['ILAI', 'RILAI', 'DQN', 'PPO']:
            type_data = self.df[self.df['ai_type'] == ai_type]
            
            # Survival capability metrics
            survival_rate = len(type_data[type_data['survival_days'] >= 10]) / len(type_data) * 100
            avg_survival_days = type_data['survival_days'].mean()
            max_survival_days = type_data['survival_days'].max()
            
            # Learning capability metrics (based on reputation growth)
            avg_reputation = type_data['reputation'].mean()
            reputation_std = type_data['reputation'].std()
            
            # Adaptation capability metrics (based on resource management)
            avg_final_hp = type_data['hp'].mean()
            avg_final_food = type_data['food'].mean()
            avg_final_water = type_data['water'].mean()
            
            # Comprehensive scoring
            survival_score = avg_survival_days * 10
            learning_score = (avg_reputation - 100) * 2  # Baseline reputation 100
            adaptation_score = (avg_final_hp + avg_final_food + avg_final_water) / 3
            overall_score = (survival_score + learning_score + adaptation_score) / 3
            
            metrics[ai_type] = {
                'survival_rate': survival_rate,
                'avg_survival_days': avg_survival_days,
                'max_survival_days': max_survival_days,
                'avg_reputation': avg_reputation,
                'reputation_std': reputation_std,
                'avg_final_hp': avg_final_hp,
                'avg_final_food': avg_final_food,
                'avg_final_water': avg_final_water,
                'survival_score': survival_score,
                'learning_score': learning_score,
                'adaptation_score': adaptation_score,
                'overall_score': overall_score
            }
            
        return metrics
    
    def plot_survival_comparison(self):
        """绘制生存能力比较图"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI生存能力综合比较分析', fontsize=16, fontweight='bold')
        
        # 1. 生存天数分布
        axes[0, 0].set_title('生存天数分布对比')
        survival_data = []
        labels = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, ai_type in enumerate(['ILAI', 'RILAI', 'DQN', 'PPO']):
            type_data = self.df[self.df['ai_type'] == ai_type]['survival_days']
            survival_data.append(type_data)
            labels.append(f'{self.user_types[ai_type]} (n={len(type_data)})')
        
        bp = axes[0, 0].boxplot(survival_data, labels=['ILAI', 'RILAI', 'DQN', 'PPO'], 
                               patch_artist=True, showmeans=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        axes[0, 0].set_ylabel('生存天数')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 生存率对比
        axes[0, 1].set_title('生存率对比 (≥10天)')
        survival_rates = []
        for ai_type in ['ILAI', 'RILAI', 'DQN', 'PPO']:
            type_data = self.df[self.df['ai_type'] == ai_type]
            rate = len(type_data[type_data['survival_days'] >= 10]) / len(type_data) * 100
            survival_rates.append(rate)
        
        bars = axes[0, 1].bar(['ILAI', 'RILAI', 'DQN', 'PPO'], survival_rates, 
                             color=colors, alpha=0.8)
        axes[0, 1].set_ylabel('生存率 (%)')
        axes[0, 1].set_ylim(0, 100)
        for i, (bar, rate) in enumerate(zip(bars, survival_rates)):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                           f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 3. 声誉(学习能力)对比
        axes[1, 0].set_title('学习能力对比 (平均声誉)')
        reputation_data = []
        for ai_type in ['ILAI', 'RILAI', 'DQN', 'PPO']:
            type_data = self.df[self.df['ai_type'] == ai_type]['reputation']
            reputation_data.append(type_data)
        
        bp2 = axes[1, 0].boxplot(reputation_data, labels=['ILAI', 'RILAI', 'DQN', 'PPO'], 
                                patch_artist=True, showmeans=True)
        for patch, color in zip(bp2['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        axes[1, 0].set_ylabel('Reputation Value')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Comprehensive resource management capability
        axes[1, 1].set_title('Resource Management Capability Comparison')
        ai_types = ['ILAI', 'RILAI', 'DQN', 'PPO']
        hp_avg = [self.df[self.df['ai_type'] == t]['hp'].mean() for t in ai_types]
        food_avg = [self.df[self.df['ai_type'] == t]['food'].mean() for t in ai_types]
        water_avg = [self.df[self.df['ai_type'] == t]['water'].mean() for t in ai_types]
        
        x = np.arange(len(ai_types))
        width = 0.25
        
        axes[1, 1].bar(x - width, hp_avg, width, label='HP', color='#FF6B6B', alpha=0.8)
        axes[1, 1].bar(x, food_avg, width, label='Food', color='#4ECDC4', alpha=0.8)
        axes[1, 1].bar(x + width, water_avg, width, label='Water', color='#45B7D1', alpha=0.8)
        
        axes[1, 1].set_ylabel('Average Resource Value')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(ai_types)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('ai_survival_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_learning_curves(self):
        """Plot learning curves"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Learning Ability and Adaptability Analysis', fontsize=16, fontweight='bold')
        
        metrics = self.calculate_survival_metrics()
        ai_types = list(metrics.keys())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        # 1. Learning efficiency comparison (reputation growth)
        axes[0, 0].set_title('Learning Efficiency Comparison')
        learning_scores = [metrics[ai]['learning_score'] for ai in ai_types]
        reputation_stds = [metrics[ai]['reputation_std'] for ai in ai_types]
        
        bars = axes[0, 0].bar(ai_types, learning_scores, color=colors, alpha=0.8)
        axes[0, 0].set_ylabel('Learning Score')
        for i, (bar, score) in enumerate(zip(bars, learning_scores)):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                           f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. Adaptability comparison
        axes[0, 1].set_title('Environmental Adaptability Comparison')
        adaptation_scores = [metrics[ai]['adaptation_score'] for ai in ai_types]
        
        bars = axes[0, 1].bar(ai_types, adaptation_scores, color=colors, alpha=0.8)
        axes[0, 1].set_ylabel('Adaptability Score')
        for i, (bar, score) in enumerate(zip(bars, adaptation_scores)):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                           f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 3. Comprehensive performance radar chart
        axes[1, 0].set_title('Comprehensive Performance Radar Chart')
        
        # Radar chart data
        categories = ['Survival Ability', 'Learning Ability', 'Adaptability', 'Stability']
        N = len(categories)
        
        # Calculate angles
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the circle
        
        ax_radar = plt.subplot(2, 2, 3, projection='polar')
        
        for i, ai_type in enumerate(ai_types):
            values = [
                metrics[ai_type]['survival_score'] / 100,  # 归一化
                metrics[ai_type]['learning_score'] / 80,   # 归一化  
                metrics[ai_type]['adaptation_score'] / 100, # 归一化
                100 - metrics[ai_type]['reputation_std']   # 稳定性 (标准差越小越稳定)
            ]
            values += values[:1]  # 闭合
            
            ax_radar.plot(angles, values, linewidth=2, linestyle='solid', 
                         label=self.user_types[ai_type], color=colors[i])
            ax_radar.fill(angles, values, color=colors[i], alpha=0.25)
        
        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(categories)
        ax_radar.set_ylim(0, 100)
        ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax_radar.grid(True)
        
        # 4. 生存时间分布
        axes[1, 1].set_title('生存时间分布')
        for i, ai_type in enumerate(ai_types):
            type_data = self.df[self.df['ai_type'] == ai_type]
            survival_counts = type_data['survival_days'].value_counts().sort_index()
            
            axes[1, 1].plot(survival_counts.index, survival_counts.values, 
                           marker='o', linewidth=2, label=self.user_types[ai_type], 
                           color=colors[i])
        
        axes[1, 1].set_xlabel('生存天数')
        axes[1, 1].set_ylabel('个体数量')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ai_learning_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_decision_mechanisms(self):
        """可视化决策机制对比"""
        fig, ax = plt.subplots(figsize=(16, 10))
        fig.suptitle('AI决策机制架构对比', fontsize=16, fontweight='bold')
        
        mechanisms = self.analyze_decision_mechanisms()
        
        # 创建决策机制对比表
        mechanism_features = [
            '分层认知架构', '符号化推理', '规律挖掘', '经验学习', 
            '价值函数优化', '策略梯度', '可解释性', '适应性'
        ]
        
        ai_features = {
            'ILAI': [1, 1, 1, 1, 0, 0, 1, 1],      # 高可解释性和适应性
            'RILAI': [1, 1, 1, 1, 1, 0, 0.7, 1],   # 混合方法
            'DQN': [0, 0, 0, 1, 1, 0, 0.2, 0.6],   # 价值函数方法
            'PPO': [0, 0, 0, 1, 0.5, 1, 0.2, 0.6]  # 策略梯度方法
        }
        
        # 创建热力图
        feature_matrix = np.array([ai_features[ai] for ai in ['ILAI', 'RILAI', 'DQN', 'PPO']])
        
        im = ax.imshow(feature_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # 设置标签
        ax.set_xticks(range(len(mechanism_features)))
        ax.set_xticklabels(mechanism_features, rotation=45, ha='right')
        ax.set_yticks(range(len(['ILAI', 'RILAI', 'DQN', 'PPO'])))
        ax.set_yticklabels([self.user_types[ai] for ai in ['ILAI', 'RILAI', 'DQN', 'PPO']])
        
        # 添加数值标注
        for i in range(len(['ILAI', 'RILAI', 'DQN', 'PPO'])):
            for j in range(len(mechanism_features)):
                value = feature_matrix[i, j]
                color = 'white' if value < 0.5 else 'black'
                ax.text(j, i, f'{value:.1f}', ha='center', va='center', 
                       color=color, fontweight='bold')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('能力强度', rotation=270, labelpad=20)
        
        plt.tight_layout()
        plt.savefig('ai_decision_mechanisms.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("=" * 80)
        print("AI决策机制与生存能力综合分析报告")
        print("=" * 80)
        
        mechanisms = self.analyze_decision_mechanisms()
        metrics = self.calculate_survival_metrics()
        
        print("\n1. 决策机制分析")
        print("-" * 50)
        
        for ai_type, details in mechanisms.items():
            print(f"\n【{self.user_types[ai_type]}】")
            print(f"架构: {details['架构']}")
            print(f"学习方式: {details['学习方式']}")
            print(f"决策过程: {details['决策过程']}")
            print(f"可解释性: {details['可解释性']}")
            print(f"适应性: {details['适应性']}")
            print(f"核心模块: {', '.join(details['核心模块'][:3])}...")
        
        print("\n\n2. 生存能力指标")
        print("-" * 50)
        
        # 排序并显示性能
        sorted_ais = sorted(metrics.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        
        print(f"{'AI类型':<15} {'综合评分':<10} {'生存率':<10} {'平均生存天数':<12} {'平均声誉':<10}")
        print("-" * 65)
        
        for ai_type, data in sorted_ais:
            print(f"{self.user_types[ai_type]:<15} {data['overall_score']:<10.1f} "
                  f"{data['survival_rate']:<10.1f}% {data['avg_survival_days']:<12.1f} "
                  f"{data['avg_reputation']:<10.1f}")
        
        print("\n\n3. 关键发现")
        print("-" * 50)
        
        # 分析各AI的优势
        best_survival = max(metrics.items(), key=lambda x: x[1]['survival_rate'])
        best_learning = max(metrics.items(), key=lambda x: x[1]['learning_score'])
        best_adaptation = max(metrics.items(), key=lambda x: x[1]['adaptation_score'])
        
        print(f"• 最高生存率: {self.user_types[best_survival[0]]} ({best_survival[1]['survival_rate']:.1f}%)")
        print(f"• 最强学习能力: {self.user_types[best_learning[0]]} (学习评分: {best_learning[1]['learning_score']:.1f})")
        print(f"• 最强适应能力: {self.user_types[best_adaptation[0]]} (适应评分: {best_adaptation[1]['adaptation_score']:.1f})")
        
        # 性能对比分析
        ilai_score = metrics['ILAI']['overall_score']
        dqn_score = metrics['DQN']['overall_score']
        ppo_score = metrics['PPO']['overall_score']
        
        print(f"\n• ILAI相比DQN性能提升: {((ilai_score - dqn_score) / dqn_score * 100):.1f}%")
        print(f"• ILAI相比PPO性能提升: {((ilai_score - ppo_score) / ppo_score * 100):.1f}%")
        
        print("\n\n4. 结论与建议")
        print("-" * 50)
        print("• 婴儿学习AI (ILAI) 在生存能力、学习能力和适应能力方面均表现优异")
        print("• 强化婴儿学习AI (RILAI) 结合了婴儿学习和强化学习的优势")
        print("• 传统强化学习方法在复杂环境中表现相对较弱")
        print("• 符号化推理和分层认知架构是提升AI性能的关键因素")
        
        print("=" * 80)

def main():
    """主函数"""
    analyzer = AIDecisionAnalyzer()
    
    # 生成综合分析报告
    analyzer.generate_comprehensive_report()
    
    # 生成可视化图表
    print("\n正在生成可视化图表...")
    analyzer.plot_survival_comparison()
    analyzer.plot_learning_curves() 
    analyzer.plot_decision_mechanisms()
    
    print("\n分析完成！已生成以下文件：")
    print("- ai_survival_comparison.png: 生存能力比较图")
    print("- ai_learning_analysis.png: 学习能力分析图")
    print("- ai_decision_mechanisms.png: 决策机制对比图")

if __name__ == "__main__":
    main() 