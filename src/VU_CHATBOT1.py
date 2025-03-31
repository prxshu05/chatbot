import streamlit as st
import google.generativeai as genai
import os
import gtts
import speech_recognition as sr
from io import BytesIO
from gtts.lang import tts_langs  
from pymongo import MongoClient
from datetime import datetime
import time 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googletrans import Translator

# Configure Gemini API Key
GOOGLE_API_KEY = "AIzaSyCMlS4_Ux6noZxiIQttGF2bj3h3FltS5_c"  # Replace with your API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["VUCHAT"]
collection = db["Chat history"]

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"  # SMTP server for Gmail
SMTP_PORT = 587  # Port for TLS
SENDER_EMAIL = "sunilsheshagiri60@gmail.com"  # Your email
SENDER_PASSWORD = "ywqg ldqn xtmc bukm"  # Use App Password, NOT your main password
ADMIN_EMAIL = "2023suneel@vidyashilp.edu.in"  # Admin email

# Load university data
def load_data(file_path):
    if not os.path.exists(file_path):
        return "No information available right now."
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Generate chatbot response
def get_response(query, content, lang="en"):
    if query.strip() == "":
        return "Please provide a specific question."
    
    try:
        prompt = (
            f"You are an AI assistant for Vidyashilp University. Answer briefly and accurately "
            f"in {lang} language:\n\n"
            f"Question: {query}\n\nContext:\n{content}\n\nAnswer in {lang}:"
        )
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Store in MongoDB
        now = datetime.now()
        chat_entry = {
            "question": query,
            "response": response_text,
            "language": lang,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M %p")
        }
        collection.insert_one(chat_entry)
        return response_text  
    except Exception as e:
        print(f"Error: {e}")
        return "The chatbot is currently experiencing high demand. Please try again later."

# Convert text to speech
def text_to_speech(text, lang="en"):
    supported_languages = tts_langs()
    if lang not in supported_languages:
        lang = "en"
        st.warning("⚠️ Selected language is not supported for text-to-speech. Defaulting to English.")
    
    try:
        tts = gtts.gTTS(text, lang=lang)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        return audio_bytes.getvalue()
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# Speech-to-text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.write("❌ Could not understand. Please try again.")
        except sr.RequestError:
            st.write("❌ Error connecting to speech recognition service.")
    return ""

def send_email(subject, message, recipient_email):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        return True, "✅ Thank you! Our team will contact you shortly.."
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        return False, str(e)
def send_email_to_admin(email, phone, topic):
    subject = f"New Inquiry for {topic}"
    message = f"New {topic} inquiry received.\n\nEmail: {email}\nPhone: {phone}"
    success, response = send_email(subject, message, ADMIN_EMAIL)
    return response if success else f"Failed to notify admin: {response}"

# Load university data
file_path1 = "untitled document.txt"
file_path2 = "News.txt"

content = load_data(file_path1) + "\n\n" + load_data(file_path2)


# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "response_language" not in st.session_state:
    st.session_state.response_language = "en"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "waiting_for_contact" not in st.session_state:
    st.session_state.waiting_for_contact = False




st.set_page_config(page_title="Vidyashilp University Chatbot", layout="wide")

