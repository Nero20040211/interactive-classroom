#!/usr/bin/env python3
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
from select_runtime import select_runtime

CASES = [
    # Natural-language depth signals.
    ("我需要一个详细讲解高中物理平抛运动的课程", "modern-react"),
    ("我需要一个详细的讲解物理抛物线运动的课程", "modern-react"),
    ("请详细地为我讲解平抛运动", "modern-react"),
    ("为我进行详细的讲解：牛顿第二定律", "modern-react"),
    ("给我一个细致的讲解，主题是动量守恒", "modern-react"),
    ("请深入地给我解释傅里叶变换", "modern-react"),
    ("给我一个详尽的课程讲清楚概率分布", "modern-react"),
    ("请做一个高质量的讲解，主题是 Transformer", "modern-react"),
    ("请精细讲解二分查找，并做成交互课程", "modern-react"),
    ("给我一个深入讲解细胞呼吸的可视化课程", "modern-react"),
    ("请做一份详尽讲解概率论的课程", "modern-react"),
    ("牛顿第二定律讲得更详细一点", "modern-react"),
    ("把递归讲细一点，做成课程", "modern-react"),
    ("我想要高质量讲解 Transformer 的课程", "modern-react"),
    ("I want a detailed interactive course on linear algebra", "modern-react"),
    ("Give me an in-depth explanation of recursion", "modern-react"),
    # Explicit modern technology requests.
    ("Use React and Motion library to teach projectile motion", "modern-react"),
    ("用 React 和 Tailwind 做这门课", "modern-react"),
    ("请采用 Framer Motion 做交互动画", "modern-react"),
    # Ambiguity / negative controls.
    ("我要学习密码学", "auto"),
    ("我想学习深度学习", "auto"),
    ("简单讲一下牛顿第二定律", "auto"),
    ("Teach me motion in one dimension", "auto"),
    ("I want to understand motion and forces", "auto"),
    # Portable constraints must beat depth/technology mentions.
    ("我需要详细讲解平抛运动，但不要 React，只要轻量单文件", "portable"),
    ("详细讲解平抛运动，别用 React", "portable"),
    ("详细的讲解平抛运动，但别用 React", "portable"),
    ("请详细地为我讲解递归，不过不使用任何框架", "portable"),
    ("详细讲解概率论，不使用任何框架", "portable"),
    ("精讲二分查找，只用原生 HTML/CSS/JS", "portable"),
    ("深入讲解递归，vanilla JS", "portable"),
    ("Give me a detailed course on mitosis, but use portable zero-build output", "portable"),
    ("Detailed explanation of photosynthesis, do not use React", "portable"),
    ("In-depth course on algorithms without frameworks", "portable"),
    ("Use React for a detailed course, but actually make it framework-free", "portable"),
]

for text, expected in CASES:
    got = select_runtime(text).profile
    if got != expected:
        raise SystemExit(f"FAIL: {text!r}: expected {expected}, got {got}")

fallback = select_runtime("请精细讲解二分查找", modern_toolchain_available=False)
if fallback.profile != "portable" or fallback.reason != "modern-toolchain-unavailable":
    raise SystemExit(f"FAIL: toolchain fallback incorrect: {fallback}")

print(f"RUNTIME ROUTING: PASS ({len(CASES)} prompt cases + toolchain fallback)")
