import tkinter as tk
import random

# Set up game dimensions
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = CANVAS_WIDTH // BLOCK_SIZE
BOARD_HEIGHT = CANVAS_HEIGHT // BLOCK_SIZE
FALL_SPEED = 1  # Move piece by 1 pixel at a time for smoothness
FAST_DROP_SPEED = 100  # Speed when the Down key is pressed



# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1], [1, 1]],  # O shape
    [[0, 1, 0], [1, 1, 1]],  # T shape
    [[1, 1, 0], [0, 1, 1]],  # S shape
    [[0, 1, 1], [1, 1, 0]],  # Z shape
    [[1, 1, 1], [1, 0, 0]],  # L shape
    [[1, 1, 1], [0, 0, 1]],  # J shape
]

# Colors for each shape
SHAPE_COLORS = ['cyan', 'yellow', 'purple', 'green', 'red', 'orange', 'blue']

# Piece class
class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = BOARD_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0
        self.pixel_y = 0  # This keeps track of the y position in pixels for smooth movement

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))  # Rotate the shape 90 degrees

# Tetris game class
class Tetris:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        # Initialize board and piece
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()

        # Initialize score and game state
        self.score = 0
        self.running = True
        self.drop_speed = FALL_SPEED  # Normal fall speed

        # Add score label
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Helvetica", 12))
        self.score_label.pack()

        self.root.bind("<Key>", self.handle_key)
        self.update()

    def new_piece(self):
        """Generate a new random piece"""
        shape = random.choice(SHAPES)
        color = random.choice(SHAPE_COLORS)
        return Piece(shape, color)

    def draw_board(self):
        """Draw the board and current piece"""
        self.canvas.delete("all")  # Clear the canvas
        
        # Draw the board with locked pieces
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] is not None:
                    self.canvas.create_rectangle(
                        x * BLOCK_SIZE, y * BLOCK_SIZE,
                        (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                        fill=self.board[y][x], outline='black'
                    )

        # Draw the current piece
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    self.canvas.create_rectangle(
                        (self.current_piece.x + x) * BLOCK_SIZE, 
                        self.current_piece.pixel_y + (y * BLOCK_SIZE),
                        (self.current_piece.x + x + 1) * BLOCK_SIZE, 
                        self.current_piece.pixel_y + (y * BLOCK_SIZE) + BLOCK_SIZE,
                        fill=self.current_piece.color, outline='black'
                    )

    def valid_move(self, dx, dy):
        """Check if moving the piece by dx, dy is valid"""
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    new_x = self.current_piece.x + x + dx
                    new_y = (self.current_piece.y + y + dy)
                    if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x] is not None:
                        return False
        return True

    def lock_piece(self):
        """Lock the current piece into the board, clear rows, and generate a new piece"""
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    self.board[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_full_rows()
        self.current_piece = self.new_piece()

        # Check for Game Over
        if not self.valid_move(0, 1) and self.current_piece.y == 0:
            self.game_over()

    def handle_key(self, event):
        """Handle user input"""
        if event.keysym == 'Left' and self.valid_move(-1, 0):
            self.current_piece.x -= 1
        elif event.keysym == 'Right' and self.valid_move(1, 0):
            self.current_piece.x += 1
        elif event.keysym == 'Down':  # Speed up drop when down key is pressed
            self.drop_speed = FAST_DROP_SPEED
        elif event.keysym == 'Up':  # Rotate piece
            original_shape = self.current_piece.shape
            self.current_piece.rotate()
            if not self.valid_move(0, 0):  # If the rotated shape is not valid, undo the rotation
                self.current_piece.shape = original_shape

    def check_collision(self):
        """Check if the piece has hit the bottom or another piece"""
        if not self.valid_move(0, 1):
            self.lock_piece()

    def clear_full_rows(self):
        """Check and clear any full rows, and update the score"""
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared_rows = BOARD_HEIGHT - len(new_board)
        self.score += cleared_rows * 100  # 100 points for each cleared row
        self.score_label.config(text=f"Score: {self.score}")  # Update the score label

        # Add empty rows at the top
        for _ in range(cleared_rows):
            new_board.insert(0, [None for _ in range(BOARD_WIDTH)])
        self.board = new_board

    def game_over(self):
        """Display Game Over message and stop the game"""
        self.running = False
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="GAME OVER", font=("Helvetica", 30), fill="red")
        print("Game Over")

    def update(self):
        """Game loop to update the board"""
        # If the piece is still falling and hasn't hit the bottom
        self.current_piece.pixel_y += self.drop_speed

        # If the piece reaches the next block boundary, check for collision
        if self.current_piece.pixel_y >= (self.current_piece.y + 1) * BLOCK_SIZE:
            self.current_piece.pixel_y = (self.current_piece.y + 1) * BLOCK_SIZE
            self.current_piece.y += 1
            self.check_collision()

        self.draw_board()

        # Reset drop speed if the down key is not pressed anymore
        self.drop_speed = FALL_SPEED

        if self.running:
            self.root.after(10, self.update)  # Update the game every 10 ms for smoother falling


# Main game execution
root = tk.Tk()
game = Tetris(root)
root.title('Tetris')
root.mainloop()