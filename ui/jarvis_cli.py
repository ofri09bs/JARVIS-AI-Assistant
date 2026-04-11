import sys
import time
import os
from core import jarvis_brain
import threading
import queue
from core.jarvis_brain import notification_queue

# ANSI color codes for terminal styling
COLOR_CYAN = '\033[96m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'

def print_banner():
    # Print a welcome banner for the CLI
    banner = f"""{COLOR_CYAN}
    ====================================================
           J.A.R.V.I.S. - Command Line Interface
    ====================================================
    {COLOR_RESET}"""
    print(banner)

def print_help():
    # Print the available built-in CLI commands
    help_text = f"""
    {COLOR_YELLOW}[System Help Menu]{COLOR_RESET}
    - Type your request normally to interact with Jarvis.
    - 'help'  : Show this menu.
    - 'clear' : Clear the terminal screen.
    - 'exit', 'quit', 'close' : Terminate the session.
    """
    print(help_text)

def clear_screen():
    # Clear the terminal screen dynamically based on the OS
    os.system('cls' if os.name == 'nt' else 'clear')

def cli_queue_listener():
    # Infinite loop that checks the queue while the user is typing
    while True:
        try:
            task = notification_queue.get_nowait()
            if task["type"] == "speak":
                message = task["message"]
                
                print(f"\n{COLOR_GREEN}Jarvis: {COLOR_RESET}{message}") 
                print("You: ", end="", flush=True)  # Re-print the input prompt so the user knows they can still type
                
        except queue.Empty:
            pass
            
        time.sleep(0.5)

def main():
    clear_screen()
    print_banner()
    
    # Initialize the core brain memory before taking inputs
    print(f"{COLOR_YELLOW}Initializing Jarvis core systems...{COLOR_RESET}")
    jarvis_brain.initialize_memory()
    print(f"{COLOR_GREEN}Systems online. Awaiting your command, Sir.{COLOR_RESET}\n")

    # Start the background thread to listen for notifications while the user is typing
    threading.Thread(target=cli_queue_listener, daemon=True).start()

    # Main interaction loop
    while True:
        try:
            # Get user input with a styled prompt
            user_input = input(f"{COLOR_CYAN}You: {COLOR_RESET}").strip()
            
            # Skip processing if the input is completely empty
            if not user_input:
                continue
                
            command_lower = user_input.lower()
            
            # Handle hardcoded CLI system commands
            if command_lower in ['exit', 'quit', 'close']:
                print(f"\n{COLOR_GREEN}Powering down systems. Goodbye, Sir.{COLOR_RESET}")
                break
                
            elif command_lower == 'help':
                print_help()
                continue
                
            elif command_lower == 'clear':
                clear_screen()
                continue

            # Start the execution timer
            start_time = time.time()
            
            # Send the input to the brain for processing
            response = jarvis_brain.process_user_input(user_input)
            
            # Calculate total elapsed time
            elapsed_time = time.time() - start_time
            if not response == "":
            # Print the final response and the performance metric
                print(f"{COLOR_GREEN}Jarvis: {COLOR_RESET}{response}")
            #print(f"{COLOR_YELLOW}[Executed in {elapsed_time:.2f}s]{COLOR_RESET}\n")

        except KeyboardInterrupt:
            # Handle Ctrl+C exit gracefully without crashing the console
            print(f"\n{COLOR_RED}[Interrupt sequence detected]. Shutting down. Goodbye, Sir.{COLOR_RESET}")
            sys.exit(0)
            
        except Exception as e:
            # Catch unexpected errors to keep the loop running
            print(f"\n{COLOR_RED}[System Error]: {str(e)}{COLOR_RESET}\n")

if __name__ == "__main__":
    main()