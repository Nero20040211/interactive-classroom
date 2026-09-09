#!/usr/bin/env python3
"""Static visual contract for the Modern learning workbench."""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_modern_visual_style.py PATH_TO_STYLES_CSS")
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    checks = [
        ("light surface tokens", "--ic-bg:" in text and "--ic-surface:" in text and "--ic-line:" in text),
        ("dark surface tokens", "@media (prefers-color-scheme: dark)" in text and "--ic-bg: #0c1220" in text),
        ("accent and semantic tokens", "--ic-accent:" in text and "--ic-good:" in text and "--ic-warn:" in text),
        ("workbench three-column layout", "grid-template-columns: 248px minmax(0, 1fr) 216px" in text),
        ("reading column", ".ic-reading-column" in text and "max-width: 78ch" in text),
        ("widget frame", ".ic-widget-frame" in text and "border-radius: var(--ic-radius-lg)" in text),
        ("scene and outline rails", ".ic-scene-rail" in text and ".ic-outline-rail" in text),
        ("outline buttons keep natural text flow", ".ic-outline-list" in text and ".ic-outline-button" in text and "overflow-wrap: anywhere" in text),
        ("medium breakpoint", "@media (max-width: 1180px)" in text),
        ("narrow breakpoint", "@media (max-width: 820px)" in text),
        ("internal animation scroll strategy", "overscroll-behavior: contain" in text and "overflow: auto" in text),
        ("keyboard focus", ":focus-visible" in text and "outline-offset" in text),
        ("reduced motion", "@media (prefers-reduced-motion: reduce)" in text and "transition: none" in text),
    ]
    failures = [label for label, ok in checks if not ok]
    for label in failures:
        print(f"FAIL: {label}")
    if failures:
        print(f"MODERN VISUAL RESULT: FAIL ({len(failures)} failure(s))")
        return 1
    print(f"MODERN VISUAL RESULT: PASS ({len(checks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
