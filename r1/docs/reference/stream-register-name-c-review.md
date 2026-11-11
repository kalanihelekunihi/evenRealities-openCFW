# R1 stream registration by name in C

The stock wrapper at `0x897e8` (100 code bytes) now has one C implementation,
`r1_sensor_stream_register_by_name`, in `runtime/native_stream_register_name.c`.
It uses the existing C object lookup and exposes the deeper registration body
at `0x89890` as `r1_sensor_stream_register_object`.
[Machine receipt](stream-register-name-c-review.json).

The wrapper looks up the supplied name without adding a null-name guard.
On success it forwards the returned object, group pointer, callback word,
order word and captured fifth word, returning the backend result unchanged.
On lookup failure it tests fresh logging modes in stock order, emits the
native missing-object diagnostics when enabled, then returns zero regardless
of logging return registers. Pointer values are forwarded without invented
validation or replacement strings.

The native wrapper captures the incoming fifth word before lookup. A plain C
parameter initially compiled to a later stack load; the accepted candidate
makes the capture explicit with an initialized volatile local. A separate
initialized result local preserves the native non-tail provider frame.
Both native and accepted C providers see 32-byte frames and the same full fifth
argument value. Private stack contents, including unused variadic words, are
not asserted identical.

Verification passed 3,584 paired cases covering null/opaque name and group
pointers, full-width callback/order/flag words, found/missing objects, backend
return values, logging modes and interrupt masks. Modeled lookup mutations of
the incoming stack word stress capture timing; the actual lookup implementation
does not establish such writes. No downstream string dereference or live
registry traversal is inferred from these modeled providers.

Another 64 paired cases execute the actual native/C factory activation and
registration wrappers together. Lookup and deeper registration remain modeled.
The registration wrapper retains its 32-byte relative frame; the factory
activation caller's existing 16-versus-24-byte gap remains explicit. Five mutants
were rejected: skipping null-name lookup, narrowing flags, deferring fifth-word
capture, changing the SDK tag and returning nonzero for a missing object.
Production replay passed again after the negative controls.

All 608 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 607 objects remain
identical. The name-wrapper import resolves while the object-registration
import becomes explicit, leaving totals unchanged at 168 application imports
and 34 bootloader imports. The deeper frontier candidate name now matches its
valid C interface; that row remains unresolved, not an accepted provider.

The scoped qualifier admits no executable bytes. The source plan is unchanged,
and the fresh hybrid matches the locked application using 4,271 source-built
bytes, 641,889 executable pull-through bytes and 248 resource bytes. This step
does not establish deeper allocation/subscription behavior, actual stream
registration or callback delivery, a complete source-only link, candidate byte
identity or physical hardware operation. APSR and unused private words remain
outside the replay comparison.

The subsequent [sample-buffer converter](stream-sample-rate-c-review.md) supplies
one dependency of object registration. The backend itself and its final C
call chain remain unfinished.

The subsequent [object-registration body](stream-register-object-c-review.md)
resolves the backend import in C with documented frame and architectural gaps.
