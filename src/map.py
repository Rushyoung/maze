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


class generate:
    def __init__(self, map_size):
        assert map_size >= 7, "Map size must be at least 7"
        assert map_size % 2 == 1, "Map size must be an odd number"
        self.map_size = map_size
        self.map = [[0 for _ in range(map_size)] for _ in range(map_size)]
        self.val = [[random.random() for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.paths = [[None for _ in range(map_size)] for _ in range(map_size)]
        self.walls = []
        self.generate()
        del self.val
        del self.paths
        del self.walls

    def __call__(self, x, y):
        return self.map[x][y]
    
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

    def print(self):
        for row in self.map:
            print("".join('##' if cell == 1 else '  ' for cell in row))

del random