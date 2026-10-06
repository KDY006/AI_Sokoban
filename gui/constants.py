# gui/constants.py
import pygame

# 1. Kích thước ô lưới và tốc độ khung hình
TILE_SIZE = 64  # Mỗi ô trên map có kích thước 64x64 pixel
FPS = 60        # 60 khung hình/giây

# 2. Bảng màu RGB hiển thị
COLOR_BG = (35, 39, 42)          # Màu nền tối
COLOR_TEXT = (255, 255, 255)      # Chữ màu trắng
COLOR_PANEL = (44, 47, 51)        # Khung viền/thông tin
COLOR_STATUS = (0, 255, 127)      # Màu chữ trạng thái (xanh lá)

# 3. Cấu hình các phím điều khiển (Yêu cầu đề bài)
KEY_PAUSE = pygame.K_SPACE        # Space: Tạm dừng / Tiếp tục
KEY_FORWARD = pygame.K_RIGHT      # Mũi tên phải: Bước tới (Forward)
KEY_BACKWARD = pygame.K_LEFT      # Mũi tên trái: Tua lùi (Backward)