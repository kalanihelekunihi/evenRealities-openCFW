# Native GPIO and ship-mode frame closure in C

Current implementation: [ordinary C GPIO/pulse ABI](ship-pure-c-review.md). The scratch-register/frame preservation described below is historical.

The ship-mode C candidate now reuses outgoing argument word zero as its pin
word, matching stock at `0x50708`. Empty constraints retain R4 zero, R5's
incoming value until after the first configuration, and incoming R6. The
configured Clang profile exposes the native 24-byte frame instead of 32.
GPIO configuration at `0x78dea` retains the four saved incoming argument words
and native live R4–R8 values in a 40-byte frame instead of 32. It restores
R0–R3 from those words, including a decoded pin changed by the helper.
The port decoder itself is unchanged. Every executed operation remains C.

The root's shift uses ARM register-LSL semantics: the shift count is the low
byte, and counts of 32 or greater produce zero. This avoids undefined C shifts
when a controlled decoder boundary mutates the exposed pin word. Final R2/R3
come from the outgoing words, preserving the native restore behavior.

The product object passes 5,678 paired stock/C cases: the earlier 262 decoder,
3,310 raw configuration and ten complete-chain cases, plus 2,096 controlled
pin-word/port/delay cases. Provider frame snapshots, live R4–R11 and restored
R0–R3 now match. The full C chain reaches nested decode at the native 64-byte
depth. The decoder is modeled only for controlled mutation cases; the main
configuration/pulse suite executes the actual C helper. The earlier frame
object, wrong shift fallback, wrong outgoing alias and enlarged configuration
scratch are all rejected.

This does not establish exact rebuilding. A strict ordered-memory probe rejects
the first stack save: native writes incoming R2 at SP-24 first, while C writes
saved R4 at SP-16 first. Qualification selects no regions. These differences
remain explicit; the bounded suite excludes initial save/store order and nested
private return addresses. Electrical GPIO behavior, real delay/scheduling,
faults, asynchronous activity and arbitrary control-frame aliases are unproven.

All 581 R1 units compile. The 580 other objects, manifest, imports, port-decoder
code and source plan remain unchanged. Hybrid application identity still matches
the locked stock hash. Probes are under `build/goal-r1-ship-frame-c`; durable
results are in the adjacent JSON. This supersedes the frame-gap measurements
in [the original GPIO review](ship-mode-c-review.md).
