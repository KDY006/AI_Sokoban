# AI SOKOBAN SOLVER & COMPETITIVE TWO-AGENT GAME

> **Đồ án Giữa kỳ môn Nhập môn Trí tuệ Nhân tạo (Introduction to Artificial Intelligence)**  
> **Khoa Công nghệ Thông tin - Trường Đại học Tôn Đức Thắng**  
> Dự án phát triển hệ thống giải bài toán Sokoban tự động bằng các thuật toán tìm kiếm trạng thái (UCS, A*) và mô phỏng môi trường thi đấu đối kháng giữa hai tác nhân (Competitive Two-Agent) với giao diện trực quan xây dựng bằng thư viện Pygame.

---

## 1. Yêu cầu hệ thống & Cài đặt môi trường

### Yêu cầu phiên bản
* **Hệ điều hành:** Tương thích hoàn toàn trên **Windows 10/11** và **macOS 13.7.8 (Ventura)** chip Intel Core i5 / Apple Silicon.
* **Python:** Khuyến nghị phiên bản $\ge 3.10$ (ví dụ: Python 3.10, 3.11, 3.12).

### Cài đặt các thư viện cần thiết
Dự án sử dụng các thư viện chuẩn cho thuật toán, đồ họa và thực nghiệm đối chiếu. Mở Terminal/Command Prompt tại thư mục dự án và chạy:

```bash
pip install -r requirements.txt
```

Danh sách các thư viện chính trong `requirements.txt`:
* `pygame==2.6.1`: Xây dựng giao diện đồ họa 2D trực quan và tương tác bàn phím (R5, R8).
* `numpy>=1.24.0`: Xử lý ma trận chi phí phục vụ thuật toán Hungarian.
* `scipy>=1.10.0`: Thuật toán Hungarian (`linear_sum_assignment`) ghép cặp tối ưu Hộp - Đích (R2, R4).
* `matplotlib>=3.7.0`: Vẽ biểu đồ cột đối chiếu Time & Space Complexity giữa UCS và A* (R3).

---

## 2. Cấu trúc thư mục dự án

