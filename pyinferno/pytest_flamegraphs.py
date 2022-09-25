from pathlib import Path
from typing import cast

import pytest

from pyinferno import InfernoError, InfernoProfiler


def pytest_addoption(parser):
    group = parser.getgroup('flamegraphs')
    group.addoption(
        '--flamegraphs',
        action='store_true',
        default=False,
        help='Generate flamegraphs for test run.'
    )
    group.addoption(
        '--flamegraph-dir',
        action='store',
        type=Path,
        metavar="dir",
        default=Path("flamegraphs"),
        help='Directory to save flamegraphs into.'
    )


@pytest.fixture(autouse=True)
def __flamegraphs(request):
    if not request.config.getoption("--flamegraphs"):
        yield
    else:
        target_dir = cast(Path, request.config.getoption("--flamegraph-dir"))
        if target_dir.exists() and not target_dir.is_dir():
            raise InfernoError(f"flamegraph-dir '{target_dir}' is not a directory.")
        if not target_dir.exists():
            target_dir.mkdir()

        p = InfernoProfiler()
        p.enable()
        yield
        p.disable()

        name = request.function.__name__
        p.write_flamegraph(target_dir / f"{name}.svg")
