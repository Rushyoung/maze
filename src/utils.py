import pygame
import src.config as config
import collections

def RGB(color: str) -> tuple[int, int, int]:
    """
    Convert a hex color string to an RGB tuple.
    :param color: Hex color string (e.g., "99d9ea").
    :return: Tuple (R, G, B) representing the color.
    """
    assert isinstance(color, str), "Color must be a string"
    assert len(color) == 6, "Color must be a 6-digit hex string"
    assert all(c in "0123456789abcdefABCDEF" for c in color), "Color must be a valid hex string"
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

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
    def __init__(self, start_pos: tuple[int, int] = (1, 1)):
        self.route = [] # 记录未来的移动路径，量子化移动
        self.route.append(start_pos)
        self.dx = 0
        self.dy = 0

    def control(self, maze, keys):
        """
        Handle movement events for the playable character.
        
        :param event: The pygame event to handle.
        """
        if keys[pygame.K_UP]:
            self.go('up')
        elif keys[pygame.K_DOWN]:
            self.go('down')
        elif keys[pygame.K_LEFT]:
            self.go('left')
        elif keys[pygame.K_RIGHT]:
            self.go('right')
        if maze[self.route[-1]] == 1:
            self.route.pop()
    
    def go(self, flag: str):
        assert flag in ['up', 'down', 'left', 'right'], "Invalid direction"
        if flag == 'up':
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0], self.route[-1][1] - 1)
        elif flag == 'down':
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0], self.route[-1][1] + 1)
        elif flag == 'left':
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0] - 1, self.route[-1][1])
        elif flag == 'right':
            self.route.append(self.route[-1])
            self.route[-1] = (self.route[-1][0] + 1, self.route[-1][1])

    def follow_path(self, path: list[tuple[int, int]]):
        """
        Sets a new path for the player to follow automatically.
        Any existing queued moves are cleared. The new path is appended
        to the player's current grid position.

        :param path: A list of (x, y) grid coordinates for the player to visit in order.
        """
        if not path:
            return
        self.route = self.route[1:]  # Clear future moves, keep current position
        self.route.extend(path)
        self.dx, self.dy = 0, 0  # Reset animation interpolation

    def move(self):
        """
        Move the playable character to the next position in the route.
        If the route is empty, do nothing.
        """
        if len(self.route) <= 1:
            return 0, 0
        distance = len(self.route) - 1
        # speed = distance / 20
        # speed = max(1/20, speed)
        speed = 1 / 10
        dx = (self.route[1][0] - self.route[0][0]) * speed
        dy = (self.route[1][1] - self.route[0][1]) * speed
        if abs(dx) > abs(1 - abs(self.dx)) or abs(dy) > abs(1 - abs(self.dy)):
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
        return (self.route[0][0] + self.dx) * config.CELL_SIZE, (self.route[0][1] + self.dy) * config.CELL_SIZE
    

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
    

class _number:
    def __init__(self, value: int = 0):
        self.__val__ = value
        self.__hook__ = None

    def __call__(self, func):
        self.__hook__ = func
        return self

    def add(self, value: int = 1):
        self.__val__ += value
        if self.__hook__:
            self.__hook__()
        return self.__val__
    
    def sub(self, value: int = 1):
        self.add(-value)
    
    def data(self) -> int:
        return self.__val__
    
    def update(self, value: int):
        """
        Update the value of the number.
        
        :param value: The new value to set.
        """
        self.__val__ = value
        if self.__hook__:
            self.__hook__()
    

class sidebar:
    def __init__(self):
        self.back = pygame.Surface((config.SIDE_WIDTH, config.MAZE_SIZE * config.CELL_SIZE))
        self.back.fill(RGB("99d9ea"))
        self.bar = None
        self.score = _number()(self.flash)
        self.tip_line = 0
        self.flash()

    def flash(self):
        self.bar = self.back.copy()
        font = pygame.font.Font("./assets/fonts/Pixel32.ttf", 32)
        text = font.render(f"分数: {self.score.data():02}", True, RGB("e7f543"))
        shawdow = font.render(f"分数: {self.score.data():02}", True, RGB("1ea433"))
        text_rect = text.get_rect(topright=(config.SIDE_WIDTH - 10, 10))
        shawdow_rect = shawdow.get_rect(topright=(config.SIDE_WIDTH - 10-4, 10))
        self.bar.blit(shawdow, shawdow_rect)
        self.bar.blit(text, text_rect)

    def add_tip(self, tip: str):
        font = pygame.font.Font("./assets/fonts/Pixel32.ttf", 24)
        text = font.render(tip, True, RGB("1e48ad"))
        # 每行不覆盖前面的，往下排
        text_rect = text.get_rect(topleft=(10, config.MAZE_SIZE * config.CELL_SIZE - 40))
        text_rect.top -= self.tip_line * 30
        self.back.blit(text, text_rect)
        self.tip_line += 1
        self.flash()
    
