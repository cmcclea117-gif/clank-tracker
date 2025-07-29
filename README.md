# CLANK! Tracker

A Python-based gameplay monitoring tool for the CLANK! board game that uses screen capture and OCR to track game state, card usage, and scenarios.

## 🎮 Features

- **Screen Capture**: Automatically captures game area during play
- **OCR Recognition**: Reads card names and game text using multiple OCR engines
- **Game State Tracking**: Monitors gameplay progression and events
- **Session Management**: Saves and loads game sessions with detailed statistics
- **Scenario Detection**: Identifies current game scenarios based on visible cards
- **Future**: Random scenario image generation

## 🛠️ Technology Stack

- **Python 3.8+**
- **PyAutoGUI**: Screen capture automation
- **OpenCV**: Image processing and computer vision
- **Tesseract & EasyOCR**: Text recognition engines
- **Pillow**: Image manipulation
- **NumPy & Matplotlib**: Data processing and visualization

## 📁 Project Structure

```
clank-tracker/
├── src/
│   ├── main.py              # Main application entry point
│   ├── screen_capture.py    # Screen capture functionality
│   ├── ocr_processor.py     # OCR text recognition
│   └── game_tracker.py      # Game state tracking
├── tests/                   # Unit tests
├── docs/                    # Session data and documentation
├── assets/                  # Screenshots and images
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR**
   - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

3. **Run the Tracker**
   ```bash
   python src/main.py
   ```

## 🎯 Usage

The CLANK! Tracker monitors your screen during gameplay and automatically:
- Detects card names using OCR
- Tracks game progression and events
- Saves session data for analysis
- Identifies scenarios based on visible cards

## 📊 Session Tracking

Each gaming session is tracked with:
- Unique session ID and timestamps
- All detected cards with confidence scores
- Game events and state changes
- Screenshots with OCR results
- Session statistics and reports

## 🔮 Future Enhancements

- Real-time GUI interface
- Enhanced scenario recognition
- Random scenario image generation
- Comprehensive card database
- Gameplay statistics and analytics
- Multi-player session support

## 🤝 Contributing

This is a development project. Feel free to contribute by:
- Improving OCR accuracy
- Adding new card recognition patterns
- Enhancing scenario detection logic
- Building the GUI interface

## 📄 License

This project is for educational and personal use. CLANK! is a trademark of Dire Wolf Digital.