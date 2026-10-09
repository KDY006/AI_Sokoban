"""
Module: experiments/benchmark.py
Phụ trách: Quý
Mô tả: Script thực nghiệm đối chiếu Time & Space Complexity giữa UCS và A* (R3).
       Đo đạc:
         - Thời gian chạy (Execution Time ms)
         - Số node mở rộng (Nodes Expanded)
         - Bộ nhớ đỉnh Frontier (Peak Frontier Memory / Space Complexity)
       Xuất bảng số liệu CSV và biểu đồ đối chiếu trực quan (PNG).
"""

import os
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

# Đảm bảo console Windows không bị lỗi bảng mã cp1252 khi UCS in log tiếng Việt
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Đảm bảo đường dẫn import từ thư mục gốc dự án
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
        # Tự động tìm các map hợp lệ có nội dung trong thư mục maps/
        candidate_files = []
        if os.path.exists(maps_dir):
            for fname in sorted(os.listdir(maps_dir)):
                if fname.endswith('.txt'):
                    fpath = os.path.join(maps_dir, fname)
                    if os.path.getsize(fpath) > 0:
                        candidate_files.append(fpath)
        map_files = candidate_files

    if not map_files:
        print("[-] Không tìm thấy file bản đồ hợp lệ nào trong thư mục maps/.")
        return

    results = []

    print("=" * 80)
    print("           BENCHMARK SO SÁNH HIỆU NĂNG: UCS vs A* (HUNGARIAN BFS)")
    print("=" * 80)

    for map_file in map_files:
        map_name = os.path.basename(map_file)
        print(f"\n[*] Đang chạy thực nghiệm trên: {map_name} ...")

        try:
            init_state, walls, goals, r, c = parse_map(map_file)
        except Exception as e:
            print(f"[-] Bỏ qua {map_name} do lỗi đọc file: {e}")
            continue

        # 1. Chạy Uniform Cost Search (UCS)
        prob_ucs = SokobanProblem(init_state, walls, goals)
        act_ucs, cost_ucs, stats_ucs = ucs_search(prob_ucs)

        # 2. Chạy A* Search
        prob_astar = SokobanProblem(init_state, walls, goals)
        act_astar, cost_astar, stats_astar = astar_search(prob_astar)

        # Tính toán tỷ lệ tối ưu / cải thiện
        node_ratio = round(stats_ucs['expanded_nodes'] / max(1, stats_astar['expanded_nodes']), 2)
        speedup = round(stats_ucs['time_ms'] / max(0.001, stats_astar['time_ms']), 2)

        row = {
            'Map': map_name,
            'Boxes': len(goals),
            'Cost_UCS': cost_ucs,
            'Cost_AStar': cost_astar,
            'Optimal_Match': (cost_ucs == cost_astar),
            'UCS_Nodes': stats_ucs['expanded_nodes'],
            'AStar_Nodes': stats_astar['expanded_nodes'],
            'Node_Reduction_Ratio': node_ratio,
            'UCS_Peak_Frontier': stats_ucs['max_frontier_size'],
            'AStar_Peak_Frontier': stats_astar['max_frontier_size'],
            'UCS_Time_ms': round(stats_ucs['time_ms'], 2),
            'AStar_Time_ms': round(stats_astar['time_ms'], 2),
            'Speedup': speedup
        }
        results.append(row)

        print(f"  + UCS   : Cost = {cost_ucs} | Nodes = {stats_ucs['expanded_nodes']:,} | Peak Frontier = {stats_ucs['max_frontier_size']:,} | Time = {stats_ucs['time_ms']:.2f} ms")
        print(f"  + A*    : Cost = {cost_astar} | Nodes = {stats_astar['expanded_nodes']:,} | Peak Frontier = {stats_astar['max_frontier_size']:,} | Time = {stats_astar['time_ms']:.2f} ms")
        print(f"  => A* giảm {node_ratio}x số node duyệt, nhanh hơn {speedup}x so với UCS.")

    if not results:
        print("[-] Không có kết quả thực nghiệm nào được ghi nhận.")
        return

    # 1. Xuất dữ liệu ra file CSV
    csv_file = os.path.join(results_dir, 'benchmark_results.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[+] Đã lưu bảng số liệu CSV: {csv_file}")

    # 2. Vẽ biểu đồ đối chiếu trực quan (PNG)
    maps = [r['Map'].replace('.txt', '') for r in results]
    ucs_nodes = [r['UCS_Nodes'] for r in results]
    astar_nodes = [r['AStar_Nodes'] for r in results]

    ucs_mem = [r['UCS_Peak_Frontier'] for r in results]
    astar_mem = [r['AStar_Peak_Frontier'] for r in results]

    ucs_times = [r['UCS_Time_ms'] for r in results]
    astar_times = [r['AStar_Time_ms'] for r in results]

    x = np.arange(len(maps))
    width = 0.35

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Đồ thị 1: Số lượng Node mở rộng (Nodes Expanded - Log scale)
    ax1 = axes[0]
    ax1.bar(x - width/2, ucs_nodes, width, label='UCS', color='#E74C3C', alpha=0.9)
    ax1.bar(x + width/2, astar_nodes, width, label='A* (Hungarian BFS)', color='#2980B9', alpha=0.9)
    ax1.set_title('Số Node mở rộng (Nodes Expanded - Log Scale)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(maps, rotation=15, ha='right')
    ax1.set_ylabel('Nodes (Log Scale)')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # Đồ thị 2: Bộ nhớ đỉnh Frontier (Space Complexity - Log scale)
    ax2 = axes[1]
    ax2.bar(x - width/2, ucs_mem, width, label='UCS', color='#E67E22', alpha=0.9)
    ax2.bar(x + width/2, astar_mem, width, label='A* (Hungarian BFS)', color='#27AE60', alpha=0.9)
    ax2.set_title('Bộ nhớ đỉnh Frontier (Peak Frontier Size - Log Scale)', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(maps, rotation=15, ha='right')
    ax2.set_ylabel('Max Frontier Size (Log Scale)')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    # Đồ thị 3: Thời gian thực thi (Time ms - Log scale)
    ax3 = axes[2]
    ax3.bar(x - width/2, ucs_times, width, label='UCS', color='#8E44AD', alpha=0.9)
    ax3.bar(x + width/2, astar_times, width, label='A* (Hungarian BFS)', color='#16A085', alpha=0.9)
    ax3.set_title('Thời gian chạy (Execution Time ms - Log Scale)', fontsize=11, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(maps, rotation=15, ha='right')
    ax3.set_ylabel('Thời gian (ms, Log Scale)')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    chart_path = os.path.join(results_dir, 'benchmark_chart.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[+] Đã xuất biểu đồ đối chiếu: {chart_path}")
    print("=" * 80)


if __name__ == '__main__':
    run_benchmark()