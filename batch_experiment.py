#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import random
import time
from datetime import datetime

class BatchExperiment:
    """批量实验管理器"""
    
    def __init__(self):
        self.results = []
    
    def get_config(self):
        """获取实验配置"""
        print("🧪 AI生存游戏 - 批量实验模式")
        print("="*50)
        
        try:
            # 猛兽数量
            predator_input = input("猛兽数量 (默认30): ").strip()
            predator_count = int(predator_input) if predator_input else 30
            
            # 游戏天数
            days_input = input("游戏天数 (默认30): ").strip()
            game_days = int(days_input) if days_input else 30
            
            # 运行次数
            runs_input = input("运行次数 (默认1): ").strip()
            run_count = int(runs_input) if runs_input else 1
            
            print(f"\n📋 配置确认:")
            print(f"   🐅 猛兽数量: {predator_count}")
            print(f"   📅 游戏天数: {game_days}")
            print(f"   🔄 运行次数: {run_count}")
            
            confirm = input("\n开始实验? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return None
            
            return {
                'predator_count': predator_count,
                'game_days': game_days,
                'run_count': run_count
            }
            
        except (ValueError, KeyboardInterrupt):
            print("❌ 配置无效或已取消")
            return None
    
    def create_modified_main(self, predator_count, game_days, seed):
        """创建修改后的主程序副本"""
        
        # 读取原始main.py
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改设置
        modifications = [
            (f'settings["seed"] = {settings.get("seed", 42)}', f'settings["seed"] = {seed}'),
            (f'settings["game_duration"] = {settings.get("game_duration", 30)}', f'settings["game_duration"] = {game_days}'),
            (f'settings["animal_abundance_predator"] = {settings.get("animal_abundance_predator", 30)}', f'settings["animal_abundance_predator"] = {predator_count}'),
        ]
        
        modified_content = content
        for old, new in modifications:
            if old in content:
                modified_content = modified_content.replace(old, new)
        
        # 修改主程序入口为无界面模式
        ui_start = '''if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root)
    root.mainloop()'''
        
        headless_start = f'''if __name__ == "__main__":
    # 无界面模式
    import time
    print("🎮 无界面游戏开始...")
    print(f"种子: {seed}, 天数: {game_days}, 猛兽: {predator_count}")
    
    start_time = time.time()
    game = Game(settings, None, None)
    
    # 运行游戏循环
    for day in range(1, {game_days} + 1):
        game.current_day = day
        
        # 检查存活玩家
        alive = [p for p in game.players if p.is_alive()]
        if not alive:
            print(f"第{{day}}天: 所有玩家死亡")
            break
        
        # 玩家行动
        for player in game.players:
            if player.is_alive():
                try:
                    player.take_turn(game)
                except:
                    pass
        
        # 动物行动
        for animal in game.game_map.animals:
            if animal.alive:
                try:
                    animal.move(game.game_map, game.players)
                except:
                    pass
        
        # 群体狩猎和资源重生
        if day % game.group_hunt_frequency == 0:
            try:
                game.group_hunt()
            except:
                pass
        
        try:
            game.respawn_resources()
        except:
            pass
        
        # 进度显示
        if day % max(1, {game_days} // 10) == 0:
            print(f"第{{day}}天 - 存活: {{len(alive)}}")
    
    # 结束游戏
    game.end_game()
    duration = time.time() - start_time
    print(f"游戏完成，耗时: {{duration:.1f}}秒")
    
    # 保存结果
    import json
    result = {{
        'seed': {seed},
        'duration': duration,
        'final_day': game.current_day,
        'rankings': game.rankings if hasattr(game, 'rankings') else [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }}
    
    with open(f'game_result_{{seed}}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"结果已保存: game_result_{{seed}}.json")'''
        
        modified_content = modified_content.replace(ui_start, headless_start)
        
        # 保存修改后的文件
        temp_filename = f'main_headless_{seed}.py'
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return temp_filename
    
    def run_single_experiment(self, config, run_index):
        """运行单次实验"""
        seed = random.randint(1, 999999)
        
        print(f"\n🚀 实验 {run_index}/{config['run_count']}")
        print(f"   种子: {seed}")
        
        try:
            # 创建修改后的主程序
            temp_file = self.create_modified_main(
                config['predator_count'], 
                config['game_days'], 
                seed
            )
            
            # 运行游戏
            start_time = time.time()
            result = subprocess.run([sys.executable, temp_file], 
                                  capture_output=True, text=True, timeout=300)
            duration = time.time() - start_time
            
            # 清理临时文件
            os.remove(temp_file)
            
            if result.returncode == 0:
                print(f"   ✅ 成功 ({duration:.1f}秒)")
                
                # 读取结果文件
                result_file = f'game_result_{seed}.json'
                if os.path.exists(result_file):
                    import json
                    with open(result_file, 'r', encoding='utf-8') as f:
                        game_result = json.load(f)
                    os.remove(result_file)  # 清理结果文件
                    return game_result
                else:
                    return {'seed': seed, 'success': True, 'duration': duration}
            else:
                print(f"   ❌ 失败: {result.stderr[:100]}...")
                return {'seed': seed, 'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 超时")
            return {'seed': seed, 'success': False, 'error': 'timeout'}
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return {'seed': seed, 'success': False, 'error': str(e)}
    
    def save_batch_results(self, config, results):
        """保存批量结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'batch_experiment_{timestamp}.txt'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("AI生存游戏 - 批量实验报告\n")
            f.write("="*50 + "\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"配置: 猛兽{config['predator_count']}, 天数{config['game_days']}, 次数{config['run_count']}\n\n")
            
            successful = [r for r in results if r.get('success', False)]
            failed = [r for r in results if not r.get('success', False)]
            
            f.write(f"统计: 成功{len(successful)}, 失败{len(failed)}\n")
            if successful:
                avg_time = sum(r.get('duration', 0) for r in successful) / len(successful)
                f.write(f"平均耗时: {avg_time:.1f}秒\n")
            
            f.write("\n详细结果:\n")
            for i, result in enumerate(results, 1):
                f.write(f"\n{i}. 种子{result['seed']}: ")
                if result.get('success', False):
                    f.write(f"成功 ({result.get('duration', 0):.1f}秒)\n")
                    if 'rankings' in result and result['rankings']:
                        f.write("   前3名:\n")
                        for j, rank in enumerate(result['rankings'][:3], 1):
                            f.write(f"     {j}. {rank.get('name', 'Unknown')}\n")
                else:
                    f.write(f"失败 - {result.get('error', 'Unknown')}\n")
        
        print(f"\n📄 报告已保存: {filename}")
    
    def run_batch(self, config):
        """运行批量实验"""
        print(f"\n🚀 开始批量实验...")
        
        results = []
        for i in range(1, config['run_count'] + 1):
            result = self.run_single_experiment(config, i)
            results.append(result)
            
            progress = i / config['run_count'] * 100
            print(f"📊 进度: {progress:.1f}%")
        
        self.save_batch_results(config, results)
        
        # 统计
        successful = [r for r in results if r.get('success', False)]
        print(f"\n📈 完成! 成功: {len(successful)}/{len(results)}")
        
        return results

def main():
    """主函数"""
    # 检查main.py是否存在
    if not os.path.exists('main.py'):
        print("❌ 未找到main.py文件")
        return
    
    # 导入设置
    try:
        sys.path.append('.')
        from main import settings
        globals()['settings'] = settings
        print("✅ 成功加载游戏设置")
    except ImportError as e:
        print(f"❌ 导入设置失败: {e}")
        return
    
    experiment = BatchExperiment()
    
    # 获取配置
    config = experiment.get_config()
    if not config:
        return
    
    try:
        # 运行批量实验
        results = experiment.run_batch(config)
        print("🎉 批量实验完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️  实验被中断")
    except Exception as e:
        print(f"\n❌ 实验失败: {e}")

if __name__ == "__main__":
    main() 