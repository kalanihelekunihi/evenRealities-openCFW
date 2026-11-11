# R1 hardware health module startup in C

`native_health_module.c` supplies startup `0x4c5c4` as ordinary C, following the
[native contract and corrected boundary](health-module-native-analysis.md).
The [review receipt](health-module-c-review.json) binds REA stock bytes, production
source/object hashes, differential checks, native initialization and qualification.

Startup installs the wear-status callback through the existing C Goodix setter,
then freshly reads its algorithm-stream handle. A zero handle registers `acc`/`algo`
with the stock callback, rate 1 and flags 1, publishing the raw returned handle
after registration. It writes status 2, registers group 4 then group 3 against
the address of the existing system thread-reference cell, and returns the raw
result of the final wear/raw-HR start routine. Earlier provider result words do
not stop this sequence. The callback arguments remain pointer-only contracts;
their bodies and full callable signatures are not inferred from registration.

The stream handle owns four bytes at `0x20006e98`; status owns one byte at
`0x2001e479`, adjacent to the separately owned health-mode byte. Native RW and ZI
handlers run on poisoned memory with guards, and an independent RW decoder
confirms all five owned bytes start at zero. The existing Goodix callback word
at `0x200076c8` and system event context are reused without duplicate definitions.
Final source-only placement remains unproven.

The fixture passes 576 paired stock/C cases covering handle/result boundaries,
first-provider handle installation/clearing, registration-time handle mutation,
subscriber-time status mutation, raw return words and interrupt masks. Another
288 paired cases execute the actual C Goodix setter with the new startup body.
Provider arguments, state, write widths and R0 are compared; preserved registers,
SP, masks and FPSCR are checked. Both routines use a 16-byte provider-call frame
and restore it before the final call. Seven compiled defects are rejected: wrong
flags, wrong status, thread value instead of its address, rejection of a zero
returned handle, wrong group, wrong final result and a stale handle read.
Other provider bodies remain modeled. Caller-clobbered registers, APSR and private
stack residue are excluded. Physical/concurrent startup remains unverified.

All 639 units compile and both relocatable compositions pass without duplicate
strong symbols. All 638 previous objects are unchanged. The module import is
resolved while five deeper native imports are exposed: ADT, motion, group-4 and
sleep callbacks, and the final raw-HR start routine. Application/bootloader imports
are therefore 175/34. Manifest validation passes. Exact qualification rejects the
body; the canonical plan remains at 4,339 source-built bytes. A fresh hybrid
matches the locked application with 641,821 executable pull-through and 248 resource
bytes. Complete source-only linking and byte identity from C remain unfinished.
