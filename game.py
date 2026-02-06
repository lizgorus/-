import arcade
import random
import sys
import time
from enum import Enum
import pygame
import math
import json
import os

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
LIGHT_GRAY = (230, 230, 230)
RED = (220, 60, 60)
GREEN = (60, 180, 75)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
CYAN = (64, 224, 208)
DARK_RED = (178, 34, 34)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
BACKGROUND = (25, 25, 35)
PANEL_BG = (40, 40, 55)
BUTTON_COLOR = (65, 105, 225)
BUTTON_HOVER = (100, 149, 237)
BUTTON_ACTIVE = (30, 144, 255)
BUTTON_TEXT = WHITE
MENU_BG = (20, 20, 30, 180)
TEXT_COLOR = (220, 220, 240)
ACCENT_COLOR = (100, 200, 255)

GRADIENT_TOP = (15, 15, 25)
GRADIENT_MIDDLE = (35, 35, 55)
GRADIENT_BOTTOM = (60, 70, 90)

GREEN_TICK = (60, 180, 75)
LIME_TICK = (144, 238, 144)
YELLOW_TICK = (255, 215, 0)
RED_TICK = (220, 60, 60)
GOLD_CROWN = (255, 215, 0)


class Difficulty(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    MASTER = 5


class AnimatedBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.stars = []
        self.grid_cells = []
        self.time = 0
        self.gradient_phase = 0
        self.grid_offset = 0

        arcade_window = arcade.Window(100, 100, "Hidden Arcade Window")
        arcade_window.close()

        for _ in range(150):
            x = random.randint(0, width)
            y = random.randint(0, height // 2)
            size = random.uniform(0.1, 0.8)
            speed = random.uniform(0.1, 0.4)
            brightness = random.uniform(0.5, 1.0)
            self.stars.append({
                'x': x, 'y': y, 'size': size,
                'speed': speed, 'brightness': brightness,
                'phase': random.uniform(0, math.pi * 2)
            })

        for _ in range(150):
            self.create_particle()

        self.create_grid_background()

    def create_particle(self):
        x = random.randint(0, self.width)
        y = random.randint(self.height // 2, self.height)
        size = random.randint(2, 5)

        color_choices = [
            (120, 180, 255, 180),
            (180, 120, 255, 180),
            (120, 255, 220, 180),
            (255, 220, 120, 180),
            (255, 150, 150, 180),
            (150, 255, 150, 180),
        ]
        color = random.choice(color_choices)

        speed_x = random.uniform(-0.4, 0.4)
        speed_y = random.uniform(-0.6, -0.2)
        lifetime = random.randint(150, 350)

        self.particles.append({
            'x': x, 'y': y, 'size': size, 'color': color,
            'speed_x': speed_x, 'speed_y': speed_y,
            'lifetime': lifetime, 'max_lifetime': lifetime
        })

    def create_grid_background(self):
        cell_size = 40
        rows = self.height // cell_size + 2
        cols = self.width // cell_size + 2

        for r in range(rows):
            for c in range(cols):
                x = c * cell_size
                y = r * cell_size
                self.grid_cells.append({
                    'x': x,
                    'y': y,
                    'size': cell_size,
                    'alpha': random.randint(20, 40)
                })

    def update(self):
        self.time += 1
        self.gradient_phase = (self.gradient_phase + 0.001) % (2 * math.pi)
        self.grid_offset = (self.grid_offset + 0.3) % 40

        for particle in self.particles[:]:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['lifetime'] -= 1

            particle['speed_x'] *= 0.995
            particle['speed_y'] *= 0.995

            if (particle['lifetime'] <= 0 or
                    particle['y'] < -50 or
                    particle['x'] < -50 or
                    particle['x'] > self.width + 50):
                self.particles.remove(particle)
                self.create_particle()

        for star in self.stars:
            star['brightness'] = 0.6 + 0.4 * math.sin(self.time * 0.015 + star['phase'])

    def draw(self, screen):
        for y in range(self.height):
            pos = y / self.height

            if pos < 0.5:
                ratio = pos * 2
                r = int(GRADIENT_TOP[0] * (1 - ratio) + GRADIENT_MIDDLE[0] * ratio)
                g = int(GRADIENT_TOP[1] * (1 - ratio) + GRADIENT_MIDDLE[1] * ratio)
                b = int(GRADIENT_TOP[2] * (1 - ratio) + GRADIENT_MIDDLE[2] * ratio)
            else:
                ratio = (pos - 0.5) * 2
                r = int(GRADIENT_MIDDLE[0] * (1 - ratio) + GRADIENT_BOTTOM[0] * ratio)
                g = int(GRADIENT_MIDDLE[1] * (1 - ratio) + GRADIENT_BOTTOM[1] * ratio)
                b = int(GRADIENT_MIDDLE[2] * (1 - ratio) + GRADIENT_BOTTOM[2] * ratio)

            wave = math.sin(y * 0.01 + self.time * 0.02) * 2
            r = max(10, min(70, r + wave))
            g = max(10, min(80, g + wave))
            b = max(10, min(100, b + wave))

            pygame.draw.line(screen, (r, g, b), (0, y), (self.width, y))

        cell_size = 40
        for cell in self.grid_cells:
            cell_y = cell['y'] + self.grid_offset
            if cell_y > self.height:
                cell_y -= self.height + cell_size

            cell_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            pygame.draw.rect(cell_surface, (255, 255, 255, cell['alpha']),
                             (0, 0, cell_size, cell_size), 1)
            screen.blit(cell_surface, (cell['x'], cell_y))

        for star in self.stars:
            alpha = int(255 * star['brightness'])
            star_color = (255, 255, 255, alpha)

            size = star['size'] * (1 + 0.1 * math.sin(self.time * 0.02 + star['phase']))

            surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surface, star_color, (int(size), int(size)), int(size))
            screen.blit(surface, (int(star['x'] - size), int(star['y'] - size)))

        for particle in self.particles:
            alpha = int(particle['color'][3] * (particle['lifetime'] / particle['max_lifetime']))
            color = (*particle['color'][:3], alpha)

            pygame.draw.circle(screen, color,
                               (int(particle['x']), int(particle['y'])),
                               particle['size'])

            if abs(particle['speed_x']) > 0.1 or abs(particle['speed_y']) > 0.1:
                trail_length = 4
                for i in range(1, trail_length + 1):
                    trail_alpha = alpha * (1 - i / trail_length) * 0.5
                    trail_color = (*color[:3], int(trail_alpha))
                    trail_x = particle['x'] - particle['speed_x'] * i * 1.5
                    trail_y = particle['y'] - particle['speed_y'] * i * 1.5
                    trail_size = particle['size'] * (1 - i / trail_length)
                    pygame.draw.circle(screen, trail_color,
                                       (int(trail_x), int(trail_y)),
                                       int(trail_size))


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        self.is_question = False
        self.highlight = False
        self.animation_progress = 0

    def __repr__(self):
        return f"Cell({self.row}, {self.col}, mine={self.is_mine})"

    def update_animation(self, speed=0.1):
        if self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + speed)
        return self.animation_progress < 1.0


class Board:
    def __init__(self, rows, cols, mines, difficulty):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.difficulty = difficulty
        self.grid = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.flags_placed = 0
        self.cells_revealed = 0
        self.total_cells = rows * cols
        self.game_ended = False
        self.animation_delay = 0

        for r in range(rows):
            row = []
            for c in range(cols):
                cell = Cell(r, c)
                cell.animation_delay = (r * 0.05) + (c * 0.02)
                row.append(cell)
            self.grid.append(row)

    def place_mines(self, first_click_row, first_click_col):
        excluded_cells = set()

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r = first_click_row + dr
                c = first_click_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    excluded_cells.add((r, c))

        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        mine_positions = [pos for pos in all_positions if pos not in excluded_cells]
        mine_positions = random.sample(mine_positions, self.mines)

        for r, c in mine_positions:
            self.grid[r][c].is_mine = True

        self.calculate_neighbor_mines()

    def calculate_neighbor_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.grid[nr][nc].is_mine:
                                    count += 1
                    self.grid[r][c].neighbor_mines = count

    def reveal(self, row, col):
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or
                self.grid[row][col].is_revealed or self.grid[row][col].is_flagged):
            return not self.game_over

        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()

        cell = self.grid[row][col]
        cell.is_revealed = True

        if cell.is_mine:
            self.game_over = True
            self.game_ended = True
            self.elapsed_time = time.time() - self.start_time if self.start_time else 0
            self.reveal_all_mines()
            return False

        self.cells_revealed += 1

        if cell.neighbor_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        self.reveal(row + dr, col + dc)

        if self.cells_revealed == self.total_cells - self.mines:
            self.game_won = True
            self.game_ended = True
            self.elapsed_time = time.time() - self.start_time if self.start_time else 0
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.grid[r][c].is_mine and not self.grid[r][c].is_flagged:
                        self.grid[r][c].is_flagged = True
                        self.flags_placed += 1

        return not self.game_over

    def toggle_flag(self, row, col):
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or
                self.grid[row][col].is_revealed or self.game_over or self.game_won):
            return

        cell = self.grid[row][col]

        if cell.is_flagged:
            cell.is_flagged = False
            cell.is_question = False
            self.flags_placed -= 1
        elif cell.is_question:
            cell.is_question = False
        else:
            cell.is_flagged = True
            self.flags_placed += 1

    def toggle_question(self, row, col):
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or
                self.grid[row][col].is_revealed or self.game_over or self.game_won):
            return

        cell = self.grid[row][col]

        if cell.is_question:
            cell.is_question = False
        elif cell.is_flagged:
            cell.is_flagged = False
            cell.is_question = True
        else:
            cell.is_question = True

    def chord(self, row, col):
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or
                not self.grid[row][col].is_revealed or self.game_over or self.game_won):
            return

        cell = self.grid[row][col]
        if cell.neighbor_mines == 0:
            return

        flag_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc].is_flagged:
                        flag_count += 1

        if flag_count == cell.neighbor_mines:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.grid[nr][nc].is_flagged and not self.grid[nr][nc].is_question:
                            self.reveal(nr, nc)

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].is_mine:
                    self.grid[r][c].is_revealed = True

    def get_time(self):
        if self.game_over or self.game_won:
            return self.elapsed_time
        elif self.start_time:
            return time.time() - self.start_time
        else:
            return 0

    def reset(self):
        self.grid = []
        self.game_over = False
        self.game_won = False
        self.game_ended = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.flags_placed = 0
        self.cells_revealed = 0
        self.animation_delay = 0

        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                cell = Cell(r, c)
                cell.animation_delay = (r * 0.05) + (c * 0.02)
                row.append(cell)
            self.grid.append(row)

    def update_animations(self):
        animating = False
        for r in range(self.rows):
            for c in range(self.cols):
                if hasattr(self.grid[r][c], 'animation_delay'):
                    if self.grid[r][c].animation_delay > 0:
                        self.grid[r][c].animation_delay -= 0.016
                    else:
                        if self.grid[r][c].update_animation(0.1):
                            animating = True
        return animating


