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
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.small_font = pygame.font.SysFont("Consolas", 14)
        self.clock = pygame.time.Clock()
        
        self.history_states = []
        self.current_step = 0
        self.is_paused = True
        self.running = False
        
        self.screen = None
        self.grid_width = 0
        self.grid_height = 0
        self.panel_height = 80
        self.sprites = {}
        self._load_sprites()

    def _load_sprites(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        elements = ["player", "box", "target", "wall", "floor"]
        for elem in elements:
            path = os.path.join(assets_dir, f"{elem}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.sprites[elem] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            else:
                self.sprites[elem] = None

    def load_map_from_file(self, file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\r\n") for line in f.readlines() if line.strip()]
        max_len = max(len(l) for l in lines) if lines else 0
        return [list(line.ljust(max_len)) for line in lines]

    def set_states(self, states):
        self.history_states = states
        self.current_step = 0
        if states:
            self._setup_screen(states[0])

    def _setup_screen(self, sample_state):
        grid = sample_state.grid if hasattr(sample_state, 'grid') else sample_state
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if self.grid_height > 0 else 0
        
        screen_w = max(self.grid_width * TILE_SIZE, 600)
        screen_h = self.grid_height * TILE_SIZE + self.panel_height
        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption(self.title)

    def draw_cell(self, char, x, y):
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # 1. Vẽ sàn nhà mặc định
        if self.sprites.get("floor"):
            self.screen.blit(self.sprites["floor"], (x, y))
        else:
            pygame.draw.rect(self.screen, (40, 44, 52), rect)
            pygame.draw.rect(self.screen, (55, 60, 70), rect, 1)

        # 2. Tường: Ký tự '%' hoặc '#'
        if char in ["%", "#"]:
            if self.sprites.get("wall"):
                self.screen.blit(self.sprites["wall"], (x, y))
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), rect)
                
        # 3. Điểm đích: Ký tự 'D' hoặc '.'
        elif char in ["D", "."]:
            if self.sprites.get("target"):
                self.screen.blit(self.sprites["target"], (x, y))
            else:
                pygame.draw.circle(self.screen, (220, 20, 60), rect.center, TILE_SIZE // 4)
                
        # 4. Thùng/Hộp: Ký tự 'C' hoặc '$'
        elif char in ["C", "$"]:
            if self.sprites.get("box"):
                self.screen.blit(self.sprites["box"], (x, y))
            else:
                pygame.draw.rect(self.screen, (205, 133, 63), rect.inflate(-16, -16), border_radius=6)
                
        # 5. Người chơi 1: Ký tự 'A' hoặc '@'
        elif char in ["A", "@"]:
            if self.sprites.get("player"):
                self.screen.blit(self.sprites["player"], (x, y))
            else:
                # Vẽ hình tròn xanh dương cho Player 1
                pygame.draw.circle(self.screen, (30, 144, 255), rect.center, TILE_SIZE // 3)
                
        # 6. Người chơi 2 (Dành cho chế độ đối kháng Competitive Two-Agent): Ký tự 'B'
        elif char == "B":
            # Vẽ hình tròn màu cam/vàng cho Player 2
            pygame.draw.circle(self.screen, (255, 140, 0), rect.center, TILE_SIZE // 3)

    def draw_panel(self):
        screen_w = self.screen.get_width()
        panel_rect = pygame.Rect(0, self.grid_height * TILE_SIZE, screen_w, self.panel_height)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)
        pygame.draw.line(self.screen, (70, 75, 85), (0, panel_rect.top), (screen_w, panel_rect.top), 2)
        
        status_txt = "PAUSED" if self.is_paused else "PLAYING"
        status_surf = self.font.render(f"Trang thai: {status_txt}", True, COLOR_STATUS)
        self.screen.blit(status_surf, (20, panel_rect.top + 12))
        
        total_steps = max(0, len(self.history_states) - 1)
        step_surf = self.font.render(f"Buoc: {self.current_step} / {total_steps}", True, COLOR_TEXT)
        self.screen.blit(step_surf, (screen_w - 200, panel_rect.top + 12))
        
        guide_txt = "Space: Pause/Resume | [->]: Buoc toi | [<-]: Lui buoc | ESC: Thoat"
        guide_surf = self.small_font.render(guide_txt, True, (180, 180, 180))
        self.screen.blit(guide_surf, (20, panel_rect.top + 48))

    def render(self, state):
        self.screen.fill(COLOR_BG)
        grid = state.grid if hasattr(state, 'grid') else state
        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                self.draw_cell(char, c * TILE_SIZE, r * TILE_SIZE)
        self.draw_panel()
        pygame.display.flip()

    def run_interactive(self):
        if not self.history_states:
            return
        self.running = True
        auto_tick = 0
        while self.running:
            self.clock.tick(FPS)
            auto_tick += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == KEY_PAUSE:
                        self.is_paused = not self.is_paused
                    elif event.key == KEY_FORWARD:
                        if self.current_step < len(self.history_states) - 1:
                            self.current_step += 1
                    elif event.key == KEY_BACKWARD:
                        if self.current_step > 0:
                            self.current_step -= 1

            if not self.is_paused and auto_tick >= (FPS // 2):
                auto_tick = 0
                if self.current_step < len(self.history_states) - 1:
                    self.current_step += 1
                else:
                    self.is_paused = True

            current_state = self.history_states[self.current_step]
            self.render(current_state)
        pygame.quit()