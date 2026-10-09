"""
Module: experiments/verify_heuristic.py
Phụ trách: Quý
Mô tả: Script thực nghiệm tự động kiểm chứng tính Admissibility (đáng tin)
       và Consistency (nhất quán) của hàm Heuristic Hungarian BFS (R4).
       Kết xuất bảng kết quả tổng hợp ra màn hình console và file CSV.
"""

import os
import sys
import csv
from collections import deque
from typing import Dict, List, Tuple

# Đảm bảo console Windows không bị lỗi bảng mã cp1252
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Đảm bảo đường dẫn import từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import parse_map
from core.problem import SokobanProblem
from search.astar import astar_search, SokobanHeuristic


def verify_heuristic_on_map(map_file: str, max_transitions_to_test: int = 2000) -> Dict:
    """
    Kiểm chứng Admissibility và Consistency trên một bản đồ cụ thể:
    1. Kiểm chứng Admissibility:
       - h(Goal) == 0.
       - h(S0) <= h*(S0) (tính tối ưu từ nghiệm A*).
       - h(S_k) <= h*(S_k) trên toàn bộ các trạng thái dọc theo đường đi nghiệm tối ưu.
    2. Kiểm chứng Consistency:
       - Duyệt BFS không gian trạng thái từ S0.
       - Với mọi bước chuyển (s -> s') với chi phí c = 1: kiểm tra h(s) - h(s') <= 1.
    """
    map_name = os.path.basename(map_file)
    print(f"\n{'='*70}")
    print(f"[*] KIỂM CHỨNG HEURISTIC TRÊN BẢN ĐỒ: {map_name}")
    print(f"{'='*70}")

    try:
        init_state, walls, goals, r, c = parse_map(map_file)
    except Exception as e:
        print(f"[-] Bỏ qua {map_name} do lỗi đọc file: {e}")
        return {}

    problem = SokobanProblem(init_state, walls, goals)
    heuristic = SokobanHeuristic(problem)

    # 1. Tìm đường đi nghiệm tối ưu bằng A*
    actions, opt_cost, stats = astar_search(problem)
    if actions is None:
        print("[-] Bản đồ không có lời giải, bỏ qua kiểm chứng.")
        return {}

    # --- KIỂM CHỨNG ADMISSIBILITY ---
    # a. Kiểm tra tại trạng thái ban đầu S0
    h_s0 = heuristic.calculate(problem.initial_state)
    is_admissible_s0 = (h_s0 <= opt_cost)

    # b. Kiểm tra dọc theo đường đi nghiệm tối ưu
    curr_state = problem.initial_state
    path_admissible = True
    path_states_tested = 0
    max_h_star_gap = 0.0

    if h_s0 <= opt_cost:
        max_h_star_gap = max(max_h_star_gap, opt_cost - h_s0)

    for step_idx, act in enumerate(actions):
        next_st, _ = problem.get_successor(curr_state, act)
        remaining_opt_cost = opt_cost - (step_idx + 1)
        h_val = heuristic.calculate(next_st)
        path_states_tested += 1

        if h_val > remaining_opt_cost:
            path_admissible = False
            print(f"  [!] Vi phạm Admissibility tại bước {step_idx + 1}: h = {h_val} > h* = {remaining_opt_cost}")
            break

        curr_state = next_st

    # c. Kiểm tra Goal State: h(Goal) phải bằng 0
    goal_h = heuristic.calculate(curr_state)
    is_goal_zero = (goal_h == 0.0)

    admissible_overall = is_admissible_s0 and path_admissible and is_goal_zero

    # --- KIỂM CHỨNG CONSISTENCY ---
    # Duyệt BFS không gian trạng thái thực tế để kiểm tra mọi cạnh (s -> s')
    queue = deque([problem.initial_state])
    visited = {problem.initial_state}
    tested_transitions = 0
    inconsistent_cases = 0
    max_delta_h = -float('inf')
    min_delta_h = float('inf')

    while queue and tested_transitions < max_transitions_to_test:
        curr = queue.popleft()
        h_curr = heuristic.calculate(curr)
        if h_curr == float('inf'):
            continue

        for action in problem.get_actions(curr):
            succ, step_cost = problem.get_successor(curr, action)
            h_succ = heuristic.calculate(succ)
            tested_transitions += 1

            if h_succ != float('inf'):
                delta_h = h_curr - h_succ
                max_delta_h = max(max_delta_h, delta_h)
                min_delta_h = min(min_delta_h, delta_h)

                # Điều kiện Consistent: h(s) <= step_cost + h(s') <=> h(s) - h(s') <= step_cost
                if delta_h > step_cost:
                    inconsistent_cases += 1
                    print(f"  [!] Vi phạm Consistent: h(s)={h_curr}, h(s')={h_succ}, c={step_cost}, delta={delta_h}")

            if succ not in visited and tested_transitions < max_transitions_to_test:
                visited.add(succ)
                queue.append(succ)

    consistent_overall = (inconsistent_cases == 0)

    # In kết quả kiểm chứng
    print(f"\n--- BÁO CÁO KẾT QUẢ CHO {map_name} ---")
    print(f"1. TÍNH ADMISSIBILITY (Đáng tin):")
    print(f"   - Chi phí tối ưu h*(S0)        : {opt_cost}")
    print(f"   - Heuristic ước lượng h(S0)    : {h_s0}")
    print(f"   - h(Goal) = 0                  : {'ĐÚNG (0.0)' if is_goal_zero else 'SAI'}")
    print(f"   - Số trạng thái trên đường tối ưu đã test : {path_states_tested}")
    print(f"   - Kết luận Admissibility       : {'THỎA MÃN (PASS)' if admissible_overall else 'VI PHẠM (FAIL)'}")

    print(f"\n2. TÍNH CONSISTENCY (Nhất quán / Đơn điệu):")
    print(f"   - Số bước chuyển tiếp đã test  : {tested_transitions:,}")
    print(f"   - Delta h tối đa (h(s) - h(s')): {max_delta_h:.2f} (Yêu cầu <= 1.0)")
    print(f"   - Delta h tối thiểu            : {min_delta_h:.2f}")
    print(f"   - Số vi phạm tính nhất quán    : {inconsistent_cases}")
    print(f"   - Kết luận Consistency         : {'THỎA MÃN (PASS)' if consistent_overall else 'VI PHẠM (FAIL)'}")

    return {
        'Map': map_name,
        'Optimal_Cost_h_star': opt_cost,
        'Initial_h': h_s0,
        'Admissible_S0': is_admissible_s0,
        'Goal_h_Zero': is_goal_zero,
        'Path_States_Tested': path_states_tested,
        'Admissible_Overall': 'PASS' if admissible_overall else 'FAIL',
        'Transitions_Tested': tested_transitions,
        'Max_Delta_h': round(max_delta_h, 2) if max_delta_h != -float('inf') else 0.0,
        'Min_Delta_h': round(min_delta_h, 2) if min_delta_h != float('inf') else 0.0,
        'Inconsistent_Count': inconsistent_cases,
        'Consistent_Overall': 'PASS' if consistent_overall else 'FAIL'
    }


def run_all_verifications():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    maps_dir = os.path.join(base_dir, 'maps')

    candidate_files = []
    if os.path.exists(maps_dir):
        for fname in sorted(os.listdir(maps_dir)):
            if fname.endswith('.txt'):
                fpath = os.path.join(maps_dir, fname)
                if os.path.getsize(fpath) > 0:
                    candidate_files.append(fpath)

    all_results = []
    for m in candidate_files:
        res = verify_heuristic_on_map(m)
        if res:
            all_results.append(res)

    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)
    csv_file = os.path.join(results_dir, 'verify_heuristic_results.csv')

    if all_results:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n[+] Đã xuất toàn bộ kết quả kiểm chứng ra: {csv_file}")


if __name__ == '__main__':
    run_all_verifications()