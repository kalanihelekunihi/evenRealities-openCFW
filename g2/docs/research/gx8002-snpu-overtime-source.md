# GX8002 overtime diagnostics/restart candidates

Stock dump helper: package0xf064/runtime0x10205ad8, envelope68, frame24.
It reads32 words sequentially, prints each using `0x%08x `, prints a newline
after words10/20/30, then a final newline after word32. The source uses a
countdown for line breaks, producing60 bytes with the same24-byte frame.
GCC's modulo optimization had produced80 bytes; that attempt was not linked
or admitted. Observed r0 is the final printf return, preserved explicitly.

Stock overtime reset: package0xf0a8/runtime0x10205b1c, envelope188, frame32.
Candidate188 bytes/frame28. Reads indexed base-address2 through pointer5cc,
current command and previous interrupt through live pointer5c4. Prints
addresses, dumps32 words before the mapped current command minus128, prints
another heading, dumps32 words at the mapped command, then reads/prints its
first byte. Mapping is unsigned32 addition of0x20000000.

If previous interrupt is zero, retrieve task head through a fresh pointer5c4.
Otherwise head is the word at previous+0x20000004. Then disable via5c4,
reset via5c8, initialize registers, restore head via fresh5c4, enable via
fresh5c4. No idle wait is present here. Original helper return values are
ignored. The control flow must not be merged with suspend/resume behavior.

The five literal strings are source-defined and checked byte-for-byte:
word format8 bytes at1020ac0e, address format70 at1020ac16,
before heading30 at1020ac5c, command heading23 at1020ac7a, type format16
at1020ac91. Total147 bytes. Existing source-owned newline at1020b7c2 is
reused, not claimed twice. All sizes include terminating NUL.

Files: runtime_gx8002_snpu_overtime_reset.c,
build_gx8002_snpu_overtime_candidate.py,
gx8002-snpu-overtime-candidate.json. At the initial candidate checkpoint both routines and all five strings
were unqualified and unregistered. Qualification required state/pointer mutations at helper
boundaries; distinct mapped memory values; printf ABI/clobbers; changing dump
reads; both head-selection paths; exact restart order and ABI checks. Command
addresses must be modeled within valid mapped readable memory. Source's
command byte and head reads use const RAM pointers; qualification must verify
actual emitted loads and ordering. No physical hardware validity claim.

Dump qualification checkpoint: verify_gx8002_snpu_dump.py compares decoded
stock and candidate instructions against an independent read/printf sequence.
402 cases cover three aligned RAM locations, full-width seed patterns, fixed
and changing read responses after print calls, caller-register clobbers and
the24-byte frame. Eight tests check exact32 reads, newline positions10/20/30/32,
final printf return, wrong stride/count/target and broken frame. The reviewed
report gx8002-snpu-dump-verification.json deliberately keeps source_admitted
false: the combined ELF also contains the still-unqualified reset routine.
That dump-only checkpoint left the integrated firmware unchanged at 512 tests.


## Combined admission

Both functions and five strings are now qualified and registered through
verify_gx8002_snpu_overtime.py. Its independent model composes decoded dump
execution with reset execution, including the actual nested stack pointer,
changing reads, caller clobbers and live state-pointer changes at every helper
and print boundary. All 4,824 reset cases and 402 dump cases pass; 14 reset
tests and eight dump tests exercise both head paths, all 256 command-byte
encodings, scratch initialization/bounds and mutation rejection. Source frame
is 28 bytes versus stock 32; nested dump frame is 24 in both.

The standalone dump report intentionally remains source_admitted=false: it
alone cannot admit the combined ELF. The combined overtime report supplies
admission for both code sections and all five strings. Full native macOS
integration passes 534 tests. Hardware behavior remains unqualified.
