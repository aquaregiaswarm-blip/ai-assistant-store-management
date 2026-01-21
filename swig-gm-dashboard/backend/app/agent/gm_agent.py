"""GM AI Agent orchestrator using OpenAI API with tools."""
import json
import os
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List, Generator
from openai import OpenAI


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal and date types from DuckDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

from .prompts import get_system_prompt
from .tools import execute_tool
from ..config import settings


# Convert our tool definitions to OpenAI function format
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_transactions",
            "description": "Query sales transaction data with flexible aggregation. Use this to answer questions about sales, revenue, transaction counts, and order patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"},
                    "aggregation": {
                        "type": "string",
                        "enum": ["daily", "hourly", "by_channel", "by_employee"],
                        "description": "How to aggregate the data"
                    }
                },
                "required": ["store_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_workforce",
            "description": "Query workforce and scheduling data. Use this for questions about who's working, schedules, attendance, and labor hours.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "query_type": {
                        "type": "string",
                        "enum": ["schedule_today", "whos_working", "attendance", "minors"],
                        "description": "Type of workforce query"
                    },
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"}
                },
                "required": ["store_id", "query_type", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_compliance",
            "description": "Check for labor compliance issues including minor hours, break violations, and overtime risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "check_type": {
                        "type": "string",
                        "enum": ["violations", "minor_status", "overtime_risk", "all"],
                        "description": "Type of compliance check"
                    },
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"}
                },
                "required": ["store_id", "check_type", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_performance",
            "description": "Compare current performance to historical periods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "date": {"type": "string", "description": "Date to compare from in YYYY-MM-DD format"},
                    "comparison": {
                        "type": "string",
                        "enum": ["yesterday", "last_week", "same_day_last_week"],
                        "description": "What period to compare against"
                    }
                },
                "required": ["store_id", "date", "comparison"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_items",
            "description": "Get the best-selling items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"},
                    "limit": {"type": "integer", "description": "Number of items to return (default 10)"},
                    "item_type": {
                        "type": "string",
                        "enum": ["Base_Beverage", "Food", "Modifier", "all"],
                        "description": "Filter by item type"
                    }
                },
                "required": ["store_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_linebuster",
            "description": "Analyze linebuster effectiveness through queue position data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"}
                },
                "required": ["store_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_peak_hours",
            "description": "Get detailed peak hour analysis showing busiest times.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "integer", "description": "Store ID to query"},
                    "date": {"type": "string", "description": "Date to query in YYYY-MM-DD format"}
                },
                "required": ["store_id", "date"]
            }
        }
    }
]


class GMAgent:
    """AI Agent for Swig General Managers using OpenAI."""

    def __init__(self, store_id: int, store_name: str):
        # Get API key from settings (loaded from .env) or environment
        api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)
        self.store_id = store_id
        self.store_name = store_name
        self.current_date = settings.data_current_date
        self.conversation_history: List[Dict] = []
        self.model = "gpt-4o"
        self.max_tokens = 4096

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

        response = self._call_openai()

        # Handle tool calls loop
        while response.choices[0].message.tool_calls:
            tool_results = self._process_tool_calls(response)

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

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """Send a message and stream the response."""
        # For simplicity, just yield the full response
        response = self.chat(user_message)
        yield response

    def _call_openai(self):
        """Make a call to the OpenAI API."""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(self.conversation_history)

        return self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            tools=OPENAI_TOOLS,
            messages=messages
        )

    def _process_tool_calls(self, response) -> List[Dict]:
        """Process tool calls from the response and return results."""
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
