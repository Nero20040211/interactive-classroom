# Process Animation Contract

## 适用范围

`process-animation` 只用于让学习者观察一个知识机制随共同时间展开。静态关系、分类或构造应使用 `diagram`、`figure` 或对应的学科原生 widget；不要为了增加视觉动效而把静态内容改成过程动画。

便携 renderer 与 Modern renderer 共享同一组课程字段。时间轴控制属于 renderer，学科适配器只负责选择可观察的对象、原语和确定性模型。这样同一份 Stage/Scene 数据可以在两个 runtime 中校验，而不会把 React 状态写进课程模型。

## 配置字段

过程动画的 `content.widgetConfig` 可以声明：

- `autoplay`：默认 `true`。进入当前场景后自动播放当前时间轴一次；只有显式写 `false` 才关闭自动播放。
- `loop`：默认 `false`。只有显式写 `true` 才在末步后回到首步。
- `timeline`：可选的 `initialHoldMs`、`defaultMotionMs` 与 `defaultPauseMs`，用于控制认知上可读的停留时间。
- `actors`：带稳定 `id`、`primitive`、初始状态和语义角色的对象集合；`entities` 是兼容旧课程的别名。
- `steps`：按时间顺序排列的离散状态。每一步至少包含 `title`、`caption`、`semanticAction`、`focus`、`changeSummary`、`whyItMatters` 与按 actor id 索引的 `states`。
- `animationSemantics`：声明 `profile`、概念实体、状态变量、步骤逻辑、运动理由、误导边界及必要的 `semanticRelations`。它补充内容语义，不接管播放控制。

`states` 必须使学习者能看见实际的状态变化，例如位置、方向、大小、透明度、组成或关系变化。仅逐个显现标签、颜色或装饰节点不能满足过程动画契约。每个 SVG/Canvas 交互区都要通过 `focus` 或教学目标提供可访问名称，并在正文或 caption 中说明观察什么、变化是什么、为什么有助于当前结论。

## 学科原语适配

原语应与机制相称，并保持子图形的本地坐标稳定：

- chemistry：`molecule`、`particle` 或键/组成变化；
- biology：`pathway-token`、`particle` 或区室/信号变化；
- computer science：`pointer`、`token` 或数据结构中的具体对象；
- language：`token`、短语或句法成分；
- statistics：`point`、`distribution` 或样本状态；
- social science：`evidence-card`、主张/证据关系或因果节点；
- physics：`body`、`vector`、`track` 或适配的运动实验室。

这些适配器定义“哪个对象变化”，不改变统一的首步、末步、暂停、重播、直接选步和循环语义。未实现的 native widget 必须在生成/构建阶段显式降级到 portable 或报告能力错误；不得用 `GenericLab` 作为交付占位。

## 播放与 reduced motion

播放只作用于当前场景的时间轴，不自动翻页或跳转课程目录。两种 runtime 都应提供：

- 播放/暂停，并以 `aria-pressed` 或等价状态向辅助技术暴露；
- 重播，从首个离散状态开始；
- 上一步、下一步或逐步按钮；
- 当前步骤、观察重点、变化摘要和重要性说明。

便携 renderer 使用 `requestAnimationFrame` 在相邻状态之间采样位置、尺寸、旋转和透明度；Modern renderer 使用组件状态和本地 Motion transition 表达同一状态变化。场景离开、手动跳步、重置或参数改变时必须取消待处理的 frame/timer，避免旧场景继续写入 DOM。

当 `prefers-reduced-motion: reduce` 或学习者的 reduced-motion 设置生效时，禁止自动推进和连续插值，但保留清晰的离散状态、caption、暂停/重播和键盘操作。离散状态本身仍应足以支持学习者回答“哪一个变量变化、哪一个保持、这一步为何重要”。

## 验证门

发布前至少运行：

```powershell
python scripts/audit_animation_content_fit.py <course.json-or-html>
python scripts/test_cross_runtime_animation.py .
python scripts/validate_html.py <portable-or-modern.html> --strict
```

Modern 课程还必须通过 capability/registry 检查，并在真实浏览器中验证自动播放、暂停、重播、参数联动、键盘焦点、390 px 窄屏与离线运行。验证应分别记录静态契约结果、物理/模型采样结果和人工浏览器观察，不能把分类或静态字符串命中当作动画行为证据。
