import pygame
import random

from src import map
from src import config
from src import utils
from src import anima
from src import passwd
from src import path as p

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.MAZE_SIZE * config.CELL_SIZE + config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
    pygame.display.set_caption("Amaze")

    # 加载配置
    LOAD_FROM_FILE = True


    maze: map.map = None
    locker = passwd.cracker("assets/pwd/pwd_010.json")

    if LOAD_FROM_FILE:
        
        print("Loading map from assets/maze/maze.json...")
        config.MAZE_SIZE = 15
        maze = map.map.load_from_json("assets/maze/maze_7_7.json")
        if maze is None:
            print("Failed to load map. Exiting.")
            return
    else:
        print("Generating new map...")
        maze = map.recursive(config.MAZE_SIZE)
        maze[1, 1] = 'S'
        maze[config.MAZE_SIZE - 1, config.MAZE_SIZE - 2] = 'E'
        
        # 在地图数据上随机放置元素
        maze.random(config.COIN, config.COIN_COUNT)
        maze.random(config.CLUE, locker.clue_amount())
        maze.random(config.TRAP, config.TRAP_COUNT)
        maze.random(config.BOSS, config.BOSS_COUNT) # <--- 新增：放置BOSS
        
        # 保存新生成的地图，以便下次可以直接加载
        print("Saving newly generated map to assets/maze/maze.json...")
        maze.save_to_json("assets/maze/maze.json")

    
    # 创建背景Surface（只绘制一次静态元素）
    background = pygame.Surface(screen.get_size())
    background.fill((235, 235, 235))  # 填充背景

    path_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    sidebar = utils.sidebar()
    manager = anima.manager()
    # brick
    for x in range(config.MAZE_SIZE):
        for y in range(config.MAZE_SIZE):
            path = "assets/images/brick.png"
            if maze[x, y] != config.WALL or maze[x,y] ==config.EXIT:
                path = "assets/images/background.png"
            brick_image = utils.image(path, (config.CELL_SIZE, config.CELL_SIZE))
            background.blit(brick_image, (x * config.CELL_SIZE, y * config.CELL_SIZE))

    # locker
    locker_positions = maze.get_positions_of(config.LOCKER)
    lockers = map.elements()
    for pos in locker_positions:
        lockers.append(pos)
    if locker_positions:
        locker_image = anima.animation(anima.sprite("assets/images/key.png"))
        locker_image.set(
            locker_positions[0][0] * config.CELL_SIZE,
            locker_positions[0][1] * config.CELL_SIZE,
        )
        manager.add("locker", locker_image)

    # exit
    exit_pos = maze.get_positions_of(config.EXIT)
    exits = map.elements()
    for pos in exit_pos:
        exits.append(pos)

    # fire(main)
    fire = anima.animation(anima.sprite("assets/images/nailong.png"))
    fire.set(
        config.CELL_SIZE,
        config.CELL_SIZE,
    )
    manager.add("fire", fire)


    # coin
    coin_positions = maze.get_positions_of(config.COIN)
    coins = map.elements()
    for pos in coin_positions:
        coins.append(pos)
    coin_sprite = anima.sprite("assets/images/coin/coin.png")
    for idx, (x, y) in enumerate(coins):
        coin = anima.animation(coin_sprite)
        coin.set(
            x * config.CELL_SIZE + 4,
            y * config.CELL_SIZE + 4,
        )
        coin.current_frame = random.randint(0, coin.frame_count - 1)
        manager.add(f"coin_{idx}", coin)

    # clue
    clue_positions = maze.get_positions_of(config.CLUE)
    clues = map.elements()
    for pos in clue_positions:
        clues.append(pos)
    clue_sprite = anima.sprite("assets/images/cuel.png")
    for idx, (x, y) in enumerate(clues):
        clue = anima.animation(clue_sprite)
        clue.set(
            x * config.CELL_SIZE,
            y * config.CELL_SIZE,
            1
        )
        manager.add(f"cuel_{idx}", clue)

    # trap
    trap_positions = maze.get_positions_of(config.TRAP)
    traps = map.elements()
    for pos in trap_positions:
        traps.append(pos)
    trap_sprite = anima.sprite("assets/images/man/man.png")
    for idx, (x, y) in enumerate(traps):
        trap = anima.animation(trap_sprite)
        trap.set(
            x * config.CELL_SIZE,
            y * config.CELL_SIZE,
            1
        )
        manager.add(f"trap_{idx}", trap)

    # boss
    boss_positions = maze.get_positions_of(config.BOSS)
    bosses = map.elements()
    for pos in boss_positions:
        bosses.append(pos)
    boss_sprite = anima.sprite("assets/images/boss/boss.png") 
    for idx, (x, y) in enumerate(bosses):
        boss = anima.animation(boss_sprite)
        boss.set(
            x * config.CELL_SIZE,
            y * config.CELL_SIZE,
            1
        )
        manager.add(f"boss_{idx}", boss)

    # path
    path_finder = p.pathFind(maze)
    rewards, path_result = path_finder.find()
    print(f"Path found, rewards: {rewards}")
    
    # --- 路径绘制逻辑 ---
    path_overlay.fill((0, 0, 0, 0))  # 确保路径覆盖层是完全透明的
    if isinstance(path_result, list) and path_result: # 检查路径是否是一个非空列表
        for i in range(len(path_result) - 1):
            # 为了匹配背景的错误绘制方式，我们也错误地使用坐标
            # 将 (行, 列) 直接当作 (x, y)
            start_pos = (path_result[i][0] * config.CELL_SIZE + config.CELL_SIZE // 2, 
                         path_result[i][1] * config.CELL_SIZE + config.CELL_SIZE // 2)
            end_pos = (path_result[i+1][0] * config.CELL_SIZE + config.CELL_SIZE // 2, 
                       path_result[i+1][1] * config.CELL_SIZE + config.CELL_SIZE // 2)
            
            # 使用config中定义的颜色绘制路径线段
            pygame.draw.line(path_overlay, config.COLOR_DP_PATH, start_pos, end_pos, 3)

    clock = pygame.time.Clock()
    if LOAD_FROM_FILE:
        player = utils.playable(maze.get_positions_of(config.START)[0])
    else:
        player = utils.playable()
    keyboard = utils.key()

    auto_path_started = False  # 添加一个标志位，确保自动寻路只执行一次

    fps = 0
    while(fps := fps + 1):
        # 在游戏主循环中检查是否超过1秒并且自动寻路尚未开始
        if not auto_path_started and pygame.time.get_ticks() > 1000:
            # 检查路径查找是否成功返回了一个列表
            if isinstance(path_result, list):
                player.follow_path(path_result)
            auto_path_started = True  # 更新标志位，防止重复执行

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keyboard[pygame.K_ESCAPE]:
                pygame.quit()
                return
            keyboard.update(event)
        
        # if fps % 10 == 0:
        #     player.control(maze, keyboard)
        

        player.move()
        fire.moveTo(*player.position())

        if(player.route[0] in coins):
            manager.remove(f"coin_{coins.remove(player.route[0])}")
            sidebar.score.add()

        if(player.route[0] in traps):
            trap = traps.remove(player.route[0])
            manager.remove(f"trap_{trap}")
            sidebar.score.add(config.VALUE_MAP[config.TRAP])

        if(player.route[0] in clues):
            manager.remove(f"cuel_{clues.remove(player.route[0])}")
            sidebar.add_tip(locker.clue_get())

        if(player.route[0] in bosses):
            manager.remove(f"boss_{bosses.remove(player.route[0])}")
            # 您可以在这里添加击败boss后的其他效果，比如加分
            print("Boss defeated!")

        if(player.route[0] in lockers):
            print("in locker")
            if "locker" in manager.animations:
                manager.remove("locker")
            lockers.remove(player.route[0])
            sidebar.add_tip(locker.crack())
        
        if(player.route[0] in exits):
            # 在这里添加游戏结束逻辑
            print("Congratulations! You've reached the exit!")
            # 可以选择退出游戏或显示胜利画面
            

        screen.blit(background, (0, 0))
        screen.blit(path_overlay, (0, 0)) # 在背景之上，精灵之下，绘制路径
        screen.blit(sidebar.bar, (config.MAZE_SIZE * config.CELL_SIZE, 0))
        manager.update(screen)
        pygame.display.flip()
        clock.tick(60)  # 稳定60 FPS

main()