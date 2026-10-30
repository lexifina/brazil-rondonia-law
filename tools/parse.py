"""Builds corpus.d/10-constituicao.json for Rondônia from the cached Assembleia Legislativa PDF (no network).

    python -X utf8 parse.py

The Assembleia Legislativa publishes the Constituição do Estado de Rondônia only as a compiled PDF ("texto atualizado
até a Emenda Constitucional nº 179/2026"). rdread.py reads the text in force from it: crossed-out text (vector
strike-through lines), earlier wordings and court-decision notes (dark-blue or green italic) and the publisher's
alteration notes (blue) are left out. consistency.py must find no repeated or backward article, §, inciso or alínea
number, or the article is left out. The text in force is given as one version, credited to the publisher, dated by
the latest date the alteration notes cite.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rdread  # noqa: E402
import consistency  # noqa: E402
from br_lib import units_of, write_part, sha, dates_in  # noqa: E402

URL = 'https://www.al.ro.leg.br/downloads/constituicao-do-estado-de-rondonia'
SITE = 'https://www.al.ro.leg.br'
RETRIEVED = '2026-10-30'
PDF = HERE / '.cache' / 'raw' / sha(URL.encode())
LICENCE = ('Text: Assembleia Legislativa do Estado de Rondônia, www.al.ro.leg.br. Lei 9.610/1998 art. 8 IV: the texts '
           'of laws and other official acts are not protected by copyright. Non-official text: only the Diário Oficial '
           'is authoritative.')
COUNTRY = {
    'code': 'BR-RO', 'name': 'Rondônia', 'slug': 'brazil-rondonia', 'lang': 'pt', 'tz': 'America/Porto_Velho',
    'future_branch': 'futuro',
    'publisher': {'name': 'Assembleia Legislativa do Estado de Rondônia (ALE/RO)', 'email': 'legislacao@al.ro.leg.br.invalid'},
    'default_in_force_rule': {
        'text': 'Decreto-Lei 4.657/1942 (LINDB) art. 1: unless it says otherwise, a law takes effect 45 days after its '
                'official publication. Constitutional amendments take effect on their publication; this record dates '
                'the compiled Constituição by the latest alteration its notes cite.',
        'source': 'https://www.planalto.gov.br/ccivil_03/decreto-lei/del4657compilado.htm'},
    'licence_note': LICENCE,
}
DECISIONS = [
    'The Constituição do Estado de Rondônia (promulgated 28 September 1989) is given only as its text in force, from '
    'the Assembleia Legislativa\'s compiled PDF ("texto atualizado até a Emenda Constitucional nº 179/2026"), '
    'credited to the publisher as the oldest version available and dated 17 June 2026, the latest date its alteration '
    'notes cite (EC nº 179, de 17/06/2026, DO-e-ALE nº 110 of the same day). The wordings in between are not '
    'reconstructed, so no earlier version is given rather than a wrong one.',
    'The compiled PDF marks what is no longer in force outside its text layer, and the text in force is read from those '
    'marks: text crossed out by strike-through lines (revoked, declared unconstitutional or suspended), earlier '
    'wordings ("Redação anterior: ...", "Dispositivo revogado: ...") and court-decision notes printed in dark-blue or '
    'green italic, the publisher\'s alteration notes printed in blue ("(NR dada pela EC nº ...)", "(Acrescido pela '
    '...)"), and provisions printed small and in colour without being in force are all left out; what is kept is the '
    'black text at body size (and the small capitals of headings). A provision left with only its number, or its '
    'number and a status word ("§ 1º REVOGADO", "Parágrafo único. (Inconstitucional)"), is left out. Wording restored '
    'by a court decision (efeito repristinatório) is printed in black and is kept.',
    'Check: within each article every § number, every inciso within its § and every alínea within its inciso must '
    'appear once and in increasing order, and article numbers must increase; an article that fails (a sign of an '
    'earlier wording the PDF did not mark) is left out.',
    'One file per Art. (articles of the Ato das Disposições Constitucionais Transitórias as adt-*); headings of the '
    'Títulos, Capítulos and Seções stand above the first article under them; "000-titulo" holds the title, the line '
    'naming the last amendment included and the preamble. The signatures of 1989 stay with the last transitional '
    'article. The text of Emenda Constitucional nº 146/2021 that the PDF reprints after the signatures is an amending '
    'act, not part of the Constituição, and is left out.',
]
AI = ["Claude Code (claude-opus-5-5) wrote Lexifina's code and chose the sources. No model output is used as legal "
      "text or dates: every word comes from the Assembleia Legislativa's PDF."]


def build():
    paras, removed = rdread.read(PDF, first_page=0)
    i = next(n for n, p in enumerate(paras) if p.startswith('Os Deputados Constituintes'))
    e = next(n for n, p in enumerate(paras) if p.startswith('Porto Velho, 28 de setembro de 1989'))
    removed += paras[:i] + paras[e + 1:]  # the cover's names and the reprinted EC 146/2021 (for the letters check)
    head = ['CONSTITUIÇÃO DO ESTADO DE RONDÔNIA', 'TEXTO ATUALIZADO ATÉ A EMENDA CONSTITUCIONAL N° 179/2026', 'PREÂMBULO']
    lines = [('p', h) for h in head] + [('p', p) for p in paras[i:e + 1]]
    units = units_of(lines)
    bad = consistency.check(units)
    for k in bad:
        del units[k]
    dates = sorted(d for x in removed for d in dates_in(x) if d <= RETRIEVED)
    return units, bad, removed, dates[-1]


def main():
    units, bad, removed, frm = build()
    assert frm == '2026-06-17', frm
    law = 'constituicao-1989'
    part = {
        'country': COUNTRY,
        'sources': [{'name': 'Assembleia Legislativa do Estado de Rondônia: Constituição do Estado (texto atualizado, PDF)',
                     'url': URL, 'retrieved': RETRIEVED, 'licence': LICENCE,
                     'notes': f'{len(units) - 1} articles; left out by the consistency check: {", ".join(bad) or "none"}.'}],
        'laws': {law: {'label': 'Constituição do Estado de Rondônia', 'title': 'Constituição do Estado de Rondônia',
                       'kind': 'law', 'enacted': '1989-09-28', 'published': None, 'url': URL,
                       'temporary_until': None, 'restores': None, 'note': None}},
        'acts': [{'slug': 'constituicao', 'short': 'CE-RO', 'title': 'Constituição do Estado de Rondônia', 'url': URL,
                  'first_law': None, 'earlier_laws': [law],
                  'versions': [{'from': frm, 'source_url': URL, 'sha256': sha(PDF.read_bytes()), 'units': units,
                                'note': 'Text in force as compiled by the Assembleia Legislativa (texto atualizado até a '
                                        'Emenda Constitucional nº 179/2026), dated by the latest alteration its notes '
                                        'cite. Earlier versions are not in the record.'}]}],
        'applies': [], 'decisions': DECISIONS, 'ai_use': AI,
    }
    write_part(HERE / 'corpus.d', '10-constituicao', part)
    print(len(units), 'units; left out:', bad)


if __name__ == '__main__':
    main()
