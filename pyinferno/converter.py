from typing import Dict, List, Tuple
from .flameprof import calc_callers, prepare


def lines_from_stats(stats: Dict[Tuple, Tuple]) -> List[str]:
    funcs, calls = calc_callers(stats)
    blocks = prepare(funcs, calls)
    result = []
    for b in blocks:
        trace = []
        for t in b['trace']:
            # file, function, line number
            filename, lineno, function = t
            if function.startswith("<") and lineno == 0:
                trace.append(function)
            else:
                trace.append('{}:{}:{}'.format(filename, function, lineno))
        stack = ';'.join(trace)
        measurement = round(b['ww'] * 1000000)
        result.append(f"{stack} {measurement}")
    return result
