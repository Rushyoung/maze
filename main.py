import pygame

from src import map
from src import config
from src import utils
from src import anima

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.MAZE_SIZE * config.CELL_SIZE + config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
    pygame.display.set_caption("Amaze")

    maze = map.generate(config.MAZE_SIZE)

    # 将 assets/images/brick.png 按照maze的结构绘制到屏幕上
    # brick.png 是一个 16x16 的砖块图像
    # 砖块在 maze 中的值为 True
    for i in range(config.MAZE_SIZE):
        for j in range(config.MAZE_SIZE):
            if maze[i, j]:
                brick_image = utils.image("assets/images/brick.png", (config.CELL_SIZE, config.CELL_SIZE))
                screen.blit(brick_image, (j * config.CELL_SIZE, i * config.CELL_SIZE))
    pygame.display.flip()

    manager = anima.manager()
    
    fire = anima.animation(anima.load("assets/images/fire", range(4)))
    fire.speed(1/30)
    fire.loop = True
    manager.add("fire", fire)

    count = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        pygame.display.flip()
        manager.update(screen)

        # 稳定60 FPS
        pygame.time.Clock().tick(60)

main()