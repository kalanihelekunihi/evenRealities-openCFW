# Reset and main startup recovery

Reset assembly is adapted from authenticated NationalChip lvp_kws
arch/cpu/csky/ck804/start.S at8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
Its named stack/system/main symbols link to the recovered image-A addresses.
The40-byte output is byte-exact. The original PSR value, control-register31
bit3 clear, initial stack pointer, system-init/main order and returned-main
loop are checked with varied initial control values and helper clobbers. Four
regression tests reject wrong stack/control/call/loop destinations. The MIT
startup notice is included by the experimental package Makefile target.

Reset integration passes278 tests. There are121 C functions and two architecture
assembly entries, with8428 C bytes,120 assembly bytes,2216 source data,80
metadata,326 fill and314922 retained bytes, across163 replacement regions.
The reset entry introduces no code-byte or frame change. It does not substitute
its original returned-main loop for the remaining main implementation.

The pinned lvp/main.c and three API headers were fetched and authenticated by
Git blob IDs. Their function order identifies the shipped main sequence. The
mode enum establishes TWS=1. Stack monitoring is absent from the shipped call
sequence. An adapted C candidate, runtime_gx8002_main.c, compiles to40/44 bytes
with an eight-byte frame matching stock. Its provenance, bindings and hashes
are in gx8002-main-candidate.json. Main is not yet admitted: a reproducible
builder, decoded loop/return checks and full integration remain.

The app-event initializer and event tick are already source-owned. System
initialization, mode initialization/tick and system shutdown remain retained
and must be reconstructed. Whole startup composition and physical boot remain
unqualified. No hardware was accessed or flashed.

Main now has a reproducible builder and decoded comparison.120 terminating
cases cover0..1024 repeated nonzero results including high-bit values, followed
by zero, with three helper-clobber seeds. Three continuing-loop checkpoints
check that nonzero ticks keep requesting event processing and another mode
tick without running shutdown. Six rejection tests cover missing frames,
wrong initial mode/helper, missing/unused tick values and wrong return frames.
The eight-byte stock frame is preserved. Main admission is registered and
full codec integration is running; package target includes its MIT notice.

Additional pinned upstream system/mode files are now authenticated locally.
Their source and stock field accesses identify the two-entry idle/TWS table,
loop flag2002E6E4 and current index2002E6E8. The five record fields are type,
init, done, tick and buffer_init. Evidence is in
gx8002-mode-source-identification.json. Upstream SystemDone is empty and stock
at package11008 is an immediate return. The remaining nontrivial system/mode
services are still separate reconstruction work.

Main integrated with284 passing tests. Codec ownership now includes122 C
functions /138 occurrences, two assembly entries and24 source-data regions,
for164 total replacements. Bytes:8468 C,120 assembly,2216 source data,80
metadata,330 fill and314878 retained. Codec SHA:
57175b6a427347945ad62d6698f1b4a11e5f3a0bc5878d7cd070387247a3f5e7.
Main's upstream-derived loop is now source-built; separate system/mode
services and whole-device runnability remain unfinished.
