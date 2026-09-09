# OpenMAIC Alignment Notes

This Skill is an original Codex/offline implementation inspired by public OpenMAIC architecture and product concepts. It does not vendor OpenMAIC code.

## Adopted architectural ideas

| OpenMAIC concept | adaptation |
|---|---|
| Outline → scene generation pipeline | Two-stage planning: route/outline first, then specialized scene generation |
| Stage/Scene lesson skeleton | Lightweight embedded Stage/Scene course model with stable IDs |
| Slide / Quiz / Interactive / PBL | High-level scene families, with `interactive.widgetType` |
| Deep Interactive Mode widget types | `simulation`, `visualization3d`, `game`, `code`, `diagram`; plus offline extensions |
| PBL | roles, mission, resources, milestones/microtasks, deterministic state/effects, debrief |
| Stage-level classroom agents | generation-time roster compiled into symbolic role identities |
| Agent → widget actions | local Action Bus: highlight/select/set-state/reveal/reset/focus |
| Playback/action timeline | per-scene ordered action list with manual teacher-guidance playback |
| Edit with AI / scene patching | `ic-revise` preserves stable IDs and prefers atomic scene-level changes |
| Offline-ready interactive export | strict self-contained HTML with embedded assets/data only |
| Vocational procedural widgets | `procedural-skill` widget with steps/checkpoints/hazards/remediation |

## Deliberately not adopted by default

- OpenMAIC server/runtime;
- provider configuration or LLM API keys;
- PostgreSQL or server-backed sessions;
- React renderer/editor dependency;
- remote TTS/ASR/image/video providers;
- cloud web search inside the classroom;
- live free-form AI chat inside the HTML;
- external Three.js/KaTeX/CDN dependencies.

If the user explicitly accepts a non-strict-offline build, those boundaries may be relaxed deliberately, but never silently.

## Compatibility principle

Keep the internal model conceptually close enough to OpenMAIC that later export/migration is feasible:

- `Course → Stage → Scene`;
- stable IDs;
- high-level scene family;
- `interactive.widgetType`;
- `actions[]` as an ordered instruction set;
- stage roster;
- PBL config separate from learner runtime state.

Do not claim byte/schema compatibility with `@openmaic/dsl` unless a real converter is implemented and tested.
