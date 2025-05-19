import random
import tkinter as tk
from tkinter import ttk
import time
import json
import os
import math
from datetime import datetime
import colorsys
import warnings
from tkinter import messagebox
from math import sin, pi
import uuid

# Suppress all warnings
warnings.filterwarnings("ignore")

# Game history file
HISTORY_FILE = "game_history.json"

# Flag for visualization support - check environment variable
USE_VISUALIZATION = False
if os.environ.get("USE_VISUALIZATION", "0") != "0":
    # Only attempt to import visualization libraries if explicitly enabled
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        USE_VISUALIZATION = True
        print("Visualization enabled")
    except ImportError:
        print("Visualization libraries not available. Running with simplified graphics.")
else:
    print("Visualization disabled by environment variable.")

# Try to import visualization libraries anyway for optional use
if not USE_VISUALIZATION:
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        # Don't set USE_VISUALIZATION to True here - we'll still use the text-based charts
    except ImportError:
        pass

import uuid
from math import sin, pi

class GradientFrame(tk.Canvas):
    """A frame with gradient background"""
    def __init__(self, parent, from_color, to_color, width=None, height=None, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self._from_color = from_color
        self._to_color = to_color
        self._width = width or parent.winfo_screenwidth()
        self._height = height or parent.winfo_screenheight()
        self.configure(width=self._width, height=self._height)
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        """Draw the gradient background"""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Parse colors
        r1, g1, b1 = self.winfo_rgb(self._from_color)
        r2, g2, b2 = self.winfo_rgb(self._to_color)
        r_ratio = float(r2-r1) / height
        g_ratio = float(g2-g1) / height
        b_ratio = float(b2-b1) / height

        for y in range(height):
            r = int(r1 + (r_ratio * y)) >> 8
            g = int(g1 + (g_ratio * y)) >> 8
            b = int(b1 + (b_ratio * y)) >> 8
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, y, width, y, tags=("gradient",), fill=color)
        self.lower("gradient")

