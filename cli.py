"""Simple CLI entry point for transcription."""
# pragma: no cover

import argparse
import sys
from pathlib import Path

# Add path for RunPodClient
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "common-utils"))

from runpod_client import RunPodClient


def main(argv=None):
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Transcribe audio using RunPod")
    parser.add_argument("audio_url", help="URL of the audio file to transcribe")
    args = parser.parse_args(argv)

    client = RunPodClient()
    result = client.transcribe(args.audio_url)
    print(result)


if __name__ == "__main__":
    main()
