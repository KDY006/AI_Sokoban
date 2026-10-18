import random


class TwoAgentEnv:

    def __init__(self, map_file, max_steps):
        self.max_steps = max_steps
        self.current_step = 0
        self.grid = []
        self.goals = set()
        self.p1_pos = None
        self.p2_pos = None
        self.load_map(map_file)

    def load_map(self, map_file):
        with open(map_file, "r", encoding="utf-8") as f:
            for line in f:
                row_str = line.rstrip("\r\n")
                if row_str:
                    self.grid.append(list(row_str))

        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                ch = self.grid[r][c]
                if ch == "A":
                    self.p1_pos = (r, c)
                elif ch == "P":
                    self.p2_pos = (r, c)

                if ch in ["D", "C", "K"]:
                    self.goals.add((r, c))

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

    def is_wall(self, pos):
        r, c = pos
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            return self.grid[r][c] == "%"
        return True

    def is_box(self, pos):
        r, c = pos
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            ch = self.grid[r][c]
            return ch in ["B", "C", "K"]
        return False

    def check_conflict(self, p1_act, p2_act):
        next_p1 = self.get_next_position(self.p1_pos, p1_act)
        next_p2 = self.get_next_position(self.p2_pos, p2_act)

        if next_p1 == next_p2:
            return True
        
        if self.is_box(next_p1) and next_p1 == next_p2:
            return True

        if next_p1 == self.p2_pos and next_p2 == self.p1_pos:
            return True

        return False

    def apply_move(self, agent_id, act):
        cur_pos = self.p1_pos if agent_id == 1 else self.p2_pos
        other_agent_pos = self.p2_pos if agent_id == 1 else self.p1_pos
        target_pos = self.get_next_position(cur_pos, act)

        if self.is_wall(target_pos) or target_pos == other_agent_pos:
            return False

        if self.is_box(target_pos):
            box_next_pos = self.get_next_position(target_pos, act)

            if (
                self.is_wall(box_next_pos)
                or self.is_box(box_next_pos)
                or box_next_pos == other_agent_pos
            ):
                return False

            br, bc = box_next_pos
            if box_next_pos in self.goals:
                self.grid[br][bc] = "C" if agent_id == 1 else "K"
            else:
                self.grid[br][bc] = "B"

        cr, cc = cur_pos
        tr, tc = target_pos

        self.grid[cr][cc] = "D" if cur_pos in self.goals else " "

        if agent_id == 1:
            self.p1_pos = target_pos
            self.grid[tr][tc] = "A"
        else:
            self.p2_pos = target_pos
            self.grid[tr][tc] = "P"

        return True

    def step(self, act1, act2):
        self.current_step += 1

        if self.check_conflict(act1, act2):
            p = random.uniform(0.0, 1.0)
            if p < 0.5:
                self.apply_move(agent_id=1, act=act1)
            else:
                self.apply_move(agent_id=2, act=act2)
        else:
            self.apply_move(agent_id=1, act=act1)
            self.apply_move(agent_id=2, act=act2)

    def is_game_over(self):
        return self.current_step >= self.max_steps

    def get_scores(self):
        score_p1 = 0
        score_p2 = 0
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] == "C":
                    score_p1 += 1
                elif self.grid[r][c] == "K":
                    score_p2 += 1
        return score_p1, score_p2