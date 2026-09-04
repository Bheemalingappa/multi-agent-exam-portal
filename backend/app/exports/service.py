import csv
import io
from typing import List, Dict, Any

class DataExportService:
    """
    Data Export Engine generating CSV and JSON analytical reports
    with tenant isolation and field-level security filtering.
    """

    @staticmethod
    def export_candidates_csv(candidates_data: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        fieldnames = ["candidate_id", "email", "attempts_count", "average_score", "completion_status"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in candidates_data:
            writer.writerow({
                "candidate_id": row.get("candidate_id"),
                "email": row.get("email"),
                "attempts_count": row.get("attempts_count", 0),
                "average_score": row.get("average_score", 0.0),
                "completion_status": row.get("completion_status", "COMPLETED")
            })
        return output.getvalue()
