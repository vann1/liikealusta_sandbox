from websocket_client import WebsocketClient
import utils as utils
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from colorama import init, Fore, Style

"""MOTIONPLATFORM INTERFACE"""
class MotionPlatform_Interface():
    def __init__(self):
        self.error = False
        
    async def init(self):
        """
        Initializes logger for motionplatform_interface class and WebsocketClient object.
        Connects to websocket server.
        """
        try:
            self.logger = setup_logging("motionplatform_interface", "motionplatform_interface.log")
            self.wsclient = WebsocketClient(self.logger, identity="interface", on_message=self.handle_client_message)
            await self.wsclient.connect()
        except Exception as e:
            self.logger.error("Error while initializing motionplatfrom_interface.")

    def handle_client_message(self, message):
        """
        Handles messages recevied from server.
        """
        event = utils.extract_part("event=", message=message)
        clientmessage = utils.extract_part("message=", message=message)
        if not event:
            self.logger.error("No event specified in message.")
            return 
        if not clientmessage: 
            self.logger.error("No client message specified in message.")
            return
        elif event == "error":
            self.error = clientmessage
            

    async def rotate(self,pitch,roll):
        """
        Takes parameters pitch and roll and rotates motionplatform accordingly with given values.
        Raises ValueError if rotate frequency is too fast.
        """
        try:
            if self.error:
                self.logger.error(f"Error rotating motionplatform. Error: {self.error}")
                raise ValueError(f"Error rotating motionplatform. Error: {self.error}")
            await self.wsclient.send(f"action=rotate|pitch={pitch}|roll={roll}|")
        except Exception as e:
            self.logger.error("Error while calling rotate function.")


    
    
"""THIS IS FOR LOGGING"""        
# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output based on log level."""
    # Define color formats for different log levels
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def __init__(self, fmt, use_hyperlinks=True):
        super().__init__(fmt)
        self.use_hyperlinks = use_hyperlinks
        
        
    def format(self, record):
        try:
            # Apply the color based on the log level
            color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)  # Default to white if level not found
            if self.use_hyperlinks and record.levelno in (logging.ERROR, logging.CRITICAL):
                # Ensure the filename is an absolute path
                record.hyperlink = f"{os.path.abspath(record.pathname)}:{record.lineno}"
            else:
                record.hyperlink = f"{record.module}:{record.lineno}"
            # Format the message with color and reset
            formatted = color + super().format(record) + Style.RESET_ALL
            return formatted
        except Exception as e:
            # Fallback if path resolution fails
            record.hyperlink = f"{record.filename}:{record.lineno}"
            logging.getLogger(__name__).warning(
                f"Failed to resolve path for {record.filename}:{record.lineno}: {str(e)}"
            )
def setup_logging(name, filename, log_to_file=True):
    log_dir = "logs"
    parent_log_dir = os.path.join(Path(__file__).parent.parent.parent, "logs")
    if not os.path.exists(parent_log_dir):
        os.makedirs(parent_log_dir)
    
    log_format = '%(asctime)s - %(levelname)s - MODULE: - %(hyperlink)s - %(message)s'

    # Set up file handler
    log_file = os.path.join(parent_log_dir, filename)
    # Set up file handler (plain text, no colors or hyperlinks)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,
        backupCount=1,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    console_formatter = ColoredFormatter(log_format, use_hyperlinks=True)    
    #setup console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    # config root logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        if log_to_file:
            logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger         