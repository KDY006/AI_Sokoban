"""
Module: main_single.py
Mo ta: Khoi chay chuong trinh giai Sokoban che do Don tac nhan (Single-Agent).
Doc ban do, chay thuat toan tim kiem (UCS hoac A*), in thong ke va mo giao dien Pygame.
"""

import os
import sys
import argparse
from typing import List, Tuple, FrozenSet

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    # Chuyen doi State thanh ma tran 2D phuc vu hien thi GUI
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
    # Lay danh sach file ban do trong thu muc maps/
    maps_dir = os.path.join(BASE_DIR, "maps")
    valid_maps = []
    if os.path.exists(maps_dir):
        for fname in sorted(os.listdir(maps_dir)):
            if fname.endswith(".txt"):
                fpath = os.path.join(maps_dir, fname)
                if os.path.getsize(fpath) > 0 and not fname.startswith("competitive_map"):
                    valid_maps.append(fpath)
    return valid_maps


def interactive_select_options() -> Tuple[str, str]:
    # Hien thi menu chon ban do va thuat toan
    maps = get_available_maps()
    print("=" * 65)
    print("        HE THONG GIAI SOKOBAN DON TAC NHAN (SINGLE-AGENT)")
    print("=" * 65)

    print("\n--- [BUOC 1] CHON BAN DO ---")
    for idx, mpath in enumerate(maps, 1):
        mname = os.path.basename(mpath)
        print(f"  {idx}. {mname}")
    print(f"  {len(maps) + 1}. Nhap duong dan file ban do tuy chinh...")

    default_map = maps[0] if maps else os.path.join(BASE_DIR, "maps", "example_map.txt")
    choice_map = input(f"\nChon ban do [1-{len(maps) + 1}] (Mac dinh 1 - {os.path.basename(default_map)}): ").strip()

    selected_map = default_map
    if choice_map.isdigit():
        val = int(choice_map)
        if 1 <= val <= len(maps):
            selected_map = maps[val - 1]
        elif val == len(maps) + 1:
            custom_path = input("Nhap duong dan file map: ").strip()
            if os.path.exists(custom_path):
                selected_map = custom_path
            else:
                print(f"[!] Khong tim thay file {custom_path}, su dung mac dinh: {os.path.basename(default_map)}")
    elif choice_map:
        if os.path.exists(choice_map):
            selected_map = choice_map

    print("\n--- [BUOC 2] CHON THUAT TOAN TIM KIEM ---")
    print("  1. UCS  - Uniform Cost Search")
    print("  2. A*   - A* Search (Hungarian BFS Heuristic)")
    choice_algo = input("\nChon thuat toan [1/2] (Mac dinh 2 - A*): ").strip()

    selected_algo = "A*" if choice_algo in ["2", "astar", "A*", "a*"] else "UCS"
    if choice_algo == "1" or choice_algo.lower() == "ucs":
        selected_algo = "UCS"

    return selected_map, selected_algo


def main():
    parser = argparse.ArgumentParser(description="Chuong trinh giai Sokoban Single-Agent")
    parser.add_argument("--map", type=str, default=None, help="Duong dan file ban do")
    parser.add_argument("--algo", type=str, choices=["ucs", "astar", "UCS", "A*"], default=None, help="Thuat toan: ucs hoac astar")
    args = parser.parse_args()

    if args.map is not None and args.algo is not None:
        map_file = args.map
        algo_name = "A*" if args.algo.lower() == "astar" else "UCS"
    else:
        map_file, algo_name = interactive_select_options()

    if not os.path.exists(map_file):
        print(f"[X] Loi: Khong tim thay file ban do: {map_file}")
        return

    print("\n" + "=" * 65)
    print(f"[*] Ban do da chon: {os.path.basename(map_file)}")
    print(f"[*] Thuat toan:     {algo_name}")
    print("=" * 65)

    # Doc file ban do
    try:
        init_state, walls, goals, max_row, max_col = parse_map(map_file)
    except Exception as e:
        print(f"[X] Loi doc ban do: {e}")
        return

    num_boxes = len(init_state.boxes_pos)
    num_goals = len(goals)

    # Kiem tra cac truong hop bat kha thi ban dau
    if num_goals == 0:
        print("[!] Ban do khong co o dich. Loi ban do, khong the giai duoc.")
        return

    if num_boxes == 0:
        print("[!] Ban do khong co hop. Loi ban do, khong the giai duoc.")
        return

    if num_boxes < num_goals:
        print(f"[!] So hop ({num_boxes}) it hon so o dich ({num_goals}). Loi ban do, khong the giai duoc.")
        return

    if num_boxes > num_goals:
        print(f"[*] Ban do du thung: {num_boxes} hop cho {num_goals} dich.")

    problem = SokobanProblem(init_state, walls, goals)
    print(f"[*] Kich thuoc me cung: {max_row} hang x {max_col} cot")
    print(f"[*] So luong hop/dich:  {num_boxes} hop / {num_goals} dich")
    print(f"[*] Dang chay giai thuat {algo_name}...")

    # Chay thuat toan tim kiem
    if algo_name == "UCS":
        actions, cost, stats = ucs_search(problem)
    else:
        actions, cost, stats = astar_search(problem)

    print("\n" + "-" * 65)
    print("                    KET QUA TIM KIEM")
    print("-" * 65)
    if actions is None:
        print("[!] Khong tim thay loi giai. Ket thuc tro choi.")
        print(f"  - So node da mo rong:    {stats.get('expanded_nodes', 0):,}")
        print(f"  - Bo nho Frontier dinh:  {stats.get('max_frontier_size', 0):,}")
        print(f"  - Thoi gian chay:        {stats.get('time_ms', 0):.2f} ms")
    else:
        print("[OK] Tim thay loi giai thanh cong:")
        print(f"  - So buoc hanh dong:     {len(actions):,} buoc")
        print(f"  - Tong chi phi:          {cost}")
        print(f"  - So node da mo rong:    {stats.get('expanded_nodes', 0):,}")
        print(f"  - Bo nho Frontier dinh:  {stats.get('max_frontier_size', 0):,}")
        print(f"  - Thoi gian chay:        {stats.get('time_ms', 0):.2f} ms")
        print(f"  - Chuoi hanh dong:       {', '.join(actions[:10])}{' ...' if len(actions) > 10 else ''}")

        # Tai tao chuoi trang thai grid 2D cho Replay
        states_for_view = [state_to_grid(init_state, walls, goals, max_row, max_col)]
        curr_state = init_state
        for act in actions:
            curr_state, _ = problem.get_successor(curr_state, act)
            states_for_view.append(state_to_grid(curr_state, walls, goals, max_row, max_col))

        # Mo giao dien do hoa
        print("\n[*] Dang mo giao dien Pygame...")
        print("    [Space]: Tam dung / Tiep tuc | [->]: Buoc toi | [<-]: Lui buoc | [ESC]: Thoat")
        view = SokobanView(title=f"AI Sokoban - {os.path.basename(map_file)} | {algo_name}")
        view.set_states(states_for_view, algorithm=algo_name)
        view.run()


if __name__ == "__main__":
    main()
