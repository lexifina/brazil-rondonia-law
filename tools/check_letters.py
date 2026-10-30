"""Independent letters-and-digits check of the Rondônia part against the source PDF, read by a second engine (xpdf /
poppler pdftotext -raw, not pymupdf).

    python -X utf8 check_letters.py [corpus.d/10-constituicao.json]

Private. The sha256 of the cached PDF must equal the recorded one. Then the units, in order (heading marks "#" left
out), reduced to letters and digits, must be found in pdftotext's text of the whole PDF reduced the same way, with
nothing out of order. pdftotext sees neither strike-through lines nor colours, so its text also holds what rdread.py
left out (crossed-out text, earlier wordings, notes, the cover and the reprinted EC 146/2021). Source text between two
placed stretches of the record may be passed over only when it can be cut into stretches that each lie inside one
piece rdread.py recorded as left out (the engines cut rows at different places; a stretch under 4 letters must be a
whole piece or the start or end of one). Record text not found, or source text that is not left-out text, is a
mismatch; so is any source text after the last unit that is not left-out text.
"""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FF = '\x0c'


def ld(s):
    return ''.join(ch for ch in s if ch.isalnum())


def source(pdf):
    out = subprocess.run(['pdftotext', '-raw', '-enc', 'UTF-8', str(pdf), '-'], capture_output=True, check=True).stdout
    return ld(out.decode('utf-8'))


def main(part):
    import rdread  # noqa: E402  (the parser's own record of what it left out)
    import parse  # noqa: E402
    c = json.loads(Path(part).read_text(encoding='utf-8'))
    bad = 0
    for a in c['acts']:
        v = a['versions'][0]
        pdf = parse.PDF
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == v['sha256'], 'sha256 differs'
        S = source(pdf)
        _, _, removed, _ = parse.build()
        pool = collections.Counter(x for x in (ld(r) for r in removed) if x)
        units = [(k, ld(re.sub(r'(?m)^#+ ', '', u['text']))) for k, u in v['units'].items()]
        U = ''.join(t for _, t in units)
        # the first unit's start: its first 40 letters
        j = S.find(U[:40])
        if j < 0:
            print('FAIL first unit not found'); return 1
        pieces = sorted(pool, key=len, reverse=True)

        R = '\x00' + '\x00'.join(pieces) + '\x00'  # every left-out piece, kept apart

        def covered(gap):
            """Can gap be cut into stretches that each lie inside one left-out piece? (The two engines cut rows at
            different places, so a stretch may be part of a piece; a stretch shorter than 4 letters must be a whole
            piece, or the very start or end of one.) -> Counter (of stretches) or None."""
            use, k = collections.Counter(), 0
            while k < len(gap):
                lo, hi = 0, len(gap) - k  # longest prefix of gap[k:] inside a piece
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if gap[k:k + mid] in R:
                        lo = mid
                    else:
                        hi = mid - 1
                while lo >= 4 or (lo and not ('\x00' + gap[k:k + lo] in R or gap[k:k + lo] + '\x00' in R)):
                    if lo >= 4:
                        break
                    lo -= 1  # a short stretch must be a whole piece, or the start or end of one
                if lo == 0:
                    return None
                s = gap[k:k + lo]
                use[s] += 1
                k += lo
            return use

        def place(seg, j, tries=6):
            """First position >= j where seg occurs and the source before it is all left-out text."""
            pos = S.find(seg, j)
            while pos >= 0 and tries:
                use = covered(S[j:pos])
                if use is not None:
                    return pos, use
                pos = S.find(seg, pos + 1)
                tries -= 1
            return None, None

        lines = [ld(l) for k, u in v['units'].items() for l in re.sub(r'(?m)^#+ ', '', u['text']).splitlines()]
        lines = [l for l in lines if l]
        gaps, used_total, split = 0, 0, 0
        for n, L in enumerate(lines):
            pos, use = place(L, j)
            if pos is not None:
                used_total += sum(len(x) * n for x, n in use.items()); gaps += bool(use)
                j = pos + len(L)
                continue
            # the line is broken in the source by left-out text (a crossed-out word inside it): place it piece by piece
            split += 1
            k = 0
            while k < len(L):
                seg = L[k:k + 12]
                pos, use = place(seg, j)
                if pos is None:
                    print('FAIL record text not placed:', L[max(0, k - 30):k], '|', L[k:k + 80], '| source:', S[j:j + 100])
                    q = S.find(seg, j)
                    if q >= 0:  # where the source before its next occurrence stops being left-out text
                        g = S[j:q]
                        for cut in range(len(g), 0, -1):
                            if covered(g[:cut]) is not None:
                                print('   left-out text ends at', cut, 'of', len(g), ':', g[max(0, cut - 60):cut], '||', g[cut:cut + 80])
                                break
                        else:
                            print('   gap starts unexplained:', g[:120])
                    bad += 1
                    break
                used_total += sum(len(x) * n for x, n in use.items()); gaps += bool(use)
                j = pos
                while k < len(L) and j < len(S) and S[j] == L[k]:
                    k += 1; j += 1
            if bad:
                break
        U = ''.join(lines)
        tail = S[j:]
        use = covered(tail)
        ok_tail = use is not None
        tail_n = sum(len(x) * n for x, n in use.items()) if ok_tail else 0
        removed_n = sum(len(x) * n for x, n in pool.items())
        print(f'{a["slug"]}: {len(lines)} lines, {len(U)} letters/digits matched in order ({split} lines broken by '
              f'left-out text); {gaps} gaps of left-out text; letters passed over as left-out text: {used_total} in gaps + {tail_n} after the last '
              f'unit, of {removed_n} the parser left out (the rest is the cover, before the first unit); tail explained: {ok_tail}')
        if not ok_tail:
            print('   unexplained tail:', tail[:300]); bad += 1
    print('mismatches:', bad)
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / 'corpus.d' / '10-constituicao.json')) else 0)
