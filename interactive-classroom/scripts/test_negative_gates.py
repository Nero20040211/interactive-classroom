#!/usr/bin/env python3
"""Destructive checks proving the strict validator rejects important contract failures."""
from __future__ import annotations
import html, json, os, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SHELL = (ROOT / "assets" / "classroom-shell.html").read_text(encoding="utf-8")
VALIDATOR = ROOT / "scripts" / "validate_html.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def load(name: str) -> dict:
    path = ROOT / "examples" / "regression" / f"{name}.json"
    if not path.is_file():
        path = ROOT / "scripts" / "fixtures" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def render(course: dict, path: Path) -> None:
    meta = course.get("meta") or {}
    out = SHELL.replace("{{TITLE}}", html.escape(str(meta.get("title", "课程"))))
    out = out.replace("{{SUBTITLE}}", html.escape(str(meta.get("subtitle", ""))))
    out = out.replace("{{COURSE_JSON}}", json.dumps(course, ensure_ascii=False, separators=(",", ":")))
    path.write_text(out, encoding="utf-8")


def first_process(course: dict) -> dict:
    for scene in course.get("scenes", []):
        content = scene.get("content") or {}
        if content.get("widgetType") == "process-animation":
            return content.get("widgetConfig") or {}
    raise RuntimeError("fixture has no process-animation")


def run_validator(path: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(VALIDATOR), str(path), "--strict"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    cases: list[tuple[str, dict, str]] = []

    d = load("chemistry"); d.setdefault("meta", {})["version"] = "forbidden"
    cases.append(("release-field", d, "version-neutral contract violation"))

    d = load("chemistry")
    for scene in d.get("scenes", []):
        knowledge = scene.get("knowledge") or (scene.get("content") or {}).get("knowledge")
        if isinstance(knowledge, dict) and knowledge.get("mentalModel"):
            knowledge["mentalModel"] = str(knowledge["mentalModel"]) + " x = 2"
            break
    cases.append(("raw-math-leak", d, "substantive math leaked"))

    d = load("machine-learning")
    for scene in d.get("scenes", []):
        knowledge = scene.get("knowledge") or (scene.get("content") or {}).get("knowledge")
        if isinstance(knowledge, dict):
            knowledge.setdefault("citations", []).append({"sourceId": "missing-source"})
            break
    cases.append(("unknown-citation", d, "references unknown source"))

    d = load("geography")
    for scene in d.get("scenes", []):
        content = scene.get("content") or {}
        if content.get("widgetType") == "map-lab":
            (content.get("widgetConfig") or {}).get("points", [])[0]["lon"] = 999
            break
    cases.append(("bad-longitude", d, "invalid lon/lat"))

    d = load("computer-science")
    d["scenes"].append({
        "id": "NEG-STACK", "type": "interactive", "title": "stack check", "objectiveIds": [d["objectives"][0]["id"]],
        "knowledge": {"mentalModel": "栈只允许从同一端压入和弹出元素；验证时必须保持操作顺序与数据结构语义一致。",
                      "workedExamples": [{"id": "neg-ex", "variantType": "standard", "title": "操作序列", "text": "依次压入两个元素后，下一次弹出应先得到后压入的元素。"}],
                      "boundaries": ["这里检查抽象栈语义，不讨论并发容器或持久化数据结构。"],
                      "keyPoints": ["操作必须保持栈顶语义。"]},
        "content": {"widgetType": "data-structure-lab", "widgetConfig": {"kind": "stack", "initial": ["A"], "maxSize": 5, "prompt": "检查操作", "invariant": "FIFO"}}
    })
    cases.append(("bad-stack-invariant", d, "stack invariant must state LIFO"))

    d = load("chemistry")
    first_process(d)["steps"][0].pop("semanticAction", None)
    cases.append(("missing-semantic-action", d, "semanticAction"))

    d = load("modern-projectile-course")
    for scene in d.get("scenes", []):
        knowledge = scene.get("knowledge") or (scene.get("content") or {}).get("knowledge")
        if isinstance(knowledge, dict) and knowledge.get("workedExamples"):
            knowledge["workedExamples"][0]["figureRef"] = "missing-figure"
            break
    cases.append(("unresolved-worked-example-figure", d, "worked-example violation"))

    d = load("modern-projectile-course")
    for scene in d.get("scenes", []):
        content = scene.get("content") or {}
        if content.get("widgetType") == "motion-lab":
            experiments = (content.get("widgetConfig") or {}).get("experiments") or []
            experiments[1]["experimentKey"] = experiments[0]["experimentKey"]
            break
    cases.append(("duplicate-experiment-key", d, "duplicate experimentKey"))

    d = load("modern-projectile-course")
    d["scenes"].extend([
        {"id": "NEG-MAP-A", "type": "reference", "title": "层级图一", "objectiveIds": [], "knowledge": {}, "content": {"widgetType": "diagram", "widgetConfig": {"kind": "mind-map", "visualPurpose": "hierarchy", "mindMapJustification": "课程目标本身是层级归类。"}}},
        {"id": "NEG-MAP-B", "type": "reference", "title": "层级图二", "objectiveIds": [], "knowledge": {}, "content": {"widgetType": "diagram", "widgetConfig": {"kind": "knowledge-graph", "visualPurpose": "network"}}},
    ])
    cases.append(("unjustified-mind-map", d, "mindMapJustification"))

    ok = True
    with tempfile.TemporaryDirectory(prefix="ic-negative-") as td_raw:
        td = Path(td_raw)
        for name, course, expected in cases:
            path = td / f"{name}.html"
            render(course, path)
            code, out = run_validator(path)
            passed = code != 0 and expected in out
            print(f"{name}: {'EXPECTED FAIL' if passed else 'UNEXPECTED RESULT'}")
            if not passed:
                print(out)
            ok &= passed

        # Corrupted embedded course JSON must fail hard in strict mode.
        malformed = td / "malformed-course-json.html"
        render(load("chemistry"), malformed)
        raw = malformed.read_text(encoding="utf-8").replace('const course={', 'const course={BROKEN', 1)
        malformed.write_text(raw, encoding="utf-8")
        code, out = run_validator(malformed)
        passed = code != 0 and ("could not parse embedded course JSON" in out or "embedded course data not found" in out)
        print(f"malformed-course-json: {'EXPECTED FAIL' if passed else 'UNEXPECTED RESULT'}")
        if not passed: print(out)
        ok &= passed

        # Network-path destructive tests operate on an otherwise valid rendered HTML.
        base = td / "network-base.html"
        render(load("physics"), base)
        baseline = base.read_text(encoding="utf-8")
        network_cases = [
            ("remote-css-url", '<style>.probe{background:url(https://example.com/tracker.png)}</style>', "remote CSS url() resource"),
            ("send-beacon", '<script>navigator.sendBeacon("https://example.com/telemetry","x")</script>', "navigator.sendBeacon network API"),
            ("remote-dynamic-import", '<script>import("https://example.com/module.js")</script>', "remote dynamic import"),
            ("remote-dom-src", '<script>const img=document.createElement("img");img.src="https://example.com/p.png";</script>', "remote DOM src/href assignment"),
        ]
        for name, injection, expected in network_cases:
            path = td / f"{name}.html"
            path.write_text(baseline.replace("</body>", injection + "</body>"), encoding="utf-8")
            code, out = run_validator(path)
            passed = code != 0 and expected in out
            print(f"{name}: {'EXPECTED FAIL' if passed else 'UNEXPECTED RESULT'}")
            if not passed: print(out)
            ok &= passed

    print("NEGATIVE GATE RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
