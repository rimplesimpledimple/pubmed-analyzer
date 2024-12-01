from .prompts import TXT_PAPER_SUMMARY_PROMPT, TXT_PAPER_TABLE_PROMPT
from .base_analyzer import ContentAnalyzer
from ..llm.claude_llm import ClaudeLLM, ClaudeLLMConfig
from ..storage.storage import Storage
from .extractor.content_extractor import ContentExtractor
from ..models.paper import PaperContent, TableInfo, PaperAnalysis
import os
from ...utils.logger import logger

class TextDumpAnalyzer(ContentAnalyzer):
    """Analyzes paper by sending the entire txt content to Claude LLM."""

    def __init__(self, storage: Storage, content_extractor: ContentExtractor, api_key: str = os.getenv("CLAUDE_API_KEY")):
        config = ClaudeLLMConfig(api_key=api_key)
        self.llm = ClaudeLLM(config)
        self.storage = storage
        self.content_extractor = content_extractor
    
    def analyze_paper(self, paper_id: str) -> PaperAnalysis:
        """Analyze paper content in steps to generate insights."""
        # Extract content
        logger.info("Extracting content for paper: %s", paper_id)
        content = self.content_extractor.extract_content(paper_id)        
                                
        logger.info("Generating summary for paper: %s", paper_id)
        summary = self._generate_summary(content)        
                        
        logger.info("Identifying main table for paper: %s", paper_id)
        table_info = self._identify_main_table(content)    

        metadata = self.storage.get_metadata(paper_id)

        return PaperAnalysis(
            paper_id=paper_id,
            metadata=metadata,
            summary=summary,
            main_table=table_info
        )
    
    def _generate_summary(self, content: PaperContent) -> str:
        """Generate summary of the paper."""
        # generate a str with the paper content
        # format is: Title, Abstract, Page Contents
        paper_str = f""        
        for index, page in enumerate(content.page_contents):
            paper_str += f"\nPage {index+1}:\n"
            paper_str += f"{page}\n"
        
        # generate summary
        prompt = TXT_PAPER_SUMMARY_PROMPT.format(title=content.title, abstract=content.abstract, content=paper_str)
        json_structure = {
            "summary": "Summary of the paper"
        }
        return self.llm.chat(prompt, json_structure=json_structure, clear_history=True)["summary"]

    
    def _identify_main_table(self, content: PaperContent) -> TableInfo:
        """Identify the main results table."""
        paper_str = f""        
        for index, page in enumerate(content.page_contents):
            paper_str += f"\nPage {index+1}:\n"
            paper_str += f"{page}\n"
        
        prompt = TXT_PAPER_TABLE_PROMPT.format(title=content.title, abstract=content.abstract, content=paper_str)
        
        json_structure = {
            "table_description": "Description of the main results table",
            "csv_content": "CSV formatted content of the table",
            "footnotes": "Any footnotes associated with the table"
        }
                
        res = self.llm.chat(prompt, json_structure=json_structure, clear_history=True)        
        return TableInfo(
            description=res["table_description"],
            csv_content=res["csv_content"],
            footnotes=res["footnotes"]
        )