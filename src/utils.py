import pygame
from src.config import CELL_SIZE
import collections

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

    def control(self, maze, keys):
        """
        Handle movement events for the playable character.
        
        :param event: The pygame event to handle.
        """
        if keys[pygame.K_UP]:
                    self.route.append(self.route[-1])
                    self.route[-1] = (self.route[-1][0], self.route[-1][1] - 1)
        elif keys[pygame.K_DOWN]:
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0], self.route[-1][1] + 1)
        elif keys[pygame.K_LEFT]:
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0] - 1, self.route[-1][1])
        elif keys[pygame.K_RIGHT]:
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0] + 1, self.route[-1][1])
        if maze[self.route[-1]] == 1:
            self.route.pop()
        
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
            self.dx = 0
            self.dy = 0
        else:
            self.dx += dx
            self.dy += dy
        
    def position(self) -> tuple[int, int]:
        """
        Get the current position of the playable character.
        :return: Tuple (x, y) representing the current position.
        """
        return (self.route[0][0] + self.dx) * CELL_SIZE, (self.route[0][1] + self.dy) * CELL_SIZE
    

class key:
    def __init__(self):
        self.inner_data = collections.defaultdict(bool)

    def update(self, event: pygame.event.Event):
        """
        Update the key state based on the event.
        
        :param event: The pygame event to update the key state.
        """
        if event.type == pygame.KEYDOWN:
            self.inner_data[event.key] = True
        elif event.type == pygame.KEYUP:
            self.inner_data[event.key] = False

    def __getitem__(self, key):
        """
        Get the state of a specific key.
        
        :param key: The key to check.
        :return: True if the key is pressed, False otherwise.
        """
        return self.inner_data.get(key, False)