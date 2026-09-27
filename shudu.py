# -*- coding: utf-8 -*-
import pygame
import os
import random

# 初始化pygame
pygame.init()

# 常量设置
WIDTH, HEIGHT = 540, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数独游戏")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 80, 80)
GREEN = (0, 180, 0)

# ========== 解决中文乱码：自动加载系统中文字体 ==========
def get_cn_font(size):
    font_path = None
    if os.name == "nt":
        # Windows 黑体
        font_path = "C:/Windows/Fonts/simhei.ttf"
    elif os.uname().sysname == "Darwin":
        # Mac 苹方
        font_path = "/System/Library/Fonts/STHeitiMedium.ttc"
    else:
        # Linux 文泉驿微米黑
        if os.path.exists("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
            font_path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    if font_path and os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    else:
        # 找不到中文字体时回退，文字自动换成英文，避免方块
        return pygame.font.SysFont(None, size)

FONT_BIG = get_cn_font(48)
FONT_MID = get_cn_font(36)
FONT_SMALL = get_cn_font(28)

# ---------------------- 数独生成与校验工具函数 ----------------------
def is_valid(board, row, col, num):
    # 检查行，跳过当前格子
    for i in range(9):
        if i != col and board[row][i] == num:
            return False
    # 检查列，跳过当前格子
    for i in range(9):
        if i != row and board[i][col] == num:
            return False
    # 检查3x3宫格，跳过当前格子
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            r = start_row + i
            c = start_col + j
            if not (r == row and c == col) and board[r][c] == num:
                return False

    return True

def find_empty(board):
    """MRV: 找候选数字最少的空位，返回坐标；无空位返回None"""
    min_candidates = 10
    best_pos = None
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                cnt = 0
                for n in range(1,10):
                    if is_valid(board, r, c, n):
                        cnt +=1
                if cnt == 0:
                    return (r,c)  # 无解格子直接返回
                if cnt < min_candidates:
                    min_candidates = cnt
                    best_pos = (r,c)
    return best_pos

def fill_board(board):
    pos = find_empty(board)
    if not pos:
        return True
    row, col = pos
    # 获取当前格子所有合法数字，再随机打乱
    candidates = []
    for num in range(1,10):
        if is_valid(board, row, col, num):
            candidates.append(num)
    random.shuffle(candidates)
    for num in candidates:
        board[row][col] = num
        if fill_board(board):
            return True
        board[row][col] = 0
    return False

def generate_sudoku(difficulty):
    """
    difficulty: easy=简单, medium=中等, hard=困难
    挖空数量：简单30，中等40，困难50
    """
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_board(board)
    # 挖去格子
    if difficulty == "easy":
        remove = 30
    elif difficulty == "medium":
        remove = 40
    else:
        remove = 50
    count = 0
    while count < remove:
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            count += 1
    return board

# ---------------------- 界面绘制函数 ----------------------
def draw_select_screen():
    """难度选择界面"""
    SCREEN.fill(WHITE)
    title = FONT_BIG.render("Select Difficulty", True, BLACK)
    SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    # 按钮区域
    btn_easy = pygame.Rect(140, 200, 260, 70)
    btn_medium = pygame.Rect(140, 300, 260, 70)
    btn_hard = pygame.Rect(140, 400, 260, 70)

    pygame.draw.rect(SCREEN, GRAY, btn_easy)
    pygame.draw.rect(SCREEN, GRAY, btn_medium)
    pygame.draw.rect(SCREEN, GRAY, btn_hard)

    text_easy = FONT_MID.render("easy", True, BLACK)
    text_medium = FONT_MID.render("medium", True, BLACK)
    text_hard = FONT_MID.render("hard", True, BLACK)

    SCREEN.blit(text_easy, (btn_easy.centerx - text_easy.get_width()//2, btn_easy.centery - text_easy.get_height()//2))
    SCREEN.blit(text_medium, (btn_medium.centerx - text_medium.get_width()//2, btn_medium.centery - text_medium.get_height()//2))
    SCREEN.blit(text_hard, (btn_hard.centerx - text_hard.get_width()//2, btn_hard.centery - text_hard.get_height()//2))
    pygame.display.update()
    return btn_easy, btn_medium, btn_hard

def draw_game_screen(board, selected, original_board):
    """游戏界面绘制"""
    SCREEN.fill(WHITE)
    cell_size = WIDTH // 9
    # 绘制网格线，粗线分隔3*3
    for i in range(10):
        line_width = 4 if i % 3 == 0 else 1
        pygame.draw.line(SCREEN, BLACK, (i*cell_size, 0), (i*cell_size, WIDTH), line_width)
        pygame.draw.line(SCREEN, BLACK, (0, i*cell_size), (WIDTH, i*cell_size), line_width)

    # 选中格子高亮
    if selected is not None:
        r, c = selected
        rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
        pygame.draw.rect(SCREEN, LIGHT_BLUE, rect)

    # 绘制数字
    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val != 0:
                if original_board[r][c] != 0:
                    # 原始题目数字固定黑色
                    color = BLACK
                else:
                    # 玩家填写数字，校验是否冲突
                    if is_valid(board, r, c, val):
                        color = GREEN
                    else:
                        color = RED
                text = FONT_BIG.render(str(val), True, color)
                SCREEN.blit(text, (c*cell_size + 14, r*cell_size + 8))

    # 底部提示文字
    tip = FONT_SMALL.render("Click cell | 1~9 input | Backspace clear", True, BLACK)
    SCREEN.blit(tip, (10, WIDTH + 10))
    pygame.display.update()

# ---------------------- 主循环 ----------------------
def main():
    state = "select"  # select:难度选择页面, game:游戏页面
    board = None
    original_board = None
    selected_cell = None
    clock = pygame.time.Clock()

    running = True
    while running:
        if state == "select":
            btn_easy, btn_medium, btn_hard = draw_select_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if btn_easy.collidepoint(pos):
                        board = generate_sudoku("easy")
                        original_board = [row.copy() for row in board]
                        state = "game"
                    elif btn_medium.collidepoint(pos):
                        board = generate_sudoku("medium")
                        original_board = [row.copy() for row in board]
                        state = "game"
                    elif btn_hard.collidepoint(pos):
                        board = generate_sudoku("hard")
                        original_board = [row.copy() for row in board]
                        state = "game"

        elif state == "game":
            draw_game_screen(board, selected_cell, original_board)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # 鼠标左键选中格子
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if my < WIDTH:
                        cell_size = WIDTH //9
                        col = mx // cell_size
                        row = my // cell_size
                        selected_cell = (row, col)
                # 键盘输入数字/删除
                if event.type == pygame.KEYDOWN:
                    if selected_cell is not None:
                        r, c = selected_cell
                        # 原始题目格子不能修改
                        if original_board[r][c] != 0:
                            continue
                        # 数字1~9
                        if event.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                            num = int(pygame.key.name(event.key))
                            board[r][c] = num
                        # Backspace / Delete清空
                        if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
                            board[r][c] = 0
        clock.tick(30)
    # pygame.quit()

if __name__ == "__main__":
    main()