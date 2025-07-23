import streamlit as st
import openai
import os

# Load OpenAI API Key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="🩺 ICU/HDU Handover Assistant", layout="wide")
st.title("🩺 ICU/HDU Chat-Based Handover Assistant")

st.markdown("Type or speak your patient update. This tool will format it into a structured ICU/HDU handover.")

# Set up chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a clinical assistant helping nurses organise ICU and HDU handovers.

Structure the summary in this format:
1. Patient Details
2. Reason for Admission
3. Current Issues
4. ABCDE (Airway, Breathing, Circulation, Disability, Exposure)
5. Renal, Neurology, Allergies, Infections (MRSA, urine, sputum, swabs), Antibiotics
6. Observations
7. Plan
8. Escalation Status
9. Family Notes

Ask follow-up questions if anything is missing. Format clearly with headers and bullet points if needed."""}
    ]

# Show chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Voice upload
st.markdown("🎙️ Upload voice note (MP3 or WAV)")
audio_file = st.file_uploader("Upload your voice handover:", type=["mp3", "wav"])
if audio_file:
    st.audio(audio_file)
    with st.spinner("Transcribing..."):
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        voice_input = transcript["text"]
        st.success("Transcribed:")
        st.markdown(f"> {voice_input}")
        st.session_state.messages.append({"role": "user", "content": voice_input})

# Text input
if prompt := st.chat_input("Write your handover or continue chat..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
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

# Final handover generation
if st.button("📋 Generate Final Handover"):
    with st.spinner("Generating structured handover..."):
        full_context = st.session_state.messages + [
            {"role": "user", "content": "Please provide the full final ICU/HDU handover now using the proper format."}
        ]
        final = openai.ChatCompletion.create(
            model="gpt-4",
            messages=full_context,
            temperature=0.3
        )
        handover = final.choices[0].message.content
        st.session_state.final_handover = handover

        st.success("✅ Handover Ready")
        st.markdown("---")
        st.markdown(handover)

        # Copy to clipboard (works visually for now)
        st.markdown("📋 **Copy the handover below:**")
        st.code(handover)

        # Download button
        st.download_button("📥 Download Handover as .txt", handover, file_name="handover.txt")
