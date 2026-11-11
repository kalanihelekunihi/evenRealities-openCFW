# Respiratory update C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-respiratory-c-review.md) records production consolidation and exact-pointer host replay.

Stock respiratory stage `0x60680` (734 bytes) now has a compilable experimental
C root. The [receipt](gomore-respiratory-c-investigation.json) binds REA bytes,
pseudocode, source/object and replay under `build/goal-r1-gomore-respiratory-c/`.
Production still imports this stage; no source manifest or canonical image
selection changes at this checkpoint.

The candidate preserves gap filling capped at twenty history calls, code-byte
load order, interleaved square sums, unavailable/error flags, encoded rate checks,
signaling comparisons and raw-bit clamps, elapsed-gap clearing, confidence
penalties, ordered history shifts and selected output aggregation. Software FP
conversion/arithmetic providers are called explicitly: ordinary C double casts
would not preserve the stock binary32 promotion behavior for all raw patterns.
Selected confidence is reloaded after the threshold mean, preserving output aliases.

An initial C frame was 24 bytes smaller than stock. A 44-byte C scratch object
with reserved space, initialized only at the two observed float slots, now yields
the native 96-byte entry-relative frame. Estimator rate/confidence pointers are
entry SP minus 80/minus 84. Both numeric addresses and provider SP are compared
without normalization. Private saved-register/uninitialized reserved bytes remain
outside the data contract. No inline assembly or persistent RAM is introduced.

**2,792 native/C root cases** pass with the optical estimator modeled and all other
native helpers executing, including history, statistics, clear, software FP and
square root. Cases cover elapsed/counter variation, raw FP boundaries and seeded words,
NaNs/zeros, unavailable flags, selected-confidence aliases and FP modes. Estimator
mutations change history/codes, input flags and rounding mode, return a nonzero
status, and clobber caller-saved integer/FP registers. Return status also has an
independent flag-bit expectation. Full record
and output bytes, return flags, all six estimator argument words, FPSCR, final
SP and saved integer/high-FP registers agree. This is not yet a completely C
lower graph or a reconstructed optical estimator.

Nine compiled defects are rejected: fill cap, unavailable/error flags, clamp,
gap clearing, history direction, cached selected confidence, penalty scale and
resetting nonpositive confidence. Compilation failures do not count. **51
boundary cases**, including **47 faults**, match partial writes, invalid access
address/size, estimator arguments, memory, return and FPSCR; private stack writes
are excluded.

The actual host/coordinator chain passes **334 semantic cases**, including nine
faults and 3,259 modeled calls, with the respiratory root executing. Logging,
optical estimation and fifteen other stage providers remain modeled. Other lower
helpers execute natively. The current production coordinator uses a smaller C
frame: optical rate/confidence/provider-SP offsets from outer host entry are
(-584,-588,-600), versus stock (-640,-644,-656). The direct respiratory frame
matches; this caller difference prevents a whole-chain pointer-equality claim.

An experimental C-only 56-byte volatile coordinator reservation closes that
observed gap. All 334 host cases pass with exact numeric optical pointers/SP
explicitly asserted, and all 4,512 direct coordinator/oracle cases also pass.
This variant remains under the ignored build directory; it adds one private
frame write and has not changed production source or qualified image selection.
Private frame bytes and other caller frame differences remain outside the proof.

Production owner consolidation, clear-two helper review, normal source-object
build/replay and qualification remain pending. The existing
generic respiratory owner must be consolidated before production promotion.
The native clear-two helper also needs its exact C interface/owner reviewed.
Physical execution, source-only final linking and byte identity remain unproven.
The normal build remains 687 units with 179 application and 34 bootloader imports.

The [clear-two investigation](gomore-clear-two-c-investigation.md) now verifies
that dependency and repeats all 2,792 root cases with C clear, C history and
all three C statistics helpers linked. Software FP and EABI byte clear still
execute natively; production consolidation remains pending.

The subsequent [clear-two production review](gomore-clear-two-c-review.md)
adds that dependency to the normal build and reruns root/boundary replay with
its production object. The experimental respiratory declaration now uses the
shared pointer header. Root and coordinator-frame promotion are still pending.
