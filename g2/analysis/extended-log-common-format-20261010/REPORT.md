# Bounded logger conversion families and stock caller ABIs

`common_format.c` defines a bounded source contract for stock formatter
`0x44b76c`: literal text, `%%`, and plain `%d`, `%u`, `%x`, `%X`, `%p`, `%s`
conversions, with one 32-bit argument word per conversion. It also supports
the validated `0`/`-`/`#` flags, fixed decimal widths through 24, fixed or
`*` string precision, a single `l` or `z` on 32-bit integers, `%c`, and
two-word `%llu`/`%lld` decimal conversions. A final literal `%` matches
stock output. It does not cover other flags, numeric precision or floating
point values. `%p`
in stock output is lowercase hexadecimal without a `0x` prefix in this
domain. Format addresses and strings are read from the authenticated main
image; the stripped image SHA-256 is
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

`verify.py` compiles the source for Cortex-M55 and M4 with warnings as errors,
then compares stock and source formatter execution in Unicorn for **336**
fixtures. They cover eight concrete stock format literals, zero through
1,024-byte destination capacities, signed extremes, unsigned/hex values,
null and nonnull pointer values, and short/long strings. Return count and
the full 2,048-byte destination window match in every case. The source API
precondition is the plain syntax above; these fixtures sample it rather than
proving every possible literal/string/argument combination. `verify_width.py`
adds **196** original/source comparisons for eight authenticated literals:
`%02X`, `%08x`, `%.20s`, `%.*s`, `%lu`, `%#x`, mixed `%02d`/`%-24s`/`%s`,
and mixed `%d`/`%08X` with four words. These include widths and precision
at short/long string boundaries, negative signed values, hex extremes,
and seven destination capacities. Full destination windows and return counts
agree.

Caller `0x43c922` visibly passes four `%u` arguments on stack words 2–5
after line and format at words 0–1. Caller `0x52fa9c` uses the same layout
for mixed `%d`/`%08X` format `0x72d3e8`. `abi.c` now has the narrow
`g2_log_candidate_four_word_stock_abi` source adapter for these two
four-conversion formats. The same source file includes bounded one-word
adapters for actual `%c` caller `0x4afa4e` and `%zu` caller `0x4d6626`,
and a three-word adapter for `%llu`/`%d` caller `0x4f624c` (low/high
64-bit words followed by the 32-bit argument). `verify_abi4.py` compares
**720** stock
logger entry versus source entry fixtures across six normal levels, four
argument vectors, enabled/disabled state, and three global limits under an
initialized quiet logger fixture. Ordered lock/output/unlock calls, output
arguments, all 1,040 shared-buffer bytes, stack restoration and return PC
match. This validates five representative one-, three- and four-word call
layouts; it
does not establish arbitrary `va_list` or all caller argument counts.

The main source archive now contains **27** translation units, and its
relocatable link still has the same four direct FlashDB unresolved symbols.
The direct SMP count stays **10/11**. The caller inventory found 5,032
distinct format addresses among 6,227 literal-resolved syntactic BL sites.
`verify_excluded.py` adds **96** stock/source formatter comparisons for
authenticated `%c`, `%zu`, `%llu`, `%lld`, and final literal `%` formats.
The `%llu` and `%lld` source uses two little-endian argument words and a
32-bit-only decimal algorithm. Signed negative and positive 64-bit limits
were sampled; all capacities, return counts and full destination windows
match. This is bounded to the selected format literals and arguments.

Remaining formatter breadth includes additional width/precision/flag
combinations, floating point and variable conversion counts; those need
their own original
versus source comparisons. Fatal level-six and null-module control flow also
remain outside the productive source entry contract. No whole logger body,
initialized production RAM, output transport, or byte-identical payload is
claimed.

`syntax_frontier.py` performs a separate static syntax triage against the
caller inventory. Of 6,227 literal-resolved syntactic sites, 6,209 contain
only tokens admitted by the current source parser and 18 sites (18 unique
format addresses) contain other syntax; 12 sites have runtime format pointers.
The outside set now consists of `%f`/`%.2f` formats. These numbers are
parser-token counts, **not** a claim
that 6,209 calls or their argument layouts have been behaviorally validated.
The selected direct formatter literals and five whole-entry call formats above
remain the measured sample. `syntax_frontier.json` lists the excluded sites.

The authenticated float caller at `0x49d580` converts three float32 inputs
with `vcvt.f64.f32` and stores three 64-bit values at stack offsets +8,
+16 and +24 before calling the logger with three `%f` conversions.
`probe_float.py` confirms the format literal and records a direct stock
formatter stop at `0x4d435c` (`vmul.f64 d0,d0,d1`) under Unicorn Cortex-M4,
M7 and M33 models for a nonzero 1.5 input. These models cannot execute that
FP64 instruction; there is no source float candidate or output-equivalence
claim. QEMU M55 executes standalone FP64, but its MPS3 board does not map
the stock `0x438000` image address (see `extended-log-float-runtime-20261010`).
An address-compatible FP64 runtime or live firmware trace with initialized
formatter state is the next discriminating input. The count of remaining
float format sites is 18 syntactic sites, not an implementation-time estimate.
