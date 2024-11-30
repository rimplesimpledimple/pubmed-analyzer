from pydantic import BaseModel, HttpUrl
from typing import Optional, List


# Update existing models and add new ones to match domain classes
class GetAnalysisRequest(BaseModel):
    url: HttpUrl

class GetDownloadResponse(BaseModel):
    content: bytes


class Metadata(BaseModel):
    id: str
    title: str    
    abstract: str    
    url: str

class TableInfo(BaseModel):
    description: str
    csv_content: str
    footnotes: str

# Add new model for complete paper analysis
class PaperAnalysis(BaseModel):
    paper_id: str
    metadata: Metadata
    summary: str
    main_table: Optional[TableInfo]

