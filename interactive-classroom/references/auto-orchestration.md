# Auto Orchestration — Natural-language Learning

Use this reference when the learner provides only a topic or a broad learning goal.

## Trigger

Examples: “我要学习密码学”, “教我概率论”, “我想系统学 JavaScript”, “带我复习中国古代史”.

Treat these as `ic-learn` automatically. Never require the user to name the skill, mode, widget, agent roster, discipline profile, output filename, or validation command.

### Modern Runtime depth trigger

If the same learning request explicitly asks for a detailed/fine-grained/in-depth course — for example “详细讲解…课程”, “详细的讲解…”, “详细地为我讲解…”, “精细讲解…”, “深入/详尽/高质量讲解…”, or “detailed / in-depth / thorough interactive course” — route to `modern-react` before ordinary complexity routing, unless the learner explicitly asks for portable/zero-build/no-React output. Use `scripts/select_runtime.py` as the deterministic fast-path reference.

## Default inference

When unspecified:

- level: foundation → intermediate;
- length: compact complete lesson/course, normally 6–10 scenes;
- language: user's language;
- runtime: one self-contained offline HTML;
- evidence: standard domain knowledge plus user-provided sources when present;
- roles: Teacher + only peers that add value;
- widgets: chosen by objective, never by showcase value;
- assessment: after instruction, with at least one transfer/application item for reasoning objectives.

## Topic routing examples

- cryptography → primary formal/quantitative + computational/data; use diagram/equation/code/game selectively; teach threat model, primitive purpose and assumptions before exercises.
- calculus → formal/quantitative; equation + diagram/simulation + numeric/step assessment.
- physics → physical/experimental; concept explanation + diagram + simulation + numeric interpretation.
- programming → computational/data; execution-model explanation + code trace/debugging + state diagram + output prediction.
- history → historical/interpretive; context explanation + timeline/source annotation + competing interpretations + evidence-based reflection.
- language learning → language/communication; explanation + annotated examples + bounded practice + ordering/matching/self-rubric.

## Scope control

If a topic is enormous, do not ask “which part?” by default. Generate a foundation map, teach the first coherent layer, and show the chosen scope in orientation. The user can later request deeper modules.

## Quality invariant

A learner should encounter the authored knowledge explanation before the core interaction in each substantial learning scene. Interactivity may deepen or test understanding, but it must not be the only carrier of the concept.

## automatic interaction decision

After building the learning map, ask three additional questions per core concept:

1. Does the explanation contain substantive symbolic relations? If yes, route them to structured MathML formula atoms; do not leave equations in prose.
2. Does the mechanism unfold through stages, flow, or state transitions? If yes, consider a staged animated diagram with learner-controlled playback.
3. Does the concept contain meaningful learner-changeable parameters? If yes, prefer a deterministic adjustable experiment over a fixed demonstration.

Do not use all three merely because the runtime supports them.
