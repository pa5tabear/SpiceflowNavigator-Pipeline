"""Simple CLI entry point for transcription."""
# pragma: no cover

import argparse
import sys
import builtins
import multiprocessing as mp
from runpod_client import RunPodClient
from analyzer import StrategicAnalyzer
from workflow import WorkflowManager


def _transcribe_proc(audio_url: str) -> None:
    """Process target to transcribe audio and print the result."""
    print(RunPodClient().transcribe(audio_url))


def _analyze_proc(text: str) -> None:
    """Process target to analyze text and print the result."""
    print(StrategicAnalyzer().analyze(text))


def _workflow_proc(feed_url: str) -> None:
    """Process target to execute the workflow."""
    WorkflowManager(feed_url).run()


def _run_multi(audio_url: str, text: str, feed_url: str) -> None:
    """Run transcription, analysis and workflow concurrently."""
    procs = [
        mp.Process(target=_transcribe_proc, args=(audio_url,)),
        mp.Process(target=_analyze_proc, args=(text,)),
        mp.Process(target=_workflow_proc, args=(feed_url,)),
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()


def main(argv=None):
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio using RunPod",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("audio_url", help="URL of the audio file to transcribe")
    parser.add_argument(
        "--multi",
        action="store_true",
        help="Run transcription, analysis and workflow concurrently",
    )
    parser.add_argument("--text", default="Test text")
    parser.add_argument("--feed-url", default="https://example.com/feed")
    args = parser.parse_args(argv)

    if args.multi:
        _run_multi(args.audio_url, args.text, args.feed_url)
        return

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
