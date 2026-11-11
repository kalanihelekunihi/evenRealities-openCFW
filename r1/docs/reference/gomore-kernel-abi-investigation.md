# GoMore resampling kernel ABI investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-kernels-c-review.md) records consolidation and normal-build integration.

REA and locked Thumb instructions identify ACC `0x8245c` and PPG `0x8247e`
as wrappers around interpolation `0x882ec` and filtering `0x641f0`.
The [receipt](gomore-kernel-abi-investigation.json) binds experimental source,
object, REA output and replay. No production source is changed at this checkpoint.

Both stock entries take four words: state, source, count and destination.
They unconditionally call interpolation with `(source, count, 25, count,
destination)`, then filtering with `(state, destination, 25)`. Neither root
checks pointers or count. ACC discards both provider returns and returns zero;
PPG restores its frame and tail-branches to filtering, exposing that provider's
raw R0 at the machine boundary. This does not infer a semantic public return
value for the filter's C API.

The PPG REA pseudocode omits the interpolation fifth argument and includes an
extra filter argument. Instructions explicitly store destination at outgoing
SP before interpolation and branch with three filter arguments; instruction
and replay evidence govern those details.

Experimental four-argument C wrappers pass **320 native/C cases**, each checked
against independent ordered-call expectations. Counts include zero, 25 and signed
extremes; pointers include null, invalid and aliased values; provider return words
span zero, one and high-bit values. Integer callee-saved registers, final SP and
return behavior are checked. Interpolation/filter are modeled, so null/invalid
pointer tests establish unconditional dispatch only. They do not establish
native provider dereference behavior. Both native wrappers use 16 bytes before
interpolation; this C profile uses 24. PPG reaches filtering with entry SP restored
on both paths; ACC still has the 16/24-byte difference at filtering.

The existing generic owner functions `gomore_primitives_resample25_and_filter`
and its `_tail` variant have seven arguments, injected providers and null guards.
They are not direct stock ABI providers. Before integration, consolidate their
stock ownership rather than add a second implementation: retain the generic
checked behavior only as an explicitly separate provider helper for its existing
high-level callers, and supply one verified four-word stock implementation.

The lower interpolation and IIR filter also have existing generic owners. Audit
those against stock before treating them as native dependencies. The filter
pseudocode incorrectly presents raw float loads as integer casts; its instructions
use VLDR/VMUL/VMLA/VMLS and ordered history copies. Full provider reconstruction,
negative controls, actual resampler integration and byte identity remain open.
