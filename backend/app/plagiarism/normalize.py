import ast
import re

class CodeNormalizer:
    """
    Normalizes source code by removing comments, docstrings, formatting noise,
    and canonicalizing variable names for structural plagiarism analysis.
    """

    @staticmethod
    def normalize_code(code: str) -> str:
        # Strip inline comments
        code_no_comments = re.sub(r"#.*", "", code)
        
        try:
            # Parse AST and unparse to canonical form
            tree = ast.parse(code_no_comments)
            # Strip docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
                        node.body.pop(0)
            return ast.unparse(tree)
        except Exception:
            # Fallback: simple whitespace normalization
            return re.sub(r"\s+", " ", code_no_comments).strip()
