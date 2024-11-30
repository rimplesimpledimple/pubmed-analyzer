from fastapi import FastAPI
from core.paper_service import PaperService
from core.downloader.download_manager import DownloadManager
from core.storage.local_storage import LocalStorage
from core.identifier.identifier import Identifier
from core.downloader.downloader import PaperSource
from core.downloader.pubmed_downloader import PubMedDownloader
from core.analyzer.pdf_dump_analyzer import PdfDumpAnalyzer
from core.analyzer.text_dump_analyzer import TextDumpAnalyzer
from pathlib import Path
from core.analyzer.extractor.content_extractor import ContentExtractor
from utils.logger import setup_logging
from dotenv import load_dotenv
from api.paper_handler import PaperHandler
import uvicorn

storage_root = Path("data")

def create_app() -> FastAPI:
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Initialize dependencies
    downloaders = {
        PaperSource.PUBMED: PubMedDownloader(email="test@test.com")
    }
    storage = LocalStorage(storage_root)
    identifier = Identifier()
    download_manager = DownloadManager(downloaders=downloaders, storage=storage, identifier=identifier)    

    # Choose analyzer strategy
    txt_dump_analyzer = TextDumpAnalyzer(storage=storage, content_extractor=ContentExtractor(storage))
    # pdf_dump_analyzer = PdfDumpAnalyzer(storage=storage)
    
    # Create paper service instance
    paper_service = PaperService(
        download_manager=download_manager,
        storage=storage,
        identifier=identifier,
        analyzer=txt_dump_analyzer
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="Pubmed Paper Analyzer API",
        description="API for processing and retrieving Pubmed papers"
    )
    
    # Setup paper handler with routes
    paper_handler = PaperHandler(paper_service)
    paper_handler.register_routes(app)
    
    return app

def main():
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
