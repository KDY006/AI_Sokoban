from collections import deque
import threading


class agent_player2:

    def __init__(self):
        self.name = "Player 2"
        self.time_limit = 0.85

    def get_next_position(self, pos, act):
        if pos is None:
            return None
        r, c = pos
        if act == "North":
            return (r - 1, c)
        if act == "South":
            return (r + 1, c)
        if act == "West":
            return (r, c - 1)
        if act == "East":
            return (r, c + 1)
        return (r, c)

    def get_push_direction(self, agent_pos, box_pos):
        ar, ac = agent_pos
        br, bc = box_pos
        if ar == br + 1 and ac == bc:
            return "North"
        if ar == br - 1 and ac == bc:
            return "South"
        if ar == br and ac == bc + 1:
            return "West"
        if ar == br and ac == bc - 1:
            return "East"
        return None

    def bfs_path(self, grid, start_pos, target_pos, obstacles):
        if start_pos == target_pos:
            return []

        queue = deque([(start_pos, [])])
        visited = set([start_pos])

        while queue:
            curr, path = queue.popleft()
            if curr == target_pos:
                return path

            for act in ["North", "South", "West", "East"]:
                nxt = self.get_next_position(curr, act)
                nr, nc = nxt
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if (
                        grid[nr][nc] != "%"
                        and nxt not in obstacles
                        and nxt not in visited
                    ):
                        visited.add(nxt)
                        queue.append((nxt, path + [act]))

        return None

    def search_best_act(self, grid, my_pos):
        boxes = []
        goals = []
        all_boxes = set()
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                ch = grid[r][c]
                if ch in ["B", "C"]:
                    boxes.append((r, c))
                if ch in ["B", "C", "K"]:
                    all_boxes.add((r, c))
                if ch == "D":
                    goals.append((r, c))

        if not boxes or not goals:
            return "Stay"

        best_plan = None
        min_cost = float("inf")

        for box in boxes:
            br, bc = box
            # Greedy bonus: Ưu tiên cướp thùng đối thủ (C)
            priority_bonus = -8 if grid[br][bc] == "C" else 0

            for goal in goals:
                gr, gc = goal

                for act in ["North", "South", "West", "East"]:
                    next_box_pos = self.get_next_position(box, act)
                    nbr, nbc = next_box_pos

                    # Ô sau khi đẩy hộp phải trống hoặc là đích (không được là tường hoặc hộp khác)
                    if not (0 <= nbr < len(grid) and 0 <= nbc < len(grid[0])):
                        continue
                    if grid[nbr][nbc] in ["%", "B", "C", "K"]:
                        continue

                    push_pos = None
                    if act == "North":
                        push_pos = (br + 1, bc)
                    elif act == "South":
                        push_pos = (br - 1, bc)
                    elif act == "West":
                        push_pos = (br, bc + 1)
                    elif act == "East":
                        push_pos = (br, bc - 1)

                    pr, pc = push_pos
                    if not (0 <= pr < len(grid) and 0 <= pc < len(grid[0])):
                        continue
                    if grid[pr][pc] in ["%", "B", "C", "K"]:
                        continue

                    # Đường đi của Agent tới ô đẩy phải tránh tất cả các hộp hiện tại
                    path_to_push = self.bfs_path(grid, my_pos, push_pos, all_boxes)
                    if path_to_push is not None:
                        # Greedy Best-First Search: Đặt trọng số cao vào khoảng cách hộp tới đích
                        h_cost = (abs(nbr - gr) + abs(nbc - gc)) * 3
                        cost = h_cost + len(path_to_push) + priority_bonus
                        if cost < min_cost:
                            min_cost = cost
                            best_plan = (path_to_push, act, push_pos, box)

        if best_plan is not None:
            path_to_push, push_act, push_pos, target_box = best_plan

            if my_pos != push_pos:
                if len(path_to_push) > 0:
                    return path_to_push[0]
            else:
                # Đang đứng tại ô đẩy -> Thực hiện đẩy hộp theo hướng chính xác
                push_dir = self.get_push_direction(my_pos, target_box)
                return push_dir if push_dir else push_act

        return "Stay"

    def get_act(self, grid, my_pos):
        result = ["Stay"]

        def worker():
            result[0] = self.search_best_act(grid, my_pos)

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=self.time_limit)

        return result[0]