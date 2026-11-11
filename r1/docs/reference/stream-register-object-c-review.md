# R1 stream object registration and timer-period store in C

The stock registration body at `0x89890` (464 code bytes) and timer-period store
at `0x8a5d0` (20 bytes) now have one C implementation each in
`runtime/native_stream_register_object.c`.
[Machine receipt](stream-register-object-c-review.json).

Registration preserves the list-empty result captured before prepend changes
the list. Failed record allocation logs and returns zero. Successful records
retain stock ordering: clamp orders above one after diagnostics; truncate
strlen to a byte before clamping to eight; write callback, order byte, low flag
byte and zero status halfword; copy name bytes; then write the owner pointer.
No new record clearing, terminator, validation, lock or rollback is introduced.

For a first listener, the object rate is published before buffer allocation.
The returned buffer is published even when null, before the fatal boundary.
The driver-start callback and context use the observed reloads, then current
rate and mode choose timer creation with the stream-dispatch callback. For an
existing list, a higher requested rate may allocate a new buffer, convert samples
through the verified C sample-rate helper, free the freshly reloaded old buffer,
and publish the new pointer and returned byte count. Timer period and reset
diagnostics use their native reload points. Partial state and provider mutations
are retained rather than silently repaired.

Orders of zero are not rejected by stock. A reachable zero-rate period can
execute UDIV with a zero divisor. Portable C division by zero is undefined and
the configured compiler has no supported raw UDIV intrinsic. The candidate uses
an explicit unresolved `r1_stream_zero_divisor_result` boundary only for that
case. Replays observe zero with Unicorn's divide-trap setting disabled; this
does not establish real CCR settings, UsageFault dispatch or exception-frame
identity. No default hardware result is invented in the source provider.

Null object/group and buffer-allocation failures call the existing explicit
C architectural fault provider. Comparisons stop before its BASEPRI/store
transition and retain its separately documented exception-register gaps.
The timer-period helper stores its word and returns the original pointer on
non-null input; null input uses that same fault boundary.

Verification passed 2,867 paired registration cases with ordered object/record
accesses and snapshots, covering initial and existing listeners, allocation
failures, zero/high orders, string-length truncation, aliasing, driver callbacks,
mode changes, masks and provider mutations. Another 108 paired cases execute
the actual native/C sample converter inside registration. The timer-period
helper passed 32 direct paired cases. Five mutants were rejected: missing group
guard, wrong length truncation, wrong order clamp, skipped driver start and
freeing the new buffer. Production replay passed again after the negatives.

Frame identity remains open. Native registration providers see 48 bytes; C
providers see 40. A strict native-frame check rejects the candidate. The linked
sample converter adds its matched 40-byte frame, giving 88 versus 80 bytes at
nested copies. Timer-period non-null paths have zero-byte frames; the null
boundary has zero native bytes versus eight C bytes. Caller-saved registers,
private stack words, APSR and physical exception effects are excluded from the
comparison. The native fifth-word load timing is not claimed for private
caller-stack aliases. Allocator/list/string/memory/timer/logging providers and
driver callbacks remain modeled outside the sample-converter chain.

All 610 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 609 objects remain
identical. The object-registration import resolves; the append-based timer
constructor, stream dispatcher and architectural zero-divisor provider become
explicit dependencies. Totals are 170 application imports and 34 bootloader
imports. Timer constructor/dispatcher frontier names now match their C interfaces
but remain unresolved providers.

The scoped qualifier admits no executable bytes, so the source plan is unchanged.
The fresh hybrid matches the locked application using 4,271 source-built bytes,
641,889 executable pull-through bytes and 248 resource bytes. Actual heap,
registry, driver and timer integration, zero-divisor hardware behavior, physical
sensor delivery, full source-only linking and candidate byte identity remain
unfinished.

The subsequent [append timer constructor](stream-timer-back-c-review.md) resolves
`r1_stream_timer_create_back` and passes 108 registration cases through the actual
C timer constructors, tick and wake providers. The current composition has 169
application imports. The dispatcher and architectural zero-divisor provider
remain unresolved; the registration frame gap above remains.

The subsequent [native stream dispatcher](stream-dispatch-c-review.md) resolves
`r1_stream_timer_dispatch` with a tested C candidate. Its deferred-cleanup
continuation at `0x89ba8` remains an explicit import, so application imports stay
at 169. The architectural zero-divisor provider and physical sensor delivery
remain unfinished.

The architectural zero-divisor dependency is now supplied by the
[shared primitive](divide-zero-c-review.md), with these callers tested against
the actual provider under nontrapping emulator conditions.
