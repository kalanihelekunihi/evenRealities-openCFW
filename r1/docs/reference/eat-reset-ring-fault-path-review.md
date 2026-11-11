# R1 `AT^RESET_RING` fault path, 2026-11-11

The locked R1 application has the command callback at `0x4f598..0x4f5cb`.
It calls the retained log sink at `0x7f030` five times in order:

1. `ASSERTION FAILED!`
2. `File: %s` with `..\\..\\..\\platform\\services\\eAT\\at_system.c`
3. `Line: %d` with `103`
4. `Function: %s` with `at_reset`
5. `Expression: %s` with `0`

The callback then loads literal `0xe7f00000` from `0x4f64c`, stores it on
the stack, and executes `BLX` through the stack pointer. In ARM state that
word disassembles as `ldrb r0, [r0, r0]!`; execution from stack or the
resulting memory access can fault. The callback's following `return 1` is
only reachable if the stack-executed word returns, which it does not under
the normal fault path. This is the same architectural issue as the three
remaining assertion-transfer imports. A direct `NVIC_SystemReset` call
would skip the stock fault route and its fault-vector effects.

No C replacement is selected yet. The strict application receipt at
`build/r1-link-eat-kv-read-c-20261111/report.json` keeps the callback
undefined instead of substituting a trap or a different reset. The next
implementation needs a source-owned C fault/reset policy and a comparison
of retained logs, reset-cause state and fault-vector behavior. This review
does not establish physical execution or byte identity.
