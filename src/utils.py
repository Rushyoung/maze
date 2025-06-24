import pygame
from src.config import CELL_SIZE

def image(path: str, size: tuple[int, int] = None) -> pygame.Surface:
    """
    Load an image from the given path and optionally resize it.

    :param path: Path to the image file.
    :param size: Optional tuple (width, height) to resize the image.
    :return: Loaded and optionally resized pygame Surface.
    """
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    return image


class playable:
    def __init__(self):
        self.route = [] # 记录未来的移动路径，量子化移动
        self.route.append((1, 1))
        self.dx = 0
        self.dy = 0

    def handle(self, maze, event: pygame.event.Event):
        """
        Handle movement events for the playable character.
        
        :param event: The pygame event to handle.
        """
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    self.route.append(self.route[-1])
                    self.route[-1] = (self.route[-1][0], self.route[-1][1] - 1)
                case pygame.K_DOWN:
                    self.route.append(self.route[-1])
                    self.route[-1] = (self.route[-1][0], self.route[-1][1] + 1)
                case pygame.K_LEFT:
                    self.route.append(self.route[-1])
                    self.route[-1] = (self.route[-1][0] - 1, self.route[-1][1])
                case pygame.K_RIGHT:
                    self.route.append(self.route[-1])
                    self.route[-1] = (self.route[-1][0] + 1, self.route[-1][1])
        if maze[self.route[-1]] == 1:
            self.route.pop()
        print(f"Current route: {self.route}")
        
    def move(self):
        """
        Move the playable character to the next position in the route.
        If the route is empty, do nothing.
        """
        if len(self.route) <= 1:
            return 0, 0
        distance = len(self.route) - 1
        speed = distance / 30
        speed = max(1/30, speed)
        dx = (self.route[1][0] - self.route[0][0]) * speed
        dy = (self.route[1][1] - self.route[0][1]) * speed
        if abs(dx) > abs(self.route[1][0] - self.dx) or abs(dy) > abs(self.route[1][1] - self.dy):
            self.route.pop(0)
            if abs(dx) > abs(self.route[0][0] - self.dx):
                dx = self.route[0][0] - self.dx
            if abs(dy) > abs(self.route[0][1] - self.dy):
                dy = self.route[0][1] - self.dy
        else:
            self.dx += dx
            self.dy += dy
        return dx * CELL_SIZE, dy * CELL_SIZE
        
    def position(self) -> tuple[int, int]:
        """
        Get the current position of the playable character.
        :return: Tuple (x, y) representing the current position.
        """
        return self.route[0]