import React, { useEffect, useMemo, useRef, useState } from "react";
import { useReducedMotion } from "motion/react";
import * as m from "motion/react-m";
import {
  getAnimationConfig,
  nextTimelineIndex,
  resolveStepState,
} from "./animation-contract.js";
import { projectileState, sampleProjectile } from "./model-contract.js";

const panel =
  "rounded-xl border border-black/10 bg-black/[0.02] p-4 dark:border-white/15 dark:bg-white/[0.035]";
const button =
  "min-h-10 rounded-lg border border-black/15 px-3 py-2 text-sm dark:border-white/20";
const warning =
  "rounded-lg border border-amber-700/25 bg-amber-500/[0.07] p-3 text-sm dark:border-amber-300/25";

function cfgOf(scene) {
  return scene?.content?.widgetConfig || {};
}

function num(value, fallback = 0) {
  const result = Number(value);
  return Number.isFinite(result) ? result : fallback;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function textOf(value, fallback = "未声明") {
  if (value == null || value === "") return fallback;
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) return value.map((item) => textOf(item, "")).filter(Boolean).join("；");
  if (typeof value === "object") {
    return textOf(value.text ?? value.body ?? value.prompt ?? value.evidenceQuestion ?? value.label ?? value.title ?? value.spoken, fallback);
  }
  return fallback;
}

function TextValue({ value, fallback = "未声明" }) {
  if (Array.isArray(value)) {
    return (
      <>
        {value.map((item, index) => (
          <React.Fragment key={index}>
            {index ? <br /> : null}
            <TextValue value={item} fallback={fallback} />
          </React.Fragment>
        ))}
      </>
    );
  }
  return <>{textOf(value, fallback)}</>;
}

const mathTags = new Set([
  "math",
  "mrow",
  "mi",
  "mn",
  "mo",
  "mtext",
  "mspace",
  "mfrac",
  "msqrt",
  "mroot",
  "msup",
  "msub",
  "msubsup",
  "munder",
  "mover",
  "munderover",
  "mtable",
  "mtr",
  "mtd",
  "menclose",
  "semantics",
  "annotation",
]);

function formulaText(value) {
  if (value == null) return "";
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (typeof value === "object") {
    return textOf(value.tex ?? value.expression ?? value.text ?? value.spoken ?? value.formula, "");
  }
  return "";
}

function sanitizeMathML(value) {
  const raw = typeof value === "object" ? value?.mathml : value;
  if (typeof raw !== "string" || !raw.trim() || typeof DOMParser === "undefined") return "";
  const doc = new DOMParser().parseFromString(raw, "application/xml");
  if (doc.querySelector("parsererror") || doc.documentElement?.localName !== "math") return "";
  const root = doc.documentElement;
  for (const element of [root, ...root.querySelectorAll("*")]) {
    if (!mathTags.has(element.localName)) return "";
    for (const attribute of [...element.attributes]) {
      const name = attribute.name.toLowerCase();
      if (name.startsWith("on") || ["href", "xlink:href", "src", "style"].includes(name)) {
        element.removeAttribute(attribute.name);
      }
    }
  }
  return new XMLSerializer().serializeToString(root);
}

function FormulaView({ value, label = "公式" }) {
  const safe = useMemo(() => sanitizeMathML(value), [value]);
  return (
    <div className="ic-formula-block overflow-x-auto rounded-lg border border-black/10 bg-white/50 p-3 dark:border-white/10 dark:bg-black/10">
      <span className="sr-only">{label}</span>
      {safe ? (
        <span className="ic-math" dangerouslySetInnerHTML={{ __html: safe }} />
      ) : (
        <code className="whitespace-pre-wrap text-sm">{formulaText(value) || "未声明公式"}</code>
      )}
    </div>
  );
}

function parameterSource(cfg) {
  const source = cfg?.parameters;
  if (!source || Array.isArray(source)) return {};
  return source;
}

function declaredParameter(cfg, id, fallback) {
  const source = Array.isArray(cfg?.parameters)
    ? cfg.parameters.find((item) => item?.id === id || item?.key === id)
    : null;
  const model = cfg?.model?.parameters || {};
  const objectValue = parameterSource(cfg)[id];
  return source?.initial ?? source?.value ?? model[id] ?? objectValue ?? cfg?.[id] ?? fallback;
}

const projectileDefaults = Object.freeze({
  v0: { id: "v0", label: "初速度 v₀", unit: "m/s", initial: 8, min: 0, max: 24, step: 0.5 },
  h: { id: "h", label: "初始高度 h", unit: "m", initial: 12, min: 1, max: 48, step: 0.5 },
  g: { id: "g", label: "重力加速度 g", unit: "m/s²", initial: 9.8, min: 1, max: 20, step: 0.1 },
});

function projectileParameterDefinitions(cfg) {
  return Object.values(projectileDefaults).map((fallback) => {
    const declared = Array.isArray(cfg?.parameters)
      ? cfg.parameters.find((item) => item?.id === fallback.id || item?.key === fallback.id)
      : null;
    return {
      ...fallback,
      ...(declared || {}),
      min: num(declared?.min, fallback.min),
      max: num(declared?.max, fallback.max),
      step: num(declared?.step, fallback.step),
    };
  });
}

function projectileParameters(cfg) {
  return {
    v0: num(declaredParameter(cfg, "v0", projectileDefaults.v0.initial), projectileDefaults.v0.initial),
    h: num(declaredParameter(cfg, "h", projectileDefaults.h.initial), projectileDefaults.h.initial),
    g: num(declaredParameter(cfg, "g", projectileDefaults.g.initial), projectileDefaults.g.initial),
  };
}

function axisMax(value, fallback) {
  if (Array.isArray(value)) return Math.max(1, num(value[1], fallback));
  return Math.max(1, num(value, fallback));
}

