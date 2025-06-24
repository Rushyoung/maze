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


class moveable:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.goal = []
        self.ux = x
        self.uy = y

    def handle(self, event: pygame.event.Event):
        """
        Handle movement events.
        
        :param event: The pygame event to handle.
        """
        if event.type == pygame.KEYDOWN:
            # 只有当上一个动画播放完毕后才接受新的移动指令
            if self.goal:
                return

            # 在新的移动开始前，记录当前位置用于撤销
            self.ux = self.x
            self.uy = self.y

            move_amount = 16
            match event.key:
                case pygame.K_UP:
                    self.goal.append((self.x, self.y - move_amount))
                case pygame.K_DOWN:
                    self.goal.append((self.x, self.y + move_amount))
                case pygame.K_LEFT:
                    self.goal.append((self.x - move_amount, self.y))
                case pygame.K_RIGHT:
                    self.goal.append((self.x + move_amount, self.y))
    
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
        使用线性插值将对象向目标位置平滑移动，以实现恒速动画。
        """
        if not self.goal:
            return 0, 0

        # 动画速度（像素/帧）。速度为4，移动16像素需要4帧。
        speed = 4.0 

        target_x, target_y = self.goal[0]
        
        dx = target_x - self.x
        dy = target_y - self.y

        dist = (dx**2 + dy**2)**0.5

        if dist <= speed:
            # 距离足够近，直接移动到目标点并完成移动
            move_dx = dx
            move_dy = dy
            self.x = target_x
            self.y = target_y
            self.goal.pop(0)
        else:
            # 以恒定速度向目标移动
            move_dx = (dx / dist) * speed
            move_dy = (dy / dist) * speed
            self.x += move_dx
            self.y += move_dy
            
        return move_dx, move_dy

    def position(self):
        """
        Get the current position of the moveable object.
        
        :return: Tuple (x, y) representing the current position.
        """
        return self.x, self.y
    
    def __call__(self, x: int, y: int):
        """
        Set the position of the moveable object.
        
        :param x: New x-coordinate.
        :param y: New y-coordinate.
        """
        self.ux = self.x
        self.uy = self.y
        self.x = x
        self.y = y

    def undo(self):
        """
        撤销上一次的移动，恢复到移动前的位置，并清除移动目标。
        """
        self.x = self.ux
        self.y = self.uy
        self.goal.clear()