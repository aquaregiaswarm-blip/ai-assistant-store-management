"""GM AI Agent orchestrator using Claude API with tools."""
import json
from typing import Dict, List, Optional, Generator
from anthropic import Anthropic

from .prompts import get_system_prompt
from .tools import TOOL_DEFINITIONS, execute_tool
from ..config import settings


class GMAgent:
    """AI Agent for Swig General Managers."""

    def __init__(self, store_id: int, store_name: str):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.store_id = store_id
        self.store_name = store_name
        self.current_date = settings.data_current_date
        self.conversation_history: List[Dict] = []
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """Get the system prompt with store context."""
        return get_system_prompt(
            store_id=self.store_id,
            store_name=self.store_name,
            current_date=self.current_date
        )

    def chat(self, user_message: str) -> str:
        """Send a message and get a response (non-streaming)."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self._call_claude()

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            tool_results = self._process_tool_calls(response)
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            response = self._call_claude()

        # Extract final text response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, 'text'):
                assistant_message += block.text

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Send a message and stream the response."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # First, handle any tool calls needed
        response = self._call_claude()

        while response.stop_reason == "tool_use":
            tool_results = self._process_tool_calls(response)
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            response = self._call_claude()

        # Now stream the final response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, 'text'):
                assistant_message += block.text
                yield block.text

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

    def _call_claude(self):
        """Make a call to the Claude API."""
        return self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.get_system_prompt(),
            tools=TOOL_DEFINITIONS,
            messages=self.conversation_history
        )

    def _process_tool_calls(self, response) -> List[Dict]:
        """Process tool calls from the response and return results."""
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Inject store_id and date if not provided
                if "store_id" not in tool_input:
                    tool_input["store_id"] = self.store_id
                if "date" not in tool_input:
                    tool_input["date"] = self.current_date

                # Execute the tool
                result = execute_tool(tool_name, tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        return tool_results

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def set_store(self, store_id: int, store_name: str):
        """Change the active store."""
        self.store_id = store_id
        self.store_name = store_name
        self.clear_history()


# Session management for API
_agent_sessions: Dict[str, GMAgent] = {}


def get_or_create_agent(session_id: str, store_id: int, store_name: str) -> GMAgent:
    """Get existing agent session or create a new one."""
    if session_id not in _agent_sessions:
        _agent_sessions[session_id] = GMAgent(store_id, store_name)
    else:
        # Update store if changed
        agent = _agent_sessions[session_id]
        if agent.store_id != store_id:
            agent.set_store(store_id, store_name)

    return _agent_sessions[session_id]


def clear_session(session_id: str):
    """Clear a session."""
    if session_id in _agent_sessions:
        del _agent_sessions[session_id]
