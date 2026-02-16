from typing import Dict, List

def render_patient_view(record: Dict) -> Dict[str, List[str] | str]:
    dx = record.get("diagnoses", [])
    allergies = record.get("allergies", [])
    meds = record.get("medications", [])

    summary_lines = []
    if dx:
        summary_lines.append(f"You were seen in the emergency department for: {', '.join(dx)}.")
    else:
        summary_lines.append("You were seen in the emergency department.")

    if allergies:
        summary_lines.append(f"Allergies on file: {', '.join(allergies)}.")

    return {
        "title": "Patient View",
        "summary": summary_lines,
        "medications": meds,
        "discharge_instructions": record.get("discharge_instructions", ""),
        "follow_up": record.get("follow_up", ""),
        "return_precautions": record.get("return_precautions", ""),
    }
