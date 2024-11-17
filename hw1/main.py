import os
import sys
import tarfile
import csv
import time
import argparse
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path


class Logger:
    def __init__(self, log_file, username):
        self.log_file = log_file
        self.username = username

    def log(self, action):
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), self.username, action])


class VirtualFileSystem:
    def __init__(self, tar_path):
        self.root = Path("/tmp/vfs")
        self.current_dir = self.root
        self.extract_tar(tar_path)

    def extract_tar(self, tar_path):
        if not self.root.exists():
            self.root.mkdir(parents=True)
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=self.root)

    def change_dir(self, path):
        new_path = self.current_dir.joinpath(path).resolve()
        if new_path.is_dir() and str(new_path).startswith("/private" + str(self.root)):
            self.current_dir = new_path
        else:
            print(new_path.is_dir())
            print(str(new_path).startswith(str(self.root)))
            print(str(new_path), str(self.root))
            raise FileNotFoundError(f"Directory {path} not found")

    def list_dir(self):
        return os.listdir(self.current_dir)

    def remove_file(self, filename):
        file_path = self.current_dir.joinpath(filename)
        if file_path.is_file():
            file_path.unlink()
        else:
            raise FileNotFoundError(f"File {filename} not found")

    def find(self, filename):
        result = []
        for root, _, files in os.walk(self.current_dir):
            if filename in files:
                result.append(os.path.join(root, filename))
        return result


class ShellEmulator:
    def __init__(self, vfs, logger):
        self.vfs = vfs
        self.logger = logger

    def run_command(self, command):
        try:
            if command.startswith("ls"):
                self.logger.log("ls")
                return "\n".join(self.vfs.list_dir())
            elif command.startswith("cd "):
                path = command.split(" ", 1)[1]
                self.vfs.change_dir(path)
                self.logger.log(f"cd {path}")
            elif command.startswith("rm "):
                filename = command.split(" ", 1)[1]
                self.vfs.remove_file(filename)
                self.logger.log(f"rm {filename}")
            elif command.startswith("find "):
                filename = command.split(" ", 1)[1]
                result = self.vfs.find(filename)
                self.logger.log(f"find {filename}")
                return "\n".join(result) if result else "File not found"
            elif command == "exit":
                self.logger.log("exit")
                sys.exit(0)
            else:
                return "Unknown command"
        except Exception as e:
            return str(e)
        return ""


class ShellGUI(tk.Tk):
    def __init__(self, emulator, username):
        super().__init__()
        self.emulator = emulator
        self.title(f"{username}'s Shell Emulator")
        self.geometry("600x400")

        self.output_text = scrolledtext.ScrolledText(self, state='disabled', wrap='word')
        self.output_text.pack(expand=True, fill='both')

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self, textvariable=self.input_var)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.pack(fill='x')

    def on_enter(self, event):
        command = self.input_var.get()
        self.input_var.set('')
        result = self.emulator.run_command(command)
        self.display_output(f"$ {command}\n{result}\n")

    def display_output(self, text):
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.configure(state='disabled')
        self.output_text.see(tk.END)

def parse_args():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--username', required=True, help="Username for the shell prompt")
    parser.add_argument('--vfs', required=True, help="Path to the virtual file system tar archive")
    parser.add_argument('--log', required=True, help="Path to the log file")
    return parser.parse_args()

def main():
    args = parse_args()

    vfs = VirtualFileSystem(args.vfs)
    logger = Logger(args.log, args.username)

    emulator = ShellEmulator(vfs, logger)

    gui = ShellGUI(emulator, args.username)
    gui.mainloop()

if __name__ == '__main__':
    main()
