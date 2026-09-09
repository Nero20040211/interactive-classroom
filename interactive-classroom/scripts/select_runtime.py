#!/usr/bin/env python3
"""Natural-language fast-path router for Interactive Classroom frontend selection.

The router is release-number agnostic. It only captures learner-facing runtime
intent. `auto` means the Skill should continue with the normal complexity router
in references/frontend-runtime.md.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RuntimeDecision:
    profile: str
    reason: str
    matched: str | None = None


# Explicit framework prohibition wins over every positive/complexity signal.
PORTABLE_PATTERNS = [
    r"(?:不要|不用|别用|不使用|禁止使用|不需要)\s*(?:任何)?\s*(?:react|modern(?:\s+runtime)?|tailwind|motion(?:\s+(?:库|runtime))?|框架|前端框架)",
    r"只(?:要|用)\s*(?:原生|vanilla)?\s*(?:html(?:\s*/\s*css(?:\s*/\s*js)?)?|javascript|js)",
    r"原生\s*html\s*/?\s*css\s*/?\s*(?:javascript|js)",
    r"只要(?:一个)?(?:轻量|简单)?单文件",
    r"轻量单文件",
    r"单个\s*html",
    r"零构建",
    r"无需构建",
    r"不要(?:安装|使用)\s*(?:node|npm|依赖)",
    r"\bportable\b",
    r"\bzero[- ]?build\b",
    r"\bsingle[- ]?(?:file|html)\b",
    r"\bframework[- ]?free\b",
    r"\bno\s+(?:react|frameworks?)\b",
    r"\bwithout\s+(?:react|frameworks?)\b",
    r"\bdo\s+not\s+use\s+(?:react|frameworks?)\b",
    r"\bdon['’]?t\s+use\s+(?:react|frameworks?)\b",
    r"\bvanilla\s+(?:js|javascript)\b",
]

# Avoid a naked `motion` token: it is frequently a physics topic, not the
# Motion animation library. Match the library only when the technology intent
# is explicit.
EXPLICIT_MODERN_PATTERNS = [
    r"\bmodern[- ]?react\b",
    r"\bmodern\s+runtime\b",
    r"\breact\b",
    r"\btailwind(?:\s*css)?\b",
    r"\bframer\s+motion\b",
    r"\bmotion\s+(?:library|runtime|for\s+react)\b",
    r"(?:使用|用|采用)\s*motion(?:\s*(?:库|runtime))?",
    r"(?:使用|用|采用)\s*react",
    r"组件(?:化|架构)",
    r"component\s+architecture",
]

# Avoid standalone "深度" because "深度学习" is a subject name, not a request
# for a deeper rendering profile.
DEPTH_PATTERNS = [
    # Chinese adjective + optional structural particle/pronoun + teaching noun/verb.
    # This deliberately accepts natural variants such as “详细的讲解”,
    # “详细地为我讲解”, “细致的课程”, and “深入地给我解释”.
    r"详细(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|学习|课程|教程|分析|说明)",
    r"更(?:加)?详细(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|说明)?",
    r"讲(?:得|的)?(?:更|更加)?详细(?:一点|一些)?",
    r"讲细(?:一点|一些)?",
    r"精细(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|说明)?",
    r"精讲",
    r"细致(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|说明)?",
    r"详尽(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|说明)?",
    r"深入(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|学习|说明)",
    r"深度(?:解析|讲解|课程|教程)",
    r"全面(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程|分析|说明)",
    r"系统(?:地|的)?(?:详细|深入)(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|学习)?",
    r"高质量(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程)",
    r"交互式(?:的)?详细(?:地|的)?(?:(?:为|给)我)?(?:进行)?(?:讲解|解释|课程|教程)?",
    r"可视化精讲",
    r"\bdetailed\s+(?:interactive\s+)?(?:course|explanation|lesson|tutorial|walkthrough)\b",
    r"\bin[- ]depth\s+(?:interactive\s+)?(?:course|explanation|lesson|tutorial)\b",
    r"\bdeep[- ]dive\s+(?:course|explanation|lesson|tutorial)\b",
    r"\bthorough\s+(?:interactive\s+)?(?:course|explanation|lesson|tutorial)\b",
    r"\bfine[- ]grained\s+(?:interactive\s+)?(?:course|explanation|lesson|tutorial)\b",
    r"\bcomprehensive\s+(?:interactive\s+)?(?:course|explanation|lesson|tutorial)\b",
    r"\brich(?:ly)?\s+interactive\s+(?:course|explanation|lesson|tutorial)\b",
]


def _first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def select_runtime(text: str, modern_toolchain_available: bool = True) -> RuntimeDecision:
    normalized = " ".join((text or "").strip().split())
    if not normalized:
        return RuntimeDecision("auto", "empty-request")

    portable = _first_match(PORTABLE_PATTERNS, normalized)
    if portable:
        return RuntimeDecision("portable", "explicit-portable-constraint", portable)

    modern = _first_match(EXPLICIT_MODERN_PATTERNS, normalized)
    if modern:
        if modern_toolchain_available:
            return RuntimeDecision("modern-react", "explicit-modern-stack", modern)
        return RuntimeDecision("portable", "modern-toolchain-unavailable", modern)

    depth = _first_match(DEPTH_PATTERNS, normalized)
    if depth:
        if modern_toolchain_available:
            return RuntimeDecision("modern-react", "natural-language-depth-trigger", depth)
        return RuntimeDecision("portable", "modern-toolchain-unavailable", depth)

    return RuntimeDecision("auto", "continue-complexity-routing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the Interactive Classroom runtime fast path from learner wording.")
    parser.add_argument("request", help="Learner request text")
    parser.add_argument("--no-modern-toolchain", action="store_true", help="Simulate a generation environment without the modern Node/npm toolchain")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON instead of a compact text result")
    args = parser.parse_args()
    decision = select_runtime(args.request, modern_toolchain_available=not args.no_modern_toolchain)
    if args.json:
        print(json.dumps(asdict(decision), ensure_ascii=False))
    else:
        print(decision.profile)
        print(f"reason={decision.reason}")
        if decision.matched:
            print(f"matched={decision.matched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
