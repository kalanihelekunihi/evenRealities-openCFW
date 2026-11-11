# R1 sleep-interval engine: native contract before C binding

REA identifies the complete 258-byte routine at `0x7244e`. The native interface
has five arguments: context, current-time word pointer, timezone halfword
pointer, mode and output-record pointer. Its existing provider-rich portable
counterpart has a different ABI and validation policy. The frontier now
records an unresolved native route, rather than implying the portable symbol
is an accepted binding. The [receipt](gomore-interval-engine-native-analysis.json)
binds REA evidence, the executable replay, results and unchanged source hashes.

The first operation writes zero to output byte 26, before reading context
byte 184. A zero enable byte returns 64 immediately; any other value enters
the active path. There are no null guards. Thus a null output faults at address
26 even when disabled; an invalid context faults only after that output store.

The active path initializes an eight-byte control record to `00 03 05 00 00
00 00 00`, updates the second word of context+192 through the existing native
setter using the first current-time load, and snapshots forty descriptor bytes.
It calls compose at `0x67558` with candidate output, context, context+272,
timezone pointer, mode, controls, descriptor snapshot, context+232 and
context+304. The returning compose routine copies all 32 candidate bytes;
its return register is not a success/failure condition here.

The candidate clamp is **not an unsigned gap-under-900 check**. The outer test
requires context word 172 to exceed candidate start unsigned; the difference
is then compared with 900 as a signed 32-bit value. Large wrapped differences
with the sign bit set therefore pass. Clamping replaces start with the context
word and rounds the unsigned remaining span down to a multiple of 30 seconds,
with wrapping addition. Flag bit 3 alone controls a 32-byte candidate copy to
context+272; other flag bits are preserved in the final output.

Merge at `0x72024` receives context+192, a fresh current-time word, a freshly
loaded and sign-extended timezone halfword, candidate flags masked with 8,
context+232, the descriptor snapshot and the signed control byte 1. Provider
returns do not stop the caller. After merge, the full candidate is copied to
the output. Only then does the engine load the policy pointer at context+312.
It reads an unaligned word at pointer+2, stores it at context+304, then reads
pointer+6 and stores it at context+308. These cannot be collapsed into an
earlier pointer load or an eight-byte snapshot: output can replace the pointer,
and the first destination store can overlap the second source word.

Finally, control byte 0 is forced to zero and the current eight control bytes
are committed as two word stores to context+184 and +188. Other control bytes
remain live across the providers. Hardcoding the initial 3/5 values would
change reentrant behavior. Completed active calls return zero.

The native fixture passes **2,152 cases**, comprising 2,120 completed returns
and 32 faults. Cases cover enable bytes 0/1/255, flag bytes 0/8/128/255, time
rounding and wrapping boundaries, timezone extremes, mode extremes, policy
source overlap, output aliases and control changes. Of 72 provider-mutation
configurations, 66 are reached. The independent scalar shadow confirms 708
clamps, including **288 clamps with a large wrapped difference**. Comparisons
assert provider argument order, live values, candidate contents, policy/store
order and width, guarded SRAM, return values, saved registers, SP, masks and
FPSCR. Native private frame offsets are recorded (candidate entry-SP−120,
snapshot entry-SP−88, controls entry-SP−48); their exact placement is not yet
claimed necessary for a C implementation.

Setter, copy, compose and merge are modeled providers in this analysis. This
is not a compiled-engine or physical-hardware validation. The source/manifest
and all 666 production object hashes are unchanged; composition remains at
164 application and 34 bootloader imports. The byte-qualified plan is unchanged.
The next implementation must preserve the signed clamp, live control/current/
timezone/policy loads, ordered unaligned policy accesses and native faults,
then execute existing C setter/memory providers and the reconstructed caller
in paired comparisons before promoting this route.

The subsequent [engine C review](gomore-interval-engine-c-review.md) implements
this native contract and verifies it through the actual C interval-update caller,
setter, memory routines, propagation and packed accessors. Compose and merge
remain explicit native dependencies.
