import ast
import operator
import re
import platform
import sys
from pathlib import Path


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def calculate(expression: str):
    """
    Safely evaluate a mathematical expression.
    """

    expression = expression.strip()
    expression = expression.rstrip(".")
    expression = expression.replace(",", "")

    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Invalid mathematical expression.")

    try:
        tree = ast.parse(expression, mode="eval")
        return _evaluate(tree.body)

    except Exception:
        raise ValueError("Invalid mathematical expression.")


def _evaluate(node):

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.BinOp):

        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Operator not allowed.")

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):

        operation = OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Operator not allowed.")

        operand = _evaluate(node.operand)

        return operation(operand)

    raise ValueError("Expression contains an unsupported operation.")


def get_system_info() -> dict:
    """
    Return basic read-only information about the machine
    running JARVIS.
    """

    return {
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
    }


def list_files(directory: str = ".") -> list:
    """
    List files and folders in a directory.
    Read-only operation.
    """

    path = Path(directory).resolve()

    if not path.exists():
        raise ValueError("Directory does not exist.")

    if not path.is_dir():
        raise ValueError("Path is not a directory.")

    return [
        item.name
        for item in path.iterdir()
    ]


def read_file(file_path: str) -> str:
    """
    Read a text file.
    Read-only operation.
    """

    path = Path(file_path).resolve()

    if not path.exists():
        raise ValueError("File does not exist.")

    if not path.is_file():
        raise ValueError("Path is not a file.")

    # Only allow common text/code files for now
    allowed_extensions = {
        ".txt",
        ".md",
        ".py",
        ".json",
        ".csv",
        ".html",
        ".css",
        ".js",
        ".xml",
        ".yaml",
        ".yml",
    }

    if path.suffix.lower() not in allowed_extensions:
        raise ValueError("This file type is not supported yet.")

    try:
        return path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        raise ValueError("This file is not a readable UTF-8 text file.")


def find_files(directory: str, filename: str) -> list:
    """
    Search for files by name.
    Read-only operation.
    """

    path = Path(directory).resolve()

    if not path.exists():
        raise ValueError("Directory does not exist.")

    results = []

    for item in path.rglob("*"):

        if item.is_file() and item.name.lower() == filename.lower():
            results.append(str(item))

    return results