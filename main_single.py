"""
Module: main_single.py
Mục đích: Điểm khởi chạy chính cho chế độ Đơn tác nhân (Single-Agent - R5).
Tính năng:
  - Cho phép người dùng chọn bản đồ (danh sách maps/ hoặc nhập file tùy ý).
  - Cho phép lựa chọn thuật toán giải: UCS hoặc A* (Heuristic Hungarian BFS).
  - Đo lường và in thống kê hiệu năng chi tiết (Thời gian ms, Chi phí, Số node mở rộng, Bộ nhớ Frontier).
  - Tái tạo chuỗi trạng thái 2D và khởi chạy giao diện đồ họa trực quan Pygame.
  - Hỗ trợ các phím điều khiển: Space (Tạm dừng/Tiếp tục), -> (Bước tới), <- (Lùi bước), ESC (Thoát).
"""

import os
import sys
import argparse
from typing import List, Tuple, FrozenSet

# Đảm bảo console UTF-8 trên Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thêm thư mục gốc vào PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.state import parse_map, State
from core.problem import SokobanProblem
from core.ucs import ucs_search
from search.astar import astar_search
from gui.game_view import SokobanView


def state_to_grid(
    state: State,
    walls: FrozenSet[Tuple[int, int]],
    goals: FrozenSet[Tuple[int, int]],
    max_row: int,
    max_col: int
) -> List[List[str]]:
    """
    Chuyển đổi đối tượng State thành ma trận lưới 2D ký tự chuẩn theo quy ước đề bài:
      '%' : Tường
      'A' : Người chơi
      '+' : Người chơi đứng trên ô đích
      'B' : Hộp chưa vào đích
      'C' : Hộp đã nằm trên ô đích
      'D' : Ô đích trống
      ' ' : Sàn trống
    """
    grid = [[" " for _ in range(max_col)] for _ in range(max_row)]

    for r, c in walls:
        if 0 <= r < max_row and 0 <= c < max_col:
            grid[r][c] = "%"

    for r, c in goals:
        if 0 <= r < max_row and 0 <= c < max_col:
            grid[r][c] = "D"

    for r, c in state.boxes_pos:
        if 0 <= r < max_row and 0 <= c < max_col:
            grid[r][c] = "C" if (r, c) in goals else "B"

    ar, ac = state.player_pos
    if 0 <= ar < max_row and 0 <= ac < max_col:
        grid[ar][ac] = "+" if (ar, ac) in goals else "A"

    return grid


def get_available_maps() -> List[str]:
    """Lấy danh sách các file bản đồ hợp lệ trong thư mục maps/."""
    maps_dir = os.path.join(BASE_DIR, "maps")
    valid_maps = []
    if os.path.exists(maps_dir):
        for fname in sorted(os.listdir(maps_dir)):
            if fname.endswith(".txt"):
                fpath = os.path.join(maps_dir, fname)
                if os.path.getsize(fpath) > 0 and fname != "competitive_map.txt":
                    valid_maps.append(fpath)
    return valid_maps


def interactive_select_options() -> Tuple[str, str]:
    """Hiển thị menu tương tác trên console để người dùng chọn map và thuật toán."""
    maps = get_available_maps()
    print("=" * 65)
    print("        HỆ THỐNG GIẢI SOKOBAN ĐƠN TÁC NHÂN (SINGLE-AGENT)")
    print("=" * 65)

    print("\n--- [BƯỚC 1] CHỌN BẢN ĐỒ ---")
    for idx, mpath in enumerate(maps, 1):
        mname = os.path.basename(mpath)
        print(f"  {idx}. {mname}")
    print(f"  {len(maps) + 1}. Nhập đường dẫn file bản đồ tùy chỉnh...")

    default_map = maps[0] if maps else os.path.join(BASE_DIR, "maps", "example_map.txt")
    choice_map = input(f"\nChọn bản đồ [1-{len(maps) + 1}] (Mặc định 1 - {os.path.basename(default_map)}): ").strip()

    selected_map = default_map
    if choice_map.isdigit():
        val = int(choice_map)
        if 1 <= val <= len(maps):
            selected_map = maps[val - 1]
        elif val == len(maps) + 1:
            custom_path = input("Nhập đường dẫn file map: ").strip()
            if os.path.exists(custom_path):
                selected_map = custom_path
            else:
                print(f"[!] Không tìm thấy file {custom_path}, sử dụng mặc định: {os.path.basename(default_map)}")
    elif choice_map:
        if os.path.exists(choice_map):
            selected_map = choice_map

    print("\n--- [BƯỚC 2] CHỌN THUẬT TOÁN TÌM KIẾM (YÊU CẦU 5) ---")
    print("  1. UCS  - Uniform Cost Search (Tìm kiếm chi phí đồng nhất)")
    print("  2. A*   - A* Search (Heuristic Hungarian BFS - Không Manhattan/Euclidean)")
    choice_algo = input("\nChọn thuật toán [1/2] (Mặc định 2 - A*): ").strip()

    selected_algo = "A*" if choice_algo in ["2", "astar", "A*", "a*"] else "UCS"
    if choice_algo == "1" or choice_algo.lower() == "ucs":
        selected_algo = "UCS"

    return selected_map, selected_algo


