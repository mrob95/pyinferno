from __future__ import annotations

import contextlib
import os
import tempfile
import webbrowser
from pathlib import Path

from pyinstrument.profiler import Profiler

from .renderer import InfernoRenderer


@contextlib.contextmanager
def InfernoProfiler(
    file: str | Path | None = None,
    auto_open: bool = False,
    title: str | None = None,
    **kwargs,
):
    if file is None and not auto_open:
        raise ValueError(
            "Must pass a file to save the flamegraph to, or auto_open=True to open directly in the browser."
        )
    profiler = Profiler(**kwargs)
    profiler.start()
    try:
        yield profiler
    finally:
        profiler.stop()
        output = profiler.output(InfernoRenderer(title=title))

        if file:
            outpath = file
        else:
            outpath = tempfile.NamedTemporaryFile(prefix="flamegraph-", suffix=".svg", delete=False).name

        with open(outpath, "w+") as f:
            f.write(output)

        if auto_open:
            filepath = os.path.relpath(outpath)
            webbrowser.open(filepath)