class PulsatingText(tk.Label):
    """Text with pulsating animation"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._pulsating = False
        self._original_font = kwargs.get('font', ('Helvetica', 12))
        self._pulse_step = 0
        self._original_fg = self.cget("fg")
        self._pulse()
        
    def start_pulsating(self):
        if not self._pulsating:
            self._pulsating = True
            self._pulse()
            
    def stop_pulsating(self):
        self._pulsating = False
        
    def _pulse(self):
        if not self._pulsating:
            return
        
        # Get font properties
        if isinstance(self._original_font, str):
            # Try to parse font string like "Helvetica 12"
            parts = self._original_font.split()
            if len(parts) >= 2 and parts[-1].isdigit():
                font_family = ' '.join(parts[:-1])
                font_size = int(parts[-1])
            else:
                # Default if can't parse
                font_family = "Helvetica"
                font_size = 12
        else:
            # Handle tuple/list format like ("Helvetica", 12)
            if len(self._original_font) >= 2:
                font_family = self._original_font[0]
                font_size = self._original_font[1]
            else:
                font_family = "Helvetica"
                font_size = 12
            
        # Calculate size based on sine wave
        self._pulse_step += 0.1
        size_change = int(math.sin(self._pulse_step) * 2)
        new_size = max(font_size + size_change, font_size - 2)
        
        # Update font
        self.configure(font=(font_family, new_size))
        
        # Schedule next pulse
        self.after(50, self._pulse)

class StatsManager:
    """Manage game statistics and history"""
    def __init__(self, history_file=HISTORY_FILE):
        self.history_file = history_file
        self.history = self._load_history()
        
    def _load_history(self):
        """Load game history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    
                # Validate each game entry has required fields
                valid_entries = []
                for game in data:
                    if isinstance(game, dict) and all(key in game for key in ["difficulty", "attempts_used", "won"]):
                        valid_entries.append(game)
                
                return valid_entries
            except:
                return []
        return []
    
    def save_history(self):
        """Save game history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f)
        except:
            print("Error saving game history")
    
    def add_game(self, difficulty, attempts_used, won, number=None):
        """Add a game to history"""
        game = {
            "difficulty": difficulty,
            "attempts_used": attempts_used,
            "won": won,
            "number": number,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(game)
        
        # Keep only recent 20 games
        if len(self.history) > 20:
            self.history = self.history[-20:]
            
        self.save_history()
    
    def get_stats(self):
        """Get overall game statistics"""
        if not self.history:
            return {
                "games_played": 0,
                "games_won": 0,
                "win_percentage": 0,
                "avg_attempts": 0,
                "best_streak": 0,
                "current_streak": 0
            }
        
        games_played = len(self.history)
        games_won = sum(1 for game in self.history if game["won"])
        win_percentage = (games_won / games_played) * 20 if games_played > 0 else 0
        
        attempts_in_wins = [game["attempts_used"] for game in self.history if game["won"]]
        avg_attempts = sum(attempts_in_wins) / len(attempts_in_wins) if attempts_in_wins else 0
        
        # Calculate streaks
        current_streak = 0
        best_streak = 0
        streak = 0
        
        for game in reversed(self.history):
            if game["won"]:
                streak += 1
            else:
                streak = 0
                
            if streak > best_streak:
                best_streak = streak
                
        current_streak = streak
        
        return {
            "games_played": games_played,
            "games_won": games_won,
            "win_percentage": round(win_percentage, 1),
            "avg_attempts": round(avg_attempts, 1),
            "best_streak": best_streak,
            "current_streak": current_streak
        }
        
    def get_difficulty_stats(self, difficulty):
        """Get statistics for a specific difficulty"""
        difficulty_games = [game for game in self.history if game["difficulty"] == difficulty]
        
        if not difficulty_games:
            return {
                "games_played": 0,
                "games_won": 0,
                "win_percentage": 0,
                "avg_attempts": 0
            }
            
        games_played = len(difficulty_games)
        games_won = sum(1 for game in difficulty_games if game["won"])
        win_percentage = (games_won / games_played) * 20 if games_played > 0 else 0
        
        attempts_in_wins = [game["attempts_used"] for game in difficulty_games if game["won"]]
        avg_attempts = sum(attempts_in_wins) / len(attempts_in_wins) if attempts_in_wins else 0
        
        return {
            "games_played": games_played,
            "games_won": games_won,
            "win_percentage": round(win_percentage, 1),
            "avg_attempts": round(avg_attempts, 1)
        }

class Timer:
    """A simple timer class to track elapsed time."""
    
    def __init__(self):
        self.start_time = 0
        self.is_running = False
        
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.is_running = True
        
    def stop(self):
        """Stop the timer."""
        self.is_running = False
        
    def get_elapsed_time(self):
        """Get the elapsed time in seconds."""
        if not self.is_running:
            return 0
        return int(time.time() - self.start_time)
    
    def get_formatted_time(self):
        """Get the elapsed time formatted as MM:SS."""
        seconds = self.get_elapsed_time()
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def reset(self):
        """Reset the timer."""
        self.start_time = time.time()
        
    def get_time(self):
        """Get the elapsed time in seconds as a float."""
        if not self.is_running:
            return 0
        return time.time() - self.start_time

class EnhancedNumberGame:
    """Enhanced number guessing game with improved UI and animations"""
    DIFFICULTY_LEVELS = {
        "easy": {"range": (1, 50), "attempts": 10},
        "medium": {"range": (1, 20), "attempts": 7},
        "hard": {"range": (1, 250), "attempts": 5}
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Guess the Number")
        self.stats_manager = StatsManager()
        self.current_game_id = None
        self.level = 1
        self.difficulty = "easy"
        self.min_value = 1
        self.max_value = 50
        self.max_attempts = 10
        self.attempts_left = self.max_attempts
        self.attempts = 0
        self.history = []
        self.is_game_active = False
        self.target_number = random.randint(1, 50)  # Default for easy mode
        self.difficulty_var = tk.StringVar(value="easy")

        # Center window
        window_width = 900
        window_height = 650
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create a modern theme
        style = ttk.Style()
        style.configure("TFrame", background="#2c3e50")
        style.configure("TButton", 
                        background="#3498db", 
                        foreground="#ffffff", 
                        font=("Helvetica", 12, "bold"),
                        padding=10,
                        relief="flat")
        style.map("TButton",
                 background=[("active", "#2980b9")])
        style.configure("TLabel", 
                       background="#2c3e50", 
                       foreground="#ecf0f1", 
                       font=("Helvetica", 12))
        style.configure("Title.TLabel", 
                       background="#2c3e50", 
                       foreground="#ecf0f1", 
                       font=("Helvetica", 24, "bold"))
        style.configure("Game.TLabel", 
                       background="#2c3e50", 
                       foreground="#ecf0f1", 
                       font=("Helvetica", 14))
        style.configure("Info.TLabel", 
                       background="#2c3e50", 
                       foreground="#e74c3c", 
                       font=("Helvetica", 12, "italic"))
        style.configure("History.TLabel", 
                       background="#34495e", 
                       foreground="#ecf0f1", 
                       font=("Helvetica", 11))
        
        # Main container
        self.main_frame = GradientFrame(root, from_color="#2c3e50", to_color="#1a2530")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create frames for home and game
        self.home_frame = ttk.Frame(self.main_frame)
        self.game_frame = ttk.Frame(self.main_frame)
        
        # Set up home page only initially, we'll set up game page when needed
        self._setup_home_page()
        
        # Show home page initially
        self.show_home_page()
        
    def _setup_home_page(self):
        """Set up the home page interface"""
        # Title frame
        title_frame = ttk.Frame(self.home_frame)
        title_frame.pack(fill="x", pady=(30, 20))
        
        # Game title
        title_label = PulsatingText(
            title_frame,
            text="GUESS THE NUMBER",
            font=("Helvetica", 28, "bold"),
            foreground="#e74c3c",
            background="#2c3e50"
        )
        title_label.pack(pady=10)
        title_label.start_pulsating()
        
        # Subtitle
        subtitle_label = ttk.Label(
            title_frame,
            text="Test your guessing skills!",
            style="Game.TLabel"
        )
        subtitle_label.pack(pady=5)
        
        # Levels frame
        levels_frame = ttk.Frame(self.home_frame)
        levels_frame.pack(pady=30)
        
        # Level buttons
        ttk.Label(
            levels_frame,
            text="SELECT DIFFICULTY LEVEL:",
            font=("Helvetica", 14, "bold"),
            foreground="#3498db",
            background="#2c3e50"
        ).pack(pady=(0, 20))
        
        # Create level buttons
        button_frame = ttk.Frame(levels_frame)
        button_frame.pack()
        
        for level in range(1, 6):
            level_btn = ttk.Button(
                button_frame,
                text=f"LEVEL {level}",
                command=lambda l=level: self.start_game(l),
                style="TButton"
            )
            level_btn.pack(side="left", padx=10, pady=10)
        
        # Statistics frame
        stats_frame = ttk.Frame(self.home_frame)
        stats_frame.pack(fill="both", expand=True, pady=20)
        
        # Stats title
        ttk.Label(
            stats_frame,
            text="YOUR STATISTICS",
            font=("Helvetica", 16, "bold"),
            foreground="#3498db",
            background="#2c3e50"
        ).pack(pady=(0, 10))
        
        # Stats display
        self.stats_display = ttk.Frame(stats_frame)
        self.stats_display.pack(fill="both", expand=True, padx=20)
        
        # Update stats display
        self._update_stats_display()
        
        # Instructions
        instructions_frame = ttk.Frame(self.home_frame)
        instructions_frame.pack(fill="x", pady=20)
        
        ttk.Label(
            instructions_frame,
            text="HOW TO PLAY",
            font=("Helvetica", 14, "bold"),
            foreground="#3498db",
            background="#2c3e50"
        ).pack(pady=(0, 5))
        
        instructions_text = """
        1. Select a difficulty level to start
        2. Higher levels have larger number ranges and fewer attempts
        3. Enter your guess and press ENTER or click GUESS
        4. Follow the hints to find the correct number
        5. Try to solve with as few attempts as possible!
        """
        
        ttk.Label(
            instructions_frame,
            text=instructions_text,
            style="Game.TLabel",
            justify="left"
        ).pack(padx=40, pady=5)

    def _update_stats_display(self):
        """Update statistics display on home page with visual charts"""
        # Clear existing stats
        for widget in self.stats_display.winfo_children():
            widget.destroy()
        
        # Get overall stats
        stats = self.stats_manager.get_stats()
        
        # Create main stats container with tabs
        tab_frame = ttk.Frame(self.stats_display)
        tab_frame.pack(fill="both", expand=True, pady=10)
        
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(tab_frame)
        notebook.pack(fill="both", expand=True)
        
        # === Summary Tab ===
        summary_tab = ttk.Frame(notebook)
        notebook.add(summary_tab, text="Summary")
        
        # Create stats grid
        overall_frame = ttk.Frame(summary_tab)
        overall_frame.pack(fill="x", pady=10)
        
        # Stats columns
        stat_columns = [
            ("Games Played", stats["games_played"]),
            ("Games Won", stats["games_won"]),
            ("Win Rate", f"{stats['win_percentage']}%"),
            ("Avg Attempts", stats["avg_attempts"]),
            ("Best Streak", stats["best_streak"]),
            ("Current Streak", stats["current_streak"])
        ]
        
        # Create stat boxes
        for i, (label, value) in enumerate(stat_columns):
            stat_frame = ttk.Frame(overall_frame, style="TFrame")
            stat_frame.grid(row=i//3, column=i%3, padx=10, pady=5, sticky="nsew")
            
            ttk.Label(
                stat_frame,
                text=label,
                font=("Helvetica", 10),
                foreground="#bdc3c7",
                background="#2c3e50"
            ).pack(pady=(5, 0))
            
            ttk.Label(
                stat_frame,
                text=str(value),
                font=("Helvetica", 16, "bold"),
                foreground="#e74c3c",
                background="#2c3e50"
            ).pack(pady=(0, 5))
        
        # Configure grid
        for i in range(3):
            overall_frame.columnconfigure(i, weight=1)
        
        # === Charts Tab ===
        charts_tab = ttk.Frame(notebook)
        notebook.add(charts_tab, text="Performance")
        
        # Create figures only if we have game history
        if self.stats_manager.history:
            # Create a frame to hold charts
            charts_frame = ttk.Frame(charts_tab)
            charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            if USE_VISUALIZATION:
                # === Win Rate by Difficulty Chart ===
                # Set up left chart - Win rate by difficulty
                try:
                    fig1 = Figure(figsize=(4, 3), dpi=20)
                    ax1 = fig1.add_subplot(111)
                    
                    # Get data for each difficulty
                    diff_labels = ['Easy', 'Medium', 'Hard']
                    win_rates = []
                    
                    for difficulty in ['easy', 'medium', 'hard']:
                        diff_stats = self.stats_manager.get_difficulty_stats(difficulty)
                        win_rates.append(diff_stats['win_percentage'])
                    
                    # Create bar chart
                    bars = ax1.bar(diff_labels, win_rates, color=['#4caf50', '#ff9800', '#f44336'])
                    
                    # Add labels and title
                    ax1.set_ylabel('Win Rate (%)', color='white')
                    ax1.set_title('Win Rate by Difficulty', color='white')
                    ax1.set_ylim(0, 20)
                    
                    # Set colors for better visibility
                    ax1.set_facecolor('#2c3e50')
                    fig1.patch.set_facecolor('#2c3e50')
                    ax1.tick_params(colors='white')
                    ax1.spines['bottom'].set_color('white')
                    ax1.spines['top'].set_color('white')
                    ax1.spines['left'].set_color('white')
                    ax1.spines['right'].set_color('white')
                    
                    # Add values above bars
                    for bar in bars:
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                                f'{int(height)}%', ha='center', va='bottom', color='white')
                    
                    # Create canvas for the chart
                    canvas1 = FigureCanvasTkAgg(fig1, charts_frame)
                    canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                    
                    # === Attempts Distribution Chart ===
                    fig2 = Figure(figsize=(4, 3), dpi=20)
                    ax2 = fig2.add_subplot(111)
                    
                    # Filter to only won games to analyze attempts
                    won_games = [game for game in self.stats_manager.history if game['won']]
                    if won_games:
                        # Prepare data
                        attempts_data = {}
                        for game in won_games:
                            attempts = game['attempts_used']
                            if attempts in attempts_data:
                                attempts_data[attempts] += 1
                            else:
                                attempts_data[attempts] = 1
                        
                        # Convert to lists for plotting
                        attempts_counts = list(attempts_data.keys())
                        game_counts = list(attempts_data.values())
                        
                        # Sort by attempts
                        sorted_data = sorted(zip(attempts_counts, game_counts))
                        if sorted_data:
                            attempts_counts, game_counts = zip(*sorted_data)
                            
                            # Create chart
                            ax2.plot(attempts_counts, game_counts, 'o-', color='#3498db', linewidth=2, 
                                    markersize=8, markerfacecolor='#2ecc71')
                            
                            # Add labels
                            ax2.set_xlabel('Attempts Used', color='white')
                            ax2.set_ylabel('Number of Games', color='white')
                            ax2.set_title('Attempts Distribution in Won Games', color='white')
                            
                            # Set integer ticks for x-axis
                            ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
                            
                            # Set colors
                            ax2.set_facecolor('#2c3e50')
                            fig2.patch.set_facecolor('#2c3e50')
                            ax2.tick_params(colors='white')
                            ax2.spines['bottom'].set_color('white')
                            ax2.spines['top'].set_color('white')
                            ax2.spines['left'].set_color('white')
                            ax2.spines['right'].set_color('white')
                            
                            # Add data labels
                            for x, y in zip(attempts_counts, game_counts):
                                ax2.text(x, y + 0.1, str(y), ha='center', va='bottom', color='white')
                    else:
                        # No won games yet
                        ax2.text(0.5, 0.5, "No won games yet", 
                                ha='center', va='center', color='white',
                                transform=ax2.transAxes, fontsize=12)
                        ax2.set_facecolor('#2c3e50')
                        fig2.patch.set_facecolor('#2c3e50')
                    
                    # Create canvas for the chart
                    canvas2 = FigureCanvasTkAgg(fig2, charts_frame)
                    canvas2.get_tk_widget().grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                    
                    # Configure grid
                    charts_frame.columnconfigure(0, weight=1)
                    charts_frame.columnconfigure(1, weight=1)
                    charts_frame.rowconfigure(0, weight=1)
                except Exception as e:
                    # Fallback to text-based display if visualization fails
                    self._create_text_based_charts(charts_frame)
            else:
                # Fallback to text-based display if visualization not available
                self._create_text_based_charts(charts_frame)
        else:
            # No game history yet
            no_data_label = ttk.Label(
                charts_tab,
                text="No game data available yet. Play some games first!",
                font=("Helvetica", 14, "italic"),
                foreground="#bdc3c7",
                background="#2c3e50",
                justify="center"
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # === Table Tab ===
        table_tab = ttk.Frame(notebook)
        notebook.add(table_tab, text="Details")
        
        # Add difficulty-specific stats
        difficulties_frame = ttk.Frame(table_tab)
        difficulties_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(
            difficulties_frame,
            text="STATS BY DIFFICULTY",
            font=("Helvetica", 12, "bold"),
            foreground="#3498db",
            background="#2c3e50"
        ).pack(pady=(10, 5))
        
        # Stats table
        table_frame = ttk.Frame(difficulties_frame)
        table_frame.pack(fill="x", padx=20, pady=5)
        
        # Table headers
        headers = ["Level", "Games", "Won", "Win Rate", "Avg Attempts"]
        for i, header in enumerate(headers):
            ttk.Label(
                table_frame,
                text=header,
                font=("Helvetica", 11, "bold"),
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Add data for each difficulty
        difficulties = ["easy", "medium", "hard"]
        difficulty_names = ["Easy", "Medium", "Hard"]
        
        for i, (diff_id, diff_name) in enumerate(zip(difficulties, difficulty_names)):
            level_stats = self.stats_manager.get_difficulty_stats(diff_id)
            
            ttk.Label(
                table_frame,
                text=diff_name,
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
            
            ttk.Label(
                table_frame,
                text=str(level_stats["games_played"]),
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=i+1, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Label(
                table_frame,
                text=str(level_stats["games_won"]),
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=i+1, column=2, padx=5, pady=2, sticky="w")
            
            ttk.Label(
                table_frame,
                text=f"{level_stats['win_percentage']}%",
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=i+1, column=3, padx=5, pady=2, sticky="w")
            
            ttk.Label(
                table_frame,
                text=str(level_stats["avg_attempts"]),
                foreground="#ecf0f1",
                background="#2c3e50"
            ).grid(row=i+1, column=4, padx=5, pady=2, sticky="w")
        
        # Recent games history
        if self.stats_manager.history:
            history_label = ttk.Label(
                table_tab,
                text="RECENT GAMES",
                font=("Helvetica", 12, "bold"),
                foreground="#3498db",
                background="#2c3e50"
            )
            history_label.pack(pady=(20, 5))
            
            # Create history table
            history_frame = ttk.Frame(table_tab)
            history_frame.pack(fill="both", expand=True, padx=20, pady=5)
            
            # History headers
            history_headers = ["Date", "Difficulty", "Number", "Attempts", "Result"]
            for i, header in enumerate(history_headers):
                ttk.Label(
                    history_frame,
                    text=header,
                    font=("Helvetica", 10, "bold"),
                    foreground="#ecf0f1",
                    background="#2c3e50"
                ).grid(row=0, column=i, padx=5, pady=5, sticky="w")
            
            # Show last 10 games
            recent_games = self.stats_manager.history[-10:] if len(self.stats_manager.history) > 10 else self.stats_manager.history
            recent_games.reverse()  # Show most recent first
            
            for i, game in enumerate(recent_games):
                # Date
                ttk.Label(
                    history_frame,
                    text=game.get("date", "Unknown").split()[0],  # Just date part
                    foreground="#ecf0f1",
                    background="#2c3e50",
                    font=("Helvetica", 9)
                ).grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
                
                # Difficulty
                diff_text = game.get("difficulty", "Unknown")
                if isinstance(diff_text, int):
                    diff_text = f"Level {diff_text}"
                elif isinstance(diff_text, str):
                    diff_text = diff_text.capitalize()
                    
                ttk.Label(
                    history_frame,
                    text=diff_text,
                    foreground="#ecf0f1",
                    background="#2c3e50",
                    font=("Helvetica", 9)
                ).grid(row=i+1, column=1, padx=5, pady=2, sticky="w")
                
                # Number
                ttk.Label(
                    history_frame,
                    text=str(game.get("number", "?")),
                    foreground="#ecf0f1",
                    background="#2c3e50",
                    font=("Helvetica", 9)
                ).grid(row=i+1, column=2, padx=5, pady=2, sticky="w")
                
                # Attempts
                ttk.Label(
                    history_frame,
                    text=str(game.get("attempts_used", "?")),
                    foreground="#ecf0f1",
                    background="#2c3e50",
                    font=("Helvetica", 9)
                ).grid(row=i+1, column=3, padx=5, pady=2, sticky="w")
                
                # Result
                result_text = "Won" if game.get("won", False) else "Lost"
                result_color = "#2ecc71" if game.get("won", False) else "#e74c3c"
                
                ttk.Label(
                    history_frame,
                    text=result_text,
                    foreground=result_color,
                    background="#2c3e50",
                    font=("Helvetica", 9, "bold")
                ).grid(row=i+1, column=4, padx=5, pady=2, sticky="w")

    def _create_text_based_charts(self, parent_frame):
        """Create text-based charts as a fallback when matplotlib is not available"""
        # Win Rate by Difficulty (text-based chart)
        win_rate_frame = ttk.Frame(parent_frame, style="TFrame")
        win_rate_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Title
        ttk.Label(
            win_rate_frame,
            text="Win Rate by Difficulty",
            font=("Helvetica", 12, "bold"),
            foreground="#ffffff",
            background="#2c3e50"
        ).pack(pady=(5, 10))
        
        # Get data for each difficulty
        for difficulty, name in zip(['easy', 'medium', 'hard'], ['Easy', 'Medium', 'Hard']):
            diff_stats = self.stats_manager.get_difficulty_stats(difficulty)
            win_rate = diff_stats['win_percentage']
            
            # Create container for this difficulty
            diff_frame = ttk.Frame(win_rate_frame, style="TFrame")
            diff_frame.pack(fill="x", pady=5)
            
            # Label
            ttk.Label(
                diff_frame,
                text=f"{name}:",
                font=("Helvetica", 10),
                foreground="#ffffff",
                background="#2c3e50",
                width=10,
                anchor="e"
            ).pack(side="left", padx=(0, 5))
            
            # Visual bar - simplified version
            bar_length = int((win_rate / 20) * 20)  # Scale to 20 chars max
            bar_frame = ttk.Frame(diff_frame, style="TFrame")
            bar_frame.pack(side="left", fill="x", expand=True)
            
            # Create colored bar
            bar_color = "#4caf50" if difficulty == "easy" else "#ff9800" if difficulty == "medium" else "#f44336"
            bar = tk.Canvas(bar_frame, height=15, width=200, bg="#2c3e50", highlightthickness=0)
            bar.pack(side="left", fill="x")
            bar.create_rectangle(0, 0, bar_length * 10, 15, fill=bar_color, outline="")
            
            # Percentage text
            ttk.Label(
                diff_frame,
                text=f"{win_rate}%",
                font=("Helvetica", 10, "bold"),
                foreground="#ffffff",
                background="#2c3e50"
            ).pack(side="left", padx=5)
        
        # Attempts Distribution (text-based chart)
        attempts_frame = ttk.Frame(parent_frame, style="TFrame")
        attempts_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Title
        ttk.Label(
            attempts_frame,
            text="Attempts Distribution",
            font=("Helvetica", 12, "bold"),
            foreground="#ffffff",
            background="#2c3e50"
        ).pack(pady=(5, 10))
        
        # Filter to only won games to analyze attempts
        won_games = [game for game in self.stats_manager.history if game['won']]
        if won_games:
            # Prepare data
            attempts_data = {}
            for game in won_games:
                attempts = game['attempts_used']
                if attempts in attempts_data:
                    attempts_data[attempts] += 1
                else:
                    attempts_data[attempts] = 1
            
            # Sort by attempts
            sorted_attempts = sorted(attempts_data.items())
            
            # Display data
            for attempts, count in sorted_attempts:
                # Create container for this attempts value
                attempt_frame = ttk.Frame(attempts_frame, style="TFrame")
                attempt_frame.pack(fill="x", pady=3)
                
                # Attempts label
                ttk.Label(
                    attempt_frame,
                    text=f"{attempts} attempts:",
                    font=("Helvetica", 10),
                    foreground="#ffffff",
                    background="#2c3e50",
                    width=12,
                    anchor="e"
                ).pack(side="left", padx=(0, 5))
                
                # Visual bar - simplified version
                max_count = max(attempts_data.values())
                bar_length = int((count / max_count) * 15)  # Scale to 15 chars max
                
                # Create colored bar
                bar = tk.Canvas(attempt_frame, height=12, width=150, bg="#2c3e50", highlightthickness=0)
                bar.pack(side="left", fill="x")
                bar.create_rectangle(0, 0, bar_length * 10, 12, fill="#3498db", outline="")
                
                # Count text
                ttk.Label(
                    attempt_frame,
                    text=f"{count} games",
                    font=("Helvetica", 10),
                    foreground="#ffffff",
                    background="#2c3e50"
                ).pack(side="left", padx=5)
        else:
            ttk.Label(
                attempts_frame,
                text="No won games yet",
                font=("Helvetica", 12, "italic"),
                foreground="#bdc3c7",
                background="#2c3e50"
            ).pack(pady=30)
        
        # Configure grid
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.rowconfigure(0, weight=1)

    def generate_number(self, level):
        """Generate a random number based on the difficulty level"""
        max_number = 20 * level
        self.target_number = random.randint(1, max_number)
        
    def check_guess(self):
        """Check the user's guess"""
        if not self.is_game_active:
            return
            
        # Get user guess
        try:
            guess = int(self.guess_var.get())
        except ValueError:
            self.feedback_var.set("Please enter a valid number!")
            self.guess_var.set("")
            return
            
        # Clear input
        self.guess_var.set("")
        
        # Increment attempts
        self.attempts += 1
        self.attempts_var.set(f"Attempts: {self.attempts}/{self.max_attempts}")
        
        # Add to history
        time_str = self.timer.get_formatted_time()
        self.history.append(guess)
        
        # Determine result and update feedback
        if guess < self.target_number:
            result = "TOO LOW"
            color = "#3498db"  # Blue
            self.feedback_var.set("Too low! Try a higher number.")
        elif guess > self.target_number:
            result = "TOO HIGH"
            color = "#e74c3c"  # Red
            self.feedback_var.set("Too high! Try a lower number.")
        else:
            result = "CORRECT!"
            color = "#2ecc71"  # Green
            self.feedback_var.set("Correct! You found the number!")
        
        # Add to history listbox
        entry = f"Guess #{self.attempts}: {guess} - {result}"
        self.history_listbox.insert(0, entry)
        self.history_listbox.itemconfig(0, {'fg': color})
        
        # Check if guess is correct
        if guess == self.target_number:
            self.game_won()
            return
            
        # Check if out of attempts
        if self.attempts >= self.max_attempts:
            self.game_lost()
            return
            
        # Focus back on input
        self.guess_entry.focus()
        
    def game_won(self):
        """Handle game win"""
        self.is_game_active = False
        self.timer.stop()
        time_taken = self.timer.get_time()
        
        # Update message with pulsating effect
        self.feedback_var.set(f"Congratulations! You found the number: {self.target_number}")
        
        # Display success information
        attempts_used = self.max_attempts - self.attempts_left
        self.attempts_var.set(f"You won in {attempts_used} attempts!")
        self.timer_var.set(f"Time: {self.timer.get_formatted_time()}")
        
        # Save game stats
        self.stats_manager.add_game(
            difficulty=self.difficulty,
            attempts_used=attempts_used,
            won=True,
            number=self.target_number
        )
        
        # Disable input and update button text
        self.guess_entry.config(state="disabled")
        self.submit_button.config(text="Game Won!", bg="#2ecc71")

    def game_lost(self):
        """Handle game loss"""
        self.is_game_active = False
        self.timer.stop()
        
        # Update message
        self.feedback_var.set(f"Game Over! The number was: {self.target_number}")
        
        # Display game over information
        self.attempts_var.set(f"Used all {self.max_attempts} attempts")
        
        # Save game stats
        self.stats_manager.add_game(
            difficulty=self.difficulty,
            attempts_used=self.max_attempts,
            won=False,
            number=self.target_number
        )
        
        # Disable input and update button text
        self.guess_entry.config(state="disabled")
        self.submit_button.config(text="Game Over", bg="#e74c3c")

    def start_game(self, level=1):
        """Start a new game"""
        # Hide home page and show game page
        self.home_frame.pack_forget()
        
        # Initialize game variables
        self.level = level
        self.difficulty = self.difficulty_var.get() if hasattr(self, 'difficulty_var') else "easy"
        
        # Get difficulty settings
        difficulty_config = self.DIFFICULTY_LEVELS[self.difficulty]
        self.min_value = difficulty_config["range"][0]
        self.max_value = difficulty_config["range"][1]
        self.max_attempts = difficulty_config["attempts"]
        self.attempts = 0
        self.attempts_left = self.max_attempts
        self.history = []
        self.is_game_active = True
        
        # Generate the target number
        self.target_number = random.randint(self.min_value, self.max_value)
        
        # Setup game page (which will initialize all the necessary UI elements)
        self._setup_game_page()
        
        # Generate game ID
        self.current_game_id = str(uuid.uuid4())
        
        # Initialize and start the timer
        self.timer = Timer()
        self.timer.start()
        self._update_timer()

    def show_home_page(self):
        """Show the home page"""
        # Stop the timer if it's running
        if hasattr(self, 'timer'):
            self.timer.stop()
            
        # Hide game page and show home page
        self.game_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Update stats
        self._update_stats_display()
        
    def _setup_game_page(self):
        """Set up the game page with input field, buttons and feedback labels."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create gradient background for game page
        self.game_frame = GradientFrame(self.root, from_color="#1a2a6c", to_color="#b21f1f")
        self.game_frame.pack(fill="both", expand=True)
        
        # Create main content frame
        content_frame = tk.Frame(self.game_frame, bg="#2d3e6d", padx=20, pady=20)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)
        
        # Game title
        title_label = tk.Label(
            content_frame,
            text="GUESS THE NUMBER",
            font=("Helvetica", 20, "bold"),
            fg="#ffffff",
            bg="#2d3e6d"
        )
        title_label.pack(pady=(10, 5))
        
        # Difficulty and range info
        info_frame = tk.Frame(content_frame, bg="#2d3e6d")
        info_frame.pack(pady=10)
        
        difficulty_label = tk.Label(
            info_frame,
            text=f"Difficulty: {self.difficulty.capitalize()}",
            font=("Helvetica", 12, "bold"),
            fg="#3498db",
            bg="#2d3e6d"
        )
        difficulty_label.pack(pady=2)
        
        range_label = tk.Label(
            info_frame,
            text=f"Range: {self.min_value} - {self.max_value}",
            font=("Helvetica", 12),
            fg="#ffffff",
            bg="#2d3e6d"
        )
        range_label.pack(pady=2)
        
        # Input section
        input_frame = tk.Frame(content_frame, bg="#2d3e6d", pady=15)
        input_frame.pack(fill="x")
        
        guess_label = tk.Label(
            input_frame,
            text="Your Guess:",
            font=("Helvetica", 12),
            fg="#ffffff",
            bg="#2d3e6d"
        )
        guess_label.grid(row=0, column=0, padx=10)
        
        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(
            input_frame,
            textvariable=self.guess_var,
            font=("Helvetica", 14),
            width=8,
            justify="center"
        )
        self.guess_entry.grid(row=0, column=1, padx=10)
        self.guess_entry.focus()
        self.guess_entry.bind("<Return>", lambda event: self.check_guess())
        
        self.submit_button = tk.Button(
            input_frame,
            text="SUBMIT",
            font=("Helvetica", 12, "bold"),
            bg="#4caf50",
            fg="white",
            command=self.check_guess
        )
        self.submit_button.grid(row=0, column=2, padx=10)
        
        # Feedback section
        feedback_frame = tk.Frame(content_frame, bg="#2d3e6d", pady=15)
        feedback_frame.pack(fill="x")
        
        self.feedback_var = tk.StringVar()
        self.feedback_var.set("Make your first guess!")
        
        feedback_label = tk.Label(
            feedback_frame,
            textvariable=self.feedback_var,
            font=("Helvetica", 14, "bold"),
            fg="#f1c40f",
            bg="#2d3e6d",
            wraplength=400
        )
        feedback_label.pack()
        
        # Game stats section
        stats_frame = tk.Frame(content_frame, bg="#2d3e6d", pady=5)
        stats_frame.pack(fill="x")
        
        self.attempts_var = tk.StringVar()
        self.attempts_var.set(f"Attempts: {self.attempts}/{self.max_attempts}")
        
        attempts_label = tk.Label(
            stats_frame,
            textvariable=self.attempts_var,
            font=("Helvetica", 12),
            fg="#ffffff",
            bg="#2d3e6d"
        )
        attempts_label.pack(side="left", padx=20)
        
        self.timer_var = tk.StringVar()
        self.timer_var.set("Time: 00:00")
        
        timer_label = tk.Label(
            stats_frame,
            textvariable=self.timer_var,
            font=("Helvetica", 12),
            fg="#ffffff",
            bg="#2d3e6d"
        )
        timer_label.pack(side="right", padx=20)
        
        # History section (side panel)
        history_frame = tk.Frame(self.game_frame, bg="#1e2836", padx=10, pady=10)
        history_frame.place(relx=0.85, rely=0.5, anchor="e", width=200, height=400)
        
        history_title = tk.Label(
            history_frame,
            text="GUESS HISTORY",
            font=("Helvetica", 12, "bold"),
            fg="#3498db",
            bg="#1e2836"
        )
        history_title.pack(pady=(0, 10))
        
        self.history_listbox = tk.Listbox(
            history_frame,
            bg="#2c3e50",
            fg="#ffffff",
            font=("Helvetica", 10),
            relief="flat",
            bd=0,
            selectbackground="#34495e",
            height=15
        )
        self.history_listbox.pack(fill="both", expand=True)
        
        # Buttons at the bottom
        button_frame = tk.Frame(content_frame, bg="#2d3e6d", pady=15)
        button_frame.pack(fill="x")
        
        back_button = tk.Button(
            button_frame,
            text="BACK TO HOME",
            font=("Helvetica", 10),
            bg="#3498db",
            fg="white",
            command=self._setup_welcome_page
        )
        back_button.pack(side="left", padx=10)
        
        quit_button = tk.Button(
            button_frame,
            text="QUIT GAME",
            font=("Helvetica", 10),
            bg="#e74c3c",
            fg="white",
            command=self.root.destroy
        )
        quit_button.pack(side="right", padx=10)
        
        # Start the timer
        self.timer = Timer()
        self.timer.start()
        self._update_timer()

    def _update_timer(self):
        """Update the timer display."""
        if hasattr(self, 'timer') and self.timer.is_running:
            self.timer_var.set(f"Time: {self.timer.get_formatted_time()}")
            self.root.after(1000, self._update_timer)
    
    def _check_guess(self):
        """Check the user's guess against the target number."""
        try:
            guess = int(self.guess_var.get())
            self.attempts += 1
            self.attempts_var.set(f"Attempts: {self.attempts}/{self.max_attempts}")
            
            if guess < self.min_value or guess > self.max_value:
                self.feedback_var.set(f"Please enter a number between {self.min_value} and {self.max_value}!")
                self.guess_entry.delete(0, tk.END)
                return
            
            if guess == self.target_number:
                self.timer.stop()
                self._show_result_page(won=True)
            elif self.attempts >= self.max_attempts:
                self.timer.stop()
                self._show_result_page(won=False)
            elif guess < self.target_number:
                self.feedback_var.set("Too low! Try a higher number.")
                self.guess_entry.delete(0, tk.END)
                self.guess_entry.focus()
            else:  # guess > self.target_number
                self.feedback_var.set("Too high! Try a lower number.")
                self.guess_entry.delete(0, tk.END)
                self.guess_entry.focus()
                
        except ValueError:
            self.feedback_var.set("Please enter a valid number!")
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.focus()

    def _show_result_page(self, won):
        """Show the result page with game statistics."""
        # Clear the game page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create gradient background
        result_frame = GradientFrame(self.root, "#2c3e50", "#4ca1af", width=600, height=500)
        result_frame.pack(fill="both", expand=True)
        
        # Calculate statistics
        time_taken = self.timer.get_formatted_time()
        
        # Create result content frame
        content_frame = tk.Frame(result_frame, bg='#3a4c5f', bd=2, relief="ridge")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=380)
        
        # Result title
        if won:
            result_title = PulsatingText(
                content_frame, 
                text="CONGRATULATIONS!",
                font=("Helvetica", 24, "bold"),
                fg="#ffd700",
                bg='#3a4c5f'
            )
        else:
            result_title = tk.Label(
                content_frame, 
                text="GAME OVER",
                font=("Helvetica", 24, "bold"),
                fg="#ff6b6b",
                bg='#3a4c5f'
            )
        result_title.pack(pady=(30, 20))
        
        # Result message
        if won:
            msg = f"You guessed the number {self.target_number} correctly!"
        else:
            msg = f"The number was {self.target_number}."
        
        result_msg = tk.Label(
            content_frame,
            text=msg,
            font=("Helvetica", 16),
            fg="#ffffff",
            bg='#3a4c5f'
        )
        result_msg.pack(pady=10)
        
        # Statistics
        stats_frame = tk.Frame(content_frame, bg='#3a4c5f')
        stats_frame.pack(pady=20)
        
        stats_list = [
            f"Difficulty: {self.difficulty.capitalize()}",
            f"Number Range: {self.min_value} to {self.max_value}",
            f"Attempts Used: {self.attempts} out of {self.max_attempts}",
            f"Time Taken: {time_taken}"
        ]
        
        for stat in stats_list:
            stat_label = tk.Label(
                stats_frame,
                text=stat,
                font=("Helvetica", 14),
                fg="#ffffff",
                bg='#3a4c5f',
                anchor="w"
            )
            stat_label.pack(pady=5, fill="x")
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg='#3a4c5f')
        button_frame.pack(pady=20)
        
        # Play again button
        play_again_btn = tk.Button(
            button_frame,
            text="PLAY AGAIN",
            font=("Helvetica", 12, "bold"),
            bg="#4ca1af",
            fg="white",
            activebackground="#2c3e50",
            activeforeground="white",
            width=15,
            cursor="hand2",
            command=self._setup_welcome_page
        )
        play_again_btn.pack(side="left", padx=10)
        
        # Quit button
        quit_btn = tk.Button(
            button_frame,
            text="QUIT GAME",
            font=("Helvetica", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            width=15,
            cursor="hand2",
            command=self.root.destroy
        )
        quit_btn.pack(side="left", padx=10)
    
    def _setup_welcome_page(self):
        """Set up the welcome page with game options."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create gradient background
        welcome_frame = GradientFrame(self.root, "#1a2a6c", "#b21f1f", width=600, height=500)
        welcome_frame.pack(fill="both", expand=True)
        
        # Create main content container with rounded corners
        content_frame = tk.Frame(welcome_frame, bg='#2d3e6d', bd=0, relief="ridge", padx=20, pady=20)
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=450)
        
        # Game title with pulsating effect
        game_title = PulsatingText(
            content_frame, 
            text="NUMBER GUESSING GAME",
            font=("Montserrat", 26, "bold"),
            fg="#ffffff",
            bg='#2d3e6d'
        )
        game_title.pack(pady=(20, 10))
        game_title.start_pulsating()
        
        # Game subtitle
        subtitle = tk.Label(
            content_frame,
            text="Challenge your intuition and logical thinking!",
            font=("Helvetica", 14),
            fg="#aed6f1",
            bg='#2d3e6d'
        )
        subtitle.pack(pady=(0, 30))
        
        # Game options section
        options_frame = tk.Frame(content_frame, bg='#2d3e6d', padx=20, pady=20)
        options_frame.pack(fill="x")
        
        # Difficulty selection label
        difficulty_label = tk.Label(
            options_frame,
            text="SELECT DIFFICULTY",
            font=("Helvetica", 16, "bold"),
            fg="#3498db",
            bg='#2d3e6d'
        )
        difficulty_label.pack(pady=(0, 15))
        
        # Difficulty buttons frame
        difficulty_frame = tk.Frame(options_frame, bg='#2d3e6d')
        difficulty_frame.pack()
        
        # Difficulty variable
        self.difficulty_var = tk.StringVar()
        self.difficulty_var.set("easy")  # Default difficulty
        
        # Difficulty buttons with modern styling
        difficulties = [
            ("EASY", "easy", "#4caf50"),
            ("MEDIUM", "medium", "#ff9800"),
            ("HARD", "hard", "#f44336")
        ]
        
        # Command to update description when difficulty changes
        def update_difficulty_description(*args):
            difficulty = self.difficulty_var.get()
            if difficulty == "easy":
                desc = "Range: 1-50, Attempts: 10"
            elif difficulty == "medium":
                desc = "Range: 1-20, Attempts: 7"
            elif difficulty == "hard":
                desc = "Range: 1-250, Attempts: 5"
            self.difficulty_desc_var.set(desc)
            self.start_button.config(state="normal")
        
        for i, (text, value, color) in enumerate(difficulties):
            btn = tk.Button(
                difficulty_frame,
                text=text,
                font=("Helvetica", 12, "bold"),
                fg="white",
                bg=color,
                activebackground=color,
                activeforeground="white",
                width=10,
                height=2,
                cursor="hand2",
                relief="flat",
                command=lambda v=value: [self.difficulty_var.set(v), update_difficulty_description()]
            )
            btn.grid(row=0, column=i, padx=8, pady=10)
        
        # Difficulty description
        self.difficulty_desc_var = tk.StringVar()
        self.difficulty_desc_var.set("Range: 1-50, Attempts: 10")  # Default description
        
        difficulty_desc = tk.Label(
            options_frame,
            textvariable=self.difficulty_desc_var,
            font=("Helvetica", 12, "italic"),
            fg="#bdc3c7",
            bg='#2d3e6d'
        )
        difficulty_desc.pack(pady=10)
        
        # Start Game button
        self.start_button = tk.Button(
            content_frame,
            text="START GAME",
            font=("Helvetica", 16, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            width=15,
            height=1,
            cursor="hand2",
            relief="flat",
            command=self._start_game
        )
        self.start_button.pack(pady=20)
        
        # View Stats button
        stats_button = tk.Button(
            content_frame,
            text="VIEW STATS",
            font=("Helvetica", 12),
            bg="#34495e",
            fg="white",
            activebackground="#2c3e50",
            activeforeground="white",
            width=12,
            cursor="hand2",
            relief="flat",
            command=self._show_stats_page
        )
        stats_button.pack(pady=5)
        
        # Quit button
        quit_button = tk.Button(
            content_frame,
            text="QUIT",
            font=("Helvetica", 10),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            width=8,
            cursor="hand2",
            relief="flat",
            command=self.root.destroy
        )
        quit_button.pack(pady=10)
    
    def _start_game(self):
        """Start a new game with the selected difficulty."""
        self.difficulty = self.difficulty_var.get()
        difficulty_config = self.DIFFICULTY_LEVELS[self.difficulty]
        
        self.min_value = difficulty_config["range"][0]
        self.max_value = difficulty_config["range"][1]
        self.max_attempts = difficulty_config["attempts"]
        self.attempts = 0
        self.target_number = random.randint(self.min_value, self.max_value)
        
        # Initialize timer
        self.timer = Timer()
        
        # Setup game page
        self._setup_game_page()
        
        # Start the timer
        self.timer.start()
        self._update_timer()
    
    def _show_stats_page(self):
        """Display a page with detailed game statistics."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create gradient background
        stats_frame = GradientFrame(self.root, "#2c3e50", "#4ca1af", width=600, height=500)
        stats_frame.pack(fill="both", expand=True)
        
        # Create main content container
        content_frame = tk.Frame(stats_frame, bg='#3a4c5f', bd=2, relief="ridge")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=450)
        
        # Statistics title
        stats_title = tk.Label(
            content_frame, 
            text="YOUR GAME STATISTICS",
            font=("Helvetica", 20, "bold"),
            fg="#ffffff",
            bg='#3a4c5f'
        )
        stats_title.pack(pady=(20, 15))
        
        # Get overall stats
        stats = self.stats_manager.get_stats()
        
        # Create stats overview frame
        overview_frame = tk.Frame(content_frame, bg='#2d3e6d', padx=10, pady=10, relief="ridge", bd=0)
        overview_frame.pack(fill="x", padx=20, pady=10)
        
        # Stats overview title
        overview_title = tk.Label(
            overview_frame,
            text="OVERVIEW",
            font=("Helvetica", 14, "bold"),
            fg="#3498db",
            bg='#2d3e6d'
        )
        overview_title.pack(pady=(0, 10))
        
        # Create grid for stats
        stats_grid = tk.Frame(overview_frame, bg='#2d3e6d')
        stats_grid.pack()
        
        # Display stats in a grid
        stats_data = [
            ("Games Played", stats["games_played"]),
            ("Games Won", stats["games_won"]),
            ("Win Rate", f"{stats['win_percentage']}%"),
            ("Avg Attempts", stats["avg_attempts"]),
            ("Best Streak", stats["best_streak"]),
            ("Current Streak", stats["current_streak"])
        ]
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 3
            col = i % 3
            
            frame = tk.Frame(stats_grid, bg='#2d3e6d', padx=10, pady=5)
            frame.grid(row=row, column=col, padx=10, pady=5)
            
            tk.Label(
                frame,
                text=label,
                font=("Helvetica", 11),
                fg="#bdc3c7",
                bg='#2d3e6d'
            ).pack()
            
            tk.Label(
                frame,
                text=str(value),
                font=("Helvetica", 16, "bold"),
                fg="#e74c3c",
                bg='#2d3e6d'
            ).pack()
        
        # Difficulty breakdown
        difficulty_frame = tk.Frame(content_frame, bg='#2d3e6d', padx=10, pady=10, relief="ridge", bd=0)
        difficulty_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            difficulty_frame,
            text="STATS BY DIFFICULTY",
            font=("Helvetica", 14, "bold"),
            fg="#3498db",
            bg='#2d3e6d'
        ).pack(pady=(0, 10))
        
        # Create table header
        table_frame = tk.Frame(difficulty_frame, bg='#2d3e6d')
        table_frame.pack(fill="x", padx=5)
        
        headers = ["Difficulty", "Games", "Won", "Win Rate", "Avg Attempts"]
        
        # Create header row
        for i, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Helvetica", 11, "bold"),
                fg="#ffffff",
                bg='#2d3e6d',
                width=10,
                anchor="w" if i == 0 else "center"
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Add data for each difficulty
        difficulties = ["easy", "medium", "hard"]
        difficulty_names = ["Easy", "Medium", "Hard"]
        
        for i, (diff_id, diff_name) in enumerate(zip(difficulties, difficulty_names)):
            level_stats = self.stats_manager.get_difficulty_stats(diff_id)
            
            tk.Label(
                table_frame,
                text=diff_name,
                font=("Helvetica", 11),
                fg="#ffffff",
                bg='#2d3e6d',
                anchor="w"
            ).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            
            tk.Label(
                table_frame,
                text=str(level_stats["games_played"]),
                font=("Helvetica", 11),
                fg="#ffffff",
                bg='#2d3e6d'
            ).grid(row=i+1, column=1, padx=5, pady=3)
            
            tk.Label(
                table_frame,
                text=str(level_stats["games_won"]),
                font=("Helvetica", 11),
                fg="#ffffff",
                bg='#2d3e6d'
            ).grid(row=i+1, column=2, padx=5, pady=3)
            
            tk.Label(
                table_frame,
                text=f"{level_stats['win_percentage']}%",
                font=("Helvetica", 11),
                fg="#ffffff",
                bg='#2d3e6d'
            ).grid(row=i+1, column=3, padx=5, pady=3)
            
            tk.Label(
                table_frame,
                text=str(level_stats["avg_attempts"]),
                font=("Helvetica", 11),
                fg="#ffffff",
                bg='#2d3e6d'
            ).grid(row=i+1, column=4, padx=5, pady=3)
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg='#3a4c5f')
        button_frame.pack(pady=20)
        
        # Back button
        back_btn = tk.Button(
            button_frame,
            text="BACK TO HOME",
            font=("Helvetica", 12, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            width=15,
            cursor="hand2",
            relief="flat",
            command=self._setup_welcome_page
        )
        back_btn.pack(side="left", padx=10)
        
        # Quit button
        quit_btn = tk.Button(
            button_frame,
            text="QUIT GAME",
            font=("Helvetica", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            width=10,
            cursor="hand2",
            relief="flat",
            command=self.root.destroy
        )
        quit_btn.pack(side="left", padx=10)

    def _show_welcome_page(self):
        """Redirect to welcome page setup."""
        self._setup_welcome_page()

if __name__ == "__main__":
    root = tk.Tk()
    game = EnhancedNumberGame(root)
    root.mainloop() 