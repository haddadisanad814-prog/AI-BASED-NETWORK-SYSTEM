from system_status import status

def ai_brain(query):
    query = query.lower()

    if "network" in query and "health" in query:
        return status

    if "failed" in query:
        failed = [k for k,v in status.items() if v == "failure"]
        return failed if failed else "No failed nodes"

    if "report" in query:
        return "Today's report generated from logs"

    return "Command not understood"