from datetime import datetime
import inspect
from typing import List
import os

def log(*msg: str) -> None:
    """
    Logs messages to log.txt, prepending the current datetime and 
    the file path of the function that called 'log'.
    """
    caller_frame = inspect.stack()[1]
    file_path = caller_frame.filename
    file_name = os.path.basename(file_path)
    
    # 3. Format the log line prefix
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Format time with milliseconds
    prefix = f"[{time_str}]\t[{file_name}]\t"
    
    # 4. Write to the log file
    with open("./log.txt", "a") as f:
        for m in msg:
            f.write(f"{prefix}{m}\n")
            



def log_empty_row():
    with open("./log.txt", "a") as f:
        f.write("\n")