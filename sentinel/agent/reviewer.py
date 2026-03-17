import json
import anthropic
from sentinel.config import ANTHROPIC_API_KEY
from sentinel.tools.static_analysis import run_pylint
from sentinel.tools.ast_parser import parse_structure

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# These are the tools we expose to Claude
# Claude reads these definitions and decides when to call them
TOOLS = [
    {
        "name": "run_pylint",
        "description": "Runs pylint static analysis on a Python file and returns code issues like unused variables, bad naming, complexity problems.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path of the file being analyzed"
                },
                "content": {
                    "type": "string",
                    "description": "The full source code content of the file"
                }
            },
            "required": ["filepath", "content"]
        }
    },
    {
        "name": "parse_structure",
        "description": "Parses the AST of a Python file to extract functions, classes, their sizes and arguments. Useful for spotting oversized functions or poor structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path of the file being analyzed"
                },
                "content": {
                    "type": "string",
                    "description": "The full source code content of the file"
                }
            },
            "required": ["filepath", "content"]
        }
    }
]


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """
    Claude decides to call a tool — we actually execute it here
    and return the result as a string back to Claude.
    """
    if tool_name == "run_pylint":
        result = run_pylint(tool_input["filepath"], tool_input["content"])
    elif tool_name == "parse_structure":
        result = parse_structure(tool_input["filepath"], tool_input["content"])
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result)


def run_review_agent(files: list[dict]) -> str:
    """
    Core agentic loop.
    Sends files to Claude, lets it call tools, feeds results back,
    until Claude is ready to write the final report.
    """

    # Build the initial message with all file contents
    file_summary = "\n\n".join(
        f"### {f['path']}\n```python\n{f['content'][:3000]}\n```"
        for f in files
    )

    messages = [
        {
            "role": "user",
            "content": f"""You are Sentinel, an expert code reviewer.

You have been given the following Python files from a GitHub repository.
Use the available tools to analyze each file — run pylint for issues and 
parse_structure to understand the code layout.

After analyzing, produce a structured markdown report with:
- An overall summary
- Per-file findings ranked by severity (high / medium / low)
- Specific line numbers where relevant
- Suggested fixes for each issue

Here are the files:

{file_summary}
"""
        }
    ]

    # Agentic loop — keeps going until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=TOOLS,
            messages=messages
        )

        # Claude is done — no more tool calls, just the final report
        if response.stop_reason == "end_turn":
            final_text = next(
                block.text for block in response.content
                if hasattr(block, "text")
            )
            return final_text

        # Claude wants to call tools — process each one
        if response.stop_reason == "tool_use":

            # Add Claude's response to message history
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process every tool call Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → Claude calling: {block.name}({block.input.get('filepath', '')})")
                    result = process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Send tool results back to Claude
            messages.append({
                "role": "user",
                "content": tool_results
            })