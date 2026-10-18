
---

# BÁO CÁO KIỂM TRA MÃ NGUỒN VÀ TIẾN ĐỘ DỰ ÁN

---

## 1. Tình trạng 2 file `main` ngoài cùng (Điểm khởi chạy dự án)

| Tệp tin | Trạng thái hiện tại | Vấn đề phát hiện |
| :--- | :---: | :--- |
| [`main_single.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_single.py) | **Chưa hoàn thiện** (30 dòng) | • Chỉ in kết quả text ra console, **chưa kết nối với Pygame GUI** ([`SokobanView`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/gui/game_view.py#L9)).<br>• Đang bị comment thuật toán A* (chỉ hardcode chạy UCS).<br>• Chưa cho phép người dùng lựa chọn thuật toán (UCS hoặc A*) theo **Yêu cầu 5**.<br>• Chưa có hàm tái tạo chuỗi trạng thái lưới 2D (`grid`) từ danh sách hành động để nạp vào giao diện. |
| [`main_competitive.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_competitive.py) | **Rỗng hoàn toàn** (0 byte) | • File chưa có bất kỳ dòng mã nào.<br>• Chưa có luồng nhập số bước $n$ từ bàn phím.<br>• Chưa có vòng lặp mô phỏng đối kháng và kết nối dữ liệu lịch sử vào giao diện thi đấu. |

---

## 2. Kiểm tra Yêu cầu 6: Chế độ đối kháng 2 Agent & Cơ chế xử lý va chạm xác suất

Đề bài và yêu cầu bổ sung quy định:
> *Nếu hai agent cùng đi vào một vị trí hoặc cùng đẩy một hộp thì: tạo giá trị xác suất $p \sim \text{Uniform}(0, 1)$. Nếu $p < 0.5$ thì Agent 1 thực hiện hành động, Agent 2 đứng yên (mất lượt), và ngược lại ($p \ge 0.5$). Số bước $n$ do người dùng nhập. Hai agent không được đi xuyên qua nhau.*

