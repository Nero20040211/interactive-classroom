# Interactive Classroom

面向 Codex 的离线、知识优先、跨学科交互课堂 Skill 组合：一个 Skill 负责生成课程，另一个负责在明确请求后审查反馈并改进可复用规则。

## 两个 Skill，两个职责

| Skill | 职责 |
| --- | --- |
| [`interactive-classroom`](./interactive-classroom/) | 根据学习意图生成并交付知识优先的 Stage/Scene 交互课程与离线 HTML。 |
| [`interactive-classroom-refiner`](./interactive-classroom-refiner/) | 接收明确的学习反馈和回归证据，审查问题、形成可验证的改进计划，并在获得明确请求后改进interactive-classroom Skill。 |

两个 Skill 保持分离：学习者答错或留下反馈不会自动修改 interactive-classroom Skill。

## 工作流

请求主题 → 课程大纲 → 深度场景与交互 → 单文件离线 HTML → 显式学习反馈 → reviewed refinement

## 核心能力

- 知识优先：先建立前置知识、概念、机制、例题与边界，再进入练习。
- 跨学科课程：支持数学、物理、化学、生物、统计、ML/AI、计算机科学、地理、语言、人文与社会科学等方向。
- 两种运行档案：按意图和复杂度选择 portable 或 modern-react，并共享稳定的 Stage/Scene 学习模型。
- 可验证交互：原理揭示型动画、学科原生小组件、结构化数学、来源与引用、练习进阶和学习反馈导出。

## 快速开始

将两个目录复制到用户级 Codex Skills 目录：

```text
Windows: %USERPROFILE%\.codex\skills\interactive-classroom
Windows: %USERPROFILE%\.codex\skills\interactive-classroom-refiner
macOS/Linux: ~/.codex/skills/interactive-classroom
macOS/Linux: ~/.codex/skills/interactive-classroom-refiner
```

然后在 Codex 中直接提出自然语言请求，例如：

- `我要学习密码学`
- `请精细讲解二分查找，并做成交互课程`
- `请根据这门课的学习反馈优化 interactive-classroom`

## portable 与 modern-react

- **portable**：零构建、单文件 HTML，适合轻量课程；明确说 `portable`、`zero-build`、`不要 React` 或“只要轻量单文件”可强制选择它。
- **modern-react**：在生成阶段使用本地 React、Tailwind CSS 与 Motion 工具链，编译成单个离线 HTML；详细、深入、状态密集或动画丰富的课程可触发该档案。工具链不可用时应回退到 portable 并说明。

学习者收到的是 HTML 交付物，不需要在浏览器端构建项目。

## 离线与隐私边界

严格离线运行默认不需要服务器、外部 LLM API key、CDN、远程脚本或样式、fetch、WebSocket、分析服务或隐藏的实时模型。课程可在生成阶段使用本地工具链；这不改变学习者运行时的离线边界。开放式文字作答属于自我诊断，除非用户明确接入真实模型。

## 验证入口

在 [`interactive-classroom`](./interactive-classroom/) 目录中运行静态发布检查：

```bash
python scripts/validate_skill.py .
python scripts/validate_frontend_runtime.py .
python scripts/test_runtime_routing.py
python scripts/test_cross_runtime_animation.py
python scripts/run_regression.py
python scripts/test_negative_gates.py
```

便携课程还可运行 `scripts/render_course.py`、`scripts/validate_html.py --strict` 和 `scripts/validate_mastery_gate.py`。Refiner 的反馈、计划、决策日志和 Skill 检查入口位于 [`interactive-classroom-refiner/scripts/`](./interactive-classroom-refiner/scripts/)。

## 目录导航

- [Teaching Skill README](./interactive-classroom/README.md) · [SKILL.md](./interactive-classroom/SKILL.md)
- [Refiner Skill README](./interactive-classroom-refiner/README.md) · [SKILL.md](./interactive-classroom-refiner/SKILL.md)
- [Teaching references](./interactive-classroom/references/)
- [Teaching scripts](./interactive-classroom/scripts/)
- [Refiner references](./interactive-classroom-refiner/references/)
- [Refiner scripts](./interactive-classroom-refiner/scripts/)

## 限制、许可证与贡献提示

这是面向 Codex 的本地 Skill 组合，不提供实时在线课堂服务；modern-react 的生成阶段构建也不等于学习者运行时联网。两个 Skill 均采用 MIT 许可证，详见 [`interactive-classroom/LICENSE.txt`](./interactive-classroom/LICENSE.txt) 和 [`interactive-classroom-refiner/LICENSE.txt`](./interactive-classroom-refiner/LICENSE.txt)。
