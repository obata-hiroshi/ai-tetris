import pygame
import random

# Game constants
CELL_SIZE = 30
COLS, ROWS = 10, 20
SIDE_WIDTH = 150
WIDTH, HEIGHT = COLS * CELL_SIZE + SIDE_WIDTH, ROWS * CELL_SIZE
PREVIEW_CELL = CELL_SIZE // 2
FPS = 60

# Define shapes and colors
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1],
     [1, 1]],         # O
    [[0, 1, 0],
     [1, 1, 1]],      # T
    [[1, 0, 0],
     [1, 1, 1]],      # J
    [[0, 0, 1],
     [1, 1, 1]],      # L
    [[1, 1, 0],
     [0, 1, 1]],      # S
    [[0, 1, 1],
     [1, 1, 0]],      # Z
]
COLORS = [
    (0, 240, 240),  # cyan
    (240, 240, 0),  # yellow
    (160, 0, 240),  # purple
    (0, 0, 240),    # blue
    (240, 160, 0),  # orange
    (0, 240, 0),    # green
    (240, 0, 0),    # red
]


def new_bag():
    bag = SHAPES[:]
    random.shuffle(bag)
    return bag


piece_queue = []


def next_piece():
    if not piece_queue:
        piece_queue.extend(new_bag())
    shape = piece_queue.pop(0)
    return Piece(shape)


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


class Piece:
    def __init__(self, shape=None):
        self.shape = shape or random.choice(SHAPES)
        self.color = COLORS[SHAPES.index(self.shape)]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        new_shape = rotate(self.shape)
        if not collision(new_shape, self.x, self.y):
            self.shape = new_shape


def create_grid(locked_positions):
    grid = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid


def collision(shape, offset_x, offset_y, locked_positions=None):
    locked_positions = locked_positions or {}
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = x + offset_x
                new_y = y + offset_y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return True
                if new_y > -1 and (new_x, new_y) in locked_positions:
                    return True
    return False


def clear_rows(grid, locked):
    cleared = 0
    for y in range(len(grid) - 1, -1, -1):
        if (0, 0, 0) not in grid[y]:
            cleared += 1
            del_row(y, locked)
    return cleared


def del_row(row, locked):
    keys = sorted(list(locked), key=lambda k: k[1])
    for x, y in keys:
        if y < row:
            locked[(x, y + 1)] = locked.pop((x, y))
        elif y == row:
            del locked[(x, y)]


def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                surface,
                grid[y][x],
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )
    grid_width = COLS * CELL_SIZE
    for x in range(COLS + 1):
        pygame.draw.line(surface, (30, 30, 30), (x * CELL_SIZE, 0), (x * CELL_SIZE, ROWS * CELL_SIZE))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, (30, 30, 30), (0, y * CELL_SIZE), (grid_width, y * CELL_SIZE))


def draw_piece(surface, piece, color=None):
    draw_color = color or piece.color
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and y + piece.y > -1:
                pygame.draw.rect(
                    surface,
                    draw_color,
                    (
                        (piece.x + x) * CELL_SIZE,
                        (piece.y + y) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    ),
                )


def get_ghost_piece(piece, locked):
    ghost = Piece(piece.shape)
    ghost.x, ghost.y = piece.x, piece.y
    while not collision(ghost.shape, ghost.x, ghost.y + 1, locked):
        ghost.y += 1
    return ghost


def draw_preview(surface, shape, offset_x, offset_y):
    if shape is None:
        return
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    surface,
                    COLORS[SHAPES.index(shape)],
                    (
                        offset_x + x * PREVIEW_CELL,
                        offset_y + y * PREVIEW_CELL,
                        PREVIEW_CELL,
                        PREVIEW_CELL,
                    ),
                )


def lock_piece(piece, locked):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and piece.y + y > -1:
                locked[(piece.x + x, piece.y + y)] = piece.color


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = next_piece()
    hold_shape = None
    hold_used = False
    fall_time = 0
    fall_speed = 0.5
    score = 0
    lines = 0
    level = 1

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            if not collision(current_piece.shape, current_piece.x, current_piece.y + 1, locked_positions):
                current_piece.y += 1
            else:
                lock_piece(current_piece, locked_positions)
                cleared = clear_rows(grid, locked_positions)
                if cleared:
                    lines += cleared
                    score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 0) * level
                    level = lines // 10 + 1
                    fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                current_piece = next_piece()
                hold_used = False
                if collision(current_piece.shape, current_piece.x, current_piece.y, locked_positions):
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not collision(current_piece.shape, current_piece.x - 1, current_piece.y, locked_positions):
                    current_piece.x -= 1
                elif event.key == pygame.K_RIGHT and not collision(current_piece.shape, current_piece.x + 1, current_piece.y, locked_positions):
                    current_piece.x += 1
                elif event.key == pygame.K_DOWN and not collision(current_piece.shape, current_piece.x, current_piece.y + 1, locked_positions):
                    current_piece.y += 1
                    score += 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    drop = 0
                    while not collision(current_piece.shape, current_piece.x, current_piece.y + 1, locked_positions):
                        current_piece.y += 1
                        drop += 1
                    score += drop * 2
                    lock_piece(current_piece, locked_positions)
                    cleared = clear_rows(grid, locked_positions)
                    if cleared:
                        lines += cleared
                        score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 0) * level
                        level = lines // 10 + 1
                        fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                    current_piece = next_piece()
                    hold_used = False
                    if collision(current_piece.shape, current_piece.x, current_piece.y, locked_positions):
                        running = False
                elif event.key == pygame.K_c:
                    if not hold_used:
                        if hold_shape is None:
                            hold_shape = current_piece.shape
                            current_piece = next_piece()
                        else:
                            hold_shape, current_piece.shape = current_piece.shape, hold_shape
                            current_piece.color = COLORS[SHAPES.index(current_piece.shape)]
                            current_piece.x = COLS // 2 - len(current_piece.shape[0]) // 2
                            current_piece.y = 0
                        hold_used = True

        draw_grid(win, grid)
        ghost = get_ghost_piece(current_piece, locked_positions)
        draw_piece(win, ghost, color=(80, 80, 80))
        draw_piece(win, current_piece)

        draw_preview(win, hold_shape, COLS * CELL_SIZE + 20, 40)
        for i, shape in enumerate(piece_queue[:3]):
            draw_preview(win, shape, COLS * CELL_SIZE + 20, 120 + i * 60)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        lines_text = font.render(f"Lines: {lines}", True, (255, 255, 255))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        win.blit(score_text, (COLS * CELL_SIZE + 20, HEIGHT - 80))
        win.blit(lines_text, (COLS * CELL_SIZE + 20, HEIGHT - 60))
        win.blit(level_text, (COLS * CELL_SIZE + 20, HEIGHT - 40))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
