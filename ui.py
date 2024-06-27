import math
import random
import urllib.request
import numpy as np
import tkinter as tk
from tkinter import font as tkfont

import cv2
from PIL import Image, ImageTk

from recognize import recognize_images

SCISSORS = 'scissors'
ROCK = 'rock'
PAPER = 'paper'


def select_winner(result):
    if len(result) == 0:
        return -1
    if result[0] == result[1]:
        return 0
    if result[0] == ROCK and result[1] == SCISSORS:
        return 1
    if result[0] == ROCK and result[1] == PAPER:
        return 2
    if result[0] == PAPER and result[1] == SCISSORS:
        return 2
    if result[0] == PAPER and result[1] == ROCK:
        return 1
    if result[0] == SCISSORS and result[1] == PAPER:
        return 1
    if result[0] == SCISSORS and result[1] == ROCK:
        return 2
    return -1


def get_low_photo():
    image_url = "http://172.20.10.6/cam-lo.jpg"
    img_response = urllib.request.urlopen(image_url)
    imgnp = np.array(bytearray(img_response.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    return img


def get_high_photo():
    image_url = "http://172.20.10.6/cam-hi.jpg"
    img_response = urllib.request.urlopen(image_url)
    imgnp = np.array(bytearray(img_response.read()), dtype=np.uint8)
    img = cv2.imdecode(imgnp, -1)
    return img


class RockPaperScissorsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors Registration")

        # Load background image using Pillow
        self.bg_image = Image.open("rock_paper_scissors_background.png")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Custom fonts
        self.title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=14)
        self.button_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

        # Frame for registration form
        self.frame = tk.Frame(root, bg='white', bd=5)
        self.frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.15, anchor='n')

        self.label = tk.Label(self.frame, text="Enter your username", bg='white', font=self.label_font)
        self.label.place(relwidth=0.4, relheight=1)

        self.entry = tk.Entry(self.frame, font=self.label_font)
        self.entry.place(relx=0.4, relwidth=0.3, relheight=1)

        self.register_button = tk.Button(self.frame, text="Register", command=self.register_user, bg="#4CAF50",
                                         fg="white", font=self.button_font)
        self.register_button.place(relx=0.7, relheight=1, relwidth=0.15)

        self.unregister_button = tk.Button(self.frame, text="Unregister", command=self.unregister_user, bg="#f44336",
                                           fg="white", font=self.button_font)
        self.unregister_button.place(relx=0.85, relheight=1, relwidth=0.15)

        # Frame for registered users list
        self.list_frame = tk.Frame(root, bg='white', bd=5)
        self.list_frame.place(relx=0.5, rely=0.3, relwidth=0.75, relheight=0.5, anchor='n')

        self.list_label = tk.Label(self.list_frame, text="Registered Users", bg='white', font=self.title_font)
        self.list_label.place(relwidth=1, relheight=0.1)

        # Scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.place(relx=0.95, rely=0.1, relheight=0.9)

        self.user_listbox = tk.Listbox(self.list_frame, font=self.label_font, yscrollcommand=self.scrollbar.set,
                                       bg="#f0f0f0", activestyle="dotbox", selectbackground="#d0e0f0",
                                       selectforeground="#000000")
        self.user_listbox.place(rely=0.1, relwidth=0.95, relheight=0.9)

        self.scrollbar.config(command=self.user_listbox.yview)

        # Start game button
        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, bg="#007BFF", fg="white",
                                      font=self.button_font)
        self.start_button.place(relx=0.5, rely=0.85, anchor='n', relwidth=0.3, relheight=0.1)

        self.registered_users = ['q', 'b', 'c', 'd']

    def register_user(self):
        username = self.entry.get().strip()
        if username and username not in self.registered_users:
            self.registered_users.append(username)
            self.update_user_list()
            self.entry.delete(0, tk.END)
        elif username in self.registered_users:
            tk.messagebox.showerror("Error", "Username already registered.")
        else:
            tk.messagebox.showerror("Error", "Please enter a username.")

    def unregister_user(self):
        username = self.entry.get().strip()
        if username in self.registered_users:
            self.registered_users.remove(username)
            self.update_user_list()
            self.entry.delete(0, tk.END)
        else:
            tk.messagebox.showerror("Error", "Username not found.")

    def update_user_list(self):
        self.user_listbox.delete(0, tk.END)
        for user in self.registered_users:
            self.user_listbox.insert(tk.END, user)

    def start_game(self):
        if len(self.registered_users) < 3:
            tk.messagebox.showerror("Error", "At least 3 players are required to start the game.")
        else:
            self.game_index = 0
            self.winners = []
            self.current_players = self.registered_users.copy()
            self.open_game_window(self.current_players)

    def open_game_window(self, players):
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title("Rock Paper Scissors Game")
        self.game_window.geometry("1024x768")

        game_label = tk.Label(self.game_window, text="Rock Paper Scissors", font=self.title_font)
        game_label.pack(pady=20)

        self.current_game_label = tk.Label(self.game_window,
                                           text=f"Game {self.game_index // 2 + 1}: {self.current_players[self.game_index]} vs {self.current_players[self.game_index + 1]}",
                                           font=self.label_font)
        self.current_game_label.pack(pady=20)

        play_button = tk.Button(self.game_window, text="Play",
                                command=lambda: self.play_game(self.current_players[self.game_index],
                                                               self.current_players[self.game_index + 1]), bg="#007BFF",
                                fg="white", font=self.button_font)
        play_button.pack(pady=20)

        show_tree_button = tk.Button(self.game_window, text="Show Tree",
                                     command=lambda: self.show_tree(players, self.winners), bg="#28a745", fg="white",
                                     font=self.button_font)
        show_tree_button.pack(pady=20)

    def play_game(self, player1, player2):
        play_game_window = tk.Toplevel(self.root)
        play_game_window.title("Game")
        play_game_window.geometry("600x600")

        game_label = tk.Label(play_game_window, text=f"{player1} vs {player2}", font=self.label_font)
        game_label.pack(pady=5)

        outcome_label = tk.Label(play_game_window, text="", font=self.label_font)
        outcome_label.pack(pady=5)

        countdown_label = tk.Label(play_game_window, text="5", font=self.label_font)
        countdown_label.pack(pady=5)

        trigger_button = tk.Button(play_game_window, text="Trigger Outcome", command=lambda: countdown(5), bg="#007BFF",
                                   fg="white", font=self.button_font)
        trigger_button.pack(pady=5)

        retry_button = tk.Button(play_game_window, text="Retry", command=lambda: retry(), bg="#007BFF",
                                 fg="white", font=self.button_font)
        retry_button.pack(pady=5)

        photo_label = tk.Label(play_game_window)
        photo_label.pack(pady=5)

        self.update_photo_flag = True  # Initialize the flag

        def retry():
            countdown_label.config(text="5")
            if self.update_photo_flag != True:
                self.update_photo_flag = True
                update_photo()

        def update_photo():
            if not self.update_photo_flag:
                return
            try:
                photo = cv2.resize(get_low_photo(), (360, 240))
                photo = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(photo)
                imgtk = ImageTk.PhotoImage(image=img)
                photo_label.config(image=imgtk)
                photo_label.image = imgtk  # Keep a reference to avoid garbage collection
            except Exception as e:
                print("Error in downloading live image: ", e)
            finally:
                play_game_window.after(200, update_photo)  # Schedule the next update

        def countdown(count):
            if count >= 0:
                countdown_label.config(text=str(count))
                play_game_window.after(1000, countdown, count - 1)
            else:
                trigger_game()

        def trigger_game():
            self.update_photo_flag = False  # Stop the photo update process
            saved_image = get_high_photo()
            resized_image = cv2.resize(saved_image, (360, 240))
            resized_image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(resized_image_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            photo_label.config(image=imgtk)
            photo_label.image = imgtk  # Keep a reference to avoid garbage collection
            result = recognize_images(saved_image)
            winner = select_winner(result)
            if winner == 0:
                outcome_label.config(text=f"{player1} vs {player2}: Draw!")
            elif winner in [1, 2]:
                winner = player1 if winner == 1 else player2
                self.winners.append(winner)
                outcome_label.config(text=f"{player1} vs {player2}: {winner} wins!")
                self.game_index += 2
                play_game_window.after(3000, lambda: [play_game_window.destroy(), self.update_main_game_window()])
            else:
                outcome_label.config(text="Image was not good. Please try again...")

        update_photo()

    def update_main_game_window(self):
        if self.game_index < len(self.current_players) - 1:
            self.current_game_label.config(
                text=f"Game {self.game_index // 2 + 1}: {self.current_players[self.game_index]} vs {self.current_players[self.game_index + 1]}")
        else:
            if len(self.winners) > 1:
                self.current_players = self.winners.copy()
                self.winners = []
                self.game_index = 0
                self.current_game_label.config(
                    text=f"Game {self.game_index // 2 + 1}: {self.current_players[self.game_index]} vs {self.current_players[self.game_index + 1]}")
            else:
                final_label = tk.Label(self.game_window, text=f"The final winner is {self.winners[0]}",
                                       font=self.title_font)
                final_label.pack(pady=20)

    def show_tree(self, players, winners):
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Elimination Tree")
        tree_window.geometry("1024x768")
        self.create_elimination_tree(tree_window, players, winners)

    def create_elimination_tree(self, parent, players, winners):
        num_players = len(players)
        num_rounds = math.ceil(math.log2(num_players))
        bracket_frame = tk.Frame(parent)
        bracket_frame.pack(pady=20)

        current_players = players.copy()
        for round_num in range(num_rounds):
            round_frame = tk.Frame(bracket_frame)
            round_frame.pack(side=tk.LEFT, padx=20)

            round_label = tk.Label(round_frame, text=f"Round {round_num + 1}", font=self.label_font)
            round_label.pack()

            next_round_players = []
            for i in range(0, len(current_players), 2):
                match_frame = tk.Frame(round_frame)
                match_frame.pack(pady=10)

                if i < len(current_players):
                    player1_label = tk.Label(match_frame, text=current_players[i], font=self.label_font)
                    player1_label.pack()
                else:
                    player1_label = tk.Label(match_frame, text="Bye", font=self.label_font)
                    player1_label.pack()

                if i + 1 < len(current_players):
                    player2_label = tk.Label(match_frame, text=current_players[i + 1], font=self.label_font)
                    player2_label.pack()
                else:
                    player2_label = tk.Label(match_frame, text="Bye", font=self.label_font)
                    player2_label.pack()

                if round_num == 0:
                    next_round_players.append(
                        f"Winner of {current_players[i]} vs {current_players[i + 1] if i + 1 < len(current_players) else 'Bye'}")
                else:
                    next_round_players.append(winners.pop(
                        0) if winners else f"Winner of {current_players[i]} vs {current_players[i + 1] if i + 1 < len(current_players) else 'Bye'}")

            current_players = next_round_players

        final_label = tk.Label(bracket_frame, text="Final Winner", font=self.title_font)
        final_label.pack(side=tk.LEFT, padx=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = RockPaperScissorsApp(root)
    root.geometry("800x600")
    root.mainloop()
