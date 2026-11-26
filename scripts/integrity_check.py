#!/usr/bin/env python3
"""Compare an original block of text with a revised version.

Reports what a revision lost or gained, so that a rewrite can be reconciled
with its source before anyone judges the prose:

  * numbers, quotations, names and references that disappeared or appeared
  * source sentences with no counterpart in the revision
  * revision sentences with no counterpart in the source (possible new claims)
  * the net change in word count

It flags candidates for a human to confirm. It does not judge meaning.

Usage:
    python integrity_check.py --source original.txt --edit revised.txt
    python integrity_check.py --source original.txt --edit revised.txt --json

Standard library only.
"""
import argparse
import difflib
import json
import re
import sys

STOPWORDS = set(
    """a about above after again all also am an and any are as at be because been
    before being below between both but by can could did do does doing down during
    each few for from further had has have having he her here hers him his how i if
    in into is it its itself just may me might more most must my no nor not now of
    off on once only or other our ours out over own same she should so some such
    than that the their theirs them then there these they this those through to too
    under until up very was we were what when where which while who whom why will
    with would you your yours""".split()
)

NUMBER = re.compile(r"(?<![A-Za-z])[£$€]?\d[\d,]*(?:\.\d+)?%?")
QUOTE = re.compile(r"[\"“]([^\"“”]{3,}?)[\"”]")
URL = re.compile(r"https?://[^\s)\]>]+")
BRACKET_REF = re.compile(r"\[\d+(?:[,–-]\s*\d+)*\]")
AUTHOR_YEAR = re.compile(r"\([A-Z][A-Za-z'-]+(?:\s+(?:et al\.|and|&)\s*[A-Za-z'-]*)?,?\s+\d{4}[a-z]?\)")
CAP_SEQ = re.compile(r"\b[A-Z][A-Za-z0-9&'-]*(?:\s+(?:of|the|and|for|&)?\s*[A-Z][A-Za-z0-9&'-]*)*")
SENT_SPLIT = re.compile(r"(?<=[.!?])[\"”')\]]*\s+(?=[\"“'(\[]*[A-Z0-9])|\n{2,}")


def sentences(text):
    parts = [p.strip() for p in SENT_SPLIT.split(text) if p and p.strip()]
    return [re.sub(r"\s+", " ", p) for p in parts]


def words(text):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text.lower())


def content_words(text):
    return {w for w in words(text) if len(w) > 3 and w not in STOPWORDS}


def numbers(text):
    return {m.group(0).replace(",", "").rstrip(".") for m in NUMBER.finditer(text)}


def quotations(text):
    return {re.sub(r"\s+", " ", m.group(1)).strip() for m in QUOTE.finditer(text)}


def references(text):
    found = set(URL.findall(text))
    found |= set(BRACKET_REF.findall(text))
    found |= set(AUTHOR_YEAR.findall(text))
    return found


def names(text):
    """Capitalised terms, ignoring a word that is capitalised only because it opens a sentence."""
    connectors = {"of", "the", "and", "for", "&"}
    found = set()
    for sent in sentences(text):
        lead = re.match(r"[^A-Za-z0-9]*", sent).end()
        for m in CAP_SEQ.finditer(sent):
            tokens = m.group(0).split()
            if m.start() <= lead and tokens and not tokens[0].isupper():
                tokens = tokens[1:]
            while tokens and tokens[0].lower() in connectors:
                tokens = tokens[1:]
            while tokens and tokens[-1].lower() in connectors:
                tokens = tokens[:-1]
            if not tokens:
                continue
            term = " ".join(tokens)
            if len(tokens) == 1 and term.lower() in STOPWORDS:
                continue
            found.add(term)
    return found


def best_match(sentence, candidates):
    a = words(sentence)
    best = 0.0
    for cand in candidates:
        ratio = difflib.SequenceMatcher(None, a, words(cand)).ratio()
        if ratio > best:
            best = ratio
    return best


