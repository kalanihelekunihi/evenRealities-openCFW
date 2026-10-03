# Independent review 2591: disable transition with original callbacks

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate receipt, source images, inventory, pseudocode, and replay hashes match. I ran an isolated copy of the replay with its output redirected to a fresh directory; all 24 cases pass. The cases cover readiness on poll read 1 or 2 and timeout, both incoming PRIMASK values, two MMIO patterns, and pending byte 0/1.

The path executes the original disable flow and callback entries without firmware-function interception. Its fixture table explicitly installs nonnull callbacks at slots 4, 12, and 16. A successful poll takes the operation-3 transition callback's no-op path, then runs post-callback and conditionally enters the original pending helper. Pending is cleared only when nonzero; this packet gates the pending helper off, so no field write occurs. Timeout skips the transition callback but still runs pre/post. Assertions cover callback order, mask state at writes, poll reads and delays, MMIO writes, result (0 success, 4 timeout), high registers, and stack.

Readiness/MMIO are modeled, and the table is manually installed rather than produced by the profile initializer. Only the operation-3 no-op callback branch is covered; other operations, active pending adjustment, profile compatibility, physical behavior, and concurrent mutation remain unresolved. This review does not establish callback installation ownership or admit canonical records.
