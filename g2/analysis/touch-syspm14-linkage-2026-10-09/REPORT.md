# PM registration and sleep wrapper linkage

Three unchanged public-source selected extents match:
RegisterCallback `[0xA3B0,0xA444)`148bytes;
CpuEnterSleep `[0xA528,0xA58C)`100bytes;
CpuEnterDeepSleep `[0xA58C,0xA5F4)`104bytes. All352newbytes await review.
The no-callback sleep/deep-sleep helpers also match20/40bytes, outside the
selected denominator. Existing32assemblybytes are reused.

Registration validates a callback descriptor and inserts it into the callback
list in order, updating previous/next pointers. Original PC-relative references
bind the source callback-list state to `0x20000F34`; no runtime list population
is assumed. Sleep wrappers perform callback readiness/check phases, enter a
critical section, invoke before/after transition phases and the direct sleep
helper, restore PRIMASK, and dispatch the completion/failure phase.

Important residual: authentic ExecuteCallback remains mismatched at
`0xA444` (69 differing bytes over its emitted220byte extent). It is linked at
the proven call address but its mismatch is recorded, not counted exact.
Consequently matching wrappers establish local static bytes/call topology,
not a matching complete sleep composition, callback semantics, physical sleep,
or IRQ delivery. `results.json` preserves each dependency and mismatch position.
