"""
Screen Capture Module - Handles capturing game screen content
"""

import pyautogui
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import time


class ScreenCapture:
    """Handles screen capture functionality for CLANK! game monitoring"""
    
    def __init__(self):
        """Initialize screen capture settings"""
        # Disable pyautogui failsafe for automated capture
        pyautogui.FAILSAFE = False
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Screen resolution: {self.screen_width}x{self.screen_height}")
    
    def capture_full_screen(self) -> Image.Image:
        """Capture the entire screen"""
        screenshot = pyautogui.screenshot()
        return screenshot
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """Capture a specific region of the screen"""
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    
    def capture_game_area(self) -> Image.Image:
        """
        Capture the main game area (to be customized based on game layout)
        Currently captures center portion of screen
        """
        # Assume game is in center 80% of screen
        margin_x = int(self.screen_width * 0.1)
        margin_y = int(self.screen_height * 0.1)
        width = int(self.screen_width * 0.8)
        height = int(self.screen_height * 0.8)
        
        return self.capture_region(margin_x, margin_y, width, height)
    
    def save_screenshot(self, image: Image.Image, filename: str, directory: str = "assets") -> str:
        """Save screenshot to file"""
        filepath = f"{directory}/{filename}"
        image.save(filepath)
        return filepath
    
    def preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold for better text recognition
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        processed_image = Image.fromarray(thresh)
        return processed_image