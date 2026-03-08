from core.assignment_manager import add_assignment


def add_assignment_tool(title: str, subject: str, due_date: str):
    """
    Add a new assignment.

    Parameters
    ----------
    title : str
        Assignment title
    subject : str
        Subject name
    due_date : str
        Due date in YYYY-MM-DD format
    """

    try:

        if not title:
            return "Error: Assignment title is required."

        if not due_date:
            return "Error: Due date is required."

        result = add_assignment(title, subject, due_date)

        return result

    except Exception as e:
        return f"Error adding assignment: {str(e)}"
