# --- 1. 游戏配置 (Configuration) ---
# 迷宫元素符号
WALL = '#'
PATH = ' '
START = 'S'
EXIT = 'E'
COIN = 'G'
TRAP = 'T'
LOCKER = 'L'
BOSS = 'B'
CLUE = 'C'
SIDE_WIDTH = 200

# 资源和陷阱的数值定义
VALUE_MAP = {
    COIN: 1,       # 金币价值
    TRAP: -1,      # 陷阱惩罚 (设置为较大负数以强力规避)
    PATH: 0,
    LOCKER: 0,
    BOSS: 0,     # Boss也视为一个巨大的障碍/惩罚
    EXIT: 0,
    START: 0,
    CLUE: 0,
}

# 尺寸和颜色
MAZE_SIZE = 21      # 迷宫尺寸 (建议为奇数)
CELL_SIZE = 24      # 每个单元格的像素大小
SCREEN_WIDTH = MAZE_SIZE * CELL_SIZE
SCREEN_HEIGHT = MAZE_SIZE * CELL_SIZE + 80 # 为下方的UI文本留出空间
FPS = 60

# 迷宫元素数量
## 金币
# COIN = 4
COIN_COUNT = 10  # 金币数量

# 线索
# CLUE = 5
CLUE_COUNT = 3 # 线索数量

# trap
TRAP_COUNT = 2 # 陷阱数量

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