function graphPoints(values, xAccessor, yAccessor, xMax, yMin, yMax, bounds) {
  const width = bounds.right - bounds.left;
  const height = bounds.bottom - bounds.top;
  return values
    .map((item) => {
      const x = clamp(num(xAccessor(item), 0) / Math.max(0.0001, xMax), 0, 1);
      const y = clamp((num(yAccessor(item), 0) - yMin) / Math.max(0.0001, yMax - yMin), 0, 1);
      return `${(bounds.left + x * width).toFixed(2)},${(bounds.bottom - y * height).toFixed(2)}`;
    })
    .join(" ");
}

function chartFrame({ title, children, ariaLabel }) {
  return (
    <svg
      viewBox="0 0 760 340"
      role="img"
      aria-label={ariaLabel || title}
      className="w-full rounded-xl border border-black/10 bg-white/50 dark:border-white/10 dark:bg-black/10"
    >
      <title>{title}</title>
      {children}
    </svg>
  );
}

function Arrow({ x1, y1, x2, y2, color = "currentColor", opacity = 0.8 }) {
  const length = Math.hypot(x2 - x1, y2 - y1) || 1;
  const ux = (x2 - x1) / length;
  const uy = (y2 - y1) / length;
  const size = 7;
  return (
    <g opacity={opacity} stroke={color} fill={color}>
      <line x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="2.5" />
      <path
        d={`M ${x2} ${y2} L ${x2 - ux * size - uy * size * 0.65} ${y2 - uy * size + ux * size * 0.65} L ${x2 - ux * size + uy * size * 0.65} ${y2 - uy * size - ux * size * 0.65} Z`}
      />
    </g>
  );
}

function PrimitiveActor({ actor, state, reduced, motionMs }) {
  const primitive = String(actor?.primitive || actor?.type || "node").toLowerCase();
  const x = num(state?.x, num(actor?.x, 100));
  const y = num(state?.y, num(actor?.y, 180));
  const rotate = num(state?.rotate ?? state?.rotation, num(actor?.rotate ?? actor?.rotation, 0));
  const scale = Math.max(0.01, num(state?.scale, num(actor?.scale, 1)));
  const opacity = clamp(num(state?.opacity, num(actor?.opacity, 1)), 0, 1);
  const label = textOf(state?.label ?? state?.face ?? actor?.label ?? actor?.name ?? actor?.id, "对象");
  const semanticLabel = textOf(
    state?.focus ?? state?.teachingGoal ?? actor?.focus ?? actor?.teachingGoal ?? actor?.semanticRole ?? label,
    label,
  );
  const width = Math.max(12, num(actor?.w, 72));
  const height = Math.max(12, num(actor?.h, 54));
  const duration = reduced ? 0 : Math.max(0.08, num(motionMs, 1100) / 1000);

  let children;
  if (primitive === "zone") {
    children = (
      <>
        <rect x={-width / 2} y={-height / 2} width={width} height={height} rx="18" fill="currentColor" fillOpacity=".055" stroke="currentColor" strokeDasharray="8 6" strokeWidth="2" />
        <text x="0" y={-height / 2 + 23} textAnchor="middle" fontSize="15" fontWeight="600">
          {label}
        </text>
      </>
    );
  } else if (primitive === "track") {
    const x2 = num(actor?.length ?? actor?.x2 ?? state?.length, 300);
    const y2 = num(actor?.dy ?? actor?.y2 ?? state?.dy, 0);
    children = (
      <>
        <line x1="0" y1="0" x2={x2} y2={y2} stroke="currentColor" strokeWidth="3" strokeDasharray="9 7" opacity=".45" />
        {label ? <text x={x2 / 2} y={y2 / 2 - 8} textAnchor="middle" fontSize="13">{label}</text> : null}
      </>
    );
  } else if (primitive === "vector" || primitive === "pointer") {
    const length = num(state?.length ?? actor?.length, 100);
    const dy = num(state?.dy ?? actor?.dy, 0);
    children = (
      <>
        <Arrow x1="0" y1="0" x2={length} y2={dy} />
        {label ? <text x={length + 9} y={dy + 5} fontSize="14">{label}</text> : null}
      </>
    );
  } else if (primitive === "molecule") {
    const atoms = actor?.atoms || actor?.particles || [
      { id: "a", x: -24, y: 0, label: "A" },
      { id: "b", x: 24, y: 0, label: "B" },
    ];
    const bonds = actor?.bonds || (atoms.length > 1 ? [{ from: atoms[0].id, to: atoms[1].id }] : []);
    const byId = Object.fromEntries(atoms.map((atom, index) => [atom.id ?? index, atom]));
    children = (
      <>
        {bonds.map((bond, index) => {
          const from = byId[bond.from] || atoms[bond.from];
          const to = byId[bond.to] || atoms[bond.to];
          if (!from || !to) return null;
          return <line key={`bond-${index}`} x1={num(from.x)} y1={num(from.y)} x2={num(to.x)} y2={num(to.y)} stroke="currentColor" strokeWidth="7" opacity=".5" />;
        })}
        {atoms.map((atom, index) => (
          <g key={atom.id ?? index}>
            <circle cx={num(atom.x)} cy={num(atom.y)} r={num(atom.r, 17)} fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />
            <text x={num(atom.x)} y={num(atom.y) + 5} textAnchor="middle" fontSize="12">{atom.label ?? atom.id ?? index + 1}</text>
          </g>
        ))}
      </>
    );
  } else if (primitive === "particle") {
    children = <circle cx="0" cy="0" r={num(actor?.r, 18)} fill="currentColor" />;
  } else if (primitive === "pathway-token") {
    children = (
      <>
        <circle cx="0" cy="0" r={num(actor?.r, 18)} fill="var(--ic-paper)" stroke="currentColor" strokeWidth="3" />
        <path d="M -7 0 L 0 7 L 10 -8" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </>
    );
  } else if (primitive === "token") {
    children = (
      <>
        <rect x={-width / 2} y={-height / 2} width={width} height={height} rx="12" fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />
        <text x="0" y="5" textAnchor="middle" fontSize="14">{label}</text>
      </>
    );
  } else if (primitive === "point") {
    children = <><circle cx="0" cy="0" r={num(actor?.r, 10)} fill="currentColor" /><text x="13" y="5" fontSize="13">{label}</text></>;
  } else if (primitive === "evidence-card") {
    children = (
      <>
        <rect x={-width / 2} y={-height / 2} width={width} height={height} rx="10" fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />
        <line x1={-width / 2 + 12} y1={-8} x2={width / 2 - 12} y2={-8} stroke="currentColor" strokeWidth="2" opacity=".6" />
        <line x1={-width / 2 + 12} y1={8} x2={width / 2 - 22} y2={8} stroke="currentColor" strokeWidth="2" opacity=".45" />
        <text x="0" y={height / 2 + 18} textAnchor="middle" fontSize="13">{label}</text>
      </>
    );
  } else if (primitive === "body") {
    children = <rect x={-width / 2} y={-height / 2} width={width} height={height} rx="14" fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />;
  } else if (primitive === "die") {
    children = (
      <>
        <rect x={-width / 2} y={-height / 2} width={width} height={height} rx="12" fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />
        <text x="0" y="6" textAnchor="middle" fontSize="25" fontWeight="700">{label}</text>
      </>
    );
  } else {
    children = (
      <>
        <circle cx="0" cy="0" r={num(actor?.r, Math.min(width, height) / 2 || 24)} fill="var(--ic-paper)" stroke="currentColor" strokeWidth="2" />
        <text x="0" y="5" textAnchor="middle" fontSize="14">{label}</text>
      </>
    );
  }

  return (
    <m.g
      animate={{ x, y, rotate, scale, opacity }}
      transition={{ duration, ease: "easeInOut" }}
      role="img"
      aria-label={semanticLabel}
    >
      {children}
    </m.g>
  );
}

