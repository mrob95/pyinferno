from pathlib import Path
import pytest
from pyinferno import Profiler, flamegraph_from_lines, lines_from_stats


def test_simple_from_lines():
    testdata = Path("testdata/01_simple_from_lines")
    with open(testdata / "input.prof") as f:
        result = flamegraph_from_lines(f.readlines())
    with open(testdata / "output.svg") as f:
        assert result == f.read().strip()


def test_convert_stats_to_lines():
    testdata = Path("testdata/02_convert_stats_to_lines")
    with open(testdata / "input") as f:
        sample_stats = f.read()
    stats = eval(sample_stats)
    lines = lines_from_stats(stats)
    with open(testdata / "output.prof") as f:
        assert "\n".join(lines) == f.read().strip()
