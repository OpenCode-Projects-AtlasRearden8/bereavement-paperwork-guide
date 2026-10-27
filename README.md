# Bereavement Paperwork Guide

A warm, plain-English, education-only manual for the paperwork that follows a
death: the first-week checklist, who to call and in what order, what to keep
copies of for good, the accounts and subscriptions to close, mail and benefits
basics, red flags for predatory "help," and a gentle self-pacing structure for
the shock-brain weeks. It comes with a printable call-log worksheet, a binder
checklist, and a glossary that translates the vocabulary before you have to
use it on the phone.

Everything here is **local-first**: plain Markdown documents plus a tiny
build script that turns them into a small static HTML site on your own
machine. No accounts, no cloud, no tracking. Print it, put it in a binder,
pencil in the blanks as you go.
Examples use U.S. agencies (the shapes are similar elsewhere, but names and
timelines differ).

## Who it's for

The person standing in the aisle of a house trying to remember which papers
come first — usually a spouse, an adult child, or the sibling everyone calls.
Written like a friend would explain it: step by step, never condescending,
and never rushed.

## What's inside

| Doc | What it covers |
| --- | --- |
| [docs/index.md](docs/index.md) | Start here — how to use the guide, what it is and isn't |
| [docs/01-first-week.md](docs/01-first-week.md) | The first-week checklist, gently |
| [docs/02-who-to-call.md](docs/02-who-to-call.md) | Who to call, in what order — with phone scripts |
| [docs/03-what-to-keep.md](docs/03-what-to-keep.md) | The "forever file": copies worth keeping long-term |
| [docs/04-accounts-and-subscriptions.md](docs/04-accounts-and-subscriptions.md) | Closing accounts, subscriptions, autopay |
| [docs/05-mail-and-benefits.md](docs/05-mail-and-benefits.md) | Mail handling, forwarding, and benefits basics |
| [docs/06-predatory-help-red-flags.md](docs/06-predatory-help-red-flags.md) | Scams and predatory "help" — patterns and defenses |
| [docs/07-self-pacing.md](docs/07-self-pacing.md) | Self-pacing for shock-brain — gentle structure |
| [docs/08-call-log.md](docs/08-call-log.md) | Printable call-log worksheet |
| [docs/09-binder-checklist.md](docs/09-binder-checklist.md) | The paperwork binder, one evening to assemble |
| [docs/10-glossary.md](docs/10-glossary.md) | Glossary in plain English |

Worksheets that are fillable on your own machine:

| File | What it is |
| --- | --- |
| [worksheets/call-log.csv](worksheets/call-log.csv) | Every call, tracked: who, ref number, next step |
| [worksheets/subscriptions-tracker.csv](worksheets/subscriptions-tracker.csv) | The subscription hunt, one row per charge |

## How to run it

Requirements: Python 3.8+ (standard library only — nothing to install).

```bash
python3 build.py            # or: ./build.sh — builds the static site into site/
python3 build.py --serve    # optional: preview at http://localhost:8000
python3 build.py --clean    # remove site/
```

Open `site/index.html` in any browser. `site/print/08-call-log.html` and
`site/print/09-binder-checklist.html` are print-only versions (no nav) —
print them, keep them in the binder.

Run the tests:

```bash
python3 -m unittest discover -s tests -v    # or: ./test.sh
```

## How this is different from its neighbors

Three guides cover three different moments, on purpose, so each stays short:

- **caregiver-coordination-guide** — for when the person is *alive* and needs
  care: sharing the load among family, med and doctor logs, sibling task
  splits.
- **digital-legacy-handbook** — for *before* the worst day: getting an online
  life ready (accounts, password locations, memorializing, closing charges in
  advance).
- **bereavement-paperwork-guide (this one)** — for *after* a death has
  already happened: the admin that lands on someone, in order, at bearable
  speed.

## What this is not

This is practical education — paperwork scaffolding, checklists, scripts, and
vocabulary. It is **not legal advice, not tax advice, and not grief
counseling**. Estate rules vary by state and country; the agencies and
professionals will tell you exactly what they need from you. For anything
high-stakes (wills, probate, large debts), a local attorney or the agency's
own representative is worth the hour, and the
[glossary](docs/10-glossary.md) exists so you can walk into that call
already knowing the words.

## Credits

Built and maintained by **Asdale Dynamics, LLC** — beginner-friendly AI
education, books, and practical tools. Part of Dylan Asdale's plain-English
manuals and free kits.

Licensed under the MIT License — see [LICENSE](LICENSE).
"Copyright (c) 2026 Asdale Dynamics, LLC".