class IconRenderer:
    @staticmethod
    def create_play_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        points = [
            (size * 0.2, size * 0.1),
            (size * 0.2, size * 0.9),
            (size * 0.9, size * 0.5)
        ]
        pygame.draw.polygon(surface, color, points)

        return surface

    @staticmethod
    def create_settings_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)
        radius = size // 2 - 2

        pygame.draw.circle(surface, color, center, radius, 2)

        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)

            inner_x = center[0] + (radius - 3) * math.cos(rad)
            inner_y = center[1] + (radius - 3) * math.sin(rad)

            outer_x = center[0] + (radius + 3) * math.cos(rad)
            outer_y = center[1] + (radius + 3) * math.sin(rad)

            pygame.draw.line(surface, color, (inner_x, inner_y), (outer_x, outer_y), 3)

        pygame.draw.circle(surface, color, center, radius // 3)

        return surface

    @staticmethod
    def create_stats_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        bar_width = size // 5
        bar_heights = [size * 0.7, size * 0.4, size * 0.9, size * 0.3, size * 0.6]

        for i, height in enumerate(bar_heights):
            x = i * (bar_width + 1) + 2
            y = size - height - 2
            pygame.draw.rect(surface, color, (x, y, bar_width, height))

        return surface

    @staticmethod
    def create_quit_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        margin = size * 0.2
        pygame.draw.line(surface, color,
                         (margin, margin), (size - margin, size - margin), 3)
        pygame.draw.line(surface, color,
                         (size - margin, margin), (margin, size - margin), 3)

        return surface

    @staticmethod
    def create_back_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        points = [
            (size * 0.7, size * 0.1),
            (size * 0.3, size * 0.5),
            (size * 0.7, size * 0.9)
        ]
        pygame.draw.polygon(surface, color, points)

        return surface

    @staticmethod
    def create_restart_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)
        radius = size // 3

        pygame.draw.arc(surface, color,
                        (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                        math.radians(30), math.radians(330), 3)

        arrow_angle = math.radians(30)
        arrow_x = center[0] + radius * math.cos(arrow_angle)
        arrow_y = center[1] + radius * math.sin(arrow_angle)

        arrow_points = [
            (arrow_x, arrow_y),
            (arrow_x - 5, arrow_y - 3),
            (arrow_x - 2, arrow_y),
            (arrow_x - 5, arrow_y + 3)
        ]
        pygame.draw.polygon(surface, color, arrow_points)

        return surface

    @staticmethod
    def create_flag_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.rect(surface, (150, 150, 150),
                         (size * 0.4, size * 0.2, size * 0.1, size * 0.7))

        flag_points = [
            (size * 0.45, size * 0.2),
            (size * 0.8, size * 0.35),
            (size * 0.45, size * 0.5)
        ]
        pygame.draw.polygon(surface, color, flag_points)

        return surface

    @staticmethod
    def create_rocket_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        rocket_points = [
            (size * 0.5, size * 0.1),
            (size * 0.3, size * 0.7),
            (size * 0.7, size * 0.7)
        ]
        pygame.draw.polygon(surface, color, rocket_points)

        fire_points = [
            (size * 0.3, size * 0.7),
            (size * 0.5, size * 0.9),
            (size * 0.7, size * 0.7)
        ]
        pygame.draw.polygon(surface, (255, 100, 50), fire_points)

        return surface

    @staticmethod
    def create_crown_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        crown_points = [
            (size * 0.2, size * 0.6),
            (size * 0.3, size * 0.3),
            (size * 0.5, size * 0.4),
            (size * 0.7, size * 0.3),
            (size * 0.8, size * 0.6)
        ]
        pygame.draw.polygon(surface, color, crown_points)

        jewel_positions = [(size * 0.3, size * 0.3),
                           (size * 0.5, size * 0.4),
                           (size * 0.7, size * 0.3)]
        for pos in jewel_positions:
            pygame.draw.circle(surface, (255, 215, 0),
                               (int(pos[0]), int(pos[1])), size // 8)

        return surface

    @staticmethod
    def create_skull_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        pygame.draw.circle(surface, color, (size // 2, size // 2), size // 3)

        pygame.draw.circle(surface, BLACK,
                           (size // 2 - size // 8, size // 2), size // 10)
        pygame.draw.circle(surface, BLACK,
                           (size // 2 + size // 8, size // 2), size // 10)

        pygame.draw.arc(surface, BLACK,
                        (size // 2 - size // 5, size // 2 + size // 10,
                         size // 2.5, size // 5),
                        math.radians(0), math.radians(180), 2)

        return surface

    @staticmethod
    def create_target_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)

        pygame.draw.circle(surface, color, center, size // 3)
        pygame.draw.circle(surface, WHITE, center, size // 4)
        pygame.draw.circle(surface, color, center, size // 6)
        pygame.draw.circle(surface, WHITE, center, size // 8)

        return surface

    @staticmethod
    def create_star_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)
        radius = size // 3

        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = radius if i % 2 == 0 else radius * 0.4
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            points.append((x, y))

        pygame.draw.polygon(surface, color, points)

        return surface

    @staticmethod
    def create_checkmark_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        points = [
            (size * 0.25, size * 0.5),
            (size * 0.45, size * 0.7),
            (size * 0.75, size * 0.3)
        ]
        pygame.draw.lines(surface, color, False, points, 4)

        return surface

    @staticmethod
    def create_difficulty_icon(size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)
        radius = size // 2 - 2

        pygame.draw.circle(surface, color, center, radius, 2)

        pygame.draw.polygon(surface, color, [
            (center[0] - radius * 0.3, center[1]),
            (center[0] + radius * 0.3, center[1]),
            (center[0], center[1] - radius * 0.6)
        ])

        return surface


class Button:
    def __init__(self, x, y, width, height, text,
                 color=BUTTON_COLOR, hover_color=BUTTON_HOVER,
                 active_color=BUTTON_ACTIVE, text_color=BUTTON_TEXT,
                 font_size=24, border_radius=12, icon_type=None,
                 animation_delay=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_active = False
        self.border_radius = border_radius
        self.icon_type = icon_type
        self.animation_delay = animation_delay
        self.animation_progress = 0
        self.target_y = y
        self.start_y = y - 50
        self.rect.y = self.start_y

        self.font_size = font_size
        self.update_font()

        self.icon = None
        if icon_type:
            self.icon = self.create_icon(30, text_color)

    def create_icon(self, size, color):
        if self.icon_type == "play":
            return IconRenderer.create_play_icon(size, color)
        elif self.icon_type == "difficulty":
            return IconRenderer.create_difficulty_icon(size, color)
        elif self.icon_type == "stats":
            return IconRenderer.create_stats_icon(size, color)
        elif self.icon_type == "quit":
            return IconRenderer.create_quit_icon(size, color)
        elif self.icon_type == "back":
            return IconRenderer.create_back_icon(size, color)
        elif self.icon_type == "restart":
            return IconRenderer.create_restart_icon(size, color)
        elif self.icon_type == "flag":
            return IconRenderer.create_flag_icon(size, color)
        elif self.icon_type == "rocket":
            return IconRenderer.create_rocket_icon(size, color)
        elif self.icon_type == "crown":
            return IconRenderer.create_crown_icon(size, color)
        elif self.icon_type == "skull":
            return IconRenderer.create_skull_icon(size, color)
        elif self.icon_type == "target":
            return IconRenderer.create_target_icon(size, color)
        elif self.icon_type == "star":
            return IconRenderer.create_star_icon(size, color)
        elif self.icon_type == "checkmark":
            return IconRenderer.create_checkmark_icon(size, color)
        return None

    def update_font(self):
        try:
            test_font = pygame.font.SysFont('Arial Black', self.font_size)
            if not test_font:
                test_font = pygame.font.SysFont('Arial', self.font_size, bold=True)
        except:
            test_font = pygame.font.SysFont('Arial', self.font_size, bold=True)

        text_width, _ = test_font.size(self.text)

        while text_width > self.rect.width * 0.9 and self.font_size > 12:
            self.font_size -= 1
            try:
                test_font = pygame.font.SysFont('Arial Black', self.font_size)
                if not test_font:
                    test_font = pygame.font.SysFont('Arial', self.font_size, bold=True)
            except:
                test_font = pygame.font.SysFont('Arial', self.font_size, bold=True)
            text_width, _ = test_font.size(self.text)

        try:
            self.font = pygame.font.SysFont('Arial Black', self.font_size)
            if not self.font:
                self.font = pygame.font.SysFont('Arial', self.font_size, bold=True)
        except:
            self.font = pygame.font.SysFont('Arial', self.font_size, bold=True)

    def update_animation(self):
        if self.animation_delay > 0:
            self.animation_delay -= 0.016
            return True

        if self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + 0.1)
            ease_out = 1 - (1 - self.animation_progress) ** 3
            current_y = self.start_y + (self.target_y - self.start_y) * ease_out
            self.rect.y = current_y
            return True
        return False

    def draw(self, screen):
        if self.animation_delay > 0:
            return

        if self.is_active:
            color = self.active_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        alpha = int(255 * self.animation_progress)
        if alpha < 255:
            temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.draw_gradient_button(temp_surface, color)
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, self.rect.topleft)
        else:
            self.draw_gradient_button(screen, color)

        if alpha > 0:
            text_surface = self.font.render(self.text, True, self.text_color)
            if alpha < 255:
                text_surface.set_alpha(alpha)

            text_rect = text_surface.get_rect(center=self.rect.center)

            if self.icon:
                icon_rect = self.icon.get_rect(midright=(text_rect.left - 10, text_rect.centery))
                if alpha < 255:
                    icon_copy = self.icon.copy()
                    icon_copy.set_alpha(alpha)
                    screen.blit(icon_copy, icon_rect)
                else:
                    screen.blit(self.icon, icon_rect)

            screen.blit(text_surface, text_rect)

    def draw_gradient_button(self, screen, base_color):
        pygame.draw.rect(screen, base_color, self.rect, border_radius=self.border_radius)

        top_rect = pygame.Rect(self.rect.x, self.rect.y,
                               self.rect.width, self.rect.height // 2)
        top_color = self.lighten_color(base_color, 30)
        pygame.draw.rect(screen, top_color, top_rect, border_radius=self.border_radius)

        border_color = self.lighten_color(base_color, 50)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=self.border_radius)

        if self.is_hovered or self.is_active:
            shine = pygame.Surface((self.rect.width, 5), pygame.SRCALPHA)
            shine.fill((255, 255, 255, 100))
            screen.blit(shine, (self.rect.x, self.rect.y + 5))

    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def set_active(self, active):
        self.is_active = active

    def is_clicked(self, pos, event):
        if self.animation_delay > 0 or self.animation_progress < 0.8:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_active = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_active = False
        return False


class DifficultySelector:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.difficulties = [
            ("НОВИЧОК", Difficulty.BEGINNER, GREEN_TICK, 1),
            ("ЛЮБИТЕЛЬ", Difficulty.INTERMEDIATE, LIME_TICK, 2),
            ("ПРОДВИНУТЫЙ", Difficulty.ADVANCED, YELLOW_TICK, 3),
            ("ЭКСПЕРТ", Difficulty.EXPERT, RED_TICK, 4),
            ("МАСТЕР", Difficulty.MASTER, GOLD_CROWN, 0)
        ]
        self.selected_index = 0

        try:
            self.font = pygame.font.SysFont('Arial Black', 22)
            if not self.font:
                self.font = pygame.font.SysFont('Arial', 22, bold=True)
        except:
            self.font = pygame.font.SysFont('Arial', 22, bold=True)

        try:
            self.title_font = pygame.font.SysFont('Arial Black', 28)
            if not self.title_font:
                self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        except:
            self.title_font = pygame.font.SysFont('Arial', 28, bold=True)

        self.button_width = width // len(self.difficulties)
        self.button_height = 60

    def draw(self, screen):
        self.draw_panel_background(screen)

        title = self.title_font.render("ВЫБЕРИТЕ СЛОЖНОСТЬ", True, ACCENT_COLOR)
        title_rect = title.get_rect(centerx=self.rect.centerx, y=self.rect.y + 25)
        screen.blit(title, title_rect)

        selected_diff = self.difficulties[self.selected_index]
        info_text = self.get_difficulty_info(selected_diff[1])
        info_surface = self.font.render(info_text, True, TEXT_COLOR)
        info_rect = info_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 60)
        screen.blit(info_surface, info_rect)

        button_y = self.rect.y + 95
        for i, (name, diff, color, count) in enumerate(self.difficulties):
            button_rect = pygame.Rect(
                self.rect.x + i * self.button_width,
                button_y,
                self.button_width - 10,
                self.button_height
            )

            if i == self.selected_index:
                button_color = BUTTON_ACTIVE
                text_color = WHITE
            else:
                button_color = BUTTON_COLOR
                text_color = TEXT_COLOR

            self.draw_difficulty_button(screen, button_rect, button_color, name, text_color, color, count)

    def draw_panel_background(self, screen):
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 200), panel_surface.get_rect(),
                         border_radius=20)

        glass_effect = pygame.Surface((self.rect.width, self.rect.height // 3), pygame.SRCALPHA)
        glass_effect.fill((255, 255, 255, 30))
        panel_surface.blit(glass_effect, (0, 0))

        pygame.draw.rect(panel_surface, (*ACCENT_COLOR, 100), panel_surface.get_rect(),
                         3, border_radius=20)

        screen.blit(panel_surface, self.rect)

    def draw_difficulty_button(self, screen, rect, color, text, text_color, icon_color, count):
        pygame.draw.rect(screen, color, rect, border_radius=12)

        top_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 2)
        top_color = self.lighten_color(color, 30)
        pygame.draw.rect(screen, top_color, top_rect, border_radius=12)

        border_color = self.lighten_color(color, 50)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

        if count == 0:
            crown_icon = IconRenderer.create_crown_icon(25, icon_color)
            icon_rect = crown_icon.get_rect(center=(rect.centerx, rect.y + 25))
            screen.blit(crown_icon, icon_rect)
        else:
            center_x = rect.centerx
            center_y = rect.y + 25

            for i in range(count):
                icon = self.create_checkmark_icon(20, icon_color)
                offset_y = i * 4
                icon_rect = icon.get_rect(center=(center_x, center_y - offset_y))
                screen.blit(icon, icon_rect)

        font_size = 14
        try:
            font = pygame.font.SysFont('Arial Black', font_size)
            if not font:
                font = pygame.font.SysFont('Arial', font_size, bold=True)
        except:
            font = pygame.font.SysFont('Arial', font_size, bold=True)

        text_surface = font.render(text, True, text_color)

        while text_surface.get_width() > rect.width * 0.85 and font_size > 10:
            font_size -= 1
            try:
                font = pygame.font.SysFont('Arial Black', font_size)
                if not font:
                    font = pygame.font.SysFont('Arial', font_size, bold=True)
            except:
                font = pygame.font.SysFont('Arial', font_size, bold=True)
            text_surface = font.render(text, True, text_color)

        text_rect = text_surface.get_rect(centerx=rect.centerx, y=rect.y + 42)
        screen.blit(text_surface, text_rect)

    def create_checkmark_icon(self, size, color):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        points = [
            (size * 0.25, size * 0.5),
            (size * 0.5, size * 0.75),
            (size * 0.75, size * 0.25)
        ]
        pygame.draw.lines(surface, color, False, points, 3)

        return surface

    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)

    def get_difficulty_info(self, difficulty):
        if difficulty == Difficulty.BEGINNER:
            return "9×9 поле, 10 мин"
        elif difficulty == Difficulty.INTERMEDIATE:
            return "16×16 поле, 40 мин"
        elif difficulty == Difficulty.ADVANCED:
            return "16×30 поле, 99 мин"
        elif difficulty == Difficulty.EXPERT:
            return "20×30 поле, 150 мин"
        elif difficulty == Difficulty.MASTER:
            return "24×40 поле, 250 мин"
        return ""

    def check_click(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button_y = self.rect.y + 95
            for i in range(len(self.difficulties)):
                button_rect = pygame.Rect(
                    self.rect.x + i * self.button_width,
                    button_y,
                    self.button_width - 10,
                    self.button_height
                )
                if button_rect.collidepoint(pos):
                    self.selected_index = i
                    return self.difficulties[i][1]
        return None

    def get_selected_difficulty(self):
        return self.difficulties[self.selected_index][1]


class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        try:
            self.title_font = pygame.font.SysFont('Arial Black', 72)
            if not self.title_font:
                self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        except:
            self.title_font = pygame.font.SysFont('Arial', 72, bold=True)

        button_width = 300
        button_height = 70
        start_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 50

        self.play_button = Button(start_x, start_y, button_width, button_height,
                                  "ИГРАТЬ", icon_type="play", animation_delay=0.3)
        self.difficulty_button = Button(start_x, start_y + 90, button_width, button_height,
                                        "СЛОЖНОСТЬ", icon_type="difficulty", animation_delay=0.5)
        self.quit_button = Button(start_x, start_y + 180, button_width, button_height,
                                  "ВЫХОД", icon_type="quit", animation_delay=0.7)

        self.difficulty_selector = DifficultySelector(
            screen_width // 2 - 250, screen_height // 2 - 120, 500, 200
        )
        self.show_difficulty_selector = False

        self.back_button = Button(screen_width // 2 - 100, screen_height - 100,
                                  200, 50, "НАЗАД", icon_type="back")

        self.title_y = -100
        self.title_target_y = 180
        self.title_velocity = 0
        self.animation_time = 0
        self.buttons_animating = True

    def update(self):
        self.animation_time += 1

        diff = self.title_target_y - self.title_y
        self.title_velocity += diff * 0.05
        self.title_velocity *= 0.9
        self.title_y += self.title_velocity

        if abs(diff) < 0.5 and abs(self.title_velocity) < 0.5:
            self.title_y = self.title_target_y

        still_animating = False
        if self.play_button.update_animation():
            still_animating = True
        if self.difficulty_button.update_animation():
            still_animating = True
        if self.quit_button.update_animation():
            still_animating = True

        self.buttons_animating = still_animating

    def draw(self, screen, background):
        background.draw(screen)

        menu_bg = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        menu_bg.fill((0, 0, 0, 100))
        screen.blit(menu_bg, (0, 0))

        title = self.title_font.render("САПЕР", True, ACCENT_COLOR)
        title_shadow = self.title_font.render("САПЕР", True, (255, 255, 255, 50))

        title_rect = title.get_rect(centerx=self.screen_width // 2, y=int(self.title_y))
        shadow_rect = title_shadow.get_rect(centerx=self.screen_width // 2 + 4, y=int(self.title_y) + 4)

        for i in range(3):
            glow_size = 4 + i * 2
            glow_surface = pygame.Surface((title_rect.width + glow_size * 2,
                                           title_rect.height + glow_size * 2),
                                          pygame.SRCALPHA)
            glow_text = self.title_font.render("САПЕР", True, (*ACCENT_COLOR, 50 - i * 15))
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2,
                                                   glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
            screen.blit(glow_surface, (title_rect.x - glow_size, title_rect.y - glow_size))

        screen.blit(title_shadow, shadow_rect)
        screen.blit(title, title_rect)

        if self.show_difficulty_selector:
            self.difficulty_selector.draw(screen)
            self.back_button.draw(screen)
        else:
            self.play_button.draw(screen)
            self.difficulty_button.draw(screen)
            self.quit_button.draw(screen)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if self.show_difficulty_selector:
            self.back_button.check_hover(mouse_pos)

            if self.back_button.is_clicked(mouse_pos, event):
                self.show_difficulty_selector = False
                return "menu"

            selected = self.difficulty_selector.check_click(mouse_pos, event)
            if selected:
                return selected
        else:
            self.play_button.check_hover(mouse_pos)
            self.difficulty_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)

            if self.play_button.is_clicked(mouse_pos, event):
                return "play"

            if self.difficulty_button.is_clicked(mouse_pos, event):
                self.show_difficulty_selector = True
                return "difficulty_menu"

            if self.quit_button.is_clicked(mouse_pos, event):
                return "quit"

        return None


class MinesweeperGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Сапер")
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = AnimatedBackground(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.state = "MENU"
        self.difficulty = Difficulty.BEGINNER

        self.rows = 9
        self.cols = 9
        self.mines = 10
        self.cell_size = 50
        self.board_offset_x = 0
        self.board_offset_y = 0

        self.board = None

        try:
            self.font_small = pygame.font.SysFont('Arial Black', 20)
            if not self.font_small:
                self.font_small = pygame.font.SysFont('Arial', 20, bold=True)
        except:
            self.font_small = pygame.font.SysFont('Arial', 20, bold=True)

        try:
            self.font_medium = pygame.font.SysFont('Arial Black', 28)
            if not self.font_medium:
                self.font_medium = pygame.font.SysFont('Arial', 28, bold=True)
        except:
            self.font_medium = pygame.font.SysFont('Arial', 28, bold=True)

        try:
            self.font_large = pygame.font.SysFont('Arial Black', 48)
            if not self.font_large:
                self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        except:
            self.font_large = pygame.font.SysFont('Arial', 48, bold=True)

        try:
            self.font_huge = pygame.font.SysFont('Arial Black', 72)
            if not self.font_huge:
                self.font_huge = pygame.font.SysFont('Arial', 72, bold=True)
        except:
            self.font_huge = pygame.font.SysFont('Arial', 72, bold=True)

        self.menu_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80,
                                  200, 50, "МЕНЮ", icon_type="back")
        self.restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 140,
                                     200, 50, "ЗАНОВО", icon_type="restart")

        self.stats = {
            Difficulty.BEGINNER: {"best_time": None, "games_played": 0, "games_won": 0},
            Difficulty.INTERMEDIATE: {"best_time": None, "games_played": 0, "games_won": 0},
            Difficulty.ADVANCED: {"best_time": None, "games_played": 0, "games_won": 0},
            Difficulty.EXPERT: {"best_time": None, "games_played": 0, "games_won": 0},
            Difficulty.MASTER: {"best_time": None, "games_played": 0, "games_won": 0}
        }

        self.stats_updated = False

        self.load_stats()

    def init_game(self, difficulty):
        self.difficulty = difficulty

        if difficulty == Difficulty.BEGINNER:
            self.rows = 9
            self.cols = 9
            self.mines = 10
            self.cell_size = 50
        elif difficulty == Difficulty.INTERMEDIATE:
            self.rows = 16
            self.cols = 16
            self.mines = 40
            self.cell_size = 35
        elif difficulty == Difficulty.ADVANCED:
            self.rows = 16
            self.cols = 30
            self.mines = 99
            self.cell_size = 28
        elif difficulty == Difficulty.EXPERT:
            self.rows = 20
            self.cols = 30
            self.mines = 150
            self.cell_size = 25
        elif difficulty == Difficulty.MASTER:
            self.rows = 24
            self.cols = 40
            self.mines = 250
            self.cell_size = 22

        board_width = self.cols * self.cell_size
        board_height = self.rows * self.cell_size
        self.board_offset_x = (SCREEN_WIDTH - board_width) // 2
        self.board_offset_y = (SCREEN_HEIGHT - board_height) // 2 - 30

        min_board_y = 100
        if self.board_offset_y < min_board_y:
            self.board_offset_y = min_board_y

        board_bottom = self.board_offset_y + board_height
        if board_bottom > SCREEN_HEIGHT - 160:
            self.board_offset_y = SCREEN_HEIGHT - 160 - board_height

        self.board = Board(self.rows, self.cols, self.mines, difficulty)

        self.stats_updated = False

        self.state = "PLAYING"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if (self.state == "GAME_OVER" or self.state == "GAME_WON") and event.key == pygame.K_r:
                    self.init_game(self.difficulty)
                elif (self.state == "GAME_OVER" or self.state == "GAME_WON") and event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.main_menu.show_difficulty_selector = False
                elif self.state == "PLAYING" and event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.main_menu.show_difficulty_selector = False

            if self.state == "MENU":
                result = self.main_menu.handle_event(event)

                if result == "quit":
                    self.running = False
                elif result == "play":
                    self.init_game(self.difficulty)
                elif isinstance(result, Difficulty):
                    self.difficulty = result
                    self.main_menu.show_difficulty_selector = False
                elif result == "difficulty_menu":
                    pass
                elif result == "menu":
                    pass

            elif self.state == "PLAYING":
                mouse_pos = pygame.mouse.get_pos()

                self.restart_button.check_hover(mouse_pos)
                self.menu_button.check_hover(mouse_pos)

                if self.restart_button.is_clicked(mouse_pos, event):
                    self.init_game(self.difficulty)

                if self.menu_button.is_clicked(mouse_pos, event):
                    self.state = "MENU"
                    self.main_menu.show_difficulty_selector = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    board_x = mouse_pos[0] - self.board_offset_x
                    board_y = mouse_pos[1] - self.board_offset_y

                    if (0 <= board_x < self.cols * self.cell_size and
                            0 <= board_y < self.rows * self.cell_size):
                        col = board_x // self.cell_size
                        row = board_y // self.cell_size

                        if event.button == 1:
                            if not self.board.reveal(row, col):
                                if self.board.game_over:
                                    self.state = "GAME_OVER"
                                    if not self.stats_updated:
                                        self.update_stats(False)
                                        self.stats_updated = True
                                elif self.board.game_won:
                                    self.state = "GAME_WON"
                                    if not self.stats_updated:
                                        self.update_stats(True)
                                        self.stats_updated = True

                        elif event.button == 3:
                            self.board.toggle_flag(row, col)

                        elif event.button == 2:
                            self.board.toggle_question(row, col)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if not self.board.game_over and not self.board.game_won:
                        board_x = mouse_pos[0] - self.board_offset_x
                        board_y = mouse_pos[1] - self.board_offset_y

                        if (0 <= board_x < self.cols * self.cell_size and
                                0 <= board_y < self.rows * self.cell_size):
                            col = board_x // self.cell_size
                            row = board_y // self.cell_size

                            if self.board.grid[row][col].is_revealed:
                                self.board.chord(row, col)

                                if self.board.game_over:
                                    self.state = "GAME_OVER"
                                    if not self.stats_updated:
                                        self.update_stats(False)
                                        self.stats_updated = True
                                elif self.board.game_won:
                                    self.state = "GAME_WON"
                                    if not self.stats_updated:
                                        self.update_stats(True)
                                        self.stats_updated = True

            elif self.state == "GAME_OVER" or self.state == "GAME_WON":
                mouse_pos = pygame.mouse.get_pos()
                self.restart_button.check_hover(mouse_pos)
                self.menu_button.check_hover(mouse_pos)

                if self.restart_button.is_clicked(mouse_pos, event):
                    self.init_game(self.difficulty)

                if self.menu_button.is_clicked(mouse_pos, event):
                    self.state = "MENU"
                    self.main_menu.show_difficulty_selector = False

    def update_stats(self, won):
        if self.stats_updated:
            return

        stats = self.stats[self.difficulty]
        stats["games_played"] += 1

        if won:
            stats["games_won"] += 1
            game_time = self.board.get_time()

            if stats["best_time"] is None or game_time < stats["best_time"]:
                stats["best_time"] = game_time

        self.save_stats()
        self.stats_updated = True

    def save_stats(self):
        try:
            stats_dict = {}
            for diff, stats in self.stats.items():
                stats_dict[diff.value] = {
                    "best_time": stats["best_time"],
                    "games_played": stats["games_played"],
                    "games_won": stats["games_won"]
                }

            with open("minesweeper_stats.json", "w") as f:
                json.dump(stats_dict, f, indent=2)
        except:
            pass

    def load_stats(self):
        try:
            if os.path.exists("minesweeper_stats.json"):
                with open("minesweeper_stats.json", "r") as f:
                    stats_dict = json.load(f)

                    for diff_value, stats in stats_dict.items():
                        for diff in Difficulty:
                            if diff.value == int(diff_value):
                                self.stats[diff] = {
                                    "best_time": stats["best_time"],
                                    "games_played": stats["games_played"],
                                    "games_won": stats["games_won"]
                                }
                                break
        except:
            pass

    def draw(self):
        self.background.update()

        if self.state == "MENU":
            self.main_menu.update()
            self.main_menu.draw(self.screen, self.background)
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "GAME_OVER":
            self.draw_game()
            self.draw_game_over()
        elif self.state == "GAME_WON":
            self.draw_game()
            self.draw_game_won()

        pygame.display.flip()

    def draw_game(self):
        self.background.draw(self.screen)

        info_panel_height = 100
        info_panel = pygame.Rect(0, 0, SCREEN_WIDTH, info_panel_height)
        panel_surface = pygame.Surface((SCREEN_WIDTH, info_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 200), panel_surface.get_rect())

        glass_effect = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
        glass_effect.fill((255, 255, 255, 30))
        panel_surface.blit(glass_effect, (0, 0))

        self.screen.blit(panel_surface, (0, 0))

        if self.board:
            if self.board.update_animations():
                pass

            for r in range(self.board.rows):
                for c in range(self.board.cols):
                    cell = self.board.grid[r][c]
                    rect = pygame.Rect(
                        self.board_offset_x + c * self.cell_size,
                        self.board_offset_y + r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )

                    if not cell.is_revealed and cell.animation_progress < 1.0:
                        animated_rect = pygame.Rect(
                            rect.x,
                            rect.y,
                            int(rect.width * cell.animation_progress),
                            int(rect.height * cell.animation_progress)
                        )
                        animated_rect.center = rect.center
                        self.draw_3d_cell(self.screen, animated_rect, cell)

                        if cell.is_flagged:
                            flag_rect = animated_rect.copy()
                            flag_rect.width = int(rect.width * cell.animation_progress * 0.8)
                            flag_rect.height = int(rect.height * cell.animation_progress * 0.8)
                            flag_rect.center = rect.center
                            self.draw_flag(self.screen, flag_rect, cell)
                        elif cell.is_question:
                            question_rect = animated_rect.copy()
                            question_rect.width = int(rect.width * cell.animation_progress * 0.8)
                            question_rect.height = int(rect.height * cell.animation_progress * 0.8)
                            question_rect.center = rect.center
                            self.draw_question(self.screen, question_rect, cell)
                    else:
                        if cell.is_revealed:
                            pygame.draw.rect(self.screen, (240, 240, 245), rect)

                            if cell.is_mine:
                                if self.board.game_over:
                                    pygame.draw.circle(self.screen, RED, rect.center, self.cell_size // 3)
                                    for i in range(8):
                                        angle = i * 45
                                        rad = math.radians(angle)
                                        end_x = rect.centerx + int(self.cell_size // 2 * math.cos(rad))
                                        end_y = rect.centery + int(self.cell_size // 2 * math.sin(rad))
                                        pygame.draw.line(self.screen, (255, 150, 50), rect.center, (end_x, end_y), 3)
                                elif cell.is_flagged:
                                    pygame.draw.rect(self.screen, (200, 255, 200), rect)
                                    pygame.draw.circle(self.screen, GREEN, rect.center, self.cell_size // 4)
                            elif cell.neighbor_mines > 0:
                                color = self.get_number_color(cell.neighbor_mines)
                                number = self.font_medium.render(str(cell.neighbor_mines), True, color)
                                number_rect = number.get_rect(center=rect.center)
                                self.screen.blit(number, number_rect)
                        else:
                            self.draw_3d_cell(self.screen, rect, cell)

                        if not cell.is_revealed:
                            if cell.is_flagged:
                                self.draw_flag(self.screen, rect, cell)
                            elif cell.is_question:
                                self.draw_question(self.screen, rect, cell)

                    pygame.draw.rect(self.screen, (100, 100, 120), rect, 1)

        if self.board:
            time_text = self.font_large.render(f"Время: {self.board.get_time():.1f}", True, TEXT_COLOR)
            self.screen.blit(time_text, (20, 30))

            mines_left = self.board.mines - self.board.flags_placed
            mines_text = self.font_large.render(f"Мины: {mines_left}", True, TEXT_COLOR)
            mines_x = SCREEN_WIDTH - mines_text.get_width() - 20
            self.screen.blit(mines_text, (mines_x, 30))

            diff_names = {
                Difficulty.BEGINNER: "НОВИЧОК",
                Difficulty.INTERMEDIATE: "ЛЮБИТЕЛЬ",
                Difficulty.ADVANCED: "ПРОДВИНУТЫЙ",
                Difficulty.EXPERT: "ЭКСПЕРТ",
                Difficulty.MASTER: "МАСТЕР"
            }
            diff_text = self.font_medium.render(diff_names[self.difficulty], True, ACCENT_COLOR)
            diff_rect = diff_text.get_rect(centerx=SCREEN_WIDTH // 2, y=25)
            self.screen.blit(diff_text, diff_rect)

            size_text = self.font_medium.render(f"{self.rows}×{self.cols} | {self.mines} мин", True, TEXT_COLOR)
            size_rect = size_text.get_rect(centerx=SCREEN_WIDTH // 2, y=60)
            self.screen.blit(size_text, size_rect)

        self.restart_button.rect.y = SCREEN_HEIGHT - 140
        self.menu_button.rect.y = SCREEN_HEIGHT - 80
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def draw_3d_cell(self, screen, rect, cell):
        base_color = (180, 190, 210) if cell.highlight else (160, 170, 190)
        pygame.draw.rect(screen, base_color, rect)

        pygame.draw.line(screen, (220, 230, 240),
                         (rect.left, rect.top), (rect.right, rect.top), 2)
        pygame.draw.line(screen, (220, 230, 240),
                         (rect.left, rect.top), (rect.left, rect.bottom), 2)

        pygame.draw.line(screen, (120, 130, 150),
                         (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 2)
        pygame.draw.line(screen, (120, 130, 150),
                         (rect.right - 1, rect.top), (rect.right - 1, rect.bottom), 2)

    def draw_flag(self, screen, rect, cell):
        pole_start = (rect.centerx - rect.width // 4, rect.centery + rect.height // 4)
        pole_end = (rect.centerx - rect.width // 4, rect.centery - rect.height // 4)
        pygame.draw.line(screen, BLACK, pole_start, pole_end, 2)

        flag_color = RED
        if self.board and self.board.game_over and not cell.is_mine:
            flag_color = (255, 100, 100)
        elif self.board and self.board.game_won and cell.is_mine:
            flag_color = GREEN

        flag_points = [
            (rect.centerx - rect.width // 4, rect.centery - rect.height // 4),
            (rect.centerx + rect.width // 4, rect.centery - rect.height // 8),
            (rect.centerx - rect.width // 4, rect.centery)
        ]
        pygame.draw.polygon(screen, flag_color, flag_points)

    def draw_question(self, screen, rect, cell):
        question_color = BLUE
        question = self.font_medium.render("?", True, question_color)
        question_rect = question.get_rect(center=rect.center)
        screen.blit(question, question_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_width = 500
        panel_height = 220
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 240), panel_surface.get_rect(), border_radius=20)
        pygame.draw.rect(panel_surface, (255, 100, 100, 150), panel_surface.get_rect(), 4, border_radius=20)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        game_over_text = self.font_huge.render("ПОРАЖЕНИЕ", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 70))
        self.screen.blit(game_over_text, game_over_rect)

        if self.board:
            time_text = self.font_large.render(f"Время: {self.board.get_time():.1f} сек", True, TEXT_COLOR)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 140))
            self.screen.blit(time_text, time_rect)

        hint_text = self.font_medium.render("R - Начать заново    ESC - В меню", True, TEXT_COLOR)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 180))
        self.screen.blit(hint_text, hint_rect)

    def draw_game_won(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_width = 500
        panel_height = 250
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*PANEL_BG, 240), panel_surface.get_rect(), border_radius=20)
        pygame.draw.rect(panel_surface, (100, 255, 100, 150), panel_surface.get_rect(), 4, border_radius=20)

        self.screen.blit(panel_surface, (panel_x, panel_y))

        game_won_text = self.font_huge.render("ПОБЕДА!", True, (100, 255, 100))
        game_won_rect = game_won_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 70))
        self.screen.blit(game_won_text, game_won_rect)

        if self.board:
            time_text = self.font_large.render(f"Время: {self.board.get_time():.1f} сек", True, TEXT_COLOR)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 140))
            self.screen.blit(time_text, time_rect)

            stats = self.stats[self.difficulty]
            if stats["best_time"] is not None and abs(self.board.get_time() - stats["best_time"]) < 0.01:
                record_text = self.font_medium.render("НОВЫЙ РЕКОРД!", True, YELLOW)
                record_rect = record_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 180))
                self.screen.blit(record_text, record_rect)

        hint_text = self.font_medium.render("R - Начать заново    ESC - В меню", True, TEXT_COLOR)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 210))
        self.screen.blit(hint_text, hint_rect)

    def get_number_color(self, number):
        colors = {
            1: BLUE,
            2: GREEN,
            3: RED,
            4: PURPLE,
            5: (178, 34, 34),
            6: (64, 224, 208),
            7: BLACK,
            8: (128, 128, 128)
        }
        return colors.get(number, BLACK)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MinesweeperGame()
    game.run()
