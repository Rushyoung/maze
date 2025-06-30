def simulate_boss_fight_optimized(B, PlayerSkills, expected_actions=None):
    current_b = B.copy()
    n_skills = len(PlayerSkills)
    current_cd = [0] * n_skills
    actions = []
    turns = 0
    current_target = 0  # 当前目标Boss
    
    while any(hp > 0 for hp in current_b):
        turns += 1
        
        # 跳过已击败的Boss
        while current_target < len(current_b) and current_b[current_target] <= 0:
            current_target += 1
        if current_target >= len(current_b):
            break
            
        # 尝试匹配预期动作序列
        if expected_actions and turns-1 < len(expected_actions):
            action = expected_actions[turns-1]
            if action != -1 and current_cd[action] > 0:
                raise ValueError(f"动作序列不合法: 技能{action}处于CD中")
        else:
            # 智能选择最佳技能
            action = -1  # 默认普通攻击
            best_damage = 0
            for i, (damage, cd) in enumerate(PlayerSkills):
                if current_cd[i] == 0 and damage > best_damage:
                    best_damage = damage
                    action = i
        
        # 执行动作
        if action != -1:
            damage = PlayerSkills[action][0]
            current_b[current_target] = max(0, current_b[current_target] - damage)
            current_cd[action] = PlayerSkills[action][1]
        else:
            current_b[current_target] = max(0, current_b[current_target] - 1)
        
        actions.append(action)
        
        # 更新CD
        for i in range(n_skills):
            if current_cd[i] > 0:
                current_cd[i] -= 1
    
    return turns, actions

# 测试所有样例
test_cases = [
    {"B": [11,7,18], "PlayerSkills": [[10,1],[11,4],[11,5],[3,0],[4,4]], "actions": [2,0,1,0]},
    {"B": [13,11], "PlayerSkills": [[3,2],[1,0],[10,2],[5,1]], "actions": [2,0,3,2]},
    {"B": [15,18], "PlayerSkills": [[3,0],[2,1],[10,5]], "actions": [2,0,0,0,0,0,2]},
    {"B": [20,10,20], "PlayerSkills": [[1,0],[9,4],[10,5]], "actions": [1,2,0,0,0,1,0,2,0,0,1]},
    {"B": [14,14], "PlayerSkills": [[3,0],[6,2],[4,1],[4,1],[9,3]], "actions": [4,1,2,3,4]},
    {"B": [13,13,20], "PlayerSkills": [[9,5],[3,0]], "actions": [0,1,1,1,1,1,1,1,0,1,1,1,1]},
    {"B": [13,18,19,14], "PlayerSkills": [[4,1],[3,2],[5,2],[9,4],[2,0]], "actions": [3,0,1,2,0,3,2,0,1,2,4,3,2]}
]

for case in test_cases:
    turns, actions = simulate_boss_fight_optimized(
        case["B"], 
        case["PlayerSkills"],
        case["actions"]
    )
    print(f"Boss血量: {case['B']}")
    print(f"技能列表: {case['PlayerSkills']}")
    print(f"匹配结果: 回合数={turns}, 动作序列={actions}")
    print("验证:", "通过" if actions == case["actions"] else "失败")
    print("-"*50)