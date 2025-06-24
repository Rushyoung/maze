import pygame
import random

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
    coin_sprite = anima.sprite("assets/images/coin/coin.png")
    for idx, pos in enumerate(coins):
        x, y = pos
        coin = anima.animation(coin_sprite)
        coin.speed(1/16)
        coin.loop = True
        coin.x = x * config.CELL_SIZE + 4
        coin.y = y * config.CELL_SIZE + 4
        coin.current_frame = random.randint(0, coin.frame_count - 1)
        manager.add(f"coin_{idx}", coin)
        

    clock = pygame.time.Clock()
    player = utils.playable()
    keyboard = utils.key()

    fps = 0
    while True:
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
            idx = coins.index(player.route[0])
            manager.remove(f"coin_{idx}")
            coins[idx] = None  # 移除已收集的金币

        screen.blit(background, (0, 0))
        manager.update(screen)
        
        # 3. 最后刷新显示
        pygame.display.flip()
        
        clock.tick(60)  # 稳定60 FPS
        fps += 1
        if fps % 60 == 0:
            fps = 0

main()