export function ProcessAnimationWidget({ scene }) {
  const cfg = cfgOf(scene);
  const steps = Array.isArray(cfg.steps) ? cfg.steps : [];
  const actors = Array.isArray(cfg.actors || cfg.entities) ? cfg.actors || cfg.entities : [];
  const reduced = useReducedMotion();
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(() => getAnimationConfig(cfg).autoplay && !reduced);
  const { step, states } = resolveStepState(cfg, stepIndex);
  const animationConfig = useMemo(() => getAnimationConfig(cfg), [cfg]);
  const missingSemantic = ["focus", "changeSummary", "whyItMatters"].filter(
    (field) => !String(step?.[field] ?? "").trim(),
  );

  useEffect(() => {
    if (reduced && playing) setPlaying(false);
  }, [playing, reduced]);

  useEffect(() => {
    if (reduced || !playing || !steps.length) return undefined;
    const timing = animationConfig.timeline;
    const delay = Number(step.motionMs) || timing.defaultMotionMs;
    const timer = setTimeout(() => {
      const next = nextTimelineIndex(stepIndex, steps.length, animationConfig.loop);
      if (next == null) setPlaying(false);
      else setStepIndex(next);
    }, delay + timing.defaultPauseMs);
    return () => clearTimeout(timer);
  }, [animationConfig, playing, reduced, cfg, stepIndex, steps.length, step?.motionMs]);

  const moveTo = (index) => {
    setStepIndex(clamp(index, 0, Math.max(0, steps.length - 1)));
    setPlaying(false);
  };

  return (
    <section className={panel} data-modern-widget="process-animation" data-modern-runtime="timeline-autoplay-reduced-motion">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">{cfg.title || "原理过程动画"}</h3>
          {cfg.principle ? <p className="mt-1 text-sm opacity-75">原理：{cfg.principle}</p> : null}
        </div>
        <span className="text-xs opacity-60">步骤 {steps.length ? stepIndex + 1 : 0}/{steps.length}</span>
      </div>

      {missingSemantic.length ? (
        <p className={`${warning} mt-4`} role="alert">
          此步骤的过程语义不完整，缺少：{missingSemantic.join("、")}。生成阶段必须补齐这些字段。
        </p>
      ) : null}

      <svg
        viewBox={cfg.canvas?.viewBox || "0 0 800 380"}
        role="img"
        aria-label={step?.focus || cfg.teachingGoal || cfg.title || "过程动画"}
        className="mt-4 w-full rounded-xl border border-black/10 bg-white/50 dark:border-white/10 dark:bg-black/10"
      >
        <title>{step?.focus || cfg.teachingGoal || cfg.title || "过程动画"}</title>
        {actors.map((actor) => (
          <PrimitiveActor
            key={actor.id}
            actor={actor}
            state={states[actor.id] || {}}
            reduced={reduced}
            motionMs={step?.motionMs || animationConfig.timeline.defaultMotionMs}
          />
        ))}
      </svg>

      <div className="mt-4 rounded-lg border border-black/10 p-3 dark:border-white/10" aria-live="polite">
        {step?.title ? <h4 className="font-semibold">{step.title}</h4> : null}
        <dl className="mt-2 grid gap-2 text-sm/6 sm:grid-cols-3">
          <div><dt className="font-semibold opacity-65">关注</dt><dd><TextValue value={step?.focus} /></dd></div>
          <div><dt className="font-semibold opacity-65">变化</dt><dd><TextValue value={step?.changeSummary} /></dd></div>
          <div><dt className="font-semibold opacity-65">为什么重要</dt><dd><TextValue value={step?.whyItMatters} /></dd></div>
        </dl>
        {step?.caption ? <p className="mt-3 text-sm/6 opacity-75">说明：{step.caption}</p> : null}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2" role="group" aria-label="过程动画控制">
        <button type="button" className={button} data-animation-control="process-play" aria-pressed={playing} onClick={() => setPlaying((value) => !value)}>
          {playing ? "暂停" : "播放"}
        </button>
        <button type="button" className={button} data-animation-control="process-replay" onClick={() => { setStepIndex(0); setPlaying(!reduced); }}>
          重播
        </button>
        <button type="button" className={button} disabled={stepIndex <= 0} onClick={() => moveTo(stepIndex - 1)}>
          ← 上一步
        </button>
        <button type="button" className={button} disabled={stepIndex >= steps.length - 1} onClick={() => moveTo(stepIndex + 1)}>
          下一步 →
        </button>
        <div className="flex flex-wrap gap-1" role="list" aria-label="动画步骤">
          {steps.map((item, index) => (
            <button
              key={item.id || index}
              type="button"
              className={`${button} min-w-10 px-2 aria-[current=step]:bg-[var(--ic-accent)] aria-[current=step]:text-white`}
              aria-current={index === stepIndex ? "step" : undefined}
              aria-label={`第 ${index + 1} 步${item.title ? `：${item.title}` : ""}`}
              onClick={() => { setStepIndex(index); setPlaying(false); }}
              onKeyDown={(event) => {
                if (["ArrowRight", "ArrowDown"].includes(event.key)) { event.preventDefault(); moveTo(index + 1); }
                if (["ArrowLeft", "ArrowUp"].includes(event.key)) { event.preventDefault(); moveTo(index - 1); }
                if (event.key === "Home") { event.preventDefault(); moveTo(0); }
                if (event.key === "End") { event.preventDefault(); moveTo(steps.length - 1); }
              }}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>
      {cfg.principleCheck ? (
        <p className="mt-4 rounded-lg bg-black/[0.035] p-3 text-sm dark:bg-white/[0.05]">
          <strong>原理检查：</strong><TextValue value={cfg.principleCheck?.prompt ?? cfg.principleCheck} />
        </p>
      ) : null}
    </section>
  );
}

function experimentItems(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function logState(state) {
  return `${state.t.toFixed(2)} s · (${state.x.toFixed(2)}, ${state.y.toFixed(2)}) m`;
}

export function MotionLabWidget({ scene }) {
  const cfg = cfgOf(scene);
  const reduced = useReducedMotion();
  const animationConfig = getAnimationConfig(cfg);
  const definitions = projectileParameterDefinitions(cfg);
  const [params, setParams] = useState(() => projectileParameters(cfg));
  const [time, setTime] = useState(0);
  const [playing, setPlaying] = useState(() => animationConfig.autoplay && !reduced);
  const [trials, setTrials] = useState([]);
  const trialId = useRef(0);
  const state = useMemo(() => projectileState(params, time), [params, time]);
  const samples = useMemo(() => sampleProjectile(params, 120), [params]);
  const xMax = axisMax(cfg.xMax ?? cfg.xDomain, 160);
  const yMax = axisMax(cfg.yMax ?? cfg.yDomain, 64);
  const mainBounds = { left: 48, right: 720, top: 24, bottom: 286 };

  useEffect(() => {
    setTime((value) => Math.min(value, projectileState(params).T));
  }, [params.g, params.h]);

  useEffect(() => {
    if (reduced && playing) setPlaying(false);
  }, [playing, reduced]);

  useEffect(() => {
    if (reduced || !playing) return undefined;
    let frameId = 0;
    let previous;
    const tick = (now) => {
      if (previous == null) previous = now;
      const delta = Math.max(0, (now - previous) / 1000);
      previous = now;
      setTime((value) => {
        const next = Math.min(state.T, value + delta);
        if (next >= state.T) setPlaying(false);
        return next;
      });
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [playing, reduced, state.T]);

  const toMain = (item) => ({
    x: mainBounds.left + clamp(item.x / xMax, 0, 1) * (mainBounds.right - mainBounds.left),
    y: mainBounds.bottom - clamp(item.y / yMax, 0, 1) * (mainBounds.bottom - mainBounds.top),
  });
  const ball = toMain(state);
  const trajectory = graphPoints(samples, (item) => item.x, (item) => item.y, xMax, 0, yMax, mainBounds);
  const xTime = graphPoints(samples, (item) => item.t, (item) => item.x, state.T, 0, xMax, { left: 48, right: 355, top: 28, bottom: 214 });
  const yTime = graphPoints(samples, (item) => item.t, (item) => item.y, state.T, 0, yMax, { left: 48, right: 355, top: 28, bottom: 214 });
  const addTrial = () => {
    trialId.current += 1;
    setTrials((items) => [
      { id: trialId.current, v0: params.v0, h: params.h, g: params.g, t: state.t, x: state.x, y: state.y },
      ...items,
    ].slice(0, 8));
  };

  return (
    <section className={panel} data-modern-widget="motion-lab" data-modern-runtime="motion-lab-raf-trials">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">平抛运动实验</h3>
          <p className="mt-1 text-sm opacity-75">同一组参数同时驱动轨迹、速度分量和时间图，坐标范围保持固定以便比较。</p>
        </div>
        <span className="text-xs opacity-60">模型：projectile</span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {definitions.map((definition) => (
          <label key={definition.id} className="text-sm">
            <span className="flex justify-between gap-2"><span>{definition.label}</span><span>{params[definition.id]} {definition.unit}</span></span>
            <input
              className="mt-2 w-full"
              type="range"
              min={definition.min}
              max={definition.max}
              step={definition.step}
              value={params[definition.id]}
              aria-label={definition.label}
              onChange={(event) => setParams((value) => ({ ...value, [definition.id]: Number(event.target.value) }))}
            />
          </label>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2" role="group" aria-label="平抛时间控制">
        <button type="button" className={button} aria-pressed={playing} onClick={() => setPlaying((value) => !value)}>{playing ? "暂停" : "播放"}</button>
        <button type="button" className={button} onClick={() => { setTime(0); setPlaying(!reduced); }}>重播</button>
        <label className="min-w-64 flex-1 text-sm">时间 t = {state.t.toFixed(2)} s
          <input className="mt-2 w-full" type="range" min="0" max={state.T || 1} step="0.01" value={state.t} aria-label="时间 t" onChange={(event) => { setTime(Number(event.target.value)); setPlaying(false); }} />
        </label>
      </div>
      {chartFrame({
        title: "固定尺度的平抛轨迹",
        ariaLabel: "固定坐标范围内的平抛轨迹、球和速度分量",
        children: (
          <>
            <line x1={mainBounds.left} y1={mainBounds.bottom} x2={mainBounds.right} y2={mainBounds.bottom} stroke="currentColor" opacity=".35" />
            <line x1={mainBounds.left} y1={mainBounds.top} x2={mainBounds.left} y2={mainBounds.bottom} stroke="currentColor" opacity=".35" />
            <polyline points={trajectory} fill="none" stroke="currentColor" strokeWidth="3" opacity=".45" />
            <circle cx={ball.x} cy={ball.y} r="10" fill="var(--ic-accent)" />
            <Arrow x1={ball.x} y1={ball.y} x2={ball.x + clamp(state.vx * 4, 0, 130)} y2={ball.y} color="#2563eb" />
            <Arrow x1={ball.x} y1={ball.y} x2={ball.x} y2={ball.y + clamp(-state.vy * 3, -130, 130)} color="#dc2626" />
            <text x={ball.x + 12} y={ball.y - 12} fontSize="13">球</text>
            <text x={mainBounds.right - 5} y={mainBounds.bottom + 25} textAnchor="end" fontSize="12">x / m（固定范围 {xMax}）</text>
            <text x={mainBounds.left - 8} y={mainBounds.top - 8} textAnchor="end" fontSize="12">y / m（固定范围 {yMax}）</text>
          </>
        ),
      })}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {chartFrame({
          title: "x-t 图",
          ariaLabel: "水平位置随时间变化的 x-t 图",
          children: <><polyline points={xTime} fill="none" stroke="currentColor" strokeWidth="3" /><text x="350" y="250" textAnchor="end" fontSize="12">t</text><text x="42" y="20" fontSize="12">x</text></>,
        })}
        {chartFrame({
          title: "y-t 图",
          ariaLabel: "竖直位置随时间变化的 y-t 图",
          children: <><polyline points={yTime} fill="none" stroke="currentColor" strokeWidth="3" /><text x="350" y="250" textAnchor="end" fontSize="12">t</text><text x="42" y="20" fontSize="12">y</text></>,
        })}
      </div>
      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
        <div><dt className="opacity-65">当前坐标</dt><dd>{state.x.toFixed(2)} m, {state.y.toFixed(2)} m</dd></div>
        <div><dt className="opacity-65">速度分量</dt><dd>vₓ={state.vx.toFixed(2)} m/s，vᵧ={state.vy.toFixed(2)} m/s</dd></div>
        <div><dt className="opacity-65">派生量</dt><dd>T={state.T.toFixed(2)} s，射程={state.range.toFixed(2)} m，|v|={state.speed.toFixed(2)} m/s</dd></div>
      </dl>
      <div className="mt-4 rounded-lg border border-black/10 p-3 dark:border-white/10">
        <div className="flex flex-wrap items-center justify-between gap-2"><strong>试次记录</strong><button type="button" className={button} onClick={addTrial}>记录当前试次</button></div>
        {trials.length ? <div className="mt-3 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr><th className="p-1">#</th><th className="p-1">v₀</th><th className="p-1">h</th><th className="p-1">t</th><th className="p-1">位置</th></tr></thead><tbody>{trials.map((trial) => <tr key={trial.id}><td className="p-1">{trial.id}</td><td className="p-1">{trial.v0}</td><td className="p-1">{trial.h}</td><td className="p-1">{trial.t.toFixed(2)}</td><td className="p-1">{logState(trial)}</td></tr>)}</tbody></table></div> : <p className="mt-2 text-sm opacity-65">调节参数或时间后记录一组可比较的试次。</p>}
      </div>
      {experimentItems(cfg.experimentPrompts || cfg.experiments).length ? <div className="mt-4 rounded-lg bg-black/[0.035] p-3 text-sm dark:bg-white/[0.05]"><strong>实验提示</strong><ul className="mt-2 list-disc space-y-1 pl-5">{experimentItems(cfg.experimentPrompts || cfg.experiments).map((item, index) => <li key={index}><TextValue value={item} /></li>)}</ul></div> : null}
    </section>
  );
}

const simulationDefaults = Object.freeze({
  projectile: [
    { id: "v0", label: "初速度 v₀", unit: "m/s", initial: 8, min: 0, max: 24, step: 0.5 },
    { id: "h", label: "初始高度 h", unit: "m", initial: 12, min: 1, max: 48, step: 0.5 },
    { id: "g", label: "重力加速度 g", unit: "m/s²", initial: 9.8, min: 1, max: 20, step: 0.1 },
  ],
  "oblique-projectile": [
    { id: "v", label: "初速度 v", unit: "m/s", initial: 14, min: 0, max: 30, step: 0.5 },
    { id: "theta", label: "发射角 θ", unit: "°", initial: 45, min: -20, max: 85, step: 1 },
    { id: "h", label: "初始高度 h", unit: "m", initial: 0, min: 0, max: 48, step: 0.5 },
    { id: "g", label: "重力加速度 g", unit: "m/s²", initial: 9.8, min: 1, max: 20, step: 0.1 },
  ],
  logistic: [
    { id: "r", label: "增长率 r", unit: "", initial: 0.8, min: 0.05, max: 2, step: 0.05 },
    { id: "K", label: "容量 K", unit: "", initial: 1, min: 0.2, max: 2, step: 0.05 },
    { id: "x0", label: "初始比例 x₀", unit: "", initial: 0.1, min: 0.01, max: 0.8, step: 0.01 },
  ],
  linear: [
    { id: "slope", label: "斜率 a", unit: "", initial: 0.7, min: -2, max: 2, step: 0.05 },
    { id: "intercept", label: "截距 b", unit: "", initial: 0.2, min: -1, max: 1, step: 0.05 },
  ],
});

function simulationKind(cfg) {
  const model = cfg?.model;
  const declared = typeof model === "string" ? model : model?.kind || model?.type || cfg?.kind;
  const aliases = {
    "projectile-motion": "projectile",
    "horizontal-projectile": "projectile",
    "inclined-projectile": "oblique-projectile",
    "oblique-projectile": "oblique-projectile",
    "logistic-growth": "logistic",
    "linear-regression": "linear",
  };
  const kind = aliases[declared] || declared || "projectile";
  if (kind === "projectile" && (cfg?.parameters || []).some((item) => ["v", "theta", "angle"].includes(item?.id || item?.key))) {
    return "oblique-projectile";
  }
  return ["projectile", "oblique-projectile", "logistic", "linear"].includes(kind) ? kind : "projectile";
}

function simulationDefinitions(cfg, kind) {
  const defaults = simulationDefaults[kind] || simulationDefaults.projectile;
  return defaults.map((fallback) => {
    const declared = Array.isArray(cfg?.parameters)
      ? cfg.parameters.find((item) => item?.id === fallback.id || item?.key === fallback.id)
      : null;
    return { ...fallback, ...(declared || {}), min: num(declared?.min, fallback.min), max: num(declared?.max, fallback.max), step: num(declared?.step, fallback.step) };
  });
}

function simulationParameters(cfg, kind) {
  const definitions = simulationDefinitions(cfg, kind);
  return Object.fromEntries(definitions.map((definition) => [definition.id, num(declaredParameter(cfg, definition.id, definition.initial), definition.initial)]));
}

function simulationValue(kind, x, params) {
  if (kind === "projectile" || kind === "oblique-projectile") {
    return projectileState(
      kind === "oblique-projectile" ? { ...params, model: "oblique-projectile" } : params,
      x,
    ).y;
  }
  if (kind === "logistic") {
    const K = Math.max(0.01, num(params.K, 1));
    const r = num(params.r, 0.8);
    const x0 = clamp(num(params.x0, 0.1), 0.0001, K - 0.0001);
    return K / (1 + ((K - x0) / x0) * Math.exp(-r * x));
  }
  return num(params.slope, 0.7) * x + num(params.intercept, 0.2);
}

function simulationAssumptions(cfg, kind) {
  const model = cfg?.model || {};
  const value = model.assumptions || cfg?.assumptions || {
    projectile: ["忽略空气阻力，水平方向速度保持不变。", "竖直方向只受恒定重力加速度影响。"],
    "oblique-projectile": ["忽略空气阻力，水平方向速度分量保持不变。", "竖直方向只受恒定重力加速度影响。"],
    logistic: ["增长率 r 恒定，容量 K 不随时间改变。", "总体变化只由当前规模决定。"],
    linear: ["在观察区间内，因变量与自变量近似线性关系。", "残差和测量误差未被建模。"],
  }[kind];
  return experimentItems(value);
}

export function SimulationWidget({ scene }) {
  const cfg = cfgOf(scene);
  const reduced = useReducedMotion();
  const animationConfig = getAnimationConfig(cfg);
  const initialKind = simulationKind(cfg);
  const [kind, setKind] = useState(initialKind);
  const [params, setParams] = useState(() => simulationParameters(cfg, initialKind));
  const [progress, setProgress] = useState(0);
  const [playing, setPlaying] = useState(() => animationConfig.autoplay && !reduced);

  useEffect(() => {
    setParams(simulationParameters(cfg, kind));
    setProgress(0);
    setPlaying(!reduced && getAnimationConfig(cfg).autoplay);
  }, [cfg, kind, reduced]);

  const definitions = simulationDefinitions(cfg, kind);
  const projectileDuration = (kind === "projectile" || kind === "oblique-projectile")
    ? projectileState(kind === "oblique-projectile" ? { ...params, model: "oblique-projectile" } : params).T
    : 0;
  const xMax = kind === "projectile" || kind === "oblique-projectile"
    ? projectileDuration
    : axisMax(cfg.xMax ?? cfg.xDomain ?? cfg.model?.xDomain, 10);
  const rawValues = useMemo(() => Array.from({ length: 121 }, (_, index) => {
    const x = (xMax * index) / 120;
    return { x, y: simulationValue(kind, x, params) };
  }), [kind, params, xMax]);
  const yDomain = cfg.yDomain || cfg.model?.yDomain;
  const fallbackYMax = kind === "projectile" || kind === "oblique-projectile"
    ? axisMax(yDomain, Math.max(16, num(params.h, 12) * 1.2, ...rawValues.map((item) => item.y)))
    : kind === "logistic" ? Math.max(1, num(params.K, 1) * 1.2) : Math.max(1, ...rawValues.map((item) => item.y), 1);
  const yMin = Array.isArray(yDomain) ? num(yDomain[0], 0) : kind === "linear" ? Math.min(0, ...rawValues.map((item) => item.y)) : 0;
  const yMax = Array.isArray(yDomain) ? num(yDomain[1], fallbackYMax) : fallbackYMax;
  const bounds = { left: 48, right: 720, top: 24, bottom: 286 };
  const plot = graphPoints(rawValues, (item) => item.x, (item) => item.y, xMax, yMin, yMax, bounds);
  const activeX = xMax * clamp(progress, 0, 1);
  const activeY = simulationValue(kind, activeX, params);
  const activePoint = {
    x: bounds.left + clamp(activeX / Math.max(xMax, 0.0001), 0, 1) * (bounds.right - bounds.left),
    y: bounds.bottom - clamp((activeY - yMin) / Math.max(yMax - yMin, 0.0001), 0, 1) * (bounds.bottom - bounds.top),
  };

  useEffect(() => {
    if (reduced && playing) setPlaying(false);
  }, [playing, reduced]);

  useEffect(() => {
    if (reduced || !playing) return undefined;
    let frameId = 0;
    let previous;
    const tick = (now) => {
      if (previous == null) previous = now;
      const delta = Math.max(0, (now - previous) / 1000);
      previous = now;
      setProgress((value) => {
        const next = Math.min(1, value + delta / Math.max(1.2, num(cfg.duration, 4)));
        if (next >= 1) setPlaying(false);
        return next;
      });
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [cfg.duration, playing, reduced]);

  const modelName = cfg.model?.title || cfg.model?.name || kind;
  const experimentHints = cfg.experimentHints || cfg.experimentPrompts || cfg.experiments;

  return (
    <section className={panel} data-modern-widget="simulation" data-modern-runtime="simulation-raf-model">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><h3 className="font-semibold">{cfg.title || "模型模拟实验"}</h3><p className="mt-1 text-sm opacity-75">选择可解释模型，观察参数如何改变曲线形状。</p></div>
        <label className="text-sm">模型
          <select className="ml-2 rounded border border-black/15 bg-[var(--ic-paper)] p-2 dark:border-white/20" value={kind} onChange={(event) => setKind(event.target.value)} aria-label="选择模拟模型">
            <option value="projectile">projectile</option><option value="oblique-projectile">oblique-projectile</option><option value="logistic">logistic</option><option value="linear">linear</option>
          </select>
        </label>
      </div>
      <p className="mt-3 text-sm"><strong>当前模型：</strong>{modelName}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {definitions.map((definition) => (
          <label key={definition.id} className="text-sm"><span className="flex justify-between gap-2"><span>{definition.label}</span><span>{params[definition.id]} {definition.unit}</span></span><input className="mt-2 w-full" type="range" min={definition.min} max={definition.max} step={definition.step} value={params[definition.id]} aria-label={definition.label} onChange={(event) => setParams((value) => ({ ...value, [definition.id]: Number(event.target.value) }))} /></label>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2"><button type="button" className={button} aria-pressed={playing} onClick={() => setPlaying((value) => !value)}>{playing ? "暂停" : "播放"}</button><button type="button" className={button} onClick={() => { setProgress(0); setPlaying(!reduced); }}>重播</button><label className="min-w-64 flex-1 text-sm">时间进度 {Math.round(progress * 100)}%<input className="mt-2 w-full" type="range" min="0" max="1" step="0.01" value={progress} aria-label="模拟时间进度" onChange={(event) => { setProgress(Number(event.target.value)); setPlaying(false); }} /></label></div>
      <svg viewBox="0 0 760 340" role="img" aria-label={`${kind} 模型曲线`} className="mt-4 w-full rounded-xl border border-black/10 bg-white/50 dark:border-white/10 dark:bg-black/10"><title>{kind} 模型曲线</title><line x1={bounds.left} y1={bounds.bottom} x2={bounds.right} y2={bounds.bottom} stroke="currentColor" opacity=".35" /><line x1={bounds.left} y1={bounds.top} x2={bounds.left} y2={bounds.bottom} stroke="currentColor" opacity=".35" /><polyline points={plot} fill="none" stroke="currentColor" strokeWidth="3" /><circle cx={activePoint.x} cy={activePoint.y} r="9" fill="var(--ic-accent)" /><text x={bounds.right - 4} y={bounds.bottom + 25} textAnchor="end" fontSize="12">x / t = {activeX.toFixed(2)}</text><text x={activePoint.x + 12} y={activePoint.y - 12} fontSize="13">y={activeY.toFixed(2)}</text></svg>
      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-3"><div><dt className="opacity-65">参数</dt><dd>{definitions.map((definition) => `${definition.id}=${num(params[definition.id]).toFixed(2)}`).join("，")}</dd></div><div><dt className="opacity-65">当前派生量</dt><dd>x/t={activeX.toFixed(2)}，y={activeY.toFixed(2)}</dd></div><div><dt className="opacity-65">可观察结果</dt><dd>{kind === "projectile" || kind === "oblique-projectile" ? `落地时间 ${projectileDuration.toFixed(2)} s` : "曲线随参数连续变化"}</dd></div></dl>
      <div className="mt-4 grid gap-3 md:grid-cols-2"><div className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/10"><strong>模型假设</strong><ul className="mt-2 list-disc space-y-1 pl-5">{simulationAssumptions(cfg, kind).map((item, index) => <li key={index}><TextValue value={item} /></li>)}</ul></div>{experimentItems(experimentHints).length ? <div className="rounded-lg bg-black/[0.035] p-3 text-sm dark:bg-white/[0.05]"><strong>实验提示</strong><ul className="mt-2 list-disc space-y-1 pl-5">{experimentItems(experimentHints).map((item, index) => <li key={index}><TextValue value={item} /></li>)}</ul></div> : null}</div>
      {cfg.boundary ? <p className="mt-3 text-xs opacity-65">边界：<TextValue value={cfg.boundary} /></p> : null}
    </section>
  );
}

export function EquationWidget({ scene }) {
  const cfg = cfgOf(scene);
  const reducedMotion = useReducedMotion();
  const target = cfg.formula || cfg.expression || cfg.text || cfg.targetFormula || cfg.equation;
  const steps = Array.isArray(cfg.steps) ? cfg.steps : [];
  const variables = Array.isArray(cfg.variables)
    ? cfg.variables
    : Object.entries(cfg.variables || {}).map(([id, meaning]) => ({ id, meaning }));
  const initialReveal = steps.length ? clamp(Math.round(num(cfg.initialReveal, 1)), 1, steps.length) : 0;
  const [reveal, setReveal] = useState(initialReveal);
  const [predictionChoice, setPredictionChoice] = useState("");
  const [predictionFeedback, setPredictionFeedback] = useState("");
  const prediction = cfg.nextStepPrediction || cfg.prediction;
  const predictionOptions = Array.isArray(prediction?.options) ? prediction.options : [];
  const predictionAnswer = prediction?.correctId ?? prediction?.answer ?? prediction?.expected;
  useEffect(() => {
    setReveal(initialReveal);
    setPredictionChoice("");
    setPredictionFeedback("");
  }, [scene?.id, initialReveal]);
  const checkPrediction = () => {
    if (!predictionChoice) {
      setPredictionFeedback("先选择一个下一步，再检查你的预测。");
      return;
    }
    if (predictionAnswer == null) {
      setPredictionFeedback("这道预测题未声明标准答案，请结合理由自行复核。");
      return;
    }
    setPredictionFeedback(String(predictionChoice) === String(predictionAnswer) ? "预测正确：继续看这一步的理由。" : "再检查目标、已知条件和下一步需要消去的量。");
  };
  return (
    <section className={panel} data-modern-widget="equation" data-modern-runtime="equation-mathml-fallback" data-equation-reveal={reveal}>
      <h3 className="font-semibold">{cfg.title || "公式与推导"}</h3>
      {cfg.prompt ? <p className="mt-2 text-sm/7"><TextValue value={cfg.prompt} /></p> : null}
      <div className="mt-4"><h4 className="text-sm font-semibold opacity-65">目标公式</h4>{target ? <FormulaView value={target} label="目标公式" /> : <p className={`${warning} mt-2`} role="alert">未声明目标公式；生成阶段必须提供 formula 或 expression。</p>}</div>
      {steps.length ? <div className="mt-5" data-equation-steps><div className="flex flex-wrap items-center justify-between gap-3"><h4 className="text-sm font-semibold opacity-65">逐步推导</h4><span className="text-xs opacity-65" aria-live="polite">已显示 {reveal}/{steps.length} 步</span></div><ol className="mt-3 space-y-3">{steps.slice(0, reveal).map((step, index) => { const formula = step?.formula || step?.expression || step?.text || step; return <li key={step?.id || index} className="ic-equation-step rounded-lg border border-black/10 p-3 dark:border-white/10" data-equation-step={index + 1}><div className="text-xs font-semibold opacity-65">第 {index + 1} 步{step?.title ? ` · ${step.title}` : ""}</div><FormulaView value={formula} label={`第 ${index + 1} 步`} />{step?.reason ? <p className="mt-2 text-sm/6"><strong>理由：</strong><TextValue value={step.reason} /></p> : <p className="mt-2 text-sm opacity-65">理由：未声明</p>}{step?.assumption ? <p className="mt-2 text-xs opacity-65"><strong>条件：</strong><TextValue value={step.assumption} /></p> : null}</li>; })}</ol><div className="mt-3 flex flex-wrap items-center gap-2"><button type="button" className={`${button} primary`} disabled={reveal >= steps.length} onClick={() => setReveal((value) => Math.min(steps.length, value + 1))}>揭示下一步</button><button type="button" className={button} onClick={() => setReveal(initialReveal)}>重置推导</button><span className="text-xs opacity-65">{reducedMotion ? "减弱动效：保留离散步骤与手动控制。" : "每次只揭示一个推理环节。"}</span></div></div> : null}
      {predictionOptions.length ? <fieldset className="ic-equation-prediction mt-5 rounded-lg border border-black/10 p-3 dark:border-white/10"><legend className="px-1 text-sm font-semibold">{prediction.prompt || "预测下一步"}</legend><div className="mt-2 grid gap-2">{predictionOptions.map((option, index) => { const id = String(option?.id ?? option?.value ?? index); const label = option?.label ?? option?.text ?? option; return <label key={id} className="flex gap-2 rounded-lg border border-black/10 p-2 text-sm dark:border-white/10"><input type="radio" name={`equation-prediction-${scene?.id || "scene"}`} value={id} checked={predictionChoice === id} onChange={() => { setPredictionChoice(id); setPredictionFeedback(""); }} /><span><TextValue value={label} /></span></label>; })}</div><button type="button" className={`${button} mt-3`} onClick={checkPrediction}>检查预测</button>{predictionFeedback ? <p className="mt-2 text-sm" role="status" aria-live="polite">{predictionFeedback}</p> : null}</fieldset> : null}
      {variables.length ? <div className="mt-5"><h4 className="text-sm font-semibold opacity-65">变量</h4><dl className="mt-2 grid gap-2 sm:grid-cols-2">{variables.map((variable, index) => <div key={variable.id || variable.symbol || index} className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/10"><dt className="font-semibold">{variable.symbol || variable.label || variable.id}</dt><dd className="mt-1 opacity-75"><TextValue value={variable.meaning || variable.description || variable.text} /></dd></div>)}</dl></div> : null}
      {cfg.assumptions ? <div className="mt-5 rounded-lg bg-black/[0.035] p-3 text-sm dark:bg-white/[0.05]"><strong>假设</strong><div className="mt-2"><TextValue value={cfg.assumptions} /></div></div> : null}
      {cfg.boundary ? <p className="mt-3 text-sm opacity-70"><strong>边界：</strong><TextValue value={cfg.boundary} /></p> : null}
    </section>
  );
}
