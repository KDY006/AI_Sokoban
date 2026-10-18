from collections import deque
import heapq
import threading


class agent_player1:

    def __init__(self):
        self.name = "Player 1"
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

    def bfs_path(self, grid, start_pos, target_pos, obstacles):
        """Tìm đường đi ngắn nhất cho Agent từ start_pos tới target_pos né tường & vật cản."""
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
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                if grid[r][c] in ["B", "K"]:
                    boxes.append((r, c))
                elif grid[r][c] == "D":
                    goals.append((r, c))

        if not boxes or not goals:
            return "Stay"

        best_plan = None
        min_total_cost = float("inf")

        for box in boxes:
            br, bc = box
            for goal in goals:
                gr, gc = goal

                for act in ["North", "South", "West", "East"]:
                    next_box_pos = self.get_next_position(box, act)

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
                    if grid[pr][pc] == "%":
                        continue

                    path_to_push = self.bfs_path(grid, my_pos, push_pos, {box})
                    if path_to_push is not None:
                        cost = len(path_to_push) + abs(br - gr) + abs(bc - gc)
                        if cost < min_total_cost:
                            min_total_cost = cost
                            best_plan = (path_to_push, act, push_pos, box)

        if best_plan is not None:
            path_to_push, push_act, push_pos, target_box = best_plan
            if my_pos != push_pos:
                if len(path_to_push) > 0:
                    return path_to_push[0]
            else:

                return push_act

        return "Stay"

    def get_act(self, grid, my_pos):
        result = ["Stay"]

        def worker():
            result[0] = self.search_best_act(grid, my_pos)

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=self.time_limit)

        return result[0]