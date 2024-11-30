import base64
from ..models.paper import PaperAnalysis, TableInfo
from .prompts import PDF_SUMMARY_PROMPT, PDF_MAIN_TABLE_PROMPT
from .base_analyzer import ContentAnalyzer
from ..llm.claude_llm import ClaudeLLM, ClaudeLLMConfig
from ..storage.storage import Storage
import os

class PdfDumpAnalyzer(ContentAnalyzer):
    """Analyzes paper by sending the entire content to Claude LLM."""
    
    def __init__(self, storage: Storage, api_key: str = os.getenv("CLAUDE_API_KEY")):
        config = ClaudeLLMConfig(api_key=api_key)
        self.llm = ClaudeLLM(config)
        self.storage = storage
    
    def analyze_paper(self, paper_id: str) -> PaperAnalysis:
        """Analyze paper content by sending PDF to Claude."""
        pdf_data = self._get_pdf_data(paper_id)
        
        # Get analysis using PDF support
        summary = self.llm.chat_with_pdf(PDF_SUMMARY_PROMPT, pdf_data, json_structure={"summary": "Summary of the paper"})
        print(f"Summary: {summary} \n\n")

        # Get table selection
        table_selection = self.llm.chat_with_pdf(
            PDF_MAIN_TABLE_PROMPT, 
            pdf_data, 
            json_structure={
                "table_description": "Description of the main results table", 
                "csv_content": "CSV formatted content of the table", 
                "footnotes": "Any footnotes associated with the table"
            }
        )
        print(f"Table selection: {table_selection} \n\n")
                        
        return PaperAnalysis(
            summary=summary["summary"],
            main_table=TableInfo(
                description=table_selection["table_description"],
                csv_content=table_selection["csv_content"],
                footnotes=table_selection["footnotes"]
            )
        )
    
    def _get_pdf_data(self, paper_id: str) -> str:
        """Fetch PDF data and encode in base64."""
        with self.storage.get_paper_reader(paper_id) as reader:
            pdf_content = reader.read()
        return base64.standard_b64encode(pdf_content).decode("utf-8")