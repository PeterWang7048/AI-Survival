#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量测试RILAI与ILAI的性能对比脚本
每种AI在标准模式和困难模式下各测试5次，使用不同随机种子
计算平均结果并生成报告
"""

import subprocess
import pandas as pd
import numpy as np
import os
import random
import re
import matplotlib.pyplot as plt
import matplotlib
import time
import json
from datetime import datetime

# 修复中文显示问题
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 实验配置
AI_TYPES = ["RILAI", "ILAI"]
MODES = [
    {"name": "标准模式", "predator": 50, "resource": 70},
    {"name": "困难模式", "predator": 100, "resource": 70}
]
TESTS_PER_MODE = 5
GAME_DURATION = 30

# 随机种子列表 - 为每种配置生成不同的随机种子
random.seed(42)  # 确保可重复性
SEEDS = [random.randint(1000, 9999) for _ in range(TESTS_PER_MODE * len(MODES) * len(AI_TYPES))]

# 存储结果的目录
RESULTS_DIR = "ai_comparison_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# 结果数据结构
results = {
    ai_type: {
        mode["name"]: [] for mode in MODES
    } for ai_type in AI_TYPES
}

def run_test(ai_type, mode, seed, test_index):
    """运行单次测试并返回结果"""
    print(f"\n正在测试 {ai_type} - {mode['name']} - 种子:{seed} (第{test_index+1}次/共{TESTS_PER_MODE}次)")
    
    # 构建命令
    cmd = [
        "python", "auto_run_rilai_gui.py",
        f"--ai-type={ai_type}",
        f"--predator={mode['predator']}",
        f"--duration={GAME_DURATION}",
        f"--resource={mode['resource']}",
        f"--seed={seed}"
    ]
    
    # 运行命令
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    # 解析结果
    test_result = parse_test_results(output, ai_type)
    test_result["seed"] = seed
    
    return test_result

def parse_test_results(output, ai_type):
    """从命令输出中解析测试结果"""
    result = {
        "生存率": 0,
        "平均生存天数": 0,
        "最佳排名": 30,
        "前十数量": 0,
        "平均血量": 0,
        "平均食物": 0,
        "平均水": 0,
        "log_file": "",
        "ai_players": []
    }
    
    # 提取日志文件名
    log_match = re.search(r"测试完成，日志已保存到: (game_\d+\.log)", output)
    if log_match:
        result["log_file"] = log_match.group(1)
    
    # 修复RILAI玩家识别的正则表达式
    player_name_pattern = r"RL\d+" if ai_type == "RILAI" else f"{ai_type}\d+"
    ai_player_pattern = re.compile(rf"\|(\d+)\|{player_name_pattern}\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|")
    ai_players = []
    
    # 提取排名数据
    rank_pattern = re.compile(r"\|(\d+)\|" + (r"RL\d+" if ai_type == "RILAI" else ai_type + r"\d+") + r"\|")
    ranks = [int(match.group(1)) for match in rank_pattern.finditer(output)]
    
    for match in ai_player_pattern.finditer(output):
        player = {
            "排名": int(match.group(1)),
            "生存天数": int(match.group(2)),
            "声誉": int(match.group(3)),
            "血量": int(match.group(4)),
            "食物": int(match.group(5)),
            "水": int(match.group(6)),
            "探索率": int(match.group(7)),
            "发现植物": int(match.group(8)),
            "采集植物": int(match.group(9)),
            "遭遇动物": int(match.group(10)),
            "击杀动物": int(match.group(11)),
            "发现大树": int(match.group(12)),
            "探索山洞": int(match.group(13)),
            "分享信息": int(match.group(14))
        }
        ai_players.append(player)
    
    # 计算统计数据
    if ai_players:
        # 生存率 - 存活到最后一天的比例
        survived_players = [p for p in ai_players if p["生存天数"] == GAME_DURATION]
        result["生存率"] = len(survived_players) / len(ai_players) * 100
        
        # 平均生存天数
        result["平均生存天数"] = sum(p["生存天数"] for p in ai_players) / len(ai_players)
        
        # 最佳排名
        result["最佳排名"] = min(ranks) if ranks else 30
        
        # 前十数量
        result["前十数量"] = sum(1 for r in ranks if r <= 10)
        
        # 平均资源
        result["平均血量"] = sum(p["血量"] for p in ai_players) / len(ai_players)
        result["平均食物"] = sum(p["食物"] for p in ai_players) / len(ai_players)
        result["平均水"] = sum(p["水"] for p in ai_players) / len(ai_players)
        
        # 存储AI玩家数据
        result["ai_players"] = ai_players
    
    return result

def calculate_averages():
    """计算平均结果"""
    averages = {
        ai_type: {
            mode["name"]: {
                "生存率": 0,
                "平均生存天数": 0,
                "最佳排名": 0,
                "前十数量": 0,
                "平均血量": 0,
                "平均食物": 0,
                "平均水": 0
            } for mode in MODES
        } for ai_type in AI_TYPES
    }
    
    for ai_type in AI_TYPES:
        for mode in MODES:
            mode_results = results[ai_type][mode["name"]]
            mode_avg = averages[ai_type][mode["name"]]
            
            if mode_results:
                mode_avg["生存率"] = np.mean([r["生存率"] for r in mode_results])
                mode_avg["平均生存天数"] = np.mean([r["平均生存天数"] for r in mode_results])
                mode_avg["最佳排名"] = np.mean([r["最佳排名"] for r in mode_results])
                mode_avg["前十数量"] = np.mean([r["前十数量"] for r in mode_results])
                mode_avg["平均血量"] = np.mean([r["平均血量"] for r in mode_results])
                mode_avg["平均食物"] = np.mean([r["平均食物"] for r in mode_results])
                mode_avg["平均水"] = np.mean([r["平均水"] for r in mode_results])
    
    return averages

def generate_comparison_chart(averages):
    """生成对比图表"""
    plt.figure(figsize=(16, 12))
    plt.style.use('ggplot')
    
    # 设置颜色
    colors = {'RILAI': '#5DA5DA', 'ILAI': '#F15854'}
    
    # 数据准备
    metrics = ["生存率", "平均生存天数", "最佳排名", "前十数量"]
    bar_width = 0.35
    
    for i, metric in enumerate(metrics):
        ax = plt.subplot(2, 2, i+1)
        
        # 确定x轴位置
        x = np.arange(len(MODES))
        
        # 绘制柱状图
        for j, ai_type in enumerate(AI_TYPES):
            values = [averages[ai_type][mode["name"]][metric] for mode in MODES]
            bars = ax.bar(x + (j-0.5) * bar_width, values, bar_width, label=ai_type, color=colors[ai_type])
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                if metric == "生存率":
                    ax.text(bar.get_x() + bar.get_width()/2., height + 3, f'{height:.1f}%', ha='center', va='bottom')
                elif metric == "平均生存天数":
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}天', ha='center', va='bottom')
                else:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3, f'{height:.1f}', ha='center', va='bottom')
        
        # 设置图表属性
        ax.set_title(f'{metric}对比')
        ax.set_xticks(x)
        ax.set_xticklabels([mode["name"] for mode in MODES])
        
        if metric == "生存率":
            ax.set_ylim(0, 110)
            ax.set_ylabel('生存率 (%)')
        elif metric == "平均生存天数":
            ax.set_ylim(0, 35)
            ax.set_ylabel('平均生存天数 (天)')
        elif metric == "最佳排名":
            ax.set_ylim(0, 30)
            ax.set_ylabel('平均最佳排名')
            # 反转Y轴，使排名越小的位置越高
            ax.invert_yaxis()
        else:
            ax.set_ylim(0, 10)
            ax.set_ylabel('平均进入前十数量')
        
        ax.legend()
    
    plt.suptitle('RILAI vs ILAI 多次测试平均性能对比', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_path = os.path.join(RESULTS_DIR, f'AI比较_{timestamp}.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    
    return chart_path

def generate_report(averages, chart_path):
    """生成实验报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(RESULTS_DIR, f'AI比较实验报告_{timestamp}.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# RILAI与ILAI多次测试性能对比报告\n\n")
        
        f.write("## 实验设置\n\n")
        f.write(f"- 每种AI在每种模式下测试{TESTS_PER_MODE}次\n")
        f.write(f"- 游戏持续时间: {GAME_DURATION}天\n")
        f.write("- 使用不同随机种子进行测试\n")
        f.write("- 标准模式: 猛兽数量=50, 资源丰富度=70\n")
        f.write("- 困难模式: 猛兽数量=100, 资源丰富度=70\n\n")
        
        f.write("## 平均结果数据\n\n")
        
        # 创建数据表格
        f.write("### 标准模式(50猛兽)结果\n\n")
        f.write("| 指标 | RILAI | ILAI | 优势AI |\n")
        f.write("|------|-------|------|--------|\n")
        
        mode_name = MODES[0]["name"]
        for metric in ["生存率", "平均生存天数", "最佳排名", "前十数量", "平均血量", "平均食物", "平均水"]:
            rilai_value = averages["RILAI"][mode_name][metric]
            ilai_value = averages["ILAI"][mode_name][metric]
            
            # 确定哪个AI更好
            # 对于排名，数值越小越好
            if metric == "最佳排名":
                better_ai = "RILAI" if rilai_value < ilai_value else "ILAI"
            else:
                better_ai = "RILAI" if rilai_value > ilai_value else "ILAI"
            
            # 格式化值
            if metric == "生存率":
                rilai_str = f"{rilai_value:.1f}%"
                ilai_str = f"{ilai_value:.1f}%"
            elif metric == "平均生存天数":
                rilai_str = f"{rilai_value:.1f}天"
                ilai_str = f"{ilai_value:.1f}天"
            else:
                rilai_str = f"{rilai_value:.1f}"
                ilai_str = f"{ilai_value:.1f}"
            
            f.write(f"| {metric} | {rilai_str} | {ilai_str} | {better_ai} |\n")
        
        f.write("\n### 困难模式(100猛兽)结果\n\n")
        f.write("| 指标 | RILAI | ILAI | 优势AI |\n")
        f.write("|------|-------|------|--------|\n")
        
        mode_name = MODES[1]["name"]
        for metric in ["生存率", "平均生存天数", "最佳排名", "前十数量", "平均血量", "平均食物", "平均水"]:
            rilai_value = averages["RILAI"][mode_name][metric]
            ilai_value = averages["ILAI"][mode_name][metric]
            
            # 确定哪个AI更好
            if metric == "最佳排名":
                better_ai = "RILAI" if rilai_value < ilai_value else "ILAI"
            else:
                better_ai = "RILAI" if rilai_value > ilai_value else "ILAI"
            
            # 格式化值
            if metric == "生存率":
                rilai_str = f"{rilai_value:.1f}%"
                ilai_str = f"{ilai_value:.1f}%"
            elif metric == "平均生存天数":
                rilai_str = f"{rilai_value:.1f}天"
                ilai_str = f"{ilai_value:.1f}天"
            else:
                rilai_str = f"{rilai_value:.1f}"
                ilai_str = f"{ilai_value:.1f}"
            
            f.write(f"| {metric} | {rilai_str} | {ilai_str} | {better_ai} |\n")
        
        # 添加图表
        f.write(f"\n## 性能对比图表\n\n")
        f.write(f"![RILAI vs ILAI 性能对比]({os.path.basename(chart_path)})\n\n")
        
        # 分析综述
        f.write("## 分析综述\n\n")
        
        # 生存能力对比
        f.write("### 生存能力对比\n\n")
        std_survival_rilai = averages["RILAI"][MODES[0]["name"]]["生存率"]
        std_survival_ilai = averages["ILAI"][MODES[0]["name"]]["生存率"]
        hard_survival_rilai = averages["RILAI"][MODES[1]["name"]]["生存率"]
        hard_survival_ilai = averages["ILAI"][MODES[1]["name"]]["生存率"]
        
        f.write(f"* **RILAI**：在生存能力方面表现{('出色' if std_survival_rilai > std_survival_ilai else '一般')}，")
        f.write(f"标准模式下生存率{std_survival_rilai:.1f}%，困难模式下生存率{hard_survival_rilai:.1f}%。")
        f.write("生存策略偏向稳健保守，有效避免了致命危险。\n\n")
        
        f.write(f"* **ILAI**：生存能力{('较弱' if std_survival_ilai < std_survival_rilai else '较强')}，")
        f.write(f"标准模式下生存率{std_survival_ilai:.1f}%，困难模式下生存率{hard_survival_ilai:.1f}%。\n\n")
        
        # 竞争力对比
        f.write("### 竞争力对比\n\n")
        std_rank_rilai = averages["RILAI"][MODES[0]["name"]]["最佳排名"]
        std_rank_ilai = averages["ILAI"][MODES[0]["name"]]["最佳排名"]
        hard_rank_rilai = averages["RILAI"][MODES[1]["name"]]["最佳排名"]
        hard_rank_ilai = averages["ILAI"][MODES[1]["name"]]["最佳排名"]
        
        std_top10_rilai = averages["RILAI"][MODES[0]["name"]]["前十数量"]
        std_top10_ilai = averages["ILAI"][MODES[0]["name"]]["前十数量"]
        hard_top10_rilai = averages["RILAI"][MODES[1]["name"]]["前十数量"]
        hard_top10_ilai = averages["ILAI"][MODES[1]["name"]]["前十数量"]
        
        f.write(f"* **RILAI**：在竞争力方面表现{('较强' if std_rank_rilai < std_rank_ilai else '较弱')}，")
        f.write(f"标准模式下平均最佳排名{std_rank_rilai:.1f}，困难模式下平均最佳排名{hard_rank_rilai:.1f}。")
        f.write(f"标准模式下平均有{std_top10_rilai:.1f}个进入前十，困难模式下平均有{hard_top10_rilai:.1f}个进入前十。\n\n")
        
        f.write(f"* **ILAI**：竞争力表现{('较强' if std_rank_ilai < std_rank_rilai else '较弱')}，")
        f.write(f"标准模式下平均最佳排名{std_rank_ilai:.1f}，困难模式下平均最佳排名{hard_rank_ilai:.1f}。")
        f.write(f"标准模式下平均有{std_top10_ilai:.1f}个进入前十，困难模式下平均有{hard_top10_ilai:.1f}个进入前十。\n\n")
        
        # 环境适应性对比
        f.write("### 环境适应性对比\n\n")
        rilai_survival_drop = std_survival_rilai - hard_survival_rilai
        ilai_survival_drop = std_survival_ilai - hard_survival_ilai
        
        f.write(f"* **RILAI**：从标准模式到困难模式，生存率下降{rilai_survival_drop:.1f}%点，")
        f.write(f"表明其对环境变化有{'较强' if rilai_survival_drop < ilai_survival_drop else '一般'}的适应性。\n\n")
        
        f.write(f"* **ILAI**：从标准模式到困难模式，生存率下降{ilai_survival_drop:.1f}%点，")
        f.write(f"表明其对环境变化的适应性{'较强' if ilai_survival_drop < rilai_survival_drop else '一般'}。\n\n")
        
        # 资源管理对比
        f.write("### 资源管理对比\n\n")
        std_food_rilai = averages["RILAI"][MODES[0]["name"]]["平均食物"]
        std_food_ilai = averages["ILAI"][MODES[0]["name"]]["平均食物"]
        hard_food_rilai = averages["RILAI"][MODES[1]["name"]]["平均食物"]
        hard_food_ilai = averages["ILAI"][MODES[1]["name"]]["平均食物"]
        
        std_water_rilai = averages["RILAI"][MODES[0]["name"]]["平均水"]
        std_water_ilai = averages["ILAI"][MODES[0]["name"]]["平均水"]
        hard_water_rilai = averages["RILAI"][MODES[1]["name"]]["平均水"]
        hard_water_ilai = averages["ILAI"][MODES[1]["name"]]["平均水"]
        
        f.write(f"* **RILAI**：资源管理表现{('较好' if std_food_rilai > std_food_ilai or std_water_rilai > std_water_rilai else '一般')}，")
        f.write(f"标准模式下平均食物{std_food_rilai:.1f}、水{std_water_rilai:.1f}，")
        f.write(f"困难模式下平均食物{hard_food_rilai:.1f}、水{hard_water_rilai:.1f}。\n\n")
        
        f.write(f"* **ILAI**：资源管理表现{('较好' if std_food_ilai > std_food_rilai or std_water_ilai > std_water_rilai else '一般')}，")
        f.write(f"标准模式下平均食物{std_food_ilai:.1f}、水{std_water_ilai:.1f}，")
        f.write(f"困难模式下平均食物{hard_food_ilai:.1f}、水{hard_water_ilai:.1f}。\n\n")
        
        # 结论
        f.write("## 结论\n\n")
        
        # 综合评估哪个AI更好
        rilai_points = 0
        ilai_points = 0
        
        # 计算总分
        for mode in MODES:
            mode_name = mode["name"]
            for metric in ["生存率", "平均生存天数", "平均血量", "平均食物", "平均水"]:
                if averages["RILAI"][mode_name][metric] > averages["ILAI"][mode_name][metric]:
                    rilai_points += 1
                else:
                    ilai_points += 1
            
            # 对于排名，数值越小越好
            if averages["RILAI"][mode_name]["最佳排名"] < averages["ILAI"][mode_name]["最佳排名"]:
                rilai_points += 1
            else:
                ilai_points += 1
                
            if averages["RILAI"][mode_name]["前十数量"] > averages["ILAI"][mode_name]["前十数量"]:
                rilai_points += 1
            else:
                ilai_points += 1
        
        # 生成结论
        if rilai_points > ilai_points:
            winner = "RILAI"
            loser = "ILAI"
        else:
            winner = "ILAI"
            loser = "RILAI"
        
        f.write(f"多次实验结果表明，在我们测试的环境条件下，**{winner}** 总体表现优于 **{loser}**。\n\n")
        
        if winner == "RILAI":
            f.write("RILAI主要优势在于较高的生存率和稳定性，适合在危险环境中长期生存。")
            f.write("但在竞争性指标如排名和资源积累方面可能略显不足。\n\n")
        else:
            f.write("ILAI主要优势在于竞争性环境中的表现，能够取得较好的排名，")
            f.write("但其生存能力可能不如RILAI稳定，在高危环境中死亡率较高。\n\n")
        
        f.write("理想的AI应该结合两者优势：保持高生存率的同时在竞争中取得优势地位。")
        f.write("未来改进方向应集中在寻找生存与竞争之间的最佳平衡点，")
        f.write("创造一种在各种环境条件下都能表现出色的通用型AI。\n")
    
    # 也保存原始数据为JSON
    data_path = os.path.join(RESULTS_DIR, f'AI比较原始数据_{timestamp}.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        # 转换为可序列化的格式
        serializable_results = {}
        for ai_type in results:
            serializable_results[ai_type] = {}
            for mode_name in results[ai_type]:
                serializable_results[ai_type][mode_name] = []
                for res in results[ai_type][mode_name]:
                    res_copy = res.copy()
                    res_copy["ai_players"] = [dict(p) for p in res_copy["ai_players"]]
                    serializable_results[ai_type][mode_name].append(res_copy)
        
        json.dump({
            "results": serializable_results,
            "averages": averages,
            "config": {
                "AI_TYPES": AI_TYPES,
                "MODES": MODES,
                "TESTS_PER_MODE": TESTS_PER_MODE,
                "GAME_DURATION": GAME_DURATION,
                "SEEDS": SEEDS
            }
        }, f, ensure_ascii=False, indent=2)
    
    return report_path

def main():
    """主函数"""
    print(f"开始比较RILAI与ILAI (每种模式{TESTS_PER_MODE}次测试)")
    
    # 运行测试
    seed_index = 0
    for ai_type in AI_TYPES:
        for mode in MODES:
            for test_index in range(TESTS_PER_MODE):
                seed = SEEDS[seed_index]
                seed_index += 1
                
                test_result = run_test(ai_type, mode, seed, test_index)
                results[ai_type][mode["name"]].append(test_result)
                
                # 打印简略结果
                print(f"  结果: 生存率={test_result['生存率']:.1f}%, " +
                      f"平均天数={test_result['平均生存天数']:.1f}, " +
                      f"最佳排名={test_result['最佳排名']}, " +
                      f"前十数量={test_result['前十数量']}")
                
                # 简单暂停，避免并发问题
                time.sleep(1)
    
    # 计算平均结果
    print("\n计算平均结果...")
    averages = calculate_averages()
    
    # 生成图表
    print("生成对比图表...")
    chart_path = generate_comparison_chart(averages)
    
    # 生成报告
    print("生成实验报告...")
    report_path = generate_report(averages, chart_path)
    
    print(f"\n实验完成！报告已保存至: {report_path}")
    print(f"图表已保存至: {chart_path}")

if __name__ == "__main__":
    main() 