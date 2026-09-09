# Structured Chemistry Reaction Contract 

Use `widgetType: chemistry` for equation balancing / atom conservation. Represent each compound with an immutable composition: `coefficient` plus `atoms:[{symbol,count}]`. The coefficient may change; atom subscripts define compound identity and must not be changed merely to balance an equation.

The runtime counts atoms on both sides and can show a conservation table. `expectBalanced:true` means strict validation must find equal atom counts for every element. Use this for balancing/stoichiometric reasoning, not as a complete chemical-validity engine: thermodynamics, kinetics, states, charges, mechanisms, and reaction conditions may require additional domain evidence.
