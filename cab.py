#!/usr/bin/env python3
"""
cap: Capture Audio from background
"""
import argparse
import json
import logging
import os
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
RAW_FILE_NAME = SCRIPT_DIR / Path("_raw_audio.raw")
INFO_FILE = SCRIPT_DIR / Path("_info.json")
PID = None

parser = argparse.ArgumentParser(description="Capture Audio from background")
parser.add_argument(
    "--file_name",
    type=str,
    help="Output file name. Default name audio_YYYY-MM-DD_HH-MM-SS.mp3",
    required=False,
)
parser.add_argument(
    "--destination",
    type=str,
    help="Destination folder. Default home directory",
    required=False,
)
parser.add_argument(
    "-f",
    "--format",
    type=str,
    help="Output format. Default mp3",
    required=False,
    default="mp3",
)
parser.add_argument(
    "--env", action="store_true", help="Capture args from env", required=False
)
parser.add_argument(
    "--input",
    type=str,
    help='Input device. Use command `pactl list sources | grep -E "Name:|monitor"` to get list of available devices',
    required=False,
)

args = parser.parse_args()


def add_argument(arg: str, value: Any, expected_keys: list[str]):
    arg = arg.lower()
    if arg in expected_keys:
        setattr(args, arg, value)
    if arg == "pid":
        global PID
        PID = value


def save_session_info(pid: int):
    """Save current session info to file"""
    with open(INFO_FILE, "w") as f:
        json.dump(
            {
                "pid": pid,
                "file_name": args.file_name,
                "destination": str(args.destination),
                "format": args.format,
            },
            f,
        )


def load_session_info():
    """Load session info from file"""
    if not INFO_FILE.exists():
        return None
    with open(INFO_FILE, "r") as f:
        return json.load(f)


def parse_args(name: str | Path, is_env: bool = False):
    """Add additional arguments. When is_env true function try parsing env variables to the args,
    but when is false function try to parse args from RAW_FILE_NAME json file"""
    args_collection = vars(args).keys()

    if is_env and args.env:
        for key, value in dotenv_values(name).items():
            add_argument(key, value, args_collection)
    else:
        session_info = load_session_info() or {}
        for key, value in session_info.items():
            add_argument(key, value, args_collection)


def check_process_exists() -> str:
    """Check if the parec processing is already running"""
    proces = subprocess.Popen(["pgrep", "-f", "parec"], stdout=subprocess.PIPE)
    pid = proces.stdout.read().decode()
    return pid.replace("\n", "")


def show_notification(title: str, msg: str):
    """Show notification"""
    subprocess.Popen(["notify-send", title, msg])


def convert_audio(file_name: str | Path):
    """Convert audio to given format using ffmpeg"""
    if isinstance(file_name, Path):
        file_name = str(file_name)
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-i",
            str(RAW_FILE_NAME),
            file_name,
        ],
        check=True,
    )


def start_recording(input_device: str) -> int:
    with open(RAW_FILE_NAME, "wb") as raw_file:
        process = subprocess.Popen(
            [
                "parec",
                "-d",
                input_device,
                "--format=s16le",
                "--rate=48000",
                "--channels=2",
            ],
            stdout=raw_file,
        )

    show_notification("Recording Started", "Capturing audio...")
    return process.pid


def stop_recording(pid: int):
    """Stop recording"""
    try:
        os.kill(pid, signal.SIGTERM)
        logger.info(f"Recording stopped (PID {pid})")
    except ProcessLookupError:
        logger.error(f"Process with PID {pid} not found")


def clean_session():
    """Remove raw audio file and info file"""
    try:
        os.remove(RAW_FILE_NAME)
        os.remove(INFO_FILE)
    except Exception as e:
        logger.warning(f"Failed to clean session: {e}")


def main():
    parse_args(".env", True)
    pid = check_process_exists()
    if not pid:
        if not args.file_name:
            args.file_name = f"audio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp3"

        if not args.destination:
            args.destination = Path.home()
        pid_number = start_recording(args.input)

        save_session_info(pid_number)

    else:
        parse_args(INFO_FILE)

        stop_recording(int(pid))
        new_name = Path(args.destination) / Path(args.file_name)
        try:
            convert_audio(new_name)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert audio: {e}")
            show_notification("Recording stopped", "Failed to convert audio")
            clean_session()
            return
        show_notification("Recording stopped", f"Audio saved to {new_name}")
        clean_session()


if __name__ == "__main__":
    main()
