"""
Điểm khởi chạy chính cho chế độ Single-Agent (R5).
Cho phép chọn thuật toán: UCS hoặc A* để giải map.
"""
import sys
import os
from core.state import parse_map
from core.problem import SokobanProblem
from core.ucs import ucs_search
# Sau này Quý xong sẽ mở dòng này:
# from search.astar import astar_search

def main():
    map_file = "maps/example_map.txt"
    print(f"Đang tải bản đồ: {map_file}...")
    init_state, walls, goals, r, c = parse_map(map_file)
    problem = SokobanProblem(init_state, walls, goals)

    # Demo chạy với UCS:
    print("Đang giải bài toán bằng UCS...")
    actions, cost, stats = ucs_search(problem)
    
    if actions:
        print(f"Tìm thấy lời giải! Chi phí: {cost}, Số bước: {len(actions)}")
        # Sau này Đức xong GUI sẽ truyền actions vào giao diện Pygame tại đây
    else:
        print("Không tìm thấy đường đi!")

if __name__ == "__main__":
    main()