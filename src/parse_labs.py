import re
from typing import List, Dict, Optional

LAB_LINE = re.compile(
    r"""^\s*
    (?P<test>[A-Za-z][A-Za-z0-9\s\-\(\)\/]+?)      # test name
    \s+
    (?P<value>-?\d+(?:\.\d+)?)                    # numeric value
    \s*
    (?P<unit>[A-Za-zµ/%0-9\^\.\-]+)?              # optional unit
    \s*
    (?:\((?P<ref>[^)]+)\))?                       # optional (ref range)
    \s*
    (?P<flag>[HL])?                               # optional H/L flag
    \s*$
    """,
    re.VERBOSE
)

def parse_labs_section(labs_text: str) -> List[Dict]:
    """
    Parse simple lab lines like:
    WBC 13.2 x10^9/L (4.0 - 11.0) H
    Creatinine 112 umol/L (60 - 110) H
    """
    if not labs_text:
        return []

    labs = []
    for line in labs_text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = LAB_LINE.match(line)
        if not m:
            continue

        labs.append({
            "datetime": None,
            "test": m.group("test").strip(),
            "value": float(m.group("value")),
            "unit": (m.group("unit") or "").strip() or None,
            "ref_range": (m.group("ref") or "").strip() or None,
            "flag": (m.group("flag") or "").strip() or None,
            "raw": line,
        })

    return labs
