"""
Command Line Interface for CLANK! Tracker

Provides interactive CLI for testing and manual operation of the tracker.
"""

import argparse
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from screen_capture import ScreenCapture
from ocr_processor import OCRProcessor
from game_tracker import GameTracker


class ClankTrackerCLI:
    """Command line interface for CLANK! Tracker"""
    
    def __init__(self):
        """Initialize CLI components"""
        print("🎮 Initializing CLANK! Tracker CLI...")
        
        try:
            self.screen_capture = ScreenCapture()
            self.ocr_processor = OCRProcessor()
            self.game_tracker = GameTracker()
            print("✅ All components initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            sys.exit(1)
    
    def test_screen_capture(self):
        """Test screen capture functionality"""
        print("\n📸 Testing Screen Capture...")
        
        try:
            # Capture full screen
            print("  Capturing full screen...")
            screenshot = self.screen_capture.capture_full_screen()
            print(f"  ✅ Full screen captured: {screenshot.size}")
            
            # Save test screenshot
            filepath = self.screen_capture.save_screenshot(
                screenshot, "test_capture.png", "assets"
            )
            print(f"  💾 Screenshot saved: {filepath}")
            
            # Test game area capture
            print("  Capturing game area...")
            game_area = self.screen_capture.capture_game_area()
            print(f"  ✅ Game area captured: {game_area.size}")
            
        except Exception as e:
            print(f"  ❌ Screen capture failed: {e}")
    
    def test_ocr_processing(self, image_path=None):
        """Test OCR processing on screenshot or specified image"""
        print("\n🔍 Testing OCR Processing...")
        
        try:
            if image_path:
                from PIL import Image
                image = Image.open(image_path)
                print(f"  Processing image: {image_path}")
            else:
                print("  Capturing current screen for OCR...")
                image = self.screen_capture.capture_game_area()
            
            # Preprocess for OCR
            processed_image = self.screen_capture.preprocess_for_ocr(image)
            print("  ✅ Image preprocessed for OCR")
            
            # Extract text with both engines
            print("  Running Tesseract OCR...")
            tesseract_text = self.ocr_processor.extract_text_pytesseract(processed_image)
            print(f"  Tesseract result: '{tesseract_text[:100]}...'")
            
            print("  Running EasyOCR...")
            easyocr_results = self.ocr_processor.extract_text_easyocr(processed_image)
            print(f"  EasyOCR found {len(easyocr_results)} text regions")
            
            # Extract card names
            card_names = self.ocr_processor.extract_card_names(image)
            print(f"  🎴 Detected cards: {card_names}")
            
            return card_names
            
        except Exception as e:
            print(f"  ❌ OCR processing failed: {e}")
            return []
    
    def test_game_tracking(self, cards=None):
        """Test game tracking functionality"""
        print("\n📊 Testing Game Tracking...")
        
        try:
            if not cards:
                cards = ["Test Adventure", "Sample Equipment", "Skill Card"]
            
            # Track card detection
            self.game_tracker.track_card_detection(cards, "test_screenshot.png")
            print(f"  ✅ Tracked {len(cards)} cards")
            
            # Track game event
            self.game_tracker.track_game_event(
                "test_event", 
                "CLI testing session", 
                {"source": "cli", "cards_count": len(cards)}
            )
            print("  ✅ Tracked game event")
            
            # Get session stats
            stats = self.game_tracker.get_session_stats()
            print(f"  📈 Session stats:")
            print(f"    - Session ID: {stats['session_id']}")
            print(f"    - Duration: {stats['duration']}")
            print(f"    - Cards seen: {stats['unique_cards_seen']}")
            print(f"    - Events: {stats['total_events']}")
            
            return stats
            
        except Exception as e:
            print(f"  ❌ Game tracking failed: {e}")
            return None
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        print("\n🎯 Interactive CLANK! Tracker Mode")
        print("Commands: capture, ocr, track, stats, report, save, quit")
        
        while True:
            try:
                command = input("\nclank-tracker> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    print("👋 Goodbye!")
                    break
                
                elif command == "capture":
                    self.test_screen_capture()
                
                elif command == "ocr":
                    cards = self.test_ocr_processing()
                    if cards:
                        self.game_tracker.track_card_detection(cards)
                
                elif command.startswith("ocr "):
                    # OCR on specific file
                    image_path = command[4:].strip()
                    cards = self.test_ocr_processing(image_path)
                    if cards:
                        self.game_tracker.track_card_detection(cards)
                
                elif command == "track":
                    self.test_game_tracking()
                
                elif command == "stats":
                    stats = self.game_tracker.get_session_stats()
                    print("\n📊 Current Session Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                
                elif command == "report":
                    report = self.game_tracker.generate_session_report()
                    print(report)
                
                elif command == "save":
                    filepath = self.game_tracker.save_session()
                    print(f"💾 Session saved to: {filepath}")
                
                elif command == "help":
                    self.show_help()
                
                elif command == "auto":
                    self.auto_monitoring_mode()
                
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def auto_monitoring_mode(self):
        """Automatic monitoring mode - captures and processes periodically"""
        print("\n🤖 Starting automatic monitoring mode...")
        print("Press Ctrl+C to stop")
        
        interval = 5  # seconds between captures
        
        try:
            while True:
                print(f"\n🔄 Capturing and processing... (interval: {interval}s)")
                
                # Capture and process
                cards = self.test_ocr_processing()
                if cards:
                    self.game_tracker.track_card_detection(cards)
                    print(f"  📝 Session now has {len(self.game_tracker.current_session['cards_seen'])} unique cards")
                
                # Wait for next capture
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Automatic monitoring stopped")
            
            # Show final stats
            stats = self.game_tracker.get_session_stats()
            print(f"\n📊 Final session stats: {stats['unique_cards_seen']} cards, {stats['total_events']} events")
    
    def show_help(self):
        """Show available commands"""
        print("""
🎮 CLANK! Tracker CLI Commands:

Basic Testing:
  capture     - Test screen capture functionality
  ocr         - Test OCR on current screen
  ocr <file>  - Test OCR on specific image file
  track       - Test game tracking with sample data

Session Management:
  stats       - Show current session statistics
  report      - Generate detailed session report
  save        - Save current session to file

Interactive:
  auto        - Start automatic monitoring mode
  help        - Show this help message
  quit/exit   - Exit the application

Examples:
  clank-tracker> ocr screenshot.png
  clank-tracker> auto
  clank-tracker> stats
        """)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CLANK! Tracker - Board game monitoring with OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run component tests and exit"
    )
    
    parser.add_argument(
        "--image", "-i",
        type=str,
        help="Test OCR on specific image file"
    )
    
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="Start in automatic monitoring mode"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Interval for automatic monitoring (seconds)"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = ClankTrackerCLI()
    
    if args.test:
        # Run component tests
        print("🧪 Running component tests...")
        cli.test_screen_capture()
        cards = cli.test_ocr_processing(args.image)
        cli.test_game_tracking(cards)
        
        # Save test session
        filepath = cli.game_tracker.save_session()
        print(f"\n💾 Test session saved: {filepath}")
        
    elif args.auto:
        # Auto monitoring mode
        cli.auto_monitoring_mode()
        
    else:
        # Interactive mode
        cli.interactive_mode()


if __name__ == "__main__":
    main()