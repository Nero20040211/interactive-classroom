#!/usr/bin/env python3
"""Static/data regression for the optional Modern Runtime.

This deliberately avoids npm/browser execution. It proves that bundled course
shapes are covered by the React teaching contract and that built-in widgets are
real registry entries rather than empty placeholders.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "modern-runtime" / "src"
CAPS = json.loads((SRC / "runtime-capabilities.json").read_text(encoding="utf-8"))
APP = (SRC / "App.jsx").read_text(encoding="utf-8")
ANIMATION_WIDGETS = (SRC / "animation-widgets.jsx").read_text(encoding="utf-8")
BUILTINS = (SRC / "builtin-widgets.jsx").read_text(encoding="utf-8")
REGISTRY = (SRC / "widget-registry.jsx").read_text(encoding="utf-8")

failures: list[str] = []
scene_types = set(CAPS.get("sceneTypes") or [])
builtin_types = set(CAPS.get("builtinWidgetTypes") or [])
semantic_kinds = set(CAPS.get("semanticBlockKinds") or [])

for token in [
    "function QuizScene", "function ExplainBackScene", "function MasterySummary",
    "function StructuredScene", "function SemanticBlock", "function PedagogicalFigure", "function WorkedExample",
    "statement", "formula", "definitionFormula", "sections", "proofSketch", "strategy", "conclusion", "prompt", "result", "resultFormula", "solution",
    "pedagogicalFigures", "figureRef", "motion-components", "data-worked-example", "data-example-figure", "collectCitationIds", "flattenText({title:s.title,intro:s.intro,knowledge:s.knowledge,content:s.content})",
    "document.addEventListener('keydown'", "Escape", "重置学习", "学习反馈",
]:
    if token not in APP:
        failures.append(f"Modern teaching contract missing token: {token}")

for token in ["data-equation-steps", "data-equation-step", "揭示下一步", "nextStepPrediction", "reducedMotion"]:
    if token not in ANIMATION_WIDGETS:
        failures.append(f"Modern equation contract missing token: {token}")

if "...builtinWidgetRegistry" not in REGISTRY or "...generatedWidgetRegistry" not in REGISTRY:
    failures.append("widget registry must compose built-in and generated registries")

for widget in sorted(builtin_types):
    if not re.search(rf'["\']{re.escape(widget)}["\']\s*:\s*[A-Za-z_][A-Za-z0-9_]*', BUILTINS):
        failures.append(f"builtin widget has no concrete registry component: {widget}")

if "GenericLab" in BUILTINS or re.search(r':\s*GenericLab\b', BUILTINS):
    failures.append("Modern registry must not map a teaching widget to GenericLab")
for expected_widget in {"motion-lab", "simulation"}:
    if expected_widget not in builtin_types:
        failures.append(f"Modern capabilities missing native widget: {expected_widget}")

def validate_process_semantics(label: str, config: dict) -> None:
    for index, step in enumerate(config.get("steps") or []):
        for field in ("focus", "changeSummary", "whyItMatters"):
            value = step.get(field) if isinstance(step, dict) else None
            if not isinstance(value, str) or not value.strip():
                failures.append(
                    f"{label}: process-animation step {index + 1} missing semantic field: {field}"
                )

required_semantics = {"definition", "theorem", "proof", "example", "exercise"}
if not required_semantics.issubset(semantic_kinds):
    failures.append("runtime capabilities must include core textbook semantic block kinds")

course_files = [
    ROOT / "examples" / "example-course.json",
    *sorted((ROOT / "examples" / "regression").glob("*.json")),
    ROOT / "scripts" / "fixtures" / "animation-contract.json",
]
seen_scenes: set[str] = set()
seen_widgets: set[str] = set()
for path in course_files:
    data = json.loads(path.read_text(encoding="utf-8"))
    if path.name == "animation-contract.json":
        for case in data.get("cases", []):
            validate_process_semantics(f"{path.name}:{case.get('id', 'case')}", case)
    for scene in data.get("scenes", []):
        st = scene.get("type")
        if st:
            seen_scenes.add(st)
            if st not in scene_types:
                failures.append(f"{path.name}: scene type not supported by Modern Runtime: {st}")
        wt = (scene.get("content") or {}).get("widgetType")
        if wt:
            seen_widgets.add(wt)
            if wt not in builtin_types:
                failures.append(f"{path.name}: bundled regression widget is not a Modern built-in: {wt}")
            if not re.search(rf'["\']{re.escape(wt)}["\']\s*:\s*[A-Za-z_][A-Za-z0-9_]*', BUILTINS):
                failures.append(f"{path.name}: widget {wt} has no concrete Modern component")
            if wt == "process-animation":
                validate_process_semantics(path.name, (scene.get("content") or {}).get("widgetConfig") or {})

for expected in {"quiz", "explain-back", "mastery", "interactive", "concept", "orientation"}:
    if expected not in seen_scenes:
        failures.append(f"Modern regression corpus does not exercise scene type: {expected}")

if len(seen_widgets) < 10:
    failures.append(f"Modern regression corpus exercises too few widget families: {len(seen_widgets)}")

if failures:
    for failure in failures:
        print("FAIL:", failure)
    print(f"MODERN RUNTIME RESULT: FAIL ({len(failures)} failure(s))")
    raise SystemExit(1)
print(f"MODERN RUNTIME RESULT: PASS ({len(seen_scenes)} scene types, {len(seen_widgets)} widget families across {len(course_files)} courses)")