```text
AI_Sokoban/
│
├── core/                               # Biểu diễn trạng thái bản đồ và giải thuật cốt lõi (R1, R2)
│   ├── state.py                        # Lớp State bất biến (hashable) và hàm parse_map đọc bản đồ
│   ├── problem.py                      # Lớp SokobanProblem: không gian trạng thái, goal test, successor
│   └── ucs.py                          # Cài đặt giải thuật Uniform Cost Search (UCS)
│
├── search/                             # Cài đặt giải thuật A* và hàm Heuristic (R2)
│   ├── heuristic.py                    # Hàm SokobanHeuristic (Hungarian BFS Matching né tường, không Manhattan/Euclidean)
│   └── astar.py                        # Cài đặt giải thuật A* Search và cấu trúc AStarNode
│
├── competitive/                        # Môi trường và tác nhân cho chế độ đối kháng 2 Agent (R6, R7, R8)
│   ├── two_agent_env.py                # Môi trường TwoAgentEnv: xử lý va chạm, xác suất p ~ U(0,1), tính điểm
│   ├── agent_player1.py                # Thuật toán điều khiển của Player 1 (A)
│   └── agent_player2.py                # Thuật toán điều khiển của Player 2 (P)
│
├── gui/                                # Module hiển thị đồ họa Pygame (R5, R8)
│   ├── assets/                         # Bộ sprite đồ họa Kenney Sokoban
│   │   ├── player.png                  # Nhân vật Player 1 (A)
│   │   ├── player2.png                 # Nhân vật Player 2 (P)
│   │   ├── box.png                     # Thùng chưa vào đích (B)
│   │   ├── box_docked.png              # Thùng trên đích của Player 1 (C)
│   │   ├── box_p2.png                  # Thùng trên đích của Player 2 (K)
│   │   ├── target.png                  # Ô đích (D)
│   │   ├── wall.png                    # Tường (%)
│   │   └── floor.png                   # Sàn nhà (' ')
│   ├── constants.py                    # Cấu hình hằng số (kích thước ô TILE_SIZE=64, FPS=60, phím tắt)
│   └── game_view.py                    # Lớp SokobanView quản lý hiển thị và tương tác phím
│
├── experiments/                        # Module thực nghiệm và đánh giá khoa học (R3, R4)
│   ├── benchmark.py                    # Thực nghiệm đối chiếu Time & Space Complexity (UCS vs A*)
│   ├── verify_heuristic.py             # Thực nghiệm kiểm chứng tính Admissibility & Consistency
│   └── results/                        # Kết quả thực nghiệm lưu trữ
│       ├── benchmark_results.csv       # Bảng số liệu đối chiếu UCS vs A*
│       ├── benchmark_chart.png         # Biểu đồ trực quan hóa so sánh hiệu năng
│       └── verify_heuristic_results.csv # Bảng kiểm chứng tính đúng đắn toán học của Heuristic
│
├── maps/                               # Các file cấu hình bản đồ kiểm thử
│   ├── example_map.txt                 # Bản đồ chuẩn theo đề bài (7 hộp)
│   ├── map_02_two_boxes.txt            # Bản đồ kiểm thử 2 hộp
│   ├── map_03_three_boxes.txt          # Bản đồ kiểm thử 3 hộp
│   ├── map_04_four_boxes.txt           # Bản đồ kiểm thử 4 hộp
│   └── competitive_map.txt             # Bản đồ thi đấu đối kháng 2 Agent
│
├── main_single.py                      # Chương trình chính chạy chế độ Đơn tác nhân (R1, R2, R5)
├── main_competitive.py                 # Chương trình chính chạy chế độ Đối kháng 2 Agent (R6, R7, R8)
├── test_gui.py                         # File kiểm thử độc lập giao diện GUI
├── requirements.txt                    # Danh sách thư viện phụ thuộc
└── README.md                           # Tài liệu hướng dẫn sử dụng và chạy toàn bộ dự án
```

---

## 3. Quy ước ký hiệu bản đồ (Map Notation)

Dự án tuân thủ nghiêm ngặt quy ước ký tự theo đề bài:
* `%` : Vật cản / Tường (Wall)
* `' '` : Ô trống / Sàn nhà (Floor)
* `D` : Điểm đích đặt thùng (Goal)
* `B` : Thùng chưa vào đích (Box)
* `A` : Vị trí xuất phát của Người chơi 1 (Player 1)
* `P` : Vị trí xuất phát của Người chơi 2 (Player 2 - chế độ đối kháng)
* `C` : Thùng đã nằm trên điểm đích do Player 1 đưa vào
* `K` : Thùng đã nằm trên điểm đích do Player 2 đưa vào
* `+` : Người chơi đứng trên ô đích

---

## 4. Hướng dẫn chạy toàn bộ dự án (Execution Guide)

### Chế độ 1: Chạy chương trình chính Đơn tác nhân (Single-Agent - Yêu cầu 1, 2, 5)

File khởi chạy: `main_single.py`

#### Cách 1: Chạy tương tác qua menu Console (Khuyến nghị)
```bash
python main_single.py
```
* Bước 1: Chọn bản đồ từ danh sách (`1. example_map.txt`, `2. map_02_two_boxes.txt`, ...) hoặc nhập file tùy ý.
* Bước 2: Chọn thuật toán:
  * `1` : **UCS** (Uniform Cost Search)
  * `2` : **A\*** (A* Search với hàm Hungarian BFS Heuristic)
* Sau khi tìm kiếm thành công, console sẽ hiển thị bảng chỉ số hiệu năng (chi phí tối ưu, số bước, số node mở rộng, bộ nhớ đỉnh, thời gian chạy).
* Cửa sổ Pygame sẽ tự động mở lên để diễn hoạt từng bước di chuyển của Agent.

