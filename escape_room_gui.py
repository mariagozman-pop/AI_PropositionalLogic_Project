import subprocess
import sys
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
            'room2': ['puzzle2', 'trap1']
        }
        self.prover9_file = 'escape_room.in'

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

    def write_prover9_input(self, goal_statements, additional_facts=None):
       with open('current_state.in', 'w') as f:
        # Place the include directive at the top
        f.write('% Include game rules from escape_room.in\n')
        f.write(f'include "{self.prover9_file}".\n\n')

        f.write('formulas(assumptions).\n')
        f.write('% Current Game State\n')
        # Player's current location
        f.write(f'at({self.player},{self.current_room}).\n')
        # Player's inventory
        for item in self.inventory:
            f.write(f'has({self.player},{item}).\n')
        # Solved puzzles
        for puzzle in self.solved_puzzles:
            f.write(f'solved({self.player},{puzzle}).\n')
        # Open doors
        for door in self.open_doors:
            f.write(f'open({door}).\n')
        # Disarmed traps
        for trap in self.disarmed_traps:
            f.write(f'disarmed({trap}).\n')
        # Include additional facts if any
        if additional_facts:
            for fact in additional_facts:
                f.write(f'{fact}.\n')
        f.write('end_of_list.\n\n')

        f.write('formulas(goals).\n')
        # Write goal statements
        for goal in goal_statements:
            f.write(f'{goal}.\n')
        f.write('end_of_list.\n')

    def run_prover9(self):
        result = subprocess.run(['/mnt/c/Users/Calina/Desktop/ANUL3/AI/Lab6 again/LADR-2009-11A/bin/prover9', '-f', 'current_state.in'], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        if 'THEOREM PROVED' in output:
            return True
        else:
            return False

    def update_display(self):
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, f"Current Location: {self.current_room}\n")
        self.display_text.insert(tk.END, f"Inventory: {', '.join(self.inventory) if self.inventory else 'Empty'}\n\n")

        available_actions = ["Available actions:"]
        available_actions.append("Look Around")
        puzzles_in_room = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('puzzle')]
        if puzzles_in_room:
            available_actions.append("Solve Puzzle")
            self.solve_button.config(state=tk.NORMAL)
        else:
            self.solve_button.config(state=tk.DISABLED)
        if any(door in self.doors_connected_to_current_room() and door not in self.open_doors for door in self.doors_connected_to_current_room()):
            available_actions.append("Open Door")
            self.open_button.config(state=tk.NORMAL)
        else:
            self.open_button.config(state=tk.DISABLED)
        if any(door in self.open_doors for door in self.doors_connected_to_current_room()):
            available_actions.append("Move to Another Room")
            self.move_button.config(state=tk.NORMAL)
        else:
            self.move_button.config(state=tk.DISABLED)
        traps_in_room = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('trap')]
        if traps_in_room:
            available_actions.append("Disarm Trap")
            self.disarm_button.config(state=tk.NORMAL)
            # Add warning about trap
            self.display_text.insert(tk.END, "Warning: There is a trap here!\n")
        else:
            self.disarm_button.config(state=tk.DISABLED)

        self.display_text.insert(tk.END, "\n".join(available_actions))

    def look_around(self):
        items = self.items_in_rooms.get(self.current_room, [])
        if items:
            message = f"You see the following items: {', '.join(items)}"
        else:
            message = "There is nothing interesting here."
        messagebox.showinfo("Look Around", message)

    def solve_puzzle(self):
        puzzles_in_room = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('puzzle')]
        if puzzles_in_room:
            if len(puzzles_in_room) > 1:
                puzzle_to_solve = simpledialog.askstring("Solve Puzzle", f"Which puzzle do you want to solve? ({', '.join(puzzles_in_room)})")
                if puzzle_to_solve not in puzzles_in_room:
                    messagebox.showwarning("Solve Puzzle", "Invalid puzzle.")
                    return
            else:
                puzzle_to_solve = puzzles_in_room[0]

            if puzzle_to_solve == 'puzzle1':
                # Present the riddle for puzzle1
                riddle = "I speak without a mouth and hear without ears. I have nobody, but I come alive with wind. What am I?"
                answer = simpledialog.askstring("Riddle Puzzle", riddle)
                if answer and answer.strip().lower() == "echo":
                    self.solved_puzzles.append('puzzle1')
                    self.items_in_rooms[self.current_room].remove('puzzle1')
                    # Record that the player provided the correct answer
                    self.write_prover9_input([f'correct_answer({self.player},puzzle1)'])
                    # Check if you now have key1
                    self.write_prover9_input([f'has({self.player},key1)'])
                    if self.run_prover9():
                        self.inventory.append('key1')
                        messagebox.showinfo("Solve Puzzle", "Correct! You obtained key1.")
                    else:
                        messagebox.showinfo("Solve Puzzle", "You solved the puzzle but didn't get anything.")
                    self.update_display()
                else:
                    messagebox.showwarning("Riddle Puzzle", "Incorrect answer. Try again later.")
            elif puzzle_to_solve == 'puzzle2':
                # Present the riddle for puzzle2
                riddle = "I am not alive, but I grow. I don't have lungs, but I need air. What am I?"
                answer = simpledialog.askstring("Riddle Puzzle", riddle)
                if answer and answer.strip().lower() == "fire":
                    self.solved_puzzles.append('puzzle2')
                    self.items_in_rooms[self.current_room].remove('puzzle2')
                    # Record that the player provided the correct answer
                    self.write_prover9_input([f'correct_answer({self.player},puzzle2)'])
                    # Check if you now have key2
                    self.write_prover9_input([f'has({self.player},key2)'])
                    if self.run_prover9():
                        self.inventory.append('key2')
                        messagebox.showinfo("Solve Puzzle", "Correct! You obtained key2.")
                    else:
                        messagebox.showinfo("Solve Puzzle", "You solved the puzzle but didn't get anything.")
                    self.update_display()
                else:
                    messagebox.showwarning("Riddle Puzzle", "Incorrect answer. Try again later.")
        else:
            messagebox.showwarning("Solve Puzzle", "There is no puzzle to solve here.")

    def open_door(self):
        # Check which doors are connected to the current room and not yet open
        doors_to_open = [door for door in self.doors_connected_to_current_room() if door not in self.open_doors]
        if doors_to_open:
            if len(doors_to_open) > 1:
                door_to_open = simpledialog.askstring("Open Door", f"Which door do you want to open? ({', '.join(doors_to_open)})")
                if door_to_open not in doors_to_open:
                    messagebox.showwarning("Open Door", "Invalid door.")
                    return
            else:
                door_to_open = doors_to_open[0]
            # Check if you can open the door
            self.write_prover9_input([f'open({door_to_open})'])
            if self.run_prover9():
                self.open_doors.append(door_to_open)
                messagebox.showinfo("Open Door", f"You opened {door_to_open}.")
                self.update_display()
            else:
                messagebox.showwarning("Open Door", "You cannot open the door. Maybe you need a key.")
        else:
            messagebox.showwarning("Open Door", "There is no door to open here.")

    def move_to_room(self):
        # Check which rooms are accessible
        accessible_rooms = []
        for door in self.doors_connected_to_current_room():
            if door in self.open_doors:
                connected_rooms = self.get_connected_rooms(door)
                next_room = [room for room in connected_rooms if room != self.current_room][0]
                accessible_rooms.append(next_room)
        if accessible_rooms:
            if len(accessible_rooms) > 1:
                target_room = simpledialog.askstring("Move", f"Which room do you want to move to? ({', '.join(accessible_rooms)})")
                if target_room not in accessible_rooms:
                    messagebox.showwarning("Move", "Invalid room.")
                    return
            else:
                target_room = accessible_rooms[0]
            # Check if you can move to the selected room
            self.write_prover9_input([f'can_move({self.player},{self.current_room},{target_room})'])
            if self.run_prover9():
                self.current_room = target_room
                messagebox.showinfo("Move", f"You moved to {self.current_room}.")
                if self.current_room == 'exit':
                    messagebox.showinfo("Congratulations!", "You have successfully escaped the room!")
                    self.exit_game()
                else:
                    self.update_display()
            else:
                messagebox.showwarning("Move", "You cannot move to that room.")
        else:
            messagebox.showwarning("Move", "There is no accessible room to move to.")

    def disarm_trap(self):
        traps_in_room = [item for item in self.items_in_rooms.get(self.current_room, []) if item.startswith('trap')]
        if traps_in_room:
            trap_to_disarm = traps_in_room[0]  # Assuming only one trap per room
            self.write_prover9_input([f'disarmed({trap_to_disarm})'])
            if self.run_prover9():
                self.disarmed_traps.append(trap_to_disarm)
                self.items_in_rooms[self.current_room].remove(trap_to_disarm)
                messagebox.showinfo("Disarm Trap", f"You disarmed {trap_to_disarm}.")
                self.update_display()
            else:
                messagebox.showwarning("Disarm Trap", "You cannot disarm the trap. Maybe you need an item.")
        else:
            messagebox.showwarning("Disarm Trap", "There is no trap to disarm here.")

    def check_safety(self):
        # Check if the room is safe
        self.write_prover9_input([f'safe({self.player},{self.current_room})'])
        if self.run_prover9():
            messagebox.showinfo("Check Safety", "The room is safe.")
        else:
            messagebox.showinfo("Check Safety", "The room is not safe.")

    def exit_game(self):
        self.destroy()

    def doors_connected_to_current_room(self):
        # Returns a list of doors connected to the current room
        doors = []
        if self.current_room == 'room1':
            doors.append('door1')
        elif self.current_room == 'room2':
            doors.append('door1')
            doors.append('door2')
        return doors

    def get_connected_rooms(self, door):
        # Returns the rooms connected by the specified door
        if door == 'door1':
            return ['room1', 'room2']
        elif door == 'door2':
            return ['room2', 'exit']
        else:
            return []

if __name__ == '__main__':
    game = EscapeRoomGame()
    game.mainloop()
