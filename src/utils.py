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


class controlable:
    """
    A class to handle control inputs for the game.
    """
    def __init__(self, x, y):
        self.keys = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "quit": pygame.K_ESCAPE
        }
        self.x = x
        self.y = y

    def is_pressed(self, key: str) -> bool:
        """
        Check if a specific key is pressed.

        :param key: The key to check.
        :return: True if the key is pressed, False otherwise.
        """
        return pygame.key.get_pressed()[self.keys[key]]