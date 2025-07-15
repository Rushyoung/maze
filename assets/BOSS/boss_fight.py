import json
import heapq
from copy import deepcopy
from typing import List, Tuple, Optional

class BossFightSolver:
    """
    使用分支限界策略求解Boss战的最优出牌顺序
    """
    
    def __init__(self, json_file: str):
        """初始化求解器，从JSON文件读取数据"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.bosses = data["B"]  # Boss血量列表
        self.player_skills = data["PlayerSkills"]  # 玩家技能 [伤害, 冷却回合]
        self.boss_count = len(self.bosses)
        self.skill_count = len(self.player_skills)
        
        # 最优解相关
        self.best_turns = float('inf')
        self.best_actions = []
        
        print(f"Boss数量: {self.boss_count}, 血量: {self.bosses}")
        print(f"技能数量: {self.skill_count}, 技能: {self.player_skills}")

    def calculate_min_turns_estimate(self, boss_hp_list: List[int], skill_cooldowns: List[int], turn: int) -> int:
        """
        计算击败剩余所有Boss的最少回合数估计（启发式函数）
        这是一个乐观估计，用于剪枝
        """
        remaining_bosses = [hp for hp in boss_hp_list if hp > 0]
        if not remaining_bosses:
            return 0
        
        # 计算每个技能在未来可用的最早回合
        available_skills = []
        for i, (damage, cooldown) in enumerate(self.player_skills):
            if damage > 0:  # 只考虑有伤害的技能
                next_available = max(turn + 1, skill_cooldowns[i])
                available_skills.append((damage, next_available, i))
        
        if not available_skills:
            return float('inf')
        
        # 按伤害/可用时间比值排序，优先使用高效技能
        available_skills.sort(key=lambda x: -x[0] / max(1, x[1] - turn))
        
        total_estimate = 0
        
        # 对每个Boss，计算使用最优技能组合的最少回合数
        for boss_hp in remaining_bosses:
            boss_turns = 0
            current_hp = boss_hp
            current_turn = turn
            temp_cooldowns = skill_cooldowns.copy()
            
            while current_hp > 0:
                best_skill = None
                best_damage = 0
                
                # 找到当前回合可用的最高伤害技能
                for damage, _, skill_idx in available_skills:
                    if temp_cooldowns[skill_idx] <= current_turn:
                        if damage > best_damage:
                            best_damage = damage
                            best_skill = skill_idx
                
                if best_skill is not None:
                    current_hp -= best_damage
                    temp_cooldowns[best_skill] = current_turn + self.player_skills[best_skill][1] + 1
                
                current_turn += 1
                boss_turns += 1
                
                # 防止无限循环
                if boss_turns > 1000:
                    return float('inf')
            
            total_estimate += boss_turns
        
        return total_estimate

    def solve(self):
        """
        使用分支限界算法求解最优出牌顺序
        返回: (最少回合数, 出牌顺序)
        """
        
        # 状态: (估计总回合数, 当前回合, 当前Boss索引, Boss血量列表, 技能冷却列表, 已执行动作)
        initial_state = (
            0,  # 估计总回合数
            0,  # 当前回合
            0,  # 当前Boss索引
            self.bosses.copy(),  # Boss血量列表
            [0] * self.skill_count,  # 技能冷却时间
            []  # 已执行的动作序列
        )
        
        # 优先队列: 按估计总回合数排序
        pq = []
        heapq.heappush(pq, initial_state)
        
        nodes_explored = 0
        nodes_pruned = 0
        
        while pq:
            estimated_turns, turn, boss_idx, boss_hp_list, skill_cooldowns, actions = heapq.heappop(pq)
            nodes_explored += 1
            
            # 剪枝: 如果当前估计已经超过最优解，跳过
            if estimated_turns >= self.best_turns:
                nodes_pruned += 1
                continue
            
            # 检查是否击败了所有Boss
            if boss_idx >= self.boss_count:
                if turn < self.best_turns:
                    self.best_turns = turn
                    self.best_actions = actions.copy()
                    print(f"找到更优解: {turn} 回合, 动作: {actions}")
                continue
            
            # 当前Boss已被击败，进入下一个Boss
            if boss_hp_list[boss_idx] <= 0:
                next_estimate = turn + self.calculate_min_turns_estimate(
                    boss_hp_list[boss_idx + 1:] + [0] * boss_idx, 
                    [max(0, cd - turn) for cd in skill_cooldowns], 
                    turn
                )
                
                if next_estimate < self.best_turns:
                    heapq.heappush(pq, (
                        next_estimate,
                        turn,
                        boss_idx + 1,
                        boss_hp_list.copy(),
                        skill_cooldowns.copy(),
                        actions.copy()
                    ))
                continue
            
            # 尝试每个技能
            for skill_idx in range(self.skill_count):
                damage, cooldown = self.player_skills[skill_idx]
                
                # 检查技能是否可用
                if skill_cooldowns[skill_idx] > turn:
                    continue
                
                # 计算新状态
                new_turn = turn + 1
                new_boss_hp_list = boss_hp_list.copy()
                new_boss_hp_list[boss_idx] = max(0, new_boss_hp_list[boss_idx] - damage)
                new_skill_cooldowns = skill_cooldowns.copy()
                new_skill_cooldowns[skill_idx] = new_turn + cooldown
                new_actions = actions + [skill_idx]
                
                # 计算启发式估计
                remaining_hp = new_boss_hp_list[boss_idx:]
                estimate = new_turn + self.calculate_min_turns_estimate(
                    remaining_hp, 
                    [max(0, cd - new_turn) for cd in new_skill_cooldowns], 
                    new_turn
                )
                
                # 只有估计值小于当前最优解才加入队列
                if estimate < self.best_turns:
                    heapq.heappush(pq, (
                        estimate,
                        new_turn,
                        boss_idx,
                        new_boss_hp_list,
                        new_skill_cooldowns,
                        new_actions
                    ))
        
        print(f"搜索完成: 探索节点 {nodes_explored}, 剪枝节点 {nodes_pruned}")
        return self.best_turns, self.best_actions

    def validate_solution(self, actions: List[int]) -> bool:
        """验证解的正确性"""
        boss_hp_list = self.bosses.copy()
        skill_cooldowns = [0] * self.skill_count
        
        for turn, skill_idx in enumerate(actions):
            if skill_cooldowns[skill_idx] > turn:
                print(f"错误: 第{turn}回合技能{skill_idx}还在冷却中")
                return False
            
            damage, cooldown = self.player_skills[skill_idx]
            
            # 找到当前目标Boss
            current_boss = 0
            while current_boss < len(boss_hp_list) and boss_hp_list[current_boss] <= 0:
                current_boss += 1
            
            if current_boss >= len(boss_hp_list):
                print(f"错误: 第{turn}回合时所有Boss已被击败")
                return False
            
            boss_hp_list[current_boss] -= damage
            skill_cooldowns[skill_idx] = turn + cooldown + 1
            
            print(f"回合{turn + 1}: 使用技能{skill_idx}(伤害{damage}), Boss{current_boss}剩余血量{max(0, boss_hp_list[current_boss])}")
        
        # 检查是否所有Boss都被击败
        for i, hp in enumerate(boss_hp_list):
            if hp > 0:
                print(f"错误: Boss{i}还有{hp}血量")
                return False
        
        print("解验证通过!")
        return True

def main():
    """主函数"""
    import os
    
    # 检查文件是否存在
    for i in range(1, 10):
        json_file = f"assets/BOSS/boss_case_{i}.json"
        if not os.path.exists(json_file):
            print(f"错误: 文件 {json_file} 不存在")
            return
        
        # 创建求解器并求解
        solver = BossFightSolver(json_file)
        min_turns, actions = solver.solve()
        
        if min_turns == float('inf'):
            print("无法找到解决方案!")
            return
        
        print("\n=== 最优解 ===")
        print(f"最少回合数: {min_turns}")
        print(f"出牌顺序: {actions}")
        
        # 验证解的正确性
        print("\n=== 解验证 ===")
        solver.validate_solution(actions)
        
        # 输出结果到JSON文件
        result = {
            "min_turns": min_turns,
            "actions": actions
        }
    
    output_file = "assets/BOSS/boss_solution.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n结果已保存到 {output_file}")

if __name__ == "__main__":
    main()
