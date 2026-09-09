# Discipline Router

Run this before designing a substantial classroom. The goal is not to label the learner; it is to select appropriate representations, practice and assessment.

## 1. Formal / quantitative

Examples: mathematics, logic, theoretical computer science, cryptographic mathematics, quantitative economics.

Prioritize:
- `equation` for derivation/proof steps;
- `diagram` for dependency/proof structure;
- `simulation` for functions/parameter intuition;
- numeric / ordering / step-selection assessment;
- explicit notation and assumptions.

Avoid treating symbolic derivation as a prose discussion problem.

## 2. Physical / experimental

Examples: physics, chemistry, engineering.

Prioritize:
- `simulation` with units and assumptions;
- `visualization3d` for structures/spatial systems;
- `diagram` for forces, circuits, processes;
- `procedural-skill` for lab procedures;
- numeric tolerance, prediction and graph interpretation.

Require dimensional/unit checks where relevant. Never invent physical constants or lab results.

## 3. Life / clinical

Examples: biology, anatomy, physiology, medicine, health sciences.

Prioritize:
- `visualization3d` / `annotation` for structure;
- `diagram` for pathways;
- `data-lab` for experimental/clinical data interpretation;
- case-based PBL;
- `procedural-skill` only as educational simulation.

For medical/clinical content, clearly distinguish education from diagnosis/treatment/certification and preserve source uncertainty.

## 4. Computational / data

Examples: programming, algorithms, statistics, data science, applied cryptography/security engineering.

Prioritize:
- `code` for tracing/debugging/output prediction;
- `diagram` for state machines, call graphs, algorithms;
- `data-lab` for datasets/statistical reasoning;
- `simulation` for probabilistic/algorithmic behavior;
- code-output, numeric and classification assessment.

Do not claim arbitrary code was executed unless a real embedded runtime was used.

## 5. Social / decision

Examples: sociology, communication, political science, economics, management, policy, law.

Prioritize:
- discussion / debate;
- `diagram` for mechanisms/institutions;
- `data-lab` for empirical evidence;
- PBL for decisions/tradeoffs;
- timeline for policy/history;
- evidence and counterexample review.

Distinguish normative claims from empirical claims.

## 6. Historical / interpretive

Examples: history, philosophy, literature, cultural studies.

Prioritize:
- timelines;
- source comparison;
- `annotation` for passages/documents/images;
- discussion with competing interpretations;
- argument maps;
- evidence-based explain-back.

Do not turn contested interpretation into deterministic “one correct answer” unless the learning target is factual recall.

## 7. Language / communication

Examples: second-language learning, grammar, rhetoric, writing.

Prioritize:
- dialogue;
- `game` for bounded practice;
- ordering/matching/cloze-like deterministic tasks;
- `annotation` for sentence/text structure;
- `media` only if actual embedded audio/video exists;
- self-rubric for open writing/speaking.

Do not claim pronunciation or semantic quality was AI-graded offline.

## 8. Visual / spatial / creative

Examples: geography, art, design, architecture.

Prioritize:
- `visualization3d`;
- `annotation`;
- `diagram`;
- spatial comparison;
- embedded source images where available;
- critique prompts + self-rubric.

A generic node graph is not a substitute for real spatial/image evidence.

## 9. Procedural / vocational

Examples: lab technique, manufacturing, maintenance, clinical skills training, field procedures.

Prioritize:
- `procedural-skill`;
- PBL scenarios;
- ordered steps;
- checkpoints;
- hazard/constraint callouts;
- decision logs.

Never imply that browser completion grants real-world qualification.

## Mixed courses

A course can combine profiles. Example: econometrics = formal + computational/data + social/decision. Choose one primary profile and 1–2 secondary profiles, then use widget types by learning objective, not by course label.


## Knowledge-first adaptation

Routing selects representations, but every route still needs explicit explanation. Before any specialized widget, state the underlying concept, notation/assumptions, a concrete example or evidence, common mistake/boundary, and the learning takeaway.

### Cryptography recipe

For a broad request such as “我要学习密码学”:

- primary: formal/quantitative; secondary: computational/data;
- foundation sequence: goals/threat model → symmetric encryption → public-key idea → hashes/MACs/signatures → key exchange/protocol composition → practice;
- prioritize diagrams for primitive relationships/protocol flow, equations for modular arithmetic when needed, code-trace only for safe toy/educational algorithms, and misconception checks such as “hash ≠ encryption” and “encoding ≠ encryption”;
- explicitly separate mathematical toy examples from production cryptographic security.


## subject-specific routing additions

- High-school physics / engineering basics: when equations are central, pair MathML exposition with `quantity-lab`; state SI unit and dimension where useful, and teach that dimensional consistency is necessary but not sufficient.
- High-school chemistry: use `chemistry` for balancing/atom conservation with structured compound compositions; keep chemical identity fixed and adjust coefficients only.
- Biology: emphasize structure → process → function → evidence. Prefer diagrams/annotation over theorem language unless the topic is genuinely formal.
- Machine learning/data science: pair equations with `data-lab`; label synthetic data and separate predictive association from causal claims.
- Artificial intelligence/theoretical algorithms: definitions/invariants/theorems may use textbook semantics; use `proof-practice` only after the proof/derivation is taught.

## interaction defaults by discipline

- **formal / quantitative:** strict structured MathML for every substantive relation; use equation/proof-practice rather than prose equations.
- **physical / experimental:** prefer adjustable quantities/simulations with units and deterministic recalculation when variables are meaningful.
- **life / clinical:** use staged explanatory diagrams for directional/process mechanisms when sequence is central; do not animate merely for decoration.
- **computational / data:** prefer adjustable data/model parameters with live metrics when teaching fitting, optimization, thresholds, or trade-offs.
- **chemistry inside physical/experimental:** use structured compounds/reactions; for balancing, expose coefficient adjustment without changing formula subscripts.
- **historical / interpretive / language:** animation and sliders are optional and should not be forced when the epistemic task is evidence interpretation or close reading.


## pack routing

After assigning the broad profile, resolve a concrete `meta.disciplinePack` and read `discipline-packs/<id>/PACK.md`. Preferred mapping: formal/quantitative→mathematics or statistics; physical/experimental→physics or chemistry; life/clinical→biology (medical courses additionally need safety boundaries); computational/data→computer-science or ml-ai; social/decision→social-science; historical/interpretive→humanities; language/communication→language; visual/spatial geography→geography; procedural/vocational→procedural-vocational.
