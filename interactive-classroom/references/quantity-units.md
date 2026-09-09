# Quantity, Unit, and Dimension Contract 

For physics/engineering scenes where dimensional reasoning matters, use `widgetType: quantity-lab`. Each quantity declares `id`, `label`, `symbol`, `unit`, and `dimension`; value is optional. The relation declares `lhsDimension` and `rhsDimension` and may include a structured MathML formula.

Teach the difference: unit = chosen measurement scale; dimension = physical type. Dimensional consistency is necessary, not sufficient, for a physical equation. Never infer empirical constants from dimensions alone.
