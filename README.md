# Rondônia: law history in git

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is the law of Rondônia, Brazil, which global-law reads at `brazil/rondonia/acts/`.

The law of the State of Rondônia (Estado de Rondônia) (Brazil) as a git history: one file per Artigo, one paragraph per line, so `git blame`, `git log` and `git diff` work line by line. The text is Portuguese, the only official language.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

## What this repository holds

| Folder | Act | Versions |
| --- | --- | ---: |
| `constituicao/` | Constituição do Estado de Rondônia (28 September 1989), text in force as compiled up to Emenda Constitucional nº 179/2026 | 1 |

The Constituição is given **only as its text in force**, credited to the Assembleia Legislativa as the oldest version available: the wordings in between are not reconstructed yet, so no earlier version is shown rather than a wrong one. Leis Complementares, ordinary laws and the Emendas Constitucionais as acts are not included yet.

## Source

[Assembleia Legislativa do Estado de Rondônia](https://www.al.ro.leg.br), published by the Assembleia Legislativa do Estado de Rondônia. Each version names the page it was taken from and that page's sha256, in `data/versions.json`.

## Dates

The text in force is dated 17 June 2026, the latest date the compiled text's alteration notes cite (Emenda Constitucional nº 179, de 17/06/2026, published in the DO-e-ALE nº 110 the same day). Commits are at noon in Porto Velho.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

The Assembleia Legislativa publishes the Constituição only as a compiled PDF. The PDF marks what is no longer in force outside its text layer, and the text in force is read from those marks: text crossed out by strike-through lines (revoked, declared unconstitutional or suspended), earlier wordings ("Redação anterior: ...", "Dispositivo revogado: ...") and court-decision notes in dark-blue or green italic, and the publisher's blue alteration notes ("(NR dada pela EC nº ...)", "(Acrescido pela ...)") are left out; the black text at body size is kept. A provision left with only its number, or its number and a status word ("§ 1º REVOGADO"), is left out. Wording restored by a court decision (efeito repristinatório) is printed in black and is kept. Within each article every §, inciso and alínea number must appear once and in increasing order. One file per Art.; articles of the Ato das Disposições Constitucionais Transitórias are `adt-*`. Headings of the Títulos, Capítulos and Seções stand above the first article under them; `000-titulo.md` holds the title, the line naming the last amendment included, and the preamble.

## How it is checked

Every version is read back from git on the day it took effect (`tools/check_repo.py`) and must match the corpus; an independent letters-and-digits comparison of every version against the source page must show no difference. Results are in `REPRODUCE.md`.

## What "author" means

The author of each commit is the law that made the text, or, for a consolidated text, the publisher, with an e-mail address that cannot exist; the committer is always Lexifina.

## Limits

Not a complete history: the Constituição starts at its text in force. The text is not the official version: only the Diário Oficial is authoritative. The text in force is read from the PDF's strike-through lines and colours; the independent check (a second PDF reader, which sees neither) confirms every word of the record is in the PDF in order and everything passed over is text the reader left out, but it cannot confirm the strike-through itself. The signatures of 1989 stay with the last transitional article's file. The text of Emenda Constitucional nº 146/2021 that the PDF reprints after the signatures is an amending act and is left out.

## Licence

See [LICENSE](LICENSE): Brazilian law texts are not protected by copyright (Lei 9.610/1998, art. 8, IV). Fonte: Assembleia Legislativa do Estado de Rondônia, Assembleia Legislativa do Estado de Rondônia.
