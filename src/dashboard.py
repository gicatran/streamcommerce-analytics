def get_dashboard_html() -> str:
    """
    Load dashboard HTML from file
    """

    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>Error: Dashboard template not found</h1>"
