import re
import requests
from typing import Optional, BinaryIO
from Bio import Entrez

from ..models.paper import PaperMetadata
from .downloader import PaperDownloader
from ...utils.exceptions import UserFacingError, InternalError
from ...utils.logger import logger


class PubMedDownloader(PaperDownloader):
    """PubMed-specific implementation of the PaperDownloader interface."""
    
    def __init__(self, email: str):
        """Initialize the PubMed downloader.
        
        Args:
            email: Email address for NCBI's E-utilities (required by their API)
        """
        Entrez.email = email
        
    def download_to_writer(self, pubmed_url: str, writer: BinaryIO) -> None:
        """Download paper from PubMed directly to a file. The idea is to not keep the entire PDF in memory 
        
        Args:
            identifier: Pubmed URL
            writer: A binary file-like object to write to
            
        Raises:
            UserFacingError: If the URL is invalid or article is not accessible
            InternalError: If there are network issues
        """
        pmid = self._extract_pmid(pubmed_url)
        if not pmid:
            logger.error(f"The URL: {pubmed_url} does not point to a valid PubMed article.")
            raise UserFacingError(
                message=f"The URL: {pubmed_url} does not point to a valid PubMed article.",
                status_code=400,
            )
        
        pmcid = self._get_pmcid(pmid) 
        try:                         
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/pdf/"
            response = requests.get(
                    pdf_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}, 
                    stream=True
                )
                
            if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        writer.write(chunk)
                return
            
            # If we get here, either status code wasn't 200 or content type wasn't PDF
            raise UserFacingError(
                message="This article is not accessible or does not exist",
                status_code=response.status_code
            )
                    
        except requests.RequestException as e:
            # Catch all requests exceptions and convert to appropriate error
            if isinstance(e, requests.HTTPError) and e.response.status_code in (403, 404):
                logger.error(f"Article not accessible: {e}")
                raise UserFacingError(
                    message="This article is not accessible or does not exist",
                    status_code=e.response.status_code
                ) from e
                
            logger.error(f"Error downloading from PMC: {e}")
            raise InternalError("Failed to download PDF due to network error") from e

    def get_metadata(self, url: str) -> PaperMetadata:
        """Get paper metadata from PubMed."""
        identifier = self._extract_pmid(url)

        try:
            handle = Entrez.efetch(db="pubmed", id=identifier, rettype="xml")
            records = Entrez.read(handle)
            handle.close()

            article = records['PubmedArticle'][0]['MedlineCitation']['Article']
            
            # Extract abstract text properly
            abstract = ''
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_text = article['Abstract']['AbstractText']
                if isinstance(abstract_text, list):
                    abstract = ' '.join(str(text) for text in abstract_text)
                else:
                    abstract = str(abstract_text)

            metadata = PaperMetadata(
                id=identifier,
                title=article.get('ArticleTitle', ''),
                abstract=abstract,                
                url=url
            )
            
            return metadata
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            raise InternalError(f"Error fetching metadata: {e}") from e
        
    def _extract_pmid(self, identifier: str) -> Optional[str]:
        """Validate and extract PMID from a PubMed identifier."""
        if 'pubmed.ncbi.nlm.nih.gov' in identifier:
            pattern = r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?'
            match = re.search(pattern, identifier)
            return match.group(1) if match else None
        return identifier if identifier.isdigit() else None

    def _get_pmcid(self, pmid: str) -> Optional[str]:
        """Get PMC ID from PubMed ID.
        
        Raises:
            UserFacingError: If the PMC ID is not found
        """
        try:
            handle = Entrez.elink(dbfrom="pubmed", id=pmid, db="pmc")
            result = Entrez.read(handle)
            handle.close()

            linkset = result[0]
            if linkset.get('LinkSetDb'):
                for linksetdb in linkset['LinkSetDb']:
                    if linksetdb['DbTo'] == 'pmc':
                        pmcid = linksetdb['Link'][0]['Id']
                        if pmcid:
                            return pmcid
            
            logger.error(f"No PMC ID found for PMID: {pmid}")
            raise UserFacingError(
                message=f"No PMC ID found for PMID: {pmid}. Possible reason: Free access to the paper is not available.",
                status_code=500,
            )
        
        except UserFacingError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting PMC ID for PMID: {pmid}. Error: {e}")
            raise InternalError(
                f"Error getting PMC ID for PMID: {pmid}. Error: {e}"
            )
