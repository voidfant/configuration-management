import argparse

from src.shell_emu import ShellEmulator

def parse_args():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--username', required=True, help="Username for the shell prompt")
    parser.add_argument('--vfs', required=True, help="Path to the virtual file system tar archive")
    parser.add_argument('--log', required=True, help="Path to the log file")
    return parser.parse_args()


def main():
    args = parse_args()
    app = ShellEmulator(args.username, args.vfs, args.log)
    app.mainloop()

if __name__ == "__main__":
    main()
