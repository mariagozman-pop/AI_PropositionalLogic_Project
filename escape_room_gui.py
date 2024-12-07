
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import tkinter.font as tkFont


class TrapDialog(tk.Toplevel):
    def __init__(self, parent, riddle, options, correct_option, timeout=50):
        super().__init__(parent)
        self.title("Trap Activated!")
        self.geometry("900x500")  
        self.resizable(False, False)
        self.correct_option = correct_option.lower()
        self.player_choice = None
        self.timeout = timeout
        self.remaining_time = timeout
        self.timer_running = True
        self.after_id = None

        self.center_window(900, 500) 

        self.grid_columnconfigure(0, weight=1)

        self.riddle_label = tk.Label(
            self,
            text=riddle,
            wraplength=860, 
            justify="center",
            font=self.get_standard_font(14),  
            bg="#B4975A", 
            fg="#3E2723"
        )
        self.riddle_label.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        options_frame = tk.Frame(self, bg="#F5F5DC")
        options_frame.grid(row=1, column=0, padx=20, pady=20)

        self.selected_option = tk.StringVar(value="") 

        for option in options:
            rb = tk.Radiobutton(
                options_frame,
                text=option,
                variable=self.selected_option,
                value=option.lower(),
                font=self.get_standard_font(12),
                bg="#B4975A",  
                fg="#3E2723", 
                command=self.option_selected
            )
            rb.pack(anchor="w", pady=5)

        # Submit Button
        self.submit_button = tk.Button(
            self,
            text="Submit",
            command=self.submit_choice,
            bg="#C5A55D", 
            fg="black",
            font=self.get_standard_font(14),
            width=20,
            height=2,
            state=tk.DISABLED 
        )
        self.submit_button.grid(row=2, column=0, pady=20)

        # Timer Label
        self.timer_label = tk.Label(
            self,
            text=f"Time Remaining: {self.remaining_time} seconds",
            font=self.get_standard_font(12, italic=True),  # Increased font size
            bg="#F5F5DC",
            fg="#333333"
        )
        self.timer_label.grid(row=3, column=0, pady=10)

        # Start the countdown
        self.update_timer()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_standard_font(self, size, italic=False):
        """Return a standard font."""
        style = "italic" if italic else "normal"
        return ("DejaVu Sans", size, style)

    def center_window(self, width, height):
        self.update_idletasks() 
        parent = self.master
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def update_timer(self):
        if self.remaining_time > 0 and self.timer_running:
            self.timer_label.config(text=f"Time Remaining: {self.remaining_time} seconds")
            self.remaining_time -= 1
            # Schedule the next update after 1 second and save the id
            self.after_id = self.after(1000, self.update_timer)
        elif self.remaining_time <= 0 and self.timer_running:
            self.timer_running = False
            messagebox.showwarning("Time's Up!", "You failed to answer in time. Game Over!")
            self.master.exit_game()
            self.destroy()

    def option_selected(self):
        """Enable the submit button when an option is selected."""
        if self.selected_option.get():
            self.submit_button.config(state=tk.NORMAL)

    def submit_choice(self):
        if not self.timer_running:
            return 
        self.player_choice = self.selected_option.get()
        self.timer_running = False
        if self.after_id:
            self.after_cancel(self.after_id)  
        self.destroy()

    def on_close(self):
        if self.timer_running:
            self.timer_running = False
            if self.after_id:
                self.after_cancel(self.after_id)
            messagebox.showwarning("Time's Up!", "You failed to answer in time. Game Over!")
            self.master.exit_game()
        self.destroy()


