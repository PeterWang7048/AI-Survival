#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译系统快速设置脚本
Quick Translation System Setup Script
"""

import os
import sys

def create_translation_config(enable_translation=True):
    """创建翻译配置文件"""
    try:
        config_content = 'true' if enable_translation else 'false'
        with open('translation_config.txt', 'w') as f:
            f.write(config_content)
        
        status = "启用" if enable_translation else "禁用"
        print(f"✅ 翻译系统配置已保存: {status}")
        return True
    except Exception as e:
        print(f"❌ 保存翻译配置失败: {str(e)}")
        return False

def check_translation_dependencies():
    """检查翻译系统依赖"""
    required_files = [
        'translation_dictionary.py',
        'log_translation_engine.py', 
        'log_translation_monitor.py',
        'auto_translation_integration.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 缺少以下翻译系统文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n请确保翻译系统文件已正确安装。")
        return False
    else:
        print("✅ 翻译系统依赖检查通过")
        return True

def test_translation_system():
    """测试翻译系统"""
    print("🧪 测试翻译系统...")
    
    try:
        from auto_translation_integration import start_auto_translation, stop_auto_translation
        
        # 启动翻译系统
        monitor = start_auto_translation(enable_translation=True, silent_mode=False)
        
        if monitor:
            print("✅ 翻译系统启动成功")
            
            # 停止翻译系统
            stop_auto_translation(silent_mode=False)
            print("✅ 翻译系统停止成功")
            print("🎉 翻译系统测试通过")
            return True
        else:
            print("❌ 翻译系统启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 翻译系统测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🌍 翻译系统快速设置")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 命令行参数模式
        arg = sys.argv[1].lower()
        if arg in ['enable', 'on', 'true', '1']:
            enable = True
        elif arg in ['disable', 'off', 'false', '0']:
            enable = False
        else:
            print("❌ 无效参数。使用 'enable' 或 'disable'")
            return
        
        if create_translation_config(enable):
            status = "启用" if enable else "禁用"
            print(f"🎯 翻译系统已{status}")
    else:
        # 交互模式
        print("\n请选择操作:")
        print("1. 启用翻译系统")
        print("2. 禁用翻译系统")
        print("3. 检查翻译系统依赖")
        print("4. 测试翻译系统")
        print("5. 退出")
        
        while True:
            try:
                choice = input("\n请输入选项 (1-5): ").strip()
                
                if choice == '1':
                    if create_translation_config(True):
                        print("🎉 翻译系统已启用！")
                        print("   现在运行 main.py 时会自动启动翻译系统")
                    break
                    
                elif choice == '2':
                    if create_translation_config(False):
                        print("🔇 翻译系统已禁用")
                        print("   现在运行 main.py 时不会启动翻译系统")
                    break
                    
                elif choice == '3':
                    check_translation_dependencies()
                    break
                    
                elif choice == '4':
                    if check_translation_dependencies():
                        test_translation_system()
                    break
                    
                elif choice == '5':
                    print("👋 再见！")
                    break
                    
                else:
                    print("❌ 无效选择，请输入 1-5")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 操作失败: {str(e)}")
                break

if __name__ == "__main__":
    main() 