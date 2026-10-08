# P2-21229 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x482040..0x4820BC (124 bytes); instruction and literal-reference outputs match. Leading ASCII zero bytes trigger repeated exponent decrement, cursor/count updates, and no explicit encoded length bound. The retained base is selected as SP0+1 for `f`, 1 for `e`, or 0 otherwise; precision is added, then strict signed `<` clamps to length-1. The discard check uses a fresh byte and threshold `> '4'` to choose retained `'9'` versus `'0'`. A backward scan searches for that retained byte; the `'9'` path increments the preceding digit. If the scan passes before the base, the code increments exponent and adjusts base/count as recorded. Sentinel-dependent behavior and rounding policy remain unresolved; no conventional rounding rule is inferred.
