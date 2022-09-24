import pstats
from .pyinferno import flamegraph_from_lines
from cProfile import Profile

class Profiler:
    def __init__(self, path: str):
        self.path = path
        self.profiler = Profile()

    def enable(self):
        self.profiler.enable()

    def disable(self):
        self.profiler.disable()

    def get_stats(self) -> pstats.Stats:
        self.profiler.create_stats()
        return pstats.Stats(self.profiler)
