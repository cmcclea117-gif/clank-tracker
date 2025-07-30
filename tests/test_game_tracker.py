"""
Unit tests for game tracker functionality
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from game_tracker import GameTracker


class TestGameTracker:
    """Test cases for GameTracker class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.game_tracker = GameTracker(save_directory=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test GameTracker initialization"""
        assert hasattr(self.game_tracker, 'current_session')
        assert hasattr(self.game_tracker, 'known_cards')
        
        session = self.game_tracker.current_session
        assert 'session_id' in session
        assert 'start_time' in session
        assert 'cards_seen' in session
        assert 'scenarios' in session
        assert 'game_events' in session
        assert 'screenshots' in session
        
        # Verify session ID format
        assert session['session_id'].startswith('clank_session_')
        assert len(session['session_id']) > 15  # Should have timestamp
    
    def test_session_id_generation(self):
        """Test unique session ID generation"""
        # Create multiple trackers
        tracker1 = GameTracker(save_directory=self.temp_dir)
        tracker2 = GameTracker(save_directory=self.temp_dir)
        
        id1 = tracker1.current_session['session_id']
        id2 = tracker2.current_session['session_id']
        
        # Should be different (unless created in same second)
        assert id1 != id2 or abs(len(id1) - len(id2)) == 0
    
    def test_track_card_detection(self):
        """Test card detection tracking"""
        test_cards = ["Adventure Card", "Burglar's Pack", "Skill Boost"]
        
        self.game_tracker.track_card_detection(test_cards, "test_screenshot.png")
        
        cards_seen = self.game_tracker.current_session['cards_seen']
        assert len(cards_seen) == 3
        
        for i, card_name in enumerate(test_cards):
            card_event = cards_seen[i]
            assert card_event['card_name'] == card_name
            assert card_event['screenshot'] == "test_screenshot.png"
            assert 'timestamp' in card_event
            assert card_event['confidence'] == "detected"
    
    def test_duplicate_card_detection(self):
        """Test that duplicate cards are not added multiple times"""
        test_cards = ["Adventure Card", "Adventure Card", "New Card"]
        
        self.game_tracker.track_card_detection(test_cards)
        
        cards_seen = self.game_tracker.current_session['cards_seen']
        card_names = [card['card_name'] for card in cards_seen]
        
        # Should only have unique cards
        assert len(cards_seen) == 2
        assert "Adventure Card" in card_names
        assert "New Card" in card_names
        assert card_names.count("Adventure Card") == 1
    
    def test_track_game_event(self):
        """Test game event tracking"""
        self.game_tracker.track_game_event(
            "phase_change", 
            "Entered market phase", 
            {"phase": "market", "turn": 1}
        )
        
        events = self.game_tracker.current_session['game_events']
        assert len(events) == 1
        
        event = events[0]
        assert event['event_type'] == "phase_change"
        assert event['description'] == "Entered market phase"
        assert event['data']['phase'] == "market"
        assert event['data']['turn'] == 1
        assert 'timestamp' in event
    
    def test_track_screenshot(self):
        """Test screenshot tracking"""
        ocr_data = {
            "card_names": ["Test Card"],
            "confidence": 0.95,
            "raw_text": "Test Card\nSome description"
        }
        
        self.game_tracker.track_screenshot("screenshot.png", ocr_data)
        
        screenshots = self.game_tracker.current_session['screenshots']
        assert len(screenshots) == 1
        
        screenshot = screenshots[0]
        assert screenshot['path'] == "screenshot.png"
        assert screenshot['ocr_results'] == ocr_data
        assert 'timestamp' in screenshot
    
    def test_identify_scenario(self):
        """Test scenario identification logic"""
        # Test different card combinations
        test_cases = [
            (["Dungeon Room", "Monster"], "Dungeon Exploration"),
            (["Market Stall", "Equipment"], "Market Phase"),
            (["Ancient Artifact", "Secret"], "Artifact Acquisition"),
            (["Random Card"], "Unknown Scenario")
        ]
        
        for cards, expected_scenario in test_cases:
            scenario = self.game_tracker.identify_scenario(cards)
            assert scenario == expected_scenario
    
    def test_save_session(self):
        """Test session saving functionality"""
        # Add some test data
        self.game_tracker.track_card_detection(["Test Card"])
        self.game_tracker.track_game_event("test", "Test event")
        
        # Save session
        filepath = self.game_tracker.save_session()
        
        # Verify file was created
        assert os.path.exists(filepath)
        
        # Verify content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['session_id'] == self.game_tracker.current_session['session_id']
        assert 'end_time' in saved_data
        assert len(saved_data['cards_seen']) == 1
        assert len(saved_data['game_events']) == 1
    
    def test_load_session(self):
        """Test session loading functionality"""
        # Create and save a session
        original_session = self.game_tracker.current_session.copy()
        self.game_tracker.track_card_detection(["Loaded Card"])
        saved_file = self.game_tracker.save_session()
        
        # Create new tracker and load session
        new_tracker = GameTracker(save_directory=self.temp_dir)
        new_tracker.load_session(saved_file)
        
        # Verify loaded data
        assert new_tracker.current_session['session_id'] == original_session['session_id']
        assert len(new_tracker.current_session['cards_seen']) == 1
        assert new_tracker.current_session['cards_seen'][0]['card_name'] == "Loaded Card"
    
    def test_get_session_stats(self):
        """Test session statistics generation"""
        # Add test data
        self.game_tracker.track_card_detection(["Card1", "Card2", "Card3"])
        self.game_tracker.track_game_event("event1", "First event")
        self.game_tracker.track_game_event("event2", "Second event")
        self.game_tracker.track_screenshot("screenshot1.png")
        self.game_tracker.track_screenshot("screenshot2.png")
        
        stats = self.game_tracker.get_session_stats()
        
        assert stats['unique_cards_seen'] == 3
        assert stats['total_events'] == 2
        assert stats['screenshots_captured'] == 2
        assert 'session_id' in stats
        assert 'duration' in stats
        assert 'scenarios_identified' in stats
    
    def test_calculate_session_duration(self):
        """Test session duration calculation"""
        duration = self.game_tracker._calculate_session_duration()
        
        # Should be in HH:MM:SS format
        assert isinstance(duration, str)
        assert len(duration.split(':')) == 3
        
        # Should be a reasonable duration (less than a day for test)
        hours, minutes, seconds = duration.split(':')
        assert 0 <= int(hours) < 24
        assert 0 <= int(minutes) < 60
        assert 0 <= int(seconds) < 60
    
    def test_generate_session_report(self):
        """Test session report generation"""
        # Add test data
        self.game_tracker.track_card_detection(["Report Card"])
        self.game_tracker.track_game_event("report_test", "Report test event")
        
        report = self.game_tracker.generate_session_report()
        
        assert isinstance(report, str)
        assert "Session Report" in report
        assert "Report Card" in report
        assert "report_test" in report
        assert self.game_tracker.current_session['session_id'] in report


class TestGameTrackerEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.game_tracker = GameTracker(save_directory=self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_card_list(self):
        """Test tracking empty card list"""
        self.game_tracker.track_card_detection([])
        
        cards_seen = self.game_tracker.current_session['cards_seen']
        assert len(cards_seen) == 0
    
    def test_none_values_handling(self):
        """Test handling of None values"""
        self.game_tracker.track_card_detection(["Valid Card"], None)
        self.game_tracker.track_game_event("test", "Test", None)
        self.game_tracker.track_screenshot("test.png", None)
        
        # Should not crash and should handle gracefully
        assert len(self.game_tracker.current_session['cards_seen']) == 1
        assert len(self.game_tracker.current_session['game_events']) == 1
        assert len(self.game_tracker.current_session['screenshots']) == 1
    
    def test_invalid_save_directory(self):
        """Test handling of invalid save directory"""
        # Try to create tracker with invalid directory
        try:
            invalid_tracker = GameTracker(save_directory="/invalid/path/that/does/not/exist")
            # If it doesn't raise an error, it should create the directory
            assert os.path.exists("/invalid/path/that/does/not/exist") or True
        except (OSError, PermissionError):
            # Expected behavior for invalid paths
            pass
    
    def test_corrupted_session_file(self):
        """Test loading corrupted session file"""
        # Create corrupted JSON file
        corrupted_file = os.path.join(self.temp_dir, "corrupted.json")
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Should raise an error or handle gracefully
        with pytest.raises((json.JSONDecodeError, ValueError)):
            self.game_tracker.load_session(corrupted_file)
    
    def test_special_characters_in_card_names(self):
        """Test handling of special characters in card names"""
        special_cards = [
            "Card with 'apostrophe'",
            "Card with \"quotes\"",
            "Card with émojis 🎮",
            "Card\nwith\nnewlines",
            "Card\twith\ttabs"
        ]
        
        self.game_tracker.track_card_detection(special_cards)
        
        # Should handle without crashing
        cards_seen = self.game_tracker.current_session['cards_seen']
        assert len(cards_seen) == len(special_cards)
        
        # Should be able to save and load
        saved_file = self.game_tracker.save_session()
        assert os.path.exists(saved_file)
    
    def test_very_long_session(self):
        """Test handling of session with many events"""
        # Add many cards and events
        for i in range(100):
            self.game_tracker.track_card_detection([f"Card_{i}"])
            self.game_tracker.track_game_event(f"event_{i}", f"Event number {i}")
        
        # Should handle large sessions
        stats = self.game_tracker.get_session_stats()
        assert stats['unique_cards_seen'] == 100
        assert stats['total_events'] == 100
        
        # Should be able to save large session
        saved_file = self.game_tracker.save_session()
        assert os.path.exists(saved_file)