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
        self.point_values = {} 
        self.coin_group_map = {} # 新增：存储金币组代表 -> 完整组成员

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
                # 为了让内部路径更合理，选择距离起点最近的金币作为代表
                group.sort(key=lambda pos: self._bfs(self.start_pos, pos)[0])
                representative = group[0] 
                points_to_process.append(representative)
                self.point_values[representative] = len(group) * VALUE_MAP.get(COIN, 0)
                self.coin_group_map[representative] = group # 保存代表与组的映射
        
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
                print(f"Required point: Index {i}, Position {pos}, Type {char}")
        
        print(f"Required mask: {bin(self.required_mask)} (decimal: {self.required_mask})")

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

                            # 更新DP表：收益优先，距离次要
                            current_best_reward, current_best_dist = dp[new_mask][j]
                            
                            # 强制收益优先的比较逻辑
                            should_update = False
                            if current_best_reward == -1:  # 该状态尚未被访问
                                should_update = True
                            elif new_reward > current_best_reward:  # 收益更高，直接更新
                                should_update = True
                            elif new_reward == current_best_reward and new_dist < current_best_dist:  # 收益相同时，距离更短
                                should_update = True
                            
                            if should_update:
                                dp[new_mask][j] = (new_reward, new_dist)
                                path_tracker[new_mask][j] = i
                                print(f"Updated: {self.idx_to_pos[i]} -> {self.idx_to_pos[j]} | "
                                      f"New State Reward: {new_reward}, Distance: {new_dist}")

        # --- 寻找最优解并回溯路径 ---
        best_reward = -float('inf')
        best_dist_to_exit = float('inf')
        best_mask = -1
        best_last_idx = -1
        end_idx = self.pos_to_idx[self.end_pos]

        # 第一阶段：找到最大收益
        max_possible_reward = -float('inf')
        for mask in range(1, 1 << n):
            if (mask & self.required_mask) == self.required_mask:  # 必须包含所有必需节点
                for i in range(n):
                    if dp[mask][i][0] != -1:
                        reward, dist = dp[mask][i]
                        if reward > max_possible_reward:
                            max_possible_reward = reward

        print(f"Maximum possible reward: {max_possible_reward}")

        # 第二阶段：在最大收益的路径中，找到最短到达出口的路径
        for mask in range(1, 1 << n):
            if (mask & self.required_mask) == self.required_mask:  # 必须包含所有必需节点
                for i in range(n):
                    if dp[mask][i][0] != -1:
                        reward, dist = dp[mask][i]
                        
                        # 只考虑达到最大收益的路径
                        if reward == max_possible_reward:
                            # 计算从当前位置到出口的距离
                            dist_to_exit = self.dist_matrix[i][end_idx]
                            total_dist_to_exit = dist + dist_to_exit
                            
                            # 选择到达出口距离最短的路径
                            should_select = False
                            if best_last_idx == -1:  # 第一个最大收益解
                                should_select = True
                            elif total_dist_to_exit < best_dist_to_exit:  # 到出口距离更短
                                should_select = True
                            
                            if should_select:
                                best_reward = reward
                                best_dist_to_exit = total_dist_to_exit
                                best_mask = mask
                                best_last_idx = i
                                print(f"Best solution updated: Reward={reward}, Distance to exit={total_dist_to_exit}, Ending at {self.idx_to_pos[i]}")

        if best_reward == -1:
            return "No valid path found that visits all required points.", []

        # --- 回溯并构建最终路径（包括到出口的路径） ---
        final_path = []
        if best_last_idx != -1:
            curr_idx = best_last_idx
            mask = best_mask
            
            # 1. 首先，回溯高层级的路径访问顺序
            path_sequence = []
            while curr_idx != -1:
                path_sequence.append(curr_idx)
                prev_idx = path_tracker[mask][curr_idx]
                mask &= ~(1 << curr_idx)
                curr_idx = prev_idx
            path_sequence.reverse()

            # 2. 根据高层级顺序，逐段构建详细路径
            if path_sequence:
                final_path.append(self.idx_to_pos[path_sequence[0]])

            for i in range(len(path_sequence) - 1):
                u_idx, v_idx = path_sequence[i], path_sequence[i+1]
                current_path_end_pos = final_path[-1]
                v_pos_representative = self.idx_to_pos[v_idx]
                
                if v_pos_representative in self.coin_group_map:
                    group = self.coin_group_map[v_pos_representative]
                    _, _, segment_to_group = self._bfs(current_path_end_pos, v_pos_representative)
                    final_path.pop(-1)
                    final_path.extend(segment_to_group)
                    
                    internal_path_points = [p for p in group if p != v_pos_representative]
                    internal_path_points.sort(key=lambda p: self._bfs(v_pos_representative, p)[0])
                    
                    current_loc_in_group = v_pos_representative
                    for member in internal_path_points:
                        _, _, internal_segment = self._bfs(current_loc_in_group, member)
                        final_path.pop(-1)
                        final_path.extend(internal_segment)
                        current_loc_in_group = member
                else:
                    _, _, segment = self._bfs(current_path_end_pos, v_pos_representative)
                    final_path.pop(-1)
                    final_path.extend(segment)

            # 3. 最后，添加从最后一个位置到出口的路径
            if final_path:
                last_pos = final_path[-1]
                if last_pos != self.end_pos:
                    _, _, segment_to_exit = self._bfs(last_pos, self.end_pos)
                    final_path.pop(-1)  # 移除重复点
                    final_path.extend(segment_to_exit)

        return best_reward, final_path


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
