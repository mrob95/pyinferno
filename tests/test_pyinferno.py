import os
import subprocess
import time
from pathlib import Path

import pytest
from pyinstrument.profiler import Profiler

from pyinferno import InfernoError, Renderer, flamegraph_from_lines

TITLE = "My fantastic title"

SAMPLE_CODE = """
import time
def a():
    time.sleep(0.2)
a()"""


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


def test_pyinstrument():
    p = Profiler()
    p.start()
    time.sleep(0.2)
    p.stop()
    result = p.output(Renderer(title=TITLE))
    assert len(result) > 0
    assert TITLE in result


def test_pyinstrument_default_title():
    p = Profiler()
    p.start()
    time.sleep(0.2)
    p.stop()
    result = p.output(Renderer())
    assert len(result) > 0


def test_profiler_context_manager():
    with Profiler() as p:
        time.sleep(0.2)
    result = p.output(Renderer(title=TITLE))
    assert len(result) > 0
    assert TITLE in result


def test_pyinstrument_cli(tmp_path):
    code_path = tmp_path / "code.py"
    out_path = tmp_path / "out.svg"
    with open(code_path, "w+") as f:
        f.write(SAMPLE_CODE)
    subprocess.run([
        "pyinstrument",
        "-r", "pyinferno.Renderer",
        "-p", f"title={TITLE}",
        "-o",
        str(out_path.absolute()),
        str(code_path.absolute()),
    ], check=True)
    with open(out_path) as f:
        result = f.read()
    assert len(result) > 0
    assert TITLE in result


def test_pyinferno_cli(tmp_path):
    code_path = tmp_path / "code.py"
    out_path = tmp_path / "out.svg"
    with open(code_path, "w+") as f:
        f.write(SAMPLE_CODE)
    subprocess.run([
        "pyinferno",
        "-o",
        str(out_path.absolute()),
        str(code_path.absolute()),
    ], check=True)
    with open(out_path) as f:
        result = f.read()
    assert len(result) > 0
    assert "code.py" in result


def test_error_from_rust():
    with pytest.raises(InfernoError):
        flamegraph_from_lines(["not a valid trace"])
