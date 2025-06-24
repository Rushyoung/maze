class animation:
    # frames, 精灵图
    def __init__(self, frames):
        self.frames = frames
        self.current_frame = 0
        self.frame_count = len(frames)
        self.x = 0
        self.y = 0

    def __call__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if self.current_frame >= self.frame_count - 1:
            return False
        self.current_frame += 1
        # @todo
        # 播放当前帧
        return True