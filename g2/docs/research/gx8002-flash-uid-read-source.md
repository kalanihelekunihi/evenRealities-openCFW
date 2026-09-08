# Flash UID read candidate

Recovered runtime_gx8002_flash_uid_read.c at package0x16118/runtime10024104.
Native macOS-Os fits140/140 bytes and matches the original12-byte saved frame.
Signature follows the authenticated interface declaration: byte buffer, signed
int capacity and int output count. Not admitted; decoded qualification pending.

Reads selected_device and manufacturer byte at+6 (not the signed halfword used
by OTP routines). Unsupported values other than85/5e write output count zero
and return-1, with no helpers/MMIO. Supported paths store MIN.S32(requested,16)
to output before wait-idle. Then controller8=0,4c=0,0=c07,4=count-1,10=1,
18=40000,f4=0,8=1,60=4b, followed by four zero writes to60. Each received byte
polls28&8, reads60, stores low byte and advances destination modulo32 until
buffer+count. RX-empty runs and return is0. No extra controller teardown.

Zero count still configures count-1=ffffffff and sends all five prefix bytes.
Negative capacities retain their bit pattern and represent huge unsigned loop
distances in machine code; source preserves this rather than clamping them.
No physical buffer validity or hardware behavior is established. Need decoded
output alias/order, byte/word effects, clobbers, boundaries and large signed
count loop qualification before admission.

Aligning the public signature to the interface's signed int capacity and output
count reduced native code to136/140 bytes (initial unsigned signature140).
The current builder report and C source use the signed signature; behavior
still needs decoded verification.12-byte frame unchanged.

Prepared expected-event model and five passing model tests. Covers rejected
manufacturer count-zero behavior, accepted zero request with all five FIFO
writes, byte-only manufacturer comparison, positive count clamping, wrapped
receive addresses and count-store ordering even when output aliases selected
state. Negative count finite traces explicitly fail rather than silently
clamping to zero/16. Decoded source/stock execution still remains; model tests
alone do not qualify this candidate.

Initial decoded stock/source comparison passes960 cases: requests0..17,31,
INT32_MAX; four manufacturer bytes; ordinary and selected-state/device-word
output count aliases; two polling schedules and two clobber seeds. Exact
read/write/helper/byte traces and12-byte frame/ABI return match the expected
model. Negative capacities and target rejection tests remain before admission.
No physical controller or UID data was accessed.

UID checks expanded with five target rejection tests (ten including model)
and16 negative-capacity MIN.S32 checkpoints.960 full positive/zero cases still
pass. Checkpoints prove selection only; full huge-loop/exit qualification
remains and UID is not admitted. No hardware operation was performed.

Added a pinned eight-instruction receive loop for each binary, with 252 decoded
step cases and a reviewed modular counter argument. Fourteen summarized
entry/exit cases with three final-word/status variants connect negative count
selection, count output, controller setup, loop postconditions and RX-empty
cleanup/return. The 960 complete finite traces and 16 regression tests pass.
The admission adapter now records the argument hash and rebuilds all evidence;
full codec integration is running. Large-count qualification is conditional on
modeled accesses, not validity of a multi-gigabyte RAM buffer or physical UID
behavior. See gx8002-uid-receive-loop-argument.md for those assumptions.

UID read integrated after all reviewed comparisons reproduced on macOS. The
candidate now includes 118 C functions (134 code occurrences), 16 data regions,
and 150 total replacement regions. All 254 integration tests passed. Ownership:
8180 compiled C bytes, 2040 source data, 80 metadata, 326 fill, 315466 retained.
Codec SHA:3e4bb3499377dd3334e2d9a66561cbc29d35cbc2335f6308b954c31a4dc7424d.
UID qualification comprises 960 full traces, 16 signed-count checkpoints,
252 receive steps, 14 summarized transfers with three postcondition variants,
and 16 regression tests. See the pinned loop argument for access assumptions.
All non-null functions in the identified flash interface now have integrated
source, but the interface table, device records and wider firmware still have
remaining ownership work. Source-only completion and hardware qualification
are not claimed; the goal remains active.
