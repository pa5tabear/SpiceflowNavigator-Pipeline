import os
import pytest

endpoint = os.environ.get("RUNPOD_ENDPOINT")

@pytest.mark.skipif(endpoint is None, reason="RUNPOD_ENDPOINT not set")
def test_runpod_endpoint_present():
    assert isinstance(endpoint, str) and endpoint.strip()
