import pygame
import os
import sys
from gui.constants import (
    TILE_SIZE, FPS, COLOR_BG, COLOR_TEXT, COLOR_PANEL, COLOR_STATUS,
    KEY_PAUSE, KEY_FORWARD, KEY_BACKWARD
)

class SokobanView:
    """
    Game Engine & Pygame Visualization.
    Quy uoc ky hieu ban do theo dung de bai:
      '%' : Wall / Obstacles
      'A' : Player 1 (the man)
      'P' : Player 2 (Che do doi khang 2 Agent)
      'B' : Box (Thung)
      'D' : Goal (Diem dich dat thung - cham do)
      'C' : Box on Goal (Thung da nam tren diem dich - mau nau dam)
      ' ' : Blank cell (San nha)
    """
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

    def _load_sprites(self):
        """Load anh tu assets neu co."""
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        elements = ["player", "player2", "box", "box_docked", "target", "wall", "floor"]
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

    def set_states(self, states):
        self.history_states = states
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
        
        # Load sprite sau khi da co display surface
        self._load_sprites()

    def draw_cell(self, char, x, y):
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # 1. Ve san nha (Blank cells)
        if self.sprites.get("floor"):
            self.screen.blit(self.sprites["floor"], (x, y))
        else:
            pygame.draw.rect(self.screen, (40, 44, 52), rect)
            pygame.draw.rect(self.screen, (55, 60, 70), rect, 1)

        # 2. Tuong (Walls / Obstacles): Ky tu '%'
        if char == "%":
            if self.sprites.get("wall"):
                self.screen.blit(self.sprites["wall"], (x, y))
            else:
                pygame.draw.rect(self.screen, (90, 95, 105), rect)
                pygame.draw.rect(self.screen, (40, 44, 52), rect, 3)

        # 3. Diem dich (Designated positions of boxes - red points): Ky tu 'D'
        elif char == "D":
            if self.sprites.get("target"):
                self.screen.blit(self.sprites["target"], (x, y))
            else:
                pygame.draw.circle(self.screen, (220, 20, 60), rect.center, TILE_SIZE // 4)
                pygame.draw.circle(self.screen, (255, 100, 100), rect.center, TILE_SIZE // 7)

        # 4. Thung (Boxes): Ky tu 'B'
        elif char == "B":
            if self.sprites.get("box"):
                self.screen.blit(self.sprites["box"], (x, y))
            else:
                box_rect = rect.inflate(-14, -14)
                pygame.draw.rect(self.screen, (210, 140, 70), box_rect, border_radius=6)
                pygame.draw.rect(self.screen, (150, 80, 30), box_rect, 3, border_radius=6)
                pygame.draw.line(self.screen, (150, 80, 30), box_rect.topleft, box_rect.bottomright, 2)
                pygame.draw.line(self.screen, (150, 80, 30), box_rect.bottomleft, box_rect.topright, 2)

        # 5. Thung da nam tren dich (Box on Goal - dark brown boxes): Ky tu 'C'
        elif char == "C":
            if self.sprites.get("box_docked"):
                self.screen.blit(self.sprites["box_docked"], (x, y))
            else:
                box_rect = rect.inflate(-14, -14)
                pygame.draw.rect(self.screen, (110, 55, 25), box_rect, border_radius=6)
                pygame.draw.rect(self.screen, (220, 20, 60), box_rect, 3, border_radius=6)
                pygame.draw.circle(self.screen, (220, 20, 60), box_rect.center, 6)

        # 6. Nguoi choi 1 (Player 1 / the man): Ky tu 'A'
        elif char == "A":
            if self.sprites.get("player"):
                self.screen.blit(self.sprites["player"], (x, y))
            else:
                pygame.draw.circle(self.screen, (30, 144, 255), rect.center, TILE_SIZE // 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (rect.centerx - 6, rect.centery - 4), 4)
                pygame.draw.circle(self.screen, (255, 255, 255), (rect.centerx + 6, rect.centery - 4), 4)

        # 7. Nguoi choi 2 o che do doi khang (Player 2): Ky tu 'P'
        elif char == "P":
            if self.sprites.get("player2"):
                self.screen.blit(self.sprites["player2"], (x, y))
            else:
                pygame.draw.circle(self.screen, (255, 140, 0), rect.center, TILE_SIZE // 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (rect.centerx - 6, rect.centery - 4), 4)
                pygame.draw.circle(self.screen, (255, 255, 255), (rect.centerx + 6, rect.centery - 4), 4)

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