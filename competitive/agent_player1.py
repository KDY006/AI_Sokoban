from collections import deque
import heapq
import threading


class agent_player1:

    def __init__(self):
        self.name = "Player 1"
        self.time_limit = 0.75  

    def bfs_distance(self, grid, start_pos, target_pos):
        if start_pos is None or target_pos is None:
            return float("inf")

        queue = deque([(start_pos, 0)])
        visited = set([start_pos])

        while queue:
            curr_pos, dist = queue.popleft()

            if curr_pos == target_pos:
                return dist

            r, c = curr_pos
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                    if grid[nr][nc] != "%" and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append(((nr, nc), dist + 1))

        return float("inf")

    def heuristic(self, grid, my_pos, box_pos, goal_pos):
        dist_agent_to_box = self.bfs_distance(grid, my_pos, box_pos)
        dist_box_to_goal = self.bfs_distance(grid, box_pos, goal_pos)
        return dist_agent_to_box + dist_box_to_goal

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

        best_box = min(
            boxes, key=lambda b: self.bfs_distance(grid, my_pos, b)
        )

        pq = []
        h_start = self.bfs_distance(grid, my_pos, best_box)
        heapq.heappush(pq, (h_start, [], my_pos))

        visited = set()

        while len(pq) > 0:
            h_val, acts, curr_pos = heapq.heappop(pq)

            if curr_pos in visited:
                continue
            visited.add(curr_pos)

            cr, cc = curr_pos
            br, bc = best_box
            if abs(cr - br) + abs(cc - bc) == 1:
                if len(acts) > 0:
                    return acts[0]
                return "Stay"

            for act in ["North", "South", "West", "East"]:
                next_pos = self.get_next_position(curr_pos, act)
                if next_pos is not None:
                    nr, nc = next_pos
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                        if grid[nr][nc] != "%" and next_pos not in visited:
                            h_next = self.bfs_distance(grid, next_pos, best_box)
                            heapq.heappush(pq, (h_next, acts + [act], next_pos))

        return "Stay"

    def get_act(self, grid, my_pos):
        result = ["Stay"]

        def worker():
            result[0] = self.search_best_act(grid, my_pos)

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=self.time_limit)

        return result[0]