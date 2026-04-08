"""
OCR Module
Extract text from images using OCR
"""

from typing import Optional, Union
from PIL import Image
import io
import asyncio
import numpy as np

try:
    import pytesseract
    # Set Tesseract executable path (update this to your installation path)
    # Common Windows paths:
    # C:\Program Files\Tesseract-OCR\tesseract.exe
    # C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

from app.utils.logger import logger

class OCRProcessor:
    """
    Optical Character Recognition for images
    """
    
    def __init__(self, languages: str = 'eng'):
        self.languages = languages
        self.available = TESSERACT_AVAILABLE
        
        if not self.available:
            logger.warning("Tesseract not installed. OCR will not work.")
        else:
            # Verify tesseract is actually accessible
            try:
                import subprocess
                result = subprocess.run([pytesseract.pytesseract.tesseract_cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"Tesseract OCR initialized successfully")
                else:
                    logger.warning(f"Tesseract executable found but version check failed")
                    self.available = False
            except Exception as e:
                logger.warning(f"Tesseract executable not accessible: {e}")
                self.available = False
    
    async def process_image(
        self,
        image: Union[Image.Image, bytes, str],
        preprocess: bool = True
    ) -> str:
        """
        Extract text from image
        """
        if not self.available:
            return "[OCR not available - Tesseract not installed or configured]"
        
        # Load image
        img = await self._load_image(image)
        
        if img is None:
            return ""
        
        # Preprocess if requested
        if preprocess:
            img = await self._preprocess_image(img)
        
        # Run OCR in thread pool
        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(
                    img,
                    lang=self.languages,
                    config='--psm 6'  # Assume uniform block of text
                )
            )
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
    
    async def process_image_batch(
        self,
        images: list,
        preprocess: bool = True
    ) -> list:
        """
        Process multiple images
        """
        tasks = [self.process_image(img, preprocess) for img in images]
        return await asyncio.gather(*tasks)
    
    async def _load_image(self, image: Union[Image.Image, bytes, str]) -> Optional[Image.Image]:
        """Load image from various formats"""
        try:
            if isinstance(image, Image.Image):
                return image
            elif isinstance(image, bytes):
                return Image.open(io.BytesIO(image))
            elif isinstance(image, str):
                return Image.open(image)
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR"""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Convert to numpy for further processing
        img_array = np.array(image)
        
        # Apply threshold (optional – can be removed for better results)
        # img_array = (img_array > 128) * 255
        # img_array = img_array.astype(np.uint8)
        
        # Convert back to PIL (keeping grayscale, not binary)
        return Image.fromarray(img_array)
    
    async def get_confidence(self, image: Image.Image) -> float:
        """
        Get OCR confidence score
        """
        if not self.available:
            return 0.0
        
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_data(image, output_type='dict')
            )
            
            confidences = [int(c) for c in data['conf'] if c != '-1']
            if confidences:
                return sum(confidences) / len(confidences)
            return 0.0
        except:
            return 0.0
    
    async def detect_language(self, image: Image.Image) -> str:
        """
        Detect text language in image
        """
        text = await self.process_image(image)
        if not text:
            return "unknown"
        
        # Simple language detection (can be enhanced)
        try:
            import langdetect
            return langdetect.detect(text)
        except:
            return "unknown"

# Global instance
ocr_processor = OCRProcessor()