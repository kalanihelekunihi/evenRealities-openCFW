# R1 sensor update and timestamp hysteresis in C

Follow-up: [validation/output copying](gomore-lower-providers-c-review.md)
now has C implementations with actual caller replay. The stock version leaf
is verified as zero; nonzero tests are counterfactual. Counts below describe
the preceding sensor-update build.

`native_gomore_sensor_update.c` implements stock sensor update `0x94384`
(350-byte inventory body) and timestamp clamp `0x68570` (38 bytes). The
[receipt](gomore-sensor-update-c-review.json) binds REA pseudocode/bytes,
production objects, independent replay/oracles, qualification and composition.
It adds no assembly and owns one cold-zero debug byte at `0x20007c61`, verified
by native startup RW/ZI handlers and an independent decoder.

Diagnostics run only when that byte equals **one**. They load signed UTC offset,
then time, preserve native raw float-to-double promotion, and reload lengths
on every logging-loop condition. Array reads/promotions occur in Z, Y, X order
before the X/Y/Z variadic log arguments. The existing promotion helper preserves
the native raw exponent rebias and zero handling; an ordinary C floating cast
would not reproduce its denormal/NaN/negative-zero behavior.

The operational path first reads signed readiness from the current context.
Negative readiness returns directly, even without reading the packet when
diagnostics are disabled. Runtime validation consumes a fresh timestamp;
negative validation logs and returns the captured error. Timestamp hysteresis
uses wrapping unsigned +/-3 comparisons, returns one for timestamp zero without
reading context, and can select the previous index plus one.

The parent reloads context after the clamp. An empty last-index cell receives
index minus one before a fresh nested-pointer read and monotonic comparison.
A non-increasing index logs and returns -4. Otherwise host-input update runs,
then the existing C no-op and output-copy providers run **even when host update
returns an error**. Context is freshly loaded after output copy, followed by
separate nested-pointer reads for last-index and sequence stores. The sequence
increments its low 31 bits while preserving the high bit through the native
rotate/add/rotate operation. The captured host result is returned unchanged.

**3,053 paired native/C/oracle cases** pass, including **18 expected faults** and
6,708 diagnostic log calls. Cases cover signed readiness/validation, timestamp
and counter boundaries, debug values 0/1/2/255, signed UTC offsets, raw FP logging,
live count/time/context mutations, invalid packets and contexts, and 255-element
logging loops. Exact observed calls/state, returns, guarded regions, preserved
registers, SP, masks and FPSCR match; fault prefixes compare native/C state.

Another **512 cases run through the actual native/C idle callback and sensor
update**, with independent final memory/result checks and 1,696 diagnostic calls.
Lower time/health/log/validation/host/output-copy/reinitialization providers remain
modeled. The existing no-op's exact C body is independently compiled for these
fixtures because its production vendor object has a monolithic text section;
its two instruction bytes are checked against that production object. Production
continues to reuse the existing symbol, with no new implementation copy.
Ten compiled defects are rejected, including cached counts/context, unsigned
readiness, incorrect validation/index comparisons, sequence carry and skipping
post-host work on errors.

All **677 units** compile without duplicate strong symbols. All **676 prior
source/object pairs** remain unchanged. Application imports become **167**;
bootloader imports remain **34**. Resolving sensor update exposes native logging,
runtime validation, host-input update and output-copy interfaces. The parameterized
frozen GoMore functions are not used as replacements for these raw native ABIs.

Neither function qualifies as instruction-identical. The canonical plan remains
**4,369 source-built bytes**, and the fresh hybrid matches the locked application
through executable pull-through. Context allocation/initialization, output
lifecycle, complete source-only firmware linking, byte identity, concurrent
execution and physical sensor behavior remain unproven.
