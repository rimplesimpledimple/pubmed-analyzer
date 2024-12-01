from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
import os

from src.core.paper_service import PaperService
from src.core.downloader.download_manager import DownloadManager
from src.core.storage.local_storage import LocalStorage
from src.core.identifier.identifier import Identifier
from src.core.downloader.downloader import PaperSource
from src.core.downloader.pubmed_downloader import PubMedDownloader
from src.core.analyzer.pdf_dump_analyzer import PdfDumpAnalyzer
from src.core.analyzer.text_dump_analyzer import TextDumpAnalyzer
from src.core.analyzer.extractor.content_extractor import ContentExtractor
from src.utils.logger import setup_logging
from src.api.paper_handler import PaperHandler
from src.core.llm.openai_llm import OpenAILLM, OpenAILLMConfig
from src.core.llm.claude_llm import ClaudeLLM, ClaudeLLMConfig
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

    if os.getenv("OPENAI_API_KEY"):
        llm = OpenAILLM(config=OpenAILLMConfig(api_key=os.getenv("OPENAI_API_KEY")))
    else:
        llm = ClaudeLLM(config=ClaudeLLMConfig(api_key=os.getenv("CLAUDE_API_KEY")))

    # Choose analyzer strategy
    analyzer = TextDumpAnalyzer(storage=storage, content_extractor=ContentExtractor(storage), llm=llm)
    # analyzer = PdfDumpAnalyzer(storage=storage, llm=llm)
    
    # Create paper service instance
    paper_service = PaperService(
        download_manager=download_manager,
        storage=storage,
        identifier=identifier,
        analyzer=analyzer
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
