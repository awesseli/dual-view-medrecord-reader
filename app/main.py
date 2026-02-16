import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))


import streamlit as st
from pypdf import PdfReader

from src.parse_fields import build_record_from_sections



from src.parse_sections import split_into_sections

st.set_page_config(page_title="Dual View Medical Record Reader")
st.title("Dual-View Medical Record Reader")

use_sample = st.checkbox("Use sample medical record text (for testing)")

sample_text = """Diagnosis: Chest pain (rule-out)
Allergies: Penicillin
Medications: Aspirin 81 mg daily

Discharge Instructions: Rest, avoid heavy exertion for 24 hours.
Follow-up: Family doctor in 2-3 days.
Return Precautions: Return immediately for worsening chest pain, shortness of breath, fainting, or sweating.
"""

examples_dir = Path(__file__).resolve().parents[1] / "data" / "examples"
example_files = sorted([p for p in examples_dir.glob("*.pdf")])

example_choice = st.selectbox(
    "Or choose a sample PDF from data/examples/",
    ["(none)"] + [p.name for p in example_files]
)


uploaded_file = st.file_uploader("Upload a PDF medical record", type=["pdf"])

# --- ALWAYS initialize these so they exist ---
text = ""
sections = {}
record = None

# --- Choose source of text ---
if use_sample:
    text = sample_text

elif example_choice != "(none)":
    example_path = examples_dir / example_choice
    reader = PdfReader(str(example_path))
    extracted_pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)
    text = "\n".join(extracted_pages)

elif uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    extracted_pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)
    text = "\n".join(extracted_pages)


# --- Show raw text (optional but helpful) ---
if text.strip():
    st.subheader("Extracted Text (Raw)")
    st.text_area("PDF/Text Content", text, height=250)

    # --- Create sections ONLY if we have text ---
    sections = split_into_sections(text)

    record = build_record_from_sections(sections)

    st.subheader("Structured Record (JSON)")
    st.json(record)

from src.render_patient import render_patient_view
from src.render_emt import render_emt_view

# --- Display sections safely ---

if record is not None:
    patient_view = render_patient_view(record)
    emt_view = render_emt_view(record)

    tab_patient, tab_emt, tab_json, tab_raw = st.tabs(["Patient", "EMT", "JSON", "Raw Text"])


    with tab_patient:
        st.header(patient_view["title"])
        for line in patient_view["summary"]:
            st.write("• " + line)

        st.subheader("Medications")
        if patient_view["medications"]:
            for m in patient_view["medications"]:
                st.write("• " + m)
        else:
            st.write("None listed.")

        st.subheader("Discharge Instructions")
        st.write(patient_view["discharge_instructions"] or "Not available.")

        st.subheader("Follow-up")
        st.write(patient_view["follow_up"] or "Not available.")

        st.subheader("When to seek help")
        st.write(patient_view["return_precautions"] or "Not available.")

    with tab_emt:
        st.header(emt_view["title"])

        st.subheader("Allergies")
        for a in emt_view["allergies"]:
            st.write("• " + a)

        st.subheader("Medications")
        for m in emt_view["medications"]:
            st.write("• " + m)

        st.subheader("Problems / Diagnoses")
        for d in emt_view["problems"]:
            st.write("• " + d)

        st.subheader("Return Precautions (from record)")
        st.write(emt_view["return_precautions"] or "Not available.")

    with tab_json:
        st.json(record)

    with tab_raw:
        
        st.text_area("Raw extracted text", text, height=350)
else:
    st.info("Upload a PDF or toggle the sample text to generate views.")

