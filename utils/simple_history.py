"""
Simple Conversation History Manager - Alternative to complex SessionContext.

Optimized for Streamlit integration and maximum simplicity.
Provides lightweight conversation tracking with statistics and export capabilities.
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
    Simple conversation history for user-agent interactions.
    
    Optimized for Streamlit and straightforward usage.
    
    Features:
        - Lightweight interaction tracking
        - Token counting with automatic fallback
        - Session statistics and analytics
        - Multiple export formats (JSON, text, markdown)
        - Chart marker filtering for agent context
        - Search capabilities
        
    Attributes:
        history (List[Dict[str, Any]]): List of interaction entries
        session_id (str): Unique session identifier (timestamp-based)
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
        Adds a user-agent interaction to the history.

        Args:
            user_input (str): The user's input/question
            agent_response (str): The agent's response
            agent_name (str): Name of the responding agent. Defaults to "Assistant"
            metadata (Optional[Dict[str, Any]]): Additional metadata for the interaction

        Returns:
            None
            
        Notes:
            - Automatically timestamps each interaction
            - Ensures response is converted to string for UI display
            - Metadata defaults to empty dict if not provided
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_name,
            "response": str(agent_response),  # Ensure string for UI display
            "metadata": metadata or {},
        }

        self.history.append(entry)

    def get_history(self, last_n: Optional[int] = None, strip_charts: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation history.

        Args:
            last_n (Optional[int]): Only return the last N entries. None returns all entries
            strip_charts (bool): If True, removes __CHART__ markers from responses.
                               Useful for agent context to save tokens. Defaults to False

        Returns:
            List[Dict[str, Any]]: List of conversation entries with keys:
                - timestamp (str): ISO format timestamp
                - user (str): User input
                - agent (str): Agent name
                - response (str): Agent response (with or without chart markers)
                - metadata (dict): Additional metadata
                
        Notes:
            - Returns copy of history to prevent accidental modifications
            - Chart stripping uses regex pattern: __CHART__.*?__CHART__
            - Useful for reducing token count in agent context
        """
        history = self.history[-last_n:] if last_n and last_n > 0 else self.history.copy()
        
        if strip_charts:
            # Entferne Chart-Marker für Agent-Kontext (Token-Optimierung)
            import re
            cleaned_history = []
            for entry in history:
                cleaned_entry = entry.copy()
                response = entry["response"]
                # Entferne __CHART__pfad__CHART__ Pattern
                cleaned_response = re.sub(r'__CHART__[^_]+__CHART__', '', response)
                cleaned_entry["response"] = cleaned_response.strip()
                cleaned_history.append(cleaned_entry)
            return cleaned_history
        
        return history

    def get_last_response(self) -> Optional[str]:
        """
        Retrieves the last agent response or None.

        Returns:
            Optional[str]: Last agent response text, or None if history is empty
        """
        if self.history:
            return self.history[-1]["response"]
        return None

    def get_last_user_input(self) -> Optional[str]:
        """
        Retrieves the last user input or None.

        Returns:
            Optional[str]: Last user input text, or None if history is empty
        """
        if self.history:
            return self.history[-1]["user"]
        return None

    def clear_history(self):
        """
        Clears the complete history and resets session ID.

        Returns:
            None
            
        Notes:
            - Removes all conversation entries
            - Generates new session ID with current timestamp
            - Useful for starting fresh conversations
        """
        self.history.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_conversation_count(self) -> int:
        """
        Returns the number of conversation turns.

        Returns:
            int: Total number of interactions in history
        """
        return len(self.history)

    def search_history(
        self, search_term: str, case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Simple search in conversation history.

        Args:
            search_term (str): Search term to find
            case_sensitive (bool): Whether to match case. Defaults to False

        Returns:
            List[Dict[str, Any]]: List of matching conversation entries
            
        Notes:
            - Searches both user input and agent responses
            - Case-insensitive by default
            - Returns all entries containing the search term
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
        Exports history in various formats.

        Args:
            format (str): Export format - "json", "text", or "markdown". Defaults to "json"

        Returns:
            str: Formatted history as string
            
        Raises:
            ValueError: If unsupported format is specified
            
        Notes:
            - JSON: Pretty-printed with Unicode support
            - Text: Simple numbered format with timestamps
            - Markdown: Formatted with headers and bold labels
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
        """
        Calculates simple session statistics.

        Returns:
            Dict[str, Any]: Statistics dictionary with keys:
                - session_id (str): Session identifier
                - total_interactions (int): Number of conversation turns
                - agents_used (dict): Count of interactions per agent
                - first_interaction (str): Timestamp of first interaction
                - last_interaction (str): Timestamp of last interaction
                - avg_user_input_length (int): Average user input tokens
                - avg_response_length (int): Average response tokens
                
        Notes:
            - Returns minimal stats if history is empty
            - Token counts use tiktoken or character-based fallback
            - Aggregates agent usage across all interactions
        """
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
    Singleton pattern for a default conversation instance.
    
    Can be used in simple applications for quick conversation tracking.

    Returns:
        SimpleConversationHistory: Global conversation history instance
        
    Notes:
        - Creates instance on first call
        - Returns same instance on subsequent calls
        - Use reset_conversation() to clear and restart
    """
    global _default_conversation
    if _default_conversation is None:
        _default_conversation = SimpleConversationHistory()
    return _default_conversation


def reset_conversation():
    """
    Resets the default conversation.

    Returns:
        None
        
    Notes:
        - Clears the global conversation instance
        - Next call to get_conversation_history() creates new instance
        - Useful for starting fresh sessions
    """
    global _default_conversation
    _default_conversation = None


# Convenience functions für noch einfachere Usage
def add_chat(user_input: str, agent_response: str, agent_name: str = "Assistant"):
    """
    Convenience function - adds chat to default conversation.

    Args:
        user_input (str): User's input message
        agent_response (str): Agent's response message
        agent_name (str): Name of the agent. Defaults to "Assistant"

    Returns:
        None
        
    Notes:
        - Uses global conversation instance
        - Automatically creates instance if needed
        - Simplified API for basic use cases
    """
    conversation = get_conversation_history()
    conversation.add_interaction(user_input, agent_response, agent_name)


def get_chat_history(last_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Convenience function - retrieves chat history.

    Args:
        last_n (Optional[int]): Number of last entries to return. None returns all

    Returns:
        List[Dict[str, Any]]: List of conversation entries
        
    Notes:
        - Uses global conversation instance
        - Wrapper around get_conversation_history().get_history()
        - Simplified API for basic use cases
    """
    conversation = get_conversation_history()
    return conversation.get_history(last_n)
