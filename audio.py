from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def audio_strip(audio_path: str) -> str:
    """
    Removes silence from the beginning and end of an MP3 audio file.

    Args:
        audio_path: The path to the audio file.

    Returns:
        The path to the modified audio file.
    """
    audio = AudioSegment.from_file(audio_path, format="mp3")

    # detect_nonsilent returns a list of [start, end] milliseconds for non-silent parts
    nonsilent_chunks = detect_nonsilent(
        audio,
        min_silence_len=500,  # consider silence of at least 500ms
        silence_thresh=audio.dBFS - 16,
    )

    if not nonsilent_chunks:
        # The file is entirely silent, do nothing
        return audio_path

    # Get the start of the first non-silent chunk and the end of the last one
    start_trim = nonsilent_chunks[0][0]
    end_trim = nonsilent_chunks[-1][1]

    # Add a small buffer to avoid cutting too abruptly
    start_trim = max(0, start_trim - 100)
    end_trim = min(len(audio), end_trim + 100)

    trimmed_audio = audio[start_trim:end_trim]
    trimmed_audio.export(audio_path, format="mp3")

    return audio_path
