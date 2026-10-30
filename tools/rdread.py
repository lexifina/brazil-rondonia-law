"""Rondônia Constituição (Assembleia Legislativa, "texto atualizado") PDF -> paragraphs of the text in force. Private.

The compiled PDF prints the text in force in black at body size (10 pt; a few provisions at 9 pt). It marks everything
else in a way the text layer alone does not show:
- revoked, unconstitutional or suspended text is crossed out by vector strike-through lines (page drawings under
  1.5 pt high across the middle of the text), usually grey, sometimes black or coloured;
- earlier wordings ("Redação anterior: ...", "Dispositivo revogado: ...") and court-decision notes are dark-blue
  (#215868) or green italic, mostly at 8 pt;
- the publisher's alteration notes ("(NR dada pela EC nº ...)", "(Acrescido pela ...)") are blue, at 8 pt.
So a character is kept when no strike line crosses it, its colour is black (or the near-black #6e6964 of one
provision) and it is at least 8.5 pt; the 8 pt black capitals of small-caps headings ("SEÇÃO") are kept on a heading
row. Characters are grouped into rows by baseline and read left to right. A paragraph that is left with only its
number ("Art. 148-B.", "I -", "§ 3º"), or its number and a status word ("§ 1º REVOGADO", "Parágrafo único.
(Inconstitucional)"), is the number of a crossed-out or revoked provision and is left out too.
"""
import re
import unicodedata

import pymupdf

KEEP_COLORS = {0x000000, 0x6e6964}
ENUM_ONLY = re.compile(r'^(?:Art\.?\s*\d+[º°o]?(?:\s*-\s*[A-Z])?\.?|§\s*\d+[º°o]?\.?|Parágrafo único\.?|[IVXLC]+\s*[-–]|'
                       r'[a-z]\))[\s\W]*$')
STATUS = re.compile(r'^\(?\s*(?:revogad|inconstitucional|suprimid|vetad|exclu[íi]d)\w*\b[^()]*\)?[\s.;]*$', re.I)
ENUM = re.compile(r'^(?:Art\.?\s*\d|§\s*\d|Parágrafo único|[IVXLC]+\s*[-–]\s|[a-z]\)\s)')


def norm(s):
    s = unicodedata.normalize('NFC', s.replace('\xa0', ' ').replace('­', ''))
    return re.sub(r'\s+', ' ', s).strip()


def strikes(page):
    return [d['rect'] for d in page.get_drawings() if d['rect'].height < 1.5 and d['rect'].width > 2]


def page_rows(page):
    st = strikes(page)
    chars = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                for c in s['chars']:
                    bb = pymupdf.Rect(c['bbox'])
                    cx = (bb.x0 + bb.x1) / 2
                    h = bb.y1 - bb.y0
                    struck = any(r.x0 <= cx <= r.x1 and bb.y0 + 0.25 * h < (r.y0 + r.y1) / 2 < bb.y1 - 0.12 * h
                                 for r in st)
                    chars.append({'c': c['c'], 'x': bb.x0, 'y': round(c['origin'][1], 1), 'size': s['size'],
                                  'color': s['color'], 'italic': bool(s['flags'] & 2), 'struck': struck})
    chars.sort(key=lambda c: (c['y'], c['x']))
    rows = []
    for c in chars:
        if rows and abs(rows[-1][-1]['y'] - c['y']) < 2.5:
            rows[-1].append(c)
        else:
            rows.append([c])
    out = []
    for r in rows:
        r.sort(key=lambda c: c['x'])
        keep = [not c['struck'] and c['color'] in KEEP_COLORS and c['size'] >= 8.5 for c in r]
        big = ''.join(c['c'] for c, k in zip(r, keep) if k)
        if big.strip() and not re.search(r'[a-zà-ÿ]', big):  # a heading row: small-caps letters stay with it
            keep = [k or (not c['struck'] and c['color'] == 0 and c['size'] >= 7.5) for c, k in zip(r, keep)]
        kept = norm(''.join(c['c'] for c, k in zip(r, keep) if k))
        removed, run = [], ''
        for c, k in zip(r, keep):  # each stretch left out, as one piece
            if k:
                if norm(run):
                    removed.append(norm(run))
                run = ''
            else:
                run += c['c']
        if norm(run):
            removed.append(norm(run))
        x = next((c['x'] for c in r if c['c'].strip()), None)  # where the printed row starts
        out.append({'kept': kept, 'removed': removed, 'x': x, 'y': r[0]['y']})
    return out


def read(path, first_page=1):
    """-> (paras, removed): paras = list of paragraph strings in reading order; removed = list of the strings left
    out (row remnants and enumerator-only paragraphs), in reading order."""
    d = pymupdf.open(path)
    paras, removed, cur, gap = [], [], None, True
    for pno in range(first_page, d.page_count):
        for row in page_rows(d[pno]):
            removed.extend(row['removed'])
            t = row['kept']
            if not t or not re.search(r'\w', t):
                if t:
                    removed.append(t)
                if not t and row['removed']:
                    gap = True
                continue
            heading = not re.search(r'[a-zà-ÿ]', t) and len(t) < 120 and (row['x'] or 0) > 100  # centred
            new = (cur is None or gap or heading or (row['x'] or 0) > 62 or bool(ENUM.match(t))
                   or cur['heading'])
            if new:
                cur = {'text': t, 'heading': heading}
                paras.append(cur)
            else:
                cur['text'] += ('' if t[0] in ',.;:)' else ' ') + t  # no space before punctuation at a row join
            gap = False
    for i in range(len(paras) - 1, 0, -1):  # a heading printed on two rows ('DAS DISPOSIÇÕES CONSTITUCIONAIS' / 'TRANSITÓRIAS')
        if paras[i]['heading'] and paras[i]['text'].strip() in ('TRANSITÓRIAS', 'TRANSITORIAS') and paras[i - 1]['heading']:
            paras[i - 1]['text'] += ' ' + paras[i]['text']
            del paras[i]
    out = []
    for p in paras:
        t = norm(p['text'])
        m = re.match(r'^(?:Art\.?\s*\d+[º°o]?(?:\s*-\s*[A-Z])?\.?|§\s*\d+[º°o]?\.?|Parágrafo único\.?|[IVXLC]+\s*[-–]|[a-z]\))\s*', t)
        if ENUM_ONLY.match(t) or (m and STATUS.match(t[m.end():])):
            removed.append(t)
            continue
        out.append(t)
    return out, removed
