# R1 HRV scheduler native contract and C conversion constraint

Follow-up: the [C scheduler review](hrv-scheduler-c-review.md) now implements this
contract with the production record offset preserved. The native-only status
below describes this analysis snapshot, before that implementation.

The [native analysis receipt](hrv-scheduler-native-analysis.json) binds REA's
784-byte code/data read at `0x49f0c`, the locked application and ELF hashes,
and 2,064 successful native probes. The executable scheduler body is 382 bytes.
REA's merged callback pseudocode includes this tail-called body, but it has
its own entry, frame and argument contract. This is native analysis evidence;
the scheduler remains unimplemented in C.

The scheduler first checks flag bytes 1 and 2 and requires mode byte 1. It then
reads the health-enable flag; when enabled it checks wear mode, timer, and
stream, in that order. It does not recheck the initial mode after providers.
Nonzero input, including `0xffffffff`, skips the clock and logs the successful
start as `hourly`. Zero input reads local timestamp and logs `catchup`.

For zero input the unsigned calculation is `3600 - (timestamp % 3600)`.
Remaining time at or below 150 seconds skips scheduling: timestamp 3449 starts,
3450 does not. Accepted starts use **120 seconds**, or 120,000 milliseconds.
The subsequent subtraction/clamp path cannot reduce that duration once the
strict greater-than-150 gate has passed. Timestamp wrap inputs were included.

Timer creation uses timeout callback `0x49e5d`, duration 120,000 and argument
zero. The returned timer is published after the provider returns. A nonzero
result clears the 208-byte session buffer and registers `hrv` / `algo`, with
producer `0x4a24d` and arguments 1,1; its stream is also published late. Timer
creation failure logs without clearing the buffer. Stream registration failure
logs, then calls the existing timer-release routine, which reads the fresh
timer field and clears it after the lower release returns. Success logs carry
the label and duration using ring tag `0x0c800000`; failure and disabled-health
logs use `0x0c000000`. The SDK tag is `0x001c0003`.

Of the 2,064 probes, **640 execute the actual native flag getter and record
reader**, with full, prefix24, prefix25, flag-only and absent NV writes, both
read statuses, four flag-byte inputs and sixteen poisoned-stack seeds. The
scheduler frame is 32 bytes, the getter frame eight and the record reader
frame 64: the record starts **104 bytes below scheduler entry**. The reader
ignores storage status and consumes unwritten record byte 24. Absent-write
results vary between 0 and 1 across seeds, establishing that a changed caller
frame can change scheduling. A C candidate must preserve and directly verify
this behavior with the actual getter/reader before acceptance. A mocked
health-enable result would omit this dependency.

The probes check call ordering/arguments, logging, late handle publication,
public SRAM and guards, saved integer registers, SP, interrupt masks and FPSCR.
External time, wear-mode, logging, allocation/registration and timer-release
providers are modeled. This establishes neither C equivalence, final source
linking, complete scheduling nor physical hardware operation. Production
firmware sources, manifests, frontier selections and source plan were not
changed by this analysis.
