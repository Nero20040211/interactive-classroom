# Motion Lab 

Use `widgetType: motion-lab` for mechanics topics where the learner must connect **physical motion, vector components, time graphs, equations, and controlled experiments**.

## Canonical horizontal-projectile model

Parameters: `v0` (m/s, dimension L T^-1), `h` (m, dimension L), and `g` (m/s^2, dimension L T^-2). The local runtime derives flight time, horizontal range, position, velocity components, speed and velocity angle.

Required teaching pattern:

1. predict a relationship;
2. change one independent variable while holding others fixed;
3. observe the moving object and velocity vectors;
4. scrub time and inspect the same instant in the trajectory, x–t graph and y–t graph;
5. record trials;
6. compare trials and explain the relationship with the structured MathML equations.

## Representation rules

- keep trajectory axes labeled with quantity and SI unit;
- use a fixed comparison scale derived from the allowed parameter ranges, not a new auto-scale after every slider change;
- distinguish current position from the full predicted path;
- show horizontal and vertical velocity components separately;
- provide a time scrubber so animation never hides intermediate states;
- graphs must have axis labels/units and synchronize their current-time marker;
- parameter manipulation must update in place without scene re-render;
- allow replay/pause and clean up timers when leaving/resetting the scene;
- trial logging is session-local and deterministic.

## Horizontal projectile misconceptions to target

- the object is **not** pushed horizontally after release; horizontal speed stays constant only under the no-air-resistance model;
- gravity changes vertical velocity, not horizontal velocity;
- flight time depends on height and gravity, not horizontal launch speed;
- horizontal range depends on both launch speed and flight time;
- the trajectory is parabolic because horizontal displacement is linear in time while vertical displacement is quadratic in time.

Do not use this widget when a simpler quantity lab or static diagram teaches the target better.
