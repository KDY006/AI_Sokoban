"""
Module: main_competitive.py
Mục đích: Điểm khởi chạy chính cho chế độ Thi đấu đối kháng 2 Tác nhân (Competitive Two-Agent - R6, R7, R8).
Tính năng:
  - Cho phép người dùng nhập số bước n từ bàn phím theo yêu cầu đề bài.
  - Tải bản đồ thi đấu đối kháng (mặc định maps/competitive_map.txt).
  - Tích hợp 2 tác nhân độc lập: agent_player1 (A* Search) và agent_player2 (Greedy Best-First).
  - Giám sát thời gian ra quyết định mỗi bước (đảm bảo <= 1,000 ms).
  - Mô phỏng cơ chế xử lý va chạm xác suất: p ~ Uniform(0, 1) (p < 0.5: P1 đi, ngược lại P2 đi).
  - Ghi nhận lịch sử trạng thái, điểm số thời gian thực và xác định người thắng cuộc.
  - Khởi chạy giao diện Pygame hiển thị trận đấu với màu hộp riêng biệt cho từng bên.
"""

import os
import sys
import copy
import time
import argparse
from typing import List, Tuple

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

from competitive.two_agent_env import TwoAgentEnv
from competitive.agent_player1 import agent_player1
from competitive.agent_player2 import agent_player2
from gui.game_view import SokobanView


def interactive_input_steps() -> Tuple[int, str]:
    """Hỏi người dùng số bước tối đa n và chọn bản đồ thi đấu."""
    print("=" * 70)
    print("      HỆ THỐNG THI ĐẤU ĐỐI KHÁNG 2 AGENT SOKOBAN (COMPETITIVE R6-R8)")
    print("=" * 70)

    # 1. Nhập số bước n
    default_n = 50
    user_input = input(f"\nNhập số bước tối đa n (Mặc định {default_n}): ").strip()
    max_steps = default_n
    if user_input.isdigit() and int(user_input) > 0:
        max_steps = int(user_input)

    # 2. Chọn map
    default_map = os.path.join(BASE_DIR, "maps", "competitive_map.txt")
    print(f"\nBản đồ thi đấu mặc định: {os.path.basename(default_map)}")
    map_choice = input("Nhấn Enter để dùng mặc định, hoặc nhập đường dẫn map: ").strip()

    selected_map = default_map
    if map_choice and os.path.exists(map_choice):
        selected_map = map_choice

    return max_steps, selected_map