def main():
    parser = argparse.ArgumentParser(description="Chương trình giải Sokoban Single-Agent (R5)")
    parser.add_argument("--map", type=str, default=None, help="Đường dẫn file bản đồ")
    parser.add_argument("--algo", type=str, choices=["ucs", "astar", "UCS", "A*"], default=None, help="Thuật toán: ucs hoặc astar")
    parser.add_argument("--no-gui", action="store_true", help="Chỉ giải và in kết quả console, không mở Pygame GUI")
    args = parser.parse_args()

    # Xác định map và thuật toán
    if args.map is not None and args.algo is not None:
        map_file = args.map
        algo_name = "A*" if args.algo.lower() == "astar" else "UCS"
    else:
        map_file, algo_name = interactive_select_options()

    if not os.path.exists(map_file):
        print(f"[X] Lỗi: Không tìm thấy file bản đồ: {map_file}")
        return

    print("\n" + "=" * 65)
    print(f"[*] Bản đồ đã chọn: {os.path.basename(map_file)}")
    print(f"[*] Thuật toán:     {algo_name}")
    print("=" * 65)

    # Đọc bản đồ
    try:
        init_state, walls, goals, max_row, max_col = parse_map(map_file)
    except Exception as e:
        print(f"[X] Lỗi đọc bản đồ: {e}")
        return

    problem = SokobanProblem(init_state, walls, goals)
    print(f"[*] Kích thước mê cung: {max_row} hàng x {max_col} cột")
    print(f"[*] Số lượng hộp/đích:  {len(goals)} hộp")
    print(f"[*] Đang thực thi giải thuật {algo_name}...")

    # Chạy thuật toán đã chọn
    if algo_name == "UCS":
        actions, cost, stats = ucs_search(problem)
    else:
        actions, cost, stats = astar_search(problem)

    # Hiển thị thống kê
    print("\n" + "-" * 65)
    print("                    KẾT QUẢ TÌM KIẾM")
    print("-" * 65)
    if actions is None:
        print("[!] Không tìm thấy lời giải cho bản đồ này!")
        print(f"  + Số node đã duyệt:      {stats.get('expanded_nodes', 0):,}")
        print(f"  + Thời gian chạy:        {stats.get('time_ms', 0):.2f} ms")
        return

    print(f"  + Trạng thái:            THÀNH CÔNG (Đã tìm ra lời giải tối ưu)")
    print(f"  + Tổng chi phí (Cost):   {cost}")
    print(f"  + Số bước di chuyển:     {len(actions)}")
    print(f"  + Số node đã mở rộng:    {stats.get('expanded_nodes', 0):,}")
    print(f"  + Bộ nhớ Frontier đỉnh:  {stats.get('max_frontier_size', 0):,}")
    print(f"  + Thời gian thực thi:    {stats.get('time_ms', 0):.2f} ms")
    
    # In chuỗi hành động rút gọn
    act_str = " -> ".join(actions[:15])
    if len(actions) > 15:
        act_str += f" ... và {len(actions) - 15} bước nữa"
    print(f"  + Lộ trình di chuyển:    {act_str}")
    print("-" * 65)

    # Tái tạo chuỗi trạng thái lưới 2D cho GUI
    history_grids = []
    curr_state = init_state
    history_grids.append(state_to_grid(curr_state, walls, goals, max_row, max_col))

    for act in actions:
        next_state, _ = problem.get_successor(curr_state, act)
        history_grids.append(state_to_grid(next_state, walls, goals, max_row, max_col))
        curr_state = next_state

    # Khởi chạy Pygame GUI
    if not args.no_gui:
        print("\n[*] Đang khởi động giao diện Pygame trực quan...")
        print("  - Phím [Space]:     Tạm dừng / Tiếp tục tự động chạy")
        print("  - Phím [->] Phải:   Bước tới 1 bước (khi đang Pause)")
        print("  - Phím [<-] Trái:   Lùi lại 1 bước (khi đang Pause)")
        print("  - Phím [ESC]:       Đóng cửa sổ\n")

        view = SokobanView(title=f"AI Sokoban - Single Agent ({algo_name}) | {os.path.basename(map_file)}")
        view.set_states(history_grids, algorithm=algo_name)
        view.run_interactive()
    else:
        print("[*] Chế độ --no-gui được bật, kết thúc chương trình mà không mở GUI.")


if __name__ == "__main__":
    main()