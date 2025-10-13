import os
from agents import (
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)
from openai import AsyncAzureOpenAI, OpenAIError
from typing import Any
import pandas as pd

from clean_csv_file import CSVloader
from prepare_customer_data import PrepareCustomerData
from db.vectorstore_chroma import ChromaVectorStore
from test.test_questions import TestQuestions


def load_csv(path: str, write_local: bool = False) -> pd.DataFrame:
    # Load CSV file
    csv_loader = CSVloader(path=path, encoding="utf-8")
    df = csv_loader.load_csv()

    # Prepare DataFrame with additional features
    customer_data = PrepareCustomerData(
        data=df,
        nps_category=True,
        nps_category_col_name="NPS",
        feedback_length=True,
        feedback_token_model="gpt-4o-mini",
        feedback_col_name="Verbatim",
        sentiment_analysis=True,
        sentiment_col_name="Verbatim",
    )

    df = customer_data.data

    # Optionally write enhanced CSV locally
    if write_local:
        write_prepared_csv(df)

    print(f"✅ CSV-Daten geladen: {df.shape[0]} Einträge")

    return df


def write_prepared_csv(
    data: pd.DataFrame, path: str = "./data/feedback_data_enhanced.csv"
) -> None:
    # Schreibe DataFrame in CSV-Datei
    data.to_csv(path, index=False, encoding="utf-8", mode="w")
    print(f"Enhanced CSV written to {path}")


def load_vectorstore(
    data: pd.DataFrame, type: str = "chroma", create_new_store: bool = False
) -> Any | None:
    # Erstelle oder lade Chroma Vectorstore
    if type == "chroma":
        vectorstore_manager = ChromaVectorStore(
            data=data,
            file_path="./chroma",
            file_name="feedback_vectorstore",
            collection_name="feedback_data",
            batch_size=100,
            embedding_model="text-embedding-3-small",
        )

        chroma_collection = vectorstore_manager.create_vectorstore(
            force_recreate=create_new_store
        )
        get_vectorstore_info(collection=chroma_collection)

        if not validate_vectorstore(chroma_collection):
            return None
        return chroma_collection
    print(
        f"❌ FEHLER: Unbekannter VectorStore-Typ '{type}'. Have to be 'chroma' for now."
    )
    return None


def validate_vectorstore(collection: Any | None) -> bool:
    if collection is None:
        print("❌ FEHLER: VectorStore ist None!")
        return False
    if collection.count() == 0:
        print("❌ FEHLER: VectorStore ist leer - keine Dokumente wurden erstellt!")
        return False
    return True


def get_vectorstore_info(collection: Any | None) -> None:
    print(
        f"VectorStore loaded with {collection.count() if collection else 0} documents"
    )


def get_azure_openai_client() -> AsyncAzureOpenAI | None:
    # Check required environment variables
    if not os.environ.get("AZURE_OPENAI_API_KEY", ""):
        raise ValueError("AZURE_OPENAI_API_KEY environment variable not set")
    if not os.environ.get("AZURE_OPENAI_ENDPOINT", ""):
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
    if not os.environ.get("AZURE_OPENAI_API_VERSION", ""):
        raise ValueError("AZURE_OPENAI_API_VERSION environment variable not set")

    try:
        azure_client = AsyncAzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
        )

        set_default_openai_client(azure_client)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(True)

        print("✅ Azure OpenAI Client initialized")

        return azure_client
    except OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
        print("❌ FEHLER: Azure OpenAI Client konnte nicht initialisiert werden!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("❌ FEHLER: Azure OpenAI Client konnte nicht initialisiert werden!")
    return None


def get_test_questions(
    test_meta: bool = True,
    test_feedback: bool = True,
    test_validation: bool = True,
    test_sentiment: bool = True,
    test_parameters: bool = True,
    test_complex: bool = True,
    test_edge: bool = False,
    questions_per_category: int = 2,
) -> list[str]:
    """
    Generiert Testfragen basierend auf den übergebenen Flags.

    Args:
        test_meta: Meta-Fragen (Datensatz-Informationen)
        test_feedback: Feedback-Analysen
        test_validation: Markt-Validierung
        test_sentiment: Sentiment-Analysen
        test_parameters: User-Parameter Extraktion
        test_complex: Komplexe Multi-Kriterien Queries
        test_edge: Edge Cases (standardmäßig deaktiviert)
        questions_per_category: Anzahl Fragen pro aktivierter Kategorie

    Returns:
        Liste der generierten Testfragen
    """
    test_queries = []

    if test_meta:
        questions = TestQuestions.get_questions_by_category("META_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_feedback:
        questions = TestQuestions.get_questions_by_category(
            "FEEDBACK_ANALYSIS_QUESTIONS"
        )
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_validation:
        questions = TestQuestions.get_questions_by_category(
            "MARKET_VALIDATION_QUESTIONS"
        )
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_sentiment:
        questions = TestQuestions.get_questions_by_category("SENTIMENT_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_parameters:
        questions = TestQuestions.get_questions_by_category("USER_PARAMETER_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_complex:
        questions = TestQuestions.get_questions_by_category("COMPLEX_QUESTIONS")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    if test_edge:
        questions = TestQuestions.get_questions_by_category("EDGE_CASES")
        if questions_per_category > 0 and questions_per_category <= len(questions):
            test_queries.extend(questions[:questions_per_category])
        else:
            test_queries.extend(questions)

    return test_queries
