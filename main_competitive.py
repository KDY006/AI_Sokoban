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

Quy ước ký hiệu bản đồ chế độ đối kháng (Two-Agent Map Legend):
  % : Tường / Chướng ngại vật cố định (Wall)
  ' ' : Ô trống nền (Empty floor)
  D : Ô đích chung (Designated goal)
  B : Hộp tự do trung lập (Neutral box)
  A : Vị trí Player 1 (Màu Xanh Dương)
  P : Vị trí Player 2 (Màu Cam)
  C : Hộp đã vào đích được ghi điểm bởi Player 1 (+1 điểm cho P1)
  K : Hộp đã vào đích được ghi điểm bởi Player 2 (+1 điểm cho P2)
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
    """Hoi nguoi dung so buoc toi da n va chon ban do thi dau."""
    print("=" * 70)
    print("      HE THONG THI DAU DOI KHANG 2 AGENT SOKOBAN (COMPETITIVE R6-R8)")
    print("=" * 70)

    # 1. Nhập số bước n
    default_n = 50
    user_input = input(f"\nNhap so buoc toi da n (Mac dinh {default_n}): ").strip()
    max_steps = default_n
    if user_input.isdigit() and int(user_input) > 0:
        max_steps = int(user_input)

    # 2. Chọn map
    default_map = os.path.join(BASE_DIR, "maps", "competitive_map.txt")
    print(f"\nBan do thi dau mac dinh: {os.path.basename(default_map)}")
    map_choice = input("Nhan Enter de dung mac dinh, hoac nhap duong dan map: ").strip()

    selected_map = default_map
    if map_choice and os.path.exists(map_choice):
        selected_map = map_choice

    return max_steps, selected_map


def main():
    parser = argparse.ArgumentParser(description="Chuong trinh thi dau doi khang 2 Agent Sokoban (R6, R7, R8)")
    parser.add_argument("--steps", "-n", type=int, default=None, help="So buoc toi da n cho tran dau")
    parser.add_argument("--map", type=str, default=None, help="Duong dan file ban do thi dau")
    parser.add_argument("--no-gui", action="store_true", help="Chay mo phong in log ra console, khong mo Pygame GUI")
    args = parser.parse_args()

    # Nhập số bước và bản đồ
    if args.steps is not None:
        max_steps = args.steps
        map_file = args.map if args.map else os.path.join(BASE_DIR, "maps", "competitive_map.txt")
    else:
        max_steps, map_file = interactive_input_steps()

    if not os.path.exists(map_file):
        print(f"[X] Loi: Khong tim thay file ban do: {map_file}")
        return

    print("\n" + "=" * 70)
    print(f"[*] Ban do thi dau:     {os.path.basename(map_file)}")
    print(f"[*] So buoc toi da (n): {max_steps} buoc")
    print(f"[*] Player 1 (A):       agent_player1 (A* Search - Mau Xanh)")
    print(f"[*] Player 2 (P):       agent_player2 (Greedy Best-First - Mau Cam)")
    print(f"[*] Co che va cham:     Xac suat p ~ Uniform(0, 1) | p < 0.5: P1 di, p >= 0.5: P2 di")
    print("=" * 70)

    # Khởi tạo môi trường và 2 tác nhân
    env = TwoAgentEnv(map_file, max_steps=max_steps)
    p1 = agent_player1()
    p2 = agent_player2()

    # Lưu lịch sử ban đầu (bước 0)
    history_states: List[List[List[str]]] = [copy.deepcopy(env.grid)]
    history_scores: List[Tuple[int, int]] = [(0, 0)]

    print("\n[*] BAT DAU TRAN THI DAU DOI KHANG...")
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
            print(f"  [!] CANH BAO: Player 1 vuot qua thoi gian quy dinh ({t1_elapsed:.1f} ms > 1,000 ms)!")
        if t2_elapsed > 1000.0:
            print(f"  [!] CANH BAO: Player 2 vuot qua thoi gian quy dinh ({t2_elapsed:.1f} ms > 1,000 ms)!")

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
        conflict_msg = " | [XUNG DOT PHAT SINH - Xu ly theo xac suat p ~ U(0,1)]" if has_conflict else ""

        print(
            f"  Buoc {step:02d}/{max_steps}: "
            f"P1 (A) -> {act1:<5} ({t1_elapsed:4.1f}ms) | "
            f"P2 (P) -> {act2:<5} ({t2_elapsed:4.1f}ms) | "
            f"Diem: {score_p1} - {score_p2}{conflict_msg}"
        )

        if env.is_game_over():
            break

    # Phân định thắng bại sau n bước
    final_p1, final_p2 = env.get_scores()
    print("-" * 70)
    print("                    KET QUA CHUNG CUOC")
    print("-" * 70)
    print(f"  + Tong so buoc hoan thanh: {len(history_states) - 1} / {max_steps}")
    print(f"  + Diem Player 1 (A):        {final_p1} hop tren dich (Thung 'C')")
    print(f"  + Diem Player 2 (P):        {final_p2} hop tren dich (Thung 'K')")

    if final_p1 > final_p2:
        winner_text = "PLAYER 1 CHIEN THANG!"
    elif final_p2 > final_p1:
        winner_text = "PLAYER 2 CHIEN THANG!"
    else:
        winner_text = "KET QUA HOA NHAU!"

    print(f"  ==> {winner_text}")
    print("-" * 70)

    # Khởi chạy giao diện Pygame hiển thị kết quả
    if not args.no_gui:
        print("\n[*] Dang khoi dong giao dien Pygame truc quan...")
        print("  - Phim [Space]:     Tam dung / Tiep tuc tu dong dien hoat")
        print("  - Phim [->] Phai:   Buoc toi 1 luot (khi dang Pause)")
        print("  - Phim [<-] Trai:   Lui lai 1 luot (khi dang Pause)")
        print("  - Phim [ESC]:       Dong cua so\n")

        view = SokobanView(title=f"AI Sokoban - Competitive Match ({final_p1} - {final_p2}) | n={max_steps}")
        view.set_competitive_history(states=history_states, scores=history_scores, max_steps=max_steps)
        view.run_interactive()
    else:
        print("[*] Che do --no-gui duoc bat, ket thuc chuong trinh ma khong mo GUI.")


if __name__ == "__main__":
    main()
