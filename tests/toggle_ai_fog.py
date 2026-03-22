#!/usr/bin/env python3
"""
AI迷雾思考模式切换工具
"""

import json
import os

def toggle_ai_fog_mode():
    """切换AI迷雾思考模式"""
    config_path = "katrain/config.json"
    
    if not os.path.exists(config_path):
        print("❌ 配置文件不存在:", config_path)
        return
    
    try:
        # 读取配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取当前设置
        current_setting = config.get("fog", {}).get("ai_uses_fog", False)
        
        print(f"当前AI迷雾思考模式: {'开启' if current_setting else '关闭'}")
        
        # 询问用户选择
        print("\n请选择AI思考模式:")
        print("1. 开启迷雾思考 - AI只基于可见信息思考（更有挑战性）")
        print("2. 关闭迷雾思考 - AI基于全盘信息思考（原始行为）")
        print("3. 取消")
        
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            new_setting = True
            mode_name = "迷雾思考模式"
        elif choice == "2":
            new_setting = False
            mode_name = "全盘思考模式"
        elif choice == "3":
            print("取消操作")
            return
        else:
            print("❌ 无效选择")
            return
        
        # 确保fog配置存在
        if "fog" not in config:
            config["fog"] = {}
        
        # 更新设置
        config["fog"]["ai_uses_fog"] = new_setting
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ 已设置为 {mode_name}")
        print(f"   ai_uses_fog = {new_setting}")
        
        if current_setting != new_setting:
            print("\n⚠️  请重启KaTrain以使设置生效")
        else:
            print("\n设置未改变")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")

def show_current_setting():
    """显示当前设置"""
    config_path = "katrain/config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        ai_uses_fog = config.get("fog", {}).get("ai_uses_fog", False)
        
        print("=== 当前AI迷雾思考设置 ===")
        print(f"ai_uses_fog: {ai_uses_fog}")
        
        if ai_uses_fog:
            print("🌫️  AI在迷雾下思考 - 只基于可见信息做决策")
            print("   - AI无法看到迷雾中的对方棋子")
            print("   - AI可能会尝试非法落子并失去回合")
            print("   - 更具挑战性和真实性")
        else:
            print("🔍 AI基于全盘信息思考 - 原始行为")
            print("   - AI可以看到整个棋盘")
            print("   - AI不会受到迷雾影响")
            print("   - 迷雾只影响人类玩家")
            
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")

if __name__ == "__main__":
    print("🎮 KaTrain AI迷雾思考模式设置工具")
    print("=" * 40)
    
    show_current_setting()
    print()
    
    while True:
        print("请选择操作:")
        print("1. 切换AI思考模式")
        print("2. 查看当前设置")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            toggle_ai_fog_mode()
        elif choice == "2":
            show_current_setting()
        elif choice == "3":
            print("再见！")
            break
        else:
            print("❌ 无效选择")
        
        print("\n" + "=" * 40)