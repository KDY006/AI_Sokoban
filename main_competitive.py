"""
Module: main_competitive.py
Mo ta: Khoi chay che do thi dau doi khang 2 Tac nhan (Competitive Two-Agent).
Quan ly vong dau n buoc, xu ly xung dot ngau nhien, tinh diem va mo giao dien Pygame.
"""

import os
import sys
import copy
import time
import argparse
from typing import List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from competitive.two_agent_env import TwoAgentEnv
from competitive.agent_player1 import agent_player1
from competitive.agent_player2 import agent_player2
from gui.game_view import SokobanView


def interactive_input_steps() -> Tuple[int, str]:
    # Menu nhap so buoc va chon ban do thi dau
    print("=" * 70)
    print("      HE THONG THI DAU DOI KHANG 2 AGENT SOKOBAN (COMPETITIVE R6-R8)")
    print("=" * 70)

    default_n = 50
    user_input = input(f"\nNhap so buoc toi da n (Mac dinh {default_n}): ").strip()
    max_steps = default_n
    if user_input.isdigit() and int(user_input) > 0:
        max_steps = int(user_input)

    print("\n--- CHON BAN DO THI DAU ---")
    print("  1. competitive_map_v1.txt (Dau truong mo - Arena Open Layout)")
    print("  2. competitive_map_v2.txt (Dau truong co tru can - Tactical Pillars)")
    choice_map = input("Chon ban do [1/2] (Mac dinh 1): ").strip()

    if choice_map == "2":
        selected_map_name = "competitive_map_v2.txt"
    else:
        selected_map_name = "competitive_map_v1.txt"

    map_path = os.path.join(BASE_DIR, "maps", selected_map_name)
    return max_steps, map_path


def main():
    parser = argparse.ArgumentParser(description="Che do thi dau doi khang 2 Agent Sokoban")
    parser.add_argument("--steps", type=int, default=None, help="So buoc toi da n")
    parser.add_argument("--map", type=str, default=None, help="Duong dan file ban do thi dau")
    args = parser.parse_args()

    if args.steps is not None and args.map is not None:
        max_steps = args.steps
        map_path = args.map
    elif args.steps is not None:
        max_steps = args.steps
        map_path = os.path.join(BASE_DIR, "maps", "competitive_map_v1.txt")
    else:
        max_steps, map_path = interactive_input_steps()

    if not os.path.exists(map_path):
        print(f"[X] Loi: Khong tim thay file ban do: {map_path}")
        return

    print("\n" + "=" * 70)
    print(f"[*] Khoi tao dau truong: {os.path.basename(map_path)}")
    print(f"[*] So buoc thi dau toi da: n = {max_steps}")
    print("=" * 70)

    # Khoi tao moi truong va 2 tac nhan
    env = TwoAgentEnv(map_path, max_steps)
    p1 = agent_player1()
    p2 = agent_player2()

    history_states = [copy.deepcopy(env.grid)]
    history_scores = [[0, 0]]

    # Vong lap thi dau tung buoc
    for step in range(1, max_steps + 1):
        grid_for_p1 = copy.deepcopy(env.grid)
        grid_for_p2 = copy.deepcopy(env.grid)

        t1_start = time.perf_counter()
        act1 = p1.get_act(grid_for_p1, env.p1_pos)
        t1_elapsed = (time.perf_counter() - t1_start) * 1000

        t2_start = time.perf_counter()
        act2 = p2.get_act(grid_for_p2, env.p2_pos)
        t2_elapsed = (time.perf_counter() - t2_start) * 1000

        # Thuc hien buoc di trong moi truong
        env.step(act1, act2)
        score1, score2 = env.get_scores()

        history_states.append(copy.deepcopy(env.grid))
        history_scores.append([score1, score2])

        if step % 10 == 0 or step == max_steps or step <= 5:
            print(f"  + Buoc {step:3d}/{max_steps} | P1: {act1:5s} ({t1_elapsed:4.1f}ms) | P2: {act2:5s} ({t2_elapsed:4.1f}ms) | Diem: P1={score1} - P2={score2}")

        if env.is_game_over():
            break

    # Tong ket ket qua tran dau
    final_s1, final_s2 = env.get_scores()
    print("\n" + "=" * 70)
    print("                    KET QUA THI DAU CHUNG CUOC")
    print("=" * 70)
    print(f"[*] Tong so buoc da dau:  {env.current_step} / {max_steps}")
    print(f"[*] Diem so Player 1:     {final_s1} diem (Thung Xam 'C')")
    print(f"[*] Diem so Player 2:     {final_s2} diem (Thung Xanh 'K')")

    if final_s1 > final_s2:
        print("[*] Ket luan:             PLAYER 1 (A* Search) CHIEN THANG!")
    elif final_s2 > final_s1:
        print("[*] Ket luan:             PLAYER 2 (Greedy Best-First) CHIEN THANG!")
    else:
        print("[*] Ket luan:             HAI BEN HOA NHAU!")
    print("=" * 70)

    # Mo giao dien do hoa
    print("\n[*] Dang mo giao dien Pygame...")
    print("    [Space]: Tam dung / Tiep tuc | [->]: Buoc toi | [<-]: Lui buoc | [ESC]: Thoat")
    view = SokobanView(title=f"AI Sokoban - Competitive Match ({final_s1} - {final_s2}) | n={max_steps}")
    view.set_competitive_history(history_states, history_scores, max_steps)
    view.run()


if __name__ == "__main__":
    main()
