from typing import Iterator
from .downloader.download_manager import DownloadManager
from .storage.storage import Storage
from ..identifier.identifier import Identifier
from .models.paper import PaperMetadata, PaperAnalysis
from .analyzer.base_analyzer import ContentAnalyzer
from ..utils.logger import logger

class PaperService:
    """Service for orchestrating academic paper operations."""
    
    def __init__(self, download_manager: DownloadManager, storage: Storage, 
                 identifier: Identifier, analyzer: ContentAnalyzer):
        self.download_manager = download_manager
        self.storage = storage
        self.identifier = identifier
        self.analyzer = analyzer

    def get_analysis(self, url: str) -> PaperAnalysis:
        """
        Get complete analysis of a paper including metadata, summary, and tables.
        """
        logger.info("Processing paper from URL: %s", url)
        
        paper_identifier = self.identifier.from_url(url)
        
        # Check cache first
        if self.storage.check_paper_exists(paper_identifier.id):
            logger.info("Paper already processed: %s", paper_identifier.id)
            return self.storage.get_analysis(paper_identifier.id)
            
        # Download and store paper
        paper_metadata = self.download_manager.download(url)        

        # Analyze paper
        analysis = self.analyzer.analyze_paper(paper_identifier.id)
        
        # Store results        
        self.storage.store_summary(paper_identifier.id, analysis.summary)
        self.storage.store_table(paper_identifier.id, analysis.main_table)        
        
        return analysis

    def get_paper_metadata(self, url: str) -> PaperMetadata:
        """
        Retrieve metadata for a specific paper.
        """        
        paper_identifier = self.identifier.from_url(url)
        if not self.storage.check_paper_exists(paper_identifier.id):
            paper_metadata = self.download_manager.download(url)
            self.storage.store_metadata(paper_identifier.id, paper_metadata)
        return self.storage.get_metadata(paper_identifier.id)

    def download_paper(self, url: str) -> Iterator[bytes]:
        """
        Stream a paper's content as bytes.                
        """
        logger.info("Streaming paper from URL: %s", url)
        paper_identifier = self.identifier.from_url(url)
        
        # Download if not already in storage
        if not self.storage.check_paper_exists(paper_identifier.id):
            self.download_manager.download(url)
            
        return self.storage.get_paper_reader(paper_identifier.id)
            



