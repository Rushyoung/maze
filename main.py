import pygame
import math

from src import map
from src import config
from src import utils
from src import anima

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.MAZE_SIZE * config.CELL_SIZE + config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
    pygame.display.set_caption("Amaze")

    maze = map.generate(config.MAZE_SIZE)
    maze[config.MAZE_SIZE - 1, config.MAZE_SIZE - 2] = 0
    
    # 创建背景Surface（只绘制一次静态元素）
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))  # 填充黑色背景
    
    for x in range(config.MAZE_SIZE):
        for y in range(config.MAZE_SIZE):
            if maze[x, y] == 1:
                brick_image = utils.image("assets/images/brick.png", (config.CELL_SIZE, config.CELL_SIZE))
                background.blit(brick_image, (x * config.CELL_SIZE, y * config.CELL_SIZE))
    
    screen.blit(background, (0, 0))
    pygame.display.flip()

    manager = anima.manager()
    
    fire = anima.animation(anima.load("assets/images/fire", range(7)))
    fire.speed(1/24)
    fire.loop = True
    fire.x = config.CELL_SIZE
    fire.y = config.CELL_SIZE
    manager.add("fire", fire)

    coins = maze.random(config.COIN, config.COIN_COUNT)
    for idx, pos in enumerate(coins):
        x, y = pos
        coin = anima.animation(anima.load("assets/images/coin", range(6)))
        coin.speed(1/16)
        coin.loop = True
        coin.x = x * config.CELL_SIZE + 4
        coin.y = y * config.CELL_SIZE + 4
        manager.add(f"coin_{idx}", coin)
        

    clock = pygame.time.Clock()
    control = utils.playable()

    while True:
        for event in pygame.event.get():
            match(event.type):
                case pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    control.handle(maze, event)
                case pygame.QUIT:
                    return
        fire.move(*control.move())

        screen.blit(background, (0, 0))
        manager.update(screen)
        
        # 3. 最后刷新显示
        pygame.display.flip()
        
        clock.tick(60)  # 稳定60 FPS

main()