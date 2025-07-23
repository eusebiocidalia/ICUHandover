import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---- System Prompt Template ----
system_prompt = """
You are a clinical assistant helping nurses summarise patient handovers for ICU or HDU settings.

Structure the handover as follows:
1. Patient Details
   - Name / ID / DOB
   - Location (e.g. ICU Bed)
   - Allergies
   - Diagnosis
   - Reason for Admission
   - Background / History

2. Current Issues

3. ABCDE Assessment
   - A – Airway
   - B – Breathing
   - C – Circulation
   - D – Disability
   - E – Exposure

4. Other Systems
   - Renal
   - Neurology
   - Infections (site, MRSA/urine/sputum/swab results)
   - Antibiotics (name, dose, duration)

5. Observations & Trends (e.g., GCS, NEWS2, vitals)

6. Plan of Care

7. Escalation Status (e.g., DNACPR)

8. Family / Communication Notes

Format clearly with section headers and bullet points when needed. Use clinical shorthand appropriately.
"""

# ---- Streamlit App ----
st.set_page_config(page_title="Nurse Handover Assistant", layout="wide")
st.title("🩺 ICU/HDU Nurse Handover Assistant")

st.markdown("""
Type in your free-text patient summary below (e.g., what you'd say during handover),
and this app will structure it into a professional format.
""")

# Dropdown for ward type
ward_type = st.selectbox("Ward Type", ["ICU", "HDU"])

# Free-text input
user_input = st.text_area("🗣️ Nurse Notes", height=300, placeholder="E.g., John Smith, ICU bed 3. Sepsis from pneumonia. On norad. Propofol sedation. GCS 10. MRSA neg. No family update today...")

if st.button("Generate Structured Handover"):
    if not user_input.strip():
        st.warning("Please enter some handover notes first.")
    else:
        with st.spinner("Generating handover..."):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
                handover_output = response['choices'][0]['message']['content']
                st.success("Structured handover generated:")
                st.markdown("----")
                st.markdown(handover_output)
                st.download_button("📥 Download as Text", handover_output, file_name="handover.txt")
            except Exception as e:
                st.error(f"Error generating handover: {str(e)}")
