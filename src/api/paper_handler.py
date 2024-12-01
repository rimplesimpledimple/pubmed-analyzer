from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict
from ..core.paper_service import PaperService
from ..utils.exceptions import UserFacingError
from .models import (
    GetAnalysisRequest, 
    PaperAnalysis,
    Metadata,
    TableInfo
)
from ..utils.logger import logger

app = FastAPI(
    title="Pubmed Paper Analyzer API",
    description="API for processing and retrieving Pubmed papers"
)

class PaperHandler:
    def __init__(self, paper_service: PaperService):
        self.paper_service = paper_service
        
    def register_routes(self, app: FastAPI):
        """Register all routes with the FastAPI application"""

        @app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            if isinstance(exc, UserFacingError):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"error": str(exc)}
                )
            elif isinstance(exc, HTTPException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"error": exc.detail}
                )
            else:
                logger.error(f"Internal error: {str(exc)}", exc_info=True)
                return JSONResponse(
                    status_code=500,
                    content={"error": "An internal error occurred"}
                )
        
        @app.post("/get-analysis", response_model=PaperAnalysis)
        async def get_analysis(analysis_request: GetAnalysisRequest):
            """Process a paper from a given URL"""
            analysis = self.paper_service.get_analysis(str(analysis_request.url))
            resp_metadata = Metadata(
                id=analysis.metadata.id,
                title=analysis.metadata.title,
                abstract=analysis.metadata.abstract,
                url=analysis.metadata.url
            )

            resp_table = TableInfo(                
                description=analysis.main_table.description,
                csv_content=analysis.main_table.csv_content,
                footnotes=analysis.main_table.footnotes
            )
            resp_analysis = PaperAnalysis(
                paper_id=analysis.paper_id,
                metadata=resp_metadata,
                summary=analysis.summary,
                main_table=resp_table
            )
            return resp_analysis

        @app.get("/papers/{url:path}/metadata", response_model=Metadata)
        async def get_metadata(url: str):
            """Get metadata for a paper by URL"""
            metadata = self.paper_service.get_paper_metadata(url)

            resp_metadata = Metadata(
                id=metadata.id,
                title=metadata.title,
                abstract=metadata.abstract,
                url=metadata.url
            )
            return resp_metadata

        @app.get("/papers/{url:path}/download")
        async def download_paper(url: str):
            """Download paper content"""
            
            return StreamingResponse(
                self.paper_service.download_paper(url),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=paper_{url.split('/')[-1]}.pdf"
                }
            ) 