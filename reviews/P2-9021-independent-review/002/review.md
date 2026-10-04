# P2-9021 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The independent replay ran 96 original-byte cases and passed full 64-byte descriptor comparisons; only halfword+42 is cleared when initially nonzero, while adjacent +44 and all other seeded bytes match expectations.
- Entry R3 return, preserved R4-R7, PRIMASK, SP, and stop-PC assertions passed for both masks.

Limitations:

- Callback slot was null in all cases. Callback-present behavior, concurrent mutation, and physical effects remain outside scope.
