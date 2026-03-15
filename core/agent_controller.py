from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import streamlit as st

from tools.daily_planner_tool import daily_planner_tool
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
from tools.add_assignment_tool import add_assignment_tool
from tools.reminder_tool import check_due_assignments_tool
from tools.study_suggestion_tool import suggest_study_session_tool
from tools.nl_schedule_tool import schedule_from_text_tool
from tools.list_events_tool import list_events_tool


# --------------------------------------------------
# TOOL INPUT SCHEMAS
# --------------------------------------------------


class DailyPlannerInput(BaseModel):
    day: str = Field(
        default="today",
        description="Which day to plan. Either 'today' or 'tomorrow'.",
    )


class FreeTimeInput(BaseModel):
    date: str | None = Field(
        default=None,
        description="Optional date in YYYY-MM-DD format",
    )


class AddAssignmentInput(BaseModel):
    title: str
    subject: str
    due_date: str


class AddEventInput(BaseModel):
    title: str
    date: str
    start_time: str
    end_time: str


# --------------------------------------------------
# DEFINE TOOLS
# --------------------------------------------------

tools = [
    StructuredTool.from_function(
        name="add_event",
        func=add_event_tool,
        args_schema=AddEventInput,
        description="""
Create a calendar event.

Requires:
title
date (YYYY-MM-DD)
start_time (HH:MM)
end_time (HH:MM)
""",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="find_free_time",
        func=find_free_time,
        args_schema=FreeTimeInput,
        description="""
Find available free time in the user's schedule.
""",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="add_assignment",
        func=add_assignment_tool,
        args_schema=AddAssignmentInput,
        description="Add a new assignment with title, subject and due date.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="check_due_assignments",
        func=check_due_assignments_tool,
        description="Check assignments due today or tomorrow.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="suggest_study_session",
        func=suggest_study_session_tool,
        description="Suggest study sessions for urgent assignments.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="schedule_from_text",
        func=schedule_from_text_tool,
        description="Schedule an event from natural language.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="list_events",
        func=list_events_tool,
        description="List upcoming calendar events.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="daily_planner",
        func=daily_planner_tool,
        args_schema=DailyPlannerInput,
        description="Generate a daily plan for today or tomorrow.",
        return_direct=True,
    ),
]


# --------------------------------------------------
# LLM CONFIGURATION
# --------------------------------------------------

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=800,
)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an AI academic scheduling assistant.

Your job is to help students manage:

• calendar events
• assignments
• study sessions
• free time
• daily planning

Users may speak casually or provide incomplete instructions.

If required information is missing, ask a clarifying question
instead of calling a tool.

Example:
User: "schedule physics"
Assistant: "What date and time should I schedule it for?"

When a tool provides the final answer,
return that answer directly to the user.

Be clear, helpful, and concise.
"""


# --------------------------------------------------
# CREATE AGENT
# --------------------------------------------------

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    debug=False,
)


# --------------------------------------------------
# RUN AGENT
# --------------------------------------------------


def run_agent(query: str):

    if not query:
        return "Please enter a request."

    try:

        result = agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ]
            }
        )

        messages = result.get("messages", [])

        for msg in reversed(messages):

            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "I couldn't generate a response."

    except Exception as e:

        return f"Assistant error: {str(e)}"
