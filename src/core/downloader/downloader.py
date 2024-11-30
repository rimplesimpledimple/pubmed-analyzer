from abc import ABC, abstractmethod
from enum import Enum
from typing import BinaryIO
from ..models.paper import PaperMetadata

class PaperSource(Enum):
    """Represents a source of a paper."""
    PUBMED = 'pubmed'

class PaperDownloader(ABC):
    """Base class for paper downloaders."""

    @abstractmethod
    def download_to_writer(self, url: str, writer: BinaryIO) -> None:
        """Download a paper directly to a writer.
        
        Args:
            url: The URL of the paper to download
            writer: A binary file-like object to write the paper to
            
        Raises:
            UserFacingError: If the URL is invalid or article is not accessible'                        
        """
        pass

    @abstractmethod
    def get_metadata(self, url: str) -> PaperMetadata:
        """Retrieve metadata for a paper.        
        """
        pass


