import re

HEADER_ALIASES = {
    "diagnosis": [
        "diagnosis", "diagnoses", "discharge diagnosis", "discharge diagnoses",
        "discharge dx", "dx", "impression", "primary diagnosis", "final diagnosis"
    ],
    "allergies": [
        "allergies", "allergy", "allergy list", "allergies list", "allergies:", "allergy information",
        "nkda"  # special-case: often appears as content, but can appear as header-like
    ],
    "medications": [
        "medications", "meds", "med list", "medication list", "current medications",
        "discharge medications", "rx", "prescriptions"
    ],
    "discharge instructions": [
        "discharge instructions", "instructions", "plan", "instructions / plan", "home care", "care instructions"
    ],
    "follow-up": [
        "follow-up", "follow up", "followup", "follow-up instructions", "follow up instructions", "follow up plan"
    ],
    "return precautions": [
        "return precautions", "return to ed if", "return to er if", "return if", "seek care if", "when to return",
        "return to emergency if", "go to ed if"
    ],
    "vitals": ["vitals", "vital signs"],
    "labs": ["labs", "laboratory", "lab results", "bloodwork", "blood work"],
    "imaging": ["imaging", "radiology", "ct", "x-ray", "xray", "ultrasound", "cxr"],
}

def split_into_sections(text: str) -> dict:
    """
    Robust section splitter:
    - Supports many header aliases
    - Supports "HEADER:" and "HEADER" (line-based)
    - Returns canonical section keys
    """
    if not text:
        return {}

    # Build regex that matches any header alias at start of a line
    alias_to_canonical = {}
    all_aliases = []
    for canonical, aliases in HEADER_ALIASES.items():
        for a in aliases:
            a_clean = a.strip().lower()
            alias_to_canonical[a_clean] = canonical
            all_aliases.append(re.escape(a_clean))

    # Match headers at the start of a line, optionally followed by ":".
    # Example matches:
    # "DISCHARGE DIAGNOSES:" or "FOLLOW UP:" or "RETURN TO ED IF:"
    pattern = re.compile(
        r"(?im)^(?P<header>" + "|".join(sorted(all_aliases, key=len, reverse=True)) + r")\s*:?\s*$"
        r"|^(?P<header2>" + "|".join(sorted(all_aliases, key=len, reverse=True)) + r")\s*:\s*",
        re.MULTILINE
    )

    matches = list(pattern.finditer(text))
    if not matches:
        return {}

    sections = {}

    def canonicalize(raw: str) -> str:
        return alias_to_canonical.get(raw.strip().lower(), raw.strip().lower())

    for i, m in enumerate(matches):
        header_raw = (m.group("header") or m.group("header2") or "").strip().lower()
        canonical = canonicalize(header_raw)

        # Content starts at end of this match
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        # Merge if same canonical appears twice
        if canonical in sections and content:
            sections[canonical] = (sections[canonical] + "\n" + content).strip()
        else:
            sections[canonical] = content

    # Special-case: if NKDA appears anywhere and allergies empty, set allergies to NKDA
    if ("allergies" not in sections or not sections["allergies"].strip()) and re.search(r"\bNKDA\b", text, re.I):
        sections["allergies"] = "NKDA"

    return sections
