
import os
import uuid
import html
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
import textwrap

from main import run_pipeline
from core.rag_engine import ask_question


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="VidzAI | Video Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FIX: STREAMLIT HTML RENDERING
# ============================================================

_original_markdown = st.markdown

def markdown_fixed(body, *args, **kwargs):

    if kwargs.get("unsafe_allow_html", False) and isinstance(body, str):

        body = textwrap.dedent(body).strip()

        return st.html(body)

    return _original_markdown(body, *args, **kwargs)


st.markdown = markdown_fixed



DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# 2. SESSION STATE
# ============================================================

defaults = {
    "result": None,
    "chat_history": [],
    "video_source": None,
    "navigation": "Overview",
    "pending_question": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 3. CUSTOM CSS - DESIGN SYSTEM
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #F6F7FB;
    --white: #FFFFFF;
    --text: #000000;
    --muted: #777D8E;
    --border: #E9EAF0;
    --purple: #7257D9;
    --purple-dark: #5C43C1;
    --purple-light: #F0EDFF;
    --sidebar: #191A26;
    --green: #16966B;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 3rem 3rem 3rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: var(--sidebar);
    border-right: 1px solid #2C2D39;
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem;
}

section[data-testid="stSidebar"] * {
    color: #EDEDF3;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 7px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 9px;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: 0.2s;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #292A38;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #302B4A;
    border-color: #514477;
}

/* TYPOGRAPHY */

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.6px;
}

h1 {
    font-size: 31px !important;
    font-weight: 800 !important;
}

h2 {
    font-size: 23px !important;
    font-weight: 750 !important;
}

h3 {
    font-size: 17px !important;
    font-weight: 700 !important;
}

/* HERO */

.hero {
    background:
        radial-gradient(
            circle at 90% 10%,
            rgba(164, 145, 255, 0.35),
            transparent 32%
        ),
        linear-gradient(115deg, #292344, #443679, #6553A8);
    padding: 40px;
    border-radius: 18px;
    margin: 20px 0 30px;
    color: white;
}

.hero-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #D1C7FF;
    margin-bottom: 15px;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: 34px;
    font-weight: 800;
    line-height: 1.3;
    letter-spacing: -1px;
    color: white;
}

.hero-description {
    font-size: 14px;
    color: #DDD7F5;
    max-width: 650px;
    line-height: 1.8;
    margin-top: 13px;
}

.hero-chip {
    display: inline-block;
    margin-top: 22px;
    margin-right: 8px;
    padding: 7px 12px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: 7px;
    font-size: 11px;
    color: white;
}

/* SECTION HEADERS */

.kicker {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.6px;
    color: var(--purple);
    margin-bottom: 8px;
}

.muted {
    font-size: 13px;
    color: var(--muted);
    line-height: 1.7;
}

/* FEATURE CARDS */

.feature-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 20px;
    min-height: 145px;
    transition: 0.2s;
}

.feature-card:hover {
    border-color: #D0C6F6;
    transform: translateY(-2px);
}

.feature-icon {
    font-size: 23px;
    margin-bottom: 13px;
}

.feature-title {
    font-size: 14px;
    font-weight: 700;
    color: #242438;
}

.feature-description {
    font-size: 12px;
    color: var(--muted);
    margin-top: 7px;
    line-height: 1.6;
}

/* SURFACES */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 13px;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
    background: white !important;
    color: var(--text) !important;
    border: 1px solid #E2E3EB !important;
    border-radius: 9px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 2px rgba(114,87,217,0.1) !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: gray;
    border-radius: 9px;
}

/* BUTTONS */

.stButton > button {
    background: var(--purple);
    color: white;
    border: 1px solid var(--purple);
    border-radius: 9px;
    min-height: 43px;
    font-size: 13px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    background: var(--purple-dark);
    border-color: var(--purple-dark);
    color: white;
}

.stDownloadButton > button {
    background: white;
    color: var(--purple);
    border: 1px solid #DDD5F7;
    border-radius: 9px;
    font-weight: 600;
}

