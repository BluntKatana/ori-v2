import logging
import os

class Logger:
    def __init__(self, name: str, log_dir: str = "logs"):
        """Initializes a logger with both file and console handlers."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s')

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}.log")

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # Stream handler (console output)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Add handlers only if they are not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger

# Usage
# log = Logger("ori_v2").get_logger()
# log.info("Hello World!")
