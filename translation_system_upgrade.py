#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译系统升级脚本 - 安全部署改进版翻译引擎
Translation System Upgrade Script - Safely deploy improved translation engine
"""

import os
import shutil
import datetime
from typing import Dict, List

class TranslationSystemUpgrade:
    """翻译系统升级管理器"""
    
    def __init__(self):
        self.backup_dir = "backups/translation_system"
        self.current_files = [
            "log_translation_engine.py",
            "log_translation_monitor.py",
            "auto_translation_integration.py"
        ]
        self.new_files = [
            "log_translation_engine_improved.py"
        ]
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"📁 创建备份目录: {self.backup_dir}")
    
    def create_backup(self) -> bool:
        """创建当前系统的备份"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_subdir)
            
            print(f"💾 创建系统备份: {backup_subdir}")
            
            for file in self.current_files:
                if os.path.exists(file):
                    shutil.copy2(file, backup_subdir)
                    print(f"  ✅ 备份: {file}")
                else:
                    print(f"  ⚠️ 文件不存在: {file}")
            
            # 备份配置文件
            config_files = ["translation_config.txt", "complete_translation_dictionary.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, backup_subdir)
                    print(f"  ✅ 备份配置: {config_file}")
            
            print(f"✅ 备份完成: {backup_subdir}")
            return True
            
        except Exception as e:
            print(f"❌ 备份失败: {str(e)}")
            return False
    
    def test_improved_engine(self) -> Dict:
        """测试改进版翻译引擎"""
        print("🧪 测试改进版翻译引擎...")
        
        try:
            from log_translation_engine_improved import ImprovedLogTranslationEngine
            
            engine = ImprovedLogTranslationEngine()
            test_results = engine.test_translation_quality()
            
            print(f"📊 测试结果:")
            print(f"  成功率: {test_results['successful_translations']}/{test_results['total_tests']} ({test_results['successful_translations']/test_results['total_tests']*100:.1f}%)")
            
            return test_results
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return {'successful_translations': 0, 'total_tests': 0}
    
    def deploy_improved_engine(self, test_results: Dict) -> bool:
        """部署改进版翻译引擎"""
        # 检查测试结果
        if test_results['successful_translations'] < test_results['total_tests'] * 0.8:
            print("⚠️ 测试成功率不足80%，建议不要部署")
            return False
        
        print("🚀 部署改进版翻译引擎...")
        
        try:
            # 创建新版本的引擎文件
            improved_content = ""
            with open("log_translation_engine_improved.py", 'r', encoding='utf-8') as f:
                improved_content = f.read()
            
            # 替换类名和相关内容
            improved_content = improved_content.replace(
                "class ImprovedLogTranslationEngine:",
                "class LogTranslationEngine:"
            )
            improved_content = improved_content.replace(
                "ImprovedLogTranslationEngine()",
                "LogTranslationEngine()"
            )
            
            # 写入新版本
            with open("log_translation_engine_new.py", 'w', encoding='utf-8') as f:
                f.write(improved_content)
            
            print("✅ 新版本引擎已准备就绪")
            return True
            
        except Exception as e:
            print(f"❌ 部署失败: {str(e)}")
            return False
    
    def safe_replace_engine(self) -> bool:
        """安全替换翻译引擎"""
        print("🔄 安全替换翻译引擎...")
        
        try:
            # 停止现有翻译服务
            print("🛑 停止现有翻译服务...")
            
            # 替换主引擎文件
            if os.path.exists("log_translation_engine_new.py"):
                if os.path.exists("log_translation_engine.py"):
                    os.rename("log_translation_engine.py", "log_translation_engine_old.py")
                
                os.rename("log_translation_engine_new.py", "log_translation_engine.py")
                print("✅ 翻译引擎已更新")
                
                # 测试新引擎
                try:
                    from log_translation_engine import LogTranslationEngine
                    engine = LogTranslationEngine()
                    print("✅ 新引擎加载成功")
                    return True
                except Exception as e:
                    print(f"❌ 新引擎加载失败: {str(e)}")
                    # 回滚
                    self.rollback_engine()
                    return False
            else:
                print("❌ 新引擎文件不存在")
                return False
                
        except Exception as e:
            print(f"❌ 替换失败: {str(e)}")
            return False
    
    def rollback_engine(self) -> bool:
        """回滚翻译引擎"""
        print("🔄 回滚翻译引擎...")
        
        try:
            if os.path.exists("log_translation_engine_old.py"):
                if os.path.exists("log_translation_engine.py"):
                    os.remove("log_translation_engine.py")
                os.rename("log_translation_engine_old.py", "log_translation_engine.py")
                print("✅ 引擎已回滚")
                return True
            else:
                print("❌ 备份引擎不存在")
                return False
                
        except Exception as e:
            print(f"❌ 回滚失败: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        print("🧹 清理临时文件...")
        
        temp_files = [
            "log_translation_engine_new.py",
            "log_translation_engine_old.py"
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"  🗑️ 删除: {temp_file}")
    
    def run_upgrade(self) -> bool:
        """运行完整升级流程"""
        print("🚀 开始翻译系统升级...")
        print("=" * 60)
        
        # 步骤1: 创建备份
        print("\n📋 步骤1: 创建系统备份")
        if not self.create_backup():
            print("❌ 备份失败，升级中止")
            return False
        
        # 步骤2: 测试改进版引擎
        print("\n📋 步骤2: 测试改进版引擎")
        test_results = self.test_improved_engine()
        if test_results['successful_translations'] == 0:
            print("❌ 测试失败，升级中止")
            return False
        
        # 步骤3: 部署改进版引擎
        print("\n📋 步骤3: 部署改进版引擎")
        if not self.deploy_improved_engine(test_results):
            print("❌ 部署失败，升级中止")
            return False
        
        # 步骤4: 安全替换引擎
        print("\n📋 步骤4: 安全替换引擎")
        if not self.safe_replace_engine():
            print("❌ 替换失败，升级中止")
            return False
        
        # 步骤5: 最终测试
        print("\n📋 步骤5: 最终测试")
        try:
            from log_translation_engine import LogTranslationEngine
            engine = LogTranslationEngine()
            final_test = engine.test_translation_quality()
            
            if final_test['successful_translations'] >= final_test['total_tests'] * 0.8:
                print("✅ 最终测试通过")
                self.cleanup_temp_files()
                print("\n🎉 翻译系统升级成功!")
                print(f"   成功率: {final_test['successful_translations']}/{final_test['total_tests']} ({final_test['successful_translations']/final_test['total_tests']*100:.1f}%)")
                return True
            else:
                print("❌ 最终测试失败，执行回滚")
                self.rollback_engine()
                return False
                
        except Exception as e:
            print(f"❌ 最终测试出错: {str(e)}")
            self.rollback_engine()
            return False
    
    def show_status(self):
        """显示系统状态"""
        print("📊 翻译系统状态:")
        print("-" * 40)
        
        # 检查文件状态
        for file in self.current_files:
            if os.path.exists(file):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (缺失)")
        
        # 检查配置文件
        config_files = ["translation_config.txt", "complete_translation_dictionary.json"]
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"  ✅ {config_file}")
            else:
                print(f"  ❌ {config_file} (缺失)")
        
        # 检查备份
        if os.path.exists(self.backup_dir):
            backup_count = len([d for d in os.listdir(self.backup_dir) if d.startswith("backup_")])
            print(f"  📁 备份数量: {backup_count}")
        else:
            print(f"  📁 备份数量: 0")

def main():
    """主函数"""
    print("🌍 翻译系统升级管理器")
    print("=" * 50)
    
    upgrader = TranslationSystemUpgrade()
    
    while True:
        print("\n🔧 选择操作:")
        print("1. 显示系统状态")
        print("2. 测试改进版引擎")
        print("3. 运行完整升级")
        print("4. 创建备份")
        print("5. 退出")
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == "1":
            upgrader.show_status()
        elif choice == "2":
            upgrader.test_improved_engine()
        elif choice == "3":
            if upgrader.run_upgrade():
                print("✅ 升级成功!")
            else:
                print("❌ 升级失败!")
        elif choice == "4":
            upgrader.create_backup()
        elif choice == "5":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main() 