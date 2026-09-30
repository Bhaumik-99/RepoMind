from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    path: str
    content: str
    start_line: int
    end_line: int

def chunk_file(path: str, content: str, chunk_lines: int = 80, overlap: int = 15) -> list[Chunk]:
    lines = content.splitlines()
    if not lines:
        return []
    result: list[Chunk] = []
    step = max(1, chunk_lines - overlap)
    for start in range(0, len(lines), step):
        end = min(len(lines), start + chunk_lines)
        body = "\n".join(lines[start:end]).strip()
        if body:
            result.append(
                Chunk(
                    f"{path}:{start + 1}-{end}",
                    path,
                    body,
                    start + 1,
                    end,
                )
            )
        if end >= len(lines):
            break
    return result
