from moviepy import VideoFileClip
import os


def extract_audio(video_path, output_path="recordings/extracted_audio.wav"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    video = VideoFileClip(video_path)

    if video.audio is None:
        video.close()
        raise ValueError("Video me audio track nahi mila.")

    video.audio.write_audiofile(
        output_path,
        codec="pcm_s16le"
    )

    video.close()

    return output_path