"""
Module: experiments/benchmark.py
Mo ta: Thuc nghiem so sanh hieu nang (thoi gian, so node mo rong, bo nho frontier) giua UCS va A*.
"""

import os
import csv
import sys
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
from core.ucs import ucs_search
from search.astar import astar_search


def run_benchmark(map_files=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)

    if map_files is None:
        maps_dir = os.path.join(base_dir, 'maps')
        # Danh sach 5 map thuc nghiem theo yeu cau: deadlock va 1, 2, 3, 4 thung
        benchmark_target_maps = [
            'map_deadlock.txt',
            'map_01_one_box.txt',
            'map_02_two_boxes.txt',
            'map_03_three_boxes.txt',
            'map_04_four_boxes.txt'
        ]
        candidate_files = []
        for mname in benchmark_target_maps:
            fpath = os.path.join(maps_dir, mname)
            if os.path.exists(fpath):
                candidate_files.append(fpath)

        map_files = candidate_files if candidate_files else [
            os.path.join(maps_dir, f) for f in os.listdir(maps_dir)
            if f.endswith('.txt') and not f.startswith('competitive_map')
        ]

    benchmark_data = []

    print("=" * 80)
    print("       BENCHMARK SO SANH HIEU NANG: UCS VS A* (HUNGARIAN BFS + DEADLOCK)")
    print("=" * 80)

    for fpath in map_files:
        mname = os.path.basename(fpath)
        print(f"\n[*] Dang chay thuc nghiem tren: {mname} ...")

        try:
            init_state, walls, goals, r, c = parse_map(fpath)
        except Exception as e:
            print(f"[-] Bo qua {mname} do loi: {e}")
            continue

        if len(init_state.boxes_pos) < len(goals):
            continue

        problem_ucs = SokobanProblem(init_state, walls, goals)
        problem_astar = SokobanProblem(init_state, walls, goals)

        # Chay thuat toan UCS
        ucs_actions, ucs_cost, ucs_stats = ucs_search(problem_ucs)

        # Chay thuat toan A*
        astar_actions, astar_cost, astar_stats = astar_search(problem_astar)

        row = {
            "Map": mname,
            "Goals": len(goals),
            "UCS_Cost": ucs_cost if ucs_actions is not None else "Khong loi giai",
            "AStar_Cost": astar_cost if astar_actions is not None else "Khong loi giai",
            "UCS_Nodes": ucs_stats["expanded_nodes"],
            "AStar_Nodes": astar_stats["expanded_nodes"],
            "UCS_Frontier": ucs_stats["max_frontier_size"],
            "AStar_Frontier": astar_stats["max_frontier_size"],
            "UCS_Time_ms": round(ucs_stats["time_ms"], 2),
            "AStar_Time_ms": round(astar_stats["time_ms"], 2)
        }
        benchmark_data.append(row)

        print(f"  + UCS   : Cost = {row['UCS_Cost']} | Nodes = {row['UCS_Nodes']:,} | Peak Frontier = {row['UCS_Frontier']:,} | Time = {row['UCS_Time_ms']:.2f} ms")
        print(f"  + A*    : Cost = {row['AStar_Cost']} | Nodes = {row['AStar_Nodes']:,} | Peak Frontier = {row['AStar_Frontier']:,} | Time = {row['AStar_Time_ms']:.2f} ms")

        if astar_stats["expanded_nodes"] > 0:
            reduction = ucs_stats["expanded_nodes"] / astar_stats["expanded_nodes"]
            speedup = ucs_stats["time_ms"] / max(astar_stats["time_ms"], 0.001)
            print(f"  => A* giam {reduction:.1f}x so node duyet, nhanh hon {speedup:.2f}x so voi UCS.")
        elif row["AStar_Cost"] == "Khong loi giai":
            print("  => A* phat hien Deadlock ngay lap tuc (h = inf) -> Mo rong 0 node, dung tuc thi!")

    # Luu ket qua ra tep CSV
    csv_file = os.path.join(results_dir, "benchmark_results.csv")
    fieldnames = [
        "Map", "Goals", "UCS_Cost", "AStar_Cost",
        "UCS_Nodes", "AStar_Nodes", "UCS_Frontier", "AStar_Frontier",
        "UCS_Time_ms", "AStar_Time_ms"
    ]
    with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(benchmark_data)
    print(f"\n[+] Da luu bang so lieu CSV: {csv_file}")

    # Ve bieu do so sanh
    plot_benchmark_charts(benchmark_data, results_dir)


