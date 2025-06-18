import re

def parse_log_line(line):
    """
    Extracts timestamp (up to seconds), level, and message from a log line.
    Returns:
        (timestamp, level + message) or (None, None) if the line is malformed.
    """
    # Match format: TIMESTAMP LEVEL CLASS: MESSAGE
    match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} (\w+) (.+?): (.*)", line)

    if not match:
        return None, None

    timestamp = match.group(1) 
    level = match.group(2)
    message = match.group(4)

    return timestamp, f"{level} {message}"