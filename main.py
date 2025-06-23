import pygame
import random
import heapq
import time
import json

# --- 1. 游戏配置 (Configuration) ---
# 迷宫元素符号
WALL = '#'
PATH = ' '
START = 'S'
EXIT = 'E'
GOLD = 'G'
TRAP = 'T'
LOCKER = 'L'
BOSS = 'B'

# 资源和陷阱的数值定义
VALUE_MAP = {
    GOLD: 10,       # 金币价值
    TRAP: -50,      # 陷阱惩罚 (设置为较大负数以强力规避)
    PATH: 0,
    LOCKER: 0,
    BOSS: -100,     # Boss也视为一个巨大的障碍/惩罚
    EXIT: 0,
    START: 0
}

# 尺寸和颜色
MAZE_SIZE = 31      # 迷宫尺寸 (建议为奇数)
CELL_SIZE = 20      # 每个单元格的像素大小
SCREEN_WIDTH = MAZE_SIZE * CELL_SIZE
SCREEN_HEIGHT = MAZE_SIZE * CELL_SIZE + 80 # 为下方的UI文本留出空间
FPS = 60

# 颜色定义
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (230, 230, 230)
COLOR_WALL = (50, 50, 80)
COLOR_START = (0, 255, 0)
COLOR_EXIT = (255, 0, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_TRAP = (139, 0, 255)
COLOR_BOSS = (255, 105, 180)
COLOR_LOCKER = (30, 144, 255)
COLOR_DP_PATH = (65, 105, 225, 180) # 动态规划路径颜色 (半透明)
COLOR_GREEDY_AI = (255, 165, 0)      # 贪心AI玩家颜色
COLOR_GREEDY_PATH = (255, 165, 0, 80) # 贪心AI路径颜色


class MazeGenerator:
    """使用分治法 (Recursive Division) 生成迷宫"""
    def __init__(self, size, screen):
        if size % 2 == 0:
            size += 1  # 确保尺寸为奇数
        self.size = size
        self.maze = [[PATH for _ in range(size)] for _ in range(size)]
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def _visualize_step(self, text):
        """可视化每一步操作"""
        draw_maze_grid(self.screen, self.maze)
        draw_ui_text(self.screen, text)
        pygame.display.flip()
        time.sleep(0.02)

    def _recursive_division(self, x, y, width, height):
        if width <= 2 or height <= 2:
            return

        # 决定分割方向：如果宽度大于高度，则垂直分割，反之亦然
        horizontal = width < height
        if width == height:
            horizontal = random.choice([True, False])

        if horizontal:
            # 水平分割
            wall_y = y + random.choice(range(1, height - 1, 2))
            passage_x = x + random.choice(range(0, width, 2))
            for i in range(x, x + width):
                if self.maze[wall_y][i] != PATH: continue
                if i != passage_x:
                    self.maze[wall_y][i] = WALL
            self._visualize_step(f"水平分割区域 ({x},{y}) to ({x+width},{y+height})")
            
            self._recursive_division(x, y, width, wall_y - y)
            self._recursive_division(x, wall_y + 1, width, y + height - (wall_y + 1))
        else:
            # 垂直分割
            wall_x = x + random.choice(range(1, width - 1, 2))
            passage_y = y + random.choice(range(0, height, 2))
            for i in range(y, y + height):
                if self.maze[i][wall_x] != PATH: continue
                if i != passage_y:
                    self.maze[i][wall_x] = WALL
            self._visualize_step(f"垂直分割区域 ({x},{y}) to ({x+width},{y+height})")
            
            self._recursive_division(x, y, wall_x - x, height)
            self._recursive_division(wall_x + 1, y, x + width - (wall_x + 1), height)

    def _add_elements(self):
        """在通路上随机添加S, E, G, T, L, B等元素"""
        path_cells = [(r, c) for r, row in enumerate(self.maze) for c, cell in enumerate(row) if cell == PATH]
        random.shuffle(path_cells)
        
        elements_to_place = {
            START: 1, EXIT: 1, BOSS: 1,
            GOLD: int(self.size * 0.8),
            TRAP: int(self.size * 0.5),
            LOCKER: int(self.size * 0.3)
        }
        
        for element, count in elements_to_place.items():
            for _ in range(count):
                if not path_cells: break
                r, c = path_cells.pop(0)
                self.maze[r][c] = element
        
        # 将迷宫矩阵保存为JSON文件
        with open('maze.json', 'w') as f:
            json.dump(self.maze, f, indent=2)
        print("迷宫已生成并保存为 maze.json")

    def generate(self):
        """生成迷宫主函数"""
        # 1. 初始化为空白区域并画上外墙
        self.maze = [[PATH for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            self.maze[0][i] = WALL
            self.maze[self.size - 1][i] = WALL
            self.maze[i][0] = WALL
            self.maze[self.size - 1][i] = WALL
        
        self._visualize_step("开始生成迷宫...")
        
        # 2. 从(1,1)开始递归分割
        self._recursive_division(1, 1, self.size - 2, self.size - 2)
        
        # 3. 添加游戏元素
        self._add_elements()
        self._visualize_step("迷宫生成完毕！")
        return self.maze

class PathFinder:
    """路径规划算法集合"""

    @staticmethod
    def get_element_position(maze, element):
        for r, row in enumerate(maze):
            for c, cell in enumerate(row):
                if cell == element:
                    return (r, c)
        return None

    @staticmethod
    def dynamic_programming_solve(maze):
        """使用类Dijkstra的动态规划思想计算最优路径和最大资源"""
        size = len(maze)
        start_pos = PathFinder.get_element_position(maze, START)
        exit_pos = PathFinder.get_element_position(maze, EXIT)

        if not start_pos or not exit_pos: return 0, []

        dp = [[float('-inf')] * size for _ in range(size)]
        parent = [[None] * size for _ in range(size)]
        dp[start_pos[0]][start_pos[1]] = 0
        
        # 优先队列存储 (负收益, r, c)，因为 heapq 是最小堆
        pq = [(-0, start_pos[0], start_pos[1])] 

        path_found = False
        while pq:
            current_value_neg, r, c = heapq.heappop(pq)
            current_value = -current_value_neg

            if current_value < dp[r][c]: continue
            if (r, c) == exit_pos:
                path_found = True
                break

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < size and 0 <= nc < size and maze[nr][nc] != WALL:
                    cell_type = maze[nr][nc]
                    new_value = dp[r][c] + VALUE_MAP.get(cell_type, 0)
                    
                    if new_value > dp[nr][nc]:
                        dp[nr][nc] = new_value
                        parent[nr][nc] = (r, c)
                        heapq.heappush(pq, (-new_value, nr, nc))
        
        path = []
        if path_found:
            curr = exit_pos
            while curr is not None:
                path.append(curr)
                curr = parent[curr[0]][curr[1]]
            path.reverse()
        
        max_value = dp[exit_pos[0]][exit_pos[1]]
        return max_value, path

class GreedyAI:
    """贪心算法AI玩家"""
    def __init__(self, maze, start_pos):
        self.maze = maze
        self.pos = start_pos
        self.path_taken = [start_pos]
        self.score = 0

    def _default_move(self):
        """视野内无目标时的默认移动策略：随机移动"""
        r, c = self.pos
        possible_moves = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.maze_size and 0 <= nc < self.maze_size and self.maze[nr][nc] != WALL:
                possible_moves.append((nr, nc))
        return random.choice(possible_moves) if possible_moves else self.pos

    def move_step(self):
        """根据3x3视野内的信息，计算并执行下一步移动"""
        r, c = self.pos
        self.maze_size = len(self.maze)
        vision_cells = []

        # 1. 扫描3x3视野寻找金币
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.maze_size and 0 <= nc < self.maze_size and self.maze[nr][nc] == GOLD:
                    distance = abs(dr) + abs(dc)
                    # 性价比 = 价值 / 距离 (此处价值固定, 故仅考虑距离)
                    score = VALUE_MAP[GOLD] / distance
                    vision_cells.append({'pos': (nr, nc), 'score': score, 'move':(r+dr, c+dc)})

        if vision_cells:
            # 2. 选择性价比最高的目标
            vision_cells.sort(key=lambda x: x['score'], reverse=True)
            best_target_pos = vision_cells[0]['pos']
            
            # 3. 朝最优目标移动一步
            move_r, move_c = r, c
            if best_target_pos[0] != r and self.maze[r + (1 if best_target_pos[0] > r else -1)][c] != WALL:
                move_r += (1 if best_target_pos[0] > r else -1)
            elif best_target_pos[1] != c and self.maze[r][c + (1 if best_target_pos[1] > c else -1)] != WALL:
                move_c += (1 if best_target_pos[1] > c else -1)
            else: # 首选路径被挡，走备选
                if best_target_pos[1] != c and self.maze[r][c + (1 if best_target_pos[1] > c else -1)] != WALL:
                     move_c += (1 if best_target_pos[1] > c else -1)
                elif best_target_pos[0] != r and self.maze[r + (1 if best_target_pos[0] > r else -1)][c] != WALL:
                     move_r += (1 if best_target_pos[0] > r else -1)
                else: # 被困住，随机移动
                     move_r, move_c = self._default_move()
            next_pos = (move_r, move_c)
        else:
            # 4. 视野内无金币，执行默认探索策略
            next_pos = self._default_move()

        # 更新位置和分数
        self.pos = next_pos
        self.path_taken.append(self.pos)
        cell_val = VALUE_MAP.get(self.maze[self.pos[0]][self.pos[1]], 0)
        self.score += cell_val
        if self.maze[self.pos[0]][self.pos[1]] == GOLD:
           self.maze[self.pos[0]][self.pos[1]] = PATH # 拾取金币

        return self.pos

# --- 3. 绘图和主逻辑 (Drawing and Game Logic) ---

CELL_IMAGES = {}
def load_images():
    """加载并缩放所有图像资源"""
    font_gold = pygame.font.SysFont('arial', int(CELL_SIZE * 0.8))
    font_symbols = pygame.font.SysFont('arial', int(CELL_SIZE * 1.2))
    CELL_IMAGES[WALL] = pygame.Surface((CELL_SIZE, CELL_SIZE)); CELL_IMAGES[WALL].fill(COLOR_WALL)
    CELL_IMAGES[PATH] = pygame.Surface((CELL_SIZE, CELL_SIZE)); CELL_IMAGES[PATH].fill(COLOR_BLACK)
    CELL_IMAGES[START] = font_symbols.render("S", True, COLOR_START);
    CELL_IMAGES[EXIT] = font_symbols.render("E", True, COLOR_EXIT);
    CELL_IMAGES[GOLD] = font_gold.render("G", True, COLOR_GOLD);
    CELL_IMAGES[TRAP] = font_symbols.render("T", True, COLOR_TRAP);
    CELL_IMAGES[BOSS] = font_symbols.render("B", True, COLOR_BOSS);
    CELL_IMAGES[LOCKER] = font_symbols.render("L", True, COLOR_LOCKER);

# 加载中文字体
def load_chinese_font(size):
    """加载支持中文的字体"""
    try:
        return pygame.font.Font("simhei.ttf", size)  # 使用黑体字体
    except FileNotFoundError:
        print("未找到 simhei.ttf 字体文件，请确保字体文件位于程序目录下。")
        return pygame.font.SysFont('arial', size)  # 退回到默认字体

# 修改 draw_ui_text 函数以支持中文字体
def draw_ui_text(screen, text):
    """在屏幕底部绘制UI提示文字"""
    pygame.draw.rect(screen, (40, 40, 40), (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
    font = load_chinese_font(28)  # 使用支持中文的字体
    lines = text.split('|')
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, COLOR_WHITE)
        screen.blit(text_surface, (15, SCREEN_HEIGHT - 70 + i * 30))

def draw_maze_grid(screen, maze):
    """绘制整个迷宫网格"""
    screen.fill(COLOR_BLACK)
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            img = CELL_IMAGES.get(cell, CELL_IMAGES[PATH])
            if isinstance(img, pygame.Surface):
                screen.blit(img, rect)
            else: # Text surfaces
                text_rect = img.get_rect(center=rect.center)
                screen.blit(img, text_rect)

def draw_path(screen, path, color, width=CELL_SIZE//3):
    """在迷宫上绘制路径"""
    if len(path) < 2: return
    pygame.draw.lines(screen, color, False, 
                      [(c*CELL_SIZE + CELL_SIZE//2, r*CELL_SIZE + CELL_SIZE//2) for r,c in path], 
                      width)

def draw_transparent_rect(screen, color, rect):
    """绘制半透明矩形"""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill(color)
    screen.blit(s, rect.topleft)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("算法驱动的迷宫探险")
    clock = pygame.time.Clock()
    
    load_images()
    
    game_state = 'WELCOME' # 'GENERATING', 'IDLE', 'SHOWING_DP', 'RUNNING_GREEDY'
    maze = [[]]
    dp_path = []
    greedy_ai = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    game_state = 'GENERATING'
                elif event.key == pygame.K_d and game_state == 'IDLE':
                    game_state = 'SHOWING_DP'
                    max_val, path = PathFinder.dynamic_programming_solve(maze)
                    dp_path = path
                    print(f"动态规划找到最优路径: 最大收益={max_val:.2f}, 长度={len(path)}步")
                elif event.key == pygame.K_a and game_state == 'IDLE':
                    start_pos = PathFinder.get_element_position(maze, START)
                    if start_pos:
                        greedy_ai = GreedyAI(maze, start_pos)
                        game_state = 'RUNNING_GREEDY'
                elif event.key == pygame.K_r:
                    game_state = 'WELCOME'
                    dp_path = []
                    greedy_ai = None

        # --- 游戏逻辑更新 ---
        if game_state == 'GENERATING':
            generator = MazeGenerator(MAZE_SIZE, screen)
            maze = generator.generate()
            dp_path = []
            greedy_ai = None
            game_state = 'IDLE'
        
        if game_state == 'RUNNING_GREEDY' and greedy_ai:
            if greedy_ai.pos != PathFinder.get_element_position(maze, EXIT):
                greedy_ai.move_step()
            else: # AI到达终点
                print(f"贪心AI完成探索: 最终得分={greedy_ai.score}, 路径长度={len(greedy_ai.path_taken)}步")
                game_state = 'IDLE'


        # --- 渲染 ---
        screen.fill(COLOR_BLACK)
        if game_state == 'WELCOME' or not maze:
             draw_ui_text(screen, "欢迎来到迷宫探险! | 按 'G' 生成迷宫, 'Q' 退出")
        else:
            draw_maze_grid(screen, maze)
            
            # 绘制路径
            if game_state == 'SHOWING_DP' and dp_path:
                # 绘制动态规划路径
                for r,c in dp_path:
                    draw_transparent_rect(screen, COLOR_DP_PATH, pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

            if greedy_ai:
                # 绘制贪心AI走过的路径
                if len(greedy_ai.path_taken) > 1:
                     draw_path(screen, greedy_ai.path_taken, COLOR_GREEDY_PATH, CELL_SIZE)
                # 绘制贪心AI当前位置
                ai_rect = pygame.Rect(greedy_ai.pos[1]*CELL_SIZE, greedy_ai.pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.ellipse(screen, COLOR_GREEDY_AI, ai_rect.inflate(-CELL_SIZE//4, -CELL_SIZE//4))


            # 更新UI文本
            if game_state == 'IDLE':
                 draw_ui_text(screen, "迷宫已就绪 | 'D': 显示DP最优路径 | 'A': 运行贪心AI | 'R': 重置")
            elif game_state == 'SHOWING_DP':
                 draw_ui_text(screen, f"蓝色为DP最优路径 (收益: {PathFinder.dynamic_programming_solve(maze)[0]:.0f}) | 'A': 运行贪心AI | 'R': 重置")
            elif game_state == 'RUNNING_GREEDY':
                 draw_ui_text(screen, f"贪心AI正在运行... | 得分: {greedy_ai.score} | 'R': 重置")
            
        pygame.display.flip()
        clock.tick(FPS if game_state != 'RUNNING_GREEDY' else 10) # 贪心AI模式放慢速度以便观察

    pygame.quit()

if __name__ == '__main__':
    main()