#### Cách 2: Chạy trực tiếp qua tham số dòng lệnh CLI
```bash
# Chạy thuật toán A* trên bản đồ chuẩn
python main_single.py --map maps/example_map.txt --algo astar

# Chạy thuật toán UCS trên bản đồ 2 hộp
python main_single.py --map maps/map_02_two_boxes.txt --algo ucs

# Chạy không mở cửa sổ đồ họa (chỉ xem log kết quả trên console)
python main_single.py --map maps/map_02_two_boxes.txt --algo astar --no-gui
```

---

### Chế độ 2: Chạy chương trình chính Đối kháng 2 Agent (Competitive - Yêu cầu 6, 7, 8)

File khởi chạy: `main_competitive.py`

#### Cách 1: Chạy tương tác qua Console
```bash
python main_competitive.py
```
* Nhập số bước tối đa $n$ từ bàn phím (ví dụ: `30`, `50`, `100`, mặc định là `50`).
* Nhấn Enter để chọn bản đồ thi đấu mặc định `maps/competitive_map.txt`.
* Hai tác nhân `agent_player1` và `agent_player2` sẽ tự động ra quyết định theo từng lượt (thời gian tính toán mỗi bước $\le 1,000$ ms).
* **Quy tắc giải quyết va chạm xác suất:** Nếu 2 agent cùng di chuyển vào 1 vị trí, cùng đẩy 1 hộp hoặc va chạm trực diện đi xuyên qua nhau, hệ thống sinh ngẫu nhiên $p \sim \text{Uniform}(0, 1)$:
  * Nếu $p < 0.5$: Agent 1 được thực hiện hành động, Agent 2 đứng yên (mất lượt).
  * Nếu $p \ge 0.5$: Agent 2 được thực hiện hành động, Agent 1 đứng yên (mất lượt).
* Toàn bộ diễn biến trận đấu được ghi nhận và diễn hoạt trên giao diện Pygame với màu sắc hộp riêng biệt (thùng P1 là `'C'`, thùng P2 là `'K'`), bảng điểm cập nhật thời gian thực và công bố kết quả chung cuộc.

#### Cách 2: Chạy qua tham số dòng lệnh CLI
```bash
# Chạy trận đấu 50 bước
python main_competitive.py --steps 50

# Chạy trận đấu 100 bước trên bản đồ tùy chỉnh
python main_competitive.py -n 100 --map maps/competitive_map.txt

# Chạy nhanh chỉ in kết quả log trên console
python main_competitive.py --steps 30 --no-gui
```

---

### Chế độ 3: Chạy thực nghiệm so sánh Time & Space Complexity (Yêu cầu 3)

File thực nghiệm: `experiments/benchmark.py`

```bash
python experiments/benchmark.py
```

* Script sẽ tự động chạy cả 2 thuật toán **UCS** và **A\*** trên toàn bộ các bản đồ trong thư mục `maps/`.
* Thu thập các chỉ số thực nghiệm:
  * Thời gian thực thi (Execution Time - ms)
  * Số node đã mở rộng (Expanded Nodes)
  * Bộ nhớ đỉnh Frontier (Peak Frontier Size)
* **Kết quả đầu ra:**
  * Bảng số liệu chi tiết: `experiments/results/benchmark_results.csv`
  * Biểu đồ cột so sánh trực quan đa chiều: `experiments/results/benchmark_chart.png`

---

### Chế độ 4: Chạy kiểm chứng tính Admissibility & Consistency của Heuristic (Yêu cầu 4)

File thực nghiệm: `experiments/verify_heuristic.py`

```bash
python experiments/verify_heuristic.py
```

* Tự động kiểm chứng toán học hàm `SokobanHeuristic`:
  * **Tính Admissibility (Đáng tin):** Kiểm tra $h(S_0) \le h^*(S_0)$, $h(\text{Goal}) = 0$, và $h(S_k) \le h^*(S_k)$ dọc theo toàn bộ đường đi nghiệm tối ưu.
  * **Tính Consistency (Nhất quán / Đơn điệu):** Duyệt BFS hàng ngàn bước chuyển trạng thái $(s \rightarrow s')$ với chi phí bước đi $c=1$, kiểm tra điều kiện tam giác $h(s) - h(s') \le c = 1$.
