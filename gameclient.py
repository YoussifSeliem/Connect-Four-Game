import tkinter as tk
from tkinter import messagebox
from socket import *
from threading import Thread


class ConnectFour:
    def __init__(self, master):
        self.master = master
        self.master.title("Connect Four")
        self.player1_score = tk.IntVar()
        self.player2_score = tk.IntVar()
        self.chat_frame = tk.Frame(master, bg="sky blue")
        self.input_entry = tk.Entry(self.chat_frame, width=40)
        self.msg_text = tk.Text(self.chat_frame, height=35, width=50)
        # Initial scores
        self.player1_score.set(0)
        self.player2_score.set(0)
        self.canvas = tk.Canvas(master, width=500, height=450, bg="sky blue", highlightthickness=0)
        self.canvas.grid(row=1 ,column=0 ,columnspan=2 ,pady=10)
        self.board = [[0] * 7 for _ in range(6)]  # 6 rows, 7 columns
        self.turn = 1  # Player 1's turn: 1, Player 2's turn: 2
        self.start_server()
        self.draw_board()

    def start_server(self):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.connect(('127.0.0.1', 50000))
        self.acc = Thread(target=self.receive_message)
        self.acc.start()
        
    def draw_board(self):
        self.canvas.delete("all")
        for row in range(6):
            for col in range(7):
                x0, y0 = col * 70, row * 70
                x1, y1 = x0 + 70, y0 + 70
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")
                if self.board[row][col] == 1:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="red", outline="")
                elif self.board[row][col] == 2:
                    self.canvas.create_oval(x0 + 5, y0 + 5, x1 - 5, y1 - 5, fill="yellow", outline="")
                if row < 5:
                    self.canvas.create_line(x0, y1, x1, y1, fill="black", width=2)
                if col < 6:
                    self.canvas.create_line(x1, y0, x1, y1, fill="black", width=2)
        print (self.turn)

                    
    def drop_piece(self, col):
        
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                self.draw_board()
                print(f"here {self.turn}")
                if self.turn == 2:
                    self.send_play(col)
                if self.check_win(row, col):
                    messagebox.showinfo("Winner", f"Player {self.turn} wins!")
                    if self.turn == 1:
                        self.player1_score.set(self.player1_score.get() + 1)
                    else:
                        self.player2_score.set(self.player2_score.get() + 1)
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
        self.s.send(str(col).encode("utf-8"))

    def handle_play(self,n):
        self.drop_piece(n)
        print(f"there {self.turn}")

    def apply_play(self,p):
        p = p.decode("utf-8")
        if p == "RESET":
            if self.check() == 'yes':
                self.reset_board()
                msg = "YES"
                self.s.send(msg.encode("utf-8"))
            else:
                msg = "NO"
                print("I said no")
                self.s.send(msg.encode("utf-8"))
            return
        elif p == "QUIT":
            msg = "QUIT"
            self.s.send(msg.encode("utf-8"))
            self.master.destroy()
            self.s.close()
        elif p == "YES":
            self.reset_board()
            return
        elif p == "NO":
            return
        elif p not in ['1', '2', '3', '4', '5', '6', '7']:
            self.msg_text.insert(tk.END, p + "\n")
            return
        p = int(p)
        self.handle_play(p)

    
    def check(self):
        return messagebox.askquestion("RESET","Reset?")


    # def handle_client(self):
    #         self.c,ad = self.s.accept()
    #         receive = Thread(target = self.receive_message, args = [self.c,])
    #         receive.start()
        
    def receive_message(self):
        while True:
            self.p = self.s.recv(1024)
            self.apply_play(self.p)

    def send_message(self,col):
        if self.turn != 2:
            return
        self.drop_piece(col)
    
    def reset(self):
        msg = "RESET"
        self.s.send(msg.encode("utf-8"))
        ### the other accepts
        return

    def quit(self):
        msg = "QUIT"
        self.s.send(msg.encode("utf-8"))
        return
    
    def chat_send(self):
        msg = self.input_entry.get()
        msg = "player2 : "+msg
        self.msg_text.insert(tk.END, msg + "\n")
        self.s.send(msg.encode("utf-8"))
        self.input_entry.delete(0, tk.END)
    


def main():
    root = tk.Tk()
    root.configure(bg="white")
    game = ConnectFour(root)
    
    
    game.chat_frame.grid(row=0, column=2,rowspan=4, padx=5)

    chat_label = tk.Label(game.chat_frame, text="Chat", font=("Helvetica", 14, "bold"), bg = "sky blue")
    chat_label.grid(row=0, column=2, padx=5,pady=5)

    game.msg_text.grid(row=1, column=2, padx=5,pady=5)

    
    game.input_entry.grid(row=2, column=2, padx=5,pady=5)

    send_button = tk.Button(game.chat_frame, text="Send", command=game.chat_send)
    send_button.grid(row=3, column=2, padx=5,pady=5)

    # def create_drop_piece_handler(col):
    #     print("I'm clicking")
    #     if game.turn != 2:
    #         return
    #     print("click is good")
    #     def handler():
    #         game.drop_piece(col)
    #     return handler

        # Labels to display scores
    player1 = tk.Frame(root, bg="white")
    player1.grid(row=0, column=0, padx=5)

    player1_label = tk.Label(player1, text="Player 1", width=13, height=1,padx=2,pady=5, bg="sky blue", relief=tk.GROOVE)
    player1_label.grid(row=0, column=0)

    player1_score_label = tk.Label(player1, textvariable=game.player1_score, width=3, height=1,padx=2,pady=5, bg="sky blue", relief=tk.GROOVE)
    player1_score_label.grid(row=0, column=1)

    
    player2 = tk.Frame(root, bg="white")
    player2.grid(row=0, column=1, padx=5)

    player2_label = tk.Label(player2, text="Player 2", width=13, height=1,padx=2,pady=5, bg="sky blue", relief=tk.GROOVE)
    player2_label.grid(row=0, column=2)

    player2_score_label = tk.Label(player2, textvariable=game.player2_score, width=3, height=1,padx=2,pady=5, bg="sky blue", relief=tk.GROOVE)
    player2_score_label.grid(row=0, column=3)


    buttons_frame = tk.Frame(root, bg="white")
    buttons_frame.grid(row=2 ,column=0 ,columnspan=2 ,pady=10)
    buttons = []
    for col in range(7):
        button = tk.Button(buttons_frame, text=str(col+1), font=("Helvetica", 12, "bold"), width=5, height=1,
                   command=lambda col=col: game.send_message(col), bg="sky blue", relief=tk.GROOVE)
        button.grid(row=0, column=col, padx=5)
        buttons.append(button)
    
    reset = tk.Button(game.master, text="RESET", font=("Helvetica", 12, "bold"), width=13, height=1,padx=5,pady=5,
                   command=game.reset, bg="sky blue", relief=tk.GROOVE)
    reset.grid(row=3, column=0, padx=5)

    quit = tk.Button(game.master, text="QUIT", font=("Helvetica", 12, "bold"), width=13, height=1,padx=5,pady=5,
                   command=game.quit, bg="sky blue", relief=tk.GROOVE)
    quit.grid(row=3, column=1, padx=5)


    root.mainloop()


if __name__ == "__main__":
    main()
