import re
from typing import List, Dict, Any

class SemanticCodeChunker:
    """
    Splits source code files into semantic chunks along function and class boundaries
    for vector embedding and RAG reviewer context construction.
    """

    @staticmethod
    def chunk_code(source_code: str, language: str = "python") -> List[Dict[str, Any]]:
        chunks = []
        lines = source_code.split("\n")
        current_chunk = []
        chunk_type = "module"
        chunk_id = 0

        for line in lines:
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                if current_chunk:
                    content = "\n".join(current_chunk).strip()
                    if content:
                        chunks.append({
                            "chunk_id": chunk_id,
                            "type": chunk_type,
                            "content": content,
                            "line_count": len(current_chunk)
                        })
                        chunk_id += 1
                    current_chunk = []
                chunk_type = "function" if line.strip().startswith("def ") else "class"
            current_chunk.append(line)

        if current_chunk:
            content = "\n".join(current_chunk).strip()
            if content:
                chunks.append({
                    "chunk_id": chunk_id,
                    "type": chunk_type,
                    "content": content,
                    "line_count": len(current_chunk)
                })

        return chunks
