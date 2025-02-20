import logging

LOG_FILE = "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def dedent(string):
    lines = [line for line in string.split("\n") if line.strip()]
    min_indent = len(lines[0]) - len(lines[0].lstrip())
    for line in lines[1:]:
        min_indent = min(min_indent, len(line) - len(line.lstrip()))
    result = '\n'.join([line[min_indent:] for line in lines])
    return result

logger = logging.getLogger("main_logger")