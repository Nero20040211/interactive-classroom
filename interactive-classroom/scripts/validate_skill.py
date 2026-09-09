#!/usr/bin/env python3
"""Comprehensive static release gate for the interactive-classroom Skill.

The executable Skill is release-number agnostic. A public release identifier is
allowed only in README.md for human-facing release bookkeeping. Validation is
capability-driven and never branches on a Skill release number.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PACKS = [
    "mathematics", "physics", "chemistry", "biology", "computer-science",
    "ml-ai", "statistics", "social-science", "humanities", "language",
    "geography", "procedural-vocational",
]
REGRESSION_FIXTURES = [
    "physics", "biology", "chemistry", "machine-learning",
    "artificial-intelligence", "geography", "computer-science",
    "statistics", "language", "humanities", "social-science",
]

CORE_REQUIRED = [
    "SKILL.md", "README.md", "LICENSE.txt", "agents/openai.yaml",
    "assets/classroom-shell.html",
    "assets/modern-runtime/package.json",
    "assets/modern-runtime/package-lock.json",
    "assets/modern-runtime/build.mjs",
    "assets/modern-runtime/template.html",
    "assets/modern-runtime/src/main.jsx",
    "assets/modern-runtime/src/App.jsx",
    "assets/modern-runtime/src/builtin-widgets.jsx",
    "assets/modern-runtime/src/animation-contract.js",
    "assets/modern-runtime/src/model-contract.js",
    "assets/modern-runtime/src/animation-widgets.jsx",
    "assets/modern-runtime/src/runtime-capabilities.json",
    "assets/modern-runtime/src/styles.css",
    "assets/modern-runtime/src/course.generated.json",
    "assets/modern-runtime/src/widget-registry.jsx",
    "assets/modern-runtime/src/widget-manifest.json",
    "examples/example-course.json",
    "scripts/render_course.py",
    "scripts/select_runtime.py",
    "scripts/test_runtime_routing.py",
    "scripts/test_modern_runtime.py",
    "scripts/test_knowledge_contract.py",
    "scripts/test_cross_runtime_animation.py",
    "scripts/check_python_syntax.py",
    "scripts/validate_html.py",
    "scripts/validate_mastery_gate.py",
    "scripts/validate_frontend_runtime.py",
    "scripts/audit_three_indicators.py",
    "scripts/audit_visual_style.py",
    "scripts/audit_animation_content_fit.py",
    "scripts/audit_modern_visual_style.py",
    "scripts/run_regression.py",
    "scripts/test_negative_gates.py",
    "scripts/fixtures/modern-projectile-course.json",
    "scripts/fixtures/modern-multidiscipline-animation-course.json",
]

REFERENCE_REQUIRED = [
    "action-protocol.md", "animated-explanations.md", "animation-content-fit.md",
    "assessment.md", "auto-orchestration.md", "chemistry-reactions.md",
    "course-schema.md", "deep-explanation.md", "discipline-animation-profiles.md",
    "discipline-pack-maturity.md", "discipline-packs.md", "discipline-router.md",
    "frontend-craft.md", "frontend-runtime.md", "html-contract.md",
    "process-animation.md",
    "interactive-experiments.md", "learner-facing-contract.md",
    "long-course-navigation.md", "mastery-practice-loop.md", "math-richtext.md",
    "math-typesetting.md", "openmaic-alignment.md", "pedagogical-figures.md",
    "pedagogy.md", "practice-foundations.md", "practice-progression.md",
    "proof-practice.md", "quality-gate.md", "quantity-units.md", "roles.md",
    "scene-contract.md", "scene-design.md", "scroll-state-contract.md",
    "session-feedback-export.md", "source-citation.md",
    "source-coverage-inventory.md", "textbook-semantics.md",
    "three-indicator-quality-gate.md", "visual-inspiration.md",
    "visual-style-sources.md", "visual-system.md",
]

# Stale development/release artifacts that must never be referenced by a formal
# version-neutral Skill. Strings are split so this validator does not trigger its
# own content scanner.
STALE_MARKERS = [
    "SELF" + "-AUDIT", "REGRESSION" + "-v", "CHANGELOG" + "-v",
    "--strict" + "-v", "regression" + "-v",
    "run_github_" + "textbook_stress.py",
    "cryptography-course-" + "basic.json",
    "cryptography-course-" + "deep.json",
]

FORBIDDEN_META_FIELDS = {
    "version", "schemaVersion", "runtimeProfileVersion", "runtimeProfileContract",
}


def run_check(cmd: list[str], label: str, root: Path) -> tuple[str, str | None]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if proc.returncode:
        output = ((proc.stdout or "") + (proc.stderr or "")).strip().replace("\n", " | ")
        return label, f"{label} failed: {output}"
    return label, None


def load_json(path: Path, rel: str, failures: list[str]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"invalid JSON {rel}: {exc}")
        return None
    if not isinstance(value, dict):
        failures.append(f"JSON root must be an object: {rel}")
        return None
    return value


def validate_markdown_paths(root: Path, failures: list[str]) -> None:
    """Check concrete, backticked in-package path references for dead links."""
    candidates = [root / "SKILL.md", root / "README.md"]
    candidates += list((root / "references").rglob("*.md"))
    candidates += list((root / "discipline-packs").rglob("*.md"))
    pattern = re.compile(r"`((?:references|scripts|examples|discipline-packs|assets)/[^`\n]+)`")
    for doc in candidates:
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        for raw in pattern.findall(text):
            ref = raw.strip().rstrip(".,;:")
            # Placeholders/globs are documentation patterns, not concrete links.
            if any(ch in ref for ch in "*<>{}"):
                continue
            target = root / ref
            if ref.endswith("/"):
                if not target.is_dir():
                    failures.append(f"dead directory reference in {doc.relative_to(root)}: {ref}")
            elif not target.exists():
                failures.append(f"dead file reference in {doc.relative_to(root)}: {ref}")


def main(root: Path) -> int:
    root = root.resolve()
    failures: list[str] = []

    required = list(CORE_REQUIRED)
    required += [f"references/{name}" for name in REFERENCE_REQUIRED]
    required += [f"discipline-packs/{pack}/PACK.md" for pack in PACKS]
    required += [f"examples/regression/{name}.json" for name in REGRESSION_FIXTURES]
    for rel in required:
        if not (root / rel).is_file():
            failures.append(f"missing {rel}")

    # Skill entry contract.
    skill = root / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            failures.append("SKILL.md missing YAML frontmatter")
        if not re.search(r"^name:\s*interactive-classroom\s*$", text, re.M):
            failures.append("SKILL.md name must be interactive-classroom")
        if "# Interactive Classroom" not in text:
            failures.append("SKILL.md missing main heading")
        tokens = [
            "knowledge-first", "Stage/Scene", "Discipline Router", "Discipline Packs",
            "semanticBlocks", "MathML", "interactive-experiments", "motion-lab",
            "map-lab", "data-structure-lab", "recursion-lab", "complexity-lab",
            "Three learner-quality indicators", "interactive-classroom-refiner",
            "frontend-runtime.md", "modern-react", "React", "Tailwind", "Motion",
            "--strict", "select_runtime.py", "test_runtime_routing.py", "test_modern_runtime.py", "run_regression.py", "test_negative_gates.py",
        ]
        for token in tokens:
            if token not in text:
                failures.append(f"SKILL.md missing contract token: {token}")

    # README is the sole human-facing location for the public release identifier.
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        if not re.search(r"\bv1\.0\.0\b", text):
            failures.append("README.md must identify the current public release")
        if "does **not** participate in runtime routing" not in text:
            failures.append("README.md must state that the release number is documentation-only")

    # Portable shell baseline and stable semantic markers.
    shell = root / "assets/classroom-shell.html"
    if shell.is_file():
        text = shell.read_text(encoding="utf-8")
        tokens = [
            'interactive-classroom-schema" content="stage-scene',
            'data-interactive-classroom="stable"', "lessonToc", "sceneSearch",
            "bookmarkCurrentBtn", "bibliographyDialog", "renderCitations",
            "executeAction", "renderSemanticBlock", "motion-lab", "map-lab",
            "data-structure-lab", "recursion-lab", "complexity-lab",
            "renderProcessAnimation", "sessionFeedbackBundle",
            'data-ui-craft="reader-first"', "prefers-reduced-motion", "aria-live",
        ]
        for token in tokens:
            if token not in text:
                failures.append(f"classroom shell missing capability token: {token}")
        if "interactive-classroom-release" in text:
            failures.append("classroom shell must not expose a Skill release marker")
        if "schemaVersion" in text:
            failures.append("classroom shell must not depend on schemaVersion")

    # Course metadata must be release-number agnostic.
    course_files = sorted((root / "examples").rglob("*.json"))
    generated = root / "assets/modern-runtime/src/course.generated.json"
    if generated.is_file():
        course_files.append(generated)
    for path in course_files:
        rel = path.relative_to(root).as_posix()
        data = load_json(path, rel, failures)
        if data is None:
            continue
        meta = data.get("meta") or {}
        if isinstance(meta, dict):
            for key in FORBIDDEN_META_FIELDS:
                if key in meta:
                    failures.append(f"{rel} must not use meta.{key}")

    # No Skill/history release markers outside README. Third-party dependency
    # versions (React/Tailwind/Motion/esbuild) are operational pins, not Skill
    # release identifiers; the pattern below intentionally targets only historic
    # Interactive Classroom v1-v4 style markers and the current public release.
    release_marker = re.compile(r"\bv(?:1|2|3|4)(?:\.\d+)+\b|\b1\.0\.0\b")
    text_suffixes = {".md", ".py", ".html", ".json", ".yaml", ".yml", ".mjs", ".jsx", ".js", ".css", ".txt"}
    for path in root.rglob("*"):
        if not path.is_file() or path.name in {"README.md", "validate_skill.py"}:
            continue
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = release_marker.search(text)
        if match:
            failures.append(
                f"release/history version marker outside README: {path.relative_to(root)} -> {match.group(0)}"
            )

    # Formal package filenames and directories must be version-neutral.
    versioned_name = re.compile(r"(?:^|[-_])v\d+(?:[._-]\d+)+", re.I)
    for path in root.rglob("*"):
        if versioned_name.search(path.name):
            failures.append(f"versioned path in formal Skill: {path.relative_to(root)}")

    # No references to removed development artifacts or version-gated interfaces.
    for path in root.rglob("*"):
        if not path.is_file() or path.name == "validate_skill.py":
            continue
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in STALE_MARKERS:
            if marker in text:
                failures.append(f"stale development reference in {path.relative_to(root)}: {marker}")

    validate_markdown_paths(root, failures)

    # Catch common cleanup scars from release-history removal.
    for doc in [root / "SKILL.md", root / "README.md", *list((root / "references").rglob("*.md")), *list((root / "discipline-packs").rglob("*.md"))]:
        if not doc.is_file():
            continue
        for line_no, line in enumerate(doc.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            stripped = line.rstrip()
            if stripped.lstrip().startswith("#") and (stripped.endswith("()") or stripped.endswith("—")):
                failures.append(f"cleanup artifact in heading {doc.relative_to(root)}:{line_no}: {stripped}")

    # Formal package hygiene.
    forbidden_parts = {"node_modules", "dist", ".build", ".pytest_cache"}
    forbidden_suffixes = {".map"}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in forbidden_parts for part in rel.parts):
            failures.append(f"generated/build artifact in formal Skill: {rel}")
        if path.is_file() and path.suffix.lower() in forbidden_suffixes:
            failures.append(f"generated/build artifact in formal Skill: {rel}")

    # Only run expensive sub-gates once the package is structurally complete.
    # Independent gates run in parallel so the aggregate command remains useful
    # as the regression corpus grows. Individual gates retain their own order.
    if not failures:
        checks = [
            ([sys.executable, "scripts/validate_frontend_runtime.py", "."], "frontend runtime"),
            ([sys.executable, "scripts/test_runtime_routing.py"], "runtime intent routing"),
            ([sys.executable, "scripts/test_modern_runtime.py"], "modern teaching/runtime regression"),
            ([sys.executable, "scripts/check_python_syntax.py", "."], "Python syntax"),
            ([sys.executable, "scripts/audit_visual_style.py", "assets/classroom-shell.html"], "visual style"),
            ([sys.executable, "scripts/run_regression.py"], "cross-disciplinary regression"),
            ([sys.executable, "scripts/test_negative_gates.py"], "negative gates"),
        ]
        sibling = root.parent / "interactive-classroom-refiner"
        if sibling.is_dir():
            checks += [
                ([sys.executable, str(sibling / "scripts/validate_skill.py"), str(sibling)], "sibling refiner"),
                ([sys.executable, str(sibling / "scripts/validate_sibling_contract.py"), str(sibling), str(root)], "feedback/refiner bridge"),
            ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(checks))) as executor:
            futures = [executor.submit(run_check, cmd, label, root) for cmd, label in checks]
            results = [future.result() for future in futures]
        order = {label: i for i, (_, label) in enumerate(checks)}
        for label, failure in sorted(results, key=lambda x: order[x[0]]):
            if failure:
                failures.append(failure)
            else:
                print(f"CHECK: {label}: PASS")

    if failures:
        for item in dict.fromkeys(failures):
            print("FAIL:", item)
        print(f"RESULT: FAIL ({len(set(failures))} failure(s))")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(main(target))