/* TABS */

.stTabs [data-baseweb="tab-list"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 5px;
    gap: 5px;
}

.stTabs [data-baseweb="tab"] {
    color: #74798A;
    font-size: 12px;
    font-weight: 600;
    border-radius: 7px;
}

.stTabs [aria-selected="true"] {
    background: var(--purple-light);
    color: var(--purple) !important;
}

/* CHAT */

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
}

/* UPLOADER */

[data-testid="stFileUploader"] {
    background: #FAFAFD;
    border: 1px dashed #D7D0ED;
    border-radius: 10px;
}

/* STATUS */

[data-testid="stStatusWidget"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 12px;
}

/* DIVIDER */

hr {
    border-color: var(--border);
}

/* MOBILE */

@media(max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 25px;
    }

    .hero-title {
        font-size: 25px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 4. REUSABLE FUNCTIONS
# ============================================================

def section_heading(kicker, title, description=None):

    st.markdown(
        f"""
        <div class="kicker">{kicker}</div>
        <h2>{title}</h2>
        """,
        unsafe_allow_html=True
    )

    if description:
        st.markdown(
            f'<div class="muted">{description}</div>',
            unsafe_allow_html=True
        )


def feature_card(icon, title, description):

    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def save_uploaded_file(uploaded_file):

    extension = Path(uploaded_file.name).suffix.lower()

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = DOWNLOAD_DIR / filename

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return str(file_path)


def reset_workspace():

    st.session_state.result = None
    st.session_state.chat_history = []
    st.session_state.video_source = None
    st.session_state.pending_question = None


def render_report(title, icon, content):

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
            margin-bottom:18px;
        ">
            <div style="
                width:40px;
                height:40px;
                background:#F0EDFF;
                border-radius:10px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:20px;
            ">{icon}</div>

            <div style="
                font-size:18px;
                font-weight:750;
                color:#252538;
            ">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if content:
        st.markdown(str(content))
    else:
        st.caption("No information available.")


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="padding:5px 5px 25px;">

        <div style="display:flex;align-items:center;gap:11px;">

            <div style="
                background:#7257D9;
                width:40px;
                height:40px;
                border-radius:11px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:21px;
            ">🎬</div>

            <div>
                <div style="
                    font-family:Manrope;
                    font-size:20px;
                    font-weight:800;
                    color:white;
                ">VidzAI</div>

                <div style="
                    font-size:9px;
                    letter-spacing:1.5px;
                    color:#A0A0AE;
                ">VIDEO INTELLIGENCE</div>
            </div>

        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:10px;color:#898A99;'
        'letter-spacing:1.5px;font-weight:700;margin-bottom:10px;">'
        'WORKSPACE</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        ["Overview", "Analysis Report", "AI Assistant"],
        key="navigation",
        label_visibility="collapsed"
    )

    st.divider()

    if st.session_state.result:

        st.markdown("""
        <div style="
            padding:12px;
            border-radius:9px;
            background:#292A39;
            border:1px solid #414157;
        ">
            <div style="color:#A998FF;font-size:11px;font-weight:700;">
                ● ANALYSIS READY
            </div>
            <div style="font-size:12px;color:#E4E4EC;margin-top:7px;">
                Your video knowledge base is active.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("＋ New Analysis", use_container_width=True):
            reset_workspace()
            st.session_state.navigation = "Overview"
            st.rerun()

    else:

        st.markdown(
            '<div style="font-size:12px;color:#9697A5;">'
            'No active analysis.</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="
        border-top:1px solid #343544;
        padding-top:18px;
        font-size:11px;
        color:#9C9DAB;
        line-height:2;
    ">
        <b style="color:white;">AI TECHNOLOGY</b><br>
        Generative AI<br>
        Speech Recognition<br>
        Retrieval Augmented Generation

        <br><br>
        <span style="color:#B9A8FF;">✦ Powered by VidzAI</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 6. OVERVIEW PAGE
# ============================================================

if page == "Overview":

    st.markdown(
        '<div class="kicker">YOUR AI WORKSPACE</div>',
        unsafe_allow_html=True
    )

    st.markdown("# Video Intelligence Studio")

    st.markdown(
        '<div class="muted">'
        'Transform videos into structured knowledge and actionable insights.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="hero">

        <div class="hero-label">
            ✦ INTELLIGENCE STARTS HERE
        </div>

        <div class="hero-title">
            Your videos have more to say.<br>
            Let AI uncover it.
        </div>

        <div class="hero-description">
            Transform YouTube videos and local recordings into
            intelligent summaries, decisions, action items and
            searchable knowledge.
        </div>

        <span class="hero-chip">TRANSCRIBE</span>
        <span class="hero-chip">ANALYZE</span>
        <span class="hero-chip">INTERACT</span>

    </div>
    """, unsafe_allow_html=True)

    section_heading(
        "01 / NEW ANALYSIS",
        "Start with your video",
        "Choose your source and configure your transcription preferences."
    )

    with st.container(border=True):

        st.markdown("### Video source")

        source_type = st.radio(
            "Input type",
            ["YouTube URL", "Local media file"],
            horizontal=True,
            label_visibility="collapsed"
        )

        source = None
        uploaded_file = None

        if source_type == "YouTube URL":

            source = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                label_visibility="collapsed"
            )

        else:

            uploaded_file = st.file_uploader(
                "Upload audio or video",
                type=["mp3", "wav", "mp4", "m4a", "webm", "ogg"]
            )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("##### Transcription language")

            language = st.selectbox(
                "Language",
                ["english", "hinglish"],
                format_func=str.title,
                label_visibility="collapsed"
            )

        with col2:

            st.markdown("##### Analysis mode")

            st.markdown("""
            <div style="
                background:#F7F6FC;
                border:1px solid #E8E2F8;
                padding:11px;
                border-radius:9px;
                font-size:12px;
                color:#6352A0;
            ">
                ✦ Full AI Analysis + RAG
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        analyze = st.button(
            "✦  Generate Intelligence Report",
            type="primary",
            use_container_width=True
        )

    if analyze:

        if source_type == "YouTube URL":

            if not source or not source.strip():

                st.warning("Please enter a YouTube URL.")
                st.stop()

            source = source.strip()

        else:

            if uploaded_file is None:

                st.warning("Please upload a media file.")
                st.stop()

            source = save_uploaded_file(uploaded_file)

        try:

            with st.status(
                "Generating your intelligence report...",
                expanded=True
            ) as status:

                st.write("01 · Extracting audio")
                st.write("02 · Transcribing video content")
                st.write("03 · Generating title and summary")
                st.write("04 · Extracting action items")
                st.write("05 · Identifying key decisions")
                st.write("06 · Extracting open questions")
                st.write("07 · Building RAG knowledge base")

                result = run_pipeline(source, language)

                st.session_state.result = result

                st.session_state.video_source = (
                    source if source_type == "YouTube URL"
                    else uploaded_file.name
                )

                st.session_state.chat_history = []

                status.update(
                    label="Your report is ready!",
                    state="complete",
                    expanded=False
                )

            st.success("Video analysis completed successfully!")
            st.session_state.navigation = "Analysis Report"
            st.rerun()

        except Exception as error:

            st.error(f"Analysis failed: {error}")

    st.write("")
    st.write("")

    section_heading(
        "02 / AI CAPABILITIES",
        "Everything important, in one place",
        "Your video is automatically transformed into meaningful information."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        feature_card(
            "📝",
            "Smart Summary",
            "Understand lengthy videos through structured AI summaries."
        )

    with c2:
        feature_card(
            "☑️",
            "Action Items",
            "Identify tasks and important follow-ups."
        )

    with c3:
        feature_card(
            "💡",
            "Key Decisions",
            "Discover important decisions discussed in the video."
        )

    with c4:
        feature_card(
            "❔",
            "Open Questions",
            "Identify unanswered questions and discussion points."
        )

    st.write("")
    st.write("")

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:

            st.markdown("### ✦ Explore your video with AI")

            st.markdown(
                '<div class="muted">'
                'Ask questions and retrieve information directly '
                'from your video through Retrieval Augmented Generation.'
                '</div>',
                unsafe_allow_html=True
            )

        with col2:

            if st.button("Open AI Assistant →", use_container_width=True):

                if st.session_state.result:
                    st.session_state.navigation = "AI Assistant"
                    st.rerun()
                else:
                    st.warning("Analyze a video first.")


# ============================================================
# 7. ANALYSIS REPORT PAGE
# ============================================================

elif page == "Analysis Report":

    result = st.session_state.result

    if result is None:

        st.write("")
        st.write("")

        with st.container(border=True):

            st.markdown("## No analysis available")

            st.markdown(
                "Your intelligence report will appear here "
                "after you analyze a video."
            )

            if st.button("Go to Overview"):
                st.session_state.navigation = "Overview"
                st.rerun()

    else:

        col1, col2 = st.columns([4, 1])

        with col1:

            st.markdown(
                '<div class="kicker">VIDEO INTELLIGENCE / REPORT</div>',
                unsafe_allow_html=True
            )

            st.markdown("# Analysis Report")

            st.markdown(
                '<div class="muted">'
                'Your video transformed into structured knowledge.'
                '</div>',
                unsafe_allow_html=True
            )

        with col2:

            st.write("")

            st.download_button(
                "↓ Download Transcript",
                data=result["transcript"],
                file_name="video_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.write("")

        with st.container(border=True):

            st.markdown(
                '<div class="kicker">GENERATED VIDEO TITLE</div>',
                unsafe_allow_html=True
            )

            st.markdown(f"## {html.escape(str(result['title']))}")

            st.markdown("""
            <span style="
                display:inline-block;
                background:#EAF8F2;
                color:#16966B;
                padding:6px 10px;
                border-radius:6px;
                font-size:10px;
                font-weight:700;
            ">
                ✓ ANALYSIS COMPLETE
            </span>
            """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        section_heading(
            "REPORT CONTENT",
            "Your extracted insights",
            "Explore each section of your generated intelligence report."
        )

        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Summary",
            "☑️ Action Items",
            "💡 Key Decisions",
            "❔ Open Questions"
        ])

        with tab1:

            with st.container(border=True):
                render_report("Executive Summary", "📝", result["summary"])

        with tab2:

            with st.container(border=True):
                render_report("Action Items", "☑️", result["action_items"])

        with tab3:

            with st.container(border=True):
                render_report("Key Decisions", "💡", result["key_decisions"])

        with tab4:

            with st.container(border=True):
                render_report("Open Questions", "❔", result["open_questions"])

        st.write("")
        st.write("")

        section_heading(
            "SOURCE MATERIAL",
            "Full video transcript",
            "Review the original transcribed content used for AI analysis."
        )

        with st.container(border=True):

            st.markdown("### 📄 Transcript")

            st.text_area(
                "Transcript",
                value=result["transcript"],
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )

            st.download_button(
                "↓ Download Full Transcript",
                data=result["transcript"],
                file_name="full_transcript.txt",
                mime="text/plain"
            )


# ============================================================
# 8. AI ASSISTANT PAGE
# ============================================================

elif page == "AI Assistant":

    st.markdown(
        '<div class="kicker">YOUR PERSONAL VIDEO ASSISTANT</div>',
        unsafe_allow_html=True
    )

    st.markdown("# Chat with your video")

    st.markdown(
        '<div class="muted">'
        'Ask questions, retrieve information and explore your video using AI.'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    result = st.session_state.result

    if result is None:

        with st.container(border=True):

            st.markdown("## 🧠 Your AI workspace is waiting")

            st.markdown(
                "Analyze a video to create a searchable knowledge base. "
                "Your AI assistant will become available once processing is complete."
            )

            if st.button("Start Video Analysis"):
                st.session_state.navigation = "Overview"
                st.rerun()

    else:

        # CONNECTED KNOWLEDGE BASE

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(
                    '<div class="kicker">CONNECTED KNOWLEDGE BASE</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"### {html.escape(str(result['title']))}"
                )

                st.caption(
                    f"Source: {st.session_state.video_source}"
                )

            with col2:

                st.markdown("""
                <div style="
                    margin-top:15px;
                    background:#EAF8F2;
                    color:#16966B;
                    text-align:center;
                    padding:10px;
                    border-radius:8px;
                    font-size:10px;
                    font-weight:700;
                ">
                    ● CONNECTED
                </div>
                """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        chat_col, side_col = st.columns([2.5, 1])

        # CHAT WORKSPACE

        with chat_col:

            st.markdown("### Conversation")

            st.caption("Your current conversation.")

            if st.button("＋ New Conversation", key="new_chat"):

                st.session_state.chat_history = []
                st.session_state.pending_question = None
                st.rerun()

            if not st.session_state.chat_history:

                with st.container(border=True):

                    st.markdown("""
                    <div style="
                        text-align:center;
                        padding:25px 10px;
                    ">
                        <div style="font-size:35px;">✦</div>

                        <div style="
                            font-family:Manrope;
                            font-size:19px;
                            font-weight:750;
                            color:#29283D;
                            margin-top:12px;
                        ">
                            Start exploring your video
                        </div>

                        <div style="
                            color:#777E8D;
                            font-size:13px;
                            margin-top:8px;
                        ">
                            Ask a question about anything discussed
                            in your video.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            for message in st.session_state.chat_history:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            question = st.chat_input(
                "Ask something about your video..."
            )

            if st.session_state.pending_question:

                question = st.session_state.pending_question
                st.session_state.pending_question = None

            if question and question.strip():

                question = question.strip()

                st.session_state.chat_history.append({
                    "role": "user",
                    "content": question
                })

                try:

                    with st.spinner("Searching your video knowledge..."):

                        answer = ask_question(
                            result["rag_chain"],
                            question
                        )

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": str(answer)
                    })

                except Exception as error:

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Unable to generate an answer: {error}"
                    })

                st.rerun()

        # ASSISTANT SIDEBAR

        with side_col:

            with st.container(border=True):

                st.markdown("### ✨ Suggested prompts")

                st.caption("Try asking these questions.")

                suggestions = [
                    "Summarize the main discussion.",
                    "What were the key decisions?",
                    "List all action items.",
                    "What questions remain unanswered?"
                ]

                for index, suggestion in enumerate(suggestions):

                    if st.button(
                        suggestion,
                        key=f"suggestion_{index}",
                        use_container_width=True
                    ):

                        st.session_state.pending_question = suggestion
                        st.rerun()

            st.write("")

            with st.container(border=True):

                st.markdown("### About this assistant")

                st.markdown("""
                <div style="
                    font-size:12px;
                    color:#777E8D;
                    line-height:1.9;
                ">
                    Your assistant uses Retrieval Augmented
                    Generation to retrieve relevant information
                    from your analyzed video.

                    <br><br>

                    <b style="color:#303043;">Knowledge source</b><br>
                    Video transcript

                    <br><br>

                    <b style="color:#303043;">Interaction</b><br>
                    Context-aware Q&A

                    <br><br>

                    <b style="color:#16966B;">
                    ● Knowledge base active
                    </b>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# 9. FOOTER
# ============================================================

st.markdown("""
<div style="
    border-top:1px solid #E9EAF0;
    margin-top:55px;
    padding-top:18px;
    display:flex;
    justify-content:space-between;
    color:#999EAB;
    font-size:11px;
">
    <span>VidzAI · Video Intelligence Workspace</span>
    <span>Powered by Generative AI & RAG</span>
</div>
""", unsafe_allow_html=True)
