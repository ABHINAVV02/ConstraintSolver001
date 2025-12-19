import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout, QLineEdit, QMessageBox, QDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Profiler
nodes = 0
backtracks = 0

def reset_profiler():
    global nodes, backtracks
    nodes = backtracks = 0

# n queens
def solve_nqueens_all(N):
    global nodes, backtracks
    board = [-1] * N
    solutions = []

    def is_safe(r, c):
        for i in range(r):
            if board[i] == c or abs(board[i] - c) == abs(i - r):
                return False
        return True

    def backtrack(row):
        global nodes, backtracks
        nodes += 1
        if row == N:
            solutions.append(board.copy())
            return
        for col in range(N):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1
                backtracks += 1

    backtrack(0)
    return solutions

# sudoku
def solve_sudoku(grid):
    global nodes, backtracks

    def is_safe(r, c, num):
        for x in range(9):
            if grid[r][x] == num or grid[x][c] == num:
                return False

        sr, sc = r - r % 3, c - c % 3
        for i in range(3):
            for j in range(3):
                if grid[sr + i][sc + j] == num:
                    return False
        return True

    def solve():
        global nodes, backtracks
        nodes += 1
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    for num in range(1, 10):
                        if is_safe(r, c, num):
                            grid[r][c] = num
                            if solve():
                                return True
                            grid[r][c] = 0
                            backtracks += 1
                    return False
        return True

    solve()
    return grid

# n queen dialog
class NQueenDialog(QDialog):
    def __init__(self, solutions):
        super().__init__()
        self.solutions = solutions
        self.index = 0
        self.N = len(solutions[0])

        self.setWindowTitle("N-Queens Solutions")
        self.setFixedSize(self.N * 50, self.N * 50 + 60)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(0)
        self.main_layout.addLayout(self.board_layout)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀ Prev")
        self.next_btn = QPushButton("Next ▶")
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        self.main_layout.addLayout(btn_layout)

        self.counter = QLabel()
        self.counter.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.counter)

        self.prev_btn.clicked.connect(self.prev_solution)
        self.next_btn.clicked.connect(self.next_solution)

        self.draw_board()

    def draw_board(self):
        for i in reversed(range(self.board_layout.count())):
            self.board_layout.itemAt(i).widget().setParent(None)

        board = self.solutions[self.index]

        for i in range(self.N):
            for j in range(self.N):
                cell = QLabel()
                cell.setFixedSize(45, 45)
                cell.setAlignment(Qt.AlignCenter)

                if (i + j) % 2 == 0:
                    cell.setStyleSheet("background-color:#EEE;")
                else:
                    cell.setStyleSheet("background-color:#444;color:white;")

                if board[i] == j:
                    cell.setText("♛")
                    cell.setFont(QFont("Arial", 22, QFont.Bold))

                self.board_layout.addWidget(cell, i, j)

        self.counter.setText(
            f"Solution {self.index + 1} / {len(self.solutions)}"
        )

    def next_solution(self):
        if self.index < len(self.solutions) - 1:
            self.index += 1
            self.draw_board()

    def prev_solution(self):
        if self.index > 0:
            self.index -= 1
            self.draw_board()

# sudoku dialog
class SudokuDialog(QDialog):
    def __init__(self, grid):
        super().__init__()
        self.setWindowTitle("Sudoku Solution")
        self.setFixedSize(420, 420)

        layout = QGridLayout()
        self.setLayout(layout)

        for i in range(9):
            for j in range(9):
                cell = QLabel(str(grid[i][j]))
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont("Arial", 14, QFont.Bold))
                cell.setFixedSize(45, 45)

                if (i // 3 + j // 3) % 2 == 0:
                    cell.setStyleSheet("background-color:#F2F2F2; border:1px solid black;")
                else:
                    cell.setStyleSheet("background-color:#D6D6D6; border:1px solid black;")

                layout.addWidget(cell, i, j)

# Gui
class SolverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Constraint Solver Platform")
        self.setGeometry(200, 100, 400, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Constraint Solver (Backtracking)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)

        # N Queens
        layout.addWidget(QLabel("N-Queens (Enter N):"))
        self.n_input = QLineEdit()
        layout.addWidget(self.n_input)

        nq_btn = QPushButton("Solve N-Queens (All Solutions)")
        nq_btn.clicked.connect(self.run_nqueens)
        layout.addWidget(nq_btn)

        # Sudoku
        layout.addWidget(QLabel("Sudoku Input (0 for empty):"))

        self.sudoku_cells = [[QLineEdit() for _ in range(9)] for _ in range(9)]
        sudoku_layout = QGridLayout()

        for i in range(9):
            for j in range(9):
                cell = self.sudoku_cells[i][j]
                cell.setFixedSize(30, 30)
                cell.setAlignment(Qt.AlignCenter)
                sudoku_layout.addWidget(cell, i, j)

        layout.addLayout(sudoku_layout)

        s_btn = QPushButton("Solve Sudoku")
        s_btn.clicked.connect(self.run_sudoku)
        layout.addWidget(s_btn)

        self.stats = QLabel("")
        layout.addWidget(self.stats)

    def run_nqueens(self):
        reset_profiler()
        N = int(self.n_input.text())
        if N <= 0 or N > 10:
            QMessageBox.warning(self, "Error", "Enter N between 1 and 10")
            return

        solutions = solve_nqueens_all(N)

        if not solutions:
            QMessageBox.information(self, "N-Queens", "No solution exists")
            return

        dialog = NQueenDialog(solutions)
        dialog.exec_()

        self.stats.setText(
            f"Solutions: {len(solutions)} | Nodes: {nodes} | Backtracks: {backtracks}"
        )

    def run_sudoku(self):
        reset_profiler()
        grid = []
        for i in range(9):
            row = []
            for j in range(9):
                text = self.sudoku_cells[i][j].text()
                row.append(int(text) if text else 0)
            grid.append(row)

        solved = solve_sudoku(grid)
        dialog = SudokuDialog(solved)
        dialog.exec_()

        self.stats.setText(f"Nodes: {nodes} | Backtracks: {backtracks}")

# excution part
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolverGUI()
    window.show()
    sys.exit(app.exec_())
