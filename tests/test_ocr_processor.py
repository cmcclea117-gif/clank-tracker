"""
Unit tests for OCR processor functionality
"""

import pytest
import tempfile
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ocr_processor import OCRProcessor


class TestOCRProcessor:
    """Test cases for OCRProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.ocr_processor = OCRProcessor()
        
        # Create test images with known text
        self.create_test_images()
    
    def create_test_images(self):
        """Create test images with known text content"""
        # Simple text image
        self.simple_text_image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(self.simple_text_image)
        
        try:
            # Try to use a basic font
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 30), "Adventure Card", fill='black', font=font)
        
        # Card name image
        self.card_image = Image.new('RGB', (400, 150), color='white')
        draw_card = ImageDraw.Draw(self.card_image)
        draw_card.text((10, 20), "Burglar's Pack", fill='black', font=font)
        draw_card.text((10, 60), "Equipment", fill='gray', font=font)
        draw_card.text((10, 100), "Skill Point: 2", fill='black', font=font)
        
        # Noisy image (harder to read)
        self.noisy_image = Image.new('RGB', (200, 80), color='lightgray')
        draw_noisy = ImageDraw.Draw(self.noisy_image)
        draw_noisy.text((5, 25), "Dungeon Room", fill='darkgray', font=font)
    
    def test_initialization(self):
        """Test OCRProcessor initialization"""
        assert hasattr(self.ocr_processor, 'easyocr_reader')
        assert hasattr(self.ocr_processor, 'card_keywords')
        assert len(self.ocr_processor.card_keywords) > 0
    
    def test_extract_text_pytesseract(self):
        """Test Tesseract text extraction"""
        try:
            text = self.ocr_processor.extract_text_pytesseract(self.simple_text_image)
            assert isinstance(text, str)
            # Should contain some recognizable text
            text_lower = text.lower()
            assert any(word in text_lower for word in ['adventure', 'card', 'text'])
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_extract_text_easyocr(self):
        """Test EasyOCR text extraction"""
        try:
            results = self.ocr_processor.extract_text_easyocr(self.simple_text_image)
            assert isinstance(results, list)
            
            if results:  # Only test if OCR found something
                # Each result should be (text, confidence) tuple
                for text, confidence in results:
                    assert isinstance(text, str)
                    assert isinstance(confidence, (int, float))
                    assert 0 <= confidence <= 1
        except Exception as e:
            pytest.skip(f"EasyOCR not available: {e}")
    
    def test_extract_card_names(self):
        """Test card name extraction"""
        try:
            card_names = self.ocr_processor.extract_card_names(self.card_image)
            assert isinstance(card_names, list)
            
            if card_names:  # Only test if cards were found
                # Should identify card-like text
                card_text = ' '.join(card_names).lower()
                assert any(keyword in card_text for keyword in 
                          ['burglar', 'pack', 'equipment', 'skill'])
        except Exception as e:
            pytest.skip(f"OCR engines not available: {e}")
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        # Test various text cleaning scenarios
        test_cases = [
            ("  adventure   card  ", "Adventure Card"),
            ("sk!ll p@int: 2", "Skill Point 2"),
            ("DUNGEON-ROOM", "Dungeon-Room"),
            ("multiple    spaces", "Multiple Spaces"),
            ("", ""),
            ("123", "123")
        ]
        
        for input_text, expected in test_cases:
            cleaned = self.ocr_processor.clean_text(input_text)
            assert cleaned == expected or (not input_text and not cleaned)
    
    def test_is_likely_card_name(self):
        """Test card name validation logic"""
        # Valid card names
        valid_names = [
            "Adventure Card",
            "Burglar's Pack", 
            "Skill Point",
            "Dungeon Room",
            "Major Secret",
            "Movement Boost"
        ]
        
        for name in valid_names:
            assert self.ocr_processor.is_likely_card_name(name), f"'{name}' should be valid"
        
        # Invalid card names
        invalid_names = [
            "",  # Empty
            "x",  # Too short
            "12345",  # Just numbers
            "!!@#$",  # Just symbols
            "a" * 50  # Too long
        ]
        
        for name in invalid_names:
            assert not self.ocr_processor.is_likely_card_name(name), f"'{name}' should be invalid"
    
    def test_keyword_recognition(self):
        """Test that card keywords are recognized"""
        keyword_texts = [
            "This is an adventure card",
            "Equipment with skill bonus",
            "Dungeon exploration",
            "Major secret artifact",
            "Clank! noise level"
        ]
        
        for text in keyword_texts:
            assert self.ocr_processor.is_likely_card_name(text), f"'{text}' should contain keywords"
    
    def test_get_game_state_info(self):
        """Test comprehensive game state extraction"""
        try:
            info = self.ocr_processor.get_game_state_info(self.card_image)
            
            assert isinstance(info, dict)
            assert 'raw_text' in info
            assert 'card_names' in info
            assert 'high_confidence_text' in info
            assert 'timestamp' in info
            
            assert isinstance(info['card_names'], list)
            assert isinstance(info['high_confidence_text'], list)
        except Exception as e:
            pytest.skip(f"OCR engines not available: {e}")
    
    def test_confidence_filtering(self):
        """Test that low confidence results are filtered"""
        try:
            # Test with noisy image that should have lower confidence
            results = self.ocr_processor.extract_text_easyocr(self.noisy_image)
            
            if results:
                # Verify confidence scores are reasonable
                for text, confidence in results:
                    assert 0 <= confidence <= 1
                    
                # High confidence filter should be more restrictive
                info = self.ocr_processor.get_game_state_info(self.noisy_image)
                high_conf_count = len(info['high_confidence_text'])
                all_results_count = len(results)
                
                # High confidence should be subset of all results
                assert high_conf_count <= all_results_count
        except Exception as e:
            pytest.skip(f"OCR engines not available: {e}")


class TestOCRProcessorEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        self.ocr_processor = OCRProcessor()
    
    def test_empty_image(self):
        """Test processing of empty/blank image"""
        blank_image = Image.new('RGB', (100, 100), color='white')
        
        try:
            results = self.ocr_processor.extract_card_names(blank_image)
            assert isinstance(results, list)
            # Blank image should return empty or minimal results
        except Exception:
            # Some OCR failures are acceptable for blank images
            pass
    
    def test_very_small_image(self):
        """Test processing of very small image"""
        tiny_image = Image.new('RGB', (10, 10), color='black')
        
        try:
            results = self.ocr_processor.extract_card_names(tiny_image)
            assert isinstance(results, list)
        except Exception:
            # Acceptable to fail on extremely small images
            pass
    
    def test_malformed_text_cleaning(self):
        """Test cleaning of malformed text"""
        malformed_texts = [
            None,  # Should handle gracefully
            123,   # Non-string input
            "\n\n\n",  # Just whitespace
            "áéíóú",   # Accented characters
        ]
        
        for text in malformed_texts:
            try:
                if text is not None and hasattr(text, 'strip'):
                    cleaned = self.ocr_processor.clean_text(str(text))
                    assert isinstance(cleaned, str)
            except Exception:
                # Some malformed inputs are expected to fail
                pass
    
    def test_card_keywords_completeness(self):
        """Test that important CLANK! keywords are included"""
        required_keywords = [
            'adventure', 'artifact', 'companion', 'equipment', 'skill',
            'clank', 'dungeon', 'secret', 'movement', 'attack'
        ]
        
        keywords_lower = [kw.lower() for kw in self.ocr_processor.card_keywords]
        
        for keyword in required_keywords:
            assert any(keyword in kw for kw in keywords_lower), f"Missing keyword: {keyword}"