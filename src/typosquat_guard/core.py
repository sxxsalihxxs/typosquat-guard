from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def normalize_name(name: str) -> str:
    n = name.strip().lower()
    n = n.replace("_", "-")
    return n


def parse_requirements_txt(path: str) -> List[str]:
    pkgs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            # Skip pip options/includes for MVP
            if s.startswith(("-", "--")):
                continue

            m = NAME_RE.match(s)
            if not m:
                continue
            raw = m.group(1)
            # Remove extras like pkg[foo]
            raw = raw.split("[", 1)[0]
            pkgs.append(normalize_name(raw))
    # de-dup while preserving order
    seen = set()
    out = []
    for p in pkgs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def levenshtein(a: str, b: str) -> int:
    # classic DP, ok for small allowlists
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


def distance_threshold(name: str) -> int:
    L = len(name)
    if L <= 6:
        return 1
    if L <= 12:
        return 2
    return 3


def find_typosquat_candidate(
    name: str, allowlist: Iterable[str]
) -> Optional[Tuple[str, int]]:
    """
    Return best candidate (closest allowlisted name, distance) if suspicious.
    """
    n = normalize_name(name)
    best: Optional[Tuple[str, int]] = None
    for good in allowlist:
        g = normalize_name(good)
        # cheap filters
        if n[0:1] != g[0:1]:
            continue
        if abs(len(n) - len(g)) > 3:
            continue
        d = levenshtein(n, g)
        if best is None or d < best[1]:
            best = (g, d)

    if best is None:
        return None

    thr = distance_threshold(n)
    # suspicious only if close AND not exactly the same
    if 0 < best[1] <= thr:
        return best
    return None


@dataclass
class Finding:
    package: str
    risk: str
    reason: str
    suggestion: str


def risk_from_distance(dist: int) -> str:
    if dist <= 1:
        return "HIGH"
    if dist == 2:
        return "MED"
    return "LOW"


def scan_requirements(req_path: str, allowlist_path: str) -> Tuple[List[str], List[Finding]]:
    allow = []
    with open(allowlist_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                allow.append(normalize_name(s))

    pkgs = parse_requirements_txt(req_path)
    findings: List[Finding] = []
    for p in pkgs:
        cand = find_typosquat_candidate(p, allow)
        if cand:
            good, dist = cand
            risk = risk_from_distance(dist)
            findings.append(
                Finding(
                    package=p,
                    risk=risk,
                    reason=f"`{good}` ile çok benzer (edit distance={dist})",
                    suggestion=f"`{good}` mi demek istediniz? Paketi doğrulayın / gerekirse değiştirin.",
                )
            )
    return pkgs, findings


def render_markdown(req_path: str, pkgs: List[str], findings: List[Finding]) -> str:
    hi = sum(1 for f in findings if f.risk == "HIGH")
    med = sum(1 for f in findings if f.risk == "MED")
    low = sum(1 for f in findings if f.risk == "LOW")

    lines: List[str] = []
    lines.append("## Typosquat / Sahte Paket Taraması\n")
    lines.append(f"**Dosya:** `{req_path}`  \n")
    lines.append(f"**Toplam paket:** {len(pkgs)}  \n")
    lines.append(f"**High:** {hi} | **Med:** {med} | **Low:** {low}\n")

    if not findings:
        lines.append("✅ Şüpheli typosquat bulgusu yok.\n")
        return "\n".join(lines)

    lines.append("### Bulgular\n")
    lines.append("| Paket | Risk | Neden | Öneri |")
    lines.append("|---|---:|---|---|")
    for f in findings:
        lines.append(f"| `{f.package}` | **{f.risk}** | {f.reason} | {f.suggestion} |")

    lines.append("\n### Detay\n")
    for f in findings:
        lines.append(f"#### `{f.package}` ({f.risk})")
        lines.append(f"- Neden: {f.reason}")
        lines.append(f"- Öneri: {f.suggestion}\n")

    return "\n".join(lines)
