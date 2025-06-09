import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli import main


def test_cli(monkeypatch, capsys):
    dummy_url = "http://example.com/audio.wav"
    with patch("spiceflow.cli.RunPodClient") as MockClient:
        instance = MockClient.return_value
        instance.transcribe.return_value = "dummy-transcript"

        cli.main([dummy_url])

        instance.transcribe.assert_called_once_with(dummy_url)

    captured = capsys.readouterr()
    assert captured.out.strip() == "dummy-transcript"