def coverage(sentence, other_text_words):
    cw = content_words(sentence)
    if not cw:
        return 1.0
    return len(cw & other_text_words) / len(cw)


def classify(src_sents, edit_sents, edit_text):
    edit_cw = content_words(edit_text)
    rows = []
    for s in src_sents:
        ratio = best_match(s, edit_sents)
        cov = coverage(s, edit_cw)
        if ratio >= 0.9:
            status = "kept"
        elif ratio >= 0.55:
            status = "changed"
        elif cov >= 0.6:
            status = "reworded or merged"
        else:
            status = "no counterpart"
        rows.append({"sentence": s, "status": status,
                     "similarity": round(ratio, 2), "coverage": round(cov, 2)})
    return rows


def new_material(src_text, edit_sents, src_sents):
    src_cw = content_words(src_text)
    rows = []
    for s in edit_sents:
        if best_match(s, src_sents) >= 0.55:
            continue
        cov = coverage(s, src_cw)
        if cov < 0.5:
            rows.append({"sentence": s, "coverage": round(cov, 2)})
    return rows


def compare(source, edit):
    src_sents, edit_sents = sentences(source), sentences(edit)
    report = {
        "words": {"source": len(words(source)), "edit": len(words(edit)),
                  "net": len(words(edit)) - len(words(source))},
        "numbers": {"missing": sorted(numbers(source) - numbers(edit)),
                    "new": sorted(numbers(edit) - numbers(source))},
        "quotations": {"missing": sorted(quotations(source) - quotations(edit)),
                       "new": sorted(quotations(edit) - quotations(source))},
        "names": {"missing": sorted(names(source) - names(edit)),
                  "new": sorted(names(edit) - names(source))},
        "references": {"missing": sorted(references(source) - references(edit)),
                       "new": sorted(references(edit) - references(source))},
        "source_sentences": classify(src_sents, edit_sents, edit),
        "new_material": new_material(source, edit_sents, src_sents),
    }
    flags = sum(len(report[k]["missing"]) + len(report[k]["new"])
                for k in ("numbers", "quotations", "names", "references"))
    flags += sum(1 for r in report["source_sentences"] if r["status"] == "no counterpart")
    flags += len(report["new_material"])
    report["flags"] = flags
    return report


def render(report):
    out = []
    w = report["words"]
    out.append(f"Words: {w['source']} -> {w['edit']} (net {w['net']:+d})")
    for key, label in (("numbers", "Numbers"), ("quotations", "Quotations"),
                       ("names", "Names and capitalised terms"), ("references", "References")):
        missing, new = report[key]["missing"], report[key]["new"]
        if missing:
            out.append(f"{label} in the source but not the revision: " + "; ".join(missing))
        if new:
            out.append(f"{label} in the revision but not the source: " + "; ".join(new))
        if not missing and not new:
            out.append(f"{label}: no change")
    counts = {}
    for r in report["source_sentences"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in counts.items()) or "none"
    out.append(f"Source sentences: {summary}")
    lost = [r for r in report["source_sentences"] if r["status"] == "no counterpart"]
    if lost:
        out.append("Source sentences with no counterpart (confirm each was cut on purpose):")
        out.extend(f"  - {r['sentence']}" for r in lost)
    if report["new_material"]:
        out.append("Revision sentences with little basis in the source (check for new claims):")
        out.extend(f"  - {r['sentence']}" for r in report["new_material"])
    out.append(f"Items to confirm: {report['flags']}")
    out.append("This check flags candidates. It does not judge meaning.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", required=True, help="file holding the original text")
    ap.add_argument("--edit", required=True, help="file holding the revised text")
    ap.add_argument("--json", action="store_true", help="print the full report as JSON")
    args = ap.parse_args()
    with open(args.source, encoding="utf-8") as f:
        source = f.read()
    with open(args.edit, encoding="utf-8") as f:
        edit = f.read()
    report = compare(source, edit)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
