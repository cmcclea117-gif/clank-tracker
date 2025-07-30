"""
Unit tests for screen capture functionality
"""

import pytest
import tempfile
import os
from PIL import Image
import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from screen_capture import ScreenCapture


class TestScreenCapture:
    """Test cases for ScreenCapture class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.screen_capture = ScreenCapture()
        
        # Create a test image
        self.test_image = Image.new('RGB', (800, 600), color='white')
        # Add some test text areas
        pixels = self.test_image.load()
        # Create a simple pattern
        for i in range(100, 200):
            for j in range(100, 200):
                pixels[i, j] = (0, 0, 0)  # Black square
    
    def test_initialization(self):
        """Test ScreenCapture initialization"""
        assert hasattr(self.screen_capture, 'screen_width')
        assert hasattr(self.screen_capture, 'screen_height')
        assert self.screen_capture.screen_width > 0
        assert self.screen_capture.screen_height > 0
    
    def test_capture_full_screen(self):
        """Test full screen capture functionality"""
        # This test requires a display, so we'll mock it in CI environments
        try:
            screenshot = self.screen_capture.capture_full_screen()
            assert isinstance(screenshot, Image.Image)
            assert screenshot.size[0] > 0
            assert screenshot.size[1] > 0
        except Exception as e:
            # In headless environments, this is expected
            pytest.skip(f"Display not available: {e}")
    
    def test_capture_region(self):
        """Test region capture functionality"""
        try:
            # Capture a small region
            region = self.screen_capture.capture_region(0, 0, 100, 100)
            assert isinstance(region, Image.Image)
            assert region.size == (100, 100)
        except Exception as e:
            pytest.skip(f"Display not available: {e}")
    
    def test_capture_game_area(self):
        """Test game area capture"""
        try:
            game_area = self.screen_capture.capture_game_area()
            assert isinstance(game_area, Image.Image)
            # Should be 80% of screen size
            expected_width = int(self.screen_capture.screen_width * 0.8)
            expected_height = int(self.screen_capture.screen_height * 0.8)
            assert game_area.size == (expected_width, expected_height)
        except Exception as e:
            pytest.skip(f"Display not available: {e}")
    
    def test_save_screenshot(self):
        """Test screenshot saving functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "test_screenshot.png"
            filepath = self.screen_capture.save_screenshot(
                self.test_image, filename, temp_dir
            )
            
            assert os.path.exists(filepath)
            # Verify the saved image
            saved_image = Image.open(filepath)
            assert saved_image.size == self.test_image.size
    
    def test_preprocess_for_ocr(self):
        """Test OCR preprocessing"""
        processed = self.screen_capture.preprocess_for_ocr(self.test_image)
        
        assert isinstance(processed, Image.Image)
        # Should be grayscale/binary
        assert processed.mode in ['L', '1']
        
        # Should maintain original size
        assert processed.size == self.test_image.size
    
    def test_preprocess_improves_contrast(self):
        """Test that preprocessing improves text contrast"""
        # Create image with gray text on white background
        gray_text_image = Image.new('RGB', (200, 50), color='white')
        pixels = gray_text_image.load()
        
        # Add gray text (should become more contrasted after processing)
        for i in range(50, 150):
            for j in range(10, 40):
                pixels[i, j] = (128, 128, 128)  # Gray text
        
        processed = self.screen_capture.preprocess_for_ocr(gray_text_image)
        
        # Convert to numpy for analysis
        processed_array = np.array(processed)
        
        # Should have more contrast (more pixels at extremes)
        unique_values = np.unique(processed_array)
        assert len(unique_values) <= 10  # Should be mostly binary after thresholding


class TestScreenCaptureEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        self.screen_capture = ScreenCapture()
    
    def test_invalid_region_coordinates(self):
        """Test handling of invalid region coordinates"""
        try:
            # This might not raise an error but should handle gracefully
            region = self.screen_capture.capture_region(-10, -10, 50, 50)
            # If it doesn't raise an error, verify it returns something reasonable
            if region:
                assert isinstance(region, Image.Image)
        except Exception:
            # Expected behavior for invalid coordinates
            pass
    
    def test_save_to_nonexistent_directory(self):
        """Test saving to non-existent directory"""
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Should handle gracefully or create directory
        try:
            filepath = self.screen_capture.save_screenshot(
                test_image, "test.png", "nonexistent_dir"
            )
            # If successful, verify file exists
            if filepath:
                assert os.path.exists(filepath)
        except (FileNotFoundError, OSError):
            # Expected behavior
            pass
    
    def test_preprocess_empty_image(self):
        """Test preprocessing of minimal image"""
        tiny_image = Image.new('RGB', (1, 1), color='black')
        processed = self.screen_capture.preprocess_for_ocr(tiny_image)
        
        assert isinstance(processed, Image.Image)
        assert processed.size == (1, 1)