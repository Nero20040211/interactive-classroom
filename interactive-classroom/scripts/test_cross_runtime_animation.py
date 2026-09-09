#!/usr/bin/env python3
"""Cross-runtime contract checks for deterministic animation and model state."""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts" / "fixtures" / "modern-multidiscipline-animation-course.json"
PORTABLE = ROOT / "assets" / "classroom-shell.html"
MODERN_SRC = ROOT / "assets" / "modern-runtime" / "src"
MODEL = MODERN_SRC / "model-contract.js"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def close(actual: object, expected: float, tolerance: float = 1e-8) -> bool:
    try:
        return math.isfinite(float(actual)) and abs(float(actual) - expected) <= tolerance
    except (TypeError, ValueError):
        return False


def node_model_states() -> tuple[dict, dict, str | None]:
    module_url = MODEL.as_uri()
    script = f"""
import {{ projectileState }} from {json.dumps(module_url)};
const horizontal = projectileState({{ v0: 8, h: 12, g: 9.8 }}, 0.8);
const oblique = projectileState({{ v: 14, theta: 45, h: 0, g: 9.8 }}, 1);
console.log(JSON.stringify({{ horizontal, oblique }}));
"""
    proc = subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=ENV,
    )
    if proc.returncode:
        return {}, {}, (proc.stdout or "") + (proc.stderr or "")
    try:
        result = json.loads((proc.stdout or "").strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        return {}, {}, f"could not parse Node model output: {exc}; output={proc.stdout!r}"
    return result.get("horizontal") or {}, result.get("oblique") or {}, None


def main() -> int:
    failures: list[str] = []
    horizontal, oblique, node_error = node_model_states()
    if node_error:
        failures.append(node_error)
    else:
        expected_horizontal = {"t": 0.8, "x": 6.4, "y": 8.864, "vx": 8.0, "vy": -7.84}
        for key, expected in expected_horizontal.items():
            if not close(horizontal.get(key), expected):
                failures.append(f"horizontal projectile {key} expected {expected}, got {horizontal.get(key)!r}")
        if not close(horizontal.get("T"), math.sqrt(24 / 9.8)):
            failures.append("horizontal projectile T does not match the shared model")

        angle = math.radians(45)
        expected_oblique = {
            "t": 1.0,
            "x": 14 * math.cos(angle),
            "y": 14 * math.sin(angle) - 0.5 * 9.8,
            "vx": 14 * math.cos(angle),
            "vy": 14 * math.sin(angle) - 9.8,
        }
        for key, expected in expected_oblique.items():
            if not close(oblique.get(key), expected):
                failures.append(f"oblique projectile {key} expected {expected}, got {oblique.get(key)!r}")
        if not close(oblique.get("range"), 20.0, 1e-7):
            failures.append(f"oblique projectile range expected 20, got {oblique.get('range')!r}")

    portable_text = PORTABLE.read_text(encoding="utf-8")
    for token in ("process-animation", "requestAnimationFrame", "prefers-reduced-motion", "process-play", "process-replay"):
        if token not in portable_text:
            failures.append(f"portable animation runtime missing {token}")
    modern_text = "\n".join(path.read_text(encoding="utf-8") for path in MODERN_SRC.glob("*.jsx"))
    modern_text += "\n" + (MODEL.read_text(encoding="utf-8"))
    for token in ("ProcessAnimationWidget", "MotionLabWidget", "SimulationWidget", "EquationWidget", "requestAnimationFrame", "obliqueProjectileState", "projectileState"):
        if token not in modern_text:
            failures.append(f"Modern animation runtime missing {token}")

    course = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected = {
        "multi-chemistry-bond": ("chemistry", "molecule", "chemistry-bond-formation"),
        "multi-biology-flow": ("biology", "pathway-token", "biology-pathway-transmission"),
        "multi-cs-pointer": ("computer-science", "pointer", "computer-science-pointer-update"),
        "multi-language-token": ("language", "token", "language-phrase-highlighting"),
        "multi-statistics-point": ("statistics", "point", "statistics-sample-update"),
        "multi-social-evidence": ("social-science", "evidence-card", "social-science-evidence-link"),
    }
    scenes = {scene.get("id"): scene for scene in course.get("scenes", [])}
    if set(scenes) != set(expected):
        failures.append(f"multidiscipline fixture must contain exactly six named cases, got {sorted(scenes)}")

    for scene_id, (pack, primitive, profile) in expected.items():
        scene = scenes.get(scene_id)
        if not scene:
            continue
        content = scene.get("content") or {}
        cfg = content.get("widgetConfig") or {}
        actors = cfg.get("actors") or []
        steps = cfg.get("steps") or []
        if content.get("widgetType") != "process-animation":
            failures.append(f"{scene_id} is not a process-animation scene")
        if len(steps) < 2:
            failures.append(f"{scene_id} needs at least two semantic steps")
        if not any(actor.get("primitive") == primitive for actor in actors if isinstance(actor, dict)):
            failures.append(f"{scene_id} missing discipline primitive {primitive}")
        semantics = cfg.get("animationSemantics") or {}
        if semantics.get("profile") != profile:
            failures.append(f"{scene_id} profile mismatch: {semantics.get('profile')!r}")
        actor_ids = {actor.get("id") for actor in actors if isinstance(actor, dict)}
        previous: dict = {}
        changed_transitions = 0
        for index, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                failures.append(f"{scene_id} step {index} is not an object")
                continue
            for field in ("semanticAction", "focus", "changeSummary", "whyItMatters"):
                if not isinstance(step.get(field), str) or not step[field].strip():
                    failures.append(f"{scene_id} step {index} missing {field}")
            states = step.get("states") or {}
            if not states:
                failures.append(f"{scene_id} step {index} has no state change")
            if any(actor_id not in actor_ids for actor_id in states):
                failures.append(f"{scene_id} step {index} references an unknown actor")
            if previous and any(previous.get(actor_id) != states.get(actor_id) for actor_id in actor_ids):
                changed_transitions += 1
            previous = states
        if changed_transitions < 2:
            failures.append(f"{scene_id} does not contain two observable state transitions")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        print(f"CROSS RUNTIME ANIMATION RESULT: FAIL ({len(failures)} failure(s))")
        return 1
    print("CROSS RUNTIME ANIMATION RESULT: PASS (shared physics model + six discipline process cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
