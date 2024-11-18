import csv
from datetime import datetime

class Logger:
    def __init__(self, log_path: str, username: str):
        self.log_path = log_path
        self.username = username
        
        # Create/clear log file
        with open(log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'username', 'command', 'arguments'])
    
    def log(self, command: str, arguments: str = ""):
        with open(self.log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                self.username,
                command,
                arguments
            ])