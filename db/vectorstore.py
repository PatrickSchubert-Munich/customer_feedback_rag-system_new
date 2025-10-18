import os
import pandas as pd

from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    """
    Abstract base class for vector store implementations.

    This class defines the interface that all vector store implementations
    must follow for creating and managing document embeddings.
    """

    # Embedding-Dimensionen basierend auf Modell (OpenAI Standard-Dimensionen)
    _MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-ada-002": 1536,  # BESTE Cross-Lingual Performance (92% avg similarity)
        "text-embedding-3-large": 3072,
    }

    def __init__(
        self,
        data: pd.DataFrame,
        file_path: str = "",
        file_name: str = "",
        collection_name: str = "",
        batch_size: int = 100,
        embedding_model: str = "text-embedding-ada-002",  # Geändert: Ada-002 für Cross-Lingual
    ) -> None:
        """
        Initialize the vector store.

        Args:
            data: pandas DataFrame containing the data to embed
            file_path: Path where the vector store will be persisted
            file_name: Name of the file/store
            collection_name: Name of the collection/store
            batch_size: Number of documents to process in each batch
            embedding_model: Name of the OpenAI embedding model to use

        Raises:
            ValueError: If data is None, empty, or missing critical columns
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")

        # Early validation of absolutely critical columns
        critical_columns = ["NPS", "Market", "Verbatim"]
        missing_critical = [col for col in critical_columns if col not in data.columns]
        if missing_critical:
            raise ValueError(
                f"DataFrame is missing critical columns: {missing_critical}"
            )

        if file_path == "":
            file_path = "."
        if file_name == "":
            file_name = "vectorstore"
        if collection_name == "":
            self.collection_name = "my-collection"
        else:
            self.collection_name = collection_name

        self.data = data
        self.file_path = file_path
        self.file_name = file_name
        self.persist_directory = os.path.join(self.file_path, self.file_name)
        self.batch_size = batch_size
        self.embedding_model = embedding_model

    @abstractmethod
    def create_vectorstore(self, force_recreate: bool = False) -> Any:
        """
        Create or load a vectorstore from a DataFrame.

        Args:
            force_recreate (bool): If True, recreates the store even if it exists.
                                  Deletes existing vectorstore and creates fresh instance.

        Returns:
            Any: The created/loaded vectorstore instance (collection, index, etc.),
                 or None if creation fails
                 
        Notes:
            - Implementations should load existing store if available (unless force_recreate=True)
            - Should handle chunking, embedding, and persistence
            - Should validate DataFrame structure before processing
            - Should provide progress feedback during creation
        """
        pass

    @abstractmethod
    def split_and_chunk_text(self) -> tuple[list[str], list[dict], list[str]]:
        """
        Split and chunk text data from DataFrame for embedding.

        This method should implement the chunking strategy appropriate for
        the data type. For customer feedback, most implementations should
        avoid excessive chunking to preserve semantic units.

        Returns:
            tuple[list[str], list[dict], list[str]]: Three-element tuple containing:
                - documents (list[str]): List of text chunks ready for embedding
                - metadatas (list[dict]): List of metadata dicts per chunk with all
                  relevant fields (NPS, sentiment, topic, etc.)
                - ids (list[str]): List of unique identifiers per chunk
                
        Notes:
            - Should use RecursiveCharacterTextSplitter with semantic separators
            - Should preserve all metadata from original DataFrame rows
            - Should filter out invalid/too-short entries
            - Should provide chunking statistics
        """
        pass

    @abstractmethod
    def delete_vectorstore(self) -> bool:
        """
        Delete vectorstore completely if it exists.

        Returns:
            bool: True if the vectorstore was successfully deleted,
                  False if deletion failed or vectorstore doesn't exist
                  
        Notes:
            - Should remove all persisted data (files, directories, collections)
            - Should handle cases where vectorstore doesn't exist gracefully
            - Irreversible operation - implementations should be cautious
            - Should provide feedback about deletion status
        """
        pass
