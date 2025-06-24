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
    
    # 创建背景Surface（只绘制一次静态元素）
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))  # 填充黑色背景
    
    for i in range(config.MAZE_SIZE):
        for j in range(config.MAZE_SIZE):
            if maze[i, j]:
                brick_image = utils.image("assets/images/brick.png", (config.CELL_SIZE, config.CELL_SIZE))
                background.blit(brick_image, (j * config.CELL_SIZE, i * config.CELL_SIZE))
    
    screen.blit(background, (0, 0))
    pygame.display.flip()

    manager = anima.manager()
    
    fire = anima.animation(anima.load("assets/images/fire", range(7)))
    fire.speed(1/24)
    fire.loop = True
    manager.add("fire", fire)

    clock = pygame.time.Clock()
    control = utils.moveable(config.CELL_SIZE, config.CELL_SIZE)
    x = y = 1
    fire.x, fire.y = x, y

    while True:
        for event in pygame.event.get():
            match(event.type):
                case pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                case pygame.QUIT:
                    return
        control.handle(event)
        fire.move(*control.move())

        screen.blit(background, (0, 0))
        manager.update(screen)
        
        # 3. 最后刷新显示
        pygame.display.flip()
        
        clock.tick(60)  # 稳定60 FPS

main()