import os
import time
from pathlib import Path

import pytest

from pyinferno import (InfernoError, InfernoProfiler, flamegraph_from_lines,
                       lines_from_stats)

TITLE = "My fantastic title"

def test_simple_from_lines():
    testdata = Path("testdata/01_simple_from_lines")
    with open(testdata / "input.prof") as f:
        result = flamegraph_from_lines(f.readlines(), TITLE)
    if os.getenv("TEST_OVERWRITE"):
        with open(testdata / "output.svg", "w+") as f:
            f.write(result)
    with open(testdata / "output.svg") as f:
        contents = f.read().strip()
        assert result == contents
        assert TITLE in contents


def test_convert_stats_to_lines():
    testdata = Path("testdata/02_convert_stats_to_lines")
    with open(testdata / "input") as f:
        sample_stats = f.read()
    stats = eval(sample_stats)
    result = "\n".join(lines_from_stats(stats))
    if os.getenv("TEST_OVERWRITE"):
        with open(testdata / "output.prof", "w+") as f:
            f.write(result)
    with open(testdata / "output.prof") as f:
        assert result == f.read().strip()


def test_profiler_manual(tmp_path):
    p = InfernoProfiler()
    p.enable()
    time.sleep(0.5)
    p.disable()
    result = p.get_flamegraph()
    assert len(result) > 0

    out_path = tmp_path / "output"
    p.write_flamegraph(out_path)
    with open(out_path) as f:
        assert len(f.read()) > 0


def test_profiler_context_manager(tmp_path):
    out_path = tmp_path / "output"
    with InfernoProfiler(out_path, TITLE) as p:
        time.sleep(0.5)
    result = p.get_flamegraph()
    assert len(result) > 0
    with open(out_path) as f:
        contents = f.read()
        assert len(contents) > 0
        assert TITLE in contents


def test_error_from_rust():
    with pytest.raises(InfernoError):
        flamegraph_from_lines(["not a valid trace"])