class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D4C1A0")  
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(
            self,
            text="Welcome to the Escape Room Game!",
            font=self.get_standard_font(24),  
            bg="#C7A500",
            fg="#5C4033",  
            wraplength=760, 
            justify="center"
        )
        title_label.pack(pady=40)

        # Start Game Button
        start_button = tk.Button(
            self,
            text="Start Game",
            font=self.get_standard_font(14),
            bg="#8B5E3C",  
            fg="white",
            width=20,
            height=2,
            command=lambda: self.controller.show_frame("GameMenu")
        )
        start_button.pack(pady=10)

        # Rules Button
        rules_button = tk.Button(
            self,
            text="View Rules",
            font=self.get_standard_font(14),
            bg="#8B5E3C",  
            fg="white",
            width=20,
            height=2,
            command=lambda: self.controller.show_frame("RulesScreen")
        )
        rules_button.pack(pady=10)

        # Exit Button
        exit_button = tk.Button(
            self,
            text="Exit",
            font=self.get_standard_font(14),
            bg="#8B5E3C", 
            fg="white",
            width=20,
            height=2,
            command=self.controller.exit_game
        )
        exit_button.pack(pady=10)

    def get_standard_font(self, size, italic=False):
        """Return a standard font."""
        style = "italic" if italic else "normal"
        return ("DejaVu Sans", size, style)


class RulesScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D4C1A0")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Rules Title
        rules_title = tk.Label(
            self,
            text="Game Rules",
            font=self.get_standard_font(20),
            bg="#C7A500",  
            fg="#5C4033"  
        )
        rules_title.pack(pady=20)

        # Rules Text
        rules_text = (
            "1. Explore the rooms by clicking the button ""Look around"".\n"
            "2. If you look around the room without disarming a trap, you may trigger it.\n"
            "3. Solve puzzles to gain keys.\n"
            "4. Use keys to open doors and move between rooms.\n"
            "5. Disarm traps proactively using the 'Disarm Trap' button.\n"
            "6. If a trap is triggered, solve a riddle within 50 seconds to survive.\n"
            "7. Ensure all traps in a room are disarmed to make the room safe.\n"
            "8. Reach the exit to win the game!\n"
            "\nGood luck!"
        )

        # Rules Label
        rules_label = tk.Label(
            self,
            text=rules_text,
            wraplength=760,
            justify="center",
            font=self.get_standard_font(14),
            bg="#D4C1A0",  
            fg="#5C0433" 
        )
        rules_label.pack(padx=20, pady=10, fill="x", expand=False)

        # Back Button
        back_button = tk.Button(
            self,
            text="Back to Welcome",
            font=self.get_standard_font(14),
            bg="#8B5E3C",  
            fg="white",
            width=20,
            height=2,
            command=lambda: self.controller.show_frame("WelcomeScreen")
        )
        back_button.pack(pady=10)

    def get_standard_font(self, size, italic=False):
        """Return a standard font."""
        style = "italic" if italic else "normal"
        return ("DejaVu Sans", size, style)


class GameMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D4C1A0")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Game Menu Title
        menu_title = tk.Label(
            self,
            text="Game Menu",
            font=self.get_standard_font(28),  
            bg="#C7A500", 
            fg="#5C4033"
        )
        menu_title.pack(pady=30)

        # Start Game Button
        start_game_button = tk.Button(
            self,
            text="Start Escape Room",
            font=self.get_standard_font(16),
            bg="#8B5E3C",  
            fg="white",
            width=25,
            height=2,
            command=lambda: self.controller.show_frame("EscapeRoomGameScreen")
        )
        start_game_button.pack(pady=15)

        #Back Button
        back_button = tk.Button(
            self,
            text="Back to Welcome",
            font=self.get_standard_font(16),
            bg="#8B5E3C",  # Earthy Brown
            fg="white",
            width=25,
            height=2,
            command=lambda: self.controller.show_frame("WelcomeScreen")
        )
        back_button.pack(pady=15)

        # Exit Button
        exit_button = tk.Button(
            self,
            text="Exit",
            font=self.get_standard_font(16),
            bg="#8B5E3C",  # Earthy Brown
            fg="white",
            width=25,
            height=2,
            command=self.controller.exit_game
        )
        exit_button.pack(pady=15)

    def get_standard_font(self, size, italic=False):
        """Return a standard font."""
        style = "italic" if italic else "normal"
        return ("DejaVu Sans", size, style)


class EscapeRoomGameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D4C1A0")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Display Area
        self.display_text = tk.Label(
            self,
            text="",
            bg="#D4C1A0",  # Light Beige
            fg="#3E2723",  # Dark Brown Text
            font=self.get_standard_font(14),
            justify="left",
            anchor="nw",
            padx=10,
            pady=10,
            bd=2,
            relief="groove"
        )
        self.display_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Button Frame
        button_frame = tk.Frame(self, bg="#D4C1A0")
        button_frame.pack(pady=10)

        # Uniform Button Style 
        button_bg = "#C5A55D"  
        button_fg = "black"
        button_font = self.get_standard_font(14)
        button_width = 25
        button_height = 2

        # "Look Around" button
        self.look_button = tk.Button(
            button_frame,
            text="Look Around",
            command=self.look_around,
            state=tk.NORMAL,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.look_button.grid(row=0, column=0, padx=10, pady=5)

        # "Solve Puzzle" button, initially disabled
        self.solve_button = tk.Button(
            button_frame,
            text="Solve Puzzle",
            command=self.solve_puzzle,
            state=tk.DISABLED,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.solve_button.grid(row=0, column=1, padx=10, pady=5)

        # "Open Door" button
        self.open_button = tk.Button(
            button_frame,
            text="Open Door",
            command=self.open_door,
            state=tk.NORMAL,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.open_button.grid(row=1, column=0, padx=10, pady=5)

        # "Move to Another Room" button
        self.move_button = tk.Button(
            button_frame,
            text="Move to Another Room",
            command=self.move_to_room,
            state=tk.NORMAL,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.move_button.grid(row=1, column=1, padx=10, pady=5)

        # "Disarm Trap" button, initially disabled
        self.disarm_button = tk.Button(
            button_frame,
            text="Disarm Trap",
            command=self.disarm_trap,
            state=tk.DISABLED,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.disarm_button.grid(row=2, column=0, padx=10, pady=5)

        # "Check Safety" button
        self.check_button = tk.Button(
            button_frame,
            text="Check Safety",
            command=self.check_safety,
            state=tk.NORMAL,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.check_button.grid(row=2, column=1, padx=10, pady=5)

        # "Exit Game" button
        self.exit_button = tk.Button(
            button_frame,
            text="Exit Game",
            command=self.controller.exit_game,
            bg=button_bg,
            fg=button_fg,
            font=button_font,
            width=button_width,
            height=button_height
        )
        self.exit_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.update_display()

    def get_standard_font(self, size, italic=False):
        """Return a standard font."""
        style = "italic" if italic else "normal"
        return ("DejaVu Sans", size, style)

    def write_current_state(self, goal_statements):
        """Write the complete state and goals to the Prover9 input file."""
        with open(self.controller.current_state_file, 'w') as f:
            f.write('formulas(assumptions).\n')
            f.write('% Game Rules and Logic\n')

            # Include static rules
            f.write('room(room1).\nroom(room2).\nroom(exit).\n')
            f.write('door(door1).\ndoor(door2).\n')
            f.write('connects(door1, room1, room2).\nconnects(door2, room2, exit).\n')
            f.write('key(key1).\nkey(key2).\n')
            f.write('opens(key1, door1).\nopens(key2, door2).\n')
            f.write('puzzle(puzzle1).\npuzzle(puzzle2).\n')

            f.write('all X (correct_answer(X, puzzle1) -> solved(X, puzzle1)).\n')
            f.write('all X (solved(X, puzzle1) -> has(X, key1)).\n')
            f.write('all X (correct_answer(X, puzzle2) -> solved(X, puzzle2)).\n')
            f.write('all X (solved(X, puzzle2) -> has(X, key2)).\n')
            f.write('trap(trap1).\n')

            f.write('all X all Y (room(Y) & (all Z (trap_in_room(Y, Z) -> disarmed(Z))) -> safe(X, Y)).\n')

            f.write('all X all Y all A all B (door(Y) & connects(Y, A, B) & open(Y) & at(X, A) -> can_move(X, A, B)).\n')
            f.write('all X all Y all K (has(X, K) & opens(K, Y) & action_open_door(X, Y) -> open(Y)).\n\n')
            
            f.write('safe(player, room1).\n')
            
            f.write('disarmed(trap1) -> safe(player, room2).')

            # Dynamic game state
            f.write('% Current State\n')
            f.write(f'at({self.controller.player},{self.controller.current_room}).\n')
            for item in self.controller.inventory:
                f.write(f'has({self.controller.player},{item}).\n')
            for puzzle in self.controller.solved_puzzles:
                f.write(f'solved({self.controller.player},{puzzle}).\n')
            for door in self.controller.open_doors:
                f.write(f'open({door}).\n')
            for trap in self.controller.disarmed_traps:
                f.write(f'disarmed({trap}).\n')

            # Include trap_in_room facts
            for room in self.controller.rooms:
                traps = [trap for trap in self.controller.items_in_rooms.get(room, []) if trap.startswith('trap')]
                for trap in traps:
                    f.write(f'trap_in_room({room}, {trap}).\n')

            # Include any actions
            if hasattr(self.controller, 'actions'):
                for action in self.controller.actions:
                    f.write(f'{action}.\n')
            f.write('end_of_list.\n\n')

            # Add goals
            f.write('formulas(goals).\n')
            for goal in goal_statements:
                f.write(f'{goal}.\n')
            f.write('end_of_list.\n')

    def run_prover9(self, goal_statements):
        """Run Prover9 to validate goals."""
        self.write_current_state(goal_statements)
        try:
            result = subprocess.run(
                [self.controller.prover9_path, '-f', self.controller.current_state_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return 'THEOREM PROVED' in result.stdout
        except FileNotFoundError:
            messagebox.showerror("Error", "Prover9 executable not found. Please check the path.")
            return False

    def update_display(self):
        # Access game state via controller and update the display
        display_content = (
            f"Current Location: {self.controller.current_room}\n\n"
            f"Inventory: {', '.join(self.controller.inventory) if self.controller.inventory else 'Empty'}\n"
            f"Solved Puzzles: {', '.join(self.controller.solved_puzzles) if self.controller.solved_puzzles else 'None'}\n"
            f"Open Doors: {', '.join(self.controller.open_doors) if self.controller.open_doors else 'None'}\n"
            f"Disarmed Traps: {', '.join(self.controller.disarmed_traps) if self.controller.disarmed_traps else 'None'}\n"
        )
        self.display_text.config(text=display_content)

        # Update button states based on current room's contents
        items = self.controller.items_in_rooms.get(self.controller.current_room, [])

        # Enable or disable "Solve Puzzle" button
        has_puzzle = any(item.startswith('puzzle') for item in items)
        if has_puzzle:
            self.solve_button.config(state=tk.NORMAL)
        else:
            self.solve_button.config(state=tk.DISABLED)

        # Enable or disable "Disarm Trap" button
        has_active_trap = any(item.startswith('trap') and item not in self.controller.disarmed_traps for item in items)
        self.disarm_button.config(state=tk.DISABLED)

    def look_around(self):
        active_traps = [
            trap for trap in self.controller.items_in_rooms.get(self.controller.current_room, [])
            if trap.startswith('trap') and trap not in self.controller.disarmed_traps
        ]
        if active_traps:
            for trap in active_traps:
                messagebox.showerror("Trap Triggered", f"You triggered {trap}!")
                self.handle_trap(trap)
            return

        items = self.controller.items_in_rooms.get(self.controller.current_room, [])

        puzzle_items = [item for item in items if item.startswith('puzzle')]

        if puzzle_items:
            self.controller.puzzle_seen = True  
            self.solve_button.config(state=tk.NORMAL) 
            messagebox.showinfo("Look Around", f"You see: {', '.join(puzzle_items)}.")

            self.run_prover9([f'seen({self.controller.player}, {puzzle_items[0]})']) 
        else:
            self.controller.puzzle_seen = False  
            self.solve_button.config(state=tk.DISABLED)
            messagebox.showinfo("Look Around", "There is no puzzle here.")

    def handle_trap(self, trap):
        """Handle trap activation by presenting a riddle with a timer."""
        # Define the riddle, options, and correct option
        riddle = (
            "You are locked in a trap with no obvious way out. On the wall, there is a lever with a sign that reads:\n\n"
            "\"Pulling this lever will not free you unless the statement on the wall is false.\"\n\n"
            "If this lever does not free you, pulling it will flood the room with poison gas or unleash venomous snakes.\n\n"
            "Be cautious! Do you pull the lever?"
        )
        options = ["Yes", "No"]
        correct_option = "Yes"  # "Yes" corresponds to "Pull the lever."

        # Create and display the TrapDialog
        trap_dialog = TrapDialog(self, riddle, options, correct_option, timeout=50)
        self.wait_window(trap_dialog)  # Wait until the dialog is closed

        # After the dialog is closed, check the player's choice
        if trap_dialog.player_choice == correct_option.lower():
            # Correct choice, disarm the trap
            self.controller.disarmed_traps.append(trap)
            self.controller.items_in_rooms[self.controller.current_room].remove(trap)
            self.update_display()
            messagebox.showinfo("Trap Disarmed", f"You pulled the lever and disarmed {trap}!")
            # Update Prover9 state to reflect disarmed trap
            self.run_prover9([f'disarmed({trap})'])
        else:
            # Player failed to choose correctly
            messagebox.showwarning("Game Over", "You chose not to pull the lever. Game Over!")
            self.controller.exit_game()


    def get_puzzle_riddle(self, puzzle):
        """Return the riddle and answer for a given puzzle."""
        if puzzle == 'puzzle1':
            return (
                "I hold diverse types without a fuss. Mutable and dynamic, adaptable to us. In Python's realm, I'm versatile and neat, What data structure am I, complete?",
                "dictionary"
            )
        elif puzzle == 'puzzle2':
            return (
                "I can hold all types in my domain. Mutable and changeable, not quite the same. A sequence ordered, I obey your command. What data structure am I in Python's land?",
                "list"
            )
        return None, None  # Return None if no riddle is found

    def solve_puzzle(self):
        """Present a riddle and attempt to solve the puzzle."""
        if not getattr(self.controller, 'puzzle_seen', False):
            messagebox.showwarning("Puzzle", "You need to look around first to see the puzzle!")
            return

        puzzles = [
            item for item in self.controller.items_in_rooms.get(self.controller.current_room, [])
            if item.startswith('puzzle')
        ]
        if not puzzles:
            messagebox.showwarning("No Puzzle", "There is no puzzle to solve here.")
            return

        puzzle = puzzles[0]  # Get the first puzzle in the room
        riddle, answer = self.get_puzzle_riddle(puzzle)

        if not riddle:
            messagebox.showerror("Error", "No riddle defined for this puzzle.")
            return

        # Present the riddle to the player
        player_answer = simpledialog.askstring("Solve Puzzle", riddle)
        if player_answer and player_answer.strip().lower() == answer:
            # Update the game state if the answer is correct
            self.controller.solved_puzzles.append(puzzle)
            self.controller.items_in_rooms[self.controller.current_room].remove(puzzle)
            self.run_prover9([f'solved({self.controller.player},{puzzle})'])  # Validate with Prover9

            # Grant the corresponding key
            if puzzle == 'puzzle1':
                self.controller.inventory.append('key1')
            elif puzzle == 'puzzle2':
                self.controller.inventory.append('key2')

            self.update_display()
            messagebox.showinfo("Puzzle Solved", f"You solved {puzzle} and found a key!")
        else:
            messagebox.showwarning("Puzzle", "Wrong answer. Try again later.")

    def open_door(self):
        door = 'door1' if self.controller.current_room == 'room1' else 'door2'
        key_required = 'key1' if door == 'door1' else 'key2'

        if key_required in self.controller.inventory:
            # Add the action to the game state
            self.controller.actions = [f'action_open_door({self.controller.player},{door})']

            if self.run_prover9([f'open({door})']):
                if door not in self.controller.open_doors:
                    self.controller.open_doors.append(door)
                self.update_display()
                messagebox.showinfo("Door Opened", f"You opened {door}!")
            else:
                messagebox.showwarning("Door Locked", "You cannot open this door.")
            # Clear actions after processing
            self.controller.actions = []
        else:
            messagebox.showwarning("No Key", f"You need {key_required} to open {door}.")

    def move_to_room(self):
        self.controller.puzzle_seen = False  
        
        if self.controller.current_room == 'room1':
            target_room = 'room2'
        elif self.controller.current_room == 'room2':
            target_room = 'exit'
        else:
            messagebox.showinfo("End", "You have already reached the exit!")
            return

        # Check if moving to 'exit' to display congratulations
        if target_room == 'exit':
            if self.run_prover9([f'can_move({self.controller.player},{self.controller.current_room},{target_room})']):
                self.controller.current_room = target_room
                self.update_display()
                messagebox.showinfo("Congratulations!", "You have successfully escaped the room! Congratulations!")
                self.controller.exit_game()
            else:
                messagebox.showwarning("Move", "You cannot move to that room.")
            return

        if self.run_prover9([f'can_move({self.controller.player},{self.controller.current_room},{target_room})']):
            self.controller.current_room = target_room
            self.update_display()
            messagebox.showinfo("Move", f"You moved to {target_room}.")
        else:
            messagebox.showwarning("Move", "You cannot move to that room.")

    def disarm_trap(self):
        # Only allow disarming if a trap is present and not yet disarmed
        active_traps = [
            trap for trap in self.controller.items_in_rooms.get(self.controller.current_room, [])
            if trap.startswith('trap') and trap not in self.controller.disarmed_traps
        ]
        if active_traps:
            trap = active_traps[0]  # Assuming one trap per room for simplicity
            # Attempt to disarm the trap via Prover9
            if self.run_prover9([f'trap_in_room(room2, trap1)']):
                self.controller.disarmed_traps.append(trap)
                self.controller.items_in_rooms[self.controller.current_room].remove(trap)
                self.update_display()
                messagebox.showinfo("Trap Disarmed", f"You disarmed {trap}!")
                # Update Prover9 state
                self.run_prover9([f'disarmed({trap})'])
            else:
                # Inform the player they cannot disarm the trap without the required conditions
                messagebox.showwarning(
                    "Cannot Disarm Trap",
                    "You do not have the necessary items to disarm the trap."
                )
        else:
            messagebox.showwarning("Trap", "There is no active trap to disarm here.")

    def check_safety(self):
        # Optional action; does not interfere with 'Look Around'
        if self.run_prover9([f'safe({self.controller.player},{self.controller.current_room})']):
            messagebox.showinfo("Safety", "The room is safe.")
        else:
            messagebox.showwarning("Safety", "The room is not safe! Be cautious.")
            self.disarm_button.config(state="normal")



class EscapeRoomApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Escape Room Game")
        self.geometry("800x600")  # Window size
        self.center_window(800, 600)
        self.resizable(False, False)

        # Initialize game state
        self.player = 'player'
        self.rooms = ['room1', 'room2', 'exit']
        self.current_room = 'room1'
        self.inventory = []
        self.solved_puzzles = []
        self.open_doors = []
        self.disarmed_traps = []
        self.items_in_rooms = {
            'room1': ['puzzle1'],
            'room2': ['puzzle2', 'trap1'],
        }
        self.prover9_path = '/mnt/c/Users/Maria Gozman-Pop/OneDrive/Desktop/Semester1/AI/Lab6/LADR-2009-11A/LADR-2009-11A/bin/prover9'
        self.current_state_file = 'current_state.in'
        self.actions = []  # Initialize actions

        # Container for all frames
        container = tk.Frame(self, bg="#D2B48C")  # Match frame background
        container.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to allow container to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold different frames
        self.frames = {}

        # Initialize frames
        for F in (WelcomeScreen, RulesScreen, GameMenu, EscapeRoomGameScreen):
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the Welcome Screen initially
        self.show_frame("WelcomeScreen")

    def center_window(self, width, height):
        self.update_idletasks()  # Ensure window size is calculated
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, frame_name):
        '''Show a frame for the given frame name'''
        frame = self.frames[frame_name]
        frame.tkraise()

    def exit_game(self):
        self.destroy()


if __name__ == '__main__':
    app = EscapeRoomApp()
    app.mainloop()
