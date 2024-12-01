from typing import List, Tuple
import fitz
from ...storage.storage import Storage
from ...models.paper import PaperContent

class ContentExtractor:
    """Extracts raw content from pdf files."""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        
    def extract_content(self, paper_id: str, format: str = "markdown") -> PaperContent:
        """
        Extract all content from a pdf file.
        
        Args:
            paper_id: ID of the paper to extract
            format: Output format for text extraction (plain/markdown)
        """
        
        with self.storage.get_paper_reader(paper_id) as reader:
            metadata = self.storage.get_metadata(paper_id)
            doc = fitz.open(stream=reader.read(), filetype="pdf")            
            page_contents = self._extract_page_contents(doc, format)        
            doc.close()
            
            return PaperContent(                
                page_contents=page_contents,
                title=metadata.title,
                abstract=metadata.abstract
            )
    
    
    def get_page_image(self, paper_id: str, page_number: int) -> Tuple[bytes, str]:
        """
        Get a specific page as an image at original size.
        page_number: 1-based page number (first page = 1)
        Returns a tuple of (image_bytes, mime_type)
        """
        with self.storage.get_paper_reader(paper_id) as reader:
            doc = fitz.open(stream=reader.read(), filetype="pdf")
            
            # Convert 1-based to 0-based indexing
            zero_based_page = page_number - 1
            
            if zero_based_page < 0 or zero_based_page >= len(doc):
                doc.close()
                raise ValueError(f"Page number {page_number} is out of range. Valid range: 1 to {len(doc)}")
            
            page = doc[zero_based_page]
            mat = fitz.Matrix(1, 1)  # Use original size (1.0 zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img_bytes = pix.tobytes("png")
            doc.close()
            
            return img_bytes, "image/png"    
        
    def _extract_page_contents(self, doc: fitz.Document, format: str = "markdown") -> List[str]:
        """
        Extract content from each page as a separate list element.
        
        Args:
            doc: The PDF document
            format: Output format - one of:
                - "plain": Simple text with minimal formatting
                - "markdown": Text formatted as markdown                
        """
        page_contents = []
        for page in doc:        
            text = page.get_text(format)                                
            page_contents.append(text)
        return page_contents