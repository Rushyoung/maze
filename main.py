import pygame
import random

from src import map
from src import config
from src import utils
from src import anima
from src import passwd

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.MAZE_SIZE * config.CELL_SIZE + config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
    pygame.display.set_caption("Amaze")

    maze:map.map = map.recursive(config.MAZE_SIZE)
    maze[config.MAZE_SIZE - 1, config.MAZE_SIZE - 2] = 'E'
    
    # 创建背景Surface（只绘制一次静态元素）
    background = pygame.Surface(screen.get_size())
    background.fill((235, 235, 235))  # 填充黑色背景

    sidebar = utils.sidebar()
    locker  = passwd.cracker("assets/pwd/pwd_000.json")
    manager = anima.manager()
    # brick
    for x in range(config.MAZE_SIZE):
        for y in range(config.MAZE_SIZE):
            path = "assets/images/brick.png"
            if maze[x, y] != 1:
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
    fire = anima.animation(anima.sprite("assets/images/fire/fire.png"))
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

        if fps % 10 == 0:
            player.control(maze, keyboard)
        player.move()
        fire.moveTo(*player.position())

        if(player.route[0] in coins):
            manager.remove(f"coin_{coins.remove(player.route[0])}")
            sidebar.score.add()

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