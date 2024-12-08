
from PIL import Image, ImageGrab
import time
from threading import Thread
import wowzer
from Xlib import display, X
import numpy as np
import cv2 as cv    

import sight.mana_bar as mana_bar
import fishing.fishing_agent as fishing_agent


FPS_REPORT_DELAY = 3


class MainAgent:
    def __init__(self):
        self.agents = []
        self.fishing_thread = None

        self.cur_img = None
        self.cur_imgHSV = None

        self.zone = "Feralas"
        self.time = "day"


def update_screen(agent):
    """
    Captures the screen continuously, updates the agent's current image in both
    BGR and HSV formats, and reports FPS periodically.

    Args:
        agent (object): An instance of the MainAgent class.
    """
    print("Starting computer vision screen update...")

    # Try to determine screen resolution
    try:
        screen = ImageGrab.grab()
        width, height = screen.size
        print("Detected display resolution: {} x {}".format(width, height))
    except Exception as e:
        print(f"Error detecting screen resolution: {e}")
        return

    # Initialize timing variables
    loop_time = time.time()
    fps_print_time = time.time()

    while True:
        try:
            # Capture screen
            screenshot = ImageGrab.grab()
            screenshot = np.array(screenshot)

            # Convert color formats
            screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
            screenshotHSV = cv.cvtColor(screenshot, cv.COLOR_BGR2HSV)

            # Update agent's current images
            agent.cur_img = screenshot
            agent.cur_imgHSV = screenshotHSV

            # Calculate and print FPS periodically
            cur_time = time.time()
            if cur_time - fps_print_time >= FPS_REPORT_DELAY:
                fps = 1 / (cur_time - loop_time)
                print('FPS: {:.2f}'.format(fps))
                fps_print_time = cur_time

            loop_time = cur_time

            # Allow OpenCV to process events (necessary for OpenCV functions)
            if cv.waitKey(1) == ord('q'):
                print("Exiting screen update loop.")
                break

        except Exception as e:
            print(f"Error during screen update: {e}")
            break

def print_menu():
    print('Enter a command:')
    print('\tS\tStart main AI agent screen capture.')
    print('\tZ\tSet zone')
    print('\tF\tStart fishing.')
    print('\tQ\tQuit wowzer.')

def run():
    main_agent = MainAgent()

    print_menu()
    while True:
        user_input = input()
        user_input = str.lower(user_input).strip()

        if user_input == 's':
            update_screen_thread = Thread(
                target=update_screen, 
                args=(main_agent,), 
                name="update screen thread",
                daemon=True)
            update_screen_thread.start()

        elif user_input == 'f':        
            agent = fishing_agent.FishingAgent(main_agent)
            agent.run()

        elif user_input == 'z':
            print('Enter zone name:')
            print('\tOptions:')
            print('\t\tDustwallow')
            print('\t\tFeralas')
            main_agent.zone = input().title().strip()

        elif user_input == 'q':
            print("Shutting down wowzer.")
            break       
        
        else:
            print("Invalid entry.")
            print_menu()

    print("Done.")
    
if __name__ == '__main__':
    wowzer.run()
