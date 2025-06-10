"""Simple CLI entry point for transcription."""
# pragma: no cover

import argparse
import sys
import builtins
from runpod_client import RunPodClient


def main(argv=None):
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio using RunPod",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("audio_url", help="URL of the audio file to transcribe")
    args = parser.parse_args(argv)

    if not args.audio_url:
        parser.error("audio_url is required")

    client = RunPodClient()
    print("Transcribing...", file=sys.stderr)
    result = client.transcribe(args.audio_url)
    print(result)


# allow tests referencing `cli.main`
cli = sys.modules[__name__]
builtins.cli = cli


if __name__ == "__main__":
    main()
