import pygame

from src import map
from src import config

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.MAZE_SIZE * config.CELL_SIZE + config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
    pygame.display.set_caption("Simple Pygame Window")

    maze = map.generate(config.MAZE_SIZE)

    # 将 assets/images/brick.png 按照maze的结构绘制到屏幕上
    # brick.png 是一个 16x16 的砖块图像
    # 砖块在 maze 中的值为 True
    for i in range(config.MAZE_SIZE):
        for j in range(config.MAZE_SIZE):
            if maze(i, j):
                brick_image = pygame.image.load("assets/images/brick.png")
                brick_image = pygame.transform.scale(brick_image, (config.CELL_SIZE, config.CELL_SIZE))
                screen.blit(brick_image, (j * config.CELL_SIZE, i * config.CELL_SIZE))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # 这里可以添加更多的游戏逻辑

        pygame.display.flip()

    pygame.quit()

main()