"""
Module: experiments/benchmark.py
Mo ta: Thuc nghiem so sanh hieu nang (thoi gian, so node mo rong, bo nho frontier) giua UCS va A*.
"""

import os
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

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
        benchmark_target_maps = [
            'map_deadlock.txt',
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
    print("           BENCHMARK SO SANH HIEU NANG: UCS vs A* (HUNGARIAN BFS)")
    print("=" * 80)

    for fpath in map_files:
        mname = os.path.basename(fpath)
        print(f"\n[*] Dang chay thuc nghiem tren: {mname} ...")

        try:
            init_state, walls, goals, r, c = parse_map(fpath)
        except Exception as e:
            print(f"[-] Bo qua {mname} do loi: {e}")
            continue

        # Kiem tra ban do co du thung de giai khong
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
            "UCS_Cost": ucs_cost if ucs_actions is not None else "Unsolvable",
            "AStar_Cost": astar_cost if astar_actions is not None else "Unsolvable",
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

    # Luu ket qua ra tap tin CSV
    csv_file = os.path.join(results_dir, "benchmark_results.csv")
    fieldnames = [
        "Map", "Goals", "UCS_Cost", "AStar_Cost",
        "UCS_Nodes", "AStar_Nodes", "UCS_Frontier", "AStar_Frontier",
        "UCS_Time_ms", "AStar_Time_ms"
    ]
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(benchmark_data)
    print(f"\n[+] Da luu bang so lieu CSV: {csv_file}")

    # Ve bieu do so sanh
    plot_benchmark_charts(benchmark_data, results_dir)


def plot_benchmark_charts(data, results_dir):
    if not data:
        return

    # Loc cac map co loi giai de ve bieu do
    solvable_data = [d for d in data if d["AStar_Cost"] != "Unsolvable"]
    if not solvable_data:
        solvable_data = data

    maps = [d["Map"] for d in solvable_data]
    x = np.arange(len(maps))
    width = 0.35

    ucs_nodes = [max(d["UCS_Nodes"], 1) for d in solvable_data]
    astar_nodes = [max(d["AStar_Nodes"], 1) for d in solvable_data]

    ucs_mem = [max(d["UCS_Frontier"], 1) for d in solvable_data]
    astar_mem = [max(d["AStar_Frontier"], 1) for d in solvable_data]

    ucs_time = [d["UCS_Time_ms"] for d in solvable_data]
    astar_time = [d["AStar_Time_ms"] for d in solvable_data]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Bieu do 1: So node da mo rong (Log-Scale)
    axes[0].bar(x - width/2, ucs_nodes, width, label='UCS', color='#e74c3c')
    axes[0].bar(x + width/2, astar_nodes, width, label='A* (Hungarian BFS)', color='#2ecc71')
    axes[0].set_yscale('log')
    axes[0].set_title('So Node da mo rong (Log Scale)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(maps, rotation=15, ha='right')
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Bieu do 2: Bo nho Frontier dinh (Log-Scale)
    axes[1].bar(x - width/2, ucs_mem, width, label='UCS', color='#e67e22')
    axes[1].bar(x + width/2, astar_mem, width, label='A* (Hungarian BFS)', color='#3498db')
    axes[1].set_yscale('log')
    axes[1].set_title('Bo nho Frontier dinh (Log Scale)')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(maps, rotation=15, ha='right')
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # Bieu do 3: Thoi gian thuc thi (ms)
    axes[2].bar(x - width/2, ucs_time, width, label='UCS', color='#9b59b6')
    axes[2].bar(x + width/2, astar_time, width, label='A* (Hungarian BFS)', color='#1abc9c')
    axes[2].set_title('Thoi gian thuc thi (ms)')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(maps, rotation=15, ha='right')
    axes[2].legend()
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    chart_file = os.path.join(results_dir, 'benchmark_chart.png')
    plt.savefig(chart_file, dpi=300)
    plt.close()
    print(f"[+] Da xuat bieu do doi chieu: {chart_file}")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
