"""
CLANK! Tracker - Main application entry point

A gameplay monitoring tool for CLANK! board game that:
- Captures screen content during gameplay
- Uses OCR to read card names and game state
- Tracks scenarios and gameplay progression
- Eventually generates random scenario images
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from screen_capture import ScreenCapture
from ocr_processor import OCRProcessor
from game_tracker import GameTracker


def main():
    """Main application entry point"""
    print("🎮 CLANK! Tracker Starting...")
    
    # Initialize components
    screen_capture = ScreenCapture()
    ocr_processor = OCRProcessor()
    game_tracker = GameTracker()
    
    print("✅ Components initialized successfully")
    print("Ready to track CLANK! gameplay!")
    
    # TODO: Add main application loop
    # TODO: Add GUI or CLI interface
    # TODO: Add real-time monitoring


if __name__ == "__main__":
    main()