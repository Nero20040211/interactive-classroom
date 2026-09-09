export const DEFAULT_TIMELINE = Object.freeze({
  initialHoldMs: 700,
  defaultMotionMs: 1100,
  defaultPauseMs: 650,
});

const finite = (value, fallback) =>
  Number.isFinite(Number(value)) ? Number(value) : fallback;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export function getAnimationConfig(config = {}) {
  const timeline = { ...DEFAULT_TIMELINE, ...(config.timeline || {}) };
  return {
    autoplay: config.autoplay !== false,
    loop: config.loop === true,
    timeline: {
      initialHoldMs: Math.max(0, finite(timeline.initialHoldMs, 700)),
      defaultMotionMs: Math.max(120, finite(timeline.defaultMotionMs, 1100)),
      defaultPauseMs: Math.max(0, finite(timeline.defaultPauseMs, 650)),
    },
  };
}

export function resolveStepState(config = {}, index = 0) {
  const actors = config.actors || config.entities || [];
  const steps = config.steps || [];
  const step = steps[Math.max(0, Math.min(index, steps.length - 1))] || {};
  const states = {};

  for (const actor of actors) {
    const base = {
      ...(actor.initialState || {}),
      x: actor.initialState?.x ?? actor.x,
      y: actor.initialState?.y ?? actor.y,
    };
    states[actor.id] = {
      ...base,
      ...(step.states?.[actor.id] || {}),
    };
  }

  return { step, states };
}

export function interpolateState(from = {}, to = {}, progress = 1) {
  const p = clamp(finite(progress, 1), 0, 1);
  const out = {};

  for (const key of new Set([...Object.keys(from), ...Object.keys(to)])) {
    const a = from[key];
    const b = to[key];
    out[key] =
      Number.isFinite(Number(a)) && Number.isFinite(Number(b))
        ? Number(a) + (Number(b) - Number(a)) * p
        : p < 1
          ? a
          : b;
  }

  return out;
}

export function nextTimelineIndex(index, length, loop = false) {
  if (length <= 0 || index < 0 || index >= length - 1) {
    return loop && length > 0 ? 0 : null;
  }
  return index + 1;
}
