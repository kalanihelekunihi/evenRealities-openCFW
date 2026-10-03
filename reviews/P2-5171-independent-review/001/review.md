# Independent review P2-5171

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay and literal calculations pass for both extents. The map tracks global handle loads/reloads, initialization and take/release adapter call order, status-zero helper path, time/context callbacks, and distinct return aliases (including POP R0 incoming R7 and POP R1 incoming R7). ADR consumers are resolved from their aligned PC bases.

## Limits

Child semantics are not inferred; global handle meaning, synchronization/hardware behavior and logger formatting remain outside scope. Gap bytes A6DA..A6F0 are excluded. Private partial map; accepted:false.
