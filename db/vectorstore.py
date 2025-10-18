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
        "text-embedding-3-small": 1536,  # Korrekt: 1536 Dimensionen (vorher fälschlicherweise 384)
        "text-embedding-ada-002": 1536,
        "text-embedding-3-large": 3072,
    }

    def __init__(
        self,
        data: pd.DataFrame,
        file_path: str = "",
        file_name: str = "",
        collection_name: str = "",
        batch_size: int = 100,
        embedding_model: str = "text-embedding-3-small",
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
            force_recreate: If True, recreate the store even if it exists

        Returns:
            The created/loaded vectorstore instance, or None if creation fails
        """
        pass

    @abstractmethod
    def split_and_chunk_text(self) -> tuple[list[str], list[dict], list[str]]:
        """
        Split text by recursively looking at characters.

        Recursively tries to split by different characters to find one
        that works.

        Returns:
            Tuple containing (documents, metadatas, ids) ready for vector store
        """
        pass

    @abstractmethod
    def delete_vectorstore(self) -> bool:
        """
        Delete vectorstore if the vectorstore file/directory exists.

        Returns:
            True if the vectorstore successfully deleted, otherwise False
        """
        pass
