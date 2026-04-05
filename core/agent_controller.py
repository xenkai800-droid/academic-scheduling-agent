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
        default="today", description="Which day to plan. Either 'today' or 'tomorrow'."
    )


# --------------------------------------------------
# DEFINE TOOLS
# --------------------------------------------------

tools = [
    StructuredTool.from_function(
        name="add_event",
        func=add_event_tool,
        description="""
        ⚠️ INTERNAL TOOL - DO NOT USE FOR NORMAL USER REQUESTS

        This tool should ONLY be used when all details are explicitly structured.

        For natural language scheduling (e.g. "schedule physics tomorrow"),
        ALWAYS use schedule_from_text instead.

        Using this tool directly may bypass validation, conflict detection,
        and holiday rules.
        """,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="find_free_time",
        func=find_free_time,
        description="""
        Use when the user asks about free time, availability,
        specific dates, weekdays, or periods like morning,
        afternoon, or evening.
        """,
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
    StructuredTool.from_function(
        name="suggest_study_session",
        func=suggest_study_session_tool,
        description="""
        Use when the user asks when they should study,
        plan study time, or schedule study sessions.
        """,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="schedule_from_text",
        func=schedule_from_text_tool,
        description="""
        PRIMARY scheduling tool.

        Use this for ALL scheduling requests written in natural language.

        Handles:
        - date parsing
        - time parsing
        - conflict detection
        - holiday validation
        - study recommendations

        Example:
        "schedule physics tomorrow at 2pm"
        """,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="list_events",
        func=list_events_tool,
        description="""
        Use when the user asks about their schedule,
        upcoming events, meetings, or calendar.
        """,
        return_direct=True,
    ),
    StructuredTool.from_function(
        name="daily_planner",
        func=daily_planner_tool,
        args_schema=DailyPlannerInput,
        description="""
        Plan the user's day intelligently.

        This tool:
        • checks upcoming events
        • checks assignments
        • analyzes free time
        • suggests study sessions

        Use when the user asks to:
        - plan their day
        - organize their schedule
        - prepare for tomorrow
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
    max_tokens=800,
)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are an AI academic scheduling assistant.

Your job is to help students organize their academic life by managing:

• calendar events
• assignments
• study sessions
• free time
• daily planning

You should behave like a helpful assistant, not a command parser.
Users may speak casually, imperfectly, or give incomplete instructions.

--------------------------------------------------
USER INPUT HANDLING
--------------------------------------------------

Users may give messy, incomplete, or informal requests.

Examples:
"I have physics tomorrow put it in calendar"
"schedule physics"
"when can I study tomorrow"
"do I have anything tomorrow"

Before choosing a tool:

• Interpret the user's intent
• Rewrite the request internally into a clear action
• Then choose the correct tool

Example:

User: "i have physics tomorrow put it in calendar"

Internal interpretation:
schedule event → physics tomorrow

--------------------------------------------------
CLARIFICATION RULES
--------------------------------------------------

If a request is missing important information required by a tool,
DO NOT call the tool yet.

Instead ask a clarifying question.

Examples:

User: "schedule physics"
Assistant: "What date and time should I schedule it for?"

User: "add assignment math homework"
Assistant: "When is the assignment due?"

User: "schedule study tomorrow"
Assistant: "What subject would you like to study?"

Always guide the user toward a clear request.

--------------------------------------------------
TOOL TYPES
--------------------------------------------------

You have access to several tools.

There are two categories:

--------------------------------------------------
HIGH-LEVEL TOOLS (Orchestrator Tools)
--------------------------------------------------

These tools already perform multiple internal operations.

daily_planner
suggest_study_session
schedule_from_text

If one of these tools is used:

• DO NOT call additional tools afterwards
• The result from that tool is the final answer

--------------------------------------------------
SINGLE-ACTION TOOLS
--------------------------------------------------

These tools perform one specific task.

add_event
add_assignment
list_events
find_free_time
check_due_assignments

--------------------------------------------------
TOOL USAGE GUIDE
--------------------------------------------------

add_event  
→ INTERNAL TOOL. DO NOT USE for user requests.

schedule_from_text  
→ ALWAYS use this for ANY scheduling request, including specific dates like "15 August".

find_free_time  
→ Use when the user asks about available time or free slots.

check_due_assignments  
→ Use when the user asks about assignment deadlines.

suggest_study_session  
→ Use when the user asks when they should study.

list_events  
→ Use when the user asks about their calendar or upcoming events.

daily_planner  
→ Use when the user asks to plan or organize their day.

--------------------------------------------------
GENERAL RULES
--------------------------------------------------

• Prefer the most specific tool available.
• Do not call unnecessary tools.
• If a tool returns the final answer, return it directly.
• If no tool is required, respond normally.
• Always prioritize helpfulness and clarity.

--------------------------------------------------
GOAL
--------------------------------------------------

Your goal is to help students stay organized,
manage their time effectively,
and make scheduling easy and intuitive.
"""


# --------------------------------------------------
# CREATE AGENT
# --------------------------------------------------

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    debug=True,
)


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

        for msg in reversed(messages):

            if hasattr(msg, "content") and msg.content:
                return msg.content

        return "No response generated."

    except Exception as e:

        return f"Agent error: {str(e)}"