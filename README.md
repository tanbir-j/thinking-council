# Thinking Council

Thinking Council is an adaptive skill for reviewing, challenging, and helping to produce professional work: articles, white papers, consulting reports, board papers, business cases, client decks, models, and single paragraphs. It thinks freely first, then judges tightly.

Three chambers do the judging:

- **The Harness Team**, a five-part business-thinking chain covering strategic context, evidence, persuasion, people and practical delivery. It runs on every review.
- **A practitioner bench**, summoned when the work needs it: a strategy partner, an audit partner, a private equity operating partner, or the executive who will read the work.
- **The Council of Philosophers**, a selectively appointed bench used to compress, expand, reflect on or strengthen execution of the argument.

## Operating modes

| Mode | Job |
|---|---|
| Single counsel | One reviewer, one method |
| Open Field | Thinking partner before anything is written: angles, hypotheses, the best version of the eventual output |
| Close Read | One paragraph or block at a time. Is the thought complete, and can this reader follow it? |
| Council Glance | Quick diagnostic on a concept, outline, or thesis |
| Full Council | Developmental review of a draft, report, or model |
| Boardroom Rehearsal | The work is read by simulated named executives before the real ones see it |
| Final Gate | Readiness decision for publication or for a client. Also called Publication Tribunal |
| Drafting Room | Produces the deliverable, as a scaffold or a draft |

Every Council review ends with four things: a verdict, the findings, the strongest objection, and the next move. Everything else appears only when the work calls for it.

## Invocation

The Council runs on demand. It starts when you name it or ask for one of its modes by name, carries on through follow-ups about that review, and steps back when you change subject. "Review this email" does not summon it. "Thinking Council: review this email" does.

In products that read `agents/openai.yaml`, automatic triggering can be switched off altogether by adding `policy.allow_implicit_invocation: false`. The skill then has to be selected explicitly each time, so the setting is left off here.

## Close Read

Close Read rests on one finding: the largest gains in clarity come from fixing the thought before polishing the sentence. For each block it asks what job the block has, what it claims, why the claim holds, what follows, how a reader would check it, and which ideas it has merged. Voice comes last.

It works this way by design:

- **Diagnosis first.** Text is rewritten only on request, only for the block in hand.
- **Keep is the default.** Most paragraphs in a competent draft should be left alone.
- **The author owns every claim.** A missing link is a question for the author. Anything the reviewer contributes is marked as proposed.
- **Reclass or adjustment.** A change that leaves the claims intact is a reclass. A change that adds, removes, narrows, or strengthens a claim is an adjustment and is listed for approval.
- **Reconcile.** When the author rewrites a block in their own words, `scripts/integrity_check.py` compares it with the original and reports numbers, quotations, names, references, and sentences that were lost or added.
- **Cold-reader test.** A reader with no context restates the claim, the reason, and the consequence. A mismatch fails the edit.

Close Read is an editorial method. It makes no claim about who or what wrote a text and does not predict the result of any AI-detection tool.

## Layout

```
SKILL.md                     router: modes, chambers, workflow
references/
├── close-read.md            paragraph-level review
├── council-roster.md        seats, methods, guards
├── thinking-modes.md        compression, expansion, reflection, execution
├── article-profile.md       published work: gates, scorecard, verdicts
├── venue-profiles.md        word budgets and venue rules
├── deliverable-profiles.md  consultancy work, reports, models
├── executive-credibility.md how the work lands with senior executives
├── drafting-room.md         scaffolds, drafts, skeletons
├── output-formats.md        default shape of each mode
└── author-profile.md        template: fill in or override privately
scripts/
└── integrity_check.py       compares an original with a revision
evals/                       behaviour cases and trigger tests, all invented
```

## Your own profile

`references/author-profile.md` is a template. The council reads it to learn what you want to be known for, where you want to be pushed, how you write, and which venues you draft yourself.

To keep that private, put a filled copy at `references/private/author-profile.md`. The skill reads the private copy first, and `.gitignore` keeps the folder out of the repository.

## Checking a rewrite

```
python scripts/integrity_check.py --source original.txt --edit revised.txt
```

Standard library only. Add `--json` for the full report. The script flags candidates for a person to confirm and does not judge meaning.

## Current status

This is a public preview shared for evaluation and feedback.

The article workflow has had the most use. Close Read, the consultancy profiles, and the model profile are newer and have had less.

## Installation

Download the latest `skill.zip` file from the Releases section.

In ChatGPT, open the Skills area, select **Create**, then select **Upload from your computer** and upload the ZIP file.

Review externally sourced skills before installing them.

## Suggested test prompts

- Review this article concept using Council Glance.
- Run the Full Council on this first draft.
- Close Read: this paragraph is from the section on controls and the reader is a group CFO.
- Close Read, reconcile: here is my rewrite of that paragraph and the original.
- Thinking Council, Single counsel: review this proposal as a strategy partner.
- Run a Boardroom Rehearsal on this board paper with the CFO as the reader.
- Run a Final Gate and assess whether this qualifies as thought leadership.
- Thinking Council: tell me what must change before this article is worth putting my name on.

## Tests

Each folder under `evals/` holds a prompt, a description of a good result, and a set of single-statement graders. Every passage in them is invented. They test behaviour: diagnosing without rewriting, leaving a strong paragraph alone, protecting quotations and figures, catching lost material, refusing to invent facts, and staying out of an unrelated task.

`evals/trigger-eval.json` lists prompts that should and should not summon the Council. A skill that works well and turns up uninvited is still defective.

## Feedback requested

I am particularly interested in:

1. Whether the review identifies issues that a normal AI critique misses
2. Whether the Harness Team works as one coherent framework
3. Whether the selected philosophers add genuinely different perspectives
4. Whether the recommendations are specific enough to improve the work
5. Whether the scoring and verdicts feel credible
6. Where the review becomes repetitive, theatrical or unnecessarily complicated
7. Whether Close Read leaves strong paragraphs alone and asks before it assumes

## Sources

Three published frameworks are adapted and credited where they are used:

- the Four Modes framework by Tey Bannerman (thinking modes)
- the pyramid principle by Barbara Minto (strategy partner seat)
- the trust equation from *The Trusted Advisor* by Maister, Green, and Galford (executive credibility)

The Harness Team seats borrow the names of well-known fictional characters as shorthand for a method. This project is not affiliated with or endorsed by their rights holders.

## Licence

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

The licence covers the author's own work in this repository. The frameworks credited under Sources and the fictional character names belong to their respective owners.

## Author

Created by Tanbir Jasimuddin as part of a wider body of work on finance transformation, analytics, strategy, operations and practical uses of AI.
