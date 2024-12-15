import subprocess
import cv2
import numpy as np
import pyautogui
import time
import pytesseract
import logging
from screeninfo import get_monitors
import keyboard 

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting the app...")

# Update the path to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\AA.exe" 

# Get the primary monitor (the first monitor in the list)
def get_primary_monitor():
    monitors = get_monitors()
    primary_monitor = monitors[0] 
    logging.info(f"Primary monitor detected: {primary_monitor}")
    return primary_monitor


def capture_screen():
    primary_monitor = get_primary_monitor()
    screenshot = pyautogui.screenshot(region=(primary_monitor.x, primary_monitor.y, primary_monitor.width, primary_monitor.height))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def find_green_areas(image):
    try:
        logging.debug("Converting image to HSV...")
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define a broader range for green color in HSV (adjust for better results)
        lower_green = np.array([50, 100, 100])  # Broader green range
        upper_green = np.array([80, 255, 255])

        logging.debug("Creating a mask for green areas...")
        green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logging.debug(f"Found {len(contours)} green areas.")
        return contours
    except Exception as e:
        logging.error(f"Error detecting green areas: {e}")
        return [], None


def preprocess_image(image):
    try:
        logging.debug("Preprocessing image for OCR...")
     
        scale_percent = 200  #
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)


        gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        binary_image = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return binary_image
    except Exception as e:
        logging.error(f"Error preprocessing image: {e}")
        return None


def check_accept_text(image, contours):
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter out small contours
        if w < 100 or h < 30:
            logging.debug(f"Ignoring small contour at ({x}, {y}, {w}, {h})")
            continue

        logging.debug(f"Checking area at ({x}, {y}, {w}, {h})")
 
        cropped = image[y:y+h, x:x+w]


        processed_image = preprocess_image(cropped)
        if processed_image is not None:
            text = pytesseract.image_to_string(processed_image, config="--psm 6 --oem 3").strip()
            logging.debug(f"OCR Result: {text}")

            if "ACCEPT" in text.upper():
                logging.info(f"Found 'ACCEPT' button at ({x}, {y}, {w}, {h})")
                return x, y, w, h
    return None, None, None, None


def template_matching(image, template_path):
    try:
   
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            logging.error(f"Failed to load template image from {template_path}")
            return None, None, None, None
        
     
        img_height, img_width = image.shape[:2]
        temp_height, temp_width = template.shape[:2]
        
        if temp_height > img_height or temp_width > img_width:
            logging.warning(f"Resizing template as it is larger than the image: {template.shape} -> ({img_height}, {img_width})")
            template = cv2.resize(template, (img_width, img_height), interpolation=cv2.INTER_LINEAR)

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

       
        result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8 
        locations = np.where(result >= threshold)

    
        for pt in zip(*locations[::-1]):
            logging.info(f"Found 'ACCEPT' button at {pt}")
            return pt[0], pt[1], template.shape[1], template.shape[0]
        
        return None, None, None, None
    except Exception as e:
        logging.error(f"Error during template matching: {e}")
        return None, None, None, None


def click_center(x, y, width, height):
    center_x = x + width // 2
    center_y = y + height // 2
    logging.info(f"Clicking at position ({center_x}, {center_y})")
    pyautogui.click(center_x, center_y)


logging.info("Press 'P' to start the scanning process.")
while True:
    try:
        if keyboard.is_pressed('p'): 
            logging.info("Key 'P' pressed. Starting the scan...")
            while True:
                try:
                    screen = capture_screen()
                    contours = find_green_areas(screen)
                    if contours:
                        x, y, w, h = check_accept_text(screen, contours)
                        if x is not None:
                            logging.info("Clicking on the 'ACCEPT' button based on green detection...")
                            click_center(x, y, w, h)
                            break
                        else:
                            logging.debug("No 'ACCEPT' button found in green areas.")
                    else:
                        logging.debug("No green areas detected.")

                    # Fallback to template matching if green detection fails
                    x, y, w, h = template_matching(screen, 'C:\\AutoAccepter\\accept.png') 
                    if x is not None:
                        logging.info("Clicking on the 'ACCEPT' button based on template matching...")
                        click_center(x, y, w, h)
                        break

                    time.sleep(1)  
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
            print("cleaning the temp files")
            time.sleep(3)
            command = 'del /q /s %temp%\\*'
            subprocess.run(command, shell=True, check=True)
            print ("cleaned the temp files, goobye and i love you.")        
            break  # Exit

        time.sleep(0.1) 
    except Exception as e:
        logging.error(f"An error occurred: {e}")
