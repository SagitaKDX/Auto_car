import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import time
import threading
from pathfinding_car import CarPathfinder
from typing import List, Tuple, Optional

class InteractivePathfinder:
    def __init__(self, grid_file: str = 'floor2.csv'):
        self.root = tk.Tk()
        self.root.title("🚗 Interactive Car Pathfinder - Enhanced")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        
        self.pathfinder = CarPathfinder(grid_file)
        self.grid = self.pathfinder.grid
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        
        self.start_pos = None
        self.end_pos = None
        self.current_path = None
        self.mode = "obstacle"
        self.is_dragging = False
        self.last_pos = None
        
        self.zoom_level = 1.0
        self.base_cell_size = min(500 // self.rows, 500 // self.cols)
        self.base_cell_size = max(self.base_cell_size, 8)
        self.cell_size = int(self.base_cell_size * self.zoom_level)
        
        self.animation_speed = 50
        self.path_animation_running = False
        
        self.stats = {
            'paths_found': 0,
            'total_steps': 0,
            'obstacles_modified': 0
        }
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
    def setup_styles(self):
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        self.style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Stats.TLabel', font=('Arial', 9), foreground='#34495e')
        self.style.configure('Mode.TRadiobutton', font=('Arial', 10))
        
        self.colors = {
            'free': '#ecf0f1',
            'obstacle': '#2c3e50',
            'start': '#2ecc71',
            'end': '#e74c3c',
            'path': '#3498db',
            'path_animated': '#f39c12',
            'grid_line': '#bdc3c7',
            'hover': '#95a5a6'
        }
        
    def setup_keyboard_shortcuts(self):
        self.root.bind('<Key-1>', lambda e: self.set_mode('obstacle'))
        self.root.bind('<Key-2>', lambda e: self.set_mode('start'))
        self.root.bind('<Key-3>', lambda e: self.set_mode('end'))
        self.root.bind('<Control-f>', lambda e: self.find_path())
        self.root.bind('<Control-r>', lambda e: self.reset_grid())
        self.root.bind('<Control-s>', lambda e: self.save_grid())
        self.root.bind('<Control-o>', lambda e: self.load_grid())
        self.root.bind('<plus>', lambda e: self.zoom_in())
        self.root.bind('<minus>', lambda e: self.zoom_out())
        self.root.focus_set()
        
    def set_mode(self, mode):
        self.mode_var.set(mode)
        self.change_mode()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, text="🚗 Interactive Car Pathfinder", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(status_frame, text="Ready", 
                                     font=('Arial', 10), foreground='green')
        self.status_label.pack()
        
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(mode_frame, text="Mode:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.mode_var = tk.StringVar(value="obstacle")
        
        modes = [
            ("🔧 Edit Obstacles (1)", "obstacle"),
            ("🟢 Set Start (2)", "start"),
            ("🔴 Set End (3)", "end")
        ]
        
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, 
                           value=value, command=self.change_mode, 
                           style='Mode.TRadiobutton').pack(anchor=tk.W, pady=2)
        
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(action_frame, text="Actions:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        button_config = {'width': 12, 'style': 'Accent.TButton'}
        
        self.find_path_btn = ttk.Button(action_frame, text="🔍 Find Path", 
                                       command=self.find_path_animated, **button_config)
        self.find_path_btn.pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="🧹 Clear Path", 
                  command=self.clear_path, **button_config).pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="🔄 Reset Grid", 
                  command=self.reset_grid, **button_config).pack(pady=2, fill=tk.X)
        
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(file_frame, text="File Operations:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        ttk.Button(file_frame, text="📁 Load Grid", 
                  command=self.load_grid, **button_config).pack(pady=2, fill=tk.X)
        
        ttk.Button(file_frame, text="💾 Save Grid", 
                  command=self.save_grid, **button_config).pack(pady=2, fill=tk.X)
        
        ttk.Button(file_frame, text="📊 Export Path", 
                  command=self.export_path, **button_config).pack(pady=2, fill=tk.X)
        
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(side=tk.LEFT)
        
        ttk.Label(zoom_frame, text="View:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        zoom_controls = ttk.Frame(zoom_frame)
        zoom_controls.pack(fill=tk.X)
        
        ttk.Button(zoom_controls, text="🔍+", command=self.zoom_in, width=4).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(zoom_controls, text="🔍-", command=self.zoom_out, width=4).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(zoom_controls, text="🔍=", command=self.zoom_reset, width=4).pack(side=tk.LEFT)
        
        self.zoom_label = ttk.Label(zoom_frame, text=f"Zoom: {int(self.zoom_level*100)}%", 
                                   font=('Arial', 9))
        self.zoom_label.pack(pady=2)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        info_frame = ttk.Frame(left_panel)
        info_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, text="Click on grid to edit. Select mode first.", 
                                   font=("Arial", 10), foreground='#7f8c8d')
        self.info_label.pack(side=tk.LEFT)
        
        self.coords_label = ttk.Label(info_frame, text="", font=("Arial", 10, "bold"), 
                                     foreground='#2980b9')
        self.coords_label.pack(side=tk.RIGHT)
        
        canvas_container = ttk.Frame(left_panel)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container, bg=self.colors['free'], 
                               highlightthickness=1, highlightbackground='#bdc3c7')
        
        scrollbar_v = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar_v.set)
        
        scrollbar_h = ttk.Scrollbar(left_panel, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=scrollbar_h.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        directions_frame = ttk.LabelFrame(right_panel, text="📋 Navigation Instructions", padding=10)
        directions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.directions_text = tk.Text(directions_frame, width=30, height=20, 
                                      font=("Consolas", 9), state=tk.DISABLED,
                                      bg='#f8f9fa', fg='#2c3e50')
        
        directions_scroll = ttk.Scrollbar(directions_frame, command=self.directions_text.yview)
        directions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.directions_text.configure(yscrollcommand=directions_scroll.set)
        self.directions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        stats_frame = ttk.LabelFrame(right_panel, text="📊 Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_labels = {}
        for key in ['paths_found', 'total_steps', 'obstacles_modified']:
            label = ttk.Label(stats_frame, text="", style='Stats.TLabel')
            label.pack(anchor=tk.W, pady=2)
            self.stats_labels[key] = label
        
        self.update_stats_display()
        
        legend_frame = ttk.LabelFrame(right_panel, text="🎨 Legend", padding=10)
        legend_frame.pack(fill=tk.X)
        
        legend_items = [
            ("⬜ Free space", self.colors['free']),
            ("⬛ Obstacle", self.colors['obstacle']), 
            ("🟢 Start point", self.colors['start']),
            ("🔴 End point", self.colors['end']),
            ("🟦 Path", self.colors['path'])
        ]
        
        for text, color in legend_items:
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, pady=1)
            
            color_box = tk.Frame(frame, width=15, height=15, bg=color, relief='solid', bd=1)
            color_box.pack(side=tk.LEFT, padx=(0, 8))
            
            ttk.Label(frame, text=text, font=("Arial", 9)).pack(side=tk.LEFT)
        
        shortcuts_frame = ttk.LabelFrame(right_panel, text="⌨️ Shortcuts", padding=5)
        shortcuts_frame.pack(fill=tk.X, pady=(10, 0))
        
        shortcuts = [
            "1/2/3: Change mode",
            "Ctrl+F: Find path",
            "Ctrl+R: Reset grid", 
            "+/-: Zoom in/out"
        ]
        
        for shortcut in shortcuts:
            ttk.Label(shortcuts_frame, text=shortcut, font=("Arial", 8)).pack(anchor=tk.W)
        
        self.draw_grid()
        
    def update_status(self, message, color='black'):
        self.status_label.config(text=message, foreground=color)
        self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground='green'))
        
    def update_stats_display(self):
        self.stats_labels['paths_found'].config(text=f"Paths Found: {self.stats['paths_found']}")
        self.stats_labels['total_steps'].config(text=f"Total Steps: {self.stats['total_steps']}")
        self.stats_labels['obstacles_modified'].config(text=f"Obstacles Modified: {self.stats['obstacles_modified']}")
        
    def zoom_in(self):
        if self.zoom_level < 3.0:
            self.zoom_level *= 1.2
            self.update_zoom()
            
    def zoom_out(self):
        if self.zoom_level > 0.3:
            self.zoom_level /= 1.2
            self.update_zoom()
            
    def zoom_reset(self):
        self.zoom_level = 1.0
        self.update_zoom()
        
    def update_zoom(self):
        self.cell_size = max(int(self.base_cell_size * self.zoom_level), 3)
        self.zoom_label.config(text=f"Zoom: {int(self.zoom_level*100)}%")
        self.draw_grid()
        
    def change_mode(self):
        self.mode = self.mode_var.get()
        mode_text = {
            "obstacle": "🔧 Click/drag to toggle obstacles (Black = blocked, White = free)",
            "start": "🟢 Click to set start position",
            "end": "🔴 Click to set end position"
        }
        self.info_label.config(text=mode_text.get(self.mode, ""))
        
    def on_mouse_move(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.coords_label.config(text=f"Position: ({row}, {col})")
        
    def on_mouse_leave(self, event):
        self.coords_label.config(text="")
        
    def on_canvas_click(self, event):
        self.is_dragging = True
        self.handle_canvas_interaction(event)
        
    def on_canvas_drag(self, event):
        if self.is_dragging and self.mode == "obstacle":
            self.handle_canvas_interaction(event)
        
    def on_canvas_release(self, event):
        self.is_dragging = False
        self.last_pos = None
        
    def handle_canvas_interaction(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
            
        if self.mode == "obstacle":
            if self.last_pos != (row, col):
                self.grid[row][col] = 1 - self.grid[row][col]
                self.pathfinder.grid = self.grid
                self.stats['obstacles_modified'] += 1
                self.update_stats_display()
                self.last_pos = (row, col)
                
        elif self.mode == "start":
            if self.grid[row][col] == 1:
                messagebox.showwarning("Invalid Position", "Cannot set start on obstacle!")
                return
            self.start_pos = (row, col)
            self.update_status("Start position set", 'green')
            
        elif self.mode == "end":
            if self.grid[row][col] == 1:
                messagebox.showwarning("Invalid Position", "Cannot set end on obstacle!")
                return
            self.end_pos = (row, col)
            self.update_status("End position set", 'green')
            
        self.clear_path()
        self.draw_grid()
        
    def draw_grid(self):
        self.canvas.delete("all")
        
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = self.colors['free']
                if self.grid[row][col] == 1:
                    color = self.colors['obstacle']
                
                if self.current_path and (row, col) in self.current_path:
                    if (row, col) != self.start_pos and (row, col) != self.end_pos:
                        color = self.colors['path']
                
                if self.start_pos == (row, col):
                    color = self.colors['start']
                elif self.end_pos == (row, col):
                    color = self.colors['end']
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, 
                                           outline=self.colors['grid_line'], width=1)
        
    def find_path_animated(self):
        if self.path_animation_running:
            return
            
        if not self.start_pos:
            messagebox.showwarning("Missing Start", "Please set a start position first!")
            return
        if not self.end_pos:
            messagebox.showwarning("Missing End", "Please set an end position first!")
            return
            
        self.find_path_btn.config(state='disabled', text="🔄 Finding...")
        self.update_status("Calculating path...", 'orange')
        
        def pathfind_thread():
            self.pathfinder.grid = self.grid
            path = self.pathfinder.astar_pathfind(self.start_pos, self.end_pos)
            
            self.root.after(0, lambda: self.handle_path_result(path))
            
        threading.Thread(target=pathfind_thread, daemon=True).start()
        
    def handle_path_result(self, path):
        self.find_path_btn.config(state='normal', text="🔍 Find Path")
        
        if path:
            self.current_path = path
            self.stats['paths_found'] += 1
            self.stats['total_steps'] += len(path)
            self.update_stats_display()
            
            directions = self.pathfinder.get_directions(path)
            
            self.directions_text.config(state=tk.NORMAL)
            self.directions_text.delete(1.0, tk.END)
            
            header = f"🎯 PATH FOUND!\n{'='*25}\n"
            self.directions_text.insert(tk.END, header)
            self.directions_text.insert(tk.END, f"📏 Length: {len(path)} steps\n")
            self.directions_text.insert(tk.END, f"⏱️ From: {self.start_pos}\n")
            self.directions_text.insert(tk.END, f"🏁 To: {self.end_pos}\n\n")
            
            self.directions_text.insert(tk.END, "🧭 NAVIGATION:\n")
            self.directions_text.insert(tk.END, "-" * 20 + "\n")
            
            direction_icons = {
                "UP": "⬆️", "DOWN": "⬇️", 
                "LEFT": "⬅️", "RIGHT": "➡️"
            }
            
            for i, direction in enumerate(directions, 1):
                icon = direction_icons.get(direction, "❓")
                self.directions_text.insert(tk.END, f"{i:2d}. {icon} {direction}\n")
                
            self.directions_text.insert(tk.END, f"\n📍 COORDINATES:\n")
            self.directions_text.insert(tk.END, "-" * 15 + "\n")
            for i, pos in enumerate(path):
                self.directions_text.insert(tk.END, f"{i:2d}. {pos}\n")
                
            self.directions_text.config(state=tk.DISABLED)
            
            self.animate_path(path)
            self.update_status(f"Path found! {len(path)} steps", 'green')
        else:
            messagebox.showerror("No Path", "❌ No path found! The destination is unreachable.")
            self.update_status("No path found", 'red')
            
    def animate_path(self, path):
        self.path_animation_running = True
        self.draw_grid()
        
        def animate_step(step):
            if step >= len(path):
                self.path_animation_running = False
                return
                
            pos = path[step]
            if pos != self.start_pos and pos != self.end_pos:
                row, col = pos
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=self.colors['path_animated'], 
                                           outline=self.colors['grid_line'], width=2)
                
            self.root.after(self.animation_speed, lambda: animate_step(step + 1))
            
        animate_step(0)
        
    def find_path(self):
        self.find_path_animated()
        
    def clear_path(self):
        self.current_path = None
        self.path_animation_running = False
        self.directions_text.config(state=tk.NORMAL)
        self.directions_text.delete(1.0, tk.END)
        self.directions_text.config(state=tk.DISABLED)
        self.draw_grid()
        self.update_status("Path cleared", 'blue')
        
    def reset_grid(self):
        try:
            self.pathfinder = CarPathfinder('floor2.csv')
            self.grid = self.pathfinder.grid
            self.start_pos = None
            self.end_pos = None
            self.clear_path()
            self.update_status("Grid reset", 'blue')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset grid: {str(e)}")
        
    def load_grid(self):
        filename = filedialog.askopenfilename(
            title="Load Grid File", 
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.pathfinder = CarPathfinder(filename)
                self.grid = self.pathfinder.grid
                self.rows = len(self.grid)
                self.cols = len(self.grid[0])
                self.start_pos = None
                self.end_pos = None
                self.clear_path()
                self.draw_grid()
                self.update_status("Grid loaded successfully", 'green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load grid: {str(e)}")
                
    def save_grid(self):
        filename = filedialog.asksaveasfilename(
            title="Save Grid File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    for row in self.grid:
                        writer.writerow(row)
                self.update_status("Grid saved successfully", 'green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save grid: {str(e)}")
                
    def export_path(self):
        if not self.current_path:
            messagebox.showwarning("No Path", "Please find a path first before exporting!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Path",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write("Car Navigation Path Export\n")
                    file.write("=" * 30 + "\n\n")
                    file.write(f"Start Position: {self.start_pos}\n")
                    file.write(f"End Position: {self.end_pos}\n")
                    file.write(f"Path Length: {len(self.current_path)} steps\n\n")
                    
                    directions = self.pathfinder.get_directions(self.current_path)
                    file.write("Navigation Instructions:\n")
                    file.write("-" * 25 + "\n")
                    for i, direction in enumerate(directions, 1):
                        file.write(f"Step {i}: {direction}\n")
                        
                    file.write(f"\nPath Coordinates:\n")
                    file.write("-" * 20 + "\n")
                    for i, pos in enumerate(self.current_path):
                        file.write(f"Step {i}: {pos}\n")
                        
                self.update_status("Path exported successfully", 'green')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export path: {str(e)}")
                
    def run(self):
        self.root.mainloop()

def main():
    try:
        app = InteractivePathfinder()
        app.run()
    except FileNotFoundError:
        print("Error: floor2.csv file not found!")
        messagebox.showerror("File Not Found", "floor2.csv file not found! Please make sure the file exists.")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 