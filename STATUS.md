# STATUS.md

Last verified: 2026-10-27

## What was built

**Bereavement Paperwork Guide** — a warm, plain-English, education-only
manual for the paperwork that follows a death: the first-week checklist,
who to call in what order, the "forever file" of copies to keep, accounts
and subscriptions to close, mail and benefits basics, predatory-"help" red
flags, and a gentle self-pacing structure for shock-brain weeks. It is
never legal, tax, or grief-counseling advice, and the text says so on every
page (footer) plus a dedicated section on the start page.

Local-first: plain Markdown documents plus a dependency-free Python build
script that generates a small static HTML site. No accounts, no cloud, no
tracking. Print pages and fillable CSV worksheets included.

Contents:

- `docs/` — 11 Markdown pages:
  - `index.md` — start here: how to use it, what it is/isn't, the three
    working rules, and a "first 48 hours" fast lane
  - `01-first-week.md` — the first-week checklist + an explicit "not yet"
    list
  - `02-who-to-call.md` — a 13-row call-order table, five scripts
    (opener, voicemail, third-transfer, debt collector, verify-and-callback),
    and the "have-ready card" template
  - `03-what-to-keep.md` — the forever-file checklist, keep-for table
    (forever / 7 years / 1–2 years), the two-places rule, shredding basics
  - `04-accounts-and-subscriptions.md` — the billing hunt (email keyword
    sweep included), a three-box sort (keep-running / subscriptions /
    debts), the safe canceling order, category-by-category traps table
  - `05-mail-and-benefits.md` — mail forwarding + the watch-the-mail
    schedule, government benefits map (SSA/Medicare/Medicaid/VA/IRS/unclaimed
    property), survivor benefits in plain English, deceased-flag + freeze at
    the three credit bureaus, and the don't-pay-yet principle
  - `06-predatory-help-red-flags.md` — a pattern/what-you-do table
    (13 patterns incl. AI-written scam letters), seven verification habits,
    and an "if something already went wrong" recovery section
  - `07-self-pacing.md` — shock-brain mechanics, minimum viable tasks, the
    15-minute timer, the phone-call sandwich, low-power day menu, the hard
    box, and a warm crisis-line section (988 / iasp.info)
  - `08-call-log.md` — printable call-log worksheet (also a CSV)
  - `09-binder-checklist.md` — shopping list + ten-tab binder checklist +
    maintenance habits
  - `10-glossary.md` — 30 plain-English terms (incl. the POA-ends-at-death
    surprise)
- `worksheets/call-log.csv` and `worksheets/subscriptions-tracker.csv` —
  fillable local spreadsheets with one clearly-marked SAMPLE row
- `build.py` — stdlib-only Markdown-subset renderer + static site generator
  (warm serif design, responsive, print stylesheet, heading anchors,
  `--serve` preview, `--clean`, copies the CSVs into `site/worksheets/`)
- `build.sh` / `test.sh` — thin wrappers
- `tests/test_build.py` — 40 tests (Details below)
- `LICENSE` (MIT, "Copyright (c) 2026 Asdale Dynamics, LLC"), `README.md`
  (credits Asdale Dynamics, LLC)

Distinct on purpose from its neighbors: `caregiver-coordination-guide`
(care while the person is alive) and `digital-legacy-handbook` (preparing an
online life *before* the worst day); both are named in the README and the
start page so nobody builds the same guide twice.

## How to run it

Requires Python 3.8+ (standard library only; nothing to install).

```bash
python3 build.py                              # build site/ from docs/
python3 build.py --serve                      # preview at http://localhost:8000
python3 build.py --clean                      # remove site/
python3 -m unittest discover -s tests -v      # run the test suite
```

Open `site/index.html` in a browser; `site/print/08-call-log.html` and
`site/print/09-binder-checklist.html` are print-only worksheet pages;
`site/worksheets/*.csv` are the fillable trackers.

## Verification results

- `python3 build.py` — builds 11 pages + 2 print pages + 2 CSVs into `site/`
- `python3 -m unittest discover -s tests -v` — **OK, 40/40 tests pass**, in
  ~0.12 s, covering:
  - renderer unit tests (headings + anchor ids, escaping, inline styles,
    links, nested/ordered/checkbox lists, tables, blockquotes, code fences,
    hr, soft-wrapped paragraphs)
  - doc checks: every page exists and starts with an H1; expected key
    phrases per chapter (checklists, scripts, 988 section, ten tabs, glossary
    POA entry); disclaimers present in README and index; both sibling guides
    named (distinctness); no guessed URLs or placeholders (no
    example.invalid/TODO/FIXME)
  - link integrity: every doc-to-doc `.md` link and `#anchor` resolves to a
    real heading in the target doc (anchors verified via the same slugifier
    the build uses); in-page anchors resolve; `.csv` links resolve
  - build checks: all built pages exist (incl. print pages + copied CSVs);
    every built page passes an HTML tag-balance check; footer on every
    content page carries the exact "Copyright (c) 2026 Asdale Dynamics, LLC"
    line and the "never legal, tax, or grief-counseling advice" note; print
    pages have no nav/footer and their relative links are rewritten to
    resolve; no raw markdown leftovers; every local href resolves (including
    `#fragments` handled); rebuild is byte-identical (deterministic)
  - worksheet checks: CSV header/row widths; SAMPLE rows clearly marked
  - repo checks: LICENSE copyright line exact; README credits **Asdale
    Dynamics, LLC** and documents `--serve`/`--clean`; secret-pattern scan
    (AWS keys, GitHub tokens, private-key blocks, Google API keys, Slack
    tokens, live keys) clean; live HTTP smoke test (server on an ephemeral
    port, `GET /index.html` → 200 and correct content)
- Served `site/` via a local static server — `/index.html`,
  `/print/08-call-log.html`, `/worksheets/call-log.csv` all return 200
- Hand-verified rendering of the trickiest blocks: the filler-line
  have-ready card (`<pre>`), scripts in italic blockquotes, the 13-row call
  table, and checkbox lists

## Known gaps / future work

- The Markdown renderer covers the subset this guide uses (headings,
  paragraphs, nested lists, checkboxes, tables, single-level blockquotes,
  code fences, inline styles, heading anchors). It is not a CommonMark
  implementation; obscure constructs (reference links, setext headings,
  nested blockquotes) are out of scope.
- Content is U.S.-flavored; the text repeatedly says which parts are
  state-dependent and defers to agencies and local professionals. Country
  variants (UK/CA/IN etc.) are a future expansion, not a rewrite.
- The call log's print sheet is one page of 12 blank rows; some families
  will want a second page — printing the page twice works, but a dedicated
  "page 2" variant could exist.
- No dark mode. Print styling is tuned for the two worksheet pages first.
- A future idea: a fill-in PDF version of the call log and the have-ready
  card (browser print-to-PDF already covers it locally).
