from __future__ import annotations

from .pyinferno import InfernoError, flamegraph_from_lines

from pyinstrument.renderers.base import Renderer


class InfernoRenderer(Renderer):
    output_file_extension = "svg"

    def __init__(self, title: str | None = None):
        self.title = title

    def should_skip(self, filename: str, function: str) -> bool:
        return filename.startswith("<frozen importlib._bootstrap")

    def render(self, session) -> str:
        """
        Return a string that contains the rendered form of `frame`.
        """
        samples_per_s = session.sample_count/session.duration
        lines = []
        for record in session.frame_records:
            formatted_frames = []
            frames, time_spent = record
            for frame in frames:
                try:
                    identifier, _, attributes = frame.partition("\x01")
                    function, filename, lineno = identifier.split("\x00")
                except ValueError:
                    raise InfernoError(f"Could not parse frame '{frame}'")
                if not self.should_skip(filename, function):
                    formatted_frames.append(":".join((filename, lineno, function)))
            lines.append(f"{';'.join(formatted_frames)} {round(time_spent*samples_per_s)}")
        return flamegraph_from_lines(lines, self.title)
