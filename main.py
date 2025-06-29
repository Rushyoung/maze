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

    maze:map.map = map.recursive(config.MAZE_SIZE)
    maze[1, 1] = 'S'  # 设置起点
    maze[config.MAZE_SIZE - 1, config.MAZE_SIZE - 2] = 'E'
    
    # 创建背景Surface（只绘制一次静态元素）
    background = pygame.Surface(screen.get_size())
    background.fill((235, 235, 235))  # 填充黑色背景

    path_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    sidebar = utils.sidebar()
    locker  = passwd.cracker("assets/pwd/pwd_010.json")
    manager = anima.manager()
    # brick
    for x in range(config.MAZE_SIZE):
        for y in range(config.MAZE_SIZE):
            path = "assets/images/brick.png"
            if maze[x, y] != config.WALL:
                path = "assets/images/background.png"
            brick_image = utils.image(path, (config.CELL_SIZE, config.CELL_SIZE))
            background.blit(brick_image, (x * config.CELL_SIZE, y * config.CELL_SIZE))

    # locker 
    ender = map.elements()
    ender.append((config.MAZE_SIZE - 1, config.MAZE_SIZE - 2))
    locker_image = anima.animation(anima.sprite("assets/images/key.png"))
    locker_image.set(
        (config.MAZE_SIZE - 1) * config.CELL_SIZE,
        (config.MAZE_SIZE - 2) * config.CELL_SIZE,
    )
    manager.add("locker", locker_image)

    # fire(main)
    fire = anima.animation(anima.sprite("assets/images/nailong.png"))
    fire.set(
        config.CELL_SIZE,
        config.CELL_SIZE,
    )
    manager.add("fire", fire)

    # coin
    coins = maze.random(config.COIN, config.COIN_COUNT)
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
    clues = maze.random(config.CLUE, locker.clue_amount())
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
    traps = maze.random(config.TRAP, config.TRAP_COUNT)
    trap_sprite = anima.sprite("assets/images/man/man.png")
    for idx, (x, y) in enumerate(traps):
        trap = anima.animation(trap_sprite)
        trap.set(
            x * config.CELL_SIZE,
            y * config.CELL_SIZE,
            1
        )
        manager.add(f"trap_{idx}", trap)

    # path
    path_finder = p.pathFind(maze)
    rewards, path_result = path_finder.find()
    # ?
    path_overlay.fill((0, 0, 0, 0))  # 清空路径覆盖层
    if isinstance(path_result, list):
        for i in range(len(path_result) - 1):
            start = path_result[i]
            end = path_result[i + 1]
            pygame.draw.line(path_overlay, config.COLOR_DP_PATH, 
                             (start[1] * config.CELL_SIZE + config.CELL_SIZE // 2, 
                              start[0] * config.CELL_SIZE + config.CELL_SIZE // 2),
                             (end[1] * config.CELL_SIZE + config.CELL_SIZE // 2, 
                              end[0] * config.CELL_SIZE + config.CELL_SIZE // 2), 3)

    clock = pygame.time.Clock()
    player = utils.playable()
    keyboard = utils.key()

    fps = 0
    while(fps := fps + 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keyboard[pygame.K_ESCAPE]:
                pygame.quit()
                return
            keyboard.update(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    # 检查路径查找是否成功返回了一个列表
                    if isinstance(path_result, list):
                        player.follow_path(path_result)
        
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
            sidebar.score.sub(2)

        if(player.route[0] in clues):
            manager.remove(f"cuel_{clues.remove(player.route[0])}")
            sidebar.add_tip(locker.clue_get())

        if(player.route[0] in ender):
            print("in locker")
            manager.remove("locker")
            ender.remove(player.route[0])
            sidebar.add_tip(locker.crack())

        screen.blit(background, (0, 0))
        screen.blit(sidebar.bar, (config.MAZE_SIZE * config.CELL_SIZE, 0))
        manager.update(screen)
        pygame.display.flip()
        clock.tick(60)  # 稳定60 FPS

main()