from backend.app.ingestion.chunker import chunk_file

def test_chunker_has_line_ranges():
    chunks = chunk_file("a.py", "\n".join(str(i) for i in range(1, 181)), chunk_lines=80, overlap=15)
    assert chunks
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 80
    assert chunks[-1].end_line == 180
