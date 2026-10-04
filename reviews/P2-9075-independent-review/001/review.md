# P2-9075 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 14 original parser-entry and partial-header byte-stream cases with allocation and dispatch paths kept unreachable.
- Full parser state and ring memory, header count/type/busy fields, modified saved-R3 return slot, preserved registers, PRIMASK/SP/PC matched the independent seeded-memory expectations.

Limitations:

- Only entry/partial-header paths are covered. Allocation, completed-header, payload, dispatch, malformed pointers, and physical transport remain outside scope.
