from abc import ABC, abstractmethod
from typing import BinaryIO, ContextManager
from ..models.paper import PaperMetadata, PaperAnalysis
from typing import List
from ..exceptions import InternalError

class StorageError(InternalError):
    """Exception raised for storage errors."""
    pass


class Storage(ABC):
    """Abstract base class for paper storage backends."""
    @abstractmethod
    def check_paper_exists(self, paper_id: str) -> bool:
        """Check if a paper exists."""
        pass

    @abstractmethod
    def list_papers(self) -> List[PaperMetadata]:
        """List all stored papers and their metadata."""
        pass

    @abstractmethod
    def get_paper_writer(self, paper_id: str) -> ContextManager[BinaryIO]:
        """
        Get a context manager that provides a binary writer for the paper.
        
        Example:
            with storage.get_paper_writer(paper_id) as writer:
                downloader.download_to_writer(url, writer)
        """
        pass

    @abstractmethod
    def get_paper_reader(self, paper_id: str) -> ContextManager[BinaryIO]:
        """Get a context manager that provides a binary reader for the paper."""
        pass

    @abstractmethod
    def get_metadata(self, paper_id: str) -> PaperMetadata:
        """Retrieve metadata for a stored paper."""
        pass

    @abstractmethod
    def store_metadata(self, paper_id: str, metadata: PaperMetadata) -> None:
        """Store metadata for a paper."""
        pass

    @abstractmethod
    def store_summary(self, paper_id: str, summary: str) -> None:
        """Store a summary for a paper."""
        pass    

    @abstractmethod
    def store_table(self, paper_id: str, table: dict) -> None:
        """Store a table for a paper."""
        pass

    @abstractmethod
    def get_table(self, paper_id: str) -> dict:
        """Retrieve a table for a paper."""
        pass

    @abstractmethod
    def get_analysis(self, paper_id: str) -> PaperAnalysis:
        """Retrieve an analysis for a paper."""
        pass
