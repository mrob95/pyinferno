# PyInferno
Python package that renders [pyinstrument](https://github.com/joerick/pyinstrument) profiles as flamegraphs, using the [inferno](https://github.com/jonhoo/inferno) rust crate.

![Example pandas trace](https://github.com/mrob95/pyinferno/blob/master/images/pandas_example.png?raw=true)

## Installation
Install from [PyPi](https://pypi.org/project/pyinferno/):
```
pip install pyinferno
```
## Usage
### Context manager
To profile a specific piece of code, use the [pyinstrument Profiler class](https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-specific-chunk-of-code), then render the result using pyinferno's `InfernoRenderer`:
```python
from pyinstrument.profiler import Profiler
from pyinferno import InfernoRenderer
import time

def slow():
    time.sleep(0.5)

with Profiler() as profiler:
    slow()

output = profiler.render(InfernoRenderer(title="slow"))

with open("flamegraph.svg", "w+") as f:
    f.write(output)
```

### Command-line
To profile a Python script, you can pass `pyinferno.Renderer` as the renderer to the `pyinstrument` CLI:
```bash
pyinstrument -r pyinferno.Renderer -o flamegraph.svg slow.py
```

For convenience, `pyinferno` includes its own script which wraps the `pyinstrument` CLI:
```bash
pyinferno slow.py
```

If no output file is specified, the flamegraph will be written to a temporary file and automatically opened using python's `webbrowser` module. To save the flamegraph to a file, pass the `-o` option:
```bash
pyinferno -o flamegraph.svg slow.py
```

To profile a python module, pass the `-m` argument:
```bash
pyinferno -m pytest -k slow_test
```