# 🎨 Dark Black Theme & Custom Animations
st.markdown("""
    <style>
        /* Background & Text */
        .stApp {
            background-color: black;
            color: white;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            background: linear-gradient(90deg, #ffcc00, #ff6600);
            color: black;
            transition: 0.3s;
            font-weight: bold;
            font-size: 16px;
            border: 2px solid #ffcc00;
        }
        .stButton > button:hover {
            background: #ffffff;
            color: black;
            transform: scale(1.05);
            box-shadow: 0px 0px 15px #ffcc00;
        }

        /* Chat Box Styling */
        .chat-box {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            color: white;
            box-shadow: 0px 0px 8px rgba(255, 255, 255, 0.2);
        }

        /* Sidebar */
        .stSidebar {
            background: #121212;
            color: white;
        }

        /* Images */
        .stImage {
            border-radius: 10px;
            box-shadow: 5px 5px 20px rgba(255,255,255,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# 🏫 **Header and Logo**
col1, col2 = st.columns([4, 1])  
with col1:
    st.title("🎓 Vidyashilp University Chatbot 🤖")  
with col2:
   st.image("image.png", use_container_width=True)

# 🌄 **Main Banner**
st.image("https://vidyashilp.edu.in/wp-content/uploads/2024/09/Website-1.jpg", use_container_width=True)
st.write("Hey! How may I assist you today? 😊")

# 📜 **Chat History Sidebar**
st.sidebar.header("📜 Chat History")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if st.session_state.chat_history:
    with st.sidebar.expander("View Previous Chats", expanded=True):
        for q, r in reversed(st.session_state.chat_history[-10:]):  
            st.write(f"**🧑 You:** {q}")
            st.write(f"**🤖 Chatbot:** {r}")
            st.write("---")
else:
    st.sidebar.write("No chat history yet.")

# 🌐 **Language Selection**
st.sidebar.subheader("🌍 Select Language")
language_options = {
    "English": "en", "Hindi": "hi", "Konkani": "kn", "Kannada": "kn", "Dogri": "doi",
    "Bodo": "brx", "Urdu": "ur", "Tamil": "ta", "Kashmiri": "ks",
    "Assamese": "as", "Bengali": "bn", "Marathi": "mr", "Sindhi": "sd",
    "Maithili": "mai", "Punjabi": "pa", "Malayalam": "ml", "Manipuri": "mni",
    "Telugu": "te", "Sanskrit": "sa", "Nepali": "ne", "Santali": "sat",
    "Gujarati": "gu", "Odia": "or"
}

st.sidebar.markdown('<p style="color: white; font-size: 16px;"><b>Choose response language:</b></p>', unsafe_allow_html=True)
selected_lang = st.sidebar.selectbox("", list(language_options.keys()))
st.session_state.response_language = language_options[selected_lang]

# 💡 **Quick Topics with Animated Buttons**

st.subheader("💡 Quick Topics")
topics = ["Admissions", "Courses", "Faculty", "Events", "Fees", "Scholarships", "FAQ", "News"]
cols = st.columns(3)

for i, topic in enumerate(topics):
    if cols[i % 3].button(f"📌 {topic}"):
        st.session_state.selected_topic = topic
        st.session_state.show_contact_form = topic == "Admissions"  # Show only for Admissions
        st.session_state.email = ""  # Reset fields when switching topics
        st.session_state.phone = ""

# 💬 **Chat Interface**
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "response_language" not in st.session_state:
    st.session_state.response_language = "en"
if "show_contact_form" not in st.session_state:
    st.session_state.show_contact_form = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "email" not in st.session_state:
    st.session_state.email = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""

if st.session_state.selected_topic:

    # Contact Form for Admissions (Only disappears after both fields are filled and submitted)
    if st.session_state.show_contact_form:
        st.write("📩 Please enter your details for Admissions inquiries.")
        st.session_state.email = st.text_input("Email Address", value=st.session_state.email, key="email_input")
        st.session_state.phone = st.text_input("Phone Number", value=st.session_state.phone)

        if st.button("Submit"):
            if st.session_state.email and st.session_state.phone:
                admin_message = send_email_to_admin(st.session_state.email, st.session_state.phone, "Admissions")
                st.success(admin_message)
                st.session_state.show_contact_form = False  # Hide form only after valid submission
            else:
                st.error("Please provide both email and phone number before submitting.")

    # ⏳ **Loading Animation**
    with st.spinner(f"Fetching information on {st.session_state.selected_topic}..."):
        time.sleep(3)  # Simulating processing time
        topic_query = f"Tell me about {st.session_state.selected_topic} at Vidyashilp University."
        topic_response = get_response(topic_query, content, st.session_state.response_language)
        st.session_state.chat_history.append((topic_query, topic_response))
        st.write(topic_response)

        audio_data = text_to_speech(topic_response, st.session_state.response_language)
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
        else:
            st.write("⚠ Unable to generate audio.") 
    st.session_state.selected_topic = None  

# 🎤 **Voice Input with Button Animation**
st.subheader("🎤 Speak Instead of Typing")

if st.button("🎙 Start Voice Input"):
    user_query = speech_to_text()  # Ensure speech_to_text() is implemented
    if user_query:
        response = get_response(user_query, content, st.session_state.response_language)
        st.session_state.chat_history.append((user_query, response))
        st.write(f"**Chatbot:** {response}")

        # Convert to speech and play
        audio_data = text_to_speech(response, st.session_state.response_language)
        if audio_data:
            st.audio(audio_data, format="audio/mp3")


st.markdown('<p style="color: white; font-size: 18px;"><b>Ask a question:</b></p>', unsafe_allow_html=True)
user_query = st.text_input("")
if "show_contact_form" not in st.session_state:
    st.session_state.show_contact_form = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "response_language" not in st.session_state:
    st.session_state.response_language = "en"
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

# 🚀 **Submit User Query**
if st.button("🚀 Submit"):
    if user_query:
        if "admissions" in user_query.lower():  # Auto-trigger contact form for admissions
            st.session_state.show_contact_form = True
            st.session_state.pending_query = user_query  # Store query to answer later
        else:
            with st.spinner("Thinking... 🤔"):
                try:
                    response = get_response(user_query, content, st.session_state.response_language)
                    
                    if not response or "I don't know" in response:  # If chatbot can't answer
                        admin_message = send_email_to_admin(None, None, f"User Query: {user_query}")
                        st.warning("⚠️ The chatbot couldn't answer your question. It has been sent to the admin for review.")
                        st.success(admin_message)
                    else:
                        st.session_state.chat_history.append((user_query, response))
                        st.write(f"**🤖 Chatbot:** {response}")

                        # 🎙 Convert response to speech
                        audio_data = text_to_speech(response, st.session_state.response_language)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3")
                        else:
                            st.warning("⚠️ Could not generate audio version")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a question")

# 📩 **Show Contact Form for Admissions & Auto-Hide After Submission**
if st.session_state.show_contact_form:
    st.write("📩 Please enter your details for Admissions inquiries.")
   

    if st.button("Submit Details"):
        if st.session_state.email and st.session_state.phone:
            admin_message = send_email_to_admin(st.session_state.email, st.session_state.phone, "Admissions")
            st.success(admin_message)
            st.session_state.show_contact_form = False  # Hide form after valid submission
            
            # Answer stored query after form submission
            if st.session_state.pending_query:
                with st.spinner("Fetching response... 🤔"):
                    try:
                        response = get_response(st.session_state.pending_query, content, st.session_state.response_language)
                        
                        if not response or "I don't know" in response:  # If chatbot can't answer
                            admin_message = send_email_to_admin(st.session_state.email, st.session_state.phone, f"User Query: {st.session_state.pending_query}")
                            st.warning("⚠️ The chatbot couldn't answer your question. It has been sent to the admin for review.")
                            st.success(admin_message)
                        else:
                            st.session_state.chat_history.append((st.session_state.pending_query, response))
                            st.write(f"**🤖 Chatbot:** {response}")

                            # 🎙 Convert response to speech
                            audio_data = text_to_speech(response, st.session_state.response_language)
                            if audio_data:
                                st.audio(audio_data, format="audio/mp3")
                            else:
                                st.warning("⚠️ Could not generate audio version")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

                st.session_state.pending_query = ""  # Clear pending query after answering
        else:
            st.error("⚠️ Please provide both email and phone number before submitting.")