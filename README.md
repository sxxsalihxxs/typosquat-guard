# typosquat-guard

Typosquat Guard is a lightweight security tool that detects **typosquatting and suspicious packages**
in dependency files such as `requirements.txt`.

It is designed to integrate directly into developer workflows (PR checks, CI/CD),
helping teams catch **supply-chain security risks early**.

---

## Why does this exist?

Software supply-chain attacks often start with a **malicious package that looks almost identical**
to a legitimate one (e.g. `reqeusts` vs `requests`).

These attacks:
- Are easy to miss in code reviews
- Can affect thousands of services
- Have caused real-world incidents across the industry

Typosquat Guard aims to **shift security left** by adding automated checks
directly into the development process.

---

## How it works

1. Parses dependency files (currently `requirements.txt`)
2. Normalizes package names
3. Compares them against a known-good allowlist
4. Uses edit-distance heuristics to detect likely typosquatting
5. Generates a human-readable Markdown report

---

## Example

requests==2.31.0
reqeusts==2.0.0



            ┌───────────────────────────┐
            │   Developer opens a PR     │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   requirements.txt found  │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Normalize package names    │
            │ (lowercase, -, _)          │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Compare with allowlist    │
            │ (edit distance check)     │
            └─────────────┬─────────────┘
                          │
           ┌──────────────┴──────────────┐
           │                               │
           ▼                               ▼
┌──────────────────────┐      ┌────────────────────────┐
│ No suspicious match  │      │ Possible typosquatting │
│ → Pass               │      │ (reqeusts ≈ requests) │
└──────────────────────┘      └─────────────┬──────────┘
                                            │
                                            ▼
                             ┌────────────────────────┐
                             │ Risk score calculated  │
                             │ (LOW / MED / HIGH)     │
                             └─────────────┬──────────┘
                                            │
                                            ▼
                             ┌────────────────────────┐
                             │ Markdown report        │
                             │ posted to PR comment   │
                             └────────────────────────┘
                                                           
