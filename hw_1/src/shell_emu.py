import tkinter as tk
from tkinter import scrolledtext
from src.logger import Logger
from src.vfs import VirtualFileSystem

class ShellEmulator(tk.Tk):
    def __init__(self, username: str, tar_path: str, log_path: str):
        super().__init__()
        
        self.username = username
        self.fs = VirtualFileSystem()
        self.fs.load_from_tar(tar_path)
        self.logger = Logger(log_path, username)
        
        self.title(f"Shell Emulator - {username}")
        self.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create input frame
        input_frame = tk.Frame(self)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Create prompt label
        self.prompt_label = tk.Label(
            input_frame, 
            text=f"{self.username}:{self.fs.current_directory}$ "
        )
        self.prompt_label.pack(side='left')
        
        # Create input entry
        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side='left', expand=True, fill='x')
        self.input_entry.bind('<Return>', self.process_command)
        
        # Set focus to input
        self.input_entry.focus()
        
    def update_prompt(self):
        self.prompt_label.config(
            text=f"{self.username}:{self.fs.current_directory}$ "
        )
        
    def process_command(self, event):
        command = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not command:
            return
            
        # Log the command
        self.logger.log(command.split()[0], " ".join(command.split()[1:]))
        
        # Display command in text area
        self.text_area.insert(
            tk.END, 
            f"{self.username}:{self.fs.current_directory}$ {command}\n"
        )
        
        # Process command
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]
        
        if cmd == "exit":
            self.quit()
        elif cmd == "ls":
            path = args[0] if args else ""
            files = self.fs.ls(path)
            self.text_area.insert(tk.END, "  ".join(files) + "\n")
        elif cmd == "cd":
            if not args:
                self.text_area.insert(tk.END, "cd: missing directory argument\n")
            elif not self.fs.cd(args[0]):
                self.text_area.insert(tk.END, f"cd: {args[0]}: No such directory\n")
            self.update_prompt()
        elif cmd == "rm":
            if not args:
                self.text_area.insert(tk.END, "rm: missing operand\n")
            elif not self.fs.rm(args[0]):
                self.text_area.insert(tk.END, f"rm: {args[0]}: No such file or directory\n")
        elif cmd == "find":
            if len(args) < 2:
                self.text_area.insert(tk.END, "find: missing arguments\n")
            else:
                results = self.fs.find(args[0], args[1])
                for result in results:
                    self.text_area.insert(tk.END, f"{result}\n")
        else:
            self.text_area.insert(tk.END, f"command not found: {cmd}\n")
        
        # Scroll to bottom
        self.text_area.see(tk.END)