* **Kết quả đầu ra:** Bảng tổng hợp kiểm định lưu tại `experiments/results/verify_heuristic_results.csv` (Đạt kết quả 100% PASS trên tất cả các map).

---

### Chế độ 5: Chạy kiểm thử nhanh giao diện đồ họa GUI (Yêu cầu 5, 8)

File kiểm thử: `test_gui.py`

```bash
python test_gui.py
```

* Chạy độc lập 2 cửa sổ để kiểm tra toàn bộ tính năng đồ họa:
  * **Cửa sổ 1 (Chế độ đơn):** Kiểm tra hiển thị thuật toán, số bước, các phím điều khiển Pause, Step Forward, Step Backward.
  * **Cửa sổ 2 (Chế độ đối kháng):** Kiểm tra 2 nhân vật A và P, thùng C và thùng K, bảng điểm P1 vs P2 và banner thông báo kết quả thắng/thua.

---

## 5. Các phím điều khiển trên giao diện (Pygame Controls)

Khi cửa sổ Pygame hiển thị (ở cả chế độ Đơn và Đối kháng), người dùng có thể tương tác:
* **Phím Space (`K_SPACE`):** Chuyển đổi giữa chế độ `PAUSED` (tạm dừng) và `PLAYING` (tự động diễn hoạt các bước tiếp theo).
* **Phím Mũi tên phải (`->`):** Bước tới 1 lượt (hoạt động khi đang ở trạng thái Pause).
* **Phím Mũi tên trái (`<-`):** Lùi lại 1 lượt trước đó (hoạt động khi đang ở trạng thái Pause).
* **Phím ESC (`K_ESCAPE`):** Đóng cửa sổ trò chơi an toàn.

---

## 6. Bảng tổng hợp mức độ hoàn thiện 8 Yêu cầu (Rubric)

| Yêu cầu | Mô tả nội dung | Điểm | File cài đặt chính | Trạng thái |
| :---: | :--- | :---: | :--- | :---: |
| **R1** | Formulate bài toán tìm kiếm trạng thái (State, Action, Transition, Goal Test) | 1.0 | `core/state.py`, `core/problem.py` |  **Hoàn thành** |
| **R2** | Cài đặt UCS và A* với hàm Heuristic không dùng Manhattan/Euclidean | 1.0 | `core/ucs.py`, `search/heuristic.py`, `search/astar.py` |  **Hoàn thành** |
| **R3** | Thực nghiệm so sánh Time & Space Complexity giữa UCS và A* (CSV + Biểu đồ) | 1.0 | `experiments/benchmark.py` |  **Hoàn thành** |
| **R4** | Đánh giá & kiểm chứng tính Admissibility và Consistency của Heuristic | 1.0 | `experiments/verify_heuristic.py` |  **Hoàn thành** |
| **R5** | Xây dựng GUI Pygame chế độ Đơn, chọn UCS/A*, phím Space, `->`, `<-` | 1.0 | `gui/game_view.py`, `main_single.py` |  **Hoàn thành** |
| **R6** | Mô hình hóa bài toán đối kháng 2 Agent, xử lý va chạm xác suất Uniform(0,1), $n$ bước | 1.0 | `competitive/two_agent_env.py`, `main_competitive.py` |  **Hoàn thành** |
| **R7** | Cài đặt thuật toán điều khiển cho 2 Agent (thời gian quyết định $\le 1,000$ ms) | 1.0 | `competitive/agent_player1.py`, `competitive/agent_player2.py` |  **Hoàn thành** |
| **R8** | Cập nhật GUI hỗ trợ đối kháng, màu thùng phân biệt ('C' vs 'K'), 2 file mã nguồn riêng | 1.0 | `gui/game_view.py`, `main_competitive.py` |  **Hoàn thành** |