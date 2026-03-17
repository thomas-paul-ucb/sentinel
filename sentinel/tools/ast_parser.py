import ast


def parse_structure(filepath: str, content: str) -> dict:
    """
    Uses Python's AST module to extract functions and classes
    from source code without executing it.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"file": filepath, "error": str(e), "functions": [], "classes": []}

    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "length": node.end_lineno - node.lineno + 1,
                "args": [arg.arg for arg in node.args.args]
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "length": node.end_lineno - node.lineno + 1,
            })

    return {
        "file": filepath,
        "functions": functions,
        "classes": classes
    }