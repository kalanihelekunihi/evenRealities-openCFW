# GX8002 logging wrapper recovery

The UART error logger at package `0x101B0` forwards a null output handle,
format pointer and variadic argument list to `0x10010`. This matches the
pinned SDK `utility/libc/tinyprintf.c` wrapper's call pattern. The authenticated
[source record](gx8002-printf-candidate.json) records the candidate provenance;
it does not assert that the entire formatter is already matched.

The reconstructed C wrapper links in 28 bytes at `0x10206C24`, with formatter
entry `0x10206A84`. Stock uses 30 bytes, spilling the format argument too; the
new compiler saves only variadic argument registers and adjusts the stack
accordingly. This ABI difference needs target qualification before admission.
A host fixture checks eight integer arguments plus a string and propagation
of the formatter result, but is not evidence for C-SKY stack behavior.

Upstream tinyprintf emits characters through `fputc`, with EOF affecting its
count. Formatter and output dependencies must be reconstructed, including
that error behavior. Neither this wrapper nor a null-output substitute is
admitted to firmware in this step. The UART dispatcher remains pending.

The character helper at package `0xFF24` calls `fputc` at `0x101FC` and converts
its EOF comparison to a written-character count. The latter matches the pinned
SDK libc port: forward the character to console, ignore the stream and return
zero. A C reconstruction links byte-exactly in ten bytes, calling the console
entry at package `0xCD7C`. The [port record](gx8002-fputc-candidate.json)
authenticates the SDK port/header evidence. No output is stubbed in firmware;
the console routine and complete formatter still require recovery, so this
wrapper is not admitted yet.

The console entry at package `0xCD7C` loads the configured port from
`0x2002731C` and calls `0xCB40`. That routine selects a 128-byte descriptor
from `0x20026A94`, inserts carriage return before an input integer equal to
newline (10), and transmits the character narrowed to eight bits. The check
occurs before narrowing: integer 266 is not treated as newline.

The transmit routine at `0xC7D8` loads the MMIO base from descriptor offset 4,
polls base+20 bit 5 until set, then writes the full provided word at base+0.
No timeout is present. The source candidate preserves these operations without
inventing semantics for the unused descriptor fields. Its
[build record](gx8002-uart-console-candidate.json) records linked 16-byte transmit,
36-byte port wrapper and 20-byte console wrapper sections. Building with
`-Os -fno-inline` resolves the earlier 52-byte port-wrapper overflow.
`python3 g2/tools/link_gx8002_uart_console.py` reproduces the native macOS
build, authenticates stock, checks envelopes and rejects unresolved symbols
or relocations. The linked console wrapper matches all 20 stock bytes.
The other two routines still need target behavioral comparison, including
MMIO polling and pre-narrowing newline handling. No source admission occurs
from compilation or placement alone.

The transmit loop now passes 420 decoded stock/source execution comparisons
with an independent ordered MMIO oracle. Cases include two descriptor/base
pairs, full-word character values, readiness delays, unrelated status bits,
and finite never-ready prefixes. Run
`python3 g2/tools/compare_gx8002_uart_transmit.py`; the report is
`gx8002-uart-transmit-comparison.json`. Three interpreter tests check polling,
full-word writes and rejection of unsupported or wrong-address operations.
This is a restricted instruction model without hardware timing; port-wrapper
verification remains required before console source admission.

Port-wrapper follow-up: `python3 g2/tools/compare_gx8002_uart_putc.py`
rebuilds and checks 6,160 decoded stock/source cases against an independent
transmit-call oracle. It verifies pre-narrowing newline handling, descriptor
stride/wraparound and preservation across caller-clobbering transmit calls.
Out-of-range ports are arithmetic probes, not claims of valid device access.
The underlying 420 MMIO cases also pass; six UART interpreter tests pass.
Firmware ownership integration is the next step; no new source bytes are
counted yet, and hardware behavior remains unqualified.

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

Logging source is now wired into the experimental codec builder through
reviewed report equality, source/code hashes and linked-section checks.
All six routines are compiled on macOS; BSD notice retention is part of the
Make package target. No formatter wrapper is silently stubbed, and excluded
memory-stream routines remain retained rather than counted as recovered.
