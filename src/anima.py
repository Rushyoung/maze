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


class animation:
    # frames, 精灵图
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

    def speed(self, speed: int|float):
        self.step = speed

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