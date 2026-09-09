#!/usr/bin/env python3
"""Positive regression for rich knowledge parity and reusable visual contracts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts" / "fixtures" / "modern-projectile-course.json"
APP = (ROOT / "assets" / "modern-runtime" / "src" / "App.jsx").read_text(encoding="utf-8")
WIDGETS = (ROOT / "assets" / "modern-runtime" / "src" / "animation-widgets.jsx").read_text(encoding="utf-8")
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    policy = data.get("meta", {}).get("figurePolicy") or {}
    if policy.get("mode") != "direct-first":
        failures.append("fixture must exercise figurePolicy.mode=direct-first")

    key_seen: dict[str, str] = {}
    figure_count = 0
    example_count = 0
    for scene in data.get("scenes", []):
        knowledge = scene.get("knowledge") or (scene.get("content") or {}).get("knowledge") or {}
        figures = {figure.get("id"): figure for figure in knowledge.get("pedagogicalFigures") or [] if isinstance(figure, dict) and figure.get("id")}
        figure_count += len(figures)
        for example in knowledge.get("workedExamples") or []:
            if not isinstance(example, dict):
                continue
            example_count += 1
            ref = example.get("figureRef")
            if not ref or ref not in figures:
                failures.append(f"{scene.get('id')}/{example.get('id')}: unresolved local figureRef")
            if example.get("visualNeed") in {"spatial", "mechanical", "structural", "process", "dynamic", "geometry"} and not ref:
                failures.append(f"{scene.get('id')}/{example.get('id')}: visual example has no figureRef")
        cfg = (scene.get("content") or {}).get("widgetConfig") or {}
        values = cfg.get("experimentPrompts") if cfg.get("experimentPrompts") is not None else cfg.get("experiments")
        if not isinstance(values, list):
            values = [] if values is None else [values]
        for item in values:
            if not isinstance(item, dict):
                continue
            key = str(item.get("experimentKey") or item.get("key") or "").strip()
            role = str(item.get("experimentRole") or item.get("role") or "").strip()
            if key:
                if key in key_seen:
                    failures.append(f"duplicate experimentKey in {key_seen[key]} and {scene.get('id')}")
                key_seen[key] = str(scene.get("id"))
            if data.get("meta", {}).get("experimentDedupPolicy") == "stable-key" and (not key or not role):
                failures.append(f"{scene.get('id')}: structured experiment needs key and role")

    required_app = ["function WorkedExample", "figureRef", "motion-components", "data-worked-example", "data-example-figure", "definitionFormula", "resultFormula"]
    required_widgets = ["data-equation-steps", "data-equation-step", "揭示下一步", "nextStepPrediction", "setReveal"]
    for token in required_app:
        if token not in APP:
            failures.append(f"Modern App missing rich knowledge token: {token}")
    for token in required_widgets:
        if token not in WIDGETS:
            failures.append(f"Modern equation widget missing token: {token}")
    if figure_count < example_count or example_count < 1:
        failures.append("fixture must cover at least one direct figure for each worked example")

    with tempfile.TemporaryDirectory(prefix="ic-knowledge-contract-") as temp:
        output = Path(temp) / "modern-projectile.html"
        code, out = run([sys.executable, str(ROOT / "scripts" / "render_course.py"), str(FIXTURE), str(output)])
        if code:
            failures.append("portable render failed: " + out.strip())
        else:
            code, out = run([sys.executable, str(ROOT / "scripts" / "validate_html.py"), str(output), "--strict"])
            if code:
                failures.append("strict rendered contract failed: " + out.strip())
            html = output.read_text(encoding="utf-8") if output.is_file() else ""
            for token in ['data-example-figure="', 'data-worked-example="', '运动分量教学图']:
                if token not in html:
                    failures.append(f"portable output missing inline figure token: {token}")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        print(f"KNOWLEDGE CONTRACT RESULT: FAIL ({len(failures)} failure(s))")
        return 1
    print(f"KNOWLEDGE CONTRACT RESULT: PASS ({example_count} worked examples, {figure_count} direct figures, {len(key_seen)} unique experiments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