def main():
    parser = argparse.ArgumentParser(description="Chương trình thi đấu đối kháng 2 Agent Sokoban (R6, R7, R8)")
    parser.add_argument("--steps", "-n", type=int, default=None, help="Số bước tối đa n cho trận đấu")
    parser.add_argument("--map", type=str, default=None, help="Đường dẫn file bản đồ thi đấu")
    parser.add_argument("--no-gui", action="store_true", help="Chạy mô phỏng in log ra console, không mở Pygame GUI")
    args = parser.parse_args()

    # Nhập số bước và bản đồ
    if args.steps is not None:
        max_steps = args.steps
        map_file = args.map if args.map else os.path.join(BASE_DIR, "maps", "competitive_map.txt")
    else:
        max_steps, map_file = interactive_input_steps()

    if not os.path.exists(map_file):
        print(f"[X] Lỗi: Không tìm thấy file bản đồ: {map_file}")
        return

    print("\n" + "=" * 70)
    print(f"[*] Bản đồ thi đấu:     {os.path.basename(map_file)}")
    print(f"[*] Số bước tối đa (n): {max_steps} bước")
    print(f"[*] Player 1 (A):       agent_player1 (A* Search - Màu Xanh)")
    print(f"[*] Player 2 (P):       agent_player2 (Greedy Best-First - Màu Cam)")
    print(f"[*] Cơ chế va chạm:     Xác suất p ~ Uniform(0, 1) | p < 0.5: P1 đi, p >= 0.5: P2 đi")
    print("=" * 70)

    # Khởi tạo môi trường và 2 tác nhân
    env = TwoAgentEnv(map_file, max_steps=max_steps)
    p1 = agent_player1()
    p2 = agent_player2()

    # Lưu lịch sử ban đầu (bước 0)
    history_states: List[List[List[str]]] = [copy.deepcopy(env.grid)]
    history_scores: List[Tuple[int, int]] = [(0, 0)]

    print("\n[*] BẮT ĐẦU TRẬN THI ĐẤU ĐỐI KHÁNG...")
    print("-" * 70)

    # Vòng lặp thi đấu n bước
    for step in range(1, max_steps + 1):
        # 1. Player 1 quyết định hành động
        t1_start = time.perf_counter()
        act1 = p1.get_act(copy.deepcopy(env.grid), env.p1_pos)
        t1_elapsed = (time.perf_counter() - t1_start) * 1000

        # 2. Player 2 quyết định hành động
        t2_start = time.perf_counter()
        act2 = p2.get_act(copy.deepcopy(env.grid), env.p2_pos)
        t2_elapsed = (time.perf_counter() - t2_start) * 1000

        # Cảnh báo nếu có agent vượt quá thời gian cho phép 1,000 ms (R7)
        if t1_elapsed > 1000.0:
            print(f"  [!] CẢNH BÁO: Player 1 vượt quá thời gian quy định ({t1_elapsed:.1f} ms > 1,000 ms)!")
        if t2_elapsed > 1000.0:
            print(f"  [!] CẢNH BÁO: Player 2 vượt quá thời gian quy định ({t2_elapsed:.1f} ms > 1,000 ms)!")

        # 3. Kiểm tra xung đột và thực thi hành động qua môi trường
        has_conflict = False
        if hasattr(env, "check_conflict"):
            try:
                has_conflict = env.check_conflict(act1, act2)
            except Exception:
                has_conflict = False

        env.step(act1, act2)
        score_p1, score_p2 = env.get_scores()

        # Lưu lại lịch sử phục vụ hiển thị trên giao diện
        history_states.append(copy.deepcopy(env.grid))
        history_scores.append((score_p1, score_p2))

        # In log chi tiết từng bước
        conflict_msg = " | [XUNG ĐỘT PHÁT SINH - Xử lý theo xác suất p ~ U(0,1)]" if has_conflict else ""

        print(
            f"  Bước {step:02d}/{max_steps}: "
            f"P1 (A) -> {act1:<5} ({t1_elapsed:4.1f}ms) | "
            f"P2 (P) -> {act2:<5} ({t2_elapsed:4.1f}ms) | "
            f"Điểm: {score_p1} - {score_p2}{conflict_msg}"
        )

        if env.is_game_over():
            break

    # Phân định thắng bại sau n bước
    final_p1, final_p2 = env.get_scores()
    print("-" * 70)
    print("                    KẾT QUẢ CHUNG CUỘC")
    print("-" * 70)
    print(f"  + Tổng số bước hoàn thành: {len(history_states) - 1} / {max_steps}")
    print(f"  + Điểm Player 1 (A):        {final_p1} hộp trên đích (Thùng 'C')")
    print(f"  + Điểm Player 2 (P):        {final_p2} hộp trên đích (Thùng 'K')")

    if final_p1 > final_p2:
        winner_text = "PLAYER 1 CHIẾN THẮNG!"
    elif final_p2 > final_p1:
        winner_text = "PLAYER 2 CHIẾN THẮNG!"
    else:
        winner_text = "KẾT QUẢ HÒA NHAU!"

    print(f"  ==> {winner_text}")
    print("-" * 70)

    # Khởi chạy giao diện Pygame hiển thị kết quả
    if not args.no_gui:
        print("\n[*] Đang khởi động giao diện Pygame trực quan...")
        print("  - Phím [Space]:     Tạm dừng / Tiếp tục tự động diễn hoạt")
        print("  - Phím [->] Phải:   Bước tới 1 lượt (khi đang Pause)")
        print("  - Phím [<-] Trái:   Lùi lại 1 lượt (khi đang Pause)")
        print("  - Phím [ESC]:       Đóng cửa sổ\n")

        view = SokobanView(title=f"AI Sokoban - Competitive Match ({final_p1} - {final_p2}) | n={max_steps}")
        view.set_competitive_history(states=history_states, scores=history_scores, max_steps=max_steps)
        view.run_interactive()
    else:
        print("[*] Chế độ --no-gui được bật, kết thúc chương trình mà không mở GUI.")


if __name__ == "__main__":
    main()
