import sys
from datetime import datetime
import os

class OutputLogger:
    def __init__(self):
        self.terminal = sys.stdout
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = open(
            os.path.join(self.log_dir, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            "w",
            encoding="utf-8"
        )

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def __del__(self) -> None:
        """Clean up by closing the log file."""
        if hasattr(self, 'log_file'):
            self.log_file.close()
