# interactive-classroom-refiner v1.2

A separate opt-in sibling Skill for feeding explicit learner feedback and real-course regression evidence back into `interactive-classroom` through a reviewed maintenance workflow.

The release identifier in this README is documentation only. It does not participate in feedback validation, scope classification, promotion decisions, sibling discovery, or regression selection.

Current classrooms export the version-neutral `interactive-classroom-session-feedback` schema. The Refiner accepts current version-neutral `interactive-classroom-refinement-bundle` inputs from manual workflows. Legacy versioned bundles are not accepted directly: migrate them with `scripts/migrate_feedback_bundle.py`, then validate the current output. Neither current format is allowed to request automatic Skill mutation.

The formal `interactive-classroom.zip` archive places this Skill beside `interactive-classroom/` so Codex can discover both. The teaching Skill teaches and exports explicit feedback; this Refiner changes reusable teaching rules only after the user explicitly asks for refinement and the proposed change survives the relevant regression evidence.

Reusable changes are guarded by a validated dry-run refinement plan, scoped path allowlists, regression requirements, and a privacy-minimized decision-log validator.
