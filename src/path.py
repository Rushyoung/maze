from src.config import *
import heapq

class pathFind:
    """
    使用带状态的全局最优路径搜索（A*变体），寻找迷宫中的最优收益路径。
    此算法适用于“一次性”资源（如金币）的场景。
    """
    def __init__(self, maze):
        self.maze = maze
        self.rows, self.cols = MAZE_SIZE, MAZE_SIZE
        
        # --- 识别所有关键点和必经点 ---
        self.start_pos = None
        self.end_pos = None
        self.must_visit_points = {} # 使用字典存储必经点，方便查找
        
        # 动态查找所有关键点
        key_types_to_find = [START, EXIT, CLUE, COIN, BOSS]
        must_visit_types = [CLUE, BOSS]
        
        for r in range(self.rows):
            for c in range(self.cols):
                char = self.maze[r, c]
                if char in key_types_to_find:
                    if char == START:
                        self.start_pos = (r, c)
                    elif char == EXIT:
                        self.end_pos = (r, c)
                    elif char in must_visit_types:
                        # 给每个必经点一个唯一的位，用于掩码
                        bit = 1 << len(self.must_visit_points)
                        self.must_visit_points[(r, c)] = bit

    def find(self):
        """
        执行全局最优路径搜索。
        """
        if not self.start_pos or not self.end_pos:
            return "Start or End point not found in maze.", []

        # --- 初始化搜索 ---
        
        # 1. 定义目标掩码：当所有必经点的位都被设置时，任务完成
        # (1 << N) - 1 会生成一个 N 位的、所有位都为1的掩码
        num_must_visit = len(self.must_visit_points)
        target_mask = (1 << num_must_visit) - 1

        # 2. 初始化优先队列
        # 存储元组: (-reward, reward, pos, visited_mask, path)
        # -reward 用于实现最大堆，因为 heapq 是最小堆
        # visited_mask 记录访问了哪些必经点
        pq = [(-0, 0, self.start_pos, 0, [self.start_pos])]

        # 3. 初始化 visited 集合，防止重复搜索
        # 存储元组: (pos, visited_mask)
        # 这确保了即使回到同一点，但若访问过的必经点集合不同，也视为新状态
        visited = set()

        # --- 开始搜索循环 ---
        while pq:
            # 取出当前收益最高的路径
            neg_reward, reward, pos, mask, path = heapq.heappop(pq)

            # 检查当前状态是否已经处理过
            if (pos, mask) in visited:
                continue
            visited.add((pos, mask))

            # 检查当前位置是否是一个新的必经点
            if pos in self.must_visit_points:
                mask |= self.must_visit_points[pos]

            # 检查是否到达终点，并且所有必经点都已访问
            if pos == self.end_pos and mask == target_mask:
                # 由于使用了优先队列（最大堆），第一个找到的满足条件的路径就是最优解。
                return reward, path

            # --- 向四周探索 ---
            r, c = pos
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                # 检查边界和墙
                if not (0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr, nc] != WALL):
                    continue
                
                new_pos = (nr, nc)
                
                # 计算新路径的收益
                # 注意：这里的收益是实时累加的，金币只会被计算一次
                new_reward = reward + VALUE_MAP.get(self.maze[new_pos], 0)
                
                # 将新状态加入优先队列
                new_path = path + [new_pos]
                heapq.heappush(pq, (-new_reward, new_reward, new_pos, mask, new_path))

        # 如果队列为空还没找到完整路径，则说明无解
        return "No valid path found that visits all required points.", []


if __name__ == "__main__":
    import json
    try:
        with open('maze.json', 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
        maze = maze_data['maze']
        
        path_finder = pathFind(maze)
        reward, path = path_finder.find()

        if isinstance(reward, str):
            print(reward) # 打印错误或未找到路径的信息
        else:
            # 在地图上标记路径
            # 创建一个副本以避免修改原始迷宫数据
            display_maze = [list(row) for row in maze]
            for r, c in path:
                if display_maze[r][c] not in [START, EXIT, CLUE, BOSS]:
                    display_maze[r][c] = '.'
            
            print(f"Optimal path found with reward: {reward}")
            for row in display_maze:
                print(''.join(row))

    except FileNotFoundError:
        print("Error: maze.json not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
