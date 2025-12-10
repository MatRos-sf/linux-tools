"""
This script combines multiple mp3 files from a directory into a single summary
audio file, with configurable silence between the clips.
"""
import logging
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from pydub import AudioSegment

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def make_summary_audio(audios: list[AudioSegment], duration_gap: int) -> AudioSegment:
    """
    Concatenates a list of audio segments with silence in between.

    Args:
        audios: A list of pydub AudioSegment objects.
        duration_gap: A multiplier for the duration of the preceding audio clip
                      to determine the length of silence to insert.

    Returns:
        A single pydub AudioSegment object.
    """
    summary_audio = AudioSegment.empty()
    if not audios:
        return summary_audio

    for i, audio in enumerate(audios):
        summary_audio += audio
        if i < len(audios) - 1:  # Don't add silence after the last one
            silence_duration_ms = audio.duration_seconds * duration_gap * 1000
            silence_audio = AudioSegment.silent(duration=silence_duration_ms)
            summary_audio += silence_audio

    return summary_audio


def main():
    """
    Finds all mp3 files in a directory, combines them into a single
    file with silence in between, and saves the result.
    """
    parser = ArgumentParser(
        description="Combine multiple mp3 files into a summary audio file."
    )
    parser.add_argument(
        "--base_dir",
        type=str,
        required=True,
        help="Directory containing the mp3 files.",
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        required=True,
        help="Directory to save the summary audio.",
    )
    parser.add_argument(
        "--duration_gap",
        type=int,
        default=2,
        help="Multiplier for silence duration between audio clips (default 2).",
    )
    parser.add_argument(
        "--remove_after",
        action="store_true",
        help="Remove original mp3 files after creating the summary.",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    list_file_mp3 = sorted(list(base_dir.glob("*.mp3")))
    if not list_file_mp3:
        logger.warning(f"No mp3 files found in {base_dir}")
        return

    logger.info(f"Found {len(list_file_mp3)} audio files.")

    audio_segment_collection = [AudioSegment.from_mp3(f) for f in list_file_mp3]

    logger.info("Creating summary audio...")
    summary_audio = make_summary_audio(audio_segment_collection, args.duration_gap)

    logger.info("Exporting summary audio...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = save_dir / f"summary_audio_{timestamp}.mp3"
    summary_audio.export(output_path, format="mp3")
    logger.info(f"File has been saved to {output_path}")

    if args.remove_after:
        logger.info("Removing original files...")
        for f in list_file_mp3:
            f.unlink()
        logger.info("Original files removed.")


if __name__ == "__main__":
    main()
