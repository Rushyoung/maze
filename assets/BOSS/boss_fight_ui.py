import pygame
import sys

# 初始化 pygame
pygame.init()

# 设置窗口大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("BOSS FIGHT")

# 定义颜色
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 定义字体
font = pygame.font.SysFont(None, 36)

# Boss 和 Skill 的初始状态
B = [11, 7, 18]
PlayerSkills = [[10, 1], [11, 4], [11, 5], [3, 0], [4, 4]]
actions = [2, 0, 1, 0]

# 当前回合和当前目标 Boss
current_turn = 0
current_target = 0

# Boss 和 Skill 的显示位置
boss_positions = [(200, 50), (200, 150), (200, 250)]
skill_positions = [(100, 400 + i * 50) for i in range(len(PlayerSkills))]

# 初始化 CD 状态
current_cd = [0] * len(PlayerSkills)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 清屏
    screen.fill(WHITE)

    # 绘制 Boss 血量条
    for i, hp in enumerate(B):
        color = RED if i == 0 else YELLOW if i == 1 else BLUE
        text = font.render(f"BOSS{i+1}:", True, BLACK)
        screen.blit(text, (boss_positions[i][0] - 100, boss_positions[i][1] + 10))
        pygame.draw.rect(screen, color, (boss_positions[i][0], boss_positions[i][1], 200, 40))
        pygame.draw.rect(screen, BLACK, (boss_positions[i][0], boss_positions[i][1], 200, 40), 2)
        text = font.render(f"{hp}/{hp}", True, BLACK)
        screen.blit(text, (boss_positions[i][0] + 80, boss_positions[i][1] + 10))

    # 绘制 Skill 状态
    for i, (damage, cd) in enumerate(PlayerSkills):
        pygame.draw.rect(screen, BLACK, (skill_positions[i][0], skill_positions[i][1], 400, 40), 2)
        text = font.render(f"Skill{i}    DAMAGE:{damage}    CD:{cd}", True, BLACK)
        screen.blit(text, (skill_positions[i][0] + 10, skill_positions[i][1] + 10))
        if current_cd[i] > 0:
            cd_text = font.render(f"LEFT CD:{current_cd[i]}", True, RED)
            screen.blit(cd_text, (skill_positions[i][0] + 10, skill_positions[i][1] + 30))

    # 绘制当前回合数
    turn_text = font.render(f"CURREENT ROUND {current_turn}", True, BLACK)
    screen.blit(turn_text, (500, 500))

    # 如果有预期动作序列，则执行动作
    if current_turn < len(actions):
        action = actions[current_turn]
        if action != -1 and current_cd[action] == 0:
            B[current_target] = max(0, B[current_target] - PlayerSkills[action][0])
            current_cd[action] = PlayerSkills[action][1]
        
        # 更新当前目标 Boss
        while current_target < len(B) and B[current_target] <= 0:
            current_target += 1

        current_turn += 1

    # 更新 CD 状态
    for i in range(len(current_cd)):
        if current_cd[i] > 0:
            current_cd[i] -= 1

    # 如果所有 Boss 被击败，显示胜利信息
    if all(hp <= 0 for hp in B):
        victory_text = font.render("YOU WIN!!!", True, GREEN)
        screen.blit(victory_text, (350, 100))

    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    pygame.time.Clock().tick(1)  # 每秒 1 帧，便于观察每回合的变化

# 退出 pygame
pygame.quit()
sys.exit()