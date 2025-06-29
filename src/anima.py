import pygame
import os


def load(path: str, name: range)-> 'list[pygame.Surface]':
    """
    Load a series of images from a directory.
    
    :param path: The directory containing the images.
    :param name: A range object indicating the indices of the images to load.
    :return: A list of loaded pygame.Surface objects.
    """
    frames = []
    for i in name:
        frame_path = f"{path}/{i:02}.png"
        if not os.path.exists(frame_path):
            print(f"Warning: Image {frame_path} does not exist.")
            continue
        try:
            frame = pygame.image.load(frame_path).convert_alpha()
            frames.append(frame)
        except pygame.error as e:
            print(f"Error loading image {frame_path}: {e}")
    return frames


def sprite(path: str, size = None) -> 'list[pygame.Surface]':
    """
    can only load square sprite sheet.
    
    :param path: The directory containing the images.
    :param size: The size of each sprite. If None, it will use the height of the first sprite.
    :return: A list of resized pygame.Surface objects.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"file {path} does not exist.")
    frames = []
    frame = pygame.image.load(path).convert_alpha()
    if size is None:
        size = frame.get_height()
    frame_count = frame.get_width() // size
    for i in range(frame_count):
        sub_frame = frame.subsurface((i * size, 0, size, size))
        frames.append(pygame.transform.scale(sub_frame, (size, size)))
    return frames


class animation:
    def __init__(self, frames):
        self.frames = frames
        self.current_frame = 0
        self.frame_count = len(frames)
        self.x = 0
        self.y = 0
        self.step = 1
        self.loop = False

    def __call__(self, x, y):
        self.x = x
        self.y = y

    def position(self):
        return self.x, self.y

    def reset(self):
        self.current_frame = 0

    def set(self, x: int, y: int, speed: float = 1/16, loop: bool = True):
        self.x = x
        self.y = y
        self.step = speed
        self.loop = loop

    def resize(self, width: int, height: int):
        """
        Resize all frames to the specified width and height.
        
        :param width: The new width for the frames.
        :param height: The new height for the frames.
        """
        self.frames = [pygame.transform.scale(frame, (width, height)) for frame in self.frames]

    def update(self):
        if self.current_frame >= self.frame_count:
            if not self.loop:
                return False, None
            self.current_frame = 0
        self.current_frame += self.step
        return True, self.frames[int(self.current_frame - self.step)]
    
    def move(self, dx: int, dy: int):
        """
        Move the animation by the specified delta x and delta y.
        
        :param dx: The change in x position.
        :param dy: The change in y position.
        """
        self.x += dx
        self.y += dy

    def moveTo(self, x: int, y: int):
        """
        Move the animation to a specific position.
        
        :param x: The new x position.
        :param y: The new y position.
        """
        self.x = x
        self.y = y
    

class manager:
    def __init__(self):
        self.animations: dict[str, animation] = {}
    
    def add(self, name: str, anima: animation):
        if name in self.animations:
            raise ValueError(f"Animation '{name}' already exists.")
        self.animations[name] = anima

    def update(self, screen: 'pygame.Surface'):
        for key in self.animations:
            status, frame = self.animations[key].update()
            if not status:
                continue
            x, y = self.animations[key].position()
            screen.blit(frame, (x, y))

    def reset(self, name: str):
        if name not in self.animations:
            raise ValueError(f"Animation '{name}' does not exist.")
        self.animations[name].reset()

    def remove(self, name: str):
        if name not in self.animations:
            raise ValueError(f"Animation '{name}' does not exist.")
        del self.animations[name]