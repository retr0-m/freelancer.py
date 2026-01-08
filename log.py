from datetime import datetime
import inspect
from typing import List
import os
from config import VERSION

FILE="./log.txt"

def logo():
    msg=f"""
        ███████╗██████╗ ███████╗███████╗██╗      █████╗ ███╗   ██╗ ██████╗███████╗██████╗
        ██╔════╝██╔══██╗██╔════╝██╔════╝██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗
        █████╗  ██████╔╝█████╗  █████╗  ██║     ███████║██╔██╗ ██║██║     █████╗  ██████╔╝
        ██╔══╝  ██╔══██╗██╔══╝  ██╔══╝  ██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗
        ██║     ██║  ██║███████╗███████╗███████╗██║  ██║██║ ╚████║╚██████╗███████╗██║  ██║
        ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝
                                        VERSION {VERSION}
        """
    with open(FILE, "a") as f:
        f.write(msg)
    print(msg)


def log(*msg: str) -> None:
    """
    Logs messages to log.txt, prepending:
    - timestamp with milliseconds
    - file name
    - function name
    - line number
    """

    # Caller info (1 level up the stack)
    frame = inspect.stack()[1]
    file_name = os.path.basename(frame.filename)
    func_name = frame.function
    line_no = frame.lineno

    # Timestamp
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # Prefix
    prefix = (
        f"[{time_str}]\t"
        f"[{file_name} - {func_name}():{line_no}]\t\t"
    )

    # Write log
    with open(FILE, "a", encoding="utf-8") as f:
        for m in msg:
            f.write(f"{prefix}{m}\n")

def log_fatal_error(msg):
    log(f"[FATAL ERROR]\t{msg}")


def log_empty_row():
    with open(FILE, "a") as f:
        f.write("\n")


