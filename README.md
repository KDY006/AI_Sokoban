# AI SOKOBAN SOLVER & COMPETITIVE TWO-AGENT GAME

> **Đồ án Giữa kỳ môn Nhập môn Trí tuệ Nhân tạo (Introduction to Artificial Intelligence - 503043)**  
> **Khoa Công nghệ Thông tin - Trường Đại học Tôn Đức Thắng (TDTU)**  
> Dự án phát triển hệ thống giải bài toán Sokoban tự động bằng các giải thuật tìm kiếm không gian trạng thái (UCS, A*) và mô phỏng môi trường thi đấu đối kháng hai tác nhân (Competitive Two-Agent) với giao diện đồ họa trực quan Pygame.

---

## 1. Thông tin Nhóm thực hiện

| STT | Họ và Tên | Mã số sinh viên (MSSV) | Nhiệm vụ đảm nhiệm chính |
| :---: | :--- | :---: | :--- |
| 1 | Nguyễn Văn Duy | 52400010 | Quản lý dự án, Kiến trúc cốt lõi `core/`, Mô hình hóa R1, Cài đặt UCS R2.1, Tích hợp hệ thống và Main CLI |
| 2 | Lê Văn Quý | 52400153 | Nghiên cứu Heuristic Hungarian BFS `search/heuristic.py` R2.2, Cài đặt A* R2.2, Thực nghiệm Benchmark R3, Kiểm chứng Admissibility & Consistency R4 |
| 3 | Huỳnh Thiên Đức | 52400110 | Thiết kế giao diện đồ họa hướng đối tượng (OOP) `gui/` R5, Tích hợp sprite Kenney, Xử lý tương tác phím (Space, Tua tới/lui) và Scale màn hình động |
| 4 | Lê Tiến Đạt | 52400105 | Mô hình hóa môi trường đối kháng `competitive/two_agent_env.py` R6, Cơ chế giải quyết xung đột ngẫu nhiên, Thuật toán Agent Player 1 & 2 R7, GUI thi đấu Real-time R8 |

---

## 2. Yêu cầu Hệ thống & Cài đặt Môi trường

### Yêu cầu phiên bản
* **Hệ điều hành:** Chạy mượt mà trên **Windows 10/11** và **macOS 13.7.8 (Ventura)** chip Intel Core i5 / Apple Silicon (theo đúng yêu cầu đề bài).
* **Python:** Khuyến nghị phiên bản $\ge 3.10$ (ví dụ: Python 3.10, 3.11, 3.12).

### Cài đặt thư viện phụ thuộc
Mở Terminal / Command Prompt tại thư mục gốc `source` và chạy lệnh:

```bash
pip install -r requirements.txt
```

Danh mục các thư viện chính:
* `pygame==2.6.1`: Xây dựng giao diện đồ họa 2D trực quan và xử lý tương tác bàn phím (R5, R8).
* `numpy>=1.24.0`: Xử lý ma trận chi phí khoảng cách né tường.
* `scipy>=1.10.0`: Thuật toán Hungarian (`linear_sum_assignment`) giải bài toán ghép cặp cực tiểu Hộp - Đích (R2, R4).
* `matplotlib>=3.7.0`: Vẽ biểu đồ cột đối chiếu Time & Space Complexity giữa UCS và A* (R3).

---

## 3. Hướng dẫn Chạy Toàn bộ Dự án

### 3.1. Chạy Chế độ Đơn tác nhân (Single-Agent: R1, R2, R5)
Hệ thống hỗ trợ cả chế độ tương tác qua Menu console và chế độ truyền tham số dòng lệnh:

* **Cách 1: Chạy Menu tương tác (Khuyến nghị khi demo)**
  ```bash
  python main_single.py
  # hoặc trên Windows:
  py main_single.py
  ```
  - Bước 1: Nhập số thứ tự để chọn bản đồ (ví dụ: `1` cho `example_map.txt`, `8` cho `map_200.txt`, `9` cho `map_deadlock.txt`).
  - Bước 2: Chọn thuật toán (`1`: UCS, `2`: A*).
  - Thuật toán sẽ tính toán lời giải, in số liệu thống kê ra console và tự động khởi chạy cửa sổ Pygame GUI.

* **Cách 2: Chạy trực tiếp bằng tham số dòng lệnh**
  ```bash
  # Giải bản đồ example_map bằng thuật toán A*
  py main_single.py --map maps/example_map.txt --algo astar

  # Giải bằng thuật toán UCS
  py main_single.py --map maps/example_map.txt --algo ucs
  ```

* **Các phím thao tác trên giao diện Pygame (R5)**:
  - `[Phím Space]`: Tạm dừng (Pause) / Tiếp tục (Resume) hoạt ảnh giải đố.
  - `[Phím Mũi tên Phải ->]`: Bước tới 1 bước (khi đang Pause).
  - `[Phím Mũi tên Trái <-]`: Lùi lại 1 bước (khi đang Pause).
  - `[Phím ESC]`: Đóng cửa sổ trò chơi.

