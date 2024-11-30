from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from dataclasses import asdict

class PaperSource(Enum):
    """Represents a source of a paper."""
    PUBMED = 'pubmed'

@dataclass
class PaperIdentifier:
    """A paper identifier."""
    id: str    
    url: str   
    source: PaperSource

@dataclass
class PaperMetadata:
    """Metadata for a paper."""
    id: str
    title: str    
    abstract: str    
    url: str

    def dict(self) -> dict:
        """Convert the metadata to a dictionary."""
        return asdict(self)

@dataclass
class TableInfo:
    """Information about a table in the paper."""
    description: str
    csv_content: str
    footnotes: str    


@dataclass
class PaperContent:
    """Raw content extracted from a paper pdf."""
    title: str
    abstract: str
    page_contents: List[str]    

@dataclass
class PaperAnalysis: 
    """Results of paper analysis."""
    paper_id: str
    metadata: PaperMetadata
    summary: str
    main_table: Optional[TableInfo] 
