#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taxi论文级实验 - 可配置版本 + 动态随机种子
支持手工输入实验次数：快速测试1次，论文实验20次等
配置：50回合 × N次运行
✨ 新增：动态随机种子功能，确保每次运行使用不同的随机种子
"""

import os
import time
import random
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

# 导入原始实验框架
from taxi_baseline_framework import *

class UnifiedTaxiLogger:
    """统一Taxi日志系统 - 多文件日志版本"""
    
    def __init__(self):
        self.log_dir = Path("000log")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = None
        self.main_log_file = None
        self.start_time = None
        
    def create_main_log_file(self, experiment_name: str):
        """创建主汇总日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        main_log_filename = self.log_dir / f"taxi-summary-{timestamp}.log"
        
        self.main_log_file = open(main_log_filename, 'w', encoding='utf-8')
        self.start_time = datetime.now()
        
        # 写入主日志头信息
        self._log_to_file(self.main_log_file, "🚕 Taxi可配置论文级实验汇总日志")
        self._log_to_file(self.main_log_file, f"实验名称: {experiment_name}")
        self._log_to_file(self.main_log_file, f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._log_to_file(self.main_log_file, "🎯 基于原始comprehensive_baseline_experiment.py")
        self._log_to_file(self.main_log_file, "📊 配置: 6个基线智能体完整对比")
        self._log_to_file(self.main_log_file, "🔧 外围统一日志系统 (不修改核心机制)")
        self._log_to_file(self.main_log_file, "✨ 新增: 动态随机种子功能")
        self._log_to_file(self.main_log_file, "=" * 80)
        
        return str(main_log_filename)
        
    def create_run_log_file(self, experiment_name: str, run_number: int):
        """为单次运行创建独立日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_filename = self.log_dir / f"taxi-run{run_number:02d}-{timestamp}.log"
        
        # 如果已有文件打开，先关闭
        if self.log_file:
            self.close_current_run_log()
            
        self.log_file = open(log_filename, 'w', encoding='utf-8')
        
        # 写入头信息
        self._log_to_file(self.log_file, "🚕 Taxi可配置论文级实验详细日志")
        self._log_to_file(self.log_file, f"实验名称: {experiment_name}")
        self._log_to_file(self.log_file, f"运行编号: 第{run_number}次运行")
        self._log_to_file(self.log_file, f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log_to_file(self.log_file, "🎯 基于原始comprehensive_baseline_experiment.py")
        self._log_to_file(self.log_file, "📊 配置: 6个基线智能体完整对比")
        self._log_to_file(self.log_file, "🔧 外围统一日志系统 (不修改核心机制)")
        self._log_to_file(self.log_file, "✨ 新增: 动态随机种子功能")
        self._log_to_file(self.log_file, "=" * 80)
        
        return str(log_filename)
    
    def _log_to_file(self, file, message: str):
        """记录日志到指定文件"""
        if file:
            file.write(f"{message}\n")
            file.flush()
    
    def log(self, message: str):
        """记录日志到当前运行日志和控制台"""
        print(message, flush=True)
        if self.log_file:
            self._log_to_file(self.log_file, message)
            
    def log_to_main(self, message: str):
        """记录日志到主汇总日志和控制台"""
        print(message, flush=True)
        if self.main_log_file:
            self._log_to_file(self.main_log_file, message)
    
    def log_to_both(self, message: str):
        """记录日志到运行日志、主日志和控制台"""
        print(message, flush=True)
        if self.log_file:
            self._log_to_file(self.log_file, message)
        if self.main_log_file:
            self._log_to_file(self.main_log_file, message)
            
    def close_current_run_log(self):
        """关闭当前运行的日志文件"""
        if self.log_file:
            self._log_to_file(self.log_file, "\n" + "="*80)
            self._log_to_file(self.log_file, f"📊 **详细日志文件**: {self.log_file.name}")
            self._log_to_file(self.log_file, "🎉 **单次运行实验数据就绪！**")
            self._log_to_file(self.log_file, f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._log_to_file(self.log_file, "=" * 80)
            self._log_to_file(self.log_file, "🎉 **单次运行日志记录完成！**")
            self.log_file.close()
            self.log_file = None
            
    def close_main_log_file(self):
        """关闭主汇总日志文件"""
        if self.main_log_file:
            end_time = datetime.now()
            total_time = (end_time - self.start_time).total_seconds()
            self._log_to_file(self.main_log_file, f"\n⏱️ 实验完成，总用时: {total_time:.1f}秒")
            self._log_to_file(self.main_log_file, f"📊 **汇总日志文件**: {self.main_log_file.name}")
            self._log_to_file(self.main_log_file, "🎉 **可配置论文实验汇总数据就绪！**")
            self._log_to_file(self.main_log_file, f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self._log_to_file(self.main_log_file, "=" * 80)
            self._log_to_file(self.main_log_file, "🎉 **可配置论文级实验汇总日志记录完成！**")
            self.main_log_file.close()
            self.main_log_file = None

class TaxiExperimentProgressBar:
    """Taxi实验详细进度条 - 增强版"""
    
    def __init__(self):
        self.current_agent = ""
        self.agents_completed = 0
        self.total_agents = 6
        self.current_run = 0
        self.total_runs = 1
        
    def show_experiment_start(self, num_runs: int):
        """显示实验开始信息"""
        self.total_runs = num_runs
        print(f"🚀 **开始Taxi实验**: 50回合 × {num_runs}次运行")
        print(f"📊 **总计**: {6 * num_runs} 个智能体实验")
        print(f"⏱️ **预计用时**: ~{num_runs * 8:.0f} 分钟")
        print("=" * 60, flush=True)
        
    def show_run_progress(self, run_number: int, total_runs: int):
        """显示运行进度"""
        self.current_run = run_number
        progress_percent = (run_number / total_runs) * 100
        filled_length = int(40 * run_number // total_runs)
        bar = '█' * filled_length + '░' * (40 - filled_length)
        
        print(f"\n📊 **运行进度**: [{bar}] {progress_percent:.1f}% (第{run_number}/{total_runs}次运行)")
        print("-" * 60, flush=True)
        
    def show_agent_start(self, agent_name: str):
        """显示智能体开始训练"""
        # 智能体进度图标
        icons = {
            "ILAI System": "🧠",
            "A* Search Agent": "🎯", 
            "Rule-Based Agent": "⚙️",
            "Deep Q Network": "🤖",
            "Q-Learning Agent": "📈",
            "Random Agent": "🎲"
        }
        icon = icons.get(agent_name, "🔄")
        
        print(f"\n{icon} **{agent_name}** - 开始50回合训练...")
        print("  ", end="", flush=True)  # 为进度条预留空间
        
    def show_episode_progress(self, episode: int, total_episodes: int):
        """显示回合级进度条"""
        if episode % max(1, total_episodes // 20) == 0 or episode == total_episodes:  # 每5%显示一次
            progress_percent = (episode / total_episodes) * 100
            filled_length = int(25 * episode // total_episodes)
            bar = '█' * filled_length + '░' * (25 - filled_length)
            
            print(f"\r  📈 训练进度: [{bar}] {progress_percent:.0f}% ({episode}/{total_episodes}回合)", end="", flush=True)
            
            if episode == total_episodes:
                print()  # 完成后换行
    
    def show_agent_complete(self, agent_name: str, success_rate: float):
        """显示智能体完成"""
        self.agents_completed += 1
        
        # 成功率图标
        if success_rate >= 50:
            rate_icon = "🌟"
        elif success_rate >= 30:
            rate_icon = "✅"
        elif success_rate >= 10:
            rate_icon = "⚠️"
        else:
            rate_icon = "❌"
        
        overall_progress = (self.agents_completed / (self.total_agents * self.total_runs)) * 100
        print(f"  {rate_icon} **完成！** 成功率: {success_rate:.1f}% | 总进度: {overall_progress:.1f}%")
        print("-" * 50, flush=True)

class ConfigurableTaxiPaperExperiment:
    """可配置的Taxi论文级实验执行器 + 动态随机种子"""
    
    def __init__(self, num_runs: int = 1):
        self.logger = UnifiedTaxiLogger()
        self.progress_bar = TaxiExperimentProgressBar()
        self.original_experiment = None
        self.num_runs = num_runs
        self.seed_history = []  # 记录使用过的随机种子
        
    def generate_dynamic_seed(self, run_index: int) -> int:
        """生成动态随机种子"""
        # 🎲 多重随机化策略
        base_seed = 42
        time_component = int(time.time() * 1000) % 10000  # 基于当前时间
        run_component = run_index * 1000                  # 基于运行编号
        random_component = random.randint(1, 999)         # 额外随机数
        
        dynamic_seed = base_seed + run_component + time_component + random_component
        
        # 避免种子重复
        while dynamic_seed in self.seed_history:
            random_component = random.randint(1, 999)
            dynamic_seed = base_seed + run_component + time_component + random_component
        
        self.seed_history.append(dynamic_seed)
        return dynamic_seed
    
    def run_configurable_comparison_with_logging(self, experiment_name: str):
        """运行可配置的完整对比实验 + 多文件日志 + 动态随机种子"""
        
        # 创建主汇总日志文件
        main_log_file = self.logger.create_main_log_file(experiment_name)
        
        try:
            self.logger.log_to_main(f"🚕 **Taxi可配置完整基线对比实验**")
            self.logger.log_to_main(f"📊 实验配置: 50回合 × {self.num_runs}次运行")
            self.logger.log_to_main(f"🎯 包含6个基线智能体")
            self.logger.log_to_main(f"✨ 动态随机种子: 每次运行使用不同种子")
            self.logger.log_to_main(f"📁 主日志文件: {main_log_file}")
            self.logger.log_to_main("")
            
            # 显示实验开始信息
            self.progress_bar.show_experiment_start(self.num_runs)
            
            # 记录生成的日志文件信息
            generated_log_files = [main_log_file]
            
            # 累计所有运行的结果
            all_run_results = []
            
            experiment_start_time = time.time()
            
            # 执行多次运行
            for run_idx in range(self.num_runs):
                # 🎲 生成动态随机种子
                dynamic_seed = self.generate_dynamic_seed(run_idx)
                
                self.logger.log_to_main(f"\n🔄 **开始第 {run_idx + 1}/{self.num_runs} 次实验运行**")
                self.logger.log_to_main(f"🎲 动态随机种子: {dynamic_seed}")
                self.logger.log_to_main(f"运行开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 显示运行进度
                self.progress_bar.show_run_progress(run_idx + 1, self.num_runs)
                
                # 为这次运行创建独立日志文件
                run_log_file = self.logger.create_run_log_file(experiment_name, run_idx + 1)
                generated_log_files.append(run_log_file)
                
                # ✨ 关键修改：增加动态随机种子配置 + 启用详细日志
                config = ExperimentConfig(
                    episodes=50,
                    num_runs=1,  # 每次只运行1次，外层控制总次数
                    max_steps_per_episode=200,
                    detailed_logging=True,  # ✅ 启用详细日志以获取决策记录
                    clear_libraries=True,
                    statistical_analysis=True,
                    random_seed=dynamic_seed  # 🎲 动态随机种子
                )
                
                # 执行单次实验
                single_run_results = self._run_single_experiment(config, run_idx + 1)
                
                # 关闭当前运行的日志文件
                self.logger.close_current_run_log()
                
                if single_run_results:
                    all_run_results.append(single_run_results)
                    self.logger.log_to_main(f"   ✅ 第{run_idx + 1}次运行完成，日志已保存：{run_log_file}")
                else:
                    self.logger.log_to_main(f"   ❌ 第{run_idx + 1}次运行失败")
            
            # 计算最终统计结果
            if all_run_results:
                final_results = self._calculate_aggregated_results(all_run_results)
                experiment_time = time.time() - experiment_start_time
                
                # 生成最终报告（写入主日志）
                self._log_final_summary_to_main_log(final_results, experiment_time)
                self._log_unified_leaderboard_to_main_log(final_results)
                
                # 记录随机种子使用情况
                self.logger.log_to_main(f"\n🎲 **随机种子使用记录**:")
                for i, seed in enumerate(self.seed_history, 1):
                    self.logger.log_to_main(f"   第{i:2d}次运行: 种子 {seed}")
                
                # 验证随机化效果
                if len(self.seed_history) > 1:
                    self.logger.log_to_main(f"\n🔍 **随机化效果验证**:")
                    unique_seeds = len(set(self.seed_history))
                    self.logger.log_to_main(f"   总运行次数: {len(self.seed_history)}")
                    self.logger.log_to_main(f"   唯一种子数: {unique_seeds}")
                    if unique_seeds == len(self.seed_history):
                        self.logger.log_to_main("   ✅ 随机种子功能正常 - 每次运行都使用了不同种子")
                    else:
                        self.logger.log_to_main("   ⚠️ 发现重复种子 - 可能需要检查随机化逻辑")
                
                # 记录所有生成的文件
                self.logger.log_to_main(f"\n📁 **生成的日志文件汇总**:")
                self.logger.log_to_main(f"   🗂️ 主汇总日志: {main_log_file}")
                for i, log_file in enumerate(generated_log_files[1:], 1):
                    self.logger.log_to_main(f"   📄 运行{i:02d}详细日志: {log_file}")
                
                return final_results
            else:
                self.logger.log_to_main("❌ 所有实验运行都失败了")
                return None
                
        except KeyboardInterrupt:
            self.logger.log_to_main("\n⏹️ 实验被用户中断")
            return None
        except Exception as e:
            self.logger.log_to_main(f"\n❌ 实验执行错误: {e}")
            return None
        finally:
            # 确保关闭所有日志文件
            self.logger.close_current_run_log()
            self.logger.close_main_log_file()
    
    def _run_single_experiment(self, config: ExperimentConfig, run_number: int):
        """执行单次实验运行"""
        try:
            # 记录使用的种子到当前运行日志
            self.logger.log(f"🎲 本次运行随机种子: {config.random_seed}")
            
            # 创建原始实验实例
            self.original_experiment = ComprehensiveBaselineExperiment(config)
            
            # 🔧 阻止底层脚本生成重复日志文件
            self._disable_base_logging()
            
            # 设置日志代理 - 最小侵入式
            self.set_logging_proxy()
            
            # 记录实验开始前的结果数量
            initial_results_count = len(getattr(self.original_experiment, 'results', {}))
            
            # 运行实验
            results = self.original_experiment.run_complete_comparison()
            
            # 检查实验是否真正完成 - 通过结果数量判断而非返回值
            final_results_count = len(getattr(self.original_experiment, 'results', {}))
            
            if final_results_count > initial_results_count:
                # 实验成功完成，生成单次运行排行榜
                self.logger.log(f"✅ 单次实验成功完成，生成了 {final_results_count} 个智能体结果")
                self._generate_run_leaderboard(self.original_experiment.results, run_number)
                
                return {
                    'results': self.original_experiment.results,
                    'raw_data': getattr(self.original_experiment, 'raw_data', {}),
                    'success': True
                }
            else:
                self.logger.log(f"⚠️ 实验运行完成但没有生成预期结果")
                return None
            
        except Exception as e:
            self.logger.log(f"❌ 单次实验运行失败: {e}")
            return None
    
    def _disable_base_logging(self):
        """禁用底层脚本的日志文件生成，避免重复日志文件"""
        try:
            # 阻止底层脚本创建自己的日志文件
            if hasattr(self.original_experiment, '_create_run_log_file'):
                # 替换为空方法
                self.original_experiment._create_run_log_file = lambda *args, **kwargs: None
            
            if hasattr(self.original_experiment, '_close_run_log_file'):
                # 替换为空方法
                self.original_experiment._close_run_log_file = lambda *args, **kwargs: None
            
            # 阻止底层脚本设置 log_file 属性
            if hasattr(self.original_experiment, 'current_run_log_file'):
                self.original_experiment.current_run_log_file = None
                
        except Exception as e:
            self.logger.log(f"⚠️ 禁用底层日志时出现警告: {e}")
    
    def set_logging_proxy(self):
        """设置日志代理 - 最小侵入式 + 进度条集成"""
        original_log = getattr(self.original_experiment, 'log', None)
        
        episode_count = 0
        def enhanced_log_with_progress(message):
            """增强的日志方法：原有日志 + 统一日志 + 进度条"""
            nonlocal episode_count
            
            # 检测回合开始的日志消息来显示进度
            if "回合" in message and ("开始" in message or "结束" in message):
                if "开始" in message:
                    episode_count += 1
                    self.progress_bar.show_episode_progress(episode_count, 50)
                elif "结束" in message and "成功率" in message:
                    # 智能体完成一个回合，确保进度条显示100%
                    self.progress_bar.show_episode_progress(50, 50)
            
            # 调用原有日志和统一日志
            if original_log:
                original_log(message)  # 保持原有日志机制
            self.logger.log(message)  # 同时写入统一日志
        
        # 只在存在log方法时才替换
        if original_log:
            self.original_experiment.log = enhanced_log_with_progress
        
        # 为智能体设置进度回调
        original_run_agent = getattr(self.original_experiment, 'run_single_agent', None)
        if original_run_agent:
            def enhanced_run_agent(agent_name, *args, **kwargs):
                # 显示智能体开始训练
                self.progress_bar.show_agent_start(agent_name)
                result = original_run_agent(agent_name, *args, **kwargs)
                if hasattr(result, 'success_rate'):
                    self.progress_bar.show_agent_complete(agent_name, result.success_rate)
                return result
            self.original_experiment.run_single_agent = enhanced_run_agent
    
    def _calculate_aggregated_results(self, all_run_results):
        """计算多次运行的聚合结果"""
        if not all_run_results:
            return {}
        
        # 获取所有智能体名称
        all_agent_names = set()
        for run_results in all_run_results:
            if isinstance(run_results, dict) and 'results' in run_results:
                all_agent_names.update(run_results['results'].keys())
            elif hasattr(run_results, 'results'):
                all_agent_names.update(run_results.results.keys())
            elif isinstance(run_results, dict):
                # 过滤掉非智能体结果的键
                agent_keys = {k for k in run_results.keys() if k not in ['raw_data', 'success', 'config']}
                all_agent_names.update(agent_keys)
        
        aggregated_results = {}
        
        for agent_name in all_agent_names:
            # 收集该智能体的所有运行结果
            agent_metrics_list = []
            for run_results in all_run_results:
                if isinstance(run_results, dict) and 'results' in run_results and agent_name in run_results['results']:
                    metrics = run_results['results'][agent_name]
                    if metrics:
                        agent_metrics_list.append(metrics)
                elif hasattr(run_results, 'results') and agent_name in run_results.results:
                    metrics = run_results.results[agent_name]
                    if metrics:
                        agent_metrics_list.append(metrics)
                elif isinstance(run_results, dict) and agent_name in run_results:
                    metrics = run_results[agent_name]
                    if metrics:
                        agent_metrics_list.append(metrics)
            
            if agent_metrics_list:
                # 计算平均指标
                avg_success_rate = sum(m.success_rate for m in agent_metrics_list) / len(agent_metrics_list)
                avg_reward = sum(m.avg_reward for m in agent_metrics_list) / len(agent_metrics_list)
                avg_steps = sum(m.avg_steps for m in agent_metrics_list) / len(agent_metrics_list)
                avg_pickup_rate = sum(m.avg_pickup_rate for m in agent_metrics_list) / len(agent_metrics_list)
                avg_dropoff_rate = sum(m.avg_dropoff_rate for m in agent_metrics_list) / len(agent_metrics_list)
                
                # 计算标准差
                if len(agent_metrics_list) > 1:
                    success_rate_std = (sum((m.success_rate - avg_success_rate) ** 2 for m in agent_metrics_list) / (len(agent_metrics_list) - 1)) ** 0.5
                    reward_std = (sum((m.avg_reward - avg_reward) ** 2 for m in agent_metrics_list) / (len(agent_metrics_list) - 1)) ** 0.5
                    steps_std = (sum((m.avg_steps - avg_steps) ** 2 for m in agent_metrics_list) / (len(agent_metrics_list) - 1)) ** 0.5
                else:
                    success_rate_std = 0.0
                    reward_std = 0.0
                    steps_std = 0.0
                
                # 创建聚合的指标对象
                class AggregatedMetrics:
                    def __init__(self):
                        self.success_rate = avg_success_rate
                        self.success_rate_std = success_rate_std
                        self.avg_reward = avg_reward
                        self.reward_std = reward_std
                        self.avg_steps = avg_steps
                        self.steps_std = steps_std
                        self.avg_pickup_rate = avg_pickup_rate
                        self.avg_dropoff_rate = avg_dropoff_rate
                        self.convergence_episode = agent_metrics_list[0].convergence_episode if hasattr(agent_metrics_list[0], 'convergence_episode') else 0
                        self.execution_time = sum(getattr(m, 'execution_time', 0) for m in agent_metrics_list)
                        
                        # 95%置信区间
                        if len(agent_metrics_list) > 1:
                            try:
                                import scipy.stats as stats
                                n = len(agent_metrics_list)
                                success_rates = [m.success_rate for m in agent_metrics_list]
                                mean = avg_success_rate
                                std_err = success_rate_std / (n ** 0.5)
                                margin = stats.t.ppf(0.975, n-1) * std_err
                                self.confidence_interval_95 = (max(0, mean - margin), min(100, mean + margin))
                            except ImportError:
                                # 如果scipy不可用，使用简单估算
                                margin = 1.96 * success_rate_std / (len(agent_metrics_list) ** 0.5)
                                self.confidence_interval_95 = (max(0, avg_success_rate - margin), min(100, avg_success_rate + margin))
                        else:
                            self.confidence_interval_95 = (avg_success_rate, avg_success_rate)
                
                aggregated_results[agent_name] = AggregatedMetrics()
        
        return aggregated_results
    
    def _log_final_summary(self, results, experiment_time):
        """记录最终实验摘要"""
        self.logger.log(f"\n{'='*80}")
        self.logger.log("📊 **详细实验结果分析**")
        self.logger.log(f"{'='*80}")
        
        if results:
            for agent_name, metrics in results.items():
                if metrics:
                    self.logger.log(f"\n🤖 **{agent_name}**:")
                    self.logger.log(f"   ✅ 成功率: {metrics.success_rate:.1f}% ± {metrics.success_rate_std:.1f}%")
                    self.logger.log(f"   💰 平均奖励: {metrics.avg_reward:+.1f} ± {metrics.reward_std:.1f}")
                    self.logger.log(f"   🚶 平均步数: {metrics.avg_steps:.1f} ± {metrics.steps_std:.1f}")
                    # 对于Taxi环境，计算成功时的平均步数
                    if metrics.success_rate > 0:
                        successful_avg_steps = metrics.avg_steps * (metrics.success_rate / 100.0)
                        self.logger.log(f"   🎯 成功时平均步数: {successful_avg_steps:.1f}")
                    self.logger.log(f"   🎯 接载成功率: {metrics.avg_pickup_rate:.1f}%")
                    self.logger.log(f"   🚁 送达成功率: {metrics.avg_dropoff_rate:.1f}%")
                    self.logger.log(f"   📈 收敛回合: {metrics.convergence_episode}")
                    self.logger.log(f"   ⏱️ 执行时间: {metrics.execution_time:.2f}秒")
                    
                    # 95%置信区间
                    ci_low, ci_high = metrics.confidence_interval_95
                    self.logger.log(f"   📊 95%置信区间: [{ci_low:.1f}%, {ci_high:.1f}%]")
        
        self.logger.log(f"\n📈 **实验统计摘要**:")
        self.logger.log(f"   🎯 总回合数: 50回合 × {self.num_runs}次运行 × 6智能体")
        total_episodes = 50 * self.num_runs * 6
        self.logger.log(f"   📊 总episode数: {total_episodes:,}")
        self.logger.log(f"   ⏱️ 总耗时: {experiment_time:.1f}秒")
        self.logger.log(f"   🏆 实验框架: 原始comprehensive_baseline_experiment.py")
    
    def _log_unified_leaderboard(self, results):
        """生成统一排行榜"""
        self.logger.log(f"\n{'='*80}")
        self.logger.log("🏆 **Taxi智能体统一排行榜**")
        self.logger.log(f"{'='*80}")
        
        # 按成功率排序
        sorted_results = sorted(
            [(name, metrics) for name, metrics in results.items() if metrics],
            key=lambda x: x[1].success_rate,
            reverse=True
        )
        
        medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣']
        
        for i, (agent_name, metrics) in enumerate(sorted_results):
            medal = medals[i] if i < len(medals) else f'{i+1}️⃣'
            
            self.logger.log(f"{medal} **{agent_name}**:")
            self.logger.log(f"     ✅ 成功率: {metrics.success_rate:.1f}% ± {metrics.success_rate_std:.1f}%")
            self.logger.log(f"     💰 平均奖励: {metrics.avg_reward:+.1f}")
            self.logger.log(f"     🚶 平均步数: {metrics.avg_steps:.1f}")
            # 对于Taxi环境，计算成功时的平均步数
            if metrics.success_rate > 0:
                successful_avg_steps = metrics.avg_steps * (metrics.success_rate / 100.0)
                self.logger.log(f"     🎯 成功时平均步数: {successful_avg_steps:.1f}")
            self.logger.log(f"     🎯 接载率: {metrics.avg_pickup_rate:.1f}%")
            self.logger.log(f"     🚁 送达率: {metrics.avg_dropoff_rate:.1f}%")
            self.logger.log("")
        
        # 特别关注ILAI系统
        ilai_metrics = None
        for name, metrics in results.items():
            if 'ILAI' in name and metrics:
                ilai_metrics = metrics
                break
        
        if ilai_metrics:
            self.logger.log(f"🎯 **ILAI系统专项分析**:")
            self.logger.log(f"   成功率: {ilai_metrics.success_rate:.1f}%")
            self.logger.log(f"   历史对比: 预期36-43% (当前: {ilai_metrics.success_rate:.1f}%)")
            if ilai_metrics.success_rate >= 30:
                self.logger.log("🏆 **ILAI系统表现优秀** - 达到预期水平")
            elif ilai_metrics.success_rate >= 20:
                self.logger.log("✅ **ILAI系统表现良好** - 接近预期水平")
            else:
                self.logger.log("⚠️ **ILAI系统需要调优** - 低于预期水平")
        
        # 添加论文标准格式表格
        self.logger.log(f"\n📊 **论文标准格式表格**:")
        self.logger.log(f"{'='*90}")
        self.logger.log(f"Algorithm            | Success Rate (%) | Avg. Steps (Successful) | Avg. Reward")
        self.logger.log(f"{'-'*90}")
        
        for i, (agent_name, metrics) in enumerate(sorted_results):
            # 格式化智能体名称
            formatted_name = {
                "ILAI System": "ILAI System",
                "A* Search Agent": "A* Search", 
                "Rule-Based Agent": "Rule-based Agent",
                "Deep Q Network": "Deep Q-Network",
                "Q-Learning Agent": "Q-Learning",
                "Random Agent": "Random Baseline"
            }.get(agent_name, agent_name)
            
            success_rate = metrics.success_rate
            # 计算成功时的平均步数（估算）
            if success_rate > 0:
                successful_avg_steps = metrics.avg_steps * (success_rate / 100.0)
            else:
                successful_avg_steps = 0.0
            avg_reward = metrics.avg_reward
            
            self.logger.log(f"{formatted_name:<20} | {success_rate:>13.1f}% | {successful_avg_steps:>18.1f} | {avg_reward:>10.1f}")
        
        self.logger.log(f"{'='*90}")
        
        self.logger.log(f"{'='*80}")
    
    def _log_final_summary_to_main_log(self, results, experiment_time):
        """记录最终实验摘要到主日志"""
        self.logger.log_to_main(f"\n{'='*80}")
        self.logger.log_to_main("📊 **详细实验结果分析**")
        self.logger.log_to_main(f"{'='*80}")
        
        if results:
            for agent_name, metrics in results.items():
                if metrics:
                    self.logger.log_to_main(f"\n🤖 **{agent_name}**:")
                    self.logger.log_to_main(f"   ✅ 成功率: {metrics.success_rate:.1f}% ± {metrics.success_rate_std:.1f}%")
                    self.logger.log_to_main(f"   💰 平均奖励: {metrics.avg_reward:+.1f} ± {metrics.reward_std:.1f}")
                    self.logger.log_to_main(f"   🚶 平均步数: {metrics.avg_steps:.1f} ± {metrics.steps_std:.1f}")
                    # 对于Taxi环境，计算成功时的平均步数
                    if metrics.success_rate > 0:
                        successful_avg_steps = metrics.avg_steps * (metrics.success_rate / 100.0)
                        self.logger.log_to_main(f"   🎯 成功时平均步数: {successful_avg_steps:.1f}")
                    self.logger.log_to_main(f"   🎯 接载成功率: {metrics.avg_pickup_rate:.1f}%")
                    self.logger.log_to_main(f"   🚁 送达成功率: {metrics.avg_dropoff_rate:.1f}%")
                    self.logger.log_to_main(f"   📈 收敛回合: {metrics.convergence_episode}")
                    self.logger.log_to_main(f"   ⏱️ 执行时间: {metrics.execution_time:.2f}秒")
                    
                    # 95%置信区间
                    ci_low, ci_high = metrics.confidence_interval_95
                    self.logger.log_to_main(f"   📊 95%置信区间: [{ci_low:.1f}%, {ci_high:.1f}%]")
        
        self.logger.log_to_main(f"\n📈 **实验统计摘要**:")
        self.logger.log_to_main(f"   🎯 总回合数: 50回合 × {self.num_runs}次运行 × 6智能体")
        total_episodes = 50 * self.num_runs * 6
        self.logger.log_to_main(f"   📊 总episode数: {total_episodes:,}")
        self.logger.log_to_main(f"   ⏱️ 总耗时: {experiment_time:.1f}秒")
        self.logger.log_to_main(f"   🏆 实验框架: 原始comprehensive_baseline_experiment.py")
    
    def _log_unified_leaderboard_to_main_log(self, results):
        """生成统一排行榜到主日志"""
        self.logger.log_to_main(f"\n{'='*80}")
        self.logger.log_to_main("🏆 **Taxi智能体统一排行榜**")
        self.logger.log_to_main(f"{'='*80}")
        
        # 按成功率排序
        sorted_results = sorted(
            [(name, metrics) for name, metrics in results.items() if metrics],
            key=lambda x: x[1].success_rate,
            reverse=True
        )
        
        medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣']
        
        for i, (agent_name, metrics) in enumerate(sorted_results):
            medal = medals[i] if i < len(medals) else f'{i+1}️⃣'
            
            self.logger.log_to_main(f"{medal} **{agent_name}**:")
            self.logger.log_to_main(f"     ✅ 成功率: {metrics.success_rate:.1f}% ± {metrics.success_rate_std:.1f}%")
            self.logger.log_to_main(f"     💰 平均奖励: {metrics.avg_reward:+.1f}")
            self.logger.log_to_main(f"     🚶 平均步数: {metrics.avg_steps:.1f}")
            # 对于Taxi环境，计算成功时的平均步数
            if metrics.success_rate > 0:
                successful_avg_steps = metrics.avg_steps * (metrics.success_rate / 100.0)
                self.logger.log_to_main(f"     🎯 成功时平均步数: {successful_avg_steps:.1f}")
            self.logger.log_to_main(f"     🎯 接载率: {metrics.avg_pickup_rate:.1f}%")
            self.logger.log_to_main(f"     🚁 送达率: {metrics.avg_dropoff_rate:.1f}%")
            self.logger.log_to_main("")
        
        # 特别关注ILAI系统
        ilai_metrics = None
        for name, metrics in results.items():
            if 'ILAI' in name and metrics:
                ilai_metrics = metrics
                break
        
        if ilai_metrics:
            self.logger.log_to_main(f"🎯 **ILAI系统专项分析**:")
            self.logger.log_to_main(f"   成功率: {ilai_metrics.success_rate:.1f}%")
            self.logger.log_to_main(f"   历史对比: 预期36-43% (当前: {ilai_metrics.success_rate:.1f}%)")
            if ilai_metrics.success_rate >= 30:
                self.logger.log_to_main("🏆 **ILAI系统表现优秀** - 达到预期水平")
            elif ilai_metrics.success_rate >= 20:
                self.logger.log_to_main("✅ **ILAI系统表现良好** - 接近预期水平")
            else:
                self.logger.log_to_main("⚠️ **ILAI系统需要调优** - 低于预期水平")
        
        # 添加论文标准格式表格
        self.logger.log_to_main(f"\n📊 **论文标准格式表格**:")
        self.logger.log_to_main(f"{'='*90}")
        self.logger.log_to_main(f"Algorithm            | Success Rate (%) | Avg. Steps (Successful) | Avg. Reward")
        self.logger.log_to_main(f"{'-'*90}")
        
        for i, (agent_name, metrics) in enumerate(sorted_results):
            # 格式化智能体名称
            formatted_name = {
                "ILAI System": "ILAI System",
                "A* Search Agent": "A* Search", 
                "Rule-Based Agent": "Rule-based Agent",
                "Deep Q Network": "Deep Q-Network",
                "Q-Learning Agent": "Q-Learning",
                "Random Agent": "Random Baseline"
            }.get(agent_name, agent_name)
            
            success_rate = metrics.success_rate
            # 计算成功时的平均步数（估算）
            if success_rate > 0:
                successful_avg_steps = metrics.avg_steps * (success_rate / 100.0)
            else:
                successful_avg_steps = 0.0
            avg_reward = metrics.avg_reward
            
            self.logger.log_to_main(f"{formatted_name:<20} | {success_rate:>13.1f}% | {successful_avg_steps:>18.1f} | {avg_reward:>10.1f}")
        
        self.logger.log_to_main(f"{'='*90}")
        
        self.logger.log_to_main(f"{'='*80}")
        self.logger.log_to_main("🎉 **Taxi论文级实验完成！**")
    
    def _generate_run_leaderboard(self, run_results, run_number):
        """为单次运行生成详细排行榜"""
        if not run_results:
            return
            
        self.logger.log(f"\n" + "🏆" * 15 + f" 第{run_number}次运行排行榜 " + "🏆" * 15)
        self.logger.log("="*60)
        
        # 按成功率排序
        sorted_run_results = []
        for agent_name, result in run_results.items():
            if hasattr(result, 'success_rate'):
                success_rate = result.success_rate
                sorted_run_results.append((agent_name, result, success_rate))
        
        sorted_run_results.sort(key=lambda x: x[2], reverse=True)
        
        for rank, (agent_name, result, success_rate) in enumerate(sorted_run_results, 1):
            avg_reward = getattr(result, 'avg_reward', 0)
            avg_steps = getattr(result, 'avg_steps', 0)
            avg_pickup_rate = getattr(result, 'avg_pickup_rate', 0)
            avg_dropoff_rate = getattr(result, 'avg_dropoff_rate', 0)
            
            medal = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}️⃣"
            
            self.logger.log(f"{medal} **{agent_name}** (排名: {rank}/6)")
            self.logger.log(f"   📊 成功率: {success_rate:.1f}%")
            self.logger.log(f"   💰 平均奖励: {avg_reward:+.1f}")
            self.logger.log(f"   🚶 平均步数: {avg_steps:.1f}")
            if success_rate > 0:
                successful_avg_steps = avg_steps * (success_rate / 100.0)
                self.logger.log(f"   🎯 成功时平均步数: {successful_avg_steps:.1f}")
            self.logger.log(f"   🎯 接载率: {avg_pickup_rate:.1f}%")
            self.logger.log(f"   🚁 送达率: {avg_dropoff_rate:.1f}%")
            self.logger.log(f"   {'-'*40}")
        
        # 添加论文标准格式表格
        self.logger.log(f"\n📊 **第{run_number}次运行论文格式表格**:")
        self.logger.log(f"{'='*90}")
        self.logger.log(f"Algorithm            | Success Rate (%) | Avg. Steps (Successful) | Avg. Reward")
        self.logger.log(f"{'='*90}")
        
        for rank, (agent_name, result, success_rate) in enumerate(sorted_run_results, 1):
            avg_reward = getattr(result, 'avg_reward', 0)
            avg_steps = getattr(result, 'avg_steps', 0)
            
            # 计算成功时的平均步数（估算）
            if success_rate > 0:
                successful_avg_steps = avg_steps * (success_rate / 100.0)
            else:
                successful_avg_steps = 0.0
            
            # 格式化智能体名称
            formatted_name = {
                "ILAI System": "ILAI System",
                "A* Search Agent": "A* Search", 
                "Rule-Based Agent": "Rule-based Agent",
                "Deep Q Network": "Deep Q-Network",
                "Q-Learning Agent": "Q-Learning",
                "Random Agent": "Random Baseline"
            }.get(agent_name, agent_name)
            
            self.logger.log(f"{formatted_name:<20} | {success_rate:>13.1f}% | {successful_avg_steps:>18.1f} | {avg_reward:>10.1f}")
        
        self.logger.log(f"{'='*90}")
        self.logger.log(f"🎉 **第{run_number}次运行排行榜完成！**")

def main():
    """主函数"""
    print("🚕 **Taxi可配置论文级实验 + 动态随机种子**")
    print("=" * 50)
    print("🎯 实验配置: 50回合 × N次运行")
    print("📊 包含6个基线智能体完整对比")
    print("✨ 动态随机种子: 确保每次运行不同")
    print("=" * 50)
    
    try:
        # 获取用户输入的实验次数
        while True:
            try:
                num_runs = input("请输入实验次数 (1=快速测试, 20=论文实验, 其他数字=自定义): ").strip()
                num_runs = int(num_runs)
                if num_runs <= 0:
                    print("❌ 实验次数必须大于0，请重新输入")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")
        
        print(f"\n🚀 开始执行 Taxi 实验: 50回合 × {num_runs}次运行")
        print(f"🎲 动态随机种子: 每次运行使用不同种子")
        print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        experiment = ConfigurableTaxiPaperExperiment(num_runs=num_runs)
        results = experiment.run_configurable_comparison_with_logging(f"ConfigurableTaxiExperiment-{num_runs}runs")
        
        print(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 **Taxi可配置论文级实验完成！**")
        
        if results:
            print("\n📊 **最终结果快速预览**:")
            sorted_results = sorted(results.items(), key=lambda x: x[1].success_rate, reverse=True)
            for rank, (agent_name, result) in enumerate(sorted_results[:3], 1):
                medal = ["🥇", "🥈", "🥉"][rank-1]
                print(f"{medal} {agent_name}: {result.success_rate:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⏹️  实验被用户中断")
    except Exception as e:
        print(f"\n❌ 实验执行错误: {e}")

if __name__ == "__main__":
    main()
