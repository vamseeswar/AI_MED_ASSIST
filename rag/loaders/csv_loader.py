import csv
from typing import List, Dict, Any
from backend.app.core.logging import app_logger


def extract_csv(file_path: str) -> List[Dict[str, Any]]:
    """Extracts CSV data into structured tabular representations and record summaries."""
    sections_data = []

    rows = []
    headers = []

    for encoding in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            with open(file_path, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                all_rows = list(reader)
                if all_rows:
                    headers = all_rows[0]
                    rows = all_rows[1:]
                break
        except Exception:
            continue

    if not headers and not rows:
        raise ValueError("CSV file is empty or unreadable.")

    # Header overview
    header_summary = f"Columns ({len(headers)}): {', '.join(headers)}"

    # Group rows into batches of 15 rows per logical page
    batch_size = 15
    for i in range(0, max(len(rows), 1), batch_size):
        page_num = (i // batch_size) + 1
        batch_rows = rows[i:i + batch_size]

        formatted_rows = []
        for r in batch_rows:
            row_items = [f"{headers[idx] if idx < len(headers) else f'Col{idx}'}: {val.strip()}" for idx, val in enumerate(r)]
            formatted_rows.append("; ".join(row_items))

        content_block = (
            f"CSV Document Overview: {header_summary}\n\n"
            f"Records {i + 1} to {min(i + len(batch_rows), len(rows))}:\n"
            + "\n".join(formatted_rows)
        )

        sections_data.append({
            "page_number": page_num,
            "section_heading": f"Data Records {i + 1}-{min(i + len(batch_rows), len(rows))}",
            "content": content_block,
            "metadata": {
                "source_type": "csv",
                "columns": headers,
                "row_count": len(rows),
                "page_number": page_num
            }
        })

    return sections_data
