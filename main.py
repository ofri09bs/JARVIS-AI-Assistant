import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add the current directory to sys.path
import threading
from features.jarvis_cron import start_cron_loop
import subprocess
import dotenv

# Enable ANSI colors in Windows terminal
subprocess.Popen('', shell=True)  # This is a hack to enable ANSI escape codes in Windows terminals

# --- Style Constants ---
COLOR_CYAN = '\033[96m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'

def clear_screen():
    # Clear the terminal screen dynamically based on the OS
    subprocess.run(['cls'] if os.name == 'nt' else ['clear'], shell=True)

def print_main_menu():
    # ASCII Art for Jarvis
    logo = f"""{COLOR_CYAN}
      _   _  ___  ___  _   _  ___  ___ 
     | | / \ |  \ |  \ | | | |  | / __|
     | | | | |   /|   /| \ / |  | \__ \\
    _/_/ \_/ \_|_\\_|_\\ \___/  _|_|___/
    {COLOR_RESET}"""
    print(logo)
    print(f"{COLOR_YELLOW}=== Main System Initialization ==={COLOR_RESET}")
    print("Please select interface mode:")
    print(f"  [{COLOR_GREEN}1{COLOR_RESET}] Command Line Interface (CLI)")
    print(f"  [{COLOR_GREEN}2{COLOR_RESET}] Graphical User Interface (GUI)")
    print(f"  [{COLOR_RED}3{COLOR_RESET}] Exit System\n")

def run_main():
    # Main entry point for the application launcher
    threading.Thread(target=start_cron_loop, daemon=True).start()  # Start the cron loop in a separate thread
    while True:
        clear_screen()
        print_main_menu()
        choice = input(f"{COLOR_CYAN}Selection (1/2/3): {COLOR_RESET}").strip().lower()
        
        if choice in ['1', 'cli']:
            print(f"{COLOR_GREEN}Launching CLI...{COLOR_RESET}")
            from ui import jarvis_cli
            # Assuming jarvis_cli has a main() function
            if hasattr(jarvis_cli, 'main'):
                jarvis_cli.main()
            else:
                print(f"{COLOR_RED}Error: Could not find main() in jarvis_cli.{COLOR_RESET}")
                input("Press Enter to continue...")
            break
            
        elif choice in ['2', 'gui']:
            print(f"{COLOR_GREEN}Launching GUI...{COLOR_RESET}")
            from ui import jarvis_interface
            # Assuming jarvis_interface has a run_gui() function
            if hasattr(jarvis_interface, 'run_gui'):
                jarvis_interface.run_gui()
            else:
                print(f"{COLOR_RED}Error: Could not find run_gui() in jarvis_interface.{COLOR_RESET}")
                input("Press Enter to continue...")
            break
            
        elif choice in ['3', 'exit', 'quit']:
            print(f"{COLOR_YELLOW}Powering down systems. Goodbye, Sir.{COLOR_RESET}")
            sys.exit(0)
            
        else:
            print(f"{COLOR_RED}Invalid input. Please select a valid option.{COLOR_RESET}")
            input("Press Enter to try again...")

if __name__ == "__main__":
    run_main()