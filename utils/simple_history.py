"""
Simple Conversation History Manager - Alternative zum komplexen SessionContext.
Optimiert für Streamlit Integration und maximale Einfachheit.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text using tiktoken with clean fallback logic.

    Args:
        text: Input text to tokenize
        model: OpenAI model name for encoding

    Returns:
        int: Token count (actual tokens or estimated from chars)
    """
    if not text:
        return 0

    if not TIKTOKEN_AVAILABLE or tiktoken is None:
        # Fallback: 1 token ≈ 4 chars for German/English
        return len(str(text)) // 4

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(str(text)))


class SimpleConversationHistory:
    """
    Einfache Conversation History für User-Agent Interactions.
    Optimiert für Streamlit und eine einfache Nutzung.
    """

    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_interaction(
        self,
        user_input: str,
        agent_response: str,
        agent_name: str = "Assistant",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Füge eine User-Agent Interaction zur History hinzu.

        Args:
            user_input: Die Benutzereingabe
            agent_response: Die Agent-Antwort
            agent_name: Name des Agents (optional)
            metadata: Zusätzliche Metadaten (optional)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_name,
            "response": str(agent_response),  # Ensure string for UI display
            "metadata": metadata or {},
        }

        self.history.append(entry)

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Hole die Conversation History.

        Args:
            last_n: Nur die letzten N Einträge (None = alle)

        Returns:
            Liste der Conversation Entries
        """
        if last_n is None:
            return self.history.copy()
        return self.history[-last_n:] if last_n > 0 else []

    def get_last_response(self) -> Optional[str]:
        """Hole die letzte Agent-Response oder None."""
        if self.history:
            return self.history[-1]["response"]
        return None

    def get_last_user_input(self) -> Optional[str]:
        """Hole den letzten User-Input oder None."""
        if self.history:
            return self.history[-1]["user"]
        return None

    def clear_history(self):
        """Lösche die komplette History."""
        self.history.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_conversation_count(self) -> int:
        """Anzahl der Conversation Turns."""
        return len(self.history)

    def search_history(
        self, search_term: str, case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Einfache Suche in der History.

        Args:
            search_term: Suchbegriff
            case_sensitive: Groß-/Kleinschreibung beachten

        Returns:
            Liste der gefundenen Entries
        """
        if not case_sensitive:
            search_term = search_term.lower()

        results = []
        for entry in self.history:
            user_text = entry["user"] if case_sensitive else entry["user"].lower()
            response_text = (
                entry["response"] if case_sensitive else entry["response"].lower()
            )

            if search_term in user_text or search_term in response_text:
                results.append(entry)

        return results

    def export_history(self, format: str = "json") -> str:
        """
        Exportiere History in verschiedenen Formaten.

        Args:
            format: "json", "text", oder "markdown"

        Returns:
            Formatierte History als String
        """
        if format == "json":
            return json.dumps(self.history, indent=2, ensure_ascii=False)

        elif format == "text":
            lines = [f"=== Conversation History ({self.session_id}) ==="]
            for i, entry in enumerate(self.history, 1):
                lines.append(f"\n[{i}] {entry['timestamp'][:19]}")
                lines.append(f"User: {entry['user']}")
                lines.append(f"{entry['agent']}: {entry['response']}")
            return "\n".join(lines)

        elif format == "markdown":
            lines = [f"# Conversation History ({self.session_id})"]
            for i, entry in enumerate(self.history, 1):
                lines.append(f"\n## Interaction {i} - {entry['timestamp'][:19]}")
                lines.append(f"**User:** {entry['user']}")
                lines.append(f"**{entry['agent']}:** {entry['response']}")
            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Einfache Session-Statistiken."""
        if not self.history:
            return {"total_interactions": 0, "session_id": self.session_id}

        # Zähle Agent-Typen und Token
        agents = {}
        total_user_tokens = 0
        total_response_tokens = 0

        for entry in self.history:
            agent = entry["agent"]
            agents[agent] = agents.get(agent, 0) + 1
            total_user_tokens += count_tokens(entry["user"])
            total_response_tokens += count_tokens(entry["response"])

        first_interaction = self.history[0]["timestamp"]
        last_interaction = self.history[-1]["timestamp"]

        return {
            "session_id": self.session_id,
            "total_interactions": len(self.history),
            "agents_used": agents,
            "first_interaction": first_interaction,
            "last_interaction": last_interaction,
            "avg_user_input_length": total_user_tokens // len(self.history),
            "avg_response_length": total_response_tokens // len(self.history),
        }


# Global instance for simple usage (optional)
_default_conversation = None


def get_conversation_history() -> SimpleConversationHistory:
    """
    Singleton pattern für eine Default-Conversation.
    Kann in einfachen Anwendungen verwendet werden.
    """
    global _default_conversation
    if _default_conversation is None:
        _default_conversation = SimpleConversationHistory()
    return _default_conversation


def reset_conversation():
    """Reset der Default-Conversation."""
    global _default_conversation
    _default_conversation = None


# Convenience functions für noch einfachere Usage
def add_chat(user_input: str, agent_response: str, agent_name: str = "Assistant"):
    """Convenience function - füge Chat zur default conversation hinzu."""
    conversation = get_conversation_history()
    conversation.add_interaction(user_input, agent_response, agent_name)


def get_chat_history(last_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """Convenience function - hole Chat History."""
    conversation = get_conversation_history()
    return conversation.get_history(last_n)
