import pygame


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


class moveable:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.goal = []

    def handle(self, event: pygame.event.Event):
        """
        Handle movement events.
        
        :param event: The pygame event to handle.
        """
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    self.goal.append((self.x, self.y - 10))
                case pygame.K_DOWN:
                    self.goal.append((self.x, self.y + 10))
                case pygame.K_LEFT:
                    self.goal.append((self.x - 10, self.y))
                case pygame.K_RIGHT:
                    self.goal.append((self.x + 10, self.y))
    
    def distance(self):
        def __dist(p1, p2):
            return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
        if not self.goal:
            return 0
        ans = __dist((self.x, self.y), self.goal[0])
        if len(self.goal) > 1:
            for i in range(1, len(self.goal)):
                ans += __dist(self.goal[i - 1], self.goal[i])
        return ans
    
    def move(self):
        """
        Move the object towards the first goal position if available.
        """
        sign = lambda x: (x > 0) - (x < 0)
        if not self.goal:
            return 0, 0
        distance = self.distance()
        distance = distance / 30
        distance = max(1, distance)
        dx = sign(self.goal[0][0] - self.x) * distance
        dy = sign(self.goal[0][1] - self.y) * distance
        is_done = False
        if abs(dx) >= abs(self.goal[0][0] - self.x):
            dx = self.goal[0][0] - self.x
            is_done = True
        if abs(dy) >= abs(self.goal[0][1] - self.y):
            dy = self.goal[0][1] - self.y
            is_done = True
        if is_done:
            self.goal.pop(0)
        self.x += dx
        self.y += dy
        return dx, dy
    
    def __call__(self, x: int, y: int):
        """
        Set the position of the moveable object.
        
        :param x: New x-coordinate.
        :param y: New y-coordinate.
        """
        self.x = x
        self.y = y