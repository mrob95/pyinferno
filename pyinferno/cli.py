import argparse
import os
import subprocess
import sys
import tempfile
import webbrowser


def main():

    parser = argparse.ArgumentParser(usage="pyinferno [-o outfile] [pyinstrument_options] <script> [args]")
    parser.add_argument(
        "-o", "--outfile",
        action="store",
        dest="outfile",
        help="File to save the flamegraph to",
        default=None,
    )
    inferno_args, pyinstrument_args = parser.parse_known_args()
    if inferno_args.outfile:
        outpath = inferno_args.outfile
    else:
        outpath = tempfile.NamedTemporaryFile(prefix="flamegraph-", suffix=".svg", delete=False).name

    argv = sys.argv[1:]
    if not argv:
        parser.print_usage()
        sys.exit(0)

    args = [
        "pyinstrument",
        "-r", "pyinferno.Renderer",
        "-p", f"title={' '.join(pyinstrument_args)}",
        "-o", outpath,
        *pyinstrument_args
    ]
    subprocess.run(args, check=True)

    if not inferno_args.outfile:
        filepath = os.path.relpath(outpath)
        webbrowser.open(filepath)
