from src.config import *
import heapq
from collections import deque

class pathFind:
    """
    迷宫路径规划算法，使用动态规划解决带收益的旅行商问题
    """
    def __init__(self, maze):
        self.maze = maze
        self.rows, self.cols = MAZE_SIZE, MAZE_SIZE
        
        self._identify_key_points()
        self._build_graph()

    def _get_neighbors(self, pos):
        """获取某位置的所有可通行邻居"""
        r, c = pos
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < self.rows and 0 <= nc < self.cols and 
                self.maze[nr, nc] != WALL):
                neighbors.append((nr, nc))
        return neighbors

    def _is_important_junction(self, pos):
        """判断某位置是否为重要分叉路口（连接多个有价值的区域）"""
        if self.maze[pos] == WALL:
            return False
        
        neighbors = self._get_neighbors(pos)
        if len(neighbors) < 3:  # 不是分叉路口
            return False
        
        # 从每个方向探索，看能到达什么重要点
        important_destinations = []
        
        for neighbor in neighbors:
            # BFS探索这个方向能到达的重要点
            queue = deque([neighbor])
            visited = {pos, neighbor}
            max_explore_distance = 8  # 减少探索距离
            
            for step in range(max_explore_distance):
                if not queue:
                    break
                    
                current = queue.popleft()
                char = self.maze[current]
                
                # 如果找到重要点，记录并停止这个方向的探索
                if char in {COIN, CLUE, BOSS, LOCKER, EXIT}:
                    important_destinations.append((current, char))
                    break
                
                # 继续探索
                next_neighbors = self._get_neighbors(current)
                for next_pos in next_neighbors:
                    if next_pos not in visited:
                        visited.add(next_pos)
                        queue.append(next_pos)
        
        # 只有连接2个或以上重要点的分叉路口才被认为是重要的
        return len(important_destinations) >= 2

    def _identify_key_points(self):
        """识别所有关键点并建立索引"""
        self.key_points = []
        self.pos_to_idx = {}
        self.idx_to_pos = {}
        self.point_values = {}
        
        required_types = {CLUE, BOSS, LOCKER}
        
        # 收集基本关键点（起点、终点、必需点、金币）
        for r in range(self.rows):
            for c in range(self.cols):
                char = self.maze[r, c]
                pos = (r, c)
                if char == START:
                    self.start_pos = pos
                    self.key_points.append(pos)
                    self.point_values[pos] = 0
                elif char == EXIT:
                    self.end_pos = pos
                    self.key_points.append(pos)
                    self.point_values[pos] = 0
                elif char in required_types or char == COIN:
                    self.key_points.append(pos)
                    self.point_values[pos] = VALUE_MAP.get(char, 0)

        # 构建索引映射
        for i, pos in enumerate(self.key_points):
            self.pos_to_idx[pos] = i
            self.idx_to_pos[i] = pos

        # 设置必需节点的掩码
        self.required_mask = 0
        for i, pos in enumerate(self.key_points):
            char = self.maze[pos]
            if char in required_types:
                self.required_mask |= (1 << i)
                print(f"Required point: Index {i}, Position {pos}, Type {char}")
        
        print(f"Required mask: {bin(self.required_mask)} (decimal: {self.required_mask})")
        print(f"Total key points: {len(self.key_points)}")

    def _bfs_with_path_analysis(self, start_pos, end_pos):
        """使用BFS计算两点间的最短路径"""
        if start_pos == end_pos:
            return 0, 0, 0, [start_pos]
        
        queue = deque([(start_pos, [start_pos])])
        visited = {start_pos}
        
        while queue:
            pos, path = queue.popleft()
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos[0] + dr, pos[1] + dc
                new_pos = (nr, nc)
                
                if (0 <= nr < self.rows and 0 <= nc < self.cols and 
                    self.maze[nr, nc] != WALL and new_pos not in visited):
                    
                    new_path = path + [new_pos]
                    
                    if new_pos == end_pos:
                        return self._analyze_path_rewards(new_path)
                    
                    visited.add(new_pos)
                    queue.append((new_pos, new_path))
        
        return float('inf'), 0, 0, []

    def _analyze_path_rewards(self, path):
        """分析路径上的收益和成本"""
        distance = len(path) - 1
        coin_reward = 0
        trap_penalty = 0
        
        # 只分析路径中间的格子，起点和终点的价值由DP主循环单独计算
        for i in range(1, len(path) - 1): # 修改循环范围，直接排除起点和终点
            pos = path[i]
            char = self.maze[pos]
            
            if char == COIN:
                coin_reward += VALUE_MAP[COIN]
            elif char == TRAP:
                trap_penalty += abs(VALUE_MAP[TRAP])
        
        return distance, coin_reward, trap_penalty, path

    def _build_graph(self):
        """计算所有关键点之间的成本和路径"""
        n = len(self.key_points)
        self.dist_matrix = [[float('inf')] * n for _ in range(n)]
        self.reward_matrix = [[0] * n for _ in range(n)]
        self.penalty_matrix = [[0] * n for _ in range(n)]
        self.path_map = {}

        print("Building graph between key points...")
        
        for i in range(n):
            for j in range(i, n):
                pos1 = self.idx_to_pos[i]
                pos2 = self.idx_to_pos[j]
                
                dist, coin_reward, trap_penalty, path = self._bfs_with_path_analysis(pos1, pos2)
                
                self.dist_matrix[i][j] = self.dist_matrix[j][i] = dist
                self.reward_matrix[i][j] = self.reward_matrix[j][i] = coin_reward
                self.penalty_matrix[i][j] = self.penalty_matrix[j][i] = trap_penalty
                self.path_map[(i, j)] = path
                self.path_map[(j, i)] = list(reversed(path))
        
        print("Graph building complete.")

    def _find_optimal_nodes_to_visit(self):
        """使用动态规划找到最优的节点集合"""
        n = len(self.key_points)
        start_idx = self.pos_to_idx[self.start_pos]
        end_idx = self.pos_to_idx[self.end_pos]

        print(f"Finding optimal nodes to visit with {n} key points...")

        # dp[mask][i] = (max_reward, min_dist)
        dp = [[(-float('inf'), float('inf'))] * n for _ in range(1 << n)]
        dp[1 << start_idx][start_idx] = (0, 0)

        # 动态规划主循环
        for mask in range(1, 1 << n):
            for i in range(n):
                current_reward, current_dist = dp[mask][i]
                if current_reward == -float('inf'):
                    continue
                
                for j in range(n):
                    if (mask & (1 << j)) or self.dist_matrix[i][j] == float('inf'):
                        continue
                    
                    new_mask = mask | (1 << j)
                    
                    # 计算移动成本和收益
                    path_dist = self.dist_matrix[i][j]
                    path_coin_reward = self.reward_matrix[i][j]
                    path_trap_penalty = self.penalty_matrix[i][j]
                    
                    # 计算到达j点的总收益
                    target_pos = self.idx_to_pos[j]
                    target_value = self.point_values.get(target_pos, 0)
                    
                    # 总收益 = 当前收益 + 路径金币收益 + 目标点价值 - 路径陷阱惩罚
                    new_reward = current_reward + path_coin_reward + target_value - path_trap_penalty
                    new_dist = current_dist + path_dist
                    
                    # 更新DP状态
                    old_reward, old_dist = dp[new_mask][j]
                    
                    should_update = False
                    if old_reward == -float('inf'):
                        should_update = True
                    elif new_reward > old_reward:
                        should_update = True
                    elif new_reward == old_reward and new_dist < old_dist:
                        should_update = True
                    
                    if should_update:
                        dp[new_mask][j] = (new_reward, new_dist)

        # 寻找最优的节点集合
        best_reward = -float('inf')
        best_mask = -1

        for mask in range(1, 1 << n):
            if (mask & self.required_mask) == self.required_mask:
                for i in range(n):
                    reward, dist = dp[mask][i]
                    if reward > -float('inf'):
                        # 计算到出口的总成本
                        dist_to_exit = self.dist_matrix[i][end_idx]
                        penalty_to_exit = self.penalty_matrix[i][end_idx]
                        reward_to_exit = self.reward_matrix[i][end_idx]
                        
                        final_reward = reward + reward_to_exit - penalty_to_exit
                        
                        if final_reward > best_reward:
                            best_reward = final_reward
                            best_mask = mask

        if best_mask == -1:
            return set(), -1

        # 提取要访问的节点
        nodes_to_visit = set()
        for i in range(n):
            if best_mask & (1 << i):
                nodes_to_visit.add(i)

        print(f"Optimal nodes to visit: {[self.idx_to_pos[i] for i in nodes_to_visit]}")
        return nodes_to_visit, best_reward

    def _greedy_path_ordering(self, nodes_to_visit):
        """使用贪心策略按距离排序节点访问顺序"""
        start_idx = self.pos_to_idx[self.start_pos]
        end_idx = self.pos_to_idx[self.end_pos]
        
        # 移除起点和终点，只对中间节点排序
        remaining_nodes = nodes_to_visit.copy()
        remaining_nodes.discard(start_idx)
        remaining_nodes.discard(end_idx)
        
        # 贪心选择路径
        path_sequence = [start_idx]
        current_node = start_idx
        
        while remaining_nodes:
            # 找到距离当前节点最近的未访问节点
            best_next = None
            best_distance = float('inf')
            best_score = -float('inf')
            
            for next_node in remaining_nodes:
                distance = self.dist_matrix[current_node][next_node]
                
                # 计算这个节点的价值密度（收益/距离）
                node_pos = self.idx_to_pos[next_node]
                node_value = self.point_values.get(node_pos, 0)
                path_reward = self.reward_matrix[current_node][next_node]
                path_penalty = self.penalty_matrix[current_node][next_node]
                
                net_reward = node_value + path_reward - path_penalty
                
                # 综合评分：考虑距离和收益
                if distance > 0:
                    score = net_reward / distance  # 价值密度
                else:
                    score = net_reward
                
                # 优先选择距离近且价值高的节点
                if (score > best_score or 
                    (abs(score - best_score) < 0.1 and distance < best_distance)):
                    best_next = next_node
                    best_distance = distance
                    best_score = score
            
            if best_next is not None:
                path_sequence.append(best_next)
                remaining_nodes.remove(best_next)
                current_node = best_next
                
                print(f"Next node: {self.idx_to_pos[best_next]}, distance: {best_distance:.1f}, score: {best_score:.2f}")
            else:
                break
        
        # 添加终点
        path_sequence.append(end_idx)
        
        return path_sequence

    def find(self):
        """执行改进的路径规划算法"""
        print("=== Phase 1: Finding optimal nodes to visit ===")
        nodes_to_visit, best_reward = self._find_optimal_nodes_to_visit()
        
        if not nodes_to_visit:
            return "No valid path found", []
        
        print(f"Expected reward: {best_reward}")
        
        print("\n=== Phase 2: Greedy ordering of nodes ===")
        path_sequence = self._greedy_path_ordering(nodes_to_visit)
        
        print(f"Visit sequence: {[self.idx_to_pos[idx] for idx in path_sequence]}")
        
        print("\n=== Phase 3: Building detailed path ===")
        # 构建详细路径
        final_path = []
        total_distance = 0
        
        for i in range(len(path_sequence)):
            if i == 0:
                # 起点
                final_path.append(self.idx_to_pos[path_sequence[i]])
            else:
                # 获取从前一个点到当前点的路径
                from_idx = path_sequence[i-1]
                to_idx = path_sequence[i]
                segment = self.path_map.get((from_idx, to_idx), [])
                
                if segment and len(segment) > 1:
                    # 跳过起点避免重复
                    final_path.extend(segment[1:])
                    total_distance += self.dist_matrix[from_idx][to_idx]
                else:
                    # 如果没有找到路径，直接添加目标点
                    final_path.append(self.idx_to_pos[to_idx])

        print(f"Total distance: {total_distance}")
        print(f"Final path length: {len(final_path)}")
        
        return best_reward, final_path

    def find_with_debug(self):
        """调试版本的路径查找"""
        print("=== Debug Mode: Analyzing all possible paths ===")
        
        # 首先找到最优节点集合
        nodes_to_visit, best_reward = self._find_optimal_nodes_to_visit()
        
        if not nodes_to_visit:
            return "No valid path found", []
        
        # 尝试不同的访问顺序
        print("\n=== Comparing different visit orders ===")
        
        # 1. 贪心距离优先
        greedy_sequence = self._greedy_path_ordering(nodes_to_visit)
        greedy_distance = sum(self.dist_matrix[greedy_sequence[i]][greedy_sequence[i+1]] 
                            for i in range(len(greedy_sequence)-1))
        
        print(f"Greedy order: {[self.idx_to_pos[idx] for idx in greedy_sequence]}")
        print(f"Greedy distance: {greedy_distance}")
        
        # 2. 如果节点不多，可以尝试其他启发式排序
        if len(nodes_to_visit) <= 8:
            print("Trying alternative orderings...")
            
            # 按节点价值排序
            value_sorted = sorted(nodes_to_visit, 
                                key=lambda x: self.point_values.get(self.idx_to_pos[x], 0), 
                                reverse=True)
            
            # 移除起点和终点
            start_idx = self.pos_to_idx[self.start_pos]
            end_idx = self.pos_to_idx[self.end_pos]
            
            value_sequence = [start_idx] + [x for x in value_sorted if x not in {start_idx, end_idx}] + [end_idx]
            value_distance = sum(self.dist_matrix[value_sequence[i]][value_sequence[i+1]] 
                               for i in range(len(value_sequence)-1))
            
            print(f"Value-first order: {[self.idx_to_pos[idx] for idx in value_sequence]}")
            print(f"Value-first distance: {value_distance}")
            
            # 选择更好的顺序
            if value_distance < greedy_distance * 0.9:
                print("Choosing value-first order")
                final_sequence = value_sequence
            else:
                print("Choosing greedy order")
                final_sequence = greedy_sequence
        else:
            final_sequence = greedy_sequence
        
        # 构建详细路径
        final_path = []
        for i in range(len(final_sequence)):
            if i == 0:
                final_path.append(self.idx_to_pos[final_sequence[i]])
            else:
                from_idx = final_sequence[i-1]
                to_idx = final_sequence[i]
                segment = self.path_map.get((from_idx, to_idx), [])
                
                if segment and len(segment) > 1:
                    final_path.extend(segment[1:])
                else:
                    final_path.append(self.idx_to_pos[to_idx])
        
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
            print(f"Final path length: {len(path)}")
            print(f"Best reward: {reward}")
    
    except FileNotFoundError:
        print("maze.json file not found")
    except Exception as e:
        print(f"Error: {e}")
