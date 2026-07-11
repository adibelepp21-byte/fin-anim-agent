#!/usr/bin/env python3
"""Measure an audio file's duration in seconds via ffprobe.

Used by the whiteboard_explainer workflow: after generating a beat's
narration clip (e.g. via the elevenlabs skill), measure its real length here
and write it into that beat's `duration` field — don't guess a duration from
word count, since TTS pacing varies (see SKILL.md).

Usage:
    python3 audio_duration.py narration_01.mp3
"""
from __future__ import annotations

import subprocess
import sys


def get_audio_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: audio_duration.py <audio-file>", file=sys.stderr)
        sys.exit(1)
    print(f"{get_audio_duration(sys.argv[1]):.2f}")
