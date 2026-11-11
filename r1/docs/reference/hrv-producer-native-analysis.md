# R1 HRV producer native contract before C conversion

Follow-up: the [C producer review](hrv-producer-c-review.md) now implements the
surrounding control flow while retaining two FP instruction boundaries. The
native-only implementation status below describes this earlier analysis snapshot.

The [receipt](hrv-producer-native-analysis.json) binds REA bytes, the locked
artifact/ELF hashes and **4,464 native cases: 4,448 completed and 16 matched
expected fault cases**. An independent live-memory ring oracle checks the
sampling stage, including payload/metadata aliases. This is native contract
analysis; the 336-byte producer at `0x4a24c` still needs a C implementation.

The callback ignores context R0 and length R2, consuming payload R1. It first
increments the halfword at session-buffer offset 206, wrapping to 16 bits.
Values below 10 return without touching the payload. Otherwise it rereads
payload byte 9 for each iteration and handles at most four halfword samples.
Zero samples are skipped. Buffer fields are head at 200, used at 202, valid
at 204 and callback count at 206. Below 100 used entries, insertion is
`(head + used) % 100` and used increments. At or above 100, the **unchecked
old head** selects the replacement slot; a nonzero replaced value decrements
valid, and head advances modulo 100. The incoming sample is reread after these
metadata writes, then stored, then valid is freshly incremented with halfword
wrap. Head values 100 and 65,535 are covered: writes can target metadata or
memory outside the 208-byte buffer. A C replacement must not silently clamp
this stock behavior or cache the live count/sample across aliasing stores.

After the loop, fresh callback count must reach 60 and fresh valid count 70.
The RMSSD provider receives the raw buffer and current used count. The callback
captures **whether a timer exists after that provider returns**, before its
floating comparison and fresh wear-mode predicate. Stock uses signaling
`VCMPE` against zero; both quiet and signaling NaNs fail the comparison, skip
the wear query and set the invalid-operation flag. An ordinary quiet C compare
would miss that exception behavior. Tests architecturally warm the FP context
before setting FPSCR, and cover FZ, DN, rounding modes, signed zero, denormals,
NaNs and infinities. The receipt retains representative exact FPSCR results.

Positive results with a nonzero wear predicate create a fully initialized
eight-byte event: low halfword of native `VCVT.u32` conversion, zero halfword,
and a fresh backend timestamp word. Event kind is 7; event-publish failures
are ignored. The callback tears down the session, then—only if the captured
timer-presence flag was true—releases the **fresh** shared timer through the
existing C coordinator and sets state flag byte 1 to 1. Native conversion
saturates positive infinity/overflow before narrowing; an unchecked C cast
cannot establish the same values and exception flags.

Failure emits fresh-mode ring/SDK logs, then uses the captured timer-presence
flag differently: a present timer clears only the 208-byte buffer, leaving the
stream and timer; no timer invokes session teardown, potentially unregistering
the stream, then clears the buffer. Neither branch releases the timer. It
does not set the success-completion flag.

Cases cover callback/used/valid wrap boundaries, ring-head overflow, count
0/1/4/5/255, zero/nonzero samples, payload aliases with ring/metadata, initial
timer presence, FP results and wear predicates. Null and `0xffffffff` payloads
fault only when the callback-counter gate reaches payload access; the earlier
return still works. RMSSD, wear/time, event, logging, unregister and lower timer
release are modeled; native cleanup, memory clearing and producer instructions
execute. Preserved integer/FP registers, SP and interrupt masks are checked on
return. This does not prove the RMSSD algorithm, C equivalence, concurrency,
physical operation or final source linking. All 655 current source/object
hashes, manifest and canonical source plan remain unchanged by this analysis.
