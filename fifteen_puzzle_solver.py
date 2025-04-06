import shutil
import tkinter as tk
# from tkinter import filedialog
from PIL import Image, ImageTk
import random
import os
import heapq

TILE_SIZE = 200
GRID_SIZE = 4
IMG_DIR = "fifteen_tiles"
os.makedirs(IMG_DIR, exist_ok=True)


class FifteenPuzzleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("15 Puzzle Game")
        self.tiles = []
        self.tile_imgs = {}
        self.board = []
        self.empty_pos = (2, 2)
        self.drag_data = {"tile": None, "row": None, "col": None}

        self.canvas = tk.Canvas(master, width=TILE_SIZE * GRID_SIZE, height=TILE_SIZE * GRID_SIZE)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.load_image()

        # self.load_btn = tk.Button(master, text="Load Image", command=self.load_image)
        # self.load_btn.pack(pady=10)

        # self.solve_btn = tk.Button(master, text="Solve Puzzle", command=self.solve_puzzle)
        # self.solve_btn.pack(pady=5)

    def load_image(self):
        filepath = 'puzzle_picture.jpg'
        # filepath = filedialog.askopenfilename()
        # if not filepath:
        #     return
        img = Image.open(filepath).resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))

        self.tiles.clear()
        self.tile_imgs.clear()
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

        count = 1
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                left = j * TILE_SIZE
                upper = i * TILE_SIZE
                tile = img.crop((left, upper, left + TILE_SIZE, upper + TILE_SIZE))

                path = f"{IMG_DIR}/tile_{count}.png"
                tile.save(path)
                self.tile_imgs[count] = ImageTk.PhotoImage(tile)
                if (i, j) == self.empty_pos:
                    self.tiles.append(0)
                else:
                    self.tiles.append(count)
                count += 1

        self.shuffle_board()
        self.draw_board()
        shutil.rmtree(IMG_DIR, ignore_errors=True)

    def shuffle_board(self):
        while True:
            random.shuffle(self.tiles)
            self.board = [self.tiles[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if self.board[i][j] == 0:
                        self.empty_pos = (i, j)
            if self.is_solvable():
                break

    def is_solvable(self):
        flat = sum(self.board, [])
        inv = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] and flat[j] and flat[i] > flat[j]:
                    inv += 1
        row = self.empty_pos[0]
        return (inv + row) % 2 == 0

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = self.board[i][j]
                if val != 0:
                    self.canvas.create_image(j * TILE_SIZE, i * TILE_SIZE, anchor='nw', image=self.tile_imgs[val],
                                             tags=f"tile_{i}_{j}")

    def start_drag(self, event):
        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.can_move(row, col):
            tile_id = self.canvas.find_withtag(f"tile_{row}_{col}")
            if tile_id:
                self.drag_data["tile"] = tile_id[0]
                self.drag_data["row"] = row
                self.drag_data["col"] = col
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y

    def do_drag(self, event):
        if self.drag_data["tile"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["tile"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def end_drag(self, event):
        if self.drag_data["tile"]:
            row = self.drag_data["row"]
            col = self.drag_data["col"]
            if self.can_move(row, col):
                self.move_tile(row, col)
                self.draw_board()
                if self.check_win():
                    self.canvas.create_text(TILE_SIZE * 2, TILE_SIZE * 2, text="You Win!", font=("Arial", 32),
                                            fill="green")
            self.drag_data = {"tile": None, "row": None, "col": None}

    def can_move(self, row, col):
        er, ec = self.empty_pos
        return abs(er - row) + abs(ec - col) == 1

    def move_tile(self, row, col):
        er, ec = self.empty_pos
        self.board[er][ec], self.board[row][col] = self.board[row][col], self.board[er][ec]
        self.empty_pos = (row, col)

    def check_win(self):
        correct = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
        current = sum(self.board, [])
        return current == correct

    def solve_puzzle(self):
        def board_to_tuple(board):
            return tuple(tuple(row) for row in board)

        def find_zero(state):
            for i in range(4):
                for j in range(4):
                    if state[i][j] == 0:
                        return i, j

        def manhattan(state):
            dist = 0
            for i in range(4):
                for j in range(4):
                    val = state[i][j]
                    if val != 0:
                        goal_i, goal_j = (val - 1) // 4, (val - 1) % 4
                        dist += abs(i - goal_i) + abs(j - goal_j)
            return dist

        def get_neighbors(state):
            neighbors = []
            x, y = find_zero(state)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 4 and 0 <= ny < 4:
                    new_state = [list(row) for row in state]
                    new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                    neighbors.append(((x, y), (nx, ny), tuple(tuple(row) for row in new_state)))
            return neighbors

        def a_star(start):
            goal = tuple([tuple([i * 4 + j + 1 for j in range(4)]) for i in range(4)])
            goal = list(map(list, goal))
            goal[3][3] = 0
            goal = tuple(tuple(row) for row in goal)

            frontier = [(manhattan(start), 0, start, [])]
            visited = set()
            while frontier:
                est, cost, state, path = heapq.heappop(frontier)
                if state in visited:
                    continue
                visited.add(state)
                if state == goal:
                    return path
                for (from_pos, to_pos, neighbor) in get_neighbors(state):
                    if neighbor not in visited:
                        heapq.heappush(frontier, (
                            cost + 1 + manhattan(neighbor), cost + 1, neighbor, path + [(from_pos, to_pos)]))
            return []

        moves = a_star(board_to_tuple(self.board))
        self.animate_solution(moves)

    def animate_solution(self, moves):
        if not moves:
            return

        def update_frame(i=0):
            if i >= len(moves):
                return
            from_pos, to_pos = moves[i]
            fx, fy = from_pos
            tx, ty = to_pos
            self.board[fx][fy], self.board[tx][ty] = self.board[tx][ty], self.board[fx][fy]
            self.empty_pos = (fx, fy)
            self.draw_board()
            self.master.after(300, update_frame, i + 1)

        update_frame()


if __name__ == '__main__':
    root = tk.Tk()
    app = FifteenPuzzleGUI(root)
    root.mainloop()
