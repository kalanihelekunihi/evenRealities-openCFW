# R1 wear ADT status and teardown in C

`native_wear_adt.c` supplies status callback `0x3d150` and teardown `0x3d0c0` as
ordinary C. The [review receipt](wear-adt-c-review.json) binds REA stock bytes,
production hashes, differential checks, native initialization and qualification.

The callback stores the incoming low byte but retains the full word for control
flow. Sleep gate exactly 1 tears down. Otherwise a nonzero handle/status OR only
tears down for full-word status exactly 1; zero handle and zero status register
`adt`/`algo`, rate 1, flags 1. The returned handle is published after registration,
then the timer is freshly read; an absent timer is created for 7000 ms with the
native timeout callback and context zero, then published. High status bits must
not be discarded after the byte store. The startup module's ADT declaration now
uses the established uint32 argument; its compiled object remains unchanged.

Teardown captures the stream handle, clears it before unregistering `adt`, then
clears active byte and count word. It freshly reads the timer and clears that
word before release. Provider mutations can therefore leave a new stream or timer
installed. This differs from raw-HR teardown's late clears and is preserved.
The deeper sample `0x3ce1c` and timeout `0x4c6cc` contracts remain pointer-only.

Six fields own 15 bytes: status `0x20006e94`, stream `0x20006e9c`, timer
`0x20006ea4`, active `0x2001e468`, count `0x2001e46c` and sleep gate `0x2001e47a`.
Native RW/ZI execution on poison with guards and an independent RW decoder agree
that status starts at 1 and the other fields at zero. The initial zero-status C
probe was corrected before final build/verification. Adjacent wear and health
fields remain separately owned; final source-only placement remains unproven.

The fixture passes 8,730 paired stock/C cases, covering full-word status boundaries,
sleep gate values, zero/full-word handles and provider results, mutations of the
public fields at each provider boundary, and interrupt masks. It compares provider
arguments, callback pointers, public state and write widths, and checks preserved
registers, SP, masks and FPSCR. Seven compiled defects are rejected: truncated
branch status, boolean sleep gate, late stream clear, late timer clear, wrong
period, lost count clear and stale timer. Providers remain modeled. Both routines
have void contracts; R0 residue, caller-clobbered registers, APSR and private stack
are excluded. Physical/concurrent behavior remains unverified.

All 643 units compile and both relocatable compositions pass without duplicate
strong symbols. All 642 earlier objects remain unchanged. ADT status is resolved
while sample and timeout callbacks are exposed, leaving application/bootloader
imports at 174/34. Manifest validation passes. The callback's working executable
span is recorded as 74 bytes; teardown remains 42. Neither body qualifies as exact.
The plan stays at 4,341 source-built bytes. A fresh hybrid matches the locked
application with 641,819 executable pull-through and 248 resource bytes. Complete
source-only linking and byte identity from C remain unfinished.
