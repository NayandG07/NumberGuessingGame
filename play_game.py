"""
Fixed Number Guessing Game launcher
"""
import os
import sys
import tkinter as tk
import traceback
import random

# Make sure we avoid any numpy/matplotlib issues
os.environ["USE_VISUALIZATION"] = "0"

def create_simple_game():
    """Create a simple number guessing game that works reliably"""
    print("Creating a simple number guessing game instead...")
    
    root = tk.Tk()
    root.title("Number Guessing Game")
    
    # Configure window
    window_width = 500
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg="#2c3e50")
    
    # Make sure window is visible
    root.attributes("-topmost", True)
    root.update()
    root.attributes("-topmost", False)
    
    # Game state variables
    target_number = random.randint(1, 20)
    attempts = 0
    
    # Set up the main frame
    main_frame = tk.Frame(root, bg="#2c3e50", padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Create title
    title = tk.Label(
        main_frame,
        text="NUMBER GUESSING GAME",
        font=("Helvetica", 24, "bold"),
        bg="#2c3e50",
        fg="#ecf0f1"
    )
    title.pack(pady=20)
    
    # Create game message
    message = tk.Label(
        main_frame,
        text="I'm thinking of a number between 1 and 20.\nCan you guess it?",
        font=("Helvetica", 14),
        bg="#2c3e50",
        fg="#ecf0f1",
        justify="center",
        wraplength=400
    )
    message.pack(pady=10)
    
    # Create attempts label
    attempts_label = tk.Label(
        main_frame,
        text="Attempts: 0",
        font=("Helvetica", 12),
        bg="#2c3e50",
        fg="#ecf0f1"
    )
    attempts_label.pack(pady=5)
    
    # Create input frame
    input_frame = tk.Frame(main_frame, bg="#2c3e50")
    input_frame.pack(pady=20)
    
    # Create input field
    guess_var = tk.StringVar()
    guess_entry = tk.Entry(
        input_frame,
        textvariable=guess_var,
        font=("Helvetica", 16),
        width=10,
        justify="center"
    )
    guess_entry.grid(row=0, column=0, padx=10)
    guess_entry.focus()
    
    # Function to check guess
    def check_guess():
        nonlocal attempts
        try:
            guess = int(guess_var.get())
            attempts += 1
            attempts_label.config(text=f"Attempts: {attempts}")
            
            if guess < target_number:
                message.config(text=f"Too low! Try a higher number.")
            elif guess > target_number:
                message.config(text=f"Too high! Try a lower number.")
            else:
                message.config(text=f"Congratulations! You found the number {target_number} in {attempts} attempts!")
                guess_entry.config(state="disabled")
                submit_button.config(state="disabled")
                
            guess_var.set("")
            guess_entry.focus()
            
        except ValueError:
            message.config(text="Please enter a valid number!")
            guess_var.set("")
            guess_entry.focus()
    
    # Function to start a new game
    def new_game():
        nonlocal target_number, attempts
        target_number = random.randint(1, 20)
        attempts = 0
        attempts_label.config(text=f"Attempts: {attempts}")
        message.config(text="I'm thinking of a number between 1 and 20.\nCan you guess it?")
        guess_var.set("")
        guess_entry.config(state="normal")
        submit_button.config(state="normal")
        guess_entry.focus()
    
    # Create buttons
    submit_button = tk.Button(
        input_frame,
        text="Guess",
        font=("Helvetica", 14),
        bg="#3498db", 
        fg="white",
        padx=10,
        command=check_guess
    )
    submit_button.grid(row=0, column=1, padx=10)
    
    # Bind enter key to check guess
    guess_entry.bind("<Return>", lambda event: check_guess())
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#2c3e50")
    button_frame.pack(pady=20)
    
    # New game button
    new_game_button = tk.Button(
        button_frame,
        text="New Game",
        font=("Helvetica", 12),
        bg="#2ecc71",
        fg="white",
        padx=10,
        command=new_game
    )
    new_game_button.grid(row=0, column=0, padx=10)
    
    # Quit button
    quit_button = tk.Button(
        button_frame,
        text="Quit",
        font=("Helvetica", 12),
        bg="#e74c3c",
        fg="white",
        padx=10,
        command=root.destroy
    )
    quit_button.grid(row=0, column=1, padx=10)
    
    print("Simple game created successfully. Starting main loop...")
    return root

def main():
    """Main function to start the game"""
    print("=== NUMBER GUESSING GAME LAUNCHER ===")
    print("Starting game...")
    
    try:
        # Create and run simple game
        root = create_simple_game()
        root.mainloop()
        print("Game closed by user")
        
    except Exception as e:
        print("\nERROR: Game encountered a problem!")
        print(f"Error: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 