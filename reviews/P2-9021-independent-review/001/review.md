# P2-9021 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The fixture receipt pins the locked image and its current scope, results, and replay script; the recorded case set contains 96 rows across four field values, four index values, three error values, and both PRIMASK values.
- The test script’s independent expected-byte model changes only descriptor halfword+42, checks the full 64-byte descriptor including adjacent halfword+44, and checks saved entry R3, preserved callee registers, PRIMASK, SP, and stop PC.

Limitations:

- Unicorn is unavailable in this environment, so I could not independently rerun original instructions. The review checks the recorded result artifact and replay/oracle structure only.
- Only callback-absent synthetic SRAM cases are represented; callback-present, concurrent mutation, and physical behavior are outside scope.
