from typing import Dict, Type
from .downloader import PaperDownloader, PaperMetadata
from ..identifier.identifier import Identifier
from .downloader import PaperSource
from ..storage.storage import Storage
from ...utils.exceptions import InternalError

class DownloadManager:
    """Manages the paper download process and coordinates between different downloaders."""
    
    def __init__(self, downloaders: Dict[PaperSource, Type[PaperDownloader]], storage: Storage, identifier: Identifier):
        self.storage = storage
        self.identifier = identifier
        self.downloaders = downloaders
    
    def _get_appropriate_downloader(self, url: str, source: PaperSource) -> PaperDownloader:
        """Determine the appropriate downloader based on the URL."""

        # Check if the source exists in downloaders dictionary
        if source.value == PaperSource.PUBMED.value:
            return self.downloaders[PaperSource.PUBMED]                        
        
        raise InternalError(f"No downloader found for URL: {url}")
    
    def download(self, url: str) -> PaperMetadata:
        """Download and store a paper, returning its metadata."""
        paper_identifier = self.identifier.from_url(url)        
        downloader = self._get_appropriate_downloader(url, paper_identifier.source)
        
        # Get paper metadata
        metadata = downloader.get_metadata(url)
        self.storage.store_metadata(paper_identifier.id, metadata)
            
        # Download paper directly to storage
        with self.storage.get_paper_writer(paper_identifier.id) as writer:                
            downloader.download_to_writer(url, writer)
                
        return metadata                
    
        