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
        self.prover9_path = '/path/to/prover9'  # Replace with the correct path to the prover9 executable
        self.current_state_file = 'current_state.in'

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        # Display area
        self.display_text = tk.Text(self, height=15, width=70)
        self.display_text.pack(pady=10)

        # Action buttons
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

        # Update the display with the initial state
        self.update_display()

    def write_current_state(self, goal_statements=None):
        with open(self.current_state_file, 'w') as f:
            f.write('formulas(assumptions).\n')
            f.write(f'at({self.player},{self.current_room}).\n')
            for item in self.inventory:
                f.write(f'has({self.player},{item}).\n')
            for puzzle in self.solved_puzzles:
                f.write(f'solved({self.player},{puzzle}).\n')
            for door in self.open_doors:
                f.write(f'open({door}).\n')
            for trap in self.disarmed_traps:
                f.write(f'disarmed({trap}).\n')
            f.write('end_of_list.\n\n')

            if goal_statements:
                f.write('formulas(goals).\n')
                for goal in goal_statements:
                    f.write(f'{goal}.\n')
                f.write('end_of_list.\n')

    def run_prover9(self, goal_statements):
        self.write_current_state(goal_statements)
        try:
            result = subprocess.run(['/mnt/c/Users/Calina/Desktop/ANUL3/AI/Lab6 again/LADR-2009-11A/bin/prover9', '-f', self.current_state_file], stdout=subprocess.PIPE, text=True)
            output = result.stdout
            return 'THEOREM PROVED' in output
        except FileNotFoundError:
            messagebox.showerror("Error", "Prover9 executable not found. Please check the path.")
            return False

    def update_display(self):
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, f"Current Location: {self.current_room}\n")
        self.display_text.insert(tk.END, f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n\n")

    def look_around(self):
        items = self.items_in_rooms.get(self.current_room, [])
        if items:
            message = f"You look around and see: {', '.join(items)}."
        else:
            message = "You look around but see nothing interesting."
        messagebox.showinfo("Look Around", message)

    def solve_puzzle(self):
        riddle = "I speak without a mouth and hear without ears. What am I?"
        answer = simpledialog.askstring("Solve Puzzle", riddle)
        if answer and answer.lower() == "echo":
            self.inventory.append('key1')
            self.update_display()
            messagebox.showinfo("Puzzle Solved", "You solved the puzzle and found a key!")
        else:
            messagebox.showwarning("Puzzle", "Wrong answer. Try again later.")

    def open_door(self):
        if self.run_prover9([f'open(door1)']):
            self.open_doors.append('door1')
            self.update_display()
            messagebox.showinfo("Door Opened", "You opened the door to the next room!")
        else:
            messagebox.showwarning("Door", "The door is locked. You may need a key.")

    def move_to_room(self):
        if 'door1' in self.open_doors:
            self.current_room = 'room2'
            self.update_display()
            messagebox.showinfo("Move", "You moved to room2.")
        else:
            messagebox.showwarning("Move", "The door is locked.")

    def disarm_trap(self):
        if 'key1' in self.inventory:
            if self.run_prover9([f'disarmed(trap1)']):
                self.disarmed_traps.append('trap1')
                self.update_display()
                messagebox.showinfo("Trap Disarmed", "You disarmed the trap!")
            else:
                messagebox.showwarning("Trap", "The trap cannot be disarmed.")
        else:
            messagebox.showwarning("Trap", "You need a key to disarm this trap.")

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
