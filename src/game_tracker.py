"""
Game Tracker Module - Tracks CLANK! gameplay state and progression
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class GameTracker:
    """Tracks and manages CLANK! game state and progression"""
    
    def __init__(self, save_directory: str = "docs"):
        """Initialize game tracker"""
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # Game state tracking
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "cards_seen": [],
            "scenarios": [],
            "game_events": [],
            "screenshots": []
        }
        
        # Known CLANK! cards database (to be expanded)
        self.known_cards = self._load_card_database()
        
        print(f"Game tracker initialized - Session: {self.current_session['session_id']}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"clank_session_{timestamp}"
    
    def _load_card_database(self) -> Dict[str, Any]:
        """Load known card database (placeholder for now)"""
        # This will eventually load from a comprehensive card database
        return {
            "Adventure Cards": [],
            "Skill Cards": [],
            "Equipment Cards": [],
            "Artifacts": [],
            "Companions": []
        }
    
    def track_card_detection(self, card_names: List[str], screenshot_path: str = None):
        """Record detected cards in current session"""
        timestamp = datetime.now().isoformat()
        
        for card_name in card_names:
            card_event = {
                "card_name": card_name,
                "timestamp": timestamp,
                "screenshot": screenshot_path,
                "confidence": "detected"  # Could be enhanced with confidence scores
            }
            
            # Add to current session if not already seen
            if card_name not in [card["card_name"] for card in self.current_session["cards_seen"]]:
                self.current_session["cards_seen"].append(card_event)
                print(f"📄 New card detected: {card_name}")
    
    def track_game_event(self, event_type: str, description: str, data: Dict = None):
        """Track general game events"""
        event = {
            "event_type": event_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        self.current_session["game_events"].append(event)
        print(f"🎯 Game event: {event_type} - {description}")
    
    def track_screenshot(self, screenshot_path: str, ocr_results: Dict = None):
        """Track screenshot and associated OCR data"""
        screenshot_data = {
            "path": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "ocr_results": ocr_results
        }
        
        self.current_session["screenshots"].append(screenshot_data)
    
    def identify_scenario(self, detected_cards: List[str]) -> str:
        """
        Attempt to identify current scenario based on detected cards
        This is a placeholder - will be enhanced with actual scenario logic
        """
        # Basic scenario detection logic
        if any("dungeon" in card.lower() for card in detected_cards):
            return "Dungeon Exploration"
        elif any("market" in card.lower() for card in detected_cards):
            return "Market Phase"
        elif any("artifact" in card.lower() for card in detected_cards):
            return "Artifact Acquisition"
        else:
            return "Unknown Scenario"
    
    def save_session(self):
        """Save current session to file"""
        session_file = self.save_directory / f"{self.current_session['session_id']}.json"
        
        # Add end time
        self.current_session["end_time"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)
        
        print(f"💾 Session saved: {session_file}")
        return str(session_file)
    
    def load_session(self, session_file: str):
        """Load previous session from file"""
        with open(session_file, 'r') as f:
            self.current_session = json.load(f)
        
        print(f"📂 Session loaded: {session_file}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        stats = {
            "session_id": self.current_session["session_id"],
            "duration": self._calculate_session_duration(),
            "unique_cards_seen": len(self.current_session["cards_seen"]),
            "total_events": len(self.current_session["game_events"]),
            "screenshots_captured": len(self.current_session["screenshots"]),
            "scenarios_identified": len(set(self.current_session.get("scenarios", [])))
        }
        return stats
    
    def _calculate_session_duration(self) -> str:
        """Calculate session duration"""
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        end_time = datetime.now()
        
        if "end_time" in self.current_session:
            end_time = datetime.fromisoformat(self.current_session["end_time"])
        
        duration = end_time - start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    def generate_session_report(self) -> str:
        """Generate a text report of the current session"""
        stats = self.get_session_stats()
        
        report = f"""
🎮 CLANK! Tracker Session Report
================================

Session ID: {stats['session_id']}
Duration: {stats['duration']}
Cards Detected: {stats['unique_cards_seen']}
Game Events: {stats['total_events']}
Screenshots: {stats['screenshots_captured']}

📄 Cards Seen:
"""
        
        for card in self.current_session["cards_seen"]:
            report += f"  - {card['card_name']} (at {card['timestamp']})\n"
        
        report += "\n🎯 Game Events:\n"
        for event in self.current_session["game_events"][-5:]:  # Last 5 events
            report += f"  - {event['event_type']}: {event['description']}\n"
        
        return report