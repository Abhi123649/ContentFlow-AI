import streamlit as st
from dotenv import load_dotenv
import os
import whisper
from crewai import Agent, Task, Crew, LLM

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="ContentFlow AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #f7f8fc;
    }

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Logo */
    .brand {
        font-size: 25px;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }

    .brand-subtitle {
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 30px;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 32px;
        border-radius: 20px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    .hero h1 {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #d1d5db;
        font-size: 16px;
        margin-bottom: 0;
    }

    /* Cards */
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }

    .metric-title {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .5px;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
        margin-top: 5px;
    }

    /* Section heading */
    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: #111827;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* Status */
    .status {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: #ecfdf5;
        color: #047857;
    }

    /* Transcript box */
    textarea {
        border-radius: 12px !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 45px;
    }

    /* Generated post */
    .post-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.04);
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "generated_post" not in st.session_state:
    st.session_state.generated_post = None

if "approved" not in st.session_state:
    st.session_state.approved = False

if "rejected" not in st.session_state:
    st.session_state.rejected = False

if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

if "changes_count" not in st.session_state:
    st.session_state.changes_count = 0

if "content_input" not in st.session_state:
    st.session_state.content_input = ""

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "generated_count" not in st.session_state:
    st.session_state.generated_count = 0

if "generate_from_voice" not in st.session_state:
    st.session_state.generate_from_voice = False

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown('<div class="brand">✦ ContentFlow AI</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="brand-subtitle">AI-powered content workspace</div>',
        unsafe_allow_html=True
    )

    st.markdown("### Workspace")

    st.markdown("📝  Content Generator")
    st.markdown("🎙️  Voice & Transcript")
    st.markdown("📋  Approval Queue")
    st.markdown("📊  Analytics")

    st.divider()

    st.markdown("### AI Engine")

    st.markdown(
        '<span class="status">● AI Engine Online</span>',
        unsafe_allow_html=True
    )

    st.write("")

    st.caption("CrewAI + OpenRouter")
    st.caption("ContentFlow AI • POC v1.0")

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

