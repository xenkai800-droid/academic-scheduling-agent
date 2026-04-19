from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import streamlit as st
import traceback


# ---------------- IMPORT TOOLS ----------------

from tools.daily_planner_tool import daily_planner_tool
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
from tools.add_assignment_tool import add_assignment_tool
from tools.reminder_tool import check_due_assignments_tool
from tools.study_suggestion_tool import suggest_study_session_tool
from tools.nl_schedule_tool import schedule_from_text_tool
from tools.list_events_tool import list_events_tool
from tools.semester_template_tool import load_semester_template


# ---------------- INPUT SCHEMAS ----------------

class QueryInput(BaseModel):
    query: str = Field(description="User query")


class DailyPlannerInput(BaseModel):
    day: str = Field(default="today", description="Which day to plan")


class ScheduleInput(BaseModel):
    query: str = Field(description="User scheduling request")


class FreeTimeInput(BaseModel):
    query: str = Field(description="User query like 'tomorrow', 'monday morning'")


# ---------------- DEBUG WRAPPER ----------------

def debug_tool(func):
    def wrapper(*args, **kwargs):
        print(f"\n[TOOL CALL] {func.__name__}")
        print("ARGS:", args, kwargs)

        try:
            result = func(*args, **kwargs)
            print("[TOOL RESULT]:", result)
            return result
        except Exception as e:
            print("[TOOL ERROR]:", str(e))
            traceback.print_exc()
            return f"❌ Tool Error: {str(e)}"
    return wrapper


# ---------------- TOOLS ----------------

tools = [

    StructuredTool.from_function(
        name="load_semester_template",
        func=debug_tool(load_semester_template),
        description="Load semester timetable template",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="schedule_from_text",
        func=debug_tool(schedule_from_text_tool),
        args_schema=ScheduleInput,
        description="Schedule an event from natural language",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="find_free_time",
        func=debug_tool(find_free_time),
        args_schema=FreeTimeInput,
        description="Find free time based on query",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="list_events",
        func=debug_tool(list_events_tool),
        args_schema=QueryInput,
        description="Show events (today, tomorrow, etc.)",
        return_direct=True,
    ),

    # 🔥 FIXED ASSIGNMENT TOOL
    StructuredTool.from_function(
        name="add_assignment",
        func=debug_tool(add_assignment_tool),
        args_schema=QueryInput,  # ✅ THIS IS THE FIX
        description="Add assignment (e.g. 'add assignment physics due tomorrow')",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="check_due_assignments",
        func=debug_tool(check_due_assignments_tool),
        description="Check assignments due",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="suggest_study_session",
        func=debug_tool(suggest_study_session_tool),
        description="Suggest study session",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="daily_planner",
        func=debug_tool(daily_planner_tool),
        args_schema=DailyPlannerInput,
        description="Generate a daily plan",
        return_direct=True,
    ),

    StructuredTool.from_function(
        name="add_event",
        func=debug_tool(add_event_tool),
        description="Internal scheduling tool",
        return_direct=True,
    ),
]


# ---------------- LLM ----------------

llm = ChatGroq(
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=800,
)


# ---------------- SYSTEM PROMPT ----------------

SYSTEM_PROMPT = """
You are a smart academic scheduling assistant.

Always use tools when possible.

If user asks about schedule:
→ pass full query to list_events

If scheduling:
→ use schedule_from_text

If free time:
→ use find_free_time

If assignment:
→ use add_assignment and pass full query

Be short, clear, helpful.
"""


# ---------------- AGENT ----------------

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    debug=False,
)


# ---------------- RESPONSE CLEANER ----------------

def clean_response(text):

    if not text:
        return "⚠️ I couldn't understand that."

    text = text.strip()

    if len(text) > 1500:
        text = text[:1500] + "..."

    return text


# ---------------- RUN AGENT ----------------

def run_agent(query):

    print("\n========== NEW REQUEST ==========")
    print("USER:", query)

    try:

        if not query or not query.strip():
            return "❌ Please enter a valid request."

        result = agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ]
            }
        )

        messages = result.get("messages", [])

        print("\n--- FULL MESSAGE TRACE ---")

        for msg in messages:
            print(type(msg).__name__, ":", getattr(msg, "content", ""))

        print("--- END TRACE ---\n")

        for msg in reversed(messages):
            if msg.__class__.__name__ == "ToolMessage" and msg.content:
                return clean_response(msg.content)

        for msg in reversed(messages):
            if msg.__class__.__name__ == "AIMessage" and msg.content:
                return clean_response(msg.content)

        return "⚠️ I couldn't understand that."

    except Exception as e:
        traceback.print_exc()
        return f"❌ Error: {str(e)}"