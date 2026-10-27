"""
Module: experiments/verify_heuristic.py
Mo ta: Thuc nghiem kiem chung tinh dang tin (Admissibility) va nhat quan (Consistency) cua Heuristic Hungarian BFS.
"""

import os
import sys
import csv
from collections import deque
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

# Cau hinh font tieng Viet co dau cho Matplotlib
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Calibri', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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


def verify_heuristic_on_map(map_file: str, max_transitions_to_test: int = 2000) -> Tuple[Dict, List[float], List[float], List[float]]:
    map_name = os.path.basename(map_file)
    print(f"\n{'='*70}")
    print(f"[*] KIEM CHUNG HEURISTIC TREN BAN DO: {map_name}")
    print(f"{'='*70}")

    try:
        init_state, walls, goals, r, c = parse_map(map_file)
    except Exception as e:
        print(f"[-] Bo qua {map_name} do loi: {e}")
        return None, [], [], []

    if len(init_state.boxes_pos) < len(goals):
        return None, [], [], []

    problem = SokobanProblem(init_state, walls, goals)
    heuristic = SokobanHeuristic(problem)

    # 1. Kiem chung tinh Admissibility doc theo lo trinh toi uu
    h_start = heuristic.calculate(init_state)
    actions, cost_star, _ = astar_search(problem)

    if actions is None:
        return None, [], [], []

    admissible_violations = 0
    curr_state = init_state
    remaining_cost = cost_star

    path_h_values = []
    path_h_star_values = []

    for act in actions:
        h_curr = heuristic.calculate(curr_state)
        path_h_values.append(h_curr)
        path_h_star_values.append(remaining_cost)

        if h_curr > remaining_cost:
            admissible_violations += 1
        curr_state, step_cost = problem.get_successor(curr_state, act)
        remaining_cost -= step_cost

    h_goal = heuristic.calculate(curr_state)
    path_h_values.append(h_goal)
    path_h_star_values.append(0)

    is_goal_zero = (h_goal == 0.0)
    is_admissible = (admissible_violations == 0) and is_goal_zero and (h_start <= cost_star)

    # 2. Kiem chung tinh Consistency bang BFS
    queue = deque([init_state])
    visited = {init_state}
    transitions_tested = 0
    consistent_violations = 0
    delta_h_list = []
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
            delta_h_list.append(delta_h)
            max_delta_h = max(max_delta_h, delta_h)
            min_delta_h = min(min_delta_h, delta_h)
            transitions_tested += 1

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
    print(f"   - So trang thai kiem tra       : {len(actions) + 1}")
    print(f"   - Ket luan Admissibility       : {'THOA MAN (PASS)' if is_admissible else 'VI PHAM (FAIL)'}")

    print(f"\n2. TINH CONSISTENCY (Nhat quan):")
    print(f"   - So buoc chuyen tiep kiem tra : {transitions_tested:,}")
    print(f"   - Delta h toi da (h(s) - h(s')): {max_delta_h:.2f} (Yeu cau <= 1.0)")
    print(f"   - Delta h toi thieu            : {min_delta_h:.2f}")
    print(f"   - So lan vi pham               : {consistent_violations}")
    print(f"   - Ket luan Consistency         : {'THOA MAN (PASS)' if is_consistent else 'VI PHAM (FAIL)'}")

    summary = {
        "Map": map_name,
        "h_start": h_start,
        "h_star": cost_star,
        "Admissibility": "PASS" if is_admissible else "FAIL",
        "Transitions_Tested": transitions_tested,
        "Max_Delta_h": round(max_delta_h, 2),
        "Consistency": "PASS" if is_consistent else "FAIL"
    }
    return summary, path_h_values, path_h_star_values, delta_h_list


def plot_verification_charts(path_h, path_h_star, all_deltas, results_dir):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle('KIỂM CHỨNG TOÁN HỌC HEURISTIC HUNGARIAN BFS (TIẾNG VIỆT CÓ DẤU)', fontsize=14, fontweight='bold', y=0.98)

    # Bieu do 1: Admissibility doc lo trinh toi uu (h(s) <= h*(s))
    steps = list(range(len(path_h)))
    axes[0].plot(steps, path_h_star, label='Chi phí thực tế còn lại: h*(s)', color='#e74c3c', marker='o', linewidth=2.5)
    axes[0].plot(steps, path_h, label='Ước lượng Heuristic: h(s)', color='#27ae60', marker='s', linewidth=2, linestyle='--')
    axes[0].fill_between(steps, path_h, path_h_star, color='#2ecc71', alpha=0.2, label='Vùng Admissible hợp lệ (h ≤ h*)')
    axes[0].set_title('Kiểm chứng Admissibility: h(s) ≤ h*(s)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Số bước đi trên lộ trình tối ưu', fontsize=10)
    axes[0].set_ylabel('Giá trị Heuristic / Chi phí thực tế', fontsize=10)
    axes[0].legend(frameon=True, facecolor='white', framealpha=0.9)
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Bieu do 2: Consistency phan phoi Delta h (h(s) - h(s') <= 1)
    if all_deltas:
        axes[1].hist(all_deltas, bins=15, color='#3498db', edgecolor='black', alpha=0.85, label='Phân phối thực tế của Δh')
        axes[1].axvline(x=1.0, color='#e74c3c', linestyle='--', linewidth=2.5, label='Ngưỡng cận trên: c(s, a, s\') = 1.0')
        axes[1].set_title('Kiểm chứng Consistency: Δh = h(s) - h(s\') ≤ 1.0', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Giá trị biến thiên Heuristic Δh', fontsize=10)
        axes[1].set_ylabel('Tần suất xuất hiện (Số bước chuyển)', fontsize=10)
        axes[1].legend(frameon=True, facecolor='white', framealpha=0.9)
        axes[1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_file = os.path.join(results_dir, 'verify_heuristic_chart.png')
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"[+] Da xuat bieu do kiem chung Heuristic: {out_file}")


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    maps_dir = os.path.join(base_dir, "maps")
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    test_maps = [
        "map_01_one_box.txt",
        "map_02_two_boxes.txt",
        "map_03_three_boxes.txt"
    ]

    all_results = []
    sample_path_h = []
    sample_path_h_star = []
    combined_deltas = []

    for m in test_maps:
        fpath = os.path.join(maps_dir, m)
        if os.path.exists(fpath):
            res, ph, ph_star, deltas = verify_heuristic_on_map(fpath)
            if res:
                all_results.append(res)
                if not sample_path_h and ph:
                    sample_path_h = ph
                    sample_path_h_star = ph_star
                combined_deltas.extend(deltas)

    csv_file = os.path.join(results_dir, "verify_heuristic_results.csv")
    if all_results:
        with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n[+] Da xuat toan bo ket qua kiem chung ra: {csv_file}")

    if sample_path_h and combined_deltas:
        plot_verification_charts(sample_path_h, sample_path_h_star, combined_deltas, results_dir)


if __name__ == "__main__":
    main()
