import random
from collections import defaultdict

class MarkovModel:
    def __init__(self):
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.last_move = None

    def update_model(self, move):
        if self.last_move is not None:
            self.transition_counts[self.last_move][move] += 1
        self.last_move = move

    def predict_next_move(self):
        if self.last_move is None:
            return random.choice(['R', 'P', 'S'])
        
        next_move_counts = self.transition_counts[self.last_move]
        total = sum(next_move_counts.values())
        
        if total == 0:
            return random.choice(['R', 'P', 'S'])
        
        probabilities = {move: count / total for move, count in next_move_counts.items()}
        predicted_move = max(probabilities, key=probabilities.get)
        
        # Counter the predicted move
        if predicted_move == 'R':
            return 'P'  # Paper beats Rock
        elif predicted_move == 'P':
            return 'S'  # Scissors beats Paper
        else:
            return 'R'  # Rock beats Scissors

    def get_winner(self, player_move, ai_move):
        if player_move == ai_move:
            return 'Draw'
        elif (player_move == 'R' and ai_move == 'S') or \
            (player_move == 'P' and ai_move == 'R') or \
            (player_move == 'S' and ai_move == 'P'):
            return 'Player'
        else:
            return 'AI'

    def play_game(self):
        ai_wins = 0
        player_wins = 0
        draws = 0
        total_games = 0

        print("Welcome to Rock-Paper-Scissors!")
        print("Enter your move: R for Rock, P for Paper, S for Scissors. Enter Q to quit.")

        while True:
            player_move = input("Your move: ").upper()
            if player_move not in ['R', 'P', 'S', 'Q']:
                print("Invalid move. Please enter R, P, S, or Q.")
                continue
            
            if player_move == 'Q':
                print("Thanks for playing!")
                break

            ai_choice = self.predict_next_move()
            winner = self.get_winner(player_move, ai_choice)
            
            if winner == 'AI':
                ai_wins += 1
            elif winner == 'Player':
                player_wins += 1
            else:
                draws += 1

            total_games += 1
            ai_win_rate = (ai_wins / total_games) * 100

            print(f"AI chose: {ai_choice}")
            print(f"Winner: {winner}")
            print(f"AI Win Rate: {ai_win_rate:.2f}%")

            self.update_model(player_move)

