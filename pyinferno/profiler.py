from __future__ import annotations

import pstats
from cProfile import Profile
from pathlib import Path

from .converter import lines_from_stats
from .pyinferno import InfernoError, flamegraph_from_lines


class InfernoProfiler:
    def __init__(self, out_path: str | Path | None = None):
        self.out_path = out_path
        self.profiler = Profile()
        self.enabled = False

    def enable(self):
        self.profiler.enable()
        self.enabled = True

    def disable(self):
        self.profiler.disable()
        self.enabled = False
        self.flamegraph = self.get_flamegraph()

    def get_flamegraph(self) -> str:
        if self.enabled:
            raise InfernoError("Cannot get_flamegraph until after InfernoProfiler.disable has been called.")

        self.profiler.create_stats()
        stats = pstats.Stats(self.profiler)
        lines = lines_from_stats(stats.stats)
        return flamegraph_from_lines(lines)

    def write_flamegraph(self, out_path: str | Path):
        if self.enabled:
            raise InfernoError("Cannot write_flamegraph until after InfernoProfiler.disable has been called.")

        flamegraph = self.get_flamegraph()
        with open(out_path, "w+") as f:
            f.write(flamegraph)

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, type, value, traceback):
        self.disable()
        if self.out_path is not None:
            self.write_flamegraph(self.out_path)
