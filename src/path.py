from src.config import *
import heapq
from collections import deque

class pathFind:
    """
    - 将所有关键点（起点、终点、资源）作为图的节点。
    - 使用BFS计算节点间的“距离”和“陷阱惩罚”，构建两个独立的成本矩阵。
    - 使用动态规划（带位掩码）解决此图上的“带收益的旅行商问题”，并在决策时分别考量两种成本。
    """
    def __init__(self, maze):
        self.maze = maze
        self.rows, self.cols = MAZE_SIZE, MAZE_SIZE
        
        self._identify_key_points()
        self._build_graph()

    def _identify_key_points(self):
        """识别所有关键点，并将它们建立索引和位掩码。相邻的金币会被合并处理。"""
        self.key_points = []
        self.pos_to_idx = {}
        self.idx_to_pos = {}
        self.point_values = {} # 新增：存储每个关键点的价值

        all_coins = []
        other_points = []
        required_types = {CLUE, BOSS, LOCKER}

        # 1. 分离金币和其他关键点
        for r in range(self.rows):
            for c in range(self.cols):
                char = self.maze[r, c]
                pos = (r, c)
                if char == START:
                    self.start_pos = pos
                elif char == EXIT:
                    self.end_pos = pos
                elif char == COIN:
                    all_coins.append(pos)
                elif (char in VALUE_MAP and VALUE_MAP[char] > 0) or (char in required_types):
                    other_points.append(pos)

        # 2. 对金币进行智能聚类 (Smart Clustering)
        coin_groups = []
        if all_coins:
            # --- 调试代码开始 ---
            print("\n--- Coin Clustering Analysis ---")
            # --- 调试代码结束 ---
            # a. 构建一个只包含金币的邻接表，边表示两金币间路径无陷阱
            coin_adj = {pos: [] for pos in all_coins}
            for i in range(len(all_coins)):
                for j in range(i + 1, len(all_coins)):
                    coin1 = all_coins[i]
                    coin2 = all_coins[j]
                    # 使用 _bfs 检查路径质量
                    _, traps, _ = self._bfs(coin1, coin2)
                    # --- 调试代码开始 ---
                    if traps == 0:
                        print(f"Found trap-free path between {coin1} and {coin2}. Linking them.")
                    # --- 调试代码结束 ---
                    if traps == 0:
                        coin_adj[coin1].append(coin2)
                        coin_adj[coin2].append(coin1)

            # b. 在金币邻接图上寻找连通分量
            visited_coins = set()
            for coin_pos in all_coins:
                if coin_pos not in visited_coins:
                    current_group = []
                    q = deque([coin_pos])
                    visited_coins.add(coin_pos)
                    while q:
                        pos = q.popleft()
                        current_group.append(pos)
                        for neighbor in coin_adj[pos]:
                            if neighbor not in visited_coins:
                                visited_coins.add(neighbor)
                                q.append(neighbor)
                    coin_groups.append(current_group)
            
            # --- 调试代码开始 ---
            print("\n--- Identified Coin Groups ---")
            for idx, group in enumerate(coin_groups):
                print(f"Group {idx+1}: Representative={group[0]}, Members={group}, Total Value={len(group) * VALUE_MAP.get(COIN, 0)}")
            print("------------------------------\n")
            # --- 调试代码结束 ---

        # 3. 将金币组的代表和其他点合并到 points_to_process
        points_to_process = list(other_points)
        for group in coin_groups:
            if group:
                representative = group[0] # 使用第一个金币作为代表
                points_to_process.append(representative)
                # 计算并存储整个金币组的总价值
                self.point_values[representative] = len(group) * VALUE_MAP.get(COIN, 0)
        
        # 为非金币组的关键点填充价值
        for pos in other_points:
            self.point_values[pos] = VALUE_MAP.get(self.maze[pos], 0)
        
        # 4. 构建最终的关键点列表
        self.key_points.append(self.start_pos)
        for pos in points_to_process:
            if pos != self.start_pos:
                self.key_points.append(pos)
        
        if self.end_pos not in self.key_points:
            self.key_points.append(self.end_pos)

        for i, pos in enumerate(self.key_points):
            self.pos_to_idx[pos] = i
            self.idx_to_pos[i] = pos
            
        self.required_mask = 0
        for i, pos in enumerate(self.key_points):
            char = self.maze[pos]
            if char in required_types:
                self.required_mask |= (1 << i)

    def _bfs(self, start_pos, end_pos):
        """使用BFS计算两点间的最优路径，同时返回距离、陷阱惩罚和详细路径。"""
        # 状态: (cost, distance, trap_penalty, pos, path)。
        # cost是Dijkstra排序的依据，这里只关心距离，所以cost就是distance。
        pq = [(0, 0, 0, start_pos, [start_pos])]
        # visited 存储到达某点的最小距离
        visited_costs = {start_pos: 0}

        while pq:
            cost, dist, traps, pos, path = heapq.heappop(pq)

            if pos == end_pos:
                return dist, traps, path

            if cost > visited_costs[pos]:
                continue

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos[0] + dr, pos[1] + dc

                if not (0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr, nc] != WALL):
                    continue
                
                new_pos = (nr, nc)
                new_dist = dist + 1
                new_traps = traps
                
                if self.maze[new_pos] == TRAP:
                    # VALUE_MAP[TRAP]是负数，所以用负号来变正
                    new_traps -= VALUE_MAP.get(TRAP, 0)
                
                if new_pos not in visited_costs or new_dist < visited_costs[new_pos]:
                    visited_costs[new_pos] = new_dist
                    new_path = path + [new_pos]
                    heapq.heappush(pq, (new_dist, new_dist, new_traps, new_pos, new_path))
                    
        return float('inf'), float('inf'), []

    def _build_graph(self):
        """计算所有关键点之间的成本和路径，构建图。"""
        n = len(self.key_points)
        self.dist_matrix = [[float('inf')] * n for _ in range(n)]
        self.trap_penalty_matrix = [[float('inf')] * n for _ in range(n)]
        self.path_map = {}

        for i in range(n):
            for j in range(i, n):
                pos1 = self.idx_to_pos[i]
                pos2 = self.idx_to_pos[j]
                dist, traps, path = self._bfs(pos1, pos2)
                self.dist_matrix[i][j] = self.dist_matrix[j][i] = dist
                self.trap_penalty_matrix[i][j] = self.trap_penalty_matrix[j][i] = traps
                self.path_map[(i, j)] = path
                self.path_map[(j, i)] = list(reversed(path))
        
        # --- 在这里添加调试代码 ---
        print("--- Key Points ---")
        for i, pos in self.idx_to_pos.items():
            print(f"Index {i}: Position {pos}, Type: {self.maze[pos]}")
        print("\n--- Distance Matrix ---")
        for r in self.dist_matrix:
            print([f"{d:4.0f}" for d in r])
        print("\n--- Trap Penalty Matrix ---")
        for r in self.trap_penalty_matrix:
            print([f"{t:4.0f}" for t in r])
        # --- 调试代码结束 ---

    def find(self):
        """执行动态规划并回溯路径。"""
        n = len(self.key_points)
        start_idx = self.pos_to_idx[self.start_pos]
        end_idx = self.pos_to_idx[self.end_pos]

        # dp[mask][i] = (max_reward, min_dist)。
        # 存储到达状态(mask, i)时的最大收益和最小距离
        dp = [[(-1, float('inf'))] * n for _ in range(1 << n)]
        path_tracker = [[-1] * n for _ in range(1 << n)]

        dp[1 << start_idx][start_idx] = (0, 0)

        for mask in range(1, 1 << n):
            for i in range(n):
                if dp[mask][i][0] != -1: # 如果状态可达
                    for j in range(n):
                        # 如果j不在mask中，且i和j之间有路
                        if not (mask & (1 << j)) and self.dist_matrix[i][j] != float('inf'):
                            
                            new_mask = mask | (1 << j)

                            current_reward, current_dist = dp[mask][i]
                            path_dist = self.dist_matrix[i][j]
                            path_traps = self.trap_penalty_matrix[i][j]
                            item_value = self.point_values.get(self.idx_to_pos[j], 0)

                            # 检查是否应该前往节点 j
                            should_go = False
                            # 真实收益 = 当前收益 + 物品价值 - (路径陷阱数量 * 单个陷阱惩罚值)
                            trap_penalty_value = abs(VALUE_MAP.get(TRAP, 1)) # 从配置获取惩罚值
                            new_reward = current_reward + item_value - (path_traps * trap_penalty_value)
                            new_dist = current_dist + path_dist

                            # 更新DP表：如果新路径收益更高，或者收益相同但距离更短，则更新
                            if new_reward > dp[new_mask][j][0] or \
                               (new_reward == dp[new_mask][j][0] and new_dist < dp[new_mask][j][1]):
                                dp[new_mask][j] = (new_reward, new_dist)
                                path_tracker[new_mask][j] = i

        # --- 寻找最优解并回溯路径 ---
        best_reward = -1
        min_dist_for_best_reward = float('inf')
        final_mask = -1

        for mask in range(1, 1 << n):
            # 检查是否满足必经点要求，并且终点也被访问
            if (mask & self.required_mask) == self.required_mask and (mask & (1 << end_idx)):
                reward, dist = dp[mask][end_idx]
                if reward > best_reward or (reward == best_reward and dist < min_dist_for_best_reward):
                    best_reward = reward
                    min_dist_for_best_reward = dist
                    final_mask = mask
        
        if best_reward == -1:
            return "No valid path found that visits all required points.", []

        # --- 回溯路径 ---
        key_point_path_indices = []
        curr_node = end_idx
        curr_mask = final_mask
        while curr_node != -1:
            key_point_path_indices.append(curr_node)
            prev_node = path_tracker[curr_mask][curr_node]
            if prev_node != -1:
                curr_mask &= ~(1 << curr_node)
            curr_node = prev_node
        
        key_point_path_indices.reverse()

        full_path = [self.start_pos]
        for i in range(len(key_point_path_indices) - 1):
            start_node_idx = key_point_path_indices[i]
            end_node_idx = key_point_path_indices[i+1]
            segment = self.path_map.get((start_node_idx, end_node_idx), [])
            full_path.extend(segment[1:])

        return best_reward, full_path


if __name__ == "__main__":
    import json
    try:
        with open('maze.json', 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
        maze = maze_data['maze']
        
        path_finder = pathFind(maze)
        reward, path = path_finder.find()

        if isinstance(reward, str):
            print(reward)
        else:
            display_maze = [list(row) for row in maze]
            for r, c in path:
                if display_maze[r][c] not in [START, EXIT, CLUE, BOSS, COIN]:
                    display_maze[r][c] = '.'
            
            print(f"Optimal path found with reward: {reward}")
            for row in display_maze:
                print(''.join(row))

    except FileNotFoundError:
        print("Error: maze.json not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
