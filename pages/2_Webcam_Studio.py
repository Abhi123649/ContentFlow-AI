
import streamlit as st
import cv2
import sounddevice as sd
import numpy as np
import wave
import threading
import time
from pathlib import Path

st.set_page_config(
    page_title="Webcam Studio",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Webcam Studio")
st.write("Record your video with microphone audio and convert speech into text.")

# Settings
SAMPLE_RATE = 48000
MIC_DEVICE = None

OUTPUT_DIR = Path("recordings")
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_FILE = OUTPUT_DIR / "webcam_video.mp4"
AUDIO_FILE = OUTPUT_DIR / "webcam_audio.wav"


def record_audio(duration, audio_data, errors):
    try:
        audio = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            device=MIC_DEVICE
        )
        sd.wait()
        audio_data.append(audio.copy())
    except Exception as e:
        errors.append(str(e))


# Recording duration
duration = st.slider(
    "Recording Duration (seconds)",
    min_value=10,
    max_value=60,
    value=10,
    step=10
)

# Start recording
if st.button(
    "🔴 Start Recording",
    type="primary",
    use_container_width=True
):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Camera could not be opened. Check camera permission.")
        st.stop()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(
        str(VIDEO_FILE),
        cv2.VideoWriter_fourcc(*"mp4v"),
        20.0,
        (width, height)
    )

    if not writer.isOpened():
        cap.release()
        st.error("Could not create the video file.")
        st.stop()

    audio_data = []
    audio_errors = []

    audio_thread = threading.Thread(
        target=record_audio,
        args=(duration, audio_data, audio_errors)
    )
    audio_thread.start()

    preview = st.empty()
    status = st.empty()
    progress = st.progress(0)

    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                status.error("Camera frame could not be read.")
                break

            writer.write(frame)

            elapsed = time.time() - start_time
            percent = min(int(elapsed / duration * 100), 100)

            progress.progress(percent)
            status.info(
                f"🔴 Recording... {min(int(elapsed), duration)} / {duration} seconds"
            )

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            preview.image(frame_rgb, channels="RGB")

            if elapsed >= duration:
                break

    finally:
        cap.release()
        writer.release()
        audio_thread.join()
        preview.empty()

    if audio_errors:
        st.error("Microphone recording failed.")
        st.code(audio_errors[0])

    elif audio_data:
        audio_int16 = np.int16(
            np.clip(audio_data[0], -1.0, 1.0) * 32767
        )

        with wave.open(str(AUDIO_FILE), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        progress.progress(100)
        status.success("✅ Video and audio recording completed!")

    else:
        st.warning("No audio was recorded.")

# Recorded video playback
if VIDEO_FILE.exists():
    st.divider()
    st.subheader("🎬 Recorded Video")
    st.video(str(VIDEO_FILE))
    st.caption(f"Video saved at: {VIDEO_FILE}")

# Recorded audio playback
if AUDIO_FILE.exists():
    st.subheader("🎤 Recorded Audio")

    with open(AUDIO_FILE, "rb") as f:
        audio_bytes = f.read()

    st.audio(audio_bytes, format="audio/wav")
    st.caption(f"Audio saved at: {AUDIO_FILE}")

# Audio transcription
st.divider()
st.subheader("🧠 Audio to Transcript")

if st.button(
    "🎤 Transcribe Recorded Webcam Audio",
    use_container_width=True,
    key="transcribe_webcam_audio_btn"
):
    if not AUDIO_FILE.exists():
        st.error("Pehle webcam se recording karo.")
    else:
        try:
            import whisper

            with st.spinner(
                "Whisper audio ko text mein convert kar raha hai..."
            ):
                model = whisper.load_model("base")
                result = model.transcribe(
                    str(AUDIO_FILE),
                    fp16=False
                )
                transcript = result["text"].strip()

            if transcript:
                st.session_state["transcript"] = transcript
                st.success("✅ Transcription completed!")

                st.text_area(
                    "📝 Transcribed Text",
                    value=transcript,
                    height=220,
                    key="webcam_transcript_result"
                )

                st.download_button(
                    "⬇️ Download Transcript",
                    data=transcript,
                    file_name="webcam_transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning(
                    "Speech detect nahi hui. Microphone check karke dobara record karo."
                )

        except Exception as e:
            st.error("Transcription failed.")
            st.code(str(e))

# Show previously transcribed text after Streamlit reruns
if st.session_state.get("transcript") and not st.session_state.get(
    "transcription_displayed"
):
    st.caption("Last transcript is available in the session.")