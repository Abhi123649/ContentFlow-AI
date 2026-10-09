import streamlit as st
import tempfile
import os
from faster_whisper import WhisperModel

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Voice & Transcript | ContentFlow AI",
    page_icon="🎙️",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown(
    """
    <style>

    .main {
        background-color: #f7f8fc;
    }

    .hero {
        padding: 30px;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827, #1f2937);
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 38px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 16px;
        color: #d1d5db;
        margin-bottom: 0;
    }

    .card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #6b7280;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD WHISPER MODEL
# --------------------------------------------------
@st.cache_resource
def load_whisper_model():
    return WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 25px 0;">
            <h2 style="margin-bottom:0;">ContentFlow AI</h2>
            <p style="color:#9ca3af;">AI Content Studio</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Workspace")

    st.page_link(
        "app.py",
        label="📝 Content Generator"
    )

    st.markdown(
        """
        <div style="
            background:#eef2ff;
            padding:10px;
            border-radius:10px;
            margin:5px 0;
            font-weight:600;
        ">
        🎙️ Voice & Transcript
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("📋 Approval Queue")
    st.markdown("📊 Analytics")

    st.divider()

    st.success("🟢 AI Engine Online")

# --------------------------------------------------
# HERO
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎙️ Voice & Transcript</h1>
        <p>
            Record your idea and automatically convert your voice
            into text using AI.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# RECORDING
# --------------------------------------------------
st.markdown(
    """
    <div class="card">
        <div class="section-title">🎤 Record Your Idea</div>
        <div class="section-subtitle">
            Speak naturally about any topic. AI will convert your
            recording into a transcript.
        </div>
    """,
    unsafe_allow_html=True
)

audio_value = st.audio_input(
    "Start recording",
    sample_rate=16000
)

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# AUDIO + TRANSCRIPTION
# --------------------------------------------------
if audio_value is not None:

    st.markdown(
        """
        <div class="card">
            <div class="section-title">🔊 Recording Preview</div>
            <div class="section-subtitle">
                Listen to your recording before transcription.
            </div>
        """,
        unsafe_allow_html=True
    )

    st.audio(audio_value)

    st.download_button(
        label="⬇️ Download Recording",
        data=audio_value.getvalue(),
        file_name="voice_recording.wav",
        mime="audio/wav"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # TRANSCRIBE BUTTON
    # --------------------------------------------------

    st.markdown(
        """
        <div class="card">
            <div class="section-title">🤖 AI Transcription</div>
            <div class="section-subtitle">
                Convert your voice recording into text automatically.
            </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "✨ Generate Automatic Transcript",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "🤖 AI is listening and generating your transcript..."
            ):

                # Save uploaded audio temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                ) as temp_audio:

                    temp_audio.write(audio_value.getvalue())
                    temp_audio_path = temp_audio.name

                # Load Whisper
                model = load_whisper_model()

                # Transcribe
                segments, info = model.transcribe(
                    temp_audio_path,
                    beam_size=5,
                    vad_filter=True
                )

                transcript_text = " ".join(
                    segment.text.strip()
                    for segment in segments
                )

                # Delete temporary file
                os.remove(temp_audio_path)

                # Save transcript
                st.session_state["voice_transcript"] = transcript_text

            st.success("✅ Transcript generated successfully!")

        except Exception as e:

            st.error(
                f"❌ Transcription error: {str(e)}"
            )

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# TRANSCRIPT DISPLAY
# --------------------------------------------------
if "voice_transcript" in st.session_state:

    transcript = st.session_state["voice_transcript"]

    st.markdown(
        """
        <div class="card">
            <div class="section-title">📝 Your Transcript</div>
            <div class="section-subtitle">
                Review or edit the AI-generated transcript.
            </div>
        """,
        unsafe_allow_html=True
    )

    edited_transcript = st.text_area(
        "Transcript",
        value=transcript,
        height=250,
        label_visibility="collapsed"
    )

    st.session_state["voice_transcript"] = edited_transcript

    st.success("✅ Transcript is ready for AI content generation.")
    
    st.markdown("")

if st.button(
    "🚀 Generate LinkedIn Post from Transcript",
    type="primary",
    use_container_width=True
):
    st.session_state["content_input"] = edited_transcript
    st.session_state["generate_from_voice"] = True
    st.switch_page("app.py")

    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # PIPELINE STATUS
    # --------------------------------------------------

    st.markdown("### Pipeline Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🎙️ Voice Recording",
            "Ready"
        )

    with col2:
        st.metric(
            "📝 Transcript",
            "Ready"
        )

    with col3:
        st.metric(
            "🤖 AI Content",
            "Next"
        )

else:

    st.markdown("### Pipeline Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🎙️ Voice Recording",
            "Waiting"
        )

    with col2:
        st.metric(
            "📝 Transcript",
            "Waiting"
        )

    with col3:
        st.metric(
            "🤖 AI Content",
            "Waiting"
        )