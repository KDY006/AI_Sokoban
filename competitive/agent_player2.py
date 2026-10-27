"""
Module: competitive/agent_player2.py
Mo ta: Tac nhan Player 2 trong che do doi khang.
Su dung thuat toan Greedy Best-First Search day thung toi dich va kich hoat che do pha binh khi bi dan diem.
"""

from collections import deque
import threading


class agent_player2:
    def __init__(self):
        self.name = "Player 2"
        self.time_limit = 0.85
        self.static_goals = None

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
        # Tim duong di ngan nhat bang BFS
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

    def search_sabotage_act(self, grid, my_pos, opp_box_char="C", opp_char="A"):
        # Tim ke hoach day hop cua doi thu ra khoi o dich
        opp_boxes = []
        all_obstacles = set()
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                ch = grid[r][c]
                if ch == opp_box_char:
                    opp_boxes.append((r, c))
                if ch in ["B", "C", "K", opp_char]:
                    all_obstacles.add((r, c))

        if not opp_boxes:
            return None

        best_sabotage_plan = None
        min_cost = float("inf")

        for box in opp_boxes:
            br, bc = box
            for act in ["North", "South", "West", "East"]:
                nbr, nbc = self.get_next_position(box, act)

                if not (0 <= nbr < len(grid) and 0 <= nbc < len(grid[0])):
                    continue
                if grid[nbr][nbc] in ["%", "B", "C", "K", opp_char]:
                    continue

                push_pos = (br + 1, bc) if act == "North" else ((br - 1, bc) if act == "South" else ((br, bc + 1) if act == "West" else (br, bc - 1)))
                pr, pc = push_pos
                if not (0 <= pr < len(grid) and 0 <= pc < len(grid[0])):
                    continue
                if grid[pr][pc] in ["%", "B", "C", "K", opp_char]:
                    continue

                path_to_push = self.bfs_path(grid, my_pos, push_pos, all_obstacles)
                if path_to_push is not None:
                    bonus = 0 if (nbr, nbc) not in self.static_goals else 5
                    cost = len(path_to_push) + bonus
                    if cost < min_cost:
                        min_cost = cost
                        best_sabotage_plan = (path_to_push, act, push_pos, box)

        return best_sabotage_plan

    def search_best_act(self, grid, my_pos):
        # Khoi tao tap o dich co dinh
        if self.static_goals is None:
            self.static_goals = set()
            for r in range(len(grid)):
                for c in range(len(grid[r])):
                    if grid[r][c] in ["D", "C", "K"]:
                        self.static_goals.add((r, c))

        # Tinh diem va thu thap hop
        my_score = 0
        opp_score = 0
        boxes = []
        free_boxes = []
        all_obstacles = set()
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                ch = grid[r][c]
                if ch == "K":
                    my_score += 1
                elif ch == "C":
                    opp_score += 1

                if ch == "B":
                    free_boxes.append((r, c))
                if ch in ["B", "C"]:
                    boxes.append((r, c))
                if ch in ["B", "C", "K", "A"]:
                    all_obstacles.add((r, c))

        free_goals = [
            g for g in self.static_goals
            if grid[g[0]][g[1]] not in ["B", "C", "K"]
        ]

        best_plan = None
        min_cost = float("inf")

        # 1. Tim ke hoach day hop vao dich (Greedy Best-First)
        if boxes and free_goals:
            for box in boxes:
                br, bc = box
                priority_bonus = -8 if grid[br][bc] == "C" else 0

                for goal in free_goals:
                    gr, gc = goal
                    if goal == box:
                        continue

                    for act in ["North", "South", "West", "East"]:
                        next_box_pos = self.get_next_position(box, act)
                        nbr, nbc = next_box_pos

                        if not (0 <= nbr < len(grid) and 0 <= nbc < len(grid[0])):
                            continue
                        if grid[nbr][nbc] in ["%", "B", "C", "K", "A"]:
                            continue

                        push_pos = (br + 1, bc) if act == "North" else ((br - 1, bc) if act == "South" else ((br, bc + 1) if act == "West" else (br, bc - 1)))
                        pr, pc = push_pos
                        if not (0 <= pr < len(grid) and 0 <= pc < len(grid[0])):
                            continue
                        if grid[pr][pc] in ["%", "B", "C", "K"]:
                            continue

                        path_to_push = self.bfs_path(grid, my_pos, push_pos, all_obstacles)
                        if path_to_push is not None:
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
                push_dir = self.get_push_direction(my_pos, target_box)
                return push_dir if push_dir else push_act

        # 2. Chi khi het thung tu do va bi dan diem hoac bang diem moi kich hoat pha binh
        if len(free_boxes) == 0 and my_score <= opp_score:
            sabotage_plan = self.search_sabotage_act(grid, my_pos, opp_box_char="C", opp_char="A")
            if sabotage_plan is not None:
                path_to_push, push_act, push_pos, target_box = sabotage_plan
                if my_pos != push_pos:
                    if len(path_to_push) > 0:
                        return path_to_push[0]
                else:
                    push_dir = self.get_push_direction(my_pos, target_box)
                    return push_dir if push_dir else push_act

        return "Stay"

    def get_act(self, grid, my_pos):
        # Gioi han thoi gian xu ly bang threading
        result = ["Stay"]

        def worker():
            result[0] = self.search_best_act(grid, my_pos)

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=self.time_limit)

        return result[0]
