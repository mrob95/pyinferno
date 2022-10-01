import sys
import os
import subprocess
import tempfile
import webbrowser

def main():
    argv = sys.argv[1:]
    if not argv:
        print("Usage: pyinferno <script> [args]")
        sys.exit(0)

    output = tempfile.NamedTemporaryFile(prefix="flamegraph-", suffix=".svg", delete=False)
    args = [
        "pyinstrument",
        "-r", "pyinferno.Renderer",
        "-p", f"title={' '.join(argv)}",
        "-o", output.name,
        *argv
    ]
    subprocess.run(args, check=True)

    filepath = os.path.relpath(output.name)
    webbrowser.open(filepath)
