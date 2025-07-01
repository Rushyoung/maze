import pygame
import sys
import json
import boss_fight
# 初始化 pygame
pygame.init()

# 设置窗口大小
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("BOSS FIGHT SIMULATION")

# 定义颜色
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 定义字体
font_large = pygame.font.SysFont('Arial', 32, bold=True)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 18)

# 使用算法求解Boss战
solver = boss_fight.BossFightSolver("D:\\code\\work\\maze\\maze\\assets\\BOSS\\boss_case_3.json")
min_turns, actions = solver.solve()

# 从求解器获取Boss和技能数据
B = solver.bosses.copy()  # Boss血量列表
original_B = solver.bosses.copy()  # 保存原始血量用于显示
PlayerSkills = solver.player_skills  # 玩家技能列表

print(f"Boss数据: {B}")
print(f"技能数据: {PlayerSkills}")
print(f"最优解: {min_turns}回合, 动作序列: {actions}")

# 当前回合和当前目标Boss
current_turn = 0
current_target = 0
animation_speed = 60  # 每秒帧数，可以调整动画速度

# 美化后的布局位置
boss_start_y = 120
boss_spacing = 80
skill_start_y = 480  # 将技能区域向下移动，避免与Boss重叠
skill_spacing = 60
card_history_x = 800  # 已出卡牌显示区域

# 动态计算Boss和技能的显示位置
boss_positions = [(80, boss_start_y + i * boss_spacing) for i in range(len(B))]
skill_positions = [(50, skill_start_y + i * skill_spacing) for i in range(len(PlayerSkills))]

# 初始化CD状态和卡牌历史
current_cd = [0] * len(PlayerSkills)
frame_counter = 0  # 帧计数器，用于控制动画速度
played_cards = []  # 记录已出的卡牌

