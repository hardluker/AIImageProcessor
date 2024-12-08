
import cv2 as cv
import numpy as np
import pyautogui
import random
import time
from threading import Thread
import os


class FishingAgent:
    def __init__(self, main_agent):
        self.main_agent = main_agent
        
        # interpolate here_path to get the path to the fishing target image
        here_path = os.path.dirname(os.path.realpath(__file__))
        self.fishing_target = None
        self.load_fishing_targets()
        self.fishing_thread = None
        self.has_swapped_hotbar = False

    #Method to load multiple fishing targets to be evaluated.
    def load_fishing_targets(self):
        here_path = os.path.dirname(os.path.abspath(__file__))  # Get the current script's directory
        target_folder = os.path.join(here_path, "assets")  # Path to the assets folder

        # Load all images in the folder
        self.fishing_targets = []
        self.target_file_names = []  # Store filenames alongside the templates
        for file_name in os.listdir(target_folder):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                image_path = os.path.join(target_folder, file_name)
                image = cv.imread(image_path)
                if image is not None:
                    self.fishing_targets.append(image)
                    self.target_file_names.append(file_name)  # Save the filename
                else:
                    print(f"Warning: Could not load image {file_name}")

        print(f"Loaded {len(self.fishing_targets)} fishing target images.")

    def find_lure(self):
        start_time = time.time()
        best_match = None
        best_max_val = -1  # Initialize to a very low value
        best_file_name = None  # Track the filename of the best match

        # Iterate through templates and their corresponding file names
        for template, file_name in zip(self.fishing_targets, self.target_file_names):
            lure_location = cv.matchTemplate(self.main_agent.cur_img, template, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(lure_location)

            # Check if this template is a better match
            if max_val > best_max_val:
                best_max_val = max_val
                best_match = max_loc  # Update the best match location
                best_file_name = file_name  # Update the best match filename

        # Use the best match
        if best_match is not None:
            self.lure_location = best_match
            print(f"Best match found in file '{best_file_name}' with correlation: {best_max_val}")
            self.move_to_lure()
        else:
            print("No suitable match found.")

    def cast_lure(self):
        print("Casting!...")
        self.fishing = True
        self.cast_time = time.time()
        pyautogui.press('1')
        sleep_time = random.uniform(1, 3)
        print(f"Looking for lure in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        self.find_lure()

    def move_to_lure(self):
        if self.lure_location:
            # Add randomness to target position
            target_x = self.lure_location[0] + random.uniform(20, 30)  # Add random offset to X
            target_y = self.lure_location[1] + random.uniform(-5, 40)  # Add random offset to Y

            # Randomize duration
            duration = random.uniform(0.3, 0.7)

            # Move the mouse with random ease function
            ease_function = random.choice([pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad])
            pyautogui.moveTo(target_x, target_y, duration, ease_function)

            # Introduce a small delay to mimic human behavior
            time.sleep(random.uniform(0.05, 0.2))

            self.watch_lure()
        else:
            print("Warning: Attempted to move to lure_location, but lure_location is None (fishing_agent.py line 32)")
            return False

    def watch_lure(self):
        time_start = time.time()
        baseline = self.main_agent.cur_imgHSV[self.lure_location[1] + 25][self.lure_location[0]]  # Initial baseline
        deviation_threshold = [15, 15, 15]  # Set thresholds for [H, S, V]

        while True:
            pixel = self.main_agent.cur_imgHSV[self.lure_location[1] + 25][self.lure_location[0]]
            # Ensure proper subtraction by converting to int
            deviation = [abs(int(pixel[i]) - int(baseline[i])) for i in range(3)]

            # Check if deviation exceeds threshold or timeout occurs
            if (
                    any(deviation[i] > deviation_threshold[i] for i in range(3)) or
                    time.time() - time_start >= 30
            ):
                print("Bite detected!")
                print(f"Pixel values: {pixel}, Baseline: {baseline}, Deviation: {deviation}")
                break

            # Optionally, update baseline dynamically
            baseline = [(baseline[i] * 0.9 + pixel[i] * 0.1) for i in range(3)]

            #print(pixel)

        self.pull_line()

    def pull_line(self):
        sleep_time = random.uniform(1, 3)
        print(f"Sleeping for {sleep_time:.2f} seconds before clicking...")
        time.sleep(sleep_time)
        pyautogui.rightClick()
        time.sleep(1)
        self.run()

    def run(self):
        if self.main_agent.cur_img is None:
            print("Image capture not found!  Did you start the screen capture thread?")
            return
        sleep_time = random.uniform(1, 3)
        print(f"Starting fishing thread in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

        if self.has_swapped_hotbar is False:
            self.has_swapped_hotbar = True
            print("Switching to fishing hotbar (hotbar 4)")
            pyautogui.keyDown('ctrl')
            pyautogui.press('2')
            pyautogui.keyUp('ctrl')
            time.sleep(1)
        
        self.fishing_thread = Thread(
            target=self.cast_lure, 
            args=(),
            name="fishing thread",
            daemon=True)    
        self.fishing_thread.start()

    def find_lure_old(self):
        start_time = time.time()
        lure_location = cv.matchTemplate(self.main_agent.cur_img, self.fishing_target, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(lure_location)
        self.lure_location = max_loc
        self.move_to_lure()

    def watch_lure_old(self):
        time_start = time.time()
        while True:
            pixel = self.main_agent.cur_imgHSV[self.lure_location[1] + 25][self.lure_location[0]]
            if self.main_agent.zone == "Dustwallow":
                if pixel[0] >= 20 or pixel[1] < 60 or pixel[2] < 40 or time.time() - time_start >= 30:
                    print("Bite detected!")
                    break
            elif self.main_agent.zone == "Feralas" and self.main_agent.time == "night":
                if pixel[0] >= 70:
                    print("Bite detected!")
                    break
                if time.time() - time_start >= 30:
                    print("Fishing timeout!")
                    break
            elif self.main_agent.zone == "Stormwind":
                print("Stormwind")
                if pixel[1] >= 120 or time.time() - time_start >= 30:
                    print("Bite detected!")
                    break
            elif self.main_agent.zone == "Feralas":
                print("Feralas")
                if pixel[1] < 145 or time.time() - time_start >= 30:
                    print("Bite detected!")
                    print(f"Pixel values: {pixel}")
                    break
            print(pixel)
        self.pull_line()
