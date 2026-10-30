# How this repository was made (Rondônia)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Assembleia Legislativa do Estado de Rondônia: Constituição do Estado (texto atualizado, PDF) | <https://www.al.ro.leg.br/downloads/constituicao-do-estado-de-rondonia> | 2026-10-30 | Text: Assembleia Legislativa do Estado de Rondônia, www.al.ro.leg.br. Lei 9.610/1998 art. 8 IV: the texts of laws and other official acts are not protected by copyright. Non-official text: only the Diário Oficial is authoritative. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constituicao` | Constituição do Estado de Rondônia | 1 | 2026-06-17 to 2026-06-17 |

The build made 1 commits:

| Commits | Kind |
| ---: | --- |
| 1 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futuro`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 1 laws in the record.
- 1 tags.

## Dates

Each commit is dated at noon (America/Porto_Velho) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Decreto-Lei 4.657/1942 (LINDB) art. 1: unless it says otherwise, a law takes effect 45 days after its official publication. Constitutional amendments take effect on their publication; this record dates the compiled Constituição by the latest alteration its notes cite. https://www.planalto.gov.br/ccivil_03/decreto-lei/del4657compilado.htm

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `da3881c45b458ba823b80e7c42a4a4cc9375cbd664bfb5b2177e2d40533b5856` (280875 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

1 versions of 1 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- The Constituição do Estado de Rondônia (promulgated 28 September 1989) is given only as its text in force, from the Assembleia Legislativa's compiled PDF ("texto atualizado até a Emenda Constitucional nº 179/2026"), credited to the publisher as the oldest version available and dated 17 June 2026, the latest date its alteration notes cite (EC nº 179, de 17/06/2026, DO-e-ALE nº 110 of the same day). The wordings in between are not reconstructed, so no earlier version is given rather than a wrong one.
- The compiled PDF marks what is no longer in force outside its text layer, and the text in force is read from those marks: text crossed out by strike-through lines (revoked, declared unconstitutional or suspended), earlier wordings ("Redação anterior: ...", "Dispositivo revogado: ...") and court-decision notes printed in dark-blue or green italic, the publisher's alteration notes printed in blue ("(NR dada pela EC nº ...)", "(Acrescido pela ...)"), and provisions printed small and in colour without being in force are all left out; what is kept is the black text at body size (and the small capitals of headings). A provision left with only its number, or its number and a status word ("§ 1º REVOGADO", "Parágrafo único. (Inconstitucional)"), is left out. Wording restored by a court decision (efeito repristinatório) is printed in black and is kept.
- Check: within each article every § number, every inciso within its § and every alínea within its inciso must appear once and in increasing order, and article numbers must increase; an article that fails (a sign of an earlier wording the PDF did not mark) is left out.
- One file per Art. (articles of the Ato das Disposições Constitucionais Transitórias as adt-*); headings of the Títulos, Capítulos and Seções stand above the first article under them; "000-titulo" holds the title, the line naming the last amendment included and the preamble. The signatures of 1989 stay with the last transitional article. The text of Emenda Constitucional nº 146/2021 that the PDF reprints after the signatures is an amending act, not part of the Constituição, and is left out.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (claude-opus-5-5) wrote Lexifina's code and chose the sources. No model output is used as legal text or dates: every word comes from the Assembleia Legislativa's PDF.