---

### 3.2. Chạy Chế độ Đối kháng Hai tác nhân (Competitive Two-Agent: R6, R7, R8)

* **Cách 1: Chạy tương tác**
  ```bash
  py main_competitive.py
  ```
  - Bước 1: Nhập số bước tối đa $n$ (mặc định 50 bước, có thể nhập `24`, `35`, `50`,...).
  - Bước 2: Chọn bản đồ thi đấu:
    - `1`: `competitive_map_v1.txt` - Đấu trường mở Arena Open Layout.
    - `2`: `competitive_map_v2.txt` - Đấu trường có trụ chướng ngại vật phân luồng Tactical Pillars.
  - Trận đấu diễn ra theo thời gian thực giữa Player 1 (Màu Xám / Áo Xám) và Player 2 (Màu Xanh / Áo Xanh).
  - Console hiển thị log thời gian thực tế từng bước (< 25 ms / bước, đạt chuẩn R7 $\le 1,000$ ms). Khi phát sinh xung đột cùng ô, hệ thống tự động kích hoạt cơ chế xác suất $p \sim \text{Uniform}(0, 1)$ theo R6.
  - Cửa sổ Pygame mở ra tái hiện lại toàn bộ trận đấu với màu sắc thùng phân biệt: Thùng của P1 vào đích (`C`) và Thùng của P2 vào đích (`K`).

* **Cách 2: Chạy với tham số dòng lệnh**
  ```bash
  # Chạy đấu trường v1 (mặc định) 50 bước
  py main_competitive.py --steps 50

  # Chạy đấu trường v2 có trụ cản
  py main_competitive.py --steps 50 --map maps/competitive_map_v2.txt
  ```

---

### 3.3. Chạy Thực nghiệm So sánh Hiệu năng (Benchmark: R3)
Script tự động chạy đối chiếu toàn diện độ phức tạp thời gian và không gian giữa UCS và A* trên tập bản đồ chuẩn có độ khó tăng tiến:

```bash
python -m experiments.benchmark
# hoặc
py -m experiments.benchmark
```

* **Đầu ra tự động**:
  1. In bảng đối chiếu trực quan ra màn hình console.
  2. Xuất bảng số liệu chi tiết ra file CSV: `experiments/results/benchmark_results.csv`.
  3. Xuất biểu đồ cột 3 tiêu chí (*Số Node mở rộng Log-Scale*, *Bộ nhớ đỉnh Frontier Log-Scale*, *Thời gian thực thi ms*) ra file ảnh: `experiments/results/benchmark_chart.png`.

---

### 3.4. Chạy Kiểm chứng Toán học Heuristic (Verify Heuristic: R4)
Script tự động kiểm chứng thực nghiệm tính **Admissibility ($h(s) \le h^*(s)$)** và **Consistency ($\Delta h \le 1$)** của hàm Heuristic Hungarian BFS:

```bash
python -m experiments.verify_heuristic
# hoặc
py -m experiments.verify_heuristic
```

* **Đầu ra tự động**:
  - Duyệt toàn bộ các trạng thái trên lộ trình tối ưu để kiểm tra tính chấp nhận được ($h \le h^*$).
  - Duyệt BFS hàng ngàn bước chuyển tiếp trạng thái $(s \rightarrow s')$ với chi phí $c=1$ để kiểm tra tính nhất quán ($h(s) - h(s') \le 1$).
  - Báo cáo kết luận **100% PASS (Thỏa mãn)** cho toàn bộ các bản đồ.
  - Xuất bảng số liệu tổng hợp ra: `experiments/results/verify_heuristic_results.csv`.

---

## 4. Bảng Ký hiệu Quy ước Bản đồ (Map Legends)

### Chế độ Đơn tác nhân (Single-Agent - R1 đến R5)
* `%` : Bức tường / Chướng ngại vật cố định (Wall).
* ` ` : Ô sàn trống (Empty Floor).
* `A` : Vị trí ban đầu của Người chơi (Agent).
* `+` : Người chơi đang đứng trên ô đích (Player on Goal).
* `B` : Thùng gỗ chưa vào đích (Box).
* `D` : Điểm đích được chỉ định (Designated Goal).
* `C` : Thùng gỗ đã nằm trên điểm đích (Box on Goal).

### Chế độ Đối kháng Hai tác nhân (Competitive Two-Agent - R6 đến R8)
* `A` : Vị trí Player 1 (Màu Xám).
* `P` : Vị trí Player 2 (Màu Xanh).
* `B` : Thùng tự do trung lập (Cả hai bên đều có thể đẩy).
* `C` : Thùng đã vào đích được ghi điểm bởi Player 1 (+1 điểm cho P1).
* `K` : Thùng đã vào đích được ghi điểm bởi Player 2 (+1 điểm cho P2).