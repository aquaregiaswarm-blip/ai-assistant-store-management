"""GM AI Agent orchestrator supporting OpenAI and Claude via Vertex AI."""
import json
import os
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List, Generator, Optional

from .prompts import get_system_prompt
from .tools import execute_tool, TOOL_DEFINITIONS
from ..config import settings


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal and date types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# Convert tool definitions to OpenAI function format
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"]
        }
    }
    for tool in TOOL_DEFINITIONS
]


class GMAgent:
    """AI Agent for Swig General Managers supporting OpenAI and Claude."""

    def __init__(self, store_id: int, store_name: str):
        self.store_id = store_id
        self.store_name = store_name
        self.current_date = settings.data_current_date
        self.conversation_history: List[Dict] = []
        self.max_tokens = 4096
        
        # Determine provider from model name
        self.model = settings.llm_model
        self.provider = self._detect_provider(self.model)
        
        # Initialize appropriate client
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        else:
            raise ValueError(f"Unknown model provider for: {self.model}")

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        if model.startswith("gpt-") or model.startswith("o1"):
            return "openai"
        elif model.startswith("claude-"):
            return "anthropic"
        else:
            # Default to OpenAI for unknown models
            return "openai"

    def _init_openai(self):
        """Initialize OpenAI client."""
        from openai import OpenAI
        
        api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")
        
        self.client = OpenAI(api_key=api_key)

    def _init_anthropic(self):
        """Initialize Anthropic client via Vertex AI."""
        from anthropic import AnthropicVertex
        
        self.client = AnthropicVertex(
            region=settings.gcp_region,
            project_id=settings.gcp_project_id
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt with store context."""
        return get_system_prompt(
            store_id=self.store_id,
            store_name=self.store_name,
            current_date=self.current_date
        )

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        if self.provider == "openai":
            return self._chat_openai()
        else:
            return self._chat_anthropic()

    def _chat_openai(self) -> str:
        """Handle chat with OpenAI."""
        response = self._call_openai()

        # Handle tool calls loop
        while response.choices[0].message.tool_calls:
            tool_results = self._process_openai_tool_calls(response)

            # Add assistant message with tool calls
            self.conversation_history.append(response.choices[0].message)

            # Add tool results
            for result in tool_results:
                self.conversation_history.append(result)

            response = self._call_openai()

        # Extract final text response
        assistant_message = response.choices[0].message.content or ""

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def _chat_anthropic(self) -> str:
        """Handle chat with Anthropic/Claude."""
        response = self._call_anthropic()

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            tool_results = self._process_anthropic_tool_use(response)

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Add tool results
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            response = self._call_anthropic()

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

    def _call_openai(self):
        """Make a call to the OpenAI API."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # Convert history for OpenAI (handle message objects)
        for msg in self.conversation_history:
            if hasattr(msg, 'model_dump'):
                messages.append(msg.model_dump())
            else:
                messages.append(msg)

        return self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            tools=OPENAI_TOOLS,
            messages=messages
        )

    def _call_anthropic(self):
        """Make a call to the Anthropic API via Vertex."""
        # Build messages (Anthropic doesn't use system in messages array)
        messages = []
        for msg in self.conversation_history:
            if isinstance(msg.get("content"), list):
                # Already formatted content blocks
                messages.append(msg)
            else:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.get_system_prompt(),
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

    def _process_openai_tool_calls(self, response) -> List[Dict]:
        """Process tool calls from OpenAI response."""
        tool_results = []

        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            # Inject store_id and date if not provided
            if "store_id" not in tool_input:
                tool_input["store_id"] = self.store_id
            if "date" not in tool_input:
                tool_input["date"] = self.current_date

            # Execute the tool
            result = execute_tool(tool_name, tool_input)

            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, cls=DecimalEncoder)
            })

        return tool_results

    def _process_anthropic_tool_use(self, response) -> List[Dict]:
        """Process tool use from Anthropic response."""
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
                    "content": json.dumps(result, cls=DecimalEncoder)
                })

        return tool_results

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Send a message and stream the response."""
        # For simplicity, just yield the full response
        response = self.chat(user_message)
        yield response

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
