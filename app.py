
from google import genai
from dotenv import load_dotenv
import os
import datetime
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()
db = firestore.client()
# =========================
# CONFIG
# =========================
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="centered"
)

# =========================
# FIREBASE INIT
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_interview(role, question, answer, feedback):
    doc = {
        "role": role,
        "question": question,
        "answer": answer,
        "feedback": feedback,
        "timestamp": datetime.datetime.now()
    }
    db.collection("interviews").add(doc)

# =========================
# CLEAN UI
# =========================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
        }

        .card {
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            background-color: #FAFAFA;
            margin-bottom: 12px;
        }

        .subtle {
            color: #6B7280;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================
st.title("🎯 AI Interview Coach")
st.markdown("<p class='subtle'>Practice interviews, get AI feedback, and improve your skills.</p>", unsafe_allow_html=True)

# =========================
# ROLE
# =========================
role = st.selectbox(
    "Select Role",
    ["Data Analyst", "Data Scientist", "Software Engineer", "Machine Learning Engineer"]
)

# =========================
# 1. QUESTION GENERATION
# =========================
st.divider()
st.subheader("📌 Interview Questions")

if st.button("Generate Questions"):
    with st.spinner("Generating..."):

        prompt = f"""
        Generate interview questions for a {role}.

        Include:
        - 5 Technical Questions
        - 3 HR Questions
        - 2 Scenario-based Questions
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        st.markdown(f"<div class='card'>{response.text}</div>", unsafe_allow_html=True)

# =========================
# 2. MOCK INTERVIEW MODE
# =========================
st.divider()
st.subheader("🧠 Mock Interview Mode")

if "mock_question" not in st.session_state:
    st.session_state.mock_question = ""

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🎯 Generate Question"):
        with st.spinner("Creating question..."):

            prompt = f"""
            Generate ONE tough interview question for a {role}.
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            st.session_state.mock_question = response.text

with col2:
    if st.button("🔄 Reset"):
        st.session_state.mock_question = ""

# Show question
if st.session_state.mock_question:
    st.markdown(
        f"""
        <div class="card">
            <b>Interview Question</b><br><br>
            {st.session_state.mock_question}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### ✍️ Your Answer")

    answer = st.text_area(
        "",
        placeholder="Write your structured answer here...",
        height=180,
        label_visibility="collapsed"
    )

    if st.button("🚀 Evaluate Answer"):
        if not answer:
            st.warning("Please write your answer first.")
        else:
            with st.spinner("Evaluating..."):

                eval_prompt = f"""
                You are an expert interview coach.

                Role: {role}

                Question:
                {st.session_state.mock_question}

                Answer:
                {answer}

                Provide:
                - Technical Score /10
                - Clarity Score /10
                - Depth Score /10
                - Strengths
                - Weaknesses
                - Improvements
                - Improved Answer
                """

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=eval_prompt
                )

                feedback = response.text

                st.markdown("### 📊 Feedback")
                st.markdown(f"<div class='card'>{feedback}</div>", unsafe_allow_html=True)

                # SAVE TO FIREBASE
                save_interview(
                    role,
                    st.session_state.mock_question,
                    answer,
                    feedback
                )

# =========================
# 3. ROADMAP
# =========================
st.divider()
st.subheader("🛤️ Learning Roadmap")

skill_goal = st.text_input("Target Role", placeholder="Data Scientist")

if st.button("Generate Roadmap"):
    if not skill_goal:
        st.warning("Enter a role first.")
    else:
        with st.spinner("Creating roadmap..."):

            roadmap_prompt = f"""
            Create a 3-month roadmap for becoming a {skill_goal}.
            Include skills, projects, and interview prep.
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=roadmap_prompt
            )

            st.markdown(f"<div class='card'>{response.text}</div>", unsafe_allow_html=True)