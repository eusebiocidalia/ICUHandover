import streamlit as st
import openai
import os
import base64
import smtplib
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="🩺 ICU/HDU Handover Assistant", layout="wide")
st.title("🩺 ICU/HDU Chat-Based Handover Assistant")

# Session state setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a clinical assistant helping nurses organise patient handovers.

Structure information clearly in this format:
1. Patient Details
2. Reason for Admission
3. Current Issues
4. ABCDE (Airway, Breathing, Circulation, Disability, Exposure)
5. Renal, Neurology, Allergies, Infections, Antibiotics
6. Plan, Escalation, Family

After chat, check what’s missing and ask follow-up questions if needed.
"""}
    ]

# Display chat
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Voice recorder
st.markdown("🎙️ Or record voice:")
audio_file = st.file_uploader("Upload voice file (MP3 or WAV)", type=["mp3", "wav"])
if audio_file:
    st.audio(audio_file)
    with st.spinner("Transcribing..."):
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        voice_input = transcript["text"]
        st.success("Transcribed:")
        st.markdown(f"> {voice_input}")
        st.session_state.messages.append({"role": "user", "content": voice_input})

# Text input
if prompt := st.chat_input("Type your handover message..."):
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

# Generate final handover
if st.button("📋 Generate Structured Handover"):
    with st.spinner("Compiling..."):
        context = st.session_state.messages + [
            {"role": "user", "content": "Please now provide the full structured ICU/HDU handover."}
        ]
        final = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context,
            temperature=0.3
        )
        handover = final.choices[0].message.content
        st.session_state.final_handover = handover

        st.success("✅ Final handover ready:")
        st.markdown("---")
        st.code(handover, language="markdown")

        st.download_button("📥 Download .txt", handover, file_name="handover.txt")

        st.markdown("📋 **Copy to clipboard**:")
        st.code(handover)

# Email function
def send_email(receiver_email, subject, body):
    msg = EmailMessage()
    msg["From"] = st.secrets["EMAIL_SENDER"]
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"])
        smtp.send_message(msg)

# Email option
if "final_handover" in st.session_state:
    st.markdown("📧 **Send by email**")
    email_input = st.text_input("Recipient email")
    if st.button("Send Email"):
        try:
            validate_email(email_input)
            send_email(email_input, "ICU/HDU Handover", st.session_state.final_handover)
            st.success("Email sent!")
        except EmailNotValidError as e:
            st.error(f"Invalid email: {e}")
        except Exception as e:
            st.error(f"Failed to send: {e}")

