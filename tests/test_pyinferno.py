from pathlib import Path
import time
from pyinferno import InfernoProfiler, flamegraph_from_lines, lines_from_stats


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


def test_profiler_manual(tmp_path):
    p = InfernoProfiler()
    p.enable()
    time.sleep(0.5)
    p.disable()
    result = p.get_flamegraph()
    assert result is not None
    assert len(result) > 0

    out_path = tmp_path / "output"
    p.write_flamegraph(out_path)
    with open(out_path) as f:
        assert len(f.read()) > 0


def test_profiler_context_manager(tmp_path):
    out_path = tmp_path / "output"
    with InfernoProfiler(out_path) as p:
        time.sleep(0.5)
    result = p.get_flamegraph()
    assert result is not None
    assert len(result) > 0
    with open(out_path) as f:
        assert len(f.read()) > 0
