import mss
import pyautogui
import cv2 as cv
import numpy as np
import time
import multiprocessing

class ScreenCaptureAgent:
    def __init__(self) -> None:
        self.img = None
        self.img_health = None
        self.img_health_HSV = None
        self.capture_process = None
        self.fps = None
        self.enable_cv_preview = True

        self.top_left = (514,771)
        self.bottom_right = (700,788)

        self.w, self.h = pyautogui.size()
        print("screen resolution w: " + str(self.w) + " h: "+str(self.h))
        self.monitor = {"top": 0, "left": 0, "width": self.w, "height": self.h}


    def capture_screen(self):
        fps_report_time = time.time()
        fps_report_delay = 4
        n_frames = 1
        with mss.mss() as sct:
            while True:
                self.img = sct.grab(monitor=self.monitor)
                self.img = np.array(self.img)

                self.img_health = self.img[
                    self.top_left[1]:self.bottom_right[1],
                    self.top_left[0]:self.bottom_right[0]       
                ]

                #converting BGR to HSV because HSV is better with characterizing 'green'
                self.img_health_HSV = cv.cvtColor(self.img_health, cv.COLOR_BGR2HSV)
                hue_pct = hue_match_pct(self.img_health_HSV, 80, 115)

                #if preview is enabled, show screencaptures at 40% of screen size
                if self.enable_cv_preview:
                    small = cv.resize(self.img, (0,0), fx=0.4, fy=0.4)

                    if self.fps is None:
                        fps_text = ""
                    else:
                        fps_text = f'FPS: {self.fps:.1f}'

                    cv.putText(
                        small,                                         
                        fps_text,
                        (20,50),
                        cv.FONT_HERSHEY_DUPLEX,
                        1,
                        (255,0,255),
                        1,
                        cv.LINE_AA
                    )

                    cv.putText(
                        small,
                        "Health: " + str(hue_match_pct(self.img_health_HSV, 80, 115)),
                        (20,100),
                        cv.FONT_HERSHEY_DUPLEX,
                        1,
                        (0,0,255),
                        1,
                        cv.LINE_AA
                    )

                    cv.imshow("computer vision", small)
                    cv.imshow("Health Bar", self.img_health)
                    cv.waitKey(3)

                elapsed_time = time.time() - fps_report_time
                if elapsed_time >= fps_report_delay: 
                    self.fps = n_frames / elapsed_time
                    print('FPS: '+str(self.fps))
                    if hue_pct < 30:
                        print("LOW HEALTH")
                        #pyautogui.press('2')
                    else:
                        print('Health: ' + str(hue_pct))
                    n_frames = 0
                    fps_report_time = time.time()
                n_frames += 1


class bcolors:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

def convert_hue(hue):
    ratio = 360/180
    return np.round(hue / ratio, 2)

def hue_match_pct(img, hue_low, hue_high):
    match_pixels = 0
    no_match_pixels = 0
    for pixel in img:
        for h, s, v, in pixel:
            if convert_hue(hue_low) <= h <= convert_hue(hue_high):
                match_pixels += 1
            else:
                no_match_pixels +=1
        total_pixels = match_pixels + no_match_pixels
        return np.round(match_pixels/total_pixels, 2)*100

def print_menu():
     print(f'Command Menu')
     print(f'\tr - run\t\tStart Screen Capture')
     print(f'\ts - stop\tStop Screen Capture')
     print(f'\tq - quit\tStop Quit the Program')

if __name__ == "__main__":
    screen_agent = ScreenCaptureAgent()
    while True:
        print_menu()
        user_input = input().strip().lower()
        if user_input == 'quit' or user_input == 'q':
            if screen_agent.capture_process is not None:
                screen_agent.capture_process.terminate()
            break
        elif user_input == 'run' or user_input == 'r':
            if screen_agent.capture_process is not None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process already running.')
                continue
            screen_agent.capture_process = multiprocessing.Process(
                target=screen_agent.capture_screen,
                args=(),
                name="screen capture process"
            )
            screen_agent.capture_process.start()

        elif user_input == 'stop' or user_input == 's':
            if screen_agent.capture_process is None:
                print(f'{bcolors.YELLOW}WARNING:{bcolors.ENDC} Capture process is not running.')
                continue 
            screen_agent.capture_process.terminate()
            screen_agent.capture_process = None
        else:
            print(f'{bcolors.RED}ERROR:{bcolors.ENDC} Invalid selection.')

print("Done.")