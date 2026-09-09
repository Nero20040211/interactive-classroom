import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { getAnimationConfig, interpolateState, nextTimelineIndex } from "../assets/modern-runtime/src/animation-contract.js";

const fixture = JSON.parse(await readFile(new URL("./fixtures/animation-contract.json", import.meta.url), "utf8"));
assert.equal(fixture.cases.length, 6);
for (const item of fixture.cases) {
  const cfg = getAnimationConfig(item);
  assert.equal(cfg.autoplay, true, item.id);
  assert.ok(cfg.timeline.defaultMotionMs >= 800, item.id);
  const start = item.actors[0].initialState;
  const end = item.steps[0].states[item.actors[0].id];
  const mid = interpolateState(start, end, 0.5);
  assert.notDeepEqual(mid, start, item.id);
  assert.notDeepEqual(mid, end, item.id);
  assert.equal(nextTimelineIndex(0, 1, false), null, item.id);
}
assert.equal(nextTimelineIndex(2, 3, true), 0);
console.log("ANIMATION CONTRACT RESULT: PASS");
