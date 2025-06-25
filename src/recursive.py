import random

class Recursive:
    def __init__(self, mazeSize) -> None:
        assert mazeSize >= 7, "迷宫尺寸至少为7"
        assert mazeSize % 2 == 1, "迷宫尺寸必须为奇数"
        self.size = mazeSize
        # 初始化一个全为空格的迷宫
        self.map = [[' ' for _ in range(mazeSize)] for _ in range(mazeSize)]
        # 添加边界墙
        for i in range(mazeSize):
            self.map[0][i] = '#'
            self.map[mazeSize - 1][i] = '#'
            self.map[i][0] = '#'
            self.map[i][mazeSize - 1] = '#'
        
    def generate(self):
        self._divide(1, 1, self.size - 2, self.size - 2)
        return self.map

    def _divide(self, x, y, width, height):
        if width < 3 or height < 3:
            return
        
        if width > height:
            direction = 'v'
        elif width < height:
            direction = 'h'
        else:
            direction = random.choice(['v', 'h'])
        
        if direction == 'v':
            candidate_cols = [col for col in range(x+1, x+width-1) if col % 2 == 0]
            if not candidate_cols:
                return
            wall_x = random.choice(candidate_cols)
            candidate_door_rows = [row for row in range(y, y+height) if row % 2 == 1]
            door_y = random.choice(candidate_door_rows)
            
            for i in range(y, y+height):
                if i == door_y:
                    self.map[i][wall_x] = ' '
                else:
                    self.map[i][wall_x] = '#'
            
            self._divide(x, y, wall_x - x, height)
            self._divide(wall_x+1, y, (x+width) - (wall_x+1), height)
            
        elif direction == 'h':
            candidate_rows = [row for row in range(y+1, y+height-1) if row % 2 == 0]
            if not candidate_rows:
                return
            wall_y = random.choice(candidate_rows)
            candidate_door_cols = [col for col in range(x, x+width) if col % 2 == 1]
            door_x = random.choice(candidate_door_cols)
            
            for j in range(x, x+width):
                if j == door_x:
                    self.map[wall_y][j] = ' '
                else:
                    self.map[wall_y][j] = '#'
                    
            self._divide(x, y, width, wall_y - y)
            self._divide(x, wall_y+1, width, (y+height) - (wall_y+1))

    def print_maze(self):
        for i in range(self.size):
            print(' '.join(self.map[i]))

    def save_maze(self):
        pass


if __name__ == '__main__':
    gen = Recursive(21)
    gen.generate()
    gen.print_maze()
