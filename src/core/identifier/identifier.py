from urllib.parse import urlparse
import re
from ..models.paper import PaperIdentifier, PaperSource
from ...utils.exceptions import UserFacingError

class Identifier:
    """Utility class for creating paper identifiers from URLs."""

    @staticmethod
    def from_url(url: str) -> PaperIdentifier:
        """Create a PaperIdentifier from a URL."""
        parsed_url = urlparse(url)
        
        # PubMed validation
        if 'pubmed' in parsed_url.netloc or 'ncbi.nlm.nih.gov' in parsed_url.netloc:
            pmid_match = re.search(r'/(\d+)/?$', parsed_url.path)
            if not pmid_match:
                raise UserFacingError(
                    "Invalid PubMed URL. Expected format: https://pubmed.ncbi.nlm.nih.gov/PMID/"
                )
            
            return PaperIdentifier(
                id=pmid_match.group(1),
                url=url,
                source=PaperSource.PUBMED
            )

        raise UserFacingError("Only PubMed URLs are currently supported")
