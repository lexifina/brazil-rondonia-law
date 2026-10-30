"""Consistency test of the text in force read by rdread.py (private): within each article, every § number, every
inciso within its § (or the caput) and every alínea within its inciso appears once and in increasing order; article
numbers increase. A duplicate or a step back means an earlier wording the PDF did not mark.

    python -X utf8 consistency.py
"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rdread  # noqa: E402
from br_lib import units_of  # noqa: E402

PDF = HERE / '.cache' / 'raw' / '3074853852e970aec17301cc80f68d971d13aba9d70d9af544250b650035a7f9'
ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}


def roman(s):
    n = 0
    for a, b in zip(s, s[1:] + ' '):
        v = ROMAN[a]
        n += -v if b != ' ' and ROMAN.get(b, 0) > v else v
    return n


def check(units):
    bad = {}
    for k, u in units.items():
        if not k.startswith(('art-', 'adt-')):
            continue
        if '-dup' in k:
            bad[k] = 'article number repeated'
            continue
        par, inc, ali = (0, ''), 0, ''
        seen = set()
        for l in u['text'].splitlines():
            if l.startswith('#'):
                continue
            m = re.match(r'^§\s*(\d+)[º°o]?(?:\s*-\s*([A-Z]))?|^(Parágrafo único)', l)
            if m:
                cur = (int(m.group(1)), m.group(2) or '') if m.group(1) else (1, 'unico')
                if cur <= par:
                    bad[k] = f'§ {cur} after § {par}: {l[:60]}'
                par, inc, ali = cur, 0, ''
                continue
            m = re.match(r'^([IVXLC]+)(?:\s*-\s*([A-Z]))?\s*[-–]\s', l)
            if m:
                cur = (roman(m.group(1)), m.group(2) or '')
                if cur <= (inc if isinstance(inc, tuple) else (inc, '')):
                    bad[k] = f'inciso {m.group(1)} after {inc} in § {par}: {l[:60]}'
                inc, ali = cur, ''
                continue
            m = re.match(r'^([a-z])(?:-([A-Z]))?\)\s', l)
            if m:
                cur = m.group(1) + (m.group(2) or '')
                if ali and cur <= ali:
                    bad[k] = f'alínea {cur} after {ali}: {l[:60]}'
                ali = cur
    return bad


def main():
    paras, removed = rdread.read(PDF)
    units = units_of([('p', p) for p in paras])
    bad = check(units)
    for k, v in bad.items():
        print(k, '|', v)
    print(len([k for k in units if k.startswith(('art-', 'adt-'))]), 'articles,', len(bad), 'inconsistent')
    return bad


if __name__ == '__main__':
    main()