st.markdown(
    """
<div class="hero">
<h1>AI Content Studio</h1>
<p>Transform your ideas and transcripts into professional, ready-to-publish LinkedIn content.</p>
</div>
""",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">AI Engine</div>
        <div class="metric-value">Online</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Posts Generated</div>
        <div class="metric-value">{st.session_state.generation_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    status = "Approved" if st.session_state.approved else "Pending"

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Current Status</div>
        <div class="metric-value">{status}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Platform</div>
        <div class="metric-value">LinkedIn</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN WORKSPACE
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">🎙️ Content Input</div>',
    unsafe_allow_html=True
)
# ---------------------------------------------------------
# WHISPER AUDIO TRANSCRIPTION
# ---------------------------------------------------------

st.markdown("### 🎤 Audio to Transcript")

audio_file = st.file_uploader(
    "Upload your recorded audio",
    type=["wav", "mp3", "m4a" ],
)
if audio_file is not None:

    st.audio(audio_file)

    if st.button("🧠 Transcribe with Whisper"):

        with st.spinner("Whisper is converting your audio into text..."):

            try:
                os.makedirs("recordings", exist_ok=True)

                audio_path = os.path.join(
                    "recordings",
                    audio_file.name
                )

                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                model = whisper.load_model("base")

                result = model.transcribe(audio_path)

                st.session_state.transcript = result["text"].strip()

                st.success("Transcription completed successfully! 🎉")

            except Exception as e:

                st.error("Transcription failed.")

                st.code(str(e))


# Use Whisper transcript automatically

if st.session_state.transcript:

    transcript = st.text_area(
        "Whisper Transcript",
        value=st.session_state.transcript,
        height=220,
        key="whisper_transcript"
    )

else:

    transcript = st.text_area(
        "Transcript",
        value=st.session_state.content_input,
        height=220,
        placeholder=(
            "Example:\n\n"
            "Today I want to talk about why freshers should learn "
            "AI skills in 2026..."
        ),
        key="manual_transcript",
        label_visibility="collapsed",
    )

st.caption(
    "Paste the transcript or raw idea from your 1-minute video below."
)

# ---------------------------------------------------------
# GENERATE CONTENT
# ---------------------------------------------------------
generate = st.button(
    "✨ Generate LinkedIn Post",
    type="primary",
    use_container_width=False,
)

if st.session_state.generate_from_voice:
    generate = True
    st.session_state.generate_from_voice = False

if generate:

    if not transcript.strip():

        st.warning("Please enter a transcript before generating content.")

    else:

        st.session_state.approved = False
        st.session_state.rejected = False

        with st.spinner("AI is analyzing your content and writing the post..."):

            try:

                llm = LLM(
                    model="openrouter/openrouter/free",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENAI_API_KEY"),
                )

                content_agent = Agent(
                    role="LinkedIn Content Strategist",
                    goal=(
                        "Transform raw transcripts into engaging, "
                        "professional and natural LinkedIn posts."
                    ),
                    backstory=(
                        "You are an experienced LinkedIn content strategist "
                        "who understands professional audiences, storytelling, "
                        "hooks, engagement and personal branding."
                    ),
                    llm=llm,
                    verbose=False,
                )

                task = Task(
                    description=f"""
                    Convert the following transcript into a high-quality
                    LinkedIn post.

                    TRANSCRIPT:
                    {transcript}

                    REQUIREMENTS:

                    1. Start with a strong attention-grabbing hook.
                    2. Keep the tone natural and human.
                    3. Do not sound robotic or AI-generated.
                    4. Organize the content into short readable paragraphs.
                    5. Highlight the main insight from the transcript.
                    6. Add practical value where appropriate.
                    7. End with an engaging call to action.
                    8. Add 5-10 relevant hashtags.
                    9. Do not mention that AI created the post.
                    10. Keep it suitable for LinkedIn.
                    """,

                    expected_output=(
                        "A polished LinkedIn post with a strong hook, "
                        "valuable content, CTA and relevant hashtags."
                    ),

                    agent=content_agent,
                )

                crew = Crew(
                    agents=[content_agent],
                    tasks=[task],
                    verbose=False,
                )

                result = crew.kickoff()

                st.session_state.generated_post = str(result)
                st.session_state.generation_count += 1

                st.success("Content generated successfully!")

            except Exception as e:

                st.error(
                    "Something went wrong while generating the post."
                )

                st.code(str(e))

# ---------------------------------------------------------
# GENERATED POST
# ---------------------------------------------------------

if st.session_state.generated_post:

    st.markdown(
        '<div class="section-title">📝 Generated Content</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="post-container">',
        unsafe_allow_html=True
    )

    st.markdown(st.session_state.generated_post)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # Action buttons

    approve_col, reject_col, regenerate_col = st.columns(3)

    with approve_col:

        if st.button(
            "✅ Approve Post",
            use_container_width=True
        ):

            st.session_state.approved = True
            st.session_state.rejected = False

            os.makedirs("approved_posts", exist_ok=True)

            file_number = len(os.listdir("approved_posts")) + 1

            file_path = os.path.join(
                "approved_posts",
                f"linkedin_post_{file_number}.txt"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.generated_post)

            st.success("Post approved and saved successfully! 🎉")

    with reject_col:

        if st.button(
            "✕ Request Changes",
            use_container_width=True
        ):

            st.session_state.rejected = True
            st.session_state.changes_count += 1
            st.session_state.approved = False

            st.warning(
                "Post marked for changes. Edit your transcript and generate again."
            )

    with regenerate_col:

        if st.button(
            "↻ Generate Again",
            use_container_width=True
        ):

            st.session_state.generated_post = None
            st.session_state.approved = False
            st.session_state.rejected = False

            st.rerun()

# ---------------------------------------------------------
# APPROVAL STATUS
# ---------------------------------------------------------

if st.session_state.approved:

    st.markdown("""
    <div style="
        margin-top:20px;
        padding:18px;
        border-radius:14px;
        background:#ecfdf5;
        border:1px solid #a7f3d0;
        color:#065f46;
        font-weight:600;
    ">
        ✓ Content approved and ready for publishing.
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.rejected:

    st.markdown("""
    <div style="
        margin-top:20px;
        padding:18px;
        border-radius:14px;
        background:#fff7ed;
        border:1px solid #fed7aa;
        color:#9a3412;
        font-weight:600;
    ">
        ⚠ Content needs changes before approval.
    </div>
    """, unsafe_allow_html=True)
    # ---------------------------------------------------------
# CONTENT DASHBOARD
# ---------------------------------------------------------

st.markdown("---")
st.subheader("📊 Content Dashboard")

approved_count = 0

if os.path.exists("approved_posts"):
    approved_count = len(
        [
            f for f in os.listdir("approved_posts")
            if f.endswith(".txt")
        ]
    )

generated_count = st.session_state.get("generation_count", 0)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📝 Generated Posts",
        generated_count
    )

with col2:
    st.metric(
        "✅ Approved Posts",
        approved_count
    )

with col3:
    st.metric(
        "📁 Saved Posts",
        approved_count
    )

with col4:
    st.metric(
        "✏️ Changes Requested",
        st.session_state.get("changes_count", 0)
    )
# ---------------------------------------------------------
# APPROVED POSTS
# ---------------------------------------------------------

st.markdown("---")
st.subheader("📁 Approved Posts")

if os.path.exists("approved_posts"):

    approved_files = os.listdir("approved_posts")

    if approved_files:

        for file in approved_files:

            file_path = os.path.join(
                "approved_posts",
                file
            )

            with open(file_path, "r", encoding="utf-8") as f:
                post_content = f.read()

            with st.expander(f"📄 {file}"):

                st.text_area(
                    "Post Content",
                    value=post_content,
                    height=200,
                    key=f"approved_{file}"
                )

                st.download_button(
                    "⬇️ Download Post",
                    data=post_content,
                    file_name=file,
                    mime="text/plain",
                    key=f"download_{file}"
                )

    else:
        st.info("No approved posts yet.")

else:
    st.info("No approved posts yet.")
# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("""
<div class="footer">
    ContentFlow AI • AI Content Automation POC<br>
    Built with Streamlit • CrewAI • OpenRouter
</div>
""", unsafe_allow_html=True)