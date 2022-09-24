# Adapted from https://github.com/baverman/flameprof/blob/master/flameprof.py

# MIT License
#
# Copyright (c) 2017 Anton Bobrov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import Counter
from typing import Dict, Tuple

def calc_callers(stats: Dict[Tuple, Tuple]):
    roots = set()
    funcs = {}
    calls = {}
    for func, (cc, nc, tt, ct, clist) in stats.items():
        funcs[func] = {'calls': [], 'called': [], 'stat': (cc, nc, tt, ct)}
        if not clist:
            roots.add(func)
            calls[('root', func)] = funcs[func]['stat']

    for func, (_, _, _, _, clist) in stats.items():
        for cfunc, t in clist.items():
            assert (cfunc, func) not in calls
            funcs[cfunc]['calls'].append(func)
            funcs[func]['called'].append(cfunc)
            calls[(cfunc, func)] = t

    total = sum(funcs[r]['stat'][3] for r in roots)
    ttotal = sum(funcs[r]['stat'][2] for r in funcs)

    if not (0.8 < total / ttotal < 1.2):
        print('Warning: flameprof can\'t find proper roots, root cumtime is {} but sum tottime is {}'.format(total, ttotal))

    # Try to find suitable root
    newroot = max((r for r in funcs if r not in roots), key=lambda r: funcs[r]['stat'][3])
    nstat = funcs[newroot]['stat']
    ntotal = total + nstat[3]
    if 0.8 < ntotal / ttotal < 1.2:
        roots.add(newroot)
        calls[('root', newroot)] = nstat
        total = ntotal
    else:
        total = ttotal

    funcs['root'] = {'calls': roots,
                     'called': [],
                     'stat': (1, 1, 0, total)}

    return funcs, calls


def prepare(funcs: Dict[Tuple, Dict], calls: Dict[Tuple, Tuple], threshold: float=0.0001):
    blocks = []
    block_counts = Counter()

    def _counts(parent, visited, level=0):
        for child in funcs[parent]['calls']:
            k = parent, child
            block_counts[k] += 1
            if block_counts[k] < 2:
                if k not in visited:
                    _counts(child, visited | {k}, level+1)

    def _calc(parent, timings, level, origin, visited, trace=(), pccnt=1, pblock=None):
        childs = funcs[parent]['calls']
        _, _, ptt, ptc = timings
        fchilds = sorted(((f, funcs[f], calls[(parent, f)], max(block_counts[(parent, f)], pccnt))
                          for f in childs),
                         key=lambda r: r[0])

        gchilds = [r for r in fchilds if r[3] == 1]

        bchilds = [r for r in fchilds if r[3] > 1]
        if bchilds:
            gctc = sum(r[2][3] for r in gchilds)
            bctc = sum(r[2][3] for r in bchilds)
            rest = ptc-ptt-gctc
            if bctc > 0:
                factor = rest / bctc
            else:
                factor = 1
            bchilds = [(f, ff, (round(cc*factor), round(nc*factor), tt*factor, tc*factor), ccnt)
                       for f, ff, (cc, nc, tt, tc), ccnt in bchilds]

        for child, _, (cc, nc, tt, tc), ccnt in gchilds + bchilds:
            if tc/maxw > threshold:
                ckey = parent, child
                ctrace = trace + (child,)
                block = {
                    'trace': ctrace,
                    'ww': tt,
                }
                blocks.append(block)
                if ckey not in visited:
                    _calc(child, (cc, nc, tt, tc), level + 1, origin, visited | {ckey},
                          ctrace, ccnt, block)
            elif pblock:
                pblock['ww'] += tc

            origin += tc

    maxw = funcs['root']['stat'][3] * 1.0
    _counts('root', set())
    _calc('root', (1, 1, maxw, maxw), 0, 0, set())

    return blocks
