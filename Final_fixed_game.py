import random
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import traceback
from datetime import datetime, timedelta

class NumberGuessingGame:
    def __init__(self):
        print("Initializing NumberGuessingGame...")
        self.root = tk.Tk()
        self.root.title("Number Guessing Game")
        self.root.geometry("1000x700")
        
        # Create necessary directories
        for directory in ['data', 'avatars']:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Game modes
        self.game_modes = {
            'classic': {
                'name': 'Classic Mode',
                'description': 'Standard number guessing game',
                'max_attempts': 7,
                'time_limit': None,
                'range': (1, 20)
            },
            'sudden_death': {
                'name': 'Sudden Death',
                'description': 'One attempt to guess correctly!',
                'max_attempts': 1,
                'time_limit': None,
                'range': (1, 20)
            },
            'survival': {
                'name': 'Survival Mode',
                'description': 'Score accumulates across rounds',
                'max_attempts': 5,
                'time_limit': None,
                'range': (1, 20)
            },
            'time_attack': {
                'name': 'Time Attack',
                'description': 'Guess under time pressure',
                'max_attempts': 10,
                'time_limit': 60,
                'range': (1, 20)
            }
        }
        
        # Color schemes
        self.themes = {
            'light': {
                'bg': '#C3E0E5',
                'card': '#F8F8F8',
                'primary': '#39A78E',
                'secondary': '#6497B1',
                'accent': '#FFD700',
                'text': '#333333',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'error': '#F44336',
                'border': '#BBBBBB'
            },
            'dark': {
                'bg': '#1A1A1A',
                'card': '#2D2D2D',
                'primary': '#64B5F6',
                'secondary': '#7986CB',
                'accent': '#9575CD',
                'text': '#FFFFFF',
                'success': '#81C784',
                'warning': '#FFB74D',
                'error': '#E57373',
                'border': '#424242'
            }
        }
        
        # Current theme
        self.current_theme = 'light'
        self.colors = self.themes[self.current_theme]
        
        # Game variables
        self.score = 0
        self.difficulty = "medium"
        self.attempts = 0
        self.max_attempts = 7
        self.secret_number = 0
        self.game_active = False
        self.hints_remaining = 1
        self.start_time = 0
        self.last_guess = None
        self.guess_history = []
        self.timer_running = False
        self.time_elapsed = 0
        self.sound_enabled = True
        self.music_enabled = True
        self.current_mode = 'classic'
        self.survival_score = 0
        self.winning_streak = 0
        self.games_played = 0
        
        # High scores
        self.high_scores = self.load_high_scores()
        
        # Player profile
        self.player_profile = {
            'name': 'Player',
            'avatar': 'default',
            'games_played': 0,
            'total_score': 0,
            'best_time': float('inf'),
            'achievements': [],
            'stats': {
                'accuracy': 0,
                'avg_guess_time': 0,
                'total_guesses': 0,
                'correct_guesses': 0
            }
        }
        
        # Achievement definitions
        self.achievements = {
            'first_win': {'name': 'First Win', 'description': 'Win your first game', 'unlocked': False},
            'winning_streak': {'name': 'Winning Streak', 'description': 'Win 3 games in a row', 'unlocked': False},
            'perfect_game': {'name': 'Perfect Game', 'description': 'Win with the first guess', 'unlocked': False},
            'speed_demon': {'name': 'Speed Demon', 'description': 'Win in under 30 seconds', 'unlocked': False},
            'master_guesser': {'name': 'Master Guesser', 'description': 'Play 10 games', 'unlocked': False}
        }
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", 
                           padding=10, 
                           font=('Helvetica', 12))
        
        # Initialize UI components
        self.setup_ui()
        self.load_profile()
        
        print("Initialization complete!")
        
    def load_high_scores(self):
        try:
            with open('data/high_scores.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Initialize high scores for each difficulty and game mode
            scores = {
                'easy': 0,
                'medium': 0,
                'hard': 0,
                'sudden_death': 0,
                'survival': 0,
                'time_attack': 0
            }
            self.save_high_scores(scores)
            return scores
            
    def save_high_scores(self, scores=None):
        if scores is None:
            scores = self.high_scores
        with open('data/high_scores.json', 'w') as f:
            json.dump(scores, f)
            
    def load_profile(self):
        try:
            with open('data/profile.json', 'r') as f:
                self.player_profile = json.load(f)
                self.player_name_label.config(text=self.player_profile['name'])
        except FileNotFoundError:
            self.save_profile_data()
            
    def save_profile_data(self):
        with open('data/profile.json', 'w') as f:
            json.dump(self.player_profile, f)
            
    def setup_ui(self):
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(expand=True, fill="both")
        
        # Top bar with profile and settings
        self.top_bar = tk.Frame(self.main_container, bg=self.colors['card'], height=50)
        self.top_bar.pack(fill="x", padx=10, pady=5)
        
        # Profile section
        self.profile_frame = tk.Frame(self.top_bar, bg=self.colors['card'])
        self.profile_frame.pack(side="left", padx=10)
        
        self.avatar_label = tk.Label(self.profile_frame, 
                                   text="👤",
                                   font=("Helvetica", 20),
                                   bg=self.colors['card'],
                                   fg=self.colors['text'])
        self.avatar_label.pack(side="left", padx=5)
        
        self.player_name_label = tk.Label(self.profile_frame,
                                        text=self.player_profile['name'],
                                        font=("Helvetica", 12),
                                        bg=self.colors['card'],
                                        fg=self.colors['text'])
        self.player_name_label.pack(side="left", padx=5)
        
        # Settings button
        self.settings_button = ttk.Button(self.top_bar,
                                        text="⚙️",
                                        style="Custom.TButton",
                                        command=self.show_settings)
        self.settings_button.pack(side="right", padx=10)
        
        # Main game area
        self.game_area = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.game_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Title
        self.title_label = tk.Label(self.game_area,
                                  text="Number Guessing Game",
                                  font=("Helvetica", 28, "bold"),
                                  bg=self.colors['bg'],
                                  fg=self.colors['primary'])
        self.title_label.pack(pady=20)
        
        # Game card
        self.game_card = tk.Frame(self.game_area,
                                bg=self.colors['card'],
                                relief="solid",
                                bd=1)
        self.game_card.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Status bar with progress
        self.status_frame = tk.Frame(self.game_card, bg=self.colors['card'])
        self.status_frame.pack(fill="x", pady=10)
        
        # Progress bar for attempts
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame,
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        # Status labels
        self.status_labels_frame = tk.Frame(self.status_frame, bg=self.colors['card'])
        self.status_labels_frame.pack(fill="x", pady=5)
        
        self.difficulty_label = tk.Label(self.status_labels_frame,
                                       text="🎯 Difficulty: Medium",
                                       font=("Helvetica", 12),
                                       bg=self.colors['card'],
                                       fg=self.colors['text'])
        self.difficulty_label.pack(side="left", padx=15)
        
        self.attempts_label = tk.Label(self.status_labels_frame,
                                     text="🎲 Attempts: 0/7",
                                     font=("Helvetica", 12),
                                     bg=self.colors['card'],
                                     fg=self.colors['text'])
        self.attempts_label.pack(side="left", padx=15)
        
        self.timer_label = tk.Label(self.status_labels_frame,
                                  text="⏱️ Time: 0:00",
                                  font=("Helvetica", 12),
                                  bg=self.colors['card'],
                                  fg=self.colors['text'])
        self.timer_label.pack(side="left", padx=15)
        
        self.hints_label = tk.Label(self.status_labels_frame,
                                  text="💡 Hints: 1",
                                  font=("Helvetica", 12),
                                  bg=self.colors['card'],
                                  fg=self.colors['text'])
        self.hints_label.pack(side="left", padx=15)
        
        # Message display
        self.message_frame = tk.Frame(self.game_card, bg=self.colors['card'])
        # Will be packed in start_new_game
        
        self.message_label = tk.Label(self.message_frame,
                                    text="Welcome to Number Guessing Game!",
                                    font=("Helvetica", 14),
                                    bg=self.colors['card'],
                                    fg=self.colors['text'],
                                    wraplength=600)
        self.message_label.pack()
        
        # Input area
        self.input_frame = tk.Frame(self.game_card, bg=self.colors['card'])
        # Will be packed in start_game_round
        
        self.guess_entry = tk.Entry(self.input_frame,
                                  font=("Helvetica", 14),
                                  width=10,
                                  relief="solid",
                                  bd=1,
                                  bg=self.colors['bg'],
                                  fg=self.colors['text'])
        self.guess_entry.pack(side="left", padx=5)
        
        # Buttons
        self.buttons_frame = tk.Frame(self.game_card, bg=self.colors['card'])
        # Will be packed in start_game_round
        
        self.guess_button = ttk.Button(self.buttons_frame,
                                     text="🎯 Guess",
                                     style="Custom.TButton",
                                     command=self.make_guess)
        self.guess_button.pack(side="left", padx=5)
        
        self.hint_button = ttk.Button(self.buttons_frame,
                                    text="💡 Hint",
                                    style="Custom.TButton",
                                    command=self.get_hint)
        self.hint_button.pack(side="left", padx=5)
        
        # Start Game Button
        self.start_button = ttk.Button(self.game_card,
                                     text="▶️ Start Game",
                                     style="Custom.TButton",
                                     command=self.start_game_round)
        # Will be packed in start_new_game
        
        # Menu buttons
        self.menu_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.menu_frame.pack(fill="x", pady=10)
        
        self.new_game_button = ttk.Button(self.menu_frame,
                                        text="🔄 New Game",
                                        style="Custom.TButton",
                                        command=self.start_new_game)
        self.new_game_button.pack(side="left", padx=5)
        
        self.difficulty_button = ttk.Button(self.menu_frame,
                                          text="⚙️ Difficulty",
                                          style="Custom.TButton",
                                          command=self.show_difficulty_menu)
        self.difficulty_button.pack(side="left", padx=5)
        
        self.high_scores_button = ttk.Button(self.menu_frame,
                                           text="🏆 High Scores",
                                           style="Custom.TButton",
                                           command=self.show_high_scores)
        self.high_scores_button.pack(side="left", padx=5)
        
        # Bind enter key to guess
        self.guess_entry.bind('<Return>', lambda e: self.make_guess())
        
        # Start in a ready state
        self.start_new_game()
        
    def update_status(self):
        self.difficulty_label.config(text=f"🎯 Difficulty: {self.difficulty.capitalize()}")
        self.attempts_label.config(text=f"🎲 Attempts: {self.attempts}/{self.max_attempts}")
        self.hints_label.config(text=f"💡 Hints: {self.hints_remaining}")
        
    def update_progress(self):
        progress = (self.attempts / self.max_attempts) * 100
        self.progress_var.set(progress)
        
    def update_timer(self):
        if self.timer_running:
            self.time_elapsed = time.time() - self.start_time
            minutes = int(self.time_elapsed // 60)
            seconds = int(self.time_elapsed % 60)
            self.timer_label.config(text=f"⏱️ Time: {minutes}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
            
    def animate_message(self, message, color=None):
        if color:
            self.message_label.config(fg=color)
        self.message_label.config(text=message)
        
    def calculate_score(self):
        base_score = 1000
        time_penalty = int(self.time_elapsed * 2)
        hint_penalty = (1 - self.hints_remaining) * 100  # Penalty for hints used
        attempt_penalty = self.attempts * 50
        
        score = base_score - time_penalty - hint_penalty - attempt_penalty
        return max(0, score)
        
    def update_player_stats(self):
        self.player_profile['games_played'] += 1
        self.player_profile['total_score'] += self.score
        if self.time_elapsed < self.player_profile['best_time']:
            self.player_profile['best_time'] = self.time_elapsed
        self.save_profile_data()
        
    def show_difficulty_menu(self):
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("Select Difficulty")
        difficulty_window.geometry("400x300")
        difficulty_window.configure(bg=self.colors['bg'])
        
        tk.Label(difficulty_window,
                text="Select Difficulty",
                font=("Helvetica", 16, "bold"),
                bg=self.colors['bg'],
                fg=self.colors['primary']).pack(pady=20)
                
        difficulties = [
            ("Easy", "1-20, 7 attempts"),
            ("Medium", "1-20, 5 attempts"),
            ("Hard", "1-20, 3 attempts")
        ]
        
        for diff, desc in difficulties:
            frame = tk.Frame(difficulty_window, bg=self.colors['bg'])
            frame.pack(fill="x", pady=5)
            
            ttk.Button(frame,
                      text=f"{diff}\n{desc}",
                      style="Custom.TButton",
                      command=lambda d=diff.lower(): self.set_difficulty(d, difficulty_window)).pack()
                      
    def set_difficulty(self, difficulty, window):
        self.difficulty = difficulty
        if difficulty == "easy":
            self.max_attempts = 7
        elif difficulty == "medium":
            self.max_attempts = 5
        else:
            self.max_attempts = 3
        window.destroy()
        self.start_new_game()
        
    def show_high_scores(self):
        high_scores_window = tk.Toplevel(self.root)
        high_scores_window.title("High Scores")
        high_scores_window.geometry("400x300")
        high_scores_window.configure(bg=self.colors['bg'])
        
        tk.Label(high_scores_window,
                text="High Scores",
                font=("Helvetica", 16, "bold"),
                bg=self.colors['bg'],
                fg=self.colors['primary']).pack(pady=20)
                
        # Display high scores for difficulties
        for difficulty in ['easy', 'medium', 'hard']:
            if difficulty in self.high_scores:
                score = self.high_scores[difficulty]
                frame = tk.Frame(high_scores_window, bg=self.colors['bg'])
                frame.pack(fill="x", pady=5)
                
                tk.Label(frame,
                        text=f"{difficulty.capitalize()}:",
                        font=("Helvetica", 12),
                        bg=self.colors['bg'],
                        fg=self.colors['text']).pack(side="left", padx=10)
                        
                tk.Label(frame,
                        text=str(score),
                        font=("Helvetica", 12),
                        bg=self.colors['bg'],
                        fg=self.colors['primary']).pack(side="right", padx=10)
                        
    def change_theme(self, theme):
        self.current_theme = theme
        self.colors = self.themes[theme]
        self.root.configure(bg=self.colors['bg'])
        self.main_container.configure(bg=self.colors['bg'])
        self.game_area.configure(bg=self.colors['bg'])
        self.game_card.configure(bg=self.colors['card'])
        self.top_bar.configure(bg=self.colors['card'])
        self.profile_frame.configure(bg=self.colors['card'])
        self.status_frame.configure(bg=self.colors['card'])
        self.status_labels_frame.configure(bg=self.colors['card'])
        self.message_frame.configure(bg=self.colors['card'])
        self.input_frame.configure(bg=self.colors['card'])
        self.buttons_frame.configure(bg=self.colors['card'])
        self.menu_frame.configure(bg=self.colors['bg'])
        
        # Update text colors
        self.title_label.configure(bg=self.colors['bg'], fg=self.colors['primary'])
        self.message_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.avatar_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.player_name_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.difficulty_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.attempts_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.timer_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        self.hints_label.configure(bg=self.colors['card'], fg=self.colors['text'])
        
        # Update entry colors
        self.guess_entry.configure(bg=self.colors['bg'], fg=self.colors['text'])
        
    def get_hint(self):
        if not self.game_active:
            return
            
        if self.hints_remaining > 0:
            self.hints_remaining -= 1
            hint = self.get_dynamic_hint()
            self.animate_message(hint, self.colors['accent'])
            self.update_status()
        else:
            self.animate_message("No hints remaining!", self.colors['error'])
            
    def get_dynamic_hint(self):
        if self.difficulty == 'easy':
            # Range-based hint
            range_size = 5
            lower = ((self.secret_number - 1) // range_size) * range_size + 1
            upper = lower + range_size - 1
            return f"The number is between {lower} and {upper}"
        elif self.difficulty == 'medium':
            # Parity-based hint
            return f"The number is {'even' if self.secret_number % 2 == 0 else 'odd'}"
        else:
            # Math-based hint for hard difficulty
            hints = [
                f"The number is {'divisible' if self.secret_number % 3 == 0 else 'not divisible'} by 3",
                f"The number is {'greater' if self.secret_number > 10 else 'less than or equal'} to 10",
                f"The sum of its digits is {sum(int(d) for d in str(self.secret_number))}"
            ]
            return random.choice(hints)
            
    def make_guess(self):
        if not self.game_active:
            return
            
        try:
            guess = int(self.guess_entry.get())
            if guess < 1 or guess > 20:
                self.animate_message("Please enter a number between 1 and 20!", self.colors['error'])
                return
                
            self.attempts += 1
            self.last_guess = guess
            self.guess_history.append(guess)
            self.update_status()
            self.update_progress()
            
            guess_time = time.time() - self.start_time
            
            if guess == self.secret_number:
                self.game_active = False
                self.timer_running = False
                self.score = self.calculate_score()
                self.update_player_stats()
                self.update_stats(True, guess_time)
                
                if self.current_mode == 'survival':
                    self.survival_score += self.score
                    message = f"🎉 Correct! Score: {self.score}\nTotal Survival Score: {self.survival_score}"
                else:
                    message = f"🎉 Congratulations! You guessed the number!\n\nIt took you {self.attempts} attempts\nYour score: {self.score}"
                    
                if self.score > self.high_scores[self.difficulty]:
                    message += "\n\n🏆 New high score!"
                    self.high_scores[self.difficulty] = self.score
                    self.save_high_scores()
                    
                self.animate_message(message, self.colors['success'])
                self.update_achievements()
            else:
                self.update_stats(False, guess_time)
                if guess < self.secret_number:
                    self.animate_message("📈 Too low! Try again.", self.colors['warning'])
                else:
                    self.animate_message("📉 Too high! Try again.", self.colors['warning'])
                    
            if self.attempts >= self.max_attempts and self.game_active:
                self.game_active = False
                self.timer_running = False
                self.animate_message(f"Game Over! The number was {self.secret_number}", self.colors['error'])
                
            self.guess_entry.delete(0, tk.END)
            
        except ValueError:
            self.animate_message("Please enter a valid number!", self.colors['error'])
            
    def start_game_round(self):
        """Starts a new round of the game after the user clicks Start."""
        mode = self.game_modes[self.current_mode]
        self.secret_number = random.randint(*mode['range'])
        self.attempts = 0
        self.hints_remaining = 1
        self.game_active = True
        self.start_time = time.time()
        self.time_elapsed = 0
        self.timer_running = True
        self.guess_history = []
        self.update_status()
        self.update_progress()
        self.animate_message(f"I'm thinking of a number between {mode['range'][0]} and {mode['range'][1]}")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()
        self.update_timer()
        
        # Hide start button, show input and buttons
        self.start_button.pack_forget()
        self.message_frame.pack(pady=(50, 10), anchor='center')
        self.input_frame.pack(pady=(0, 10), anchor='center')
        self.buttons_frame.pack(anchor='center')
        
    def start_new_game(self):
        """Resets the UI to the initial state with the start button."""
        self.game_active = False
        self.timer_running = False
        self.attempts = 0
        self.hints_remaining = 1
        self.time_elapsed = 0
        self.update_status()
        self.update_progress()
        self.timer_label.config(text="⏱️ Time: 0:00")
        self.animate_message("Click Start Game to begin!")
        
        # Show start button, hide input and buttons
        self.input_frame.pack_forget()
        self.buttons_frame.pack_forget()
        self.message_frame.pack(pady=(50, 10), anchor='center')
        self.start_button.pack(pady=20, anchor='center')
        
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])
        
        # Theme selection
        theme_frame = tk.Frame(settings_window, bg=self.colors['bg'])
        theme_frame.pack(fill="x", pady=10)
        
        tk.Label(theme_frame,
                text="Theme",
                font=("Helvetica", 12, "bold"),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(pady=5)
                
        theme_var = tk.StringVar(value=self.current_theme)
        
        for theme in ['light', 'dark']:
            ttk.Radiobutton(theme_frame,
                           text=theme.capitalize(),
                           variable=theme_var,
                           value=theme,
                           command=lambda t=theme: self.change_theme(t)).pack()
                           
        # Profile settings
        profile_frame = tk.Frame(settings_window, bg=self.colors['bg'])
        profile_frame.pack(fill="x", pady=10)
        
        tk.Label(profile_frame,
                text="Profile",
                font=("Helvetica", 12, "bold"),
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(pady=5)
                
        name_frame = tk.Frame(profile_frame, bg=self.colors['bg'])
        name_frame.pack(fill="x", pady=5)
        
        tk.Label(name_frame,
                text="Name:",
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(side="left")
                
        name_entry = tk.Entry(name_frame)
        name_entry.insert(0, self.player_profile['name'])
        name_entry.pack(side="left", padx=5)
        
        # Avatar selection
        avatar_frame = tk.Frame(profile_frame, bg=self.colors['bg'])
        avatar_frame.pack(fill="x", pady=5)
        
        tk.Label(avatar_frame,
                text="Avatar:",
                bg=self.colors['bg'],
                fg=self.colors['text']).pack(side="left")
                
        avatars = ['👤', '🎮', '🎲', '🎯', '🎪', '🎨']
        avatar_var = tk.StringVar(value=self.player_profile['avatar'])
        
        for avatar in avatars:
            ttk.Radiobutton(avatar_frame,
                           text=avatar,
                           variable=avatar_var,
                           value=avatar,
                           command=lambda a=avatar: self.change_avatar(a)).pack(side="left", padx=5)
                           
        ttk.Button(profile_frame,
                  text="Save Profile",
                  command=lambda: self.save_profile(name_entry.get())).pack(pady=5)
                  
    def change_avatar(self, avatar):
        self.player_profile['avatar'] = avatar
        self.avatar_label.config(text=avatar)
        self.save_profile_data()
        
    def save_profile(self, name):
        self.player_profile['name'] = name
        self.player_name_label.config(text=name)
        self.save_profile_data()
        
    def update_stats(self, guess_correct=False, guess_time=0):
        stats = self.player_profile['stats']
        stats['total_guesses'] += 1
        if guess_correct:
            stats['correct_guesses'] += 1
        if stats['total_guesses'] > 0:  # Prevent division by zero
            stats['accuracy'] = (stats['correct_guesses'] / stats['total_guesses']) * 100
        # Update average guess time
        if stats['total_guesses'] == 1:
            stats['avg_guess_time'] = guess_time
        else:
            stats['avg_guess_time'] = ((stats['avg_guess_time'] * (stats['total_guesses'] - 1)) + guess_time) / stats['total_guesses']
        self.save_profile_data()
        
    def update_achievements(self):
        if not self.achievements['first_win']['unlocked'] and self.score > 0:
            self.unlock_achievement('first_win')
            
        self.winning_streak += 1
        if self.winning_streak >= 3 and not self.achievements['winning_streak']['unlocked']:
            self.unlock_achievement('winning_streak')
            
        if self.attempts == 1 and not self.achievements['perfect_game']['unlocked']:
            self.unlock_achievement('perfect_game')
            
        if self.time_elapsed < 30 and not self.achievements['speed_demon']['unlocked']:
            self.unlock_achievement('speed_demon')
            
        self.games_played += 1
        if self.games_played >= 10 and not self.achievements['master_guesser']['unlocked']:
            self.unlock_achievement('master_guesser')
            
    def unlock_achievement(self, achievement_id):
        self.achievements[achievement_id]['unlocked'] = True
        if achievement_id not in self.player_profile['achievements']:
            self.player_profile['achievements'].append(achievement_id)
        self.show_achievement_notification(achievement_id)
        self.save_profile_data()
        
    def show_achievement_notification(self, achievement_id):
        achievement = self.achievements[achievement_id]
        notification = tk.Toplevel(self.root)
        notification.title("Achievement Unlocked!")
        notification.geometry("300x150")
        notification.configure(bg=self.colors['card'])
        
        tk.Label(notification,
                text="🏆 Achievement Unlocked!",
                font=("Helvetica", 16, "bold"),
                bg=self.colors['card'],
                fg=self.colors['primary']).pack(pady=10)
                
        tk.Label(notification,
                text=achievement['name'],
                font=("Helvetica", 12),
                bg=self.colors['card'],
                fg=self.colors['text']).pack()
                
        tk.Label(notification,
                text=achievement['description'],
                font=("Helvetica", 10),
                bg=self.colors['card'],
                fg=self.colors['text']).pack()
                
        ttk.Button(notification,
                  text="OK",
                  command=notification.destroy).pack(pady=10)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        print("Starting Number Guessing Game...")
        game = NumberGuessingGame()
        print("Running main loop...")
        game.run()
        print("Game ended normally")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Traceback:", file=sys.stderr)
        traceback.print_exc() 