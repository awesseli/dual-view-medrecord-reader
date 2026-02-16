from typing import Dict, List

def render_emt_view(record: Dict) -> Dict[str, List[str] | str]:
    dx = record.get("diagnoses", [])
    allergies = record.get("allergies", [])
    meds = record.get("medications", [])

    return {
        "title": "EMT View",
        "allergies": allergies if allergies else ["None listed"],
        "medications": meds if meds else ["None listed"],
        "problems": dx if dx else ["Not specified"],
        "return_precautions": record.get("return_precautions", ""),
    }
