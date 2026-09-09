#!/usr/bin/env python3
"""Independent current mastery/practice/figure gate.

This script intentionally checks learning coverage separately from the HTML/runtime
validator so the course builder does not certify its own pedagogical completeness.
It reads the embedded `const course = {...};` payload from a generated classroom.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def extract_course(text: str) -> dict:
    m = re.search(r"const\s+course\s*=\s*(\{.*?\})\s*;\s*const\s+initialState", text, re.S)
    if m:
        return json.loads(m.group(1))
    m = re.search(r'<script[^>]+id=["\']course-data["\'][^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', text, re.I | re.S)
    if m:
        return json.loads(m.group(1))
    raise ValueError("embedded course JSON not found")


def check(course: dict) -> list[str]:
    failures: list[str] = []
    meta = course.get("meta") or {}
    policy = meta.get("practicePolicy") or {}
    if policy.get("mode") != "mastery-loop":
        return failures

    inventory = course.get("contentInventory") or []
    if not inventory:
        failures.append("contentInventory is empty")

    examples: set[str] = set()
    example_meta: dict[str, dict] = {}
    practices: set[str] = set()
    practice_meta: dict[str, dict] = {}
    figures: dict[str, dict] = {}
    explain_map: dict[str, list[str]] = {}
    mastery_scene = None
    for scene in course.get("scenes") or []:
        k = scene.get("knowledge") or (scene.get("content") or {}).get("knowledge") or {}
        for ex in k.get("workedExamples") or []:
            if isinstance(ex, dict) and ex.get("id"):
                examples.add(ex["id"]); example_meta[ex["id"]] = ex
        for f in k.get("pedagogicalFigures") or []:
            if isinstance(f, dict) and f.get("id"):
                figures[f["id"]] = f
        for b in k.get("semanticBlocks") or []:
            if not isinstance(b, dict) or not b.get("id"):
                continue
            if b.get("kind") == "example":
                examples.add(b["id"]); example_meta[b["id"]] = b
            if b.get("kind") == "exercise":
                practices.add(b["id"]); practice_meta[b["id"]] = b
        if scene.get("type") in {"quiz", "mastery"}:
            for q in (scene.get("content") or {}).get("items") or []:
                if isinstance(q, dict) and q.get("id"):
                    practices.add(q["id"]); practice_meta[q["id"]] = q
        if scene.get("type") == "explain-back":
            ec = scene.get("content") or {}
            for cid in ec.get("conceptIds") or []:
                explain_map.setdefault(cid, []).append(scene.get("id", "?"))
            if len(ec.get("requiredIdeas") or []) < 2:
                failures.append(f"{scene.get('id','?')}: explain-back needs >=2 requiredIdeas")
            if len(ec.get("commonGaps") or []) < 3:
                failures.append(f"{scene.get('id','?')}: explain-back needs >=3 commonGaps")
        if scene.get("type") == "mastery" and (scene.get("content") or {}).get("masteryGate"):
            mastery_scene = scene

    min_ex = int(policy.get("minWorkedExamplesPerCore", 2))
    min_pr = int(policy.get("minPracticeItemsPerCore", 3))
    for item in inventory:
        if not isinstance(item, dict) or item.get("importance", "support") != "core":
            continue
        iid = item.get("id", "?")
        if not item.get("label") or not item.get("sourceLocator"):
            failures.append(f"{iid}: inventory item needs label and sourceLocator")
        ex = item.get("exampleRefs") or []
        pr = item.get("practiceRefs") or []
        if len(ex) < min_ex:
            failures.append(f"{iid}: needs >= {min_ex} worked examples")
        if len(pr) < min_pr:
            failures.append(f"{iid}: needs >= {min_pr} practice items")
        for rid in ex:
            if rid not in examples:
                failures.append(f"{iid}: unknown example ref {rid}")
        for rid in pr:
            if rid not in practices:
                failures.append(f"{iid}: unknown practice ref {rid}")
        if policy.get("requireExplainBack") and not (item.get("explainBackRefs") or explain_map.get(iid)):
            failures.append(f"{iid}: no explain-back coverage")
        if policy.get("requireExampleContrast"):
            variants = {str((example_meta.get(r) or {}).get("variantType", "")) for r in ex}
            if "standard" not in variants:
                failures.append(f"{iid}: no standard worked example")
            if not variants.intersection({"contrast","boundary","misconception","reverse"}):
                failures.append(f"{iid}: no contrast/boundary/misconception worked example")
        if policy.get("requirePracticeProgression"):
            levels = {str((practice_meta.get(r) or {}).get("practiceLevel", "")) for r in pr}
            if "guided" not in levels:
                failures.append(f"{iid}: no guided practice")
            if "independent" not in levels:
                failures.append(f"{iid}: no independent practice")
            if not levels.intersection({"transfer","retrieval"}):
                failures.append(f"{iid}: no transfer/retrieval practice")
        fig_policy = (meta.get("figurePolicy") or {})
        if fig_policy.get("mode") == "geometry-native":
            refs = item.get("figureRefs") or []
            min_fig = int(fig_policy.get("minFiguresPerCore", 2))
            if len(refs) < min_fig:
                failures.append(f"{iid}: needs >= {min_fig} pedagogical figures")
            if any(r not in figures for r in refs):
                failures.append(f"{iid}: unknown pedagogical figure ref")
            if fig_policy.get("requireKindDiversity"):
                kinds = {(figures.get(r) or {}).get("figureKind") for r in refs}
                if not kinds.intersection({"concept","step","reasoning"}):
                    failures.append(f"{iid}: lacks representation-building figure")
                if not kinds.intersection({"compare","misconception"}):
                    failures.append(f"{iid}: lacks compare/misconception figure")

    if policy.get("requireCumulativeRetrieval"):
        mixed = False
        for scene in course.get("scenes") or []:
            c = scene.get("content") or {}
            if scene.get("type") == "quiz" and c.get("cumulative"):
                obj = {oid for q in c.get("items") or [] for oid in (q.get("objectiveIds") or [])}
                mixed |= len(obj) >= 2
        if not mixed:
            failures.append("no cumulative retrieval quiz mixing >=2 objectives")

    if not mastery_scene:
        failures.append("no independent masteryGate scene")
    else:
        content = mastery_scene.get("content") or {}
        gate = content.get("masteryGate") or {}
        qids = {q.get("id") for q in content.get("items") or [] if isinstance(q, dict)}
        threshold = gate.get("threshold")
        if not isinstance(threshold, (int, float)) or not (0 < float(threshold) <= 1):
            failures.append("masteryGate.threshold must be in (0,1]")
        objectives = {o if isinstance(o, str) else o.get("id") for o in course.get("objectives") or []}
        rules = gate.get("objectiveRules") or []
        ruled = {r.get("objectiveId") for r in rules}
        if objectives - ruled:
            failures.append("masteryGate does not cover every objective: " + ", ".join(sorted(x for x in objectives-ruled if x)))
        qmap = {q.get('id'): q for q in content.get('items') or [] if isinstance(q, dict)}
        for r in rules:
            ids = r.get("questionIds") or []
            if len(ids) < 2:
                failures.append(f"mastery objective {r.get('objectiveId','?')} needs >=2 questions")
            if any(x not in qids for x in ids):
                failures.append(f"mastery objective {r.get('objectiveId','?')} references unknown question")
            min_correct = r.get('minCorrect')
            if not isinstance(min_correct, int) or min_correct < 1 or min_correct > len(ids):
                failures.append(f"mastery objective {r.get('objectiveId','?')} has invalid minCorrect")
            if policy.get('requireTwoNovelTransfers'):
                if int(r.get('minCorrect', 0)) < 2:
                    failures.append(f"mastery objective {r.get('objectiveId','?')} must require >=2 correct transfer items")
                if any(not (qmap.get(x) or {}).get('novelTransfer') for x in ids):
                    failures.append(f"mastery objective {r.get('objectiveId','?')} contains a non-novel-transfer gate item")

    if policy.get('requireDiagnostic'):
        has_diagnostic = any(s.get('type') == 'quiz' and (s.get('content') or {}).get('diagnostic') for s in course.get('scenes') or [])
        if not has_diagnostic:
            failures.append('required diagnostic quiz is missing')

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    args = ap.parse_args()
    if not args.html.is_file():
        print(f"FAIL: file not found: {args.html}")
        return 2
    try:
        course = extract_course(args.html.read_text(encoding="utf-8", errors="replace"))
        failures = check(course)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 2
    print(f"Mastery gate audit: {args.html}")
    if (course.get("meta") or {}).get("practicePolicy", {}).get("mode") != "mastery-loop":
        print("RESULT: PASS (not applicable; course does not declare mastery-loop)")
        return 0
    if failures:
        for f in failures:
            print("FAIL:", f)
        print(f"RESULT: FAIL ({len(failures)} failure(s))")
        return 1
    print("RESULT: PASS (independent coverage/mastery gate)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
