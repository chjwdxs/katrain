#!/usr/bin/env python3
"""
简化的AI迷雾思考功能测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'katrain'))

from katrain.core.fog_of_war import FogOfWar
from katrain.core.sgf_parser import Move

def test_fog_masking():
    """测试迷雾遮蔽棋盘功能"""
    print("=== 测试迷雾遮蔽棋盘功能 ===")
    
    # 创建一个简单的棋盘状态用于测试
    board_size = 19
    
    # 模拟棋盘状态：一些黑白棋子
    stones = {
        (3, 3): "B",   # 黑棋
        (15, 15): "W", # 白棋
        (3, 15): "B",  # 黑棋
        (15, 3): "W",  # 白棋
        (9, 9): "B",   # 中央黑棋
        (10, 9): "W",  # 中央白棋
    }
    
    print("1. 原始棋盘状态:")
    for pos, color in stones.items():
        print(f"   {pos}: {color}")
    
    # 创建迷雾管理器（不需要完整的Game对象）
    class MockGame:
        def __init__(self):
            self.board_size = (board_size, board_size)
    
    mock_game = MockGame()
    fog = FogOfWar(mock_game, view_distance=3)
    
    # 初始化迷雾
    fog.initialize_full_visibility()
    
    # 模拟一些回合，让迷雾产生
    print("\n2. 模拟游戏进程，产生迷雾...")
    moves = [
        ((3, 3), "B"),
        ((15, 15), "W"),
        ((3, 15), "B"),
        ((15, 3), "W"),
        ((9, 9), "B"),
        ((10, 9), "W"),
    ]
    
    for coords, player in moves:
        fog.update_after_turn(player, attempted=coords, success=True)
        print(f"   {player} 在 {coords} 落子")
    
    # 测试迷雾视野功能
    print("\n3. 测试迷雾视野功能...")
    
    # 测试黑棋视角的可见性
    print("\n   黑棋(B)的视野等级:")
    for pos, color in stones.items():
        x, y = pos
        level = fog.get_level("B", pos)
        print(f"   {pos} ({color}): 视野等级 {level}")
    
    # 测试白棋视角的可见性
    print("\n   白棋(W)的视野等级:")
    for pos, color in stones.items():
        x, y = pos
        level = fog.get_level("W", pos)
        print(f"   {pos} ({color}): 视野等级 {level}")
    
    # 检查暴露的敌方石子
    print("\n   黑棋已暴露的白棋石子:", fog.exposed["B"])
    print("   白棋已暴露的黑棋石子:", fog.exposed["W"])
    
    # 检查迷雾是否正确工作
    print("\n4. 验证迷雾效果:")
    
    # 检查是否有石子的视野等级小于2（被迷雾影响）
    b_fogged_count = sum(1 for pos in stones if fog.get_level("B", pos) < 2)
    w_fogged_count = sum(1 for pos in stones if fog.get_level("W", pos) < 2)
    
    print(f"   黑棋视角下被迷雾影响的石子数: {b_fogged_count}")
    print(f"   白棋视角下被迷雾影响的石子数: {w_fogged_count}")
    
    if b_fogged_count > 0 or w_fogged_count > 0:
        print("✓ 迷雾功能正常工作！")
    else:
        print("? 没有石子被迷雾影响，可能是视野范围太大或需要更多回合")
    
    print("\n5. 测试完成")

if __name__ == "__main__":
    test_fog_masking()