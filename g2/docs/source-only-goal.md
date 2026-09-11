# Active G2 source-only firmware goal

User direction, 2026-09-07: continue until the final firmware no longer
requires opaque functionality or binary extraction to supply functionality.
The supported build host for this work is this macOS computer. Linux build
support is not a completion requirement; existing Linux records are historical
evidence and do not justify delaying macOS reconstruction.

## Completion conditions

Every selected component must build from reviewed source and identified,
pinned upstream dependencies. Required initialized data, assets, model
parameters, and accelerator programs must have an understood, maintainable
source representation or a functionally qualified source-authored replacement.
Original firmware may serve as an authenticated analysis or differential-test
oracle, but must not supply bytes to the final build.

Typed external-provider interfaces, opaque bytes encoded as C arrays, trap
stubs, and merely compilable decompilation do not satisfy this goal. Compiler
success, package checksums, and a gapless flash map do not establish runnable
firmware. Startup, inter-component protocols, memory/peripheral behavior, and
full-device operation still require appropriate qualification.

The goal remains active until these conditions hold. Zero *unclassified*
bytes is not the same as zero opaque behavior.

## Build and evidence tracks

- `make -C g2 source` builds the existing hybrid reference for macOS. Preserve
  its verified behavior while replacing providers. It still requires stock
  payloads, so it cannot be the final source-only deliverable.
- `make -C g2 transparent-image` builds experimental Apollo recovered source.
  It remains unqualified and contains vendor-derived data and traps. Its
  reviewed-source manifest now allows verified C to supersede incorrect
  decompilation without silently falling back to it.
- `make -C g2 transparent-test` checks reconstruction, source admission,
  behavioral boundaries, and placement contracts on macOS.
- `report_transparent_coverage.py --require-release-ready` also rejects
  unreviewed emitted functions, in addition to traps, copied data, and
  compilation/placement failures. This is an Apollo software gate, not a
  six-component hardware qualification or redistribution authorization.

## Remaining scope

The existing six-component assessment still classifies every component as
source-incomplete: Apollo main, Apollo bootloader, EM9305, GX8002 codec/DSP,
PSoC touch, and STM32 case. Its machine-readable detail is in
`docs/reports/openCFW-completion-2026-08-28/assessment-data.json`; the file's
historical directory name does not imply the current data has that date.

Apollo has extensive identified third-party source which should replace
unreviewed decompiler output wherever the configuration and ABI are established.
Its experimental builder also needs a reviewed solution to stock-envelope
size limits, split functions, register/stack artifacts, and recovered data.
The [Cortex-M55 tranche](research/g2-cortex-m55-reviewed-source.md) addresses
four processor/memory functions first and documents why general decompiler
helper substitution is insufficient.

The codec has 190,912 retained executable bytes, 5,124 runtime-data bytes,
9,164 accelerator-command bytes, and 120,800 model bytes. Its typed-provider
boundaries have not reconstructed those contents. Public NationalChip grus
sources and the C-SKY toolchain are the next upstream route to investigate;
an interface-only attribution is not an implementation.

The [pinned upstream object comparison](research/gx8002-upstream-object-candidates.md)
now supplies 102 candidate matches for 68 driver symbol names. It adds no
source ownership but gives the next C-SKY reconstruction work named targets.

Do not erase or overwrite existing uncommitted reconstruction work. Do not
relabel source availability, candidate compilation, or retained byte arrays
as production source ownership.

The [macOS C-SKY toolchain and analog tranche](research/gx8002-analog-source.md)
now builds seven recovered codec leaves and checks target MMIO traces. These
172 compiled bytes correspond to 344 stock bytes across two occurrences;
production integration is still pending, so retained-byte accounting is unchanged.

The [cache tranche](research/gx8002-cache-source.md) adds an exact upstream
CSI data-cache enable adapter (32 bytes, three stock occurrences) and recovers
the distinct 28-byte external instruction-cache enable function. Both compile
on macOS; neither is yet a production firmware provider.

The [codec integration candidate](research/gx8002-source-candidate-build.md)
now emits a complete experimental FWPK and EVENOTA package using these nine
functions: 468 compiled C bytes across 18 occurrences, 80 generated header
bytes, and 325,544 explicitly retained codec bytes. Its source-only gate fails
as required. The default build remains separate and hardware qualification is
still outstanding.

The [native Ghidra C-SKY harvest](research/gx8002-ghidra-processor.md) now
provides 24 named image-B decompilations. A reproduced upstream `movih`
width bug is corrected in the local analysis copy and checked against actual
p-code; volatile MMIO classification preserves separate hardware updates.
These exports are analysis evidence, not additional source-admitted functions.

The [I2S tranche](research/gx8002-i2s-source.md) brings the codec integration
candidate to twelve functions: 564 compiled bytes across 24 occurrences,
80 generated metadata bytes, and 325,448 retained bytes. Exact instruction
comparison permits only consistent caller-saved scratch-register renaming.

The [VAD curve tranche](research/gx8002-vad-curves.md) adds five independently
qualified functions at nine occurrences. The codec candidate now has seventeen
functions, 948 compiled C bytes, 80 generated metadata bytes, 42 generated
unreachable fill bytes, and 325,022 retained stock bytes. Fill is counted
separately from code. The rebuilt package still requires whole-device validation.

The [upstream model inventory](research/gx8002-upstream-model-inventory.md)
checks 17 authenticated SDK model headers; none matches the codec command and
weight sizes. Their task/buffer interfaces remain a reconstruction lead, but
no model arrays have been admitted or substituted.

The [model interface tranche](research/gx8002-model-interface.md) adds ten
byte-exact functions using the pinned upstream GRUS task header. The codec
candidate now has 27 functions, 1,054 compiled bytes, 80 generated metadata
bytes, 42 generated fill bytes, and 324,916 retained bytes. Model/task buffer
roles are clearer, but the graph, coefficients, NPU commands, and remaining
runtime are still source-incomplete.

The C-SKY harvest also now resolves scalar literal-pool references through
explicit read-only propagation. All 24 seeds and the analog address regression
pass; this improves analysis fidelity without admitting additional firmware bytes.

The [saved-task copy recovery](research/gx8002-task-copy-recovery.md) traces
the setter to a 126-byte SRAM memcpy body. A portable C candidate compiles to
26 C-SKY bytes on macOS and passes 4,128 host cases. Target instruction and
placement qualification remain pending, so no additional bytes are admitted.

The copy candidate now also passes 4,128 restricted target-execution cases,
including byte-access traces and bounds. Stock-path comparison and placement
remain pending; the source-admitted byte count is unchanged.

The copy verifier now executes the authenticated stock body too. All 4,128
alignment/length cases match the compiled candidate in final RAM, return
pointer, and accessed bytes. Access widths/order, timing, and placement remain
outstanding; no source-admission claim is made from these finite cases.

The copy C now preserves the stock aligned word paths and exact memory-access
sequence in all 4,128 target comparisons. It compiles to 210 bytes versus the
126-byte original, so placement/size and timing qualification remain. This
supersedes the 26-byte byte-only candidate; no firmware admission yet.

Size optimization with loop rewriting disabled reduces the recovered memcpy
to 96 bytes while preserving all 4,128 exact memory-access comparisons. It is
now integrated at the original entry in the experimental codec: 28 functions,
1,150 compiled bytes, 80 metadata, 72 fill, and 324,790 retained bytes.
Hardware timing and the full six-component source-only objective remain open.

The saved-task setter now compiles and links byte-exactly against the recovered
memcpy entry. Another 1,024 host cases cover copy then translation. The
experimental codec reaches 29 functions, 1,170 compiled bytes, 80 metadata,
72 fill, and 324,770 retained bytes; its package hash is unchanged.

The application-event cluster after the model interface now has authenticated
upstream source matches for its callback layout, queue setup, and watchdog
arguments. A resume-dispatch C candidate compiles on macOS but does not yet
fit the stock body. See research/gx8002-app-core-recovery.md; no new admission.

The resume callback now links byte-exactly in 28 bytes with authenticated SDK
headers. Nine host dispatch cases pass. Experimental builder admission remains
next; this verification does not change retained-byte totals.

The 28-byte resume callback is integrated into the experimental codec with
mandatory linked-byte verification. Totals are now 30 functions, 1,198 compiled
bytes, 80 metadata, 72 fill and 324,742 retained bytes. The remaining runtime,
model/data and full six-component source-only work remain open.

The suspend callback now links byte-exactly in 32 bytes and passes nine host
cases for watchdog-before-callback order. Its watchdog-stop C dependency is
14 bytes versus a 12-byte stock envelope, so neither is newly admitted yet.

The watchdog-stop size gap is resolved with one documented BCLRI inline
assembly expression inside C. Its 12-byte body and the 32-byte suspend callback
are byte-exact and integrated. Experimental totals: 32 source functions,
1,242 compiled-source bytes, 80 metadata, 72 fill, 324,698 retained bytes.
The ledger compiled_c category includes that explicit single instruction.

Unmodified pinned upstream queue C now builds on macOS. Init, IsEmpty and
IsFull match 54 stock bytes exactly; 12,000 host queue operations pass. These
three sections await builder integration. Get/Put and optional buffer APIs
are not target-qualified by compilation or host tests alone.

The three byte-exact upstream queue sections are integrated directly from
the authenticated SDK C. Experimental totals: 35 functions, 1,296 compiled
bytes, 80 metadata, 72 fill, 324,644 retained bytes. Six relevant tests pass.

Upstream QueueGet now passes 2,196 stock/compiled target comparisons with exact
memory traces and an independent FIFO oracle. Three interpreter tests pass.
The 70-byte section fits the 74-byte stock body; integration remains next.

Upstream QueueGet is integrated with 70 compiled bytes and four separately
counted fill bytes. Experimental totals: 36 functions, 1,366 compiled bytes,
80 metadata, 76 fill, 324,570 retained bytes. Nine relevant tests pass.

Upstream QueuePut now passes 2,196 stock comparisons with exact access traces
and an independent FIFO oracle. Its 86-byte SRAM section fits the 90-byte stock
body. Five relevant tests and the prior QueueGet comparison pass. Put awaits
builder admission; retained-byte totals are unchanged in this step.

Upstream QueuePut is integrated at its original SRAM entry, replacing 90
retained bytes with 86 compiled bytes and four generated fill bytes. Totals:
37 functions, 1,452 compiled bytes, 80 metadata, 80 fill, 324,480 retained.
Ten relevant tests pass; complete source-only and device qualification remain open.

The event-trigger wrapper now links byte-exactly in 20 bytes against the
recovered queue-write entry. A host test covers 64 fill/drain cycles including
silent full-queue rejection. Builder integration is next; totals are unchanged.

The byte-exact event-trigger wrapper is integrated. Experimental totals:
38 functions, 1,472 compiled bytes, 80 metadata, 80 fill, 324,460 retained.
Seven relevant tests pass. The full source-only objective remains open.

Event-tick C now compiles in 80 bytes and passes eight host callback/order
cases, including replacement or removal of the active application by callbacks.
Watchdog-ping C matches ten stock bytes exactly. Both await target integration;
UART service and tick branch/relocation qualification remain open.

The UART tick dependency now has authenticated upstream provenance and a
132-byte C candidate. Thirty-two host dispatch/CRC-gate cases pass. CRC and
logging remain mocked in tests and retained in firmware; target qualification
and integration remain pending.

The UART CRC core matches the SDK's zlib-derived implementation. Its 1,024-byte
lookup table is now generated mathematically and matches three stock locations.
1,025 zlib comparisons plus incremental checks pass. Table placement and CRC
executable qualification remain pending; generated arrays are derived from the
polynomial, not extracted stock bytes.

CRC C now uses forward-only aligned word processing and the mathematical table.
2,052 host cases match zlib across alignments, seeds and incremental updates.
Native C-SKY compilation succeeds; helper placement, table relocation and
stock instruction comparison remain pending.

The CRC core, wrapper and mathematical table now link at original addresses
without unresolved dependencies. Core is 160 bytes within 180; wrapper/table
are byte-exact. Unexpected allocated sections and addresses are rejected.
Core instruction comparison remains pending, so firmware totals are unchanged.

The linked CRC core passes 1,028 stock/source comparisons with identical input
and table read traces and independent zlib results. Five relevant tests pass.
The code and mathematical table still await experimental integration and
separate generated-data accounting; full source-only work remains open.

Builder accounting now separates generated_source_data from compiled_c and
checks ELF executable flags. Data replacements cannot claim unreachable fill.
Six ownership tests pass. This prepares honest CRC table admission without
promoting any additional source bytes yet.

CRC code and its primary mathematical table are integrated. Experimental
totals: 40 functions, 1,644 compiled bytes, 1,024 generated source data,
80 metadata, 100 fill and 323,244 retained bytes. Eleven relevant tests pass.
The two other table copies and broader source-only work remain open.

The logger wrapper matches the SDK tinyprintf call pattern. A reconstructed
variadic wrapper links in 28 bytes and passes a host forwarding test; stock
uses a different 30-byte argument-spill layout, requiring target ABI review.
Formatter and fputc dependencies remain unresolved, with no new admission.

The formatter's output helper and libc port are now traced to SDK source.
Reconstructed fputc links byte-exactly in ten bytes; its console dependency at
0xCD7C remains unresolved. No source admission is claimed for the logger yet.

Console output is now traced through port selection, pre-narrowing CRLF
conversion and the UART transmit-ready polling loop. Three C candidates compile
on macOS. MMIO verification and port-wrapper sizing remain pending; unused
UART descriptor fields are explicitly still unreconstructed.

Console placement follow-up: the native macOS size-optimized build now fits
all three recovered functions (16/20, 36/36, 20/20 bytes). The linked console
entry is byte-exact; the reproducible linker audit rejects unresolved symbols
and relocations. MMIO and port-wrapper target comparison remains pending, so
these functions are not added to source ownership totals.

UART transmit verification: 420 stock/source cases pass exact ordered MMIO
trace comparison and an independent oracle; three interpreter tests pass.
Native macOS recompilation and fixed-address linking are part of this check.
No admission yet: the port wrapper still needs behavioral comparison.

Port-wrapper follow-up: `python3 g2/tools/compare_gx8002_uart_putc.py`
rebuilds and checks 6,160 decoded stock/source cases against an independent
transmit-call oracle. It verifies pre-narrowing newline handling, descriptor
stride/wraparound and preservation across caller-clobbering transmit calls.
Out-of-range ports are arithmetic probes, not claims of valid device access.
The underlying 420 MMIO cases also pass; six UART interpreter tests pass.
Firmware ownership integration is the next step; no new source bytes are
counted yet, and hardware behavior remains unqualified.

Console source integration completed: three reviewed functions contribute
72 compiled C bytes and four unreachable fill bytes. The native macOS codec
build and complete EVENOTA build/artifact verification pass. Codec ownership
is now 1716 compiled C, 1024 generated data, 80 metadata, 104 unreachable fill,
and 323168 retained stock bytes across 60 replacements. Codec SHA-256:
97d51cee3a0ef77ff879690132fb9d58432fa05450e7f6cfe22c03159cf77e17.
Package SHA-256: 2b948c455781f78962305d8fb98a26f90fa0b37413988762b4a346155ee1a590.
Six UART and six ownership tests pass. Descriptors/configuration and remaining
code remain retained; no source-only or hardware-completion claim.

Upstream formatter build: `python3 g2/tools/build_gx8002_tinyprintf_candidate.py`
now compiles unmodified SDK `utility/libc/tinyprintf.c` on macOS. It checks the
pinned SDK commit and Git blob identities for every SDK dependency reported
by the compiler. The source-authored configuration leaves optional long
support disabled; this still requires comparison with stock configuration.
The core formatter is 372 bytes versus the 416-byte stock entry envelope.
Its helpers and relocations remain unqualified; compilation does not count
as source admission. The original source retains its dual LGPL/BSD license
notice; any source distribution must preserve the chosen license conditions.
The build report is `gx8002-tinyprintf-candidate.json`.

Tinyprintf placement mapping: stock ui2a is package 0xfeac (120 bytes),
putf 0xff24 (24), putchw 0xff3c (212), and tfp_format 0x10010 (416).
The authenticated candidate report now records these envelopes and hashes.
Default -Os produces 124/24/240/372 bytes respectively: ui2a and putchw
do not fit. A native -Os -fno-tree-loop-optimize experiment gives
124/24/214/370, still overflowing both helpers. -O2 grows ui2a to 150
and putchw to 342 and introduces formatter jump-table data. No helper
or formatter is admitted on these placement results. Further compiler or
source recovery work must resolve the overlaps without consuming retained
neighboring functions or treating generated machine bytes as source.

A reproducible 46-variant native compiler probe now tests single/pair
optimization changes against the authenticated upstream formatter source.
`python3 g2/tools/probe_gx8002_tinyprintf_flags.py` records every section
size in `gx8002-tinyprintf-flag-probe.json`. ui2a reaches 116 bytes using
-fno-guess-branch-probability -fno-if-conversion, fitting its 120-byte entry.
No tested combination fits all four entries; putchw remains at least 214
bytes against 212 available. This resolves the ui2a size question but does
not qualify its behavior or admit any formatter bytes.

Padding-loop recovery: a preserved upstream patch moves each padding-loop
decrement into its body. The discarded final decrement affects only local
n; the space and zero modes are mutually exclusive and n is unused after
zero padding. With -Os -fno-tree-loop-optimize, putchw is 204 bytes and
fits its 212-byte entry. The upstream license remains in the patched source.
`build_gx8002_tinyprintf_padding.py` authenticates upstream, applies the patch,
compiles natively and records source/patch/code hashes. The host comparison
test passes 6,912 combinations of width, modes, sign, prefix, base, case,
text and output-failure position, comparing both attempted output and return
counts. Target execution and relocation qualification are still required.

Formatter linkage: `link_gx8002_tinyprintf_candidate.py` now rebuilds and
links ui2a/putf/putchw/tfp_format at their original entries without overlap
or remaining relocations. ui2a gets a recorded per-function optimization
attribute; applying those settings globally grew the formatter beyond its
envelope. Linked sizes are 116/24/204/370 bytes. putf is byte-exact, including
its call to fputc. Other routines still require target behavioral comparison;
unqualified variadic and memory-stream wrappers are excluded from this ELF.
No additional firmware bytes are counted as source from this link check.

Integer helper verification: `compare_gx8002_ui2a.py` rebuilds the linked
upstream candidate and compares decoded target execution against stock for
3,096 cases across bases 8/10/16, upper/lower output, small values, unsigned
boundaries and seeded random values. Both complete output buffers and ordered
byte writes match an independent Python formatting oracle. Three restricted
interpreter tests pass. This assumes ordinary nonconcurrent parameter RAM;
read ordering and hardware timing are not qualified. Formatter admission
still awaits the remaining helper/core comparisons.

Padding target verification: `compare_gx8002_putchw.py` passes 6,912
stock/patched-target comparisons with an independent padding oracle, exact
output-call ordering and return counts including modeled output failure.
The run also rebuilds and repeats the 3,096 integer cases. Two interpreter
tests pass. Ordinary parameter RAM and modeled putf calls are assumed;
core format parsing still needs target verification before source admission.

Core formatter initial target comparison: `compare_gx8002_format.py` now
executes stock and linked source parsing instructions with bounded format,
argument and stack memory, ABI-clobbering modeled helper calls, and an
independent expected-output corpus. All 341 cases pass, including signed
32-bit boundaries, octal/hexadecimal, widths, zero padding, mixed string/
integer output, escaped percent, trailing percent and unknown conversion.
Two interpreter tests pass. This repeats the helper comparisons but does
not yet cover all format edge cases, output failures, or the variadic entry
ABI; no formatter bytes have been admitted to firmware ownership.

Expanded formatter verification now passes 1,724 target executions across
431 format cases and four output-failure positions. Added alternate octal/
hex prefixes (including stock zero behavior), padded strings, integer l
modifiers, character narrowing including embedded NUL, mixed argument
sequences, and trailing flags. Failure models preserve attempted output
while reducing successful-character counts. Interpreter tests pass with
explicit failure coverage. Variadic wrapper ABI remains the next dependency;
malformed widths and undefined input cases are not qualified by this corpus.

Variadic wrapper target verification: `compare_gx8002_printf_abi.py`
rebuilds the C wrapper on macOS and passes 1,088 stock/source forwarding
cases covering 0–16 32-bit argument slots, seeded values and four return
values. It checks the null stream, format pointer, ordered arguments across
register/stack boundaries, preserved caller stack, return address, stack
pointer and callee-saved registers. Different spill sizes are equivalent
for these cases. Two rejection tests pass. This models the formatter call;
firmware integration and hardware qualification remain pending.

Logging integration review: upstream signed negation of INT_MIN needs
defined wraparound; the reproducible Tinyprintf target flags now explicitly
include -fwrapv. Rebuilt integer (3,096), padding (6,912), and formatter
(1,724) target comparisons pass with that flag. A preserved BSD-option
notice is in components/shared/gx8002/TINYPRINTF-NOTICE.txt for distribution.
The libc fputc port now has a reusable verifier requiring all ten linked
bytes to equal authenticated stock, with no unresolved symbols/relocations.
Its source console dependency was already integrated. Builder wiring for
these logging functions is still pending; firmware ownership is unchanged.

Logging integration completed and the complete package rebuild/artifact
verification pass on macOS. Six functions replace 812 retained bytes with
752 compiled bytes and 60 unreachable fill bytes. Codec totals: 2,468 C,
1,024 generated data, 80 metadata, 164 fill, 322,356 retained bytes. Codec
SHA-256 13bc7820f5b5091e61e94c707255e9c3b1e9dd524d86bb27a085930aa31985bb.
Package SHA-256 76165ccdff566c79840dc0e565558ba1e5d01ab713db0dc036f115cf8d5f36ea.
The BSD notice is alongside the package and copied by its Make target.
29 target-interpreter tests, six ownership tests and the host padding
equivalence test pass. The goal remains active: all retained components,
assets and hardware behavior must still be reconstructed/qualified.

UART dispatcher linkage: link_gx8002_uart_tick.py authenticates the SDK
packet/queue headers and stock image, recompiles the recovered C on macOS,
and links queue-get/CRC/printf dependencies at qualified source entries.
The 132-byte function fits its 136-byte envelope. Its C string produces
14 exact stock bytes at package 0x14709; byte alignment is explicit because
the stock string address is unaligned. No unresolved symbols/relocations
remain. The host dispatcher test passes; target queue/CRC/callback comparison
and registration/queue state recovery remain pending. No source admission.

UART dispatcher target comparison: compare_gx8002_uart_tick.py passes
240 stock/source executions against an independent call-sequence oracle.
Cases cover queue absence, flags 0/1/2/255, valid/invalid CRC, wrong-command
and wrong-port registrations, first/middle/last matches, duplicate matches
and callback return propagation. Stack/ABI restoration is checked; modeled
dependencies clobber caller registers. Two interpreter tests pass. Target
comparison is finite and models dependency calls; integration remains pending.

UART dispatcher integration completed. The macOS codec build and full
package build/artifact verification pass. Replaced 150 retained bytes with
132 C, 14 source-authored string and four fill bytes. Codec ownership is
2600 compiled C, 1038 generated data, 80 metadata, 168 fill, 322206 retained.
Codec SHA-256 0052754e69ceb4fd4f83d65410dff5a56cc4b1de33d9680b00e3e746821814c4;
package SHA-256 eb15ab10fa9408663c84fe4f40be86ae87ec0c8031fb2937bc0db93c58c9745c.
Three UART tests and six ownership tests pass. The experimental build remains
hybrid and unqualified on hardware. Application-event tick is the next
known source candidate whose UART dependency is now closed.

Application tick linkage: link_gx8002_app_tick.py authenticates pinned SDK
app/queue layout headers, rebuilds the event tick and watchdog service on
macOS and links both at original addresses. Tick uses its complete 80-byte
envelope; watchdog service matches all ten stock bytes. No unresolved
symbols or relocations remain. The UART function declaration now agrees
with its recovered int return type, explicitly discarded; the host test
mock returns -1 and all eight existing dispatch scenarios still pass.
Target callback/queue ordering comparison remains pending; no new admission.

Application-event target verification: compare_gx8002_app_tick.py passes
48 stock/source cases with a separate call-order oracle. Coverage includes
queued/absent events, absent application, null event/loop callbacks, and
event callbacks clearing or replacing the application before task-loop
dispatch. Both call UART then watchdog and return zero despite modeled
service return values. Stack initialization/restoration and callee-saved
registers are checked. Two interpreter tests and the eight-scenario host
test pass. Asynchronous mutation outside callbacks and hardware timing are
not qualified; event tick integration remains pending.

Event tick/watchdog integration completed: native macOS codec and full
EVENOTA build/artifact verification pass. Two functions replace 90 retained
bytes with C; codec totals are 2690 compiled C, 1038 generated data, 80
metadata, 168 fill and 322116 retained bytes. Codec SHA-256:
b7c58e950fefed78304e77aa920b2ee2f0c96cbaf37c48815ddbf3c84f1ab347.
Package SHA-256 ab8d4fde3019446cf4e966257980889ae2a6b2a9641d885c4d8bec2499261e3d.
Three event tests and six ownership tests pass. The goal remains active;
application initialization, retained state and other opaque functionality
remain to be reconstructed, and device operation is not qualified.

Initialization recovery: package 0x12260 initializes a 64-byte event queue
with 8-byte elements, calls optional AppInit, registers suspend/resume
records and configures watchdog timeouts 3000/2999. Recovered C compiles
to 116 bytes, matching the stock envelope, plus 30 bytes of string-section
content. Registration routines at 0x10c4c/0x10ca4, watchdog initialization
at 0xfcac and callback 0x12224 remain dependencies to recover. No source
admission or complete prototype/behavior qualification is claimed.

Power registration recovery: suspend/resume routines at 0x10c4c/0x10ca4
scan all eight callback slots, replace the first matching record, otherwise
append when count<8 and callback is non-null. Search precedes validation,
so null may match an empty slot without count increment. Recovered C and
a shared layout header preserve this behavior and correct initializer
prototypes to int returns. Host tests pass for both registries, full capacity,
duplicate replacement and null ordering. Native target sections are 104
bytes each, exceeding the 88-byte stock envelopes; placement and target
qualification remain pending. The eight-byte state header remains opaque.

Registration placement follow-up: -Os alone reduces each routine from
104 to 92 bytes. Combining -fno-tree-loop-optimize with
-fno-guess-branch-probability brings suspend to 88 bytes; resume remains 92.
link_gx8002_suspend_registration.py reproduces the native build and links
suspend at 0x102076c0, calling recovered memcpy at 0x10025738. It authenticates
stock, source/header hashes, rejects overflow and unresolved relocations,
and excludes the oversized resume section. Target mutation comparison
remains pending, so no new firmware ownership is claimed.

Resume placement resolved: adding -fno-gcse to the size/loop/branch flags
makes both unchanged registration functions 88 bytes. The native linker
script now includes suspend at 0x102076c0 and resume at 0x10207718, each
within its original envelope, with resolved memcpy/state references. The
linked hashes and compiler flags are recorded in the registration candidate
report. Host registration tests still pass. Target mutation comparison
remains pending; no registration bytes are yet admitted to firmware.

Power registry target comparison: compare_gx8002_power_registration.py
passes 720 decoded stock/source cases against independent state/write
oracles for both registries. Counts 0–9, first through last duplicate
matches, null/non-null callbacks and private-data boundary values agree.
The check compares complete state bytes, copy calls, count stores and return
values, and verifies callee-saved registers. Two interpreter tests plus
the host registration test pass. Memcpy is modeled; overlapping inputs and
concurrent mutation are excluded. Firmware integration remains pending.

Power registration integration completed; native macOS codec and full
package build/artifact verification pass. Added 176 C bytes; totals now
2866 compiled C, 1038 generated data, 80 metadata, 168 fill, 321940 retained.
Codec SHA-256 4ee8376b425aac46a64f0068d391964c0af93829432c76eaecb6966795f32dc8;
package SHA-256 a27e358b3629ade4d330abb7238789e6fe1f4c146d696515e296aea02802a38d.
Three registry and six ownership tests pass. Watchdog callback at 0x12224
was confirmed to call reboot at 0xfd44; that dependency and watchdog init
remain for startup recovery. Goal remains active and hardware unqualified.

Reboot recovery: C reproduces all 36 linked stock bytes at package 0xfd44,
including platform gate(24,1), five ordered MMIO stores and infinite reset
wait. The callback compiles to six bytes versus eight stock bytes because
the compiler recognizes reboot does not return. Gate runtime 0x10025080
remains a dependency; no source admission or hardware reset was performed.
Watchdog init inspection shows reset-timeout input is unused and level
timeout below 1000 is logged/rejected; further initialization recovery remains.

Watchdog initialization/interrupt recovered as C candidates. Initializer
rejects level_ms<1000, ignores reset_ms, selects a timeout exponent using
the stock signed-division/unsigned-comparison behavior, configures watchdog
registers, stores the handler, registers IRQ 11 and enables bit zero. ISR
calls the optional int-returning handler and always reads base+0x14 after
a returning callback. SDK irq_handler_t establishes int return type; the
unadmitted app-init/reboot callback declarations were corrected, superseding
the earlier candidate hashes. Native sections are 140/36 bytes versus
128/28 stock: size and target qualification remain pending. The platform
gate maps to SRAM package 0x17094 and is a larger table-driven clock routine.
No new source admission or hardware action occurred.

Watchdog arithmetic refinement replaces the explicit 64-bit sign conversion
with defined 32-bit complement arithmetic, eliminating __divdi3. The actual
selector statements pass a native host comparison for all 64,536 accepted
16-bit level timeouts. -fno-shrink-wrap brings the interrupt to its 28-byte
stock size; initializer is 132 versus 128 bytes. Updated source/flags/code
hashes are recorded. MMIO/IRQ target qualification and clock-gate recovery
remain pending; no new source admission.

Watchdog placement resolved using the uint16_t input bound: seconds<=65,
so the selection loop stops by exponent 10 before sign-bit arithmetic.
Unsigned division therefore preserves every accepted input; all 64,536
selector comparisons pass. Initializer now fits 128 bytes and ISR fits
28; linked ISR and 22-byte source diagnostic string match stock exactly.
link_gx8002_watchdog_initialize.py reproduces compilation/linking and records
source/code hashes. Clock gate and IRQ registration remain retained
dependencies; full target MMIO comparison and source admission are pending.

IRQ registration and VIC recovery: runtime_gx8002_irq.c now supplies the
handler/private registration path and wraps authenticated upstream CSI enable
and disable routines from SDK commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
Native macOS compilation/linking places 24/28/36 bytes in the original
28/28/36-byte envelopes. link_gx8002_irq.py records source, upstream dependency,
compiled section, and authenticated stock hashes. compare_gx8002_irq.py passes
1,560 stock/candidate ordered-write cases, including all seven-bit VIC indices,
high-bit IRQ inputs, registration limits, and null handlers; four interpreter
regression tests pass. Registration's enable call is modeled, with the actual
VIC routine independently compared. IRQ table storage and generic dispatcher
remain retained; no source admission or hardware qualification is claimed.
The complete source-only firmware goal remains active and macOS remains the
build target. The experimental package still contains retained stock content.

Continued IRQ recovery with pinned upstream csi_irq_save/csi_irq_restore.
Native macOS wrappers emit 10 and 6 bytes, respectively, exactly matching the
stock instruction bodies at package offsets 0x17574 and 0x17580. Each stock
12/8-byte envelope ends with two zero alignment bytes after RTS; the linker
verifier checks body length, exact bytes, final RTS, and that padding separately.
The updated five-function placement report and 1,560-case IRQ comparison pass,
as do four interpreter regression tests. These remain candidates pending source
admission; the generic dispatcher, table storage, and other firmware opacity
remain unresolved. No complete source-only or hardware-running claim is made.

Recovered IRQ bank restore and save/disable in runtime_gx8002_irq.c. The
restore routine compiles to 24 bytes identical to stock; save/disable fits its
40-byte envelope. Both use the authenticated upstream VIC register definition.
Stock saves ISER[0] and ISER[1] at 0x20026eec, then disables only IRQs 0..31;
the source preserves that asymmetry and the order of reads, writes, and calls.
Expanded decoded execution comparison passes 1,610 cases, including 50 bank
state cases with independent ordered-access oracles. Four interpreter tests
still pass. The disable callee is modeled in this comparison and separately
compared against stock. Seven IRQ functions now have linked source candidates;
source admission, state ownership, generic dispatcher recovery, and hardware
qualification remain pending. Full source-only goal remains active.

Integrated all seven qualified IRQ routines through verify_gx8002_irq.py and a
reviewed admission baseline. The native codec builder recompiles, repeats the
1,610 comparisons and exact PSR checks, then admits only matching linked
sections. Ten integration/interpreter tests pass. Codec now has 61 source-built
functions across 77 code occurrences plus two generated data regions: 3,034 C
bytes, 1,038 source-data bytes, 80 metadata bytes, 176 unreachable fill bytes,
and 321,764 retained bytes. Codec SHA-256 is
b1f8b2861b1660c5449f9ff73f90d90bb0b50b6b5d38f8ef75d772e910ee3ffb.
The full macOS experimental package rebuild and artifact verification pass;
package SHA-256 is
733c8558471b81e35d57e5fde39de1c88648cc81aa2c86c6f252e86cefc9bc28.
The default firmware remains separate. IRQ globals/dispatcher, watchdog gate,
and other retained code/data still prevent source-only completion. Goal active;
no flashing or hardware qualification performed.

Clock-gate recovery identifies pinned GRUS clk_priv.h implementations
_clk_set_high_gate and _clk_set_all_gate as matching the stock control flow,
including parent-module remapping, source-select checks, and additional gate
bits. Added a source adapter and reproducible authenticated native compiler
script. Upstream module enum matches stock (WDT=24); candidate includes the
module-info helper and source-defined parameter/divider/DTO tables. Current
-Os compilation emits gate code 288 bytes versus a 256-byte stock envelope,
lookup helper 176 bytes, jump table 76, parameter table 416, DTO table 3,
and divider table 68. No source admission: placement, table relocation,
stock-data equivalence and target MMIO behavior still need qualification.
Full source-only goal remains active; latest integrated package is unchanged.

Authenticated upstream clock tables now verify byte-for-byte after native
C-SKY linking: parameter table 416 bytes at package 0x186f4/runtime 0x200266e0,
DTO table 3 at 0x18894/0x20026880, divider table 68 at 0x18898/0x20026884.
verify_gx8002_clock_tables.py reproduces source compilation and resolves every
parameter-table pointer to those source-defined tables; all 487 bytes match.
The single alignment byte between DTO and divider tables is excluded. Analysis
code is linked outside firmware, so no executable placement or admission is
implied. Six compiler-option probes do not fit the gate routine (best 288 vs
256 bytes); disabling tree-loop optimization reduces the lookup helper from
176 to 156 bytes. Table source ownership is now evidenced; code behavior,
placement and integration remain pending. Full source-only goal stays active.

Clock placement investigation: switch and branch-layout probes reduce gate
code to 278 bytes, still above its 256-byte envelope. Native module lookup
with -fno-tree-loop-optimize initially fit in 156 bytes, but disassembly showed
interprocedural specialization removed stock's NULL-output check because the
only visible caller supplied a stack object. Added an externally callable C
lookup wrapper to retain the full input contract; the helper now retains the
check and fits in 160 bytes at runtime 0x10024a44 (stock 164-byte envelope).
The updated table verifier links this helper at its original entry, with all
three source tables at original addresses; their 487 bytes still match stock.
Gate and public analysis wrapper remain outside firmware entries. Helper
behavior comparison and admission remain pending; source-only goal active.

Clock lookup target comparison now passes 42,160 cases. The restricted decoded
executor compares stock and source-linked __module_get_info against independent
return-value, six-word output, and ordered-write oracles. Cases include original,
identity, reversed, missing, and duplicate module tables; direct-index precedence,
first fallback match at every slot; null output; valid, out-of-range, and high-bit
module IDs. Four executor negative tests reject null writes, table writes,
unknown instructions, and callee-saved corruption. Ordinary RAM reads may differ
because of optimization; concurrent mutation and overlapping output are excluded.
All source tables remain byte-exact; no hardware/timing or whole-firmware claim.
Lookup/table admission and gate placement remain next work; goal stays active.

Integrated authenticated upstream clock lookup and three source-defined tables
through verify_gx8002_clock_source.py. Admission repeats 42,160 target cases,
checks source/table hashes and resolved sections, and excludes both analysis
wrapper and unqualified gate. Ten integration/interpreter tests pass. Rebuilt
codec owns 3,194 compiled C bytes, 1,525 generated source-data bytes, 80 metadata,
180 unreachable fill, and 321,113 retained bytes. There are 62 source functions,
78 code occurrences and five data regions. Codec SHA-256:
409f4c969833b506c9711aa7215ed340a3227f7caabeda9a621990644f4f3084.
Complete macOS experimental package rebuild and artifact verification pass with
7,822 placed flash regions and zero unresolved regions. Package SHA-256:
797dc5975f893d755d849b35a5d60f0f3f82aa55c7bdc9e6f00126d19f9d284c.
Retained clock gate and other code/data remain; no hardware qualification or
source-only completion is claimed. Goal stays active; default firmware separate.

Clock gate placement resolved without editing pinned upstream clock logic.
-Os --param=case-values-threshold=3 -fno-gcse -fno-tree-forwprop emits 254 bytes
in the 256-byte stock envelope; its 148-byte generated switch-table section
fits at runtime 0x100253cc. link_gx8002_platform_gate.py authenticates upstream
inputs, compiles natively, globalizes only the source helper symbol, discards
this compilation's helper and analysis wrapper, and links both calls to the
independently qualified __module_get_info entry 0x10024a44. Disassembly confirms
both call targets. Original source tables resolve at their verified addresses.
The linked code and switch tables have recorded hashes and no relocations.
MMIO behavior and generated switch targets remain to be compared before
admission; current integrated package is unchanged and goal remains active.

Clock gate target comparison passes 8,432 cases against both stock and linked
upstream code with an independent module/clock-source register oracle. The
executor follows each binary's generated jump tables, models the separately
qualified lookup with original parameter data, and checks ordered lookup,
MMIO read, and MMIO write traces. Coverage includes all 26 modules plus invalid
and high-bit IDs, four enable values, and 68 source-register patterns (single
bits, inverse single bits, zero, all bits, and alternating patterns). Four
negative interpreter tests reject invalid jump targets, unintended writes,
wrong helper targets, and unknown instructions. The verifier regenerates its
authenticated stock wrapper rather than relying on prior build output.
Gate code/table admission remains pending; no hardware/timing qualification or
source-only completion is claimed. Full goal stays active.

Integrated qualified upstream platform gate and its compiler-generated switch
targets via reviewed admission baseline. Native codec build reruns all source
qualifications including 8,432 gate cases; ten integration/interpreter tests
pass. Added 254 C bytes, 148 generated target-table bytes, and two unreachable
fill bytes, replacing 404 retained bytes. Codec now has 63 source functions,
79 code occurrences and six data regions: 3,448 compiled C, 1,673 source data,
80 metadata, 182 fill, and 320,709 retained bytes. Codec SHA-256:
7177739ac1adb18bed3960e7ab9a10b0473cf3291e0f7163d6de37f305bf995b.
Complete macOS package rebuild and artifact verification pass, with 7,822
placed regions and zero unresolved flash regions. Package SHA-256:
a11cfbe45372624f3acd26a4f55c609f2403d4ac6f2fa02bf9bdcd811423de72.
Watchdog gate and IRQ registration dependencies now resolve to source-built
entries in this experimental codec. Watchdog initialization MMIO/callback
qualification and other retained functionality remain; goal active, no hardware
qualification, no source-only completion claim. Default firmware remains separate.

Watchdog ISR qualification passes 288 decoded stock/source cases with an
independent callback/read-order oracle. The 28-byte source ISR remains exactly
identical to stock. Tests cover null/present handler, IRQ/private argument
forwarding, callback return values including high-bit/negative representations,
and varying clear-register results. Callback clobbers caller-saved registers;
return value survives the volatile clear read at 0xa0700014. Four negative
interpreter tests pass. Returning callbacks are modeled; a nonreturning reboot
callback never reaches the clear read. Full initializer MMIO qualification and
ISR/initializer admission remain pending. Goal active; package unchanged.

Watchdog initializer target qualification passes 65,728 stock/source comparisons:
all 65,536 uint16_t level timeout values plus 192 reset/callback/private/control
variations. The independent oracle verifies invalid-timeout diagnostics, selected
timeout setting, ordered clock-gate call, timeout/reload writes, handler storage,
IRQ 11 registration, and final control-register read/enable write. External gate,
IRQ and printf calls are modeled with caller-saved register clobbering; those
callees have separate source qualification. Four negative interpreter tests
reject unknown calls, invalid reads/writes and out-of-range shifts. ISR evidence
is rerun (288 cases). No asynchronous IRQ timing or hardware qualification.
Initializer/ISR/string admission remains pending; full source-only goal active.

Integrated watchdog initializer, ISR, and C diagnostic via reviewed admission
baseline. Codec rebuild repeats 65,728 initializer and 288 ISR cases; 14
integration/interpreter tests pass. Added 156 compiled C bytes and 22 source
string bytes, replacing 178 retained bytes with no new fill. Codec has 65
source functions, 81 code occurrences, seven data regions: 3,604 C bytes,
1,695 generated source-data bytes, 80 metadata, 182 fill, 320,531 retained.
Codec SHA-256:
65df2f4e69d77f81ca3afe03bd681cf2dd8d9a580ab2913cb45d2ee4a52063b6.
Full macOS experimental package rebuild and artifact verification pass with
7,822 placed flash regions and zero unresolved regions. Package SHA-256:
572a6ec96b249ce0bdfee5d6e2897fbd4ae05243a1a2d707205b58d61f17a584.
Clock gate, lookup, IRQ registration, printf and watchdog setup now resolve to
source entries in the experimental codec. State ownership, application startup,
reboot and other retained functionality still need work. Goal active; no
hardware qualification, flashing, or complete source-only claim.

Reboot recovery now has reproducible native compilation/linking. Added explicit
noreturn on the reboot function so its int-returning watchdog callback compiles
under -Werror without fabricating a return. The 36-byte reboot remains exactly
stock; callback emits six bytes in its eight-byte envelope. Both direct reboot
and watchdog-callback paths pass decoded ordered traces through gate(24,1),
reset selection, watchdog disable/timeout/reload/enable writes, and the stock
terminal self-loop. The verifier follows the real callback-to-reboot branch;
only the separately qualified gate call is modeled. No hardware reset is run.
Source admission and application-initializer qualification remain pending;
full source-only goal stays active and integrated package remains unchanged.

Application initialization now has a reproducible native linker with authenticated
SDK application/queue type headers and hashed local registration layout. The
current C compiles and links to exactly the stock 116-byte function at runtime
0x10208cd4. Explicit source-defined registration-name arrays produce all 15 and
14 bytes (including terminators) exactly at 0x1020b3ee and 0x1020b3fd. The tool
requires byte identity for code and both strings, fixed placements, and no
unresolved symbols or relocations. Queue initialization, power registration,
watchdog setup, and reboot callback entries are resolved. Callback/call-order
qualification and startup/reboot admission remain pending; state remains retained.
Full source-only goal active; no hardware action or package update this tranche.

Application startup target comparison passes 72 cases covering absent app,
absent AppInit, returning AppInit with varied results and app-state clearing,
and successful/failed suspend/resume registration. Both stock and source code
match independent queue/callback/registration/watchdog order and stack-record
oracles; return remains zero despite modeled registration failures, as stock.
Four negative interpreter tests reject bad record pointers, unmapped reads,
out-of-frame writes and unexpected callbacks. Underlying services are modeled
and separately qualified; no concurrency, hardware startup or timing claim.
Startup/reboot admission remains pending; source-only goal stays active.

Integrated application initialization, its two source registration strings,
reboot and watchdog reboot callback through reviewed admission adapters. Fixed
a report tuple/list serialization mismatch caught by baseline equality without
changing compiled code or the reviewed baseline; a JSON round-trip regression
test now covers it. Thirteen integration/interpreter tests passed, followed by
four reboot tests including that added regression. Native codec build passes
all qualifications. Added 158 C bytes, 29 source-data bytes and two fill bytes;
68 functions across 84 code occurrences plus nine data regions now account for
3,762 C bytes, 1,724 source data, 80 metadata, 184 fill, and 320,342 retained.
Codec SHA-256:
62738253718d15fa01c951da9a3426fb2310efac1b4b9c3cb481401581199f07.
Complete macOS package rebuild and artifact verification pass with 7,822 placed
regions and zero unresolved flash regions. Package SHA-256:
c9c2908fef58be1badff0b5942ae5257677a7e441bc83a428415895c45f07a30.
Remaining runtime/state/data opacity still prevents source-only completion;
no hardware startup/reset qualification or flashing. Full goal remains active.

IRQ dispatcher recovery identifies the stock entry at 0x17588/runtime
0x10025574: nested interrupt entry, extended GPR and floating-point saves,
VIC ISR low-nine-bit vector minus 32, handler/private dispatch, and mirrored
restore/interrupt return. Added C dispatcher using authenticated CSI active-IRQ
access and compiler interrupt attribute with -mistack. Native compilation emits
60 bytes versus stock 80, but disassembly exposes omitted r18-r31 and fr0-fr7
preservation. This is an unadmitted candidate, not a size win or completion.
The reproducible compiler report records this context-preservation blocker for
that routine; architectural wrapper or compiler correction is required next.
Meaningful recovery continues; full goal active and package unchanged.

IRQ context recovery: local GCC prologue implementation only emits nie/ipush;
normal ABI frame logic does not preserve all callback-clobbered extended state.
Added source assembly entry wrapper with stock-order r18-r31 and fr0-fr7 saves
and restores around an ordinary C dispatcher. The dispatcher remains SDK-based
C; no instruction-byte arrays are used. Reproducible native build authenticates
SDK dependencies and links the 44-byte wrapper plus 44-byte C body at a temporary
analysis address with no unresolved references. Combined 88 bytes exceed the
stock 80-byte slot; placement and interrupt-state execution qualification remain
pending. Neither plain interrupt-attribute candidate nor wrapper is admitted.
Meaningful recovery continues; full source-only goal active, package unchanged.

IRQ wrapper placement resolved: grouping lr with r18-r31 in a source-assembled
r15-r31 block preserves the stock register set plus r16/r17 and removes the
separate lr save/restore instructions. Native wrapper is now 36 bytes and C
body 44, fitting exactly the original 80-byte interval at runtime 0x10025574.
Build authenticates stock, checks placement/size and unresolved references, and
records hashes. Software stack frame is 100 bytes versus stock 92, with four
additional bytes inside the C callback path; this must be considered in nested
interrupt qualification. Register restoration and dispatch behavior remain
unverified, so the candidate is not admitted. Full source-only goal active.

IRQ software-frame verification passes 24 seed/recursion configurations of the
linked wrapper: distinct extended GPR/FPU bit patterns survive modeled body
clobbers, all saved words are restored, and SP returns to its original value.
Three negative tests reject entry-order violations, unbalanced frames and
restores without saves. This checks software saves only: hardware interrupt
instructions are treated as ordered boundaries; recursive calls use independent
stacks and are explicitly not a nested-IRQ simulation. C dispatch, real callback
ABI, stack capacity and hardware interrupt behavior remain to be qualified.
No admission or package update; complete source-only goal remains active.

C IRQ dispatch body passes 768 decoded stock/source cases across all 32 valid
external vectors, four high status-bit patterns, null/present handlers, and
three private-pointer values. Independent read/callback oracles confirm low
nine-bit vector masking, subtraction of 32, correct slot selection, null-handler
skip and exact IRQ/private forwarding. Three negative tests reject invalid
vectors outside the qualified domain, unknown reads and unknown handler calls.
Stock body is compared separately from its interrupt frame. Hardware IRQ state,
actual nesting and extra software stack usage remain unqualified; no admission
or package update. Complete source-only goal remains active.

Replaced the weak independent-stack recursive IRQ check with shared software
stack memory. Nested modeled entries now allocate below the outer C callback's
saved link register, retain parent saved words, and require exact parent-memory
restoration. Callback return-address sentinels are checked. All 24 seed/depth
cases and three negative tests pass. Observed modeled software peaks are 104,
208, 312 and 416 bytes for one through four returning callback levels. These
exclude NIE/IPUSH hardware frames and are not a proof of real stack capacity
or actual nested interrupt execution. Hardware-state qualification remains
pending; candidate unadmitted and full source-only goal active.

Added `audit_gx8002_irq_sleigh.py` to authenticate the local Ghidra C-SKY
definitions against plugin commit `0daaa056e8c570ba514fc0d0226384ecf9f9df05`
and exercise their explicit stack operations with distinct register values.
The defined IPUSH/IPOP pair reverses all six registers on a round trip;
NIE/NIR's explicit EPC/EPSR stack operations are inverse. This is a decompiler
model inconsistency, not evidence of hardware behavior. The machine-readable
audit records source hashes and rejects changed stack macros. Do not use this
plugin's interrupt semantics to qualify the firmware IRQ replacement. No
candidate admission or package changes; hardware semantics remain under review.


Visually checked the manual's IPOP, NIE and NIR pages and extended the decoded
IRQ frame model with the documented 32 bytes of instruction-managed saves.
The new architecture verifier authenticates the manual and passes 24 distinct
seed/depth cases with shared stack memory; peaks are 136/272/408/544 bytes for
one through four callback levels. Three new tests check the exact initial
frame layout and reject saved R0/EPC corruption. Existing software-only checks
also pass. The model covers stack transfers and saved values, not PSR timing,
arbitrary interrupt injection, callback stack bounds or physical capacity.
Candidate remains unadmitted; no binary-removal totals or package pins changed.
Full macOS source-only goal remains active.


Traced image-A vectors to reset at runtime 0x10023500 (package 0x15514).
The reset instruction stream loads SP=0x2002f7fc before system_init/main.
Its BSS clear uses [0x20026d80,0x2002ecec), leaving a numeric 0xb10 gap to
initial SP; this is not proof of reserved stack capacity or runtime headroom.
Recorded authenticated image offsets/hashes in startup-stack-evidence.json.
An alternate C dispatcher returning handler status still compiled with a saved
LR and did not reduce the IRQ frame, so the IRQ candidate remains unchanged.

Reconstructed the adjacent word-wise clear_bss in C, cross-referenced against
pinned SDK start.S. Native macOS candidate builds to 28 bytes inside the stock
36-byte envelope, with no unresolved symbols/relocations. Linked bounds clear
32620 bytes. Target trace comparison and source admission remain outstanding;
no package pins changed. Full source-only objective remains active.


Completed decoded target comparison for the C BSS clear. Stock and candidate
both produce exactly 8155 ordered zero-word writes over the shipped range and
preserve r4-r31 (including SP/LR), across six initial register seeds. Four
focused tests reject end-boundary/unaligned writes and preserved-register
corruption, and check store postincrement. Added the source admission adapter
and explicit verification baseline. Candidate-provider registration and full
package rebuilding remain outstanding; no package pins changed this turn.
Full source-only objective remains active.


Integrated the qualified BSS clear into the codec provider and added its four
tests to the candidate target. All 88 candidate tests pass. Native macOS full
experimental package build and artifact verification pass after deliberate
codec/package hash refresh. Codec now contains 69 source-built functions at
85 code occurrences plus nine source-data replacements: 3790 compiled C,
1724 source data, 80 metadata, 192 unreachable fill and 320306 retained bytes.
Codec SHA-256: cd04489d72527fb94febad4cc7aff84877bb58557d0bcebe29ad53c44e3cf7bf.
Package SHA-256: bec346eecd7a76606a0b68ce7b77ac5638a1e48838f78b6b943d4ffc417c9cf9.
No hardware flashing/qualification. Remaining retained functionality and data
still prevent source-only completion; full goal remains active.


Recovered the next startup system_init sequence at package 0x15560, runtime
0x1002354c, against pinned SDK arch/soc/grus/system.c. Source now uses CSI MPU
and VIC helpers plus explicit external declarations, avoiding the SDK's
conflicting global int32_t/uint32_t typedef headers. Native macOS build
resolves all calls and vector references with authenticated dependency hashes.
Both O2 and Os candidates occupy 168 bytes versus the 164-byte stock envelope;
the recorded Os candidate is not admitted. Control-register/MMIO/call trace
qualification and placement remain outstanding. Clock initialization, PMU
start-mode, board initialization and vectors remain retained dependencies.
No package pins or retained-byte totals changed. Full goal remains active.


System initialization now fits its 164-byte envelope using O2 with
-fno-expensive-optimizations; the C source is unchanged. Eight bounded native
compiler probes identified this setting. Added decoded MPU-prefix comparison:
1296 combinations of initial CR18/19/20/21 values match stock and independent
mask/write-order expectations. This covers reserved-bit preservation and MPU
read/write ordering only. Conditional BSS clearing, external calls, VIC writes
and exception-enable ordering still require full-routine comparison before
admission. No package pins or retained-byte totals changed; goal stays active.


Extended system_init target comparison through return. All 2048 full-routine
cases match stock and independent expected traces, with four start-mode values,
control-register patterns and two caller-clobber patterns. ROM mode alone calls
BSS clear; clock/start-mode/board calls, VBR, nine VIC writes and final EE/IE
enable ordering match. Four negative tests reject unknown calls/MMIO, missing
return frame and incorrect PSR enable. Existing 1296 MPU-prefix cases also pass.
External services are returning models, not hardware qualification. Admission
adapter and package integration remain outstanding; goal remains active.


Integrated system initialization through an explicit admission baseline and
provider registration. All 92 candidate tests pass. Full experimental package
build and artifact verification pass on macOS after deliberate pin refresh.
Codec now has 70 source-built functions at 86 code occurrences and nine source
data replacements; 3954 compiled C bytes, 1724 data, 80 metadata, 192 fill and
320142 retained bytes. Codec SHA:
a3142c50814529c5898d9b0615fde6c47096c90c3f533ca8e030a0959b9c385e.
Package SHA:
946bafb31abd22696f71b6db71d012f8869a7ff545394a684806338a654e4001.
External clock/start-mode/board/vector functionality remains retained. No
hardware qualification or flashing; full source-only goal stays active.


Recovered reset-reason (0x10024940) and startup-mode (0x10024984) queries in
C. Status bits are checked in priority order 0,2,3,1, yielding numeric reason
codes 2,3,5,4; the fallback reads bit zero of A001002c. Mode queries reasons
2..5 only, reads A0010058 bit zero and preserves the discarded A001005c read.
Native macOS linked candidates are 66/30 bytes in 68/32-byte envelopes, with
no unresolved references or relocations. Recorded source/code/envelope hashes.
Decoded read-order and return-value comparison remains required before
admission. No package or retained-byte totals changed; full goal active.


Qualified reset-reason and startup-mode decoded bodies against stock and an
independent fixed priority table across 1536 input combinations. Actual nested
BSR/return is executed in the model; exact MMIO read order, conditional fallback
and discarded read, return values and preserved registers match. Four tests
cover unknown reads/callees, missing return frames and unsigned reason
underflow. Admission and package integration remain outstanding. Hardware
register side effects and timing are not established. Full goal active.


Integrated both startup queries through explicit reviewed admission baselines.
All 96 candidate tests pass; full experimental package build and artifact
verification pass on macOS after intentional hash refresh. Codec now contains
72 source-built functions at 88 code occurrences and nine source-data regions:
4050 compiled C, 1724 data, 80 metadata, 196 fill and 320042 retained bytes.
Codec SHA: 6529e7d55d6ca56bb7dd5564d8ae96ed8adc5b0e707db112fb1d0dd427ce1a4f.
Package SHA: 6e67d32609605ce2f1924306fa41fcc25c7d5f1ac7ecf71255d88ddae6a49479.
Clock/board/vector recovery and hardware qualification remain incomplete.
No flashing performed; full source-only goal remains active.


Recovered board entry at runtime 0x10025cbc and its fixed register helper at
0x10203c74. Entry queries reset reason, conditionally calls retained 0x100245f0
for unsigned reason >=2, then performs the helper unconditionally. The helper
writes 0x59 to A0005040/44/48/4c in order. Source-authored helper compiles to
20 byte-identical bytes on macOS. Entry compiles to 22 bytes versus its 20-byte
envelope under O2 and Os, so remains unadmitted. Recorded both candidates,
source/envelope hashes and resolved addresses. Conditional resume recovery,
entry placement and decoded behavior qualification remain outstanding. No
package pins or retained totals changed; full goal active.


Board-entry size remains 22 bytes after seven additional valid compiler probes;
no-expensive-optimizations also leaves it unchanged. Captured authenticated
212-byte static inventory/disassembly for its conditional target 0x100245f0,
including direct-call runtime addresses and seven trailing literal words.
The board_resume name is provisional. This establishes the next recovery
work: reconstruct multiple calls, register writes and callback-pointer stores,
not merely wrap an assumed resume service. No new admission/package changes;
source-only goal remains active.


Identified conditional board target 0x100245f0 as SPI-NOR initialization via
pinned SDK spl_spinor.c JEDEC cases and the nine-argument quad-XIP setup.
Authenticated SDK blob and recorded differences: SDK includes 0x856014 in
alternate-quad handling, but shipped code does not; shipped code also reloads
device ID and invokes an additional routine for 0x204016. Its XIP arguments
are 235,8,1,24,4,0,1,4,4. Do not substitute upstream behavior blindly.
The reference file has a proprietary/confidential header, so source reuse
licensing is unresolved; use evidence-backed reconstructed implementation.
This corrects the provisional board_resume interpretation. No admission or
package changes; full source-only goal active.


Reconstructed complete observed SPI-NOR initialization body in C, including
seven ordered MMIO writes, discovery failure return, stock-specific ID cases,
second device-pointer/ID read, two callback stores and nine XIP arguments.
Native macOS candidate links to 208 bytes in the stock 212-byte envelope with
no unresolved relocations. Source deliberately uses address-named unresolved
services and layout-checked state prefixes; it does not claim recovered full
callee signatures. Fixed addresses bind existing dependencies, not binary
arrays. Decoded path/argument/state/MMIO comparison remains required before
admission. No package changes; full source-only goal remains active.


Added decoded flash-selection comparison covering 819 first/second-ID cases:
JEDEC boundary neighbors, high-bit/signed extremes and distributed values.
Both stock and C candidate match an independent dispatch oracle, preserve the
stock exclusion of 0x856014 from alternate-quad handling, and reload a changed
device pointer before the second ID check. Callees clobber caller-saved
registers in the model. Prefix-supplied r5=1 and full setup/failure/callback/XIP
behavior still require complete-routine verification. No admission/package
changes; source-only goal remains active.


Added decoded flash-setup comparison through discovery. Eighteen seed/output
cases match ordered service arguments and all seven MMIO writes. The first
service receives an initialized output word; modeled writes to it do not alter
subsequent setup behavior. Caller-saved clobbers are modeled. Earlier 819
selection cases still pass. Candidate saves r5 additionally: 36-byte total
software frame versus stock 32, requiring stack impact review. Failure/success
return, callback stores and all XIP arguments still need unified verification.
No source admission or package changes; full goal active.


Revalidated current flash work and checked five further frame/size options;
all still save r5 additionally. Added decoded success/failure-tail comparison.
Twelve cases match both callback stores, all nine XIP arguments (including
five stack arguments), returned interface/null values and frame restoration.
This reruns the 18 setup and 819 selection checks. Tail initialization still
supplies expected frame/r4 state, so unified full-routine execution remains
required. Extra stack capacity and physical flash behavior remain unqualified.
No admission/package changes; full source-only goal active.


Added unified decoded flash initialization execution with continuous registers
and stack from entry through return. All 396 combinations of discovery result,
first/reloaded IDs, caller-clobber seed and output-word mutation match stock
and independent ordered effects. No section-boundary r4/r5/frame injection is
used. Both callback stores, nine XIP arguments, null/interface returns and ABI
restoration match. Observed own frames are 32 stock versus 36 candidate bytes.
External service implementations and hardware timing are still modeled; extra
stack capacity/interrupt interaction remains unqualified. No admission or
package changes; full source-only goal remains active.


Reconstructed the device-specific flash configuration service at 0x100242ec
(package 0x16300), called for ID 0x204016. It reads one byte with command 0x15;
when bit 0x10 is clear, it sets that bit, invokes two control helpers, writes
one byte using command 0x11, then invokes the first control helper again.
Returns zero on both paths. Native macOS linked C is 66 bytes versus stock 68,
with the same eight-byte frame and no unresolved relocations. Command read
must initialize its output byte; failure semantics remain unresolved. Full
256-byte-value target comparison and transport/control helper recovery remain
outstanding. No admission/package changes; full source-only goal active.


Completed decoded device-specific configuration comparison for all 256 status
bytes across four caller-clobber seeds (1024 cases). Command arguments, bit-4
preservation/update, control-call ordering, zero return and eight-byte frame
match stock. Three negative tests reject uninitialized status use, unknown
calls and invalid return frames. Read transport is modeled as filling its byte;
failure semantics and physical transport/control behavior remain unresolved.
No admission/package changes; full source-only goal remains active.


Traced the status-byte transport: it polls RX-ready, stores each requested
byte, waits for RX count zero and controller idle, then returns zero. No
explicit failure return exists in this body; non-ready hardware can wait
indefinitely. Reconstructed read/write transports plus idle/RX-empty/TX-empty
helpers in C, preserving register order and polls. Native macOS object sizes
are 16/20/20/86/88 bytes versus stock 16/20/20/88/88 envelopes. Target linking,
readiness-schedule/MMIO/buffer validation and caller-buffer-domain checks remain
outstanding; no new source admission. Transport implementation now gives a
concrete basis for qualifying the device helper's output-byte precondition.
Full goal remains active; package unchanged.


Linked all five reconstructed SPI transport functions at original entries,
with authenticated source/stock hashes, bounded sections and zero unresolved
symbols/relocations. RX-empty and TX-empty helpers are byte-identical to stock.
Idle helper passes 68 decoded busy-to-idle/continued-wait cases, preserving
status read order and zero return; upper status bits do not affect busy tests.
Finite still-busy observations are not proof of hardware liveness. Composed
RX/TX waits and transport buffer/MMIO behavior remain to be qualified before
admission. Full source-only goal active; package unchanged.


Verified FIFO-empty helpers with their actual nested idle call and continuous
register/frame state. Fifty-eight RX/TX schedule cases match stock, including
FIFO delays, subsequent controller-busy delays, zero returns, ABI restoration
and continued waiting at either stage. No synthetic callee return was used.
Full command transport/buffer behavior and hardware readiness remain to be
qualified. No admission/package changes; full source-only goal active.


Added complete decoded command-read execution with actual idle/RX-empty nested
helpers, continuous stack/register state and an independent ordered MMIO/buffer
oracle. All 150 command/count/alignment/readiness cases pass for lengths
0,1,2,7,32, including zero-length count-register underflow to 0xffffffff, no
zero-length buffer writes, low-byte extraction and exact FIFO/idle read order.
Return zero, saved-register restoration and non-overlapping stack frames are
checked. Valid nonwrapping buffers only; arbitrary counts, stalled hardware
and complete TX transport still need qualification. No admission/package
changes; full source-only goal remains active.


Added complete command-write comparison using the shared decoded interpreter
and actual nested TX-empty/idle calls. All 165 command/count/alignment/delay
cases match stock MMIO order, byte-buffer reads, zero return and frame state,
including NULL with zero length. Existing 150 read cases still pass. Four
negative tests reject zero-length buffer access, wrong MMIO order and unknown
helpers. Representative valid nonwrapping domains only; hardware liveness and
broader count/address qualification remain incomplete. No admission/package
changes; full source-only goal active.


Expanded each decoded command transport comparison to every length 0..256,
with zero-length NULL-buffer cases: 7725 read and 7725 write scenarios pass.
The 256-byte payload pattern covers every byte value. Added a loop-invariant
review explaining exact N-access behavior for valid nonwrapping RAM buffers
and preserved zero-count setup/polling semantics. No arbitrary hardware count
limit or readiness guarantee is inferred. Larger runtime buffers, controller
limits and interrupt interactions remain outside the dynamic checks. No
admission/package changes; full source-only goal remains active.


Prepared SPI transport source admission adapter and explicit reviewed baseline.
It reruns read/write/idle/FIFO-empty comparisons and requires all four checks
to reference the identical rebuilt artifact. Five replacements pass the
existing payload/relocation/placement admission gate (230 compiled bytes in
232 stock bytes); intentionally altered evidence is rejected. The replay
counts are 7725/7725/68/58. Provider registration and full experimental package
rebuild remain outstanding. Hardware readiness/limits remain unqualified;
full source-only goal stays active.


Integrated five SPI transport/polling functions through reviewed admission.
All 100 candidate tests pass; full experimental package build and artifact
verification pass on macOS after explicit hash refresh. Codec contains 77
source functions at 93 code occurrences and nine data regions: 4280 compiled
C bytes, 1724 data, 80 metadata, 198 fill, 319810 retained stock bytes.
Codec SHA: 9661dd49dc8aa77aae7cdcb6a94ad5c35e45d279f690b7869208d7c3651dc4e8.
Package SHA: eaa8d713d3f6a28a32997b2ea633288a2c3ce968d0ed6ee88f18db9059c1e5d9.
Physical SPI behavior remains unqualified. Higher flash/board routines remain
unadmitted; other opaque components still require recovery. Full goal active.


Integrated four recovered flash status/control helpers and the device-specific
JEDEC 0x204016 configuration body. Their command transport and ready/write-enable
dependencies now refer to qualified source-built functions; no new opaque
service boundary was introduced. Decoded comparisons pass 3075 status/control
and 1024 configuration cases. All 107 integration tests pass. Full experimental
package assembly and artifact verification pass on this macOS computer.

Codec now contains 82 source-built functions at 98 code occurrences plus nine
data regions: 4428 compiled C bytes, 1724 source data, 80 metadata, 202 unreachable
fill, and 319658 retained stock bytes (152 fewer than the preceding build).
Codec SHA: d438fe49d936e954218952f85bfd9ed74e36361d773f670a581bdef5b6709c4d.
Package SHA: d9999682daebcb420a098361e4c5f719b2d40f2867907b6e224327346841bfba.

Next flash candidates: generic quad-enable at package 0x162c8 uses status-2
bit 1 and command 0x31; alternate at 0x16344 reads both status bytes and uses
command 0x01 with two payload bytes. Main flash initialization, discovery,
XIP configuration, board entry and other components remain unfinished.
Polling is intentionally unbounded; physical hardware remains unqualified.
The full source-only goal remains active.

Recovered generic and paired flash quad-enable paths in
runtime_gx8002_flash_quad.c. Native macOS C-SKY compilation produces 54/60
bytes inside original 56/60-byte envelopes. Both use named reconstructed
status, ready, write-enable and command-write C dependencies. Exhaustive
status coverage (all 256 single-byte states and all 65536 paired states,
two caller-clobber seeds) passes 131584 decoded stock/source comparisons.
Three interpreter rejection tests pass. Prepared the admission adapter and
reviewed gx8002-flash-quad-verification.json baseline; provider registration
and experimental package integration remain next. The currently pinned
package remains the preceding 82-function build. Goal active.


Integrated the two quad-enable C routines. All 110 tests pass; full macOS
experimental package build and artifact verification pass. Codec now has
84 source functions / 100 code occurrences, nine source-data regions;
4542 C bytes, 1724 data, 80 metadata, 204 fill, 319542 retained bytes.
Codec SHA: fcc7a0f8c0c9fa668f2dc5dd5792f92fe552dfd86b576a129366fbe51a56c71c.
Package SHA: 193d1ea5a13dedade2f366a5a65dfba1fca0ded19be47652186aed1aeb691575.

Recovered the nine-argument XIP setup at package 0x16380 into
runtime_gx8002_flash_xip.c. Native compilation fits 204/208 bytes with no
relocations. Invalid settings disable SPI before returning -1. The sixth
argument is unused; line widths are shifted right once before validation.
Candidate is not admitted: decoded arguments/MMIO/ABI verification is next.
No physical hardware qualification; full source-only goal remains active.


Qualified XIP setup by executing full original and compiled instructions for
28328 nine-argument scenarios: 3602 accepted, 24726 rejected. Checks cover
ordered register writes, early SPI disable on rejection, unused sixth argument,
word-aligned address lengths, raw shifted line widths, mode bit selection,
unsigned bit boundaries, and preserved registers. Four negative/oracle tests
pass. Prepared verify_gx8002_flash_xip.py and its reviewed baseline. C remains
204 bytes within 208 stock bytes, with no opaque service calls. Integration
into the package is next; physical XIP hardware remains unqualified. Goal active.


Integrated XIP configuration C. All 114 tests pass; full macOS package
build and artifact verification pass. Codec now has 85 source functions at
101 code occurrences plus nine data regions: 4746 C bytes, 1724 data,
80 metadata, 208 fill, 319334 retained bytes.
Codec SHA: 9c9f99709940cac0182d91dd95cb544ed03ba5544d6c2cf8139d26c032bc8843.
Package SHA: 1c41812f899c224819b243402b34fa16fe8153dd68f1dd1e8b0639542abaa26b.

Recovered the ten-operation platform register dispatcher at package 0x17d88
into runtime_gx8002_platform_config.c. Operation 9 consumes (does not produce)
a word twice and writes bit zero to A000003C and 20027314. Initializers
previously modeled this as a potentially written output; that model needs
correction when qualifying composition. Candidate is 236 bytes without a
jump table versus 212 stock bytes. Default switch is 224 bytes + 40-byte
source-generated table. Os no-expensive and no-forwprop also 224; O2
no-expensive 240. Placement and decoded behavior qualification remain.
No physical hardware qualification; full source-only goal active.


Platform dispatcher now fits: source uses a counted eight-halfword transfer
loop and a compiler-generated jump table at the original 0x100249a4 address.
Native C-SKY output is 196 bytes / 212 code bytes and 40 / 40 table bytes;
no relocations or opaque service calls. The table is rebuilt from the C switch,
not copied from firmware. Complete decoded dispatch executes the generated
table and passes 11520 cases covering all operations, invalid unsigned
selectors, all byte values at each record offset and independent operation-9
second-read values. Four rejection/oracle tests pass. Register/memory effect
order and preserved registers match. Admission baseline and provider integration
remain outstanding; operation-7 independent packed-byte combinations are a useful
next qualification extension. Existing pinned 85-function package unchanged.
Physical hardware unqualified; source-only goal remains active.


Integrated platform dispatcher C and compiler-generated switch table after
77056 decoded comparisons (including every packed-byte pair). All 118 tests
pass; full macOS package build and artifact verification pass. Codec now has
86 source functions / 102 code occurrences and ten data regions: 4942 C bytes,
1764 data, 80 metadata, 224 fill, 319082 retained stock bytes.
Codec SHA: 202f40c2f2a356550c3f0b55893b3ca596c69957b18e3b38a81289c18023b003.
Package SHA: fb285faae8d2a891f5d6440ddbaf6e462fc886c90bc9b8cbbe58f7c3d452e133.

Updated flash initializer to named reconstructed service calls. Its full
comparison now models operation 9 as input-consuming and includes the two
register/global writes; 198 corrected cases pass. Earlier isolated setup
output-mutation evidence is superseded and must not support admission.
Initializer remains unadmitted: discovery, callbacks, state/interface ownership
and extra four-byte frame require work. Full source-only goal remains active.


Recovered flash discovery at package 0x161a4 into runtime_gx8002_flash_discover.c.
Native macOS C-SKY output fits 160/180 bytes with no relocations, same 16-byte
frame as stock. Requests JEDEC command 0x9f/three bytes, matches 24-byte table
entries, stores index/size/address-width/device pointer. Unknown IDs scan for
fallback 0xc22016 and return -2 even if it is found; negative read return gives
-1. Shipped six-entry table lacks fallback. Table inventory records names,
identifiers, offsets, values and authenticated hashes; other record fields and
pointer targets remain retained and unadmitted. Source candidate still needs
full decoded comparison before admission. Existing 86-function experimental
package is unchanged; full source-only goal remains active.


Flash discovery passes 26600 full decoded comparisons with ordered table/state
reads and writes, actual byte/halfword JEDEC assembly, real 16-byte frames,
and callee-clobber patterns. Cases include shipped/empty/fallback-only tables,
fallback inserted at every position, byte patterns, and signed transport
return boundaries. Four rejection/oracle tests pass. Fallback selection still
returns -2 even after state is populated. Negative transport cases verify the
defensive branch; recovered polling transport itself returns zero on completion.
Prepared verify_gx8002_flash_discover.py and reviewed baseline. Provider/package
integration is next. Retained table/state dependencies are explicitly declared;
physical hardware remains unqualified. Full source-only goal stays active.


Integrated flash discovery after reviewed 26600-case comparison. All 122
tests pass; macOS full package build and artifact verification pass. Codec
now has 87 source functions / 103 code occurrences plus ten data regions:
5102 C bytes, 1764 data, 80 metadata, 244 fill, 318902 retained stock bytes.
Codec SHA: 33a79d3e19d0b248e089b74eaee041f15e5a6a6272c71707239a99b8cc230b25.
Package SHA: c18f3d3b0aaa66455b494208fa1efedc026c96ee0b5eafcdff835ba2a8503da6.

Authenticated pinned SDK include/driver/gx_flash.h against its git blob and
identified the 30-slot GX_FLASH_DEV interface with CONFIG_MTD_TESTS disabled.
The shipped 120-byte table contains 23 non-null pointers; gettype and OTP-lock
anchors agree. Inventory names remaining read/program/erase, protection, OTP
and UID callbacks with upstream declarations and addresses. It does not admit
the table or callbacks; each still needs qualification. Source-only goal active.


Recovered the two callbacks installed by flash initialization:
word-program at package 0x1579c/runtime 0x10023788 and word-read at
0x15cc0/runtime 0x10023cac, in runtime_gx8002_flash_word_io.c.
Native macOS C-SKY -Os -fno-shrink-wrap yields 140/148 and 172/172 bytes,
no relocations. Disabling shrink wrapping removes a duplicate zero-length
return sequence in the read body and restores its original frame placement.
Other probes: Os/no-expensive and Os/no-tree-pre read176/program140;
O2/no-expensive read192/program170.

Read uses 0xeb/0x40003219 for JEDEC 0x1c3812/0x1c3813, otherwise
0x6b/0x40004218. Program uses command 0x32 and 0x40000218. Both transfer
floor(length/4) words with polling and controller cleanup. Read length zero
returns immediately; program zero still configures and drains hardware.
Nonmultiples truncate rather than reject. These candidates require decoded
MMIO/buffer/frame comparison before admission; package remains the existing
87-function build. Full source-only goal remains active.


Word-read/program callbacks pass 2522 full decoded comparisons. Checks compare
ordered controller/state reads and writes, exact word buffer access bounds,
original/source frames, qualified polling-helper call order, device-ID branch
boundaries and FIFO delays. Counts cover every length 0..65, 255/256/257/1024,
and a 65536-byte transfer for each direction. NULL is used only where no full
word is accessed; nonmultiples truncate as observed. Four rejection/oracle
tests pass. Prepared verify_gx8002_flash_word_io.py and reviewed baseline;
provider/package integration is next. Polling helpers are modeled using their
qualified contracts, not executed inline; hardware timing remains unqualified.
Existing 87-function package unchanged; full source-only goal active.


Integrated both word-I/O callbacks after reviewed 2522-case comparison. All
126 tests pass; macOS full package build and artifact verification pass.
Codec now has 89 source functions / 105 code occurrences plus ten data regions:
5414 C bytes, 1764 data, 80 metadata, 252 fill, 318582 retained stock bytes.
Codec SHA: 4ee3783937c3f656a78f6d68750ff97b67f62ac6a6377e2762fb2d937cc39726.
Package SHA: 6a5087b53a005901eb42e58adf4c315e2b3f08c561bf18c4f5c844f61d776ff5.

Initializer now uses named C declarations for discovery and both installed
callbacks: no address-named unknown executable dependency remains in that
source file. Its 198 decoded comparison cases pass; it remains unadmitted
pending state/interface ownership, end-to-end composition and the four-byte
stack-frame increase. Full source-only goal remains active.


Recovered flash getinfo (0x1586c) and gettype (0x16258), using the authenticated
pinned SDK gx_flash_info enum for selector naming. C uses stock behavior;
PAGE_NUM remains unsupported (-1), block/sector/erase count truncates size>>12.
Native -Os -fno-bit-tests --param=case-values-threshold=1 builds 76/76 and
12/12 bytes, plus a 56-byte compiler-generated jump table at original XIP
address 0x1020be1c. Gettype is byte-identical. Default Os tried bit-test
lowering (124 code bytes, no table); explicit table lowering fits.
Both functions pass 955 decoded comparisons of return values, state/device
read order, generated table dispatch and preserved registers. Four checker
and oracle tests pass. Admission baseline and package integration remain next;
retained data ownership and physical hardware remain unqualified. Existing
89-function package unchanged; full source-only goal active.


Integrated getinfo/gettype and C-generated selector table after reviewed
955-case comparison. All 130 tests pass; macOS full package build and artifact
verification pass. Codec now has 91 source functions / 107 code occurrences
plus eleven data regions: 5502 C bytes, 1820 data, 80 metadata, 252 fill,
318438 retained stock bytes.
Codec SHA: 3997774eeab7ffd6b4da3d090cc94fc8383062c744c5c8c5244992ea81b239ef.
Package SHA: 677de9da0229fdbeac3b863c5c2356929067f8da7c37a0d2ec9e5df52efb005f.

Identified device+0x10 protection profile (entry pointer/count; each entry
contains two status masks/values and protected length), and device+0x14 OTP
descriptor. Reconstructed four OTP region accessors at packages 0x15b38,
0x15b4c,0x15b74,0x15b8c: native sizes 20/20,36/40,24/24,20/20; count/size
getters byte-identical. Candidates require decoded qualification and admission.
Descriptor+8 region size, +12 count, +16 selected-region bits; first two words
and protection-profile initialization remain to trace. Full goal active.


Four OTP region accessors pass 40752 full decoded comparisons: unsigned
region/count boundaries, all low-byte flag values plus every upper bit,
output alias with descriptor flags, exact pointer-chain read/store order,
and preserved registers. Four rejection/oracle tests pass. Region selection
matches (old & ~7) | region after the unsigned count check; no invented mask
is applied to region itself, including synthetic counts above eight.
Prepared verify_gx8002_flash_otp_region.py and reviewed baseline. Package
integration is next. Descriptor/state ownership and physical OTP operation
remain unqualified; existing 91-function package unchanged. Goal active.


Integrated four OTP accessors after reviewed 40752-case comparison. All 134
tests pass; macOS full package build and artifact verification pass. Codec
now has 95 source functions / 111 code occurrences plus eleven data regions:
5602 C bytes, 1820 data, 80 metadata, 256 fill, 318334 retained stock bytes.
Codec SHA: 9d14f3df34768dcede554ca6e8f82a3929a2e00612208f9b0dfe683e9f6023e5.
Package SHA: 41321485948ad8a9ad1c00335db4324c3bf1f3a85c5801e6fbf637c128d3391b.

OTP read prefix confirms descriptor words 0/1 are base and region stride,
address = base + offset + selected_region * stride. Authored named C descriptor
(base/stride 0x1000, size512, count3, flags0), pending build/admission checks.
State+0x10 is command/address scratch storage. Recovered address encoder at
0x15ba0: native 60/76 bytes. It reloads width four times and uses explicit
CK804 shift semantics (six low count bits, zero for 32..63) to avoid undefined
C shifts. Manual printed LSR pages243/244 support this; width3 produces a
trailing zero. Encoder comparison/admission remains next. Full goal active.


OTP descriptor now has a native source-build verifier: named fields compile
into an exact 20-byte, four-byte-aligned structure, without relocations, matching
shipped values. Prepared reviewed gx8002-flash-otp-descriptor-verification.json.
The address encoder passes 22528 full decoded comparisons across every address
byte value/position, width boundaries, and widths changing between reads.
Checks use documented CK804 LSR low-six-bit/zero-above31 semantics; source avoids
undefined shifts. Three negative/oracle tests pass. Prepared address admission
adapter and reviewed baseline. Both providers still need package integration.
Existing 95-function package unchanged; physical hardware unqualified and full
source-only goal remains active.


Integrated address encoder and named OTP descriptor. All 137 tests pass;
macOS full package build and artifact verification pass. Codec now has 96
source functions / 112 code occurrences plus twelve data regions: 5662 C bytes,
1840 data, 80 metadata, 272 fill, 318238 retained stock bytes.
Codec SHA: d06d46b80eed72d7a84f9ae6a931bb21427680c66e8500bdd44c239467921096.
Package SHA: e94b89162c07adb78fbbf46998bd3ff49249d7b478c926377d267cf552baedfe.

Authored runtime_gx8002_flash_state.c as named 32-byte initial state; native
compilation matches all stock bytes at package 0x184f8 with no relocations.
Not admitted: five modules still declare state differently (discovery,
initializer, word I/O, info, OTP region); unify through a shared definition
and rerun affected comparisons before linking the state object. Full source-only
goal remains active; physical hardware unqualified.


Unified all six flash-state users through runtime_gx8002_flash_state.h, with
named fields, typed callbacks, size/offset assertions, and reviewed header
provenance. Existing admitted function payloads are unchanged. Discovery
26600, word I/O 2522, info 955, OTP region 40752 and initializer 198 decoded
comparisons pass. The state verifier additionally compiles the six modules
together for declaration compatibility and admits the exact 32-byte initial
state as source data without relocations.

Full native macOS codec build passes all 137 tests. Complete experimental
package build and verify-artifacts pass with unchanged hashes:
codec d06d46b80eed72d7a84f9ae6a931bb21427680c66e8500bdd44c239467921096;
package e94b89162c07adb78fbbf46998bd3ff49249d7b478c926377d267cf552baedfe.
Codec ownership: 5662 compiled C, 1872 source data, 80 metadata, 272 fill,
318206 retained bytes; 96 functions / 112 code occurrences / 13 data regions.
Device and interface tables, remaining callbacks, initializer frame and
end-to-end qualification, other components and physical execution remain
outstanding. Full source-only goal stays active. No hardware was flashed.

Recovered protection status/mode query candidates from actual instructions at
package 0x15900/0x15994. Status writes initial zero before resolving state,
checks profile/entry pointers, waits, reloads manufacturer, reads both status
registers for 0x5e/0x85, reloads profile/count after calls, then scans entries
with exact mask/value/length read order. First matching UINT32_MAX length is
still an error. Mode returns 1 only for nonnull profile and entry pointers.
Native candidate sizes are 160/148 and 36/36 bytes; status exceeds its slot.
Analysis linker explicitly permits overlapping sections solely to inspect
candidates; report marks this and source_admitted=false. Neither function is
registered for admission. Decoded equivalence, code sizing and profile startup
initialization remain next. Existing verified firmware package is unchanged.

Protection candidate sizing audit: -O1 status172 bytes, -O2/-O3 168,
-Os/-Oz160. Ten individual -Os compiler-pass variants do not reduce size;
narrow local byte/halfword types also remain160. Recorded precise query
contract and analysis-only linker limitation in gx8002-flash-protection-source.md.
Next qualification must include output aliasing and helper-driven pointer
changes; do not remove volatile reads merely to fit. No admission or package
change; full source-only goal remains active.

Protection queries pass 49152 decoded stock/source cases using separately
decoded analysis ELF sections. Checks include exact access/call order,
return values, r4-r11/SP, null/empty/populated profiles, status bytes and
manufacturer boundaries, matching UINT32_MAX, and helper-driven selected
device/profile changes. Output aliasing, independent status pairs, rejection
tests and oversized status code remain to resolve. No package admission;
full source-only goal stays active.

Protection qualification expanded to 114752 passing decoded comparisons:
all 65536 independent status pairs, partial-mask matches following status2
rejection, plus 64 output-alias cases with initial-zero mutations propagated
into profile pointers or entry lengths. Nine oracle/rejection tests pass.
Current C still160/148 status bytes and36/36 mode bytes; no provider admission
or package change. Sizing and protection-profile initialization remain next;
full source-only macOS firmware goal stays active.

Resolved protection query size using five explicit source-level CK804 narrow
load intrinsics with immediate offsets (one LD.H, four LD.B). No encoded
bytes are embedded. They preserve ordered reads while avoiding redundant
GCC extensions; remaining logic is C. Status now144/148 bytes, mode36/36.
Removed --no-check-sections; normal linker succeeds without overlapping
sections. All114752 decoded comparisons and nine oracle/rejection tests pass.
Prepared verify_gx8002_flash_protection.py and reviewed verification JSON,
including fit rejection. Package admission is next; existing package unchanged.
Protection profile initialization and hardware remain unqualified. Full goal
stays active.

Integrated protection status/mode through the reviewed verifier. Native macOS
codec build and existing137 integration tests pass; nine new protection tests
pass separately and are now included in the standard Make target. Full package
build and verify-artifacts pass. Codec now98 source functions /114 code
occurrences /13 source-data regions:5842 compiled C (including documented
source-level assembly),1872 data,80 metadata,276 fill,318022 retained bytes.
Codec SHA: ba1b5c999f1b57743b1b7fd3a7ada45acc0e5af797031bb407bdeacb68b013cd.
Package SHA: 7c3fe48b2dae8df173816bbdbe3e4ad5d6477a800602ab7037c41efe1f80bf3d.
Manifest pins updated after observed assembly hash, then rebuilt and verified.
No hardware flashed. Protection profile initialization, remaining flash
callbacks/tables, other components and whole-device execution remain; full
source-only goal stays active.

Recovered flash protection setter plus lock/unlock wrappers from package
0x159b8..0x15aa4 and identified upstream interface signatures. Native sizes
204/204,14/16,16/16; unlock byte-identical. Four explicit source-level byte
load intrinsics remove redundant extensions; normal linker overlap checks
pass. Candidate is not registered for admission. Next: decoded table walk,
status write sequence, helper state changes, output aliasing and frame/ABI
qualification. Existing verified98-function package unchanged. Full goal active.

Protection setter passes12960 decoded comparisons covering table selection,
unsigned request limits, profile replacement across helpers, command bytes,
query-return propagation,40-byte frame and preserved registers. Five tests
check table early-stop, failed-query output, missing-profile behavior,
uninitialized stack reads and invalid command arguments. Local initialization
has a reviewed byte-store/halfword-store difference; final bytes are checked.
Wrappers, broader masks/status coverage and aliases remain pending. No package
admission; full source-only goal active.

Protection setter qualification expanded:78496 setter cases including all
independent status-byte pairs,60 wrapper cases,32 output-alias cases. Wrapper
8-byte frames/arguments/return propagation checked; aliases propagate initial
zero into identifier/profile entries/length while respecting saved pointers.
Nine oracle/rejection tests pass. Native source candidates unchanged; next is
reviewed admission adapter and full macOS package integration. Physical
hardware and protection-profile initialization remain unqualified. Goal active.

Integrated protection setter and lock/unlock wrappers through reviewed
admission adapter. Native macOS codec build passes all155 tests; complete
package build and artifact verification pass. Codec now101 source functions,
117 code occurrences and13 source-data regions:6076 compiled bytes (including
documented inline assembly),1872 data,80 metadata,278 fill,317786 retained.
Codec SHA:92d2b465a61cd524d8d82c5fea28c1ef3d7de3662193a325d6bb9cffd0474988.
Package SHA:07ffb4d1e27366d5efaddcab3ffc2f2ec396776ffd5811c31959c29387d61e4c.

Located protection-profile initializer at package0x166d8/runtime0x100246c4:
six writes populate BSS0x20026ff8 with pointers0x2002657c/0x200265a4/
0x200265dc and counts5/7/9. Recorded decoded named table fields at package
0x18590/0x185b8/0x185f0 in protection-table-inventory.json. This is an analysis
inventory only, not admitted data; semantic source tables and initialization
call-path qualification are next. Full source-only goal active; no hardware
flashed and whole-device execution remains unqualified.

Authored named C protection policy tables for256/512/1024KiB capacities,
5/7/9 entries and168 total bytes. Native verifier confirms exact authenticated
stock match, alignment4, no relocations, entry layout, ordered lengths and
terminal capacities. Source uses named status fields and64KiB length units;
no binary-generated C payload. Prepared reviewed protection-tables verifier.
Located direct profile-initializer call at package0x164ae/runtime0x1002449a
inside flash interface initializer0x16450. Table package integration and
initializer reconstruction/qualification remain next; hardware bit semantics
remain unqualified. Goal active, existing101-function package unchanged.

Reconstructed profile initializer as44-byte byte-exact C at0x166d8. Replaced
initial hardcoded base with linker-resolved BSS symbol to avoid52-byte GCC
address-splitting output. Shared named table header prevents incompatible
extern types and is hashed by both builders. Table verifier regenerated,
still168 exact data bytes. Initializer admission adapter verifies exact bytes
and six decoded ordered stores, no branches/calls/frame. Prepared reviewed
JSON. Both tables and initializer await package integration; BSS ownership
and startup caller remain unqualified. Existing101-function package unchanged;
full source-only macOS goal active.

Integrated all three protection tables and byte-exact initializer. All155
native macOS codec tests pass; full package build and verify-artifacts pass.
Hashes unchanged: codec92d2b465a61cd524d8d82c5fea28c1ef3d7de3662193a325d6bb9cffd0474988;
package07ffb4d1e27366d5efaddcab3ffc2f2ec396776ffd5811c31959c29387d61e4c.
Ownership now6120 compiled bytes,2040 source data,80 metadata,278 fill,
317574 retained bytes;102 functions/118 code occurrences/16 data regions.
Caller-prefix trace confirms profile initialization only after successful
flash discovery, with IRQ15 registration beforehand and divisor4->2 around
that stage. Full interface initialization, BSS ownership, remaining flash
callbacks and all other component/runtime requirements remain outstanding.
Goal active; no hardware flashed.

Recovered IRQ15 flash callback package0x15ad4/runtime0x10023ac0 as30/32 C bytes.
It snapshots controller0xa2000030, conditionally reads0x38 on bit1 then0x3c
on bit3, returns0.846 decoded comparisons cover all low-byte statuses, every
high bit and both selected flags with varied register results. Four negative
tests pass. Prepared reviewed admission verifier; no package integration yet.
Physical IRQ side effects/timing and interface initialization remain unqualified.
Existing102-function package unchanged; full source-only goal active.

2026-09-08: Integrated flash IRQ15 callback. Native macOS codec build passes
all159 tests; full package build and artifact verification pass. Ownership:
6150 compiled bytes,2040 source data,80 metadata,280 fill,317542 retained;
103 functions/119 code occurrences/16 data regions. Codec SHA:
03cd81435091294701bda1bdb32fe62efd784a84764cbd991290b9e8222d36a7.
Package SHA:dfafa22fae521268eb15727edf1e511bdeadc77016c41e61db77cb128d6d3794.
Manifest pins refreshed after observed assembly hash and successful rebuild.
Full interface initializer, BSS ownership, remaining callbacks/components and
hardware execution remain outstanding. Full source-only goal active; no flash.

Reconstructed full interface initializer candidate0x16450/runtime0x1002443c:
428/436 native C bytes. Includes IRQ registration, profile initialization after
successful discovery, device-specific single/pair quad paths, special0xc22017
status-bit6 write, typed callbacks and XIP setup. Uses saved ID across config
calls unlike resume path. Not admitted: decoded branch/MMIO/call/frame checks
remain. Corrected admitted IRQ callback signature to(int,void*) to match actual
registration API; regenerated846-case verifier and four tests pass, compiled
hash confirmed unchanged against admitted build report. Package bytes unchanged;
full integration revalidation with updated source provenance remains next.
Full goal active; hardware unqualified.

Full-interface JEDEC dispatch passes4150 decoded stock/source cases: every
named-ID boundary, signed extremes and4096 deterministic full-width values.
Checks pair/single/no-quad paths, dual-call684015 and device-config204016;
C22017 is explicitly stopped at its first status read, not claimed as fully
qualified. ABI caller-clobbers modeled. Comparison regenerates its stock ELF
from the authenticated input instead of trusting an earlier artifact. Full
setup/special transaction/frame/callback/XIP checks remain. No admission or
package change; source-only goal active.

Full interface initializer passes35328 decoded comparisons covering all256
status bytes, named families, discovery success/failure, two clobber seeds,
48-byte frames, config/MMIO/IRQ ordering, profile init, special status command,
callback writes and nine XIP args. Separate4150-ID dispatch checks remain.
Five rejection tests pass. Candidate428/436 bytes, not admitted yet; prepare
adapter/reviewed baseline then integration. Helpers modeled; interface/BSS
ownership and physical startup unqualified. Full goal active.

Integrated full flash-interface initializer; complete native macOS codec
build passes164 tests including IRQ signature provenance revalidation. Full
package build and verify-artifacts pass. Ownership6578 compiled,2040 source
data,80 metadata,288 fill,317106 retained bytes;104 functions/120 code
occurrences/16 data regions. Codec SHA:
71865672f22d09884895df99f16ce4e2eb51d3406812f5b6d4af79a6b712c368.
Package SHA:7cf153191b71799fb609ffdc76a97ef37097ca33040398079e49022449759fbc.
Remaining interface/device table and BSS ownership, resume initialization,
remaining callbacks/components and physical whole-device behavior are not
qualified. Full source-only goal active; no hardware flashed.

Range erase candidate initially144 bytes but44-byte register frame versus
stock24. Restructured sector/block service paths; disabling loop-invariant
motion gives160/168 bytes and12-byte frame on non-rejection path, with normal
linker overlap checks. Chip erase remains20-byte exact wrapper. This removes
the previous frame growth; decoded behavior/ABI checks remain next. Compiler
probes: no-GCSE168bytes/36frame; other tried pass disables172/36; selected
-fno-move-loop-invariants160/12. No admission or package change. Prior address
encoder pointer corrected to uint32_t, verified unchanged compiled hash and
regenerated baseline. Full source-only goal active.

Range erase passes1152 decoded cases across size/address/length boundaries,
zero lengths,4KiB/64KiB decisions, clamped ends, helper args and caller-clobbers.
Stock24-byte frame and source12-byte valid-path/0 rejection frames verified.
Five oracle/rejection tests pass, including zero-length unaligned request
still erasing one sector. Chip wrapper and long wrapping sequences remain
unqualified; no admission or hardware erase. Full source-only goal active.

Chip-erase wrapper now passes32 decoded cases: reads usable size once, passes
address0 and size to range erase, preserves its4-byte frame and propagates
arbitrary helper return values. Combined range suite still1152 passing cases;
seven oracle/rejection tests pass. Long wrapping erase sequences remain next
before admission. Source-only goal active; package unchanged and no hardware
operation performed.

Erase qualification now includes three complete wrapping sequences (65551,
2 and32769 iterations) matching stock/helper order and terminating. Boundary
suite1152 cases and chip wrapper32 cases pass; eight tests pass. Documented
zero-length unaligned erase and wrapped-end large erase behavior explicitly.
Prepared reviewed verify_gx8002_flash_erase adapter/report. No integration yet;
physical hardware untouched and full source-only goal active.

Integrated range erase and chip erase. Native macOS codec build passes172
tests, including revalidated address-encoder pointer provenance. Complete
package build and verify-artifacts pass. Ownership6758 compiled,2040 source
data,80 metadata,296 fill,316918 retained;106 functions/122 code occurrences/
16 data regions. Codec SHA:
044ab2dd701ab420db59493137483856a2df83393b8d2a4d97bebe3b50fe70cd.
Package SHA:37da0f235b697d4f98dd1b77099dfbdfc1d6aeab1a22573ebb81c237c17b3cc3.
No hardware operation performed. Remaining callbacks, interface/device tables,
BSS ownership, resume startup and other components remain outstanding.
Full source-only goal active.

Recovered flash read wrapper0x15830: native60/60 C bytes with original28-byte
frame. Waits even on zero length, reloads callback per chunk, ignores callback
return, advances unsigned address and uintptr_t destination. Preserves signed
MIN.S32 chunk selection, including one large callback for bit31-set lengths.
Initial explicit sign predicate80bytes; target int32_t cast yields required
instruction/60bytes. Decoded wrapper qualification next; no admission or
package change, physical hardware untouched. Full goal active.

Read wrapper passes177 decoded cases including full32768-callback maximum
signed-positive-length trace, dynamic callback replacement, address/destination
wrap, zero length, high-bit lengths and ignored clobbered callback returns.
28-byte frame and ABI preservation checked. Five tests pass. Callback bodies
modeled; synthetic destinations do not establish buffer validity. Admission
adapter/package integration next. Full source-only goal active.

Prepared reviewed read-wrapper admission adapter/report. Rebuild repeats177
cases including32768-callback long trace; five tests pass. Adapter rejects
oversized sections and carries source/header/compiled hashes plus authenticated
stock interval. Corrected inherited builder descriptions to read-specific
constraints. Ready for registration and full macOS integration; no package
change yet. Full source-only goal active, hardware unqualified.

Integrated read wrapper. Native macOS codec build passes177 tests; full package
build and verify-artifacts pass. Ownership6818 compiled,2040 source data,80
metadata,296 fill,316858 retained bytes;107 functions/123 code occurrences/
16 data regions. Codec SHA:
5cb648116b68a78f47bed9369774bfba71ada509742469e5b9237e8544122a8e.
Package SHA:5393656bfed5d491c28ef5ad626a96f3c6af4a08e0a98a99f73030f2f71c540a.
Remaining write/OTP callbacks, interface/device data, BSS ownership, resume
startup and other components remain. No hardware operation; full goal active.

Reconstructed page-program wrapper0x15c48: zero early return, wrapped bounds,
first partial page, subsequent256-byte chunks, wait/write-enable order,
callback reloads and ignored returns. Current native124/120 after disabling
shrink wrapping; default128, O2 variants132/136 and O1=140. Not admitted;
fitting and decoded boundary/ABI/callback qualification next. Existing107-
function package unchanged; physical hardware untouched, full goal active.

Page-program fitting resolved via priority register allocator:120/120 bytes,
original32-byte frame. Initial640 decoded cases pass for partial/full pages,
zero length, bounds, wrapped addresses/destinations, dynamic callback reloads,
ignored returns and clobber seeds. Large length+offset overflow cases and
rejection tests remain. Not admitted; existing107-function package unchanged.
Full source-only goal active.

Page-program wrapper now passes640 boundary and8 overflow/clobber cases.
Six oracle/rejection tests pass; prepared reviewed admission adapter/report.
Explicitly preserves stock wrapped-sum path allowing one very large callback
length; this is not a buffer-validity claim or hardware recommendation.
Registration/full integration next; existing107-function package unchanged.
Full source-only goal active.

Integrated page-program wrapper on macOS. Native codec build passes all183
tests; full EVENOTA build and verify-artifacts pass under apple-clang.
Page-program contributes120 C bytes without envelope fill, with640 decoded
boundary cases and eight overflow/clobber cases. Current ownership:6938
compiled C,2040 source data,80 metadata,296 fill,316738 retained bytes.
There are108 functions/124 code occurrences and16 data regions (140 total).
Codec SHA-256:3c3009eb0bcc3f4c9a36f033bfc83ad059beccb0d3d19e7ef6a2937444edf164.
Package SHA-256:b0e409bbbc10c96c8f85af87a50adefac582365ed581593254b42bd00d5113a6.
The manifest pins the new candidate; matching that pin is not vendor binary
identity or hardware qualification. No hardware operation was performed.
OTP callbacks, device/interface data, BSS/startup ownership, other codec code
and the other firmware components remain. Full source-only goal stays active.

Recovered block-bounds, block-range and sync C. Native macOS sizes68/72,
38/40 and8/8; sync byte-identical. Decoded leaf comparison passes1600 boundary
and output/state-alias cases. Preserves initial output writes, rounded capacity,
wrapped range end and zero-length behavior. Wrapper call/stack verification,
independent expected-result/rejection tests and large-capacity cases remain;
not admitted yet. Existing108-function package unchanged. Full goal active.

Block-boundary qualification expanded:1600 stock/source cases now also match
an independent closed-form expected trace. Four large-capacity cases complete
at sizes0xffffffff and0x80000001, covering the last full block and first
excluded block. Seven expected-result and interpreter-rejection tests pass.
The range wrapper passes240 decoded cases checking its20-byte frame, helper
arguments, wrapped end calculation, failure propagation and caller-register
clobbers. Both calls use the same local slot; helpers remain separately
modeled. Sync remains byte-exact. Admission adapter and wrapper rejection
tests remain before package integration. Existing108-function package remains
unchanged; no hardware operation. Full source-only goal stays active.

Block-range admission report prepared and registered after11 focused tests
pass. Full macOS codec integration running in exec session41876, log
build/gx8002-board/block-range-integration.log; poll that handle rather than
restart. Existing package not yet refreshed. Recovered OTP lock-status C
separately,68/68 bytes with16-byte frame; decoded qualification pending and
not admitted. Full source-only goal active, hardware untouched.

OTP lock-status verification advances to28200 decoded cases and four rejection
tests, with independent result/bit checks. Device changes during wait and
caller-register clobbers are covered; candidate not admitted. Block-range
full integration remains live in session41876 (same handle repeatedly polled,
not restarted). No refreshed package or new ownership count claimed yet.
Full source-only goal active.

Block-range integration completed successfully:194 tests pass. Current codec
SHA0de84f82cd67e10efd7c5cf82d2a54e5dbb55e39b5756adcb7296d02484e31ee;
7052 compiled C,2040 source data,80 metadata,302 fill,316618 retained bytes;
111 functions and143 total source replacement regions. Codec manifest provider
updated; full package build now running in session56810. It still has the
previous package hash pin, so inspect expected mismatch, refresh pin to the
observed assembly hash, rebuild and verify-artifacts. Package completion not
yet claimed. Copy latest report/update build docs after package verification.

Block-bounds/range/sync integration is complete in the experimental package.
Native macOS codec build passes194 tests; full package build and
verify-artifacts pass with apple-clang. Current ownership7052 compiled C,
2040 source data,80 metadata,302 fill,316618 retained bytes. There are111
functions/127 code occurrences and16 data regions. Codec SHA-256:
0de84f82cd67e10efd7c5cf82d2a54e5dbb55e39b5756adcb7296d02484e31ee.
Package SHA-256:eec3a743137a7677b744fafc764eb4d2e30fca0add1d01f1222c4743a7bd21e2.
The new hash pin identifies this candidate, not vendor-byte equivalence.
No hardware operation; complete source-only firmware remains unfinished.

Prepared OTP-status admission adapter and regenerated reviewed verification
report successfully. It requires size fit, decoded comparison and source/header
hash evidence; still not registered in the integration builder. Registration
and full integration are next. Current verified package has111 functions.

Registered OTP-status admission and four focused tests in codec integration.
Full macOS build running in exec session68424; log is
build/gx8002-board/otp-status-integration.log. Poll same handle; do not infer
completion from the existing111-function report. Separately reconstructed OTP
lock at corrected package entry0x16264/runtime10024250, compiling100/100 bytes
with original16-byte frame. Preserves status-byte narrowing and absence of
final wait. Not admitted; decoded qualification next. Full goal active.

OTP lock decoded qualification passes25800 cases and four rejection tests.
Prepared adapter; reviewed report generation running in session27930.
OTP status full integration remains live in session68424; continue polling
that existing handle. Existing111-function package unchanged until full
integration and package assembly complete. Full goal active, no hardware use.

OTP-status integration completed:198 tests pass,112 functions. Codec SHA
f1f109b0c7f1fb9eb6fe837a8b67bc58ddbba2e98f27d120ec1332c4c2a113d7;
7120 C,2040 data,80 metadata,302 fill,316550 retained bytes. Provider pin
updated. Full package build running session15499 with old package hash pin;
inspect mismatch, refresh observed hash, rebuild and verify artifacts before
claiming package completion. Separately recovered OTP erase92/92 bytes;
qualification pending. OTP lock qualified but not registered. Full goal active.

Package assembly produced6374fd9287ce5049798221df2f5963a6ecf08d12810eb06ed2345611dcc5acb4,
as expected differing from prior pin. Updated package pin and started repeat
build in session64013. Poll this handle next, then copy TINYPRINTF notice and
run verify-artifacts. Update research build report/count/hash after verification.

OTP status integrated into the full experimental package. Native macOS codec
build passes198 tests; full build and verify-artifacts pass under apple-clang.
Ownership:7120 C,2040 source data,80 metadata,302 fill,316550 retained bytes;
112 functions/128 code occurrences plus16 data regions. Codec SHA-256:
f1f109b0c7f1fb9eb6fe837a8b67bc58ddbba2e98f27d120ec1332c4c2a113d7.
Package SHA-256:6374fd9287ce5049798221df2f5963a6ecf08d12810eb06ed2345611dcc5acb4.
Candidate hash pin does not imply vendor-byte identity or hardware validation.
The source-only goal remains active; no hardware operation was performed.

OTP lock command-write declaration aligned to const uint8_t * for consistency
with existing modules; reviewed verification regenerated successfully. Now
registered OTP lock and its four tests. Full codec build running session13103,
log build/gx8002-board/otp-lock-integration.log. Poll same handle next. Last
verified package remains112 functions; OTP erase qualification still pending.

OTP erase qualification now passes2000 decoded cases and five rejection tests;
reviewed admission report generated. Covers descriptor snapshots, address
wrap, command mutation/reload, helper ordering and20-byte frame. Not registered
yet. OTP lock integration still running in session13103; poll same handle.
Last verified package remains112 functions. Full goal active; hardware untouched.

Reconstructed OTP byte transmit routine0x15e28, including controller10=1
transition between command prefix and payload. Native C184/164 bytes; compiler
probes184..200 failed to fit. Not admitted; fitting and decoded verification
remain. OTP lock integration still live in session13103, same handle polled.
Last verified package112 functions; OTP erase ready but not registered.
Full source-only goal remains active, no hardware operation.

OTP lock integration completed:202 tests pass;113 functions. Codec SHA
f92c56731ae3896e8414d5d6c870073c24b77174258b9c3187cd675b7978064a;
7220 C,2040 data,80 metadata,302 fill,316450 retained bytes. Package assembly
observed44b611556ef32745f021fe892b58f26ba815feceb5f99f191abcdb9d3c387bcf;
updated candidate pin and repeat package build running session26774. Poll then
copy TINYPRINTF notice and run verify-artifacts; update build docs afterward.
OTP transmit additional fitting probes show180 minimum with-fno-ivopts; current
default184 remains unadmitted. OTP erase ready but not registered. Goal active.

OTP lock fully integrated. Native macOS codec build passes202 tests; full
package build and verify-artifacts pass with apple-clang. Ownership7220 C,
2040 source data,80 metadata,302 fill,316450 retained;113 functions and129
code occurrences plus16 data regions. Codec SHA:
f92c56731ae3896e8414d5d6c870073c24b77174258b9c3187cd675b7978064a.
Package SHA:44b611556ef32745f021fe892b58f26ba815feceb5f99f191abcdb9d3c387bcf.
Candidate pin identifies this hybrid, not vendor identity or hardware proof.
Full source-only goal active; no physical OTP operation.

OTP erase registered with its five tests. Full codec integration running in
session61414; log build/gx8002-board/otp-erase-integration.log. Poll same handle
next. Last verified package remains113 functions until integration succeeds
and package is regenerated. OTP transmit still oversized and unqualified.

OTP transmit fitting progresses184->180 through source-authored zero-extending
LD.B intrinsics. A status-load intrinsic offered no benefit and was removed;
additional compiler probes do not close remaining16 bytes. Current builder
report refreshed; not admitted and still needs decoded verification. OTP erase
integration remains live in session61414, same handle polled. Last verified
package113 functions. Full source-only goal active.

OTP transmit fitting advances180->176 with combined source-authored status
load/mask intrinsic. Register reservation and low-register prefix probes did
not improve; prefix probe removed. Current176/164 candidate remains unadmitted
and unqualified. OTP erase integration still live in session61414, repeatedly
polled without restart. Last verified package113 functions. Goal stays active.

OTP erase integration complete:207 tests pass,114 functions. Codec SHA
e0e125de64f3ebd3f3cf510b9ad1cac594ee6c2d96759fdd9fee63b1dc1ae50f;
7312 C,2040 data,80 metadata,302 fill,316358 retained. Provider pin updated;
package build running session21475 with old package pin. Poll, refresh observed
assembly hash, rebuild and verify artifacts before claiming package completion.
OTP transmit fitting resolved160/164 with stock16-byte frame using explicit
r0 prefix-counter binding and empty asm constraint. Still unqualified and not
admitted. Full source-only goal active; hardware untouched.

OTP erase fully integrated:207 tests pass; macOS full package build and
verify-artifacts pass. Ownership7312 C,2040 data,80 metadata,302 fill,316358
retained;114 functions/130 code occurrences/16 data regions. Codec SHA:
e0e125de64f3ebd3f3cf510b9ad1cac594ee6c2d96759fdd9fee63b1dc1ae50f.
Package SHA:87f057ec9cae015378f8abd9dcc041fcd39e5bae35e8d49ae6e1afd25c0aa6f1.
Candidate pin is not vendor identity or physical qualification. Goal active.

OTP transmit decoded comparison passes1368 cases: prefix0..8, length0..33,
255/256/257/1024, ordinary and wrapping payload pointers, zero/two stalled
polls. Exact ordered MMIO/byte-read/helper traces and ABI returns match stock.
Reuses qualified word-I/O interpreter logic, adding decoded byte reads and
postincrement. Helpers modeled; synthetic wrap does not certify valid buffers.
Rejection tests and admission remain; current114-function package unchanged.

OTP transmit qualification strengthened with explicit16-byte helper frame
checks and seven focused tests;1368 comparisons pass. Reviewed adapter/report
generated and registered. Full codec integration running session38300, log
build/gx8002-board/otp-transmit-integration.log. Poll same handle; last verified
package remains114 functions until full integration/package verification.
Goal active; physical hardware unqualified and untouched.

Reconstructed OTP write wrapper0x15ecc. Native default240/236; priority register
allocation fits228 with original40-byte frame. Source preserves wrapped bounds,
zero rejection after descriptor reads, page split, width reloads, ignored helper
returns, conditional accumulator and final wait. Not admitted; decoded
qualification next. OTP transmit integration still live in session38300; poll
same handle. Last verified package114 functions. Full goal active.

OTP write expected-event model prepared with four passing model tests,
including width mutation and huge wrapped-sum single transfer. These are not
decoded-equivalence tests; target executor/ABI comparison remains. OTP transmit
integration still live in session38300, same handle polled. Last verified
package114 functions. Full source-only goal active, hardware untouched.

OTP write decoded executor passes1344 initial stock/source cases against the
independent expected-event model, with40-byte ABI frame, clobbers and changing
address width. Broader overflow and rejection tests still required; unadmitted.
OTP transmit integration still live in session38300, same handle polled.
Last verified package114 functions. Full source-only goal active.

OTP transmit integration has now completed:214 tests pass,115 functions.
Codec SHA:ff9b2c77bf14c3816086e4629cc1c81cd20bc1deae6a79f58feeadc60e20f1fe;
7472 C,2040 data,80 metadata,306 fill,316194 retained. Provider pin updated;
package build running session2272 with previous package hash pin. Poll this
handle, refresh observed assembly hash, rebuild and verify; update build docs
only after full package verification. Full goal remains active.

OTP transmit fully integrated:214 tests pass; native macOS package build and
verify-artifacts pass.115 functions/131 code occurrences/16 data regions;
7472 C,2040 data,80 metadata,306 fill,316194 retained bytes. Codec SHA:
ff9b2c77bf14c3816086e4629cc1c81cd20bc1deae6a79f58feeadc60e20f1fe.
Package SHA:1cac2b2301ef15916da06e874b603401b5f3fde6cd48b6367627f90b0baad178.
Candidate pin is not vendor identity or hardware qualification. OTP write
also passes ten new overflow cases besides1344 baseline cases; rejection
checks and admission remain. Full source-only goal active; hardware untouched.

OTP write reviewed admission report prepared after ten focused tests pass.
Registered228-byte source and tests for full codec integration. Build running
session99564, log build/gx8002-board/otp-write-integration.log. Poll same handle
next. Last verified full package115 functions until integration and package
verification finish. Remaining OTP read/UID and data ownership work continues;
full source-only goal active and hardware untouched.

Reconstructed OTP read0x15fb8 in C: native344/352 bytes with48-byte frame
(stock52). Preserves signed32-byte chunk selection, command/dummy prefix,
ordered two-phase controller setup, final address encode and wait. Not admitted;
full decoded qualification remains. OTP write integration still live in
session99564, same handle polled. Last verified package115 functions. Goal active.

OTP read expected-event model prepared; three model tests pass. Ordered
command/dummy prefix, received bytes, width changes and final encode included.
Large signed chunks explicitly exceed finite model generation rather than
being truncated. Decoded stock/source comparison still pending. OTP write
integration remains live in session99564, same handle polled. Last verified
package115 functions. Full source-only goal active.

OTP read initial decoded comparison passes96 stock/source cases against the
expected trace, including stack locals and distinct52/48-byte frames, helper
clobbers, byte transfers and final encode. Broader coverage/rejection and
large signed-length qualification remain. OTP write integration still live
in session99564, same handle polled. Last verified package115 functions.
Full source-only goal remains active.

OTP write integration has completed:224 tests pass,116 functions. Codec SHA:
fd31c84f5ac7ccb96f4f4cbf823f4b00ffbff58fea7d403b05608ba64dcb7904;
7700 C,2040 data,80 metadata,314 fill,315958 retained. Provider pin updated;
package build running session21289 with old package pin. Poll, refresh observed
assembly hash, rebuild and verify artifacts, then update build report/docs.
Full source-only goal active.

OTP write fully integrated:224 tests pass; native macOS package build and
verify-artifacts pass.116 functions/132 code occurrences/16 data regions;
7700 C,2040 data,80 metadata,314 fill,315958 retained. Codec SHA:
fd31c84f5ac7ccb96f4f4cbf823f4b00ffbff58fea7d403b05608ba64dcb7904.
Package SHA:6da65e662d06b6d2ac448ae968735d917bbe22f5f062a8f12cc0493ec39fb9ca.
Candidate pin is not hardware proof or vendor identity. Full goal active.

OTP read comparison expanded to2592 cases with both supported manufacturers,
high flags, wrapped base/stride and width, two polling schedules and clobber
seeds. Nine model/rejection tests pass, including missing local stack space,
wrong helper, extra byte/missing effect and unknown opcode. Huge signed chunks
remain outside finite trace generation; not admitted pending separate coverage.

OTP read advances with eight decoded huge signed-length chunk checkpoints;
2592 full trace cases still pass. Candidate width-read scheduling differs at
checkpoint only and is modeled explicitly. Huge transfer loop/exit behavior
remains unqualified; do not admit on selection alone. No running integration;
last verified package116 functions. Full source-only goal active.

OTP read large-length work progresses with252 isolated decoded receive-step
checks, including wrap/high unsigned distances and preserved registers. Both
loops store low byte and increment modulo32, exit only at end. Full huge
entry/cleanup and induction connection still required; not admitted. No live
build pending, last verified package116 functions. Full goal active.

Strengthened OTP receive-loop evidence with exact decoded structure checks
(eight stock/seven source instructions) and reviewed modulo-counter argument.
252 step cases still pass. For nonzero unsigned distance d, cursor advances
once per byte and first equals end after d stores, including wrap. Argument
assumes valid accesses/eventual FIFO readiness and covers inner loop only;
full huge-transfer entry/cleanup connection remains. Goal active;116-function
package unchanged, no hardware use.

OTP read large-transfer entry/cleanup connected via explicit receive-loop
summary guarded by pinned decoded structure and nonzero distance/controller
preconditions. Fourteen compositional entry-to-return cases pass, including
four high-bit lengths;2592 full traces and eight checkpoints remain passing.
Summary rejection/postcondition review remains; not admitted yet. Last verified
package116 functions, no running build. Full goal active, hardware untouched.

OTP read receive-summary rejection/postcondition work passes: five rejection
tests, three scratch-output variants for14 compositional cases,2592 full traces
and eight signed checkpoints. Final verifier rerun after readiness precondition
passes. Admission adapter still pending; current116-function package unchanged.
Full source-only goal active, no hardware operation.

OTP read admission report regenerated successfully and14 focused tests pass.
Registered candidate with full finite/compositional evidence and reviewed-loop
argument hash. Full codec integration running session3915, log
build/gx8002-board/otp-read-integration.log. Poll same handle next. Last verified
package116 functions; full source-only goal active, hardware untouched.

Recovered UID read callback0x16118 in C:140/140 bytes and stock12-byte frame.
Interface-aligned signed int count/output signature, byte manufacturer check,
zero-length controller setup and four dummy bytes, signed MIN count preserved.
Not admitted; decoded qualification pending. OTP read integration still live
in session3915; same handle polled. Last verified package116 functions. Goal active.
UID signature alignment to authenticated signed int interface reduces current
candidate to136/140 bytes; initial140 figure preceded that correction. Still
unqualified/unadmitted. No other package ownership change claimed.

UID expected-event model prepared with five passing model tests, including
manufacturer-byte semantics, count-store alias/order and zero-length command
transmission. Negative count loops require separate qualification; decoded
executor not yet implemented. OTP read integration still live in session3915;
same handle polled. Last verified package116 functions. Goal active.

UID decoded comparison advances to960 positive/zero-capacity cases, including
output aliases, wrapped destinations, clobbers, polls and12-byte frame. Negative
capacity loops/rejection tests remain; unadmitted. OTP read integration still
live in session3915, same handle polled. Last verified package116 functions.
Full source-only goal active, hardware untouched.

OTP read integration completed:238 tests pass,117 functions. Codec SHA:
002ff61b09074547584386a2ddb6f46ee2ab17f7b88b0bcbbbdbbad5278fb0c2;
8044 C,2040 data,80 metadata,322 fill,315606 retained. Provider pin updated;
package build running session48488 with previous package pin. Poll handle,
refresh observed hash, rebuild and verify artifacts before updating package
completion docs. Full goal remains active.

OTP read fully integrated:238 tests pass; macOS package build/verify-artifacts
pass.117 functions/133 code occurrences/16 data regions;8044 C,2040 data,80
metadata,322 fill,315606 retained. Codec SHA:
002ff61b09074547584386a2ddb6f46ee2ab17f7b88b0bcbbbdbbad5278fb0c2.
Package SHA:faa96c088ea31e15bc22f0e89f674505e9ca2dea9039d4a5598ee9a595dfa3dd.
Candidate pin does not imply vendor identity or physical qualification.
Full source-only goal remains active.

UID checks expanded with five target rejection tests (ten including model)
and16 negative-capacity MIN.S32 checkpoints.960 full positive/zero cases still
pass. Checkpoints prove selection only; full huge-loop/exit qualification
remains and UID is not admitted. No hardware operation was performed.

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

The 118-function EVENOTA package built and passed verify-artifacts using the
apple-clang profile on this Mac. Package SHA:
dfb6ae7878a9f6800003c4e97af49bc20b30cfbf57968720eba2069dc263c0de.
This is the updated experimental package pin, not vendor byte identity.

Reconstructed the 120-byte flash interface as a named C struct with 23 source
callbacks and seven null capabilities. Authenticated upstream header layout,
30 offset assertions, callback declaration compilation and target byte match
pass. Corrected both initializer object declarations; full initializer machine
code is unchanged and decoded qualification passes. Registered table admission
and launched full macOS codec integration (flash-interface-table-integration.log).
The internal API still requires explicit reconciliation with public SDK C types
for whole-source integration. Source-only completion remains unproven.

Flash dispatch table integration completed on macOS; all 254 tests and final
package verification passed. There are now 17 source data regions and 151
total replacement regions, with 2160 source data bytes and 315346 retained
bytes. The 118 functions / 8180 C bytes remain unchanged. Codec and package
hashes are unchanged because the source-authored table exactly reproduces its
identified contents. No binary table payload is pulled into the linked object.
Whole-firmware source-only ownership and hardware qualification remain open.

Recreated six SPI-NOR device labels as independent C strings (52 bytes), checked
against authenticated SDK IDs and stock pointer/JEDEC references. Full macOS
integration is running in flash-device-names-integration.log. The 24-byte device
record layout is understood except for its +12 word; records remain retained.
SDK object symbol/relocation evidence identifies profile and OTP pointers but
provides no debug source types for the missing field. No hardware accessed.

Resume initializer breakthrough: a separate static-zero-configuration probe
fits212 bytes including its4-byte source constant and restores the original
32-byte frame.198 full decoded comparisons match stock effects and returns.
Platform config9 is source-qualified as reading input without modifying or
retaining its pointer. The normal candidate is still unchanged/unadmitted;
canonical build, constant accounting and rejection tests are the next step.

Device names integrated successfully:254 tests and apple-clang artifact
verification pass. Codec remains118 functions /8180 C bytes, with23 source data
regions /2212 data bytes and157 total replacement regions. Retained stock is
315294 bytes. Codec and package hashes are unchanged. The default198-case
resume comparison also still passes after adding the optional probe mapping.

Canonical resume initializer now uses208 code bytes plus4 separately owned
source-constant bytes and the original32-byte stack frame.198 full decoded
cases and seven rejection tests pass. Registered admission and launched the
complete macOS codec build in flash-resume-integration.log. Older split setup
and return tools now invoke the full continuous verifier, replacing their stale
configuration-output assumption. Source-only completion remains unproven.

While resume integration runs, a separate board-entry probe resolves its22-byte
versus20-byte envelope. Source-authored asm-goto uses CMPhSI(reason,2) and BF to
express the same unsigned condition directly. It produces20 bytes, byte-exact
to stock; the four-write register helper is also20 bytes and byte-exact. Normal
-Os, priority allocation and disabled sibling calls all stayed22 bytes. Probe
files are board-branch-probe.c/.o/.elf/.txt in build/gx8002-board. Board admission
and exact conditional/call/return checks remain; no raw instruction arrays.

Resume initializer integration completed with261 passing tests. The macOS
codec now owns119 C functions /135 code occurrences,24 data regions and159
total replacement regions:8388 C bytes,2216 source data,80 metadata,326 fill
and315082 retained bytes. Codec SHA:
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
The original32-byte frame is preserved. No physical execution or source-only
completion is claimed; remaining board admission and opaque regions continue.

The119-function experimental package built and passed apple-clang artifact
verification on macOS. Package SHA:
f266554e55cb14031ec39359f92de6dc6881d70a238e8dbc534826fa6f98058c.
This is the new candidate pin, not vendor identity or hardware qualification.

Board entry and register helper are now canonical source candidates. Both
compile byte-exact in20-byte envelopes. The conditional call uses a correctly
typed reference to the reconstructed flash initializer.1572 decoded cases
cover unsigned reset boundaries, varied helper returns and ABI clobber seeds;
five regression tests pass. The four-byte entry frame and four ordered0x59
register writes are checked. Admission is registered and full macOS integration
is running in board-initialize-integration.log. Physical register meanings and
complete startup timing remain unqualified.

Board entry and register helper integrated successfully:266 tests pass. The
codec now has121 C functions /137 code occurrences,24 source-data regions and
161 total replacement regions. Ownership is8428 C bytes,2216 source data,
80 metadata,326 fill and315042 retained bytes. Codec SHA remains
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
Both new functions are byte-exact; only ownership and published metadata change.
The source-only and hardware qualification goal remains active.

The121-function package was rebuilt to refresh its published flash-plan
metadata and passed apple-clang artifact verification. Package hash remains
f266554e55cb14031ec39359f92de6dc6881d70a238e8dbc534826fa6f98058c.
No hardware was accessed or flashed.

Expanded IRQ frame qualification from callback-only nesting to all13 decoded
wrapper instruction boundaries.234 cases (six seeds, nesting depths1..3) pass
with shared stack memory and inherited interrupted register values. The model
now asserts complete architectural register restoration and rejects unreachable
injection points. All17 IRQ tests pass, including four new boundary tests;
the original24-case software and24-case architecture checks still pass.

This is conditional frame evidence, not IRQ admission. The conservative model
injects regardless of actual PSR eligibility and does not establish exception
acceptance timing, instruction atomicity, callback stack bounds or physical
stack capacity. No firmware bytes or package changed; the121-function verified
macOS package remains current. Continue with interrupt timing/stack composition
or remaining source reconstruction; the full source-only goal stays active.

Added a pinned-ISA/SDK IRQ enable-state check:100 combinations establish NIE's
IE/EE setting and NIR's complete PSR restoration across the decoded wrapper,
with callback PSR supplied explicitly.21 IRQ tests pass. This explains why
restore-tail nesting depends on callback enable state and distinguishes the
234-case conservative stack schedule from actual interrupt acceptance.
Priority, timing, fault behavior and stack capacity remain unqualified; IRQ
is not admitted. The verified121-function macOS package remains unchanged.

IRQ ABI audit found a correction: local C-SKY GCC marks r16/r17 callee-preserved,
so the existing model's arbitrary clobbers exceed the ordinary C ABI contract.
The extra saves are conservative, not yet established mandatory. r15 still
needs protection because BSR changes the link register. Authenticated SDK
startup derives SP from configured DRAM end, while the linker separately holds
configured stack space after BSS. Neither the SDK example nor the BSS-to-SP gap
proves shipped G2 callback capacity. Saved audit hashes/expressions; next work
can investigate a smaller ABI-compliant wrapper. No image or package changed.

Compact IRQ probes ruled out several compiler-only routes. Explicit extended
GPR/FPU clobbers in the interrupt C function still produce no corresponding
context saves (60 bytes;56 with shrink wrapping disabled). Ordinary C body
variants remain44 bytes or grow to48. A noreturn branch-to-restore variant is
invalid: its callback path pushes LR and reaches restore without removing that
word. None is admitted; current explicit wrapper and verified firmware are
unchanged. Object sizes/hashes and rejection reasons are recorded in
research/gx8002-irq-compact-probes.json. Further compaction needs an explicit
frame-compatible entry/body arrangement, not trusting interrupt attributes or
noreturn to supply context management.

New compact IRQ architecture source combines dispatch and return in the original
frame instead of calling a separate C body. It is explicit assembly source,
not machine bytes encoded in C, and retains the C dispatcher as the semantic
reference. Native macOS assembly reproduces the original80 bytes exactly and
uses92 software-frame bytes /124 including instruction-managed control/GPR
state.768 decoded context+dispatch cases and four rejection/boundary tests pass.

The executor models ABI-compliant callbacks: r16/r17 remain preserved, while
caller-clobbered GPR/FPU values are varied and restored. Null handlers do not
read private data. This candidate is not admitted yet: nesting, malformed
paths and source-kind ownership accounting remain. Existing121-function package
is unchanged. Source files/tools: runtime_gx8002_irq_compact_entry.S,
build_gx8002_irq_compact_candidate.py and verify_gx8002_irq_compact.py.

Compact IRQ admission now records architecture assembly separately from C.
768 decoded dispatch/context cases,225 post-NIE nested cases and seven target
regression tests pass. Nested exceptions explicitly overwrite outer EPC/EPSR;
NIR recovers from the saved frame. Pre-NIE injection is rejected because control
state is not saved; earlier models at that point established stack layout only,
not real exception-control preservation. Original80 bytes and92-byte software
frame are preserved. Full macOS integration runs in
build/gx8002-irq/compact-integration.log; no hardware qualification claimed.

Compact IRQ integration passed274 tests. Ownership now separates8428 compiled
C bytes (121 functions /137 occurrences) and80 compiled architecture-assembly
bytes (one IRQ entry), with2216 source data,80 metadata,326 fill and314962
retained bytes. There are162 replacement regions. Codec hash is unchanged:
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
This replaces the IRQ executable region without increasing its original frame.
Complete source-only firmware and hardware qualification remain unfinished.

The macOS package was rebuilt with separate assembly ownership metadata and
passed apple-clang artifact verification. Package SHA remains
f266554e55cb14031ec39359f92de6dc6881d70a238e8dbc534826fa6f98058c.
No hardware was accessed. The full source-only goal remains active.

Pinned upstream reset assembly integrated with278 passing tests:121 C functions
plus two architecture entries. Assembly ownership rises to120 bytes; retained
bytes fall to314922 across163 replacement regions. Codec hash unchanged.
The package target now includes the NationalChip startup MIT notice.

Fetched/authenticated upstream lvp/main.c and three API headers. Shipped mode1
is TWS. Adapted C main fits40/44 bytes and matches the stock eight-byte frame;
not admitted yet. Two event callees are already source-owned; system init,
mode init/tick and shutdown remain retained. Next: make main build reproducible
and qualify the loop/return before integration, then recover those dependencies.

Reset-integrated package rebuilt on macOS and passed apple-clang artifact
verification with startup notice present. Package SHA remains
f266554e55cb14031ec39359f92de6dc6881d70a238e8dbc534826fa6f98058c.
Source-only completion and physical runnability remain unfinished.

Main qualification passes120 complete terminating traces, three continuing-loop
checkpoints and six regression tests. Reproducible native builder, admission and
MIT notice packaging are registered; full integration runs in main-integration.log.
Pinned lvp_mode.c and lvp_system_init.c are now fetched/authenticated. Identified
idle/TWS mode records and BSS loop/index state. SystemDone is an original empty
service in upstream and stock, not an unresolved function to stub. Continue
with its faithful recovery and the nontrivial mode/system services after main.

Main integrated with284 passing tests. Codec ownership now includes122 C
functions /138 occurrences, two assembly entries and24 source-data regions,
for164 total replacements. Bytes:8468 C,120 assembly,2216 source data,80
metadata,330 fill and314878 retained. Codec SHA:
57175b6a427347945ad62d6698f1b4a11e5f3a0bc5878d7cd070387247a3f5e7.
Main's upstream-derived loop is now source-built; separate system/mode
services and whole-device runnability remain unfinished.

The122-function package rebuilt on macOS and passed apple-clang artifact
verification with all three notices present. Package SHA:
15b106b1a3e521d81113312b333ee7ee2ea2f3489f3eb58f8ff9f18ab944b1f2.
This candidate pin does not imply vendor byte identity or hardware qualification.

Mode init/tick integrated on macOS:124 C functions /140 occurrences, two
assembly entries,24 source-data regions,166 total replacements. Full integration
passed292 tests. Decoded mode comparisons cover2664 init and480 tick cases,
including callback-induced index/loop changes and preserved12/8-byte frames.
Bytes:8584 C,120 assembly,2216 source data,80 metadata,334 fill,314758 retained.
Codec SHA:39125ccebe16886786fe2571eb4dfcbf3388fe6e62d81ea1fbcaaee43407db45.
The mode copyright year/notice was corrected after the full suite; its targeted
compiler/comparison replay passed and asserted unchanged replacement payloads.
Native apple-clang package build and artifact verification passed, all four
notices copied. Package SHA:
822222384bc5dc426d2491b471a70bf8e17369034c97404f8d4c08d32b7da1e3.
Goal remains active:mode objects/list/BSS/callbacks and extensive remaining
firmware are retained. Authenticated lvp_mode_idle.c and lvp_mode_tws.c are
available locally; identification is in gx8002-mode-callback-source-identification.json.
Next:recover IDLE callbacks, strings and typed info object, then TWS and the
remaining system services. SystemDone is an original empty function, not an
unknown service that may be replaced by a stub. No hardware touched.

IDLE source integrated:128 C functions /144 occurrences, two assembly entries,
27 source-data regions,173 total replacements. All298 full integration tests
pass. IDLE's four callbacks pass336 decoded comparisons; compiled callbacks,
20-byte typed mode object and two22-byte messages exactly reproduce stock.
Empty tick and successful buffer init are original upstream behavior. Ownership:
8622 C,120 assembly,2280 source data,80 metadata,336 fill,314654 retained.
Codec SHA remains39125ccebe16886786fe2571eb4dfcbf3388fe6e62d81ea1fbcaaee43407db45
because these recovered source regions reproduce the previous stock bytes.
The128-function macOS apple-clang package rebuilt and verify-artifacts passed;
all five notices are packaged. EVENOTA SHA remains
822222384bc5dc426d2491b471a70bf8e17369034c97404f8d4c08d32b7da1e3.
This ownership improvement is not whole-device qualification. Goal active.

Next TWS evidence is in gx8002-tws-source-identification.json. Its init uses
queue2002e6ec/buffer2002e700, seven8-byte elements, SNPU callback10026340,
audio callback100263dc, standby state2002e738=2 and countdown2002e73c=50.
Full init envelope108/frame12 atpkg11bfc. Helper addresses mapped; decoder
variant remains to identify. Legacy buffer source and V2 source/header fetched
and authenticated: stock buffer helper's three clears favor legacy hardware
logfbank configuration, but this is not yet full buffer verification. Continue
TWS init/done/buffer/tick and callbacks, system services and all remaining
firmware. No running builds or hardware actions remain from this turn.

TWS initialization now has a source candidate, not admitted. MAX decoder is
identified by the stock diagnostic string and authenticated max_decoder.c
Git blob2a8f84622b184635227da9cd52b6124cc1dfc4f4. Its initialization checks
MODEL_OUTPUT_LENGTH=2 against g_kws_list.count then calls KwsStrategyInit.
New runtime_gx8002_tws_initialize.c and build_gx8002_tws_candidate.py compile
natively on macOS to108 bytes exactly equal to stock atpkg11bfc/runtime10208670.
The candidate uses the upstream queue/mode/SNPU types and preserved12-byte
frame. It is not registered or counted as source ownership yet. Next complete
continuous decoded checks for initial/noninitial modes, wakeup0/1/2/boundaries,
audio success/failure, returning helper clobbers, standby writes2/50, and
upstream enum/prototype compatibility. Then admission/tests/macOS package.
Last integrated image remains128 C functions/298 tests. Goal active; no live
process remains from this turn. No hardware touched.

TWS init integrated with305 passing tests and5130 continuous decoded cases.
The initial handwritten unsigned wakeup declarations failed upstream enum
redeclaration checks under-Werror=enum-int-mismatch. Fixed by generating a
small interface header from exact authenticated enum/prototype excerpts and
using GX_WAKEUP_SOURCE in the source itself. Target compatibility probe passes;
no warning suppression. Emitted code remains108-byte exact stock equivalent.
New compare/verify/test_gx8002_tws files and admission/notice packaging registered.
Ownership:129 C functions /145 occurrences,2 assembly,27 data,174 total regions;
8730 C bytes,120 assembly,2280 source data,80 metadata,336 fill,314546 retained.
Native macOS apple-clang package rebuilt and verify-artifacts passed, with all
six notices copied. Codec SHA remains
39125ccebe16886786fe2571eb4dfcbf3388fe6e62d81ea1fbcaaee43407db45;
EVENOTA SHA remains
822222384bc5dc426d2491b471a70bf8e17369034c97404f8d4c08d32b7da1e3.
Goal active:initialization control only; whole-TWS/audio/decoder and remaining
firmware remain opaque. No running tools/builds or hardware actions remain.

Keyword strategy source/header and decoder header fetched/authenticated; see
gx8002-kws-strategy-source-identification.json. Strategy state2002e7a8 has
164 bytes:total +8 entries of20 bytes(index,value,float score,score index,pointer).
Stock reset10208964/pkg11ef0/20 calls memset164; init10208978/pkg11f04/8 delegates
reset. Insertion10208980/pkg11f0c uses matching20-byte stride/capacity8; fullfloat
semantics still require comparison. Continue MAX init/strategy or remaining
TWS done/buffer/tick/callbacks, not merely more wrappers without their services.

Keyword activation insertion now has a buildable macOS C candidate, not admitted.
Files:runtime_gx8002_kws_insert.c,build_gx8002_kws_insert_candidate.py,
gx8002-kws-insert-candidate.json/.disassembly and gx8002-kws-insert-source.md.
Uses exact authenticated upstream activation type, with size/offset assertions.
Stockpkg11f0c/runtime10208980 envelope144. Firstcompile148; -fno-shrink-wrap and
-fira-algorithm=priority fit144/frame4. Preserved ordered append stores through
volatile entry/count writes. Compiled SHA:
72bf37ef9648e882dcf430e445533e243908b40731bcce104d6b097deeaa1be4.
No source ownership change yet. Next continuous instruction comparison:
stock usesldbi.w postincrement,cmplt signed loop,cmphsi unsigned capacity,
mula.32.l/mult address math,flds/fsts/fcmplts,private r3; candidate savesprivate
inr20. Both usefr0 input score,fr1 existing score; fourintegerargs r0,r1,r2,r3.
Append order index/value/score/scoreindex/private/count now matches. First
matching entry terminates evenif score is not increased. Validcounts0..8;
negativecount skipsloopandlogs;positivecount>8 can scanoutofbounds beforecheck.
Do not clamp or claiminvalidcountmemorysafety. ManualFCMPLTS printed451–453
availablelocally; specialfloat/ABI behavior and regression tests stillneeded.
Goalactive;lastintegrated129C/305tests/macOSpackageunchanged;no liveprocesses.

Keyword activation insertion fully integrated.130 C functions /146 occurrences,
2 assembly entries,27 source-data regions,175 replacements. All314 tests pass.
New continuous decoder compares26048 cases plus578 symbolic FP-condition cases;
9 regression tests cover partial/first matches,signedzero,negativeoverflow,
invalidpositivecount reads,FP/register/frame mutations. Same FCMP operand bits
and both outcomes checked; physicalFPstatus/timing notclaimed. Typed source144
bytes matchesobserved writeorder andframe4. State/message remainseparate.
Ownership8874 C,120 assembly,2280 source data,80 metadata,336 fill,314402 retained.
Codec SHA:c261262126b6ae38b3b63b54ede2bbd666eb46c1e6950b0d79320b2a7804ecf8.
MacOS apple-clang package rebuilt and verify-artifacts passed with all7notices.
Package SHA:31f612bfb097ce05182571f8a0387a51c63d20ef895809f71dfcf5e3f829e0a9.
Goalactive; no complete firmware/source-only/hardware claim. No liveprocesses.

Next decoder evidence in gx8002-max-decoder-layout.json:activationflagsbase
2002e744 two bytes,index+4,window+8=10rows*2columns*4bytes,keywordlistcount+0x58,
listptr+0x5c. Score helperpkg11c68/runtime102086dc/frame84. Wrapperpkg11e84/
102088f8/76bytes/frame8 has vendor difference:skips state/major0 pass if first
scorehelperreturnszero, unlike pinned upstream's unconditional state test.
Contextkws is byte+13; do not assume int or upstreamunalteredflow.
Wakeword parameter table identified at20026c7c/pkg18c90,2x88bytes, upstream
lvp_param.h(no optional fields):words[40],labels[16]short,length,threshold,value,
major. hey_even labels54,54/len2/threshold567/value100/major1; hi_even same
labels/len2 threshold460/value101/major1. Otherlabels0. Details in
 gx8002-wakeword-parameter-identification.json; not yet sourceadmitted and
label54vocabulary/modelweightsnotresolved. Continue typeddata/strategyresetinit,
MAXdecoder and TWS callbacks/services plus allremaining firmware.

Wakeword parameter table integrated as176 bytes of typed source data.130 C
functions/146 occurrences,2assembly,28 data regions,176 total replacements.
All314 integration tests pass. Native macOS package rebuilt and verify-artifacts
passed with8 notices. Ownership8874 C,120 assembly,2456 source data,80 metadata,
336 fill,314226 retained. Codec/package hashes unchanged:
c261262126b6ae38b3b63b54ede2bbd666eb46c1e6950b0d79320b2a7804ecf8 /
31f612bfb097ce05182571f8a0387a51c63d20ef895809f71dfcf5e3f829e0a9.
Source/runtime_gx8002_wakeword_parameters.c uses exact authenticated upstream
type, alloffsetasserts, writabletable176bytes exactlymatchstock; labels54meaning
and modelremainseparate. Goalactive;notcompletefirmware/hardwarequalification.

Independent next candidate:runtime_gx8002_kws_reset.c and
build_gx8002_kws_reset_candidate.py build20-byte reset/8-byte init exactstock,
plus a real source-defined164-byte NOBITS activation object at2002e7a8.
Not admittedyet; requiresnestedcall/clear-range checks andmemset closure.
New gx8002-memset-source-identification.json authenticates plainSDK C and two
architectureobjects. Stockmemsetpkg12f58/runtime102099cc/160 is zextb r1,r1
followedby the exact158bytes of SDK __memset_fast (blobfd20a0df1dffbf1e130ffeb8619ff2b00f44fbd6).
Objects onlycomparisonoracles, never useasemittedimplementation. PlainSDK C
keepsinitiallyunalignedfillsbytewise; stockleadingbytesalignthenwordstores.
Stock usesCMPLTI signed16/4 comparisons (manual confirms signed). Reconstruct
faithful C preservingwidth/order,normalvalidRAM andhugecountarithmeticlimits;
then qualifyreset/init andsourceBSS. No liveprocesses orhardwareactionsremain.

Memset and strategy reset/init integrated:133 C functions/149 occurrences,
2 assembly,28 data regions,179 total replacements.327 integration tests pass.
Memset C emits102/160 bytes, no frame, preserves ordered byte/word fills and
signed block loops;45224 decoded cases+32 large boundary/prefix cases;8 tests.
Reset20/init8 exactstockfunctions execute through decoded memset for164-byte
state in70 cases,41 wordstores,4/8-byte nestedframepeaks;5 tests. Real C BSS
object at2002e7a8 size164 is linked NOBITS; it adds nofirmwarepayloadbytes.
Static internal-entry audit foundnoliteral/directbranchrefs tofastentry102099ce;
computedtargetabsence notproven. Nohardware/arbitraryRAMsizeclaim.
Ownership9004 C,120 assembly,2456 data,80 metadata,394 fill,314038 retained.
MacOS apple-clang package built and verify-artifacts passed with9notices.
Codec SHA:d87ece366d20b7841088442b1b602273980394c7dc47f5b930d531bff5f09814.
Package SHA:543588800b8459879e0ff75dacdbc8f3cafa83583e7d9cff0492818e0ff37d02.
Goalactive; no opaque-free/wholefirmware/hardwareclaim. No liveprocessesremain.

Independent next candidate runtime_gx8002_max_initialize.c and
build_gx8002_max_initialize_candidate.py compile LvpInitMaxKws32bytes at10208944/
pkg11ed0 plus exact66-byte diagnostic at1020b30d/pkg14899. Source uses actual
upstream parameter/listtypes and comparescount2, logsifdifferent, then calls
now-source-owned KwsStrategyInit. Function differsfromstockregisteraddressbase
butfits32; not yet admitted. Need count/call/frame tests thenintegrate; its
liststate andremainingMAXscore/strategy/TWScallbacks stillrequire recovery.

MAX initializer and diagnostic integrated: 134 C functions / 150 occurrences,
two assembly entries, 29 source-data regions, 181 replacements. All 333 tests
pass. Initializer comparison covers 846 cases and six regression checks; its
32-byte code and 66-byte diagnostic are source-built. Ownership: 9036 C,
120 assembly, 2522 data, 80 metadata, 394 fill, 313940 retained bytes.
The macOS apple-clang package rebuilt and passed verify-artifacts with all
ten notices present. Codec SHA:
46a34af82fe254955a09879de51d7927137518dea7d7a9d60264f42f11f5d422.
Package SHA:
86d2338335bd43f3eb8f892cde17b5b819b45a4e7eda89c7d7e07783154e16a8.
Goal remains active; complete scoring, strategy, TWS and other firmware
functionality remains. No live processes or hardware actions remain.

Next candidate: runtime_gx8002_max_list.c and
build_gx8002_max_list_candidate.py reconstruct LvpPrintMaxKwsList at
10208880/pkg11e0c, fitting 120 bytes with the original 32-byte frame. It also
defines eight bytes of list BSS at 2002e79c and five source strings totaling
97 bytes, all exact stock matches. The function first assigns count2 and the
source-owned parameter-table pointer, then prints entries while reloading count
and pointer around printf calls. It is not admitted yet. Qualify ordered state
writes, live count/pointer changes, correct string/int arguments, stride88,
and frame preservation, then integrate it. No full decoder claim from logging.

## Keyword-list integration checkpoint

LvpPrintMaxKwsList is now integrated: 135 C functions / 151 occurrences,
2 architecture entries, 34 source-data regions, 187 replacements total.
All 342 integration tests pass. The new qualification covers 546 cases and
nine regression tests, including live count/pointer reloads around printf.
Ownership: 9156 C, 120 assembly, 2619 data, 80 metadata, 394 fill,
313723 retained bytes. Codec SHA:
74e8d0b5e3626a4b7a7d4dfe143c4215a703a60d557cf518194ac1239c1a9c14.
macOS apple-clang package SHA:
4147f5dd427cfcdbdceda190e1a98ae5e156fb4e47447856d83d6da62b5deb8d.

Next prepared tranche: runtime_gx8002_tws_shutdown.c,
build_gx8002_tws_shutdown_candidate.py, verify_gx8002_tws_shutdown.py,
and test_gx8002_tws_shutdown.py. The buffer-init wrapper (8 bytes), shutdown
wrapper (36 bytes), and exit message (24 bytes) all compile exactly to stock.
The verification report covers 3108 helper-contract cases; seven tests pass.
They are qualified individually but NOT yet registered in the integrated
builder or Makefile test list. Integrate them next after reviewing the report,
then update counts/ownership and package evidence. Their downstream KWS/audio
shutdown and buffer-init helper bodies remain retained. See
research/gx8002-tws-shutdown-source.md for exact qualification boundaries.
Goal remains active; no hardware action was performed.

The keyword-list macOS package build and verify-artifacts both passed, with
all ten required notices copied. No live build processes remain.

## TWS wrapper integration checkpoint

The prior keyword-list turn made concrete progress. TWS lifecycle wrappers
are now integrated: 137 C functions / 153 occurrences, 2 architecture entries,
35 source-data regions, 190 total replacements. All 349 integration tests pass.
Ownership: 9200 C, 120 assembly, 2643 data, 80 metadata, 394 fill,
313655 retained bytes. Newly compiled sections exactly equal stock, so codec
SHA remains 74e8d0b5e3626a4b7a7d4dfe143c4215a703a60d557cf518194ac1239c1a9c14
and package SHA remains
4147f5dd427cfcdbdceda190e1a98ae5e156fb4e47447856d83d6da62b5deb8d.

Next prepared tranche: runtime_gx8002_stream_shutdown.c,
build_gx8002_stream_shutdown_candidate.py, verify_gx8002_stream_shutdown.py,
and test_gx8002_stream_shutdown.py. LvpKwsDone compiles to 20 exact bytes at
10206dac/pkg10338, calls gx_snpu_exit then clears source-defined typed callback
BSS at 20027b50, returns0. LvpAudioInDone compiles to 10 of 12 bytes at
102073f8/pkg10984, calls gx_audio_in_exit then returns0. Both have four-byte
frames. 3108 comparisons and eight tests pass. NOT yet registered in integrated
builder/Makefile. Add NATIONALCHIP-STREAM-NOTICE.txt as eleventh package notice
when integrating (currently only a candidate notice).

Pinned lvp/common/lvp_audio_in.c was fetched and authenticated. The driver
bodies are identified from authenticated SDK objects, not available C in that
SDK. gx8002-driver-exit-identification.json records object hashes; the
*-exit-oracle.disassembly.txt artifacts identify helper relocations:
gx_snpu_exit(10205d40/pkgf2cc,32 bytes) masks IRQ12, calls suspend at pkgf01c,
unmasksIRQ12, calls snpu_device_exit at pkgeb38 iff suspendreturned0,
returns saved result. gx_audio_in_exit(10204984/pkgdf10,44byte envelope)
calls _ain_reset(pkgd214), then owned gx_clock_set_module_enable(10025080)
with (3,0),(2,0),(8,0),(7,0), returns0. Reconstruct/qualify these driver C
bodies next; never emit the SDK objects as payload. Full firmware goal stays
active; no hardware actions performed.

TWS integration macOS apple-clang package build and verify-artifacts passed.
All ten admitted notices are packaged. No live processes remain.

## Recognition/audio shutdown integration checkpoint

The preceding goal turn made concrete progress. The two stream shutdown
helpers are now integrated: 139 C functions /155 occurrences,2 architecture
entries,35 data regions,192 replacements. All357 integration tests pass.
Ownership:9230 C,120 assembly,2643 data,80 metadata,396 fill,313623 retained.
Payload hashes remain unchanged: codec
74e8d0b5e3626a4b7a7d4dfe143c4215a703a60d557cf518194ac1239c1a9c14;
package4147f5dd427cfcdbdceda190e1a98ae5e156fb4e47447856d83d6da62b5deb8d.
NATIONALCHIP-STREAM-NOTICE.txt is now the eleventh admitted package notice.

Next qualified (NOT integrated) tranche: runtime_gx8002_driver_exit.c,
build_gx8002_driver_exit_candidate.py,verify_gx8002_driver_exit.py,
test_gx8002_driver_exit.py. gx_snpu_exit32bytes exact;gx_audio_in_exit42of44.
3384 call/return/ABI cases and8 tests pass. Source reconstruction from stock,
SDKobjects are identity oracles only; IRQ signatures are upstream source.
Register verifier/test, integrate, update manifests/research/package evidence.
Downstream IRQ wrappers/SNPU suspend/deviceexit/audioreset remain retained.

Next unqualified candidate: runtime_gx8002_audio_reset.c,240byte text object
built with standard native C-SKY -Os flags. Source preserves all ordered
volatile MMIO and original unbounded bit8 wait at a0a00104. Need reproducible
linker builder at10203c88/pkgd214 with320byte envelope, then independent
register/MMIO trace verifier (vary values between reads), polling completion
and nontermination-prefix checks. Object/disassembly at
build/gx8002-board/audio-reset-candidate.o and
 audio-reset-candidate-object.disassembly.txt. Authenticated SDKsection is
exact320byte stock, evidence gx8002-audio-reset-identification.json and
 audio-reset-oracle.disassembly.txt. Driver-exit reset prototype changed toint
and requalified. See gx8002-driver-exit-source.md. Goal remains active.

Stream shutdown macOS apple-clang build and verify-artifacts passed with all
11 notices packaged. No live processes remain; no hardware actions performed.

## Audio reset and driver exit integration checkpoint

Previous goal turn was progress. Audio reset and two driver exits now
integrated:142 C functions/158 occurrences,2 architecture entries,35 data
regions,195 replacements. All375 integration tests pass. Ownership:9544 C,
120 assembly,2643 data,80 metadata,478 fill,313227 retained.
CodecSHA68cf3a4aebe9e19b97e511f639bd844ca775f031fb6a7e6bfc40ebdce3d8bf9e.
PackageSHA0b6e07f2de8cd59209300d6298cb57422fde825c1709aea3bce78201f425dc38.

Audio reset build/verifier/tests now exist: build_gx8002_audio_reset_candidate.py,
verify_gx8002_audio_reset.py,test_gx8002_audio_reset.py. 240Cbytes/320envelope,
no stack;2070 completed MMIO cases,621 never-ready polling prefixes,10tests.
Models constant/latched/changing responses,selected delays0..1023; finite
prefixes1,2,32. No physical register semantics/timing claim. Driver exit
qualification3384cases/8tests. All registered in fullbuild andMakefile.

Next candidate: runtime_gx8002_snpu_suspend.c and
build_gx8002_snpu_suspend_candidate.py. Compiles/links72bytes at10205a90,
pkgf01c,frame8. Not qualified/integrated. Source uses external offsetview of
state20027350,word0 and live pointer+5c4;intervening fields explicitly
unmodeled,not sourceowned. Null initialpointer returns-1 beforestateread.
State2 returns0. Else npu_is_enabled(firstpointer);if enabled reloadpointer,
npu_disable;reloadpointer on each npu_all_idle poll untilnonzero. Thenclock
snpu_enable(0),state2,return0. Preserve helper-driven livepointer changes and
unboundedpoll. Bindings:
 npu_is_enabled1020560c, npu_disable10205600,npu_all_idle102056e4,
 gx_clock_set_module_snpu_enable100251ec. Exactsymbolrelocations available
in SDKsnpu.o .sram_text suspend at1a8..1ec. Stockatf01c..f064 in
build/gx8002-board/driver-exit-stock.elf. Need independent call/state/return/
frame verification,helperclobbers,pointer/state mutations,never-readyprefixes,
thenregister/integrate. See gx8002-snpu-suspend-source.md.

Limitedpublicsearch didnot locate matchingdriver C; not proofunavailable.
Authenticatedobjectidentity remains oracleonly. snpu_device_exit at102055ac/
pkgeb38 is originalrts+padding,canrecover faithful emptyfunction afteridentity
qualification. IRQmask/unmask wrappers100254fc/10025504 stillremaining;
underlying enable/disable implementations already owned earlier. Full goal
remains active; no hardware actions performed.

Audio reset integration macOS apple-clang package build and verify-artifacts
passed; all11 admitted notices packaged. No live processes remain.

## SNPU suspend integration checkpoint

The previous goal turn made concrete progress. SNPU suspend is now integrated:
143 C functions /159 occurrences,2 architecture entries,35 data regions,
196 replacements. All385 integration tests pass. Ownership:9616 C,120assembly,
2643data,80metadata,478fill,313155retained. Codec SHA:
4064990b92a6ab6fc82b7be4a0cb25d95920dd7ba85d8d3071e55531f8656cdd.
Package SHA:
670495e97e6826ac27a7ec9c1d916cbbd7342d07a7426d2dcb5081086d6b0ea9.

SNPU verifier covers3024 completed cases,54 never-ready prefixes,10tests.
It compares ordered state/pointer reads,writes,helpercalls,return,frame8,
helperclobbers and pointer/state mutations. The complete SNPUstate remains
unmodeled outside observed offsets; no wholedevice/hardwareclaim.

Next QUALIFIED but NOT INTEGRATED tranche: runtime_gx8002_irq_mask_wrappers.c,
build_gx8002_irq_mask_candidate.py,verify_gx8002_irq_mask.py,
test_gx8002_irq_mask.py. gx_mask_irq100254fc/pkg17510 and gx_unmask_irq
10025504/pkg17518 each8 exactbytes/frame4. Calls source-owned IRQdisable
100254c8 /enable100254ac. Public unsignedargument convertedtoint preserves
bits under targetcompiler;1884 comparisons and5tests pass. Upstreamheader
interfaceprobe authenticated. Register verifier/test,integrate next.

Next UNQUALIFIED candidate: runtime_gx8002_snpu_clock.c compiledobject36bytes
at build/gx8002-board/snpu-clock-candidate.o plus objectdisassembly. Need
reproducible linkerbuilder for runtime100251ec/pkg17200,36byte envelope.
Calls owned irqsave10025560 (pkg17574), reads/writes a0300018 bit8:
enablenonzero clearsbit,enablezero setsbit, then owned irqrestore1002556c
(pkg17580) with exactsavedstate. Frame8 original. Qualify save/read/write/
restore sequence, callerclobbers,all enable bitpatterns,registerresponse,
returnframe. See gx8002-irq-mask-source.md. Goal stays active.

SNPU suspend macOS apple-clang package build and verify-artifacts passed.
All11 admitted notices are packaged. No live processes or hardware actions.

## IRQ wrappers and SNPU clock integration checkpoint

Previous goal turn made progress. IRQ mask/unmask and SNPU clock are now
integrated:146 C functions/162 occurrences,2 architecture entries,35 data
regions,199 replacements. All398 integration tests pass. Ownership:9668 C,
120assembly,2643data,80metadata,478fill,313103retained. Codec SHA:
4e2a3b99d6dad12e37e3658b0fd88b07a991d2270edbe476067e48741f81d864.
Package SHA:
9cca75594f3a16d906e6e21fd992e9ecbae2cd2585d25aab05c286d34390e2c8.
Clock qualification8442cases/8tests;IRQmask1884cases/5tests. Allregistered.

Next candidates (NOT qualified/integrated):
1. runtime_gx8002_npu_registers.c: reg_get_bit26bytes vs12slot(pkgeb4c),
set_bit28 vs16(eb58),clear_bit28 vs16(eb68);get_value4/4(eb78),set_value4/4
(eb7c). Full defined C preserves ISA low-six-bit shift counts;32..63 produce
zero. Thusgetbit0,setbitunchangedread/write,clearbitclearswholeword.
Do NOT silently narrow inputs or use undefined shifts tofit. Need placement
or justified source-authored instructionwrapper approach foroversizehelpers.
No goalblock: ordinaryread/write andcontrolwrappers fit andworkremains.
SDKsnpu_hw.o authenticatedoracle .sram_text helpersat18,24,34,44,48.
ManualLSLline8772,LSR8991,ROTL11887 explicitlyclear >31;manualhash in
 gx8002-npu-register-candidate.json. Candidateobject/disassembly under
 build/gx8002-board/npu-register-candidate*.
2. runtime_gx8002_npu_control.c: npuenable(eb80/runtime102055f4),disable
(eb8c/10205600),isenabled(eb98/1020560c) each10Cbytes/12slot;allidle
(ec70/102056e4)12/12. void* signaturesmatchrecoveredsuspendcaller;calls
primitive set/clear/get bit0;allidlegetbit31 atpointer+12. Needlinkedbuilder,
call/arg/return/frame verification andintegration. SDKsnpu_regs.o authenticated
oracle; gx8002-npu-control-candidate.json andobject/disassemblyrecorded.
See gx8002-npu-register-source.md. Goal remains active,hardware untouched.

IRQ/clock macOS apple-clang package build and verify-artifacts passed; all11
admitted notices packaged. No live processes remain. No hardware actions.

## NPU register/control integration checkpoint

The previous goal turn made progress. Nine routines are now integrated:
152 C-accounted functions /168 occurrences,5 explicitly accounted assembly
routines,35 data regions,208 replacements. All417 integration tests pass.
Ownership:9718 C,156assembly,2643data,80metadata,492fill,313003retained.
Codec SHA:
6c612b4dc5b5f44b079dd714312fc752c3b9faa240b8e754a5bc6b262d927e63.
Package SHA:
6c7fc142bd45f0fdae300cb36d364c887b0db3c6fafa062666f1f88050906493.

Register size issue resolved transparently: runtime_gx8002_npu_registers.c
keeps fully defined portable C and enables three explicit inline LSR/LSL/ROTL
wrappers via OPEN_CFW_GX8002_NATIVE_SHIFTS for nativebuild. Whole get/set/clear
bit routines counted compiled_assembly (10/12/14 bytes),ordinaryread/write
compiled_c(4each). Portable separateELF at10300000+100stride is comparison
only,neverpayload. Nativefitsoriginal12/16/16/4/4slots;86,296 stock/native/
portable cases and12tests pass. All low6counts including32..63 preserved.
Four controlwrappers(10/10/10/12bytes) qualified withdecodedprimitives in2412
cases+7tests. Registeredbuilders/verifiers/tests:
build_gx8002_npu_register_candidate.py,verify_gx8002_npu_registers.py,
build_gx8002_npu_control_candidate.py,verify_gx8002_npu_control.py.

Next linked UNQUALIFIED batch: runtime_gx8002_npu_accessors.c,
identify_gx8002_npu_accessors.py,build_gx8002_npu_accessor_candidate.py.
Seven functions uniquelyidentified byobjectfixedbytes plusactualdecoded
primitivecalltargets; noSDKobjectpayload. Allfit:
 get_over_cmd_addr pkgedec16/16, get_op_overflow_cmd_addr edfc16/16,
 reset ee0c22/24, set_task_head ee2410/12,get_task_head ee3014/16,
 get_base_addr ee4016/16,get_cur_cmd_addr ee5014/16.
Runtime=package+101f6a74. Gettersread offsets260,292,16,index*4,256,
storeoutputandpreserveobservedr0. resetsetsbit3 atoffset4 then8;settask
writesoffset16. Framesgetter/reset8,settask4. Privateoriginalreturntypes
notclaimed;sourcegettersuint32 explicitlypreservesr0value. Need decoded
helper/MMIO/output-store/return/ABI qualification,aliasingvalidcases,
helperclobbers,indexarithmetic,paddingchecks thenregister/integrate.
Identification/linkedcandidateJSONs anddisassembly inresearch/build.
FourotherSDKaccessors hadnomatch,doNOTguessaddresses. See
 gx8002-npu-accessor-source.md. Goal active;hardware untouched.

NPU register/control macOS apple-clang build and verify-artifacts passed.
All11 notices packaged. No live processes remain; no hardware actions.

### NPU accessor recovery checkpoint

Integrated seven source-authored NPU accessors: command-address getters,
reset, task-head get/set, and indexed base-address lookup. Qualification
covers 42,880 decoded stock/source cases and 10 focused tests, including
helper clobbers, output aliasing, observed return registers, indexed-address
wrap, call order, stack frames, and zero padding. No SDK object bytes are
emitted. Full integration passes all 427 tests.

Current accounting: 159 C functions (175 occurrences), five explicitly
assembly-accounted routines, 35 source-data regions, 215 replacements.
Bytes: compiled_c 9826; compiled_assembly 156; generated_source_data 2643;
generated_container_metadata 80; generated_unreachable_fill 500;
retained_stock 312887; total codec 326092. This batch removes 116 bytes
from retained-stock ownership while reproducing the prior payload exactly.
Codec SHA-256: 6c612b4dc5b5f44b079dd714312fc752c3b9faa240b8e754a5bc6b262d927e63.
EVENOTA SHA-256: 6c7fc142bd45f0fdae300cb36d364c887b0db3c6fafa062666f1f88050906493.
The apple-clang macOS package build and verify-artifacts both passed;
all 11 notices are packaged. No hardware was accessed or flashed.

Next nine linked candidates remain UNQUALIFIED and UNREGISTERED:
- Interrupt masks: npu_en_interrupt (ebf8, 120 bytes), npu_clr_interrupt
  (ecf4, 120), npu_clr_interrupt_without_overflow (ed6c, 88), and
  npu_clr_overflow_interrupt (edc4, 40). Preserve each separate helper RMW.
- Configuration: npu_set_clock_gate (eba4, 22/24), npu_set_idle_mode
  (ebbc, 22/24; zero sets bit 4), npu_set_idle_cycle (ebd4, 24/24),
  and npu_set_overtime_thr (ebec, 10/12).
- npu_get_interrupt (ec7c, 118/120): one status read, individual volatile
  output updates, and observed return status & 0x10000.

See gx8002-npu-interrupt-source.md, identify_gx8002_npu_interrupts.py,
and the npu-interrupt-mask, npu-configuration, and npu-interrupt-status
linked-candidate reports. Qualify decoded MMIO traces, caller clobbers,
all relevant flag combinations, ignored input bits, polarity, return
behavior, and frames before admission. npu_dis_interrupt had no matching
stock identification; do not assign an address speculatively.

The goal remains active. source_only and hardware_qualified remain false;
retained codec code/data and the other firmware components still require
recovery before a complete runnable source-only firmware can be claimed.

### NPU configuration integration and interrupt qualification

Previous goal turn was progress: seven accessors were integrated and the
macOS artifact verification passed. This turn integrates four configuration
routines (clock gate, idle mode, idle cycle, overtime threshold), with
71,824 decoded comparison cases and nine mutation/behavior tests. All 436
integration tests pass. The apple-clang macOS package build and artifact
verification pass, all 11 notices copied, and no live processes remain.

Current accounting: 163 C functions / 179 occurrences, five explicitly
assembly-accounted routines, 35 source-data regions, 219 replacements.
compiled_c 9904; compiled_assembly 156; generated_source_data 2643;
generated_container_metadata 80; generated_unreachable_fill 506;
retained_stock 312803. Total codec 326092. Payload and EVENOTA hashes remain
6c612b4dc5b5f44b079dd714312fc752c3b9faa240b8e754a5bc6b262d927e63 and
6c7fc142bd45f0fdae300cb36d364c887b0db3c6fafa062666f1f88050906493.

Next integration-ready batch: four interrupt masks and one status routine.
verify_gx8002_npu_interrupt_masks.py qualifies 36,864 cases; its nine tests
pass. It preserves individual ordered RMW calls under latched/changing
register reads and all low-seven-bit combinations plus ignored high bits.
Stock uses three-register ADDU in places; the interpreter now supports it.
verify_gx8002_npu_interrupt_status.py qualifies 6,144 cases; its nine tests
pass. It covers one status snapshot, separate volatile output RMW updates,
aliasing, changing output reads, caller clobbers, observed r0 and frame.
Reviewed JSON reports exist. Both remain UNREGISTERED: add imports/tuples
in build_gx8002_source_candidate.py and tests in Makefile, then integrate.
Artifact names npu-interrupt-mask.elf and npu-interrupt-status.elf.
Expected additional envelopes 120+120+88+40+120 = 488 bytes, C 486;
use actual build output for accounting/hashes, not this estimate. Mask source
instructions differ from stock so expect payload hashes to change.
The configuration batch is already registered; do not register it twice.

See gx8002-npu-interrupt-source.md for source behavior and qualifications.
Physical hardware remains untouched and unqualified. The full source-only
goal remains active; retained code/data and other components still remain.

### NPU interrupt integration checkpoint

The previous turn was progress (four configuration routines integrated).
This turn registers and integrates four interrupt-mask routines and the
interrupt status reader. All 454 integration tests pass. macOS apple-clang
package build and verify-artifacts pass; all 11 notices copied. No live
processes remain. No hardware actions occurred.

Current: 168 C functions / 184 occurrences, five assembly-accounted routines,
35 source-data regions, 224 replacements. compiled_c 10390;
compiled_assembly 156; generated_source_data 2643;
generated_container_metadata 80; generated_unreachable_fill 508;
retained_stock 312315. Codec total 326092; EVENOTA total 4750780.
Codec SHA: 768f4c7bd1ba44d24f71fe76bc9b53379cd26071f4122e5ee2fae374ca5e5a22.
EVENOTA SHA: b5d2484666cc68a30aff2fd34b28b239144d97f5474efdf77b2e4e0fccb17557.
Manifest and research integration reports are current. Mask source code
changes instructions but preserves qualified traces; 488 bytes removed
from retained ownership. Source-only/hardware-qualified remain false.

Next qualified UNREGISTERED batch (four functions):
1. runtime_gx8002_snpu_device.c, build_gx8002_snpu_device_candidate.py,
   verify_gx8002_snpu_device.py, test_gx8002_snpu_device.py.
   11,664 cases / eight tests. Three routines:
   snpu_device_init pkg eb34/runtime102055a8 C2/envelope4;
   snpu_device_exit eb38/102055ac C2/envelope4;
   snpu_request_irq eb3c/102055b0 C14/envelope16.
   Complete authenticated SDK snpu_hw.o .sram_text (76 bytes) matched with
   only its one branch relocation resolved to owned request_irq1002553c.
   Empty hooks are authentic original returns, not missing-function stubs.
   Wrapper forwards handler/data to IRQ12; authenticated gx_irq.h supplies
   callback/helper types. Pointer encodings are forwarding tests only.
   Admission artifact snpu-device.elf; reviewed report
   gx8002-snpu-device-verification.json.
2. runtime_gx8002_npu_regs_init.c, build_gx8002_npu_regs_init_candidate.py,
   verify_gx8002_npu_regs_init.py, test_gx8002_npu_regs_init.py.
   888 cases / eight tests. pkg eedc/runtime10205950 C64/envelope76.
   Six calls each reload external volatile pointer slot20027914:
   clock_gate1, idle_cycle2000, idle_mode0, clr_interrupt111,
   en_interrupt109, overtime_thr1048576. Frame8. State is not owned.
   Admission artifact npu-regs-init.elf; reviewed report
   gx8002-npu-regs-init-verification.json.

Register those two verifier tuples and test modules, integrate, update
actual accounting/hashes and macOS package. No further confirmation needed.
Docs gx8002-snpu-device-source.md and gx8002-npu-regs-init-source.md.
Further identified but unrecovered: stock resume at pkg ef28/runtime1020599c
resembles SDK resume offsetbc. Clears state offsets0,5c0,5d0, enables SNPU
clock, conditionally disables/waits for idle using live pointer+5c4, resets
using pointer+5c8, calls npu_regs_init, returns0. Must inspect full stock
before implementation; this is a lead, not qualified behavior. SDK snpu.o
npu_regs_init74, resume bc, suspend1a8, gx_snpu_init408, exit448,
get_state5f0, stop5f8, pause620, resume638. Stock offsets need verification.
Goal remains active; broad code/data recovery across all components remains.

### SNPU shim and register initialization integration

Previous turn was progress. Integrated the three SNPU hardware shim routines
and npu_regs_init; all 470 integration tests pass. macOS apple-clang build
and verify-artifacts passed with all 11 notices packaged. No live processes
remain; no hardware actions. Current accounting: 172 C functions / 188
occurrences, five assembly-accounted routines, 35 source-data regions,
228 replacements. compiled_c10472, compiled_assembly156,
generated_source_data2643, generated_container_metadata80,
generated_unreachable_fill526, retained_stock312215; codec326092.
Codec SHA: 3aaa27cffbd6228d4f383d3a11782e23314c13e25ece90e044792d03f43ae4fe.
EVENOTA SHA: 8f9e7025f7c3fa98a115f1c8fd7da917b72c655adec78d42c4352260cbf74215.
Manifest and research integration reports updated. Full source-only goal
remains active; source_only/hardware_qualified false.

Next QUALIFIED but UNREGISTERED: internal resume at pkg ef28/runtime1020599c.
Files runtime_gx8002_snpu_resume_internal.c,
build_gx8002_snpu_resume_internal_candidate.py,
verify_gx8002_snpu_resume_internal.py,
test_gx8002_snpu_resume_internal.py; reviewed report
 gx8002-snpu-resume-internal-verification.json; artifact
 snpu-resume-internal.elf. 3024 completed cases +54 polling prefixes,
10 tests. C payload76 equals entire stock76 including literal. Clears
state offsets0,5c0,5d0; clock1; checks enabled, conditionally disables/waits
with live pointer5c4; resets with DIFFERENT pointer5c8; npu_regs_init;
return0. Frame8. Helper mutations of state and both pointers retained;
no final state overwrite. Gaps in offset-view struct explicitly unmodeled.

NEW caller evidence requiring signature refinement before recovering caller:
gx_snpu_init begins pkg f280/runtime10205cf4, not f28c. Stock at f284
sets r0=a0c00000 then calls snpu_device_init. Change the recovered empty
hook to accept an ignored void *register_base argument (rather than void),
regenerate its qualification report, then integrate together with resume.
This does not alter its original empty-return semantics or payload; current
source has no compiled caller to that hook yet. Do not silently ignore this
new interface evidence when reconstructing gx_snpu_init.
Caller instruction body64 + literals12 occupiesf280..f2cc. It writes
pointers5c4=a0c00000,5c8=a0300000,5cc=a0c00190; clears5b4,5b0; calls
tcb_init at ee60; registers ISR10205ce0 with data0; writes state2; returns0.
Still unqualified. See gx8002-snpu-resume-internal-source.md.

New UNQUALIFIED/UNREGISTERED source candidate:
runtime_gx8002_snpu_tcb_init.c and build_gx8002_snpu_tcb_init_candidate.py;
research gx8002-snpu-tcb-init-candidate.json/source.md.
pkg ee60/runtime102058d4; C108/envelope124. Ten records stride144.
For entry0..7: write control10080+entry at record+20hex+entry*12,
and address low28bits(state+record+2chex+entry*12) at nextword.
Then10088 atrecord+80hex and4100ff atrecord+10hex. Total180 writes.
Numeric control-word bit meanings remain unresolved; candidate must NOT
count as complete data recovery. Need decoded write/ABI/untouched-state
qualification and investigate descriptor semantics before admission.
No existing SDK C/header documentation found by local targeted text search;
this is not proof that external documentation is unavailable.

### Internal resume integration and caller/ISR qualification

Previous turn was progress. Refined snpu_device_init to accept an ignored
void *register_base, based on the original gx_snpu_init call. Requalification
passes 11,664 cases and eight tests with unchanged target bytes. Registered
internal resume, and full integration passes all 480 tests.

Current: 173 C functions /189 occurrences, five assembly-accounted routines,
35 source-data regions,229 replacements. compiled_c10548,
compiled_assembly156, generated_source_data2643,
generated_container_metadata80, generated_unreachable_fill526,
retained_stock312139. Codec326092. Internal resume reproduces original
76-byte payload exactly; current codec and package hashes remain
3aaa27cffbd6228d4f383d3a11782e23314c13e25ece90e044792d03f43ae4fe and
8f9e7025f7c3fa98a115f1c8fd7da917b72c655adec78d42c4352260cbf74215.

Next QUALIFIED UNREGISTERED batch:
- runtime_gx8002_snpu_initialize.c; build/verify/test use snpu_initialize;
  packagef280/runtime10205cf4, C76/envelope76; frame12.
  201 cases and eight tests. Ordered device-init argument, state pointer
  writes, zero5b4/5b0, TCB call, ISR registration and final state2/return0.
  Helpers may mutate all observed state; final state assignment preserved.
  Reviewed gx8002-snpu-initialize-verification.json; artifact
  snpu-initialize.elf. Callback uses corrected device-init prototype.
- runtime_gx8002_snpu_isr.c; build/verify/test use snpu_isr;
  packagef26c/runtime10205ce0, C20/envelope20; frame4.
  14,700 cases and six tests. Read state once; state2 skips process_status
  and leavesr0=2; otherwise calls process_status10205bd8/packagef164 and
  preserves observed helper r0. Private return types remain inferred.
  -fno-shrink-wrap preserves unconditional frame and fits20 bytes;
  default GCC generated24 bytes and was NOT admitted.
  Reviewed gx8002-snpu-isr-verification.json; artifact snpu-isr.elf.

Register both tuples and tests, then integrate and macOS-package verify.
Both retain dependencies on separately tracked TCB/process_status recovery;
qualification of a caller does not claim those helpers complete.
TCB candidate remains UNQUALIFIED with unresolved control-word semantics;
see previous checkpoint and gx8002-snpu-tcb-init-source.md.
Detailed caller/ISR docs: gx8002-snpu-initialize-source.md,
gx8002-snpu-isr-source.md. Full goal remains active and hardware untouched.

Internal-resume checkpoint macOS apple-clang package build and artifact
verification passed. All11 notices packaged; no live processes remain.

### SNPU initialization and ISR integration

Previous goal turn was progress. Registered initialization and ISR; all494
integration tests pass. Current175 C functions/191 occurrences, five
assembly-accounted routines,35 source-data regions,231 replacements.
compiled_c10644, compiled_assembly156, generated_source_data2643,
generated_container_metadata80, generated_unreachable_fill526,
retained_stock312043; codec326092. New codec SHA:
4dba6211c779a2d8d44f056b614672b96163033471d10187748594563fa02185.
New EVENOTA SHA:
ed7daaa2d0c8f82be85110bf6fd8a32b7fff205896e973f2d119614dfb211df6.
Manifest/research reports updated. Goal remains active; hardware untouched.

Next substantial candidate is UNQUALIFIED/UNREGISTERED:
runtime_gx8002_snpu_process_status.c,
build_gx8002_snpu_process_status_candidate.py,
gx8002-snpu-process-status-candidate.json/source.md.
Stock pkgf164/runtime10205bd8 envelope264. Final candidate232 bytes with
-fno-move-loop-invariants; frame44 versus original56. Typed callback fields
at record+90/94/98hex use authenticated GRUS GX_SNPU_CALLBACK header and
static offset assertions. Earlier292/260-byte experiments not admitted.
Read gx8002-snpu-process-status-source.md for detailed event priority/ring
semantics and required qualification. Stock and SDK disassemblies saved at
build/gx8002-board/snpu-process-status-stock.txt and *-sdk.txt.
No verifier or tests yet. Must cover all event paths, callback mutations,
snapshot end index, sticky STALL, preserved callback arguments across suspend,
nonmatching-completion prefixes, observed reads/writes/returns and ABI.
Control/data state still only partly understood; do not infer full recovery.

TCB initialization candidate remains unqualified with unresolved control-word
meaning. Overtime reset still retained: pkgf0a8/runtime10205b1c, envelope188;
stock disassembly captured in snpu-overtime-reset-stock.txt for next recovery.
ISA manual MVCV proof: result=!C in bit0 with other bitsclear; final status
handler returns1 if event64, otherwise2 (when no higher-priority path).
No goal completion claimed. Opaque functionality and data remain across all
components, beyond these individual source replacements.

Initialization/ISR checkpoint macOS apple-clang package build and
verify-artifacts passed. All11 notices packaged; no live processes remain.

### Status-handler qualification and integration

Previous turn was progress. Added independent model_gx8002_snpu_process_status.py
and decoded verify_gx8002_snpu_process_status.py. Qualification passes14,048
completed cases and120 noncompletion prefixes;18 mutation/behavior tests.
Registered the handler; all512 integrated tests pass. Model source SHA is
recorded in reviewed evidence. Ring domain is valid0..9; all start/end/target
positions, callback masks, helper/callback mutations and event priorities are
covered. Prefixes stop through32 record visits when no descriptor matches.
Scratch addresses normalized, bounds/initialization and saved frames checked.
Source232 bytes/frame44; original264/frame56. No hardware timing claim.

Current176 C functions/192 occurrences, five assembly-accounted routines,
35 source-data regions,232 replacements. compiled_c10876,
compiled_assembly156, generated_source_data2643,
generated_container_metadata80, generated_unreachable_fill558,
retained_stock311779; codec326092. Codec SHA:
b960ceca0d80371e51e4c16b634b6885efa54125191830a328496d167a223e9c.
EVENOTA SHA:
4917522aee59421dbf449ab079d1d8c92bd7c1a0420e1c08789b9d057ed2514f.
Manifest/research integration reports updated. Full goal remains active.

Next UNQUALIFIED/UNREGISTERED batch:
runtime_gx8002_snpu_overtime_reset.c,
build_gx8002_snpu_overtime_candidate.py,
gx8002-snpu-overtime-candidate.json/source.md.
Two functions: dump_words pkgf064/runtime10205ad8 C60/envelope68/frame24;
overtime_reset pkgf0a8/runtime10205b1c C188/envelope188/frame28 versusstock32.
Five literal strings total147 bytes verified against stock, all currently
retained (ownership checked): dump format8@1020ac0e, address format70@
1020ac16, before heading30@1020ac5c, command heading23@1020ac7a,
type format16@1020ac91. Existing max_list_newline1020b7c2 reused, not emitted.
Builder outputs one ELF with two code sections and five data sections.
No verifiers/tests yet. Qualify both code and literal ownership before registration.

Dump reads32 words and prints format each, newline after10/20/30 plusfinal.
Source countdown gives60 bytes; GCC modulo optimization yielded80 and was
rejected. Return preserves final printf r0. Source reads are volatile.
Overtime reads indexedbase2 via state5cc, current/previous via5c4; diagnostics
and two32-word dumps at current+20000000-128 and current+20000000; byte-read
cmdtype print. If previous0 get taskhead, else readword previous+20000004.
Disable5c4; reset5c8; npu_regs_init; sethead viafresh5c4; enableviafresh5c4.
No idle wait. Command byte/head use const RAM pointers; emitted loads and
helper-boundary changes need explicit checks. Other state pointers volatile.
The final C fits both envelopes; earlier failed overlap/192-byte attempts are
not admitted. All5 strings checked exact. Need printf/clobber/ordering tests,
live dump reads, both headpaths, helper mutations, restart ordering and ABI.
See detailed source doc and snpu-overtime-candidate.disassembly.txt.

TCB candidate still unqualified with unresolved descriptor control meanings;
do not count numeric control words as complete data understanding.

Status-handler checkpoint macOS apple-clang build and verify-artifacts passed.
All11 notices packaged. No live processes remain; hardware untouched.

### Diagnostic dump qualification checkpoint

Previous goal turn was progress. This turn adds
verify_gx8002_snpu_dump.py and test_gx8002_snpu_dump.py. All402 decoded
stock/source comparisons and eight tests pass. Cases cover three aligned
RAM locations,67 word/register seed patterns, fixed/changing read values at
printf boundaries, conservative caller clobbers, exact24-byte frame and
final printf return. Independent expected sequence verifies32 reads,
newlines after10/20/30/32, and full argument order. Mutations catch wrong
line counter, read stride, printf target and frame.

Reviewed report gx8002-snpu-dump-verification.json has dump_qualified=true
and source_admitted=false deliberately. Combined snpu-overtime-candidate.elf
contains the still-unqualified reset routine; do not register the whole ELF
as recovered. No integrated firmware change this turn; current512-test
macOS package and hashes from previous checkpoint remain authoritative.
No live processes. No hardware actions. Full source-only goal remains active.

Next: qualify overtime reset (pkgf0a8/runtime10205b1c), preferably composing
its two dump calls with this decoded dump interpreter. Its source frame28
versusstock32 uses16 local bytes in both. Model three initial getters into
scratch, diagnostic printf arguments and changing memory, exact two dump
addresses, command-byte load, previous==0 taskhead versus next-word head,
then disable/reset/regs_init/sethead/enable with live pointer reloads.
Model pointer changes and callback clobbers; preserve saved head across all
restart helpers. Need all five literal strings in final admission rows,
reusing the already-owned newline. See prior checkpoint and
 gx8002-snpu-overtime-source.md. The dump verifier currently rebuilds the
combined candidate and can be reused without admitting its other sections.

### Overtime integration and gxDNN reference checkpoint

Completed meaningful recovery; full source-only goal stays active. Combined
SNPU overtime reset/dump qualification passes 4,824 reset cases plus 402 dump
cases, with 14 reset and eight dump tests. Live memory/pointer changes and
nested frame/ABI are modeled together. Both C routines and five strings are
registered. The standalone dump report remains deliberately non-admitting;
the combined overtime report admits the whole candidate.

Native macOS integration passes all 534 tests. Full apple-clang package build
and verify-artifacts pass; all 11 notices copied. Current totals: 178 C
functions at 194 occurrences, five architecture routines, 40 data regions,
239 replacements. Ownership: 11124 C, 156 assembly, 2790 source data,
80 metadata, 566 unreachable fill, 311376 retained stock; codec size326092.
Codec SHA ca99fd04844ca74d55f58b534be67bc42b0127e450057e53eaceaca48ea0aec5.
EVENOTA size4750780, SHA
655d9d875879b490730640124b43ab3425b8dac10dcd0d527f5690743a531073.
Manifest pins this experimental hybrid, not vendor identity/hardware proof.
No hardware accessed. No live processes remain.

New official upstream checkout build/upstream-nationalchip-gxdnn at
0637b47c8fa0031f8f5651a903cd7d14716382fd. inspect_gxdnn_cmodel.py authenticates
its grus/lib/libcmodel.a and uses native LLVM to inspect its named ELF64
x86-64 objects. No archive bytes enter firmware; no execution of host archive.
See research/gx8002-gxdnn-cmodel.md and inventory JSON. cmd_parse.o proves
base-command low opcodes80..8f, with index=opcode-80. parse_next_cmd suggests
bit17 sequential versus linked and bit16 absolute versus relative link.
Host64 pointer layout must not be mistaken for target32 command layout.
Bit22 and opcodeff remain unresolved. Next inspect cmd_process.o/cmd_link.o
and transform_rel_to_abs disassembly under build/gxdnn-analysis, corroborate
against target TCB writes, qualify runtime_gx8002_snpu_tcb_init.c. Its108-byte
candidate in124-byte envelope remains unqualified/unregistered. Still need
180-write trace/ABI/untouched-state tests and semantic descriptor encoding.
Full model command/weight recovery and all other retained components remain.

### Descriptor semantic recovery checkpoint

Previous turn was progress (integrated overtime paths and verified package).
This turn inspected authoritative gxDNN cmd_process/transform_rel_to_abs
object disassembly. Bit22 drives cm_set_over_addr plus cm_send_int(1), with
repeat suppression on unchanged command. Opcodeff (enum9) has no arithmetic
operation and self-linked idle handling at cmd_process+3c0; it sends10hex,
then waits or sends8 and returns according to idle type. Relative addressing
uses high4bits as base slot plus low28bits as offset. Target absolute-link
masking is separately understood as the observed target bus-address mapping.

Replaced TCB magic control constants with named semantic fields in C;
native macOS candidate rebuild passes,108bytes within124. Still UNADMITTED;
no integrated payload or package change. See gx8002-gxdnn-cmodel.md for
exact object offsets and limits. Next qualify all180 writes/untouched state
and ABI of runtime_gx8002_snpu_tcb_init.c using decoded stock/source code.
No live processes or hardware operations. Full source-only goal active.

### TCB initialization qualification checkpoint

Previous turn was progress (descriptor semantics and named C fields). Added
verify_gx8002_snpu_tcb_init.py and eight tests in test_gx8002_snpu_tcb_init.py.
All67 cases pass exact180-write traces, full0x5a0 state words plus16-byte
guards each side, callee-save/SP preservation. Test mutations catch opcode,
mask, count, bounds and ABI. Address-mask test explicitly notes that fixed
state does not test all possible address bits. Stock/source decoded opcodes
include MULA, indexed stores and BNEZAD, with unknown instructions rejected.
Source108/envelope124 remains unchanged. Reviewed verification report saved.

Not registered/integrated yet. Next add import and registration tuple in
build_gx8002_source_candidate.py (artifact snpu-tcb-init.elf), add unittest
to Makefile, run full macOS integration (expected542tests), update manifest
and research ownership/hash, build/verify package and copy11 notices. Do not
count the qualified TCB candidate as integrated until actual report proves it.
Last verified package remains534tests,178C functions/194occurrences,
239replacements,311376 retained bytes. No processes live or hardware actions.
Full source-only goal active; model/runtime/other components still incomplete.

### TCB integration and submission candidate checkpoint

Previous turn was progress (qualified initializer). Registered TCB initializer
and its eight tests. Full native macOS integration passed542tests. Full
apple-clang package build and verify-artifacts passed, zero unresolved flash
regions, all11 notices included. No live processes; no hardware operations.

Current179 C functions/195 occurrences, five architecture routines,
40 source-data regions,240 replacements. Codec ownership11232 C,156assembly,
2790data,80metadata,582fill,311252retained, total326092.
Codec SHA f09ee75da3dea63df72463592302e614845543e972004729948c03ccc286b13f.
Package size4750780, SHA
9f322244b02a326940504366451ea8c405db66e18d478831006e6c7a1b34e100.
Manifest pin is experimental candidate identity, not vendor equivalence or
hardware qualification. Full source-only goal remains active.

While integration ran, reconstructed asynchronous gx_snpu_run_task at
pkgf2ec/runtime10205d60 (200-byte envelope). New files runtime_gx8002_snpu_run_task.c,
build_gx8002_snpu_run_task_candidate.py and research/gx8002-snpu-run-task-source.md.
Uses authenticated main SDK GRUS header,32-byte task assertion, named fields.
First versions304/276bytes excluded; direct record pointer compiles188bytes,
SHA9d88636fc8e77a64b92cca036cc0e00b5f5d8f01071d5237bb639022809a3545.
UNQUALIFIED, UNREGISTERED. No payload contribution. Needs decoded target
qualification for null/uninitialized/full cases, valid ten-entry ring indices,
ordered task/state reads/writes, untouched state, helper mutations/clobbers,
ABI. Source frame8 only on success; stock8 fromentry. See saved disassembly.
Helpers internalresume1020599c (owned), submit_task10205a00 (still opaque).
State20027350, registerpointer5c4, end5b4/start5b0, stride144.
Record callback90, module94, private98; base payloads28/34/40/4c/58/64/70
are ops/data/cmd/input/output/tmp/weight;7c descriptor busaddress;88=fffffffe
still needs full semantic purpose. Record10=4100ff and14selflink;84=task.cmd.
Full record/model state not yet owned. gx_snpu_get_state locatedpkgf3b4,
runtime10205e28 (12bytes inclliteral), not yet source-built. Upstream SDK
stop/pause/publicresume were not found immediately after get_state in stock;
do not assume SDK layout equals vendor layout. Continue from actual bytes.

### Command-chain recovery checkpoint

Previous turn was progress (TCB integration,542 tests and package verified).
This turn decoded submit_task pkg ef8c/runtime10205a00, matching named main
SDK snpu.o relocations, and reconstructed C. Candidate124bytes fits144.
Allthree branches modeled in source: emptytail start; stalledtail completion
query/optional previous-link update and mapped restart head; runningtail
new-descriptor flush then previous-link update/8byte flush. All finish by
storing newtail5c0. Registerpointer5c4 reloaded across helpers. Source and
stock20-byte frames. UNQUALIFIED/UNREGISTERED.

Added descriptor cache wrapper C atpkg ef74/runtime102059e8,22bytes/env24.
Two ordered clean ranges descriptor8 then descriptor+16 length108. SDK
relocations identify gx_dcache_clean_range runtime10025664. Wrapper also
UNQUALIFIED/UNREGISTERED. No integrated firmware changes. Full542-test
package/hashes from previous checkpoint remain authoritative.

See research/gx8002-snpu-submit-task-source.md. Next qualify submit/run_task
and cache wrapper target traces with state/helper mutations and ABI; inspect
cache helper ownership separately. Previous run_task188/env200 remains
unqualified. Model slot8 payloadfffffffe purpose still unresolved. No live
processes/hardware operations. Full source-only goal active.

### Descriptor cache qualification checkpoint

Previous turn was progress (chain/helper C candidates). Added wrapper
verifier verify_gx8002_snpu_task_cmd_cache_flush.py and seven tests. All2485
comparisons pass; ordered two clean calls, pointer wrapping, clobbers,
observedr0 and8-byte frame verified. Source22/env24. Reviewed report saved,
NOT registered/integrated. Last542-test package unchanged.

Underlying gx_dcache_clean_range10025664/pkg17678 is still retained stock,
envelope92 ends176d4. Decoded address align16+command8, signedsize128 chunks
with8 ordered e000f004 writes, then signedpositive16 steps. SDK header
include/driver/gx_dcache.h confirms int32_t size. Negative means no writes;
misalignment discarded without size adjustment. Next reconstruct/qualify
this helper or continue submit/run_task branch qualification. Adjacent176d4
command10 helper needs identity evidence. No live processes/hardware work.
Full source-only goal active. See gx8002-snpu-submit-task-source.md.

### Cache-clean source candidate checkpoint

Previous turn was progress (wrapper qualification). Reconstructed underlying
cache-clean helper in runtime_gx8002_dcache_clean_range.c with explicit
unsigned32 address arithmetic, signed32 size, eight unrolled MMIO writes
per128-byte chunk and16-byte residual loop. Native macOS candidate88bytes
fits92 atpkg17678/runtime10025664, SHA
6759d32ec24839030372f5d2588373fd248de487c0009122746d6f553b3cb874.
Builder authenticates upstream include/driver/gx_dcache.h and notes snpu.o
is caller-relocation identity only. UNQUALIFIED/UNREGISTERED; no package change.
Bothstock/source leaf; incidental r0 differs, API void. Need exactordered
MMIO, signed boundary/alignment/wrapping, moderatefulltraces/hugeprefixes and
callee-save checks. See gx8002-dcache-clean-range-source.md. Descriptorwrapper
2485cases/seventests is qualified but not integrated. Last542-test package
remains authoritative. No live processes/hardware actions. Full goal active.

### Cache-clean qualification checkpoint

Previous turn was progress (88-byte C candidate). Added
verify_gx8002_dcache_clean_range.py and eight tests. All12864 full cases and
144 hugepositive65-write prefixes pass exact e000f004 writes and callee-save
ABI. All16 alignments at0/20027350/fffffff0, sizes0..257,511..513,4095..4097,
negative limits. Mutations test operation/port/stride/ABI. Full report saved;
source_admitted true in reviewed report, but NOT registered/integrated yet.
No live processes or hardware work. Last542-test package unchanged.

Next register BOTH cache-clean and descriptorcachewrapper verifiers in
build_gx8002_source_candidate.py, artifacts dcache-clean-range.elf and
snpu-task-cmd-cache-flush.elf. Add eight+seven tests toMakefile (expected557).
FullmacOSintegrate, refreshhashes/manifest/research, build+verifypackage,
copy11notices. Lowercache source88/env92 at17678 image_a_sram_text;
wrapper22/env24 atef74 image_a_xip_text. Other submit/run_task candidates
remain unqualified. Full source-only goal active.

### Cache integration running; submit qualification completed

Previous turn was progress (cache qualification). Registered cache-clean and
cache wrapper plus15tests, then started fullmacOSintegration:
make -C g2 gx8002-source-candidate
log build/gx8002-board/dcache-integration.log
LIVE exec session9331, last polled and confirmedrunning. DO NOT restart based
on silent output; poll same handle. Expected557tests. Do not edit registered
sources/verifiers/reviewed reports while running. Manifest/research/package
still refer to previous542-test artifact until build actually succeeds.
Next inspect result; updatefunctioncounts181/197Cocc expected,242replacements,
compiledC11342,fill588,retained311136 expected (use actualreport), hashpins,
macOSpackagebuild/verify and11notices. Other ownership unchanged.

While build ran, added model_gx8002_snpu_submit_task.py and
verify_gx8002_snpu_submit_task.py, plus8tests. All3360cases pass complete
ordered state/link/call traces including mutation oftail/registerpointer at
everyhelper. Source andstock20-byte frames, scratchinitialized, conservative
clobbers. Reviewed report saved; NOTregistered/integrated. ModelSHA pinned.
Cases vary descriptor/tail/state/completion/headbitpatterns. Tests wrong
command offset/state/helper/frame and exactempty/running/stalledpaths.
No hardware operations. Full source-only goal active.

### Cache integration completed on macOS

Previous turn was progress (registration plus submit qualification). Polled
same live9331 until exit0; all557integrationtests passed. Nativeapple-clang
fullpackagebuild and verify-artifacts pass, all11notices copied. Zero
unresolvedflashregions. No liveprocesses/hardwareoperations.

Current181Cfunctions/197occurrences,5architecture routines,40dataregions,
242replacementregions. Ownership11342C,156assembly,2790data,80metadata,
588fill,311136retained; codec326092bytes. CodecSHA
30a21bfd64137499f3c6de0efa8e0192b44109fdef1351606daf48a7e9401974.
Package4750780bytes,SHA
63b55f14dcdc33ab02a46c983129acb0154317d6e557db124564eb4281642754.
Manifest and researchreport updated. Pin is candidate identity, not vendor
identity or device qualification. Fullsource-onlygoal remains active.

Next: qualified submit_task (3360cases/8tests,124/env144) still NOTregistered.
Outer run_task188/env200 stillUNQUALIFIED; qualify ordered task/state accesses,
allvalidringindices, failures, state/helpermutations andABI, ideally compose
actual decoded submit and cache code. Model slot8 valuefffffffe purpose
remains unresolved. Full model assets and other firmware components remain.

### Outer task submission initial qualification

Previous turn was progress (557test cache integration and package verified).
Added model_gx8002_snpu_run_task.py and decoded verifier. All1802cases pass:
100validringpositions x3states x2mutations x3seeds plusnull/uninitialized.
Sixmodeltests+seventargettests pass, including callback/privatebitpatterns,
wrongdescriptor/helper/frame/writeoffset. Source188/env200 unchanged.
ModelSHA included in report. NOTregistered/integrated. Full composition of
submit/cache still pending and slot8fffffffe purpose remains unresolved.
All liveprocesses complete; nohardwareactions; last557-testpackage unchanged.
Next compose helper behavior or address remaining semantic gap before final
admission; submit_task3360cases/8tests also qualified but unregistered.
Full source-only goal remains active.

### Immediate operand sentinel evidence checkpoint

Previous turn was progress (run_task model/target checks). Inspected pinned
upstream calc.o: calc_op_copy compares resolvedsource with64bit-2 at2c;
normalpath8b reads source, sentinelpath13a reads command+24hex immediate.
calc_op_tensor_tensor compares bothsources with-2 at a1/b4; branches170/160
load command+2chex. Strong evidence for immediateoperand sentinel. Target
slot8fffffffe likely selects same mechanism but host64/target32 mapping
still needs corroboration. Documented exactoffsets in gx8002-gxdnn-cmodel.md,
annotated candidate source conservatively, reran1802targetcases successfully
(refreshes sourceSHA/report; compiledpayload unchanged). NOTintegrated.
Next corroborate target model slot8references or compose run/submit/cache
qualification. Last557-testpackage unchanged. No liveprocesses/hardware.
Fullsource-onlygoal active.

### Shipped command-chain structure checkpoint

Previous turn was progress (upstream immediate sentinel evidence). Added
analyze_gx8002_model_command_chain.py authenticating block18d90/9164bytes.
Upstream commandlengths walk all212commands exactly:211sequential then final
linked opcode1 at239c (48bytes), link70000000 =slot7offset0. This corroborates
run_task slot7 completiondescriptor mapping. Counts185opcode1,5opcode41,
4opcode40,4opcode42,14opcode43. Noalignedword80000000; no directslot8sentinel
corroboration in shippedmodel. JSON rows saved, source_admittedfalse; no
firmwarebytes generated. Fullpayload/weights stillopaque. No liveprocesses
orhardwareactions; last557-testpackage unchanged. Fullgoalactive.
Next decode opcode1 subtypes/payload fields, or compose run/submit/cache
checks before admitting callers. Do not confuse commandboundary coverage
with modelsourcecompletion.

### Model operation and copy-field decoding checkpoint

Previous turn was progress (212commandboundaries). Extended authenticated
analyze_gx8002_model_command_chain.py using cmd_process low4payload+10hex
subtype dispatch.185generalops split123copy/20tensorvector/18bn/13active/
9tensortensor/1reduce/1format. Decoded all123copy source/destination relative
addresses,12/12/8bitextents, outer/middle elementstrides and16bitimmediate.
Evidence parse_op_copy_cmd and calc_op_copy (elementsize2,innerstride1).
Report regenerated; source_admittedfalse, nofirmwarepayload. Remaining
operators/weights/reservedfields/modelexecution unresolved. No liveprocesses
orhardware; last557-testpackage unchanged; fullgoalactive. Next use copy
address/extent data to validate tensor-memory bounds/lifetimes and decode
remaining operators, or compose pending run/submit/cache qualifiers.

### Copy geometry checkpoint

Previous turn was progress (operation/copy decoding). Added authenticated
copy geometry analyzer and5passingtests.123copies split55slot1to1,10slot3to1,
58slot1to4; max64elements. Copy-only lowerbound slotbytes1=13056,3=8464,4=7424.
No same-slot write overlaps later source read. Tests forward/backward/odd
byte overlap andslotseparation. Crossslot runtimealiasing andotheroperator
ranges remain unresolved. JSONreport saved, source_admittedfalse. No package
change/liveprocesses/hardware. Fullgoalactive; last557-testpackage authoritative.

### Tensor operand field checkpoint

Previous turn was progress (copygeometry). Extended authenticated chain
analyzer for29tensorvector/tensortensor operations:3operandaddresses,
12/12/8extents, stridefields, immediate16bits andoperationselector.
Upstreamparsevector selectorbits9..10, parsetensorbits11..12 ofpayload10hex.
Observedvector18selector0/1selector1/1selector3; tensor8selector0/1selector2.
Report regenerated. Stridebroadcast and arithmeticnames stillunresolved;
choose_calc_func usesrelocatedjumptable in calc.o, next decode it before
assigningnames. No firmwarechange/liveprocesses/hardware; last557-testpackage
unchanged. Fullgoalactive.

### Arithmetic selector resolution checkpoint

Previous turn was progress (tensorfields). Added authenticated hostobject
relocation analyzer analyze_gxdnn_arithmetic_dispatch.py. Resolves7entries
via addend-entryoffset, then LEA target relocations:0add,1sub,2mul,3div,4pow,
5exp,6log. Chainanalyzer consumes mapping; regenerated212commandreport.
29tensorops=26add,1sub,1mul,1div. Numericalprecision/rounding/hardware still
unqualified. No firmwarechange/liveprocesses/hardware. Fullgoalactive;
last557-testpackage unchanged. Next inspect half_float16 semantics or tensor
broadcast indexing, and pending composed run/submit/cache qualifications.

### Tensor broadcast geometry checkpoint

Previous turn was progress (arithmeticselectorresolution). Traced vectorloop
sourceA i*s0+j*s1+k, sourceB k, destination i*d0+j*d1+k. Tensor-tensor both
sources use same strided index. Added explicitstrides tochainreport and
analyze_gx8002_model_tensor_ranges.py;2tests pass. Tensor-only minimumbytes
slot3=1040,slot1=7380,slot6=120800 (exact declaredweightbytes). Evidence only,
no numeric results/sourceadmission. Runtimealiases/otherops remainopen.
No liveprocesses/hardware; last557-testpackage unchanged; fullgoalactive.

### Half arithmetic library identification lead

Previous turn was progress (tensorbroadcastgeometry). Inspected float16.o:
half_float detail conversion template symbols and tables; add usesbinary32
ADDSS then float2half_impl<float_round_style1>. Officialhalf.sourceforge.net
header documents same namespace/functions and MITlicense, current2.2.1.
Exacthistoricalversion notmatched; no dependencyincorporated. Reference
exp/ln lookup tables131072bytes each remainopaque, nevercopiedintofirmware.
Next pin/comparehistoricalhalf source and conversionsemantics, or continue
pending commandpublication composition. No liveprocesses/hardware; last557
packageunchanged; fullgoalactive.

### Half conversion source match checkpoint

Previous turn was progress (librarylead). Cloned upstream-rocm-half inbuild,
pinned207ee58595a64b5c4a70df221f1e6e704b807811 header1.12.0. Added authenticated
analyze_gxdnn_half_tables.py; all5tables match referencefloat16.o exactly:
base1024/shift512/mantissa8192/exponent256/offset128. Report saved. Thisproves
table sourcefamily, not exactrelease/configuration. Next compare rounding
andNaN/subnormal/overflow code; macOSnative sourceoracle possible. No opaque
payloadintegration, no liveprocesses/hardware; last557packageunchanged;
fullgoalactive.

### Native half rounding qualification checkpoint

Previous turn was progress (5tablematches). Referencefloat2half5a..6e shows
ties-to-even gating; pinnedhalfheader defaults0(tiesaway), requiringexplicit
HALF_ROUND_TIES_TO_EVEN=1. Added verify_gxdnn_half_rounding.py, nativeclang++
probe inbuild/gxdnn-analysis.104556 cases match decodedinstructionformula:
allsignedexponents,boundaryneighbors,specialpatterns,100000LCG patterns.
Report saved; noarchiveexecution/no firmwarepayload. Notall2^32 cases or
NPUhardware proof. Numericoperations/exp-ln tables stillpending. No live
processes/hardware; last557-testpackage unchanged; fullgoalactive.

### Exhaustive half expansion checkpoint

Previous turn was progress (ties-even104556conversioncases). Added
verify_gxdnn_half_expansion.py nativeclang++probe; all65536 halfencodings
match authenticatedreference tableformula binary32bits, includingNaNpayloads.
Report saved. Halfsource pinnedROCm207ee585; nofirmwaredependency yet.
Next validate arithmeticoperations using qualified conversions and carefully
account for binary32 intermediate/NaN behavior; exp/ln lookup generation and
NPUhardware stillopen. No liveprocesses/hardware; last557package unchanged;
fullsource-onlygoalactive.

### Native arithmetic reference checkpoint

Previous turn was progress (exhaustivehalfexpansion). Confirmed sub/div
operandorder A-B/AdivB fromx86rdi/rsi expansion and wrappers. Added source
reference_gxdnn_half_arithmetic.cpp; nativeclang++build withnofastmath,
fpcontractoff, ties-even.8knownanswercasespass (fourops,twoties,signedzero,
subnormal). Report/sourcehashsaved, buildcommanddocumented. Thisis smoke
validation notfullarithmeticequivalence; NaNpayloadsarchitecturedependent.
No firmwarepayload/liveprocesses/hardware; last557package unchanged;
fullgoalactive. Next broaden arithmeticchecks or composedsubmissionchecks.

### Finite half arithmetic comparison checkpoint

Previous turn was progress (nativearithmeticreference). Added reproducible
verify_gxdnn_half_arithmetic.py;113072finiteoperationcases match independent
Python pack/unpack throughbinary32/binary16,0mismatches. Signedzero/subnormal/
unitboundaries/maxfinite/overflow/randomcases. ExcludesNaNs/divzero; notall
pairsorNPUproof. Report saved. No liveprocesses/hardware; last557-testpackage
unchanged; fullgoalactive. Next specialvalues or remaining modeloperators
and composedpendingcommandpublication.

### Special-value observations checkpoint

Previous turn was progress (113072finitechecks). Added reproducible
observe_gxdnn_half_specials.py, rebuilds/authenticates nativeupstream and
rerunsfinitebaseline. Records324specialcases;4signednonzero/divzero checks
match signedinfinity. NaNoutputs observationsonly, nohardwareproof. Report
pins source/upstream. No liveprocesses/hardware; last557package unchanged;
fullgoalactive. Next return to composedsubmit/run/cache admission or recover
remaining modeloperators; NaNsiliconsemantics unresolved.

### Decoded descriptor/cache composition checkpoint

Previous turn was progress (specialarithmeticobservations). Added optional
clean_call hook tocachewrapper interpreter and stack_top tolowercache
interpreter; defaults unchanged. Newdescriptorcachecomposition executes
actual decodedlowerloops at nestedSP.72cases pass4stock/source combinations,
6addresses,3seeds, exactMMIO. Conservativecallerclobbers remain; nohardware
proof. No firmwarebytes changed. Source-admitted reports' default content
unchanged; composition report pins bothverifierhashes. Fullgoalactive.

### Command submission integration checkpoint

Expanded decoded submission/cache composition to 2,304 cases across eight
stock/source combinations. Added verifier/model hash pins and six focused
ordering/mutation tests; all 29 focused tests pass. The nested wrong-port
mutation initially targeted the unused unrolled path and was corrected to
change the residual path that descriptor publication actually executes.
Updated the source cleaner declaration to signed int32_t length; emitted
submission instructions remain identical to the previous qualified candidate.

Registered the 124-byte submission helper (144-byte original region).
Full native macOS integration passes 571 tests. The complete package builds
and verify-artifacts succeeds with apple-clang, 7,822 placed flash regions,
zero unresolved regions. All 11 notices copied. Codec: 182 C functions,
198 C occurrences, five architecture routines, 40 source-data regions,
243 replacement regions. Byte ownership: C 11,466; assembly 156; source data
2,790; metadata 80; unreachable fill 608; retained stock 310,992.
Codec SHA 714a6772dfaf9e6c4fb1edf8674cb01d8dbcc2ee2398dd04c600ad26a00f0082;
EVENOTA SHA 46f29763e9a54774bde100ed068f70cfdfbb2cb3b926ebf3d978cc95595783c2.
Reports and manifest updated. No live processes or hardware access.

The goal remains active. Next compose the unregistered outer run_task with
submission using shared driver words and nested stack, then qualify admission.
The current outer verifier mocks submit/resume; its Case/Model live in
model_gx8002_snpu_run_task.py. Do not edit registered verifier inputs during
integration. Model weights, remaining operator semantics and other firmware
components still require source recovery; this package is not source-only.

### Shared-state outer/publication checkpoint

Previous turn was progress: submission integrated and macOS package verified.
Added optional injected models to independent run/submit expected functions
and decoded interpreters, plus nested SP support for submit. Existing default
behavior unchanged; reviewed submit/run reports refreshed for model hashes.
Added verify_gx8002_run_submit_composition.py: 9,600 shared-state cases pass
all valid ring indices and four stock/source pairings. Resume driver clears
remain modeled; publication hardware helpers remain modeled. Five focused
composition tests cover descriptor/tail sharing, append links, full rejection,
resume clearing and corrupted nested head. Existing 27 related tests pass;
2,304 cache-composition cases rerun and hash pins refreshed.
No firmware payload change or new integration admission this turn. Latest
571-test package remains current. Outer run_task is still unregistered.
Next combine shared-state outer/publication with decoded cache execution,
then evaluate outer admission; physical hardware and model recovery remain
open. Full source-only goal stays active.

### Four-routine task/cache composition checkpoint

Previous turn was progress: shared outer/submit execution added. Extended
composition with injected model/nested SP support in the submit/cache helper
and optional decoded cache programs in outer Shared model. New verifier
verify_gx8002_run_submit_cache_composition.py passes 38,400 cases across all
sixteen stock/source choices for run_task/submit_task/wrapper/cleaner.
Four targeted tests cover flush/enable ordering, prior-link write/clean
ordering, no cache calls on full-ring rejection and mutated cache opcode.
All 15 composition tests pass; 9,600 and 2,304 prior composition baselines
rerun with updated hash pins. Hardware resume and NPU helper bodies remain
modeled in this four-routine composition. No silicon coherence claim.

Registered run_task (188 C bytes in 200-byte envelope) and added its 13 tests
plus nine outer composition tests to the integration target. Refreshed run
review report after correcting stale builder limitation text. Full integration
is LIVE: exec_command session 81375, command make -C g2 gx8002-source-candidate,
log g2/build/gx8002-board/run-task-integration.log. Poll this same handle;
do not restart on observation timeout. Do not edit registered verifier inputs
until completion. Expected test count 593 (prior 571 + 22).

After success, update codec manifest hash/count from build-report.json,
rebuild full package with apple-clang, review/update expected package hash,
rebuild and verify-artifacts, copy all 11 notices, update research build report
and this checkpoint. Latest verified package is still the 571-test version
(codec714a6772..., EVENOTA46f29763...). Goal remains active; weights, remaining
operators, driver-state ownership and other components still need recovery.

### Outer task integration/package completion checkpoint

Previous turn was progress with a live integration process. Polled session
81375 to successful exit; all 593 tests pass. Updated manifest codec hash and
183-function count, rebuilt apple-clang package, reviewed new expected hash,
rebuilt and verified artifacts. All 11 notices copied. Sessions 81375,24543,
48978 are terminal; no live processes or hardware accesses remain.

Current codec: 183 C functions at 199 occurrences, five architecture routines,
40 source-data regions, 244 replacement regions. C 11,654 bytes; assembly156;
source data2,790; metadata80; unreachable fill620; retained stock310,792.
Codec SHA 9b199559385fb15ce974cb4242d4c60463b6a4f3e129449957e86d60e7c656f0.
EVENOTA SHA 61264d20a0fc02827014e408fb14269516f1c7104247e8416b49d12a7bf78683.
Package size4,750,780; placed regions7,822; unresolved0. Research build report
and source notes updated. Source-only/hardware-qualified remain false.

Next retained routine inspected at package f3b4/runtime10205e28: lrw r3,
20027350; ld.w r0,(r3,0); rts; pad/literal to f3c0. Upstream gx_snpu.h declares
GX_SNPU_STATE gx_snpu_get_state(void). This is an immediate next recovery
candidate; adjacent f3c0 begins MMIO a0005080 functions, not more assumed SNPU
layout. Broader driver/state, model semantics/weights and other components
still need source recovery. Full original goal remains active.

### SNPU state getter recovery checkpoint

Previous turn was progress: 593-test package completed. Recovered the state
getter in C using authenticated SDK GX_SNPU_STATE header/32-bit ABI. Native
compiler emits exact stock12bytes (sha e0db1e81ec121e7e298e9e4a1729e274737e52a23ffac3318f1cf38986de80ae).
Added builder/verifier/test/source note under snpu-get-state names. Structural
three-instruction proof covers one volatile load/no writes/return ABI; four
tests pass, including address/store/register mutations. Adjacent f3c0 analog
code is already qualified, confirmed via analog source report.

Registered getter and added four tests. LIVE exec session14996 runs
make -C g2 gx8002-source-candidate, log
 g2/build/gx8002-board/get-state-integration.log.
Poll same handle; do not restart on observation timeout or edit verifier
inputs meanwhile. Expected597tests. After success update ownership research
report and manifest count184. Since compiled bytes equal stock, payload
hashes should stay codec9b199559... / EVENOTA61264d20...; verify actual report.
Latest verified package remains593-test version. Full goal active.

### GPIO dispatch candidate checkpoint

Previous turn was progress with state-query integration live. Session14996
was polled and remains LIVE; get-state-integration.log still at builder.
Do not restart or edit registered inputs. Finish597-test ownership update
and package verification once it exits.

Independent progress: identified retained0xf46c as GPIO ISR using authenticated
SDK gpio_mini.o (blob5f72cf7583d987a96c1d2e994504cddb857966de). Added
runtime_gx8002_gpio_isr.c and build_gx8002_gpio_isr_candidate.py,68Cbytes fit
68-byte envelope/runtime10205ee0. Candidate SHA3f877adbc531c6990cf25740acb7798c9270b21d7fec2c7203ed92064147c41d.
Table20027930,32*12records; pendinga0001030 snapshot; live callback/private/
port loads; callback then per-bit acknowledge. SDKcallbackint(int,void*).
Independent model_gx8002_gpio_isr.py and four tests pass. Not qualified or
registered. Next decode/compare target traces/ABI with mutations; pending
write-one-clear model is interpretation, not hardware proof. Source note
has precise caveats. Goal stays active; latest verified package593tests.

### GPIO decoded qualification checkpoint

Previous turn made GPIO candidate/model progress while state getter integrated.
Added verify_gx8002_gpio_isr.py:864 decoded stock/source cases pass snapshot,
live callback fields, callback clobbers, exact MMIO acknowledgements and28-byte
frame/ABI. Six target tests plus four model tests allpass. Report pins model
and source/build evidence. GPIO still unregistered; no firmwarepayloadchanges.
Pending-state write-one-clear interpretation is not silicon proof.

State-getter integration session14996 remains LIVE after repeated successful
polls, log get-state-integration.log. Keep same handle; no restart/input edits.
Finish expected597-test build/ownership update and verify existing unchanged
package hashes; then GPIO68-byte candidate is ready for integration review.
Latest verified package remains593tests. Full source-only goal stays active.

State getter integration subsequently completed:session14996 exited0,597tests
pass.184 C functions/200 C occurrences,245 replacement regions, C11,666bytes,
retained310,780. Other ownership totals unchanged. Codec hash unchanged9b199559...;
manifest count/research report updated. Direct verify-artifacts detected stale
flash-plan metadata after count change; rebuilt full apple-clang package and
copied11notices, then verification passed. Package SHA remains
61264d20a0fc02827014e408fb14269516f1c7104247e8416b49d12a7bf78683.
Sessions55455 and26854 terminal. No liveprocesses. GPIO864case/10test-qualified
candidate remains unregistered, next integration target. Fullgoalactive.

### GPIO integration and output candidate checkpoint

Previous turn made progress:597-test package verified and GPIOISR qualified.
Registered GPIOISR and its10tests. LIVE session71342 runs
make -C g2 gx8002-source-candidate with log
 g2/build/gx8002-board/gpio-isr-integration.log.
Expected607tests. Poll samehandle; no restart or registered-input edits.
After success update manifest count185/hash, rebuild package, update expected
hash from observed output, rebuild/verify and refresh reports/notices.

Independent progress: recovered GPIOdirection/level C using authenticated
SDK header, builder build_gx8002_gpio_output_candidate.py. Directionpkgf4b0
runtime10205f24,96Cbytes/env100, SHA9332e4c5856aa83291084dfe11abab445e1c885179be808e10f295203b1b7f9f.
Levelpkgf514/runtime10205f88,36Cbytes/env44,
SHAbc2e948e04cf277bc8dd790cc8ab3d624386020f6de347fea390aa71e03ecc48.
Both pending qualification/unregistered. Source note documents observed MMIO
order and enum/port behavior. Next build decoded verifier for allpin/input
patterns, orderedtransactions and ABI. Latest verifiedpackage remains597tests.
Full source-only goal remains active.

### GPIO setter decoded qualification checkpoint

Previous turn progressed:GPIOISR integration started; two setters built.
Added verify_gx8002_gpio_output.py with independent ordered MMIO model and
stock/source decoded leaf interpreter.8,040 cases pass pins0..63 plus boundary
port bits, sixenum encodings, five register patterns and two seeds. Allsix
focused tests pass including mutation of pinmask and ABI. Candidate functions
remain unregistered while GPIOISR fullintegration runs.

Session71342 remains LIVE (polled samehandle), log gpio-isr-integration.log.
Expected607tests; don't restart on observation timeout or edit registered
inputs. Finish package/hash/ownership update after completion; then setter
qualification (direction96/env100,level36/env44) is ready for integration.
Latestverifiedpackage597tests. Fullsource-onlygoalactive.

### GPIO interrupt integration completed

Previous turn progressed setter qualification. Polled live session71342 to
exit0;607tests pass. Updated manifest/function count, rebuilt apple-clang
package with reviewed new hash, copied11notices and verified artifacts.
Sessions71342,72102,21965 terminal; no live processes/hardwareaccess.
Current185 C functions/201 occurrences, five architecture routines,
40 source-data regions and246 replacementregions. C11,734; assembly156;
source data2,790; metadata80; fill620; retained310,712bytes.
Codec SHA3c4a3fca9904601b0bca7427d3d884fac4de454cbf4dbdf8b02e3dcfafb8505f;
package SHAf0245331c18a8b7c517287a6f49ecaa854733fad6a667891853439aa08d68f8d.
Package4,750,780bytes/7,822placed/zero unresolved. Research report updated.
Next integrate qualified GPIOoutput pair (8,040cases/six tests,132Cbytes in
144stock bytes). They remain unregistered. Original source-onlygoalactive.

### GPIO output integration/trigger table checkpoint

Previous turn progressed GPIOISR package607tests. Registered qualified
GPIOoutput pair and six tests. LIVE execsession9580 runs
make -C g2 gx8002-source-candidate, log gpio-output-integration.log.
Expected613tests; poll samehandle and keep registeredinputs unchanged.
After success update count187/hash/ownership, rebuild/reviewpackagehash,
rebuild/verify/copy11notices. Latestverifiedpackage607tests.

Independent progress: decoded next triggerconfiguration atf540/runtime10205fb4,
192byteenvelope, switchtable14230/runtime1020aca4. Added authenticated
analyze_gx8002_gpio_trigger_table.py and researchJSON/MD. Mapping edge1→2c,
2→28,3→24,4→14,8→18 registers relativea0001000; othersskiptriggerMMIOyet
storecallbackrecord/requestIRQ1. Port>=32 returns-1. DirectionINPUT first,
record stores port/callback/private, requestIRQtarget1002553c handler10205ee0.
Next C reconstruction and decodedqualification; reconcile ISR callbackC
prototype after liveintegration, not during. Goalremainsactive.

### GPIO trigger boundary model checkpoint

Previous turn was progress:output integration launched and trigger table
recovered. Revalidated current worktree/log and polled session9580 twice;
it remains LIVE, gpio-output-integration.log at builder. No restart or edits
to its registered inputs. Expected613tests; latest verifiedpackage607tests.

Added model_gx8002_gpio_trigger.py independent ordered registration model
and three passing tests:unsigned invalidport no side effects, unsupported
trigger still direction/record/IRQ registration, pin31 mask. Helper bodies
remain boundaries. Next finish live build/package, reconcile GPIOISR IRQ
callback prototype and reconstruct/compile/qualify trigger C. Original full
source-only goal active; no hardware access or new firmware claim.

### GPIO setter integration completed

Previous turn progressed trigger model while build live. Polled9580 to exit0,
613tests pass. Updated manifest count187/hash; rebuilt full apple-clang package
with reviewed new hash, copied11notices, verified artifacts. Sessions9580,
32412,39241 terminal; no liveprocesses/hardwareaccess.
Current187 C functions/203 occurrences, five architecture routines,
40 source-data regions,248 replacementregions. C11,866; assembly156;
source data2,790; metadata80; fill632; retained310,568.
Codec SHA7f70713935390fd79df945f1e00388015f617cd8516e6873d23ce9676504d092;
package SHA2b831d15dc3bb0c60082bc456728a331881d9cf04df20d977b6d3f8baf5e8713.
Size4,750,780/7,822placed/zero unresolved. Research reports updated.
Next reconstruct trigger C after reconciling GPIOISR IRQcallbackprototype;
trigger model and switchanalysis exist, three modeltests pass. Fullgoalactive.

### GPIO trigger C candidate checkpoint

Previous turn progressed613-test package. Reconciled GPIOISR signature to
int(int irq,void *data), ignoringargs. Emitted68bytes/compiledSHA unchanged;
refreshed ISR review report,864cases and13relatedtests pass. No packagebytes
changed. Added runtime_gx8002_gpio_trigger.c and candidatebuilder using
authenticated SDK header;176Cbytes/env192 at10205fb4, SHA
d297ea3341d8fef9496991b17e0644d3101b917ba29c18a1bda394c87721b2a4.
-fno-jump-tables avoids stock tablepullthrough; original table still retained
in hybrid and not yet reclassified. Trigger candidate unregistered/pending
decodedqualification. Next interpreter stockjmp/table,sourcebranches,20byte
frame/helpercalls/portreject/MMIO/storeorder. No liveprocesses; last613-test
package remains latestverified. Fullsource-onlygoalactive.

### GPIO trigger qualification/integration checkpoint

Previous turn progressed triggerC candidate and ISRsignature. Added
verify_gx8002_gpio_trigger.py:2,520 stock/source comparisons pass including
authenticated oldswitchtable, Cbranches, orderedrecord/MMIO/helpercalls,
callerclobbers and20-byteframe. Six target+three modeltests allpass.
Registered176-byte trigger routine (192envelope), tests added.
LIVE session30303 runs make -C g2 gx8002-source-candidate; log
 g2/build/gx8002-board/gpio-trigger-integration.log. Expected622tests.
Poll samehandle; no restart/inputedits. After success update count188/hash/
ownership, rebuildpackage/updateexpectedhash/rebuildverify/copy11notices.
Latestverifiedpackage613tests; original32-bytejumptable stillretained and
not source-owned. Helpercomposition/hardware remain separate. Fullgoalactive.

### GPIO disable candidate checkpoint

Previous turn progressed triggerqualification/integration. Polled session30303
twice; remainsLIVE, gpio-trigger-integration.log; expected622tests. No restart
or registered-input edits. Finish its package/count188/hash updates afterward.

Independent progress:reconstructed runtime_gx8002_gpio_disable_trigger.c and
builder.92Cbytes/env92 atpkgf600/runtime10206074, SHA
d90ff2fcb331b40941b032845634f56061b4dd9869c722c650b3a75727543bdb.
Port>=32reject; directionHIZ; ordered clears14,18,28,2c,24; callbackrecord
port255/callback0/private0. Added model_gx8002_gpio_disable_trigger.py reusing
trigger memorylayout; three modeltests pass. Candidateunregistered, decoded
qualification/8byteframe/helperclobbers pending. No hardwareclaim.
Latestverifiedpackage613tests; fullsource-onlygoalactive.

### GPIO disable decoded qualification checkpoint

Previous turn progressed disableC/model alongside liveenableintegration.
Added verify_gx8002_gpio_disable_trigger.py:1,225 stock/source comparisons,
all32validpins/rejectionboundaries/35seeds, ordered fiveMMIOclears and record
cleanup, directioncall/clobbers/8byteframe. Eight focusedtests pass. Report
pins both disablemodel and importedtrigger model. Candidate92bytes remains
unregistered pending active integration; no firmwarepayloadchange thisturn.

Session30303 remainsLIVE after samehandle polls; gpio-trigger-integration.log,
expected622tests. Keep inputs unchanged; finish count188/packagehash/ownership
updates when it exits, then integrate qualifieddisable. No hardwareclaim;
latestverifiedpackage613tests; fullsource-onlygoalactive.

### Trigger enable integration completed

Previous turn progressed disablequalification. Polled session30303 to exit0,
622tests pass. Updated count188/codec/hash; rebuilt macOS apple-clang package,
reviewed/updated expected hash, rebuilt/copied11notices/verified. Sessions30303,
44973,55085 terminal; no liveprocesses/hardwareaccess. Current188Cfunctions,
204Coccurrences,5architecture routines,40data regions,249replacementregions.
C12,042; assembly156; sourcedata2,790; metadata80; fill648; retained310,376.
Codec SHA585343154388afe22372388a6513227a1a398014b77595549464dec1628e68d0;
package SHAa2e676069c7fac0bd0dd00f2600f0687fc8280f9392f4075bd338fef08ae13df.
Size4,750,780;7,822placed/zero unresolved. Research reports updated.
Next integrate qualified92byte disabletrigger (1,225cases/eighttests).
Old32byte switchtable stillretained; helpercomposition/hardware and broader
opaque firmware recovery remain. Fullsource-onlygoalactive.

### GPIO disable integration and initialization recovery

Previous turn progressed622-test package. Registered qualifieddisabletrigger
and eighttests. LIVE session52159 runs make -C g2 gx8002-source-candidate,
log gpio-disable-trigger-integration.log; expected630tests. Pollsamehandle,
keep registeredinputs stable. After success count189/hash/ownership/package
rebuild andverify/notices. Lastverifiedpackage622tests.

Independent progress:GPIOinit atf65c/runtime102060d0 recoveredC, authenticated
SDKrelocation confirms gate(module4,1), thenwritea0001034zero, return0.
24Cbytes identicalstock SHAa94629e7633a0e3d039e4a24a3f9856f9246d423152e2e250caaa885f584c05c.
New builder/verifier/source/test files namedgpio_initialize/gpio-initialize.
Full straight-line structuralproof and4tests pass; gateABI declaration matches
existingvoid(unsigned,unsigned). Initunregistered; nextintegrationafterlive
build. Fullsource-onlygoalactive; hardware andremainingopaquecontent open.

### SPI device-list attribution checkpoint

Previous turn progressed disableintegration/initrecovery. Polled live52159
multiple times; remainsLIVE, log gpio-disable-trigger-integration.log,
expected630tests. No restart or registeredinputedits. Finish count189/package
updates after completion; initialization24-byte candidate is qualifiedqueued.

Independent progress: matched stockf674 instruction/padding prefix16bytes
against SDKdrivers_lib/spi/device.o .text.device_list_init. Authenticated blob
d6709f8990a19d8e08ebe21ec9059d7f580fa15b, objectSHA
b882f90d25260a0981f480f547b9212888558febffab0a0b9e1d97c01d389fec.
Saved gx8002-device-list-attribution.json; no sourceadmission. Stockliteral
20027ad0 initializes g_spi_head and g_sflash_head at+8. SDKdevice.h declares
void device_list_init(), spi_register_master(struct spi_master*), and
spi_flash_register_master(struct sflash_master*); structs in driver/spi.h.
Adjacentf688 appears registration, but needs full attribution/qualification.
This opens next subsystem after GPIO. Latestverified622tests; fullgoalactive.

### SPI device-list initializer C checkpoint

Previous turn progressed authenticated SPI attribution while disablebuild
live. Session52159 polled twice and remainsLIVE; expected630tests/log
gpio-disable-trigger-integration.log. No restart/inputedits. Finishpackage
updates when terminal; GPIOinit24bytes remainsqualifiedqueued.

Added runtime_gx8002_device_list_init.c, builder/verifier/three passingtests.
20Cbytes identicalstock atf674/runtime102060e8, SHA
4e7e5e95824bfc057f5be66b2f41e88cbc8c32e5d74c12e7d8ec2d03816b791b.
Four ordered volatilepointerstores form heads20027ad0 and20027ad8; complete
straight-line structuralproof/leafABI. No upstreamobjectpullthrough.
Qualifiedunregistered, nextbatch with GPIOinit afterliveintegration.
SPIregistrationf688 still needs fullrecovery. Latestverified622tests;
fullsource-onlygoalactive.

### GPIO disable integration completed

Previous turn progressed SPIinitializer. Polled52159 to exit0:630tests pass.
Manifest count189/codec/hash updated; macOS apple-clang package rebuilt with
reviewed new hash,11notices copied, verify-artifacts passed. Sessions52159,
97024,99570 terminal; no liveprocesses/hardwareaccess. Current189Cfunctions,
205Coccurrences,5architecture routines,40data regions,250replacementregions.
C12,134;assembly156;sourcedata2,790;metadata80;fill648;retained310,284.
Codec SHA2ef9ef908e046ba7fcbe27d07b947a491c4e893e972863a689d1dafd6500fc0b;
package SHA3224baf653f0c9b526aae6b0e341636ff8904c551b1461f888df8ce0d23d7b24.
4,750,780bytes,7,822placed,zero unresolved. Research reportsupdated.
Next batch qualifiedGPIOinit24bytes/fourtests and SPIlistinit20bytes/three
 tests, both byte-identicalstock and unregistered. Then SPIregistration
recovery from authenticateddevice.o/header. Fullsource-onlygoalactive.

### Initializer batch integration and SPI registration candidate

Previous turn progressed630-test package. Registered GPIOinit24bytes and
SPIlistinit20bytes plus7tests. LIVE session56402 runs
make -C g2 gx8002-source-candidate, log gpio-device-init-integration.log;
expected637tests. Keep inputs stable/pollsamehandle. After success count191,
ownership update/rebuildpackage metadata/verify (payloadhashes expectedunchanged).

Independent progress:reconstructed SPIregistermaster C atf688/runtime102060fc,
92bytes/env104, SHAbddd3b535a23ea53957073abde1498c0e354ab800fb12798e766756f5e44273d.
Uses authenticated spi/list/types headers; resolved legacytypedef conflict by
using SDKtypes and compileruintptr, systemincludes suppressunusedSDKparameter;
generated string.h is declarationonly forunusedinlinehelper, no memsetstub.
Candidate unqualified/unregistered. Semantics:NULL-19; zeroCS/negativebus-22;
appendmaster; bindfirsteligibleflash; snapshotnextbefore sentinelcheck.
Next independentlistmodel anddecodedverification. Latestverified630tests;
fullsource-onlygoalactive. No hardwareaccess.

### SPI registration independent model checkpoint

Previous turn progressed initializerbatch and SPI C candidate. Polled56402;
remainsLIVE, gpio-device-init-integration.log, expected637tests. Don't restart
or edit registeredinputs; finish count191/ownership/package metadata update
and verification once terminal. Lastverified630tests.

Added model_gx8002_spi_register_master.py and five passingtests. Models valid
circular lists (old0..3,flash0..8), ordered word/byte reads and insertion,
firsteligibleflashbinding, snapshotnext before sentineltest. Tests cover
validationorder/nonemptyappend/firstonly/bus+CSfilter/sentinelread. Next
stock/C interpreter against full trace/words and leafABI. Candidate remains
92bytes/env104 and unregistered. Fullsource-onlygoalactive.

### SPI registration decoded qualification checkpoint

Previous turn progressed SPI independentmodel. Added verifier
verify_gx8002_spi_register_master.py:2,593 decodedstock/Ccases pass ordered
reads/writes, firstmatch binding, validation andleafABI. Tenfocusedtests pass.
Mutationtest initially used wrongPC; corrected to target actual tail-load
instruction. Candidate92Cbytes/env104 remainsunregistered. No firmwarepayload
change or hardwareclaim. Registrymalformation/concurrency remainexcluded.

Session56402 remainsLIVE afterpolls; gpio-device-init-integration.log expected
637tests. Keep samehandle/inputs; finish count191/ownership/package metadata
rebuild/verify when terminal. Latestverified630tests. Next integrate qualified
SPIregistration after currentbatch. Fullsource-onlygoalactive.

### Initializer batch completed; SPI registration integrating

Previous turn progressed SPIdecodedqualification. Session56402 exited0;
637tests pass. Count191/ownership reportsupdated. GPIOinit+SPIlistinit add44C
bytes identicalstock; codec remains2ef9ef908e046ba7fcbe27d07b947a491c4e893e972863a689d1dafd6500fc0b.
Full macOS apple-clang rebuild/copy11notices/verify succeeded, packageSHA
3224baf653f0c9b526aae6b0e341636ff8904c551b1461f888df8ce0d23d7b24.
191Cfunctions/207occurrences,5architecture,40data,252regions. C12,178;
assembly156;data2,790;metadata80;fill648;retained310,240.
Sessions56402/96518terminal. Registered qualifiedSPIregistration and10tests;
new live build handle is recorded by following checkpoint. Expected647tests.
Do not change registeredinputs while it runs. Next SPIflashregistration
recovery/composition; full source-onlygoalactive.
LIVE session2900:make -C g2 gx8002-source-candidate, log
 g2/build/gx8002-board/spi-register-master-integration.log.
Poll samehandle; expected647tests. After success count192/hash/ownership,
package rebuild/updatehash/rebuildverify/notices. Lastverified637testpackage.

### DesignWare SPI attribution/cleanup checkpoint

Previous turn progressed637-test package and SPIregistrationintegration.
Polled2900; remainsLIVE, spi-register-master-integration.log, expected647tests.
Keep samehandle and registeredinputs stable; finish count192/hash/package
update after completion. Lastverified637tests.

Independent progress:corrected next-target assumption. Stockf6f0 is
DWcleanup, notflashregistration; exact12byte match authenticated
spi_master_v3.o (blob600d763a219007e2af7b5006989d44984abf0861,
SHA02ed04414f74b393f6703aab6a6e0484b18d30c02b74a11ecc5fe856e02684ae).
IRQf6fc exact32byte match, setupf71c prefixonly. AttributionJSONsaved.
SPIflashregistration10byteprefixnotfound (not an absenceproof).
Added DWcleanup C/builder:12byteidenticalstock SHA
7106625a18c7c6cd2c6b3da75c7b4641c5283be27d6481ab3601b09a8b399482.
Device->master->driver_data(+24)->registers(+4), storezeroatregs+8.
Candidateunqualified/unregistered; privateprefixotherfieldunknown. Next
structural/targetproof; nohardwareclaim. Fullsource-onlygoalactive.

### DW cleanup structural qualification checkpoint

Previous turn progressed DW attribution/cleanupC. Added
verify_gx8002_dw_spi_cleanup.py and4passingtests. Full six-instruction exact
contract establishes pointer-read offsets0/24/4, thenstorezero+8, leafABI;
12bytepayload identicalstock. Candidatequalifiedunregistered; validpointer
chains required. IRQf6fc contains conditionalabsolute reads38/3c, not assumed
controllerrelative; flagforunderstandingbeforebehaviorchanges.

Session2900 polledsamehandle remainsLIVE, spi-register-master-integration.log,
expected647tests. Do not restart/changeinputs. Finish count192/package/hash
updates onterminal; DWcleanup readyafter. Latestverified637tests;
fullsource-onlygoalactive.

### SPI registration package verified; DW cleanup integrating

Session2900 exited0: 647 integration tests pass. macOS apple-clang full package
build and verify-artifacts succeeded (sessions76175/90308 terminal). Count192
Cfunctions/208 occurrences;253 regions,5 architecture routines,40 data regions.
C12270,assembly156,data2790,metadata80,fill660,retained310136.
Codec SHA4e4c38c12e6313b025bae453ee0c903d8be68a34d3b28ce0c9181845a9dcb491.
EVENOTA4750780bytes SHA070a23d06fee16cff7aee90d24eee6e8ffc0cf58943afa0bae9d57c090dd5fa2.
7822 placed flash regions, zero unresolved; all11notices copied. Source-only
and hardware qualification remain false. Manifest/research report updated.

Qualified DWcleanup now registered with4tests. LIVE session6200 runs
make -C g2 gx8002-source-candidate; log
 g2/build/gx8002-board/dw-spi-cleanup-integration.log.
Expected651tests. Do not restart or edit registered inputs while running.
On success update count193/ownership, rebuild package metadata and verify;
cleanup bytes are identical stock, so payload hashes should remain unchanged.

Independent analysis analyze_gx8002_dw_spi_setup.py now relocates the
authenticated SDK object strictly for comparison: all116 bytes match stock
f71c..f790 (runtime10206190). SHA
b25118f489e60485455c13aec8b304efd82a5275a7dc91eeddacb4e3cefe9d79.
Bindings gx_clock_get_module_frequence10025210, bss20027ae0.
Initial local-symbol ENTRY approach discarded section; corrected to KEEP.
Attribution JSON saved, no firmware admission. Next reconstruct setup C and
qualify decoded transactions/ABI, keeping IRQ absolute reads38/3c unresolved.
Full source-only goal remains active; no hardware flashed.

### DW setup C reconstruction checkpoint

Previous turn was progress:647-test package verified and DWcleanup registered.
Polled session6200 repeatedly this turn: remainsLIVE, same cleanup-integration
log, expected651tests. Keep registered inputs stable and finish count193/package
metadata rebuild/verify when terminal. Lastverified package remains647tests.

Added runtime_gx8002_dw_spi_setup.c and native builder/candidate report using
SDK spi_device types and recovered16byte state. Full setup attribution was
already proven. Candidate now120bytes (original116), SHA
77afed0e770ef9340a2bee0d3adb8a56063ccde5531a86b2bca8c57a4b456db9.
First132byteversion reduced by shortening divider temporary lifetimes;
flag experiments did not improve120, restored ordinaryOs/no-jump-tables.
Unregistered/unqualified; no firmware change. Source note records exact
operation order/defaults/error behavior and next decoded verification needs.
Need resolve4byteoverrun without dropping semantics, then independent model
and ABI qualification. Fixedstate20027ae0; clockhelper10025210(module14).
No hardware claims. Source-only goal active.

### DW setup independent model checkpoint

Previous turn progressed setupC. Session6200 polled authoritative handle twice
this turn, remainsLIVE; cleanup-integration.log expected651tests. Keep same
process/registered inputs. Lastverified647-test package; finalize count193 and
package metadata/verify on terminal. Full source-onlygoalactive.

Added model_gx8002_dw_spi_setup.py and6passing modeltests. Independent rational
ceiling/evenround divider, exact transaction order, busy-state initial writes,
existingstate, defaults, livehelper changes, unsignedoverflow, zeroafterhelper
exclusion. Firsttest invocation exposed Python3.9 annotation issue; fixed with
futureannotations; rerunpassed. No decodedtargetqualification claimed yet.
-Oz sizeexperiment same120bytes asOs; restoredOs andrebuiltreport. Candidate
still4bytesover original116, unregistered; no firmwarepayloadchanges. Next
implement decodedstock/C runner againstmodel and resolve placement/size while
preserving fullbehavior. docsnote explicitlyrecords ffffffff/1 dividerwrap0.

### DW setup decoded verification checkpoint

Previous turn progressed independentmodel. Session6200 polled multiple times,
remainsLIVE (cleanup-integration.log expected651). Do not restart; finish
count193/package metadata rebuild/verify on terminal. Latestverified647tests.

Added verify_gx8002_dw_spi_setup.py:17,280 stock/Ccases pass independenttrace,
return andABI including helperclobbers, modelhelper statechanges. Fullrelocated
SDKoracle matchesstockfirst. Candidate remains120bytes/116slot, sourceadmitted
false/unregistered. O1 experiment124bytes; restoredOs120. No firmwarechange.
Added5target/mutationtests, togetherwith6modeltests all11pass. Initial standalone
unittest lacked toolmodulepath; reran with PYTHONPATH=tools (repo convention).
Targetmutations test wrongspeed,module,dividerstore,callee-savedclobber.
Reports/docs saved. Needresolve4byteoverrun and finishmodelhash/reportpinning
before admission. Framepush/pop abstractfixed12bytes; no hardwareclaims.
Goalactive, no blocker requiringuserinput.

### Setup evidence pinning checkpoint

Previous turn progressed decodedverification. Session6200 polled twice and
confirmedLIVE this turn, same cleanup-integration.log expected651. Do not
restart. Latestverified647-test package; finalize193metadata/package onterminal.

Verifier now records SHA256 of itself, independentmodel, builder and SDK
attribution script so reviewed evidence can detect tool/modelchanges. Restored
original120byteOs C after bounded compiler-layout sweep (none below120),
alternate quotient rounding124, ordinarybyte-read experiment120. No behavior
removed or firmwarechanges. Final stable rerun session12703 exited0 with
17,280cases; all11focusedtests pass. Earlier23437 terminal, no othernewlivejobs.
CandidateSHA remains77afed0e770ef9340a2bee0d3adb8a56063ccde5531a86b2bca8c57a4b456db9.
Need placement solution or further justifiedCsize improvement, then admission;
source-onlygoalactive. Avoid continuing blind compilerflag sweeps.

### Cleanup integration passed; package rebuild and IRQ source checkpoint

Previous turn progressed evidencepinning. Session6200 exited0 this turn;
651tests pass. Actualbuildreport193functions/209Coccurrences,254regions;
C12282,asm156,data2790,metadata80,fill660,retained310124. CodecSHA unchanged
4e4c38c12e6313b025bae453ee0c903d8be68a34d3b28ce0c9181845a9dcb491.
Manifestcount193updated. LIVEsession46484 apple-clang fullpackage build,
codec-source-experimental-build.log. Mustfinishcopy11notices/verify-artifacts
and researchreport/MDcountupdates. Latestverifiedpackage still647tests;
packageSHA expected unchanged070a23d06fee16cff7aee90d24eee6e8ffc0cf58943afa0bae9d57c090dd5fa2.

Setup controlmask written as mask-before-shift (clearer, same120compiledbytes).
Halfdividerexpression124experiment reverted. Stable17,280cases reranpass
(session1019terminal). Setupstillunregistered;4bytesoversize.

Added runtime/build DWspiIRQcandidate: exact observedstatus+30 thenconditional
absolute38/3creads, return0. Firstliteralpointer version arrayboundscompiler
error; externvolatileobjects/linkerbindings resolvewithoutwarning suppression.
40Cbytes/32slot, SHAe4b0a647cf4c87b4688f92b10dd1b01436e70d6d366c41778ca3a9cbfd8e4ced.
StockSHA41f80726223e7f56079c5563cb09ecbf36cbb098a9c2c2ceff98be9dcb9f83f7.
Unregistered/unqualified; hardwarelowaddressmeaning stillunresolved. Source
note added. Needplacement/decodedproof; no firmwareadmission. Fullgoalactive.

### IRQ decoded proof; cleanup package artifact verification running

Previous turn progressed651integration/IRQsource. Session46484 exited0:
fullmacOSpackagebuild succeeded. Copied11notices. LIVE session70358 runs
verify-artifacts, log codec-source-experimental-verify.log. Onsuccess update
research buildreportJSON/MD to193functions/209occurrences/254regions,
C12282,retained310124; othercounts/hashesunchanged. Lastverifiedpackage remains
647until70358terminalsuccess;651integration alreadyverified. Do not restart.

Added verify_gx8002_dw_spi_irq.py:4644decodedstock/Ccases passorderedreads,
conditionalmasks, retainedsnapshot, return0 andleafABI. Fivefocusedtests pass
including wrongrelativeaddress,mask andcallee-savedmutations. Session60476
terminalsuccess. Sourceadmittedfalse40bytes/32slot; lowaddressmeaningunresolved.
Reporthashesverifier/builder. docsupdated. Goalactive; nohardwareclaims.

### Cleanup package verified; fitting IRQ integrating

Previous turn progressed IRQproof. Session70358 exited0,651-test macOSpackage
artifactverificationpassed SHA070a23d06fee16cff7aee90d24eee6e8ffc0cf58943afa0bae9d57c090dd5fa2.
ResearchreportJSON/MD updated193functions/209occurrences/254regions,
C12282,retained310124; othercounts/hashesunchanged. No otheroldlivejobs.

ResolvedIRQsize: literalvolatile lowaddresses plus candidate-local
-fno-delete-null-pointer-checks --param=min-pagesize=0 compile32bytes. Firstflag
alone stillboundsdiagnostics; GCC--help=params identifies min-pagesize warning
assumption. Otherwarningsremainerrors. NewC SHA
770352405f41c74a6f1c1c3c213bb5167dd5da93c72116cfcc7b0fff2aeac6be.
Regenerated4644decodedcases and5tests pass. Verifier acceptsstandardargs,
exportsrow/artifact and admitsqualifiedC; hardwarequalificationfalse and
lowaddressmeaningstillunresolved. RegisteredIRQplus5tests.
LIVE session88586 make -C g2 gx8002-source-candidate; log
 g2/build/gx8002-board/dw-spi-irq-integration.log, expected656tests.
Keepregisteredinputs stable; onterminalsuccess update194/counts/hash/package
rebuildpin/verify/notices. Latestverified651testpackage. Setupstill120/116slot,
17,280cases and11tests, unregistered. Goalactive.

### Quick-transfer full upstream attribution checkpoint

Previous turn progressed fittingIRQ/integration. Session88586 polled confirmed
LIVE; dw-spi-irq-integration.log expected656tests. Keepregisteredinputsstable;
finish194/hash/packagepin/build/verify when terminal. Latestverified651package.

Added analyze_gx8002_dw_spi_quick_transfer.py: full634byte stockmatch atf790,
runtime10206204, SHA7327bfd821913d05255020723c44cf51e29af05fac10e878efec9c6a645f9d62.
AuthenticatedsameSDKobject, exactly2relocations at24/100 toclockgate10025080.
RemovedunneededBSSbinding copiedfromsetup; rerunfullidentitypassed. Comparison
only, nofirmwareprovider. Researchnote records initial state/clock/listfacts,
including surprising busy path clearingprivate10/14 andreturn0, anderror-22
shutdown. NeedfullCtransfer reconstruction/interpreter inclpostincrementops.
IRQintegrationlive, setup120/116stillunregistered, fullsource-onlygoalactive.

### Transfer width exhaustive decoding checkpoint

Previous turn progressed634byteupstreamattribution. Session88586 polledsame
handle confirmedLIVE; expected656tests, dw-spi-irq-integration.log. Preserve
registeredinputs andfinish194/package steps onterminal. Latestverified651.

Added analyze_gx8002_spi_transfer_width.py andJSON:256decodedinputcases pass
independentarithmeticmapping. Defaults0->8bits/1byte;1..8width1,9..16width2,
17..32width4(remap24bits),33..248width5..31(no dataaccessbranch),249..255width0
(laterdivisionhazard). Analysisonly,nofirmwareemission. DocsrecordTXstatus
polling andRXFIFOlevel/postincrement behavior; fulltransferC/MMIOmodel pending.
Fullsource-onlygoalactive. No hardware/completefunctionalityclaim.

### Complete SPI object relocation / private layout checkpoint

Previous turn progressedwidthdecoding. Session88586 polled confirmedLIVE;
expected656tests, dw-spi-irq-integration.log. Keepinputs; finish194/package
when terminal. Latestverified651macOSpackage. Fullsource-onlygoalactive.

Added analyze_gx8002_dw_spi_probe.py: all5completeSDKsections matchstock after
linking comparison-only, including268byteprobe atfa0c. Sourceprivate-layoutdoc
maps BSSstate20027ae0/master20027af0/private20027b14, controllera3000000,
TX/RXdepth8/c fromthresholdprobes, currentmessage10/transfer14/buffer18/len1c,
width28; fields20broadermeaning,24 andtailpadding remainunresolved. Probe
thresholdedge257mismatch->0/all256success->258 documented. Next fullprobeC or
transferC withlayout; lowIRQabsolute38/3c meaningstillnotexplained. Nooracle
byteslinkedfirmware; nohardwareclaim.

### SPI probe C candidate checkpoint

Previous turn progressedcompleteobject/private-layoutproof. Session88586
polled confirmedLIVE thisturn, dw-spi-irq-integration.log expected656. Preserve
registeredinputs; finish194/hash/packagebuild/verify when terminal. Latest651.

Added runtime_gx8002_dw_spi_probe.c andnativebuilder:256bytesfits268stockslot
fa0c/runtime10206480, SHAafc184fb1f473b55ed519f09446e8c9d396ddc424025079f3416200eadce2354.
StockSHAb9faf578c98cda7f86a6e621fe6c8a7ca6153dfe5e9710c3f9b7412495f79e63.
SDKmastertypes/recoveredprivateprefix; clock/FIFOprobe/drain/master/IRQsetup
sequence. Retainsfinalthresholdpointer; noinventedtimeouts. Unregistered and
unqualified; next independentmodel/decodedtrace+ABI inclFIFOreadbackoutcomes.
Docsnoteadded. Fullsource-onlygoalactive; hardwareunproven.

### IRQ656 integration passed; probe model added

Previous turn progressedprobeC. Session88586 exited0:656tests pass.
Actual194functions/210Coccurrences/255regions, C12314,asm156,data2790,metadata80,
fill660,retained310092. CodecSHA
1f232a64173c50c25423b0730a11cac8d4cc8ec434851b7059a84b95116d98fd.
Manifest194/providerupdated. Firstpackagebuild69348 exited1 expectedpinmismatch:
observede1040e18c550beee753582528a23166eaf69ffc48524f1cbd7741b1a0a0ec233.
Reviewednewhash/pinned. LIVE session29215 fullapple-clangpackage rebuild;
codec-source-experimental-build.log. Onsuccesscopy11notices/verify-artifacts,
thenresearchreportJSON/MDupdate194counts/hashes. Latestverifiedpackage651.

Added model_gx8002_dw_spi_probe.py and5passingmodeltests coveringordered
transactions,depthattempts/boundaries,bypass,drain/busy andstatusscriptfailure.
No decodedtargetproofyet; probe256/268 remainsunregistered. Nextprobeinterpreter
againstindependentmodel. Goalactive; hardwareunproven.

### Probe944 decoded cases; package verification running

Previous turn progressed656integration/probemodel. Session29215 exited0 full
macOSpackage build withSHAe1040e18c550beee753582528a23166eaf69ffc48524f1cbd7741b1a0a0ec233.
Copied11notices; newartifactverificationhandle recorded below. Need finishverify
and researchreportJSON/MD194counts/hashupdates. Latestverifiedpackage651.

Added verify_gx8002_dw_spi_probe.py:944decodedstock/Ccases pass independent
orderedtrace/ABI, everyFIFO mismatch2..257, existingdepths, allsuccess/drain/busy.
Session58294 terminalsuccess. Fixed12byteframe/helperclobbers modeled; nohelper
statemutation. Unregistered/sourceadmittedfalse pendingmutationtests/report
hashpins. C256/268unchanged. Goalactive; nohardwareclaim.
LIVE session97962 verify-artifacts; codec-source-experimental-verify.log.
Pollsamehandle; on success finalize194 researchreport/counts/hashes.

### IRQ package verified; qualified probe integrating

Previous turn progressed944probeproof. Session97962 exited0 macOSartifactverify
SHAe1040e18c550beee753582528a23166eaf69ffc48524f1cbd7741b1a0a0ec233.
ResearchJSON/MD updated194functions/210occurrences/255regions,C12314,
retained310092,codec1f232a64173c50c25423b0730a11cac8d4cc8ec434851b7059a84b95116d98fd.
Latestverified656-testpackage. Allolderhandles terminal.

Added6probemutation/targettests, combined5modeltests all11pass. Pinverifier,
model,builder,attributionhashes; standardartifact/rowexport. Session25714 exited0
944decodedcases. Probequalified/registered256Cbytes/268slot. No hardware/helper
compositionclaim. LIVE session93551 make -C g2 gx8002-source-candidate,
log g2/build/gx8002-board/dw-spi-probe-integration.log expected667tests.
Keepregisteredinputsstable. Onterminalsuccess update195/counts/hashes/package
pin/build/verify/notices. Setup120/116stillunregistered; fulltransferCpending.
Goalactive.

### Full SPI transfer C candidate checkpoint

Previous turn progressedprobequalification/integration. Session93551 polled
confirmedLIVE; expected667tests,dw-spi-probe-integration.log. Keepregistered
inputs; finish195/hashes/packagewhen terminal. Latestverified656package.

Movedfromsetupsizeissue to fulltransferC using recoveredlayout. Added
runtime_gx8002_dw_spi_quick_transfer.c andnativebuilder:602bytesfits634slot
f790/runtime10206204, SHA4162ba4c7d97d11e811baac421bde9f978563873e3dde5e5059ba2b358a574c6.
IncludesTX/RX/controller/config/list/alignmenterror/clockcleanup. Candidate
unregistered/unqualified; needsindependentMMIOmodel/decodedtrace+ABI especially
volatileevaluationorder, FIFOprogress andarithmetic. Setup120/116unchanged.
No hardwareclaim; no firmwarechangesfromtransfercandidate. Fullgoalactive.

### Transfer access-order corrections checkpoint

Previous turn progressedfulltransferC. Session93551 polled confirmedLIVE;
expected667tests,dw-spi-probe-integration.log. Keepinputs; finish195/package
when terminal. Latestverified656package. Fullgoalactive.

Inspectedtransfercandidate vsstock and fixedtwo concretevolatileorderingbugs:
loadprivatecontrollerpointer beforeconfig.transfer_mode read, and before
privatecleared_word store. Recompiled602bytes, SHA
0b4d660a735fc0a65583db96567d17f5d5a64d394c62377835ce469f0b1e59d2.
Disassembly confirmscorrectedsequence. Candidateunregistered/unqualified;
next fullindependentMMIO/transactionmodel anddecodedinterpreter, including
TX/RX/alignment/busy/emptylist. No firmwareadmissionfrominspectionalone.

### Transfer lifecycle scoped verification checkpoint

Previous turn progressedaccess-orderfixes. Session93551 polledconfirmedLIVE;
expected667tests,dw-spi-probe-integration.log. Keepregisteredinputs; finish195
package steps when terminal. Latestverified656. Goalactive.

Added independent model_gx8002_spi_transfer_lifecycle.py and decodedrunner:
4busy/emptyliststock/Ccases pass exacttrace,zero return,28byteframe/ABI.
Threefocusedtests added (correctpaths/wrongmessagewrite/wrongclockmodule).
Scopedreportexplicitlysourceadmittedfalse; noFIFO/nonempty/alignmentproofyet.
No transferCchanges/firmwareadmission. Next expand model to nonemptytransfers.

### Transfer alignment model checkpoint

Previous turn progressedlifecycleproof. Session93551 polled confirmedLIVE;
expected667tests,dw-spi-probe-integration.log. Preserveinputs; finish195package
onterminal. Latestverified656package. Fullgoalactive.

Added model_gx8002_spi_transfer_alignment.py and4passingtests: nonemptysetup
throughmisalignmentshutdown,TX/RXbuffer,dividertruncate/clamp,return-22. Scope
explicitlyrejectsalignedcasesrequiringFIFOmodel. Next extenddecodedrunner with
byteaccess/division/controlinstructions andcomparealignmenttraces; fullFIFO
stillpending. No transferfirmwareadmissionorhardwareclaim.

### Transfer alignment decoded proof checkpoint

Previous turn progressedalignmentmodel. Session93551 polled confirmedLIVE;
expected667tests,dw-spi-probe-integration.log. Keepregisteredinputs; finish195
package when terminal. Latestverified656package. Goalactive.

Extended lifecycleexecute optionalmodel andbyte/arithmetic/division/conditional
instructions. Addedverify_gx8002_spi_transfer_alignment.py:280stock/Ccases pass
TX/RX,widths,misalignedlength/buffer,dividerboundaries. Session89283terminal0.
Reran4lifecyclecases and7focusedtests afterinterpreterchanges. FullFIFOaligned
processing/data/waits stillunqualified; sourceadmittedfalse. CandidateCunchanged
602bytes, nofirmwareadmission. NextalignedFIFOmodel.

### Aligned TX independent model checkpoint

Previous turn progressedalignmentdecodedproof. Session93551 polledconfirmed
LIVE; expected667tests,dw-spi-probe-integration.log. Preserveinputs; finish195
packagewhen terminal. Latestverified656. Fullgoalactive.

Extractedsharedsetup_trace fromalignmentmodel preservingerrorwrapper. Added
model_gx8002_spi_transfer_tx.py withalignedTX1/2/4bytepayload, littleendiandata,
FIFOspace/backpressure scripts andreadiness/busy polling. Fourmodeltests pass,
includingfullFIFOthenprogress andincomplete-scriptfailure. Alignmentmodel4tests
stillpass; reran280decodedalignmentcases afterrefactor. TXdecodedreplaypending,
RXmodelpending. No transferadmission/hardwareclaim; candidateunchanged602bytes.

### Probe667 integrated; TX replay found/fixed byte read order

Previous turn progressedTXmodel. Session93551 exited0,667tests pass. Actual195
functions/211Coccurrences/256regions,C12570,asm156,data2790,metadata80,fill672,
retained309824; codec0312093c3824b11068b0fd29b51d4d52669a9a24dfbc15730e0100063839b99b.
Manifest195/providerupdated. Firstpackage99152 expectedhashfailure:observed
32b9da8d7190c7eccfc6cb29bb347cd20a19436090e999bdd70159cdd0f12272; reviewed/pinned.
LIVE session90495 fullmacOSpackage rebuild,codec-source-experimental-build.log.
Onsuccesscopy11notices/verify; update researchreportJSON/MD195counts/hashes.
Latestverifiedpackage656. Nootheroldlivebuilds.

AddedTXdecodedverifier andindexedloads/min.s32/mula/and instructions. First
replay71538 failedCbytebufferreadbeforecontrollerpointer. FixedCbytebranch
explicitvolatilebufferread afterpointer; rerun70478 passed12TXcases (3widths,
FIFOpressure,readinessdelays). Still602bytes SHA
964b5afa5ff89a937beda755efe5e1558d669c00643b24796e6ee25cd19a5e8b.
Reran280alignment/4lifecycle/11focusedtests afterfix. TXscope12only; RX/multiple
transfers/hardware remainunqualified. No transferadmission. Goalactive.

### RX independent model checkpoint

Previous turn progressed667integration/TXdecodedfix. Session90495 polled
confirmedLIVE; macOSpackage rebuild logcodec-source-experimental-build.log.
Expectedpin32b9da8d7190c7eccfc6cb29bb347cd20a19436090e999bdd70159cdd0f12272.
Onterminalsuccesscopy11notices/verify thenresearchJSON/MD195counts/hashes.
Latestverifiedpackage656;667integrationpassed. No otherliveprocessesknown.

Added model_gx8002_spi_transfer_rx.py and5passingtests for1/2/4bytestores,
RXchunking,emptyFIFOthenprogress,overrun/missingdatafailures. Initialmodel
rejectsoversupply/invaliddepth; decodedRXreplaypending. TX12decodedcasespassed
previously, transfer602bytecandidateunchanged/unregistered. Next interpreter
postincrementstores andRXdecodedcomparison, thenmultitransfer. Goalactive.

### Probe package verified; expanded TX/RX replay checkpoint

Previous turn progressedRXmodel. Sessions90495/15143 exited0 fullmacOSpackage
build/verify. Latestverified667-testpackage,195functions/211occurrences/256regions.
C12570,asm156,data2790,metadata80,fill672,retained309824. Codec
0312093c3824b11068b0fd29b51d4d52669a9a24dfbc15730e0100063839b99b;
package32b9da8d7190c7eccfc6cb29bb347cd20a19436090e999bdd70159cdd0f12272.
Copied11notices,researchJSON/MDupdated. No livejobsremainingknown.

Extendedinterpreter min.u32/signedcmplt/postincrementstores. AddedRXdecoded
verifier;initial9pass thenexpanded160RX/160TXcase matrices. Bothpassed
session29032terminal0. Widths0/1/8/9/16/17/24/32,counts0/1/2/3/17,depths2/16,
delayed/immediateFIFO. 16focusedtests pass. Candidate602bytesunchanged,
sourceadmittedfalse; multi-transfer messages/helpermutations/unsupportedinputs
remainincomplete. NextcomposeTX/RX/zero/error transferswithinonemessage and
qualify repeatedstate/listreads; setup120/116stillunregistered. Fullgoalactive.

### Mixed transfer message replay checkpoint

Previous turn progressed667packageverification/expandedRXTX. No livejobs.
Latestverified667macOSpackage195functions; unchangedpayloads thisturn.

Added model_gx8002_spi_transfer_message.py anddecodedverifier:252two/three
transfer combinations passstock/C(TX,RX,zero,error). Keepsoneclockpair,
remapsdistinctnodes,stopsfirsterror. Tightenedbuffers todisjointregions soRX
writes cannotinvalidate scriptedlaterTXdata; aliasedbuffers explicitlyrequire
sharedmemorymodel. Rerun252pass and3modeltests pass. Sourceadmittedfalse,
transfer602unchanged. Nextsharedmemory/alias andhelperstateeffects/qualifying
limits beforeadmission; setup120/116stillpending. Fullgoalactive.

### Shared RX/TX buffer replay checkpoint

Previous turn progressed252messagecomposition. No livejobs; latestverified667
macOSpackage195functions unchanged.

Extendedmessage model opt-in shared_buffers withbyte-memory initializedfromTX
data andupdatedfromRXstores. Sharedrangesrestrictedawayfrommetadata, conflicting
initialTXbytesrejected. Added18full/partialoverlap RX->TX cases across3widths;
all270stock/Cmessagecases pass(session36483terminal0). Fivefocusedmessage
modeltests pass includingexactoverlapbytes. No transferCchange/admission.
Next helpercomposition/stateeffects andfinalqualification/reportpins/mutations;
setup120/116stillpending. Fullgoalactive; hardwareunproven.

### FIFO target mutation checkpoint

Previous turn progressedshared-bufferreplay. No livejobs; latestverified667
macOSpackage195functions unchanged. Addedtest_gx8002_spi_transfer_fifo_target.py,
5passingmutations:RXwidth/destination/FIFOcount,TXmin-space/readinessmask.
Session22888terminal0. Transfercandidateunchanged/unregistered.

Inspectedexisting runtime_gx8002_platform_gate.c andverify_gx8002_platform_gate.py:
upstream_clk_set_high_gate/_clk_set_all_gate, separatelyqualifiedlookupmodeled.
Relevantupstreamheaderarch/soc/grus/include/clk_priv.h lines522/611. Nextcompose
transferclockcalls withqualifiedgate/lookupbehavior beforefinalqualification.
No speculativeclaimthathelpercompositionalreadyproven. Fullgoalactive.

### Transfer/gate boundary composition checkpoint

Previous turn progressedFIFOmutations. No livejobs; latestverified667package
195functions unchanged. Addedoptionalclock_hook totransferinterpreter and
verify_gx8002_spi_transfer_gate_composition.py:36combinations/72decodedgatecalls
pass(stock/Couter×stock/Cgate×TX/RX/error×3registersources). Gateoracle/allowed
clockwriteschecked. No metadatawrites observed. Tenlifecycle/FIFOtests pass,
includinghookinvocation/failurepropagation.

Explicitlimits:gateownabstractstack,modeledlookup/table; transfercallerclobbers
modeled. Notsharednestedstack orphysicalclockproof. Reports/docsrecordlimits.
Transfer602Cunchanged/unregistered; next qualificationaggregator/evidencepins
andremainingABI/unsupportedinputscope. Fullsource-onlygoalactive.

### Qualified transfer integrating checkpoint

Previous turn progressedgatecomposition. Aggregateverify_gx8002_dw_spi_quick_transfer.py
pins16evidencefiles andreruns874transfercases+36gatecombinations; candidate
identityconsistent602bytes. Session52755terminal0. All28focusedtests pass.
Explicitcontract/unsupportedinput/hardware/nestedstacklimitationsretained.
Registeredtransferand28tests. LIVE session53147 make -C g2 gx8002-source-candidate,
log g2/build/gx8002-board/dw-spi-quick-transfer-integration.log expected695tests.
Preserveallregisteredinputfiles whilebuildruns; nextfinish196counts/hash/package
pin/build/verify/notices onterminal. Latestverified667macOSpackage195functions.
Setup120/116stillunregistered. Fullsource-onlygoalactive; nohardwareclaim.

### Padmux getter source checkpoint

Previous turn progressedtransferqualification/integration. Session53147 polled
confirmedLIVE; expected695tests,dw-spi-quick-transfer-integration.log. Preserve
registeredinputs; finish196/package/hashsteps when terminal. Latestverified667.

Identifiedfollowingroutine aspadmux_get, full44byteSDKsectionidentity atfb18,
runtime1020658c. Objectgrus_padmux.o blobe42a2efc51c4ebacf55575630907be84888ba61a,
SHA2e5151ccf36515b89d72dfb124e0dc941d8d3e022c42befb4a76c9afe1f28521.
AddedC/builder/attribution/source-note. Compiles40bytesfits44, SHA
e5af2284986f0b29768c4e62c2e3170085f771cb1e6140adb89f7ee9f1f730ae.
StockSHA13c8ffcf7c31fd19cfa6542e29c9281bfc2ed30887628079f5e7440d56ae9ec3.
Unsignedid>32->-1; oneMMIOworda0010090+(id/8)*4, nibbleextract. Pin32accepted.
Unregistered/unqualified; nextdecodedMMIO/ABIproof. Fullgoalactive.

### Padmux getter decoded verification checkpoint

Previous turn progressedpadmuxC. Revalidatedcurrentcheckpoint/report andpolled
session53147 confirmedLIVE, dw-spi-quick-transfer-integration.log expected695.
Preserveregisteredinputs; finish196/package/hashes when terminal. Latest667.

Addedverify_gx8002_padmux_get.py:3034decodedstock/Ccases pass allvalidpins,
invalidboundaries andnibble/walking-bitpatterns; leafABI checked. Fourtarget
mutationtests added/pass (pin32,bounds,address,mask). Sessions28124/30504terminal.
Candidate40/44unchanged/unregistered; nexthashpins/admission. Fullgoalactive.

### Getter pinned; padmux check C checkpoint

Previous turn progressedgetterdecodedproof. Session53147 polledconfirmedLIVE,
expected695tests,dw-spi-quick-transfer-integration.log. Preserveinputs; finish
196/packageonterminal. Latestverified667. Getterqualifiedunregistered:standard
row/artifact/hashpins added,3034cases+4tests reranpass(session74863terminal0).

Addedruntime/build padmux_check C atfb44/runtime102065b8,36bytesfits36,
SHAa0567c5d096381ebe1698941c02316d253b74362a053772a12ca2e8d6bc4b165.
StockSHA43e3145e1f2f5699aaa68df92831161c21fa102c2c01fc9f2d827073aaa18dcc.
Preservesnegativearg rejection/getterunsignedbyte conversion; invalidpositive
pin getter-1 cancompareequalfunction255. Candidateunregistered/unqualified,
nextdecodedhelper/ABIproof. Fullsource-onlygoalactive.

### Padmux check decoded checkpoint

Previous turn progressedgetterpins/checkC. Session53147 polled confirmedLIVE;
expected695tests,dw-spi-quick-transfer-integration.log. Keepinputs; finish196
packagewhen terminal. Latestverified667.

Addedverify_gx8002_padmux_check.py:9324stock/Ccases pass modeledgetterresults,
negativeargs,byteconversion,callerclobbers/optional8byteframe. Fourfocusedtests
pass fornegativeearlyreturn,invalidpin255match,bytewrap,wronghelpertarget.
Getterbuildprerequisiteexplicit; sessions90454/8418terminal. Candidate36bytes
unchanged/unregistered; nextactualgettercomposition/pins. Fullgoalactive.

### Padmux checker/getter composition checkpoint

Previous turn progressedcheckdecodedproof. Session53147 polledconfirmedLIVE,
expected695tests,dw-spi-quick-transfer-integration.log. Preserveinputs; finish196
packagewhen terminal. Latestverified667.

Addedgetter_hook andverify_gx8002_padmux_check_composition.py:2592stock/Couter×
stock/Cleaf cases pass MMIO/return/callskip. Session91944terminal0. Reran9324
modeled-returncases and6focusedtests (hookuse/negativeargskip included).
Session31437terminal. Candidate36bytesunchanged/unregistered; nextevidencepins
andadmission oncecurrentintegrationdone. Hardwareunproven; fullgoalactive.

### SPI report serialization repair and padmux admission checkpoint

Integration session53147 failed at transfer baseline equality: sample gate
traces contained Python tuples while the saved JSON contained lists. Fresh
qualification proved all behavioral report values and compiled function rows
unchanged after normalizing the sample traces to JSON-compatible lists. Only
the gate-composition verifier hash changed; refreshed the reviewed aggregate
and asserted exact JSON round-trip equality. Session2118 passed. Integration
restarted as session25291 with dw-spi-quick-transfer-integration.log; expected
695 tests. No package update until terminal success; latest verified package
remains the 667-test/195-function checkpoint.

Padmux checker now has standard admission/export arguments, function row,
five evidence-file hashes, and actual decoded getter composition included.
Session62547 passed 9324 modeled-return cases plus 2592 composed cases; all
10 getter/checker tests passed. Both remain unregistered pending SPI build.

Added runtime_gx8002_padmux_set.c and its native candidate builder/report.
Session31242 passed: 76 bytes within 84 at package fb68/runtime102065dc,
compiled SHA 1f8925b8ae5ae8bdf589b1dfa6676b2a3d9c0c7c203831b7b6e32dfd707e03d3.
Unsigned pin bound 32, single-word nibble RMW, original arguments to checker,
write-before-check for invalid functions preserved. Next: decoded setter
MMIO/call/return/ABI proof and composition. Unregistered; hardware unproven.
Full source-only goal remains active across all six components.

### Padmux setter decoded checkpoint

Previous turn made concrete progress (serialization repair, checker admission,
setter C). Session25291 re-polled live this turn; preserve registered inputs.
Full SPI integration log remains dw-spi-quick-transfer-integration.log; latest
verified package remains 667 tests until this process reaches terminal success.

Added verify_gx8002_padmux_set.py: session83878 passed 12432 decoded stock/C
MMIO/helper/return/ABI cases. Added five focused tests; initial invocation from
repo root failed module discovery, corrected invocation from g2 passed all5.
Candidate 76 bytes unchanged; checker result remains modeled. Added check_hook
for next actual checker/getter composition with the post-write register word.
Source unregistered, hardware unqualified. Full source-only goal active.

### Padmux setter composed admission checkpoint

Previous turn made progress through 12432 decoded setter cases and five tests.
Session25291 re-polled live twice this turn; full SPI integration still running.
Do not edit its registered inputs or update package metadata before success.

Added verify_gx8002_padmux_set_composition.py: session17212 passed12096 cases
across eight stock/C setter/checker/getter selections and written/inverted
readback. Seven setter tests passed after adding failed-readback/no-undo and
invalid-pin/no-hook checks. Setter verifier now exports admission row/artifact
and pins seven evidence files, including decoded composition. Requalification
session62986 started. Padmux routines remain unregistered pending current build.
Next integrate getter/checker/setter after SPI package completion, and recover
padmux_init plus its default table. Hardware unqualified; full goal active.

### Padmux initializer and semantic default-table checkpoint

Previous turn progressed setter composed qualification. Session62986 terminal
success confirmed; 12432 decoded plus12096 composed cases. Session25291 polled
live twice this turn, integration log still at source-builder invocation.

Recovered initializer package fbbc/runtime10206630 in C; native build75126
passed, 72/80 bytes, SHA fa6395cc2cbc744d17d89d4f325d0003c1b48c1eac8c70eba84108aed54a1a78.
Null pointer/negative count fail; otherwise 32 default pins, first override
match, ignore setter errors. Needs decoded ABI/memory/call qualification.

Default table runtime1020acc4/package14250 decoded as32 typed pairs pin0..31,
function0. Added semantic C table and report; compiled C object matches all64
bytes of semantic generation and stock, no relocations. SHA8ddaed4c3145c740d216bc4597d5c78cdb33460e1539a147c78f4c5ec1e4d5e8.
No binary array transcription: typed boot policy with documented meaning.
Placement verifier/registration pending. Full source-only goal stays active.

### Padmux initializer decoded checkpoint

Previous turn progressed C initializer and semantic default data. Session25291
polled live this turn; full SPI integration remains pending. Preserve registered
inputs and latest verified667-test package until terminal build success.

Added verify_gx8002_padmux_init.py. Session94300 passed529 decoded stock/C cases
with exact read/call traces, optional20-byte frame, ABI and caller clobbers.
Added four focused tests (session11226), covering first duplicate match, ignored
setter failures, null/empty distinction and helper-target mutation. Source72/80
bytes unchanged. Removed an inert empty table-generation line after qualification.
Next actual setter composition and default-data placement/admission. Full goal
active; no hardware qualification or whole-firmware source-only completion.

### Padmux defaults reproducible admission checkpoint

Previous turn progressed initializer529 decodedcases and4tests; session11226
confirmed terminal pass. Session25291 polled live twice this turn; integration
still running. Preserve its registered sources/reports until terminal success.

Added verify_gx8002_padmux_defaults.py and3 policy tests, allpass. Native build
uses authenticated SDK header, typed C only, validates all32pin/functionpairs,
checks section/nonrelocation and stock correspondence, exports padmux-defaults.o
plus generated_source_data row for package14250/64bytes. Pins source/verifier
hashes and SDK header provenance. Table source admitted but unregistered.
Next initializer→setter composition, then padmux batch registration after SPI
build/package finish. Full source-only goal stays active; hardware unqualified.

### Padmux initializer/setter composition checkpoint

Previous turn progressed default-table reproducible admission. Session25291
polled live this turn; no integration restart. Added setter_hook to initializer
interpreter and verify_gx8002_padmux_init_composition.py. Session20985 passed96
scenarios/3072 actual decoded setter calls with persistent four-word MMIO state.
All stock/C combinations, several override shapes, initial words and checker
success/failure results pass. Six initializer tests pass. Session86542 reran529
initializer cases after hook addition. Checker result remains modeled at this
boundary; next compose actual checker/getter for full chain before admission.
No registered integration inputs changed. Full source-only goal active.

### SPI integration success and full padmux chain checkpoint

Previous turn progressed initializer/setter composition. Session25291 terminal0:
695 tests passed. Actual codec SHA08d72eb397e10f7ddfd4953053dd12a9c72c9055ed9924b324f91466c7191bfa,
196Cfunctions/212Coccurrences/257regions, compiledC13172, assembly156,
source-data2790, metadata80, fill704, retained309190. Updated codec manifest
and research JSON. First package build91820 reached expected old-pin mismatch;
new observed package SHA3b9fe9b84b50f259168ccdfee8d612133f01d54f467ac97bbfce744db565dc5b.
Updated pin and started rebuild79353; next copy11notices and verify-artifacts.

Extended initializer composition to actual checker/getter, all16 stock/C choices,
persistent register writes plus written/inverted readback. Session3660 passed384
scenarios/12288settercalls. Separate helper stack limitation remains. Initializer
admission pins/registration still pending; other padmux sources unregistered.
Full source-only goal remains active; hardware unqualified.

### Padmux initializer admission checkpoint

Previous turn progressed SPI695-test integration and full padmux chain. Package
rebuild79353 re-polled live twice this turn. Finish notices/verify-artifacts on
terminal success before registering padmux sources; latest completely verified
package still667-test checkpoint, new codec695-test build itself verified.

Initializer verifier now has standard args/export, placement row, ten pinned
verifier/builder files, full composition and default-policy qualification.
Session72308 passed529directcases plus384chain scenarios. Session91725 ran all
26padmux tests (get4/check6/set7/init6/defaults3). Padmux remains unregistered.
Next package finish then register four C routines and64-byte source table,
expected721integrationtests. Full source-only goal active; hardware unqualified.

### SPI package verified; padmux batch integration started

Previous turn progressed initializer admission. Rebuild79353 terminal0, full
EVENOTA4750780bytes SHA3b9fe9b84b50f259168ccdfee8d612133f01d54f467ac97bbfce744db565dc5b,
7822placedregions/0unresolved. Copied11notices; verify48418 terminal0. Latest
verified package is now695-test/196Cfunction checkpoint, codec08d72eb397e10f7ddfd4953053dd12a9c72c9055ed9924b324f91466c7191bfa.
Research MD headline counts/hashes updated; retained stock309190bytes remains.

Session39598 fresh get/check/set/init/defaults reports all exactly equal reviewed
baselines. Registered four C routines plus64-byte default table in source builder,
added26tests to Makefile. Started make integration13072, logpadmux-integration.log,
expected721tests. Preserve registered padmux sources/verifiers/reports until
terminal success. Expected200functions,216Coccurrences,41dataregions,262regions;
confirm actual ownership on completion before package metadata update. Full goal
active, source_onlyfalse, hardware_qualifiedfalse.

### RTC source candidates checkpoint

Previous turn progressed verified695-test package and padmux registration.
Session13072 polled live; padmux-integration.log expected721tests. Preserve
registered inputs until terminal success. Latest verified package unchanged.

Identified next stockfc0c..fc90 as RTC using authenticated SDK dw_rtc.o and
base_addr.h. Added start_tick and set_tick C/builders. Session80850 terminal0:
start16/16bytes SHA16405b6c894e37098adac09e9cb167e68b623eee1c3a6a91afd6cee9a3ae67a3;
set12/12bytes SHAa20e6d50e2e45f1f0edb4b1eca5b44447e26f603db47133512d71800702874f1,
setexactstock. RegisterRMW+0xc bit2, directloadregisterwrite+8. Unregistered;
next decoded MMIO/ABI verification, ISR/init recovery and full SDK attribution.
Full source-only goal active; hardware unqualified.

### RTC decoded tick checkpoint

Previous turn progressed two RTC C candidates. Session13072 polled live this
turn; padmux integration still pending, expected721tests. No registered inputs
changed. Added verify_gx8002_rtc_ticks.py: session44092 passed644decoded stock/C
cases checking exact registertrace/leafABI. Fourfocusedtests session39409 passed.
RTC start16/set12bytes unchanged/unregistered. Next admission export/pins,
SDK full attribution and RTC ISR/init recovery. Full source-only goal active.

### RTC ISR C checkpoint

Previous turn progressed tick644cases/4tests. Session13072 polled live this turn;
registered padmux integration inputs unchanged. Added runtime_gx8002_rtc_isr.c
and builder. Initial36bytes over32slot explained by shrink-wrapped duplicated
ack/return paths. Candidate-local -fno-shrink-wrap yields32exactstock bytes;
session86054 terminal0, SHA bb8cc0ade6891953872ceac15f1136faeccead9c79c3cb6b063768ee19f1d6c6.
Callback state20027b40/44, optional callback(irq,arg), thenreadRTC+18, returncallback
result or0. Next decoded callback/clobber/ABI/ack sequence verification and RTC
initialization. ISR unregistered; full source-only goal active.

### RTC ISR decoded checkpoint

Previous turn progressed32-byte exactstock ISR C. Session13072 polled live;
padmux integration ongoing, preserve registered inputs. Added RTC ISR decoded
verifier: session55049 passed540cases, exact state/call/ack order, originalIRQ,
registeredargument, callbackresult, callerclobbers and4byteframe/ABI. Fourtests
session53674 passed, including wrongtarget/read mutations. ISR stillunregistered,
callbackbody/physicalack unqualified. Next RTC admission and initialization.
Full source-only goal active; no hardware completion claim.

### RTC admission and full-section attribution checkpoint

Previous turn progressed ISR540cases/4tests. Session13072 polled live; padmux
integration still pending. Added standard ISR admission arguments/export/row,
pins builder/verifier; session46887 passed540cases. Source admitted, unregistered.
Added analyze_gx8002_rtc_primitives.py: authenticated SDK object, relocated three
complete ISR/start/set sections at knownaddresses with BSS20027b40, all exactstock.
Comparison-only ELF rtc-primitives-oracle.elf not firmwareinput. Next pin this
attribution in RTC admission, tick exports, recover RTC init. Full goalactive.

### RTC three-function admission checkpoint

Previous turn progressed ISR admission and SDK attribution. Session13072 polled
live; padmux integration still running. ISR now includes/pins attribution;
session52826 passed540cases. Added tick verify_one and start/set admission
wrappers with standard export/rows and pinned evidence. Session36391 passed
both644case qualification runs. Eight RTC tests session74188 passed. Allthree
RTC functions unregistered pending padmux build721tests/package completion.
Next RTC initialization recovery; full source-only goal active.

### RTC initializer C checkpoint

Previous turn progressed three RTC admissions. Session13072 polled live;
padmux integration ongoing. Recovered RTC initfc48/runtime102066bc source and
builder; session64389 passed72/72bytes SHA11777e797c3c28ba130d614ea61f7cc19ce41c7e7283381f300bf9a4b94f191d.
Bindings clockgate10025080/frequency10025210/requestirq1002553c/printf10206c24,
ISR10206680/start102066a0/error1020ad04. Success frequency<65536, thenRTC+20,
IRQ4nullarg,starttick; failure prints and retains preceding clock/control changes.
Added source-authored diagnostic C, unplaced. Next decoded init qualification,
helper composition and diagnostic data placement. All newRTCunregistered.
Full source-only goal active; hardware unqualified.

### RTC initialization decoded checkpoint

Previous turn progressed72-byte RTC init and diagnostic C. Session13072 polled
live; padmux build ongoing. Added verify_gx8002_rtc_init.py; session90346 passed
660stock/Ccases, exact helper/MMIO trace, callerclobbers and8-byteframe/ABI.
Fourtests passed: boundary65535/65536, failurestate, zerofrequencyIRQ, wronghelper.
No RTC admission forinit yet; helpers modeled. Next decoded start/clock/IRQ
composition and diagnostic placement. Registered integration inputs unchanged.
Full source-only goal active; physical qualification remains incomplete.

### Padmux integration passed; RTC diagnostic placement

Previous turn progressed RTC init660cases/4tests. Session13072 terminal0:
721tests pass. Actualcodec8e1467f51789e731a4367ce10dbd3ce10bee8f510226aa7556d7d0368fc29670,
262regions, C13396, assembly156, source-data2854, metadata80, fill724,
retained308882. Updated codec manifest200functions and researchJSON. Package
build75109 reached expected oldpin mismatch; observed newpackage
f97de22d33de7c0e23d7cfa637f7df185204e3a138deef8dde17bfcffde33279, pinupdated.
Next pinned rebuild then11notices/verify; latestverifiedpackage remains695test.

Added verify_gx8002_rtc_error.py source-data export at14290. First comparison
caught mistaken21-byte envelope; corrected22bytes including newline/NUL.
Native compiled literal matches stock, no relocations, source/verifier/header
provenance pinned. Unregistered. Full source-only goal active.

### RTC init/start composition checkpoint

Previous turn progressed721-test padmux integration and diagnostic placement.
Package rebuild29315 polled live. Finish notices/verify and researchMD metadata
when terminal; latestfullyverifiedpackage695test remains until then.
Added init start_hook and verify_gx8002_rtc_init_start_composition.py;
session83678 passed60scenarios (36startcalls) actualdecoded leaf with post-init
control state. SixRTCinit tests pass; session11217 reran660directcases.
Clock/frequency/IRQ/printf stillmodeled, no interveningcontrolmutation. Next
helper composition/initializer admission and RTCbatch integration. Fullgoalactive.

### Padmux package verified; RTC initializer attribution

Previous turn progressed init/start60cases and6tests. Package29315 terminal0;
11notices copied, verify45904 terminal0. Latestverified721-test package SHA
f97de22d33de7c0e23d7cfa637f7df185204e3a138deef8dde17bfcffde33279, codec
8e1467f51789e731a4367ce10dbd3ce10bee8f510226aa7556d7d0368fc29670. ResearchMD
headline counts/hashes updated200functions/216Coccurrences/2854data/308882retained.
Added separate analyze_gx8002_rtc_init.py (does not invalidate primitive pins):
allfour SDK sections match after relocation includinginit72bytes, BSS20027b40,
rodata1020ad04 and fourhelperbindings. Comparison-only. Three diagnostic tests
pass. Next initializer helper qualification/admission and RTCbatch registration.
Full source-only goal active; hardware unqualified.

### RTC primitive batch integration started

Previous turn progressed verified721-test padmux package and init attribution.
Session16473 fresh ISR/start_tick/set_tick/error reports allmatch reviewed JSON.
Registered threeRTC C routines plus22-byte diagnostic, added11tests. Started
make session66373 logrtc-primitives-integration.log, expected732tests. Preserve
registered RTC primitive builders/verifiers/attribution/source and diagnostic
inputs until terminal success. Expected203functions/219Coccurrences/42dataregions,
266regions; confirm actualreport before package updates. Initializer remains
unregistered, can continue helper composition independently. Latestverified
package remains721-test f97de22d33de7c0e23d7cfa637f7df185204e3a138deef8dde17bfcffde33279.
Full source-only goal active, hardware unqualified.

### RTC initializer clock-gate composition checkpoint

Previous turn progressed RTCprimitive registration. Session66373 polled live;
rtc-primitives-integration.log expected732tests. Preserve registered evidence.
Only unregistered initializer files changed: gate_hook and new decoded gate
composition based on existing verified gate interpreter. Session78055 passed
60scenarios/60gatecalls; module0enable1, bounded clockcontrol writes. Seveninit
tests pass; session24362 reran660directcases. Gate lookup/separate stack modeled,
frequencyIRQprintf stillmodeled. Next further helper qualification. Fullgoalactive.

### Upstream clock-frequency source candidate

Previous turn progressed RTCinit gatecomposition. Session66373 polled live;
RTCprimitive integration expected732tests. Located retained clockfrequency entry
17224/runtime10025210; prior clock admission only covered lookup/tables/gate.
Pinned SDK clk_priv.h contains _clk_get_module_frequence. Added source adapter
runtime_gx8002_clock_frequency.c and separate authenticated native builder/output
build/gx8002-clock-frequency (does not mutate registered gate inputs). Buildpassed,
reportgx8002-clock-frequency-candidate.json. Unlinked/unadmitted; next fixed-entry
link, helper/table attribution and full decoded qualification. This upstream
source can replace shared RTC/SPI frequency helper, beyond modeledreturns.
Full source-only goal active; no hardware qualification.

### Clock-frequency helper layout investigation

Previous turn progressed authenticated upstream frequency adapter. Session66373
polled live, RTCprimitive integration ongoing. Frequencyinitial544bytes exceeds
stock444bytes at17224..173e0. Targeted no-inline-functions-called-once produced
548+8wrapper, reverted. Added public lookup-contract adapter as existinggate
uses: compiler now emits __module_get_info160bytes plus frequency468bytes and
8byteadapter. This preserves lookupNULL contract and permits reuse of qualified
lookupentry; still24bytes overfrequency slot. Session86245 nativebuild passed.
Next divider helper separation/link placement and behavioral qualification.
Only unregistered frequency files changed. Full source-only goal active.

### Frequency divider boundary checkpoint

Previous turn progressed frequency lookup boundary. Session66373 polled live;
RTCprimitive integration stillrunning. Publicdivider adapter alone leftfreq468.
Targeted noinline produced specialized28-byte .isra.0 helper andfreq480; adding
noclone/noipa preserves originalaggregateargument ABI, helper40/freq468/lookup160.
Session61889 nativebuild passed. Source adapter annotations only; pinnedSDK body
unchanged. Still24-byte frequencyoverrun, unlinked/unadmitted. Next fixedentry
layout analysis/target proof, no blindbinarypull-through. Fullgoalactive.

### Clock-frequency fixed-address analysis link

Previous turn progressed shareddivider ABI. Session66373 polled live; registered
RTC integration inputs unchanged. Added link_gx8002_clock_frequency_candidate.py,
native link passed: lookup160/164 at10024a44, divider40/40 at10024ae8, freq468/444
at10025210. Analysis switchtable11000000 avoids overlap; original text overrun
would overwrite neighboring gatejump table. Allrelocs resolve, adapters discarded,
analysis ELF/disassembly plus report emitted. Not firmwareprovider/admitted.
Next inspect decoded arithmetic/layout and qualify helpers. Fullgoalactive.

### Divider slot correction from stock disassembly

Previous turn progressed analysis link. Session66373 polled live. Directstock
16afc..16b24 disassembly provesdivider ends16b18, slot28not40; followingPLL
routine starts16b18. Corrected linkreport envelope, now rejectsdivider40/28
andfrequency468/444. Session48902 rebuilt analysis successfully. Prior claimed
dividerfit superseded; no such candidate admitted. Public aggregate noipa helper
spills16bytes unnecessarily relative tostock r0/r1-only inputs. Next recover
stock-compatible helper calling shape and qualify behavior. Fullgoalactive.

### Stock-ABI divider C fits

Previous turn corrected divider28-byte envelope. Session66373 polled live;
RTCintegration unchanged. Added runtime_gx8002_clock_divider.c using upstream
GX_CLOCK_MODULE_PARAM/GX_CLOCK_DIV types with stock r0param/r1base calling shape.
Initial include lacked private paramtype; correctedclk_priv.h. Nativebuilder
passes28/28bytes SHA c6f8b015db32d4bba236e3c4e2f9b57eec0c158deda80bc3f08d982e6c3c3592.
Builder authenticates clk_priv/base/gxclock headers, no unrelated RTC oracle.
Need decodedmemory/ABI proof and integration, unregistered. Sourcefrequency
stilloversize; newhelper will permit correctstockboundary oncequalified.
Full source-only goal active.

### Divider decoded qualification checkpoint

Previous turn progressed28-byte stockABI divider C. Session66373 polled live;
RTCintegration stillrunning. Added verify_gx8002_clock_divider.py: session84860
passed12800stock/C cases across null/present descriptor, two MMIO bases, aligned
offsets, shifts0..31, masks and words. Exact descriptor/register read order and
width, resultzero-or-field+1 and leafABI checked. Threefocusedtests pass including
halfword-mask readmutation. Divider stillunregistered; next admission/export,
frequencycallingboundary adjustment and placement. Fullgoalactive.

### Divider admission/export verified

Previous turn progressed12800dividercases/3tests. Session66373 polled live;
RTC732-test integration stillrunning. Divider now standardadmission args, pinned
builder/decoder,28-byte SRAMrow and artifactexport. Session63858 requalified;
session15939 used actual reviewed_replacements against savedreport/exportELF,
passes28bytes. Unregistered untilcurrentintegration/packagefinish. Frequency
stilloversize; next adapt shared helper call preserving upstream logic and proof.
Full source-only goal active; no hardware completion claim.

### Upstream frequency divider-call adaptation

Previous turn progressed divider admission. Session66373 polled live. Unregistered
frequencybuilder now authenticates SDK header and generates minimally adapted
header: oneexact divider call replaced with qualified two-register externalcall,
plus declaration. Anchorcounts enforced; adaptedheaderhash reported. No upstream
arithmetic edits. Source no longer uses aggregate noipa helper/adapters. Generated
SDK header initially triggered existing signedness warnings because localinclude;
restored original system-header treatment with-isystem, warnings remainerrors for
adapter. Session29635 nativebuild passed: lookup160/frequency480/lookupadapter8.
Frequency still36over444slot. Oldanalysislink requires externaldividerbinding
update before rerun. Registered RTCinputs untouched, fullgoalactive.

### RTC integration passed; adapted frequency analysis link

Previous turn progressed minimal upstreamdividercall adaptation. Session66373
terminal0,732tests passed. Actualcodec bce004c362b8987f2020863bfc1dfbcb52839ac15da4ce37b7e40c32be447e02,
266regions, C13456/assembly156/data2876/metadata80/fill724/retained308800.
Updatedmanifest203functions and researchJSON. Started package79208 (expect oldpin
mismatch then update/rebuild); latestfullyverifiedpackage remains721test.

Updated frequencyanalysislink externaldivider10024ae8, removes oversizedaggregate
helper section, recordsbinding. Session49308 passedlookup160/freq480 (36over444),
no unresolvedrelocations. Analysisjumptable11000000, notfirmwareprovider. Next
finishpackage and continue frequencyplacement/behavior, RTCinithelper proof.
Fullsource-only goalactive; hardwareunqualified.

Package79208 reached expected oldpin mismatch; observed798fed4e9066e7bddd868917d64107a5598100aa28faf08260997272145de041, manifest updated. Pinned rebuild started next.

### Frequency switch inventory and layout experiment

Previous turn progressed RTC732-test integration and updated analysisbinding.
Package86041 polled live. Frequency entry stack now24bytes matchingstock but
text480. Targeted no-reorder-blocks (stock epilogue atbottom vs candidateearly)
expandedto488 andlookup164; reverted and rebuilt480/lookup160. Created19-entry
stock/source switchtarget inventory at stock17474/runtime10025460 vsanalysis
11000000. Next decodedmodule remap verification; targetinventoryalone notproof.
Package notices/verify pendingterminal rebuild. Fullgoalactive.

### Frequency decoded dispatch and RTC package verification

Previous turn progressed switchinventory. Package86041 terminal0; copied11notices
and started verify51914 (live onpoll). Latestfullyverified remains721test until
terminal success. Added verify_gx8002_frequency_dispatch.py: session61717 passed
259stock/C cases (0..255 plus signedboundaries/allones), actualjump-table walks,
lookupcall orzero-return semantics. This is dispatch-only, nofullABI/MMIO/arithmetic
claim; sourcefrequency480stilloversize. Next tests and arithmetic qualification.
Full source-only goal active.

### RTC package verified; divider integration started

Previous turn progressed frequency259dispatchcases. Verify51914 terminal0;
latestverified732-test package798fed4e9066e7bddd868917d64107a5598100aa28faf08260997272145de041,
codec bce004c362b8987f2020863bfc1dfbcb52839ac15da4ce37b7e40c32be447e02. ResearchMD
updated203functions/219Coccurrences/data2876/retained308800. Session58073 fresh
dividerreport matchesreviewed. Registered28-byte divider and3tests, started
make24299 clock-divider-integration.log expected735tests. Preserve registered
divider sources/builders/verifier/report untilterminalsuccess. Expected204functions
and267regions; confirm actualownership afterbuild. Frequency480stillunadmitted,
RTCinitadditionalhelpers stillpending. Fullsource-only goalactive.

### Frequency dispatch mutation tests

Previous turn progressed verifiedRTCpackage/divider registration. Session24299
polledlive, clock-divider-integration.log expected735tests. Added four decoded
frequencydispatch tests: alias/zeropath, unsignedbypass, wronglookup and switched
targetmutations. Initial discoveryfromroot failed tools import; correctedg2cwd
invocation passed4tests. Sourcefrequency remains480bytes/analysis-only. Next
arithmetic/MMIO qualification beyonddispatch. Registereddividerinputs unchanged.
Fullsource-only goalactive.

### PLL arithmetic model checkpoint

Previous turn progressed dispatchmutations. Session24299 polledlive,735-test
dividerintegration ongoing. Added model_gx8002_clock_pll_frequency.py and5tests;
corrected initialfilewrite cwd (no files created byfailedcommand). All5pass.
Model captures orderedoverlappinginputbands,32-bitwrap andintegerdivisionorder;
zero wrappedfeedbackdivisor rejected outsidecontract. No decodedPLL proof yet.
Next usemodel againststock/sourceinstructions. Registeredinputs unchanged,
fullsource-only goalactive.

### Decoded PLL slice checkpoint

Previous turn progressed independentPLLmodel/5tests. Session24299 polledlive;
divider735-test integration ongoing. Added verify_gx8002_clock_pll_slice.py,
session31373 passed480stock/C cases vsmodel with exactfive-registerread order.
Stockentry172b0 exits1732e/1737e; sourceentry100252f2 exits10025390/10025246.
Sliceonly: nofullABI/DTO/divider/source-selection proof. Frequency still480over
444slot. Next mutationtests and wider execution composition. Fullgoalactive.

### PLL slice mutation coverage

Previous turn progressed480decodedPLLcases. Session24299 polledlive,735-test
dividerintegration ongoing. Added test_gx8002_clock_pll_slice.py;4tests pass:
nominal/overflow, five-registersequence, wrongregisteroffset andwronginputmask
mutations against compiledslice. No registeredinputs changed. Next DTOscaling
andfull-frequency execution/placement. Fullsource-only goalactive.

Clock DTO continuation: 72 decoded stock/C arithmetic-slice cases and four
focused tests pass on macOS. The bypass bit, 25-bit numerator and 64-bit product
are now checked with ordered descriptor/MMIO reads. This does not change the
source-only status: the frequency candidate remains 36 bytes oversized and
unadmitted, and full-function composition remains outstanding. The clock-divider
integration process is still live; no newer completed package is claimed here.

Completed clock-divider package checkpoint: the native macOS integration build
passed all 735 tests. The codec now has 204 C functions at 220 occurrences,
five architecture routines, 42 data regions, and 267 replacement regions.
Ownership: compiled C 13,484; assembly 156; source data 2,876; metadata 80;
unreachable fill 724; retained stock 308,772 bytes. The 326,092-byte codec SHA is
dd1ce6168f52fa8bc4fc72d126563cc9179187d5eaa5ad72dadf7033461057f4.
The rebuilt 4,750,780-byte EVENOTA SHA is
a3156edb778357a31809e0e9c59ac13c577ad1efc972d2095ed9b7e03c707dd0.
Package build and verify-artifacts both exited successfully; all 11 source
notices were copied. No hardware was flashed. Source-only and hardware-qualified
remain false. The full goal remains active, including oversized frequency and
RTC initializer qualification plus all remaining components and opaque data.

Clock selection continuation: 26,624 decoded stock/source comparisons and four
focused tests pass natively on macOS. The check includes changing selection
register values between repeated volatile reads, preserving the zero-frequency
fallthrough when the second selection read clears. Ordered MMIO, 32 kHz shortcut,
low-frequency returns and PLL/DTO/divider routing agree at the slice boundary.
This supplies new behavioral evidence for the full frequency reconstruction;
it does not admit the oversized function or establish full ABI/hardware behavior.
The last complete package remains the 735-test clock-divider checkpoint.

Frequency size progress: an isolated source adaptation reduces the candidate
from 480 to 452 bytes using exact masked-subband arithmetic and an equivalent
unsigned early-return predicate. Two focused algebra/domain tests pass. Eight
bytes still exceed the original envelope; the probe is not linked or admitted.
The baseline qualification artifacts remain for the unchanged 480-byte candidate.
No source-only or hardware completion is claimed.

The 452-byte clock-frequency probe now has an isolated analysis link and passes
480 decoded PLL and 72 DTO cases against the stock-qualified models, including
ordered PLL register reads. Further algebraic factoring and disabling compiler
reassociation did not reduce size and were reverted. The eight-byte excess and
full-function qualification remain; no oversized code was admitted to firmware.

Size-probe selection qualification now passes 26,624 decoded cases in addition
to its 480 PLL and 72 DTO cases; six focused tests pass on macOS. A targeted
jump-threading experiment increased size to 504 bytes and was reverted. The
restored 452-byte probe remains eight bytes oversized and unadmitted. Firmware
package contents and the active full-source objective are unchanged.

Clock probe dispatch continuation: 259 linked jump-table/dispatch cases and
four mutation/boundary tests pass on macOS for the smaller candidate. The
combined report now records its analysis ELF hash alongside all slice counts.
The 452-byte candidate is still eight bytes oversized; lookup/full ABI and
whole-function composition remain incomplete. No firmware bytes were promoted.

Clock selection size experiment: two alternate C forms compiled to 460 and 456
bytes, respectively, so neither displaced the qualified 452-byte probe. A separate
script and report preserve the latter experiment without changing the candidate
or admitted firmware. The eight-byte excess remains an implementation task,
not an external blocker; full source-only reconstruction remains active.

Clock return continuation: 56 decoded stock/probe divider-call and epilogue
comparisons plus three focused tests pass on macOS. Helper target/arguments,
zero bypass, division, caller clobbers and saved-register restoration agree
under a valid-frame assumption. This is additional evidence toward complete
function verification, not full ABI proof or source admission. The overall
source-only goal remains active.

Clock return/divider composition now passes 864 decoded stock/source outer/leaf
combinations on macOS, including descriptor absence, zero divider, mask/shift
boundaries and unsigned frequencies. The actual decoded leaf drives the outer
result, replacing the earlier arbitrary divider result at this boundary. Three
return tests pass. Separate modeled frames and fixed entry assumptions remain;
no whole-function or hardware claim, and no additional source admission.

Clock text now has a 444-byte alternative that fits its envelope by using a
16-byte source-authored PLL frequency table. An isolated analysis link succeeds
with no unresolved text/table relocations. The table needs real firmware
placement and decoded qualification; existing source-owned fill intervals are
potential locations but none was assigned or overwritten. Full-function
qualification and source-only reconstruction remain active. No firmware
admission is claimed from text fit alone.

The fitting table-based clock candidate passes 480 decoded PLL cases using its
actual linked source-authored table. Table contents, indexed access bounds and
ordered MMIO reads are checked. Four existing PLL tests pass. Real table
placement, remaining path qualification and whole-function validation remain
open; source-only status is unchanged.

Fitting table candidate path qualification passes on macOS: 259 dispatch,
26,624 selection, 480 PLL, 72 DTO and 56 return cases. Evidence is now specific
to its changed code layout. Separate slice state and modeled return/helper
assumptions remain; this does not replace whole-function validation or admit
the analysis-address table into firmware. The full source-only goal stays active.

Clock table placement analysis identifies and authenticates a 16-byte source-owned
platform-config tail at runtime 0x10025e38/package 97868. The isolated link uses
real function/switch/table addresses and resolves all three sections. It does
not modify the firmware or bypass overlap rejection. Explicit ownership carving,
host/control-flow checks and complete function validation remain required.

Actual-address clock placement checks pass on macOS: 259 dispatch, 26,624
selection, 480 PLL, 72 DTO and 56 epilogue cases using the proposed firmware
switch/table addresses. This verifies the changed linked pointers within the
slice scope. Firmware remains unchanged pending host-tail safety, ownership
integration and whole-function qualification. The full source-only goal remains
active.

Proposed table host check: an authenticated local platform-config CFG walk covers
82 reachable instructions and all ten dispatch targets without entering its
unused tail. External references, startup effects and explicit ownership carving
still require review; no firmware change or source admission was made. This adds
local control-flow evidence toward table placement while the full goal remains
active.

Table-reference inventory finds one original pointer into the proposed tail,
in the platform-config dispatch table already replaced by generated source data.
The current candidate has no literal pointers into the interval under an
all-byte-alignment little-endian scan. Computed addresses remain outside this
check; ownership and whole-function integration are still pending. Goal active.

Implemented a standalone exact-tail source-data ownership partition helper.
Seven tests pass on macOS, including existing composer/checksum integration
with artificial test data and rejection of unsafe or unauthenticated partitions.
No real firmware provider uses it yet; actual table admission and complete clock
function qualification remain open. The full source-only objective stays active.

Validated the source-tail partition against the real compiled host and PLL table,
producing disjoint 196-byte code and 16-byte data regions with unchanged payloads
and authenticated stock provenance. This advances ownership integration beyond
synthetic tests; no firmware emitted and full clock qualification remains open.
The complete source-only goal remains active.

Clock lookup-result boundary now passes 1,280 decoded stock/source comparisons
on macOS: lookup failures avoid parameter reads, and the signed -1 offset returns
zero. Other byte values reach selection with correct sign extension, without
claiming later invalid-shift behavior. Full lookup-body and whole-function
composition remain outstanding. The complete source-only goal stays active.

Decoded lookup/result-gate composition passes 1,028 stock/source combinations
using actual authenticated clock records. The observed offset domain is
nonnegative and below 32, refining the valid-input scope for later full-function
checks. Separate frame translation and modeled dispatch remain limitations;
no source-only completion or firmware admission is claimed.

Clock early-return paths now pass 777 continuous entry-to-return candidate frame
cases plus three tests on macOS. Unlike prior slices, this check creates and
restores the same saved frame through the actual prologue and epilogue. The
lookup body remains modeled and successful MMIO paths still need continuous
execution. No complete-function or firmware admission claim; full goal active.

Extended continuous clock execution through low-frequency MMIO and divider
paths: 156 cases pass on macOS with one register/stack state from entry to return.
Helper arguments and saved-register restoration are checked, while helper bodies
remain modeled. PLL/DTO and full integrated behavior still need continuous
qualification; no firmware admission or source-only completion claimed.

Added continuous 32 kHz clock-path verification: 192 cases pass on macOS, and
all 156 low-frequency frame cases remain passing. Valid modeled descriptors
and helpers are still assumptions; PLL/DTO continuous execution and actual
provider integration remain outstanding. Full source-only goal active.

Continuous clock DTO paths now pass 150 cases on macOS, with the 156 low-frequency
and 192 32 kHz regressions still passing. The interpreter follows actual scaling
instructions through the same saved frame. Lookup/divider helpers remain modeled;
PLL and complete function integration are not yet proven. Goal remains active.

Continuous clock PLL paths now pass 72 cases on macOS through calculation, source
table reads, DTO and return, including invalid-PLL early exit. Low/32 kHz/DTO
regressions remain passing (156/192/150). Modeled helpers and descriptors remain
explicit limitations; whole-image/source-only completion is still unproven.

Added 1,664 continuous changing-selection clock cases with ordered MMIO traces.
Tightened byte/word read validation in the continuous interpreter; PLL/DTO frame
regressions still pass. This removes the constant-selection assumption for the
covered non-PLL routes but leaves modeled helpers and descriptors. Goal active.

Connected continuous clock execution to decoded source-divider behavior: 162
cases pass with ordered descriptor/MMIO reads driving final frequency. All 1,664
changing-selection regressions remain passing. Separate helper frames and modeled
lookup remain limitations; full firmware/source-only completion remains open.

Removed the separate divider-frame assumption for 162 clock cases: caller and
source divider now share registers, memory and the call/return address. All
cases pass on macOS, with PLL-frame regressions passing. Modeled lookup and
remaining whole-function comparison still prevent completion/admission claims.

Connected decoded lookup failure paths to the caller's actual simulated frame:
259 cases pass on macOS, with bounded info-record writes and shared call/return
state. Shared-divider regressions (162) pass. Successful lookup and full stock
comparison remain open, so no completion or firmware admission is claimed.

Removed modeled lookup for 32 successful low-frequency cases using actual source
records and shared caller/helper state. All pass on macOS, along with 259 lookup
failure regressions. Other module/routes and stock full-machine comparison
remain open; the complete source-only goal remains active.

Connected both decoded clock helpers and actual source parameter/divider tables
in one machine state. All 26 module cases pass on macOS under zeroed MMIO,
removing modeled helper results for this domain. Broader MMIO/routes and stock
comparison still require work; full source-only goal remains active.

First complete-path stock/source clock comparison passes all 26 module inputs
for the zeroed-MMIO low-frequency domain. Both lookup and divider run decoded
within the caller machine, using actual tables and continuous frame state.
Broader register-state comparison and actual firmware admission remain pending;
full source-only reconstruction is still active.

Expanded continuous stock/source clock checks from 26 to 208 cases, covering both
low-frequency sources and varied divider registers with actual descriptors.
All pass on macOS against independent divisor expectations. Higher-frequency
routes, integration and full source-only completion remain open; goal active.

Added 130 direct stock/source 24.576 MHz/DTO/divider cases using actual tables
and both decoded helpers in shared state. All pass on macOS against independent
expected frequencies. PLL stock comparison and provider integration remain open;
the full source-only objective remains active.

Added 312 direct stock/source PLL-to-return cases with actual records and both
helpers in shared state. All pass on macOS, including invalid-PLL exits and
DTO/divider behavior checked against independent calculations. Dynamic MMIO,
provider integration and complete firmware/source-only verification remain open.

Strengthened all 650 direct stock/source clock cases to compare complete ordered
MMIO read addresses, widths and values as well as results/helper calls. All pass
on macOS. This adds observable access equivalence within the tested register
states; hardware timing, dynamic registers and provider integration remain open.

Removed a circular placement dependency on current hybrid-image fill. The check
now uses freshly compiled, hash-reviewed host source and authenticated original
envelope geometry, so it can remain valid after table installation. Actual
partition and 312 PLL comparison cases pass on macOS. Goal remains active.

Created and ran the consolidated clock-frequency source evidence generator.
It replays 650 continuous comparisons plus host/partition checks and defines
three exact linked source sections with evidence hashes and export support.
All checks pass on macOS. Registration/admission remains pending; no firmware
change or complete source-only claim was made.

Registered the bounded clock-frequency source provider and explicit authenticated
platform-config tail partition in the experimental composer. The aggregate
qualification and 14 ownership/container tests pass. Started the full native
macOS integration build (clock-frequency-integration.log); no completed new
firmware/package is claimed while that process runs. Registered inputs must
remain unchanged during integration. Full source-only/hardware goal stays active.

While clock integration remains live, RTC initializer frequency composition now
passes 12 cases using the decoded source clock and its real helper/table logic.
Both successful 32 kHz initialization and high-frequency diagnostic routes agree
for stock/source outer code. Separate outer/helper frames and modeled remaining
RTC helpers remain limits. No completed package claim while integration runs.

Integration session remains verified live. Added two RTC frequency-hook
regressions; all nine initializer tests pass on macOS. They ensure helper-derived
frequency drives success/error decisions rather than a supplied placeholder.
Registered integration inputs remain unchanged; no new completed package claim.

While integration remains live, added 24 RTC IRQ composition cases using decoded
stock/source registration and enable instructions. Handler/private installation
and controller bit-4 enable agree; failure paths skip both. Separate frames and
physical delivery remain limitations. No completed new firmware claim.

Verified the source-built RTC diagnostic through stock/source decoded formatter
instructions with exact message/newline output and matching return values.
Character delivery and printf wrapper remain outside this check. Integration
is still live; no registered inputs changed and no new package completion claim.

Completed clock-frequency integration/package checkpoint: all 742 tests pass on
native macOS, followed by successful package build and verify-artifacts. Codec
SHA-256 is 94ac39c35629202cad532a4ad4f763b5b1ec60c4e5ab95cef7dcbaef010c2303;
EVENOTA SHA-256 is 1619d0f89aa0bb98e05b7eeb974f4dd3b7c3f020106d49b7904f44226d60767e.
Codec ownership: 13,928 C bytes, 156 assembly, 2,968 source data, 80 metadata,
708 unreachable fill, 308,252 retained stock. There are 205 C functions at 221
occurrences and 270 replacement regions. All 11 source notices were copied.
No hardware was flashed. Complete source-only and hardware qualification remain
false; RTC initializer and the many remaining opaque components remain work.

Added 24 RTC printf composition cases connecting the diagnostic call to decoded
wrapper forwarding and verified formatter output; nine RTC tests pass. Separate
frames/pointer translation and physical UART remain limits. Last package remains
the completed 742-test clock-frequency checkpoint; full goal stays active.

Created and ran consolidated RTC initializer qualification covering upstream
attribution, core behavior and all identified helper compositions. The 72-byte
source initializer fits and export support is ready; aggregate checks pass on
macOS. Provider registration remains pending, and the full source-only objective
is still incomplete and active.

RTC initializer aggregate is now registered. A fresh aggregate exactly matched
the reviewed baseline, and the exported ELF passed reviewed_replacements.
The native macOS integration is running (rtc-init-integration.log); do not count
this as a completed package checkpoint until that run and packaging finish.
An isolated, reproducible SPI setup compiler-option probe tested 21 variants;
minimum text remains 120 bytes against the 116-byte envelope. No SPI source or
provider was changed by these probes. The largest existing unreachable fill is
80 bytes, insufficient for straightforward relocation of the whole function.

Completed RTC initializer integration: all 751 tests passed on native macOS,
followed by successful package build and verify-artifacts. Codec SHA-256
b8e7eb55e12c0629df7ccff3ce0791c9f3cb0da80ec4ab8d1ca2efd28abbf628;
EVENOTA SHA-256 c69bbcd91c8c977bf267d9b9bce75c07d11136b6b1d8a36211c41f672b95e1f1.
206 C functions at 222 occurrences, 271 replacement regions, 14,000 C bytes,
156 assembly bytes, 2,968 source data, 80 metadata, 708 fill, and 308,180 retained
stock bytes. Eleven notices copied; no flashing. Full source-only and hardware
qualification remain false. This supersedes the pending RTC integration entry.

Recovered board pin configure at package 0xfd68 as a new C candidate. Native
macOS compilation emits 64 bytes, fitting the 64-byte slot. It is unregistered
and unqualified; next work is decoded transaction/ABI comparison, source
diagnostic data and reviewed helper compositions. Last completed package is
the 751-test RTC checkpoint. Full source-only goal remains active.

Board pin guard decoded qualification now passes 8,100 cases and seven tests
on native macOS. Error-path and initialized-state behavior match; mutation
tests detect wrong helper/default selection and ABI corruption. Helper bodies
and diagnostic data remain pending; candidate is not registered. Last package
remains the verified 751-test RTC checkpoint, and full goal is active.

Board pin diagnostic is now compiled from a C string and exact-extent checked.
Ten combined guard/data tests and 18 stock/source formatting cases pass on
macOS. Integer/output helper bodies and guard/padmux compositions remain
pending; no source admission claimed. Full source-only goal remains active.

Board guard now composes decoded padmux setter/checker/getter across 3,360
cases and all 16 stock/source combinations; 12 tests pass. Separate helper
frames and modeled readback are explicit limits. Printf composition and
integration remain pending; source-only goal stays active.

Board guard/printf forwarding now passes 288 decoded cases with both stock
and source wrappers, signed pin boundaries, initialization/error paths and
varied formatter returns. Thirteen guard/data tests pass on macOS. The wrapper
forwards the original pin value and the guard preserves its -1 error return.
Frames and format-pointer translation are explicit harness boundaries; integer
and output helper bodies remain modeled. Candidate remains unregistered and
the full source-only goal remains active.

Diagnostic integer conversion now executes decoded stock/source ui2a bodies
at the formatter boundary. All 36 formatter/integer combinations pass for
nine signed pin boundaries, including INT_MIN and -1. The formatter interpreter
fork adds an explicit hook while preserving existing registered verifiers.
Helper memory/output-buffer translation remains separate; character/padding
and physical UART remain modeled. The 288 guard/printf cases and 13 tests
still pass. Source admission and complete source-only firmware remain pending.

Diagnostic padding now executes decoded putchw with the formatter-provided
width, sign, base and converted digits. Seventy-two formatter/integer/padding
stock/source combinations pass across nine signed pin values; the 288
guard/printf cases remain passing. Separate helper memory and output-stream
translation remain explicit. Character output and physical UART are modeled.
No integration admission yet; the full source-only goal remains active.

Added decoded putf boundary verification: 210 stock/source cases establish
character/stream forwarding and failure only for fputc result 0xffffffff.
Three wrapper tests pass, 16 combined with board guard/data tests. This helper
still needs connection to formatter/padding execution; fputc and physical UART
are modeled. No new provider admission; full source-only goal remains active.

Decoded putf is now connected to both literal character emission and padding
output. All 144 stock/source formatter/integer/padding/putf combinations pass,
including equality of the emitted byte stream with the expected diagnostic.
Separate frames and buffer translation remain explicit; fputc return and
physical UART are modeled. Candidate is still unregistered; full source-only
firmware remains the active objective.

Decoded fputc now passes 108 forwarding/return cases and is connected to the
diagnostic putf path using matched stock/source wrappers. It ignores stream
and console result and returns zero. All 144 diagnostic combinations and
16 tests pass. Console output remains a modeled boundary; physical UART and
full source-only integration remain incomplete. Goal stays active.

Console/UART port wrapper composition passes 72 decoded combinations,
including selected-port reads, descriptor arithmetic, byte truncation and
CR-before-LF behavior. Two new console tests pass, 18 combined boundary/guard
tests. This composition is not yet connected to the diagnostic; UART transmit
and the port-global value remain modeled. Full source-only goal stays active.

Diagnostic composition now reaches console/UART port wrappers and compares
the CR/LF-translated transmit sequence. Each transmit call also executes both
stock/source transmitter bodies with scripted busy-then-ready MMIO and exact
read/write trace checks. All 144 diagnostic combinations and 18 tests pass.
This uses selected port zero, separate frames and scripted MMIO; physical
timing/hardware remain unqualified. Aggregate admission/integration is next;
the complete source-only goal remains active.

Board pin guard and diagnostic are registered for experimental source
admission. Fresh aggregate/data reports matched reviewed baselines and both
ELF/object exports passed reviewed_replacements. Full macOS integration is
running in board-pin-integration.log; no completed package checkpoint claimed
until terminal success and artifact verification. Last verified package remains
the 751-test RTC build. Full source-only and hardware goals remain incomplete.

While board-pin integration continues, recovered its caller at 0xfda8 as C.
Native macOS build emits 132 bytes exactly matching stock, including all eight
configuration calls and the original cleanup/diagnostic/infinite-loop failure
path. It is unregistered; decoded/composed qualification and source diagnostic
remain next. No current integration inputs changed by this candidate.

Eight-pin setup decoded comparison now passes 3,096 cases and four tests on
macOS. All 256 combinations of zero/-1 guard returns are covered, plus two
unsigned wraparound cases, varying cleanup/printf returns, and both terminal
paths. Mutation testing detects a wrong configured pin. Actual helper bodies
and fatal diagnostic source remain pending; this caller is not registered.
Board-pin integration remains the existing live process; full goal is active.

Fatal setup diagnostic now compiles from a C string and matches its 49-byte
stock extent at 0x142f2. Seven setup/data tests pass. Decoded setup/guard
composition passes 2,048 combinations: both stock/source choices, initialization
states and all 256 conflict masks. Guard padmux/printf and setup cleanup
helpers remain modeled in this composition, with separate checked frames.
The setup caller is unregistered; board-pin integration remains live and the
full source-only goal remains active.

Fatal cleanup now executes decoded setters in 48 setup/setter combinations
with shared register words. Exact ordered writes clear pins 5,6,11,12 while
preserving neighboring fields, regardless of modeled checker failure. Nine
setup/data tests pass, including hook-controlled guard failure and cleanup
call gating. Actual checker/guard/diagnostic composition remains pending.
Integration session 1482 was confirmed live this turn; full goal stays active.

Cleanup composition now includes decoded checker and getter bodies: 192
stock/source combinations pass with written and inverted readback. Shared
cleanup words retain neighboring fields and ordered writes. Nine setup/data
tests pass. Guard/printf are still modeled in this cleanup-specific harness;
separate frames and scripted readback are explicit limitations. Integration
session 1482 was confirmed live; full source-only goal remains active.

Completed board-pin integration/package checkpoint: 769 tests passed on
macOS, then package build and verify-artifacts succeeded. Codec SHA-256
7f027e84d6d8d180e6c7b40c74f0f618f99ef51ec7c3aef415013b41921e5231;
EVENOTA SHA-256 bc4def4984f11f61c26cb2d79031d8a1c47bd069b772c76d3a5daa45c36560a7.
207 C functions, 14,064 C bytes, 2,996 source-data bytes and 308,088 retained
stock bytes. Eleven notices copied. Session 1482 is terminal success; no live
integration remains. Eight-pin caller printf forwarding separately passes
24 cases and nine setup/data tests; that caller remains unregistered.
Full source-only and hardware qualification remain false; goal stays active.

Fatal setup diagnostic now passes four stock/source formatter/putf paths
through decoded fputc, console, UART wrappers and both transmitters under
scripted busy/ready MMIO. Literal text rejects unexpected integer/padding
helper calls; output exactly preserves its internal CR/LF and trailing text.
The 24 setup/printf cases and nine setup/data tests pass on macOS.
Shared whole-call stack and physical hardware remain unqualified; admission
of the setup caller remains pending and the full source-only goal is active.

Eight-pin setup and fatal diagnostic passed aggregate/export checks and are
registered for experimental integration. The full macOS suite is running in
board-pin-setup-integration.log. Last verified package remains the 769-test
board-pin checkpoint until new integration/package verification completes.
Source-only and hardware qualification remain false; full goal stays active.

While setup integration runs, recovered the next board initializer table at
0x142bc as typed source policy using authenticated SDK GX_PIN_CONFIG. Thirteen
entries cover pins 0..12; pin 2 selects function zero, all others one. The
26-byte compiled table matches stock; four policy/extent tests pass on macOS.
This table is unregistered; initializer code/call composition remains next.
Integration session 58083 was confirmed live; full source-only goal is active.

Recovered board pin initializer at 0xfe2c in C. It compiles to 104 bytes on
macOS, fitting the original slot; unregistered and unqualified. It performs
table initialization/checks, conditional GPIO direction, eight-pin setup, then
sets the initialized flag only after setup returns. Header authentication and
decoded/composed behavior remain next. Integration 58083 is live; goal active.

Initializer builder now authenticates gx_padmux.h and gx_gpio.h against
NationalChip commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, recording Git
blob and SHA-256 identities. The C GPIO prototype now matches the recovered
implementation and upstream GX_GPIO_DIRECTION enum; direction zero is named
GX_GPIO_DIRECTION_INPUT. Native compilation remains 104 bytes with unchanged
code SHA-256 55cfa58578b79d4a14bb295ac596892a8a9cd304edbbc7d5d9060578f5f36753.
Decoded qualification remains next. Integration 58083 was confirmed live;
the full source-only goal remains active.

Initializer decoded comparison passes 240 cases and three tests on macOS,
covering table variations, error-bit branches and setup return/nonreturn.
The initialized flag is absent from nonreturn traces. Helpers and nonreturn
are modeled at call boundaries; actual helper composition remains pending.
Integration 58083 was confirmed live; full source-only goal remains active.

Initializer now consumes the decoded setup terminal path in 2,048
stock/source combinations across all 256 guard failure masks and diagnostic
branches. Setup self-loop prevents the initialized flag write. Four initializer
tests pass, including a hook overriding an assumed return. Lower helpers remain
modeled in this composition and frames are separate. Integration 58083 was
confirmed live; complete source-only firmware remains the active goal.

Completed eight-pin setup integration/package checkpoint: 778 macOS tests,
package build and verify-artifacts passed. 208 C functions, 14,196 C bytes,
3,045 source-data bytes and 307,907 retained stock bytes. Codec SHA remains
7f027e84d6d8d180e6c7b40c74f0f618f99ef51ec7c3aef415013b41921e5231;
EVENOTA SHA remains bc4def4984f11f61c26cb2d79031d8a1c47bd069b772c76d3a5daa45c36560a7
because new code/data reproduce stock bytes exactly. Eleven notices copied.
Session 58083 terminal success; no live integration remains. Initializer error
message at 0x14323 is now a 19-byte source-authored literal; seven initializer/
data tests pass. Initializer remains unregistered; source-only goal active.

Initializer source-table composition passes 60 cases with exact compiled-data
read order. Initializer/GPIO composition passes 24 stock/source combinations
with shared register words and 52 ordered accesses per case, preserving
unrelated bits and setting input policy for pins 0..12. Other helpers remain
modeled in these finite compositions; initializer remains unregistered.
Full source-only firmware goal stays active.

Initializer per-pin diagnostic now passes 144 decoded formatter/output
combinations through scripted UART transmission. Initializer/printf forwarding
passes 180 cases across per-entry error masks and return values; processing
continues after diagnostics. Seven initializer/data tests pass on macOS.
Other initializer helpers and physical hardware remain unqualified in this
composition; aggregate admission is pending and full goal remains active.

Initializer pin checks now execute decoded checker/getter bodies in 32
stock/source combinations. Diagnostic decisions follow decoded register
readback; ordered reads cover all 13 pins. Eight initializer/data tests pass,
including hook-driven diagnostic selection. Post-init padmux words and other
helpers remain modeled; padmux initialization composition remains next.
The full source-only goal stays active.

Board/padmux initialization composition passes 24 decoded combinations.
The 13-entry override table feeds all 32 default-pin setter calls, with
non-board pins defaulting to function zero. Nine initializer/data tests pass,
including initialization argument forwarding and ignored helper error. Setter
bodies remain modeled in this particular composition; other reviewed helper
proofs remain separate. Full source-only admission/firmware remains pending.

Board/padmux initialization now includes decoded setter bodies and shared
register words in 96 combinations. All 32 writes are checked and final words
match the board/default policy from both zero/all-one initial states. Setter
checker and other board helpers remain modeled in this composition; decoded
checker composition is independently established. Full goal remains active.

Board initializer, diagnostic and 13-pin source table passed aggregate/export
checks and are registered. Fresh reports matched reviewed baselines for all
three artifacts. Full macOS integration runs in board-pin-initialize-integration.log.
Last verified package remains the 778-test setup checkpoint pending terminal
integration/package verification. Complete source-only goal remains active.

Recovered gsensor_workstate diagnostic accessor at 0xfe94 as C. Native macOS
build fits its 24-byte slot; both state reads are preserved across printf.
The name comes from the diagnostic, not a hardware lifecycle claim. Candidate
is unregistered; decoded behavior/data qualification remains next. Integration
85121 was confirmed live; full source-only goal remains active.

Gsensor accessor decoded comparison passes 216 cases and three tests on
macOS. First-read value is printed; second-read value is returned even when
changed during the modeled printf call. Wrong second-read address is rejected.
Printf composition, diagnostic data and state lifecycle remain pending.
Integration 85121 was confirmed live; full source-only goal stays active.

Gsensor diagnostic is source-authored and exact-extent checked at 0x14336.
It passes 144 decoded formatter/output combinations through scripted UART
transmission; six accessor/data tests pass on macOS. Accessor printf boundary
and state lifecycle remain pending. Initializer integration 85121 was confirmed
live; complete source-only firmware remains the active goal.

Gsensor accessor/printf composition passes 144 decoded cases, forwarding
the first state value while returning the second independently of printf.
Seven accessor/data tests pass. Separate frames, translated format pointer
and scripted UART/state values remain explicit limits; state producer/lifecycle
and admission remain pending. Integration 85121 confirmed live; goal active.

Authenticated stock literal inventory found one exact state-address literal
(0x20026c70 at 0xfea4), in the accessor. A neighboring pointer 0x20026c74
appears at 0x1182c. Candidate initialized-data offset 0x18c84 contains one,
but section mapping is explicitly unverified in this inventory. Computed or
indirect writers are not excluded; producer/lifecycle remains unresolved.
Integration 85121 confirmed live; full source-only goal remains active.

Gsensor candidate initialized word is now bounded by authenticated image-A
data region 0x184fc..0x18d90, SHA e0a88003909bb45ae966bfedcbf6e21a5bc83137d26bd36c7f81114fa0034384.
Its value is one. Instruction/data memory alias mapping remains unproved here;
this is not a state initialization or no-writer claim. Neighboring literal
0x20026c74 occurs in a different complex routine; producer remains unresolved.
Integration 85121 confirmed live; full source-only goal stays active.

### Board-pin initializer integrated on macOS (2026-09-08)

The native C-SKY integration completed with 791 passing tests in 21.704 seconds. The initializer adds 104 compiled C bytes; its diagnostic and configuration table add 45 source-data bytes. Codec ownership is now 14,300 compiled C bytes, 156 assembly bytes, 3,090 source-data bytes, 80 metadata bytes, 708 unreachable-fill bytes, and 307,758 retained stock bytes. The 209 C functions account for 225 occurrences.

The macOS apple-clang package build and verify-artifacts both completed successfully. Codec SHA-256: `23452eb8ae7c4848550a1d75afa5f3f6bc8850ffaad04acde19e4a13cd197379`. Package SHA-256: `eccc87d1a2d35a629e96e589360458dfa624b34ac76ed4abeb16159db082cb67` (4,750,780 bytes). Notices copied into the package directory. No hardware qualification or source-only completion is claimed. The source-only goal remains active; gsensor lifecycle and the retained code/data still require reconstruction.

### Gsensor initialized-data mapping checked (2026-09-08)

The state inventory now invokes the stock section analyzer and authenticates the three pinned SDK memory-layout sources before translating the DRAM alias. Address 0x20026c70 maps to package offset 0x18c84, containing the initialized word 1. Four tests pass for section endpoints, rejected out-of-bounds/unaligned addresses, altered stock layout, and altered SDK evidence. This supersedes the earlier unverified mapping note. It does not identify runtime writers, establish hardware behavior, or admit additional source bytes. The full source-only goal remains active.

### Gsensor reader source admission prepared (2026-09-08)

The aggregate reader qualification completed successfully, including decoded before/after-state behavior, printf forwarding, formatter/UART composition and authenticated data mapping. Eleven focused tests pass. The builder now registers the 24-byte C reader and source diagnostic; the initialized state word and its producers remain retained/unresolved. Full integration was started as session 62357, logging to build/gx8002-board/gsensor-integration.log. Do not count the new rows as a verified package checkpoint until that build and package verification complete. The prior verified package remains the 791-test checkpoint.

### Channel lookup recovered (2026-09-08)

Recovered helper at package 0x1104c as C: channel 0 returns 0x2002e050, channel 1 returns 0x2002e1cc, other values return null. Native macOS C-SKY compilation produces 28 bytes exactly matching stock (SHA-256 6bfc14e2268d8a026582d4f40694583902020dd40126f5d1bbfa60033f48e4e9). Decoded stock/source replay passes 520 cases. All four wrapping indices previously identified narrow to byte 255 and return null; the caller branches on null at 0x11638 before the array accesses. This narrows the producer search but does not exclude other writers. Lookup is not yet registered for admission. Gsensor integration session 62357 remains live as authoritatively polled; registered inputs were left unchanged.

Channel lookup regression checkpoint: four tests pass, covering both valid channels, all rejected byte values, absence of implicit argument truncation in the lookup itself, and a mutated rejection predicate. The 520-case verifier now checks the caller instructions at 0x1162a/2c/2e/32/36/38, pinning byte narrowing, original-index preservation, helper target and null rejection. Full integration session 62357 was authoritatively polled and remains live. No registered build input was modified in this checkpoint.

Channel lookup source admission is prepared in verify_gx8002_channel_lookup_source.py. A fresh exported ELF and regenerated report pass reviewed_replacements against the saved JSON baseline, admitting one 28-byte C occurrence at package 0x1104c. A tuple/list serialization mismatch in caller evidence was caught by the gate and corrected before this successful rerun. Registration is deferred until the live gsensor integration (session 62357) completes; no new package ownership is claimed yet.

Upstream UART message candidate identified at pinned SDK commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, authenticated file lvp/common/uart_message_v2.c (git blob b5ae5ebac76df3bb7e60b0209ef71234114a15db). _GetMessageHandle and _UartMessageAsyncRecvCallback structurally match package routines 0x1104c and 0x11624. This is a candidate identification, not upstream equivalence admission. Next verify MESSAGE_HANDLE size/offsets and the complete receive paths. Evidence saved in gx8002-uart-message-upstream-candidates.json.

UART message ABI probe: authenticated upstream declarations compiled on native macOS C-SKY with queue length eight yield MESSAGE_HANDLE size 380 (0x17c), MSG_PACK size 32, cur_recv_pack offset 28, cur_send_pack 60, queue 348, recv_state 368, send_state 372, pmu_lock 376. These match recovered context stride and observed accesses. Probe/report: analyze_gx8002_uart_message_layout.py and gx8002-uart-message-layout.json. This supports upstream identification, not whole-callback equivalence. The 802-test package repin build is session 6883; observed package hash 844046c8b1a2c2effd440c45f7e794ebaad242b1f5d28f5a9e7067a35b6c0b82. Verification remains pending.

### Sensor accessor package verified on macOS

The 802-test integration and apple-clang package build/verify-artifacts completed successfully. Current codec has 210 C functions at 226 occurrences, 14,324 compiled C bytes, 3,113 source-data bytes and 307,711 retained stock bytes. Codec SHA-256 e3b04bad77fd6e5df232ed910bb56d34d358c54ec4514dee49e449a94a3d6227; package SHA-256 844046c8b1a2c2effd440c45f7e794ebaad242b1f5d28f5a9e7067a35b6c0b82. Notices copied. Source-only and hardware-qualified remain false.

After the verified 802-test package checkpoint, channel lookup was registered with its four regression tests; full integration is running as session 74421, log build/gx8002-board/channel-lookup-integration.log. Upstream receive-header helper contains s_recv_header_data_count[2] = {4,4}; stock words at runtime 0x20026c74/78 (package 0x18c88/8c) also equal {4,4}. This identifies a stronger candidate for the neighboring indexed array; full header-copy equivalence remains pending.

Upstream UART header probe now compiles on native macOS C-SKY: 204 code bytes at O2, extracted from authenticated uart_message_v2.c with original copyright retained and CRC delegated by prototype. Stock inlined path 0x116d6..0x11764 uses header boundary 14, counter reset four, little-endian CRC bytes 10..13 and CRC call over ten bytes, consistent with upstream source. The probe retains a visible upstream signedness warning (-Wno-error=sign-compare); it is unlinked and not admitted. Behavioral replay and integration remain pending. Channel lookup integration session 74421 confirmed live.

Upstream UART header probe linked at isolated analysis address 0x10300000 with counters at 0x20026c74 and CRC at 0x102098a8; zero unresolved relocations, source initializer {4,4} verified. A native macOS host harness passed all eleven fragmentation splits on both ports (22 cases), checking assembled bytes, CRC call timing/length and repeated-message counter reset. CRC result is scripted; target/stock behavioral comparison remains pending. Harness preserved as tests/gx8002_uart_header_host_check.c (include generated header.c with build-directory include path when rerunning). Channel integration 74421 remains live.

UART header host verifier is now reproducible via tools/verify_gx8002_uart_header_host.py: rebuilds authenticated upstream target probe, compiles the persistent harness with macOS clang and runs it. Passing coverage: 22 fragmentation cases, four trailing-input/CRC success-failure cases and four followup counter-reset cases. CRC remains scripted and stock target comparison remains pending. Full channel-lookup integration session 74421 was polled and remains live.

Added execute_gx8002_uart_header_probe.py, a bounded interpreter for the linked upstream helper. Initial 28 decoded source cases (two ports, input lengths 0..13) pass expected return and remaining-length checks with CRC result modeled. Memory accesses are bounded by initialized dictionary bytes, unknown instructions reject. Stock inlined-path comparison, detailed ABI restoration checks and broader trace assertions remain pending; no source admission is claimed.

Decoded upstream header target verifier passes 616 combinations: both ports, counters 4..14, input lengths 0..13, CRC success/failure. Checks exact header bytes, counter state, leftover length, conditional cursor advancement, return result, CRC argument boundary and callee-preserved registers. Saved values remain abstract rather than stack-memory execution. Evidence: verify_gx8002_uart_header_target.py and gx8002-uart-header-target-verification.json. This is source-target qualification only; stock inlined execution remains pending.

Stock/upstream header comparison: compare_gx8002_uart_header.py passed 616 finite combinations using decoded stock 0x116d6..0x11764 and linked upstream helper. Compared exact header bytes, count, remaining length, conditional pointer advance and CRC calls/results. Stock path terminates at caller boundaries 0x116a4/0x11802/0x1173c; those are interpreted as incomplete/success/failure for comparison, not full callback execution. CRC remains modeled. The 806-test package rebuild completed; verify-artifacts is session 96152. No full source-only or hardware completion claimed.

806-test package verification completed successfully on macOS: 211 C functions, 227 C occurrences, 14,352 compiled C bytes and 307,683 retained stock bytes. Package SHA remains 844046c8b1a2c2effd440c45f7e794ebaad242b1f5d28f5a9e7067a35b6c0b82. Header comparison now authenticates the full stock ELF payload against IMAGE_SHA and records hashes of both interpreters. Its 616-case rerun passed, as did three explicit stock/source boundary regression tests. Whole callback and hardware remain unqualified.

Header transition extension: verify_gx8002_uart_header_transition.py passes 30 decoded cases across both ports and body lengths 1,2,4,255,256,32768,65535 with CRC pass/fail plus incomplete headers. Stock success reads length from context+0x24, sets recv_state at +0x170 to 2; failure sets zero, incomplete keeps one. Zero-body queue path deliberately remains outside this bounded model and raises rather than silently succeeding. Full callback reconstruction remains active.

Empty-header publication: verify_gx8002_uart_empty_header.py authenticates stock and decodes 0x1180a..0x11828. Six cases pass for both ports and modeled queue returns 0/1/-1. Ordered writes set receive state zero, packet port, packet length zero; queue receives the 32-byte packet before magic/length clearing. Call runtime target is 0x100261b8. Caller clobbers modeled and queue status ignored by this path. Queue internals and whole callback composition remain pending; no source-only completion claimed.

Empty header/queue composition passed 256 cases via verify_gx8002_uart_empty_header_queue.py: both ports, decoded stock/upstream LvpQueuePut and every aligned head/tail position for eight 32-byte slots. Real packet snapshot from outer decoder feeds queue; copied bytes/tail updates or full-queue no-write behavior match independent expected memory. Outer state/magic/length cleanup still occurs regardless of queue result. Separate frames and translated addresses remain explicit limits; no concurrent or whole callback qualification.

UART body reconstruction started: authenticated upstream _UartMessageAsyncRecvCheckBody extracted with copyright preserved, compiles as a 384-byte native C-SKY object via build_gx8002_uart_body_upstream_probe.py. Stock entry 0x11278 narrows channel for lookup, subtracts optional four-byte trailer, and accesses body counter at context base+0x308+4*port, consistent with upstream opening logic. Probe uses analysis-only external declarations and unresolved relocations, so dependency ABI and all copy/DMA/completion paths remain pending. No source admission claimed.

Body probe dependency review corrected port/length signedness and buffer pointer declarations to match pinned gx_uart.h; authenticated uart_message_v2.h, lvp_queue.h and gx_uart.h before compiling. Probe remains 384 bytes. Recorded stock body code extent/hash and candidate async-start/stop/buffer, queue, callback and storage addresses in gx8002-uart-body-bindings.json. Allocation preparation appears inlined; bindings are not called-routine equivalence claims.

Body probe now includes authenticated upstream _UartMessagePrepareRecv, replacing its external declaration with registration lookup, capacity/offset checks and assignment. Compiles to 480 bytes; linked at isolated analysis address 0x10301000 with candidate UART/queue/callback globals and body counters at 0x2002e358. Link has no unresolved symbols or relocations. Registration array candidate 0x2002e360 has 16 entries with 28-byte stride in stock. This is still an analysis artifact: no firmware placement/admission or behavioral equivalence yet.

Receive preparation host harness: generated prepare.c from authenticated upstream preparation function and compiled tests/gx8002_uart_prepare_host_check.c with native macOS clang. 128 combinations (16 registration positions, two trailer flags, four starting offsets) plus three rejection cases passed. Confirms body pointer assignment, offset increment/reset and failure clearing. Probe builder preserves extracted preparation source for repeat runs. Target ABI/stock preparation comparison remains pending; no firmware admission.

Preparation host coverage expanded to 138 cases and made reproducible with verify_gx8002_uart_prepare_host.py. New cases establish first-match rejection despite a later usable registration, full-packet-length wrap check despite trailer-excluded capacity, and rejection for tested flagged lengths below four. Rebuilt authenticated source and native harness passed. These characterize upstream behavior, not target equivalence or source-only completion.

C-SKY registration ABI measured from authenticated upstream: sizeof UART_MSG_REGIST=28, offsets port0/msg_id4/buffer8/capacity12/offset16/callback20/priv24. Analyzer rejects mismatch against stock field accesses. Body builder now also emits standalone prepare-target.elf at isolated 0x10302000 with registry 0x2002e360 for target replay. Build passed; behavior remains unqualified until decoded comparison.

Preparation target execution added: execute_gx8002_uart_prepare.py handles the decoded standalone upstream helper with bounded target memory and callee-preserved register checks. verify_gx8002_uart_prepare_target.py passed 576 combinations over match positions 0/7/15/absent, flags, lengths, offsets, capacities and null/non-null buffers. Exact final memory matches independent preparation semantics, including offset reset before null-buffer rejection. Stock inlined preparation comparison remains pending; no admission claimed.

Stock preparation comparison passed 576 combinations. compare_gx8002_uart_prepare.py authenticates stock ELF bytes and compares decoded inlined stock 0x11304 onward against the upstream standalone target helper. Both return classification, exact final memory and ordered writes match. Stock stops at 0x11386/0x112fa caller continuations; full body copy, asynchronous transfers and callback behavior remain pending.

Stock body copy slice now passes 160 decoded cases across ports, trailer flags, body sizes, starting counts and available input. Verifies exact destination bytes including untouched neighbors, counts/remaining length, completion cursor advance, return value and trailer state. Entry 0x113b0 assumes prior validation/preparation; partial stop 0x1140c precedes async scheduling. Initial 500-instruction bound was insufficient for 64-byte loop and was raised to 2000; rerun passed. Source-target comparison remains pending.

Body-copy comparison now passes 160 decoded stock/upstream cases via compare_gx8002_uart_body_copy.py. Upstream execution begins at linked 0x1030104e; both paths compare full modeled memory, completed return and partial continuation boundaries. Includes source postincrement loads/indexed stores and stock distinct loop structure. Async scheduling, entry validation and whole-body composition remain pending.

Async scheduling stock slice passes 2240 decoded cases (ports, all 16 base alignments, five received counts, seven remaining lengths, helper success/failure). Checks strict >32 threshold and destination past first 16-byte boundary, stop-then-buffer call order, rounded transfer length, callback/private argument, counter advance and cursor reset. Helpers modeled with caller clobbers. Source-target scheduling comparison and physical transfers remain pending.

Async scheduling stock/upstream comparison passes 2240 cases via compare_gx8002_uart_body_schedule.py. Decoded linked upstream branch at 0x103010dc and stock 0x1140c agree on helper call sequence/arguments, zero return and complete final modeled memory across alignments, thresholds and helper return codes. Instruction write order is not claimed identical; concurrent observers and actual DMA/helper execution remain unqualified. Whole-body composition remains pending.

Body input validation comparison passed 12 decoded stock/upstream cases: both ports, null buffer/null length pointer/empty input, restart helper success/failure. Exact restart arguments and -1 return match. Important scope: the original helper dereferences recv_buffer_p before its null check, so null pointer-to-pointer is not treated as safely rejected. This slice starts after that dereference; whole-function entry validation remains pending.

Already-complete body branch comparison passes 36 decoded stock/upstream cases (ports, trailer flags, lengths, helper results). Checks counter reset, restart-before-publication sequence, exact queued packet bytes, magic/length cleanup for unflagged packets, trailer state for flagged packets, zero return and final memory. Helpers remain modeled and entry assumes count already equals body size. Whole-body continuous execution remains pending.

Continuous body execution implemented in execute_gx8002_uart_body_full.py. compare_gx8002_uart_body_full.py passes 72 stock/upstream entry-to-return cases over ports, trailer flags, initial counts, input sizes and helper results. Compares return, all non-stack modeled memory, helper call sequence and callee-preserved registers; source/stock frames modeled separately. Initial coverage uses 20-byte bodies and valid registration/buffers, so broader DMA and rejection cases remain pending. No firmware source admission yet.

Continuous body comparison expanded to 2592 passing cases with body sizes 20/80/128, alignments 0/1/15 and valid/missing/undersized/null registration modes. Coverage counters: {'async': 608, 'restart': 840, 'queue': 144, 'failure': 1200}. Both whole decoded functions agree on return, non-stack memory, helper call sequence and preserved registers. Helpers remain modeled, actual DMA and source admission pending.

UART body original-entry candidate built at 0x10207cec, package 0x11278: 480 compiled bytes fit the 500-byte stock region ending 0x1146c. compare_gx8002_uart_body_full.verify(original_entry=True) passes all 2592 continuous cases; saved gx8002-uart-body-original-entry.json. Candidate ELF/disassembly in build/gx8002-uart-body-probe. No unresolved text relocations. Reviewed source admission, initialized-state ownership, helper qualification and whole-device behavior remain pending.

Original-entry body comparison expanded to 7776 passing continuous cases. Helper statuses now vary independently for restart, stop, async-buffer and queue (in addition to uniform success/failure), avoiding an assumption that all helpers share a return result. Coverage: async1824/restart2520/queue432/failure3600. Interpreter now checks exact pop register list and rejects indexed word writes outside modeled memory. Actual helper execution, independent source-admission review and hardware remain pending.

Whole-body lookup composition: full interpreter now accepts a lookup hook; comparator refreshes the admitted channel-lookup dependency and invokes its decoded C-SKY instructions at 0x10207ac0 for every lookup in both bodies. Original-entry 7776-case comparison passed. Lookup remains a separate decoded frame, but no longer a constant-table model in this run. UART/queue boundaries and physical effects remain modeled.

Whole-body queue composition passed: verify_gx8002_uart_body_queue.py refreshes recovered queue source and runs its decoded put code on each published packet, testing full/available states at tail wrap. 1728 queue executions across 7776 body cases passed exact memory expectations. Separate queue memory translation remains explicit; outer hook currently consumes available-state return, while baseline independently varies failure status. UART helpers and actual DMA remain modeled.

UART receive controls reconstructed as C in runtime_gx8002_uart_receive_control.c. Native macOS build emits start52 bytes at 0x1020368c and stop40 bytes at 0x102036c0, fitting original envelopes. Both bind IRQ save/restore at 0x10025560/6c. Start rejects null callback, sets descriptor mode/callback/private then enables receive interrupt; stop clears callbacks and receive interrupt. Compiled bytes differ from stock; decoded MMIO/order/IRQ-token qualification remains pending.

### UART receive-control and body composition checkpoint

Reconstructed receive start/stop C builds natively on macOS at the original
entries, fitting the 52/40-byte envelopes. The authenticated stock wrapper and
compiled candidates pass 192 ordered descriptor/MMIO/IRQ-token comparisons
against an independent contract. An additional 384 combinations execute the
stock and authenticated upstream PSR save/restore leaves, including initially
disabled interrupts and restoration of all processor-state bits.

The continuous upstream packet-body comparison now accepts decoded receive
control hooks. All 7,776 body cases pass at the original entry with 30,240 start
and 21,888 stop executions across stock/source implementations and three
register/PSR states. Each helper uses an isolated descriptor state; persistent
cross-call UART state and physical interrupt delivery are not claimed. The
async-buffer helper remains modeled. These candidates are not admitted into
the package yet; the last verified package remains 211 C functions with
307,683 retained codec bytes. Reports: gx8002-uart-receive-control-verification,
gx8002-uart-receive-irq, and gx8002-uart-body-control JSON under docs/research.

### Asynchronous UART buffer reconstruction

Added runtime_gx8002_uart_receive_buffer.c and native macOS candidate builder/
decoded verifier. The stock entry 0xcd0c (runtime 0x10203780) compares against
compiled C across 2,304 cases: null buffer/callback, zero and extreme lengths,
fifth stack argument, DMA selection, IRQ tokens, MMIO words, and DMA results.
Full ordered memory/helper traces and callee-saved registers are compared.

Inspection of the DMA callee at package 0xc71c demonstrated that it consumes
r1/r2 as buffer/length, in addition to r0 descriptor. The C prototype/call and
verifier explicitly preserve/check all three; a descriptor-only model was
insufficient. DMA internals remain unreconstructed, and IRQ leaves are modeled
in this particular verifier. The candidate is 100 bytes versus a 96-byte stock
envelope and is not admitted. Five initial compiler-flag probes did not reduce
size; no overlapping package placement has been performed. Latest candidate
SHA256 a46486e5e5250afa82d7bfe7d516f557cad3de67dff0df3d959d826eaccf38e4.

### UART DMA setup C and decoded qualification

Reconstructed package 0xc71c/runtime 0x10203190 as
runtime_gx8002_uart_receive_dma.c. Native macOS compilation produces 140 bytes,
fitting the stock envelope. Uses the authenticated upstream gx_dma_ahb.h
(blob 0a63d02cb756c4ca9597f595146cbdc95cf9d46d at SDK commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5).

The decoded stock/source comparison passes 768 cases with ordered memory
accesses, five helper boundaries, preserved caller buffer/length, callee-saved
registers, signed channel failure, invalid port failure, and differing results
from the two burst lookups. An independent transfer-call oracle checks all 12
configuration words against their upstream fields, as well as destination,
source, length and channel. Cache/select/burst/callback/transfer helpers remain
modeled; this function is not admitted yet. Candidate SHA256
7e8266b0b1860efb076d2dffd26d8c51aa5bb8e15a577760e054e1b1cba57581.
Reports: gx8002-uart-receive-dma-candidate.json and
 gx8002-uart-receive-dma-verification.json. Package ownership counts unchanged.

### UART DMA burst source and composition

Added runtime_gx8002_uart_dma_burst.c, using the authenticated upstream DMA
burst enumeration. Both volatile descriptor reads (offsets 0x34 and 0x38)
remain ordered even when only one direction is selected. Unsupported lengths
map to the single-transfer enumeration. Native macOS candidate is 114 bytes
in the 116-byte envelope at package 0xc5dc/runtime 0x10203050; SHA256
 dcb19548b684924c227ade43682f3012a7bb2c2ce260097aa486c9eb0d0314c4.

8,232 decoded stock/source cases pass independent mapping, read-order and ABI
contracts. 180 additional DMA setup compositions execute 300 burst calls
across all stock/source combinations, including a changed receive burst size
between the two lookups and the invalid-port early return. The 768 baseline
DMA setup cases also pass after adding the optional leaf hook. Remaining DMA
cache/channel/callback/transfer dependencies are still modeled; source
admission and package integration remain pending. Reports are
 gx8002-uart-dma-burst-verification.json and
 gx8002-uart-dma-burst-composition.json under docs/research.

### DMA callback storage and channel allocation candidates

Recovered DMA callback registration at package 0xd0f0 as C. The native macOS
candidate is 16 bytes in the 20-byte envelope and passes 189 decoded ordered
write/ABI cases, including null callback/private values and wrapping channel
arithmetic. Extreme indices are arithmetic tests, not claims of valid storage.
The leaf writes callback at 0x20027320 + 4*channel and private data eight bytes
later. Candidate SHA256
61d8d6c721972003f2d052d571f3027af0396741219eb8d167f5fd9621524121.

Recovered channel selection at package 0xcfd8 as C. It reads channel count at
0x2002e940, scans allocation bytes at 0x2002ecac under saved interrupt state,
reserves the first zero byte, calls runtime 0x10025080 with (25,1), and restores
interrupt state on both exits. It compiles to 76 bytes in the 76-byte envelope;
SHA256 a945f0a79b5690ff020f7d9a81c04080ddd3ad9b5d759abb85aab0fc5f21113e.
Decoded selection qualification and resource-helper identification remain next.
Neither candidate has been admitted into the package. Reports use the
 gx8002-dma-callback and gx8002-dma-select prefixes under docs/research.

### DMA selection decoded qualification and clock gate reuse

The 76-byte channel selector passes 6,132 decoded stock/source cases against
an independent ordered-access oracle: every occupancy bit pattern for counts
0..8, nonzero occupied values 1/128/255, and four IRQ tokens. Checks cover first
free channel, no-free-channel/zero-count failures, reservation before the
resource call, and restoration of the original token under caller clobbers.
The tested channel counts do not establish actual hardware capacity.

Identified runtime 0x10025080 as the previously reconstructed platform clock
gate. DMA uses module 25, enable 1. A composed verifier executes the existing
stock/source gate in 72 combinations, making 36 gate calls only after a free
channel was reserved. Gate effects match its independent oracle. The module
lookup and configuration table remain modeled/stock-backed in this proof;
physical clock behavior is unqualified. Reports: gx8002-dma-select-verification
and gx8002-dma-select-gate JSON. No package admission or ownership change yet.

### DMA transfer candidate and initialized channel domain

Added runtime_gx8002_dma_transfer.c for package 0xd104/runtime 0x10203b78.
It forwards the fifth stack argument to configuration at 0x102038f4, exits
only on -1, writes the channel mask to device+0x310, calls descriptor cache
at 0x10025664 with state[channel+218] and 416 bytes, rereads the device base,
and writes device+0x3a0. Native macOS candidate is 76 bytes against 72 available;
not admitted and decoded behavior qualification remains pending. The shift
uses the allocated-channel caller contract; out-of-range shifts are not
claimed. Latest candidate SHA cb3ef966a683ee3d791d4a04094b288f0abae47572fc1b103733ce67d5011560.

Authenticated initialization instructions at package 0xd14c show state base
0x2002e93c, device base 0xa1000000, and channel count 2 stored at 0x2002e940.
Analyzer/report gx8002-dma-channel-count verifies these decoded instructions
against the authenticated stock image. Reachability and later count mutation
remain unproven; this evidence establishes initialization, not physical
capacity. Cache helpers at package 0x1761c and 0x17678 have line-operation
loops with selector bits 2 and 8 respectively; reconstruction remains next.

### DMA transfer qualification and existing cache source reuse

The transfer candidate passes 384 decoded stock/source cases in initialized
channels 0/1, with fifth stack argument forwarding, exact -1 error semantics,
ordered MMIO writes, register preservation, and a device-base mutation across
the modeled cache call to verify the second volatile load. An equivalent
index-expression change did not reduce its 76-byte size (72-byte envelope).

Correction to the preceding cache note: runtime 0x10025664/package 0x17678
already has admitted dcache_clean_range source. Reused and refreshed that
existing verifier, then composed its decoded stock/source leaf with transfer
in 24 combinations. All pass; 16 cache calls each emit the expected 26 line
commands for 416 bytes. The setup/configuration dependency remains modeled,
and no hardware cache coherence claim is made. Reports: gx8002-dma-transfer-
verification.json and gx8002-dma-transfer-cache.json. No package change yet.

### DMA configuration dependency: bus-address translation

Inspected the full configuration routine (package 0xce80..0xcfd8). It builds
control/config fields, clears channel status, translates source/destination,
writes channel registers, bounds linked-list count, builds descriptors, and
translates the descriptor-list address. Nested source work remains necessary.

Recovered its address translator at package 0xd1ec/runtime 0x10203c60 as
runtime_gx8002_dma_bus_address.c. Native macOS C compilation is byte-identical
to the complete 20-byte stock routine, SHA256
5fbc1188c3db999213e1792838696590b573194f67c658437e35149b5e49c419.
131,388 decoded stock/source cases pass an independent interval oracle: map
[0x10000000,0x30000000) to low 28 bits, preserve other addresses. Corpus covers
both ends of every 64KiB block plus dense alias boundaries and wraparound.
Register preservation is checked. Not yet admitted; physical addressability
is not established by this arithmetic proof. Report:
gx8002-dma-bus-address-verification.json. Package ownership remains unchanged.

### DMA status clearing and descriptor candidate

Status clearing at package 0xcd90 is reconstructed as C, fits its 36-byte
space, and passes 96 decoded stock/source ordered-access and ABI cases. The
single state-base read and all five mask writes (offsets 0x338,0x340,0x348,
0x350,0x358) match an independent oracle. Shift values beyond initialized
channels 0/1 are arithmetic tests only. SHA256
b66a6721e83a15765cb80a3b0b366b842f6ec9666b23c1ee1de0024e47151790.

Inspected descriptor construction at 0xcdb4..0xce80 and added an unqualified
C candidate. It uses six-word descriptor stride, leaves word five untouched,
sets last-link pointer zero, clears final control bits 27/28, and computes
last length using signed remainder with exact multiples represented as 4095.
Direction increments preserve stock unsigned-halfword values, notably
0xf001 rather than replacing it with a signed decrement. Native candidate
is 224 bytes versus 204 available, with no additional rodata section.
Decoded behavior and valid count-domain qualification remain pending. Neither
routine is admitted; package ownership remains unchanged. Reports use
 gx8002-dma-clear and gx8002-dma-descriptors prefixes under docs/research.

### Descriptor native macOS contract checks

Added gx8002_dma_descriptors_host_check.c and native clang runner. 15,552
cases pass with address and undefined-behavior sanitizers: counts 0..17,
all 16 source/destination direction combinations, widths 0/1/2/4/128/255,
length boundaries and negative arithmetic probes. Checks cover full output
against an independent indexed oracle, untouched sixth words and trailing
sentinels, unchanged input pattern, and every next-link translation argument.
Count zero intentionally emits the final descriptor, matching the observed
stock control flow; this is not a claim that callers use zero-length DMA.

This host proof does not replace decoded stock/source instruction comparison,
which remains next. The candidate still occupies 224 bytes in a 204-byte
envelope and is not admitted. Host runner report:
gx8002-dma-descriptors-host.json. No package ownership changes.

### Descriptor decoded stock/source and bus composition

Added a bounded byte-memory descriptor interpreter with checked callee-saved
registers and stack restoration. The target C and authenticated stock pass
1,920 cases comparing all output bytes plus ordered pattern reads, descriptor
writes, and translation calls. Counts 0/1/2/3/17, all direction combinations,
widths 0/1/4/255, and six signed length probes are covered. Stack temporaries
and saved frames are abstracted; pattern/output buffers are separate.

A second run composes the byte-identical C bus translator as decoded code:
14,592 nested translation calls pass across the same descriptor corpus.
The translator's own 131,388-case proof is refreshed. Reports:
gx8002-dma-descriptors-verification.json and gx8002-dma-descriptors-bus.json.
Descriptor candidate still exceeds its stock envelope by 20 bytes and remains
unadmitted. These proofs do not establish physical DMA behavior. No package
ownership changes in this checkpoint.

### Full DMA configuration C candidate

Added runtime_gx8002_dma_configure.c for package 0xce80..0xcfd8, connecting
reconstructed clear, bus-address and descriptor helpers. Native macOS C builds
to 324 bytes within the 344-byte envelope. The authenticated upstream
GX_DMA_AHB_CH_CONFIG type has compile-time checks for its 48-byte size and
all 12 stock field offsets. Candidate preserves staged validation of address
updates, master selectors and handshake selectors; register writes occur
before the descriptor-list size rejection, as in stock. Device-base reads
around translation calls remain separate volatile accesses. The list count
uses stock signed quotient/remainder followed by unsigned byte-bound check.

This is a build candidate only: full decoded stock/source configuration
comparison, including the late failure path and nested calls, remains pending.
The width/channel caller domains and negative list-count behavior need explicit
qualification. Descriptor construction still exceeds its individual envelope;
no overlapping code has been placed into any firmware package. Report:
gx8002-dma-configure-candidate.json. Goal and package ownership remain unchanged.

### Configuration validation decoded comparison

Added bounded entry-to-first-helper/return interpreters for stock and compiled
configuration. 46,656 selector combinations pass an independent validation
oracle, including values 0,1,2,3,4 and UINT32_MAX for each of the six validated
fields. Ordered configuration reads match exactly; invalid fields return -1
before any external write, while valid cases reach the clear helper with the
channel intact. Rejection paths verify saved-register and stack restoration.

This is deliberately a partial control-flow proof: successful cases stop at
the clear call, so register programming, late descriptor-size failure and
nested descriptor construction still require full-path comparison. Report:
gx8002-dma-configure-validation.json. Candidate/source admission and package
ownership remain unchanged.

### Full configuration decoded comparison

Continuous configuration entry-to-return comparison passes 576 stock/source
cases across initialized channels 0/1, master and handshake selectors, widths
0/1/2/7, and nine length boundaries including signed probes and descriptor
capacity limits. External ordered reads/writes and clear/translation/descriptor
call arguments match. An independent oracle checks all register values, exact
late-failure write count, list-count rejection, and every descriptor argument.

The late size failure leaves five register writes, while successful setup adds
the translated list-pointer write. Saved registers and stack restoration are
checked at every return. Nested helpers remain modeled in this run; the device
base is fixed and mutable-state composition remains work to do. Report:
gx8002-dma-configure-verification.json. No package admission yet.

### Configuration nested source composition

Configuration's 576-case corpus now runs decoded clear and address-translation
leaves: 2,304 clear executions and 6,144 bus translations pass across stock/
source combinations. A separate composition passes the actual configuration
arguments to decoded stock/source descriptor builders at the actual output
address, completing 1,536 descriptor executions. Independent checks cover the
fixed source/incrementing destination pattern selected by this corpus, control
bits, and the untouched sixth descriptor word.

Helpers still execute in isolated memory/frames, with fixed device base for
clear and modeled translation inside this descriptor composition. Shared-memory
whole-chain execution and package placement remain incomplete. Reports:
gx8002-dma-configure-leaves.json and gx8002-dma-configure-descriptors.json.
The standalone descriptor proof is refreshed. No package ownership changes.

### Descriptor candidate now fits original placement

Reused the accumulated unsigned source/destination offsets for the final
entry, and applied the local GCC flag -fno-tree-scev-cprop after measured
compiler probes. The descriptor builder shrank from 224 to 156 bytes, fitting
the 204-byte envelope without binary extraction or manual machine-code edits.
The builder records the additional flag. Other compiler settings are unchanged.

Refreshed proofs on the compact candidate all pass: 1,920 decoded comparisons,
15,552 native clang ASan/UBSan cases, 14,592 decoded address-translation calls,
and 1,536 descriptor executions composed with configuration. No package
admission yet. The previously recorded descriptor-size blocker is resolved;
UART receive-buffer and DMA transfer size excesses remain separate work.

### Remaining compact-placement investigation

Measured seven optimization-pass flags, three optimization levels, and ten
register/control-flow flags for each of DMA transfer and UART receive-buffer.
None reduced the current 76/100-byte candidates to their 72/96-byte envelopes.
Do not repeat these identical probes; saved results are
 gx8002-dma-uart-fit-probes.json and gx8002-dma-uart-register-probes.json.
-O1/-O2/-Oz also failed to improve either minimum.

Expressed UART descriptor storage as an external typed 32-word-stride array,
with an explicit linker binding to 0x20026a94. This makes the storage dependency
visible for eventual source storage reconstruction and produces identical code
bytes. All 2,304 decoded receive-buffer cases pass after the change. The state
array definition and remaining compact placement remain pending. No package
changes; these candidates remain unadmitted. Next work should pursue source
layout/code-generation changes or reviewed relocation, not repeat flag probes.

### Receive-side cache range reconstruction

Unsigned-16 and signed descriptor-index experiments did not shrink DMA
transfer; restored the original unsigned indexing expression and refreshed
its 384 decoded cases successfully. No indexing restriction was retained.

Reconstructed the receive cache helper at package 0x1761c/runtime 0x10025608
as runtime_gx8002_dcache_invalid_range.c. It reuses the reviewed clean-range
C structure with the stock operation selector 2 rather than 8. The native
macOS candidate is 88 bytes in the 92-byte envelope. 12,864 complete decoded
stock/source comparisons and 144 huge-positive-size 65-write prefix checks
pass, covering signed sizes, alignment, address wrapping and preserved ABI.
The upstream gx_dcache.h is authenticated; the copied SNPU object reference
is explicitly only unrelated identity evidence, not this helper's provenance.

This completes a candidate for a previously modeled receive-DMA dependency;
source admission and caller composition remain pending. Physical cache
coherence is unqualified. Report: gx8002-dcache-invalid-range-verification.json.
No package ownership change yet.

### Receive DMA cache and allocator composition

Receive DMA now has optional decoded cache and allocator hooks. 504 composed
cache cases pass across stock/source caller and leaf combinations, with
stored cache buffer/length deliberately differing from transfer arguments.
Signed/nonpositive sizes, alignment and wrapping addresses are included.
Cache processing precedes selection even when allocation fails or port is
invalid. Both component baseline verifiers refresh successfully.

144 allocator compositions pass over both initialized channels, four occupancy
patterns, three IRQ tokens and ports 0/1/2. The selected channel is written to
the UART descriptor only after successful allocation. Invalid port failure
occurs after reservation, with no added cleanup, preserving stock behavior.
Isolated allocator state and modeled IRQ/clock boundaries remain limits.
Reports: gx8002-uart-receive-dma-cache.json and
 gx8002-uart-receive-dma-select.json. No source admission/package change yet.

### Receive DMA registration and completion handler

72 stock/source receive-DMA/callback-registration combinations pass, with 32
actual decoded registration calls. They check channel-indexed callback/private
stores, suppression on failed allocation/invalid port, and registration before
transfer setup. Report: gx8002-uart-receive-dma-callback.json.

Traced registered completion entry 0x102030e4/package 0xc670. Added
runtime_gx8002_uart_receive_complete.c: release stored channel, set it to -1,
read length then buffer, invoke cache helper 0x100256c0, then read callback,
private data and port and call it. Native candidate is 34 bytes within 36;
SHA256 5c1921ed0c842f388c3dcb96b4c7641389fc995098ac364f94842e650271020c.
Decoded completion behavior, release and cache dependencies still need
qualification. No null callback guard was added. Nothing in this checkpoint
is admitted into the package; ownership counts remain unchanged.

### Receive completion qualification and deallocation source

Receive completion passes 288 decoded stock/source cases with an independent
ordered-access oracle. Controlled release/cache mutations verify that buffer,
length, callback, private data and port are reread at their stock boundaries.
Callee-saved registers and stack restoration are checked; callbacks remain
modeled. Report: gx8002-uart-receive-complete-verification.json.

The release entry at 0xd0c4 wraps deallocation at 0xd024. Added C for the
latter: clear allocation byte under saved IRQ state, scan channel count, keep
clock active only if an allocation byte equals exactly one, otherwise disable
module 25, then restore IRQ state. Exact-one differs from selection's nonzero
check and is preserved. Native candidate and report:
gx8002-dma-deallocate-candidate.json. Decoded qualification remains pending.
No package changes or admission in this checkpoint.

### Deallocation qualification and release wrapper candidate

Deallocation passes 5,008 decoded stock/source cases against an independent
ordered-memory/clock-call oracle: all allocation combinations from 0/1/2/255
for counts 1..4, every in-table release channel, and four IRQ tokens. Exact-one
scan behavior, byte clearing, clock-disable conditions and ABI are preserved.
Counts above initialized two channels are bounded algorithm probes only.

Expressed allocation/count via one explicit external DMA-state symbol. This
keeps state ownership visible but remains 72 bytes versus 68 available. All
5,008 cases pass after this change. Added runtime_gx8002_dma_release.c wrapper
at package 0xd0c4: native C is byte-identical to stock, eight bytes, SHA256
 a88262c0eff797a3425044f38b2fd2c7c3c5fdb25d1b8230d19dcaf6d7f62031.
Wrapper decoded composition remains pending. Reports use gx8002-dma-deallocate
and gx8002-dma-release prefixes. No package admission or ownership changes.

### Release composition and completion cache candidate

The release wrapper's exact push/call/pop sequence composes with decoded
stock/source deallocation in 384 cases across initialized channels, allocation
bytes 0/1/2/255 and three IRQ tokens. The nested deallocator retains its own
abstract frame; IRQ and clock calls remain modeled. Report:
gx8002-dma-release-verification.json.

Recovered completion cache helper at package 0x176d4/runtime 0x100256c0 as
runtime_gx8002_dcache_clean_invalid_range.c, preserving command selector 10.
Native macOS build is 88 bytes in the 92-byte envelope. 12,864 full decoded
stock/source cases and 144 huge-size prefixes pass for ordered cache commands,
signed-size semantics, alignment and address wrapping. The unrelated SNPU
object identity is not claimed as provenance. Physical coherence, caller
composition and source admission remain pending. Report:
gx8002-dcache-clean-invalid-range-verification.json. No package changes.

### Receive completion with decoded release and cache leaves

128 composed completion cases pass across stock/source caller and leaf
variants, both initialized channels, four allocation patterns and four cache
sizes. Release executes the reconstructed wrapper and decoded deallocator;
completion cache executes the decoded clean/invalidate range helper. Ordered
release then cache then callback, stored channel reset to -1, allocator effects,
and exact cache commands are checked. Component baseline verifiers refresh.

These remain separate descriptor/allocation/cache frames, with modeled final
callback delivery and modeled IRQ/clock internals inside deallocation. Report:
gx8002-uart-complete-leaves.json. Shared-state whole-chain validation and
package admission remain outstanding; no package ownership changes.

### Persistent DMA allocation lifecycle

Added verify_gx8002_dma_allocation_lifecycle.py to carry actual decoded
allocation-byte results into subsequent select/deallocate calls. All 5,184
four-operation sequences pass (20,736 decoded calls), spanning every sequence
of select/free0/free1, all initial byte pairs from 0/1/2/255, and stock/source
selector/deallocator combinations. An independent persistent-state oracle
checks returned channels, reuse/exhaustion/repeated frees, clock calls and
per-operation IRQ save/restore tokens.

This removes reset-between-calls assumptions for the allocation table, but
per-call register frames are still reconstructed and IRQ/clock internals are
modeled. It does not prove concurrent or physical DMA ownership. Report:
gx8002-dma-allocation-lifecycle.json. Source admission and package integration
remain outstanding; package ownership unchanged.

### Consolidated DMA/UART source link

Added link_gx8002_dma_uart_source.py. It compiles 17 reconstructed source units
using the native macOS toolchain and authenticated upstream DMA header, then
links them together into a 1,532-byte analysis .text section. No undefined
symbols or unresolved relocations remain. Cache dependency names resolve to
the three C range implementations; DMA/configuration/descriptor/release and
receive calls link directly between source objects.

This is not a firmware image or an admission proof. The link uses a relocated
analysis address, external IRQ/clock and state bindings, and still contains
original numeric callback addresses. Those callback bindings must be made
relocation-aware before this layout can execute. Original-slot excesses are
not solved merely by this compact link. Persistent storage initialization,
full type compatibility and whole-firmware integration remain outstanding.
Report: gx8002-dma-uart-source-link.json; artifact:
build/gx8002-dma-uart-source/dma-uart.elf. Package ownership unchanged.

### Relocation-aware receive completion callback

Replaced receive-DMA's numeric completion address with a C function symbol.
The original-placement builder binds that symbol to 0x102030e4 and its 768
stock/source cases still pass. The consolidated macOS link instead resolves
it to the actual reconstructed completion routine within relocated .text.

The link check now requires an R_CKCORE_ADDR32 callback-symbol relocation in
the input object and checks the relocated pointer in the linked receive body,
rejecting the old numeric address. All 17 source units still link in 1,532
bytes with no unresolved symbols/relocations. This resolves the explicitly
recorded callback relocation issue for this subset; it does not prove the
whole analysis ELF runnable. State/IRQ/clock external bindings and full
firmware integration remain. Report: gx8002-dma-uart-source-link.json.

### DMA initialization and inferred C layout

Reconstructed full initializer 0xd14c..0xd1cc as C with a relocatable IRQ
handler symbol. Native macOS candidate is 120 bytes in 128 available. It sets
device/count, computes both aligned list addresses, clears allocation bytes,
enables module 25, writes reset/status/config registers, disables the clock,
and registers IRQ 10. Ordered decoded qualification remains pending.

Added runtime_gx8002_dma_layout.h with compile-time offsets: device 0, count 4,
two 432-byte descriptor storage regions at 8, list-address words at 0x368 and
allocation bytes at 0x370. Inferred padded size is 884; it is not yet a claim
of full linker storage ownership. Static assertions compile with the native
cross-compiler. No state instance or package replacement has been admitted.
Report: gx8002-dma-initialize-candidate.json.

### DMA initialization and interrupt delivery reconstruction (macOS)

- Added decoded initialization verification: 18 stock/source cases check state
  layout writes, descriptor alignment, allocation reset, clock calls, ordered
  MMIO writes, and IRQ 10 registration. Clock-enable mutation verifies that the
  device base is loaded after the helper. This does not establish RAM ownership
  or physical IRQ delivery.
- Reconstructed `runtime_gx8002_dma_irq_handler.c`: one status snapshot, exactly
  two channels, clear then device-base reload and disable write, deallocation,
  then callback/private-data lookup and invocation. Return is zero. Updated the
  initializer's handler prototype to match this recovered return type.
- Native C-SKY GCC builds the handler to 92 bytes (stock envelope 92) using
  `--param=max-completely-peel-times=0`; default loop expansion produced 108.
  168 decoded comparisons plus an independent sequencing oracle passed,
  covering null callbacks, high status bits, caller clobbers, and helper-driven
  device/callback/private/status changes. A unittest reruns this qualification.
- The analysis-only DMA/UART link now contains 19 source units, 1744 text bytes,
  SHA-256 `10fe903c9c65c506a1b804c9d6cd4a59739493d265f9247f0a220f981027a3ab`,
  with no unresolved symbols/relocations. State, clock, IRQ registration and
  interrupt-mask helpers still use explicit external bindings.
- These functions remain unadmitted to the firmware package. The last packaged
  checkpoint and its 307683 retained codec bytes are unchanged. Next work is
  composed interrupt-to-completion execution and integration qualification;
  passing isolated models or a relocated analysis link is not runnable firmware.

### Composed DMA IRQ to UART completion

- Added `verify_gx8002_dma_irq_completion.py` and a regression test. 5120 cases
  execute decoded stock/source IRQ handlers with decoded clear, deallocation,
  release, UART completion and cache routines. Allocation bytes persist across
  both channel visits and the callback's second deallocation.
- Verified 9216 deallocation calls and 3072 completions with an independent
  ordering/allocation oracle. Cases vary pending status, callback registration,
  allocation values (0, 1, 2, 255), and completion sizes (0, 77, 416, -1).
  Both IRQ regression tests passed in 4.035 seconds on macOS.
- Extended completion execution to accept the actual descriptor address, so
  channel 1 uses its distinct descriptor. Private pointers come through the
  decoded IRQ callback load. Descriptor channel clearing and final application
  callback arguments are checked.
- Corrected the DMA handler to the existing IRQ ABI `int (int, void *)` and
  registration to `void request_irq(int, int (*)(int, void *), void *)`, matching
  the existing reconstructed IRQ source and the pinned SDK gx_irq.h. The handler
  ignores both parameters; its compiled code size remains 92 bytes.
- The composed verifier still uses separate routine register/MMIO frames;
  IRQ masking, clock internals and the final application callback are modeled.
  No hardware qualification or package ownership is claimed. The source-only
  goal remains active, and the packaged retained-byte count is unchanged.

### DMA/UART analysis link uses reconstructed IRQ functions

- Included the existing reconstructed `runtime_gx8002_irq.c` in the native
  macOS DMA/UART analysis link, authenticating its CSI headers, SDK license and
  IRQ interface against the pinned NationalChip SDK commit. Removed absolute
  function bindings for request_irq, irq_save and irq_restore.
- The linker report checks that IRQ functions reside in compiled text, the
  initializer's DMA handler pointer relocates, and five registration/save/restore
  call sites target the linked C functions. UART completion relocation checks
  remain enabled. A native build regression passed in 0.913 seconds.
- Analysis output: 20 source units, 1916 text bytes, SHA-256
  `a4201ccca7ac8c5d7e79481145eafb055c278b35364a09aca7a67c4499ad9e7a`.
  No unresolved symbols or relocations. Clock control and persistent storage
  still have external bindings; the IRQ dispatch entry is outside this link.
  This is not a firmware package or hardware qualification. No packaged
  retained-byte reduction is claimed by this linking step.

### DMA/UART link replaces fixed clock-function dependency

- Linked the existing pinned upstream GRUS clock candidate, including its
  module lookup, source-defined tables and generated switch data. DMA resource
  calls now alias the linked platform gate; initializer, selection and
  deallocation call targets are checked in decoded linked text.
- The analysis-only link has 21 source units: text 2372 bytes, rodata 76 bytes,
  initialized data 488 bytes. Text SHA-256:
  `5edbd0a537e5e9b818dcf80a78eddc3855941237872d9e62323b06b172ee491f`.
  Source-built clock tables relocate to analysis data address 0x20080000.
  Native macOS build regression passed; no unresolved symbols/relocations.
- Clock source/header/configuration provenance is included in the link report.
  This newly linked clock compilation still needs behavior checks at its
  relocated layout; prior original-entry gate qualification is not silently
  inherited. Persistent DMA/UART/IRQ storage remains externally bound, and
  this analysis ELF is not a runnable firmware image. Packaged ownership has
  not changed in this step.

### Relocated upstream clock gate behavior

- Added `verify_gx8002_dma_uart_clock_link.py`: rebuilds the 21-unit source link
  on macOS and executes its decoded clock gate at the actual linked address,
  using its relocated switch data and source-defined module table.
- 16864 cases match the independent clock MMIO oracle: valid/invalid module
  values, enable values 0/1/2/UINT32_MAX, source-register patterns including
  every single bit and complement, and two possible results for unused
  out-of-range shift intermediates. This does not assert architecture semantics
  for those shifts; both tested results are discarded by the affected paths.
- Lookup calls remain modeled against the linked table. This establishes
  relocated gate control flow and observable MMIO for the tested domain, not
  whole-firmware execution, concurrency behavior, or physical clock operation.
  Package ownership and the source-only completion status remain unchanged.

### Clock lookup executes with the relocated gate

- Replaced the modeled lookup in the relocated clock verifier with decoded
  execution of the linked `__module_get_info`. Gate and helper now share
  registers and stack-local memory; the helper's link-register return is checked.
- Added lookup instructions and bounded stack output writes to the executor.
  All 16864 gate/lookup cases still match the independent MMIO oracle. A native
  macOS regression reruns the combined execution.
- This closes the modeled lookup boundary for the fixed linked table. It does
  not establish mutated-table fallback behavior, concurrent access, or physical
  clock effects. The analysis build remains outside firmware package ownership;
  source-only firmware completion is still unproved.

### DMA callback storage becomes relocatable

- Replaced the callback writer's absolute 0x20027320 literal with the same
  `open_cfw_gx8002_dma_callbacks` symbol used by the IRQ reader. Original-entry
  linking still binds that symbol to the stock location.
- Passed 189 decoded callback cases and 72 receive/registration composition
  cases (32 nested callback stores). Default linked text remains unchanged.
- Link verification now requires a symbol relocation and the resolved storage
  address in both writer and IRQ reader. A regression links storage at
  0x20090000, rejects stale original literals in those functions, and restores
  the default analysis layout. Both link regressions passed in 3.542 seconds.
- This removes a source-level obstacle to moving callback storage. Its final
  allocation, initialization and firmware admission remain pending; no stock
  storage ownership or packaged retained-byte reduction is claimed.

### Remaining DMA/UART fixed state references removed

- DMA clear and select now derive device/count/allocation from the shared DMA
  state symbol; UART receive start/stop use the existing UART descriptor symbol.
  Candidate linkers bind original addresses for stock comparison. The analysis
  linker requires object relocations for these three source units.
- Passed 96 clear, 6132 select and 192 receive-control decoded cases. Persistent
  allocation qualification passed 5184 sequences/20736 calls; composed IRQ
  completion passed 5120 cases/9216 deallocations/3072 completions.
- Original-envelope sizes remain 36, 76, 52 and 40 bytes respectively. The clear
  candidate is now byte-exact. The 21-unit macOS analysis link remains 2372 text
  bytes; text SHA-256 is now
  `90bb139d38c0c64a20f8dbfccf1eb3984b05feedc24fdffaff3ac8c5e89a3305`.
- These changes make state references relocatable; final storage ownership,
  startup initialization and firmware package integration still require work.
  No source-only completion or hardware qualification is claimed.

### Source-owned DMA storage analysis variant

- Added C definitions for the 884-byte DMA state and 16-byte callback array,
  matching consumer declarations and recovered layout assertions. The analysis
  linker can now allocate both in BSS instead of using absolute bindings.
- The owned-storage variant places callbacks at 0x20090000 and state at
  0x20090010. It checks ELF NOBITS ownership, symbol sizes, callback relocation,
  and that both initialized aligned 416-byte lists fit their reserved storage.
- Three native link regressions passed in 5.969 seconds. Saved the owned variant
  evidence in gx8002-dma-owned-storage-link.json, then restored the default
  analysis build/report so existing original-address verifiers remain usable.
- BSS requires startup zeroing. These addresses are analysis placements, not
  validated physical firmware RAM ownership. UART/IRQ storage and boot/runtime
  integration remain unfinished; no runnable/source-only firmware claim.

### Source-owned DMA initialization execution

- Added `verify_gx8002_dma_owned_initialize.py`, rebuilding and executing the
  initializer with the owned-storage variant's actual state and function
  addresses. 18 cases check ordered state/MMIO writes, allocation reset,
  handler registration and both descriptor pointers' alignment and containment.
- The two clock calls per case execute the linked gate and lookup in a separate
  decoded frame (36 calls), with their MMIO traces checked against the clock
  oracle. IRQ registration remains modeled. Original-address initialization
  comparisons rerun before the relocated checks.
- The verifier restores the default analysis build after testing. Startup BSS
  clearing, physical RAM placement, IRQ registration composition and firmware
  integration remain pending. No packaged ownership change is claimed.

### Initializer IRQ registration boundary replaced by decoded execution

- Added a linked IRQ registration executor that follows the call into VIC
  enable in the same register frame and checks the leaf return address.
- Owned DMA initialization now executes both clock gate/lookup and IRQ
  registration/enable dependencies: 18 initializer cases, 36 clock calls and
  18 registration calls. The IRQ oracle checks ordered handler/private table
  stores followed by VIC enable bit 10.
- Added 148 linked registration boundary cases covering IRQs 0..33 and large
  unsigned values, null/non-null handlers and private data extremes. Invalid
  inputs produce no writes. The native regression passes.
- Separate initializer/clock/IRQ abstract frames remain. Physical interrupt
  delivery, startup clearing, final memory placement and firmware integration
  are not established; the source-only goal remains active.

### Source-owned IRQ table and saved-enable storage

- Added C definitions for 32 IRQ entries (256 bytes) and two saved-enable words
  (8 bytes), matching reconstructed registration/dispatch types with size and
  private-field-offset assertions. Analysis linking can now allocate these in
  BSS and removes their original-address bindings.
- Owned DMA initialization now uses both source-owned DMA and IRQ storage.
  Its 18 initialization cases, 36 clock calls, 18 registration calls and 148
  registration boundary cases pass at the relocated IRQ table. The regression
  checks that table storage is no longer external and has the expected extent.
- BSS zeroing and physical memory placement remain integration requirements;
  UART descriptor storage remains external in this analysis variant. IRQ
  dispatch/physical delivery and complete firmware build remain unfinished.

### UART storage default audit

- Added an authenticated descriptor-default analyzer for the two 128-byte UART
  descriptors at package 0x18aa8/0x18b28. Cross-checked port, MMIO base and IRQ
  identity against pinned SDK base_addr.h and soc.h (UART bases A0100000 and
  A0200000; IRQs 6 and 7).
- Nonzero defaults at offsets 16, 28 and 32 are 115200, 8 and 1. Their consumer
  semantics still need qualification before source-owned initialization. Zero
  words include runtime state and must not be interpreted as unused fields.
- Saved gx8002-uart-descriptor-defaults.json with image/header identities and
  field evidence. This changes the next action: recover those default consumers
  rather than allocate an incorrectly zero-filled UART descriptor table.

### UART defaults traced into configuration

- Extended the authenticated descriptor analyzer with 16 exact decoded
  instruction checks from configuration at package 0xc954. Offset 16 feeds
  unsigned input-clock/(baud<<4) arithmetic, storing the integer divisor at
  offset 20. Fractional calculation follows and is not yet qualified here.
- Verified zero normalization of offsets 28 and 32 to 8 and 1. Their semantic
  field names remain unproven: the routine independently replaces low five LCR
  bits with constant 3 at ca14..ca20, rather than using these two fields there.
- The consumer evidence prevents guessing a configurable framing implementation
  from default values alone. Next reconstruction target is the configuration
  routine, including fractional divisor and FIFO/DMA setup dependencies.

### UART FIFO-depth source reconstruction

- Reconstructed the configuration dependency at package c8ec..c954 as C. It
  reads descriptor device then parameter register +f4, accepts only one-hot
  encodings in bits 23:16, and returns encoding*16; unsupported values return 0.
- Native macOS C-SKY build is 30 bytes inside the original 104-byte envelope.
  1536 decoded stock/source cases match an independent explicit mapping for
  all 256 encodings, three unrelated-bit patterns, and both UART bases. Ordered
  reads and callee-preserved registers are checked.
- Source and builders/verifier are saved under uart_fifo_depth. This remains
  unadmitted; physical FIFO operation and full UART configuration are not yet
  qualified. No packaged retained-byte reduction is claimed.

### UART configuration C candidate compiled

- Reconstructed the full c954..cabc configuration control flow in
  runtime_gx8002_uart_configure.c: default normalization, clock/baud divisor,
  fractional divisor expression, ordered register setup, FIFO-derived burst
  fields, DMA enable/channel reset, and UART IRQ registration.
- Native macOS compilation emits a 360-byte function section, equal to the
  stock envelope, with explicit unresolved dependencies on FIFO, UART ISR,
  IRQ registration, and five compiler floating-point runtime functions.
- This is an unlinked, unqualified candidate. The inferred double expression
  must be checked against the stock float helper identities and decoded effects;
  full MMIO order also needs verification. Baud values making baud<<4 zero
  remain outside defined C division behavior. No candidate bytes admitted.

### Native macOS target libgcc build

- The installed C-SKY compiler lacked libgcc.a. Built `all-target-libgcc` with
  `make -j4` and installed with `make install-target-libgcc` from
  g2/build/csky-macos/gcc-build, using the existing native macOS configuration
  and GCC source commit 1e9b70447a8417f5c692370de4533e43d754e8fa.
- Source-built archive supplies __floatunsidf, __divdf3, __muldf3, __adddf3 and
  __fixunsdfsi. UART configuration now links against it without unresolved
  symbols in an analysis ELF; FIFO/ISR/registration remain absolute bindings.
  Archive SHA-256: 9ecd75da478b51b4d25152616294e3550ef249049d242a43d1e5519d9ba48b7b.
- Saved runtime provenance and link evidence in the UART configuration report.
  This resolves a native build dependency, not stock float equivalence or
  hardware qualification. Full configuration comparison and firmware admission
  remain pending. No Linux build was used.

### Floating-point runtime provenance and mismatch audit

- Added an authenticated runtime audit covering GCC fp-bit.c/fp-bit.h,
  libgcc2.c, C-SKY build rules and COPYING.RUNTIME at the pinned source commit.
- Compared the five source-built helper bodies with equal-length stock slices
  at their inferred UART call targets. None is byte-exact. These slices are not
  claimed as established stock function extents or semantic equivalence.
- Observed closely matching unsigned-to-double pack preparation structure;
  source-built __floatunsidf calls __pack_d, while stock calls package 13b00.
  This is lineage evidence only. Next qualification must execute/check the
  arithmetic helpers rather than treating successful linking as equivalence.

### Unsigned-to-double preparation comparison

- Added decoded execution through the pack-call boundary for stock 13a5c and
  source-built __floatunsidf. Compared initialized class/sign/exponent/fraction
  fields in 8239 cases: low integers, high-bit samples, power-of-two neighbors
  and UINT32_MAX. An independent integer-normalization oracle also passes.
- Zero prepares class 2/sign 0 without initializing unused fields. Nonzero
  values prepare class 3, exponent floor(log2(value)), and fraction normalized
  to bit 60. This supports the inferred helper identity but does not execute
  __pack_d or prove the complete floating-point runtime.
- Out-of-range shift intermediates are modeled as zero before conditional
  replacement; final IEEE encoding and pack behavior remain next work.

### Unsigned integer conversion reaches final IEEE bits

- Added decoded execution of stock/source double pack helpers for the normalized
  integer domain. The 8239 preparation cases now feed their actual prepared
  fields into both pack implementations and compare final 64-bit IEEE results
  against exact host uint32-to-double conversion.
- Tested zero's uninitialized payload fields with zero and UINT32_MAX seeds.
  All cases pass. Stock carry-add packing and upstream 64-bit addition paths
  both execute; no pack-result stub supplies the output.
- Conversion and packing still use separate abstract frames. This qualifies
  the sampled unsigned integer domain only, not arbitrary floating values,
  NaNs, denormals, generic rounding, arithmetic helpers, or hardware execution.

### Double-to-unsigned wrapper comparison

- Added decoded stock/source wrapper comparison for __fixunsdfsi. 4372 cases
  cover fractional-divisor-scale values and neighboring doubles at integer,
  2^31 and UINT32_MAX boundaries. Results match truncation in the valid domain.
- Verified comparison against 2^31, signed-conversion calls, and the subtract
  then add-2^31 path. Helper arguments/order and caller-clobber resilience match.
- __gedf2, __subdf3 and __fixdfsi bodies remain modeled; this is wrapper
  qualification only. NaNs, overflow, arithmetic helper equivalence and complete
  UART configuration qualification remain outstanding.

### Signed conversion tail verification

- Added decoded stock/source execution after double unpacking in __fixdfsi.
  8716 finite in-range cases cover positive/negative fractions, fractional UART
  values, and signed integer boundaries. Both tails match truncation toward zero.
- Linked source entry is resolved from its symbol and checked against the
  expected post-unpack instruction. Stack endpoint and conditional sign handling
  are checked. Unpacked fields and entry frame are modeled; unpack execution,
  exceptional values and full floating runtime qualification remain pending.

### Double unpack source/stock execution

- Added decoded double-unpack execution with byte/halfword/word reads, bounded
  stack save, output stores, carry/64-bit normalization and ABI checks.
- 16376 cases compare stock and source-built __unpack_d against an independent
  integer decomposition oracle: every finite exponent, both signs and four
  fraction patterns. Zero and subnormal normalization are included.
- NaN/Infinity and exhaustive mantissas remain outside this corpus. This closes
  a helper qualification gap but is not yet composed into the signed conversion
  frame or the full UART arithmetic path. Firmware admission remains pending.

### Decoded unpack feeds signed conversion

- Replaced verifier-generated unpack fields in the signed-fix comparison with
  decoded stock/source unpack outputs. All four producer/consumer combinations
  execute, with zero and UINT32_MAX seeds for fields left unwritten by zero.
- 8716 input values yield 69728 composed conversion executions, all matching
  truncation toward zero. Added a regression rerunning the native source build
  and this composition. Unpack fields also retain their independent oracle.
- Frames remain separate and the conversion prefix is not executed by this
  composition. Arithmetic helpers and complete UART configuration remain
  unfinished; no source-only firmware completion or admission is claimed.

### Full signed conversion and unsigned-wrapper composition

- Executed __fixdfsi from its stock/source entry: input spills, 28-byte local
  frame, unpack arguments, decoded unpack effects, caller clobbers, conversion
  and stack/link restoration. 34864 full calls pass alongside the existing
  69728 producer/consumer tail checks over 8716 input values.
- Replaced the unsigned wrapper's signed-conversion model with that decoded
  function and its decoded unpack dependency. All 4372 unsigned-wrapper cases
  continue to pass. Comparison and subtraction remain modeled boundaries.
- Updated regression assertions. Separate nested interpreter frames remain;
  full UART configuration and arithmetic-helper qualification are unfinished.

### Double comparison core verified

- Added decoded stock/source comparison-parts execution using decoded unpacked
  inputs. 529 finite pairs match the independent numeric ordering oracle,
  including signed zero, minimum subnormals, adjacent doubles, large values
  and the unsigned conversion threshold at 2^31.
- Checks branch/sign/exponent/fraction ordering and callee-preserved registers.
  The GE wrapper, NaNs/Infinities, and composition into the unsigned wrapper
  remain outstanding. This is not full floating-runtime qualification.

### Full comparison wrapper integrated into unsigned conversion

- Added decoded GE wrapper execution: stack/spills, two actual decoded unpack
  calls, comparison-parts call and ABI restoration. All 529 finite pairs pass
  for stock/source wrappers against the numeric-order oracle.
- Unsigned conversion now calls this decoded GE path instead of a host
  comparison model. All 4372 wrapper cases pass with decoded comparison,
  signed conversion and unpacking. Only subtraction remains modeled in this
  conversion chain. Separate helper frames and finite-domain limits remain.
- UART arithmetic and complete configuration/firmware integration remain
  outstanding; no source-only completion claim.

### Subtraction wrapper input preparation

- Added decoded subtraction-wrapper execution through the addition-core call,
  including both decoded unpack calls. 169 finite operand pairs verify stack
  argument placement, second-operand sign inversion, and core input/output
  pointers for stock and source-built __subdf3.
- Covers signed zeros, subnormals, fractional and large values. The addition
  core and final packing remain unverified for subtraction; no subtraction
  result model has been promoted to qualified execution. Next work is the
  common arithmetic core shared by add/subtract.

### Authenticated addition-core host reference

- Built a host reference from the exact pinned GCC _fpadd_parts function and
  LSHIFT macro, with explicit 64-bit fraction/class scaffolding. Source hashes
  and GCC runtime license identity are recorded in gx8002-fpadd-reference.json.
- Native macOS Clang ASan/UBSan passes 66560 cancellation/doubling checks over
  33280 sign/exponent/fraction inputs. The reference supplies the actual upstream
  sticky-bit arithmetic for subsequent decoded comparisons.
- These checks do not compare stock instructions, target ABI, general rounding
  or all arithmetic paths. Stock addition-core execution remains next work;
  no firmware admission or source-only completion claim.

### Decoded addition core started

- Added an instruction executor for stock/source _fpadd_parts including
  saved registers, bounded stack/output memory, carry arithmetic and source
  64-bit arithmetic instructions. 8320 cancellation/doubling cases pass against
  exact integer invariants across signs, exponents and fraction samples.
- Unlike the host reference, this executes actual stock and linked C-SKY
  instructions. Unequal operands, exponent alignment and exceptional classes
  remain unqualified; the executor is not yet a general arithmetic proof.

### Unequal finite addition-core paths

- Extended decoded core checks with an integer sticky-alignment/sign/normalization
  oracle. Added 612 operand combinations spanning both signs and exponent gaps
  around 31/32/63/64 bits and beyond the retained fraction width.
- Added 2048 deterministic varied finite operand pairs with 52-bit fractions
  and exponents -100..100. Stock and source-built cores match the oracle for
  these cases and the existing 8320 cancellation/doubling cases.
- Enabled the AND instruction reached by alignment. Final IEEE packing for
  arithmetic results, exceptional classes and exhaustive coverage remain
  unqualified; no full subtraction or firmware completion claim yet.

### Arithmetic packing and unsigned conversion chain closed for corpus

- Finite addition-core outputs now feed decoded stock/source pack helpers:
  4096 executions match host IEEE addition for 2048 deterministic operand pairs.
- Subtraction wrapper can now execute unpack, core and pack through return.
  Ten stock/source executions of conversion-threshold subtraction cases pass.
- Replaced the unsigned conversion's subtraction model with that decoded path.
  All 4372 conversion cases pass using decoded comparison, signed conversion,
  unpack, subtraction core and packing. No host arithmetic result supplies the
  tested chain; nested helper frames are still separate.
- Multiplication/division, full UART configuration, exceptional floating values
  and firmware integration remain unfinished. No firmware admission claimed.

### Complete baud rounding addition

- Added full decoded __adddf3 wrapper checks for adding 0.5 to 4130 finite
  baud-rounding-scale values, including nextafter neighbors at integer
  boundaries. 8260 stock/source executions match the expected IEEE result.
- The path executes unpack, core and pack. Core input storage now seeds fields
  left unwritten for zero, preserving zero-class behavior without undefined
  dictionary reads. Existing core and unsigned conversion suites still pass.
- Multiplication/division and the full UART configuration remain outstanding;
  these finite-domain checks do not establish general IEEE exceptional-value
  behavior or hardware qualification. No firmware admission claimed.

### Decoded baud scaling multiplication

- Added a finite multiplication executor for the stock __muldf3 and the pinned
  GCC runtime built natively on macOS. Stock integer multiplication at package
  0x13ab4 is executed from decoded instructions; the source build's mul.u32 and
  mula.u32 paths execute with explicit register-pair arithmetic.
- 6180 zero/normal nonnegative scaling inputs produce 12360 stock/source
  executions matching multiplication by 16. Includes deterministic fraction
  samples, integer-boundary neighbors and the approximately 2^-32 lower baud
  ratio boundary. Separately, 2097 full-width integer-multiply cases match
  modulo-2^64 products.
- Unpack and pack execute decoded bodies in separate helper frames; caller
  register clobbering and multiply callee preservation are checked. This is a
  scoped interpreter, not hardware execution or full IEEE qualification.
  Subnormal results, NaNs and infinities remain outside this corpus.
- Added a regression test and gx8002-uart-scaling-multiply.json evidence report.
  Division, full ordered UART MMIO verification and firmware admission remain
  outstanding. No retained bytes or package ownership counts changed.

### Decoded UART fractional division and arithmetic chain

- Executed stock __divdf3 (package 0x13894) and macOS-built pinned GCC
  __divdf3 with decoded unpack/pack bodies. Added xor and decrement-and-branch
  handling to the existing arithmetic interpreter to cover the division loop.
- 2234 valid remainder/denominator pairs, including zero, near-half and
  near-one ratios, powers of two, the default baud denominator, large uint32
  denominators and deterministic samples, pass 4468 stock/source division
  executions against binary64 division.
- Each decoded division result then feeds decoded multiplication by 16,
  addition of 0.5 and unsigned conversion through comparison and signed fix.
  All 4468 composed executions match the expected UART fractional integer.
  Nested helpers execute decoded instructions in separate frames.
- Integer inputs currently enter this chain as exactly representable host
  binary64 values. Composing the already examined uint-to-double entry,
  executing full UART MMIO ordering and firmware integration remain required.
  No zero-denominator, NaN, infinity or subnormal-result qualification claimed.
  The source-only goal remains incomplete; package ownership is unchanged.

### Integer conversion now enters the UART arithmetic chain

- Extended uint-to-double execution beyond its former pack boundary through
  the real wrapper epilogue and return, using decoded pack instructions in a
  separate helper frame. Checks cover stack bounds, saved registers, callee
  preservation and caller-register clobbering at the helper boundary.
- 8239 uint32 inputs pass 32956 stock/source full-function executions across
  two unused-field seeds. Existing unpacked-field and IEEE-bit oracles remain.
- The UART fraction verifier now obtains both floating operands from these
  decoded conversion wrappers. All 4468 stock/source sequences pass conversion,
  division, multiplication, addition and unsigned conversion. Host arithmetic
  supplies expected results only, not the intermediate operation results.
- Full UART configuration/MMIO execution and source integration remain open.
  These scoped execution checks do not qualify exceptional IEEE values,
  hardware behavior or the complete firmware. No package ownership changed.

### UART configuration ordered execution

- Added decoded whole-function configuration execution and a stock/source
  comparison for 400 descriptor/MMIO scenarios. 333 enter baud programming;
  these execute uint-to-double, divide, multiply, add and unsigned conversion
  helpers from decoded instructions in separate frames.
- Corrected the C candidate's volatile ordering after FIFO depth lookup:
  stock reloads the device pointer before storing descriptor depth. The
  candidate now does so too. Tests include changing the device pointer at the
  FIFO helper boundary, both default-field paths and all threshold selectors
  plus out-of-range selectors.
- Ordered descriptor and MMIO read/write traces and helper arguments match;
  independent oracles check final descriptor fields and the complete ordered
  UART register-write sequence. Regression test passes on native macOS.
- FIFO depth return and IRQ registration remain modeled call boundaries in
  this test; their separate checks are not a composed UART integration proof.
  No hardware behavior, interrupt concurrency or zero shifted denominator
  qualification. Source admission and complete firmware reconstruction remain
  outstanding; no package ownership counts changed.

### UART configuration composed with FIFO depth helper

- Added an optional decoded FIFO hook to whole-function UART configuration
  execution. Both stock and source helper bodies execute, and their descriptor
  and parameter-register reads are included in the ordered trace. The source
  helper is rebuilt natively on macOS before composition.
- 1200 cases cover threshold selectors, twelve valid/invalid FIFO encodings,
  both DMA modes and an injected device-pointer change after helper return.
  2400 decoded FIFO executions and 1000 baud-programming case pairs pass stock/
  source trace comparison plus descriptor and ordered-MMIO oracles.
- This uses separate decoded helper frames; it is not a firmware image link or
  hardware run. IRQ registration remains modeled in this verifier. Source-only
  completion and firmware admission are still outstanding.

### UART configuration composed with IRQ registration and VIC enable

- Replaced the optional IRQ boundary with decoded registration plus VIC enable
  in a shared nested helper frame. The source IRQ unit is rebuilt through its
  native macOS linker, and handler-table/VIC writes join the UART ordered trace
  and resulting memory state.
- 1200 full configuration scenarios pass with both FIFO and IRQ composition:
  2400 decoded IRQ calls and 2400 FIFO calls across stock/source. IRQ inputs
  include UART lines 6 and 7, line 31, and rejected line 32. Independent oracles
  check handler/private table slots, enable mask and write ordering.
- Added a regression test. This composes separately linked source units in
  scoped instruction interpreters; it does not yet link this UART cluster into
  the firmware or execute its registered interrupt handler. No hardware or
  source-only completion claim, and no package ownership counts changed.

### UART interrupt source candidate recovered

- Recovered the registered handler at package 0xc804 / runtime 0x10203278 as
  C, including sampled pending bits, ready callbacks, non-DMA buffered receive
  and transmit, descriptor cursor/remaining updates, completion callbacks and
  the transmitter-empty polling loop. No callback-null guards or poll timeout
  were invented; source preserves the observed call assumptions and loop.
- Preserved receive-side device-pointer reloads for each byte and transmit-side
  cached device access. FIFO-space calculation in this handler uses the raw
  parameter byte shifted by four, unlike the separate validated-depth helper.
- Native macOS compilation emits 226 bytes within the original 232-byte
  envelope. Candidate authenticates stock and the pinned SDK UART header.
- This is build evidence only. Decoded trace comparison, callback mutation,
  drain-loop qualification and integration remain required before admission.
  The new source is not counted as replacing retained firmware bytes yet.

### UART interrupt dispatch verification

- Added a scoped decoded interrupt executor and independent ordered-read/
  callback oracle. 1728 cases compare original and compiled C dispatch for
  pending values 0..15, receive/transmit modes 0, 1 and 3, DMA enabled/disabled,
  three FIFO values and optional receive-callback mutation.
- Callback mutation changes device pointer, port, transmit mode/private data
  and the pending register. Checks establish that dispatch retains the sampled
  pending bits but reloads transmit-side descriptor/device fields afterward.
  Caller clobbering and callee register restoration are checked.
- Native macOS regression test passes. Buffered mode 2 and the transmit-drain
  loop are still unqualified; callback bodies are modeled effects. Handler
  source remains unadmitted and the complete source-only goal remains open.

### Buffered UART interrupt execution

- Extended decoded execution with byte buffer accesses, post-increment byte
  operations, minimum counts, signed loop comparisons and interrupt-bit clear
  instructions. Both the original and compiled handler now execute mode 2.
- 1152 cases match ordered traces and memory. Independent oracles validate
  receive bytes, transmit bytes, cursor/remaining updates, completion callback
  order and interrupt-enable masks. Buffers include unaligned addresses and
  zero/partial/full transfers; receive/transmit/both pending paths are covered.
- Transmitter drain checks complete immediately or after three empty samples,
  totaling 2560 stock/source poll reads. Permanently stalled hardware, large
  signed-count edges and buffered callback mutation remain unqualified.
- Native macOS buffered and dispatch regression tests pass. No admission or
  complete firmware claim; source-only integration remains outstanding.

### Buffered completion callback mutation

- Added 96 decoded stock/source cases where receive completion changes the
  UART device pointer, port, transmit mode, DMA state, buffer/length and
  completion callback/context before the same interrupt handles transmit.
- Ordered traces and memory agree. Independent oracles check the new transmit
  device and bytes, cursor updates, ready/completion callback arguments and
  interrupt masks on both devices. Clearing the pending register in the
  callback does not replace the handler's already sampled pending value.
- All three interrupt regression tests pass on macOS. Callback bodies remain
  modeled and this is not concurrent hardware execution. Source admission,
  stalled-drain/large-count edges and complete firmware integration remain open.

### Source-linked UART configuration cluster

- Added a native macOS analysis link containing recovered configuration,
  FIFO depth, interrupt handler, IRQ routines and source-owned IRQ storage,
  with the native-built GCC runtime archive. No absolute function bindings
  or unresolved symbols remain in this cluster.
- Linked text is 3670 bytes and IRQ BSS is 264 bytes. Checks validate source
  function sections, BSS type/extents, applied relocations, configuration calls
  to linked FIFO/IRQ functions and the relocated interrupt-handler literal.
- The handler literal is checked through decoded literal-load operands because
  its pool can lie outside the compiler's function symbol size.
- Native link regression passes. This is an analysis ELF, not a complete
  firmware image. Relocated execution, startup zeroing, physical placement and
  the remaining firmware functionality/data still require reconstruction and
  integration. No package ownership counts or completion claims changed.

### Relocated UART source-cluster execution

- Executed configuration from the source-linked UART ELF, including its
  relocated GCC arithmetic, FIFO depth, IRQ registration and VIC enable code.
  1200 cases match the stock configuration checks; 1000 enter baud arithmetic.
- Valid IRQ cases explicitly verify the source-owned table contains the actual
  relocated handler address and descriptor pointer. For stock comparison only,
  IRQ table addresses and handler-pointer values are normalized to stock
  addresses. Descriptor and MMIO effects otherwise compare unchanged.
- Native macOS relocated regression passes. Nested helper frames remain scoped
  interpreter executions; startup/BSS zeroing, physical placement, registered
  ISR dispatch integration and full firmware reconstruction remain unfinished.
  No firmware source-admission or package ownership claim changed.

### IRQ entry and dispatcher included in UART source cluster

- Extended the native source link with the existing explicit interrupt-context
  assembly wrapper and ordinary C dispatcher body, both using the cluster's
  source-owned IRQ table. These are source files, not extracted instruction
  arrays. The plain compiler interrupt attribute alone remains unsuitable
  because it omits register preservation present in stock.
- The cluster now contains seven checked entry/helper symbols, 3750 text bytes
  and 264 BSS bytes, with no unresolved symbols. The native source-link test
  passes; configuration relocation checks are rerun after the added code moves
  linked addresses.
- This does not yet compose hardware entry through dispatcher into UART ISR,
  or qualify startup, nested interrupts and physical execution. Full firmware
  source-only reconstruction remains outstanding; no package admission changed.

### Relocated IRQ dispatch to UART handler

- Extended the dispatcher interpreter with a configurable IRQ table address
  and decoded handler hook. Added 72 source-cluster dispatch cases covering
  IRQs 6, 7 and 31, status upper bits, and pending values 0..7.
- The relocated dispatcher reads the expected table slots and passes the IRQ
  and descriptor to the relocated UART handler. The handler executes in a
  separate decoded frame; receive/transmit ready callbacks match independent
  argument and ordering checks. Native regression passes.
- Active-vector and table reads are supplied by the harness. Hardware entry
  context, nested interrupts and startup are not covered by this composition.
  No firmware admission or complete source-only build claim changed.

### Relocated IRQ entry context checks

- Parameterized the existing software-frame executor's dispatcher target,
  including recursive calls, and applied it to the UART cluster's relocated
  entry and dispatcher addresses.
- 48 seed/depth/model combinations pass register restoration and frame checks
  for one through four modeled levels. Software-only peak is 104 bytes per
  level; with the existing hardware-frame model it is 136 bytes per level.
- These are modeled clobber/frame checks, not the actual combined dispatcher/
  UART call-stack demand or physical nested-interrupt execution. Source-only
  firmware completion remains unproven and no package ownership changed.

### Stalled transmitter polling prefixes

- Added verifier-only stopping at a selected number of transmitter status
  reads, without changing firmware code. 36 stock/source cases match prefixes
  of 1, 2, 16 and 128 reads with the empty bit continuously clear.
- Checks confirm buffers/cursors finish transferring before the wait, while
  interrupt enable remains unchanged and no completion callback runs during
  the observed stalled prefix. Zero-length transmission is included.
- All four interrupt regression tests pass on macOS. Finite-prefix evidence
  does not establish eventual behavior, timing or physical hardware behavior.
  No timeout was added to source; firmware integration remains unfinished.

### Source-authored UART descriptor defaults

- Added two 128-byte UART descriptors as C designated initializers, using
  authenticated SDK UART base/IRQ constants, baud 115200, the observed default
  normalization values 8 and 1, and zero initialization for mutable fields.
  No extracted byte arrays are used. Original names of fields 7/8 remain
  unestablished and are not guessed in the source.
- The native UART cluster now owns a 256-byte data section at its analysis
  data address. Compiled defaults compare exactly with authenticated stock
  descriptors; the build checks symbol size/section and the regression checks
  the new source-owned extent.
- This is source data in an analysis link, not admitted firmware ownership.
  Startup copying and relocated descriptor consumer composition remain open,
  along with the full firmware source-only objective.

### Configuration consumes source-owned UART defaults

- Parameterized configuration/FIFO descriptor addresses and executed the
  linked configuration using both descriptors loaded from compiled C data.
- 24 port/clock/FIFO combinations pass baud, threshold and IRQ registration
  oracles. Registered private pointers reference the relocated descriptors,
  and traces contain no accesses to the retained stock descriptor range.
- This models loading the data section rather than executing startup copy.
  Clock values are harness inputs and nested helpers use separate frames.
  Complete firmware integration and source-only completion remain open.

### Configured source-owned descriptors reach interrupt dispatch

- Extended the owned-defaults check to retain configuration output, arm ready
  callbacks in that descriptor, then supply the actual registered handler and
  private pointer to decoded dispatch. The relocated UART ISR now accepts the
  configured descriptor address in its execution model.
- All 24 cases reach the registered source handler and produce expected port,
  receive-count, transmit-space and private-context callback arguments.
- Application callback setup and peripheral pending values remain harness
  inputs. This connects configuration data to dispatch but does not execute
  startup or actual hardware IRQ entry. Full firmware integration remains open.

### UART initialization C candidate

- Recovered package 0xcabc..0xcb24 into C: reject ports >=2, enable module
  17/18, obtain frequency for module 16, snap within 100 Hz of a MHz boundary,
  store clock/baud into the selected descriptor and return configuration's
  result. Descriptor selection uses the source-owned symbol.
- Native macOS candidate emits 104 bytes, fitting the 104-byte stock envelope.
  The analysis placement still binds helpers to their established addresses.
- Build evidence only: clock-rounding boundary traces, helper composition and
  integration remain required. No source admission or firmware completion
  claimed for this candidate.

### UART initialization boundary verification

- 1080 decoded stock/source cases pass an independent clock-rounding and
  ordered-helper oracle, including 99/100/101 Hz boundary neighbors, large
  uint32 clocks, invalid ports, baud values and configuration return statuses.
- Native regression passes. Gate, frequency and configuration calls remain
  modeled boundaries in this initializer test; composition remains required.
  No firmware admission or source-only completion claimed.

### UART initialization source closure with upstream clocks

- Added an optional expanded UART analysis link containing initialization,
  pinned upstream gate/frequency adapters, recovered divider and their source
  tables. Output is separate from the configuration-only analysis artifact.
- Native macOS link emits 4986 text bytes with eleven checked function symbols,
  source UART/IRQ storage and no unresolved symbols. Regression passes.
- Relocated clock/initialization execution and startup remain unqualified in
  this expanded artifact. It is not a complete firmware image or admission;
  retained firmware ownership counts remain unchanged.

### Relocated initialization call and descriptor checks

- 1080 cases execute initialization from the expanded source ELF. Independent
  oracles check port rejection, clock-rounding boundaries, selected source
  descriptor addresses, helper call arguments and returned configuration status.
- Relocated gate/frequency/configuration targets resolve correctly. Helper
  results remain modeled in this check; composing their actual instruction
  execution is still required. Native macOS regression passes.
- No startup, hardware or complete source-only firmware claim changed.

### Initialization hands descriptor state to configuration

- Added a configuration callback to the initialization interpreter and composed
  it with the expanded source ELF. Initializer writes update the compiled C
  descriptor before decoded configuration runs; its return propagates back.
- 24 cases continue through configuration, actual IRQ registration output and
  decoded dispatch into the relocated UART handler. Native composed and
  existing owned-default regression tests pass.
- Clock gate/frequency helper results remain modeled at initialization's
  boundary. Startup and physical hardware execution are not covered. Complete
  source-only firmware integration remains outstanding.

### Initialization clock-gate composition

- Initialization now invokes decoded relocated upstream gate and lookup code
  in its composed check. The gate's actual call target identifies its lookup;
  literal references identify the correct source table despite duplicate local
  table names from the frequency adapter.
- All 24 initialization/configuration/dispatch cases pass with 24 decoded gate
  calls checked against an independent MMIO oracle. Frequency result remains
  supplied by the harness; gate peripheral values are modeled inputs.
- No startup, hardware execution or complete firmware admission claim changed.

### Relocated frequency helper execution probe

- Parameterized frequency entry/lookup/divider/table addresses in the existing
  decoded executor. A relocated module-16 high-frequency scenario now executes
  actual lookup, divider and source tables, returning the expected 24576000 Hz.
- Fixed width-specific source-cell reads: overlapping byte/halfword/word views
  must select the value for the requested width rather than a flattened last
  value. Existing 130 high-frequency stock/source cases still pass.
- This is one probe, not broad relocated frequency qualification. Connecting
  frequency to initialization and full firmware integration remain unfinished.

### Decoded frequency feeds UART initialization

- Added optional frequency composition using the expanded source ELF directly,
  avoiding a separate rebuild inside the helper. The decoded frequency result
  now supplies initialization, then configuration, registration and dispatch.
- Eight port/FIFO cases pass with decoded gate, frequency/lookup/divider,
  arithmetic, FIFO, IRQ and UART handler paths. Frequency uses the established
  24.576 MHz source scenario; peripheral values and callback setup are modeled.
- This narrow shared-state scenario does not establish general clock behavior,
  actual hardware IRQ entry or startup. Source-only firmware remains unfinished.

### Relocated UART frequency DTO/divider patterns

- Extended the frequency probe with register-pattern inputs and an independent
  integer oracle derived from the linked DTO/divider records. Five patterns
  cover zero, small fractions, maximum DTO fraction, bypass and all-one fields.
- The high-frequency source selector is held fixed; varying it accidentally
  entered the unconfigured PLL path during development. PLL composition is
  still outside this probe. The corrected five-pattern native test passes.
- Broader source selection, full clock peripheral state and hardware execution
  remain unqualified; source-only firmware integration remains open.

### Expanded clock-to-UART composition

- The decoded-frequency initialization path now covers all five DTO/divider
  patterns rather than only bypass. Forty port/FIFO/pattern cases pass through
  gate, frequency, initialization rounding, baud arithmetic, IRQ registration
  and dispatch. Updated native regression passes.
- Frequency expectation comes from the independent source-record arithmetic
  oracle; configuration consumes the decoded helper return. The fixed source
  selector, modeled peripheral state and separate interpreter frames remain
  limitations. Startup and complete firmware integration are still open.

### UART transmit start/stop recovery

- Recovered transmit ready-callback control from stock packages 0xcbbc and
  0xcbf0. Start rejects a null callback, sets mode/callback/context and enables
  TX interrupt bit 1 under IRQ save/restore. Stop clears callback/context and
  disables that bit while preserving the observed mode behavior.
- Native compiled C passes 192 decoded stock/source cases and independent
  ordered-write/IRQ-token oracles. Regression passes. IRQ helper bodies remain
  modeled here; control integration and firmware admission remain required.

### Receive/transmit controls linked into UART cluster

- Added both receive and transmit start/stop C objects to the source-owned UART
  cluster. All four entry points are checked as linked source functions and
  their call targets must resolve to the recovered IRQ save/restore functions.
- The configuration cluster now has 3934 text bytes and eleven checked entry/
  helper symbols; the expanded initialization cluster has fifteen symbols.
  No absolute function bindings or unresolved symbols were introduced.
- Native source-link and full clock-composition regressions pass after address
  changes. Control execution with relocated descriptors and IRQ helpers still
  needs composition; complete firmware integration remains unfinished.

### Relocated UART control traces

- Parameterized descriptor and IRQ target addresses in receive/transmit control
  execution. All four relocated entries pass 384 ordered-trace and memory
  comparisons against the independent control oracle at source-owned addresses.
- Native regression passes. IRQ tokens remain modeled at the helper boundary;
  actual IRQ save/restore composition and full firmware integration remain open.

### Relocated controls compose IRQ save/restore

- Replaced modeled control IRQ returns with decoded relocated PSR save/restore
  leaves. Expanded to 576 cases, including explicit interrupt-enabled and
  disabled processor states; 864 IRQ leaf calls pass.
- Oracles check disable/restore transitions, exact token preservation, null
  callback behavior and existing descriptor/MMIO traces. Native regression
  passes. Architectural PSR semantics remain modeled, not physical execution;
  firmware integration and source-only completion remain outstanding.

### Configuration state now feeds decoded UART start routines

- Replaced manual callback descriptor writes in the owned-defaults composition
  with actual relocated receive/transmit start execution. Both interpreters now
  accept the preceding configuration memory without resetting its state.
- The full native macOS clock-to-dispatch check passes 40 cases and 80 start
  calls. Each start executes decoded IRQ save/restore and checks the entire
  resulting memory against an independent update oracle, preserving IRQ table
  entries and unrelated configuration state.
- Standalone receive (192 cases), transmit, relocated controls, owned defaults
  and initializer composition regressions pass. An initial test command named
  a nonexistent receive test module; the receive verifier was run directly.
- Callback implementations, physical peripheral behavior, startup and complete
  source-only firmware integration remain unresolved. No ownership or hardware
  qualification claim was added; the retained-stock package was not rebuilt.

### Recovered UART drain wait from executable stock

- Added source-authored `open_cfw_gx8002_uart_flush` for codec package
  0xcb24..0xcb40. Native macOS C-SKY compilation produces 24 bytes inside the
  28-byte stock envelope, with the descriptor reference relocated normally.
- Authenticated stock/source decoded verification passes 160 cases, including
  40 finite stalled prefixes. Independent oracles check status bit 6, exact
  read order, single sampling of the device pointer, and eventual return.
  The source preserves the stock unbounded wait; only the verifier bounds
  unavailable stimuli. Native unittest passes.
- This new recovery is not yet admitted into the firmware package or the
  relocated UART cluster. Physical MMIO semantics and whole-image source-only
  completion remain unqualified; no retained-stock ownership count changed.

### Drain wait joins the source-linked UART cluster

- Linked the recovered drain wait into both UART cluster variants using the
  source-authored descriptor symbol, replacing its analysis-only absolute
  descriptor binding in the combined ELF. The default cluster now checks 12
  function symbols; the initializer/clock variant checks 16.
- Added 160 relocated execution cases using device addresses read from the
  actual compiled descriptor defaults. Checks reject stock descriptor reads
  and verify exact polling traces and termination against an independent
  oracle, including finite prefixes of indefinite waits.
- Five native macOS tests pass: isolated drain wait, relocated drain wait,
  both source links, and the full clock-to-start-to-dispatch composition.
  Firmware placement, startup and device execution remain incomplete; this
  analysis link does not constitute a runnable source-only firmware image.

### Recovered blocking UART byte receive

- Reconstructed codec 0xc7ec..0xc804 as source-authored C. Native macOS
  compilation produces 18 bytes within the 24-byte original envelope.
- Authenticated stock/source decoded comparison passes 800 cases, checking
  data-ready bit 0, single sampling of the device pointer, one full-width
  data-register read after readiness, low-byte truncation, and preserved ABI.
  Finite stalled prefixes verify that no data read happens before readiness;
  the source retains the original unbounded polling behavior.
- Native unittest passes. The routine is not yet admitted into the package;
  physical behavior and complete source-only firmware remain unqualified.

### Blocking receive joins the source UART link

- Added the recovered byte receive object to both UART source cluster builds.
  The default cluster checks 13 function symbols; initializer/clock checks 17,
  with no unresolved symbols or unapplied relocations.
- Verified 800 relocated cases with device pointers taken from actual compiled
  descriptor defaults. Independent trace/result checks cover readiness,
  full-width data reads and low-byte return, including stalled prefixes;
  any stock descriptor address access is rejected.
- Five native macOS tests pass: isolated and relocated byte receive, both
  source links, and full clock-to-start-to-dispatch composition. These remain
  analysis ELFs; startup, physical execution and complete source-only firmware
  integration are outstanding. No package ownership claim changed.

### Recovered blocking UART buffer read

- Reconstructed codec 0xcb64..0xcb90 in C. Native macOS compilation fits the
  original 44-byte envelope. The caller invokes the recovered byte receiver
  once per requested byte and returns zero for nonpositive signed lengths.
- Authenticated decoded stock/source comparison passes 84 cases, covering
  negative/zero lengths, positive lengths, byte patterns, wrapped destination
  addresses, descriptor arguments and callee-saved registers. Native unittest
  passes. Byte helper returns are modeled in this caller check; nested polling
  composition and firmware admission remain pending.

### Blocking buffer receive composes decoded polling

- Replaced modeled byte-helper results in a new composition check with decoded
  stock/source byte receiver execution. The ordered trace now includes each
  descriptor load, readiness poll, full-width data read and destination store.
- 108 cases pass, including 30 stalled prefixes that prove the caller stores no
  byte and makes no further call when its current receive remains blocked.
  Changing the modeled device between calls checks fresh descriptor sampling;
  signed nonpositive lengths remain side-effect free.
- Three native macOS regressions pass. Interpreters still use separate frames
  and modeled peripheral stimuli; firmware integration and physical execution
  remain unqualified. No source-only completion claim is made.

### Blocking buffer read joins the source UART cluster

- Linked the recovered buffer reader against the source byte receiver and
  source descriptor storage in both cluster variants (14/18 checked functions).
- 108 relocated nested execution cases pass, including 30 stalled prefixes.
  The check resolves actual ELF symbols, validates the helper call target,
  reads device pointers from compiled defaults, and compares complete ordered
  descriptor/poll/data/store traces with an independent oracle.
- Four native macOS tests pass: relocated nested receive, both source links,
  and the full clock-to-dispatch composition. Analysis links are not complete
  firmware images; startup and physical execution remain unqualified.

### Recovered blocking UART buffer write

- Reconstructed codec 0xcb90..0xcbbc as source-authored C. Native macOS
  compilation fits the original 44-byte envelope and calls the existing
  recovered byte transmitter through a normal linker symbol.
- Authenticated decoded stock/source comparison passes 84 cases, verifying
  signed nonpositive lengths, ordered source-byte loads and helper arguments,
  wrapped buffer addresses, return values and callee-saved registers.
  Native unittest passes. Transmit helper effects remain modeled here;
  nested polling composition and full firmware admission remain pending.

### Blocking buffer write composes decoded transmitter

- Added authenticated stock/source nested execution of the buffer writer and
  recovered polled transmitter. Complete ordered traces include source-byte
  loads, helper arguments, descriptor reads, status polls and MMIO writes.
- 108 cases pass, including 30 stalled prefixes with no premature peripheral
  write or subsequent byte load. Device changes between calls check fresh
  descriptor sampling; nonpositive signed lengths remain side-effect free.
- Both native macOS tests pass. Interpreter frames and peripheral stimuli are
  modeled; physical timing and complete firmware integration remain pending.

### Blocking write joins the source UART link

- Linked buffer write and the existing source transmitter into both UART
  variants (16/20 checked functions). The transmitter is selected from the
  compiler-produced console object through a relocatable source-section link;
  no stock executable extraction or console-state binding is introduced.
- 108 relocated nested cases pass, including 30 stalled prefixes. Checks
  validate the actual helper call target and descriptor addresses from source
  defaults, plus complete byte-load/poll/MMIO-write traces.
- Four native macOS regressions pass, including both source links and full
  clock-to-dispatch composition. Startup, complete image integration and
  physical execution remain unqualified; the full goal remains incomplete.

### Recovered asynchronous UART transmit-buffer entry

- Reconstructed codec 0xccac..0xcd0c in C: callback/buffer rejection,
  descriptor mode/cursor/count/context updates, DMA request setup, and the
  non-DMA interrupt-enable path with saved IRQ token restoration.
- 2,304 authenticated stock/source decoded cases pass with an independent
  final-state oracle covering descriptor and MMIO changes. Fifth stack
  argument and helper arguments/returns are checked; native unittest passes.
- DMA and IRQ helpers remain modeled in this entry-point verifier. Placement,
  nested helper composition and full firmware integration remain pending;
  this source recovery does not establish a runnable source-only image.

### Recovered UART DMA transmit completion

- Inspected DMA setup 0xc694..0xc71c: for non-0/non-1 ports stock proceeds
  without initializing the destination handshake field. This edge remains
  explicit unresolved behavior for setup reconstruction, not silently fixed.
- Recovered its completion dependency 0xc650..0xc670 as C: release channel,
  store the unused-channel sentinel, flush the selected port, then reload
  callback/context/port and invoke the callback. No null guard was added.
- Native macOS compilation produces all 32 original bytes exactly, verified
  against authenticated stock SHA-256; native unittest passes. This proves
  instruction identity at original placement, not helper closure or hardware
  execution. DMA setup and complete firmware integration remain pending.

### Transmit completion ordering and mutation verification

- Added 48 authenticated stock/source decoded cases with independent ordered
  access/call expectations. Checks prove release precedes the channel sentinel,
  drain receives the freshly loaded port, and callback/context/port are loaded
  after drain. Controlled helper mutations expose stale-load mistakes.
- Both native macOS tests pass, retaining exact 32-byte instruction identity
  verification. Release/drain/callback effects remain modeled in this check;
  physical delivery and complete source-only firmware are not established.

### Transmit completion composes decoded drain wait

- Added 108 authenticated stock/source nested completion/drain cases, including
  36 stalled prefixes. Independent ordered trace and descriptor-state oracles
  show the channel is released and marked unused before polling; callback
  fields are not read and notification is not delivered while drain is stalled.
- Controlled descriptor mutation checks port selection and callback reloads.
  Four native macOS tests pass, including prior completion and drain tests.
- Release and application callback remain modeled; decoded helpers use separate
  interpreter frames. Full image integration and physical delivery remain open.

### Transmit completion composes release and deallocation

- Replaced modeled release effects in a new completion check with decoded
  release/deallocation execution, checked against the independent allocation
  oracle. Combined this with decoded UART drain polling.
- 192 cases pass across stock/source outer and helper combinations, both DMA
  channels, multiple allocation states, and completing/stalled drains. Channel
  clearing, release-before-drain order and callback gating are checked.
- Two native macOS tests pass. Deallocation IRQ/clock effects and application
  callback remain modeled, with separate interpreter frames. This is further
  dependency qualification, not full image or physical DMA completion proof.

### DMA deallocation composes decoded IRQ leaves

- Added optional decoded IRQ hooks to the deallocation interpreter and 640
  stock/source outer/helper combinations. Checks preserve the full allocation
  trace oracle, verify actual PSR disable/restore transitions and require any
  resource-gate call to occur while interrupts are disabled.
- Two native macOS tests pass, including transmit completion leaf regression.
  Resource-gate effects and architectural PSR semantics remain modeled; this
  is dependency qualification, not physical concurrency or firmware completion.

### Completion release now carries decoded IRQ state

- Extended the transmit completion/release/deallocation/drain composition to
  execute PSR save/restore leaves. Expanded to 768 cases across enabled,
  disabled and high-bit processor states, with stock/source helper variants.
- Checks require resource gating during interrupt exclusion and exact original
  state restoration before drain starts, including when drain subsequently
  stalls. Allocation effects and callback gating retain independent oracles.
- Two native macOS tests pass. Clock effects, application callbacks and PSR
  architecture semantics remain modeled; whole-firmware and physical DMA
  completion qualification remain outstanding.

### Completion deallocation executes the source clock gate

- Replaced the completion check's modeled resource gate with decoded gate and
  module-lookup execution from the source-linked DMA/UART ELF and its compiled
  clock table. Independent MMIO oracle checks every gate call while IRQ state
  is disabled; original state must still be restored before drain.
- Expanded to 2,304 cases with three clock-register patterns. Native macOS
  regression passes. Application callbacks, MMIO stimuli and architecture
  semantics remain modeled; separate interpreter frames are not physical
  execution or a complete source-only firmware build.

### Transmit DMA setup reconstructed using upstream configuration types

- Added C setup for 0xc694 using authenticated pinned NationalChip DMA types.
  Valid ports configure memory-to-peripheral transfer and handshake 7/5.
  Stock ignores the transfer result; this behavior is retained.
- Explicit invalid-port repair releases the allocated channel and resets its
  descriptor sentinel instead of passing stock's uninitialized handshake field.
  Native host assertions check all 12 config fields, allocation failure,
  valid ports, invalid-port cleanup and ignored transfer failure.
- Native C-SKY build succeeds at 144 bytes versus 136 available. This candidate
  is not admitted: decoded stock/source valid-path qualification and placement
  remain pending, along with whole-firmware source-only completion.

### Decoded transmit DMA setup qualification for valid ports

- Added 384 authenticated stock/source target execution cases for ports 0/1,
  channel-allocation success/failure, buffer/length boundaries, burst results
  and ignored helper errors. Independent oracle checks the 12-word transfer
  configuration and cache/select/burst/callback/transfer call order.
- Different compiler stack frames are excluded from external-trace comparison;
  each is independently interpreted and ABI restoration checked. Native macOS
  unittest passes. Invalid-port cleanup remains a documented behavior repair
  covered by the separate host check, not claimed as stock equivalence.
- Helper effects remain modeled; 144-byte placement still exceeds the original
  136-byte envelope. Full source-only integration remains incomplete.

### Target qualification of invalid-port DMA cleanup

- Added 144 compiled-target repair cases across invalid ports, allocation
  failure, both real channels and allocation states. The repair invokes decoded
  release/deallocation, restores the unused-channel sentinel, returns an error
  and submits neither callback registration nor transfer.
- Independent call-order/allocation checks and both native macOS regressions
  pass. This repair is explicitly not stock equivalence; valid-port equivalence
  remains covered separately. IRQ/clock effects are modeled in this check.
- Placement overrun, remaining helper composition and full source-only image
  integration are still outstanding.

### Transmit DMA setup composes decoded burst sizing

- Added 120 stock/source setup/helper combinations with 240 decoded burst
  calls. Checks require transmit direction, both descriptor reads and the
  independent enum mapping in each resulting DMA configuration field.
- Changing the transmit size between calls verifies independent source and
  destination burst sampling. Both native macOS regressions pass, including
  invalid-port cleanup. Other setup helpers and physical DMA remain unqualified;
  source-only image integration and placement remain outstanding.

### Transmit DMA setup consumes decoded channel selection

- Added 96 stock/source setup/allocator combinations across both valid ports,
  allocation patterns and IRQ tokens. Independent allocator oracle checks state
  effects; selected channel must flow into descriptor storage, callback
  registration and the complete DMA transfer configuration.
- Exhaustion produces neither channel storage nor callback/transfer submission.
  Both native macOS tests pass, including burst-composition regression.
- Allocator IRQ/clock helpers remain modeled in this check; separate frames,
  placement and whole-image source-only integration remain outstanding.

### Transmit DMA setup composes decoded callback registration

- Added 48 stock/source setup/registration combinations with 32 decoded
  callback registrations. Independent checks verify the per-channel handler
  and private-data slots, the recovered transmit completion address and UART
  descriptor, plus registration before transfer submission.
- Allocation failure produces no registration or transfer. Three native macOS
  regressions pass, covering registration, selection and burst composition.
- Callback table writes are still in a separate frame; runtime invocation,
  DMA transfer effects and full source-only firmware integration remain open.

### Transmit DMA setup composes decoded cache cleaning

- Added 336 stock/source setup/cache combinations with independent cache-command
  oracles. Checks cover aligned/unaligned/wrapped pointers and length boundaries,
  including nonpositive signed cache lengths, before channel selection.
- Transfer arguments supply the cache range even when descriptor cache fields
  differ; cleaning still precedes an unsuccessful allocation. Both native
  macOS tests pass, including callback-registration regression.
- Cache execution uses a separate decoded frame with modeled architecture/MMIO;
  physical coherence and full source-only firmware integration remain open.

### Transmit DMA joins the source-linked DMA/UART cluster

- Added transmit setup, buffer entry, completion and drain source objects to
  the DMA/UART link: 25 source units, 2,672 text bytes, no unresolved symbols.
  Exact helper-target sets are checked for all three transmit callers and the
  completion callback literal must relocate to the source symbol.
- Four native macOS tests pass, including owned DMA storage, callback-storage
  relocation and completion/clock composition. This resolves analysis-link
  executable dependencies without extracting stock instructions.
- Persistent UART state remains externally bound in this cluster; relocated
  transmit execution, physical placement/startup and complete source-only
  firmware integration remain outstanding. This ELF is not a firmware image.

### Relocated transmit DMA setup execution

- Executed actual transmit-setup instructions from the combined source ELF in
  72 cases. Every helper target must resolve through the linked symbol map;
  callback registration must use the relocated completion address.
- Independent call/configuration/state oracles cover valid ports, allocation
  failure and explicit invalid-port cleanup. Three native macOS tests pass.
- Helper effects remain modeled here, and UART state is still externally bound.
  Source-only startup, physical placement and full firmware integration remain
  incomplete; no firmware ownership claim was added.

### DMA/UART cluster can own all runtime storage

- Added optional source UART storage to the DMA/UART linker, using authenticated
  upstream address/IRQ headers and compiled defaults checked against stock.
  With DMA, IRQ and UART storage enabled, the cluster has no external bindings
  and no unresolved symbols. UART initialized data is 256 bytes.
- Four native macOS link tests pass, including the combined storage mode.
  Existing analysis configurations remain available for comparison.
- This establishes source definitions, not startup initialization or physical
  memory placement. Relocated consumers of the combined storage mode and a
  complete runnable source-only firmware image remain unqualified.

### Transmit setup executes against source-owned UART defaults

- Added 36 decoded setup cases with all DMA/IRQ/UART storage source-linked.
  Actual compiled descriptor rows supply device pointers and initial state.
  Complete descriptor-state comparison checks that only the channel field
  changes on success and allocation failure preserves every default word.
- Tests reject retained stock descriptor accesses. Three native macOS checks
  pass, including original-binding regression and valid-port stock comparison.
- Helper effects remain modeled; startup initialization and complete runnable
  source-only firmware integration remain outstanding.

### Relocated transmit setup writes the source callback table

- Replaced the registration boundary with decoded callback-store instructions
  from the same linked ELF. The modeled four-word table uses the actual source
  BSS symbol; exact slots, completion pointer, descriptor pointer and untouched
  slots are independently checked.
- Both native macOS relocated tests pass. Owned-storage mode executes 24
  registrations across 36 setup cases; allocation failure leaves the table
  untouched. Default-binding regression also passes.
- BSS initialization is modeled, not startup execution; callback consumption,
  remaining helper effects and whole-firmware integration remain outstanding.

### DMA interrupt consumes relocated transmit registration

- Parameterized the decoded DMA ISR for linked state/table/helper addresses.
  Relocated transmit setup now feeds actual callback-table write output into
  that ISR, which dispatches the source completion pointer and UART descriptor.
- Both relocated macOS tests pass, including 24 owned-storage dispatches.
  Original stock/source ISR regression also passes. Independent checks retain
  clear/deallocate/callback ordering and exact dispatched arguments.
- ISR clear/deallocation and completion effects remain modeled in this composed
  check; hardware pending state and startup are modeled. Complete source-only
  firmware integration remains outstanding.

### Relocated DMA dispatch executes transmit completion and drain

- Extended owned-storage setup/registration/ISR composition through the actual
  relocated completion and drain instructions. Descriptor channel state from
  setup reaches completion, which resets its sentinel while preserving other
  words. The application callback receives the expected port and context.
- 24 decoded completions pass with explicit 0/32/64 drain-status stimuli;
  three native macOS regressions pass. Application completion fields remain
  harness inputs pending buffer-entry composition; release/ISR side effects
  remain modeled. Startup and full source-only firmware are not yet complete.

### Buffer entry feeds actual descriptor updates into DMA setup

- Added 72 relocated buffer/setup cases using compiled source descriptor rows,
  including 18 nested setup calls. The fifth stack argument, callback, buffer,
  count, mode and request register pass through actual decoded buffer writes.
- Independent full-memory and return oracles cover null arguments, successful
  allocation and exhaustion. Both native macOS regressions pass.
- DMA-enabled mode is a harness input; setup leaf effects remain modeled in
  this check. Connecting this entry to the longer registration/ISR/completion
  chain, startup and whole-firmware integration remain outstanding.

### Buffer submission reaches application completion through decoded chain

- Extended the source-owned buffer/setup check through decoded callback table
  writes, DMA ISR dispatch, transmit completion and drain polling. Application
  callback/context now come from actual buffer-entry descriptor writes.
- The 72 submission cases include 18 setup calls and 12 delivered completions.
  Full descriptor-state checks preserve unrelated words and verify channel
  reset. Failed submissions leave the callback table empty. Three native macOS
  regressions pass.
- DMA mode/pending stimuli and remaining setup/ISR/release effects are modeled;
  no physical transfer, startup or complete source-only firmware claim is made.

### UART completion, drain and DMA release admitted

- Admitted three reviewed C functions into the experimental codec: the
  instruction-identical 32-byte UART transmit completion callback, the
  24-byte UART drain wait in its 28-byte envelope, and the
  instruction-identical 8-byte DMA release wrapper.
- Qualification covers 48 completion order/mutation cases, 160 drain cases
  including 40 finite stalled prefixes, 384 release/deallocation compositions,
  and the existing nested completion/release/drain regressions. Thirteen focused
  ownership and composition tests pass on macOS.
- The codec now has 214 C functions at 230 occurrences and 284 total source
  replacement occurrences. Ownership is 14,416 compiled C bytes, 156 compiled
  assembly bytes, 3,113 generated source-data bytes, 80 generated metadata
  bytes, 712 generated unreachable-fill bytes, and 307,615 retained stock bytes.
- The 326,092-byte codec SHA-256 is
  `26da0f0d9fe13d659128ba11b07288ee32d940e21208efe9cbc82c92d7abdab6`.
  The 4,750,780-byte macOS EVENOTA SHA-256 is
  `f31253a2f4d0bd0e022617cadd4ae11a7e41c63848cb45eefe3f8f6e26947064`;
  package build and artifact verification pass with 7,822 placed and zero
  unresolved flash regions.
- This remains an experimental hybrid. DMA deallocation and transmit setup are
  still oversized, physical UART/DMA timing is unqualified, other components
  remain source-incomplete, and 307,615 codec bytes still depend on retained
  stock. The full source-only goal remains active.

## BL-009 bootloader gap census checkpoint

- BL-009 (`0x0042B9BA..0x00430470`, 5,978 bytes across 25 `official_blob`
  spans) is still open; no bytes closed this pass. Re-verified against a
  fresh flash plan that all 25 spans remain retained.
- Disassembly found seven spans (≈4,556 bytes) are real executable Thumb
  code, not literal/alignment filler as several of the work item's own
  labels suggested; only two spans (4 bytes total) are unambiguous
  zero-fill alignment.
- Five of the seven code spans, plus a 192-byte pointer table at
  `0x0042E104`, call or point directly into two much larger still-fully
  -opaque ranges claimed by sibling in-progress work: BL-005
  (`0x0041B862..0x0041F918`, 16,566 bytes) and BL-012
  (`0x004329D2..0x00434477`, 6,821 bytes, with neighbor BL-011 also
  in-progress). Closing BL-009's code spans without those landing first
  would either leave calls into retained bytes or require redoing the work.
- No overlay/manifest/build changes landed; see
  `docs/research/g2-bootloader-gap-census-42b9ba-430470.md` for the
  per-span classification and `docs/progress.md`'s 2026-09-11 BL-009 entry.

### CD-001 UART boot stage-one decode checkpoint

- Work item CD-001 targets the first 8,192 of the 10,240 retained bytes in
  the "UART boot stage 1 (IRAM)" region (`0x10000000..0x10002000`), which
  Wave 6 had closed only as a typed external boundary
  (`runtime_gx8002_uart_boot_stage1_boundary.c`, no source admission). This
  checkpoint records a decode-only investigation pass; it does not close any
  bytes. Ownership counts above are unchanged.
- Fixed the decode: raw `-b binary` objdump misreads this CK804EF abiv2 span
  as abiv1; wrapping it as an ELF and patching `e_flags` to `0x21006009`
  (the fix already used elsewhere in this component's tools) makes it
  readable. With that, the region resolves to a standard 64-word vector
  table, a reset prologue matching `runtime_gx8002_reset_entry.S`, a
  hand-written unsigned divide/remainder pair feeding a UART baud-divisor
  calculation shaped like the already-reconstructed
  `runtime_gx8002_uart_configure.c`, and a chain-load into what reads as
  stage two's entry point (`0x10002900`, just past CD-003's
  `0x10002800` start).
- Not yet done: none of this is compiled or run through the
  decoded-instruction execute()-comparison harness the rest of this
  component uses to qualify routines, so nothing here is claimed
  source-owned. See `docs/research/gx8002-uart-boot-stage1-cd001-analysis.md`
  for the full trace, exact repro commands, and next steps (build the
  execute() interpreter, test whether stage one shares the main runtime's
  driver source, resolve the stage-two hand-off address, coordinate with
  CD-002's adjacent `0x10002000..0x10002800` range). Goal active; hardware
  untouched.

### Completion-readiness and license-policy tooling kept truthful (XC-002)

- `make -C g2 completion-readiness` was failing closed on two false census
  drifts, not real regressions: a regex in `analyze_g2_production_raw_encoding
  _quality.py` mistook C99 designated-initializer syntax (`{.word = x}`) in
  two new GX8002 register-access files for GNU-assembler directives, and
  `analyze_g2_project_license_normalization.py`'s community-controller/Touch
  censuses hadn't caught up with 176 newly landed, already-MIT files. Both are
  fixed and re-pinned; `tools/transparent/reviewed_sources.json` was checked
  and remains accurate (nothing new to register yet this fleet run).
- One unrelated check (`_touch_generation_receipt`, Touch-owned) is still red
  because a different concurrently running item is actively editing its
  pinned input; that item must re-pin it, not this one. The completion
  assessment report and transparent-source ledger were not regenerated this
  pass — the former is blocked on the same Touch check, the latter because
  `XC-004` is concurrently regenerating the same transparent-image pipeline
  output. No functionality became source-owned by this item; it is host
  tooling only. See `docs/research/tooling-completion-readiness-truthfulness.md`.

### Case typed_external_or_unsupported byte accounting checkpoint

- The case component's 40,866-byte `typed_external_or_unsupported` bucket is
  reconciled into a non-overlapping accounting: 1,104 platform-island bytes,
  2,120 typed-gap bytes, 428 fill bytes, 7,826 genuine log-string bytes, and
  29,388 still-opaque `residual_unresolved_code_or_data` bytes. See
  `docs/research/g2-case-byte-accounting-closure.md` and
  `tools/analyze_g2_case_byte_accounting.py` (10 passing tests).
- This is accounting only: zero bytes moved into `project_source_candidate`,
  `production_routed` stays `false`. The debug/log strings and two
  first-party data tables are understood but have no logging module to route
  into yet. The case OTA updater's preserved SN identity windows are
  confirmed to lie entirely outside this range (`0x0803F000+`/`0x0807F000+`)
  — nothing to reconstruct there. The source image's 18,916-byte layout is
  documented as an intentional divergence from the stock 55,752-byte layout,
  not a silent gap: independent clean-room compilation plus 29,388
  still-unmapped bytes make byte-exact placement either meaningless or a
  route back to copying stock bytes. No hardware operation was performed.
  The full source-only goal remains active.

### Touch residual NOP-padding reconstruction checkpoint (TC-002)

- Two Touch `typed_external_or_unsupported` rows previously pinned
  "reconstructible semantics; stock authority unresolved" are now actually
  reconstructed and verified: 8 bytes of scattered architectural
  `NOP`/0xBF00 halfwords and 126 bytes of scattered legacy `MOV r8,
  r8`/0x46C0 halfwords. `tools/verify_g2_touch_nop_padding_reconstruction.py`
  compiles both canonical Thumb instructions with the project's ARMv6-M
  clang toolchain and requires the tiled, compiler-produced bytes to hash to
  the same SHA-256 already pinned for the authenticated stock content; both
  match exactly. `tests.test_g2_touch_nop_padding_reconstruction` (3 tests)
  passes. See `docs/research/g2-touch-nop-padding-reconstruction.md`.
- This is accounting/reconstruction proof only: zero bytes moved from
  `typed_external_or_unsupported` into `project_source_candidate`, the
  19,442-byte Touch complement is unchanged, and `production_routed` stays
  `false` for these 134 bytes — the freestanding Touch source candidate has
  no address-matched slot to place them in yet (that routing track is
  `TC-001`/`touch-source-experimental`). The remaining 19,308 bytes of the
  complement (Infineon CapSense/CAT2 provider boundary, owner-unresolved
  CFG/literal-pool bytes, the vector table, resident configuration/tuning
  tables, and retained log/product strings) stay exactly as previously
  classified; reproducing the log/product strings verbatim would be copying
  shipped bytes rather than reconstructing them, so they are intentionally
  left typed/retained. No hardware operation was performed. The full
  source-only goal remains active; TC-002 remains open.

### Touch source image production routing and NVIC configuration checkpoint (TC-001)

- The 31-translation-unit clean-room Touch source image
  (`components/touch/source_image`, shared runtime in
  `components/shared/touch`) is now production-routed by
  `manifests/g2-2.2.6.10-touch-source-experimental.json`, which overrides
  the `touch` component from `official_blob` to `source_build`, pins the
  built FWPK's size/SHA-256, marks the `touch_application` region
  `source_compiled`, and pins a deterministic assembled-package
  size/SHA-256. `make touch-source-experimental` builds and verifies it
  through `tools/open_cfw.py build`/`verify-artifacts`.
  `tests.test_touch_source_manifest_routing` (5 tests) confirms the
  override takes effect, every other component stays `official_blob`, and
  the assembled package is byte-for-byte reproducible.
- The image's NVIC vector-slot assumptions are now explicit, documented,
  tested configuration instead of a prose hardware blocker. New header
  `components/touch/source_image/psoc4000t_nvic.h` names every PSoC 4000T
  external IRQ with its public `psoc4000t.svd` number (the same ordering
  `g2-touch-identity-recovery.md` already cross-checked against the shipped
  vector-table shape to identify the part); `startup.c`'s vector table is
  built from these names and resized from an unexplained 48-entry array to
  the documented 29 (16 core + 13 external). `SCB1_IRQHandler`,
  `MSCLP_LP_IRQHandler`, and `MSCLP_IRQHandler` remain empty ISRs — only
  the slot *assignment* was resolvable without a board; the runtime MMIO
  *behavior* those handlers need on real hardware stays hardware-blocked.
  `tests.test_runtime_touch_nvic_config` (7 tests) pins both the header
  text and the linked ELF's vector table.
- This item does not touch the separate byte-exact stock-image
  decompilation closure (`g2-touch-software-readiness-ledger.md`, still
  open) and performs no hardware operation; `hardware_validation` stays
  `"blocked by unavailable physical evidence"` throughout. See
  `docs/research/g2-touch-source-image-production-routing.md`. The full
  source-only goal remains active.

## Documentation re-pin sweep checkpoint (XC-008)

Swept the four SHA-256-pinned reference docs
(`docs/source-coverage.md`, `docs/memory-map.md`,
`docs/upstream-inventory.md`, `docs/linux-reproducible-build.md`) for
pin/content drift. `docs/linux-reproducible-build.md`'s pin in
`tests/test_runtime_nanopb_decode_svarint_production.py` was stale (a
benign, internally-consistent scratch-directory rename landed in commit
`d794c28e` without a matching re-pin); re-pinned it to the document's
current SHA-256 through the documented test path. No prose changed in any
of the four docs — none had unfolded research content this pass, and the
other three already matched their pins. Re-running the two documented
pin-check test modules also surfaced a local toolchain-identity drift
(Xcode clang point release) and an unregistered-manifest census gap from
concurrently landing items; both are outside the four-doc pin surface and
were left for their owning items. See
`docs/research/tooling-doc-pin-resync.md`. This is a tooling/process
checkpoint with no bytes made source-owned; the source-only goal itself
remains active.

## GX8002 command-emitter generator checkpoint (XC-006)

Added a source-authored gxDNN command-stream assembler/disassembler
(`tools/gxdnn_command_emitter.py`) implementing the addressing, header
framing, and the three fully-decoded opcode-1 subtypes (`copy`,
`tensor_vector`, `tensor_tensor`), plus a half-precision quantizer
(`tools/gxdnn_quantize.py`). Round-trip tests and an oracle-fidelity test
(decode the authenticated shipped 9,164-byte command block, re-encode,
byte-exact match) pass; see `docs/research/gx8002-command-emitter-generator.md`.

This is generator infrastructure only. It does **not** close either the
9,164 accelerator-command or 120,800 model byte range from
"Remaining scope" above: six of nine opcode-1 subtypes and every
non-opcode-1 command remain fully opaque, no trained model, recovered
wake-word ground truth, or gxDNN functional interpreter exists to author or
qualify a replacement, and nothing here is production-routed. The codec's
retained accounting is unchanged.

## CD-002 codec UART-boot stage-1 data tail checkpoint

Narrowed (but did not close) the 2,048-byte `0x10002000..0x10002800`
retained span: it is compiled `.data`/zero `.bss`, not instructions, and one
value in it is a non-coincidental exact match for the public NationalChip
`grus` SDK's `arch/soc/grus/spl/spl.c:uart_new_baudrate = 115200`
initializer (same `SDK_COMMIT` already pinned elsewhere in this tree).
Rebuilding that SDK's stage-1 object cluster with our own toolchain against
the closest public board and four optimization levels reproduced the anchor
but not the surrounding bytes (≤19.2% agreement) — the exact product
board/config this span was actually built from is not present in the public
SDK snapshot, so no byte here is source-owned yet. See
`docs/research/gx8002-uart-boot-stage1-data-tail.md`. The source-only goal
remains active; the codec's retained accounting is unchanged.

## Source-only manifest and package gate checkpoint (XC-001)

Added the tooling this goal needs to measure itself end to end:
`manifests/g2-2.2.6.10-source-only.json` (a `source_build` provider for all
six EVENOTA components; extends `g2-2.2.6.10-core-source.json`, adding
codec/touch/case), `make -C g2 source-only` (build, repin, assemble, and
`open_cfw.py verify` the EVENOTA package on macOS), and `make -C g2
source-only-gate` (`analyze_g2_completion_readiness.py
--require-source-only`, exit code 6 on failure, always prints the exact
per-component release-blocking byte count). The gate treats a component as
done only if it is both byte-complete *and* `production_routed` — matching
this document's "Typed external-provider interfaces... and merely
compilable decompilation do not satisfy this goal" and the exclusion of
"candidate source that is not production-routed" from completion.

This closes no component. Selecting a `source_build` provider for codec,
touch, and case does not make them source-complete: the codec provider is
the GX8002 hybrid from `g2-2.2.6.10-codec-source-experimental.json`, still
carrying 326,000 of 326,092 retained bytes per
`docs/research/gx8002-source-candidate-build.json`; the touch and case
providers are real, link-complete source builds
(`components/touch/source_image/`, `components/case/source_image/`) but are
15,592/18,948 bytes against 34,464/55,784 stock and explicitly
`production_routed: false`, blocked on the same unavailable hardware
evidence as the rest of touch/case per `hardware-validation-policy.md`. Run
`make -C g2 source-only-gate` after any component closure lands; it names
exactly which components, and how many bytes, still block. Detail in
`docs/research/cross-cutting-source-only-gate.md`.

## Apollo data/asset generator tooling checkpoint (XC-005)

Added the generator tooling the "Apollo main application - retained data,
tables, and assets" AD-* items are told to use: `tools/assetgen_lvgl_image.py`
(PNG → `lv_image_dsc_t`), `tools/assetgen_string_pool.py` (JSON string list
→ packed blob + offset/pointer table), `tools/assetgen_nanopb_descriptor.py`
(`.proto` → nanopb `pb_msgdesc_t` C, via the real `protoc` + pinned
`nanopb==0.4.9` generator matching the vendored `third_party/nanopb` tag),
and `tools/assetgen_lvgl_font.py` (TTF/OTF → `lv_font_t`, via the real
pinned `lv_font_conv@1.5.3`, MIT). Each is round-trip-verified and, in its
own test, compiled against the real vendored headers (`third_party/lvgl`,
`third_party/nanopb`) rather than merely asserted to look right; none reads
the stock firmware image. Cordio tables and FreeType payloads get a
documented representation decision instead of a new tool: the former is
already-vendored upstream Cordio/Packetcraft `.c` source identified by the
existing `cordio-*` audit methodology, the latter is a licensed font file
the vendored FreeType 2.9.1 parses directly. Detail in
`docs/research/g2-apollo-asset-generator-tooling.md`.

This is tooling only: it owns no flash range, closes no AD-* item, and does
not by itself reduce retained-byte accounting anywhere. What remains is for
each AD-* item to identify its region's structure, choose and license a
source asset, and run the matching generator (or, for Cordio/FreeType, apply
the stated non-tooling representation) — including selecting the still-open
FreeType payload font, which this item deliberately leaves to whichever
AD-* item first needs it. No hardware operation occurred.

## 2026-09-11 checkpoint — CD-003 (codec, UART boot stage 2 reset window)

`[0x2850, 0x31E4)` (2,452 bytes) is narrowed, not closed. Two exact
NationalChip SDK object matches inside it are now admitted into
`build_gx8002_source_candidate.py` (48 bytes, `retained_stock` →
`compiled_c`): `gx_analog_config_update_enable` (byte-exact) and a second
occurrence of the reviewed `csi_vic_enable_irq` wrapper (instruction-level
equivalence, not byte identity). A third exact match, `dw_uart_getc`, has
source-identical bytes already in-tree but is blocked from integration by a
tooling gap: the candidate pipeline's placement check requires 4-byte
package-offset alignment, and this occurrence sits at a 2-byte-aligned
offset that C-SKY GCC's fixed `.text` section alignment cannot satisfy from
a plain recompile. The vector table, reset entry, BSS-clear loop, and a
larger exception-frame-building routine in the same window remain retained
stock (~2,384 of 2,452 bytes). Detail in
`docs/research/gx8002-uart-boot-stage2-reset-source.md`. No hardware
operation occurred; qualification of the admitted leaves stays blocked by
unavailable physical evidence.

## 2026-09-11 checkpoint — CD-009 (codec)

4,100 of 4,292 retained bytes at package `[0x0000B58C, 0x0000C650)`
(GX8002 image-A boot-region tail) are now reviewed `generated_source_data`
(zero-fill pad + CRC-32/MPEG-2 trailer + XIP-length word), independently
recomputed from the authenticated stock image, not embedded as opaque
bytes. The remaining 192 bytes are unmodified opaque XIP-text code behind
the existing typed boundary. See `docs/research/gx8002-image-a-stage1-
tail-source.md`. This is still a typed-boundary-adjacent, non-"done"
state for the item as a whole: 192 bytes of real executable content
remain unrecovered, and the central GX8002 readiness ledger still counts
this item's range under its prior monolithic rows pending a follow-up
split. No hardware operation occurred.

## 2026-09-11 checkpoint — BL-003 (Apollo bootloader)

30 of 11,158 retained bytes in `[0x004155E8,0x0041A648)` are now
`in_place_leaves` C, not stock: a 26-byte bounded output sink between the
AEABI byte-fill/forward-copy primitives and two 2-byte single-instruction
compatibility stubs (self-loop trap, no-op return) between the
substring-search primitive and the critical-context predicate. Both the
trap and no-op compile byte-identical to stock; the sink is the same size
with a different, behaviorally-verified instruction schedule. See
`docs/research/g2-bootloader-bounded-sink-415672-source-closure.md` and
`docs/research/g2-bootloader-trap-stubs-416026-416030-source-closure.md`.

The remaining 11,128 bytes are still retained stock. Two small literals
(an SRAM object address and the EasyLogger ANSI CSI-start escape) already
compile byte-identical to stock via the same `in_place_data` mechanism
`components/apollo_main/core_overlay/overlay.json` uses for its Cordio SMP
tables, but sit unrouted as candidate source because
`components/bootloader/core_overlay/build_component.py` has no
`in_place_data` wiring yet (`components/apollo_main/core_overlay/
build_component.py` does). Two more small literal spans have identified
but unrouted meaning (an SCB->ICSR register address plus a pointer to an
already-admitted callback; two ASCII/alignment bytes), and two address
tables (36 and 98 bytes) point at flash addresses this and prior work has
not yet named, so they are deliberately left un-encoded rather than
admitted as opaque pointer arrays. The dominant remainder is a
10,896-byte compatibility tail at `[0x00417BB8,0x0041A648)` — 97.6% of the
item — with no existing audit and a rough heuristic census of roughly
80-130 functions still to identify. Full reconnaissance in
`docs/research/g2-bootloader-bl003-remaining-recon-4155e8-41a648.md`. No
hardware operation occurred; qualification of the admitted leaves stays
blocked by unavailable physical evidence.

## 2026-09-11 checkpoint — BL-006 (bootloader)

No bytes closed. The 77-region, 5,892-byte BL-006 catalog in
`[0x0041F9B6, 0x00428378)` is now independently corroborated rather than
taken on prior audits' prose alone:
`tools/analyze_g2_bootloader_bl006_retained_survey.py` whole-image
disassembly finds zero regions with a surviving branch from genuinely
separate, still-executing code. 30 regions are confirmed-dead stock
function tails after already-source-owned replacements; 47 are literal
pools/alignment data with no control-flow reference and no data-pointer
match found elsewhere in the image. Closing either category still needs a
coordinated shared-file build-mechanism change (a dead-tail-fill primitive
for `in_place_leaves`, and/or extending the existing
`relocated_leaves`-plus-`rodata`-closure mechanism, already used for
`apollo_main`'s Cordio state-name tables, to trace and admit the literal
words) — out of proportion for a solo pass under the concurrent-agent
scope-discipline rule. Detail in `docs/research/g2-bootloader-bl006-
retained-seam-survey.md`. No hardware operation occurred.

## 2026-09-11 checkpoint — CD-006 (codec)

83 of 8,192 bytes closed in `[0x7204,0x9204)` (UART-boot stage 2 IRAM): six
literal printf format strings from the pinned NationalChip `lvp_kws` SDK
(`arch/soc/grus/trap_c.c`, `boards/.../misc_board.c`), admitted as
`generated_source_data` and production-routed through
`build_gx8002_source_candidate.py`. The rest of the span is not one
problem: an unattributed ~3,358-byte allocator/comparator code cluster
with no known upstream match; ~1,682 bytes of further printf/label strings
and small address tables, including a duplicate occurrence of the
already-admitted SPI-NOR device-name strings; and a ~3,069-byte tail that
is part of the U-Boot-derived command-line cluster
`peripheral-oss-library-provenance-audit.md` already found and explicitly
declined to reuse (GPL-2.0+, no authorized fork/release pin) — a
licensing block, not a hardware one. Detail in
`docs/research/gx8002-uart-boot-stage2-diagnostics-source.md`. No hardware
operation occurred.
