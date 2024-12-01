import json
from pathlib import Path
from typing import List, BinaryIO
from datetime import datetime

from .storage import Storage, StorageError
from ..models.paper import PaperMetadata, TableInfo, PaperAnalysis
from ...utils.logger import logger
class LocalStorage(Storage):
    """Local filesystem implementation of PaperStorage."""

    def __init__(self, storage_root: Path):
        self.storage_root = Path(storage_root)
        self.papers_dir = self.storage_root / "papers"
        self.metadata_dir = self.storage_root / "metadata"
        self.summaries_dir = self.storage_root / "summaries"
        self.tables_dir = self.storage_root / "tables"
        
        # Create directory structure
        for directory in [self.papers_dir, self.metadata_dir, 
                         self.summaries_dir, self.tables_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def check_paper_exists(self, paper_id: str) -> bool:
        """Check if a paper exists."""
        paper_path = self.papers_dir / f"{paper_id}.pdf"
        return paper_path.exists()

    def store_metadata(self, paper_id: str, metadata: PaperMetadata) -> None:
        """Store metadata for a paper."""
        metadata_path = self.metadata_dir / f"{paper_id}.json"
                
        metadata_dict = metadata.dict()        
            
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to store metadata: {e}")
            raise StorageError(f"Failed to store metadata: {e}")

    def get_paper_writer(self, paper_id: str) -> BinaryIO:
        """Get a binary writer for the paper."""
        paper_path = self.papers_dir / f"{paper_id}.pdf"
        try:
            return open(paper_path, 'wb')
        except IOError as e:
            logger.error(f"Failed to create paper writer: {e}")
            raise StorageError(f"Failed to create paper writer: {e}")

    def get_paper_reader(self, paper_id: str) -> BinaryIO:
        """Get a reader for a paper."""
        paper_path = self.papers_dir / f"{paper_id}.pdf"
        if not paper_path.exists():
            raise StorageError(f"Paper not found: {paper_id}")
        
        try:
            return open(paper_path, 'rb')
        except IOError as e:
            raise StorageError(f"Failed to read paper: {e}")

    def store_summary(self, paper_id: str, summary: str) -> None:
        """Store a summary for a paper."""
        summary_path = self.summaries_dir / f"{paper_id}.txt"
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
        except IOError as e:
            logger.error(f"Failed to store summary: {e}")
            raise StorageError(f"Failed to store summary: {e}")

    def get_summary(self, paper_id: str) -> str:
        """Retrieve a summary for a paper."""
        summary_path = self.summaries_dir / f"{paper_id}.txt"
        if not summary_path.exists():
            raise StorageError(f"Summary not found: {paper_id}")
            
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            logger.error(f"Failed to read summary: {e}")
            raise StorageError(f"Failed to read summary: {e}")

    def store_table(self, paper_id: str, table: TableInfo) -> None:
        """Store a table for a paper.
        Stores the CSV content directly as a .csv file and the metadata (description, footnotes) 
        in a separate .json file.
        """
        # Store CSV content
        csv_path = self.tables_dir / f"{paper_id}.csv"
        try:
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(table.csv_content)
        except IOError as e:
            logger.error(f"Failed to store table CSV: {e}")
            raise StorageError(f"Failed to store table CSV: {e}")

        # Store metadata
        metadata_path = self.tables_dir / f"{paper_id}_table_meta.json"
        metadata = {
            "description": table.description,
            "footnotes": table.footnotes
        }
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to store table metadata: {e}")
            # Clean up CSV file if metadata storage fails
            if csv_path.exists():
                csv_path.unlink()
            raise StorageError(f"Failed to store table metadata: {e}")

    def get_table(self, paper_id: str) -> TableInfo:
        """Retrieve a table for a paper."""
        csv_path = self.tables_dir / f"{paper_id}.csv"
        metadata_path = self.tables_dir / f"{paper_id}_table_meta.json"
        
        if not csv_path.exists() or not metadata_path.exists():
            raise StorageError(f"Table not found: {paper_id}")
        
        try:
            # Read CSV content
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # Read metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return TableInfo(
                description=metadata["description"],
                csv_content=csv_content,
                footnotes=metadata["footnotes"]
            )
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read table: {e}")
            raise StorageError(f"Failed to read table: {e}")

    def _dict_to_metadata(self, data: dict) -> PaperMetadata:
        """Convert dictionary to PaperMetadata object."""        
        if data.get("publication_date"):
            data["publication_date"] = datetime.fromisoformat(data["publication_date"])
        return PaperMetadata(**data)

    def get_metadata(self, paper_id: str) -> PaperMetadata:
        """Retrieve metadata for a stored paper."""
        metadata_path = self.metadata_dir / f"{paper_id}.json"
        
        if not metadata_path.exists():
            raise StorageError(f"Metadata not found: {paper_id}")

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(data)
            return self._dict_to_metadata(data)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read metadata: {e}")
            raise StorageError(f"Failed to read metadata: {e}")

    def list_papers(self) -> List[PaperMetadata]:
        """List all stored papers and their metadata."""
        results = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            storage_id = metadata_file.stem
            metadata = self.get_metadata(storage_id)
            if metadata:
                results.append(metadata)
                
        return results
    
    def get_analysis(self, paper_id: str) -> PaperAnalysis:
        """Retrieve an analysis for a paper."""
        metadata = self.get_metadata(paper_id)
        summary = self.get_summary(paper_id)
        table = self.get_table(paper_id)
        return PaperAnalysis(paper_id=paper_id, metadata=metadata, summary=summary, main_table=table)

    def is_paper_analyzed(self, paper_id: str) -> bool:
        """Check if a paper is analyzed."""
        try:
            if self.check_paper_exists(paper_id):
                self.get_summary(paper_id)
                self.get_table(paper_id)
                return True
        except:
            return False