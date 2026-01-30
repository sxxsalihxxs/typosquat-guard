import argparse
from typosquat_guard.core import scan_requirements, render_markdown


def main():
    ap = argparse.ArgumentParser(description="Typosquat / sahte paket tarayıcı")
    ap.add_argument("--file", required=True, help="requirements.txt yolu")
    ap.add_argument("--allowlist", default="allowlist.txt", help="allowlist yolu")
    ap.add_argument("--out", default="report.md", help="çıktı markdown dosyası")
    args = ap.parse_args()

    pkgs, findings = scan_requirements(args.file, args.allowlist)
    md = render_markdown(args.file, pkgs, findings)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Wrote {args.out} (packages={len(pkgs)}, findings={len(findings)})")

