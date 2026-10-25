"""
Module: competitive/two_agent_env.py
Mo ta: Moi truong mo phong thi dau doi khang 2 tac nhan.
Quan ly ban do, toa do agent, logic day hop, xung dot ngau nhien va tinh diem so.
"""

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
        # Doc ban do tu tap tin
        with open(map_file, "r", encoding="utf-8") as f:
            for line in f:
                row_str = line.rstrip("\r\n")
                if row_str:
                    self.grid.append(list(row_str))

        # Xac dinh vi tri ban dau cua 2 Agent va cac o dich
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
            return self.grid[r][c] in ["B", "C", "K"]
        return False

    def check_conflict(self, p1_act, p2_act):
        # Kiem tra va cham giua 2 Agent
        next_p1 = self.get_next_position(self.p1_pos, p1_act)
        next_p2 = self.get_next_position(self.p2_pos, p2_act)

        # Di chuyen vao cung 1 o
        if next_p1 == next_p2:
            return True

        # Doi cho cho nhau (head-on collision)
        if next_p1 == self.p2_pos and next_p2 == self.p1_pos:
            return True

        return False

    def apply_move(self, agent_id, act):
        # Ap dung buoc di cho tung Agent
        cur_pos = self.p1_pos if agent_id == 1 else self.p2_pos
        other_agent_pos = self.p2_pos if agent_id == 1 else self.p1_pos
        target_pos = self.get_next_position(cur_pos, act)

        # Chan boi tuong hoac Agent khac
        if self.is_wall(target_pos) or target_pos == other_agent_pos:
            return False

        # Xu ly day hop
        if self.is_box(target_pos):
            box_next_pos = self.get_next_position(target_pos, act)

            # Khong the day hop vao tuong, hop khac hoac Agent doi thu
            if (
                self.is_wall(box_next_pos)
                or self.is_box(box_next_pos)
                or box_next_pos == other_agent_pos
            ):
                return False

            br, bc = box_next_pos
            # Cap nhat ky hieu hop sau khi day
            if box_next_pos in self.goals:
                self.grid[br][bc] = "C" if agent_id == 1 else "K"
            else:
                self.grid[br][bc] = "B"

        cr, cc = cur_pos
        tr, tc = target_pos

        # Tra lai ky hieu o cu sau khi Agent roi di
        self.grid[cr][cc] = "D" if cur_pos in self.goals else " "

        # Cap nhat vi tri moi cua Agent
        if agent_id == 1:
            self.p1_pos = target_pos
            self.grid[tr][tc] = "A"
        else:
            self.p2_pos = target_pos
            self.grid[tr][tc] = "P"

        return True

    def step(self, act1, act2):
        self.current_step += 1

        # Xu ly xung dot ngau nhien bang phan phoi xac suat deu Uniform(0, 1)
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
        # Dem diem so dua tren so hop moi ben da dua vao dich
        score_p1 = sum(1 for r in range(len(self.grid)) for c in range(len(self.grid[r])) if self.grid[r][c] == "C")
        score_p2 = sum(1 for r in range(len(self.grid)) for c in range(len(self.grid[r])) if self.grid[r][c] == "K")
        return score_p1, score_p2
