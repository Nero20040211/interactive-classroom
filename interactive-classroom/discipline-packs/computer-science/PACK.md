# 计算机科学 Discipline Pack

Pack ID: `computer-science`

Status: **validated-native**

## Native learning language

Preferred: `code`, `data-structure-lab`, `recursion-lab`, `complexity-lab`, diagram and procedural-skill. Distinguish source text, runtime state, abstract data type semantics, call-stack state and asymptotic model.

## Required integrity

- Code tracing is deterministic and never presented as real Python/Java execution unless a real local runtime exists.
- Stack uses LIFO; queue uses FIFO. Operations and state must stay visible.
- Recursion lessons identify a base case and show call/return frames, not only repeated text.
- Complexity labs label counts as an abstract operation-growth model, not measured wall-clock speed. Big-O claims state assumptions and use valid model kinds.
- Algorithm/data-structure exercises should ask learners to predict state before revealing the next state when appropriate.

## Native regression

The bundled regression suite validates algorithm-state reasoning, while strict gates separately validate stack/queue invariants, recursion/call-stack configuration, and asymptotic-growth models when those widgets are used.


## animation profile

Prefer stack/array/pointer state or native recursion/search/data-structure labs. Runtime invariants and execution order govern motion.
