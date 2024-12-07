import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import time


class TrapDialog(tk.Toplevel):
    def __init__(self, parent, riddle, answer, timeout=50):
        super().__init__(parent)
        self.title("Trap Activated!")
        self.geometry("400x200")
        self.resizable(False, False)
        self.answer = answer.lower()
        self.player_answer = None
        self.timeout = timeout
        self.remaining_time = timeout
        self.timer_running = True
        self.after_id = None  # To track the after() callback

        # Riddle Label
        self.riddle_label = tk.Label(self, text=riddle, wraplength=380, justify="left")
        self.riddle_label.pack(pady=20)

        # Entry for player's answer
        self.answer_entry = tk.Entry(self, width=50)
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus_set()

        # Submit Button
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_answer)
        self.submit_button.pack(pady=5)

        # Timer Label
        self.timer_label = tk.Label(self, text=f"Time Remaining: {self.remaining_time} seconds")
        self.timer_label.pack(pady=5)

        # Start the countdown
        self.update_timer()

        # Bind the Return key to submit the answer
        self.bind('<Return>', lambda event: self.submit_answer())

        # Handle window close (e.g., clicking the 'X' button)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def submit_answer(self):
        if not self.timer_running:
            return  # Prevent submission after timeout
        self.player_answer = self.answer_entry.get().strip().lower()
        self.timer_running = False
        if self.after_id:
            self.after_cancel(self.after_id)  # Cancel any scheduled timer updates
        self.destroy()

    def on_close(self):
        if self.timer_running:
            self.timer_running = False
            if self.after_id:
                self.after_cancel(self.after_id)  # Cancel any scheduled timer updates
            messagebox.showwarning("Time's Up!", "You failed to answer in time. Game Over!")
            self.master.exit_game()
        self.destroy()


class EscapeRoomGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Escape Room Game")
        self.geometry("600x400")

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
        self.prover9_path = '/mnt/c/Users/Calina/Desktop/ANUL3/AI/Lab6 again/LADR-2009-11A/bin/prover9'  # Replace with the correct path to Prover9 executable
        self.current_state_file = 'current_state.in'

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        self.display_text = tk.Text(self, height=15, width=70, state=tk.DISABLED, bg="#f0f0f0")
        self.display_text.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack()

        # Always enabled "Look Around" button
        self.look_button = tk.Button(button_frame, text="Look Around", command=self.look_around, state=tk.NORMAL)
        self.look_button.grid(row=0, column=0, padx=5, pady=5)

        # "Solve Puzzle" button, initially disabled
        self.solve_button = tk.Button(button_frame, text="Solve Puzzle", command=self.solve_puzzle, state=tk.DISABLED)
        self.solve_button.grid(row=0, column=1, padx=5, pady=5)

        # "Open Door" button, always enabled
        self.open_button = tk.Button(button_frame, text="Open Door", command=self.open_door, state=tk.NORMAL)
        self.open_button.grid(row=0, column=2, padx=5, pady=5)

        # "Move to Another Room" button, always enabled
        self.move_button = tk.Button(button_frame, text="Move to Another Room", command=self.move_to_room)
        self.move_button.grid(row=1, column=0, padx=5, pady=5)

        # "Disarm Trap" button, initially disabled
        self.disarm_button = tk.Button(button_frame, text="Disarm Trap", command=self.disarm_trap, state=tk.DISABLED)
        self.disarm_button.grid(row=1, column=1, padx=5, pady=5)

        # "Check Safety" button, optional action
        self.check_button = tk.Button(button_frame, text="Check Safety", command=self.check_safety)
        self.check_button.grid(row=1, column=2, padx=5, pady=5)

        # "Exit Game" button
        self.exit_button = tk.Button(button_frame, text="Exit Game", command=self.exit_game)
        self.exit_button.grid(row=2, column=1, padx=5, pady=5)

        self.update_display()

    def write_current_state(self, goal_statements):
        """Write the complete state and goals to the Prover9 input file."""
        with open(self.current_state_file, 'w') as f:
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
            
            # **Removed Key Dependency for Disarming Traps**
            # Original Line:
            # f.write('all X (has(X, key2) & trap_in_room(room2, trap1) -> disarmed(trap1)).\n')
            # Updated Line: Disarming traps no longer requires key2
            f.write('trap_in_room(room2, trap1) -> disarmed(trap1).\n')
            
            # **Adjusted Implications to Reflect Removal of Key Requirement**
            # Original Line:
            # f.write('all X (disarmed(trap1) -> (has(X, key2) & trap_in_room(room2, trap1))).\n')
            # Updated Line:
            f.write('disarmed(trap1) -> trap_in_room(room2, trap1).\n')
            
            f.write('all X all Y all A all B (door(Y) & connects(Y, A, B) & open(Y) & at(X, A) -> can_move(X, A, B)).\n')
            f.write('all X all Y all K (has(X, K) & opens(K, Y) & action_open_door(X, Y) -> open(Y)).\n\n')

            # Dynamic game state
            f.write('% Current State\n')
            f.write(f'at({self.player},{self.current_room}).\n')
            for item in self.inventory:
                f.write(f'has({self.player},{item}).\n')
            for puzzle in self.solved_puzzles:
                f.write(f'solved({self.player},{puzzle}).\n')
            for door in self.open_doors:
                f.write(f'open({door}).\n')
            for trap in self.disarmed_traps:
                f.write(f'disarmed({trap}).\n')
            
            # Include trap_in_room facts
            for room in self.rooms:
                traps = [trap for trap in self.items_in_rooms.get(room, []) if trap.startswith('trap')]
                for trap in traps:
                    f.write(f'trap_in_room({room}, {trap}).\n')
            
            # Include any actions
            if hasattr(self, 'actions'):
                for action in self.actions:
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
            result = subprocess.run([self.prover9_path, '-f', self.current_state_file],
                                    stdout=subprocess.PIPE, text=True)
            return 'THEOREM PROVED' in result.stdout
        except FileNotFoundError:
            messagebox.showerror("Error", "Prover9 executable not found. Please check the path.")
            return False

    def update_display(self):
        self.display_text.config(state=tk.NORMAL)
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, f"Current Location: {self.current_room}\n")
        self.display_text.insert(tk.END, f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n")
        self.display_text.insert(tk.END, f"Solved Puzzles: {', '.join(self.solved_puzzles) if self.solved_puzzles else 'None'}\n")
        self.display_text.insert(tk.END, f"Open Doors: {', '.join(self.open_doors) if self.open_doors else 'None'}\n")
        self.display_text.insert(tk.END, f"Disarmed Traps: {', '.join(self.disarmed_traps) if self.disarmed_traps else 'None'}\n")
        self.display_text.config(state=tk.DISABLED)

        # Update button states based on current room's contents
        items = self.items_in_rooms.get(self.current_room, [])

        # Enable or disable "Solve Puzzle" button
        has_puzzle = any(item.startswith('puzzle') for item in items)
        if has_puzzle:
            self.solve_button.config(state=tk.NORMAL)
        else:
            self.solve_button.config(state=tk.DISABLED)

        # Enable or disable "Disarm Trap" button
        has_active_trap = any(item.startswith('trap') and item not in self.disarmed_traps for item in items)
        if has_active_trap:
            self.disarm_button.config(state=tk.NORMAL)
        else:
            self.disarm_button.config(state=tk.DISABLED)

    def look_around(self):
        # Check if there's a trap in the current room and it's not disarmed
        active_traps = [trap for trap in self.items_in_rooms.get(self.current_room, [])
                        if trap.startswith('trap') and trap not in self.disarmed_traps]
        if active_traps:
            for trap in active_traps:
                messagebox.showerror("Trap Triggered", f"You triggered {trap}!")
                self.handle_trap(trap)
            return

        # Check items in the current room
        items = self.items_in_rooms.get(self.current_room, [])

        # Filter out traps and only show puzzles
        puzzle_items = [item for item in items if item.startswith('puzzle')]

        # If there are puzzle items, show them and enable the "Solve Puzzle" button
        if puzzle_items:
            self.puzzle_seen = True  # Mark the puzzle as seen
            self.solve_button.config(state=tk.NORMAL)  # Enable the "Solve Puzzle" button
            messagebox.showinfo("Look Around", f"You see: {', '.join(puzzle_items)}.")

            # Update Prover9 state to reflect that the puzzle has been seen
            self.run_prover9([f'seen({self.player}, {puzzle_items[0]})'])  # Assume the first puzzle is seen
        else:
            self.puzzle_seen = False  # No puzzle, button should be disabled
            self.solve_button.config(state=tk.DISABLED)  # Disable the "Solve Puzzle" button
            messagebox.showinfo("Look Around", "There is no puzzle here.")

    def handle_trap(self, trap):
        """Handle trap activation by presenting a riddle with a timer."""
        riddle, answer = self.get_trap_riddle(trap)
        if not riddle:
            messagebox.showerror("Error", "No riddle defined for this trap.")
            self.exit_game()
            return

        # Create and display the TrapDialog
        trap_dialog = TrapDialog(self, riddle, answer, timeout=50)
        self.wait_window(trap_dialog)  # Wait until the dialog is closed

        # After the dialog is closed, check the player's answer
        if trap_dialog.player_answer == answer:
            # Correct answer, disarm the trap
            self.disarmed_traps.append(trap)
            self.items_in_rooms[self.current_room].remove(trap)
            self.update_display()
            messagebox.showinfo("Trap Disarmed", f"You solved the trap riddle and disarmed {trap}!")
            # Update Prover9 state to reflect disarmed trap
            self.run_prover9([f'disarmed({trap})'])
        else:
            # Player failed to solve the riddle or timed out
            # Note: The TrapDialog already handles game over on timeout
            # Here, handle incorrect answers
            if trap_dialog.player_answer is not None:
                messagebox.showwarning("Game Over", "You failed to solve the trap riddle. Game Over!")
                self.exit_game()
            # If the player closed the dialog without answering, the game is already over

    def get_trap_riddle(self, trap):
        """Return the riddle and answer for a given trap."""
        if trap == 'trap1':
            return "I have cities but no houses, forests but no trees, and water but no fish. What am I?", "map"
        # Add more traps as needed
        return None, None  # Return None if no riddle is found

    def get_puzzle_riddle(self, puzzle):
        """Return the riddle and answer for a given puzzle."""
        if puzzle == 'puzzle1':
            return "I speak without a mouth and hear without ears. What am I?", "echo"
        elif puzzle == 'puzzle2':
            return "I am not alive, but I grow. I don’t have lungs, but I need air. What am I?", "fire"
        return None, None  # Return None if no riddle is found

    def solve_puzzle(self):
        """Present a riddle and attempt to solve the puzzle."""
        if not getattr(self, 'puzzle_seen', False):
            messagebox.showwarning("Puzzle", "You need to look around first to see the puzzle!")
            return

        puzzles = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('puzzle')]
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
            self.solved_puzzles.append(puzzle)
            self.items_in_rooms[self.current_room].remove(puzzle)
            self.run_prover9([f'solved({self.player},{puzzle})'])  # Validate with Prover9

            # Grant the corresponding key
            if puzzle == 'puzzle1':
                self.inventory.append('key1')
            elif puzzle == 'puzzle2':
                self.inventory.append('key2')

            self.update_display()
            messagebox.showinfo("Puzzle Solved", f"You solved {puzzle} and found a key!")
        else:
            messagebox.showwarning("Puzzle", "Wrong answer. Try again later.")

    def open_door(self):
        door = 'door1' if self.current_room == 'room1' else 'door2'
        key_required = 'key1' if door == 'door1' else 'key2'

        if key_required in self.inventory:
            # Add the action to the game state
            self.actions = [f'action_open_door({self.player},{door})']

            if self.run_prover9([f'open({door})']):
                if door not in self.open_doors:
                    self.open_doors.append(door)
                self.update_display()
                messagebox.showinfo("Door Opened", f"You opened {door}!")
            else:
                messagebox.showwarning("Door Locked", "You cannot open this door.")
            # Clear actions after processing
            self.actions = []
        else:
            messagebox.showwarning("No Key", f"You need {key_required} to open {door}.")

    def move_to_room(self):
        # Determine target room based on current location
        if self.current_room == 'room1':
            target_room = 'room2'
        elif self.current_room == 'room2':
            target_room = 'exit'
        else:
            messagebox.showinfo("End", "You have already reached the exit!")
            return

        # "Open Door" and "Move to Another Room" remain enabled; no need to disable them
        if self.run_prover9([f'can_move({self.player},{self.current_room},{target_room})']):
            self.current_room = target_room
            self.update_display()
            messagebox.showinfo("Move", f"You moved to {target_room}.")
        else:
            messagebox.showwarning("Move", "You cannot move to that room.")

    def disarm_trap(self):
        # Only allow disarming if a trap is present and not yet disarmed
        active_traps = [trap for trap in self.items_in_rooms.get(self.current_room, [])
                        if trap.startswith('trap') and trap not in self.disarmed_traps]
        if active_traps:
            trap = active_traps[0]  # Assuming one trap per room for simplicity
            # Attempt to disarm the trap via Prover9
            if self.run_prover9([f'disarmed({trap})']):
                self.disarmed_traps.append(trap)
                self.items_in_rooms[self.current_room].remove(trap)
                self.update_display()
                messagebox.showinfo("Trap Disarmed", f"You disarmed {trap}!")
                # Update Prover9 state
                self.run_prover9([f'disarmed({trap})'])
            else:
                # Inform the player they cannot disarm the trap without the required conditions
                messagebox.showwarning("Cannot Disarm Trap", "You do not have the necessary items to disarm the trap.")
        else:
            messagebox.showwarning("Trap", "There is no active trap to disarm here.")

    def check_safety(self):
        # Optional action; does not interfere with 'Look Around'
        if self.run_prover9([f'safe({self.player},{self.current_room})']):
            messagebox.showinfo("Safety", "The room is safe.")
            # Optionally, you can set flags or update the display
        else:
            messagebox.showwarning("Safety", "The room is not safe! Be cautious.")
            # Optionally, inform the player about the trap

    def exit_game(self):
        self.destroy()


if __name__ == '__main__':
    game = EscapeRoomGame()
    game.mainloop()
