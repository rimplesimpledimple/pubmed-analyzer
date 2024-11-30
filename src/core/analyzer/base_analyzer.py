from abc import ABC, abstractmethod
from ..models.paper import PaperAnalysis

    

class ContentAnalyzer(ABC):
    """Abstract base class for different paper content analyzers."""    
    
    @abstractmethod
    def analyze_paper(self, paper_id: str) -> PaperAnalysis:
        """Analyze paper content and return summary and table info."""
        pass 