

import sys
import pyautogui
import mss
import numpy as np
import cv2
import time
import keyboard
import threading
from bot import find_image, read_number



def checking_screen_size():
    print("pyautogui:", pyautogui.size())  # (width, height)

    with mss.MSS() as sct:
        frame = np.array(sct.grab(sct.monitors[1]))
        print("current_frame:", frame.shape[1], frame.shape[0])  # width, height

def click_at(x, y, button="left", clicks=1):
    for i in range(clicks):
        pyautogui.click(x, y, button=button, clicks=1)
        time.sleep(0.05)
    #print(f"Clicked ({x}, {y}) with {button} button")

def drop_jump_spell(point):
    keyboard.press_and_release('s')
    time.sleep(0.15)
    click_at(point[0], point[1])


def spread_clicks(point_1, point_2, number_of_clicks):
    (x1, y1) = point_1
    (x2, y2) = point_2
    x_diff = x2 - x1
    y_diff = y2 - y1
    parts_in_middle = number_of_clicks - 1
    x_part_length = x_diff / parts_in_middle
    y_part_length = y_diff / parts_in_middle

    click_at(x1, y1)
    for x in range(1, parts_in_middle+1):
        click_at(x1 + x*x_part_length, y1 + x*y_part_length)


def show_live_screen(capture_interval: float = 1.0):
    """
    Print mouse coordinates to terminal and capture a screenshot every
    capture_interval seconds into a variable. Press Q to quit.
    """
    print(f"Tracking mouse — screenshot every {capture_interval}s — press Q to quit.")
    last_capture = 0
    current_frame = None

    home_attack_button_found = False
    find_a_match_button_found = False
    attack_button_found = False
    numbers_read = False
    numbers_ok = False
    attack_done = False
    first_skip = False
    clicked_return_home = False

    # minimum_resources 
    gold_min = 700000
    elixir_min = 700000
    dark_elixir_min = 8000

    # maximum storage number
    gold_max = 31000000
    elixir_max = 31000000
    dark_elixir_max = 500000
    storage_full = False

    program_start = time.time()
    times_up = False

    base_searched_count = 0

    if len(sys.argv) == 5:
        max_run_time = int(sys.argv[1])
        gold_min = int(sys.argv[2]) * 100000
        elixir_min = int(sys.argv[3]) * 100000
        dark_elixir_min = int(sys.argv[4]) * 1000
    else:
        max_run_time = int(input("Max run time in minutes: "))
        gold_min = int(input("Min gold per raid in 100,000: ")) * 100000
        elixir_min = int(input("Min elixir per raid in 100,000: ")) * 100000
        dark_elixir_min = int(input("Min dark elixir per raid in 1,000: ")) * 1000
    
    print(f'''Default minimum resources required:
    gold: {gold_min}
    elixir: {elixir_min}
    dark elixir: {dark_elixir_min}
    ''')

    
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        while not keyboard.is_pressed("q"):
            # x, y = pyautogui.position()
            # print(f"\rMouse: ({x}, {y})   ", end="", flush=True)

            now = time.time()
            if now - last_capture >= capture_interval:
                current_frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
                last_capture = now
                
                # 1st step - click button
                if home_attack_button_found == False:
                    pos = find_image("home_attack_button", frame=current_frame)
                    if pos:
                        print(f"\nFound home_attack_button at {pos}")
                        click_at(pos[0], pos[1], clicks=1)
                        home_attack_button_found = True
                    # else:
                    #     click_at(811, 1624)
                    #     home_attack_button_found = True


                # 2nd step - click button
                if home_attack_button_found == True and find_a_match_button_found == False:
                    pos = find_image("find_a_match_button", frame=current_frame)
                    if pos:
                        print(f"\nFound find_a_match_button at {pos}")
                        click_at(pos[0], pos[1])
                        find_a_match_button_found = True
                
                # 3rd step - click button
                if (home_attack_button_found == True and find_a_match_button_found == True 
                    and attack_button_found == False):
                    pos = find_image("attack!_button", frame=current_frame)
                    if pos:
                        print(f"\nFound attack!_button at {pos}\n")
                        click_at(pos[0], pos[1])
                        attack_button_found = True
                        # don't need it with no event troops
                        # first_skip = True

                # Also need above line, Skip the first base because the ordering is different for event troops
                if first_skip == False:
                    pos = find_image("next_button", frame=current_frame)
                    if pos:
                        print(f"Found next_button at {pos}\n")
                        click_at(pos[0], pos[1])
                        print(f'base #{base_searched_count}')
                        base_searched_count += 1
                        first_skip = True


                # 4th step - read resources number
                elif (home_attack_button_found == True and find_a_match_button_found == True 
                    and attack_button_found == True and first_skip == True and 
                    numbers_read == False):
                    time.sleep(1)
                    gold = read_number((780, 525), (945, 576), current_frame)
                    elixir = read_number((780, 590), (945, 633), current_frame)
                    dark_elixir = read_number((780, 634), (945, 692), current_frame)
                    
                    # if any number is not readable, go next
                    if not(gold and elixir and dark_elixir):
                        print('Cannot read resources number')
                        pos = find_image("next_button", frame=current_frame)
                        if pos:
                            # print(f"Found next_button at {pos}\n")
                            click_at(pos[0], pos[1])
                            time.sleep(0.5)
                    
                    # if requirements are met
                    if gold and elixir and dark_elixir:
                        
                        print(f'gold: {gold}')
                        print(f'elixir: {elixir}')
                        print(f'dark_elixir: {dark_elixir}\n')

                        numbers_read = True
                        if (gold >= gold_min and
                            elixir >= elixir_min and
                            dark_elixir >= dark_elixir_min): 
                            numbers_ok = True
                            print(f'resource requirement met')
                        else:
                            # print('Resources requirements not met')
                            # print(f'Requirements:\ngold: {gold_min}\nelixir: {elixir_min}\ndark elixir: {dark_elixir_min}')
                            pos = find_image("next_button", frame=current_frame)
                            if pos:
                                # print(f"Found next_button at {pos}\n")
                                click_at(pos[0], pos[1])
                                time.sleep(0.5)
                                print(f'base #{base_searched_count}')
                                base_searched_count += 1
                            numbers_read = False

                # 5th step - skip or attack

                # Q W E R - Heros
                # A S D - Spells
                # Z - Siege Machines
                # 1,2,3,4,5,6,7 - Troops

                left = (932, 1043)
                right = (2915, 1043)
                top_left_part = (1633, 406)
                top_right_part = (2101, 386)
                bot_left_part = (1430, 1514)
                bot_right_part = (2401, 1514)
                earthquake_spell_left = (1309, 1169)
                earthquake_spell_right = (2403, 1099)
                earthquake_spell_right_center = (2133, 1128)
                jump_spell_point = (1832, 1055)

                if numbers_read == True and numbers_ok == True and attack_done == False:
                    print('Found base to attack')

                    # Event troops
                    # keyboard.press_and_release("4")
                    # spread_clicks(left, bot_left_part, 15)
                    # spread_clicks(right, bot_right_part, 15)
                    # spread_clicks(left, top_left_part, 15)
                    # spread_clicks(right, top_right_part, 15)
                    # # keyboard.press_and_release("d")
                    # # click_at(earthquake_spell_right[0], earthquake_spell_right[1], clicks=5)
                    # keyboard.press_and_release("3")
                    # spread_clicks(left, bot_left_part, 15)
                    # spread_clicks(right, bot_right_part, 15)
                    # spread_clicks(left, top_left_part, 15)
                    # spread_clicks(right, top_right_part, 15)

                    # Spells
                    keyboard.press_and_release("a")
                    time.sleep(0.1)
                    click_at(earthquake_spell_left[0], earthquake_spell_left[1], clicks=1)
                    time.sleep(1*0.06)
                    click_at(earthquake_spell_right[0], earthquake_spell_right[1], clicks=4)
                    time.sleep(4*0.06)
                    click_at(earthquake_spell_right_center[0], earthquake_spell_right_center[1], clicks=4)
                    time.sleep(4*0.06)
                    threading.Timer(20, drop_jump_spell, args=[jump_spell_point]).start()

                    # Siege Machine
                    keyboard.press_and_release("z")
                    time.sleep(0.1)
                    click_at(right[0], right[1])
                    time.sleep(0.1)

                    # Troops
                    # Valkyrie 
                    keyboard.press_and_release("1")
                    time.sleep(0.1)
                    spread_clicks(left, top_left_part, 8)
                    time.sleep(8*0.06)
                    spread_clicks(left, bot_left_part, 8)
                    time.sleep(8*0.06)
                    spread_clicks(right, bot_right_part, 10)
                    time.sleep(10*0.06)
                    spread_clicks(right, top_right_part, 10)
                    time.sleep(10*0.06)

                    # Electro Titan
                    keyboard.press_and_release("2")
                    time.sleep(0.1)
                    click_at(right[0], right[1], clicks=2)
                    time.sleep(2*0.06)

                    # Queen (first hero)
                    keyboard.press_and_release("q")
                    time.sleep(0.1)
                    click_at(right[0] - (right[0] - bot_right_part[0])/2, 
                             right[1] - (right[1] - bot_right_part[1])/2)
                    # Activate ability delayed by 6 seconds
                    threading.Timer(10, keyboard.press_and_release, args=["q"]).start()
                    
                    # Dragon Duke
                    keyboard.press_and_release("w")
                    time.sleep(0.1)
                    click_at(left[0], left[1])
                    threading.Timer(1, keyboard.press_and_release, args=["w"]).start()
                    
                    # Warden
                    keyboard.press_and_release("e")
                    # click_at(right[0] - (right[0] - bot_right_part[0])/2, 
                    #          right[1] - (right[1] - bot_right_part[1])/2)
                    time.sleep(0.1)
                    click_at(right[0], right[1])
                    threading.Timer(10, keyboard.press_and_release, args=["e"]).start()

                    # King
                    keyboard.press_and_release("r")
                    time.sleep(0.1)
                    click_at(right[0] - (right[0] - bot_right_part[0])/2, 
                             right[1] - (right[1] - bot_right_part[1])/2)

                    # Deploy the rest undeployed troops for whatever reason
                    keyboard.press_and_release("1")
                    time.sleep(0.1)
                    click_at(right[0], right[1], clicks=8)                 

                    # Click faster forward x4
                    click_at(3075, 1255, clicks=2)


                    attack_done = True
                    
                
                # 6th step - return home
                if attack_done == True:
                    print('Waiting for return home...')
                    while True:
                        current_frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
                        pos = find_image("return_home_button", frame=current_frame)
                        time.sleep(2)
                        if pos:
                            print(f"\nFound return_home_button at {pos}")
                            click_at(pos[0], pos[1])
                            clicked_return_home = True
                            time.sleep(2)

                            # If program runs more than 23 minutes, break
                            if time.time() - program_start >= max_run_time * 60:
                                times_up = True
                            
                            print(f"{round((time.time() - program_start)/60, 1)} minutes")
                            break
                
                if times_up:
                    print('Maximum run time reached')
                    break
                
                # 7th step - check storage
                if clicked_return_home == True:
                    # while True:
                    #     current_frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
                    #     time.sleep(0.5)
                    #     gold = read_number((2802, 415), (3040, 456), current_frame)
                    #     if gold:
                    #         print(f'storage gold: {gold}')

                    #     elixir = read_number((2802, 526), (3040, 564), current_frame)
                    #     if elixir:
                    #         print(f'storage elixir: {elixir}')

                    #     dark_elixir = read_number((2875, 628), (3040, 674), current_frame)
                    #     if dark_elixir:
                    #         print(f'storage dark_elixir: {dark_elixir}')
                        
                    #     # if numbers readable
                    #     if gold and elixir and dark_elixir:
                    #         # if each any resources is max, set the min to 0
                    #         if gold == gold_max:
                    #             gold_min = 0
                    #         if elixir == elixir_max:
                    #             elixir_min = 0
                    #         if dark_elixir == dark_elixir_max:
                    #             dark_elixir_min = 0

                    #         # if all resources = max
                    #         if (gold == gold_max and
                    #             elixir == elixir_max and
                    #             dark_elixir == dark_elixir_max): 
                    #             storage_full = True
                    #             break
                    #         # if resources > max -> (reread)
                    #         # if (gold > gold_max or
                    #         #     elixir > elixir_max or
                    #         #     dark_elixir > dark_elixir_max):
                    #         #     continue
                            # else:
                    # reset checkpoints
                    home_attack_button_found = False
                    find_a_match_button_found = False
                    attack_button_found = False
                    numbers_read = False
                    numbers_ok = False
                    attack_done = False
                    first_skip = False
                    clicked_return_home = False
                    # break
                
                # if storage_full == True:
                #     print('All storages full')
                #     break

            time.sleep(0.05)

    print("\nStopped.")
    

if __name__ == "__main__":
    checking_screen_size()
    show_live_screen()