def plot_benchmark_charts(data, results_dir):
    if not data:
        return

    # Nhan truc hoanh
    name_map = {
        'map_deadlock.txt': 'Deadlock (Góc chết)',
        'map_01_one_box.txt': 'Map 01 (1 Thùng)',
        'map_02_two_boxes.txt': 'Map 02 (2 Thùng)',
        'map_03_three_boxes.txt': 'Map 03 (3 Thùng)',
        'map_04_four_boxes.txt': 'Map 04 (4 Thùng)'
    }

    labels = [name_map.get(d["Map"], d["Map"]) for d in data]
    x = np.arange(len(labels))
    width = 0.35

    # Gia tri duyet toi thieu la 1 de hien thi tren thang do log
    ucs_nodes = [max(d["UCS_Nodes"], 1) for d in data]
    astar_nodes = [max(d["AStar_Nodes"], 1) for d in data]

    ucs_mem = [max(d["UCS_Frontier"], 1) for d in data]
    astar_mem = [max(d["AStar_Frontier"], 1) for d in data]

    ucs_time = [d["UCS_Time_ms"] for d in data]
    astar_time = [d["AStar_Time_ms"] for d in data]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    fig.suptitle('SO SÁNH HIỆU NĂNG: UCS VS A* (HUNGARIAN BFS + DEADLOCK PRUNING)', fontsize=15, fontweight='bold', y=0.98)

    # Bieu do 1: So Node da mo rong (Log-Scale)
    axes[0].bar(x - width/2, ucs_nodes, width, label='UCS (Mù vô hướng)', color='#e74c3c', edgecolor='black', alpha=0.9)
    axes[0].bar(x + width/2, astar_nodes, width, label='A* (Hungarian BFS)', color='#2ecc71', edgecolor='black', alpha=0.9)
    axes[0].set_yscale('log')
    axes[0].set_title('Số Node đã mở rộng (Thang đo Log)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Số lượng Node (Log scale)', fontsize=10)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    axes[0].legend(frameon=True, facecolor='white', framealpha=0.9)
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Bieu do 2: Bo nho Frontier dinh (Log-Scale)
    axes[1].bar(x - width/2, ucs_mem, width, label='UCS (Mù vô hướng)', color='#e67e22', edgecolor='black', alpha=0.9)
    axes[1].bar(x + width/2, astar_mem, width, label='A* (Hungarian BFS)', color='#3498db', edgecolor='black', alpha=0.9)
    axes[1].set_yscale('log')
    axes[1].set_title('Bộ nhớ Frontier đỉnh (Thang đo Log)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Số trạng thái lưu trong RAM (Log scale)', fontsize=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    axes[1].legend(frameon=True, facecolor='white', framealpha=0.9)
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # Bieu do 3: Thoi gian thuc thi (mili-giay)
    axes[2].bar(x - width/2, ucs_time, width, label='UCS (Mù vô hướng)', color='#9b59b6', edgecolor='black', alpha=0.9)
    axes[2].bar(x + width/2, astar_time, width, label='A* (Hungarian BFS)', color='#1abc9c', edgecolor='black', alpha=0.9)
    axes[2].set_title('Thời gian tính toán (mili-giây)', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Thời gian (ms)', fontsize=10)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    axes[2].legend(frameon=True, facecolor='white', framealpha=0.9)
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    chart_file = os.path.join(results_dir, 'benchmark_chart.png')
    plt.savefig(chart_file, dpi=300)
    plt.close()
    print(f"[+] Da xuat bieu do doi chieu: {chart_file}")
    print("=" * 80)


if __name__ == '__main__':
    run_benchmark()
