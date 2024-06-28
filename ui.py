import math
import random
import urllib.request
import numpy as np
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
from collections import defaultdict

from recognize import recognize_images, recognize_one_hand
from agent import MarkovModel
from email_service import EmailService
# from ai_a import EnsembleAgent

import threading
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

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


def get_low_photo_duo():
   return cv2.imread(random.choice(['cam.jpg', 'cam2.jpg']))

def get_low_photo_single():
   return cv2.imread(random.choice(['rock.jpg', 'paper.jpg', 'scissors.jpg']))

def get_high_photo():
  return cv2.imread('cam.jpg')

def get_high_photo_ai(filename):
  return cv2.imread(filename)

def get_high_photo_human():
  return cv2.imread(random.choice(['rock.jpg', 'scissors.jpg']))

class RockPaperScissorsApp:
    def __init__(self, root):
        self.email_service = EmailService("benyamin.maleki@sharif.edu", "?")
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
        self.frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.25, anchor='n')

        self.label = tk.Label(self.frame, text="Enter your username", bg='white', font=self.label_font)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.entry = tk.Entry(self.frame, font=self.label_font)
        self.entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.email_label = tk.Label(self.frame, text="Enter your email", bg='white', font=self.label_font)
        self.email_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.email_entry = tk.Entry(self.frame, font=self.label_font)
        self.email_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        self.register_button = tk.Button(self.frame, text="Register", command=self.register_user, bg="#4CAF50",
                                        fg="white", font=self.button_font)
        self.register_button.grid(row=0, column=2, padx=10, pady=10, sticky='w')

        self.unregister_button = tk.Button(self.frame, text="Unregister", command=self.unregister_user, bg="#f44336",
                                        fg="white", font=self.button_font)
        self.unregister_button.grid(row=1, column=2, padx=10, pady=10, sticky='w')

        # Frame for registered users list
        self.list_frame = tk.Frame(root, bg='white', bd=5)
        self.list_frame.place(relx=0.5, rely=0.35, relwidth=0.75, relheight=0.45, anchor='n')

        self.list_label = tk.Label(self.list_frame, text="Registered Users", bg='white', font=self.title_font)
        self.list_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.grid(row=1, column=1, sticky='ns')

        self.user_listbox = tk.Listbox(self.list_frame, font=self.label_font, yscrollcommand=self.scrollbar.set,
                                    bg="#f0f0f0", activestyle="dotbox", selectbackground="#d0e0f0",
                                    selectforeground="#000000")
        self.user_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.scrollbar.config(command=self.user_listbox.yview)

        # Configure grid to expand properly
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Start game button
        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, bg="#007BFF", fg="white",
                                    font=self.button_font)
        self.start_button.place(relx=0.3, rely=0.85, anchor='n', relwidth=0.2, relheight=0.1)

        # Start game with AI button
        self.start_ai_button = tk.Button(root, text="Start Game with AI", command=self.start_game_with_ai, bg="#FF5722", fg="white",
                                        font=self.button_font)
        self.start_ai_button.place(relx=0.7, rely=0.85, anchor='n', relwidth=0.3, relheight=0.1)

        self.registered_users = []
        self.user_emails = {}
        self.player_results = defaultdict(list)
        self.start_flask_thread()


    def start_flask_thread(self):
        flask_thread = threading.Thread(target=app.run, kwargs={'port': 5000, 'host': '0.0.0.0', 'use_reloader': False})
        flask_thread.daemon = True
        flask_thread.start()

    def register_user(self):
        username = self.entry.get().strip()
        email = self.email_entry.get().strip()
        if username not in self.registered_users:
            self.registered_users.append(username)
            if email:
                self.user_emails[username] = email
            else:
                self.user_emails[username] = 'NA'
            self.update_user_list()
            self.entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
        elif username in [user['username'] for user in self.registered_users]:
            messagebox.showerror("Error", "Username already registered.")
        else:
            messagebox.showerror("Error", "Please enter both username and email.")

    def unregister_user(self):
        username = self.entry.get().strip()
        if username in [user['username'] for user in self.registered_users]:
            self.registered_users = [user for user in self.registered_users if user['username'] != username]
            self.user_emails.pop(username)
            self.update_user_list()
            self.entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Username not found.")

    def update_user_list(self):
        self.user_listbox.delete(0, tk.END)
        for username in self.registered_users:
            self.user_listbox.insert(tk.END, f"{username} ({self.user_emails[username]})")

    def start_game(self):
        if len(self.registered_users) < 3:
            messagebox.showerror("Error", "At least 3 players are required to start the game.")
        else:
            self.game_index = 0
            self.winners = []
            self.allwinners = []

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
                                     command=lambda: self.show_tree(players, self.allwinners), bg="#28a745", fg="white",
                                     font=self.button_font)
        show_tree_button.pack(pady=20)

    def play_game(self, player1, player2):
        play_game_window = tk.Toplevel(self.root)
        play_game_window.title("Game")
        play_game_window.geometry("1024x768")

        game_label = tk.Label(play_game_window, text=f"{player1} vs {player2}", font=self.label_font)
        game_label.pack(pady=5)

        outcome_label = tk.Label(play_game_window, text="", font=self.label_font)
        outcome_label.pack(pady=5)

        countdown_label = tk.Label(play_game_window, text="5", font=self.label_font)
        countdown_label.pack(pady=5)

        retry_button = tk.Button(play_game_window, text="Retry", command=lambda: retry(), bg="#007BFF",
                                 fg="white", font=self.button_font)
        retry_button.pack(pady=5)

        photo_label = tk.Label(play_game_window)
        photo_label.pack(pady=5)

        left_image_label = tk.Label(play_game_window)
        left_image_label.pack(side=tk.LEFT, padx=10)

        vs_label = tk.Label(play_game_window, text="VS", font=self.label_font)
        vs_label.pack(side=tk.LEFT, padx=10)

        right_image_label = tk.Label(play_game_window)
        right_image_label.pack(side=tk.LEFT, padx=10)

        self.update_photo_flag = True  # Initialize the flag

        def retry():
            countdown_label.config(text="5")
            vs_label.pack_forget()
            left_image_label.pack_forget()
            right_image_label.pack_forget()
            if self.update_photo_flag != True:
                self.update_photo_flag = True
                update_photo()

        def update_photo():
            if not self.update_photo_flag:
                return
            try:
                photo = get_low_photo_duo()
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

            outcome_label.config(text=f"Processing...")

            result, images = recognize_images(saved_image)
            if len(images) == 2:
                left_image, right_image = images
                # Display left and right images
                left_img = Image.fromarray(cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB))
                left_imgtk = ImageTk.PhotoImage(image=left_img)
                left_image_label.config(image=left_imgtk)
                left_image_label.image = left_imgtk

                right_img = Image.fromarray(cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB))
                right_imgtk = ImageTk.PhotoImage(image=right_img)
                right_image_label.config(image=right_imgtk)
                right_image_label.image = right_imgtk

                vs_label.pack(side=tk.LEFT, padx=10)
                left_image_label.pack(side=tk.LEFT, padx=10)
                right_image_label.pack(side=tk.LEFT, padx=10)

            winner = select_winner(result)
            if winner == 0:
                outcome_label.config(text=f"{player1} vs {player2}: Tie!")

            elif winner in [1, 2]:
                winner = player1 if winner == 1 else player2
                loser = player2 if winner == player1 else player1
                self.player_results[player1].append((winner, loser))
                self.player_results[player2].append((winner, loser))
                self.winners.append(winner)
                self.allwinners.append(winner)
                outcome_label.config(text=f"{player1} vs {player2}: {winner} wins!")
                self.game_index += 2
                play_game_window.after(3000, lambda: [play_game_window.destroy(), self.update_main_game_window()])
            else:
                outcome_label.config(text="Image was not good. Please try again...")
                

        update_photo()
        self.current_countdown = countdown



    def start_game_with_ai(self):
        self.open_ai_window()


    def open_ai_window(self):
        play_game_window = tk.Toplevel(self.root)
        play_game_window.title("Game")
        play_game_window.geometry("1024x768")

        game_label = tk.Label(play_game_window, text=f"Human vs AI", font=self.label_font)
        game_label.pack(pady=5)

        outcome_label = tk.Label(play_game_window, text="", font=(self.label_font.actual('family'), 16, 'bold'))
        outcome_label.pack(pady=5)

        countdown_label = tk.Label(play_game_window, text="5", font=self.label_font)
        countdown_label.pack(pady=5)

        retry_button = tk.Button(play_game_window, text="Retry", command=lambda: retry(), bg="#007BFF",
                                 fg="white", font=self.button_font)
        retry_button.pack(pady=5)

        ai_wins = [0]
        human_wins = [0]
        ties = [0]
        initial_game_results = f"Human: {human_wins[0]}\n AI: {ai_wins[0]}\n Ties: {ties[0]}"
        game_results = tk.Label(play_game_window, text=initial_game_results, font=self.label_font)
        def update_game_results():
            game_results.config(text=f"Human: {human_wins[0]}\n AI: {ai_wins[0]}\n Ties: {ties[0]}")
        game_results.pack(pady=5)

        left_image_label = tk.Label(play_game_window)
        left_image_label.pack(side=tk.LEFT, padx=10)
        left_image_label.place(relx=0.25, rely=0.5, anchor='center')

        vs_label = tk.Label(play_game_window, text="VS", font=self.label_font)
        vs_label.pack(side=tk.LEFT, padx=10)
        vs_label.place(relx=0.5, rely=0.5, anchor='center')

        right_image_label = tk.Label(play_game_window)
        right_image_label.pack(side=tk.LEFT, padx=10)
        right_image_label.place(relx=0.75, rely=0.5, anchor='center')

        human_choice_label = tk.Label(play_game_window, text="Human Choice", font=self.label_font)
        human_choice_label.pack(side=tk.LEFT, padx=10)
        human_choice_label.place(relx=0.2, rely=0.8, anchor='center')
       
        ai_choice_label = tk.Label(play_game_window, text="AI Choice", font=self.label_font)
        ai_choice_label.pack(side=tk.LEFT, padx=10)
        ai_choice_label.place(relx=0.8, rely=0.8, anchor='center')

        self.update_photo_flag = True  # Initialize the flag

        def retry():
            countdown_label.config(text="5")
            vs_label.pack_forget()
            left_image_label.config(image='')
            right_image_label.config(image='')
            human_choice_label.config(text="Human Choice")
            ai_choice_label.config(text="AI Choice")
            outcome_label.config(text="")
            if self.update_photo_flag != True:
                self.update_photo_flag = True
                update_photo()

        def update_photo():
            if not self.update_photo_flag:
                return
            try:
                photo = get_low_photo_single()
                resized_photo = cv2.resize(photo, (360, 240))
                resized_photo_rgb = cv2.cvtColor(resized_photo, cv2.COLOR_BGR2RGB)
                human_img = Image.fromarray(resized_photo_rgb)
                human_imgtk = ImageTk.PhotoImage(image=human_img)
                left_image_label.config(image=human_imgtk)
                left_image_label.image = human_imgtk
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
            agent = MarkovModel()
            self.update_photo_flag = False  # Stop the photo update process
            saved_image = get_high_photo_human()
            resized_image = cv2.resize(saved_image, (360, 240))
            resized_image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            human_img = Image.fromarray(resized_image_rgb)
            human_imgtk = ImageTk.PhotoImage(image=human_img)
            left_image_label.config(image=human_imgtk)
            left_image_label.image = human_imgtk  # Keep a reference to avoid garbage collection
            human_choice = recognize_one_hand(saved_image)

            outcome_label.config(text=f"Processing...")

            # Mock AI choice 
            if human_choice == 'NA':
                ai_choice = 'na'
            else:
                ai_move = agent.predict_next_move()
                ai_choice = ROCK if ai_move == 'R' else PAPER if ai_move == 'P' else SCISSORS
                human_move = 'R' if human_choice == ROCK else 'P' if human_choice == PAPER else 'S'
                agent.update_model(human_move)

            # Load AI choice image
            ai_image = cv2.imread(f'ai-{ai_choice}.png')
            resized_ai_image = cv2.resize(ai_image, (360, 240))
            resized_ai_image_rgb = cv2.cvtColor(resized_ai_image, cv2.COLOR_BGR2RGB)
            ai_img = Image.fromarray(resized_ai_image_rgb)
            ai_imgtk = ImageTk.PhotoImage(image=ai_img)
            right_image_label.config(image=ai_imgtk)
            right_image_label.image = ai_imgtk  # Keep a reference to avoid garbage collection

            # Decide winner
            human_choice_label.config(text=f"Human Choice: {human_choice.upper()}")
            ai_choice_label.config(text=f"AI Choice: {ai_choice.upper()}")

            result = [human_choice, ai_choice]
            if ai_choice == 'na':
                outcome_label.config(text="Image was not good. Please try again...")
            else:
                winner = select_winner(result)
                if winner == 0:
                    outcome_label.config(text=f"Tie!")
                    ties[0] += 1
                elif winner == 1:
                    outcome_label.config(text=f"Human wins!")
                    human_wins[0] += 1
                else:
                    outcome_label.config(text=f"AI wins!")
                    ai_wins[0] += 1
                update_game_results()

        update_photo()
        self.current_countdown = countdown


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
                for username in self.registered_users:
                    if username == self.winners[0] and username in self.user_emails:
                        matches_messages = ''
                        for match in self.player_results[username]:
                            match_result = 'You won!' if match[0] == username else 'You lost!'
                            matches_messages += f"{match[0]} vs {match[1]}: {match_result}\n"
                        message = f'Congratulations {username}! You are the final winner!\n' + matches_messages
                        self.email_service.add_email(self.user_emails[username], f"Game Result", message)       

                    elif username != self.winners[0] and username in self.user_emails: 
                        matches_messages = ''
                        for match in self.player_results[username]:
                            match_result = 'You won!' if match[0] == username else 'You lost!'
                            matches_messages += f"{match[0]} vs {match[1]}: {match_result}\n"
                        message = f'Dear {username},\n We are sorry to inform you that you are a loser.\n' + matches_messages
                        self.email_service.add_email(self.user_emails[username], f"Game Result", message)
                self.email_service.send_email()
                self.email_service.clear_emails
                self.player_results.clear()
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

        winners = winners.copy()

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
                    if current_players[i] in self.allwinners:
                        next_round_players.append(current_players[i])
                    elif current_players[i+1] in self.allwinners:
                        next_round_players.append(current_players[i+1])
                    else:
                        next_round_players.append(
                            f"Winner of {current_players[i]} vs {current_players[i + 1] if i + 1 < len(current_players) else 'Bye'}")
                else:
                    next_round_players.append(winners.pop(
                        0) if winners else f"Winner of {current_players[i]} vs {current_players[i + 1] if i + 1 < len(current_players) else 'Bye'}")

            current_players = next_round_players

        final_label = tk.Label(bracket_frame, text="Final Winner", font=self.title_font)
        final_label.pack(side=tk.LEFT, padx=20)


@app.route('/start_countdown', methods=['POST'])
def start_countdown():
    app.current_countdown(5)
    return jsonify({'status': 'countdown started'})


root = tk.Tk()
app = RockPaperScissorsApp(root)
root.geometry("800x600")
root.mainloop()
