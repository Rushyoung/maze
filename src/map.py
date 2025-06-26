import random

class _path:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent: '_path' = None
        self.rank = 0

    def union(self, other: '_path'):
        root_self = self.find()
        root_other = other.find()
        if root_self != root_other:
            # 按秩合并
            if root_self.rank < root_other.rank:
                root_self.parent = root_other
            elif root_self.rank > root_other.rank:
                root_other.parent = root_self
            else:
                root_other.parent = root_self
                root_self.rank += 1

    def find(self):
        if self.parent is None:
            return self
        else:
            # 路径压缩
            root = self.parent.find()
            self.parent = root
            return root


class _wall:
    def __init__(self, x, y, val):
        self.x = x
        self.y = y
        self.val = val

    def data(self):
        return self.x, self.y, self.val
    

class elements:
    def __init__(self):
        self.data = []

    def __contains__(self, item):
        return item in self.data
    
    def __iter__(self):
        yield from self.data
    
    def remove(self, item, deleted = None):
        idx = self.data.index(item)
        self.data[idx] = deleted
        return idx
    
    def append(self, item):
        if item not in self.data:
            self.data.append(item)

class map:
    def __init__(self, map_size):
        assert map_size >= 7, "Map size must be at least 7"
        assert map_size % 2 == 1, "Map size must be an odd number"
        self.map_size = map_size
        self.map = [[0 for _ in range(map_size)] for _ in range(map_size)]

    def print(self):
        for row in self.map:
            print("".join('##' if cell == 1 else '  ' for cell in row))

    def __getitem__(self, item):
        assert len(item) == 2, "Item must be a tuple of (x, y)"
        x, y = item
        return self.map[x][y]
    
    def __setitem__(self, item, value):
        assert len(item) == 2, "Item must be a tuple of (x, y)"
        x, y = item
        self.map[x][y] = value

    def random(self, flag, num = 1) -> elements:
        result = elements()
        for _ in range(num):
            x = random.randint(1, self.map_size - 2)
            y = random.randint(1, self.map_size - 2)
            while self.map[x][y]:
                x = random.randint(1, self.map_size - 2)
                y = random.randint(1, self.map_size - 2)
            result.append((x, y))
            self.map[x][y] = flag
        return result

    def generate(self):
        raise NotImplementedError("This method should be implemented by subclasses")

class normal(map):
    def __init__(self, map_size):
        super().__init__(map_size)
        self.val = [[random.random() for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.paths = [[None for _ in range(map_size)] for _ in range(map_size)]
        self.walls = []
        self.generate()
        del self.val
        del self.paths
        del self.walls

    def generate(self):
        for i in range(0, self.map_size, 2):
            for j in range(self.map_size):
                self.map[i][j] = 1
                self.map[j][i] = 1

        for i in range(1, self.map_size - 1, 2):
            for j in range(1, self.map_size - 1, 2):
                self.paths[i][j] = _path(i, j)

        for i in range(1, self.map_size - 1, 2):
            for j in range(2, self.map_size - 1, 2):
                self.walls.append(_wall(i, j, self.val[i][j]))
                self.walls.append(_wall(j, i, self.val[j][i]))
        self.walls.sort(key=lambda wall: wall.val)

        for wall in self.walls:
            i, j, _ = wall.data()
            if i % 2 == 1:  # 横向墙
                room1 = self.paths[i][j-1]  # 左边房间
                room2 = self.paths[i][j+1]  # 右边房间
            else:  # 纵向墙
                room1 = self.paths[i-1][j]  # 上方房间
                room2 = self.paths[i+1][j]  # 下方房间

            if room1.find() != room2.find():
                self.map[i][j] = 0
                room1.union(room2)


class recursive(map):
    def __init__(self, map_size):
        super().__init__(map_size)
        for i in range(map_size):
            self.map[0][i] = 1
            self.map[map_size - 1][i] = 1
            self.map[i][0] = 1
            self.map[i][map_size - 1] = 1
        self.generate()

    def generate(self):
        self._divide(1, 1, self.map_size - 2, self.map_size - 2)
        return self.map

    def _divide(self, x, y, width, height):
        if width < 3 or height < 3:
            return
        
        direction = random.choice([False, True]) if width == height else (width > height)
        direction = direction if random.random() > 0.2 else not direction

        if direction:
            candidate_cols = [col for col in range(x+1, x+width-1) if col % 2 == 0]
            if not candidate_cols:
                return
            wall_x = random.choice(candidate_cols)
            candidate_door_rows = [row for row in range(y, y+height) if row % 2 == 1]
            door_y = random.choice(candidate_door_rows)
            for i in range(y, y+height):
                if i == door_y:
                    self.map[i][wall_x] = 0
                else:
                    self.map[i][wall_x] = 1
            self._divide(x, y, wall_x - x, height)
            self._divide(wall_x+1, y, (x+width) - (wall_x+1), height)
        else:
            candidate_rows = [row for row in range(y+1, y+height-1) if row % 2 == 0]
            if not candidate_rows:
                return
            wall_y = random.choice(candidate_rows)
            candidate_door_cols = [col for col in range(x, x+width) if col % 2 == 1]
            door_x = random.choice(candidate_door_cols)
            for j in range(x, x+width):
                if j == door_x:
                    self.map[wall_y][j] = 0
                else:
                    self.map[wall_y][j] = 1
            self._divide(x, y, width, wall_y - y)
            self._divide(x, wall_y+1, width, (y+height) - (wall_y+1))
