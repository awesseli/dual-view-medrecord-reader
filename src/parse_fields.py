from typing import List, Dict

from src.parse_labs import parse_labs_section


def _split_list(text: str) -> List[str]:
    """
    Split comma/newline separated lists into clean items.
    Example: "Penicillin, Latex\nPeanuts" -> ["Penicillin", "Latex", "Peanuts"]
    """
    if not text:
        return []
    raw = text.replace("\n", ",")
    items = [x.strip(" -\t\r") for x in raw.split(",")]
    return [x for x in items if x]

def build_record_from_sections(sections: Dict[str, str]) -> Dict:
    """
    Convert parsed sections into a minimal structured record dict.
    We'll keep it simple first (strings/lists) and refine later.
    """
    diagnosis_text = sections.get("diagnosis") or sections.get("diagnoses") or ""
    allergies_text = sections.get("allergies") or ""
    meds_text = sections.get("medications") or ""
    labs_text= sections.get("labs","") or ""
    labs = parse_labs_section(labs_text)

    record = {
        "patient": {
            "name": None,
            "age": None,
            "sex": None,
        },
        "encounter": {
            "date": None,
            "facility": None,
            "visit_type": "ED Discharge",
        },
        "diagnoses": _split_list(diagnosis_text),
        "allergies": _split_list(allergies_text),
        # For MVP, store meds as simple strings. We can structure later.
        "medications": _split_list(meds_text),
        "vitals": [],
        "labs": labs,
        "imaging": [],
        "discharge_instructions": sections.get("discharge instructions", "") or "",
        "follow_up": sections.get("follow-up", "") or sections.get("follow up", "") or "",
        "return_precautions": sections.get("return precautions", "") or "",
        "source_evidence": None,
    }

    return record
