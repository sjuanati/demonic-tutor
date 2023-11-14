import platform
import subprocess

from constants import NETWORKS
from dotenv import load_dotenv
from utils.logger import setup_logger
from demonic_tutor import DemonicTutor

load_dotenv()
logger = setup_logger(__name__)


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
        f"0) Change network (current: {dt.network})\n"
        f"1) Convert Timestamp to Block Number\n"
        f"2) Convert Date to Block Number\n"
        f"3) Export Log Data into csv\n"
        f"4) Call Contract function\n"
        f"9) Exit\n"
    )


if __name__ == "__main__":
    dt = None
    try:
        dt = DemonicTutor(NETWORKS["ETHEREUM"])
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
        if choice == "0":
            dt.change_network()
        elif choice == "1":
            dt.get_block_number_by_timestamp()
        elif choice == "2":
            dt.get_block_number_by_date()
        elif choice == "3":
            dt.export_log_data()
        elif choice == "4":
            dt.get_contract_data()
        elif choice == "9":
            break
        if choice in ["1", "2", "3"]:
            input("Press Enter to continue...")
