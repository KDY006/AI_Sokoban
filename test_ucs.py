"""
Script kiểm thử giải thuật UCS.
Chạy từ thư mục gốc source: python test_ucs.py
"""

import os
from core.state import parse_map
from core.problem import SokobanProblem
from core.ucs import ucs_search

def run_test(map_path: str, label: str):
    print(f"\n==========================================")
    print(f"BẮT ĐẦU CHẠY UCS TRÊN: {label}")
    print(f"File: {map_path}")
    print(f"==========================================")
    
    if not os.path.exists(map_path):
        print(f"Lỗi: Không tìm thấy file {map_path}")
        return

    init_state, walls, goals, rows, cols = parse_map(map_path)
    print(f"- Kích thước map: {rows} hàng x {cols} cột")
    print(f"- Vị trí Agent: {init_state.player_pos}")
    print(f"- Số lượng hộp: {len(init_state.boxes_pos)}")
    print(f"- Số lượng đích: {len(goals)}")

    problem = SokobanProblem(init_state, walls, goals)
    actions, cost, stats = ucs_search(problem)

    if actions is not None:
        print("\n--> TÌM THẤY LỜI GIẢI TỐI ƯU!")
        print(f"- Tổng chi phí (Cost): {cost}")
        print(f"- Số bước hành động: {len(actions)}")
        print(f"- Chuỗi hành động: {actions}")
        print(f"- Số node đã mở rộng: {stats['expanded_nodes']:,} nodes")
        print(f"- Frontier cực đại: {stats['max_frontier_size']:,} nodes")
        print(f"- Thời gian thực thi: {stats['time_ms']:.2f} ms")
    else:
        print("\n--> KHÔNG TÌM THẤY ĐƯỜNG ĐI!")
        print(f"- Số node đã duyệt: {stats['expanded_nodes']}")
        print(f"- Thời gian: {stats['time_ms']:.2f} ms")

if __name__ == "__main__":
    # 1. Tạo test map đơn giản (1 hộp, 1 đích, vài bước đẩy)
    mini_map = "maps/test_mini.txt"
    os.makedirs("maps", exist_ok=True)
    with open(mini_map, "w", encoding="utf-8") as f:
        f.write("%%%%%%\n%D B A%\n%%%%%%")

    run_test(mini_map, "Bản đồ Mini (1 Hộp)")
    
    # 2. Chạy trên bản đồ chính của đề bài
    example_map = "maps/example_map.txt"
    if os.path.exists(example_map):
        run_test(example_map, "Bản đồ Example Map của Đề bài")