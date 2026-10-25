"""
Module: gui/game_view.py
Mo ta: Lop SokobanView quan ly giao dien do hoa Pygame cho che do don tac nhan va doi khang.
"""

import pygame
import os
import sys
from gui.constants import (
    TILE_SIZE, FPS, COLOR_BG, COLOR_TEXT, COLOR_PANEL, COLOR_STATUS,
    KEY_PAUSE, KEY_FORWARD, KEY_BACKWARD
)


class SokobanView:
    def __init__(self, title="AI Sokoban Visualization"):
        pygame.init()
        pygame.font.init()
        self.title = title
        self.font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.small_font = pygame.font.SysFont("Consolas", 13)
        self.clock = pygame.time.Clock()

        self.history_states = []
        self.current_step = 0
        self.is_paused = True
        self.running = False
        self.algorithm_name = "UCS"
        self.mode = "single"
        self.history_scores = []
        self.max_steps = 0

        self.screen = None
        self.grid_width = 0
        self.grid_height = 0
        self.panel_height = 95
        self.sprites = {}

    def _load_sprites(self):
        # Nap bo anh tu thu muc gui/assets
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        elements = ["player", "player2", "box", "box_docked", "box_p2", "target", "wall", "floor"]
        for elem in elements:
            path = os.path.join(assets_dir, f"{elem}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    self.sprites[elem] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                except Exception:
                    self.sprites[elem] = None
            else:
                self.sprites[elem] = None

    def load_map_from_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"Khong tim thay file ban do: {file_path}")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\r\n") for line in f.readlines() if line.strip()]
        max_len = max(len(l) for l in lines) if lines else 0
        return [list(line.ljust(max_len)) for line in lines]

    def set_states(self, states, algorithm="UCS"):
        # Thiet lap lich su trang thai cho che do don tac nhan
        self.history_states = states
        self.current_step = 0
        self.algorithm_name = algorithm
        if states:
            self._setup_screen(states[0])

    def set_competitive_history(self, states, scores, max_steps):
        # Thiet lap lich su trang thai cho che do doi khang 2 tac nhan
        self.mode = "competitive"
        self.history_states = states
        self.history_scores = scores
        self.max_steps = max_steps
        self.current_step = 0
        if states:
            self._setup_screen(states[0])

    def _setup_screen(self, sample_state):
        grid = sample_state.grid if hasattr(sample_state, 'grid') else sample_state
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if self.grid_height > 0 else 0

        screen_w = max(self.grid_width * TILE_SIZE, 640)
        screen_h = self.grid_height * TILE_SIZE + self.panel_height
        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption(self.title)

        self._load_sprites()

    def draw_cell(self, char, x, y):
        # Ve mot o tren luoi ban do
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        # San nha
        if self.sprites.get("floor"):
            self.screen.blit(self.sprites["floor"], (x, y))
        else:
            pygame.draw.rect(self.screen, (40, 44, 52), rect)
            pygame.draw.rect(self.screen, (55, 60, 70), rect, 1)

        # Tuong
        if char == "%":
            if self.sprites.get("wall"):
                self.screen.blit(self.sprites["wall"], (x, y))
            else:
                pygame.draw.rect(self.screen, (90, 95, 105), rect)

        # Diem dich
        elif char == "D":
            if self.sprites.get("target"):
                self.screen.blit(self.sprites["target"], (x, y))
            else:
                pygame.draw.circle(self.screen, (220, 20, 60), rect.center, TILE_SIZE // 4)

        # Hop
        elif char == "B":
            if self.sprites.get("box"):
                self.screen.blit(self.sprites["box"], (x, y))
            else:
                pygame.draw.rect(self.screen, (205, 133, 63), rect.inflate(-16, -16), border_radius=6)

        # Hop tren dich boi Player 1
        elif char == "C":
            if self.sprites.get("box_docked"):
                self.screen.blit(self.sprites["box_docked"], (x, y))
            elif self.sprites.get("box"):
                self.screen.blit(self.sprites["box"], (x, y))
            else:
                pygame.draw.rect(self.screen, (139, 69, 19), rect.inflate(-16, -16), border_radius=6)

        # Nguoi choi 1 dung tren dich
        elif char == "+":
            if self.sprites.get("target"):
                self.screen.blit(self.sprites["target"], (x, y))
            if self.sprites.get("player"):
                self.screen.blit(self.sprites["player"], (x, y))
            else:
                pygame.draw.circle(self.screen, (30, 144, 255), rect.center, TILE_SIZE // 3)

        # Nguoi choi 1
        elif char == "A":
            if self.sprites.get("player"):
                self.screen.blit(self.sprites["player"], (x, y))
            else:
                pygame.draw.circle(self.screen, (30, 144, 255), rect.center, TILE_SIZE // 3)

        # Nguoi choi 2
        elif char == "P":
            if self.sprites.get("player2"):
                self.screen.blit(self.sprites["player2"], (x, y))
            else:
                pygame.draw.circle(self.screen, (255, 140, 0), rect.center, TILE_SIZE // 3)

        # Hop tren dich boi Player 2
        elif char == "K":
            if self.sprites.get("box_p2"):
                self.screen.blit(self.sprites["box_p2"], (x, y))
            else:
                box_rect = rect.inflate(-14, -14)
                pygame.draw.rect(self.screen, (30, 130, 180), box_rect, border_radius=6)
                pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 3, border_radius=6)

    def draw_panel(self):
        # Ve bang dieu khien o duoi man hinh
        screen_w = self.screen.get_width()
        panel_rect = pygame.Rect(0, self.grid_height * TILE_SIZE, screen_w, self.panel_height)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)
        pygame.draw.line(self.screen, (255, 69, 0), (0, self.grid_height * TILE_SIZE), (screen_w, self.grid_height * TILE_SIZE), 2)

        total_steps = len(self.history_states) - 1
        status_text = "PAUSED" if self.is_paused else "PLAYING"
        status_color = (255, 165, 0) if self.is_paused else COLOR_STATUS

        # Hien thi theo che do don tac nhan hoac doi khang
        if self.mode == "single":
            txt_info = self.font.render(f"Thuat toan: {self.algorithm_name}", True, (0, 191, 255))
            txt_step = self.font.render(f"Buoc: {self.current_step} / {total_steps}", True, COLOR_TEXT)
            self.screen.blit(txt_info, (20, self.grid_height * TILE_SIZE + 15))
            self.screen.blit(txt_step, (screen_w - txt_step.get_width() - 20, self.grid_height * TILE_SIZE + 15))
        else:
            s1, s2 = 0, 0
            if self.history_scores and self.current_step < len(self.history_scores):
                s1, s2 = self.history_scores[self.current_step]
            txt_scores = self.font.render(f"P1 (A): {s1} diem   vs   P2 (P): {s2} diem", True, (0, 255, 255))
            txt_step = self.font.render(f"Buoc: {self.current_step} / {self.max_steps}", True, COLOR_TEXT)
            self.screen.blit(txt_scores, (20, self.grid_height * TILE_SIZE + 15))
            self.screen.blit(txt_step, (screen_w - txt_step.get_width() - 20, self.grid_height * TILE_SIZE + 15))

        txt_status = self.font.render(f"Trang thai: {status_text}", True, status_color)
        self.screen.blit(txt_status, (screen_w // 2 - txt_status.get_width() // 2, self.grid_height * TILE_SIZE + 35))

        guide = "Space: Pause/Resume | [->]: Buoc toi | [<-]: Lui buoc | ESC: Thoat"
        txt_guide = self.small_font.render(guide, True, (160, 160, 160))
        self.screen.blit(txt_guide, (screen_w // 2 - txt_guide.get_width() // 2, self.grid_height * TILE_SIZE + 68))

    def run(self):
        # Vong lap chinh cua giao dien Pygame
        self.running = True
        step_delay = 350
        last_step_time = pygame.time.get_ticks()

        while self.running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()

            # Xu ly su kien ban phim
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == KEY_PAUSE:
                        self.is_paused = not self.is_paused
                    elif event.key == KEY_FORWARD and self.is_paused:
                        if self.current_step < len(self.history_states) - 1:
                            self.current_step += 1
                    elif event.key == KEY_BACKWARD and self.is_paused:
                        if self.current_step > 0:
                            self.current_step -= 1

            # Tu dong chay buoc tiep theo neu khong tam dung
            if not self.is_paused and now - last_step_time > step_delay:
                if self.current_step < len(self.history_states) - 1:
                    self.current_step += 1
                    last_step_time = now
                else:
                    self.is_paused = True

            self.screen.fill(COLOR_BG)

            # Ve luoi ban do hien tai
            if self.history_states and self.current_step < len(self.history_states):
                cur_grid = self.history_states[self.current_step]
                for r in range(self.grid_height):
                    for c in range(self.grid_width):
                        char = cur_grid[r][c] if r < len(cur_grid) and c < len(cur_grid[r]) else " "
                        self.draw_cell(char, c * TILE_SIZE, r * TILE_SIZE)

            self.draw_panel()
            pygame.display.flip()

        pygame.quit()
