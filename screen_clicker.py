import pyautogui
import time
import sys

pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort

def click_at(x, y, button="left", clicks=1):
    pyautogui.click(x, y, button=button, clicks=clicks)
    print(f"Clicked ({x}, {y}) with {button} button")

def show_position():
    print("Move your mouse to find coordinates. Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"\rMouse position: X={x}, Y={y}   ", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

def main():
    print("=== Screen Clicker ===")
    print("1. Click at coordinate")
    print("2. Show current mouse position")
    print("3. Exit")
    print("Tip: Move mouse to top-left corner to abort any action (failsafe).\n")

    while True:
        choice = input("Choice: ").strip()

        if choice == "1":
            try:
                x = int(input("  X coordinate: "))
                y = int(input("  Y coordinate: "))
                button = input("  Button [left/right/middle, default=left]: ").strip() or "left"
                clicks = int(input("  Number of clicks [default=1]: ").strip() or "1")
                delay = float(input("  Delay before clicking in seconds [default=0]: ").strip() or "0")
                if delay > 0:
                    print(f"  Clicking in {delay}s...")
                    time.sleep(delay)
                click_at(x, y, button, clicks)
            except ValueError:
                print("  Invalid input.")

        elif choice == "2":
            show_position()

        elif choice == "3":
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
