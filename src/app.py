import os
import platform
import subprocess

from demonic_tutor import DemonicTutor
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)
INFURA_URL = os.getenv("INFURA_URL")


def clear_screen():
    """Clears the console screen"""
    # Check if the operating system is Windows
    if platform.system().lower() == "windows":
        subprocess.call("cls", shell=True)
    else:
        # Assume the OS is Unix-like and use 'clear'
        subprocess.call("clear", shell=True)


def main_menu():
    print(
        f"Welcome to the Demonic Tutor Menu\n\n"
        f"1) Convert Timestamp to Block Number\n"
        f"2) Convert Date to Block Number\n"
        f"3) Export Log Data into csv\n"
        f"4) Perform Function Call (Not Implemented)\n"
        f"0) Exit\n"
    )


if __name__ == "__main__":
    dt = None
    try:
        dt = DemonicTutor(INFURA_URL)
    except ConnectionError as ce:
        logger.error(ce)
        exit()
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        exit()

    while True:
        clear_screen()
        main_menu()
        choice = input("Please choose an option (0-3): ")
        if choice == "1":
            dt.get_block_number_by_timestamp()
        elif choice == "2":
            dt.get_block_number_by_date()
        elif choice == "3":
            dt.export_log_data()
        elif choice == "4":
            pass
        elif choice == "0":
            break
        if choice in ["1", "2", "3"]:
            input("Press Enter to continue...")
