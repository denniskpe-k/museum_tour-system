"""
services/audio_generator.py

Generates real, playable narration audio files from a script of text
using espeak-ng (a free, fully offline text-to-speech engine). This
lets AudioGuide stops have genuine spoken narration instead of a text
description, without needing any paid voice-actor budget or internet
access.

espeak-ng only needs to be present on the machine that GENERATES the
audio files (this project ships them already generated, in
assets/audio/) — the app itself only ever plays back the resulting
.wav files through Kivy's SoundLoader, so a visitor's machine does not
need espeak-ng installed at all.
"""

import os
import shutil
import subprocess

AUDIO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio"
)


def espeak_available() -> bool:
    return shutil.which("espeak-ng") is not None or shutil.which("espeak") is not None


def generate_narration_audio(script: str, filename: str, voice: str = "en", speed_wpm: int = 155) -> str:
    """
    Synthesizes `script` into a .wav file at assets/audio/<filename>,
    using espeak-ng if available. Returns the file path; regenerates
    only if the file doesn't already exist (mirrors the pattern used
    by services/floorplan_generator.py). Raises RuntimeError if no TTS
    engine is available and the file doesn't already exist — callers
    on a visitor's machine should never hit this, since the audio
    files are pre-generated and shipped with the project.
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(path):
        return path

    engine = "espeak-ng" if shutil.which("espeak-ng") else "espeak"
    if not shutil.which(engine):
        raise RuntimeError(
            "No offline text-to-speech engine (espeak-ng/espeak) is available "
            "to generate narration audio, and no pre-generated file exists."
        )

    subprocess.run(
        [engine, "-v", voice, "-s", str(speed_wpm), "-w", path, script],
        check=True, capture_output=True,
    )
    return path
