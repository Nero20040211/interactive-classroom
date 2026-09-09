#!/usr/bin/env python3
"""Render canonical course JSON with the current portable classroom shell."""
from __future__ import annotations
import argparse, html, json
from pathlib import Path


def render(course_path: Path, shell_path: Path, output_path: Path) -> None:
    course = json.loads(course_path.read_text(encoding="utf-8"))
    if not isinstance(course, dict):
        raise ValueError("course JSON must be an object")
    meta = course.get("meta") or {}
    shell = shell_path.read_text(encoding="utf-8")
    required = ["{{TITLE}}", "{{SUBTITLE}}", "{{COURSE_JSON}}"]
    missing = [x for x in required if x not in shell]
    if missing:
        raise ValueError("portable shell is missing placeholders: " + ", ".join(missing))
    out = shell.replace("{{TITLE}}", html.escape(str(meta.get("title", "Interactive Classroom"))))
    out = out.replace("{{SUBTITLE}}", html.escape(str(meta.get("subtitle", ""))))
    out = out.replace("{{COURSE_JSON}}", json.dumps(course, ensure_ascii=False, separators=(",", ":")))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(out, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("course", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--shell", type=Path)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    shell = args.shell or root / "assets" / "classroom-shell.html"
    try:
        render(args.course, shell, args.output)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"RENDER RESULT: PASS -> {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
