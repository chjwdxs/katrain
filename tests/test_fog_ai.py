#!/usr/bin/env python3
"""
测试AI在迷雾下思考功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'katrain'))

from katrain.core.game import Game
from katrain.core.engine import KataGoEngine
from katrain.core.fog_of_war import FogOfWar
from katrain.core.ai import generate_ai_move
from katrain.core.sgf_parser import Move
from katrain.core.constants import AI_DEFAULT

class MockKaTrain:
    """模拟KaTrain主类用于测试"""
    def __init__(self):
        self.debug_level = 1
        self._config = {
            "engine": {
                "katago": "",
                "model": "katrain/models/kata1-b18c384nbt-s9996604416-d4316597426.bin.gz",
                "config": "katrain/KataGo/analysis_config.cfg",
                "max_visits": 100,
                "fast_visits": 25,
                "max_time": 8.0,
            },
            "fog": {
                "ai_uses_fog": True
            }
        }
    
    def config(self, key, default=None):
        keys = key.split('/')
        value = self._config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    def log(self, message, level=1):
        print(f"[LOG] {message}")

def test_fog_ai():
    """测试AI在迷雾下思考"""
    print("=== 测试AI在迷雾下思考功能 ===")
    
    # 创建模拟环境
    katrain = MockKaTrain()
    
    try:
        # 创建引擎
        print("1. 初始化KataGo引擎...")
        engine = KataGoEngine(katrain, katrain.config("engine"))
        
        # 创建游戏
        print("2. 创建新游戏...")
        game = Game(katrain, engine)
        
        # 创建迷雾管理器
        print("3. 初始化迷雾围棋...")
        fog = FogOfWar(game, view_distance=3)
        fog.initialize_full_visibility()
        game.fog_manager = fog
        
        # 下几步棋创建一些迷雾
        print("4. 下几步棋创建迷雾环境...")
        moves = [
            Move((3, 3), player="B"),  # 黑棋
            Move((15, 15), player="W"), # 白棋
            Move((3, 15), player="B"),  # 黑棋
            Move((15, 3), player="W"),  # 白棋
        ]
        
        for move in moves:
            game.play(move)
            fog.update_after_turn(move.player, attempted=move.coords, success=True)
            print(f"   下棋: {move.player} {move.gtp()}")
        
        # 测试AI在迷雾下思考
        print("5. 测试AI在迷雾下思考...")
        
        # 获取当前玩家的可见石子数量
        current_player = game.current_node.next_player
        total_stones = len(game.stones)
        
        # 模拟AI思考
        ai_settings = {}
        print(f"   当前轮到: {current_player}")
        print(f"   棋盘上总石子数: {total_stones}")
        print(f"   AI迷雾思考开关: {katrain.config('fog/ai_uses_fog')}")
        
        # 生成AI移动
        move, played_node = generate_ai_move(game, AI_DEFAULT, ai_settings)
        
        print(f"   AI选择的移动: {move.gtp()}")
        print(f"   AI思考内容: {played_node.ai_thoughts}")
        
        # 检查是否是迷雾AI
        if "[Fog AI]" in played_node.ai_thoughts:
            print("✓ AI在迷雾下思考功能正常工作！")
        else:
            print("✗ AI没有在迷雾下思考，使用了全盘信息")
        
        print("6. 测试完成")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        if 'engine' in locals():
            try:
                engine.shutdown()
            except:
                pass

if __name__ == "__main__":
    test_fog_ai()