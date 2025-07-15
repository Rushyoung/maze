import pygame
import sys
import json
import assets.BOSS.boss_fight as boss_fight
import os
import math

def boss_fight_simulation(initial_resources):
    """
    BOSS战斗模拟函数
    参数:
        initial_resources: 初始资源值
    返回:
        剩余资源值
    """
    # 保存原窗口状态
    original_screen = pygame.display.get_surface()
    original_caption = pygame.display.get_caption()[0] if original_screen else ""
    original_size = original_screen.get_size() if original_screen else None
    
    # 创建新的窗口
    screen_width = 1200
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("BOSS战斗模拟")

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

    # 定义字体 - 支持中文
    def load_font(font_path, size, bold=False):
        """加载字体，优先使用自定义字体文件，fallback到系统字体"""
        try:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
            else:
                # 如果字体文件不存在，尝试使用系统中文字体
                chinese_fonts = [
                    "Microsoft YaHei",  # 微软雅黑
                    "SimHei",           # 黑体
                    "SimSun",           # 宋体
                    "KaiTi",            # 楷体
                    "FangSong"          # 仿宋
                ]
                
                for font_name in chinese_fonts:
                    try:
                        return pygame.font.SysFont(font_name, size, bold=bold)
                    except:
                        continue
                
                # 如果都不行，使用默认字体
                return pygame.font.SysFont('Arial', size, bold=bold)
        except:
            return pygame.font.SysFont('Arial', size, bold=bold)

    # 字体文件路径（你可以把字体文件放在这些位置）
    font_paths = {
        'regular': 'assets/fonts/SourceHanSansCN-Regular.ttf',  # 思源黑体
        'bold': 'assets/fonts/SourceHanSansCN-Bold.ttf',       # 思源黑体粗体
        'microsoft': 'assets/fonts/msyh.ttf',                  # 微软雅黑
        'simhei': 'assets/fonts/simhei.ttf'                    # 黑体
    }

    # 加载字体
    font_large = load_font(font_paths.get('bold', ''), 32, bold=True)
    font_medium = load_font(font_paths.get('regular', ''), 24)
    font_small = load_font(font_paths.get('regular', ''), 18)
    font_resource = load_font(font_paths.get('bold', ''), 28, bold=True)

    # 使用算法求解Boss战
    try:
        solver = boss_fight.BossFightSolver("assets/maze/maze_15_15_3.json")
        min_turns, actions = solver.solve()

        # 从求解器获取Boss和技能数据
        B = solver.bosses.copy()  # Boss血量列表
        original_B = solver.bosses.copy()  # 保存原始血量用于显示
        PlayerSkills = solver.player_skills  # 玩家技能列表

        print(f"Boss数据: {B}")
        print(f"技能数据: {PlayerSkills}")
        print(f"最优解: {min_turns}回合, 动作序列: {actions}")
    except Exception as e:
        print(f"Boss战斗求解失败: {e}")
        # 如果求解失败，恢复原窗口并返回原始资源值
        if original_size and original_caption:
            pygame.display.set_mode(original_size)
            pygame.display.set_caption(original_caption)
        return initial_resources

    # 游戏状态变量
    current_turn = 0
    current_target = 0
    animation_speed = 60  # 每秒帧数，可以调整动画速度
    current_resources = initial_resources  # 当前资源值
    game_over = False
    victory = False
    
    # 伤害效果相关变量
    damage_effects = []  # 存储伤害效果 [(boss_index, damage_amount, start_time, duration)]
    damage_effect_duration = 90  # 伤害效果持续帧数（1.5秒）

    # 美化后的布局位置
    boss_start_y = 120
    boss_spacing = 80
    skill_start_y = 480
    skill_spacing = 60
    card_history_x = 800

    # 动态计算Boss和技能的显示位置
    boss_positions = [(80, boss_start_y + i * boss_spacing) for i in range(len(B))]
    skill_positions = [(50, skill_start_y + i * skill_spacing) for i in range(len(PlayerSkills))]

    # 初始化CD状态和卡牌历史
    current_cd = [0] * len(PlayerSkills)
    frame_counter = 0
    played_cards = []
    total_frame_counter = 0  # 用于计算总帧数

    # 主循环
    running = True
    clock = pygame.time.Clock()

    while running:
        total_frame_counter += 1  # 总帧计数器
        
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
                    played_cards = []
                    current_resources = initial_resources
                    game_over = False
                    victory = False
                    damage_effects = []  # 重置伤害效果
                    total_frame_counter = 0
                elif event.key == pygame.K_ESCAPE:
                    # ESC键退出
                    running = False

        # 清屏
        screen.fill(WHITE)
        
        # 绘制背景装饰
        pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, screen_width, 80))
        pygame.draw.rect(screen, DARK_GRAY, (0, 80, screen_width, 4))

        # 绘制标题 - 中文
        title_text = font_large.render("BOSS战斗模拟", True, BLACK)
        title_rect = title_text.get_rect(center=(screen_width//2, 40))
        screen.blit(title_text, title_rect)

        # 绘制资源值 (右上角) - 中文
        resource_bg = pygame.Rect(screen_width - 200, 10, 180, 60)
        # 根据资源值设置背景颜色
        if current_resources > 50:
            resource_bg_color = GREEN
        elif current_resources > 20:
            resource_bg_color = YELLOW
        else:
            resource_bg_color = RED
        
        pygame.draw.rect(screen, resource_bg_color, resource_bg)
        pygame.draw.rect(screen, BLACK, resource_bg, 3)
        
        # 资源值文字 - 中文
        resource_text = font_resource.render("资源", True, BLACK)
        resource_value_text = font_large.render(str(current_resources), True, BLACK)
        
        resource_text_rect = resource_text.get_rect(center=(screen_width - 110, 25))
        resource_value_rect = resource_value_text.get_rect(center=(screen_width - 110, 50))
        
        screen.blit(resource_text, resource_text_rect)
        screen.blit(resource_value_text, resource_value_rect)

        # 绘制Boss区域标题 - 中文
        boss_title = font_medium.render("敌人状态", True, DARK_GRAY)
        screen.blit(boss_title, (50, 90))

        # 绘制Boss血量条
        for i, hp in enumerate(B):
            if i < len(boss_positions):
                boss_y = boss_positions[i][1]
                boss_x = boss_positions[i][0]
                
                # Boss标签背景
                label_bg = pygame.Rect(boss_x - 70, boss_y + 5, 60, 30)
                pygame.draw.rect(screen, DARK_GRAY, label_bg)
                label_text = font_small.render(f"敌人{i+1}", True, WHITE)
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
                
                # 如果是当前目标，添加箭头指示 - 中文
                if i == current_target and hp > 0:
                    arrow_text = font_medium.render("← 目标", True, RED)
                    screen.blit(arrow_text, (boss_x + 360, boss_y + 10))

        # 绘制伤害效果
        active_damage_effects = []
        for boss_index, damage_amount, start_time, duration in damage_effects:
            elapsed_time = total_frame_counter - start_time
            if elapsed_time < duration:
                # 计算效果进度 (0 to 1)
                progress = elapsed_time / duration
                
                # 闪烁效果：使用正弦波产生闪烁
                blink_intensity = abs(math.sin(elapsed_time * 0.3))  # 调整闪烁速度
                
                # 透明度随时间减少
                alpha = int(255 * (1 - progress) * blink_intensity)
                alpha = max(0, min(255, alpha))
                
                if boss_index < len(boss_positions) and alpha > 0:
                    boss_y = boss_positions[boss_index][1]
                    boss_x = boss_positions[boss_index][0]
                    
                    # 计算被扣除的血条部分
                    if original_B[boss_index] > 0:
                        # 计算伤害前的血量条宽度（即当前血量+伤害量）
                        current_hp = max(0, B[boss_index])
                        before_damage_hp = min(original_B[boss_index], current_hp + damage_amount)
                        
                        # 计算血条位置
                        current_hp_ratio = current_hp / original_B[boss_index]
                        before_damage_ratio = before_damage_hp / original_B[boss_index]
                        
                        current_hp_width = int(350 * current_hp_ratio)
                        before_damage_width = int(350 * before_damage_ratio)
                        
                        # 被扣除的血条部分的位置和宽度
                        damage_start_x = boss_x + current_hp_width
                        damage_width = before_damage_width - current_hp_width
                        
                        if damage_width > 0:
                            # 创建半透明表面，只绘制被扣除的部分
                            damage_surface = pygame.Surface((damage_width, 40), pygame.SRCALPHA)
                            
                            # 被扣除血条的颜色（红色半透明）
                            damage_color = (255, 0, 0, alpha)
                            pygame.draw.rect(damage_surface, damage_color, (0, 0, damage_width, 40))
                            
                            # 绘制到主屏幕的正确位置
                            screen.blit(damage_surface, (damage_start_x, boss_y))
                            
                            # 显示伤害数字 - 在被扣除血条的上方
                            if progress < 0.5:  # 只在前半段显示伤害数字
                                damage_text_x = damage_start_x + damage_width // 2  # 被扣除血条的中心位置
                                damage_text_y = boss_y - 15  # 血条上方15像素
                                
                                damage_text = font_medium.render(f"-{damage_amount}", True, (255, 255, 255))
                                damage_text_rect = damage_text.get_rect(center=(damage_text_x, damage_text_y))
                                
                                # 添加阴影效果
                                shadow_text = font_medium.render(f"-{damage_amount}", True, (0, 0, 0))
                                shadow_rect = shadow_text.get_rect(center=(damage_text_x + 2, damage_text_y + 2))
                                screen.blit(shadow_text, shadow_rect)
                                screen.blit(damage_text, damage_text_rect)
                
                active_damage_effects.append((boss_index, damage_amount, start_time, duration))
        
        # 更新伤害效果列表
        damage_effects = active_damage_effects

        # 绘制技能区域标题 - 中文
        skill_title = font_medium.render("玩家技能", True, DARK_GRAY)
        screen.blit(skill_title, (50, skill_start_y - 30))

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
                
                # 技能信息 - 中文
                skill_text = f"伤害: {damage}  |  冷却: {cd}"
                text = font_medium.render(skill_text, True, BLACK)
                screen.blit(text, (skill_x + 50, skill_y + 8))
                
                # CD状态 - 中文
                if current_cd[i] > 0:
                    cd_text = f"冷却中: {current_cd[i]} 回合"
                    cd_render = font_small.render(cd_text, True, RED)
                    screen.blit(cd_render, (skill_x + 50, skill_y + 28))
                else:
                    ready_text = "可以使用"
                    ready_render = font_small.render(ready_text, True, GREEN)
                    screen.blit(ready_render, (skill_x + 50, skill_y + 28))

        # 绘制游戏状态信息区域
        info_bg = pygame.Rect(50, 420, 700, 40)
        pygame.draw.rect(screen, LIGHT_GRAY, info_bg)
        pygame.draw.rect(screen, DARK_GRAY, info_bg, 2)

        # 绘制当前回合和剩余回合 - 中文
        turn_text = f"回合: {current_turn + 1} / {len(actions)}"
        turn_render = font_medium.render(turn_text, True, BLACK)
        screen.blit(turn_render, (60, 425))
        
        # 绘制当前使用的技能 - 中文
        if current_turn < len(actions):
            current_skill = actions[current_turn]
            skill_text = f"使用技能: {current_skill} (伤害: {PlayerSkills[current_skill][0]})"
            skill_render = font_small.render(skill_text, True, BLUE)
            screen.blit(skill_render, (350, 425))

        # 绘制已出卡牌历史区域
        card_bg = pygame.Rect(card_history_x, 100, 350, screen_height - 150)
        pygame.draw.rect(screen, WHITE, card_bg)
        pygame.draw.rect(screen, DARK_GRAY, card_bg, 3)
        
        # 卡牌历史标题 - 中文
        history_title = font_medium.render("已使用技能", True, DARK_GRAY)
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
            
            # 回合标签 - 中文
            turn_label = font_small.render(f"第{turn + 1}回合:", True, PURPLE)
            screen.blit(turn_label, (card_history_x + 15, card_y + 5))
            
            # 技能信息 - 中文
            skill_info = f"技能{skill_idx} ({PlayerSkills[skill_idx][0]}伤害)"
            skill_label = font_small.render(skill_info, True, BLACK)
            screen.blit(skill_label, (card_history_x + 90, card_y + 5))

        # 检查游戏结束条件
        if not game_over and not victory:
            # 检查是否所有Boss被击败
            if all(hp <= 0 for hp in B):
                victory = True
            # 检查是否资源耗尽
            elif current_resources <= 0:
                game_over = True

        # 控制动画进度
        if not game_over and not victory:
            frame_counter += 1
            if frame_counter >= animation_speed:
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
                            
                            # 添加伤害效果
                            damage_effects.append((current_target, damage_dealt, total_frame_counter, damage_effect_duration))
                            
                            B[current_target] = max(0, B[current_target] - damage_dealt)
                            current_cd[action] = PlayerSkills[action][1] + 1
                        
                        # 每回合消耗1点资源
                        current_resources = max(0, current_resources - 1)
                
                # 更新当前目标Boss（跳过已死亡的Boss）
                while current_target < len(B) and B[current_target] <= 0:
                    current_target += 1
                
                current_turn += 1
                
                # 更新CD状态（每回合结束时减1）
                for i in range(len(current_cd)):
                    if current_cd[i] > 0:
                        current_cd[i] -= 1

        # 显示游戏结束界面
        if victory:
            # 简化的胜利提示 - 在屏幕底部显示
            victory_bg = pygame.Rect(50, screen_height - 100, screen_width - 100, 80)
            pygame.draw.rect(screen, GREEN, victory_bg)
            pygame.draw.rect(screen, DARK_GRAY, victory_bg, 3)
            
            # 左侧显示胜利信息
            victory_text = font_medium.render("胜利！所有敌人已被击败", True, WHITE)
            screen.blit(victory_text, (70, screen_height - 85))
            
            # 右侧显示剩余资源
            resource_info = font_medium.render(f"剩余资源: {current_resources}", True, WHITE)
            resource_rect = resource_info.get_rect()
            screen.blit(resource_info, (screen_width - 250, screen_height - 85))
            
            # 操作提示
            restart_text = font_small.render("按空格重新开始，ESC退出", True, WHITE)
            restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height - 50))
            screen.blit(restart_text, restart_rect)

        elif game_over:
            # 简化的失败提示 - 在屏幕底部显示
            game_over_bg = pygame.Rect(50, screen_height - 100, screen_width - 100, 80)
            pygame.draw.rect(screen, RED, game_over_bg)
            pygame.draw.rect(screen, DARK_GRAY, game_over_bg, 3)
            
            # 左侧显示失败信息
            game_over_text = font_medium.render("游戏结束！资源耗尽", True, WHITE)
            screen.blit(game_over_text, (70, screen_height - 85))
            
            # 右侧显示最终资源
            resource_info = font_medium.render(f"最终资源: {current_resources}", True, WHITE)
            screen.blit(resource_info, (screen_width - 250, screen_height - 85))
            
            # 操作提示
            restart_text = font_small.render("按空格重新开始，ESC退出", True, WHITE)
            restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height - 50))
            screen.blit(restart_text, restart_rect)

        # 绘制操作提示 - 只在游戏进行中显示
        elif not game_over and not victory:
            hint_text = font_small.render("按空格重新开始，ESC退出", True, DARK_GRAY)
            screen.blit(hint_text, (50, screen_height - 30))

        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    # 恢复原窗口状态
    if original_size and original_caption:
        pygame.display.set_mode(original_size)
        pygame.display.set_caption(original_caption)
        print(f"恢复原窗口: {original_size}, 标题: {original_caption}")
    
    # 返回剩余资源值
    return current_resources


# 使用示例
if __name__ == "__main__":
    pygame.init()
    initial_resources = 100  # 初始资源值
    remaining_resources = boss_fight_simulation(initial_resources)
    print(f"战斗结束，剩余资源: {remaining_resources}")
    pygame.quit()