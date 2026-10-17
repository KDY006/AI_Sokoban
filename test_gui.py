"""
Script kiem thu doc lap cho SokobanView:
- Test Case 1: Che do Don voi thuat toan A*, ky hieu ban do %, A, B, D, C, +
- Test Case 2: Che do Doi khang voi P1, P2, thung C va K, bang diem va phan dinh thang/thua
"""

import copy
from gui.game_view import SokobanView


def test_single_agent():
    print("\n--- DANG CHAY TEST: CHE DO DON (A*) ---")
    print("- Bam Space de Pause/Resume")
    print("- Bam [->] hoac [<-] de di chuyen tung buoc")
    print("- Dong cua so hoac bam ESC de chuyen sang test CHE DO DOI KHANG\n")

    # Gia lap map va chuoi trang thai (A day thung B vao D tro thanh C)
    s0 = [
        ["%", "%", "%", "%", "%", "%", "%"],
        ["%", "A", "B", " ", "D", " ", "%"],
        ["%", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%"],
    ]

    s1 = [
        ["%", "%", "%", "%", "%", "%", "%"],
        ["%", " ", "A", "B", "D", " ", "%"],
        ["%", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%"],
    ]

    s2 = [
        ["%", "%", "%", "%", "%", "%", "%"],
        ["%", " ", " ", "A", "C", " ", "%"],  # Thung da vao dich (C)
        ["%", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%"],
    ]

    s3 = [
        ["%", "%", "%", "%", "%", "%", "%"],
        ["%", " ", " ", " ", "+", " ", "%"],  # Nguoi choi dung tren dich (+)
        ["%", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%"],
    ]

    view = SokobanView(title="Test GUI - Single Agent (R5)")
    view.set_states([s0, s1, s2, s3], algorithm="A*")
    view.run_interactive()


def test_competitive_two_agent():
    print("\n--- DANG CHAY TEST: CHE DO DOI KHANG ---")
    print("- Player 1 day vao dich thanh thung C")
    print("- Player 2 day vao dich thanh thung K")
    print("- Hien thi bang diem thoi gian thuc va thong bao thang cuoc\n")

    # Gia lap ban co 2 nguoi choi voi dich rieng cho moi ben
    s0 = [
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
        ["%", "A", "B", "D", " ", "D", "B", "P", "%"],
        ["%", " ", " ", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
    ]

    # Buoc 1: Ca 2 cung tien len day thung
    s1 = [
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
        ["%", " ", "A", "C", " ", "K", "P", " ", "%"],  # P1 ghi 1 diem, P2 ghi 1 diem
        ["%", " ", " ", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
    ]

    # Buoc 2: P1 tiep tuc vuon len
    s2 = [
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
        ["%", " ", " ", "C", "A", "K", " ", "P", "%"],
        ["%", " ", " ", " ", " ", " ", " ", " ", "%"],
        ["%", "%", "%", "%", "%", "%", "%", "%", "%"],
    ]

    states = [s0, s1, s2]
    scores = [(0, 0), (1, 1), (1, 1)]
    max_steps = 2

    view = SokobanView(title="Test GUI - Competitive Two Agents")
    view.set_competitive_history(states, scores, max_steps=max_steps)
    view.run_interactive()


if __name__ == "__main__":
    test_single_agent()
    test_competitive_two_agent()