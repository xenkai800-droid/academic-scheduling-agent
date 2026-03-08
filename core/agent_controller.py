from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
import streamlit as st

from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
from tools.add_assignment_tool import add_assignment_tool
from tools.reminder_tool import check_due_assignments_tool
from tools.study_suggestion_tool import suggest_study_session_tool
from tools.nl_schedule_tool import schedule_from_text_tool
from tools.list_events_tool import list_events_tool

# --------------------------------------------------
# DEFINE TOOLS
# --------------------------------------------------
tools = [
    StructuredTool.from_function(
        name="add_event",
        func=add_event_tool,
        description="""
        Create a calendar event with title, date, start time and end time.

        Use this tool ONLY when the date is in YYYY-MM-DD format
        and the time is in HH:MM format.

        If the user uses natural language like "tomorrow" or "2pm",
        use the schedule_from_text tool instead.
        """,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="find_free_time",
        func=find_free_time,
        description=" Use when the user asks about free time, availability,specific dates, weekdays, or periods like morning/afternoon/evening.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="add_assignment",
        func=add_assignment_tool,
        description="Add an assignment with title, subject and due date.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="check_due_assignments",
        func=check_due_assignments_tool,
        description="Check assignments that are due today or tomorrow.",
        return_direct=True,
    ),
    # reasoning tool
    StructuredTool.from_function(
        name="suggest_study_session",
        func=suggest_study_session_tool,
        description="""
        Use this tool when the user asks about:
        - when they should study
        - planning study time
        - study schedule
        - when to work on assignments
        - finding time to study

        This tool checks assignments and available free time to recommend a study slot.
        """,
        return_direct=False,
    ),
    StructuredTool.from_function(
        name="schedule_from_text",
        func=schedule_from_text_tool,
        description="Schedule an event using natural language like 'schedule physics class tomorrow at 2pm'.",
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="list_events",
        func=list_events_tool,
        description="""
        Use this tool when the user asks about:
        - their schedule
        - upcoming events
        - meetings tomorrow
        - what events they have
        - their calendar
        """,
        return_direct=True,
    ),
]


# --------------------------------------------------
# LLM (Groq)
# --------------------------------------------------

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=200,
)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------
SYSTEM_PROMPT = """
You are an academic scheduling assistant.

You help students manage:

• calendar events
• assignments
• study sessions
• free time

You have access to several tools.

TOOL USAGE RULES:

add_event  
→ Use ONLY when the user provides a specific date (YYYY-MM-DD) and time.

schedule_from_text  
→ Use when the user wants to schedule an event using natural language
(e.g., "schedule physics class tomorrow at 2pm").

find_free_time  
→ Use when the user asks about available time or free slots.

check_due_assignments  
→ Use when the user asks about assignments or deadlines.

suggest_study_session  
→ Use when the user asks when they should study or plan study time.

list_events  
→ Use when the user asks about their schedule, meetings, or events.

IMPORTANT RULES:

• Call ONLY ONE tool unless absolutely necessary.
• If a tool returns the answer, respond to the user.
• Do NOT call another tool after receiving a tool result.
"""

# --------------------------------------------------
# CREATE AGENT
# --------------------------------------------------

agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT, debug=True)


# --------------------------------------------------
# RUN AGENT
# --------------------------------------------------


def run_agent(query):

    try:

        result = agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ]
            }
        )

        messages = result["messages"]

        # find the last AI response
        for msg in reversed(messages):

            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "No response generated."

    except Exception as e:

        return f"Agent error: {str(e)}"
