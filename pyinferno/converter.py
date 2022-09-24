import pstats
from collections import Counter
from typing import Dict, Iterator, Tuple

# c called by b
#                                              cc, nc, tt,     ct,       clist
# ('/home/mike/profiling/test_cp.py', 6, 'c'): (1, 1, 6.8e-06, 0.500561, {('/home/mike/profiling/test_cp.py', 9, 'b'): (1, 1, 6.8e-06, 0.500561)})

def calc_callers(stats):
    roots = []
    funcs = {}
    calls = {}
    for func, (cc, nc, tt, ct, clist) in stats.items():
        funcs[func] = {'calls': [], 'called': [], 'stat': (cc, nc, tt, ct)}
        if not clist:
            roots.append(func)
            calls[('root', func)] = funcs[func]['stat']

    breakpoint()

    for func, (_, _, _, _, clist) in stats.items():
        for cfunc, t in clist.items():
            assert (cfunc, func) not in calls
            funcs[cfunc]['calls'].append(func)
            funcs[func]['called'].append(cfunc)
            calls[(cfunc, func)] = t

    breakpoint()

    total = sum(funcs[r]['stat'][3] for r in roots)
    ttotal = sum(funcs[r]['stat'][2] for r in funcs)

    if not (0.8 < total / ttotal < 1.2):
        print('Warning: flameprof can\'t find proper roots, root cumtime is {} but sum tottime is {}'.format(total, ttotal))

    # Try to find suitable root
    newroot = max((r for r in funcs if r not in roots), key=lambda r: funcs[r]['stat'][3])
    nstat = funcs[newroot]['stat']
    ntotal = total + nstat[3]
    if 0.8 < ntotal / ttotal < 1.2:
        roots.append(newroot)
        calls[('root', newroot)] = nstat
        total = ntotal
    else:
        total = ttotal

    funcs['root'] = {'calls': roots,
                     'called': [],
                     'stat': (1, 1, 0, total)}

    return funcs, calls


def prepare(funcs, calls, threshold=0.0001):
    blocks = []
    bblocks = []
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
                    'color': (pccnt==1 and ccnt > 1),
                    'level': level,
                    'name': child[2],
                    'hash_name': '{0[0]}:{0[1]}:{0[2]}'.format(child),
                    'full_name': '{0[0]}:{0[1]}:{0[2]} {5:.2%} ({1} {2} {3} {4})'.format(child, cc, nc, tt, tc, tc/maxw),
                    'w': tc,
                    'ww': tt,
                    'x': origin
                }
                blocks.append(block)
                if ckey not in visited:
                    _calc(child, (cc, nc, tt, tc), level + 1, origin, visited | {ckey},
                          ctrace, ccnt, block)
            elif pblock:
                pblock['ww'] += tc

            origin += tc

    def _calc_back(names, level, to, origin, visited, pw):
        if to and names:
            factor = pw / sum(calls[(r, to)][3] for r in names)
        else:
            factor = 1

        for name in sorted(names):
            func = funcs[name]
            if to:
                cc, nc, tt, tc = calls[(name, to)]
                ttt = tc * factor
            else:
                cc, nc, tt, tc = func['stat']
                ttt = tt * factor

            if ttt / maxw > threshold:
                block = {
                    'color': 2 if level > 0 else not func['calls'],
                    'level': level,
                    'name': name[2],
                    'hash_name': '{0[0]}:{0[1]}:{0[2]}'.format(name),
                    'full_name': '{0[0]}:{0[1]}:{0[2]} {5:.2%} ({1} {2} {3} {4})'.format(name, cc, nc, tt, tc, tt/maxw),
                    'w': ttt,
                    'x': origin
                }
                bblocks.append(block)
                key = name, to
                if key not in visited:
                    _calc_back(func['called'], level+1, name, origin, visited | {key}, ttt)

            origin += ttt

    maxw = funcs['root']['stat'][3] * 1.0
    _counts('root', set())
    _calc('root', (1, 1, maxw, maxw), 0, 0, set())
    _calc_back((f for f in funcs if f != 'root'), 0, None, 0, set(), 0)

    return blocks, bblocks, maxw


def lines_from_stats(stats: Dict[Tuple, Tuple]) -> Iterator[str]:
    funcs, calls = calc_callers(stats)
    blocks, bblocks, maxw = prepare(funcs, calls, threshold=0.001)
    for b in blocks:
        trace = []
        for t in b['trace']:
            # file, function, line number
            trace.append('{}:{}:{}'.format(t[0], t[2], t[1]))

        stack = ';'.join(trace)
        measurement = round(b['ww'] * 1000000)
        yield f"{stack} {measurement}"
