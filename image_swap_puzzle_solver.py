import shutil
import tkinter as tk
# from tkinter import filedialog
from PIL import Image, ImageTk
import random
import os

TILE_SIZE = 200
GRID_SIZE = 4
IMG_DIR = "image_swap_tiles"
os.makedirs(IMG_DIR, exist_ok=True)


class ImageSwapPuzzleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Tile Swap Puzzle")
        self.tiles = []
        self.tile_imgs = {}
        self.board = []
        self.drag_data = {"tile": None, "row": None, "col": None}

        self.canvas = tk.Canvas(master, width=TILE_SIZE * GRID_SIZE, height=TILE_SIZE * GRID_SIZE)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        # self.load_btn = tk.Button(master, text="Load Image", command=self.load_image)
        # self.load_btn.pack(pady=10)
        self.load_image()

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
                self.tiles.append(count)
                count += 1

        random.shuffle(self.tiles)
        self.board = [self.tiles[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]
        self.draw_board()
        shutil.rmtree(IMG_DIR, ignore_errors=True)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = self.board[i][j]
                self.canvas.create_image(j * TILE_SIZE, i * TILE_SIZE, anchor='nw', image=self.tile_imgs[val],
                                         tags=f"tile_{i}_{j}")

    def start_drag(self, event):
        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
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
            old_row = self.drag_data["row"]
            old_col = self.drag_data["col"]
            new_col = event.x // TILE_SIZE
            new_row = event.y // TILE_SIZE
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                self.board[old_row][old_col], self.board[new_row][new_col] = self.board[new_row][new_col], \
                self.board[old_row][old_col]
            self.drag_data = {"tile": None, "row": None, "col": None}
            self.draw_board()


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageSwapPuzzleGUI(root)
    root.mainloop()

