import pygame
import random

# Game constants
CELL_SIZE = 30
COLS, ROWS = 10, 20
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
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
    for x in range(COLS + 1):
        pygame.draw.line(surface, (30, 30, 30), (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, (30, 30, 30), (0, y * CELL_SIZE), (WIDTH, y * CELL_SIZE))


def draw_piece(surface, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and y + piece.y > -1:
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (
                        (piece.x + x) * CELL_SIZE,
                        (piece.y + y) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    ),
                )


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Tetris")
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = Piece()
    fall_time = 0
    fall_speed = 0.5

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
                for y, row in enumerate(current_piece.shape):
                    for x, cell in enumerate(row):
                        if cell and current_piece.y + y > -1:
                            locked_positions[(current_piece.x + x, current_piece.y + y)] = current_piece.color
                current_piece = Piece()
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
                elif event.key == pygame.K_UP:
                    current_piece.rotate()

        clear_rows(grid, locked_positions)
        draw_grid(win, grid)
        draw_piece(win, current_piece)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
