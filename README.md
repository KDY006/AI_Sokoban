# AI SOKOBAN SOLVER & COMPETITIVE GAME

Dự án phát triển hệ thống giải bài toán Sokoban tự động bằng các thuật toán tìm kiếm trạng thái (UCS, A*) và mô phỏng môi trường thi đấu đối kháng giữa hai tác nhân (Competitive Two-Agent) với giao diện trực quan xây dựng bằng thư viện Pygame.

---

## 1. Yêu cầu hệ thống & Cài đặt môi trường

### Yêu cầu phiên bản
* Python: Khuyến nghị >= 3.10 (Tương thích tốt trên macOS 13.7.8 Ventura chip Intel và Windows 11).

### Cài đặt các thư viện cần thiết
Dự án sử dụng thư viện Pygame cho tầng hiển thị đồ họa. Chạy lệnh sau trong Terminal để cài đặt: pip install pygame

---

## 2. Cấu trúc thư mục dự án

AI_Sokoban/
│
├── core/                       # Biểu diễn trạng thái bản đồ và logic cốt lõi
├── search/                     # Cài đặt các thuật toán tìm kiếm: UCS, A* và hàm Heuristic
├── competitive/                # Môi trường và tác nhân cho chế độ đối kháng 2 Agent
│   ├── enviroment.py           # Môi trường TwoAgentEnv xử lý va chạm và tính điểm
│   ├── agent_player1.py        # Thuật toán điều khiển của Player 1 (A)
│   └── agent_player2.py        # Thuật toán điều khiển của Player 2 (P)
│
├── gui/                        # Module hiển thị đồ họa Pygame
│   ├── assets/                 # Bộ sprite đồ họa Kenney Sokoban
│   │   ├── player.png          # Nhân vật Player 1 (A)
│   │   ├── player2.png         # Nhân vật Player 2 (P)
│   │   ├── box.png             # Thùng chưa vào đích (B)
│   │   ├── box_docked.png      # Thùng trên đích của Player 1 (C)
│   │   ├── box_p2.png          # Thùng trên đích của Player 2 (K)
│   │   ├── target.png          # Ô đích (D)
│   │   ├── wall.png            # Tường (%)
│   │   └── floor.png           # Sàn nhà (' ')
│   ├── constants.py            # Cấu hình hằng số
│   └── game_view.py            # Lớp SokobanView quản lý hiển thị và tương tác
│
├── maps/                       # Các file cấu hình bản đồ kiểm thử
│   ├── example_map.txt
│   ├── map_02_two_boxes.txt
│   ├── map_03_three_boxes.txt
│   ├── map_04_four_boxes.txt
│   └── competitive_map.txt
│
├── test_gui.py                 # File kiểm thử độc lập giao diện GUI
├── main_single.py              # Chương trình chính chạy giải thuật đơn tác nhân
├── main_competitive.py         # Chương trình chính chạy trận đối kháng 2 tác nhân
└── README.md                   # Tài liệu hướng dẫn sử dụng và chạy dự án

---

## 3. Quy ước ký hiệu bản đồ (Map Notation)

* % : Tường
* ' ' : Sàn nhà
* D : Điểm đích
* B : Thùng chưa vào đích
* A : Người chơi 1
* P : Người chơi 2
* C : Thùng vào đích do P1 đẩy
* K : Thùng vào đích do P2 đẩy
* + : Người chơi đứng trên ô đích

---

## 4. Hướng dẫn chạy chương trình

### Cách 1: Chạy kiểm thử nhanh giao diện GUI
Để test riêng biệt tính năng của module đồ họa:

python test_gui.py

* Cửa sổ 1 (Chế độ đơn): Hiển thị tên thuật toán A*, tổng số bước, trạng thái Pause/Play.
* Cửa sổ 2 (Chế độ đối kháng): Hiển thị 2 nhân vật, bảng điểm thời gian thực của P1 vs P2, thùng riêng biệt của từng bên, và kết quả thắng/thua khi hết lượt.

---

### Cách 2: Chạy chế độ Đơn (Single-Agent - R5)
Chạy chương trình chính cho chế độ đơn tác nhân:

```bash
python main_single.py
```

* Chương trình sẽ hiển thị menu tương tác để bạn chọn bản đồ (`maps/example_map.txt`, `maps/map_02_two_boxes.txt`, ...) và chọn thuật toán (`1. UCS` hoặc `2. A*`).
* Sau khi giải xong, bảng thống kê hiệu năng (chi phí, số node mở rộng, thời gian thực thi ms) sẽ hiển thị trên console và cửa sổ Pygame sẽ tự động mở để minh họa trực quan lời giải.
* Bạn cũng có thể truyền tham số dòng lệnh trực tiếp:
  ```bash
  python main_single.py --map maps/map_02_two_boxes.txt --algo astar
  python main_single.py --map maps/example_map.txt --algo ucs
  ```

---

### Cách 3: Chạy chế độ Đối kháng 2 Agent (Competitive - R6, R7, R8)
Chạy trận thi đấu đối kháng giữa 2 tác nhân AI:

```bash
python main_competitive.py
```

* Bạn sẽ được yêu cầu nhập số lượt tối đa $n$ từ bàn phím (mặc định: 50 lượt) và chọn bản đồ thi đấu (`maps/competitive_map.txt`).
* Trong suốt trận đấu, nếu xảy ra xung đột (hai agent cùng đi vào một vị trí hoặc cùng đẩy một hộp), cơ chế xác suất $p \sim \text{Uniform}(0, 1)$ ($p < 0.5$: P1 đi, ngược lại P2 đi) sẽ được kích hoạt và in chi tiết log ra console.
* Cửa sổ Pygame sẽ mở ra diễn hoạt trực quan toàn bộ trận đấu, hiển thị bảng điểm thời gian thực và công bố bên chiến thắng.
* Bạn cũng có thể chỉ định số bước qua tham số dòng lệnh:
  ```bash
  python main_competitive.py --steps 50
  python main_competitive.py -n 100 --map maps/competitive_map.txt
  ```


---

## 5. Các phím điều khiển trên giao diện (Pygame Controls)

Khi cửa sổ game đang mở, người dùng có thể tương tác bằng các phím sau:
* Phím Space: Chuyển đổi giữa chế độ PAUSED (tạm dừng) và PLAYING (tự động chạy các bước tiếp theo).
* Phím Mũi tên phải (->): Đi tới 1 bước (hoạt động khi đang Pause).
* Phím Mũi tên trái (<-): Lùi lại 1 bước trước đó (hoạt động khi đang Pause).
* Phím ESC: Thoát và đóng cửa sổ trò chơi.

---

## 6. Hướng dẫn cho thành viên nhóm khi tích hợp Module GUI (gui.game_view)

Để kết nối module hiển thị đồ họa vào bất kỳ file chạy nào, chỉ cần gọi lớp SokobanView:

### Tích hợp chế độ Đơn:
from gui.game_view import SokobanView

view = SokobanView(title="AI Sokoban - Single Agent")
view.set_states(history_states, algorithm="A*")
view.run_interactive()

### Tích hợp chế độ Đối kháng:
from gui.game_view import SokobanView

view = SokobanView(title="AI Sokoban - Competitive Two Agents")
view.set_competitive_history(states=history_states, scores=history_scores, max_steps=max_steps)
view.run_interactive()