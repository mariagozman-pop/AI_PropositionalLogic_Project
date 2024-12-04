import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog


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
        self.prover9_path = '/mnt/c/Users/Maria Gozman-Pop/OneDrive/Desktop/Semester1/AI/Lab6/LADR-2009-11A/LADR-2009-11A/bin/prover9'  # Replace with the correct path to Prover9 executable
        self.current_state_file = 'current_state.in'

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        self.display_text = tk.Text(self, height=15, width=70)
        self.display_text.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack()

        self.look_button = tk.Button(button_frame, text="Look Around", command=self.look_around)
        self.look_button.grid(row=0, column=0, padx=5, pady=5)

        self.solve_button = tk.Button(button_frame, text="Solve Puzzle", command=self.solve_puzzle)
        self.solve_button.grid(row=0, column=1, padx=5, pady=5)

        self.open_button = tk.Button(button_frame, text="Open Door", command=self.open_door)
        self.open_button.grid(row=0, column=2, padx=5, pady=5)

        self.move_button = tk.Button(button_frame, text="Move to Another Room", command=self.move_to_room)
        self.move_button.grid(row=1, column=0, padx=5, pady=5)

        self.disarm_button = tk.Button(button_frame, text="Disarm Trap", command=self.disarm_trap)
        self.disarm_button.grid(row=1, column=1, padx=5, pady=5)

        self.check_button = tk.Button(button_frame, text="Check Safety", command=self.check_safety)
        self.check_button.grid(row=1, column=2, padx=5, pady=5)

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
        f.write('all X all Y (room(Y) & -trap_in_room(Y) -> safe(X, Y)).\n')
        f.write('all X all Y (has(X, key2) & trap(Y) -> disarmed(Y)).\n')
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
            if 'trap1' in self.items_in_rooms.get(room, []):
                f.write(f'trap_in_room({room}).\n')
            else:
                f.write(f'-trap_in_room({room}).\n')  # Explicitly state that the trap is not in the room
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
            result = subprocess.run([self.prover9_path, '-f', self.current_state_file], stdout=subprocess.PIPE, text=True)
            return 'THEOREM PROVED' in result.stdout
        except FileNotFoundError:
            messagebox.showerror("Error", "Prover9 executable not found. Please check the path.")
            return False

    def update_display(self):
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, f"Current Location: {self.current_room}\n")
        self.display_text.insert(tk.END, f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n")

    def look_around(self):
        items = self.items_in_rooms.get(self.current_room, [])
        if items:
            messagebox.showinfo("Look Around", f"You see: {', '.join(items)}.")
        else:
            messagebox.showinfo("Look Around", "There is nothing of interest here.")

    
    def get_puzzle_riddle(self, puzzle):
     """Return the riddle and answer for a given puzzle."""
     if puzzle == 'puzzle1':
        return "I speak without a mouth and hear without ears. What am I?", "echo"
     elif puzzle == 'puzzle2':
        return "I am not alive, but I grow. I don’t have lungs, but I need air. What am I?", "fire"
     return None, None  # Return None if no riddle is found



    def solve_puzzle(self):
     """Present a riddle and attempt to solve the puzzle."""
     puzzles = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('puzzle')]
     if not puzzles:
        messagebox.showwarning("No Puzzle", "There is no puzzle to solve here.")
        return

     puzzle = puzzles[0]  # Get the first puzzle in the room
     riddle, answer = self.get_puzzle_riddle(puzzle)

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
        target_room = 'room2' if self.current_room == 'room1' else 'exit'
        if self.run_prover9([f'can_move({self.player},{self.current_room},{target_room})']):
            self.current_room = target_room
            self.update_display()
            messagebox.showinfo("Move", f"You moved to {target_room}.")
        else:
            messagebox.showwarning("Move", "You cannot move to that room.")



    def disarm_trap(self):
        if self.run_prover9([f'disarmed(trap1)']):
            self.disarmed_traps.append('trap1')
            self.items_in_rooms['room2'].remove('trap1')
            self.update_display()
            messagebox.showinfo("Trap Disarmed", "You disarmed the trap!")
        else:
            messagebox.showwarning("Trap", "You cannot disarm this trap.")



    def check_safety(self):
        if self.run_prover9([f'safe({self.player},{self.current_room})']):
            messagebox.showinfo("Safety", "The room is safe.")
        else:
            messagebox.showwarning("Safety", "The room is not safe!")



    def exit_game(self):
        self.destroy()


if __name__ == '__main__':
    game = EscapeRoomGame()
    game.mainloop()