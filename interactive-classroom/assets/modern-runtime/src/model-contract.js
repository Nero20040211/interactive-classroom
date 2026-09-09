const finite = (value, fallback) =>
  Number.isFinite(Number(value)) ? Number(value) : fallback;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function flightTime(height, verticalSpeed, gravity) {
  // Solve h + vy0*t - g*t²/2 = 0 and keep the non-negative root.
  return Math.max(
    0,
    (verticalSpeed + Math.sqrt(Math.max(0, verticalSpeed ** 2 + 2 * gravity * height))) /
      gravity,
  );
}

export function horizontalProjectileState(
  { v0 = 8, h = 12, g = 9.8 } = {},
  time = 0,
) {
  const safeG = Math.max(0.01, finite(g, 9.8));
  const height = Math.max(0, finite(h, 0));
  const speed = Math.max(0, finite(v0, 0));
  const T = Math.sqrt((2 * height) / safeG);
  const t = clamp(Math.max(0, finite(time, 0)), 0, T);
  const x = speed * t;
  const y = Math.max(0, height - 0.5 * safeG * t * t);
  const vx = speed;
  const vy = -safeG * t;

  return {
    t,
    T,
    x,
    y,
    vx,
    vy,
    speed: Math.hypot(vx, vy),
    range: speed * T,
    peak: height,
  };
}

export function obliqueProjectileState(
  { v = 14, theta = 45, h = 0, g = 9.8 } = {},
  time = 0,
) {
  const safeG = Math.max(0.01, finite(g, 9.8));
  const height = Math.max(0, finite(h, 0));
  const speed0 = Math.max(0, finite(v, 0));
  const angle = (finite(theta, 45) * Math.PI) / 180;
  const vx0 = speed0 * Math.cos(angle);
  const vy0 = speed0 * Math.sin(angle);
  const T = flightTime(height, vy0, safeG);
  const t = clamp(Math.max(0, finite(time, 0)), 0, T);
  const x = vx0 * t;
  const y = Math.max(0, height + vy0 * t - 0.5 * safeG * t * t);
  const vx = vx0;
  const vy = vy0 - safeG * t;
  const peak = height + (vy0 > 0 ? (vy0 ** 2) / (2 * safeG) : 0);

  return {
    t,
    T,
    x,
    y,
    vx,
    vy,
    speed: Math.hypot(vx, vy),
    range: vx0 * T,
    peak,
    v0: speed0,
    theta: (angle * 180) / Math.PI,
  };
}

export function projectileState(params = {}, time = 0) {
  // Existing courses use v0/h/g for horizontal projectile motion. A config
  // that declares v or theta is the oblique model; this keeps old data stable
  // while preventing an angle parameter from being silently ignored.
  const oblique =
    params?.model === "oblique-projectile" ||
    params?.modelKind === "oblique-projectile" ||
    params?.v != null ||
    params?.theta != null ||
    params?.angle != null;
  if (!oblique) return horizontalProjectileState(params, time);
  return obliqueProjectileState(
    { ...params, theta: params.theta ?? params.angle },
    time,
  );
}

export function sampleProjectile(params, count = 120) {
  const n = Math.max(2, Math.floor(Number(count) || 120));
  const last = projectileState(params).T;
  return Array.from({ length: n }, (_, index) =>
    projectileState(params, (last * index) / (n - 1)),
  );
}

export function sampleObliqueProjectile(params, count = 120) {
  return sampleProjectile({ ...params, model: "oblique-projectile" }, count);
}