Trong [`competitive/two_agent_env.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/two_agent_env.py):
* **Điểm đã đạt:** 
  * Cơ chế sinh số ngẫu nhiên `p = random.uniform(0.0, 1.0)` và rẽ nhánh $p < 0.5$ (Player 1 đi, Player 2 đứng yên) đã được cài đặt tại dòng 109–114.
  * Hộp đưa vào đích bởi P1 chuyển thành ký hiệu `'C'` và bởi P2 chuyển thành ký hiệu `'K'`, cho phép chiếm lại hộp của nhau.
* **Các lỗi logic nghiêm trọng phát hiện được:**
  1. **Bỏ sót va chạm đi xuyên qua nhau (Swap / Head-on collision):** Nếu Player 1 di chuyển vào vị trí của Player 2 đồng thời Player 2 di chuyển vào vị trí của Player 1 (hai bên đi đối diện nhau), hàm `check_conflict` chỉ kiểm tra `next_p1 == next_p2` nên trả về `False`. Kết quả là 2 agent đi xuyên qua nhau và tráo vị trí, **vi phạm quy tắc "The two agents cannot pass through each other"**.
  2. **Đi đè lên đối phương khi đối phương đứng yên:** Trong `apply_move`, hệ thống chỉ kiểm tra tường hoặc hộp, **không kiểm tra ô kế tiếp có phải là vị trí của đối phương hay không**. Nếu P2 đứng yên mà P1 bước vào ô của P2, P1 sẽ ghi đè và làm mất luôn P2 trên bản đồ.
  3. **Đẩy hộp đè lên đối phương:** `apply_move` không kiểm tra `box_next_pos == other_agent_pos`. Agent có thể đẩy một chiếc hộp đè lên vị trí đối thủ đang đứng.
  4. **Lỗi đọc bản đồ:** `load_map` dùng `line.strip()`, làm mất các khoảng trống ở đầu dòng (vốn là các ô sàn trống đi được trong Sokoban). Cần đổi thành `line.rstrip('\r\n')`.

---

## 3. Kiểm tra Yêu cầu 7 & 8: Thuật toán điều khiển Agent & Hiển thị thi đấu

Trong [`competitive/agent_player1.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/agent_player1.py) và [`competitive/agent_player2.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/agent_player2.py):
* **LỖI NGHIÊM TRỌNG:** 
  * Thuật toán hiện tại chỉ tìm đường đi đến ô **kề cạnh cái hộp**. Khi agent đã đứng kề cạnh hộp (`abs(cr - br) + abs(cc - bc) == 1`), danh sách hành động `acts` rỗng, thuật toán **lập tức trả về `"Stay"`**!
  * **Hậu quả:** Tôi đã chạy thử nghiệm mô phỏng và ghi nhận: **Cả 2 Agent chỉ di chuyển tới đứng cạnh cái hộp rồi ĐỨNG YÊN VĨNH VIỄN, hoàn toàn KHÔNG BAO GIỜ đẩy hộp vào đích**. Điểm số của cả hai bên luôn là 0-0 sau $n$ bước!
  * Ở [`agent_player2.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/agent_player2.py#L60), agent lại tìm kiếm `["B", "K"]` (tức là đi tìm hộp đã vào đích của chính mình thay vì hộp `'C'` của đối thủ hoặc `'B'` chưa vào đích).
  * Hai file `agent_player1.py` và `agent_player2.py` hiện tại copy paste giống hệt nhau, chưa thể hiện được sự khác biệt giữa hai đối thủ cạnh tranh theo đúng tinh thần đề bài.

---

## 4. Bảng tổng hợp đối chiếu 8 Yêu cầu theo Rubric giảng viên

| # | Yêu cầu (Rubric PDF) | Điểm | Hiện trạng trong Codebase | Đánh giá |
| :---: | :--- | :---: | :--- | :---: |
| **R1** | **Formulation**: Không gian trạng thái, hành động, goal test | 1.0 | Đã xây dựng hoàn chỉnh trong [`core/state.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/core/state.py) và [`core/problem.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/core/problem.py). |  **Hoàn thành** |
| **R2** | **UCS & A\***: Hàm Heuristic (không dùng Manhattan / Euclidean) | 1.0 | • [`core/ucs.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/core/ucs.py): UCS chuẩn tối ưu.<br>• [`search/astar.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/search/astar.py): Dùng BFS Shortest Path kết hợp thuật toán Hungarian Bipartite Matching + Corner Deadlock Pruning. Thỏa mãn tuyệt đối không dùng Euclidean/Manhattan.<br>• [`search/heuristic.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/search/heuristic.py) đang bị rỗng (cần refactor import). |  **Hoàn thành** |
| **R3** | **Thực nghiệm Time & Space Complexity** (UCS vs A\*) | 1.0 | Đã có [`experiments/benchmark.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/experiments/benchmark.py), đã chạy thực tế trên 4 bản đồ, xuất bảng CSV và biểu đồ cột trực quan `benchmark_chart.png`. |  **Hoàn thành** |
| **R4** | **Kiểm chứng Admissibility & Consistency** của Heuristic | 1.0 | Đã có [`experiments/verify_heuristic.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/experiments/verify_heuristic.py), đã kiểm chứng thành công trên cả 4 bản đồ (100% PASS), lưu file CSV. |  **Hoàn thành** |
| **R5** | **GUI Game Đơn (Pygame)**: Chọn UCS/A*, phím Space, $\rightarrow$, $\leftarrow$, số bước | 1.0 | • Giao diện [`gui/game_view.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/gui/game_view.py) đã có đầy đủ logic hiển thị và điều khiển phím.<br>• **Tuy nhiên**: File chạy chính [`main_single.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_single.py) chưa gọi GUI và chưa cho chọn thuật toán! | ⚠️ **Cần nối GUI** |
| **R6** | **Competitive Two-Agent Formulation**: Xử lý va chạm $p \sim U(0,1)$, $n$ bước, cướp hộp | 1.0 | • Đã có công thức xác suất $p < 0.5$.<br>• Chưa xử lý va chạm swap (đi xuyên nhau), chưa xử lý va chạm khi đứng yên hoặc đẩy hộp đè lên người. | ⚠️ **Cần sửa logic va chạm** |
| **R7** | **Thuật toán điều khiển 2 Agent** ($\le 1,000$ ms/step) | 1.0 | • Hai agent đang bị lỗi kẹt: chỉ đi đến cạnh hộp rồi đứng yên vĩnh viễn (0 điểm).<br>• Cần cài đặt thuật toán tìm kiếm (ví dụ A* / Greedy Best-First Search) để tính đường đẩy hộp vào đích. | ❌ **Cần sửa khẩn cấp** |
| **R8** | **Reimplement GUI đối kháng**: Màu hộp riêng ('C' vs 'K'), 2 file agent độc lập | 1.0 | • Giao diện đã có sprite riêng cho P1, P2, thùng C, thùng K, bảng điểm, thông báo thắng cuộc.<br>• File chạy chính [`main_competitive.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_competitive.py) đang rỗng 0 byte. | ⚠️ **Cần viết file main** |

---

## 5. Các phát hiện bổ sung về môi trường và tệp thừa

1. **[`requirements.txt`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/requirements.txt):** Hiện chỉ liệt kê `pygame==2.6.1`. Cần bổ sung thêm `numpy`, `scipy`, `matplotlib` để giảng viên hoặc sinh viên chạy trên macOS Ventura Intel có thể cài đặt trọn gói không bị lỗi thiếu thư viện khi chạy `benchmark.py` và `astar.py`.
2. **Các tệp rác 0 byte:**
   - [`requirments.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/requirments.py): File 0 byte, sai chính tả tên file.
   - [`competitive/enviroment.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/enviroment.py): File 0 byte, sai chính tả (`environment`).
   - [`maps/test_small.txt`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/maps/test_small.txt): File 0 byte.
   - [`search/heuristic.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/search/heuristic.py): File 0 byte.

---

# KẾ HOẠCH HÀNH ĐỘNG ĐỀ XUẤT (CHỜ BẠN DUYỆT)

Sau khi bạn duyệt báo cáo này, tôi sẽ tiến hành thực hiện các bước sau:

1. **Hoàn thiện [`main_single.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_single.py):**
   - Cho phép người dùng chọn bản đồ (danh sách bản đồ trong `maps/`) và chọn thuật toán (`1. UCS` hoặc `2. A*`).
   - Giải bài toán, in thống kê (thời gian, số node mở rộng, tổng chi phí).
   - Tái tạo chuỗi trạng thái bản đồ và khởi chạy giao diện Pygame với đầy đủ tính năng Pause (Space), Bước tới ($\rightarrow$), Lùi bước ($\leftarrow$).

2. **Nâng cấp môi trường [`competitive/two_agent_env.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/two_agent_env.py):**
   - Sửa triệt để các trường hợp xung đột:
     - Cùng đi vào 1 vị trí hoặc cùng đẩy 1 hộp $\rightarrow$ Tung xác suất $p \sim U(0, 1)$ ($p < 0.5$ thì P1 đi P2 đứng yên, ngược lại P2 đi P1 đứng yên).
     - Đi đối đầu xuyên qua nhau (swap collision: P1 tới vị trí cũ của P2 và P2 tới vị trí cũ của P1) $\rightarrow$ Coi là xung đột và tung xác suất giải quyết, không cho đi xuyên qua nhau.
     - Kiểm tra không được bước vào hoặc đẩy hộp vào vị trí đối phương đang đứng.
   - Sửa hàm đọc bản đồ không làm mất khoảng trắng.

3. **Viết lại thuật toán đẩy hộp cho [`agent_player1.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/agent_player1.py) và [`agent_player2.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/competitive/agent_player2.py):**
   - Thay vì chỉ đi tới cạnh hộp rồi đứng yên, agent sẽ:
     - Chọn mục tiêu hộp và đích đến tối ưu.
     - Tính toán vị trí đứng sau hộp để đẩy hộp về phía đích.
     - Nếu chưa ở vị trí đẩy $\rightarrow$ Tìm đường đi vòng tới vị trí đẩy.
     - Nếu đã ở vị trí đẩy $\rightarrow$ Đẩy hộp về phía đích.
   - Player 1 tập trung ghi điểm nhanh bằng thuật toán A* Heuristic.
   - Player 2 áp dụng chiến thuật Greedy Search linh hoạt (ưu tiên cướp hộp đối thủ hoặc đẩy các hộp gần nhất), đảm bảo thời gian tính toán $< 1,000$ ms.

4. **Xây dựng [`main_competitive.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/main_competitive.py):**
   - Cho phép người dùng nhập số bước tối đa $n$ từ console.
   - Khởi tạo `TwoAgentEnv` và 2 agent.
   - Chạy vòng lặp thi đấu $n$ bước, ghi lại toàn bộ chuỗi trạng thái và điểm số.
   - Khởi động giao diện Pygame đối kháng, hiển thị diễn biến trực quan, bảng điểm thời gian thực và công bố người chiến thắng.

5. **Hoàn thiện cấu trúc thư mục & tài liệu:**
   - Cập nhật [`requirements.txt`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/requirements.txt) đầy đủ.
   - Xuất hàm Heuristic vào [`search/heuristic.py`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/search/heuristic.py) để module hóa rõ ràng.
   - Xóa các file rỗng 0 byte sai chính tả.
   - Cập nhật mục 4 trong [`README.md`](file:///d:/3.1.%20AI/Mid/AI_midterm_27_52400010/source/README.md) hướng dẫn cách chạy cụ thể cho 2 file main.

---

Bạn có đồng ý với báo cáo kiểm tra và kế hoạch triển khai trên không? Khi bạn xác nhận, tôi sẽ tiến hành sửa mã nguồn ngay lập tức.