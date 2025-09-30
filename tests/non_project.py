import sys

PROMPT = "\N{snake} "

match input(PROMPT):
    case "help":
        print(f"Python {sys.version}")