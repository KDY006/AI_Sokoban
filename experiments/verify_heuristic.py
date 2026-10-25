"""
Module: experiments/verify_heuristic.py
Mo ta: Thuc nghiem kiem chung tinh dang tin (Admissibility) va nhat quan (Consistency) cua ham Heuristic Hungarian BFS.
"""

import os
import sys
import csv
from collections import deque
from typing import Dict, List, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import parse_map
from core.problem import SokobanProblem
from search.astar import astar_search
from search.heuristic import SokobanHeuristic


def verify_heuristic_on_map(map_file: str, max_transitions_to_test: int = 2000) -> Dict:
    # Kiem chung Admissibility va Consistency tren mot ban do cu the
    map_name = os.path.basename(map_file)
    print(f"\n{'='*70}")
    print(f"[*] KIEM CHUNG HEURISTIC TREN BAN DO: {map_name}")
    print(f"{'='*70}")

    try:
        init_state, walls, goals, r, c = parse_map(map_file)
    except Exception as e:
        print(f"[-] Bo qua {map_name} do loi: {e}")
        return None

    if len(init_state.boxes_pos) < len(goals):
        return None

    problem = SokobanProblem(init_state, walls, goals)
    heuristic = SokobanHeuristic(problem)

    # 1. Kiem chung tinh Admissibility
    h_start = heuristic.calculate(init_state)
    actions, cost_star, _ = astar_search(problem)

    if actions is None:
        return None

    admissible_violations = 0
    curr_state = init_state
    remaining_cost = cost_star

    # Duyet doc theo loi giai toi uu de so sanh h(s) voi h*(s)
    for act in actions:
        h_curr = heuristic.calculate(curr_state)
        if h_curr > remaining_cost:
            admissible_violations += 1
        curr_state, step_cost = problem.get_successor(curr_state, act)
        remaining_cost -= step_cost

    h_goal = heuristic.calculate(curr_state)
    is_goal_zero = (h_goal == 0.0)
    is_admissible = (admissible_violations == 0) and is_goal_zero and (h_start <= cost_star)

    # 2. Kiem chung tinh Consistency bang BFS
    queue = deque([init_state])
    visited = {init_state}
    transitions_tested = 0
    consistent_violations = 0
    max_delta_h = -float("inf")
    min_delta_h = float("inf")

    while queue and transitions_tested < max_transitions_to_test:
        s = queue.popleft()
        h_s = heuristic.calculate(s)
        if h_s == float("inf"):
            continue

        for act in problem.get_actions(s):
            s_next, step_c = problem.get_successor(s, act)
            h_next = heuristic.calculate(s_next)
            if h_next == float("inf"):
                continue

            delta_h = h_s - h_next
            max_delta_h = max(max_delta_h, delta_h)
            min_delta_h = min(min_delta_h, delta_h)
            transitions_tested += 1

            # Kiem tra dieu kien nhat quan: h(s) - h(s') <= c(s, a, s') = 1
            if delta_h > step_c + 1e-6:
                consistent_violations += 1

            if s_next not in visited:
                visited.add(s_next)
                queue.append(s_next)

    is_consistent = (consistent_violations == 0)

    # In bao cao ket qua
    print(f"\n--- BAO CAO KET QUA CHO {map_name} ---")
    print(f"1. TINH ADMISSIBILITY (Dang tin):")
    print(f"   - Chi phi toi uu h*(S0)        : {cost_star}")
    print(f"   - Heuristic uoc luong h(S0)    : {h_start}")
    print(f"   - h(Goal) = 0                  : {'DUNG (0.0)' if is_goal_zero else 'SAI'}")
    print(f"   - So trang thai da test        : {len(actions)}")
    print(f"   - Ket luan Admissibility       : {'THOA MAN (PASS)' if is_admissible else 'VI PHAM (FAIL)'}")

    print(f"\n2. TINH CONSISTENCY (Nhat quan):")
    print(f"   - So buoc chuyen tiep da test  : {transitions_tested:,}")
    print(f"   - Delta h toi da (h(s) - h(s')): {max_delta_h:.2f} (Yeu cau <= 1.0)")
    print(f"   - Delta h toi thieu            : {min_delta_h:.2f}")
    print(f"   - So vi pham                   : {consistent_violations}")
    print(f"   - Ket luan Consistency         : {'THOA MAN (PASS)' if is_consistent else 'VI PHAM (FAIL)'}")

    return {
        "Map": map_name,
        "h_start": h_start,
        "h_star": cost_star,
        "Admissibility": "PASS" if is_admissible else "FAIL",
        "Transitions_Tested": transitions_tested,
        "Max_Delta_h": round(max_delta_h, 2),
        "Consistency": "PASS" if is_consistent else "FAIL"
    }


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    maps_dir = os.path.join(base_dir, "maps")
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    test_maps = [
        "example_map.txt",
        "map_02_two_boxes.txt",
        "map_03_three_boxes.txt",
        "map_04_four_boxes.txt"
    ]

    all_results = []
    for m in test_maps:
        fpath = os.path.join(maps_dir, m)
        if os.path.exists(fpath):
            res = verify_heuristic_on_map(fpath)
            if res:
                all_results.append(res)

    # Xuat ket qua ra tap tin CSV
    csv_file = os.path.join(results_dir, "verify_heuristic_results.csv")
    if all_results:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n[+] Da xuat toan bo ket qua kiem chung ra: {csv_file}")


if __name__ == "__main__":
    main()
