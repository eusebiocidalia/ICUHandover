import streamlit as st
import openai
import os

# Streamlit secret (via Streamlit Cloud > Settings > Secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="🩺 ICU/HDU Chat Handover Assistant", layout="wide")
st.title("🩺 ICU/HDU Chat-Based Handover Assistant")

st.markdown("Chat like you're giving a handover. The assistant will help structure and complete it for you.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a clinical handover assistant helping ICU and HDU nurses.

Your job is to:
1. Listen to free-form chat and extract a structured handover.
2. Use this format:
   - Patient Details: Name, ID, Bed, DOB
   - Reason for Admission
   - Current Issues
   - ABCDE (Airway, Breathing, Circulation, Disability, Exposure)
   - Renal
   - Neurology
   - Allergies
   - Infections (including MRSA/urine/sputum/swabs)
   - Antibiotics
   - Family Notes
   - Plan
   - Escalation Status
3. If any important sections are missing, ask the nurse whether they'd like to add them.
4. Keep the conversation helpful and brief, like a supportive clinical assistant.
"""}]

# Display previous messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Give your handover or respond to assistant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenAI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.messages,
                temperature=0.4
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Generate Final Output
if st.button("📋 Generate Structured Handover"):
    with st.spinner("Assembling final handover..."):
        full_context = st.session_state.messages + [
            {
                "role": "user",
                "content": "Please now provide the final structured ICU/HDU handover from all this conversation, using headers."
            }
        ]
        final = openai.ChatCompletion.create(
            model="gpt-4",
            messages=full_context,
            temperature=0.3
        )
        handover = final.choices[0].message.content
        st.success("Here is your structured handover:")
        st.markdown("---")
        st.markdown(handover)
        st.download_button("📥 Download Handover", handover, file_name="handover.txt")

