# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the **CLANK! Tracker** - a Python-based gameplay monitoring tool for the CLANK! board game that uses screen capture and OCR to track game state, card usage, and scenarios.

## Project Structure

```
clank-tracker/
├── src/
│   ├── main.py              # Main application entry point
│   ├── screen_capture.py    # Screen capture functionality using PyAutoGUI/OpenCV
│   ├── ocr_processor.py     # OCR text recognition with Tesseract & EasyOCR
│   └── game_tracker.py      # Game state tracking and session management
├── tests/                   # Unit tests (pytest)
├── docs/                    # Session data and JSON files
├── assets/                  # Screenshots and captured images
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── CLAUDE.md               # This file
```

## Development Commands

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract OCR (required for text recognition)
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from GitHub releases
```

### Running the Application
```bash
# Run main application
python src/main.py

# Run individual modules for testing
python src/screen_capture.py
python src/ocr_processor.py
python src/game_tracker.py
```

### Testing and Development
```bash
# Run tests
pytest tests/

# Code formatting
black src/

# Linting
flake8 src/
```

## Architecture Overview

### Core Components

1. **Screen Capture (`screen_capture.py`)**
   - Uses PyAutoGUI for screen capture automation
   - OpenCV for image preprocessing and computer vision
   - Captures full screen, regions, or game-specific areas
   - Preprocesses images for optimal OCR results

2. **OCR Processor (`ocr_processor.py`)**
   - Dual OCR engine approach: Tesseract + EasyOCR
   - Specialized card name extraction with confidence scoring
   - Text cleaning and validation for game-specific content
   - CLANK! card keyword recognition and filtering

3. **Game Tracker (`game_tracker.py`)**
   - Session management with unique IDs and timestamps
   - Real-time card detection and event tracking
   - JSON-based session persistence
   - Statistics and reporting functionality
   - Scenario identification based on detected cards

4. **Main Application (`main.py`)**
   - Coordinates all components
   - Main application loop and user interface
   - Integration point for future GUI development

### Key Features

- **Multi-Engine OCR**: Uses both Tesseract and EasyOCR for improved accuracy
- **Card Database**: Extensible system for CLANK! card recognition
- **Session Persistence**: All gameplay sessions saved as JSON
- **Screenshot Management**: Automatic capture and storage
- **Scenario Detection**: Identifies game phases based on visible cards

### Technology Stack

- **Python 3.8+**: Main programming language
- **PyAutoGUI**: Screen capture and automation
- **OpenCV**: Image processing and computer vision
- **Tesseract/EasyOCR**: OCR text recognition engines
- **Pillow**: Image manipulation and processing
- **NumPy**: Numerical operations for image data
- **Matplotlib**: Visualization and plotting
- **pytest**: Testing framework

## Environment Setup

### Required System Dependencies
- **Python 3.8+**
- **Tesseract OCR**: System-level installation required
- **OpenCV dependencies**: Usually handled by pip

### Python Environment
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
- No environment variables required currently
- OCR engines auto-configured on first run
- Screen capture settings auto-detected

## Future Development Areas

1. **GUI Interface**: Real-time monitoring dashboard
2. **Enhanced OCR**: Game-specific text recognition improvements
3. **Scenario Generation**: Random scenario image creation
4. **Card Database**: Comprehensive CLANK! card catalog
5. **Analytics**: Advanced gameplay statistics and insights
6. **Multi-player Support**: Track multiple player sessions