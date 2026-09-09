# Proof Practice Contract 

`widgetType: proof-practice` is practice, not exposition. Teach the proof/derivation first using semantic proof blocks or a worked derivation.

Modes:
- `ordering`: `steps[{id,text}]` + `answer:[stepIds...]`.
- `reason-match`: `steps[{id,text}]` + `reasons[{id,text}]` + `answer:{stepId:reasonId}`.

Use at least three stable steps. Each step should correspond to one non-trivial inference. Feedback explains the dependency error rather than only saying wrong. Appropriate for mathematics, theoretical CS, selected physics derivations, statistics and AI correctness/optimality arguments. Do not force formal proof practice onto empirical biology or descriptive chemistry.
