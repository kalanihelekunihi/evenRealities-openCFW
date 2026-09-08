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
