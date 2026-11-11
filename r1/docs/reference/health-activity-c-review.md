# R1 health activity startup in C with preserved flag-getter frame

`native_health_activity.c` supplies activity startup `0x48d9c`, flag getter
`0x493f8` and the empty callback `0x491b8`. The
[review receipt](health-activity-c-review.json) binds REA bytes, production hashes,
native comparisons, raw-record counterexamples, initialization and qualification.

The C coordinator clears two words in order, reads the persisted enable byte,
conditionally logs and dispatches authorization `(0,1)`, then always registers
group 4 with the empty callback and the address of the system thread-reference
cell. Authorization and earlier log return words do not stop registration. The
raw subscriber result is returned, including full-word errors. Only the two words
at `0x20006ec4`/`0x20006ec8` are newly owned. Native RW/ZI execution on poison with
guards and an independent RW decoder confirm all eight bytes start at zero.

A plain C byte-local getter compiled with a 16-byte frame; stock uses eight bytes.
This is observable because the existing record reader ignores failed/partial NV
read status and consumes unwritten record bytes. Sixteen poisoned-stack probes
execute the actual native/C reader: the record moves from SP-72 to SP-80 and the
returned flag differs in nine cases. The original C source and object are retained
in ignored verification artifacts. The final getter preserves the native 22-byte
saved-R3 frame boundary, initializes only its output byte, calls the canonical
reader with word output null, loads the byte and restores the saved word. It does
not duplicate the record reader or zero its unwritten record. A future plain C
replacement still needs to prove this frame-dependent behavior under its compiler.

The final fixture passes 3,190 paired cases executing the existing C record-reader
kernel and its required frame bridge. Cases cover full, prefix, flag-only,
word-only and absent record writes, ignored NV status, sixteen random stack seeds,
flag bits, interrupt masks, changing log modes, provider state mutations, raw
subscriber results and the empty callback's integer/NZCVQ/FP state. Record addresses
remain SP-72 for the standalone getter and SP-80 through activity startup. Public
state, control write widths, provider arguments and enable/getter R0 are compared;
preserved registers/SP/masks/FPSCR are checked. The C kernel adds provider-call
depth but keeps the record address and unwritten contents intact. NV class-read,
authorization, subscriber and logging providers remain modeled. Caller-clobbered
registers, APSR and private stack effects are excluded except for the empty hook.
Eight compiled defects are rejected: missing word clear, skipped disabled-state
subscription, wrong authorization channel, thread value instead of address, wrong
SDK tag, boolean return, nonempty hook and the unconstrained C getter.

All 651 units compile and both relocatable compositions pass without duplicate
strong symbols. All 650 earlier sources and objects are unchanged. Activity startup
is resolved without new imports, leaving application/bootloader imports at 170/34.
Manifest validation passes. Exact qualification selects two distinct regions:
the 22-byte getter boundary and two-byte C callback; the C coordinator is rejected
as nonexact. A fresh hybrid matches the locked application before promoting those
24 source-built bytes. These are not 24 bytes of pure C implementation. The plan
now has 4,369 source-built bytes, 641,791 executable pull-through and 248 resource
bytes. Complete source-only linking, full C reconstruction, final RAM placement
and physical/concurrent hardware validation remain unfinished.
