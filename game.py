import tkinter as tk
from tkinter import messagebox
from socket import *
from threading import Thread


class ConnectFour:
    def __init__(self, master):
        self.master = master
        self.master.title("Connect Four")
        self.canvas = tk.Canvas(master, width=500, height=450, bg="light green", highlightthickness=0)
        self.canvas.grid(row=0 ,column=0 ,columnspan=2 ,pady=10)
        self.board = [[0] * 7 for _ in range(6)]  # 6 rows, 7 columns
        self.turn = 1  # Player 1's turn: 1, Player 2's turn: 2
        self.start_server()
        self.draw_board()

    def start_server(self):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.bind(('127.0.0.1', 50000))
        self.s.listen(5)
        self.c = None

        self.acc = Thread(target=self.handle_client)
        self.acc.start()
        
    def draw_board(self):
        self.canvas.delete("all")
        for row in range(6):
            for col in range(7):
                x0, y0 = col * 70, row * 70
                x1, y1 = x0 + 70, y0 + 70
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="grey", outline="")
                if self.board[row][col] == 1:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="red", outline="")
                elif self.board[row][col] == 2:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="yellow", outline="")
                if row < 5:
                    self.canvas.create_line(x0, y1, x1, y1, fill="black", width=2)
                if col < 6:
                    self.canvas.create_line(x1, y0, x1, y1, fill="black", width=2)

                    
    def drop_piece(self, col):
        
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                self.draw_board()
                if self.turn == 1:
                    self.send_play(col)
                if self.check_win(row, col):
                    messagebox.showinfo("Winner", f"Player {self.turn} wins!")
                    self.reset_board()
                elif all(self.board[row][col] != 0 for col in range(7) for row in range(6)):
                    messagebox.showinfo("Draw", "It's a draw!")
                    self.reset_board()
                else:
                    self.turn = 3 - self.turn  # Switch turn
                return
        messagebox.showerror("Invalid Move", "Column is full!")
    
    def check_win(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        for dr, dc in directions:
            count = 1
            r, c = row, col
            while True:
                r, c = r + dr, c + dc
                if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == self.turn:
                    count += 1
                else:
                    break
            r, c = row, col
            while True:
                r, c = r - dr, c - dc
                if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == self.turn:
                    count += 1
                else:
                    break
            if count >= 4:
                return True
        return False
    
    def reset_board(self):
        self.board = [[0] * 7 for _ in range(6)]
        self.turn = 1
        self.draw_board()

    def send_play(self,col):
        self.c.send(str(col).encode("utf-8"))

    def handle_play(self,n):
        self.drop_piece(n)

    def apply_play(self,p):
        p = p.decode("utf-8")
        if p == "RESET":
            if self.check() == 'yes':
                self.reset_board()
                msg = "YES"
                self.c.send(msg.encode("utf-8"))
            else:
                msg = "NO"
                self.c.send(msg.encode("utf-8"))
            return
        elif p == "YES":
            self.reset_board()
            return
        elif p == "NO":
            print("told me no")
            return
        p = int(p)
        self.handle_play(p)

    def handle_client(self):
            self.c,ad = self.s.accept()
            receive = Thread(target = self.receive_message)
            receive.start()
        
    def receive_message(self):
        while True:
            self.p = self.c.recv(10)
            self.apply_play(self.p)
            
    
    def send_message(self,col):
        if self.turn != 1:
            return
        self.drop_piece(col)

    def check(self):
        return messagebox.askquestion("RESET","Reset?")

    def reset(self):
        msg = "RESET"
        self.c.send(msg.encode("utf-8"))
        return
        


        


def main():
    root = tk.Tk()
    root.configure(bg="white")
    game = ConnectFour(root)
    
    # def create_drop_piece_handler(col):
    #     print(f"?????? : {game.turn}")
    #     def handler():
    #     return handler
        
    buttons_frame = tk.Frame(root, bg="white")
    buttons_frame.grid(row=1 ,column=0 ,columnspan=2 ,pady=10)
    # buttons = []
    for col in range(7):
        button = tk.Button(buttons_frame, text=str(col+1), font=("Helvetica", 12, "bold"), width=5, height=1,
                   command=lambda col=col: game.send_message(col), bg="sky blue", relief=tk.GROOVE)
        button.grid(row=0, column=col, padx=5)
    
    reset = tk.Button(game.master, text="RESET", font=("Helvetica", 12, "bold"), width=13, height=1,padx=5,pady=5,
                   command=game.reset, bg="light green", relief=tk.GROOVE)
    reset.grid(row=2, column=0, padx=5)

        # buttons.append(button)
    
    root.mainloop()


if __name__ == "__main__":
    main()
