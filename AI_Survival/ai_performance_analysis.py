#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI生存游戏性能分析脚本
基于游戏日志数据对四种AI类型进行多维度评价分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class AIPerformanceAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.raw_data = []
        self.processed_data = {}
        self.ai_types = ['ILAI', 'RILAI', 'DQN', 'PPO']
        
    def extract_ranking_data(self):
        """从日志中提取排名表数据"""
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取排名表
        ranking_pattern = r'\|(\d+)\|([^|]+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|([\d.]+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|'
        matches = re.findall(ranking_pattern, content)
        
        for match in matches:
            rank, player, survival_days, reputation, hp, food, water, exploration_rate, \
            found_plants, collected_plants, encountered_animals, killed_animals, \
            found_trees, explored_caves, shared_info = match
            
            ai_type = 'UNKNOWN'
            for ai in self.ai_types:
                if player.strip().startswith(ai):
                    ai_type = ai
                    break
            
            self.raw_data.append({
                'rank': int(rank),
                'player': player.strip(),
                'ai_type': ai_type,
                'survival_days': int(survival_days),
                'reputation': int(reputation),
                'hp': int(hp),
                'food': int(food),
                'water': int(water),
                'exploration_rate': float(exploration_rate),
                'found_plants': int(found_plants),
                'collected_plants': int(collected_plants),
                'encountered_animals': int(encountered_animals),
                'killed_animals': int(killed_animals),
                'found_trees': int(found_trees),
                'explored_caves': int(explored_caves),
                'shared_info': int(shared_info)
            })
    
    def analyze_performance_metrics(self):
        """分析九个维度的性能指标"""
        df = pd.DataFrame(self.raw_data)
        
        metrics = {}
        
        for ai_type in self.ai_types:
            ai_data = df[df['ai_type'] == ai_type]
            if len(ai_data) == 0:
                continue
            
            # 1. 认知和决策机制 
            decision_quality = ai_data['reputation'].mean() / 220  # 最高声誉220
            
            # 2. 生存能力 
            survival_rate = (ai_data['survival_days'] > 15).sum() / len(ai_data)
            avg_survival_days = ai_data['survival_days'].mean() / 30  # 最长30天
            survival_capability = (survival_rate + avg_survival_days) / 2
            
            # 3. 学习能力
            knowledge_gain = ai_data['shared_info'].mean() / 520  # 最高520
            
            # 4. 适应能力
            resource_management = (ai_data['food'].mean() + ai_data['water'].mean()) / 200
            
            # 5. 鲁棒性
            death_resistance = ai_data['hp'].mean() / 100
            
            # 6. 探索能力
            exploration_score = ai_data['exploration_rate'].mean() / 0.005  # 最高约0.005
            
            # 7. 社交能力
            social_score = ai_data['shared_info'].mean() / 520
            
            # 8. 数据依赖性 (反向指标)
            if ai_type in ['ILAI', 'RILAI']:
                data_dependency = 0.3  # 低依赖
            else:
                data_dependency = 0.8  # 高依赖
            
            # 9. 可解释性
            if ai_type in ['ILAI', 'RILAI']:
                interpretability = 0.9  # 高可解释性
            else:
                interpretability = 0.2  # 低可解释性
            
            metrics[ai_type] = {
                'cognitive_decision': min(decision_quality, 1.0),
                'survival_capability': min(survival_capability, 1.0),
                'learning_ability': min(knowledge_gain, 1.0),
                'adaptability': min(resource_management, 1.0),
                'robustness': min(death_resistance, 1.0),
                'exploration_capability': min(exploration_score, 1.0),
                'social_capability': min(social_score, 1.0),
                'data_dependency': data_dependency,
                'interpretability': interpretability
            }
        
        self.processed_data = metrics
        return metrics
    
    def generate_performance_matrix(self):
        """生成性能数据矩阵"""
        dimensions = [
            'cognitive_decision', 'survival_capability', 'learning_ability',
            'adaptability', 'robustness', 'exploration_capability',
            'social_capability', 'data_dependency', 'interpretability'
        ]
        
        dimension_names = [
            '认知和决策机制', '生存能力', '学习能力', '适应能力', '鲁棒性',
            '探索能力', '社交能力', '数据依赖性', '可解释性'
        ]
        
        matrix_data = []
        for ai_type in self.ai_types:
            if ai_type in self.processed_data:
                row = [self.processed_data[ai_type][dim] for dim in dimensions]
                matrix_data.append(row)
            else:
                matrix_data.append([0] * len(dimensions))
        
        df_matrix = pd.DataFrame(matrix_data, 
                                index=self.ai_types, 
                                columns=dimension_names)
        return df_matrix
    
    def create_radar_chart(self, save_path='ai_performance_radar.png'):
        """创建雷达图"""
        matrix = self.generate_performance_matrix()
        
        # 设置雷达图参数
        angles = np.linspace(0, 2 * np.pi, len(matrix.columns), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))
        
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, ai_type in enumerate(self.ai_types):
            if ai_type in self.processed_data:
                values = matrix.loc[ai_type].values.flatten().tolist()
                values += values[:1]  # 闭合图形
                
                ax.plot(angles, values, 'o-', linewidth=2, label=ai_type, color=colors[i])
                ax.fill(angles, values, alpha=0.25, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(matrix.columns, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
        ax.grid(True)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.title('四种AI类型性能雷达图对比', size=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_heatmap(self, save_path='ai_performance_heatmap.png'):
        """创建热力图"""
        matrix = self.generate_performance_matrix()
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(matrix, annot=True, cmap='RdYlGn', center=0.5, 
                    fmt='.3f', cbar_kws={'label': '性能得分'})
        plt.title('四种AI类型性能热力图', size=16, fontweight='bold')
        plt.ylabel('AI类型', fontsize=12)
        plt.xlabel('性能维度', fontsize=12)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def run_complete_analysis(self):
        """运行完整的分析流程"""
        print("开始分析AI性能数据...")
        
        # 1. 提取数据
        self.extract_ranking_data()
        print(f"已提取 {len(self.raw_data)} 条AI性能记录")
        
        # 2. 分析指标
        metrics = self.analyze_performance_metrics()
        print("性能指标分析完成")
        
        # 3. 生成可视化图表
        radar_path = self.create_radar_chart()
        print(f"雷达图已生成: {radar_path}")
        
        heatmap_path = self.create_heatmap()
        print(f"热力图已生成: {heatmap_path}")
        
        return {
            'metrics': metrics,
            'charts': [radar_path, heatmap_path]
        }

if __name__ == "__main__":
    # 运行分析
    analyzer = AIPerformanceAnalyzer('game_20250620_200945.log')
    results = analyzer.run_complete_analysis()
    
    print("\n=== 分析完成 ===")
    print("生成的文件:")
    for chart in results['charts']:
        print(f"- {chart}") 