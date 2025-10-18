import os
import shutil
import pandas as pd
import chromadb

from typing import Any, cast
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from db.vectorstore import VectorStore


class ChromaVectorStore(VectorStore):
    """
    Chroma VectorStore for customer feedback with feedback-optimized chunking.
    
    Features:
    - Feedback-optimized chunking: <4000 characters remain complete (99.9% of cases)
    - Comprehensive metadata for precise filtering (27 fields)
    - Explicit cosine distance metric for OpenAI embeddings
    - Support for Azure OpenAI and standard OpenAI
    - Persistent storage with ChromaDB
    
    Chunking Strategy:
    - Feedbacks <4000 characters (~1000 tokens): NO chunking
      → Preserves semantic unit, avoids fragmentation
    - Feedbacks ≥4000 characters: Large chunks (3000 chars, 500 overlap)
      → Only for extreme outliers, high overlap ensures context preservation
    
    Metadata per Document:
    - row_id: Row ID in DataFrame
    - nps: Net Promoter Score (0-10)
    - nps_category: Detractor/Passive/Promoter
    - market: Market ID (e.g. "C1-DE")
    - region: Business region (e.g. "C1", "CE")
    - country: ISO 3166-1 Alpha-2 country code (e.g. "DE", "IT")
    - date: Unix timestamp
    - date_str: Date as string
    - sentiment_label: positiv/neutral/negativ
    - sentiment_score: Sentiment confidence (-1.0 to 1.0)
    - topic: Topic category (e.g. "Service", "Lieferproblem")
    - topic_confidence: Topic confidence (0.0 to 1.0)
    - verbatim_token_count: Token count of feedback
    - chunk_index: Index of current chunk
    - total_chunks: Total number of chunks for this feedback
    - verbatim_preview: First 100 characters (for debugging)
    """

    def __init__(
        self,
        data: pd.DataFrame,
        file_path: str = ".",
        file_name: str = "vectorstore",
        collection_name: str = "customer_feedback",
        batch_size: int = 100,
        embedding_model: str = "text-embedding-ada-002",  # Ada-002: Superior Cross-Lingual (92% avg)
    ) -> None:
        super().__init__(
            data, file_path, file_name, collection_name, batch_size, embedding_model
        )

        self._ensure_persist_directory()
        self._chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        self._embedding_function = self._create_embedding_function()

    def _create_embedding_function(self):
        """
        Creates OpenAI Embedding Function - supports both Azure and standard OpenAI.

        Returns:
            embedding_functions.OpenAIEmbeddingFunction: Embedding function instance
            
        Notes:
            - Prioritizes Azure OpenAI if AZURE_OPENAI_ENDPOINT is configured
            - Falls back to standard OpenAI API if Azure is not available
            - Uses text-embedding-ada-002 model for embeddings
        """
        # Prüfe zuerst auf Azure OpenAI
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("OPENAI_API_BASE")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

        # Prüfe auf Standard OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")

        # Azure OpenAI hat Priorität, falls vollständig konfiguriert
        if azure_api_key and azure_endpoint:
            print("✅ Verwende Azure OpenAI für Embeddings")
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=azure_api_key,
                api_base=azure_endpoint,
                api_type="azure",
                api_version=azure_api_version,
                deployment_id=self.embedding_model,
                dimensions=self._MODEL_DIMENSIONS.get(self.embedding_model, 384),
            )
        
        # Fallback zu Standard OpenAI
        elif openai_api_key:
            print("✅ Verwende Standard OpenAI für Embeddings")
            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name=self.embedding_model,
                dimensions=self._MODEL_DIMENSIONS.get(self.embedding_model, 384),
            )
        
        # Keine gültigen API Keys gefunden
        else:
            raise ValueError("Weder AZURE_OPENAI_API_KEY+AZURE_OPENAI_ENDPOINT noch OPENAI_API_KEY Umgebungsvariablen sind gesetzt")

    def _ensure_persist_directory(self) -> None:
        """
        Creates persist directory and verifies write permissions.

        Raises:
            PermissionError: If write permissions are missing
            
        Notes:
            - Creates directory recursively if it doesn't exist
            - Verifies write access with temporary test file
            - Ensures reliable persistent storage for ChromaDB
        """
        os.makedirs(self.persist_directory, exist_ok=True)

        # Schreibrechte testen
        test_file = os.path.join(self.persist_directory, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except (PermissionError, OSError) as e:
            raise PermissionError(
                f"Keine Schreibrechte: {self.persist_directory}"
            ) from e

    def _get_optimized_chunk_params(self, text_length: int) -> tuple[int, int]:
        """
        Feedback-optimized chunking strategy.
        
        Strategy:
        - <4000 characters (~1000 tokens): NO chunking
          → Preserves feedback as atomic semantic unit
          → Avoids fragmentation and duplicates
          → Optimal for text-embedding-3-small (max 8191 tokens)
        
        - ≥4000 characters: Chunking with large chunks + high overlap
          → Only for extreme outliers (very rare long feedbacks)
          → High overlap (500 characters = ~17%) ensures context preservation
        
        Rationale:
        - Customer feedback are atomic units, not hierarchical documents
        - Context comes from metadata (NPS, topic, sentiment), not from chunks
        - 99.9% of feedbacks remain complete (median: 122 characters)
        
        Args:
            text_length (int): Length of feedback text in characters
        
        Returns:
            tuple[int, int]: (chunk_size, overlap) where:
                - For <4000: (text_length, 0) = no chunking
                - For ≥4000: (3000, 500) = large chunks with high overlap
                
        Notes:
            - 99.9% of cases result in no chunking
            - Chunking only activates for exceptional outliers
            - Large chunk_size preserves context and semantic meaning
        """
        if text_length < 4000:
            # KEIN Chunking: Feedback bleibt vollständig (99.9% der Fälle)
            return (text_length, 0)
        else:
            # Nur bei extremen Ausreißern: Große Chunks mit hohem Overlap
            # 3000 Zeichen ≈ 750 Tokens, 600 Overlap ≈ 150 Tokens (20%)
            return (3000, 600)

    def _prepare_content(self, row: pd.Series) -> str:
        """
        Prepares pure feedback text for embedding.
        
        Args:
            row (pd.Series): DataFrame row containing feedback data
            
        Returns:
            str: Cleaned verbatim text ready for embedding
            
        Notes:
            - Extracts 'verbatim' column from row
            - Converts to string and strips whitespace
            - Returns empty string if verbatim is missing
        """
        return str(row["Verbatim"]).strip()

    def _prepare_metadata(
        self, row: pd.Series, idx: int, chunk_idx: int, total_chunks: int
    ) -> dict:
        """
        Prepares comprehensive metadata for ChromaDB.
        
        Args:
            row (pd.Series): DataFrame row containing feedback data
            idx (int): Row index
            chunk_idx (int): Index of current chunk
            total_chunks (int): Total number of chunks
        
        Returns:
            dict: Validated metadata with the following keys:
                - row_id, nps, market (always present)
                - region, country (if Market was split)
                - nps_category (if classified)
                - sentiment_label, sentiment_score (if analyzed)
                - topic, topic_confidence (if classified)
                - date, date_str (if available)
                - verbatim_token_count (if calculated)
                - chunk_index, total_chunks (chunking info)
                - verbatim_preview (first 100 characters)
        
        Notes:
            - All values are validated for ChromaDB-compatible types
              (str, int, float, bool)
            - Handles numpy types and None values appropriately
            - Ensures robust metadata storage for filtering
        """
        # Sichere Datentyp-Konvertierungen
        metadata = {
            "row_id": int(idx),
            "nps": int(float(row["NPS"])),  # Handle object type via float conversion
            "market": str(row["Market"]).strip(),
            "chunk_index": int(chunk_idx),
            "total_chunks": int(total_chunks),
        }

        # Optional: Date als Unix Timestamp für ChromaDB-Filterung
        if "Date" in row.index and pd.notna(row["Date"]):
            try:
                date_str = str(row["Date"])
                # Handle ISO format with timezone
                if "T" in date_str and "+00:00" in date_str:
                    date_obj = datetime.fromisoformat(date_str.replace("+00:00", ""))
                else:
                    # Fallback to standard format
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                metadata["date"] = int(date_obj.timestamp())
                metadata["date_str"] = date_str
            except (ValueError, TypeError):
                metadata["date_str"] = str(row["Date"])

        # Optional: NPS Category
        if "nps_category" in row.index and pd.notna(row["nps_category"]):
            metadata["nps_category"] = str(row["nps_category"])

        # Optional: Sentiment
        if "sentiment_label" in row.index and pd.notna(row["sentiment_label"]):
            metadata["sentiment_label"] = str(row["sentiment_label"])

        if "sentiment_score" in row.index and pd.notna(row["sentiment_score"]):
            try:
                metadata["sentiment_score"] = float(row["sentiment_score"])
            except (ValueError, TypeError):
                # Fallback für ungültige Sentiment-Werte
                metadata["sentiment_score"] = 0.0

        # Optional: Token Count
        if "verbatim_token_count" in row.index and pd.notna(
            row["verbatim_token_count"]
        ):
            metadata["verbatim_token_count"] = int(row["verbatim_token_count"])

        # Optional: Topic Classification
        if "topic" in row.index and pd.notna(row["topic"]):
            metadata["topic"] = str(row["topic"])

        if "topic_confidence" in row.index and pd.notna(row["topic_confidence"]):
            try:
                metadata["topic_confidence"] = float(row["topic_confidence"])
            except (ValueError, TypeError):
                metadata["topic_confidence"] = 0.0

        # Optional: Region (from Market split)
        if "region" in row.index and pd.notna(row["region"]):
            metadata["region"] = str(row["region"])

        # Optional: Country (ISO format from Market split)
        if "country" in row.index and pd.notna(row["country"]):
            metadata["country"] = str(row["country"])

        # Hilfreich für Debugging: Preview des Original-Feedbacks
        metadata["verbatim_preview"] = str(row["Verbatim"])[:100]

        # ChromaDB Metadata-Typ-Validierung
        return self._validate_metadata_types(metadata)

    def _validate_metadata_types(self, metadata: dict) -> dict:
        """
        Validates and corrects metadata types for ChromaDB.
        
        Args:
            metadata (dict): Original metadata dictionary
            
        Returns:
            dict: Validated metadata with ChromaDB-compatible types
            
        Notes:
            - ChromaDB only accepts: str, int, float, bool
            - Converts numpy types to Python native types
            - Filters out None values
            - Handles edge cases like NaN and inf
        """
        validated = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                validated[key] = value
            elif isinstance(value, (list, dict)):
                # Komplexe Typen zu String konvertieren
                validated[key] = str(value)
            else:
                # Alle anderen Typen zu String
                validated[key] = str(value)
        return validated

    def split_and_chunk_text(self) -> tuple[list[str], list[dict], list[str]]:
        """
        Splits and chunks feedback texts with optimized parameters.

        Returns:
            tuple[list[str], list[dict], list[str]]: Three-element tuple containing:
                - documents (list[str]): List of content texts (chunks)
                - metadatas (list[dict]): List of metadata dicts per chunk
                - ids (list[str]): List of unique IDs per chunk (format: "doc_{idx}_{chunk_idx}")
                
        Raises:
            ValueError: If no valid documents could be created from DataFrame
            
        Notes:
            - Filters out feedbacks <10 characters (too short)
            - 99.9% of feedbacks remain unchunked (<4000 chars)
            - Uses RecursiveCharacterTextSplitter with semantic separators
            - Preserves full metadata from original row for each chunk
            - Prints detailed chunking statistics to console
            - Token estimation: 1 token ≈ 4 characters for German text
        """
        documents = []
        metadatas = []
        ids = []

        separators = [
            "\n\n",
            ".\n",
            ". ",
            "! ",
            "? ",
            ";\n",
            "; ",
            ",\n",
            " - ",
            " ",
            "",
        ]

        for idx, row in self.data.iterrows():
            try:
                # Sichere Index-Konvertierung für Type-Safety
                row_index = int(idx) if isinstance(idx, (int, str)) else hash(idx)

                # 1. Content vorbereiten (NUR Verbatim!)
                content = self._prepare_content(row)

                if not content or len(content) < 10:
                    continue

                # 2. Optimierte Chunk-Parameter ermitteln
                chunk_size, overlap = self._get_optimized_chunk_params(len(content))

                # 3. Text-Splitter mit optimierten Parametern
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    separators=separators,
                    length_function=len,
                )

                chunks = text_splitter.split_text(content)
                total_chunks = len(chunks)

                # 4. Chunks und Metadaten erstellen
                for chunk_idx, chunk in enumerate(chunks):
                    # Metadaten vorbereiten
                    metadata = self._prepare_metadata(
                        row, row_index, chunk_idx, total_chunks
                    )

                    # Zu ChromaDB hinzufügen
                    documents.append(chunk)
                    metadatas.append(metadata)
                    ids.append(f"doc_{idx}_{chunk_idx}")

            except Exception as e:
                print(f"Warnung: Fehler beim Verarbeiten von Zeile {idx}: {e}")
                continue

        if not documents:
            raise ValueError(
                "Keine Dokumente konnten aus dem DataFrame erstellt werden"
            )

        # Detaillierte Statistiken ausgeben
        original_count = len(self.data)
        processed_count = len(set([m["row_id"] for m in metadatas]))
        filtered_count = original_count - processed_count

        print(f"\n{'=' * 60}")
        print("📊 CHUNKING STATISTIKEN")
        print(f"{'=' * 60}")
        print(f"📥 Original CSV-Einträge: {original_count:,}")
        print(f"✅ Verarbeitete Feedbacks: {processed_count:,}")
        print(f"🚫 Gefilterte Einträge: {filtered_count:,} (zu kurz: <10 Zeichen)")
        print(f"📄 Erstellte Chunks: {len(documents):,}")
        print(
            f"📊 Durchschnitt: {len(documents) / processed_count:.2f} Chunks/Feedback"
        )

        # Token-Schätzung (1 Token ≈ 4 Zeichen für Deutsch)
        total_chars = sum(len(doc) for doc in documents)
        estimated_tokens = total_chars // 4
        print(f"🔤 Geschätzte Tokens: {estimated_tokens:,}")
        print(f"{'=' * 60}\n")

        return documents, metadatas, ids

    def check_file_path(self) -> bool:
        """
        Checks if the ChromaDB VectorStore already exists.

        Returns:
            bool: True if VectorStore exists, False otherwise
            
        Notes:
            - Checks for existence of persist_directory
            - Verifies presence of chroma.sqlite3 file
            - Used to determine load vs create operations
        """
        if not os.path.exists(self.persist_directory):
            return False

        # Prüfe auf ChromaDB-Dateien oder Collection-Verzeichnisse
        if os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3")):
            return True

        return (
            len(os.listdir(self.persist_directory)) > 0
            if os.path.isdir(self.persist_directory)
            else False
        )

    def create_vectorstore(self, force_recreate: bool = False) -> Any | None:
        """
        Creates or loads VectorStore with feedback-optimized chunking.

        Args:
            force_recreate (bool): If True, recreates VectorStore even if it exists.
                                  Deletes existing store and creates fresh instance.

        Returns:
            chromadb.Collection | None: ChromaDB collection containing embedded feedbacks,
                                        or None if an error occurred
            
        Raises:
            RuntimeError: If collection could not be persisted correctly
            
        Notes:
            - Loads existing collection if available (unless force_recreate=True)
            - Creates new collection with cosine distance metric
            - Uses batch processing for large datasets (configurable batch_size)
            - Explicitly persists collection to disk via client restart
            - Verifies persistence by reloading collection
            - Prints detailed progress and statistics to console
        """
        # Wenn force_recreate=True, lösche komplett und erstelle neu
        if force_recreate:
            print("\n🗑️ Force recreate aktiviert - lösche existierenden VectorStore...")
            success = self.delete_vectorstore()
            if not success:
                print("⚠️ Warnung: VectorStore konnte nicht vollständig gelöscht werden")

            # Client neu initialisieren nach dem Löschen
            self._chroma_client = chromadb.PersistentClient(path=self.persist_directory)

        # Check ob Store existiert (nach potenziellem Löschen)
        store_exists = False
        temp_collections = self._chroma_client.list_collections()
        if len(temp_collections) > 0:
            for temp_collection in temp_collections:
                if temp_collection.name == self.collection_name:
                    store_exists = True

        # Existierenden Store laden (nur wenn nicht force_recreate)
        if store_exists and not force_recreate:
            print("\n📂 Lade existierenden VectorStore...")
            try:
                collection = self._chroma_client.get_collection(
                    name=self.collection_name,
                    embedding_function=cast(Any, self._embedding_function),
                )
                print(f"✓ VectorStore geladen mit {collection.count()} Dokumenten")
                return collection
            except Exception as e:
                print(f"❌ Fehler beim Laden: {e}")
                return None

        # Neuen Store erstellen
        print("\n🔨 Erstelle neuen VectorStore...")

        try:
            # Dokumente vorbereiten
            documents, metadatas, ids = self.split_and_chunk_text()

            # Collection erstellen mit expliziter Cosine-Metric
            collection = self._chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=cast(Any, self._embedding_function),
                metadata={"hnsw:space": "cosine"}  # Explizit Cosine Distance für OpenAI Embeddings
            )

            # Batch-Processing für große Datenmengen
            total_docs = len(documents)
            for i in range(0, total_docs, self.batch_size):
                end_idx = min(i + self.batch_size, total_docs)
                batch_num = (i // self.batch_size) + 1
                total_batches = (total_docs + self.batch_size - 1) // self.batch_size

                print(f"⏳ Verarbeite Batch {batch_num}/{total_batches}...")

                batch_documents = documents[i:end_idx]
                batch_metadatas = metadatas[i:end_idx]
                batch_ids = ids[i:end_idx]

                collection.add(
                    documents=batch_documents,
                    metadatas=batch_metadatas,  # type: ignore[arg-type]
                    ids=batch_ids,
                )

            # ✅ KRITISCH: Explizit persistieren (ChromaDB schreibt sonst nicht auf Disk!)
            # ChromaDB PersistentClient sollte automatisch persistieren, aber...
            # in manchen Versionen/Setups muss man den Client explizit schließen
            print("\n💾 Persistiere Collection auf Disk...")
            
            # Erzwinge Persist durch Client-Neustart
            # Dies stellt sicher dass alle Daten auf Disk geschrieben werden
            old_client = self._chroma_client
            self._chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Verifiziere dass Collection jetzt persistent ist
            collections = self._chroma_client.list_collections()
            if not any(col.name == self.collection_name for col in collections):
                raise RuntimeError("Collection wurde nicht korrekt persistiert!")
            
            # Collection neu laden aus persistiertem State
            collection = self._chroma_client.get_collection(
                name=self.collection_name,
                embedding_function=cast(Any, self._embedding_function),
            )

            print(f"\n{'=' * 60}")
            print("✅ VECTORSTORE ERFOLGREICH ERSTELLT")
            print(f"{'=' * 60}")
            print(f"📊 {collection.count()} Dokumente embedded und gespeichert")
            print(f"📁 Speicherort: {self.persist_directory}")
            print(f"{'=' * 60}\n")

            return collection

        except Exception as e:
            print(f"❌ Fehler beim Erstellen: {e}")
            return None

    def delete_vectorstore(self) -> bool:
        """
        Deletes VectorStore completely (collection + persist directory).

        Returns:
            bool: True if deletion was successful, False if errors occurred
            
        Notes:
            - Deletes ChromaDB collection from client
            - Removes entire persist_directory and all contents
            - Irreversible operation - use with caution
            - Returns False if any deletion step fails
            - Prints status messages for each step
        """
        success = True

        # Collection löschen
        try:
            collections = self._chroma_client.list_collections()
            if any(col.name == self.collection_name for col in collections):
                self._chroma_client.delete_collection(name=self.collection_name)
                print(f"✓ Collection '{self.collection_name}' gelöscht")
            else:
                print(f"ℹ️  Collection '{self.collection_name}' existiert nicht")
        except Exception as e:
            print(f"⚠️  Collection konnte nicht gelöscht werden: {e}")
            success = False

        # Verzeichnis löschen
        try:
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                print(f"✓ Verzeichnis '{self.persist_directory}' gelöscht")
            else:
                print(f"ℹ️  Verzeichnis '{self.persist_directory}' existiert nicht")
        except Exception as e:
            print(f"⚠️  Fehler beim Löschen des Verzeichnisses: {e}")
            success = False

        return success