# 主循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 空格键重置游戏
                B = original_B.copy()
                current_turn = 0
                current_target = 0
                current_cd = [0] * len(PlayerSkills)
                frame_counter = 0
                played_cards = []  # 重置已出卡牌记录

    # 清屏
    screen.fill(WHITE)
    
    # 绘制背景装饰
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, screen_width, 80))
    pygame.draw.rect(screen, DARK_GRAY, (0, 80, screen_width, 4))

    # 绘制标题
    title_text = font_large.render("BOSS FIGHT SIMULATION", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width//2, 40))
    screen.blit(title_text, title_rect)

    # 绘制Boss区域标题
    boss_title = font_medium.render("BOSSES", True, DARK_GRAY)
    screen.blit(boss_title, (50, 90))

    # 绘制Boss血量条
    for i, hp in enumerate(B):
        if i < len(boss_positions):
            boss_y = boss_positions[i][1]
            boss_x = boss_positions[i][0]
            
            # Boss标签背景
            label_bg = pygame.Rect(boss_x - 70, boss_y + 5, 60, 30)
            pygame.draw.rect(screen, DARK_GRAY, label_bg)
            label_text = font_small.render(f"Boss{i+1}", True, WHITE)
            label_rect = label_text.get_rect(center=label_bg.center)
            screen.blit(label_text, label_rect)
            
            # 血量条背景（加阴影效果）
            shadow_rect = pygame.Rect(boss_x + 2, boss_y + 2, 350, 40)
            pygame.draw.rect(screen, GRAY, shadow_rect)
            bg_rect = pygame.Rect(boss_x, boss_y, 350, 40)
            pygame.draw.rect(screen, LIGHT_GRAY, bg_rect)
            
            # 当前血量条
            if original_B[i] > 0:
                hp_ratio = max(0, hp) / original_B[i]
                hp_width = int(350 * hp_ratio)
                
                # 血量颜色渐变
                if hp_ratio > 0.7:
                    hp_color = GREEN
                elif hp_ratio > 0.3:
                    hp_color = YELLOW
                else:
                    hp_color = RED
                
                if i == current_target and hp > 0:
                    hp_color = ORANGE  # 当前目标高亮
                
                hp_rect = pygame.Rect(boss_x, boss_y, hp_width, 40)
                pygame.draw.rect(screen, hp_color, hp_rect)
            
            # 血量条边框
            pygame.draw.rect(screen, BLACK, bg_rect, 3)
            
            # 血量文字
            hp_text = f"{max(0, hp)}/{original_B[i]}"
            text = font_medium.render(hp_text, True, BLACK)
            text_rect = text.get_rect(center=(boss_x + 175, boss_y + 20))
            screen.blit(text, text_rect)
            
            # 如果是当前目标，添加箭头指示
            if i == current_target and hp > 0:
                arrow_text = font_medium.render("← TARGET", True, RED)
                screen.blit(arrow_text, (boss_x + 360, boss_y + 10))

    # 绘制技能区域标题
    skill_title = font_medium.render("PLAYER SKILLS", True, DARK_GRAY)
    screen.blit(skill_title, (50, skill_start_y - 30))  # 调整标题位置

    # 绘制技能状态
    for i, (damage, cd) in enumerate(PlayerSkills):
        if i < len(skill_positions):
            skill_y = skill_positions[i][1]
            skill_x = skill_positions[i][0]
            
            # 技能背景框（加阴影）
            shadow_rect = pygame.Rect(skill_x + 2, skill_y + 2, 500, 50)
            pygame.draw.rect(screen, GRAY, shadow_rect)
            
            skill_color = GREEN if current_cd[i] == 0 else LIGHT_GRAY
            skill_rect = pygame.Rect(skill_x, skill_y, 500, 50)
            pygame.draw.rect(screen, skill_color, skill_rect)
            pygame.draw.rect(screen, BLACK, skill_rect, 2)
            
            # 技能编号圆圈
            circle_center = (skill_x + 25, skill_y + 25)
            pygame.draw.circle(screen, DARK_GRAY, circle_center, 18)
            pygame.draw.circle(screen, WHITE, circle_center, 15)
            skill_num = font_medium.render(str(i), True, BLACK)
            num_rect = skill_num.get_rect(center=circle_center)
            screen.blit(skill_num, num_rect)
            
            # 技能信息
            skill_text = f"Damage: {damage}  |  Cooldown: {cd}"
            text = font_medium.render(skill_text, True, BLACK)
            screen.blit(text, (skill_x + 50, skill_y + 8))
            
            # CD状态
            if current_cd[i] > 0:
                cd_text = f"Cooldown: {current_cd[i]} turns"
                cd_render = font_small.render(cd_text, True, RED)
                screen.blit(cd_render, (skill_x + 50, skill_y + 28))
            else:
                ready_text = "READY TO USE"
                ready_render = font_small.render(ready_text, True, GREEN)
                screen.blit(ready_render, (skill_x + 50, skill_y + 28))

    # 绘制游戏状态信息区域
    info_bg = pygame.Rect(50, 420, 700, 40)  # 调整信息区域位置，放在Boss和技能区域之间
    pygame.draw.rect(screen, LIGHT_GRAY, info_bg)
    pygame.draw.rect(screen, DARK_GRAY, info_bg, 2)

    # 绘制当前回合和剩余回合
    turn_text = f"Turn: {current_turn + 1} / {len(actions)}"
    turn_render = font_medium.render(turn_text, True, BLACK)
    screen.blit(turn_render, (60, 425))
    
    # 绘制当前使用的技能
    if current_turn < len(actions):
        current_skill = actions[current_turn]
        skill_text = f"Using Skill: {current_skill} (Damage: {PlayerSkills[current_skill][0]})"
        skill_render = font_small.render(skill_text, True, BLUE)  # 使用小字体节省空间
        screen.blit(skill_render, (350, 425))

    # 绘制已出卡牌历史区域
    card_bg = pygame.Rect(card_history_x, 100, 350, screen_height - 150)
    pygame.draw.rect(screen, WHITE, card_bg)
    pygame.draw.rect(screen, DARK_GRAY, card_bg, 3)
    
    # 卡牌历史标题
    history_title = font_medium.render("CARDS PLAYED", True, DARK_GRAY)
    screen.blit(history_title, (card_history_x + 10, 110))
    
    # 显示已出的卡牌
    max_visible_cards = (screen_height - 200) // 35
    start_index = max(0, len(played_cards) - max_visible_cards)
    
    for idx, (turn, skill_idx) in enumerate(played_cards[start_index:]):
        card_y = 140 + idx * 35
        
        # 卡牌背景
        card_rect = pygame.Rect(card_history_x + 10, card_y, 330, 30)
        if idx % 2 == 0:
            pygame.draw.rect(screen, LIGHT_GRAY, card_rect)
        
        # 回合标签
        turn_label = font_small.render(f"T{turn + 1}:", True, PURPLE)
        screen.blit(turn_label, (card_history_x + 15, card_y + 5))
        
        # 技能信息
        skill_info = f"Skill {skill_idx} ({PlayerSkills[skill_idx][0]} dmg)"
        skill_label = font_small.render(skill_info, True, BLACK)
        screen.blit(skill_label, (card_history_x + 60, card_y + 5))

    # 控制动画进度
    frame_counter += 1
    if frame_counter >= animation_speed:  # 每秒执行一次
        frame_counter = 0
        
        # 如果有预期动作序列，则执行动作
        if current_turn < len(actions):
            action = actions[current_turn]
            if 0 <= action < len(PlayerSkills) and current_cd[action] == 0:
                # 记录已出的卡牌
                played_cards.append((current_turn, action))
                
                # 对当前目标Boss造成伤害
                if current_target < len(B):
                    damage_dealt = PlayerSkills[action][0]
                    B[current_target] = max(0, B[current_target] - damage_dealt)
                    current_cd[action] = PlayerSkills[action][1] + 1  # +1因为当前回合就开始冷却
            
            # 更新当前目标Boss（跳过已死亡的Boss）
            while current_target < len(B) and B[current_target] <= 0:
                current_target += 1
            
            current_turn += 1
        
        # 更新CD状态（每回合结束时减1）
        for i in range(len(current_cd)):
            if current_cd[i] > 0:
                current_cd[i] -= 1

    # 如果所有Boss被击败，显示胜利信息
    if all(hp <= 0 for hp in B):
        # 胜利背景
        victory_bg = pygame.Rect(200, 300, 800, 200)
        pygame.draw.rect(screen, GREEN, victory_bg)
        pygame.draw.rect(screen, DARK_GRAY, victory_bg, 5)
        
        victory_text = font_large.render("VICTORY!", True, WHITE)
        victory_rect = victory_text.get_rect(center=(600, 350))
        screen.blit(victory_text, victory_rect)
        
        defeat_text = font_medium.render("ALL BOSSES DEFEATED!", True, WHITE)
        defeat_rect = defeat_text.get_rect(center=(600, 390))
        screen.blit(defeat_text, defeat_rect)
        
        restart_text = font_small.render("Press SPACE to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(600, 430))
        screen.blit(restart_text, restart_rect)

    # 绘制操作提示
    hint_text = font_small.render("Press SPACE to restart simulation", True, DARK_GRAY)
    screen.blit(hint_text, (50, screen_height - 30))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# 退出 pygame
pygame.quit()
sys.exit()