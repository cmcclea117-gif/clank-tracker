"""
OCR Processor Module - Handles text recognition from game screenshots
"""

import pytesseract
import easyocr
from PIL import Image
from typing import List, Dict, Tuple
import re


class OCRProcessor:
    """Handles OCR processing for reading card names and game text"""
    
    def __init__(self):
        """Initialize OCR engines"""
        # Initialize EasyOCR reader (supports multiple languages)
        self.easyocr_reader = easyocr.Reader(['en'])
        
        # Common CLANK! card name patterns and keywords
        self.card_keywords = [
            "adventure", "artifact", "companion", "equipment", "skill",
            "market", "dungeon", "major secret", "minor secret",
            "clank", "skill point", "movement", "attack", "gold"
        ]
    
    def extract_text_pytesseract(self, image: Image.Image) -> str:
        """Extract text using Tesseract OCR"""
        try:
            # Configure Tesseract for better card text recognition
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !?.,:-'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text.strip()
        except Exception as e:
            print(f"Tesseract OCR error: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Image.Image) -> List[Tuple[str, float]]:
        """Extract text using EasyOCR (returns text with confidence scores)"""
        try:
            # Convert PIL image to numpy array for EasyOCR
            import numpy as np
            img_array = np.array(image)
            
            # Extract text with bounding boxes and confidence
            results = self.easyocr_reader.readtext(img_array)
            
            # Return text and confidence pairs
            text_results = [(result[1], result[2]) for result in results]
            return text_results
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return []
    
    def extract_card_names(self, image: Image.Image) -> List[str]:
        """Extract potential card names from image"""
        card_names = []
        
        # Try both OCR engines
        tesseract_text = self.extract_text_pytesseract(image)
        easyocr_results = self.extract_text_easyocr(image)
        
        # Process Tesseract results
        if tesseract_text:
            lines = tesseract_text.split('\n')
            for line in lines:
                cleaned_line = self.clean_text(line)
                if self.is_likely_card_name(cleaned_line):
                    card_names.append(cleaned_line)
        
        # Process EasyOCR results (high confidence only)
        for text, confidence in easyocr_results:
            if confidence > 0.7:  # High confidence threshold
                cleaned_text = self.clean_text(text)
                if self.is_likely_card_name(cleaned_text):
                    card_names.append(cleaned_text)
        
        # Remove duplicates while preserving order
        unique_cards = []
        for card in card_names:
            if card not in unique_cards:
                unique_cards.append(card)
        
        return unique_cards
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\-\']', '', text)
        
        # Capitalize first letter of each word (card names are typically title case)
        text = text.title()
        
        return text.strip()
    
    def is_likely_card_name(self, text: str) -> bool:
        """Determine if extracted text is likely a card name"""
        if not text or len(text) < 3:
            return False
        
        # Check for common card keywords
        text_lower = text.lower()
        for keyword in self.card_keywords:
            if keyword in text_lower:
                return True
        
        # Check for reasonable length (most card names are 3-30 characters)
        if 3 <= len(text) <= 30:
            # Check if it contains mostly letters (not just numbers or symbols)
            letter_count = sum(1 for c in text if c.isalpha())
            if letter_count >= len(text) * 0.7:  # At least 70% letters
                return True
        
        return False
    
    def get_game_state_info(self, image: Image.Image) -> Dict[str, any]:
        """Extract general game state information from screenshot"""
        all_text = self.extract_text_pytesseract(image)
        easyocr_results = self.extract_text_easyocr(image)
        
        info = {
            "raw_text": all_text,
            "card_names": self.extract_card_names(image),
            "high_confidence_text": [text for text, conf in easyocr_results if conf > 0.8],
            "timestamp": None  # To be filled by caller
        }
        
        return info