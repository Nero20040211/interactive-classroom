#!/usr/bin/env python3
"""Run the bundled cross-disciplinary, version-neutral regression suite.

Jobs are parallelized across fixtures so the release gate remains practical even
as validated-native coverage grows. Each fixture is still rendered with the
current shell and then checked sequentially inside its own job.
"""
from __future__ import annotations
import concurrent.futures, json, os, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
FIXTURES = [
    "physics", "biology", "chemistry", "machine-learning",
    "artificial-intelligence", "geography", "computer-science",
    "statistics", "language", "humanities", "social-science",
]


def run(cmd: list[str], require_zero_warnings: bool = False) -> tuple[bool, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    out = (p.stdout or "") + (p.stderr or "")
    ok = p.returncode == 0
    if require_zero_warnings:
        ok = ok and "RESULT: PASS (0 warning(s))" in out
    return ok, out


def fixture_job(name: str, td: Path) -> tuple[str, bool, str]:
    source = ROOT / "examples" / "regression" / f"{name}.json"
    target = td / f"{name}.html"
    checks: list[tuple[list[str], bool, str]] = [
        ([sys.executable, str(ROOT / "scripts" / "render_course.py"), str(source), str(target)], False, "render"),
        ([sys.executable, str(ROOT / "scripts" / "validate_html.py"), str(target), "--strict"], True, "strict"),
        ([sys.executable, str(ROOT / "scripts" / "audit_three_indicators.py"), str(source)], False, "three indicators"),
    ]
    data = json.loads(source.read_text(encoding="utf-8"))
    if any(((s.get("content") or {}).get("widgetType") == "process-animation") for s in data.get("scenes", [])):
        checks.append(([sys.executable, str(ROOT / "scripts" / "audit_animation_content_fit.py"), str(source)], False, "animation fit"))
    ok = True; parts = [f"=== {name} ===\n"]
    for cmd, zero, label in checks:
        passed, out = run(cmd, zero); ok &= passed; parts.append(out)
        if not passed: parts.append(f"REGRESSION FAIL: {name}: {label}\n")
    return name, ok, "".join(parts)


def canonical_job(td: Path) -> tuple[str, bool, str]:
    source = ROOT / "examples" / "example-course.json"; target = td / "example-course.html"
    checks = [
        ([sys.executable, str(ROOT / "scripts" / "render_course.py"), str(source), str(target)], False, "render"),
        ([sys.executable, str(ROOT / "scripts" / "validate_html.py"), str(target), "--strict"], True, "strict"),
        ([sys.executable, str(ROOT / "scripts" / "validate_mastery_gate.py"), str(target)], False, "mastery"),
        ([sys.executable, str(ROOT / "scripts" / "audit_three_indicators.py"), str(source)], False, "three indicators"),
        ([sys.executable, str(ROOT / "scripts" / "audit_animation_content_fit.py"), str(source)], False, "animation fit"),
    ]
    ok=True; parts=["=== canonical mastery example ===\n"]
    for cmd,zero,label in checks:
        passed,out=run(cmd,zero);ok&=passed;parts.append(out)
        if not passed:parts.append(f"REGRESSION FAIL: canonical example: {label}\n")
    return "canonical",ok,"".join(parts)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ic-regression-") as td_raw:
        td=Path(td_raw); jobs=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(6,len(FIXTURES)+1)) as ex:
            jobs=[ex.submit(fixture_job,name,td) for name in FIXTURES]
            jobs.append(ex.submit(canonical_job,td))
            results=[f.result() for f in jobs]
    order={name:i for i,name in enumerate(FIXTURES+["canonical"])}
    results.sort(key=lambda x:order[x[0]])
    ok=True
    for _,passed,out in results:
        print(out,end="");ok&=passed
    print("REGRESSION RESULT:","PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
