import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from multiprocessing import Process, Manager, Event
from threading import Thread
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pyglet
import time
import os

def run_ursina_app(shared_commands, start_event):
    app = Ursina()

    # Create a simple cube entity
    cube = Entity(model='cube', color=color.orange, scale=(2, 2, 2))

    # Create a simple plane entity
    ground = Entity(model='plane', color=color.green, scale=(20, 20))

    # Create a player entity with first-person controls
    player = FirstPersonController()

    def run_custom_commands():
        while True:
            if start_event.is_set():
                for command in shared_commands.values():
                    try:
                        exec(command)
                    except Exception as e:
                        print(f"Error executing command: {e}")
                start_event.clear()
            time.sleep(0.1)

    # Start a thread to execute custom commands
    Thread(target=run_custom_commands, daemon=True).start()

    # Run the Ursina application
    app.run()

class ScratchClone:
    def __init__(self, root):
        self.root = root
        self.root.title("Scratch Clone")

        # Shared commands list and Python code
        self.manager = Manager()
        self.commands = self.manager.dict()
        self.python_code = ""
        self.ursina_command_event = Event()

        # Main frame to hold sidebar and code area
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar frame on the left
        self.sidebar_frame = tk.Frame(self.main_frame, width=220, bg="#4a90e2")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Code area frame
        self.code_frame = tk.Frame(self.main_frame, bg="#ffffff")
        self.code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Output area
        self.output_frame = tk.Frame(self.main_frame, width=250, bg="#e3e3e3")
        self.output_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Create sidebar blocks
        self.create_sidebar_blocks()

        # Create a canvas in the code area
        self.code_canvas = tk.Canvas(self.code_frame, bg="#ffffff", width=600, height=600)
        self.code_canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize blocks, labels, and cables
        self.blocks = []
        self.labels = []
        self.cables = []

        # Initialize dragging data
        self.drag_data = {"x": 0, "y": 0, "item": None}

        # Bind events for dragging and deleting
        self.code_canvas.bind("<Button-1>", self.on_click)
        self.code_canvas.bind("<B1-Motion>", self.on_drag)
        self.code_canvas.bind("<ButtonRelease-1>", self.on_release)
        self.code_canvas.bind("<Button-3>", self.on_right_click)

        # Output text area
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, height=30, width=30, bg="#e3e3e3")
        self.output_text.pack(padx=10, pady=10)

        # Run button
        self.run_button = tk.Button(self.main_frame, text="Run", command=self.run_commands)
        self.run_button.pack(pady=10, side=tk.BOTTOM)

        # Clear all functions button
        self.clear_button = tk.Button(self.main_frame, text="Clear All Functions", command=self.clear_all_functions)
        self.clear_button.pack(pady=5, side=tk.BOTTOM)

        # Add Python code area
        self.code_area_label = tk.Label(self.output_frame, text="Custom Python Code:", bg="#e3e3e3")
        self.code_area_label.pack(pady=5)
        self.code_area = tk.Text(self.output_frame, wrap=tk.WORD, height=10, width=30, bg="#f0f0f0")
        self.code_area.pack(padx=10, pady=5)
        self.code_area.insert(tk.END, self.python_code)

        # Save Python code button
        self.save_code_button = tk.Button(self.output_frame, text="Save Python Code", command=self.save_python_code)
        self.save_code_button.pack(pady=5)

        # Initialize Ursina process
        self.ursina_process = None
        self.start_event = self.manager.Event()

        # Inspector panel
        self.inspector_frame = tk.Frame(self.main_frame, width=220, bg="#e3e3e3")
        self.inspector_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.inspector_label = tk.Label(self.inspector_frame, text="Inspector", bg="#e3e3e3", font=("Arial", 12, "bold"))
        self.inspector_label.pack(pady=5)
        self.inspector_text = tk.Text(self.inspector_frame, wrap=tk.WORD, height=20, width=30, bg="#f0f0f0")
        self.inspector_text.pack(padx=10, pady=10)

        # Help button
        self.help_button = tk.Button(self.sidebar_frame, text="Help", command=self.show_help)
        self.help_button.pack(pady=5)

        # Undo and Redo buttons
        self.undo_button = tk.Button(self.sidebar_frame, text="Undo", command=self.undo)
        self.undo_button.pack(pady=5)
        self.redo_button = tk.Button(self.sidebar_frame, text="Redo", command=self.redo)
        self.redo_button.pack(pady=5)

        # Variable management
        self.variable_frame = tk.Frame(self.sidebar_frame, bg="#005dff")
        self.variable_frame.pack(pady=5, fill=tk.X)
        self.variable_label = tk.Label(self.variable_frame, text="Variables", bg="#005dff", fg="white", font=("Arial", 10, "bold"))
        self.variable_label.pack(pady=5)
        self.variable_list = tk.Listbox(self.variable_frame, bg="#f0f0f0", height=10, width=20)
        self.variable_list.pack(padx=10, pady=5)
        self.add_variable_button = tk.Button(self.variable_frame, text="Add Variable", command=self.add_variable)
        self.add_variable_button.pack(pady=5)

        # Custom Block Creator
        self.create_custom_block_button = tk.Button(self.sidebar_frame, text="Create Custom Block", command=self.create_custom_block)
        self.create_custom_block_button.pack(pady=5)

        # History for undo/redo
        self.history = []
        self.redo_stack = []

        # Pyglet window initialization
        self.pyglet_window = pyglet.window.Window(visible=False)
        pyglet.clock.schedule_interval(self.pyglet_update, 1/60)

    def pyglet_update(self, dt):
        # Update method for Pyglet
        pass

    def create_sidebar_blocks(self):
        # Dropdown menu for custom commands
        self.custom_command_label = tk.Label(self.sidebar_frame, text="Custom Blocks", bg="#005dff", fg="white", padx=10, pady=5, relief=tk.RAISED, font=("Arial", 10, "bold"))
        self.custom_command_label.pack(pady=5, fill=tk.X)
        
        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set("Select a Command")

        dropdown = ttk.Combobox(self.sidebar_frame, textvariable=self.dropdown_var, values=[
            "Move Forward", "Move Backward", "Turn Left", "Turn Right",
            "Repeat 10 Times", "If Touching Edge", "Wait 1 Sec", "Play Sound",
            "Change Color", "Set Size", "Go to x: y:", "Say Hello", "Hide", "Show",
            "Create Cube", "Create Sphere", "Custom Command", "If Started"
        ])
        dropdown.pack(pady=5, fill=tk.X)
        dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_select)

    def on_dropdown_select(self, event):
        selected_command = self.dropdown_var.get()
        x, y = self.code_canvas.winfo_pointerxy()
        x -= self.code_canvas.winfo_rootx()
        y -= self.code_canvas.winfo_rooty()
        block = self.code_canvas.create_rectangle(x, y, x + 180, y + 30, fill="#ff9999", tags="block")
        label = self.code_canvas.create_text(x + 90, y + 15, text=selected_command, tags="label", font=("Arial", 10, "bold"))
        self.blocks.append(block)
        self.labels.append(label)
        self.commands[block] = self.map_function_to_command(selected_command)
        self.history.append(('add', block, label, self.commands[block]))

    def map_function_to_command(self, func_name):
        command_map = {
            "Move Forward": "self.move_forward()",
            "Move Backward": "self.move_backward()",
            "Turn Left": "self.turn_left()",
            "Turn Right": "self.turn_right()",
            "Repeat 10 Times": "for _ in range(10): pass",
            "If Touching Edge": "self.if_touching_edge()",
            "Wait 1 Sec": "self.wait_1_sec()",
            "Play Sound": "self.play_sound()",
            "Change Color": "self.change_color()",
            "Set Size": "self.set_size()",
            "Go to x: y:": "self.go_to()",
            "Say Hello": "self.say_hello()",
            "Hide": "self.hide()",
            "Show": "self.show()",
            "Create Cube": "self.create_cube()",
            "Create Sphere": "self.create_sphere()",
        }
        return command_map.get(func_name, "")

    def on_click(self, event):
        # Start dragging
        item = self.code_canvas.find_closest(event.x, event.y)[0]
        if item in self.blocks:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        # Dragging logic
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.code_canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event):
        # Stop dragging
        self.drag_data["item"] = None

    def on_right_click(self, event):
        # Right-click context menu logic
        pass

    def prompt_custom_command(self, block, label):
        command = simpledialog.askstring("Custom Command", "Enter custom command:")
        if command:
            self.commands[block] = command
            self.code_canvas.itemconfig(label, text=command)
            self.history.append(('edit', block, label, command))

    def run_commands(self):
        self.python_code = self.code_area.get("1.0", tk.END).strip()
        self.clear_output()

        if self.ursina_process is None or not self.ursina_process.is_alive():
            self.ursina_process = Process(target=run_ursina_app, args=(self.commands, self.start_event))
            self.ursina_process.start()
        else:
            messagebox.showwarning("Warning", "Ursina application is already running.")

        if self.python_code:
            exec(self.python_code)
            self.output_text.insert(tk.END, "Python code executed.\n")

    def save_python_code(self):
        self.python_code = self.code_area.get("1.0", tk.END).strip()
        with open("custom_code.py", "w") as code_file:
            code_file.write(self.python_code)
        messagebox.showinfo("Info", "Python code saved successfully.")

    def clear_all_functions(self):
        for block in self.blocks:
            self.code_canvas.delete(block)
        for label in self.labels:
            self.code_canvas.delete(label)
        self.blocks.clear()
        self.labels.clear()
        self.commands.clear()
        self.history.clear()
        self.redo_stack.clear()

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

    def show_help(self):
        help_message = "Help Message: \n- Drag blocks to code area.\n- Use dropdown to add custom commands.\n- Click 'Run' to execute commands and custom code."
        messagebox.showinfo("Help", help_message)

    def undo(self):
        if self.history:
            action = self.history.pop()
            if action[0] == 'add':
                block, label, command = action[1], action[2], action[3]
                self.code_canvas.delete(block)
                self.code_canvas.delete(label)
                del self.commands[block]
                self.redo_stack.append(action)
            elif action[0] == 'edit':
                block, label, command = action[1], action[2], action[3]
                self.code_canvas.itemconfig(label, text=action[3])
                self.commands[block] = action[3]
                self.redo_stack.append(action)

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            if action[0] == 'add':
                block, label, command = action[1], action[2], action[3]
                self.blocks.append(block)
                self.labels.append(label)
                self.commands[block] = command
                self.code_canvas.create_rectangle(*self.code_canvas.coords(block), fill="#ff9999", tags="block")
                self.code_canvas.create_text(self.code_canvas.coords(block)[0] + 90, self.code_canvas.coords(block)[1] + 15, text=command, tags="label", font=("Arial", 10, "bold"))
            elif action[0] == 'edit':
                block, label, command = action[1], action[2], action[3]
                self.code_canvas.itemconfig(label, text=command)
                self.commands[block] = command

    def add_variable(self):
        variable_name = simpledialog.askstring("Variable Name", "Enter variable name:")
        if variable_name:
            self.variable_list.insert(tk.END, variable_name)

    def create_custom_block(self):
        block_name = simpledialog.askstring("Custom Block", "Enter custom block name:")
        if block_name:
            self.create_sidebar_blocks()

if __name__ == '__main__':
    root = tk.Tk()
    app = ScratchClone(root)
    root.mainloop()
